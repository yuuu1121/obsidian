---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Monte Carlo Policy Gradient
  - REINFORCE 알고리즘
keywords:
  - REINFORCE
  - Monte Carlo Policy Gradient
  - Policy Gradient
  - Stochastic Gradient
  - Williams
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 9.4
  - title: "Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning"
    authors: [Ronald J. Williams]
    year: 1992
author:
url:
---

# REINFORCE

```ad-note
title: Summary
collapse: true

- ==REINFORCE: [[Policy Gradient]]를 Monte Carlo 추정으로 구현한 알고리즘==
- ==Stochastic Gradient: 기댓값을 샘플로 대체하여 정책 파라미터 업데이트==
- ==핵심 수식: $\theta_{t+1} = \theta_t + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta_t) q_t(s_t, a_t)$==
- ==$\beta_t = q_t / \pi$가 Exploration-Exploitation 균형을 자연스럽게 달성==
- ==가장 단순한 Policy Gradient 알고리즘 — 다른 PG 알고리즘의 기반==
```

## Definition

[[Policy Gradient]]의 gradient를 ==Monte Carlo 추정==으로 근사하여 정책을 최적화하는 알고리즘

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta_t) \cdot q_t(s_t, a_t)$$

- $\theta$: 정책 파라미터
- $\alpha > 0$: 학습률
- $\nabla_\theta \ln \pi$: ==Score function== (log-derivative)
- $q_t(s_t, a_t)$: $q_\pi(s_t, a_t)$의 ==Monte Carlo 추정치==

**수학적으로 하는 일**: 샘플 $(s_t, a_t)$가 주어지면 $\pi(a_t|s_t, \theta)$의 값을 ==gradient-ascent==로 업데이트
- $q_t > 0$: $\pi(a_t|s_t)$ ==증가== (좋은 행동 강화)
- $q_t < 0$: $\pi(a_t|s_t)$ ==감소== (나쁜 행동 억제)

```ad-info
title: Note - Why "REINFORCE"?

Williams (1992)가 제안한 ==가장 초기의 Policy Gradient 알고리즘== 중 하나

- "REward Increment = Nonnegative Factor × Offset Reinforcement × Characteristic Eligibility"의 약자
- [[Actor-Critic]], PPO, [[Advantage Actor-Critic|A2C]] 등 현대 Policy Gradient 알고리즘이 REINFORCE를 확장하여 개발됨
```

<br/><br/>

## Derivation

<!-- Chapter 9.4 Derivation -->

[[Policy Gradient]]에서 목적함수 $J(\theta)$의 gradient:

$$\nabla_\theta J(\theta) = \mathbb{E}_{S \sim \eta, A \sim \pi} \left[ \nabla_\theta \ln \pi(A|S, \theta) \cdot q_\pi(S, A) \right]$$

**Gradient Ascent** 적용 (Return ==최대화== 목적):

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta J(\theta_t)$$

| 방법 | 목적 | 최적화 |
|:---|:---|:---|
| [[Value Function Approximation]] | 오차 $\mathbb{E}[(v_\pi - \hat{v})^2]$ ==최소화== | Gradient **Descent** ($-$) |
| Policy Gradient | Return $J(\theta)$ ==최대화== | Gradient **Ascent** ($+$) |

<br/>

### Stochastic Approximation

기댓값 계산이 불가능하므로 ==샘플로 대체== ([[Stochastic Approximation]]):

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta_t) \cdot q_t(s_t, a_t)$$

- $s_t \sim \eta$ ([[Stationary Distribution]]): 정책 $\pi$ 하에서의 ==장기적 상태 방문 분포==
- $a_t \sim \pi(a|s, \theta)$: 현재 정책을 따라 행동 선택 → ==On-Policy==

$q_t(s_t, a_t)$는 ==Episode return $G_t$==로 추정 ([[Monte Carlo Methods]]):

$$q_t(s_t, a_t) \approx G_t = \sum_{k=0}^{T-t-1} \gamma^k R_{t+k+1}$$

- Monte Carlo이므로 ==에피소드 완료 후== 업데이트
- ==Unbiased== 추정치이나 ==high variance==

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - REINFORCE

**입력**: 파라미터화된 정책 $\pi(a|s, \theta)$, 학습률 $\alpha$, 할인율 $\gamma$

**초기화**: $\theta$ 임의 설정

**For** each episode:
- 정책 $\pi(\theta)$로 에피소드 생성: $\{s_0, a_0, r_1, \ldots, s_{T-1}, a_{T-1}, r_T\}$
- **For** $t = 0, 1, \ldots, T-1$:
  - **Value update**:
    $$q_t(s_t, a_t) = \sum_{k=t+1}^{T} \gamma^{k-t-1} r_k$$
  - **Policy update**:
    $$\theta \leftarrow \theta + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta) \cdot q_t(s_t, a_t)$$

**출력**: 학습된 정책 파라미터 $\theta$
```

```ad-info
title: Note - Practical Implementation

