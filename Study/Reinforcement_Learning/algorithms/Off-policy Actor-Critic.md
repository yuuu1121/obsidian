---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Off-policy AC
  - 오프폴리시 액터-크리틱
keywords:
  - Off-policy
  - Actor-Critic
  - Importance Sampling
  - Behavior Policy
  - Target Policy
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 10.3
author:
url:
---

# Off-policy Actor-Critic

```ad-note
title: Summary
collapse: true

- ==On-policy 한계: gradient가 $A \sim \pi$를 요구하여 현재 정책으로만 샘플 생성 필요==
- ==Off-policy: behavior policy $\beta$로 생성된 샘플로 target policy $\pi$ 학습==
- ==Importance Sampling: $\frac{\pi(A|S)}{\beta(A|S)}$로 분포 차이 보정==
- ==Off-policy Gradient: $\mathbb{E}_{A \sim \beta}[\frac{\pi}{\beta} \nabla \ln \pi \cdot q_\pi]$==
```

## Definition

[[Advantage Actor-Critic|A2C]]를 off-policy로 확장하여 ==Behavior policy $\beta$로 생성된 샘플을 사용하여 target policy $\pi$를 학습==하는 Actor-Critic

| 용어 | 정의 | 역할 |
|:---|:---|:---|
| **Behavior policy** $\beta$ | 샘플 생성에 사용하는 정책 | 데이터 수집 |
| **Target policy** $\pi$ | 학습/개선 대상 정책 | 최적화 목표 |

- **On-policy**: $\beta = \pi$ (동일)
- **Off-policy**: $\beta \neq \pi$ (다름)

<br/>

### On-Policy Limitation

[[REINFORCE]], [[Actor-Critic|QAC]], [[Advantage Actor-Critic|A2C]]는 모두 ==on-policy== — True gradient가 $A \sim \pi$를 요구하기 때문:

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \eta, A \sim \pi} \left[ \nabla_\theta \ln \pi(A|S, \theta_t) (q_\pi(S, A) - v_\pi(S)) \right]$$

- 샘플로 gradient를 근사하려면 ==$A \sim \pi(\theta)$에서 action을 생성== 필요
- $\pi(\theta)$가 ==behavior policy이자 target policy== → on-policy

**한계**: ==과거 샘플 재사용 불가==
- 정책 업데이트마다 새로운 샘플 필요
- 샘플 효율성 낮음

→ ==[[Importance Sampling]]==으로 분포 차이를 보정하여 해결

<br/><br/>

## Importance Sampling in Policy Gradient
<!-- Section 10.3.1 -->

[[Importance Sampling]]을 사용하여 ==$\beta$에서 생성된 action 샘플로 $\pi$에 대한 gradient를 근사==

$$\mathbb{E}_{A \sim \pi}[f(A)] = \mathbb{E}_{A \sim \beta}\left[\frac{\pi(A|S)}{\beta(A|S)} f(A)\right]$$

- **Importance weight** $\frac{\pi(A|S)}{\beta(A|S)}$: target/behavior policy 간 분포 차이 보정
- $\beta = \pi$이면 weight = 1 → on-policy와 동일
- $\beta$가 충분히 exploratory해야 coverage condition 만족

```ad-warning
title: Note - Practical Considerations

**Coverage**: $\pi(a|s) > 0$인 모든 $(s,a)$에 대해 $\beta(a|s) > 0$ 필요

**Variance**: $\pi$와 $\beta$의 차이가 크면 ==importance weight 변동이 심해져 분산 증가==
- Weight clipping: $\min(\frac{\pi}{\beta}, c)$로 상한 제한
- PPO의 clipped objective: trust region 내로 업데이트 제한
```

<br/><br/>

## Off-policy Policy Gradient Theorem
<!-- Section 10.3.2 -->

Behavior policy $\beta$로 생성된 샘플을 사용하여 target policy $\pi$를 학습

**Metric**:

$$J(\theta) = \sum_{s \in \mathcal{S}} d_\beta(s) v_\pi(s) = \mathbb{E}_{S \sim d_\beta}[v_\pi(S)]$$

- $d_\beta$: behavior policy $\beta$ 하의 ==[[Stationary Distribution]]==
- $v_\pi$: target policy $\pi$ 하의 state value

