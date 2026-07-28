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
# 0. 그래프 한글 폰트 설정 (선택적)
# =============================================================================

def setup_korean_font(verbose=False):
    """matplotlib 그래프에서 한글이 깨지지 않도록 폰트를 설정합니다.

    matplotlib 기본 폰트(DejaVu Sans)에는 한글 글리프가 없어서, 한글 제목을
    쓰면 글자 대신 두부(□)가 찍힙니다. 이 함수는 시스템에 설치된 한글 폰트를
    찾아 지정합니다.

    OS마다 있는 폰트가 다르므로 후보를 순서대로 시도하고,
    **하나도 없으면 조용히 넘어갑니다** (그래프는 그대로 그려지고 한글만 깨짐).
    즉 이 함수 때문에 스크립트가 죽는 일은 없습니다.

    Returns
    -------
    str or None : 실제로 적용된 폰트 이름. 못 찾았으면 None.
    """
    # OS별 대표 한글 폰트 — 앞에서부터 시도합니다
    candidates = [
        "Malgun Gothic",    # Windows 기본
        "AppleGothic",      # macOS 기본
        "NanumGothic",      # 나눔고딕 (Linux에서 흔히 설치)
        "NanumBarunGothic",
        "Noto Sans CJK KR", # Linux 배포판 기본인 경우가 많음
        "Gulim", "Dotum",   # 구형 Windows 폰트
    ]

    try:
        import matplotlib.font_manager as fm
        installed = {f.name for f in fm.fontManager.ttflist}

        for name in candidates:
            if name in installed:
                plt.rcParams["font.family"] = name
                # ⚠️ 한글 폰트로 바꾸면 축의 음수 부호(−2, −1 ...)가 깨지는
                #    별개의 문제가 생깁니다. 유니코드 마이너스(U+2212) 대신
                #    ASCII 하이픈을 쓰도록 해서 막습니다.
                plt.rcParams["axes.unicode_minus"] = False
                if verbose:
                    print(f"[font] 한글 폰트 적용: {name}")
                return name

        if verbose:
            # 콘솔 인코딩(cp949 등)에서 깨지지 않도록 ASCII 문자만 씁니다
            print("[font] No Korean font found - titles may show as boxes.")
            print("       Linux: sudo apt install fonts-nanum")
            print("       then remove ~/.cache/matplotlib and rerun")

    except Exception as e:
        # 폰트 설정이 실패해도 본 작업(학습·제어)에는 아무 지장이 없으므로
        # 예외를 삼키고 계속 진행합니다.
        if verbose:
            print(f"[font] 폰트 설정 건너뜀: {e}")

    return None


# =============================================================================
# 1. 시스템 모델 (ground truth) — 학습에는 쓰지 않고 데이터 생성/검증에만 사용
# =============================================================================

def f_continuous(state, u):
    """차동구동 로봇의 연속시간 운동학.

        xdot     = v * cos(theta)
        ydot     = v * sin(theta)
        thetadot = omega

    state = [x, y, theta]  (평면상 위치 [m, m]와 자세 [rad])
    u     = [v, omega]     (선속도 [m/s], 각속도 [rad/s])

    ---------------------------------------------------------------
    이 함수가 이 예제 전체의 '비선형성의 출처'입니다.

    주목할 점: 비선형항이 v*cos(theta) 즉 **입력 x 상태함수의 곱** 입니다.
    단순히 cos(theta)만 있는 게 아니라 v가 곱해져 있다는 것이 핵심이며,
    이 구조 때문에 input-affine 모델(K@psi + B@u)로는 표현할 수 없습니다.
    자세한 것은 04_dictionary_study.py 참고.
    ---------------------------------------------------------------
    """
    x, y, th = state          # th = theta (자세각)
    v, w = u                  # w = omega (각속도)
    return np.array([v * np.cos(th),      # x 방향 속도
                     v * np.sin(th),      # y 방향 속도
                     w])                  # 자세 변화율


