---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Theory
aliases:
  - Koopman 고유함수
  - Eigenfunction
  - Koopman Mode
keywords: eigenfunction, eigenvalue, spectrum, Koopman mode decomposition
related notes: "[[Koopman Operator]], [[EDMD]], [[Koopman-Invariant Subspace]]"
dg-publish: false
---

# Koopman Eigenfunction (쿠프만 고유함수)

> [!abstract] 한 문장 요약
> Koopman 고유함수를 따라가면 **비선형 궤적이 $\phi(x_t) = \lambda^t\phi(x_0)$ 라는 단 한 줄로 예측됩니다** — 시뮬레이션 없이, 초기값과 고유값만으로 임의 시점의 미래를 알 수 있다는 뜻입니다.

아래 1→6번을 순서대로 읽으면 이 놀라운 한 줄이 어디서 나오고, 어떻게 데이터로 구하는지가 쌓입니다.

---

## 1. 정의

함수 $\phi \in \mathcal{F}$ 와 스칼라 $\lambda \in \mathbb{C}$ 가

$$
\boxed{\;\mathcal{K}\phi = \lambda\phi\;}
$$

를 만족하면, $\phi$ 를 **Koopman 고유함수**, $\lambda$ 를 **Koopman 고유값**이라고 부릅니다.

$\mathcal{K}\phi = \phi \circ T$ 이므로, 이것을 풀어쓰면 의미가 더 분명해집니다.

$$
\phi\big(T(x)\big) = \lambda\,\phi(x), \qquad \forall x \in \mathcal{X}
$$

**즉, 상태를 한 스텝 전파한 뒤 $\phi$ 로 재면, 원래 값에 그냥 $\lambda$ 를 곱한 것과 같다**는 뜻입니다. 언뜻 평범해 보이는 이 조건이 왜 그렇게 강력한지는 2번에서 바로 드러납니다.

---

## 2. 왜 강력한가 — 동역학의 완전한 대각화

고유함수를 따라 시간을 전개해봅시다.

$$
\phi(x_t) = \lambda\,\phi(x_{t-1}) = \lambda^2\phi(x_{t-2}) = \cdots = \boxed{\lambda^t\,\phi(x_0)}
$$

**비선형 시스템의 궤적이 한 줄의 지수 함수로 예측됩니다.** 시뮬레이션 없이, 초기값 $x_0$ 하나만 알면 임의 시점 $t$ 의 값이 곧바로 나온다는 뜻입니다. 원래 시스템이 아무리 비선형이어도, 고유함수라는 "올바른 좌표"로 보면 동역학은 스칼라 곱셈 하나로 줄어듭니다. 이것이 Koopman 이론이 "선형성의 매력"이라고 불리는 이유입니다.

### 고유값의 물리적 의미

그렇다면 $\lambda$ 자체는 무엇을 말해줄까요. 이산시간에서 $\lambda \in \mathbb{C}$ 를 극형식으로 $\lambda = |\lambda|e^{i\theta}$ 라 쓰면, 크기 $|\lambda|$ 가 거동을 결정합니다.

| 조건 | 거동 | 해석 |
|:---|:---|:---|
| $\|\lambda\| < 1$ | $\phi(x_t) \to 0$ | **감쇠 모드** — 이 방향으로 수축 |
| $\|\lambda\| = 1$ | 크기 유지, 각속도 $\theta$ 로 회전 | **지속 진동 / 보존량** |
| $\|\lambda\| > 1$ | 발산 | **불안정 모드** |
| $\lambda = 1$ | $\phi(x_t) = \phi(x_0)$ 상수 | **불변량(invariant)** — 보존되는 물리량 |

> [!success] 실용적 함의
> $\lambda = 1$ 인 고유함수는 **에너지, 운동량 같은 보존량**에 대응합니다. $|\lambda| = 1$ 인 것들은 **끌개(attractor)의 위상 좌표**를 줍니다. 즉 고유함수를 찾는 것은 곧 **비선형 시스템의 자연 좌표계를 찾는 것**이라고 이해하면 됩니다.

<details>
<summary><b>연속시간과의 관계</b></summary>

