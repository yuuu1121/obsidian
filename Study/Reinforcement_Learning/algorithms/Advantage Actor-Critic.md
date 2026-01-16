---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - A2C
  - Advantage Actor-Critic Methods
keywords:
  - Advantage Actor-Critic
  - A2C
  - Advantage Function
  - Baseline
  - Variance Reduction
  - TD Error
  - TD Actor-Critic
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 10.2
author:
url:
---

# Advantage Actor-Critic

```ad-note
title: Summary
collapse: true

- ==A2C: Advantage function $\delta = q - v$를 사용하여 분산을 줄이는 Actor-Critic==
- ==Baseline Invariance: $b(S)$를 빼도 gradient 기댓값은 불변==, 분산만 변화
- ==Optimal Baseline이 복잡하여 $v_\pi(s)$를 실용적 baseline으로 사용==
- ==TD Error로 근사: $\delta_t \approx r + \gamma v(s') - v(s)$==, 단일 네트워크로 구현 가능
```

## Definition

<!-- Chapter 10.2 from Mathematical Foundations of RL -->

[[Actor-Critic|QAC]]를 확장하여 ==Advantage function $\delta = q - v$를 사용하여 분산을 줄이는== Actor-Critic 알고리즘

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta_t) \cdot \delta_t(s_t, a_t)$$

- $\theta$: 정책 파라미터
- $\alpha$: 학습률
- $\delta_t(s, a) = q_t(s, a) - v_t(s)$: ==Advantage function== (평균 대비 상대적 가치)

<br/>

### Advantage Function

$$\delta_\pi(s, a) \doteq q_\pi(s, a) - v_\pi(s)$$

- $\delta > 0$: 평균보다 좋은 action → 확률 ==증가==
- $\delta < 0$: 평균보다 나쁜 action → 확률 ==감소==
- ==$q$의 절대적 값==이 아닌 ==$v$ 대비 상대적 값==으로 정책 업데이트

```ad-info
title: Note - Relative Value

특정 상태에서 action을 선택할 때, ==어떤 action이 다른 action들보다 얼마나 좋은지==만 중요

- 모든 action의 value가 높아도, 상대적으로 나쁜 action은 억제됨
- 모든 action의 value가 낮아도, 상대적으로 좋은 action은 강화됨
```

<br/><br/>

## Baseline Invariance

<!-- Chapter 10.2.1 -->

[[Actor-Critic|QAC]]는 $q_\pi$를, A2C는 $q_\pi - v_\pi$를 사용. Policy Gradient는 baseline $b(S)$에 대해 ==불변(invariant)==이므로 차감 가능:

$$\mathbb{E}_{S \sim \eta, A \sim \pi} \left[ \nabla_\theta \ln \pi(A|S, \theta) q_\pi(S, A) \right] = \mathbb{E}_{S \sim \eta, A \sim \pi} \left[ \nabla_\theta \ln \pi(A|S, \theta) (q_\pi(S, A) - b(S)) \right]$$

- $\eta$: [[Stationary Distribution]]
- 위 등식이 성립하려면 $\mathbb{E}[\nabla_\theta \ln \pi(A|S, \theta) b(S)] = 0$이어야 함

```ad-important
title: Proof - Baseline Invariance
collapse: true

$$\begin{aligned}
\mathbb{E}_{S \sim \eta, A \sim \pi} \left[ \nabla_{\theta} \ln \pi (A|S, \theta) b(S) \right] &= \sum_{s \in \mathcal{S}} \eta(s) \sum_{a \in \mathcal{A}} \pi(a|s, \theta) \nabla_{\theta} \ln \pi(a|s, \theta) b(s) \\
&= \sum_{s \in \mathcal{S}} \eta(s) \sum_{a \in \mathcal{A}} \nabla_{\theta} \pi(a|s, \theta) b(s) \\
&= \sum_{s \in \mathcal{S}} \eta(s) b(s) \sum_{a \in \mathcal{A}} \nabla_{\theta} \pi(a|s, \theta) \\
&= \sum_{s \in \mathcal{S}} \eta(s) b(s) \nabla_{\theta} \sum_{a \in \mathcal{A}} \pi(a|s, \theta) \\
&= \sum_{s \in \mathcal{S}} \eta(s) b(s) \nabla_{\theta} 1 = 0
\end{aligned}$$

$\sum_a \pi(a|s) = 1$이므로, 그 gradient는 0 $\square$
```

<br/><br/>

## Baseline Selection

<!-- Chapter 10.2.2 -->

Gradient 기댓값은 불변이지만, ==분산은 baseline $b(S)$에 따라 달라짐==

