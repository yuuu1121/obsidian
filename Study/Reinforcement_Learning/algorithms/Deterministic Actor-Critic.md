---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Deterministic Policy Gradient
  - DPG
  - 결정적 액터-크리틱
keywords:
  - Deterministic Actor-Critic
  - Deterministic Policy
  - Continuous Action Space
  - Off-policy
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 10.4
author:
url:
---

# Deterministic Actor-Critic

<!-- Section 10.4 -->

```ad-note
title: Summary
collapse: true

- ==Deterministic Policy: $a = \mu(s, \theta)$ — 확률이 아닌 행동 자체를 출력==
- ==Gradient: $\nabla_\theta J = \mathbb{E}[\nabla_\theta \mu \cdot \nabla_a q_\mu]$ — 행동 샘플링 불필요==
- ==자연스럽게 Off-policy== — Actor, Critic 모두 importance sampling 불필요
- ==연속 행동 공간에 효과적== — 무한한 행동에 대한 적분 불필요
```

## Definition

<!-- Section 10.4 Introduction -->

이전 Policy Gradient 알고리즘들이 모두 stochastic policy를 사용한 반면, ==정책을 deterministic하게== 만든 Actor-Critic 알고리즘

$$a = \mu(s, \theta)$$

- $\mu$: ==결정적 정책== — 상태 $s$를 행동 $a$로 직접 매핑 ($\mathcal{S} \to \mathcal{A}$)
- $\theta$: 정책 파라미터 (간결하게 $\mu(s, \theta)$를 $\mu(s)$로 표기)
- Stochastic policy $\pi(a|s)$와 달리 ==확률이 아닌 행동 자체==를 출력

| 속성 | Stochastic $\pi(a\|s, \theta)$ | Deterministic $\mu(s, \theta)$ |
|:---|:---|:---|
| **출력** | 행동의 ==확률 분포== | ==행동 자체== |
| **Gradient** | $\mathbb{E}_{S,A}[\nabla \ln \pi \cdot q]$ | $\mathbb{E}_S[\nabla \mu \cdot \nabla_a q]$ |
| **샘플링** | 상태 $S$, 행동 $A$ 모두 | ==상태 $S$만== |
| **Off-policy** | IS 필요 (분포 보정) | ==IS 불필요== |
| **$\pi > 0$ 조건** | 필요 (log-derivative trick) | 불필요 |
| **행동 공간** | 이산/연속 | ==연속에 효과적== |

→ Gradient에 ==행동 샘플이 불필요==하여 [[Importance Sampling]] 없이 자연스럽게 [[On-Policy vs Off-Policy|off-policy]] 학습 가능

<br/><br/>

## Deterministic Policy Gradient Theorem

<!-- Section 10.4.1 -->

