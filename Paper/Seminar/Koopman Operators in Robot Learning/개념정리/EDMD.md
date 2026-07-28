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

> [!abstract] 한 문장 요약
> EDMD는 **"상태를 딕셔너리로 들어올린 뒤 → 그 공간에서 선형 관계를 최소자승($K = \Psi(Y)\Psi(X)^\dagger$)으로 한 번에 푸는 것"** 이며, 정확도의 열쇠는 **딕셔너리의 크기가 아니라 선택한 부분공간이 Koopman-불변에 얼마나 가까운가**입니다.

아래 1→8번을 순서대로 읽으면 EDMD가 왜 그렇게 생겼는지가 쌓입니다.

---

## 1. 데이터 행렬 구성

먼저 시스템 $x_{t+1} = T(x_t)$ 에서 데이터를 모읍니다.

$$
X = [\,x_1, x_2, \ldots, x_M\,], \qquad Y = [\,y_1, y_2, \ldots, y_M\,]
$$

여기서 $y_i = T(x_i)$ 입니다. 즉 **$X$ 는 "현재 상태들", $Y$ 는 그 "한 스텝 뒤 상태들"** 입니다.

실제로는 하나의 궤적을 시간축으로 밀어서 쓸 수도 있습니다.

$$
X = [x_1, \ldots, x_M], \qquad Y = [x_2, \ldots, x_{M+1}]
$$

> [!note] 왜 "쌍"으로 모으는가
> Koopman 연산자는 정의상 **한 스텝 전파**를 표현합니다($\mathcal{K}g(x_t) = g(x_{t+1})$). 그러니 학습 데이터도 "지금과 그 다음"의 짝이어야 합니다. 궤적이 여러 개면 열 방향으로 이어붙이면 되는데, **궤적의 끝과 다음 궤적의 시작이 잘못 짝지어지지 않도록** 주의해야 합니다.

---

## 2. 리프팅 (Lifting)

핵심 아이디어는 상태 $x$ 를 그대로 쓰지 않고, **관측함수(딕셔너리) $\Psi$ 로 더 높은 차원으로 "들어올리는"** 것입니다. 예를 들어

$$
\Psi(x) = [\,x,\ x^2,\ \sin(x),\ \ldots\,]^\top
$$

같은 형태입니다. 이것을 데이터 행렬의 **각 열마다** 적용합니다.

$$
\Psi(X) = [\,\Psi(x_1),\ \Psi(x_2),\ \ldots,\ \Psi(x_M)\,] \in \mathbb{C}^{N_\Psi \times M}
$$

즉 각 데이터 포인트마다 딕셔너리를 적용한 결과를 **열로 쌓은 행렬**입니다.

> [!tip] 차원 감각 잡기
> $\Psi(X)$ 는 **세로 = 리프팅 차원 $N_\Psi$, 가로 = 데이터 개수 $M$** 입니다.
> 보통 $M \gg N_\Psi$ (데이터가 딕셔너리보다 훨씬 많음) 이어야 문제가 잘 정의됩니다. 반대면 과적합입니다.

📎 딕셔너리를 실제로 어떻게 고르는지는 [[Observable Function]]에 정리해 두었습니다.

---

## 3. 최소자승 문제 (식 6)

우리가 원하는 것은 리프팅된 공간에서 선형 관계 $\Psi(x_{t+1}) \approx K\Psi(x_t)$ 를 만족하는 행렬 $K$ 를 찾는 것입니다. 이를 오차 최소화 문제로 표현합니다.

$$
\min_{K}\ \ \big\|\,\Psi(Y) - K\Psi(X)\,\big\|_F \tag{6}
$$

여기서 $\|\cdot\|_F$ 는 **Frobenius 노름**(행렬 원소들의 제곱합의 제곱근)입니다. 쉽게 말해 **"$K\Psi(X)$ 가 $\Psi(Y)$ 에 최대한 가깝도록"** 하는 $K$ 를 찾는 것입니다.

풀어 쓰면 의미가 더 분명해집니다.

