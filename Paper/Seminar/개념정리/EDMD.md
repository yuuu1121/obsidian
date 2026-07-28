---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Algorithm
aliases:
  - Extended DMD
  - Extended Dynamic Mode Decomposition
  - DMD
keywords: EDMD, DMD, least squares, pseudoinverse, Koopman approximation
related notes: "[[Koopman Operator]], [[Observable Function]], [[Koopman-Invariant Subspace]]"
dg-publish: false
---

# EDMD (Extended Dynamic Mode Decomposition)

> [!abstract] 한 줄 요약
> 데이터 스냅샷 쌍 $(x_i, y_i)$ 로부터 유한차원 Koopman 근사 행렬 $K$ 를 **최소제곱으로 한 방에** 구하는 알고리즘. 닫힌 형태 해 $K = \Psi(Y)\Psi(X)^\dagger$ 가 존재하기 때문에 **반복 최적화 없이 즉시** 계산된다 — 이것이 Koopman이 로보틱스에서 실시간으로 쓰일 수 있는 근본 이유다.

---

## 1. 데이터 준비

시스템 $x_{t+1} = T(x_t)$ 로부터 $M$ 개의 스냅샷 쌍을 모은다.

$$
X = [\,x_1, x_2, \dots, x_M\,] \in \mathbb{R}^{N_x \times M}, \qquad
Y = [\,y_1, y_2, \dots, y_M\,] \in \mathbb{R}^{N_x \times M}
$$

여기서 $y_i = T(x_i)$, 즉 **$X$ 의 각 열을 한 스텝 전파한 것이 $Y$ 의 대응하는 열**이다.

> [!note] 궤적 데이터인 경우
> 하나의 긴 궤적 $x_1 \to x_2 \to \dots \to x_{M+1}$ 만 있다면 그냥 한 칸 밀어서 쓰면 된다.
> $$X = [x_1, \dots, x_M], \qquad Y = [x_2, \dots, x_{M+1}]$$
> 여러 궤적이 있으면 열 방향으로 이어붙이면 된다 (**궤적 간 경계에서 잘못 짝지어지지 않도록 주의**).

---

## 2. 리프팅 (Lifting)

[[Observable Function|딕셔너리]] $\psi = [\psi_1, \dots, \psi_{N_\psi}]^\top$ 를 데이터 행렬에 열 단위로 적용한다.

$$
\Psi(X) = \big[\,\psi(x_1),\ \psi(x_2),\ \dots,\ \psi(x_M)\,\big] \in \mathbb{C}^{N_\psi \times M}
$$

$$
\Psi(Y) = \big[\,\psi(y_1),\ \psi(y_2),\ \dots,\ \psi(y_M)\,\big] \in \mathbb{C}^{N_\psi \times M}
$$

**차원 감각**: $\Psi(X)$ 는 세로가 리프팅 차원 $N_\psi$, 가로가 데이터 개수 $M$ 이다. 보통 $M \gg N_\psi$ (데이터가 딕셔너리보다 많음) 이어야 문제가 잘 정의된다.

---

## 3. 최적화 문제와 닫힌 형태 해

### 목적 함수

우리가 원하는 것은 $\psi(x_{t+1}) \approx K\psi(x_t)$ 이므로, 모든 데이터에 대해 이 오차를 최소화한다. Frobenius norm 최소제곱 문제:

$$
\underset{K}{\text{minimize}} \quad \big\| \Psi(Y) - K\,\Psi(X) \big\|_F \tag{논문 (6)}
$$

Frobenius norm은 $\|A\|_F = \sqrt{\sum_{i,j}|a_{ij}|^2}$ 이므로, 이 문제는 곧 **모든 데이터 포인트·모든 관측함수에 대한 1-step 예측 오차 제곱합**을 최소화하는 것이다.

$$
\|\Psi(Y) - K\Psi(X)\|_F^2 = \sum_{i=1}^{M} \big\| \psi(y_i) - K\psi(x_i) \big\|_2^2
$$

### 해

$$
\boxed{\;K_{\mathrm{EDMD}} = \Psi(Y)\,\Psi(X)^{\dagger}\;} \tag{논문 (7)}
$$

$(\cdot)^\dagger$ 는 **Moore–Penrose 유사역행렬(pseudoinverse)** 이다.

<details>
<summary><b>왜 이 해가 나오는가 (유도)</b></summary>

$J(K) = \|\Psi(Y) - K\Psi(X)\|_F^2 = \mathrm{tr}\big[(\Psi(Y) - K\Psi(X))(\Psi(Y) - K\Psi(X))^*\big]$

$K$ 에 대해 미분하고 0으로 두면 (정규방정식, normal equation):

$$
\frac{\partial J}{\partial K} = -2\big(\Psi(Y) - K\Psi(X)\big)\Psi(X)^* = 0
$$