연속시간에서는 [[Koopman Operator|Koopman generator]] $\mathcal{L}_G\phi = \sigma\phi$ 이고, 이산시간 고유값과는 $\lambda = e^{\sigma \Delta t}$ 관계가 성립합니다. $\mathrm{Re}(\sigma) < 0$ 이 감쇠, $\mathrm{Im}(\sigma)$ 가 진동 주파수에 대응합니다.

</details>

---

## 3. 고유함수 = 1차원 불변 부분공간

한 스텝 전파가 스칼라 곱셈으로 끝난다는 사실은, 고유함수가 만드는 공간 자체에도 특별한 성질을 부여합니다. $\mathcal{S} = \mathrm{span}\{\phi\}$ 를 생각하면

$$
\mathcal{K}(c\phi) = c\lambda\phi \in \mathcal{S}
$$

이므로, **$\mathcal{S}$ 는 자동으로 [[Koopman-Invariant Subspace|Koopman 불변]]**이 됩니다. 즉 고유함수 하나가 이미 (1차원짜리) 완벽한 불변 부분공간인 셈입니다.

> [!important] 관점의 전환
> 여기서 **좋은 딕셔너리를 찾는 문제 = 고유함수들을 찾는 문제**로 바뀝니다. 고유함수 $\phi_1, \dots, \phi_r$ 을 딕셔너리로 쓰면
> $$
> K = \mathrm{diag}(\lambda_1, \dots, \lambda_r)
> $$
> 즉 **완전 대각 행렬**이 되어 모드들이 서로 완전히 분리됩니다. 이것이 이론적으로 가장 이상적인 리프팅입니다.

### 곱셈 성질 — 소수의 고유함수로 무한히 생성

고유함수는 또 하나의 유용한 성질을 갖습니다. $\phi_1, \phi_2$ 가 각각 $\lambda_1, \lambda_2$ 에 대응하는 고유함수라면, **그 곱도 고유함수**가 됩니다.

$$
\mathcal{K}(\phi_1\phi_2)(x) = \phi_1(T(x))\phi_2(T(x)) = \lambda_1\lambda_2\,\phi_1(x)\phi_2(x)
$$

$$
\Rightarrow\ \mathcal{K}(\phi_1\phi_2) = (\lambda_1\lambda_2)(\phi_1\phi_2)
$$

일반화하면 $\phi_1^{m_1}\phi_2^{m_2}\cdots$ 가 고유값 $\lambda_1^{m_1}\lambda_2^{m_2}\cdots$ 의 고유함수입니다. **소수의 고유함수만 찾아도 무한히 많은 고유함수를 생성할 수 있다**는 뜻이며, 이것이 Koopman 스펙트럼이 조밀해지는 이유이기도 합니다.

여기까지가 "고유함수란 무엇이고 왜 좋은가"였습니다. 문제는 실제 시스템에서 이 고유함수 $\phi$ 를 어떻게 손에 넣느냐입니다 — 4번에서 다룹니다.

---

## 4. 데이터로 구하기 — EDMD 좌고유벡터

[[EDMD]] 노트의 (9)식이 정확히 이 절차입니다.

**Step 1.** EDMD로 $K_{\mathrm{EDMD}} = \Psi(Y)\Psi(X)^\dagger$ 를 구합니다.

**Step 2.** $K_{\mathrm{EDMD}}$ 의 **좌고유벡터(left eigenvector)** $v$ 를 구합니다.

$$
v^\top K_{\mathrm{EDMD}} = \lambda\,v^\top
$$

**Step 3.** 근사 고유함수를 조합합니다.

$$
\phi_{\mathrm{EDMD}}(\cdot) = v^\top\psi(\cdot) = \sum_{i=1}^{N_\psi} v_i\,\psi_i(\cdot)
$$

**검증**: 이 $\phi$ 에 대해 EDMD 예측자는

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}\phi} = v^\top K_{\mathrm{EDMD}}\psi = \lambda v^\top \psi = \lambda\phi \tag{논문 (9)}
$$

정확히 고유함수 관계를 재현합니다. 즉 1번의 정의가 데이터 기반 절차로 그대로 복원되는 것입니다.

<details>
<summary><b>왜 "좌"고유벡터인가</b></summary>

$K$ 는 딕셔너리 계수 벡터에 작용합니다. 함수 $f = v^\top\psi$ 의 계수는 행벡터 $v^\top$ 이므로, $\mathcal{K}f$ 의 계수는 $v^\top K$ 입니다. 따라서 $f$ 가 고유함수이려면 $v^\top K = \lambda v^\top$, 즉 **좌고유벡터** 조건이 됩니다.

