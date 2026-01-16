---
date: 2025-07-27
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - MDP
  - 마르코프 결정 과정
keywords:
  - Markov Decision Process
  - State Space
  - Action Space
  - State Transition Probability
  - Reward Probability
  - Model
  - Dynamics
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 1
author:
url:
---

# Markov Decision Process

```ad-note
title: Summary
collapse: true

- ==MDP: 강화학습 문제를 수학적으로 표현하는 프레임워크==
- ==$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$==
- ==Sets + Model (Dynamics) + Policy로 구성==
- ==MDP + Policy → MRP로 축소== ($p_\pi(s'|s), p_\pi(r|s)$)
```

## Definition

<!-- Chapter 1 -->

==[[Markov Reward Process|MRP]]에 Action을 추가하여 의사결정이 가능한 모델==

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$$

- [[Markov Property]] 만족: ==미래는 현재 상태와 행동에만 의존==
- **Finite MDP**: $|\mathcal{S}| < \infty$, $|\mathcal{A}| < \infty$ — 가장 기본적인 경우

<br/><br/>

## Sets

### State Space ($\mathcal{S}$)

- ==에이전트가 존재할 수 있는 모든 [[State and Observation|상태]]의 집합==
- $\mathcal{S} = \{s_1, s_2, \ldots, s_n\}$

<br/>

### Action Space ($\mathcal{A}(s)$)

- ==에이전트가 선택할 수 있는 모든 [[Action|행동]]의 집합==
- $\mathcal{A} = \{a_1, a_2, \ldots, a_m\}$
- 상태별로 다를 수 있음: $\mathcal{A}(s) \subseteq \mathcal{A}$

<br/>

### Reward Set ($\mathcal{R}$)

- ==가능한 모든 [[Reward|보상]] 값의 집합==
- 기대 보상: $\sum_r p(r|s,a) r$

<br/>

### Discount Factor ($\gamma$)

- ==미래 보상의 현재 가치를 결정하는 할인 인자==
- $\gamma \in [0, 1]$
- [[Return]] 계산에 사용: $G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$

<br/><br/>

## Model (Dynamics)

==State transition probability와 reward probability를 통칭하여 model 또는 dynamics라 함==

| 유형 | 정의 | 특징 |
|:---|:---|:---|
| **Stationary** | 전이/보상 확률이 시간에 따라 불변 | 대부분의 MDP 가정 |
| **Nonstationary** | 시간에 따라 환경 동역학 변화 | 더 현실적이나 분석 어려움 |

### State Transition Probability ($p(s'|s, a)$)

==현재 상태와 행동이 주어졌을 때 다음 상태로 [[Transition Probability|전이]]할 확률==

$$p(s'|s, a) = \mathbb{P}[S_{t+1}=s' \mid S_t=s, A_t=a]$$

- 정규화 조건: $\sum_{s' \in \mathcal{S}} p(s'|s, a) = 1$

<br/>

### Reward Probability ($p(r|s, a)$)

==상태와 행동에 따른 보상의 확률 분포==

$$p(r|s, a) = \mathbb{P}[R_{t+1}=r \mid S_t = s, A_t = a]$$

- 정규화 조건: $\sum_{r \in \mathcal{R}} p(r|s, a) = 1$
- 기대 보상: $\sum_r p(r|s,a) r$

<br/><br/>

## Policy

==상태에서 [[Action|행동]]을 선택하는 규칙== ([[Policy]]에서 상세 설명)

$$\pi(a|s) = \mathbb{P}[A_t = a \mid S_t = s]$$

```ad-info
title: Note - MDP + Policy → MRP

Policy $\pi$를 고정하면 MDP가 [[Markov Reward Process|MRP]]로 축소됨.

**이유**: MDP에서 전이/보상 확률은 ==상태와 행동 $(s, a)$에 의존==. 정책 $\pi(a|s)$가 고정되면 행동 선택이 결정되므로, [[Law of Total Probability]]로 행동을 marginalize out:

$$p_\pi(s'|s) = \sum_{a} \pi(a|s) \cdot p(s'|s, a), \quad p_\pi(r|s) = \sum_{a} \pi(a|s) \cdot p(r|s, a)$$

→ 결과적으로 ==상태 $s$에만 의존==하는 전이/보상 확률 → MRP 구조
```

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: MDP를 기반으로 한 학습 프레임워크
- [[Markov Property]]: MDP의 핵심 가정 — 미래가 현재 상태와 행동에만 의존
- [[Markov Reward Process]]: MDP - Action = MRP — Policy 고정 시 MDP가 MRP로 축소
- [[Markov Process]]: MRP - Reward = MP — 상태 전이만 모델링하는 순수 확률 과정
- [[Policy]]: 상태에서 행동을 선택하는 규칙 $\pi(a|s)$
- [[Transition Probability]]: 상태 전이 확률 $p(s'|s,a)$ — MDP 동역학의 핵심
- [[Reward]]: 보상 확률 $p(r|s,a)$ — 행동의 즉각적 피드백
- [[Return]]: 누적 할인 보상 $G_t$ — $\gamma$로 할인
- [[Value Function]]: 정책의 가치 평가 $v_\pi(s)$, $q_\pi(s,a)$
- [[Bellman Equation]]: 가치함수의 재귀적 관계식
- [[Bellman Optimality Equation]]: 최적 정책 $\pi^*$ 도출의 이론적 기반
- [[Dynamic Programming]]: Model-based MDP 해법 — $p(s'|s,a)$, $p(r|s,a)$ 필요
