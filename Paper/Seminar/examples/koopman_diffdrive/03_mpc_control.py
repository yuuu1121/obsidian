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

from koopman_lib import Lifting, f_discrete, setup_korean_font

setup_korean_font()      # 그래프 한글 깨짐 방지 (폰트 없으면 자동으로 건너뜀)

# =============================================================================
# 모델 준비 — affine 과 bilinear 를 같은 데이터/딕셔너리로 학습
# =============================================================================
d = np.load("data_diffdrive.npz")
X, Y, U, dt = d["X"], d["Y"], d["U"], float(d["dt"])

# 이 시스템의 비선형성이 cos/sin(theta)이므로 삼각함수를 포함시킵니다
lifting = Lifting(poly_order=1, use_trig=True, cross_terms=False)
n_psi = lifting.dim()

# PhiX, PhiY : (n_psi, M)  -- 상태/다음상태를 딕셔너리로 리프팅한 것
# C          : (nx, n_psi) -- 디코더 (리프팅 공간 -> 원 상태로 복원)
PhiX = lifting.lift_matrix(X)
PhiY = lifting.lift_matrix(Y)
C = X.dot(pinv(PhiX))

# (A) input-affine:  PhiY ~= A_aff @ PhiX + B_aff @ U
# koopman_lib.edmd_with_input과 동일한 구성입니다 — [PhiX; U]를 세로로 쌓아
# 하나의 최소자승(K_aff = PhiY @ pinv([PhiX; U]))으로 A, B를 한번에 풉니다.
# K_aff : (n_psi, n_psi + 2)  ->  앞 n_psi열이 A_aff, 뒤 2열이 B_aff
K_aff = PhiY.dot(pinv(np.vstack([PhiX, U])))
A_aff, B_aff = K_aff[:, :n_psi], K_aff[:, n_psi:]

# (B) bilinear:  PhiY ~= A_bil @ PhiX + B_bil @ U + sum_j U[j] * (Bj[j] @ PhiX)
# 핵심은 blocks에 U[j]*PhiX 항을 추가로 쌓는 것입니다 — 이게 입력 u_j와
# 상태 PhiX의 '곱'을 회귀 변수로 명시적으로 넣어주는 부분이라, affine
# 모델에는 없던 u*state 교차항을 선형회귀 하나로 흡수할 수 있게 됩니다.
# blocks[i] shape: PhiX,U는 (n_psi,M)/(2,M), U[j:j+1,:]*PhiX는 (n_psi,M) 브로드캐스트
# -> np.vstack(blocks) : (n_psi + 2 + 2*n_psi, M)
blocks = [PhiX, U] + [U[j:j + 1, :] * PhiX for j in range(2)]
K_bil = PhiY.dot(pinv(np.vstack(blocks)))
A_bil = K_bil[:, :n_psi]                      # (n_psi, n_psi)
B_bil = K_bil[:, n_psi:n_psi + 2]             # (n_psi, 2)
# Bj[j] : (n_psi, n_psi) -- u_j에 곱해지는 상태 선형변환. 각 j마다 K_bil에서
# n_psi열씩 슬라이스해서 꺼냅니다 (blocks에 쌓은 순서와 정확히 대응)
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
# 기준 궤적 -- sinusoidal weave (지그재그로 전진하며 좌우로 흔드는 경로)
# =============================================================================
T_track = 250
nx = 3
A_amp, L = 5.0, 20.0

t = np.linspace(0, T_track * dt, T_track)
y_ref = L * (t / (T_track * dt))                      # y는 시간에 비례해 단조 전진
x_ref_pos = A_amp * np.sin(2 * np.pi * y_ref / L)      # x는 y를 따라 사인파로 흔들림
# theta_ref: 경로의 접선 방향각. dx/dy가 아니라 (dy, dx) 순서로 arctan2에
# 넣는 이유는 '진행방향 = y축 기준'이 아니라 표준 좌표계(atan2(dy,dx))로
# 접선각을 구하기 위함입니다 (여기선 두 축 다 매끈해서 결과는 동일).
# np.gradient로 이산 미분(중심차분)한 뒤 atan2로 각도를 얻으면 -pi~pi로
# 잘리므로, np.unwrap으로 이 불연속(2pi 점프)을 제거해 연속적인 theta로
# 만듭니다 -- 그래야 MPC 추종오차 계산에서 각도가 튀지 않습니다.
theta_ref = np.unwrap(np.arctan2(np.gradient(y_ref), np.gradient(x_ref_pos)))
x_ref = np.vstack((x_ref_pos, y_ref, theta_ref))       # (nx, T_track)
Phi_ref = lifting.lift_matrix(x_ref)                   # (n_psi, T_track) -- 리프팅 공간에서의 참조궤적