$$
\|\Psi(Y) - K\Psi(X)\|_F^2 = \sum_{i=1}^{M}\big\|\underbrace{\Psi(y_i)}_{\text{실제 다음 관측값}} - \underbrace{K\Psi(x_i)}_{\text{모델의 예측}}\big\|_2^2
$$

즉 **모든 데이터 포인트에 대한 1-step 예측 오차의 제곱합**입니다.

---

## 4. 닫힌 형태 해 (식 7)

이 선형 최소자승 문제는 **명시적인 해**를 가집니다.

$$
\boxed{\ K_{\text{EDMD}} = \Psi(Y)\,\Psi(X)^{\dagger}\ } \tag{7}
$$

여기서 $\dagger$ 는 **의사역행렬(pseudo-inverse)** 입니다. → 📎 [[Pseudo-inverse]]

$\Psi(X)$ 는 $N_\Psi\times M$ 로 **정사각이 아니라서** 역행렬 자체가 정의되지 않고, 데이터가 딕셔너리보다 많아($M \gg N_\Psi$) **모든 식을 정확히 만족하는 $K$ 도 없습니다.** 그럴 때 "오차를 최소화하는 답"을 주는 것이 $\dagger$ 입니다.

> [!success] 이것이 EDMD의 가장 큰 장점
> **딥러닝처럼 반복 학습이 필요 없고 한 번의 행렬 연산으로 구해집니다.** SVD 한 번이면 끝입니다.
>
> 이것이 논문이 강조하는 **데이터 효율성·실시간성의 근거**이기도 합니다.
> - 논문 [68]: 학습 단계가 경쟁 데이터 기반 방법 대비 **수 자릿수(orders of magnitude) 빠름**
> - 논문 [17]: online DMD 변형은 매 타임스텝 **rank-1 업데이트**로 갱신 가능 → 시변 시스템도 실시간 대응
> - → §I의 "runtime learning" 주장을 실제로 떠받치는 계산적 근거입니다

<details>
<summary><b>(a) 의사역행렬이 왜 최소자승 해가 되는지 — 유도</b></summary>

목적함수를 트레이스로 씁니다.

$$
J(K) = \|\Psi(Y) - K\Psi(X)\|_F^2 = \mathrm{tr}\big[(\Psi(Y) - K\Psi(X))(\Psi(Y) - K\Psi(X))^*\big]
$$

$K$ 로 미분해서 0으로 두면 (**정규방정식, normal equation**):

$$
\frac{\partial J}{\partial K} = -2\big(\Psi(Y) - K\Psi(X)\big)\Psi(X)^* = 0
$$

$$
\Rightarrow\quad \Psi(Y)\Psi(X)^* = K\,\Psi(X)\Psi(X)^*
$$

$$
\Rightarrow\quad K = \underbrace{\Psi(Y)\Psi(X)^*}_{A\ :\ \text{cross-correlation}}\ \big(\underbrace{\Psi(X)\Psi(X)^*}_{G\ :\ \text{Gram 행렬}}\big)^{-1} = \Psi(Y)\Psi(X)^\dagger
$$

**기하학적으로 읽으면**: 정규방정식 $(\Psi(Y) - K\Psi(X))\Psi(X)^* = 0$ 은 *"잔차가 $\Psi(X)$ 의 행공간에 직교한다"* 는 뜻입니다. 최소자승의 본질은 언제나 **직교 사영**입니다 — 이 관점이 6번에서 다시 등장합니다.

문헌에 따라 $K = AG^{-1}$ 또는 전치 규약으로 $K = G^\dagger A$ 로 쓰기도 하니 **행/열 규약을 반드시 확인**하세요.
</details>

---

## 5. 예측자(predictor) (식 8, 9)

$K$ 를 구했으면 이제 예측을 합니다. 딕셔너리 스팬 안의 함수 $f(\cdot) = v_f^\top\Psi(\cdot)$ 에 대해, $\mathcal{K}f$ 의 근사 예측은

$$
\mathcal{P}^{\text{EDMD}}_{\mathcal{K}f} := v_f^\top K_{\text{EDMD}}\,\Psi \tag{8}
$$

### 특별한 경우: 고유함수

