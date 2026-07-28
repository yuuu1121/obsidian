"""
[2단계] 리프팅 + EDMD로 Koopman 연산자 추정
        개념 노트 [[EDMD]] 2~5번, [[Observable Function]] 에 대응

실행:  python 02_edmd_fit.py     (먼저 01_collect_data.py 를 실행해야 합니다)

무엇을 보는가
-------------
이 스크립트가 Koopman의 심장부입니다. 딱 한 줄이 전부입니다:

    [K_psi  K_u] = Psi(Y) @ pinv([Psi(X); U])

반복 학습(경사하강)이 없습니다. SVD 한 번으로 끝납니다.
실행 시간을 출력하니 확인해보세요 — 보통 0.1초 미만입니다.
"""

import time

import numpy as np
import matplotlib.pyplot as plt

from koopman_lib import Lifting, edmd_with_input, fit_decoder, rollout, DT

# --- 데이터 로드 -------------------------------------------------------------
d = np.load("data_diffdrive.npz")
X, Y, U, dt = d["X"], d["Y"], d["U"], float(d["dt"])
M = X.shape[1]
print(f"데이터 로드: {M} 쌍, dt={dt}")

# --- 딕셔너리 선택 -----------------------------------------------------------
# use_trig=True 가 이 시스템에서 결정적입니다.
# 차동구동 로봇의 비선형성은 정확히 cos(theta), sin(theta) 에서 오기 때문입니다.
# -> 물리 정보 기반 딕셔너리 설계의 교과서적 사례 ([[Observable Function]] 4번)
lifting = Lifting(poly_order=1, use_trig=True, cross_terms=True)

print(f"\n딕셔너리 차원 N_psi = {lifting.dim()}  (원 상태 차원 3에서 리프팅)")
print("  구성: [x, y, theta] + 1차 다항식 + cos/sin(theta) + 교차항")

# --- EDMD ------------------------------------------------------------------
t0 = time.time()
K_psi, K_u, PhiX = edmd_with_input(X, Y, U, lifting)
C = fit_decoder(X, PhiX)
elapsed = time.time() - t0

print(f"\nEDMD 완료 — 소요시간 {elapsed:.4f} 초")
print(f"  K_psi shape: {K_psi.shape}   <- 자율 동역학")
print(f"  K_u   shape: {K_u.shape}   <- 입력 영향 (input-affine)")
print(f"  C     shape: {C.shape}   <- 디코더 (리프팅 -> 원 상태)")
print("\n  ** 반복 최적화 없이 닫힌 형태 해로 한 번에 구했습니다 **")

# 재구성 오차 — 디코더가 제대로 작동하는지
recon = np.linalg.norm(X - C.dot(PhiX)) / np.sqrt(M)
print(f"\n재구성 RMS 오차: {recon:.3e}  (거의 0이어야 정상)")

# --- 예측 성능 검증 ----------------------------------------------------------
rng = np.random.default_rng(1)
n_tests, horizon = 6, 30

fig, axes = plt.subplots(2, 3, figsize=(13, 6))
final_errors = []

for i, ax in enumerate(axes.ravel()):
    idx = rng.integers(0, M - horizon)
    xs, preds = rollout(X[:, idx], U[:, idx:idx + horizon],
                        K_psi, K_u, C, lifting, dt=dt)
    err = np.linalg.norm(xs - preds, axis=0)
    final_errors.append(err[-1])

    ax.semilogy(err, "o-", ms=3)
    ax.set_xlabel("step"); ax.set_ylabel("||x - x_pred||")
    ax.set_title(f"test {i}  (final err {err[-1]:.2e})")
    ax.grid(alpha=.3)

fig.suptitle("Step 2: 다단계 예측 오차 — 로그 스케일", fontsize=12)
fig.tight_layout()
plt.show()

print(f"\n마지막 스텝 평균 오차: {np.mean(final_errors):.4e}")

# --- 궤적 비교 ---------------------------------------------------------------
idx = rng.integers(0, M - horizon)
xs, preds = rollout(X[:, idx], U[:, idx:idx + horizon], K_psi, K_u, C, lifting, dt=dt)

plt.figure(figsize=(6, 6))
plt.plot(xs[0], xs[1], "-o", ms=4, label="ground truth")
plt.plot(preds[0], preds[1], "-x", ms=5, label="Koopman prediction")
plt.legend(); plt.axis("equal"); plt.grid(alpha=.3)
plt.xlabel("x [m]"); plt.ylabel("y [m]")
plt.title("Step 2: 예측 궤적 vs 실제 궤적")
plt.show()

# --- 저장 -------------------------------------------------------------------
np.savez("model_diffdrive.npz", K_psi=K_psi, K_u=K_u, C=C, dt=dt,
         poly_order=lifting.poly_order, use_trig=lifting.use_trig,
         cross_terms=lifting.cross_terms)
print("저장: model_diffdrive.npz  (다음 단계 03_mpc_control.py 에서 사용)")

# --- 직접 해보기 -------------------------------------------------------------
print("""
직접 해보기
-----------
1. use_trig=False 로 바꿔서 다시 돌려보세요. 예측 오차가 얼마나 나빠지나요?
   -> 딕셔너리에 '시스템에 대한 물리 지식'을 넣는 것의 위력

2. poly_order를 1 -> 3 으로 올려보세요. 차원이 커지는데 예측이 좋아지나요?
   -> [[EDMD]] 7번 "큰 부분공간이 반드시 좋지는 않다"를 직접 확인

3. 04_dictionary_study.py 를 실행하면 여러 조합을 한 번에 비교합니다.
""")
