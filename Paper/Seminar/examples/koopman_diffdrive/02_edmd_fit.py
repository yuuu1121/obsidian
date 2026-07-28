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
# 01번이 저장한 파일을 읽습니다. npz는 여러 배열을 한 파일에 담는 numpy 포맷.
d = np.load("data_diffdrive.npz")
X, Y, U = d["X"], d["Y"], d["U"]      # (3,M), (3,M), (2,M)
dt = float(d["dt"])                   # npz는 스칼라도 0차원 배열로 저장하므로 float() 필요
M = X.shape[1]                        # 데이터 개수 = 열 개수
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

# --- 재구성 오차: 디코더 C가 제대로 작동하는지 확인 --------------------------
# C @ psi(x) 가 다시 x를 주는지 봅니다. 딕셔너리가 상태 자신을 포함하므로
# (full-state observability) 이 값은 거의 0 (기계 정밀도 ~1e-15) 이어야 합니다.
# 만약 크게 나온다면 딕셔너리에 상태가 안 들어갔거나 규약이 어긋난 것입니다.
recon = np.linalg.norm(X - C.dot(PhiX)) / np.sqrt(M)   # RMS = Frobenius norm / sqrt(M)
print(f"\n재구성 RMS 오차: {recon:.3e}  (거의 0이어야 정상)")

# --- 예측 성능 검증 ----------------------------------------------------------
# 학습에 쓴 데이터에서 무작위로 구간을 뽑아, 그 구간의 입력 시퀀스를 주고
# 모델이 얼마나 잘 따라가는지 봅니다.
rng = np.random.default_rng(1)        # 검증용 난수 — 학습 데이터의 seed(0)와 분리
n_tests, horizon = 6, 30              # 테스트 6개, 각 30스텝(= 1.5초 @ dt=0.05)

fig, axes = plt.subplots(2, 3, figsize=(13, 6))
final_errors = []

for i, ax in enumerate(axes.ravel()):  # ravel(): 2x3 격자를 1차원으로 펴서 순회
    # M - horizon 까지만 뽑아야 구간이 데이터 끝을 넘지 않습니다
    idx = rng.integers(0, M - horizon)

    # ⚠️ 주의: 데이터가 200개 궤적을 이어붙인 것이라, 뽑은 구간이 궤적
    #    경계를 걸칠 수 있습니다. 그러면 중간에 상태가 점프해 오차가 커
    #    보입니다. 교육용이라 그대로 뒀지만, 엄밀히 하려면 궤적 인덱스를
    #    따로 관리해서 경계를 피해야 합니다.
    xs, preds = rollout(X[:, idx], U[:, idx:idx + horizon],
                        K_psi, K_u, C, lifting, dt=dt)

    # 각 시점의 오차 크기 = 3차원 벡터의 노름. axis=0 이면 열별로 계산됩니다.
    err = np.linalg.norm(xs - preds, axis=0)   # (horizon+1,)
    final_errors.append(err[-1])               # 마지막 스텝 오차만 따로 모음

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