$$X(S, A) = \nabla_\theta \ln \pi(A|S, \theta) [q_\pi(S, A) - b(S)]$$

- ==$\text{var}(X)$가 작으면== 샘플들이 $\mathbb{E}[X]$ 근처에 밀집 → ==단일 샘플로도 정확한 근사==
- ==$\text{var}(X)$가 크면== 샘플이 $\mathbb{E}[X]$에서 멀어질 수 있음 → ==업데이트 불안정==
- [[REINFORCE]]와 [[Actor-Critic|QAC]]는 $b = 0$ 사용 (==최적이 아님==)

<br/>

### Optimal Baseline

분산 $\text{var}(X)$를 최소화하는 ==최적 baseline==:

$$b^*(s) = \frac{\mathbb{E}_{A \sim \pi} \left[ \left\| \nabla_\theta \ln \pi(A|s, \theta) \right\|^2 q_\pi(s, A) \right]}{\mathbb{E}_{A \sim \pi} \left[ \left\| \nabla_\theta \ln \pi(A|s, \theta) \right\|^2 \right]}, \quad s \in \mathcal{S}$$

- $q_\pi$의 ==가중 평균== (가중치: $\|\nabla_\theta \ln \pi\|^2$)
- ==실용적으로 사용하기에 너무 복잡함==

```ad-important
title: Proof - Optimal Baseline
collapse: true

$\bar{x} = \mathbb{E}[X]$로 정의하면, $\bar{x}$는 임의의 $b(s)$에 대해 불변

$X$가 벡터이면 분산 $\text{var}(X)$는 행렬이 됨. 최적화를 위해 ==분산의 trace를 스칼라 목적함수==로 사용:

$$\begin{aligned}
\text{tr}[\text{var}(X)] &= \text{tr}\mathbb{E}[(X - \bar{x})(X - \bar{x})^T] \\
&= \text{tr}\mathbb{E}[XX^T - \bar{x}X^T - X\bar{x}^T + \bar{x}\bar{x}^T] \\
&= \mathbb{E}[X^T X - X^T \bar{x} - \bar{x}^T X + \bar{x}^T \bar{x}] \\
&= \mathbb{E}[X^T X] - \bar{x}^T \bar{x}
\end{aligned}$$

위 유도에서 trace 성질 $\text{tr}(AB) = \text{tr}(BA)$를 사용

$\bar{x}$가 불변이므로, ==$\mathbb{E}[X^T X]$만 최소화==하면 됨

<br/>

$X(S, A) = \nabla_\theta \ln \pi(A|S, \theta)[q_\pi(S, A) - b(S)]$를 대입하면:

$$\begin{aligned}
\mathbb{E}[X^T X] &= \mathbb{E}\left[(\nabla_\theta \ln \pi)^T (\nabla_\theta \ln \pi)(q_\pi(S, A) - b(S))^2\right] \\
&= \mathbb{E}\left[\|\nabla_\theta \ln \pi\|^2 (q_\pi(S, A) - b(S))^2\right]
\end{aligned}$$

$S \sim \eta$, $A \sim \pi$이므로:

$$\mathbb{E}[X^T X] = \sum_{s \in \mathcal{S}} \eta(s) \mathbb{E}_{A \sim \pi}\left[\|\nabla_\theta \ln \pi\|^2 (q_\pi(s, A) - b(s))^2\right]$$

<br/>

$\nabla_b \mathbb{E}[X^T X] = 0$이 되도록 각 $s \in \mathcal{S}$에 대해 $b(s)$를 풀면:

$$\mathbb{E}_{A \sim \pi}\left[\|\nabla_\theta \ln \pi\|^2 (b(s) - q_\pi(s, A))\right] = 0, \quad s \in \mathcal{S}$$

$b(s)$에 대해 정리하면:

$$b^*(s) = \frac{\mathbb{E}_{A \sim \pi}\left[\|\nabla_\theta \ln \pi\|^2 q_\pi(s, A)\right]}{\mathbb{E}_{A \sim \pi}\left[\|\nabla_\theta \ln \pi\|^2\right]}, \quad s \in \mathcal{S} \quad \square$$
```

<br/>

### Suboptimal Baseline

가중치를 무시하면 (모든 action에 동일한 가중치) ==단순 평균==이 되어 ==간결한 차선책==:

$$b^\dagger(s) = \mathbb{E}_{A \sim \pi}[q_\pi(s, A)] = v_\pi(s), \quad s \in \mathcal{S}$$

- ==State value $v_\pi(s)$가 suboptimal baseline==이며, 실용적이고 계산 가능
- 이 baseline을 사용하면 $q_\pi(s,a) - v_\pi(s) = \delta_\pi(s,a)$ → ==Advantage function==

