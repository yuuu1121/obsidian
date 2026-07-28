"""
[3단계] Koopman MPC로 궤적 추종 — 그리고 볼록성 vs 정확도의 실제 대가
        개념 노트 [[Koopman MPC]] 1~3번, [[Koopman with Control Input]]

실행:  python 03_mpc_control.py   (01, 02를 먼저 실행해야 합니다)
필요:  pip install cvxpy

이 스크립트는 두 모델로 각각 MPC를 돌려 비교합니다
---------------------------------------------------
(A) input-affine  z+ = A z + B u
      -> MPC가 **볼록 QP**. 전역 최적해, 초기화 불필요, 빠름.
      -> 그러나 이 시스템에서는 모델 자체가 부정확합니다 (아래 설명).

(B) bilinear      z+ = A z + B u + sum_j u_j B_j z
      -> 모델이 거의 정확합니다 (04번에서 확인: 1-step 오차 ~1e-15).
      -> 그러나 u 에 대해 비선형이라 MPC가 **비볼록**이 됩니다.
         여기서는 각 스텝에서 이전 해를 기준으로 선형화해 푸는
         반복(SQP류) 방식을 씁니다 — 국소 최적해만 보장됩니다.

왜 이런 비교가 필요한가
-----------------------
차동구동 로봇의 비선형항은 v*cos(theta), v*sin(theta) 입니다. 이것은
**입력과 상태함수의 곱**이라, input-affine 구조로는 원리적으로 표현할
수 없습니다. cos(theta)를 딕셔너리에 넣어도 소용없습니다 — 그것에 v를
곱해줄 자리가 모델에 없기 때문입니다. (04_dictionary_study.py 참고)

즉 이 예제는 논문 [[Koopman MPC]] 3번이 말하는
"때때로 비선형 실현이 더 정확한 예측을 주고, 그러면 그 트레이드오프가
정당화된다"는 상황의 구체적 사례입니다.
"""

import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import pinv

try:
    import cvxpy as cp
except ImportError:
    raise SystemExit("cvxpy가 필요합니다:  pip install cvxpy")

from koopman_lib import Lifting, f_discrete

# =============================================================================
# 모델 준비 — affine 과 bilinear 를 같은 데이터/딕셔너리로 학습
# =============================================================================
d = np.load("data_diffdrive.npz")
X, Y, U, dt = d["X"], d["Y"], d["U"], float(d["dt"])

# 이 시스템의 비선형성이 cos/sin(theta)이므로 삼각함수를 포함시킵니다
lifting = Lifting(poly_order=1, use_trig=True, cross_terms=False)
n_psi = lifting.dim()

PhiX = lifting.lift_matrix(X)
PhiY = lifting.lift_matrix(Y)
C = X.dot(pinv(PhiX))

# (A) input-affine
K_aff = PhiY.dot(pinv(np.vstack([PhiX, U])))
A_aff, B_aff = K_aff[:, :n_psi], K_aff[:, n_psi:]

# (B) bilinear
blocks = [PhiX, U] + [U[j:j + 1, :] * PhiX for j in range(2)]
K_bil = PhiY.dot(pinv(np.vstack(blocks)))
A_bil = K_bil[:, :n_psi]
B_bil = K_bil[:, n_psi:n_psi + 2]
Bj = [K_bil[:, n_psi + 2 + j * n_psi: n_psi + 2 + (j + 1) * n_psi] for j in range(2)]

# 모델 정확도 비교 (1-step)
err_aff = np.linalg.norm(Y - C.dot(K_aff.dot(np.vstack([PhiX, U])))) / np.sqrt(X.shape[1])
err_bil = np.linalg.norm(Y - C.dot(K_bil.dot(np.vstack(blocks)))) / np.sqrt(X.shape[1])

print(f"딕셔너리 차원 N_psi = {n_psi},  dt = {dt}")
print(f"모델 1-step RMS 오차")
print(f"   (A) input-affine : {err_aff:.3e}")
print(f"   (B) bilinear     : {err_bil:.3e}   <- 기계 정밀도 = 정확한 모델")
print()

# =============================================================================
# 기준 궤적
# =============================================================================
T_track = 250
nx = 3
A_amp, L = 5.0, 20.0

t = np.linspace(0, T_track * dt, T_track)
y_ref = L * (t / (T_track * dt))
x_ref_pos = A_amp * np.sin(2 * np.pi * y_ref / L)
theta_ref = np.unwrap(np.arctan2(np.gradient(y_ref), np.gradient(x_ref_pos)))
x_ref = np.vstack((x_ref_pos, y_ref, theta_ref))
Phi_ref = lifting.lift_matrix(x_ref)

# MPC 파라미터
N_mpc = 15
Q = np.eye(n_psi) * 0.1
Q[:nx, :nx] = np.diag([10.0, 10.0, 0.1])
R = np.eye(2) * 0.1
u_min = np.array([-1.5, -5.0])
u_max = np.array([1.5, 5.0])


