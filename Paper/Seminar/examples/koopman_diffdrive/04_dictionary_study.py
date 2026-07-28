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

from koopman_lib import Lifting, f_discrete

# --- 데이터 ------------------------------------------------------------------
d = np.load("data_diffdrive.npz")
X, Y, U, dt = d["X"], d["Y"], d["U"], float(d["dt"])
M = X.shape[1]


# --- 두 가지 모델 구조 --------------------------------------------------------

def fit_affine(lifting, X, Y, U):
    """Input-affine:  psi(x+) = K psi(x) + B u

    [K  B] = Psi(Y) @ pinv([Psi(X); U])
    """
    PhiX = lifting.lift_matrix(X)
    PhiY = lifting.lift_matrix(Y)
    Z = np.vstack([PhiX, U])
    K = PhiY.dot(pinv(Z))
    return K, Z, PhiX


def fit_bilinear(lifting, X, Y, U):
    """Bilinear:  psi(x+) = K psi(x) + B u + sum_j u_j B_j psi(x)

    회귀 행렬에 u_j * psi(x) 블록을 추가하는 것만으로 구현됩니다.
    여전히 psi 와 u 에 대해 **선형 최소자승**이므로 닫힌 형태 해가 유지됩니다.
    (단, 제어 단계에서는 u 에 대해 비선형이라 MPC가 비볼록이 됩니다
     -> [[Koopman MPC]] 3번의 트레이드오프)
    """
    PhiX = lifting.lift_matrix(X)
    PhiY = lifting.lift_matrix(Y)
    blocks = [PhiX, U] + [U[j:j + 1, :] * PhiX for j in range(U.shape[0])]
    Z = np.vstack(blocks)
    K = PhiY.dot(pinv(Z))
    return K, Z, PhiX


def evaluate(lifting, fitter):
    """1-step 예측 오차를 원 상태공간에서 측정합니다."""
    K, Z, PhiX = fitter(lifting, X, Y, U)
    C = X.dot(pinv(PhiX))                       # 디코더
    pred = C.dot(K.dot(Z))                      # 예측된 다음 상태
    rms = np.linalg.norm(Y - pred) / np.sqrt(M)
    return rms, K.shape


# --- 비교할 딕셔너리 ----------------------------------------------------------
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
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

names = [r[0] for r in rows]
idx = np.arange(len(rows))
w = 0.38

ax1.bar(idx - w/2, [r[2] for r in rows], w, label="input-affine", color="tab:red")
ax1.bar(idx + w/2, [r[3] for r in rows], w, label="bilinear", color="tab:green")
ax1.set_yscale("log")
ax1.set_xticks(idx); ax1.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
ax1.set_ylabel("1-step RMS error")
ax1.set_title("Model structure decides, not dictionary size")
ax1.legend(); ax1.grid(alpha=.3, axis="y")
ax1.axhline(1e-14, ls=":", c="k", lw=1)
ax1.text(len(rows)-0.5, 2e-14, "machine precision", fontsize=7, ha="right")

for r in rows:
    mk = "o" if r[4] else "s"
    ax2.scatter(r[1], r[2], marker=mk, s=90, c="tab:red", zorder=5)
    ax2.scatter(r[1], r[3], marker=mk, s=90, c="tab:green", zorder=5)
    ax2.annotate(r[0], (r[1], r[3]), fontsize=7, xytext=(4, -10),
                 textcoords="offset points")
ax2.set_yscale("log")
ax2.set_xlabel("dictionary dimension $N_\\psi$")
ax2.set_ylabel("1-step RMS error")
ax2.set_title("red = input-affine, green = bilinear\n(circle = has trig, square = no trig)")
ax2.grid(alpha=.3)

fig.suptitle("Step 4: dictionary AND model structure must match the nonlinearity",
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
