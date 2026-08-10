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


def _hertz_deflection(g: Geom, F: float, rho: float) -> float:
    """Song eq (27) with eq (28) for the contact half-width.
    f_max (pin bending) is ignored, as the paper states it does."""
    Req = 2.0 * rho * g.rrp / (rho + g.rrp)
    c = 4.99e-3 * math.sqrt(2.0 * (1 - g.nu**2) / g.E * F / g.bc * Req)
    c = max(c, 1e-12)
    return (2.0 * (1 - g.nu**2) / g.E * F / (math.pi * g.bc)
            * (2.0 / 3.0 + math.log(16.0 * g.rp * rho / c**2)))


def contact_forces(g: Geom, tol=1e-4, itmax=400, verbose=False):
    """Song eqs (20)-(32).

    delta_max and F_max are mutually dependent (Song 5.6), so this solves the
    pair simultaneously instead of the paper's fixed-point sweep -- the same
    equations, but converged on both unknowns at once, which is more robust.

    Two consistency numbers are returned so the user can judge the result
    rather than trust it blindly:
      * residual_eq27 -- how well eq(27) holds at the converged point
      * F_from_eq27   -- the force eq(27) alone would need for this delta_max

    NOTE ON THE PAPER: Song's own numbers are not self-consistent here.  Their
    F_max=1131.37 N with delta_max~0.0051 mm satisfies eq(27) (which needs
    ~1079 N) but NOT the eq(25) torque balance with Tc=0.55*T (which yields
    ~463 N for that delta_max).  Reproducing their F_max requires Tc~1.34*T,
    which the paper does not state.  The engagement range and tooth count DO
    reproduce, so the geometry side agrees.  Treat absolute forces as
    order-of-magnitude and compare cases relatively.
    """
    Tc = g.torque_share * g.T                 # N.m per disc
    K1 = g.K1m

    idx = np.arange(1, g.zp // 2 + 1)
    phi_i = idx * (2.0 * math.pi / g.zp)
    S_i = 1.0 + K1**2 - 2.0 * K1 * np.cos(phi_i)
    lam = np.sin(phi_i) / np.sqrt(S_i)        # l_i / r_c'   (eq 22)
    rc = g.rp * g.zc / g.zp                   # cycloid pitch radius [mm]
    l_i = rc * lam
    gap = np.array([initial_clearance(g, p) for p in phi_i])
    rho = abs(curvature_radius(g, phi_i[np.argmax(lam)]))

    def force_from_balance(dmax: float):
        """eq (23)+(25): the force the torque balance needs at this dmax"""
        delta = lam * dmax
        live = delta > gap
        if not live.any():
            return None, live
        den = np.sum((lam[live] - gap[live] / dmax) * l_i[live]) / 1000.0
        return Tc / den, live

    # ---- solve the coupled pair by bisection on dmax -------------------
    # residual(dmax) = W(F_balance(dmax)) - dmax   ->  root is the operating pt
    def residual(dmax: float):
        F, live = force_from_balance(dmax)
        if F is None:
            return 1.0            # dmax too small: nothing engages
        return _hertz_deflection(g, F, rho) - dmax

    lo, hi = 1e-5, 1.0            # mm; brackets deflection 10nm .. 1mm
    f_lo, f_hi = residual(lo), residual(hi)
    if f_lo * f_hi > 0:
        raise RuntimeError("cannot bracket the delta_max root "
                           f"(residual {f_lo:.3e} .. {f_hi:.3e})")
    dmax = brentq(residual, lo, hi, xtol=1e-12, rtol=1e-12)
    F, live = force_from_balance(dmax)

    # ---- distribution, eq (23) ----------------------------------------
    delta = lam * dmax
    Fi = np.zeros_like(lam)
    Fi[live] = (delta[live] - gap[live]) / dmax * F

    # consistency diagnostics
    W_at_F = _hertz_deflection(g, F, rho)
    resid = abs(W_at_F - dmax) / dmax
    try:
        F_eq27 = brentq(lambda f: _hertz_deflection(g, f, rho) - dmax,
                        1.0, 1e7, xtol=1e-6)
    except ValueError:
        F_eq27 = float("nan")

    if verbose:
        print(f"    F_max={F:.2f} N   delta_max={dmax*1000:.3f} um   "
              f"teeth={int(live.sum())}  eq27 residual={resid*100:.2e}%")

    return {
        "F_max": F, "delta_max": dmax, "pin_index": idx, "phi": phi_i,
        "F_i": Fi, "gap": gap, "delta": delta, "l_i": l_i, "rho": rho,
        "n_contact": int(live.sum()), "contact_pins": idx[live],
        "residual_eq27": resid, "F_from_eq27": F_eq27,
        "engage_deg": (float(np.degrees(phi_i[live]).min()),
                       float(np.degrees(phi_i[live]).max())),
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


def _placed_profile(g: Geom, phi_c: float, phi_in: float, modified: bool,
                    n: int = 200000):
    """The whole cycloid outline placed in the fixed pin frame: rotated by
    phi_c about its own centre, then offset by the eccentricity a at phi_in.

    Verified ground truth: for the STANDARD profile at phi_c = phi_in = 0 every
    pin touches with gap = 0.00000 mm, which is exactly the paper's statement
    that the standard cycloid is conjugate to the pins with no clearance.
    Forgetting the eccentric offset is the mistake Song 3.4 warns about."""
    th = np.linspace(0.0, 2.0 * math.pi, n)
    x, y = profile(g, th, modified)
    c, s = math.cos(phi_c), math.sin(phi_c)
    X = c * x + s * y + g.a * math.cos(phi_in)
    Y = -s * x + c * y + g.a * math.sin(phi_in)
    return X, Y


def _min_gap(g: Geom, phi_c: float, phi_in: float, modified: bool,
             X=None, Y=None):
    """smallest (distance from a pin centre to the outline) - r_rp,
    taken over every pin.  >0 means the profile is clear of all pins."""
    if X is None:
        X, Y = _placed_profile(g, phi_c, phi_in, modified)
    best = math.inf
    for i in range(g.zp):
        ang = 2.0 * math.pi / g.zp * i
        cx, cy = g.rp * math.sin(ang), g.rp * math.cos(ang)
        d = np.hypot(X - cx, Y - cy).min() - g.rrp
        best = min(best, d)
    return best


_PHASE_CACHE: dict = {}


def conjugate_phase(g: Geom, n: int = 40000) -> float:
    """Offset direction at which the STANDARD profile is conjugate to its pins.

    The profile equation places its first lobe on the +y axis, but a pin only
    lands there for particular tooth counts.  When it does not, assuming an
    offset along +y makes the outline overlap the pins by ~e, which silently
    poisons every clearance measurement.  Measured requirement:

        z_p = 40, 12, 16 -> 0 deg      z_p = 15, 11 -> 270 deg
        z_p = 30, 26     -> 180 deg    z_p = 13     ->  90 deg

    Rather than encode that table, solve for it: conjugacy means the minimum
    gap is exactly zero, so scan the offset direction and take the phase whose
    |gap| is smallest.  Self-checking and valid for any tooth count.
    """
    key = (g.rp, g.rrp, g.a, g.zc)
    if key in _PHASE_CACHE:
        return _PHASE_CACHE[key]

    std = Geom(rp=g.rp, rrp=g.rrp, a=g.a, zc=g.zc, bc=g.bc,
               drp=0.0, drrp=0.0, T=g.T)
    th = np.linspace(0.0, 2.0 * math.pi, n)
    px, py = profile(std, th, False)
    pang = 2.0 * math.pi / g.zp * np.arange(g.zp)
    pcx, pcy = g.rp * np.sin(pang), g.rp * np.cos(pang)

    def worst(phase: float) -> float:
        X = px + g.a * math.cos(phase)
        Y = py + g.a * math.sin(phase)
        b = math.inf
        for k in range(g.zp):
            d = np.hypot(X - pcx[k], Y - pcy[k]).min() - g.rrp
            if d < b:
                b = d
        return b

    # quarter-turn candidates cover every case seen; refine around the best
    coarse = [math.radians(d) for d in range(0, 360, 5)]
    best = min(coarse, key=lambda p: abs(worst(p)))
    lo, hi = best - math.radians(5), best + math.radians(5)
    for _ in range(40):                       # golden-section on |gap|
        m1 = lo + 0.382 * (hi - lo)
        m2 = lo + 0.618 * (hi - lo)
        if abs(worst(m1)) < abs(worst(m2)):
            hi = m2
        else:
            lo = m1
    phase = 0.5 * (lo + hi)

    resid = worst(phase)
    if abs(resid) > 1e-3:                     # 1 um: conjugacy must be exact
        raise RuntimeError(
            f"could not find a conjugate phase (best residual {resid*1000:.3f} "
            f"um at {math.degrees(phase):.2f} deg) -- check the geometry")
    _PHASE_CACHE[key] = phase
    return phase


def entry_angle(g: Geom, modified: bool = True):
    """Beta: how far the disc turns from its free (centred) position before the
    clearance is taken up and the first pin is touched.  Song 3.5 defines the
    return error / backlash as 2*beta.

    Out of contact the crank and the disc turn together, so phi_in = phi_c =
    beta (the paper's own assumption).  Bisect on the signed minimum gap.

    The eccentric offset is taken along the geometry's conjugate phase (see
    conjugate_phase) -- assuming +y instead makes the standard profile overlap
    its pins for tooth counts where no pin sits on that axis, which returns a
    spurious beta = 0."""
    ph = conjugate_phase(g)

    def f(beta):
        # rotate the disc by beta while keeping the offset on the conjugate axis
        return _min_gap(g, beta, ph, modified)

    f0 = f(0.0)
    if f0 <= 0.0:
        # zero clearance is only legitimate for the unmodified profile
        if not modified:
            return 0.0
        raise RuntimeError(
            f"modified profile already interferes at rest (gap "
            f"{f0*1000:.3f} um) -- modification coefficients are too large "
            f"for e = {g.a:.3f} mm")

    hi = math.radians(0.02)
    for _ in range(16):
        if f(hi) <= 0.0:
            break
        hi *= 2.0
    else:
        raise RuntimeError(f"could not bracket beta (gap still {f(hi):.3e} mm "
                           f"at {math.degrees(hi):.3f} deg)")
    return brentq(f, 0.0, hi, xtol=1e-13)


def transmission_error(g: Geom, modified: bool = True, n_steps: int = 73,
                       verbose: bool = False, n_profile: int = 120000):
    """No-load transmission error over one small period of the crank.

    Method: for each crank angle phi_in, find the disc rotation phi_c that
    brings the profile into contact with its pins -- i.e. the phi_c where the
    minimum gap crosses zero.  That IS the solution of Song eq (15) (position
    and normal both match at a tangency), reached by bisection on a scalar
    instead of fsolve on three unknowns, which removes the initial-value
    fragility the paper warns about in 3.4.

    Then  TE = phi_c - phi_in / z_c   (Song eq 16).

    Ground-truth check available to the caller: with modified=False the profile
    is conjugate, so phi_c must track phi_in/z_c and TE must stay ~0.
    """
    period = 2.0 * math.pi / g.zp
    phis = np.linspace(0.0, period, n_steps)
    ph0 = conjugate_phase(g)      # offset axis for THIS tooth count

    # precompute the unrotated outline once; rotate it per trial angle
    th = np.linspace(0.0, 2.0 * math.pi, n_profile)
    px, py = profile(g, th, modified)

    # pin centres
    pang = 2.0 * math.pi / g.zp * np.arange(g.zp)
    pcx, pcy = g.rp * np.sin(pang), g.rp * np.cos(pang)

    def gap(phi_c, phi_in):
        c, s = math.cos(phi_c), math.sin(phi_c)
        X = c * px + s * py + g.a * math.cos(phi_in + ph0)
        Y = -s * px + c * py + g.a * math.sin(phi_in + ph0)
        best = math.inf
        for k in range(g.zp):
            d = np.hypot(X - pcx[k], Y - pcy[k]).min() - g.rrp
            if d < best:
                best = d
        return best

    te, ok = [], 0
    span = period                      # search window around the ideal angle
    for p in phis:
        ideal = p / g.zc
        lo, hi = ideal, ideal + span   # advancing the disc closes the gap
        f_lo = gap(lo, p)
        if f_lo <= 0.0:
            # already in contact: back off until clear
            lo2 = ideal - span
            if gap(lo2, p) > 0.0:
                lo, f_lo = lo2, gap(lo2, p)
            else:
                te.append(np.nan)
                continue
        f_hi = gap(hi, p)
        tries = 0
        while f_hi > 0.0 and tries < 6:
            hi += span
            f_hi = gap(hi, p)
            tries += 1
        if f_hi > 0.0:
            te.append(np.nan)
            continue
        root = brentq(lambda a: gap(a, p), lo, hi, xtol=1e-13)
        te.append(root - ideal)
        ok += 1

    te = np.array(te)
    beta = entry_angle(g, modified)
    if verbose:
        print(f"    beta={math.degrees(beta)*60:.4f}'  solved {ok}/{n_steps}")
    return {
        "beta": beta,
        "backlash_arcmin": 2.0 * math.degrees(beta) * 60.0,
        "phi_in_deg": np.degrees(phis),
        "TE_arcmin": np.degrees(te) * 60.0,
        "solved": ok,
    }