**실용적 구현**: 이상적 샘플링은 샘플 효율이 낮으므로
- 먼저 정책 $\pi(\theta)$로 ==전체 에피소드 생성==
- 에피소드 내 ==모든 경험 샘플==로 $\theta$ 다중 업데이트
- [[Monte Carlo Methods#Every-Visit Implementation|MC Every-Visit]] 전략과 유사
```

<br/><br/>

## REINFORCE with Baseline

[[Advantage Actor-Critic#Baseline Invariance|Baseline]] $b(s) = v_\pi(s)$를 도입하여 ==분산을 줄인 변형==:

$$\theta_{t+1} = \theta_t + \alpha \nabla_\theta \ln \pi(a_t|s_t, \theta_t) \cdot [q_t(s_t, a_t) - v_t(s_t)]$$

| 추정 방법 | 알고리즘 |
|:---|:---|
| $q_t$, $v_t$를 ==Monte Carlo==로 추정 | **REINFORCE with Baseline** |
| $q_t$, $v_t$를 ==TD Learning==으로 추정 | [[Advantage Actor-Critic\|A2C]] |

- **Baseline 효과**: $q_t$ (절대값) → $q_t - v_t$ (상대값)으로 ==variance 감소==, bias는 그대로 (unbiased)

<br/><br/>

## Exploration-Exploitation Balance

$\nabla_\theta \ln \pi = \frac{\nabla_\theta \pi}{\pi}$를 대입하면:

$$\theta_{t+1} = \theta_t + \alpha \underbrace{\frac{q_t(s_t, a_t)}{\pi(a_t|s_t, \theta_t)}}_{\beta_t} \nabla_\theta \pi(a_t|s_t, \theta_t)$$

$\beta_t$는 ==Effective learning rate==로, 업데이트의 ==방향==과 ==크기==를 동시에 결정

**Direction (방향)**: $\text{sign}(\beta_t) = \text{sign}(q_t)$
- $q_t > 0$: $\pi(a_t|s_t)$ ==증가== → 좋은 행동 강화
- $q_t < 0$: $\pi(a_t|s_t)$ ==감소== → 나쁜 행동 억제

**Magnitude (크기)**: $|\beta_t| = |q_t| / \pi$ → ==Exploration-Exploitation Balance==
- $|q_t|$가 클수록 → ==더 강한 업데이트== (**Exploitation**: 높은 가치의 행동에 집중)
- $\pi$가 작을수록 → ==더 강한 업데이트== (**Exploration**: 덜 시도한 행동에 기회 부여)
	- 현재 $\pi$가 낮은 행동이 $q_t > 0$을 얻으면, 분모가 작아 $\beta_t$가 커짐 → ==덜 시도한 행동에 더 큰 업데이트==

```ad-example
title: Example - Exploration Effect
collapse: true

상태 $s$에서 두 행동이 동일한 가치 $q = 1$을 가질 때:
- $a_1$: $\pi = 0.9$ (자주 선택) → $\beta = 1/0.9 \approx 1.1$ (작은 업데이트)
- $a_2$: $\pi = 0.1$ (거의 안 선택) → $\beta = 1/0.1 = 10$ (==큰 업데이트==)

→ 같은 가치라면 ==덜 시도한 행동($a_2$)==에 더 큰 기회 부여

[[Epsilon-Greedy Policy]]가 ==강제로 랜덤 탐색==하는 것과 달리, REINFORCE는 ==가치 기반으로 탐색 유도==
```

```ad-important
title: Proof - $\beta_t$ Determines Probability Change
collapse: true

$\theta_{t+1} - \theta_t$가 충분히 작을 때 Taylor expansion 적용:

$$\begin{aligned}
\pi(a_t|s_t, \theta_{t+1}) &\approx \pi(a_t|s_t, \theta_t) + (\nabla_\theta \pi)^T (\theta_{t+1} - \theta_t) \\
&= \pi(a_t|s_t, \theta_t) + \alpha\beta_t \|\nabla_\theta \pi(a_t|s_t, \theta_t)\|_2^2
\end{aligned}$$

$\alpha > 0$, $\|\nabla_\theta \pi\|_2^2 \geq 0$이므로 확률 변화는 $\beta_t$의 부호에 의해 결정됨 $\square$
```

<br/><br/>

## Related Concepts

- [[Policy Gradient]]: REINFORCE의 이론적 기반 — Policy Gradient Theorem 제공
- [[Monte Carlo Methods]]: Return $G_t$ 추정 방법 — Episode 완료 후 계산
- [[Stochastic Approximation]]: 기댓값을 샘플로 대체하는 이론적 기반
- [[Stationary Distribution]]: 샘플링 분포 $\eta$의 정의
- [[Actor-Critic]]: REINFORCE를 TD로 확장한 알고리즘
- [[Advantage Actor-Critic]]: Baseline + TD 추정 — REINFORCE with Baseline의 TD 버전
- [[Epsilon-Greedy Policy]]: 강제적 탐색 방식 — REINFORCE의 자연스러운 탐색과 대비

