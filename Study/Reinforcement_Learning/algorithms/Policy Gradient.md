---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 정책 경사법
  - Policy Gradient Methods
  - PG
keywords:
  - Policy Gradient
  - Policy-based
  - Parameterized Policy
  - Average State Value
  - Average Reward
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 9
author:
url:
---

# Policy Gradient

```ad-note
title: Summary
collapse: true

- ==Policy Gradient: 파라미터화된 정책 $\pi(a|s,\theta)$를 직접 최적화==하는 방법
- ==Metric: 스칼라 목적함수== — Average State Value ($\bar{v}_\pi$), Average Reward ($\bar{r}_\pi$)
- ==Policy Gradient Theorem: $\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \eta, A \sim \pi}[\nabla_\theta \ln \pi \cdot q_\pi]$==
- ==Softmax policy==로 $\pi > 0$ 보장 → Log-derivative trick 적용 가능
```

![[Pasted image 20260112064914.png|700]]

## Definition

<!-- Section 9.1 -->
==스칼라 목적함수 $J(\theta)$를 최적화하여 파라미터화된 정책 $\pi(a|s,\theta)$를 직접 학습==하는 방법

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta J(\theta_t)$$

- $J(\theta)$: 정책 성능을 나타내는 ==스칼라 metric==
- $\nabla_\theta J$: $J$의 $\theta$에 대한 gradient
- $\alpha$: 학습률

| 접근법 | 표현 방식 | 특징 |
|:---|:---|:---|
| **Value-based** | $q(s,a)$ 추정 → greedy 정책 | 간접적 정책 도출 |
| **Policy-based** | ==$\pi(a\|s,\theta)$ 직접 최적화== | 정책 파라미터 직접 학습 |

<br/><br/>

## Policy Representation

<!-- Section 9.1 -->
![[Pasted image 20260112062814.png|500]]

### Tabular Representation

==모든 상태의 행동 확률을 테이블로 저장==:

|  | $a_1$ | $a_2$ | $a_3$ | $a_4$ | $a_5$ |
|:---|:---:|:---:|:---:|:---:|:---:|
| $s_1$ | $\pi(a_1\|s_1)$ | $\pi(a_2\|s_1)$ | $\pi(a_3\|s_1)$ | $\pi(a_4\|s_1)$ | $\pi(a_5\|s_1)$ |
| $\vdots$ | $\vdots$ | $\vdots$ | $\vdots$ | $\vdots$ | $\vdots$ |
| $s_9$ | $\pi(a_1\|s_9)$ | $\pi(a_2\|s_9)$ | $\pi(a_3\|s_9)$ | $\pi(a_4\|s_9)$ | $\pi(a_5\|s_9)$ |

- **최적 정책 정의**: ==모든 state value를 최대화==하는 정책
- **정책 업데이트**: 테이블 entry를 ==직접 변경==
- **저장 공간**: $|\mathcal{S}| \times |\mathcal{A}|$개의 확률값
- **한계**: 대규모/연속 공간 불가

<br/>

### Function Representation

==$\pi(a|s,\theta)$로 파라미터화==하여 정책 표현:

- **최적 정책 정의**: ==스칼라 metric $J(\theta)$를 최대화==하는 정책
- **정책 업데이트**: ==파라미터 $\theta$를 변경==
- **저장 공간**: ==$m$개 파라미터== ($m \ll |\mathcal{S}| \times |\mathcal{A}|$)
- **장점**: 연속 공간 처리 가능, ==유사 상태 간 경험 전파== (일반화)

```ad-info
title: Note - Analogy to Value Function Approximation

[[Value Function Approximation]]과 동일한 아이디어:
- VFA: $v(s) \to \hat{v}(s,w)$ — 가치 함수 근사
- Policy Gradient: $\pi(a|s) \to \pi(a|s,\theta)$ — ==정책 함수 근사==

둘 다 ==테이블 → 파라미터화된 함수==로의 전환
```

<br/>

### Softmax Policy

<!-- Section 9.4 -->
```ad-info
title: Note - Why Softmax?

[[#Policy Gradient Theorem|Policy Gradient Theorem]]의 expectation form은 ==$\nabla_\theta \ln \pi$==를 사용
```

$\ln \pi(a|s,\theta)$가 유효하려면 ==$\pi(a|s,\theta) > 0$==이어야 함 → ==Softmax policy== 사용:

$$\pi(a|s,\theta) = \frac{e^{h(s,a,\theta)}}{\sum_{a' \in \mathcal{A}} e^{h(s,a',\theta)}}, \quad a \in \mathcal{A}$$

