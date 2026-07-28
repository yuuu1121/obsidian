"""
[4단계] 딕셔너리 · 모델 구조 비교 실험
        개념 노트 [[Observable Function]], [[Koopman with Control Input]],
                  [[Koopman-Invariant Subspace]], [[EDMD]] 7번

실행:  python 04_dictionary_study.py   (01_collect_data.py 를 먼저 실행)

이 실험이 보여주는 것
---------------------
차동구동 로봇의 동역학을 다시 봅시다.

    x_{t+1} = x_t + v cos(theta) dt
    y_{t+1} = y_t + v sin(theta) dt
    theta_{t+1} = theta_t + omega dt

비선형항이 v*cos(theta), v*sin(theta) — 즉 **입력과 상태함수의 곱** 입니다.
여기서 결정적인 질문이 나옵니다.

    "cos(theta)를 딕셔너리에 넣기만 하면 정확해질까?"

답은 **아니오** 입니다. input-affine 모델

    psi(x+) = K psi(x) + B u

는 구조상 psi 와 u 의 **곱을 표현할 수 없습니다**. cos(theta)를 아무리
넣어도 그것에 v를 곱해줄 자리가 모델에 없습니다.

필요한 것은 bilinear 모델입니다.

    psi(x+) = K psi(x) + B u + sum_j u_j * B_j psi(x)
                               ^^^^^^^^^^^^^^^^^^^^^^ 이 항이 곱을 표현

이 실험은 (딕셔너리) x (모델 구조) 조합을 전부 비교해서, 둘이 **함께**
맞아야 한다는 것을 보여줍니다.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import pinv

from koopman_lib import Lifting, f_discrete, setup_korean_font

setup_korean_font()      # 그래프 한글 깨짐 방지 (폰트 없으면 자동으로 건너뜀)

# --- 데이터 ------------------------------------------------------------------
d = np.load("data_diffdrive.npz")
X, Y, U, dt = d["X"], d["Y"], d["U"], float(d["dt"])
M = X.shape[1]                                # 데이터 포인트 개수 (열 하나 = 샘플 하나)


# --- 두 가지 모델 구조 --------------------------------------------------------
# fit_affine 과 fit_bilinear 는 겉보기엔 거의 같은 코드(둘 다 pinv 최소자승 한 번)
# 지만, 회귀 행렬 Z에 어떤 블록을 쌓느냐가 이 스크립트 전체의 핵심 차이입니다.
# Z가 커질수록 모델이 표현할 수 있는 psi-u 결합 방식이 늘어난다는 점에 주목하세요.

def fit_affine(lifting, X, Y, U):
    """Input-affine:  psi(x+) = K psi(x) + B u

    [K  B] = Psi(Y) @ pinv([Psi(X); U])

    Z에는 psi(x)와 u가 각자 독립된 블록으로만 들어갑니다. 즉 K가 곱해지는
    대상이 'psi(x) 또는 u' 이지 'psi(x)와 u의 곱'이 아닙니다. 그래서 아무리
    딕셔너리에 cos(theta)를 넣어도 v*cos(theta) 같은 항은 이 구조로 표현이
    안 됩니다 (koopman_lib.f_continuous 참고).
    """
    PhiX = lifting.lift_matrix(X)                 # (N_psi, M)
    PhiY = lifting.lift_matrix(Y)                 # (N_psi, M)
    Z = np.vstack([PhiX, U])                      # (N_psi + m, M)  psi와 u를 그냥 쌓기만 함
    K = PhiY.dot(pinv(Z))                         # (N_psi, N_psi + m)
    return K, Z, PhiX


def fit_bilinear(lifting, X, Y, U):
    """Bilinear:  psi(x+) = K psi(x) + B u + sum_j u_j B_j psi(x)

    회귀 행렬에 u_j * psi(x) 블록을 추가하는 것만으로 구현됩니다.
    여전히 psi 와 u 에 대해 **선형 최소자승**이므로 닫힌 형태 해가 유지됩니다.
    (단, 제어 단계에서는 u 에 대해 비선형이라 MPC가 비볼록이 됩니다
     -> [[Koopman MPC]] 3번의 트레이드오프)
    """
    PhiX = lifting.lift_matrix(X)                 # (N_psi, M)
    PhiY = lifting.lift_matrix(Y)                 # (N_psi, M)
    # blocks[-1]이 fit_affine과의 차이. U[j:j+1,:] 는 (1, M) 인 j번째 입력
    # 채널이고, 그것을 PhiX 전체 (N_psi, M) 에 브로드캐스트 곱하면 각 열에서
    # u_j(t) * psi(x_t) 라는 '입력과 상태함수의 곱'이 만들어집니다. K가 이
    # 블록에 곱해지는 부분이 바로 위 docstring의 sum_j u_j B_j psi(x) 항이며,
    # v*cos(theta) 같은 곱셈 비선형성을 표현할 자리가 여기서 생깁니다.
    blocks = [PhiX, U] + [U[j:j + 1, :] * PhiX for j in range(U.shape[0])]
    Z = np.vstack(blocks)                         # (N_psi + m + m*N_psi, M)
    K = PhiY.dot(pinv(Z))                         # (N_psi, N_psi + m + m*N_psi)
    return K, Z, PhiX


def evaluate(lifting, fitter):
    """1-step 예측 오차를 원 상태공간에서 측정합니다.

    흐름: (1) fitter로 K, Z, PhiX를 얻고 -> (2) X -> PhiX 관계로부터 디코더
    C를 최소자승으로 구하고 -> (3) K@Z 로 다음 스텝의 리프팅 상태를 예측한
    뒤 C로 원 상태공간에 되돌리고 -> (4) 실제 Y와 비교해 RMS를 냅니다.
    fit_affine/fit_bilinear 어느 쪽이 오든 동일한 절차로 공정하게 비교됩니다.
    """
    K, Z, PhiX = fitter(lifting, X, Y, U)
    C = X.dot(pinv(PhiX))                       # 디코더, (3, N_psi)
    pred = C.dot(K.dot(Z))                      # (3, M)  예측된 다음 상태
    rms = np.linalg.norm(Y - pred) / np.sqrt(M)
    return rms, K.shape


# --- 비교할 딕셔너리 ----------------------------------------------------------
# 다항식 차수/교차항만 올린 것(poly1~poly3)과, 삼각함수를 넣은 것(+ trig)을
# 나란히 두어 "차원을 키우는 것"과 "맞는 함수를 넣는 것"을 구분해서 봅니다.
dicts = [
    ("poly1",                 Lifting(poly_order=1, use_trig=False, cross_terms=False)),
    ("poly2",                 Lifting(poly_order=2, use_trig=False, cross_terms=True)),
    ("poly3",                 Lifting(poly_order=3, use_trig=False, cross_terms=True)),
    ("poly1 + trig",          Lifting(poly_order=1, use_trig=True,  cross_terms=False)),
    ("poly2 + trig",          Lifting(poly_order=2, use_trig=True,  cross_terms=True)),
]

print("=" * 74)
print(f"{'딕셔너리':<16}{'차원':>6}{'input-affine':>18}{'bilinear':>18}")
print("-" * 74)

rows = []
for name, lf in dicts:
    e_aff, _ = evaluate(lf, fit_affine)
    e_bil, _ = evaluate(lf, fit_bilinear)
    rows.append((name, lf.dim(), e_aff, e_bil, "trig" in name))
    print(f"{name:<16}{lf.dim():>6}{e_aff:>18.3e}{e_bil:>18.3e}")

print("=" * 74)

# --- 핵심 관찰 ---------------------------------------------------------------
# rows의 각 튜플은 (이름, 차원, affine 오차, bilinear 오차, trig 포함 여부).
# best는 bilinear 오차(r[3]) 기준 최솟값 -> 아래 관찰 2/3에서 근거로 씁니다.
best = min(rows, key=lambda r: r[3])
print(f"""
관찰 1 — input-affine 열을 보세요
    차원을 6 -> 25 로 4배 키워도 오차가 거의 그대로입니다.
    삼각함수를 넣어도 마찬가지입니다.
    => 모델 구조가 틀렸으면 딕셔너리를 아무리 손봐도 소용없습니다.