# =============================================================================
# (A) 볼록 QP — input-affine
# =============================================================================
def run_mpc_affine():
    x = np.zeros((nx, T_track)); x[:, 0] = x_ref[:, 0]
    u_hist = np.zeros((2, T_track - 1))
    times = []

    for k in range(T_track - 1):
        H = min(N_mpc, T_track - 1 - k)
        Uv = cp.Variable((2, H))
        Zv = cp.Variable((n_psi, H + 1))

        cost = 0
        cons = [Zv[:, 0] == lifting.phi(x[:, k])]
        for i in range(H):
            cons += [Zv[:, i + 1] == A_aff @ Zv[:, i] + B_aff @ Uv[:, i]]
            cons += [Uv[:, i] <= u_max, Uv[:, i] >= u_min]
            cost += cp.quad_form(Zv[:, i] - Phi_ref[:, k + i], Q)
            cost += cp.quad_form(Uv[:, i], R)
        cost += cp.quad_form(Zv[:, H] - Phi_ref[:, k + H], Q)

        prob = cp.Problem(cp.Minimize(cost), cons)
        ts = time.time()
        prob.solve(warm_start=True)
        times.append(time.time() - ts)

        u = np.zeros(2) if Uv.value is None else np.clip(Uv.value[:, 0], u_min, u_max)
        u_hist[:, k] = u
        x[:, k + 1] = f_discrete(x[:, k], u, dt=dt)

    return x, u_hist, np.mean(times)


# =============================================================================
# (B) 비볼록 — bilinear, 이전 해 주변에서 선형화해 반복 (SQP류)
# =============================================================================
def run_mpc_bilinear(n_iter=3):
    """bilinear 항 u_j * B_j z 를 이전 iterate 기준으로 선형화합니다.

        u_j (B_j z) ~= u_j (B_j z_prev) + u_prev_j B_j (z - z_prev)

    이렇게 하면 각 반복은 QP가 되지만, 전체는 **비볼록 문제의 국소 해**를
    찾는 것입니다. 초기 추측(u_prev)에 의존한다는 점이 볼록 QP와의
    결정적 차이입니다 — [[Koopman MPC]] 3번.
    """
    x = np.zeros((nx, T_track)); x[:, 0] = x_ref[:, 0]
    u_hist = np.zeros((2, T_track - 1))
    times = []
    u_warm = np.zeros((2, N_mpc))       # 이전 스텝 해를 초기 추측으로 재사용

    for k in range(T_track - 1):
        H = min(N_mpc, T_track - 1 - k)
        u_prev = u_warm[:, :H].copy()
        ts = time.time()

        for _ in range(n_iter):
            # 현재 u_prev로 명목 궤적 z_prev 계산
            z_prev = np.zeros((n_psi, H + 1))
            z_prev[:, 0] = lifting.phi(x[:, k])
            for i in range(H):
                up = u_prev[:, i]
                z_prev[:, i + 1] = (A_bil @ z_prev[:, i] + B_bil @ up
                                    + sum(up[j] * (Bj[j] @ z_prev[:, i]) for j in range(2)))

            Uv = cp.Variable((2, H))
            Zv = cp.Variable((n_psi, H + 1))
            cost = 0
            cons = [Zv[:, 0] == lifting.phi(x[:, k])]
            for i in range(H):
                # 선형화된 동역학
                lin = A_bil @ Zv[:, i] + B_bil @ Uv[:, i]
                for j in range(2):
                    lin = lin + Uv[j, i] * (Bj[j] @ z_prev[:, i]) \
                              + u_prev[j, i] * (Bj[j] @ (Zv[:, i] - z_prev[:, i]))
                cons += [Zv[:, i + 1] == lin]
                cons += [Uv[:, i] <= u_max, Uv[:, i] >= u_min]
                cost += cp.quad_form(Zv[:, i] - Phi_ref[:, k + i], Q)
                cost += cp.quad_form(Uv[:, i], R)
            cost += cp.quad_form(Zv[:, H] - Phi_ref[:, k + H], Q)

            prob = cp.Problem(cp.Minimize(cost), cons)
            try:
                prob.solve(warm_start=True)
            except Exception:
                break
            if Uv.value is None:
                break
            u_prev = np.clip(Uv.value, u_min[:, None], u_max[:, None])

        times.append(time.time() - ts)
        u = u_prev[:, 0]
        u_hist[:, k] = u
        x[:, k + 1] = f_discrete(x[:, k], u, dt=dt)

        u_warm = np.zeros((2, N_mpc))                    # 다음 스텝 warm start
        u_warm[:, :max(H - 1, 0)] = u_prev[:, 1:H]

    return x, u_hist, np.mean(times)


# =============================================================================
# 실행 및 비교
# =============================================================================
print("(A) input-affine + 볼록 QP 실행 중...")
x_aff, u_aff, t_aff = run_mpc_affine()
e_aff = np.linalg.norm(x_ref - x_aff, axis=0)
print(f"    QP 1회 {t_aff*1000:.1f} ms,  추종오차 평균 {e_aff.mean():.3f} m")