def f_discrete(state, u, dt=DT):
    """오일러 적분으로 한 스텝 전파. 개념 노트의 T(x)에 해당합니다.

        x_{t+1} = x_t + f(x_t, u_t) * dt

    이 함수는 '실제 로봇' 역할입니다. 데이터 생성과 검증에만 쓰이고,
    학습된 Koopman 모델은 이 함수를 전혀 모릅니다 (model-free).

    주의: 오일러 적분은 가장 단순한 방법이라 dt가 크면 오차가 큽니다.
    여기서는 dt=0.05로 충분히 작아 문제없지만, 실제 시스템에서는
    RK4 같은 고차 적분기를 쓰는 것이 보통입니다.
    """
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
    # default_rng는 전역 np.random과 달리 '독립된 난수 스트림'을 만듭니다.
    # 04번처럼 여러 실험을 반복할 때, 호출 순서가 바뀌어도 결과가 흔들리지
    # 않게 하려면 이 방식이 필요합니다.
    rng = np.random.default_rng(seed)

    # 초기 상태를 뽑을 범위 — 로봇의 '동작 영역(operational envelope)'
    # 전체를 덮도록 넓게 잡습니다. 좁으면 그 밖에서는 모델이 엉망이 됩니다.
    x0_range = np.array([[-2.0, 2.0],        # x  [m]
                         [-2.0, 2.0],        # y  [m]
                         [-np.pi, np.pi]])   # theta [rad] — 한 바퀴 전체

    u_v_range = (-0.6, 0.6)     # 평상시 선속도 [m/s]
    u_w_range = (-2.0, 2.0)     # 평상시 각속도 [rad/s]

    X, Y, U = [], [], []        # 파이썬 리스트로 모은 뒤 마지막에 배열로 변환
                                # (매 스텝 np.append 하면 훨씬 느립니다)

    for _ in range(n_traj):
        # 궤적마다 새 초기 상태에서 출발 — 한 궤적이 상태공간의 일부만
        # 훑기 때문에, 짧은 궤적 여러 개가 긴 궤적 하나보다 커버리지가 좋습니다.
        state = np.array([rng.uniform(*x0_range[0]),
                          rng.uniform(*x0_range[1]),
                          rng.uniform(*x0_range[2])])

        for _ in range(t_per):
            # --- 입력 생성: persistent excitation 을 만드는 부분 ---------
            # 균등난수만 쓰면 특정 대역만 자극하게 되므로, 5% 확률로
            # 평상시 범위를 넘는 '큰 펄스'를 섞어 넓은 주파수 성분을 넣습니다.
            if rng.random() < 0.05:
                u = np.array([rng.uniform(-1.2, 1.2),    # 평상시의 2배
                              rng.uniform(-4.0, 4.0)])   # 평상시의 2배
            else:
                # 균등난수 + 작은 가우시안 노이즈
                # (노이즈를 더하는 이유: 균등분포만 쓰면 값이 특정 격자에
                #  몰리는 경향이 생겨 회귀 행렬의 조건수가 나빠질 수 있습니다)
                u = np.array([rng.uniform(*u_v_range) + 0.05 * rng.standard_normal(),
                              rng.uniform(*u_w_range) + 0.2 * rng.standard_normal()])

            # --- 한 스텝 전파해서 (현재, 다음, 입력) 삼중항을 저장 --------
            nxt = f_discrete(state, u, dt=dt)
            X.append(state.copy())      # .copy() 필수! 안 하면 나중에
            Y.append(nxt.copy())        # state가 바뀔 때 리스트 안 값도
            U.append(u.copy())          # 같이 바뀝니다 (참조 공유 버그)
            state = nxt                 # 다음 스텝으로 이어붙이기

    # 리스트 -> 배열, 그리고 전치.
    # np.array(X)는 (M, 3) 이 되므로 .T 로 (3, M) 으로 바꿉니다.
    # 이 예제 전체가 '열 하나 = 데이터 포인트 하나' 규약을 씁니다.
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
        """상태 x를 고차원으로 리프팅합니다.  (3,) -> (N_psi,)

        예: poly_order=1, use_trig=True, cross_terms=False 이면
            psi(x) = [x, y, th,          <- 항등항 3개
                      x, y, th,          <- 1차 다항식 3개 (항등항과 중복)
                      cos(th), sin(th)]  <- 삼각함수 2개
            => N_psi = 8

        (항등항과 1차 다항식이 중복되지만, pinv가 알아서 처리하므로
         결과에는 영향이 없습니다. 원본 데모의 구조를 그대로 유지했습니다.)
        """
        # --- 항등항: 상태 자신을 그대로 포함 ------------------------------
        # 이것이 full-state observability 를 보장합니다. 덕분에 리프팅
        # 상태 z의 앞 3개만 읽으면 원 상태 x를 바로 복원할 수 있습니다.
        feats = list(x)

        # --- 다항식 항: x^a * y^b * th^c  (a+b+c <= poly_order) -----------
        for exps in self.poly_terms:      # exps = 지수 튜플, 예: (1,0,1) -> x*th
            val = 1.0
            for xi, e in zip(x, exps):
                if e != 0:
                    val *= xi ** e
            feats.append(val)

        # --- 삼각함수 항: 이 시스템에서 가장 중요한 부분 -------------------
        # 동역학이 v*cos(th), v*sin(th) 이므로 cos/sin 을 넣어주면
        # 딕셔너리가 '진짜 필요한 함수'를 담게 됩니다 (물리 정보 기반 설계).
        # 단, 이것만으로는 부족하고 bilinear 모델이 함께 필요합니다 -> 04번
        if self.use_trig and self.n >= 3:
            feats.append(np.cos(x[2]))    # x[2] = theta
            feats.append(np.sin(x[2]))

        # --- 교차항: x_i * x_j (i < j) ------------------------------------
        if self.cross_terms:
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    feats.append(x[i] * x[j])

        # --- 입력 결합 리프팅 (joint lifting) -----------------------------
        # 입력을 딕셔너리 안에 넣는 방식. 미래 입력을 안다고 가정해야 해서
        # 이 예제에서는 기본적으로 끕니다 (include_u_in_phi=False).
        if self.include_u_in_phi and u is not None:
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
    # --- 1) 리프팅: 원 상태를 고차원으로 올립니다 --------------------------
    PhiX = lifting.lift_matrix(X)         # (N_psi, M)  현재 상태들을 리프팅
    PhiY = lifting.lift_matrix(Y)         # (N_psi, M)  다음 상태들을 리프팅

    # --- 2) 회귀 행렬 구성 -------------------------------------------------
    # 풀려는 식:  PhiY ~= K_psi @ PhiX + K_u @ U
    # 이것을 하나의 최소자승으로 만들려면 미지수를 옆으로,
    # 데이터를 아래로 쌓습니다:
    #
    #     PhiY  ~=  [K_psi | K_u] @ [ PhiX ]
    #                                [  U   ]
    #               \___________/    \______/
    #                    K              Z
    Z = np.vstack([PhiX, U])              # (N_psi + m, M)   m = 입력 차원(2)

    # --- 3) 닫힌 형태 해 — 여기가 EDMD의 전부입니다 -----------------------
    # 반복 학습(경사하강) 없이 SVD 한 번으로 끝납니다.
    # pinv가 하는 일: 정확한 해가 없으므로(M >> N_psi) 오차를 최소화하는
    #                 K를 직교 사영으로 찾아줍니다.
    K = PhiY.dot(pinv(Z))                 # (N_psi, N_psi + m)

    # --- 4) 합쳐서 푼 K를 다시 두 블록으로 잘라냅니다 ----------------------
    n_phi = PhiX.shape[0]                 # = N_psi
    return (K[:, :n_phi],                 # K_psi: 자율 동역학  (N_psi, N_psi)
            K[:, n_phi:],                 # K_u  : 입력 영향    (N_psi, m)
            PhiX)                         # 디코더 학습에 재사용하려고 반환


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
    xs_true = [x0.copy()]         # 실제 시스템의 궤적 (정답)
    xs_pred = [x0.copy()]         # Koopman 모델의 예측
    x_true = x0.copy()            # 실제 상태를 따로 추적

    for t in range(steps):
        u = u_seq[:, t]

        # --- 예측: 실제 상태를 리프팅해서 한 스텝 밀어봅니다 --------------
        #  psi(x_{t+1}) ~= K_psi @ psi(x_t) + K_u @ u_t
        #  그리고 디코더 C로 원 상태로 되돌립니다.
        #
        #  ⚠️ 여기서 lifting.phi(x_true) 를 쓴다는 점에 주목하세요.
        #     매 스텝 '실제 상태'에서 다시 리프팅하므로, 이것은
        #     엄밀히는 '1-step 예측을 반복'하는 것이지 진짜 다단계
        #     예측이 아닙니다. 오차가 누적되지 않아 실제보다 좋아 보입니다.
        #     진짜 다단계 예측은 04번의 rollout_lifted() 를 보세요.
        phi_next = K_psi.dot(lifting.phi(x_true)) + K_u.dot(u)
        xs_pred.append(C.dot(phi_next))

        # --- 정답: 실제 시스템을 한 스텝 굴립니다 --------------------------
        x_true = f_discrete(x_true, u, dt=dt)
        xs_true.append(x_true.copy())

    # (T+1, 3) -> (3, T+1) 로 전치해서 열 규약을 맞춥니다
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