특히 $v_\phi$ 가 $K_{\text{EDMD}}$ 의 **좌고유벡터**($v_\phi^\top K_{\text{EDMD}} = \lambda_\phi v_\phi^\top$)이면, **근사 Koopman 고유함수**를 얻습니다.

$$
\mathcal{P}^{\text{EDMD}}_{\mathcal{K}\phi} = v_\phi^\top K_{\text{EDMD}}\Psi = \lambda_\phi\,v_\phi^\top\Psi = \lambda_\phi\,\phi \tag{9}
$$

즉 **고유함수 $\phi$ 는 시간에 따라 단순히 고유값 $\lambda_\phi$ 로 스케일되며 진화한다**는 뜻입니다.

$$
\phi(x_t) = \lambda_\phi^{\,t}\,\phi(x_0)
$$

이것이 **Koopman의 "선형성" 매력의 핵심**입니다. 비선형 시스템의 궤적이 한 줄의 지수함수로 예측됩니다.

> [!warning] 왜 "좌"고유벡터인가
> $K$ 는 딕셔너리의 **계수 벡터**에 작용합니다. 함수 $f = v^\top\Psi$ 의 계수는 행벡터 $v^\top$ 이므로, $\mathcal{K}f$ 의 계수는 $v^\top K$ 입니다. 따라서 $f$ 가 고유함수이려면 $v^\top K = \lambda v^\top$ — **좌**고유벡터 조건이 됩니다.
>
> 우고유벡터를 쓰면 틀립니다. 다만 규약에 따라 $K$ 의 전치를 쓰면 좌우가 뒤바뀌므로 **본인 코드의 규약을 반드시 확인**하세요.

📎 고유함수의 물리적 의미($|\lambda|<1$ 감쇠, $|\lambda|=1$ 보존량 등)는 [[Koopman Eigenfunction]] 참고.

---

## 6. 개념적으로 가장 중요한 포인트

> [!danger] $K_{\text{EDMD}} \ne \mathcal{K}$
> $K_{\text{EDMD}}$ 는 **진짜 Koopman 연산자 $\mathcal{K}$ 자체가 아닙니다.** 이것은 $\mathcal{K}$ 의 작용을 $\mathrm{span}(\Psi)$ 위로 **직교 투영(projection)** 한 것을 인코딩합니다.

$$
\mathcal{P}_{\mathrm{span}(\Psi)}\,\mathcal{K} : \mathcal{F} \to \mathcal{F} \tag{10}
$$

여기서 투영은 **경험적 측도(empirical measure)** 기반의 $L_2$ 내적으로 정의됩니다.

$$
\mu_{X} = \frac{1}{M}\sum_{i=1}^{M}\delta_{x_i} \tag{11}
$$

데이터 포인트마다 디랙 측도를 놓은 것이니, **"가진 데이터 위에서만 오차를 재는 투영"** 이라고 이해하면 됩니다.

<details>
<summary><b>(b) 투영 연산자의 기하학적 의미 — 그림으로 이해하기</b></summary>

3차원 공간의 평면에 점을 정사영하는 것을 떠올리면 됩니다.

- **$\mathcal{F}$**(무한차원 함수공간) = 3차원 공간 전체
- **$\mathrm{span}(\Psi)$**(우리 딕셔너리가 만드는 부분공간) = 그 안의 평면
- **$\mathcal{K}f$** = $f$ 를 한 스텝 전파한 결과. 일반적으로 **평면 밖으로 나갑니다**
- **$\mathcal{P}_{\mathrm{span}(\Psi)}\mathcal{K}f$** = 그것을 평면 위로 다시 내린 그림자

```
                    Kf  ●  ← 진짜 다음 상태 (평면 밖!)
                        │
                        │ ← 이 수직 거리가 EDMD 오차
                        ▼
      ─────────────────●─────────────────  span(Ψ) 평면
                   P_span(Ψ) Kf
                   (EDMD가 실제로 주는 것)
```

**핵심 두 가지**:

1. **1스텝이면 오차가 작을 수 있지만, 다단계 예측에서는 매 스텝 "그림자 내리기"가 반복되어 오차가 누적**됩니다. 이것이 EDMD 모델의 장기 예측이 무너지는 메커니즘입니다.

