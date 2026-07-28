"""
[3단계] Koopman MPC로 궤적 추종
        개념 노트 [[Koopman MPC]] 1~3번에 대응

실행:  python 03_mpc_control.py   (01, 02를 먼저 실행해야 합니다)
필요:  pip install cvxpy

무엇을 보는가
-------------
학습된 선형 모델 z+ = K_psi z + K_u u 를 MPC에 넣으면, 원래 비선형이라
비볼록이었을 최적제어 문제가 **볼록 QP** 가 됩니다.

    min  sum ( (z-z_ref)' Q (z-z_ref) + u' R u )
    s.t. z_{t+1} = K_psi z_t + K_u u_t        <- 선형 제약
         u_min <= u <= u_max                  <- 선형 제약
         z_0 = psi(x_t)

볼록이므로 전역 최적해가 유일하고, 초기 추측이 필요 없습니다.
이것이 리프팅으로 차원이 커졌는데도 실시간 계산이 되는 이유입니다.

중요: 로봇의 물리 모델은 제어기 어디에도 쓰이지 않습니다.
      f_discrete는 '실제 로봇' 역할로 시뮬레이션에만 등장합니다.
"""

import time

import numpy as np
import matplotlib.pyplot as plt

try:
    import cvxpy as cp
except ImportError:
    raise SystemExit("cvxpy가 필요합니다:  pip install cvxpy")

from koopman_lib import Lifting, f_discrete

# --- 모델 로드 ---------------------------------------------------------------
m = np.load("model_diffdrive.npz")
A_l, B_l, C = m["K_psi"], m["K_u"], m["C"]
dt = float(m["dt"])

lifting = Lifting(poly_order=int(m["poly_order"]),
                  use_trig=bool(m["use_trig"]),
                  cross_terms=bool(m["cross_terms"]))

print(f"모델 로드: N_psi={A_l.shape[0]}, dt={dt}")

# ⚠️ 원본 demo.ipynb 주의사항 --------------------------------------------------
# 원본 노트북은 데이터를 dt=0.05로 수집한 뒤, MPC 셀에서 dt=0.1로 덮어씁니다.
# 그러면 학습된 모델의 시간 스케일과 시뮬레이션 시간 스케일이 2배 어긋납니다.
# 여기서는 학습에 쓴 dt를 그대로 사용합니다. 원본 동작을 재현하려면
# 아래 줄의 주석을 해제하세요 (추종 성능이 나빠지는 것을 볼 수 있습니다).
# dt = 0.1

# --- 기준 궤적 (sinusoidal weave) --------------------------------------------
T_track = 400
nx = 3
A_amp, L = 5.0, 20.0

t = np.linspace(0, T_track * dt, T_track)
y_ref = L * (t / (T_track * dt))
x_ref_pos = A_amp * np.sin(2 * np.pi * y_ref / L)
theta_ref = np.unwrap(np.arctan2(np.gradient(y_ref), np.gradient(x_ref_pos)))
x_ref = np.vstack((x_ref_pos, y_ref, theta_ref))

Phi_ref = lifting.lift_matrix(x_ref)

# --- MPC 파라미터 ------------------------------------------------------------
N_mpc = 15                                    # 예측 구간
Q = np.eye(A_l.shape[0]) * 0.1
Q[:nx, :nx] = np.diag([10.0, 10.0, 0.1])      # x, y 를 무겁게, yaw 는 가볍게
R = np.eye(B_l.shape[1]) * 0.1
u_min = np.array([-1.5, -5.0])
u_max = np.array([1.5, 5.0])

print(f"MPC: horizon={N_mpc}, 입력 제약 v∈[{u_min[0]},{u_max[0]}], "
      f"omega∈[{u_min[1]},{u_max[1]}]")

# --- Receding-horizon 루프 ---------------------------------------------------
x_mpc = np.zeros((nx, T_track))
x_mpc[:, 0] = x_ref[:, 0]
u_hist = np.zeros((2, T_track - 1))
solve_times = []

