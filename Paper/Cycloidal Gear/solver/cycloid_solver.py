# -*- coding: utf-8 -*-
"""
Cycloidal drive performance solver.

Computes what spreadsheet formulas cannot:
  * contact force distribution   (Song 2023, eqs 20-32; circular dependency
                                  between delta_max and F_max -> iteration)
  * backlash / return error      (entry angle beta from the contact equations)
  * transmission error           (Song 2023, eq 15; nonlinear simultaneous
                                  equations solved per input angle)

Reads parameters from the design workbook's "1.설계입력" sheet and writes the
results back into a "6.성능계산" sheet, then draws the plots.

Reference:
  Song, X., Chen, Y., Yang, J. (2023) Machines 11, 775.
      DOI 10.3390/machines11080775
  Nachimowicz, J., Rafalowski, S. (2016) Acta Mech. et Automatica 10(2).
      DOI 10.1515/ama-2016-0022
"""
from __future__ import annotations

import math
import sys
import pathlib
from dataclasses import dataclass

import numpy as np
from scipy.optimize import fsolve, brentq

# --------------------------------------------------------------------- params
@dataclass
class Geom:
    rp: float        # pin centre-circle radius            [mm]
    rrp: float       # pin radius                          [mm]
    a: float         # eccentricity                        [mm]
    zc: int          # cycloid teeth  (= reduction ratio)
    bc: float        # cycloid gear width                  [mm]
    drp: float       # pin-position modification  (<0)     [mm]
    drrp: float      # pin-radius modification    (>0)     [mm]
    T: float = 420.0     # output torque                   [N.m]
    E: float = 2.06e5    # Young's modulus                 [MPa]
    nu: float = 0.3      # Poisson ratio
    torque_share: float = 0.55   # per-disc share, Song 5.4

    @property
    def zp(self) -> int:
        return self.zc + 1

    @property
    def K1(self) -> float:
        """short width coefficient, unmodified"""
        return self.a * self.zp / self.rp

    @property
    def K1m(self) -> float:
        """short width coefficient after pin-position modification.
        Song 2023 states this MUST be refreshed once d_rp is applied."""
        return self.a * self.zp / (self.rp + self.drp)

    @property
    def iH(self) -> float:
        return self.zp / self.zc

    def check(self) -> list[str]:
        errs = []
        if self.rp / (self.a * self.zp) <= 1:
            errs.append(f"drive condition violated: rp/(a*zp)="
                        f"{self.rp/(self.a*self.zp):.4f} <= 1")
        if self.K1 >= 1:
            errs.append(f"K1 = {self.K1:.4f} >= 1 (profile self-intersects)")
        if self.drp >= 0:
            errs.append(f"d_rp should be negative, got {self.drp}")
        if self.drrp <= 0:
            errs.append(f"d_rrp should be positive, got {self.drrp}")
        return errs


# ------------------------------------------------------------------- profile
def profile(g: Geom, phi, modified: bool):
    """Nachimowicz eq (1)(2).  For the modified profile substitute
    rp -> rp+d_rp and rrp -> rrp+d_rrp (verified against Song eq 20)."""
    rp = g.rp + g.drp if modified else g.rp
    rrp = g.rrp + g.drrp if modified else g.rrp
    zp = g.zp
    Psi = np.arctan2(np.sin((1 - zp) * phi),
                     rp / (g.a * zp) - np.cos((1 - zp) * phi))
    x = rp * np.cos(phi) - rrp * np.cos(phi + Psi) - g.a * np.cos(zp * phi)
    y = -rp * np.sin(phi) + rrp * np.sin(phi + Psi) + g.a * np.sin(zp * phi)
    return x, y


def profile_normal(g: Geom, phi, modified: bool, h: float = 1e-7):
    """unit outward normal, by central difference on the parametric curve"""
    x1, y1 = profile(g, phi - h, modified)
    x2, y2 = profile(g, phi + h, modified)
    tx, ty = x2 - x1, y2 - y1
    n = np.hypot(tx, ty)
    # rotate tangent by -90deg  (t x k) -> (ty, -tx)
    return ty / n, -tx / n


# ------------------------------------------------- contact force (Song 5.x)
def initial_clearance(g: Geom, phi):
    """Song eq (20).  Physically meaningful over 0..pi only."""
    K1 = g.K1m
    S = 1.0 + K1**2 - 2.0 * K1 * np.cos(phi)
    sq = np.sqrt(S)
    return (g.drrp * (1.0 - np.sin(phi) / sq)
            - g.drp * (1.0 - K1 * np.cos(phi)
                       - np.sqrt(max(0.0, 1.0 - K1**2)) * np.sin(phi)) / sq)