# MPC 파라미터
N_mpc = 15          # 예측 구간(horizon) 길이
Q = np.eye(n_psi) * 0.1
# 리프팅된 상태 z 전체에 작은 가중치(0.1)를 주되, 앞 nx=3개(x,y,theta 원래
# 좌표에 해당)에는 훨씬 큰 가중치를 줘서 '실제로 추종하고 싶은 물리량'을
# 우선시합니다. 나머지 z 성분(cos/sin(theta) 등)은 상태 표현을 위한
# 보조항이라 직접 추종 목표로 삼지 않습니다.
Q[:nx, :nx] = np.diag([10.0, 10.0, 0.1])
R = np.eye(2) * 0.1                        # 입력 크기에 대한 가중치 (에너지/부드러움 페널티)
u_min = np.array([-1.5, -5.0])             # [v_min, omega_min]
u_max = np.array([1.5, 5.0])               # [v_max, omega_max]


# =============================================================================
# (A) 볼록 QP — input-affine
# =============================================================================
def run_mpc_affine():
    """cvxpy 기초: 미지수를 cp.Variable로 선언하고, 등식/부등식 제약을
    파이썬 리스트로 모은 뒤, cp.Problem(cp.Minimize(cost), cons)로 풀어
    prob.solve() 한 번이면 QP 솔버가 최적해를 채워줍니다.

    이 함수는 receding-horizon 방식입니다: 매 스텝 k마다 H스텝짜리 QP를
    새로 풀고, 그중 '첫 입력(Uv[:,0])'만 실제로 적용한 뒤 나머지는 버립니다.
    다음 스텝에서 실제 상태로부터 다시 H스텝 QP를 풉니다 (MPC의 정의).
    """
    x = np.zeros((nx, T_track)); x[:, 0] = x_ref[:, 0]
    u_hist = np.zeros((2, T_track - 1))
    times = []

    for k in range(T_track - 1):
        H = min(N_mpc, T_track - 1 - k)   # 마지막 근처에서는 horizon을 줄여 배열 범위를 안 넘게 함

        # cp.Variable((2, H))  ->  2행(v, omega) x H열(미래 스텝) 크기의 '미지수 행렬'.
        # 아직 값이 없고, 아래 cp.Problem.solve()가 이 자리를 채웁니다.
        Uv = cp.Variable((2, H))          # 미래 H스텝의 입력 (구할 값)
        Zv = cp.Variable((n_psi, H + 1))  # 미래 H+1개 시점의 리프팅 상태 (구할 값, 초기값 포함)

        cost = 0
        # 제약 리스트: cvxpy에서 '==', '<=', '>=' 로 만든 Constraint 객체들을
        # 파이썬 list에 그냥 쌓으면 됩니다. 이 전체가 QP의 실행가능영역(feasible set).
        cons = [Zv[:, 0] == lifting.phi(x[:, k])]   # 초기조건: 현재 실제 상태를 리프팅해서 고정
        for i in range(H):
            # 동역학 제약이 A_aff @ Zv + B_aff @ Uv 로 Zv, Uv에 대해 '선형'입니다.
            # 선형 등식 제약 + 아래 박스 제약(선형 부등식) + 이차비용(quad_form)
            # 조합이 바로 QP(quadratic program)의 정의이고, 이 조합은 항상 볼록입니다.
            cons += [Zv[:, i + 1] == A_aff @ Zv[:, i] + B_aff @ Uv[:, i]]
            cons += [Uv[:, i] <= u_max, Uv[:, i] >= u_min]   # 입력 박스 제약 (선형 부등식)
            # cp.quad_form(v, Q) == v.T @ Q @ v 를 cvxpy가 이해하는 형태로 만들어주는 함수.
            # Q가 양의준정부호이면 이 항은 v에 대해 볼록 이차함수가 됩니다.
            cost += cp.quad_form(Zv[:, i] - Phi_ref[:, k + i], Q)   # 참조궤적과의 편차 페널티
            cost += cp.quad_form(Uv[:, i], R)                       # 입력 크기 페널티
        cost += cp.quad_form(Zv[:, H] - Phi_ref[:, k + H], Q)       # 마지막(terminal) 편차도 페널티

        # 비용이 볼록 이차식이고 제약이 전부 선형이므로 이 문제는 볼록 QP입니다.
        # 즉 지역해 걱정 없이 전역 최적해가 한 번의 solve()로 보장됩니다.
        prob = cp.Problem(cp.Minimize(cost), cons)
        ts = time.time()
        prob.solve(warm_start=True)   # warm_start: 솔버 내부적으로 이전 solve의 정보를 재사용해 가속
        times.append(time.time() - ts)

        # 풀리지 않으면(수치 문제 등) Uv.value가 None일 수 있으므로 방어적으로 0 처리
        u = np.zeros(2) if Uv.value is None else np.clip(Uv.value[:, 0], u_min, u_max)
        u_hist[:, k] = u
        x[:, k + 1] = f_discrete(x[:, k], u, dt=dt)   # 실제 로봇(ground truth)에 첫 입력만 적용

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

    ---------------------------------------------------------------------
    선형화 유도 (테일러 1차 전개):
    문제의 항은 u_j(z) := u_j * (B_j @ z) 로, u와 z 둘 다에 대해 곱셈이라
    (u,z) 결합공간에서 '쌍선형(bilinear)'입니다. 두 변수를 함께 바꾸는 항이라
    QP가 요구하는 선형 제약이 아닙니다. 그래서 이전 iterate (u_prev, z_prev)
    주변에서 1차 테일러 전개를 합니다:

        f(u, z) = u_j * (B_j z)
        f(u_prev+du, z_prev+dz) ~= f(u_prev,z_prev)
                                    + df/du_j * du_j + df/dz * dz   (1차항만)
                                  = u_prev_j (B_j z_prev)                 <- 상수항
                                    + du_j (B_j z_prev)                   <- df/du_j = B_j z_prev
                                    + u_prev_j (B_j dz)                   <- df/dz   = u_prev_j B_j

        du_j = u_j - u_prev_j,  dz = z - z_prev 를 대입해 정리하면:

        u_j (B_j z) ~= u_j (B_j z_prev) + u_prev_j (B_j (z - z_prev))

    즉 아래 코드의
        Uv[j,i] * (Bj[j] @ z_prev[:,i])              <- u는 미지수(Uv), z는 이전 해(z_prev)로 고정
        + u_prev[j,i] * (Bj[j] @ (Zv[:,i] - z_prev[:,i]))  <- u는 이전 해(u_prev)로 고정, z는 미지수(Zv)
    두 항이 정확히 위 식의 두 항입니다. 두 항 모두 Uv 또는 Zv에 대해
    '선형'이 되도록 다른 쪽을 상수(이전 iterate 값)로 고정한 것이 핵심입니다
    — 이래야 매 iteration이 다시 QP로 풀립니다.

    ⚠️ n_iter가 부족하거나 초기 추측(u_prev)이 나쁘면 이 선형화 자체가
       부정확해지고, 국소해가 나쁜 곳으로 수렴할 수 있습니다 (아래 '직접
       해보기' 1번 참고).
    """
    x = np.zeros((nx, T_track)); x[:, 0] = x_ref[:, 0]
    u_hist = np.zeros((2, T_track - 1))
    times = []
    u_warm = np.zeros((2, N_mpc))       # 이전 스텝 해를 초기 추측으로 재사용

    for k in range(T_track - 1):
        H = min(N_mpc, T_track - 1 - k)
        u_prev = u_warm[:, :H].copy()   # 이번 스텝 SQP의 초기 추측 (0번째 iter의 선형화 기준점)
        ts = time.time()

        for _ in range(n_iter):
            # --- 1) 현재 u_prev로 명목(nominal) 궤적 z_prev를 실제로 전개 -----
            # bilinear 모델식 그대로(비선형 그대로) z_prev를 계산합니다.
            # 이 z_prev가 다음 QP에서 '선형화 기준점'으로 쓰입니다.
            z_prev = np.zeros((n_psi, H + 1))
            z_prev[:, 0] = lifting.phi(x[:, k])
            for i in range(H):
                up = u_prev[:, i]
                z_prev[:, i + 1] = (A_bil @ z_prev[:, i] + B_bil @ up
                                    + sum(up[j] * (Bj[j] @ z_prev[:, i]) for j in range(2)))

            # --- 2) (u_prev, z_prev) 주변에서 선형화한 QP를 새로 구성 --------
            Uv = cp.Variable((2, H))
            Zv = cp.Variable((n_psi, H + 1))
            cost = 0
            cons = [Zv[:, 0] == lifting.phi(x[:, k])]
            for i in range(H):
                # 선형화된 동역학: affine 부분(A_bil, B_bil)은 원래도 선형이라
                # 그대로 두고, bilinear 항 u_j*(Bj@z)만 테일러 1차항으로 치환합니다.
                lin = A_bil @ Zv[:, i] + B_bil @ Uv[:, i]
                for j in range(2):
                    # 위 유도의 두 항: u_j(B_j z_prev) + u_prev_j*B_j*(z - z_prev)
                    lin = lin + Uv[j, i] * (Bj[j] @ z_prev[:, i]) \
                              + u_prev[j, i] * (Bj[j] @ (Zv[:, i] - z_prev[:, i]))
                cons += [Zv[:, i + 1] == lin]
                cons += [Uv[:, i] <= u_max, Uv[:, i] >= u_min]
                cost += cp.quad_form(Zv[:, i] - Phi_ref[:, k + i], Q)
                cost += cp.quad_form(Uv[:, i], R)
            cost += cp.quad_form(Zv[:, H] - Phi_ref[:, k + H], Q)

            # 이 QP 자체는 볼록이지만(모든 항이 이제 선형/이차), 그 해가 원래의
            # 비볼록 문제의 진짜 최적해라는 보장은 없습니다 — 선형화가 근사이기
            # 때문입니다. 그래서 n_iter번 반복해 z_prev/u_prev를 갱신하며
            # 선형화 기준점을 해에 가깝게 좁혀갑니다 (SQP의 아이디어).
            prob = cp.Problem(cp.Minimize(cost), cons)
            try:
                prob.solve(warm_start=True)
            except Exception:
                break   # 솔버 실패 시 이번 반복까지의 u_prev를 그대로 사용
            if Uv.value is None:
                break
            u_prev = np.clip(Uv.value, u_min[:, None], u_max[:, None])   # 다음 iter의 선형화 기준점 갱신

        times.append(time.time() - ts)
        u = u_prev[:, 0]           # SQP 반복이 끝난 후 첫 스텝 입력만 실제로 적용 (receding horizon)
        u_hist[:, k] = u
        x[:, k + 1] = f_discrete(x[:, k], u, dt=dt)

        # --- warm start: 이번에 구한 해를 한 칸씩 밀어 다음 스텝의 초기 추측으로 --
        # 이유: MPC의 horizon은 스텝마다 1씩 미끄러지므로(receding horizon),
        # 이번 스텝의 u_prev[:,1:H] (2번째~H번째 예측입력)는 다음 스텝에서
        # 여전히 유효한 예측 구간(0번째~H-1번째)에 대응합니다. 처음부터 다시
        # 0으로 시작하는 것보다 훨씬 좋은 초기 추측이라 SQP 수렴이 빨라지고,
        # n_iter가 작아도(3회) 그럴듯한 해에 도달할 수 있습니다.
        u_warm = np.zeros((2, N_mpc))
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
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_title("추종 결과 (xy 평면)")

ax = fig.add_subplot(2, 2, 2)
ax.plot(e_aff, color="tab:red", label=f"(A) affine  mean {e_aff.mean():.2f} m")
ax.plot(e_bil, color="tab:green", label=f"(B) bilinear mean {e_bil.mean():.2f} m")
ax.set_yscale("log"); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_xlabel("step"); ax.set_ylabel("||x - x_ref|| [m]"); ax.set_title("추종 오차")

ax = fig.add_subplot(2, 2, 3)
ax.plot(u_aff[0], color="tab:red", label="(A) v")
ax.plot(u_bil[0], color="tab:green", label="(B) v")
ax.axhline(u_max[0], ls=":", c="k"); ax.axhline(u_min[0], ls=":", c="k")
ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_title("선속도 v [m/s]")

ax = fig.add_subplot(2, 2, 4)
ax.plot(u_aff[1], color="tab:red", label="(A) omega")
ax.plot(u_bil[1], color="tab:green", label="(B) omega")
ax.axhline(u_max[1], ls=":", c="k"); ax.axhline(u_min[1], ls=":", c="k")
ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_title("각속도 omega [rad/s]")

fig.suptitle("Step 3: 볼록성 vs 정확도 — 실제 트레이드오프", fontsize=12)
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