<br/><br/>

## TD Error Approximation

<!-- Chapter 10.2.3 -->

Advantage function $\delta = q - v$를 ==TD error로 근사==하여 구현을 단순화:

$$q_t(s_t, a_t) - v_t(s_t) \approx r_{t+1} + \gamma v_t(s_{t+1}) - v_t(s_t)$$

```ad-important
title: Proof - TD Error Approximation
collapse: true

Action value의 정의에서:

$$q_\pi(s_t, a_t) = \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s_t, A_t = a_t]$$

따라서:

$$\begin{aligned}
q_\pi(s_t, a_t) - v_\pi(s_t) &= \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s_t, A_t = a_t] - v_\pi(s_t) \\
&= \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) - v_\pi(S_t) | S_t = s_t, A_t = a_t]
\end{aligned}$$

샘플 $(s_t, a_t, r_{t+1}, s_{t+1})$로 기댓값을 근사하면:

$$q_t(s_t, a_t) - v_t(s_t) \approx r_{t+1} + \gamma v_t(s_{t+1}) - v_t(s_t) \quad \square$$
```

```ad-info
title: Note - Single Network Advantage

TD error 사용의 장점: ==$v(s)$를 표현하는 단일 네트워크만 필요==

| 방식 | 필요 네트워크 | 복잡도 |
|:---|:---|:---|
| $\delta_t = q_t - v_t$ | $q(s,a,w_q)$, $v(s,w_v)$ ==2개== | 높음 |
| $\delta_t = r + \gamma v(s') - v(s)$ | ==$v(s,w)$ 1개== | 낮음 |

TD error 사용 시 ==TD Actor-Critic==이라고도 부름
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - A2C (Advantage Actor-Critic)

**입력**: 정책 $\pi(a|s, \theta)$, 가치 함수 $v(s, w)$, 학습률 $\alpha_\theta, \alpha_w > 0$

**초기화**: $\theta_0$, $w_0$ 임의 설정

**목표**: $J(\theta)$를 최대화하는 최적 정책 학습

**For** 각 에피소드의 매 시점 $t$:
- 정책 $\pi(a|s_t, \theta_t)$에 따라 $a_t$ 생성
- $r_{t+1}$, $s_{t+1}$ 관측
- **Advantage** (TD error):
  $$\delta_t = r_{t+1} + \gamma v(s_{t+1}, w_t) - v(s_t, w_t)$$
- **Actor** (policy update):
  $$\theta_{t+1} = \theta_t + \alpha_\theta \delta_t \nabla_\theta \ln \pi(a_t|s_t, \theta_t)$$
- **Critic** (value update):
  $$w_{t+1} = w_t + \alpha_w \delta_t \nabla_w v(s_t, w_t)$$

**출력**: 학습된 정책 $\pi(a|s, \theta)$
```

```ad-info
title: Note - Comparison with REINFORCE

| 특성 | REINFORCE with Baseline | A2C |
|:---|:---|:---|
| **$q_t$, $v_t$ 추정** | ==Monte Carlo== | ==TD Learning== |
| **업데이트 시점** | 에피소드 종료 후 | ==매 스텝== |
| **Bias** | Unbiased | Biased |
| **Variance** | 높음 | ==낮음== |

- A2C의 정책 $\pi(\theta)$는 ==stochastic==이므로 [[Epsilon-Greedy Policy]]와 같은 별도 탐색 기법 불필요
- Gradient가 $A \sim \pi$를 요구하므로 ==On-Policy== — 과거 샘플 재사용 불가
```

<br/><br/>

## Related Concepts

- [[Actor-Critic]]: A2C의 기반 알고리즘 — baseline 없이 $q_t$를 직접 사용하는 QAC
- [[REINFORCE]]: MC 기반 Policy Gradient — baseline을 추가하면 "REINFORCE with Baseline"
- [[Policy Gradient]]: Policy Gradient Theorem이 A2C의 이론적 기반
- [[Temporal Difference Learning]]: TD error로 advantage function을 근사
- [[Value Function]]: Suboptimal baseline $v_\pi(s)$의 정의
- [[Value Function Approximation]]: Critic의 $v(s,w)$ 표현에 사용
- [[Stochastic Approximation]]: 샘플로 기댓값을 근사하는 이론적 기반
- [[Stationary Distribution]]: Policy Gradient에서 샘플링 분포 $\eta$로 사용
- [[MC vs TD]]: REINFORCE with Baseline vs A2C의 차이 이해에 필요
- [[Off-policy Actor-Critic]]: Importance Sampling을 사용한 off-policy 확장