<!-- Theorem 10.1, Equation 10.11 -->
```ad-important
title: Theorem - Off-policy Policy Gradient

Discounted case ($\gamma \in (0, 1)$)에서 $J(\theta)$의 gradient:

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \rho, A \sim \beta} \left[ \underbrace{\frac{\pi(A|S, \theta)}{\beta(A|S)}}_{\text{importance weight}} \nabla_\theta \ln \pi(A|S, \theta) \cdot q_\pi(S, A) \right]$$

- **Importance weight**: $\frac{\pi(A|S, \theta)}{\beta(A|S)}$ — 분포 차이 보정
- **State distribution** $\rho$:
  $$\rho(s) = \sum_{s' \in \mathcal{S}} d_\beta(s') \Pr_\pi(s|s'), \quad s \in \mathcal{S}$$
- **Discounted total probability**: 정책 $\pi$ 하에서 ==$s'$에서 $s$로 전이할 discounted 확률==
  $$\Pr_\pi(s|s') = \sum_{k=0}^{\infty} \gamma^k [P_\pi^k]_{s's} = [(I - \gamma P_\pi)^{-1}]_{s's}$$
  - $[P_\pi^k]_{s's}$: $k$ step 후 $s' \to s$ 전이 확률
  - $\gamma^k$로 가중하여 먼 미래일수록 영향 감소

<!-- Equation 10.11 vs Theorem 9.1 -->
On-policy gradient (Theorem 9.1)와의 ==두 가지 차이점==:
- **Importance weight** $\frac{\pi(A|S)}{\beta(A|S)}$ 추가
- ==$A \sim \beta$== instead of $A \sim \pi$

→ $\beta$에서 생성된 action 샘플로 true gradient 근사 가능
```

<!-- Box 10.2: Proof of Theorem 10.1 -->
```ad-important
title: Proof - Off-policy Policy Gradient Theorem
collapse: true

**Step 1**: $d_\beta$가 $\theta$와 독립이므로 gradient를 $v_\pi$에만 적용

$$\nabla_\theta J(\theta) = \nabla_\theta \sum_{s \in \mathcal{S}} d_\beta(s) v_\pi(s) = \sum_{s \in \mathcal{S}} d_\beta(s) \nabla_\theta v_\pi(s)$$

**Step 2**: [[Policy Gradient]]의 $\nabla_\theta v_\pi(s)$ 표현을 대입

$$\nabla_\theta v_\pi(s) = \sum_{s' \in \mathcal{S}} \Pr_\pi(s'|s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a)$$

- $\Pr_\pi(s'|s) = \sum_{k=0}^{\infty} \gamma^k [P_\pi^k]_{ss'} = [(I_n - \gamma P_\pi)^{-1}]_{ss'}$: Discounted total probability

**Step 3**: 대입 후 합의 순서 교환

$$\begin{aligned}
\nabla_\theta J(\theta) &= \sum_{s \in \mathcal{S}} d_\beta(s) \sum_{s' \in \mathcal{S}} \Pr_\pi(s'|s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a) \\
&= \sum_{s' \in \mathcal{S}} \underbrace{\left( \sum_{s \in \mathcal{S}} d_\beta(s) \Pr_\pi(s'|s) \right)}_{\rho(s')} \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s', \theta) q_\pi(s', a)
\end{aligned}$$

**Step 4**: $\rho(s')$ 정의 및 변수 변경 ($s' \to s$)

$$\rho(s) \doteq \sum_{s' \in \mathcal{S}} d_\beta(s') \Pr_\pi(s|s')$$

$$\nabla_\theta J(\theta) = \sum_{s \in \mathcal{S}} \rho(s) \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|s, \theta) q_\pi(s, a) = \mathbb{E}_{S \sim \rho} \left[ \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|S, \theta) q_\pi(S, a) \right]$$

**Step 5**: Importance sampling 적용

$\nabla_\theta \pi$를 $\beta \cdot \frac{\pi}{\beta} \cdot \frac{\nabla_\theta \pi}{\pi}$로 분해:

$$\begin{aligned}
\mathbb{E}_{S \sim \rho} \left[ \sum_{a \in \mathcal{A}} \nabla_\theta \pi(a|S, \theta) q_\pi(S, a) \right] &= \mathbb{E}_{S \sim \rho} \left[ \sum_{a \in \mathcal{A}} \beta(a|S) \frac{\pi(a|S, \theta)}{\beta(a|S)} \frac{\nabla_\theta \pi(a|S, \theta)}{\pi(a|S, \theta)} q_\pi(S, a) \right]
\end{aligned}$$

**Step 6**: Log-derivative trick 적용 ($\frac{\nabla_\theta \pi}{\pi} = \nabla_\theta \ln \pi$)

$$= \mathbb{E}_{S \sim \rho} \left[ \sum_{a \in \mathcal{A}} \beta(a|S) \frac{\pi(a|S, \theta)}{\beta(a|S)} \nabla_\theta \ln \pi(a|S, \theta) q_\pi(S, a) \right]$$

**Step 7**: $\sum_a \beta(a|S) [\cdot]$를 $A \sim \beta$에 대한 기대값으로 변환

$$= \mathbb{E}_{S \sim \rho, A \sim \beta} \left[ \frac{\pi(A|S, \theta)}{\beta(A|S)} \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right] \quad \square$$
```