t_start = time.time()
for k in range(T_track - 1):
    H = min(N_mpc, T_track - 1 - k)

    Uvar = cp.Variable((B_l.shape[1], H))
    Zvar = cp.Variable((A_l.shape[0], H + 1))

    cost = 0
    cons = [Zvar[:, 0] == lifting.phi(x_mpc[:, k])]     # 현재 상태를 리프팅해 초기조건으로

    for i in range(H):
        cons += [Zvar[:, i + 1] == A_l @ Zvar[:, i] + B_l @ Uvar[:, i]]   # 선형 동역학
        cons += [Uvar[:, i] <= u_max, Uvar[:, i] >= u_min]                # 입력 제약
        cost += cp.quad_form(Zvar[:, i] - Phi_ref[:, k + i], Q)
        cost += cp.quad_form(Uvar[:, i], R)
    cost += cp.quad_form(Zvar[:, H] - Phi_ref[:, k + H], Q)               # 종단 비용

    prob = cp.Problem(cp.Minimize(cost), cons)
    ts = time.time()
    try:
        prob.solve(warm_start=True)
    except Exception:
        prob.solve(solver=cp.OSQP, warm_start=True)
    solve_times.append(time.time() - ts)

    if Uvar.value is None:
        print(f"  [경고] step {k}: solver 실패 ({prob.status}) — 입력 0 적용")
        u_cmd = np.zeros(B_l.shape[1])
    else:
        u_cmd = np.clip(Uvar.value[:, 0], u_min, u_max)

    u_hist[:, k] = u_cmd
    x_mpc[:, k + 1] = f_discrete(x_mpc[:, k], u_cmd, dt=dt)   # '실제 로봇' 시뮬레이션

elapsed = time.time() - t_start
err = np.linalg.norm(x_ref - x_mpc, axis=0)

print(f"\n완료 — 전체 {elapsed:.1f}초, QP 1회 평균 {np.mean(solve_times)*1000:.1f} ms")
print(f"추종 오차: 평균 {err.mean():.4f} m, 최대 {err.max():.4f} m")
print(f"  (QP 1회가 {np.mean(solve_times)*1000:.1f} ms 이므로 "
      f"{1/np.mean(solve_times):.0f} Hz 제어 루프가 가능합니다)")

# --- 시각화 -----------------------------------------------------------------
fig = plt.figure(figsize=(13, 8))

ax = fig.add_subplot(2, 2, 1)
ax.plot(x_ref[0], x_ref[1], "--", lw=2, label="reference")
ax.plot(x_mpc[0], x_mpc[1], "-", lw=1.5, label="MPC closed-loop")
ax.scatter(*x_mpc[:2, 0], c="r", zorder=5, label="start")
ax.axis("equal"); ax.legend(); ax.grid(alpha=.3)
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
ax.set_title("추종 결과 (xy 평면)")

ax = fig.add_subplot(2, 2, 2)
ax.plot(err); ax.grid(alpha=.3)
ax.set_xlabel("step"); ax.set_ylabel("||x - x_ref|| [m]")
ax.set_title(f"추종 오차 (평균 {err.mean():.3f} m)")

ax = fig.add_subplot(2, 2, 3)
ax.plot(u_hist[0], label="v [m/s]")
ax.axhline(u_max[0], ls=":", c="r"); ax.axhline(u_min[0], ls=":", c="r")
ax.legend(); ax.grid(alpha=.3); ax.set_title("선속도 (점선 = 제약)")

ax = fig.add_subplot(2, 2, 4)
ax.plot(u_hist[1], label="omega [rad/s]", color="darkorange")
ax.axhline(u_max[1], ls=":", c="r"); ax.axhline(u_min[1], ls=":", c="r")
ax.legend(); ax.grid(alpha=.3); ax.set_title("각속도 (점선 = 제약)")

fig.suptitle("Step 3: Koopman MPC — 물리 모델 없이 데이터만으로 제어", fontsize=12)
fig.tight_layout()
plt.show()

# --- 직접 해보기 -------------------------------------------------------------
print("""
직접 해보기
-----------
1. N_mpc를 15 -> 5 로 줄여보세요. 추종이 나빠지는 대신 QP가 빨라집니다.
   실시간성과 성능의 트레이드오프를 직접 확인할 수 있습니다.

2. Q[:3,:3]의 yaw 가중치 0.1을 10으로 올려보세요. 자세를 더 맞추려다
   위치 추종이 나빠지는 것을 볼 수 있습니다.

3. 위쪽 'dt = 0.1' 주석을 해제해보세요. 학습 dt와 제어 dt가 어긋나면
   모델이 예측하는 한 스텝과 실제 한 스텝이 달라져 성능이 떨어집니다.
   -> 논문 VI절이 'sampling rate selection'을 열린 문제로 꼽는 이유입니다.

4. 02번에서 use_trig=False로 학습한 모델로 이 스크립트를 돌려보세요.
   딕셔너리 선택이 제어 성능까지 어떻게 전파되는지 볼 수 있습니다.
""")