우고유벡터를 쓰면 틀립니다. 다만 규약에 따라 $K$ 의 전치를 쓰면 좌우가 뒤바뀌므로 **본인 코드의 규약을 반드시 확인**해야 합니다.

</details>

---

## 5. 로보틱스 응용

고유함수의 두 성질 — $\lambda$ 의 물리적 의미(2번)와 데이터로 뽑아낼 수 있다는 사실(4번) — 은 실제 로봇 제어에서 다음과 같이 쓰입니다.

### Koopman 기반 Lyapunov 함수 [18]

$|\lambda| < 1$ 인 고유함수들로부터 **constructive control Lyapunov function**을 만들 수 있습니다. 예컨대 $V(x) = \sum_i |\phi_i(x)|^2$ 형태로 두면

$$
V(x_{t+1}) = \sum_i |\lambda_i|^2|\phi_i(x_t)|^2 < V(x_t)
$$

가 자동으로 성립합니다. **데이터로 학습한 모델에 안정성 증명서를 붙일 수 있다**는 뜻이며, 논문 서론이 강조하는 "formal properties"의 대표 사례입니다.

### 멀티로터 지면 효과 [78]

Folkestad et al.은 멀티로터가 착륙할 때 발생하는 **ground effect**(모델링이 어려운 공력)를 다루기 위해, 에피소드마다 **Koopman 고유함수 쌍을 반복 학습**하고 그로부터 실시간 제어 입력을 얻었습니다. 명목 제어 법칙에 비선형 보정을 점진적으로 더해가는 구조입니다.

---

## 6. 주의사항

지금까지의 이야기는 고유함수를 "정확히" 얻었을 때를 전제합니다. 실제로는 다음 세 가지에 주의해야 합니다.

> [!warning] 스펙트럼의 미묘함
> - **연속 스펙트럼**: 카오스적 시스템에서는 Koopman 연산자가 이산 고유값뿐 아니라 **연속 스펙트럼**을 가집니다. 유한 EDMD로는 원리적으로 포착할 수 없습니다.
> - **spurious eigenvalue**: 딕셔너리가 불변이 아니면 $K_{\mathrm{EDMD}}$ 의 고유값 중 상당수가 시스템과 무관한 **허위 고유값**입니다. residual 기반 필터링이 필요합니다.
> - **약수렴만 보장**: Korda & Mezić [30]의 수렴 결과는 고유함수에 대해 **약수렴(weak convergence)**만 줍니다. 점별(pointwise) 수렴이 아닙니다.

---

## 📌 전체 흐름 한 눈에

```
 ①  정의               𝒦φ = λφ  ⟺  φ(T(x)) = λφ(x)
         │
 ②  왜 강력한가         φ(x_t) = λᵗφ(x₀)  ← 시뮬레이션 없이 임의 시점 예측
         │              |λ|<1 감쇠 / |λ|=1 보존·진동 / |λ|>1 발산
         │
 ③  구조적 의미         span{φ} = 1차원 불변 부분공간
         │              → 고유함수들을 모으면 K = diag(λ₁...λᵣ)
         │              → 곱셈 성질로 소수의 φ에서 무한 생성
         │
 ④  데이터로 구하기      EDMD 좌고유벡터: v⊤K_EDMD = λv⊤  →  φ = v⊤ψ
         │
 ⑤  응용               Lyapunov 함수 [18], 멀티로터 지면효과 [78]
         │
 ⑥  주의               연속 스펙트럼 / spurious eigenvalue / 약수렴
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| $K_{\mathrm{EDMD}}$ 를 어떻게 구하는지 (최소자승 전 과정) | [[EDMD]] |
| 불변 부분공간 자체의 정의와 조건 | [[Koopman-Invariant Subspace]] |
| 딕셔너리(관측함수)를 어떻게 설계하는지 | [[Observable Function]] |
| Koopman 연산자·generator의 상위 개념 | [[Koopman Operator]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 상위 개념, 연속시간 generator
> - [[EDMD]] — 좌고유벡터로 고유함수 추출
> - [[Koopman-Invariant Subspace]] — 고유함수 = 1차원 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