```ad-info
title: Note - Baseline & TD Error Approximation

**[[Advantage Actor-Critic#Baseline Invariance|Baseline]] Invariance**: off-policy gradient도 ==baseline $b(S)$에 대해 불변==

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \rho, A \sim \beta} \left[ \frac{\pi(A|S, \theta)}{\beta(A|S)} \nabla_\theta \ln \pi(A|S, \theta) (q_\pi(S, A) - b(S)) \right]$$

- $\mathbb{E}[\frac{\pi}{\beta} \nabla \ln \pi \cdot b(S)] = 0$이므로 성립
- ==Variance 감소==를 위해 $b(S) = v_\pi(S)$로 설정 → ==advantage function== $q_\pi - v_\pi$ 사용

**[[Temporal Difference Learning#TD Error|TD Error]] Approximation**: ==TD error로 advantage 근사==

$$q_t(s_t, a_t) - v_t(s_t) \approx r_{t+1} + \gamma v_t(s_{t+1}) - v_t(s_t) \doteq \delta_t$$

- TD error $\delta_t$가 ==advantage function을 직접 근사==
- $\delta_t > 0$: 예상보다 좋은 행동 → 확률 증가, value 증가
```

<br/><br/>

## Algorithm
<!-- Section 10.3.3 -->

<!-- Algorithm 10.3 -->
```ad-tldr
title: Algorithm - Off-policy Actor-Critic

**입력**: Behavior policy $\beta(a|s)$, target policy $\pi(a|s, \theta_0)$, 가치 함수 $v(s, w_0)$, 학습률 $\alpha_\theta, \alpha_w > 0$

**초기화**: $\theta_0$, $w_0$ 임의 설정

**목표**: $J(\theta)$를 최대화하는 최적 정책 학습

**For** 각 에피소드의 매 시점 $t$:
- ==$\beta(s_t)$를 따라== $a_t$ 생성, $r_{t+1}$, $s_{t+1}$ 관측
- **Advantage** (TD error):
  $$\delta_t = r_{t+1} + \gamma v(s_{t+1}, w_t) - v(s_t, w_t)$$
- **Actor** (policy update — gradient ascent):
  $$\theta_{t+1} = \theta_t + \alpha_\theta \frac{\pi(a_t|s_t, \theta_t)}{\beta(a_t|s_t)} \delta_t \nabla_\theta \ln \pi(a_t|s_t, \theta_t)$$
- **Critic** (value update — gradient descent):
  $$w_{t+1} = w_t + \alpha_w \frac{\pi(a_t|s_t, \theta_t)}{\beta(a_t|s_t)} \delta_t \nabla_w v(s_t, w_t)$$

**출력**: 학습된 정책 $\pi(a|s, \theta)$
```

```ad-info
title: Note - Off-policy Characteristics

**A2C와의 차이점**: ==Actor와 Critic 모두==에 importance weight $\frac{\pi}{\beta}$ 추가

| 구성요소 | A2C (On-policy) | Off-policy AC |
|:---|:---|:---|
| **Action 생성** | $\pi(s_t)$ | ==$\beta(s_t)$== |
| **Actor update** | $+\alpha_\theta \delta_t \nabla \ln \pi$ | $+\alpha_\theta \frac{\pi}{\beta} \delta_t \nabla \ln \pi$ |
| **Critic update** | $+\alpha_w \delta_t \nabla v$ | $+\alpha_w \frac{\pi}{\beta} \delta_t \nabla v$ |

- Actor뿐 아니라 ==Critic도 IS로 off-policy 변환==
- [[Eligibility Traces]] 등 다양한 기법과 결합하여 확장 가능
```

<br/><br/>

## Related Concepts

- [[Importance Sampling]]: 분포 차이 보정을 위한 일반적 통계 기법 — off-policy 학습의 핵심
- [[Deterministic Actor-Critic]]: IS 없이 자연스럽게 off-policy하는 대안적 접근
- [[Advantage Actor-Critic]]: On-policy Actor-Critic의 대표적 알고리즘 — baseline으로 variance 감소
- [[Actor-Critic]]: Actor-Critic의 기본 구조 (QAC) — Policy Gradient + TD Learning
- [[REINFORCE]]: On-policy Monte Carlo Policy Gradient — off-policy 확장 필요성의 출발점
- [[Policy Gradient]]: Policy Gradient Theorem의 이론적 기반
- [[On-Policy vs Off-Policy]]: Behavior policy와 target policy의 관계 비교
- [[Stationary Distribution]]: Behavior policy $\beta$ 하의 상태 분포 $d_\beta$ 정의
- [[Value Function Approximation]]: Critic의 $v(s,w)$ 표현 — 함수 근사 사용
- [[Temporal Difference Learning]]: TD error $\delta_t$로 advantage function 근사