- $h(s,a,\theta)$: 상태 $s$에서 행동 $a$를 선택하는 ==preference (선호도)==
- $\pi(a|s,\theta) \in (0, 1)$, $\sum_a \pi(a|s,\theta) = 1$ 만족
- ==Neural network==으로 구현: 입력 $s$, 출력층은 softmax layer
- $\pi(a|s,\theta) > 0$ for all $a$이므로 정책은 ==stochastic이며 exploratory==

<br/><br/>

## State Distribution

<!-- Section 9.2 -->
Metric 정의를 위해 ==상태에 대한 가중치 분포 $d(s)$==를 선택해야 함

- $d(s)$: agent가 상태 $s$에 ==있을 확률== (방문 확률)
- $d(s) \geq 0$, $\sum_s d(s) = 1$

### Policy-Independent Distribution ($d_0$)

==$d$가 정책 $\pi$와 독립==인 경우:

- **균등 분포**: 모든 상태 동등하게 취급
  $$d_0(s) = 1/|\mathcal{S}|$$
- **특정 시작 상태**: 특정 상태에서만 시작
  $$d_0(s_0) = 1, \quad d_0(s \neq s_0) = 0$$

<br/>

### Policy-Dependent Distribution ($d_\pi$)

==$d$가 정책 $\pi$에 의존==하는 경우 — ==[[Stationary Distribution]]== 사용:

$$d_\pi^T P_\pi = d_\pi^T$$

- $P_\pi$: 정책 $\pi$ 하의 상태 전이 확률 행렬
- ==장기적으로 자주 방문하는 상태==에 높은 가중치
- **존재 조건**: ==Exploratory policy== (예: $\varepsilon$-greedy) 사용 시 유일한 $d_\pi$ 존재

**핵심 성질**:
- ==$P_\pi$의 고유값 1에 대응하는 좌 고유벡터==
- ==초기 분포와 무관하게== $d_\pi$로 수렴
- $d_\pi(s) > 0$ for all $s$ (Regular Markov process에서)
- **실용적 관점**: $d_\pi$를 ==명시적으로 계산할 필요 없음== — 정책 $\pi$를 따라 샘플링하면 자연스럽게 $d_\pi$에 따라 상태 방문

<br/><br/>

## Metrics for Optimal Policy

<!-- Section 9.2 -->
정책이 함수로 표현될 때 ==최적 정책을 정의하기 위한 스칼라 metric==:

- ==모든 metric은 $\pi$의 함수== → $\theta$로 파라미터화되므로 ==$\theta$의 함수==
- 최적 $\theta$를 찾아 metric 최대화가 목표

<br/>

### Average State Value

==상태 가치의 가중 평균==:

$$\bar{v}_\pi = \sum_{s \in \mathcal{S}} d(s) v_\pi(s) = \mathbb{E}_{S \sim d}[v_\pi(S)]$$

- $d(s)$: 상태 $s$의 ==가중치== (확률 분포)
- $\bar{v}_\pi$: stationary distribution $d_\pi$ 사용 시
- $\bar{v}_\pi^0$: policy-independent $d_0$ 사용 시

**동등한 표현**:

$$J(\theta) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R_{t+1}\right] = \bar{v}_\pi \quad \text{(Discounted Return)}$$

```ad-important
title: Proof - Average State Value Equivalence
collapse: true

[[Law of Total Expectation]] 적용:

$$\mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R_{t+1}\right] = \sum_{s \in \mathcal{S}} d(s) \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t R_{t+1} \middle| S_0 = s\right] = \sum_{s \in \mathcal{S}} d(s) v_\pi(s) = \bar{v}_\pi$$

- 첫 번째 등호: ==[[Law of Total Expectation]]==
- 두 번째 등호: ==State value 정의== ($v_\pi(s) = \mathbb{E}[\sum \gamma^t R_{t+1} | S_0 = s]$)
```

<br/>

### Average Reward

==즉시 보상의 가중 평균==:

$$\bar{r}_\pi = \sum_{s \in \mathcal{S}} d_\pi(s) r_\pi(s) = \mathbb{E}_{S \sim d_\pi}[r_\pi(S)]$$

- $d_\pi$: ==[[Stationary Distribution]]==
- $r_\pi(s) = \sum_{a \in \mathcal{A}} \pi(a|s,\theta) r(s,a)$: 상태 $s$에서의 ==즉시 보상 기대값==

**동등한 표현**:

$$J(\theta) = \lim_{n \to \infty} \frac{1}{n} \mathbb{E}\left[\sum_{t=0}^{n-1} R_{t+1}\right] = \bar{r}_\pi \quad \text{(Long-run Average)}$$