print("(B) bilinear + 비볼록(SQP) 실행 중...")
x_bil, u_bil, t_bil = run_mpc_bilinear()
e_bil = np.linalg.norm(x_ref - x_bil, axis=0)
print(f"    1스텝 {t_bil*1000:.1f} ms,  추종오차 평균 {e_bil.mean():.3f} m")

print(f"""
{'='*70}
결과 해석
{'='*70}
                        모델 1-step오차      추종오차       계산시간
  (A) input-affine      {err_aff:.2e}       {e_aff.mean():7.3f} m    {t_aff*1000:6.1f} ms
  (B) bilinear          {err_bil:.2e}       {e_bil.mean():7.3f} m    {t_bil*1000:6.1f} ms

(A)는 볼록이라 빠르고 전역 최적해를 보장하지만, **모델이 이 시스템의
비선형성(v*cos theta)을 구조적으로 표현하지 못해** 추종에 실패합니다.

(B)는 모델이 정확해 추종이 잘 되지만, u에 대해 비선형이라 비볼록이고
계산이 더 무거우며 국소 최적해만 얻습니다.

=> "볼록성은 공짜가 아니다". 모델 구조를 선형으로 제한한 대가가
   여기서는 제어 실패로 나타납니다. 논문이 bilinear 실현을 절충안으로
   탐구하는 이유가 이것입니다 ([[Koopman MPC]] 3번, 논문 [43][97]).

주의 1: (B)도 완벽한 추종은 아닙니다. 모델이 1-step으로는 정확해도
        MPC 성능은 예측구간 길이, 가중치 Q/R, 입력 제약, SQP 반복
        횟수에 함께 좌우됩니다. 여기서는 모델 구조의 영향을 드러내는
        것이 목적이라 나머지는 튜닝하지 않았습니다. 아래 '직접 해보기'
        1~2번으로 개선해보세요.

주의 2: 모든 시스템에서 affine이 실패하는 것은 아닙니다. 비선형성이
        입력과 얽히지 않은 시스템에서는 affine으로 충분하며, 그때는
        볼록성이라는 큰 이점을 공짜로 얻습니다.
{'='*70}""")

# =============================================================================
# 시각화
# =============================================================================
fig = plt.figure(figsize=(13, 8))

ax = fig.add_subplot(2, 2, 1)
ax.plot(x_ref[0], x_ref[1], "k--", lw=2, label="reference")
ax.plot(x_aff[0], x_aff[1], "-", lw=1.5, color="tab:red", label="(A) affine / convex QP")
ax.plot(x_bil[0], x_bil[1], "-", lw=1.5, color="tab:green", label="(B) bilinear / SQP")
ax.scatter(*x_ref[:2, 0], c="k", zorder=5, s=40)
ax.axis("equal"); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_title("Tracking in xy plane")

ax = fig.add_subplot(2, 2, 2)
ax.plot(e_aff, color="tab:red", label=f"(A) affine  mean {e_aff.mean():.2f} m")
ax.plot(e_bil, color="tab:green", label=f"(B) bilinear mean {e_bil.mean():.2f} m")
ax.set_yscale("log"); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_xlabel("step"); ax.set_ylabel("||x - x_ref|| [m]"); ax.set_title("Tracking error")

ax = fig.add_subplot(2, 2, 3)
ax.plot(u_aff[0], color="tab:red", label="(A) v")
ax.plot(u_bil[0], color="tab:green", label="(B) v")
ax.axhline(u_max[0], ls=":", c="k"); ax.axhline(u_min[0], ls=":", c="k")
ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_title("linear speed v [m/s]")

ax = fig.add_subplot(2, 2, 4)
ax.plot(u_aff[1], color="tab:red", label="(A) omega")
ax.plot(u_bil[1], color="tab:green", label="(B) omega")
ax.axhline(u_max[1], ls=":", c="k"); ax.axhline(u_min[1], ls=":", c="k")
ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_title("angular speed omega [rad/s]")

fig.suptitle("Step 3: convexity vs accuracy — the real trade-off", fontsize=12)
fig.tight_layout()
plt.show()

print("""
직접 해보기
-----------
1. run_mpc_bilinear의 n_iter를 3 -> 1 로 줄여보세요. 선형화 반복이
   줄면 국소 해의 품질이 떨어집니다 — 비볼록 문제의 특징입니다.

2. N_mpc를 15 -> 5 로 줄여보세요. 계산은 빨라지지만 추종이 나빠집니다.

3. lifting에서 use_trig=False로 바꿔보세요. bilinear조차 정확해지지
   못합니다 — 모델 구조와 딕셔너리가 **둘 다** 맞아야 한다는 04번의 결론.

4. 학습 dt(0.05)와 다른 dt로 f_discrete를 호출해보세요. 논문 VI절이
   'sampling rate selection'을 열린 문제로 꼽는 이유를 체감할 수 있습니다.
""")
