---
date: 2026-01-12
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Actor-Critic Methods
  - 액터-크리틱
  - AC
  - QAC
keywords:
  - Actor-Critic
  - QAC
  - Policy Gradient
  - Sarsa
  - TD Learning
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 10
author:
url:
---

# Actor-Critic

```ad-note
title: Summary
collapse: true

- ==Actor-Critic: Policy-based (Actor)와 Value-based (Critic)의 결합==
- ==Actor: 정책 $\pi(a|s,\theta)$ 업데이트== — Policy Gradient 사용
- ==Critic: 가치 $q(s,a,w)$ 업데이트== — TD Learning ([[Sarsa]]) 사용
- ==REINFORCE (MC) → Actor-Critic (TD)==: $q_t$ 추정 방식의 차이
- ==Incremental 업데이트==로 continuing tasks 적용 가능, variance 감소
```

![[Pasted image 20260113131739.png|700]]

## Definition

<!-- Chapter 10.1 from Mathematical Foundations of RL -->

==Policy Gradient의 action value $q_\pi$를 TD Learning으로 추정==하여 정책을 최적화하는 알고리즘

$$\theta_{t+1} = \theta_t + \alpha_\theta \nabla_\theta \ln \pi(a_t|s_t, \theta_t) \cdot q(s_t, a_t, w_t)$$

- $\theta$: 정책 파라미터 (Actor)
- $w$: 가치 함수 파라미터 (Critic)
- $\alpha_\theta$: Actor 학습률
- $q(s,a,w)$: ==파라미터화된 action value 함수== (Critic이 추정)

<br/>

### Two Components

| Component | 역할 | 학습 방법 | 이름 유래 |
|:---|:---|:---|:---|
| **Actor** | 정책 $\pi(a\|s,\theta)$ 학습 | [[Policy Gradient]] | 행동을 ==선택(act)== |
| **Critic** | 가치 $q(s,a,w)$ 추정 | [[Temporal Difference Learning\|TD Learning]] ([[Sarsa]]) | 행동을 ==평가(criticize)== |

```ad-info
title: Note - Relation to REINFORCE

<!-- Chapter 10.1 motivation -->

Actor-Critic은 ==Policy Gradient 방법의 일종== — [[REINFORCE]]와 ==$q_t$ 추정 방식==만 다름

| 특성 | [[REINFORCE]] | Actor-Critic |
|:---|:---|:---|
| **$q_t$ 추정** | ==Monte Carlo== ($G_t$) | ==TD Learning== (bootstrapping) |
| **Random Variables** | $R_{t+1}, \ldots, R_T$ (==많음==) | $R_{t+1}, S_{t+1}$ (==적음==) |
| **업데이트 시점** | 에피소드 종료 후 | ==매 스텝== (incremental) |
| **적용 환경** | Episodic tasks만 | ==Continuing tasks 포함== |
| **Bias** | ==없음== | 있음 ([[Bootstrapping]]) |
| **Variance** | ==높음== | ==낮음== |

- **Incremental Update**: 에피소드 종료를 기다리지 않고 ==매 스텝 학습== 가능
- **Continuing Tasks**: 종료 없는 환경 (로봇 제어, 서버 관리)에 적용 가능
```

<br/><br/>

## Algorithm

<!-- Chapter 10.1 Algorithm -->

==Q Actor-Critic (QAC)==: 가장 단순한 Actor-Critic 알고리즘으로, action value $q(s,a,w)$를 직접 사용