```ad-important
title: Proof - Average Reward Equivalence
collapse: true

**Step 1**: 임의의 시작 상태 $s_0 \in \mathcal{S}$에 대해:

$$\lim_{n \to \infty} \frac{1}{n} \mathbb{E}\left[\sum_{t=0}^{n-1} R_{t+1} \middle| S_0 = s_0\right] = \lim_{n \to \infty} \frac{1}{n} \sum_{t=0}^{n-1} \mathbb{E}[R_{t+1}|S_0 = s_0] = \lim_{t \to \infty} \mathbb{E}[R_{t+1}|S_0 = s_0]$$

마지막 등호는 ==Cesaro mean 성질==: 수열 $\{a_k\}$가 $\lim_{k \to \infty} a_k$로 수렴하면, $\lim_{n \to \infty} \frac{1}{n} \sum_{k=1}^n a_k = \lim_{k \to \infty} a_k$

[[Law of Total Expectation]]으로 전개:

$$\mathbb{E}[R_{t+1}|S_0 = s_0] = \sum_{s \in \mathcal{S}} r_\pi(s) \cdot p^{(t)}(s|s_0)$$

$p^{(t)}(s|s_0)$: $s_0$에서 $s$로 ==정확히 $t$ 스텝만에 전이==할 확률. [[Stationary Distribution#Limiting Distribution|Stationary distribution]] 정의에 의해 $\lim_{t \to \infty} p^{(t)}(s|s_0) = d_\pi(s)$ (==시작 상태와 무관==)

$$\lim_{t \to \infty} \mathbb{E}[R_{t+1}|S_0 = s_0] = \sum_{s \in \mathcal{S}} r_\pi(s) \cdot d_\pi(s) = \bar{r}_\pi$$

**Step 2**: [[Law of Total Expectation]] 적용하여 임의의 상태 분포 $d$에 대해 최종 결과:

$$\lim_{n \to \infty} \frac{1}{n} \mathbb{E}\left[\sum_{t=0}^{n-1} R_{t+1}\right] = \sum_{s \in \mathcal{S}} d(s) \cdot \bar{r}_\pi = \bar{r}_\pi$$
```

<br/>

### Comparison of Metrics

| 특성 | Average State Value ($\bar{v}_\pi$) | Average Reward ($\bar{r}_\pi$) |
|:---|:---|:---|
| **정의** | $\sum_s d(s) v_\pi(s)$ | $\sum_s d_\pi(s) r_\pi(s)$ |
| **동등 표현** | $\mathbb{E}[\sum_{t=0}^{\infty} \gamma^t R_{t+1}]$ | $\lim_{n \to \infty} \frac{1}{n} \mathbb{E}[\sum_{t=0}^{n-1} R_{t+1}]$ |
| **Discount** | $\gamma^t$로 discount | 없음 |
| **수렴 조건** | $\gamma < 1$이면 자연 수렴 | $\frac{1}{n}$으로 평균화하여 수렴 |

```ad-important
title: Lemma - Equivalence between $\bar{v}_\pi$ and $\bar{r}_\pi$

Discounted case ($\gamma \in (0,1)$)에서:

$$\bar{r}_\pi = (1 - \gamma)\bar{v}_\pi$$

두 metric을 ==동시에 최대화== 가능
```

```ad-important
title: Proof - Lemma
collapse: true

$\bar{v}_\pi = d_\pi^T v_\pi$, $\bar{r}_\pi = d_\pi^T r_\pi$이고, [[Bellman Equation]]에서 $v_\pi = r_\pi + \gamma P_\pi v_\pi$

양변에 $d_\pi^T$를 곱하면:

$$\bar{v}_\pi = d_\pi^T (r_\pi + \gamma P_\pi v_\pi) = d_\pi^T r_\pi + \gamma d_\pi^T P_\pi v_\pi$$

[[Stationary Distribution]] 정의 $d_\pi^T P_\pi = d_\pi^T$에 의해:

$$\bar{v}_\pi = \bar{r}_\pi + \gamma d_\pi^T v_\pi = \bar{r}_\pi + \gamma \bar{v}_\pi$$

정리하면:

$$(1-\gamma)\bar{v}_\pi = \bar{r}_\pi$$
```

<br/><br/>

## Policy Gradient Theorem

<!-- Section 9.3, 9.4 -->
Metric의 gradient를 ==계산 가능한 형태==로 표현하는 핵심 정리

```ad-important
title: Theorem - Policy Gradient Theorem

**Summation Form** (이론적 분석용):

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \eta(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a)$$

**Expectation Form** (샘플 기반 추정용):

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \eta, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) \cdot q_\pi(S, A) \right]$$

- $\eta(s)$: ==상태 분포== (metric에 따라 다름)
- $\nabla_\theta \pi$: 정책의 gradient
- $q_\pi(s,a)$: action value
```