[[Policy Gradient#Policy Gradient Theorem|Stochastic policy gradient theorem]]은 $\pi(a|s) > 0$ 조건이 필요하므로 deterministic policy에 적용 불가 → ==새로운 정리 필요==

<!-- Theorem 10.2, Equation 10.14 -->

```ad-important
title: Theorem - Deterministic Policy Gradient

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \eta(s) \nabla_\theta \mu(s) \left(\nabla_a q_\mu(s, a)\right)\Big|_{a=\mu(s)} = \mathbb{E}_{S \sim \eta} \left[ \nabla_\theta \mu(S) \left(\nabla_a q_\mu(S, a)\right)\Big|_{a=\mu(S)} \right]$$

- $\eta$: 상태 분포 (metric에 따라 다름)
  - Discounted case: $\rho_\mu(s) = \sum_{s'} d_0(s') \Pr_\mu(s|s')$ (discounted state distribution)
  - Undiscounted case: $d_\mu$ ([[Stationary Distribution]])
- $\nabla_\theta \mu(s)$: 정책의 파라미터에 대한 gradient
- $\nabla_a q_\mu(s, a)$: action value의 행동에 대한 gradient

Stochastic gradient와 달리 ==action random variable $A$가 포함되지 않음== → action 샘플링 없이 상태 샘플만으로 gradient 계산 가능 → ==자연스럽게 [[On-Policy vs Off-Policy|off-policy]]==
```

```ad-info
title: Note - Notation Convention

$(\nabla_a q_\mu(S, a))|_{a=\mu(S)}$ 표기 사용 이유:
- $\nabla_a q_\mu(S, \mu(S))$로 쓰면 $q_\mu$가 $a$의 함수임이 ==불명확==
- $|_{a=\mu(S)}$는 "먼저 $a$에 대해 미분한 후, $a = \mu(S)$를 대입"을 명시
```

<br/><br/>

## Gradient Derivation

<!-- Section 10.4.1 -->

두 가지 metric에 대해 Deterministic Policy Gradient가 유도됨. 두 경우 모두 gradient가 $\mathbb{E}[\nabla_\theta \mu \cdot \nabla_a q_\mu]$ 형태로 ==동일한 구조==를 가짐.

| Case | Metric $J$ | 상태 분포 $\eta$ |
|:---|:---|:---|
| **Discounted** ($\gamma < 1$) | $\sum_s d_0(s) v_\mu(s)$ | $\rho_\mu$ (discounted state distribution) |
| **Undiscounted** ($\gamma = 1$) | $\sum_s d_\mu(s) r_\mu(s)$ | $d_\mu$ ([[Stationary Distribution]]) |

<br/>

### Gradient of $v_\mu(s)$

$J(\theta)$의 gradient를 계산하기 위해 먼저 $\nabla_\theta v_\mu(s)$를 유도 (discounted case, $\gamma \in (0, 1)$)

<!-- Lemma 10.1 -->

```ad-important
title: Lemma - Gradient of $v_\mu(s)$

$$\nabla_\theta v_\mu(s) = \sum_{s' \in \mathcal{S}} \Pr_\mu(s'|s) \nabla_\theta \mu(s') \left(\nabla_a q_\mu(s', a)\right)\Big|_{a=\mu(s')}$$

- $\Pr_\mu(s'|s) = \sum_{k=0}^{\infty} \gamma^k [P_\mu^k]_{ss'} = [(I - \gamma P_\mu)^{-1}]_{ss'}$: ==discounted total transition probability==
- $[P_\mu^k]_{ss'}$: 정확히 $k$ step 후 $s \to s'$ 전이 확률
```

<!-- Box 10.3: Proof of Lemma 10.1 -->

```ad-important
title: Proof - Gradient of $v_\mu(s)$
collapse: true

**Step 1: State Value와 Action Value의 관계**

결정적 정책에서 state value는 단일 행동의 action value와 동일:

$$v_\mu(s) = q_\mu(s, \mu(s))$$

**Step 2: Chain Rule 적용**

$v_\mu(s) = q_\mu(s, \mu(s, \theta))$에서 $\theta$는 두 경로로 $v_\mu$에 영향:
- **직접 경로**: $q_\mu$ 자체가 $\theta$의 함수 (value function이 정책에 의존)
- **간접 경로**: $\mu(s, \theta)$를 통해 action이 $\theta$에 의존

Multivariate chain rule 적용:

<!-- Equation 10.17 -->

$$\nabla_\theta v_\mu(s) = \nabla_\theta q_\mu(s, \mu(s)) = \underbrace{(\nabla_\theta q_\mu(s, a))|_{a=\mu(s)}}_{\text{직접 경로: $q_\mu$의 $\theta$ 의존성}} + \underbrace{\nabla_\theta \mu(s) (\nabla_a q_\mu(s, a))|_{a=\mu(s)}}_{\text{간접 경로: $\mu$를 통한 $\theta$ 의존성}}$$

**Step 3: Bellman Equation으로 $\nabla_\theta q_\mu$ 계산**

Action value의 Bellman equation:

$$q_\mu(s, a) = r(s, a) + \gamma \sum_{s' \in \mathcal{S}} p(s'|s, a) v_\mu(s')$$

$r(s, a) = \sum_r r \cdot p(r|s, a)$는 $\mu$와 독립이므로:

$$\nabla_\theta q_\mu(s, a) = 0 + \gamma \sum_{s' \in \mathcal{S}} p(s'|s, a) \nabla_\theta v_\mu(s')$$

**Step 4: Step 2에 대입하여 재귀 관계 유도**

$$\nabla_\theta v_\mu(s) = \gamma \sum_{s' \in \mathcal{S}} p(s'|s, \mu(s)) \nabla_\theta v_\mu(s') + \underbrace{\nabla_\theta \mu(s) (\nabla_a q_\mu(s, a))|_{a=\mu(s)}}_{u(s)}$$

이 식은 모든 $s \in \mathcal{S}$에 대해 성립

**Step 5: Matrix-Vector Form**

$n = |\mathcal{S}|$, $m = \dim(\theta)$로 정의하면:

$$\underbrace{\begin{bmatrix} \vdots \\ \nabla_\theta v_\mu(s) \\ \vdots \end{bmatrix}}_{\nabla_\theta v_\mu \in \mathbb{R}^{mn}} = \underbrace{\begin{bmatrix} \vdots \\ u(s) \\ \vdots \end{bmatrix}}_{u \in \mathbb{R}^{mn}} + \gamma (P_\mu \otimes I_m) \nabla_\theta v_\mu$$

- $P_\mu$: $[P_\mu]_{ss'} = p(s'|s, \mu(s))$인 전이 행렬
- $\otimes$: Kronecker product
- $I_m$: $m \times m$ 단위행렬

간결하게:

$$\nabla_\theta v_\mu = u + \gamma (P_\mu \otimes I_m) \nabla_\theta v_\mu$$

**Step 6: 선형 방정식 풀이**

$\nabla_\theta v_\mu$에 대해 정리 ($(I - \gamma(P_\mu \otimes I_m))\nabla_\theta v_\mu = u$):

$$\begin{aligned}
\nabla_\theta v_\mu &= (I_{mn} - \gamma P_\mu \otimes I_m)^{-1} u \\
&= (I_n \otimes I_m - \gamma P_\mu \otimes I_m)^{-1} u \\
&= ((I_n - \gamma P_\mu) \otimes I_m)^{-1} u \\
&= [(I_n - \gamma P_\mu)^{-1} \otimes I_m] u
\end{aligned}$$

사용된 Kronecker product 성질:
- $(A \otimes B) - (C \otimes B) = (A - C) \otimes B$
- $(A \otimes B)^{-1} = A^{-1} \otimes B^{-1}$ (A, B가 가역일 때)

**Step 7: Elementwise Form**

<!-- Equation 10.19 -->

$$\begin{aligned}
\nabla_\theta v_\mu(s) &= \sum_{s' \in \mathcal{S}} [(I - \gamma P_\mu)^{-1}]_{ss'} u(s') \\
&= \sum_{s' \in \mathcal{S}} [(I - \gamma P_\mu)^{-1}]_{ss'} \nabla_\theta \mu(s') (\nabla_a q_\mu(s', a))|_{a=\mu(s')}
\end{aligned}$$

**Step 8: 확률론적 해석**

$\gamma \in (0, 1)$이고 $P_\mu$의 spectral radius $\rho(P_\mu) \leq 1$이므로 $\rho(\gamma P_\mu) < 1$ → ==Neumann series 수렴==:

$$(I - \gamma P_\mu)^{-1} = \sum_{k=0}^{\infty} (\gamma P_\mu)^k = I + \gamma P_\mu + \gamma^2 P_\mu^2 + \cdots$$

따라서:

$$[(I - \gamma P_\mu)^{-1}]_{ss'} = [I]_{ss'} + \gamma [P_\mu]_{ss'} + \gamma^2 [P_\mu^2]_{ss'} + \cdots = \sum_{k=0}^{\infty} \gamma^k [P_\mu^k]_{ss'}$$

- $[P_\mu^k]_{ss'}$: 정확히 $k$ step 후 $s$에서 $s'$로 전이할 확률
- $\gamma^k$: $k$ step 후의 discount factor

따라서 $[(I - \gamma P_\mu)^{-1}]_{ss'} = \Pr_\mu(s'|s)$는 ==discounted total transition probability==:

$$\Pr_\mu(s'|s) = \sum_{k=0}^{\infty} \gamma^k [P_\mu^k]_{ss'} = \text{``}s \to s' \text{로 도달하는 모든 경로의 discounted 확률 합''}$$

$\square$
```

<br/>

### Discounted Case

<!-- Metric 1: Average value ($\gamma < 1$) -->

위 Lemma를 사용하여 Discounted metric $J(\theta) = \sum_s d_0(s) v_\mu(s)$의 gradient를 유도

```ad-info
title: Note - Choice of $d_0$

$d_0$는 정책 $\mu$와 독립인 상태 분포. 두 가지 특수한 선택:

| 선택 | 정의 | 목적 |
|:---|:---|:---|
| **특정 시작 상태** | $d_0(s_0) = 1$, $d_0(s \neq s_0) = 0$ | $s_0$에서 시작하는 ==discounted return 최대화== |
| **Behavior policy 분포** | $d_0 = d_\beta$ | Target policy와 다른 ==behavior policy로 off-policy 학습== |
```

<!-- Theorem 10.3 -->

```ad-important
title: Theorem - Deterministic Policy Gradient in Discounted Case

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \rho_\mu(s) \nabla_\theta \mu(s) \left(\nabla_a q_\mu(s, a)\right)\Big|_{a=\mu(s)} = \mathbb{E}_{S \sim \rho_\mu} \left[ \nabla_\theta \mu(S) \left(\nabla_a q_\mu(S, a)\right)\Big|_{a=\mu(S)} \right]$$

상태 분포 $\rho_\mu$:

$$\rho_\mu(s) = \sum_{s' \in \mathcal{S}} d_0(s') \Pr_\mu(s|s')$$

- $\Pr_\mu(s|s') = \sum_{k=0}^{\infty} \gamma^k [P_\mu^k]_{s's} = [(I - \gamma P_\mu)^{-1}]_{s's}$: $s'$에서 $s$로의 discounted total transition probability
- $d_0$: 초기 상태 분포 (정책 $\mu$와 독립)
```

<!-- Box 10.4: Proof of Theorem 10.3 -->

```ad-important
title: Proof - Deterministic Policy Gradient in Discounted Case
collapse: true

**Step 1: $J(\theta)$의 Gradient 시작**

$d_0$는 $\mu$와 독립이므로:

$$\nabla_\theta J(\theta) = \nabla_\theta \sum_{s \in \mathcal{S}} d_0(s) v_\mu(s) = \sum_{s \in \mathcal{S}} d_0(s) \nabla_\theta v_\mu(s)$$

**Step 2: Lemma 대입**

$\nabla_\theta v_\mu(s)$의 Lemma 표현식을 대입:

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} d_0(s) \sum_{s' \in \mathcal{S}} \Pr_\mu(s'|s) \nabla_\theta \mu(s') \left(\nabla_a q_\mu(s', a)\right)\Big|_{a=\mu(s')}$$

**Step 3: 합산 순서 교환**

$s$와 $s'$에 대한 합의 순서를 교환:

$$\nabla_\theta J(\theta) = \sum_{s' \in \mathcal{S}} \left( \sum_{s \in \mathcal{S}} d_0(s) \Pr_\mu(s'|s) \right) \nabla_\theta \mu(s') \left(\nabla_a q_\mu(s', a)\right)\Big|_{a=\mu(s')}$$

**Step 4: 상태 분포 $\rho_\mu$ 정의**

괄호 안의 항을 $\rho_\mu(s')$로 정의:

$$\rho_\mu(s') \triangleq \sum_{s \in \mathcal{S}} d_0(s) \Pr_\mu(s'|s)$$

$\rho_\mu(s')$의 의미:
- $d_0(s)$: 초기 상태 $s$의 확률
- $\Pr_\mu(s'|s)$: $s$에서 $s'$로의 discounted total probability
- $\rho_\mu(s')$: ==초기 분포 $d_0$에서 시작하여 상태 $s'$에 도달할 discounted 확률의 총합==

대입하면:

$$\nabla_\theta J(\theta) = \sum_{s' \in \mathcal{S}} \rho_\mu(s') \nabla_\theta \mu(s') \left(\nabla_a q_\mu(s', a)\right)\Big|_{a=\mu(s')}$$

**Step 5: 변수명 변경 및 기댓값 표현**

$s'$를 $s$로 변경 (dummy variable):

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \rho_\mu(s) \nabla_\theta \mu(s) \left(\nabla_a q_\mu(s, a)\right)\Big|_{a=\mu(s)}$$

기댓값 형태로 표현:

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \rho_\mu} \left[ \nabla_\theta \mu(S) \left(\nabla_a q_\mu(S, a)\right)\Big|_{a=\mu(S)} \right] \quad \square$$
```

<br/>

### Undiscounted Case

<!-- Metric 2: Average reward ($\gamma = 1$) -->

Undiscounted metric (Average Reward)에 대한 gradient 유도

<!-- Equation 10.20 -->

$$J(\theta) = \bar{r}_\mu = \sum_{s \in \mathcal{S}} d_\mu(s) r_\mu(s) = \mathbb{E}_{S \sim d_\mu}[r_\mu(S)]$$

- $d_\mu$: 정책 $\mu$ 하에서의 ==stationary distribution==
- $r_\mu(s) = \mathbb{E}[R|s, a = \mu(s)] = \sum_r r \cdot p(r|s, \mu(s))$: 즉시 보상의 기댓값

```ad-info
title: Note - Differential Value in Undiscounted Case

Undiscounted case에서 $q_\mu$는 ==[[Policy Gradient#Differential Value (Bias)|differential value]]==로 정의:

$$q_\mu(s, a) = r(s, a) - \bar{r}_\mu + \sum_{s'} p(s'|s, a) v_\mu(s')$$

| | Discounted | Undiscounted |
|:---|:---|:---|
| **$q_\mu$ 정의** | $r + \gamma \sum_{s'} p v_\mu(s')$ | $r - \bar{r}_\mu + \sum_{s'} p v_\mu(s')$ |
| **재귀 관계** | Bellman Equation | ==Poisson Equation== |
| **수렴 보장** | $\gamma < 1$ | $-\bar{r}_\mu$ (평균 보정) |
```

<!-- Theorem 10.4 -->

```ad-important
title: Theorem - Deterministic Policy Gradient in Undiscounted Case

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} d_\mu(s) \nabla_\theta \mu(s) \left(\nabla_a q_\mu(s, a)\right)\Big|_{a=\mu(s)} = \mathbb{E}_{S \sim d_\mu} \left[ \nabla_\theta \mu(S) \left(\nabla_a q_\mu(S, a)\right)\Big|_{a=\mu(S)} \right]$$

- $d_\mu$: 정책 $\mu$ 하에서의 ==stationary distribution== ($d_\mu^T P_\mu = d_\mu^T$ 만족)
```

<!-- Box 10.5: Proof of Theorem 10.4 -->

```ad-important
title: Proof - Deterministic Policy Gradient in Undiscounted Case
collapse: true

**Step 1: State Value와 Action Value의 관계**

결정적 정책에서:

$$v_\mu(s) = q_\mu(s, \mu(s))$$

**Step 2: Chain Rule 적용**

$v_\mu(s) = q_\mu(s, \mu(s, \theta))$에서 $\theta$는 두 경로로 $v_\mu$에 영향:
- **직접 경로**: $q_\mu$ 자체가 $\theta$의 함수
- **간접 경로**: $\mu(s, \theta)$를 통해 action이 $\theta$에 의존

<!-- Equation 10.21 -->

$$\nabla_\theta v_\mu(s) = \underbrace{(\nabla_\theta q_\mu(s, a))|_{a=\mu(s)}}_{\text{직접 경로}} + \underbrace{\nabla_\theta \mu(s) (\nabla_a q_\mu(s, a))|_{a=\mu(s)}}_{\text{간접 경로}}$$

**Step 3: $\nabla_\theta q_\mu$ 계산**

Undiscounted case의 action value (Poisson Equation):
$q_\mu(s, a) = r(s, a) - \bar{r}_\mu + \sum_{s'} p(s'|s, a) v_\mu(s')$

$r(s, a) = \sum_r r \cdot p(r|s, a)$는 $\theta$와 독립이므로:

$$\nabla_\theta q_\mu(s, a) = -\nabla_\theta \bar{r}_\mu + \sum_{s'} p(s'|s, a) \nabla_\theta v_\mu(s')$$

**Step 4: 재귀 관계 유도**

$$\nabla_\theta v_\mu(s) = -\nabla_\theta \bar{r}_\mu + \sum_{s'} p(s'|s, \mu(s)) \nabla_\theta v_\mu(s') + \underbrace{\nabla_\theta \mu(s) (\nabla_a q_\mu(s, a))|_{a=\mu(s)}}_{u(s)}$$

이 식은 모든 $s \in \mathcal{S}$에 대해 성립

**Step 5: Matrix-Vector Form**

$n = |\mathcal{S}|$, $m = \dim(\theta)$로 정의:

$$\underbrace{\begin{bmatrix} \vdots \\ \nabla_\theta v_\mu(s) \\ \vdots \end{bmatrix}}_{\nabla_\theta v_\mu \in \mathbb{R}^{mn}} = -\mathbf{1}_n \otimes \nabla_\theta \bar{r}_\mu + (P_\mu \otimes I_m) \nabla_\theta v_\mu + \underbrace{\begin{bmatrix} \vdots \\ u(s) \\ \vdots \end{bmatrix}}_{u \in \mathbb{R}^{mn}}$$

간결하게:

$$\nabla_\theta v_\mu = -\mathbf{1}_n \otimes \nabla_\theta \bar{r}_\mu + (P_\mu \otimes I_m) \nabla_\theta v_\mu + u$$

- $\mathbf{1}_n$: 모든 성분이 1인 $n$차원 벡터
- $P_\mu$: $[P_\mu]_{ss'} = p(s'|s, \mu(s))$인 전이 행렬
- $\otimes$: Kronecker product

**Step 6: $\nabla_\theta \bar{r}_\mu$에 대해 정리**

<!-- Equation 10.22 -->

$$\mathbf{1}_n \otimes \nabla_\theta \bar{r}_\mu = u + (P_\mu \otimes I_m) \nabla_\theta v_\mu - \nabla_\theta v_\mu$$

**Step 7: Stationary Distribution 성질 활용**

$d_\mu$는 stationary distribution이므로 ==$d_\mu^T P_\mu = d_\mu^T$== 만족

양변에 $d_\mu^T \otimes I_m$을 곱함:

$$\begin{aligned}
(d_\mu^T \otimes I_m)(\mathbf{1}_n \otimes \nabla_\theta \bar{r}_\mu) &= (d_\mu^T \otimes I_m) u + (d_\mu^T \otimes I_m)(P_\mu \otimes I_m) \nabla_\theta v_\mu - (d_\mu^T \otimes I_m) \nabla_\theta v_\mu \\
(d_\mu^T \mathbf{1}_n) \otimes \nabla_\theta \bar{r}_\mu &= d_\mu^T \otimes I_m \cdot u + (d_\mu^T P_\mu) \otimes I_m \cdot \nabla_\theta v_\mu - d_\mu^T \otimes I_m \cdot \nabla_\theta v_\mu
\end{aligned}$$

$d_\mu^T P_\mu = d_\mu^T$이므로 마지막 두 항이 상쇄:

$$(d_\mu^T \mathbf{1}_n) \otimes \nabla_\theta \bar{r}_\mu = d_\mu^T \otimes I_m \cdot u + \underbrace{d_\mu^T \otimes I_m \cdot \nabla_\theta v_\mu - d_\mu^T \otimes I_m \cdot \nabla_\theta v_\mu}_{= 0}$$

$$(d_\mu^T \mathbf{1}_n) \otimes \nabla_\theta \bar{r}_\mu = d_\mu^T \otimes I_m \cdot u$$

**Step 8: 최종 결과**

$d_\mu^T \mathbf{1}_n = \sum_s d_\mu(s) = 1$ (확률의 합)이므로:

$$\begin{aligned}
\nabla_\theta \bar{r}_\mu &= d_\mu^T \otimes I_m u \\
&= \sum_{s \in \mathcal{S}} d_\mu(s) u(s) \\
&= \sum_{s \in \mathcal{S}} d_\mu(s) \nabla_\theta \mu(s) (\nabla_a q_\mu(s, a))|_{a=\mu(s)} \\
&= \mathbb{E}_{S \sim d_\mu} \left[ \nabla_\theta \mu(S) (\nabla_a q_\mu(S, a))|_{a=\mu(S)} \right] \quad \square
\end{aligned}$$
```

<br/><br/>

## Algorithm

<!-- Section 10.4.2 -->

Deterministic Policy Gradient Theorem의 gradient를 실제 알고리즘으로 구현

| 이론적 형태 | 알고리즘 구현 |
|:---|:---|
| $\mathbb{E}_{S \sim \eta}[\cdot]$ | 샘플 $s_t$로 대체 ([[Stochastic Approximation]]) |
| $\nabla_a q_\mu(s, a)$ | Critic $q(s, a, w)$의 gradient $\nabla_a q(s, a, w)$ |
| $q_\mu(s, a)$ | TD target $r_{t+1} + \gamma q(s_{t+1}, \mu(s_{t+1}), w)$ |

**Gradient Ascent**:

$$\theta_{t+1} = \theta_t + \alpha_\theta \mathbb{E}_{S \sim \eta} \left[ \nabla_\theta \mu(S) (\nabla_a q_\mu(S, a))|_{a=\mu(S)} \right]$$

**Stochastic Gradient Ascent** (샘플 기반):

$$\theta_{t+1} = \theta_t + \alpha_\theta \nabla_\theta \mu(s_t) (\nabla_a q(s_t, a, w_t))|_{a=\mu(s_t)}$$

<br/>

<!-- Algorithm 10.4 -->

```ad-tldr
title: Algorithm - Deterministic Actor-Critic

**입력**:
- Behavior policy $\beta(a|s)$: 탐색을 위한 정책 (환경 상호작용)
- Target policy $\mu(s, \theta)$: 학습 대상 결정적 정책 (Actor)
- Value function $q(s, a, w)$: Critic 파라미터 $w$
- 학습률 $\alpha_\theta, \alpha_w > 0$

**초기화**: $\theta_0$, $w_0$ 임의 설정

**목표**: $J(\theta)$를 최대화하는 최적 정책 학습

**For** 각 에피소드의 매 시점 $t$:
- ==$\beta(s_t)$를 따라== $a_t$ 생성, $r_{t+1}$, $s_{t+1}$ 관측
- **TD error**:
  $$\delta_t = r_{t+1} + \gamma q(s_{t+1}, \mu(s_{t+1}, \theta_t), w_t) - q(s_t, a_t, w_t)$$
- **Actor** (policy update):
  $$\theta_{t+1} = \theta_t + \alpha_\theta \nabla_\theta \mu(s_t, \theta_t) (\nabla_a q(s_t, a, w_t))|_{a=\mu(s_t)}$$
- **Critic** (value update):
  $$w_{t+1} = w_t + \alpha_w \delta_t \nabla_w q(s_t, a_t, w_t)$$

**출력**: 학습된 정책 $\mu(s, \theta)$
```

<br/>

### Natural Off-policy

Deterministic AC는 ==[[Importance Sampling]] 없이== 자연스럽게 [[On-Policy vs Off-Policy|off-policy]]

**핵심 이유**: True gradient $\nabla_\theta J = \mathbb{E}_S[\nabla_\theta \mu \cdot \nabla_a q]$에 ==action random variable $A$가 없음==

- 샘플로 gradient 근사 시 ==action 샘플링 불필요== → 상태 $S$만 샘플링
- 따라서 ==어떤 behavior policy든 사용 가능== → off-policy

| 구성요소 | Off-policy 이유 |
|:---|:---|
| **Actor** | Gradient에 ==행동 확률변수 $A$가 없음== → 상태 $S$만 샘플링 |
| **Critic** | Experience $(s_t, a_t, r_{t+1}, s_{t+1}, \tilde{a}_{t+1})$에서 ==두 정책이 관여== |

**Critic의 두 정책**:

| 행동 | 생성 정책 | 환경 상호작용 |
|:---|:---|:---|
| $a_t$ | $\beta$ (behavior) | O — 실제 전이에 사용 |
| $\tilde{a}_{t+1} = \mu(s_{t+1})$ | $\mu$ (target) | X — TD target 계산용 |

$\tilde{a}_{t+1}$은 ==환경과 상호작용하지 않으므로== importance sampling 불필요

```ad-info
title: Note - Implementation Choices

**Value Function $q(s, a, w)$**:
- **Linear**: $q(s, a, w) = \phi^T(s, a) w$ — 원래 연구 [Silver et al., 2014]
- **Neural Network**: Deep network — ==DDPG== [Lillicrap et al., 2015]

**Behavior Policy $\beta$**:
- 임의의 exploratory policy 사용 가능
- $\mu$에 노이즈 추가 시 on-policy 구현이 됨: $a_t = \mu(s_t, \theta) + \mathcal{N}(0, \sigma^2)$
```

<br/><br/>

## Related Concepts

- [[Actor-Critic]]: Stochastic policy 기반 기본 Actor-Critic — deterministic의 대비 개념
- [[Policy Gradient]]: Policy gradient의 이론적 기반 — stochastic policy gradient theorem
- [[Off-policy Actor-Critic]]: Importance sampling 기반 off-policy 학습 (stochastic policy)
- [[Advantage Actor-Critic]]: Baseline을 사용한 variance reduction
- [[Value Function Approximation]]: Critic의 $q(s,a,w)$ 표현에 사용
- [[Temporal Difference Learning]]: Critic의 TD error 기반 업데이트
- [[Stochastic Approximation]]: 기댓값을 샘플로 근사하는 이론적 기반 — gradient ascent 구현
- [[Stationary Distribution]]: Average reward metric에서 상태 분포 $d_\mu$ 정의
- [[Bellman Equation]]: Action value의 재귀적 정의 — gradient 유도에 사용
- [[On-Policy vs Off-Policy]]: Deterministic AC는 자연스럽게 off-policy