$$
\Rightarrow\ \Psi(Y)\Psi(X)^* = K\,\Psi(X)\Psi(X)^*
$$

$$
\Rightarrow\ K = \underbrace{\Psi(Y)\Psi(X)^*}_{=:A} \big(\underbrace{\Psi(X)\Psi(X)^*}_{=:G}\big)^{-1} = \Psi(Y)\Psi(X)^\dagger
$$

여기서 $G = \Psi(X)\Psi(X)^*$ 는 **Gram 행렬**, $A = \Psi(Y)\Psi(X)^*$ 는 **cross-correlation 행렬**이다. 문헌에 따라 $K = A G^{-1}$ 또는 전치 규약으로 $K = G^\dagger A$ 로 쓰기도 하니 **행/열 규약을 반드시 확인**할 것.
</details>

> [!success] 왜 이게 결정적인가
> **반복(iteration)이 없다.** SVD 한 번이면 끝난다. 신경망처럼 수천 epoch을 돌 필요가 없다. 논문 [68]이 보고하듯 Koopman 모델의 학습 단계는 경쟁 데이터 기반 방법들보다 **수 자릿수(orders of magnitude) 빠르다**. 나아가 [17] 같은 online DMD 변형은 **매 타임스텝 rank-1 업데이트**로 $K$ 를 갱신할 수 있어 시변 시스템에도 실시간 적용 가능하다.

---

## 4. 예측: EDMD Predictor

$K_{\mathrm{EDMD}}$ 를 얻고 나면 임의의 함수에 대한 예측이 가능하다.

### 일반 함수 $f \in \mathrm{span}(\psi)$

$f$ 가 딕셔너리의 선형결합으로 쓰인다고 하자.

$$
f(\cdot) = v_f^\top \psi(\cdot) = \sum_{i=1}^{N_\psi} (v_f)_i\,\psi_i(\cdot)
$$

그러면 $\mathcal{K}f$ 에 대한 EDMD 예측자는

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}f} := v_f^\top K_{\mathrm{EDMD}}\,\psi \tag{논문 (8)}
$$

> [!important] 미묘하지만 중요한 점
> $\mathcal{K}f$ 자체는 $\mathrm{span}(\psi)$ 에 **속하지 않을 수 있다**($\mathcal{K}f \notin \mathrm{span}(\psi)$). 그런데 예측자 $\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}f}$ 는 정의상 항상 $\mathrm{span}(\psi)$ 안에 있다. **바로 이 간극이 EDMD의 근사 오차**다.

### 고유함수 (특수한 경우)

$v$ 가 $K_{\mathrm{EDMD}}$ 의 **좌고유벡터(left eigenvector)** 일 때, 즉 $v^\top K_{\mathrm{EDMD}} = \lambda v^\top$ 일 때, $\phi(\cdot) = v^\top\psi(\cdot)$ 로 두면

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}\phi} = v^\top K_{\mathrm{EDMD}}\,\psi = \lambda\,v^\top\psi = \lambda\,\phi \tag{논문 (9)}
$$

즉 **좌고유벡터로 딕셔너리를 조합하면 근사 [[Koopman Eigenfunction|Koopman 고유함수]]가 나온다.** 이것이 EDMD로부터 스펙트럼 정보를 뽑는 표준 경로다.

---

## 5. EDMD가 실제로 근사하는 것 — 사영 연산자

> [!warning] $K_{\mathrm{EDMD}} \ne \mathcal{K}$
> 논문이 명확히 짚는 지점이다. EDMD 행렬은 Koopman 연산자 자체를 포착하는 게 아니라, **$\mathrm{span}(\psi)$ 위로의 사영된 작용**을 encode 한다. 즉 EDMD가 근사하는 진짜 대상은:

$$
\mathcal{P}_{\mathrm{span}(\psi)}\,\mathcal{K} : \mathcal{F} \to \mathcal{F} \tag{논문 (10)}
$$

여기서 $\mathcal{P}_{\mathrm{span}(\psi)}$ 는 $L^2(\mathcal{X})$-직교 사영 연산자이고, 내적은 **경험적 측도(empirical measure)** 기준으로 계산된다.

$$
\mu_{\mathcal{X}} = \frac{1}{M}\sum_{i=1}^{M}\delta_{x_i} \tag{논문 (11)}
$$

($\delta_{x_i}$ 는 $x_i$ 에서의 Dirac 측도.)

**해석**: 우리가 가진 유한 데이터가 만드는 측도 위에서, 딕셔너리가 span 하는 부분공간에 Koopman 작용을 정사영한 것 — 그게 EDMD다. $\mathrm{span}(\psi)$ 는 (10)의 연산자에 대해 **항상 불변**이므로, 작용을 제한해 행렬로 표현할 수 있고, 정확한 데이터에서는 그 행렬이 $K_{\mathrm{EDMD}}$ 와 일치한다 [29][30].