<br/>

### Log-Derivative Trick

Gradient를 ==기대값 형태로 표현==하기 위해 $\ln \pi$ 사용:

$$\nabla_\theta \pi = \pi \cdot \nabla_\theta \ln \pi \quad \Rightarrow \quad \sum_a \nabla_\theta \pi \cdot q = \sum_a \pi \cdot \nabla_\theta \ln \pi \cdot q = \mathbb{E}_{A \sim \pi}[\nabla_\theta \ln \pi \cdot q]$$

**장점**: 기대값 형태 → ==샘플로 근사 가능== ([[Stochastic Approximation]])
- True gradient: $\mathbb{E}[\nabla_\theta \ln \pi \cdot q_\pi]$
- Stochastic gradient: $\nabla_\theta \ln \pi(a_t|s_t) \cdot q_t(s_t, a_t)$

```ad-important
title: Proof - Log-Derivative Trick
collapse: true

**Step 1**: Summation form을 기대값으로 변환

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \eta(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a) = \mathbb{E}_{S \sim \eta} \left[ \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|S, \theta) q_\pi(S, a) \right]$$

**Step 2**: Log-derivative (Score function) 적용

$$\nabla_\theta \ln \pi(a|s, \theta) = \frac{\nabla_\theta \pi(a|s, \theta)}{\pi(a|s, \theta)} \quad \Rightarrow \quad \nabla_\theta \pi(a|s, \theta) = \pi(a|s, \theta) \nabla_\theta \ln \pi(a|s, \theta)$$

**Step 3**: 대입하여 expectation form 유도

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \eta} \left[ \sum_{a \in \mathcal{A}} \pi(a|S, \theta) \nabla_\theta \ln \pi(a|S, \theta) q_\pi(S, a) \right]$$

$\sum_a \pi(a|S,\theta) [\cdot]$는 $A \sim \pi(S,\theta)$에 대한 기대값이므로:

$$= \mathbb{E}_{S \sim \eta, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right]$$
```

<br/>

### State Distribution by Metric

Metric에 따라 상태 분포 $\eta$가 달라짐:

| Metric | $J(\theta)$ | $\eta$ | Case | 등호 |
|:---|:---|:---|:---|:---|
| Average State Value (policy-independent) | $\bar{v}_\pi^0$ | $\rho_\pi$ | Discounted | $=$ |
| Average State Value (policy-dependent) | $\bar{v}_\pi$ | $d_\pi$ | Discounted | $\approx$ |
| Average Reward | $\bar{r}_\pi$ | $d_\pi$ | Discounted | $\approx$ |
| Average Reward | $\bar{r}_\pi$ | $d_\pi$ | ==Undiscounted== | $=$ |

- Discounted $\bar{v}_\pi$, $\bar{r}_\pi$: ==$\gamma \to 1$일수록 근사가 정확==
- Undiscounted $\bar{r}_\pi$: ==정확한 등호== (가장 우아한 형태)

**$d$ vs $\eta$ 구분**: ==$d$는 Metric 정의==에서, ==$\eta$는 Gradient 공식==에서 사용

| Metric | $d$ (Metric) | $\eta$ (Gradient) | 관계 |
|:---|:---|:---|:---|
| $\bar{v}_\pi^0$ | $d_0$ | $\rho_\pi$ | ==$d \neq \eta$== |
| $\bar{v}_\pi$, $\bar{r}_\pi$ | $d_\pi$ | $d_\pi$ | $d = \eta$ |

