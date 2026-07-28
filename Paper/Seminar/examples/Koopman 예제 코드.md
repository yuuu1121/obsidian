---
date: 2026-07-28
status: Code
tags:
  - Code
  - Koopman
  - Tutorial
aliases:
  - Koopman 예제 코드
  - KoopmanRobo
keywords: KoopmanRobo, tutorial, EDMD, MPC, differential drive, example code
related notes: "[[EDMD]], [[Koopman MPC]], [[Observable Function]]"
dg-publish: false
---

# 🧪 Koopman 실행 예제

> [!abstract] 무엇인가
> 논문 저자들이 공개한 공식 튜토리얼 [KoopmanRobo](https://github.com/sunnyshi0310/KoopmanRobo)를 **단계별로 실행 가능한 스크립트**로 재구성한 것입니다. 개념 노트의 각 단계와 1:1로 대응되며, 모든 스크립트는 **실제로 실행 검증했습니다**.

---

## 🔗 원본 저장소

| 항목 | 링크 |
|:---|:---|
| **공식 튜토리얼** | https://github.com/sunnyshi0310/KoopmanRobo |
| Colab에서 바로 실행 | [demo.ipynb 열기](https://colab.research.google.com/github/sunnyshi0310/KoopmanRobo/blob/main/demo.ipynb) |
| 논문 preprint | https://arxiv.org/pdf/2408.04200 |

**저자들이 함께 안내하는 추가 구현**

| 구현 | 링크 | 내용 |
|:---|:---|:---|
| C++ | [koopmanOperatorsInRobotLearning](https://github.com/giorgosmamakoukas/koopmanOperatorsInRobotLearning) | 도립진자 예제 |
| Quadrotor | [active-learning-koopman](https://github.com/i-abr/active-learning-koopman) | 능동학습 Koopman ([[Koopman MPC]] 5–6번) |
| MATLAB | [ACD-EDMD](https://github.com/sunnyshi0310/ACD-EDMD) | 2-DOF 로봇팔, 차동구동 로봇 |
| **PyKoopman** | [dynamicslab/pykoopman](https://github.com/dynamicslab/pykoopman) | 여러 딕셔너리·추정법 비교 (가장 추천) |

---

## 📁 구성

```
examples/
└── koopman_diffdrive/
    ├── koopman_lib.py            공용 모듈 (시스템·데이터·딕셔너리·EDMD)
    ├── 01_collect_data.py        데이터 수집        → [[EDMD]] 1번
    ├── 02_edmd_fit.py            리프팅 + EDMD      → [[EDMD]] 2~5번
    ├── 03_mpc_control.py         Koopman MPC        → [[Koopman MPC]]
    ├── 04_dictionary_study.py    딕셔너리·구조 비교  → [[Observable Function]]
    └── demo_official.ipynb       원본 노트북 (참고용, 수정 없음)
```

---

## 🚀 실행 방법

```bash
cd examples/koopman_diffdrive

pip install numpy scipy matplotlib cvxpy

python 01_collect_data.py      # 데이터 생성 → data_diffdrive.npz
python 02_edmd_fit.py          # 모델 학습   → model_diffdrive.npz
python 04_dictionary_study.py  # 딕셔너리 비교 (03보다 먼저 봐도 좋습니다)
python 03_mpc_control.py       # MPC 제어 (가장 오래 걸림, 약 1분)
```

01 → 02 순서는 지켜야 합니다(파일 의존). 03과 04는 순서 무관합니다.

> [!tip] 검증된 환경
> Python 3.14 / numpy 2.4.4 / scipy 1.17.1 / matplotlib 3.10.9 / cvxpy 1.9.2 에서 전 스크립트 실행 확인했습니다. 원본 README가 명시한 테스트 버전은 numpy 1.26 / matplotlib 3.9.2 / cvxpy 1.6.4 / scipy 1.12 입니다.

---

## 🤖 대상 시스템

차동구동 로봇(differential-drive robot)의 운동학입니다.

$$
\dot{x} = v\cos\theta, \qquad \dot{y} = v\sin\theta, \qquad \dot{\theta} = \omega
$$

- 상태 $x = [x, y, \theta]^\top$ — 평면상 위치 [m, m]와 자세 [rad]
- 입력 $u = [v, \omega]^\top$ — 선속도 [m/s], 각속도 [rad/s]

> [!important] 이 시스템을 고른 것이 왜 좋은 교보재인가
> 비선형항이 $v\cos\theta$, $v\sin\theta$ — **입력과 상태함수의 곱**입니다. 이 구조 때문에 [[Koopman with Control Input|input-affine]] 모델로는 원리적으로 표현할 수 없고, bilinear가 필요합니다. 아래 ⑥에서 이것을 수치로 보여줍니다.

---

# 📐 수식 ↔ 코드 대응

이 절이 이 노트의 본론입니다. 논문의 식이 코드의 어느 줄인지 하나씩 잇습니다.

> [!abstract] 전체 파이프라인 한 눈에
> $$
> \underbrace{x_{t+1}=T_u(x_t,u_t)}_{\text{① 실제 시스템}}
> \ \xrightarrow{\ \text{데이터}\ }\
> \underbrace{X, Y, U}_{\text{② 수집}}
> \ \xrightarrow{\ \psi\ }\
> \underbrace{\Psi(X), \Psi(Y)}_{\text{③ 리프팅}}
> \ \xrightarrow{\ \text{최소자승}\ }\
> \underbrace{K}_{\text{④ EDMD}}
> \ \xrightarrow{\ \text{QP}\ }\
> \underbrace{u^\star}_{\text{⑦ MPC}}
> $$

---

## ① 시스템 모델 — $T$ 를 코드로

**연속시간** (논문 (17)식 꼴)

$$
\dot{x} = G(x, u) = \begin{bmatrix} v\cos\theta \\ v\sin\theta \\ \omega\end{bmatrix}
$$

**이산화** — 오일러 적분으로 논문 (1)식의 $T$ 를 만듭니다.

$$
x_{t+1} = T(x_t, u_t) = x_t + G(x_t, u_t)\,\Delta t
$$

```python
# koopman_lib.py
def f_continuous(state, u):
    x, y, th = state          # th = theta
    v, w = u                  # w = omega
    return np.array([v * np.cos(th),      # xdot
                     v * np.sin(th),      # ydot
                     w])                  # thetadot

def f_discrete(state, u, dt=DT):
    return state + f_continuous(state, u) * dt      # x_{t+1} = x_t + G*dt
```

> [!warning] 이 함수는 학습에 쓰이지 않습니다
> `f_discrete`는 **"실제 로봇" 역할**입니다. 데이터를 만들고 정답과 비교할 때만 쓰이며, 학습된 Koopman 모델은 이 함수의 존재를 모릅니다. 논문이 강조하는 **model-free** 가 이 뜻입니다.

---

## ② 데이터 수집 — 논문 §II-B의 $X, Y$

$$
X = [\,x_1,\ x_2,\ \dots,\ x_M\,] \in \mathbb{R}^{3\times M}
$$
$$
Y = [\,y_1,\ y_2,\ \dots,\ y_M\,], \qquad y_i = T(x_i, u_i)
$$
$$
U = [\,u_1,\ u_2,\ \dots,\ u_M\,] \in \mathbb{R}^{2\times M}
$$

```python
# koopman_lib.py — collect_data()
nxt = f_discrete(state, u, dt=dt)
X.append(state.copy())      # x_i
Y.append(nxt.copy())        # y_i = T(x_i, u_i)
U.append(u.copy())          # u_i
state = nxt                 # 다음 스텝으로

return np.array(X).T, np.array(Y).T, np.array(U).T    # (3,M), (3,M), (2,M)
```

| 수식 | 코드 | 값 |
|:---|:---|:---|
| $M$ | `X.shape[1]` | 10,000 (= 200 궤적 × 50 스텝) |
| $N_x$ | `X.shape[0]` | 3 |
| $N_u$ | `U.shape[0]` | 2 |

> [!note] 열 하나 = 데이터 포인트 하나
> 논문과 코드 모두 **$N_x \times M$ 규약**(세로가 차원, 가로가 데이터 수)을 씁니다. 문헌에 따라 전치 규약을 쓰는 경우가 있으니 다른 코드를 볼 때 주의하세요.

---

## ③ 리프팅 — 논문의 $\psi$

이 예제의 딕셔너리는 다음 성분으로 구성됩니다.

$$
\psi(x) = \big[\underbrace{x,\ y,\ \theta}_{\text{항등항}},\ \underbrace{\text{poly}(x)}_{\text{다항식}},\ \underbrace{\cos\theta,\ \sin\theta}_{\text{삼각함수}},\ \underbrace{x_ix_j}_{\text{교차항}}\big]^\top
$$

**`poly_order=1, use_trig=True` 인 경우를 끝까지 써보면**

$$
\psi(x) = \big[\,x,\ y,\ \theta,\ \underbrace{\theta,\ y,\ x}_{\text{1차 다항식}},\ \cos\theta,\ \sin\theta\,\big]^\top \in \mathbb{R}^8
$$

```python
# koopman_lib.py — Lifting.phi()
feats = list(x)                       # 항등항 3개  -> full-state observability
for exps in self.poly_terms:          # 다항식 항
    ...
if self.use_trig and self.n >= 3:
    feats.append(np.cos(x[2]))        # x[2] = theta
    feats.append(np.sin(x[2]))
```

> [!note] 항등항과 1차 다항식이 중복됩니다
> 위 식에서 $x,y,\theta$ 가 두 번 나타납니다(항등항 + 1차 다항식). 원본 데모의 구조를 그대로 유지한 것이며, `pinv`가 rank 부족을 알아서 처리하므로 **결과에는 영향이 없습니다**. 다만 $N_\psi$ 를 셀 때 헷갈릴 수 있으니 아래 표를 참고하세요.

**설정별 실제 차원** (코드로 확인한 값)

| 설정 | 항등 | 다항식 | 삼각 | 교차 | $N_\psi$ |
|:---|---:|---:|---:|---:|---:|
| `poly1` | 3 | 3 | – | – | **6** |
| `poly1 + trig` | 3 | 3 | 2 | – | **8** |
| `poly1 + trig + cross` | 3 | 3 | 2 | 3 | **11** |
| `poly2 + cross` | 3 | 9 | – | 3 | **15** |
| `poly3 + cross` | 3 | 19 | – | 3 | **25** |

**행렬 전체에 적용**

$$
\Psi(X) = \big[\,\psi(x_1),\ \psi(x_2),\ \dots,\ \psi(x_M)\,\big] \in \mathbb{R}^{N_\psi\times M}
$$

```python
def lift_matrix(self, X):
    return np.vstack([self.phi(X[:, i]) for i in range(X.shape[1])]).T
```

---

## ④ EDMD — 논문 (6)(7)식

### 풀려는 식

$$
\Psi(Y) \;\approx\; K_\psi\,\Psi(X) + K_u\,U
$$

미지수가 둘($K_\psi, K_u$)이지만, **블록을 쌓으면 하나의 최소자승**이 됩니다.

$$
\underbrace{\Psi(Y)}_{N_\psi\times M}
\;\approx\;
\underbrace{\begin{bmatrix} K_\psi & K_u\end{bmatrix}}_{K,\ \ N_\psi\times(N_\psi+N_u)}
\underbrace{\begin{bmatrix} \Psi(X) \\ U \end{bmatrix}}_{Z,\ \ (N_\psi+N_u)\times M}
$$

### 최소자승과 닫힌 형태 해

논문 (6)식:

$$
\underset{K}{\text{minimize}}\quad \big\|\Psi(Y) - K\,Z\big\|_F
$$

논문 (7)식 — **닫힌 형태 해**:

$$
\boxed{\;K = \Psi(Y)\,Z^{\dagger}\;}
$$

```python
# koopman_lib.py — edmd_with_input()
PhiX = lifting.lift_matrix(X)         # Psi(X)   (N_psi, M)
PhiY = lifting.lift_matrix(Y)         # Psi(Y)   (N_psi, M)

Z = np.vstack([PhiX, U])              # Z        (N_psi + m, M)
K = PhiY.dot(pinv(Z))                 # K = Psi(Y) @ pinv(Z)

n_phi = PhiX.shape[0]
return K[:, :n_phi], K[:, n_phi:], PhiX   # K_psi, K_u
```

### 기호 대응표

| 수식 | 코드 | shape |
|:---|:---|:---|
| $\Psi(X)$ | `PhiX` | $(N_\psi, M)$ |
| $\Psi(Y)$ | `PhiY` | $(N_\psi, M)$ |
| $Z = [\Psi(X); U]$ | `Z` | $(N_\psi+N_u,\ M)$ |
| $K = [K_\psi \mid K_u]$ | `K` | $(N_\psi,\ N_\psi+N_u)$ |
| $K_\psi$ | `K[:, :n_phi]` | $(N_\psi, N_\psi)$ |
| $K_u$ | `K[:, n_phi:]` | $(N_\psi, N_u)$ |
| $(\cdot)^\dagger$ | `pinv(·)` | → [[Pseudo-inverse]] |

> [!success] 이 한 줄이 Koopman의 실시간성 근거입니다
> `K = PhiY.dot(pinv(Z))` — **반복 최적화가 없습니다.** SVD 한 번이면 끝이라 10,000개 데이터로 0.09초에 학습됩니다. 경사하강을 수천 epoch 도는 신경망과 대비되는 지점이며, 논문 [68]의 *"orders of magnitude faster"* 가 이것입니다.

### 디코더

리프팅 상태에서 원 상태로 되돌리는 선형 사상입니다.

$$
x \approx C\,\psi(x), \qquad C = X\,\Psi(X)^{\dagger} \in \mathbb{R}^{3\times N_\psi}
$$

```python
def fit_decoder(X, PhiX):
    return X.dot(pinv(PhiX))          # C
```

딕셔너리가 상태 자신을 포함하므로(full-state observability) 원리적으로는 **앞 3행만 잘라내면** 됩니다. 실제로 재구성 오차가 `6.4e-15`(기계 정밀도)로 나오는 이유입니다.

---

## ⑤ 예측 — 두 가지 rollout의 차이

> [!warning] 이 구분을 놓치면 모델 성능을 과대평가합니다

**(a) 1-step 예측 반복** — 매 스텝 **실제 상태**에서 다시 리프팅

$$
\hat{x}_{t+1} = C\big(K_\psi\,\psi(x_t^{\text{true}}) + K_u u_t\big)
$$

```python
# koopman_lib.py — rollout()
phi_next = K_psi.dot(lifting.phi(x_true)) + K_u.dot(u)   # x_true = 실제 상태!
xs_pred.append(C.dot(phi_next))
x_true = f_discrete(x_true, u, dt=dt)
```

**(b) 순수 리프팅 rollout** — 실제 상태를 **전혀 참조하지 않음**

$$
z_{t+1} = K_\psi z_t + K_u u_t, \qquad \hat{x}_t = C z_t, \qquad z_0 = \psi(x_0)
$$

```python
# 04_dictionary_study.py
z = lifting.phi(x0)
for t in range(steps):
    z = K_psi @ z + K_u @ u_seq[:, t]     # 실제 상태 참조 없음
    preds.append(C @ z)
```

| | (a) 1-step 반복 | (b) 순수 rollout |
|:---|:---|:---|
| 매 스텝 리프팅 | 실제 상태에서 | 이전 **예측**에서 |
| 오차 누적 | **없음** | 있음 |
| 실제 성능 반영 | 과대평가 | 정직함 |
| 쓰이는 곳 | 02번 (원본 데모와 동일) | 04번 |

**(b)가 진짜 "모델만으로 미래를 예측"하는 것**이며, [[EDMD]] 6번의 투영 오차가 누적되는 모습을 관찰할 수 있습니다.

---

## ⑥ 모델 구조 — affine vs bilinear (04번의 핵심)

### 왜 이 비교가 필요한가

이 시스템의 비선형항을 다시 봅시다.

$$
v\cos\theta \;=\; \underbrace{v}_{\text{입력}} \times \underbrace{\cos\theta}_{\text{상태함수}}
$$

**입력과 상태함수의 곱**입니다. 이제 두 모델 구조가 이것을 표현할 수 있는지 따져봅니다.

### (A) Input-affine — 표현 불가

$$
\psi(x_{t+1}) \approx K\,\psi(x_t) + B\,u_t
$$

> [!danger] 구조적 한계
> 우변에 $\psi$ 와 $u$ 가 **각자 독립된 항**으로만 등장합니다. 둘의 **곱이 들어갈 자리가 없습니다.**
>
> 그래서 $\cos\theta$ 를 딕셔너리에 넣어도 소용없습니다 — 그것에 $v$ 를 곱해줄 방법이 모델에 없기 때문입니다.

```python
# 04_dictionary_study.py — fit_affine()
Z = np.vstack([PhiX, U])              # psi와 u를 그냥 쌓기만 함
K = PhiY.dot(pinv(Z))
```

### (B) Bilinear — 표현 가능

$$
\psi(x_{t+1}) \approx K\,\psi(x_t) + B\,u_t + \sum_{j=1}^{N_u} u_{t,j}\,B_j\,\psi(x_t)
$$

마지막 항이 **$u$ 와 $\psi$ 의 곱**을 담습니다.

```python
# 04_dictionary_study.py — fit_bilinear()
blocks = [PhiX, U] + [U[j:j+1, :] * PhiX for j in range(U.shape[0])]
Z = np.vstack(blocks)                 # (N_psi + m + m*N_psi, M)
K = PhiY.dot(pinv(Z))
```

> [!important] `U[j:j+1, :] * PhiX` 가 하는 일
> `U[j:j+1, :]` 는 $j$ 번째 입력 채널만 뽑은 $(1, M)$ 행벡터입니다. 이것을 $(N_\psi, M)$ 인 `PhiX`에 곱하면 **브로드캐스팅**이 일어나, 각 열 $t$ 에서
> $$u_{t,j}\cdot\psi(x_t)$$
> 가 만들어집니다. 즉 **곱셈 비선형성을 회귀 변수로 명시적으로 넣어주는 것**입니다.
>
> 중요한 점: 이렇게 해도 **$K$ 에 대해서는 여전히 선형 최소자승**이라 닫힌 형태 해가 유지됩니다. 비선형이 되는 것은 나중에 $u$ 를 **최적화 변수로 쓸 때**(MPC)입니다.

### 결과 — 8차원으로 정확한 선형화

| 딕셔너리 | $N_\psi$ | input-affine | bilinear |
|:---|---:|---:|---:|
| poly1 | 6 | 1.855e-02 | 1.600e-02 |
| poly2 | 15 | 1.854e-02 | 9.819e-03 |
| poly3 | 25 | 1.854e-02 | 4.583e-03 |
| **poly1 + trig** | **8** | 1.854e-02 | **3.525e-15** |
| poly2 + trig | 17 | 1.854e-02 | 8.528e-15 |

> [!success] 이 표가 말하는 두 가지
> **① affine 열은 전부 1.85e-02** — 차원을 6→25로 4배 키워도, 삼각함수를 넣어도 그대로입니다. **모델 구조가 틀렸으면 딕셔너리를 아무리 손봐도 소용없습니다.**
>
> **② `poly1+trig` + bilinear = 3.5e-15** — 기계 정밀도, 즉 **정확한(exact) 모델**입니다. 8차원으로 비선형 시스템이 완벽히 선형화되었고, 25차원 poly3보다 훨씬 정확합니다.
>
> 딕셔너리(**무엇을 담는가**)와 모델 구조(**어떻게 결합하는가**)가 **함께** 맞아야 $\mathrm{span}(\psi)$ 가 [[Koopman-Invariant Subspace|Koopman-불변]]이 됩니다.

---

## ⑦ MPC — 논문 (12)(13)식

### 최적화 문제

논문 (13)식에 대응합니다.

$$
\begin{aligned}
\underset{\{z_i\},\{u_i\}}{\text{minimize}}\quad
& \sum_{i=0}^{N_h-1}\Big[(z_i-z_i^{\text{ref}})^\top Q\,(z_i-z_i^{\text{ref}}) + u_i^\top R\,u_i\Big] \\
&\qquad + (z_{N_h}-z_{N_h}^{\text{ref}})^\top Q\,(z_{N_h}-z_{N_h}^{\text{ref}}) \\[4pt]
\text{subject to}\quad
& z_{i+1} = A z_i + B u_i && \text{(선형 동역학)}\\
& u_{\min} \le u_i \le u_{\max} && \text{(입력 제약)}\\
& z_0 = \psi(x_t) && \text{(현재 상태)}
\end{aligned}
$$

```python
# 03_mpc_control.py — run_mpc_affine()
Uv = cp.Variable((2, H))              # u_0 ... u_{H-1}
Zv = cp.Variable((n_psi, H + 1))      # z_0 ... z_H

cost = 0
cons = [Zv[:, 0] == lifting.phi(x[:, k])]          # z_0 = psi(x_t)

for i in range(H):
    cons += [Zv[:, i+1] == A_aff @ Zv[:, i] + B_aff @ Uv[:, i]]   # 선형 동역학
    cons += [Uv[:, i] <= u_max, Uv[:, i] >= u_min]                # 입력 제약
    cost += cp.quad_form(Zv[:, i] - Phi_ref[:, k+i], Q)           # 상태 벌점
    cost += cp.quad_form(Uv[:, i], R)                             # 입력 벌점

cost += cp.quad_form(Zv[:, H] - Phi_ref[:, k+H], Q)               # 종단 비용
prob = cp.Problem(cp.Minimize(cost), cons)
prob.solve(warm_start=True)
```

| 수식 | 코드 |
|:---|:---|
| $z_i$ | `Zv[:, i]` (cvxpy 변수) |
| $u_i$ | `Uv[:, i]` (cvxpy 변수) |
| $z_i^{\text{ref}}$ | `Phi_ref[:, k+i]` |
| $(\cdot)^\top Q(\cdot)$ | `cp.quad_form(·, Q)` |
| $N_h$ | `H` (구간 끝에서 짧아짐) |

> [!success] 왜 볼록 QP인가
> - 비용: $z^\top Q z + u^\top R u$ — $Q\succeq0$, $R\succ0$ 이므로 **볼록 이차함수**
> - 제약: $z_{i+1}=Az_i+Bu_i$, $u_{\min}\le u\le u_{\max}$ — **전부 선형(아핀)**
>
> 볼록 비용 + 아핀 제약 = **볼록 QP** → 전역 최적해가 유일하고, 초기 추측이 필요 없습니다. 리프팅으로 차원이 늘었는데도 QP 1회가 **19 ms**에 풀리는 이유입니다. 📎 [[Koopman MPC]] 2번

### Bilinear MPC — 볼록성을 잃습니다

Bilinear 모델을 쓰면 제약이 $z_{i+1} = Az_i + Bu_i + \sum_j u_{i,j}B_j z_i$ 가 되는데, **$u_{i,j}z_i$ 항이 두 최적화 변수의 곱**이라 더 이상 아핀이 아닙니다.

해법은 이전 해 $(u^{\text{prev}}, z^{\text{prev}})$ 주변에서 **테일러 1차 전개**하는 것입니다.

$$
u_j(B_jz) \;\approx\; \underbrace{u_j\,(B_jz^{\text{prev}})}_{u\text{는 변수},\ z\text{는 고정}} \;+\; \underbrace{u_j^{\text{prev}}\,B_j(z-z^{\text{prev}})}_{u\text{는 고정},\ z\text{는 변수}}
$$

각 항에서 **한쪽만 변수**이므로 결과가 선형이 됩니다.

```python
# 03_mpc_control.py — run_mpc_bilinear()
lin = A_bil @ Zv[:, i] + B_bil @ Uv[:, i]
for j in range(2):
    lin = lin + Uv[j, i] * (Bj[j] @ z_prev[:, i]) \
              + u_prev[j, i] * (Bj[j] @ (Zv[:, i] - z_prev[:, i]))
cons += [Zv[:, i+1] == lin]
```

이 QP를 `n_iter=3`번 반복하며 $(u^{\text{prev}}, z^{\text{prev}})$ 를 갱신합니다(SQP류). **전역 최적해 보장은 사라지고 국소 해만 얻습니다.**

---

## 📊 종합 — 수식 선택이 결과에 미치는 영향

| 모델 | 수식 | 1-step 오차 | 추종 오차 | 계산 |
|:---|:---|---:|---:|---:|
| **(A) affine** | $Kz+Bu$ | 1.85e-02 | 17.16 m | 18.9 ms |
| **(B) bilinear** | $Kz+Bu+\sum u_jB_jz$ | **3.52e-15** | **6.30 m** | 108.9 ms |

> [!important] 이 표가 논문의 트레이드오프를 그대로 보여줍니다
> **(A)** 는 볼록해서 빠르고 전역 최적해를 보장하지만, 모델이 $v\cos\theta$ 를 구조적으로 표현하지 못해 추종에 실패합니다.
>
> **(B)** 는 모델이 정확해 추종이 3배 가까이 개선되지만, 비볼록이라 계산이 6배 무겁고 국소 해만 얻습니다.
>
> **"볼록성은 공짜가 아니다"** — 논문 [[Koopman MPC]] 3번이 말하는 *"때때로 비선형 실현이 더 정확한 예측을 주고, 그러면 그 트레이드오프가 정당화된다"* 의 구체적 사례입니다.

> [!warning] 다만 (B)의 6.30 m 도 성공은 아닙니다
> 모델이 1-step으로 정확해도 MPC 성능은 예측구간·가중치·SQP 반복 횟수에 함께 좌우됩니다. 여기서는 **모델 구조의 영향만 분리**해 보이는 것이 목적이라 나머지를 튜닝하지 않았습니다.
>
> 또한 **모든 시스템에서 affine이 실패하는 것은 아닙니다.** 비선형성이 입력과 얽히지 않은 시스템에서는 affine으로 충분하며, 그때는 볼록성이라는 큰 이점을 공짜로 얻습니다.

---

## 📊 실제 실행 결과

아래는 이 저장소에서 직접 돌린 값입니다.

### 02번 — EDMD의 속도

```
딕셔너리 차원 N_psi = 11
EDMD 완료 — 소요시간 0.0861 초
재구성 RMS 오차: 6.437e-15
```

10,000개 데이터로 학습하는 데 **0.09초**입니다. 반복 최적화가 없기 때문이며([[Pseudo-inverse]] 한 번), 이것이 논문의 runtime learning 주장을 떠받치는 계산적 근거입니다.

### 04번 · 03번 결과

> 📎 두 실험의 결과표와 해석은 위 **[⑥ 모델 구조](#⑥-모델-구조--affine-vs-bilinear-04번의-핵심)** 와 **[📊 종합](#-종합--수식-선택이-결과에-미치는-영향)** 에 수식과 함께 정리했습니다.

**요약만 다시 적으면**

- **04번**: `poly1+trig`(8차원) + bilinear 에서 1-step 오차 **3.5e-15** — 25차원 poly3보다 정확한, 사실상 **정확한 선형화**
- **03번**: 모델 구조만 affine → bilinear 로 바꿔 추종 오차 **17.16 m → 6.30 m**, 대신 계산은 19 ms → 109 ms

---

## ⚠️ 원본 노트북에서 발견한 점

원본 `demo.ipynb`를 그대로 돌릴 때 알아두면 좋은 두 가지입니다. 교육용 코드라 의도적으로 단순화한 부분일 수 있습니다.

> [!note] ① `dt` 불일치
> 셀 4에서 `dt = 0.05`로 데이터를 수집하는데, MPC 셀(14)에서 `dt = 0.1`로 **덮어씁니다**. 학습된 모델의 시간 스케일과 시뮬레이션 시간 스케일이 2배 어긋난 채 제어가 돌아갑니다. 이 저장소의 스크립트는 학습에 쓴 `dt`를 일관되게 사용합니다.
>
> 논문 VI절이 **sampling rate selection**을 열린 문제로 꼽는 이유를 체감할 수 있는 지점이기도 합니다 (논문 [166]).

> [!note] ② input-affine의 구조적 한계
> 원본은 input-affine 모델만 사용합니다. 그런데 위 04번 결과처럼 이 시스템에서는 그 구조로 $v\cos\theta$ 를 표현할 수 없어, 딕셔너리를 어떻게 손봐도 예측 정확도가 1.85e-02 근처에서 정체됩니다. 이 저장소의 03·04번은 bilinear를 함께 제공해 그 차이를 드러냅니다.

---

## 🗺️ 개념 노트와의 대응

| 스크립트 | 대응 개념 노트 |
|:---|:---|
| 01_collect_data | [[EDMD]] 1번 (데이터 행렬), persistent excitation → 실험 결과: [[실험 기록 - 데이터 수집]] |
| 02_edmd_fit | [[Observable Function]], [[EDMD]] 2~5번, [[Pseudo-inverse]] |
| 03_mpc_control | [[Koopman MPC]] 1~3번, [[Koopman with Control Input]], [[Affine]] |
| 04_dictionary_study | [[Observable Function]], [[Koopman-Invariant Subspace]], [[EDMD]] 7번 |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
> - [[EDMD]] — 02번 스크립트의 이론
> - [[Observable Function]] — 04번 실험의 이론
> - [[Koopman MPC]] — 03번 스크립트의 이론
> - [[Koopman with Control Input]] — affine vs bilinear