### 수렴성 (Korda & Mezić [30])

딕셔너리 크기 $N_\psi \to \infty$ 및 데이터 $M \to \infty$ 에서:
- 연산자 위상(operator topology)에서 Koopman 연산자로 수렴
- 고유값 포착
- 고유함수의 **약수렴(weak convergence)**

> [!warning] 수렴성이 곧 실용적 성능은 아니다
> 논문의 강한 경고: **어떤 수렴 결과도 "더 큰 유한차원 공간이 반드시 예측에 더 좋다"를 의미하지 않는다.**
>
> **반례**: 선형 시스템 $x^+ = 0.5x$, 두 딕셔너리 $\psi_1(x) = x$, $\psi_2(x) = [x, \sin(x)]$.
> $\mathrm{span}(\psi_1) \subset \mathrm{span}(\psi_2)$ 이지만
> - $\mathrm{span}(\psi_1)$ 은 **Koopman 불변** → 예측이 **정확(exact)**
> - $\mathrm{span}(\psi_2)$ 는 불변이 아님 → 일부 함수에서 **큰 오차**
>
> 게다가 시스템 모델 없이는 **원하는 정확도를 달성할 딕셔너리 차원의 하한을 추정할 방법조차 없다**. 시스템 지식 없이 일반 기저를 쓰면 필요한 차원이 극단적으로 커질 수 있다. → 그래서 딕셔너리는 **시스템/데이터 정보에 기반해 설계·학습**되어야 한다.

---

## 6. DMD와의 관계 (논문 Remark 1)

**DMD (Dynamic Mode Decomposition)** 는 원래 유체 유동의 coherent feature 추출을 위해 제안됐다 [34]. EDMD보다 먼저 개발됐지만, 관계는 이렇다.

$$
\text{exact DMD} = \text{EDMD with } \psi = \mathrm{id} \quad (\text{리프팅 없음})
$$

즉 딕셔너리를 항등 사상으로 두면 EDMD가 exact DMD로 환원된다.

$$
K_{\mathrm{DMD}} = Y X^\dagger
$$

**DMD는 그냥 "데이터에 가장 잘 맞는 선형 시스템 행렬"** 을 구하는 것이고, EDMD는 그것을 **리프팅된 공간에서** 하는 것이다.

---

## 7. 구현 시 주의사항

| 항목 | 주의점 |
|:---|:---|
| **수치 안정성** | $\Psi(X)$ 가 ill-conditioned면 pseudoinverse가 폭발한다. SVD 기반 truncated pseudoinverse (작은 특이값 절단) 또는 Tikhonov 정규화 $K = \Psi(Y)\Psi(X)^\top(\Psi(X)\Psi(X)^\top + \gamma I)^{-1}$ 를 쓴다. |
| **데이터 개수** | $M \ge N_\psi$ 는 필수이며 실제로는 $M \gg N_\psi$ 를 권장. 아니면 overfitting. |
| **스케일링** | 딕셔너리 성분들의 크기가 크게 다르면 최소제곱이 큰 성분에 편향된다. 정규화 필수. |
| **행/열 규약** | 문헌마다 $\Psi$ 를 $N_\psi \times M$ 로 쓸지 $M \times N_\psi$ 로 쓸지 다르다. 논문 본문은 $N_\psi \times M$ 규약. |
| **궤적 경계** | 여러 궤적을 이어붙일 때 궤적 끝-시작이 잘못 짝지어지지 않게 할 것. |
| **노이즈** | 측정 노이즈는 EDMD 추정을 편향(bias)시킨다. forward-backward DMD, TLS-DMD 등의 대안 존재. |

---

## 8. 의사코드

```python
# 1. 데이터 수집
X, Y = collect_snapshot_pairs()      # (N_x, M) each,  Y[:,i] = T(X[:,i])

# 2. 리프팅
PsiX = psi(X)                        # (N_psi, M)
PsiY = psi(Y)                        # (N_psi, M)

# 3. 최소제곱 (닫힌 형태) — 반복 없음
K = PsiY @ np.linalg.pinv(PsiX)      # (N_psi, N_psi)

# 4. 예측 (multi-step rollout)
z = psi(x0)                          # (N_psi,)
for t in range(horizon):
    z = K @ z
    x_pred[t] = z[:N_x]              # full-state observability 가정 시
```

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 왜 $K$ 를 구하려 하는가
> - [[Observable Function]] — $\psi$ 를 어떻게 고르는가
> - [[Koopman-Invariant Subspace]] — EDMD가 정확해지는 조건
> - [[Consistency Index]] — EDMD residual의 한계와 대안 지표
> - [[HVOK]] — 딕셔너리 설계를 우회하는 대안
> - [[Koopman with Control Input]] — 입력 $u$ 를 포함한 확장
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