```ad-tldr
title: Algorithm - QAC (Q Actor-Critic)

**입력**: 정책 $\pi(a|s, \theta)$, 가치 함수 $q(s, a, w)$, 학습률 $\alpha_\theta, \alpha_w > 0$

**초기화**: $\theta_0$, $w_0$ 임의 설정

**목표**: $J(\theta)$를 최대화하는 최적 정책 학습

**For** 각 에피소드의 매 시점 $t$:
- 정책 $\pi(a|s_t, \theta_t)$에 따라 $a_t$ 생성
- $r_{t+1}$, $s_{t+1}$ 관측 후 정책에 따라 $a_{t+1}$ 생성
- **Critic** (value update):
  $$w_{t+1} = w_t + \alpha_w \delta_t \nabla_w q(s_t, a_t, w_t)$$
  where $\delta_t = r_{t+1} + \gamma q(s_{t+1}, a_{t+1}, w_t) - q(s_t, a_t, w_t)$
- **Actor** (policy update):
  $$\theta_{t+1} = \theta_t + \alpha_\theta q(s_t, a_t, w_t) \nabla_\theta \ln \pi(a_t|s_t, \theta_t)$$

**출력**: 학습된 정책 $\pi(a|s, \theta)$
```

```ad-info
title: Note - Critic is Sarsa

Critic의 업데이트는 ==[[Sarsa]] + [[Value Function Approximation]]==

- TD target: $\bar{q}_t = r_{t+1} + \gamma q(s_{t+1}, a_{t+1}, w_t)$
- 다음 action $a_{t+1}$이 ==현재 정책 $\pi$로 선택==됨 → [[On-Policy vs Off-Policy|On-Policy]]
- [[Q-Learning]]처럼 $\max_a q$를 사용하지 않음
```

```ad-info
title: Note - On-Policy Characteristic

Actor-Critic은 ==On-Policy== 알고리즘

- [[Policy Gradient]]의 기댓값이 $A \sim \pi$를 요구
- ==현재 정책으로 샘플 생성== 필요 → 과거 샘플 재사용 불가
- Off-policy 확장: [[Off-policy Actor-Critic]]
```

<br/><br/>

## Extensions

<!-- Chapter 10 Summary -->

QAC를 시작으로 ==각 한계를 해결하며 점진적으로 확장==되는 Actor-Critic 알고리즘 계열:

| 알고리즘 | 핵심 아이디어 | 해결하는 문제 |
|:---|:---|:---|
| **[[Advantage Actor-Critic\|A2C]]** | Baseline $v_\pi$ 추가 | ==Variance 감소== |
| **[[Off-policy Actor-Critic]]** | [[Importance Sampling]] | ==샘플 재사용== (off-policy) |
| **[[Deterministic Actor-Critic]]** | Deterministic policy $\mu(s)$ | ==연속 행동 공간==, 자연스러운 off-policy |

<br/>

### Evolution Path

- **QAC → A2C**: Policy gradient는 ==baseline에 불변== → optimal baseline $v_\pi$로 variance 감소
- **A2C → Off-policy AC**: On-policy 한계 (샘플 재사용 불가) → ==Importance Sampling==으로 off-policy 확장
- **Off-policy AC → Deterministic AC**: Stochastic policy는 action 샘플링 필요 → ==Deterministic policy==로 action 샘플링 제거

<br/><br/>

## Related Concepts

- [[Policy Gradient]]: Actor 업데이트의 이론적 기반 — Policy Gradient Theorem 제공
- [[REINFORCE]]: MC 기반 Policy Gradient — $q_t$ 추정 방식만 다름
- [[Advantage Actor-Critic]]: Baseline 추가로 variance 감소한 Actor-Critic
- [[Off-policy Actor-Critic]]: Importance Sampling으로 off-policy 확장
- [[Deterministic Actor-Critic]]: Deterministic policy 사용
- [[Sarsa]]: Critic의 업데이트 알고리즘 — On-Policy TD Control
- [[Value Function Approximation]]: Critic의 $q(s,a,w)$ 표현
- [[Temporal Difference Learning]]: Critic의 업데이트 원리
- [[MC vs TD]]: REINFORCE와 Actor-Critic의 차이 이해에 필요
- [[On-Policy vs Off-Policy]]: Actor-Critic은 On-Policy
- [[Bootstrapping]]: TD Learning의 핵심 특성 — bias 발생 원인

