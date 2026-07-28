"""
Koopman 튜토리얼 공용 모듈 — 차동구동 로봇(differential-drive robot)

논문: Shi et al., "Koopman Operators in Robot Learning", IEEE T-RO 2026
원본: https://github.com/sunnyshi0310/KoopmanRobo

원본 demo.ipynb의 코드를 재사용 가능한 형태로 정리한 것입니다.
각 함수는 개념 노트의 어느 단계에 대응하는지 docstring에 표기했습니다.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import pinv, eig, solve_discrete_are
from scipy import linalg
import time

# Set random seed for reproducibility
np.random.seed(0)

# 데이터 수집에 쓰는 샘플링 주기 [s]
# 주의: 학습과 제어에서 동일한 dt를 써야 합니다 (03_mpc_control.py 상단 주석 참고)
DT = 0.05


# =============================================================================
# 1. 시스템 모델 (ground truth) — 학습에는 쓰지 않고 데이터 생성/검증에만 사용
# =============================================================================

def f_continuous(state, u):
    """차동구동 로봇의 연속시간 운동학.

    state = [x, y, theta]  (평면상 위치와 자세)
    u     = [v, omega]     (선속도, 각속도)

    비선형성의 출처는 cos(theta), sin(theta) 입니다.
    """
    x, y, th = state
    v, w = u
    return np.array([v * np.cos(th), v * np.sin(th), w])


def f_discrete(state, u, dt=DT):
    """오일러 적분으로 한 스텝 전파. 이것이 개념 노트의 T(x)에 해당합니다."""
    return state + f_continuous(state, u) * dt


# =============================================================================
# 2. 데이터 수집  →  [[EDMD]] 1번
# =============================================================================

def collect_data(n_traj=200, t_per=50, dt=DT, seed=0):
    """짧은 궤적 여러 개에서 (x_t, x_{t+1}, u_t) 삼중항을 수집합니다.

    핵심은 persistent excitation — 입력이 충분히 다양해야 모델링하려는
    동역학이 전부 여기(excite)됩니다. 여기서는 균등난수에 가끔 큰 펄스를
    섞어 대역을 넓힙니다.

    반환: X, Y, U  각각 (3, M), (3, M), (2, M)
          X = 현재 상태들, Y = 한 스텝 뒤 상태들, U = 그때 준 입력
    """
    rng = np.random.default_rng(seed)

    x0_range = np.array([[-2.0, 2.0], [-2.0, 2.0], [-np.pi, np.pi]])
    u_v_range = (-0.6, 0.6)
    u_w_range = (-2.0, 2.0)

    X, Y, U = [], [], []
    for _ in range(n_traj):
        state = np.array([rng.uniform(*x0_range[0]),
                          rng.uniform(*x0_range[1]),
                          rng.uniform(*x0_range[2])])
        for _ in range(t_per):
            # 5% 확률로 큰 펄스 — 저주파에만 치우치지 않게 함
            if rng.random() < 0.05:
                u = np.array([rng.uniform(-1.2, 1.2), rng.uniform(-4.0, 4.0)])
            else:
                u = np.array([rng.uniform(*u_v_range) + 0.05 * rng.standard_normal(),
                              rng.uniform(*u_w_range) + 0.2 * rng.standard_normal()])
            nxt = f_discrete(state, u, dt=dt)
            X.append(state.copy())
            Y.append(nxt.copy())
            U.append(u.copy())
            state = nxt

    return np.array(X).T, np.array(Y).T, np.array(U).T


# =============================================================================
# 3. 리프팅 딕셔너리  →  [[Observable Function]]
# =============================================================================

class Lifting:
    """관측함수(딕셔너리) psi(x).

    구성 요소를 켜고 끌 수 있게 되어 있어, 딕셔너리 선택이 성능에
    어떤 영향을 주는지 직접 실험해볼 수 있습니다 ([[Observable Function]] 참고).

    Parameters
    ----------
    poly_order : 다항식 최고차수
    use_trig   : cos(theta), sin(theta) 포함 여부.
                 이 시스템의 비선형성이 정확히 삼각함수에서 오므로
                 True로 두면 예측이 크게 좋아집니다 — 물리 정보 기반 설계의 예.
    cross_terms: x_i * x_j 교차항 포함 여부
    include_u_in_phi : 입력을 딕셔너리에 넣을지 (joint lifting 방식)
    """

    def __init__(self, n_states=3, n_inputs=2, poly_order=2,
                 use_trig=True, include_u_in_phi=False, cross_terms=False):
        self.n = n_states
        self.m = n_inputs
        self.poly_order = poly_order
        self.use_trig = use_trig
        self.include_u_in_phi = include_u_in_phi
        self.cross_terms = cross_terms
        self.poly_terms = self._poly_term_indices(self.n, self.poly_order)

    def _poly_term_indices(self, n, order):
        """차수 order 이하 단항식의 지수 튜플 목록 (상수항 제외)."""
        terms = []
        for deg in range(1, order + 1):
            def rec(prefix, k, remain):
                if k == 0:
                    if remain == 0:
                        terms.append(tuple(prefix))
                    return
                for val in range(remain + 1):
                    rec(prefix + [val], k - 1, remain - val)
            rec([], n, deg)
        return terms

    def phi(self, x, u=None):
        """상태 x를 고차원으로 리프팅합니다. 반환 shape = (N_psi,)"""
        feats = list(x)                                   # 항등항 (full-state observability)

        for exps in self.poly_terms:                      # 다항식 항
            val = 1.0
            for xi, e in zip(x, exps):
                if e != 0:
                    val *= xi ** e
            feats.append(val)

        if self.use_trig and self.n >= 3:                 # 삼각함수 항 (theta는 3번째 상태)
            feats.append(np.cos(x[2]))
            feats.append(np.sin(x[2]))

        if self.cross_terms:                              # 교차항
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    feats.append(x[i] * x[j])

        if self.include_u_in_phi and u is not None:       # 입력 결합 리프팅
            feats.extend(list(u))
            for ui in u:
                feats.append(ui)
                feats.append(ui ** 2)

        return np.array(feats)

    def dim(self):
        z = self.phi(np.zeros(self.n),
                     np.zeros(self.m) if self.include_u_in_phi else None)
        return z.size

    def lift_matrix(self, X):
        """데이터 행렬 전체를 리프팅합니다. (3, M) -> (N_psi, M)"""
        return np.vstack([self.phi(X[:, i]) for i in range(X.shape[1])]).T


# =============================================================================
# 4. EDMD  →  [[EDMD]] 3~4번, [[Koopman with Control Input]] 3번
# =============================================================================

def edmd_with_input(X, Y, U, lifting):
    """입력이 있는 EDMD. input-affine 모델을 최소자승으로 한 번에 풉니다.

        psi(x_{t+1}) ~= K_psi @ psi(x_t) + K_u @ u_t

    리프팅 상태와 입력을 세로로 쌓아 하나의 최소자승으로 만듭니다.

        [K_psi  K_u] = Psi(Y) @ pinv([Psi(X); U])

    pinv는 의사역행렬입니다 → [[Pseudo-inverse]]
    반복 최적화가 없다는 점(SVD 한 번)이 Koopman의 실시간성 근거입니다.

    반환: K_psi (N_psi, N_psi), K_u (N_psi, 2), PhiX (N_psi, M)
    """
    PhiX = lifting.lift_matrix(X)
    PhiY = lifting.lift_matrix(Y)

    Z = np.vstack([PhiX, U])              # (N_psi + m, M)
    K = PhiY.dot(pinv(Z))                 # 닫힌 형태 해 — 여기가 핵심

    n_phi = PhiX.shape[0]
    return K[:, :n_phi], K[:, n_phi:], PhiX


def fit_decoder(X, PhiX):
    """리프팅 상태 -> 원 상태로 되돌리는 선형 디코더 C.

        x ~= C @ psi(x)

    딕셔너리가 상태 자신을 포함하므로(full-state observability) 원래는
    psi의 앞부분만 잘라내면 됩니다. 여기서는 일반성을 위해 최소자승으로 구합니다.
    """
    return X.dot(pinv(PhiX))


# =============================================================================
# 5. 예측 (rollout)  →  [[EDMD]] 5번
# =============================================================================

def rollout(x0, u_seq, K_psi, K_u, C, lifting, dt=DT):
    """학습된 Koopman 모델로 다단계 예측하고 실제 궤적과 비교합니다.

    주의: 매 스텝 psi를 실제 예측 상태에서 다시 계산하는 방식이 아니라,
    원본 데모와 동일하게 '한 스텝 예측'을 반복합니다. 순수한 리프팅 공간
    rollout(z_{t+1} = K z_t)을 보고 싶다면 04_dictionary_study.py 참고.

    반환: xs_true (3, T+1), xs_pred (3, T+1)
    """
    steps = u_seq.shape[1]
    xs_true = [x0.copy()]
    xs_pred = [x0.copy()]
    x_true = x0.copy()

    for t in range(steps):
        u = u_seq[:, t]
        phi_next = K_psi.dot(lifting.phi(x_true)) + K_u.dot(u)
        xs_pred.append(C.dot(phi_next))
        x_true = f_discrete(x_true, u, dt=dt)
        xs_true.append(x_true.copy())

    return np.array(xs_true).T, np.array(xs_pred).T


def rollout_lifted(x0, u_seq, K_psi, K_u, C):
    """순수 리프팅 공간 rollout — 실제 상태를 전혀 참조하지 않습니다.

        z_{t+1} = K_psi z_t + K_u u_t,     x_t = C z_t

    이것이 진짜 '모델만으로 미래를 예측'하는 것이며, 근사 오차가
    누적되는 모습을 관찰할 수 있습니다 ([[EDMD]] 6번의 투영 오차 누적).
    """
    raise NotImplementedError(
        "04_dictionary_study.py 에서 구현합니다 — 직접 채워보세요"
    )
