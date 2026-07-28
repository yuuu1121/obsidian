"""
[1단계] 데이터 수집 — 개념 노트 [[EDMD]] 1번에 대응

실행:  python 01_collect_data.py

무엇을 보는가
-------------
Koopman은 (x_t, x_{t+1}, u_t) 삼중항만 있으면 됩니다. 하나의 긴 궤적일
필요가 없다는 점이 중요합니다 — 짧은 궤적 여러 개를 이어붙여도 됩니다.

핵심 개념: persistent excitation
  입력이 충분히 다양하지 않으면, 데이터가 아무리 많아도 그 입력이
  건드리지 않은 동역학은 학습되지 않습니다. 히스토그램에서 입력이
  넓게 퍼져 있는지 확인하세요.
"""

import numpy as np
import matplotlib.pyplot as plt

from koopman_lib import collect_data, DT

# --- 데이터 수집 -------------------------------------------------------------
X, Y, U = collect_data(n_traj=200, t_per=50, dt=DT, seed=0)
M = X.shape[1]

print(f"수집 완료: {M} 개의 데이터 쌍 (200 궤적 x 50 스텝)")
print(f"  X (현재 상태) shape: {X.shape}   <- (상태차원 3, 데이터수 M)")
print(f"  Y (다음 상태) shape: {Y.shape}")
print(f"  U (입력)      shape: {U.shape}   <- (입력차원 2, 데이터수 M)")
print()
print("상태 범위:")
for i, name in enumerate(["x [m]", "y [m]", "theta [rad]"]):
    print(f"  {name:12s}  [{X[i].min():+.2f}, {X[i].max():+.2f}]")
print("입력 범위:")
for i, name in enumerate(["v [m/s]", "omega [rad/s]"]):
    print(f"  {name:12s}  [{U[i].min():+.2f}, {U[i].max():+.2f}]")

# --- 시각화 -----------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(13, 6))

for i, (name, ax) in enumerate(zip(["x position", "y position", "theta"], axes[0])):
    ax.hist(X[i], bins=40, color="steelblue")
    ax.set_title(f"state: {name}")

for i, (name, ax) in enumerate(zip(["v (linear)", "omega (angular)"], axes[1])):
    ax.hist(U[i], bins=40, color="indianred")
    ax.set_title(f"input: {name}")

# 수집한 궤적 일부를 xy 평면에 표시
ax = axes[1, 2]
for k in range(0, 10 * 50, 50):
    ax.plot(X[0, k:k + 50], X[1, k:k + 50], lw=0.8)
ax.set_title("sample trajectories (10 of 200)")
ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
ax.axis("equal")

fig.suptitle("Step 1: 수집한 데이터의 분포 — 넓게 퍼져 있어야 좋습니다", fontsize=12)
fig.tight_layout()
plt.show()

# --- 저장 -------------------------------------------------------------------
np.savez("data_diffdrive.npz", X=X, Y=Y, U=U, dt=DT)
print("\n저장: data_diffdrive.npz  (다음 단계 02_edmd_fit.py 에서 사용)")

# --- 직접 해보기 -------------------------------------------------------------
print("""
직접 해보기
-----------
1. n_traj를 20으로 줄여보세요. 히스토그램이 얼마나 성겨지나요?
   그 데이터로 02번을 돌리면 예측 오차가 어떻게 되나요?
2. collect_data의 u_w_range를 (-0.2, 0.2)로 좁혀보세요.
   각속도를 거의 안 준 데이터로 학습하면 회전 동역학이 학습될까요?
   -> 이것이 persistent excitation 이 필요한 이유입니다.
""")