2. **만약 $\mathcal{K}f$ 가 애초에 평면 안에 있다면** 그림자를 내려도 자기 자신입니다 → **오차 0**. 이 조건이 바로 [[Koopman-Invariant Subspace|Koopman 불변]]입니다. 7번의 이야기가 여기서 시작됩니다.

또 하나 — 투영의 기준이 $\mu_X$(가진 데이터)라는 점은 **데이터가 없는 영역에서는 오차를 재지도 못한다**는 뜻입니다. 학습 데이터 분포 밖(OOD)에서 Koopman 모델이 위험한 이유입니다.
</details>

### 수렴성은 보장되어 있다 (다만…)

Korda & Mezić [30]에 따르면 딕셔너리와 데이터가 충분히 커지면 연산자 위상에서 $\mathcal{K}$ 로 수렴하고, 고유값을 포착하며, 고유함수는 약수렴합니다. **그런데 이 수렴성이 실용적 성능을 보장하지는 않습니다** — 바로 다음 항목입니다.

---

## 7. 딕셔너리 선택의 미묘함

여기서 논문이 강조하는 **반직관적인 사실**이 있습니다.

> [!danger] 딕셔너리를 크게 만든다고 항상 좋은 것은 아닙니다

예시로 선형 시스템 $x^+ = 0.5x$ 를 봅시다.

| 딕셔너리 | 부분공간 | 결과 |
|:---|:---|:---|
| $\Psi_1(x) = x$ | 작음 | **Koopman-불변** → 예측이 **정확(exact)** ✅ |
| $\Psi_2(x) = [x, \sin(x)]$ | **더 큼** | 불변 아님 → 어떤 함수에 대해서는 **예측 오차가 큼** ❌ |

$\mathrm{span}(\Psi_1) \subset \mathrm{span}(\Psi_2)$ 인데도 **작은 쪽이 이깁니다.**

즉 **오차는 부분공간의 크기가 아니라 $\mathrm{span}(\Psi)$ 가 얼마나 Koopman-불변에 가까운가**에 달려 있습니다.

> [!warning] 게다가 하한을 알 수도 없습니다
> 논문이 덧붙이는 더 곤란한 사실: **시스템 모델 없이는 목표 정확도를 달성할 딕셔너리 차원의 하한을 추정할 방법조차 없습니다.** 시스템 지식 없이 일반적인 기저(다항식 전체 같은)를 쓰면 필요한 차원이 극단적으로 커질 수 있습니다.

**그래서 실무에서는** 무작정 딕셔너리를 키우기보다 **시스템/데이터 정보에 근거해 딕셔너리를 설계하거나 학습하는 것**이 중요합니다.

📎 그 방법들: [[Observable Function]] (수동 설계 / 물리 기반 / NN 기반)
📎 "불변에 가까운지"를 실제로 측정하는 법: [[Consistency Index]]

---

## 8. DMD와의 관계 (Remark 1)

DMD는 원래 **유체 흐름의 특징(coherent feature)을 뽑기 위해** 나온 방법입니다 [34]. EDMD보다 **먼저** 개발되었지만, 관계는 이렇습니다.

$$
\text{exact DMD} \;=\; \text{EDMD with }\Psi = \mathrm{id}\quad(\text{리프팅 없음})
$$

즉 EDMD의 딕셔너리를 항등함수 $\Psi(x) = x$ 로 두면 DMD가 됩니다.

$$
K_{\text{DMD}} = Y X^{\dagger}
$$

**정리하면**: DMD는 "데이터에 가장 잘 맞는 선형 시스템 행렬"을 구하는 것이고, EDMD는 **그것을 리프팅된 공간에서** 하는 것입니다. 역사적으로는 DMD가 먼저지만, 이론적으로는 EDMD가 더 일반적인 틀입니다.

---

## 📌 전체 흐름 한 눈에