def curvature_radius(g: Geom, phi):
    """Song eq (29)"""
    K1 = g.K1m
    S = 1.0 + K1**2 - 2.0 * K1 * np.cos(phi)
    denom = K1 * (1.0 + g.zp / g.a) * np.cos(phi) - (1.0 + g.zp * K1**2)
    return g.rrp + g.rp * S**1.5 / denom


def contact_forces(g: Geom, tol=1e-3, itmax=200, verbose=False):
    """Song eqs (20)-(32).  delta_max and F_max depend on each other, so the
    paper prescribes iteration from F_max0 = 2.2*T/(K1*zc*rp) until
    |F_k - F_k-1| < 0.1% F_k, then averaging the last two."""
    Tc = g.torque_share * g.T                 # N.m, per disc
    K1 = g.K1m
    rp_m = g.rp / 1000.0                      # SI for the torque balance

    # pin angular positions over the loaded half
    npins = g.zp // 2
    idx = np.arange(1, npins + 1)
    phi_i = idx * (2.0 * math.pi / g.zp)

    S_i = 1.0 + K1**2 - 2.0 * K1 * np.cos(phi_i)
    # l_i / r_c'   (Song eq 22) -- the moment-arm ratio
    lam = np.sin(phi_i) / np.sqrt(S_i)
    rc = g.rp * g.zc / g.zp                   # cycloid pitch radius [mm]
    l_i = rc * lam                            # [mm]
    gap = np.array([initial_clearance(g, p) for p in phi_i])   # [mm]

    F = 2.2 * g.T / (K1 * g.zc * rp_m)        # eq (32)  [N]
    hist = [F]
    for it in range(itmax):
        # --- deformation of the most loaded pair, eq (27) with f_max ignored
        rho = abs(curvature_radius(g, phi_i[np.argmax(lam)]))
        # eq (28): contact half-width
        Req = 2.0 * rho * g.rrp / (rho + g.rrp)
        c = 4.99e-3 * math.sqrt(2.0 * (1 - g.nu**2) / g.E
                                * F / g.bc * Req)
        c = max(c, 1e-9)
        W = (2.0 * (1 - g.nu**2) / g.E * F / (math.pi * g.bc)
             * (2.0 / 3.0 + math.log(16.0 * g.rp * rho / c**2)))
        dmax = W                              # f_max ignored (paper's choice)

        # --- which teeth carry load:  delta_i > gap_i
        delta = lam * dmax
        live = delta > gap
        if not live.any():
            raise RuntimeError("no tooth in contact - check modification coeffs")

        # --- torque balance, eq (25)
        denom = np.sum((lam[live] - gap[live] / dmax) * l_i[live]) / 1000.0
        Fnew = Tc / denom

        hist.append(Fnew)
        if abs(Fnew - F) < tol * abs(Fnew):
            F = 0.5 * (F + Fnew)              # paper averages the last two
            break
        F = Fnew
    else:
        raise RuntimeError(f"contact-force iteration did not converge in {itmax}")

    # final distribution, eq (23)
    delta = lam * dmax
    live = delta > gap
    Fi = np.zeros_like(lam)
    Fi[live] = (delta[live] - gap[live]) / dmax * F

    if verbose:
        print(f"    iterations={len(hist)-1}  F_max0={hist[0]:.1f} -> "
              f"F_max={F:.2f} N   delta_max={dmax*1000:.3f} um")

    return {
        "F_max": F, "delta_max": dmax, "pin_index": idx, "phi": phi_i,
        "F_i": Fi, "gap": gap, "delta": delta, "l_i": l_i,
        "n_contact": int(live.sum()),
        "contact_pins": idx[live],
        "iters": len(hist) - 1,
    }


# ------------------------------------------------------ TCA (Song 3.x, eq 15)
def _pin_point(g: Geom, i: int, th: float):
    """pin surface point and its unit normal, in the fixed pin frame"""
    ang = 2.0 * math.pi / g.zp * i
    cx, cy = g.rp * math.sin(ang), g.rp * math.cos(ang)
    px, py = cx + g.rrp * math.cos(th), cy + g.rrp * math.sin(th)
    # outward normal of a circle is radial
    return px, py, math.cos(th), math.sin(th)