- **$\bar{v}_\pi^0$의 경우**: Metric 정의는 $d_0$를 사용하지만, ==gradient 유도 과정에서 $\rho_\pi$가 등장==
- $\rho_\pi(s) = \sum_{s'} d_0(s') \Pr_\pi(s|s')$: ==Discounted state distribution==

```ad-info
title: Note - Complexity of Gradient Derivation

Policy Gradient의 ==기본 아이디어는 단순==하지만, gradient 유도는 복잡:
- 여러 metric ($\bar{v}_\pi^0$, $\bar{v}_\pi$, $\bar{r}_\pi$)
- Discounted vs Undiscounted case
- 각 시나리오마다 다른 수학적 처리 필요

**실용적 관점**: Policy Gradient Theorem의 ==결과만 알면 충분== — 증명은 선택적
```

<br/><br/>

## Gradient Derivation

<!-- Section 9.5, 9.6 -->
### Gradient of $v_\pi(s)$

Metric gradient 유도의 ==핵심 보조정리== — 개별 상태의 value gradient:

```ad-important
title: Lemma - Gradient of $v_\pi(s)$

Discounted case에서 임의의 $s \in \mathcal{S}$에 대해:

$$\nabla_\theta v_\pi(s) = \sum_{s' \in \mathcal{S}} \Pr_\pi(s'|s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a)$$

- $\Pr_\pi(s'|s) \doteq \sum_{k=0}^{\infty} \gamma^k [P_\pi^k]_{ss'} = [(I_n - \gamma P_\pi)^{-1}]_{ss'}$: ==Discounted total probability==
- $[P_\pi^k]_{ss'}$: 정책 $\pi$ 하에서 $s$에서 $s'$로 ==정확히 $k$ 스텝==만에 전이할 확률
```

**확률론적 해석**: $(I_n - \gamma P_\pi)^{-1} = I + \gamma P_\pi + \gamma^2 P_\pi^2 + \cdots$이므로 $\Pr_\pi(s'|s)$는 ==$s$에서 $s'$로 가는 모든 경로의 할인된 확률 합== — "총 전이 확률"이 아닌 =="할인된 총 전이 확률"==

```ad-important
title: Proof - Gradient of $v_\pi(s)$
collapse: true

**Step 1**: Product rule 적용

$$\nabla_\theta v_\pi(s) = \nabla_\theta \left[ \sum_{a \in \mathcal{A}} \pi(a|s,\theta) q_\pi(s,a) \right] = \sum_{a \in \mathcal{A}} \left[ \nabla_\theta \pi(a|s,\theta) q_\pi(s,a) + \pi(a|s,\theta) \nabla_\theta q_\pi(s,a) \right]$$

**Step 2**: $\nabla_\theta q_\pi(s,a)$ 계산

$q_\pi(s,a) = r(s,a) + \gamma \sum_{s'} p(s'|s,a) v_\pi(s')$이고, $r(s,a)$는 $\theta$와 독립이므로:

$$\nabla_\theta q_\pi(s,a) = \gamma \sum_{s' \in \mathcal{S}} p(s'|s,a) \nabla_\theta v_\pi(s')$$

**Step 3**: 대입 및 정리

$$\nabla_\theta v_\pi(s) = \underbrace{\sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s,\theta) q_\pi(s,a)}_{u(s)} + \gamma \sum_{s' \in \mathcal{S}} [P_\pi]_{ss'} \nabla_\theta v_\pi(s')$$

**Step 4**: Matrix-vector form (Kronecker product)

$u(s) = \sum_a \nabla_\theta \pi(a|s,\theta) q_\pi(s,a)$로 정의하면:

$$\nabla_\theta v_\pi = u + \gamma (P_\pi \otimes I_m) \nabla_\theta v_\pi$$

$\nabla_\theta v_\pi \in \mathbb{R}^{mn}$: 모든 상태의 gradient를 쌓은 벡터 ($m$: 파라미터 차원, $n = |\mathcal{S}|$)

**Step 5**: 재귀 방정식 풀이

$$(I_{nm} - \gamma P_\pi \otimes I_m) \nabla_\theta v_\pi = u \quad \Rightarrow \quad \nabla_\theta v_\pi = [(I_n - \gamma P_\pi)^{-1} \otimes I_m] u$$

**Step 6**: 개별 상태로 분해

$$\nabla_\theta v_\pi(s) = \sum_{s' \in \mathcal{S}} [(I_n - \gamma P_\pi)^{-1}]_{ss'} u(s') = \sum_{s' \in \mathcal{S}} \Pr_\pi(s'|s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s',\theta) q_\pi(s',a)$$
```

<br/>

### Discounted Case

<!-- Section 9.5 -->
#### Gradient of $\bar{v}_\pi^0$

Policy-independent distribution $d_0$를 사용하는 경우 ($\gamma \in (0,1)$):

$$\nabla_\theta \bar{v}_\pi^0 = \mathbb{E}_{S \sim \rho_\pi, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right]$$

**Discounted State Distribution**:

$$\rho_\pi(s) = \sum_{s' \in \mathcal{S}} d_0(s') \Pr_\pi(s|s')$$

- $\Pr_\pi(s|s') \doteq \sum_{k=0}^{\infty} \gamma^k [P_\pi^k]_{s's}$: $s'$에서 $s$로의 할인된 전이 확률 합
- Metric 정의에서는 $d_0$를 사용하지만, ==gradient에서는 $\rho_\pi$가 등장==
- $\rho_\pi$는 $d_0$에서 시작하여 ==정책 $\pi$를 따라 상태 $s$에 방문할 확률의 할인된 분포==

```ad-important
title: Proof - Gradient of $\bar{v}_\pi^0$
collapse: true

$d_0(s)$가 $\pi$와 독립이므로:

$$\nabla_\theta \bar{v}_\pi^0 = \nabla_\theta \sum_{s \in \mathcal{S}} d_0(s) v_\pi(s) = \sum_{s \in \mathcal{S}} d_0(s) \nabla_\theta v_\pi(s)$$

$\nabla_\theta v_\pi(s)$를 대입:

$$= \sum_{s \in \mathcal{S}} d_0(s) \sum_{s' \in \mathcal{S}} \Pr_\pi(s'|s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a)$$

합의 순서 교환:

$$= \sum_{s' \in \mathcal{S}} \underbrace{\left( \sum_{s \in \mathcal{S}} d_0(s) \Pr_\pi(s'|s) \right)}_{\rho_\pi(s')} \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a)$$

$s' \to s$로 변수 변경 후 log-derivative trick 적용:

$$= \mathbb{E}_{S \sim \rho_\pi, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right]$$
```

<br/>

#### Gradient of $\bar{v}_\pi$ and $\bar{r}_\pi$

Policy-dependent distribution $d_\pi$를 사용하는 경우 ($\gamma \in (0,1)$):

```ad-important
title: Theorem - Gradient of $\bar{r}_\pi$ and $\bar{v}_\pi$ (Discounted)

$$\begin{aligned}
\nabla_\theta \bar{r}_\pi = (1-\gamma) \nabla_\theta \bar{v}_\pi &\approx \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a) \\\\
&= \mathbb{E}_{S \sim d_\pi, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right]
\end{aligned}$$

==$\approx$는 근사== — $\gamma \to 1$일수록 정확 (증명의 Term 1 무시)
```

```ad-important
title: Proof - Gradient of $\bar{v}_\pi$ and $\bar{r}_\pi$ (Discounted)
collapse: true

**Step 1**: Product rule 적용

$$\nabla_\theta \bar{v}_\pi = \nabla_\theta \sum_{s \in \mathcal{S}} d_\pi(s) v_\pi(s) = \underbrace{\sum_{s \in \mathcal{S}} \nabla_\theta d_\pi(s) v_\pi(s)}_{\text{Term 1}} + \underbrace{\sum_{s \in \mathcal{S}} d_\pi(s) \nabla_\theta v_\pi(s)}_{\text{Term 2}}$$

**Step 2**: Term 2 계산

$$\sum_{s \in \mathcal{S}} d_\pi(s) \nabla_\theta v_\pi(s) = (d_\pi^T \otimes I_m) [(I_n - \gamma P_\pi)^{-1} \otimes I_m] u = [d_\pi^T (I_n - \gamma P_\pi)^{-1}] \otimes I_m \cdot u$$

**Step 3**: 핵심 항등식

[[Stationary Distribution]] 성질 $d_\pi^T P_\pi = d_\pi^T$로부터:

$$d_\pi^T (I_n - \gamma P_\pi)^{-1} = \frac{1}{1-\gamma} d_\pi^T$$

따라서:

$$\text{Term 2} = \frac{1}{1-\gamma} \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a)$$

**Step 4**: 근사

$\gamma \to 1$일 때 Term 2의 $\frac{1}{1-\gamma}$가 ==dominant==해지고, Term 1은 ==negligible==:

$$\nabla_\theta \bar{v}_\pi \approx \frac{1}{1-\gamma} \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a)$$

**Step 5**: $\bar{r}_\pi = (1-\gamma)\bar{v}_\pi$이므로:

$$\nabla_\theta \bar{r}_\pi \approx \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a) = \mathbb{E}_{S \sim d_\pi, A \sim \pi} \left[ \nabla_\theta \ln \pi q_\pi \right]$$
```

<br/>

### Undiscounted Case

<!-- Section 9.6 -->
$\bar{r}_\pi$의 gradient가 ==정확하게 유도==되는 경우 ($\gamma = 1$)

#### Discounted vs Undiscounted

| 항목 | Discounted ($\gamma < 1$) | Undiscounted ($\gamma = 1$) |
|:---|:---|:---|
| **Gradient 등호** | $\approx$ (근사) | ==$=$ (정확)== |
| **$\nabla_\theta d_\pi$ 처리** | 무시 ($\gamma \to 1$일 때) | ==자동 상쇄== |
| **$v_\pi(s)$ 정의** | $\sum_{t=0}^{\infty} \gamma^t \mathbb{E}[R_{t+1} \mid S_0 = s]$ | $\sum_{t=0}^{\infty} \mathbb{E}[R_{t+1} - \bar{r}_\pi \mid S_0 = s]$ |
| **$q_\pi(s,a)$ 재귀식** | $r(s,a) + \gamma \sum_{s'} p(s'\|s,a) v_\pi(s')$ | $r(s,a) - \bar{r}_\pi + \sum_{s'} p(s'\|s,a) v_\pi(s')$ |
| **수렴 방식** | $\gamma^t \to 0$ (할인) | $\mathbb{E}[R_t - \bar{r}_\pi] \to 0$ (평균 보정) |
| **재귀 관계** | [[Bellman Equation]] | ==Poisson Equation== |

**Undiscounted case에서 $v_\pi$ 재정의가 필요한 이유**: $\gamma = 1$이면 $\sum_{t=0}^{\infty} R_t$가 ==발산할 수 있음== → 각 보상에서 평균 $\bar{r}_\pi$를 빼서 ==differential value==로 재정의하여 수렴 보장

<br/>

#### Differential Value

Undiscounted case에서 수렴을 보장하기 위한 $v_\pi$, $q_\pi$의 ==재정의==:

$$v_\pi(s) \doteq \sum_{t=0}^{\infty} \mathbb{E}\left[R_{t+1} - \bar{r}_\pi \mid S_0 = s\right]$$

$$q_\pi(s, a) \doteq \sum_{t=0}^{\infty} \mathbb{E}\left[R_{t+1} - \bar{r}_\pi \mid S_0 = s, A_0 = a\right]$$

- ==Differential value== 또는 ==bias==라고 부름
- 상태 $s$가 평균보다 얼마나 좋은지/나쁜지를 측정
- Value 부호: ==양수/음수 가능== (discounted case는 보상 $\geq 0$일 때 $\geq 0$)

<br/>

#### Poisson Equation

Differential value $v_\pi$, $q_\pi$가 만족하는 ==재귀 관계==:

$$q_\pi(s, a) = \underbrace{r(s, a) - \bar{r}_\pi}_{\text{immediate reward} - \bar{r}_\pi} + \underbrace{\sum_{s' \in \mathcal{S}} p(s'|s, a) v_\pi(s')}_{\text{next state's differential value}}$$

**Matrix-Vector Form**:

$$v_\pi = r_\pi - \bar{r}_\pi \mathbf{1}_n + P_\pi v_\pi$$

정리: ==$(I_n - P_\pi) v_\pi = (I_n - \mathbf{1}_n d_\pi^T) r_\pi$==

| Bellman Equation | Poisson Equation |
|:---|:---|
| $v_\pi = r_\pi + \gamma P_\pi v_\pi$ | $v_\pi = r_\pi - \bar{r}_\pi \mathbf{1}_n + P_\pi v_\pi$ |
| $\gamma < 1$로 수렴 보장 | $-\bar{r}_\pi$로 수렴 보장 |

<br/>

#### Solution of Poisson Equation

**문제**: $I_n - P_\pi$가 ==singular==이므로 직접 역행렬 불가
- $(I_n - P_\pi)\mathbf{1}_n = 0$ ($P_\pi$는 행 합이 1인 전이 행렬)
- $\text{Null}(I_n - P_\pi) = \text{span}\{\mathbf{1}_n\}$

**해결**: $\mathbf{1}_n d_\pi^T$를 더해 ==invertible==하게 만듦: $A \doteq I_n - P_\pi + \mathbf{1}_n d_\pi^T$

```ad-important
title: Theorem - Solution of Poisson Equation

$$v^*_\pi = (I_n - P_\pi + \mathbf{1}_n d_\pi^T)^{-1} r_\pi$$

이 $v^*_\pi$는 Poisson equation의 해이며, ==모든 해==는 다음 형태:

$$v_\pi = v^*_\pi + c\mathbf{1}_n, \quad c \in \mathbb{R}$$

- $I_n - P_\pi$가 ==singular==이므로 해가 ==비유일==
- 해들은 ==상수 차이==만 존재
- $v_\pi$는 비유일하지만 ==$\bar{r}_\pi$는 유일== ($(P_\pi - I_n)\mathbf{1}_n = 0$이므로 상수 $c$가 상쇄)
```

```ad-important
title: Proof - Solution of Poisson Equation
collapse: true

**Step 1**: $v^*_\pi$가 해임을 증명

$A \doteq I_n - P_\pi + \mathbf{1}_n d_\pi^T$로 정의하면 $v^*_\pi = A^{-1} r_\pi$

Poisson equation $(I_n - P_\pi)v_\pi = (I_n - \mathbf{1}_n d_\pi^T) r_\pi$에 $v^*_\pi$를 대입하면 성립함을 확인

**Step 2**: 해의 일반 형태

$(I_n - P_\pi)\mathbf{1}_n = 0$이므로 $v^*_\pi$가 해이면, $v^*_\pi + c\mathbf{1}_n$도 해 ($c \in \mathbb{R}$)

**Step 3**: $A$의 역행렬 존재

핵심 항등식 (귀납법):

$$(P_\pi - \mathbf{1}_n d_\pi^T)^k = P_\pi^k - \mathbf{1}_n d_\pi^T, \quad k \geq 1$$

$\lim_{k \to \infty} P_\pi^k = \mathbf{1}_n d_\pi^T$이므로 $\lim_{k \to \infty} (P_\pi - \mathbf{1}_n d_\pi^T)^k = 0$

→ $\rho(P_\pi - \mathbf{1}_n d_\pi^T) < 1$ → $A = I_n - (P_\pi - \mathbf{1}_n d_\pi^T)$는 역행렬 존재
```

<br/>

#### Gradient of $\bar{r}_\pi$

```ad-important
title: Theorem - Gradient of $\bar{r}_\pi$ (Undiscounted)

$$\nabla_\theta \bar{r}_\pi = \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a) = \mathbb{E}_{S \sim d_\pi, A \sim \pi(S,\theta)} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right]$$

- ==$=$는 정확한 등호== (근사 아님)
```

**Poisson equation이 핵심인 이유**: Poisson equation을 $\theta$로 미분하면 ==$-\bar{r}_\pi$ 항==이 ==$-\nabla_\theta \bar{r}_\pi$==로 변환되고, $d_\pi^T$를 곱하면 $\nabla_\theta v_\pi$ 항들이 ==자동 상쇄== — Discounted case의 근사 문제 해결

```ad-important
title: Proof - Gradient of $\bar{r}_\pi$ (Undiscounted)
collapse: true

**Step 1**: $\nabla_\theta v_\pi(s)$ 전개

$$\nabla_\theta v_\pi(s) = \sum_{a \in \mathcal{A}} \left[ \nabla_\theta \pi(a|s,\theta) q_\pi(s,a) + \pi(a|s,\theta) \nabla_\theta q_\pi(s,a) \right]$$

Poisson equation에서 $\nabla_\theta q_\pi(s,a) = -\nabla_\theta \bar{r}_\pi + \sum_{s'} p(s'|s,a) \nabla_\theta v_\pi(s')$이므로:

$$\nabla_\theta v_\pi(s) = \underbrace{\sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s,\theta) q_\pi(s,a)}_{u(s)} - \nabla_\theta \bar{r}_\pi + \sum_{s' \in \mathcal{S}} [P_\pi]_{ss'} \nabla_\theta v_\pi(s')$$

**Step 2**: Matrix-vector form

$$\nabla_\theta v_\pi = u - \mathbf{1}_n \otimes \nabla_\theta \bar{r}_\pi + (P_\pi \otimes I_m) \nabla_\theta v_\pi$$

정리: $\mathbf{1}_n \otimes \nabla_\theta \bar{r}_\pi = u + (P_\pi \otimes I_m) \nabla_\theta v_\pi - \nabla_\theta v_\pi$

**Step 3**: $d_\pi^T \otimes I_m$를 양변에 곱함

$$(d_\pi^T \mathbf{1}_n) \otimes \nabla_\theta \bar{r}_\pi = d_\pi^T \otimes I_m \cdot u + (d_\pi^T P_\pi) \otimes I_m \cdot \nabla_\theta v_\pi - d_\pi^T \otimes I_m \cdot \nabla_\theta v_\pi$$

**Step 4**: Stationary distribution 성질 적용

- $d_\pi^T \mathbf{1}_n = 1$
- $d_\pi^T P_\pi = d_\pi^T$

우변의 마지막 두 항이 상쇄:

$$\nabla_\theta \bar{r}_\pi = \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s,\theta) q_\pi(s,a)$$
```

<br/><br/>

## Related Concepts

- [[Value Function Approximation]]: 동일한 파라미터화 아이디어 (가치 함수 → 정책 함수)
- [[Stationary Distribution]]: $d_\pi$의 이론적 기반 및 Poisson equation 해의 수렴성
- [[Bellman Equation]]: Metric 동등성 증명 및 $\nabla_\theta q_\pi$ 유도의 기반
- [[REINFORCE]]: Monte Carlo Policy Gradient — 본 이론의 직접적 구현
- [[Actor-Critic]]: Policy Gradient + Value Function Approximation 결합