```
 ①  데이터 수집        X = [x₁...x_M],  Y = [y₁...y_M],  yᵢ = T(xᵢ)
         │
 ②  리프팅            Ψ(X), Ψ(Y)          ← 딕셔너리 설계가 성패를 가름 (7번)
         │
 ③  최소자승 정식화    min ‖Ψ(Y) − KΨ(X)‖_F
         │
 ④  닫힌 형태 해       K = Ψ(Y)Ψ(X)†       ← 반복 없음! 실시간 가능 (4번)
         │
 ⑤  예측 / 고유분해    좌고유벡터 → φ(x_t) = λᵗφ(x₀)
         │
 ⑥  주의              K ≠ 𝒦.  span(Ψ) 위로의 투영일 뿐 (6번)
```

---

## 🔧 구현 시 실전 주의사항

| 항목 | 주의점 |
|:---|:---|
| **수치 안정성** | $\Psi(X)$ 가 ill-conditioned면 pseudoinverse가 폭발합니다. **SVD 절단**(작은 특이값 버리기) 또는 Tikhonov 정규화 $K = \Psi(Y)\Psi(X)^\top(\Psi(X)\Psi(X)^\top + \gamma I)^{-1}$ 사용 → 상세: [[Pseudo-inverse]] §5 |
| **데이터 개수** | $M \ge N_\Psi$ 는 필수, 실제로는 $M \gg N_\Psi$ 권장 |
| **스케일링** | 딕셔너리 성분들의 크기가 크게 다르면 최소자승이 큰 성분에 편향됩니다. 정규화 필수 |
| **행/열 규약** | 문헌마다 $\Psi$ 를 $N_\Psi\times M$ 로 쓸지 $M\times N_\Psi$ 로 쓸지 다릅니다. 논문 본문은 $N_\Psi\times M$ |
| **궤적 경계** | 여러 궤적을 이어붙일 때 끝-시작이 잘못 짝지어지지 않게 |
| **노이즈** | 측정 노이즈는 EDMD 추정을 **편향(bias)** 시킵니다. forward-backward DMD, TLS-DMD 등 대안 존재 |
| **검증 방법** | 1-step 오차 말고 **long-horizon rollout**으로 검증하세요. 6번의 투영 누적 때문에 1-step만 보면 속습니다 |

```python
# 1. 데이터 수집
X, Y = collect_snapshot_pairs()      # (N_x, M) each,  Y[:,i] = T(X[:,i])

# 2. 리프팅
PsiX, PsiY = psi(X), psi(Y)          # (N_psi, M)

# 3~4. 최소자승 (닫힌 형태) — 반복 없음
K = PsiY @ np.linalg.pinv(PsiX)      # (N_psi, N_psi)

# 5. 예측 (multi-step rollout)
z = psi(x0)
for t in range(horizon):
    z = K @ z
    x_pred[t] = z[:N_x]              # full-state observability 가정 시
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| **(a)** 의사역행렬이 왜 최소자승 해인가 | ↑ 4번의 접힌 섹션 (정규방정식 유도) |
| 의사역행렬 자체가 뭔지 (기초부터) | [[Pseudo-inverse]] — 정의·SVD·수치 안정성 |
| **(b)** 투영 연산자의 기하학적 의미 | ↑ 6번의 접힌 섹션 (평면과 그림자 그림) |
| **(c)** 불변 부분공간을 실제로 어떻게 찾는가 | [[Koopman-Invariant Subspace]] (SSD/T-SSD), [[Consistency Index]] |
| 딕셔너리 설계를 아예 우회하는 법 | [[HVOK]] (시간지연 임베딩) |
| 제어 입력 $u$ 를 넣으려면 | [[Koopman with Control Input]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[Pseudo-inverse]] — (7)식의 $\dagger$ 가 무엇인가 (선형대수 기초)
> - [[Koopman Operator]] — 왜 $K$ 를 구하려 하는가 (상위 개념)
> - [[Observable Function]] — $\Psi$ 를 어떻게 고르는가 (7번의 답)
> - [[Koopman-Invariant Subspace]] — EDMD가 정확해지는 조건
> - [[Consistency Index]] — 1-step residual의 함정과 대안 지표
> - [[Koopman Eigenfunction]] — 5번 고유함수의 물리적 의미
> - [[HVOK]] — 딕셔너리 설계를 우회하는 대안
> - [[Koopman with Control Input]] — 입력 $u$ 를 포함한 확장
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