def _cycloid_point(g: Geom, th: float, phi_in: float, phi_c: float,
                   modified: bool):
    """cycloid surface point + normal mapped into the pin frame via M_cp"""
    x, y = profile(g, th, modified)
    nx, ny = profile_normal(g, th, modified)
    c, s = math.cos(phi_c), math.sin(phi_c)
    # rotation by phi_c, then eccentric translation by a at angle phi_in
    X = c * x + s * y + g.a * math.cos(phi_in)
    Y = -s * x + c * y + g.a * math.sin(phi_in)
    NX = c * nx + s * ny
    NY = -s * nx + c * ny
    return X, Y, NX, NY


def _contact_residual(u, g: Geom, i: int, phi_in: float, modified: bool):
    """Song eq (15): position match (2 scalars) + normal match (1 scalar,
    the second component follows because both normals are unit length)."""
    th_c, th_p, phi_c = u
    X, Y, NX, NY = _cycloid_point(g, th_c, phi_in, phi_c, modified)
    px, py, npx, npy = _pin_point(g, i, th_p)
    return [X - px, Y - py, NX - npx]


def solve_contact(g: Geom, i: int, phi_in: float, modified: bool, guess):
    """one contact solution; returns (th_c, th_p, phi_c) or None"""
    sol, info, ier, _ = fsolve(_contact_residual, guess,
                               args=(g, i, phi_in, modified),
                               full_output=True, xtol=1e-11)
    if ier != 1:
        return None
    if max(abs(v) for v in info["fvec"]) > 1e-6:
        return None
    return sol


def entry_angle(g: Geom, modified: bool = True, i: int = 1):
    """Beta: how far the cycloid turns from its free position before the
    clearance is taken up and contact begins.  Song 3.5 -> backlash = 2*beta.

    While out of contact the crank and the disc turn together, so
    phi_in = phi_ci = beta.  We look for the smallest beta whose contact
    equations admit a solution, bracketing on the signed gap."""
    def signed_gap(beta):
        """>0 while the profiles are apart at the nominal contact point"""
        # nominal pin angle for tooth i
        ang = 2.0 * math.pi / g.zp * i
        # find the cycloid parameter whose point is nearest that pin centre
        cx, cy = g.rp * math.sin(ang), g.rp * math.cos(ang)
        th = np.linspace(0.0, 2.0 * math.pi, 4000)
        X, Y, _, _ = zip(*[_cycloid_point(g, t, beta, beta, modified)
                           for t in th[::40]])
        X, Y = np.array(X), np.array(Y)
        d = np.hypot(X - cx, Y - cy).min()
        return d - g.rrp        # >0 apart, <0 overlapping

    lo, hi = 0.0, math.radians(0.6)
    f_lo = signed_gap(lo)
    if f_lo <= 0:
        return 0.0              # already touching: no clearance
    f_hi = signed_gap(hi)
    tries = 0
    while f_hi > 0 and tries < 8:
        hi *= 2.0
        f_hi = signed_gap(hi)
        tries += 1
    if f_hi > 0:
        raise RuntimeError("could not bracket the entry angle")
    return brentq(signed_gap, lo, hi, xtol=1e-12)


def transmission_error(g: Geom, modified: bool = True, n_steps: int = 120,
                       verbose: bool = False):
    """TE = phi_out - phi_in/zc, swept over one small period (2*pi/zp of the
    crank).  Uses the previous solution as the next initial guess -- the
    continuation trick the paper hints at when it warns about initial values."""
    beta = entry_angle(g, modified)
    period = 2.0 * math.pi / g.zp
    phis = beta + np.linspace(0.0, period, n_steps)

    # initial guess: contact near the pin closest to the x-axis
    i = 1
    ang = 2.0 * math.pi / g.zp * i
    guess = [ang, ang + math.pi, beta]
    out, ok = [], 0
    for p in phis:
        sol = solve_contact(g, i, p, modified, guess)
        if sol is None:
            # retry from a few perturbed starts
            for d in (0.02, -0.02, 0.1, -0.1):
                sol = solve_contact(g, i, p, modified,
                                    [guess[0] + d, guess[1] + d, guess[2]])
                if sol is not None:
                    break
        if sol is None:
            out.append(np.nan)
            continue
        guess = list(sol)
        ok += 1
        phi_c = sol[2]
        out.append(phi_c - p / g.zc)

    te = np.array(out)
    if verbose:
        print(f"    beta={math.degrees(beta)*60:.4f} arcmin, "
              f"solved {ok}/{n_steps} steps")
    return {
        "beta": beta,
        "backlash_arcmin": 2.0 * math.degrees(beta) * 60.0,
        "phi_in_deg": np.degrees(phis),
        "TE_arcmin": np.degrees(te) * 60.0,
    }