관찰 2 — bilinear 열에서 'trig' 행을 보세요
    '{best[0]}' + bilinear 조합의 오차가 {best[3]:.2e} 입니다.
    이것은 기계 정밀도(~1e-15) 수준, 즉 **정확한(exact) 모델**입니다.
    딱 {best[1]}차원으로 비선형 시스템이 완벽히 선형화되었습니다.

관찰 3 — 두 관찰을 합치면
    딕셔너리(무엇을 담는가)와 모델 구조(어떻게 결합하는가)가
    **함께** 맞아야 합니다. 어느 한쪽만으로는 부족합니다.

    이 시스템의 비선형성 v*cos(theta) 를 표현하려면
      - cos(theta) 가 딕셔너리에 있어야 하고        <- [[Observable Function]]
      - u 와 psi 의 곱을 담을 자리가 모델에 있어야  <- [[Koopman with Control Input]]
    합니다. 둘 다 있을 때 span(psi) 가 Koopman-불변이 되고,
    그때 예측이 근사가 아니라 정확해집니다.        <- [[Koopman-Invariant Subspace]]
""")

# --- 시각화 -----------------------------------------------------------------
# 색상/마커 규칙 (두 축 모두 동일):
#   빨강(tab:red)   = input-affine 모델
#   초록(tab:green) = bilinear 모델
#   원(o)  = 딕셔너리에 trig(cos/sin) 포함  ("poly1 + trig", "poly2 + trig")
#   사각형(s) = trig 미포함
# ax1은 딕셔너리별 막대 비교, ax2는 차원 대 오차의 산점도 — 둘 다 로그축이라
# machine-precision(1e-14 수준)과 그 밖의 값들 사이 몇 자릿수 차이가 한눈에 보입니다.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

names = [r[0] for r in rows]
idx = np.arange(len(rows))
w = 0.38

ax1.bar(idx - w/2, [r[2] for r in rows], w, label="input-affine", color="tab:red")
ax1.bar(idx + w/2, [r[3] for r in rows], w, label="bilinear", color="tab:green")
ax1.set_yscale("log")
ax1.set_xticks(idx); ax1.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
ax1.set_ylabel("1-step RMS 오차")
ax1.set_title("딕셔너리 크기가 아니라 모델 구조가 결정합니다")
ax1.legend(); ax1.grid(alpha=.3, axis="y")
ax1.axhline(1e-14, ls=":", c="k", lw=1)
ax1.text(len(rows)-0.5, 2e-14, "기계 정밀도", fontsize=7, ha="right")

# r[4] (trig 포함 여부)로 마커 모양만 바꾸고, 색은 항상 affine=빨강/bilinear=초록
# 고정 -> "어떤 딕셔너리인가(마커)"와 "어떤 모델 구조인가(색)"를 동시에 읽을 수 있습니다.
for r in rows:
    mk = "o" if r[4] else "s"
    ax2.scatter(r[1], r[2], marker=mk, s=90, c="tab:red", zorder=5)
    ax2.scatter(r[1], r[3], marker=mk, s=90, c="tab:green", zorder=5)
    ax2.annotate(r[0], (r[1], r[3]), fontsize=7, xytext=(4, -10),
                 textcoords="offset points")
ax2.set_yscale("log")
ax2.set_xlabel("딕셔너리 차원 $N_\\psi$")
ax2.set_ylabel("1-step RMS 오차")
ax2.set_title("빨강 = input-affine, 초록 = bilinear\n(원 = 삼각함수 포함, 사각 = 미포함)")
ax2.grid(alpha=.3)

fig.suptitle("Step 4: 딕셔너리와 모델 구조가 '함께' 비선형성에 맞아야 합니다",
             fontsize=12)
fig.tight_layout()
plt.show()

# --- 직접 해보기 -------------------------------------------------------------
print("""
직접 해보기
-----------
1. fit_bilinear에서 blocks의 마지막 항(u_j * PhiX)을 빼보세요.
   fit_affine과 같아지면서 정확도가 무너집니다.

2. 'poly1 + trig' + bilinear 가 정확한 모델이라면, 그 딕셔너리가
   span하는 부분공간은 Koopman-불변입니다. 왜 그런지
   [[Observable Function]] 2번의 '손으로 푸는 예제'와 비교해보세요.

3. 그런데 이 정확한 bilinear 모델을 MPC에 쓰면 문제가 생깁니다.
   u 에 대해 비선형이라 최적화가 **비볼록**이 됩니다.
   -> 정확도(bilinear)와 볼록성(affine) 사이의 트레이드오프.
      이것이 [[Koopman MPC]] 3번이 말하는 바이고,
      03_mpc_control.py 가 굳이 affine 모델을 쓰는 이유입니다.
""")
