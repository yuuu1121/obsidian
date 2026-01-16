---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 가치함수
  - Value Function
  - Q-Function
  - State Value
  - Action Value
keywords:
  - Value Function
  - State Value
  - Action Value
  - Q-Function
  - Optimal Value
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 3
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Value Function

```ad-note
title: Summary
collapse: true

- ==Value Function: 특정 상태/행동에서 시작해 받을 누적 보상(Return)의 기댓값==
- ==State Value $v_\pi(s)$: "상태 $s$에 있는 것이 얼마나 좋은가?"==
- ==Action Value $q_\pi(s,a)$: "상태 $s$에서 행동 $a$를 취하는 것이 얼마나 좋은가?"==
- ==$v$와 $q$는 상호 변환 가능== — 가치 기반 RL 알고리즘의 핵심
- ==[[Policy Evaluation]]과 정책 개선의 핵심 도구==
```

## Definition

<!-- Chapter 3 from Mathematical Foundations of RL -->

==특정 상태에서 정책 $\pi$를 따라갔을 때 받을 누적 보상([[Return]])의 기댓값==

$$v_\pi(s) = \mathbb{E}_\pi[G_t | S_t = s], \quad q_\pi(s,a) = \mathbb{E}_\pi[G_t | S_t = s, A_t = a]$$

- $v_\pi(s)$: ==State value== — 상태 $s$의 가치
- $q_\pi(s,a)$: ==Action value== — 상태 $s$에서 행동 $a$의 가치
- ==즉각 보상이 아닌 미래까지 고려한 총 보상==

정의대로 계산하면 무한한 미래 보상이 필요 → [[Bellman Equation]]이 ==재귀적 분해==로 해결. 
[[Policy Evaluation]]은 Bellman Equation을 풀어 $v_\pi$를 계산하는 알고리즘

<br/><br/>

## State Value Function

==상태 $s$에서 시작하여 정책 $\pi$를 따랐을 때 얻는 기대 return==

$$v_\pi(s) = \mathbb{E}_\pi[G_t | S_t = s] = \mathbb{E}_\pi\left[\sum_{k=0}^{\infty} \gamma^k R_{t+k+1} \middle| S_t = s\right]$$

- Stochastic 시스템에서 같은 상태라도 [[Return|return]]이 다름 → ==기댓값== 사용
- ==State value로 정책의 우열 비교 가능== → [[Policy#Optimal Policy|optimal policy]]는 state value를 기준으로 정의

```ad-info
title: Note - Properties of State Value

- **$s$ 의존**: $S_t = s$를 조건으로 하는 조건부 기댓값 → 시작 상태에 따라 상이
- **$\pi$ 의존**: ==동일 상태라도 [[Policy|정책]]에 따라 trajectory가 다름== → 가치 상이
- **$t$ 독립**: ==어떤 시점에 상태 $s$에 도달하든 그 상태의 가치는 동일== (stationary policy)
```

<br/><br/>

## Action Value Function

==상태 $s$에서 행동 $a$를 취한 후 정책 $\pi$를 따랐을 때 얻는 기대 return==

$$q_\pi(s,a) = \mathbb{E}_\pi[G_t | S_t = s, A_t = a]$$

- $(s, a)$ 쌍에 대해 정의 → ==State-Action Value==라고도 부름
- 첫 행동만 $a$로 고정, 이후는 $\pi$ 따름
- $q^*(s,a)$를 알면 ==환경 모델 없이== 최적 정책 도출: $\pi^*(s) = \arg\max_a q^*(s,a)$

```ad-warning
title: Note - Unselected Actions Have Value Too

==정책이 선택하지 않는 action도 action value 존재==

흔한 오해: 정책 $\pi$가 선택하지 않는 action의 가치는 계산할 필요 없거나 0이다 → ==틀림==

- 정책이 action $a$를 선택하지 않아도, 해당 action을 취했을 때 얻을 return의 기댓값은 정의됨
- 예: $\pi$가 $a_1$을 선택하지 않아도 $q_\pi(s, a_1) = r + \gamma v_\pi(s')$로 계산 가능
- 현재 정책이 최적이 아닐 수 있음 → ==더 좋은 action을 놓치고 있을 가능성==
- RL의 목표는 최적 정책 탐색 → 모든 action을 탐색해야 더 나은 정책 발견 가능
```

<br/><br/>

## Relationship between $v$ and $q$

==State value와 action value는 서로를 통해 계산 가능== — 가치 기반 RL 알고리즘의 핵심

<br/>

### From Action Value to State Value

조건부 기댓값에 대한 [[Marginalization]] (기댓값의 [[Law of Total Probability]]):

$$\underbrace{\mathbb{E}[G_t | S_t = s]}_{v_\pi(s)} = \sum_{a \in \mathcal{A}} \underbrace{\mathbb{E}[G_t | S_t = s, A_t = a]}_{q_\pi(s,a)} \pi(a|s)$$

따라서:

$$v_\pi(s) = \sum_a \pi(a|s) q_\pi(s,a)$$

→ ==State value는 해당 상태의 action value들의 가중 평균== (가중치: 정책 확률)

<br/>

### From State Value to Action Value

[[Bellman Equation]]에서 action value의 구조를 확인:

$$v_{\pi}(s) = \sum_{a \in \mathcal{A}} \pi(a|s) \underbrace{\left[ \sum_{r \in \mathcal{R}} p(r|s, a)r + \gamma \sum_{s' \in \mathcal{S}} p(s'|s, a)v_{\pi}(s') \right]}_{q_\pi(s,a)}$$

대괄호 안이 $q_\pi(s,a)$:

$$q_\pi(s,a) = \underbrace{\sum_r p(r|s,a) r}_{\text{immediate reward}} + \gamma \underbrace{\sum_{s'} p(s'|s,a) v_\pi(s')}_{\text{future reward}}$$

→ ==Action value는 즉각 보상 + 할인된 다음 state value의 기댓값==

```ad-info
title: Note - Two Sides of the Same Coin

$v$와 $q$는 ==동전의 양면==:

| 변환 | 수식 | 해석 |
|:---|:---|:---|
| $v \leftarrow q$ | $v_\pi(s) = \sum_a \pi(a|s) q_\pi(s,a)$ | Action value의 ==기댓값== |
| $q \leftarrow v$ | $q_\pi(s,a) = r(s,a) + \gamma \sum_{s'} p(s'\|s,a) v_\pi(s')$ | ==즉각 보상 + 미래 가치== |

- [[Value Iteration]], [[Policy Iteration]]: 주로 $v$ 사용
- [[Q-Learning]], [[Sarsa]]: 주로 $q$ 사용
```

<br/><br/>

## Optimal Value Functions

<!-- Chapter 3.7 from Mathematical Foundations of RL -->

==모든 정책 중 최대 가치를 달성하는 함수==

$$v^*(s) = \max_\pi v_\pi(s), \quad q^*(s,a) = \max_\pi q_\pi(s,a)$$

- $v^*(s)$: 상태 $s$에서 ==달성 가능한 최대 기대 return==
- $q^*(s,a)$: 상태 $s$에서 행동 $a$를 취했을 때 ==달성 가능한 최대 기대 return==

```ad-info
title: Note - Properties of Optimal Value

- **유일성**: ==$v^*$, $q^*$는 항상 유일== — MDP가 주어지면 단 하나
- **MDP 해결**: $v^*$ 또는 $q^*$를 알면 ==MDP 완전히 해결==
- **정책 도출**: $q^*$에서 직접 [[Policy#Optimal Policy|최적 정책]] 도출
  $$\pi^*(s) = \arg\max_a q^*(s,a)$$
  - 정의 $\pi^* = \arg\max_\pi v_\pi(s)$와 ==논리적으로 동치== ($\max_\pi v_\pi = v^* = \max_a q^*$)
- **Model-Free**: ==$q^*$만 알면 환경 모델 없이== 최적 행동 선택 가능
```

<br/>

### Relationship

최적 가치 함수 간의 관계:

$$v^*(s) = \max_a q^*(s,a)$$

→ ==최적 state value = 최선 행동의 action value==

$$q^*(s,a) = \sum_r p(r|s,a) r + \gamma \sum_{s'} p(s'|s,a) v^*(s')$$

→ ==최적 action value = 즉각 보상 + 할인된 다음 최적 state value==

<br/>

### Computation

[[Bellman Optimality Equation]]이 최적 가치의 재귀적 관계 정의:

$$v^*(s) = \max_a \left[\sum_r p(r|s,a) r + \gamma \sum_{s'} p(s'|s,a) v^*(s')\right]$$

- ==비선형 방정식== ($\max$ 연산 포함) — 일반 Bellman Equation과 달리 closed-form 해 없음
- [[Contraction Mapping Theorem]]에 의해 ==해의 존재성/유일성 보장==
- 계산 알고리즘: [[Value Iteration]], [[Q-Learning]] 등

```ad-info
title: Note - Why Action Value is More Useful

==Action value $q^*$가 최적 정책 탐색에서 더 직접적인 역할==

| 가치 함수 | 최적 정책 도출 | Model 필요 |
|:---|:---|:---|
| $v^*$ | $\pi^*(s) = \arg\max_a [r(s,a) + \gamma \sum_{s'} p(s'\|s,a) v^*(s')]$ | ==필요== |
| $q^*$ | $\pi^*(s) = \arg\max_a q^*(s,a)$ | ==불필요== |

- $v^*$로 정책 도출 시 ==전이 확률 $p(s'|s,a)$ 필요== (Model-Based)
- $q^*$로 정책 도출 시 ==단순 argmax만== 필요 (Model-Free)
- 따라서 [[Q-Learning]] 등 Model-Free 알고리즘은 $q$를 학습
```

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: 가치 함수를 활용한 정책 최적화 프레임워크
- [[Return]]: $v_\pi(s) = \mathbb{E}[G_t | S_t = s]$ — State value는 Return의 기댓값
- [[Policy]]: 가치함수 계산의 기준 — 동일 상태라도 정책에 따라 가치 상이
- [[Bellman Equation]]: $v_\pi = r_\pi + \gamma P_\pi v_\pi$ — 가치 함수의 재귀적 관계
- [[Bellman Optimality Equation]]: $v^* = \max_a [r + \gamma P v^*]$ — 최적 가치의 재귀적 관계
- [[Policy Evaluation]]: 주어진 정책 $\pi$에 대해 $v_\pi$를 계산하는 알고리즘
- [[Policy Iteration#Policy Improvement|Policy Improvement]]: $q_\pi(s,a)$를 사용해 더 나은 정책으로 개선
- [[Value Iteration]]: $v^*$를 직접 계산하는 알고리즘
- [[Q-Learning]]: $q^*$를 모델 없이 학습하는 Off-Policy 알고리즘
- [[Sarsa]]: $q_\pi$를 학습하는 On-Policy 알고리즘
- [[Value Function Approximation]]: 대규모 상태 공간에서 가치 함수를 함수로 근사
- [[Markov Decision Process]]: 가치함수가 정의되는 프레임워크
- [[Contraction Mapping Theorem]]: 최적 가치 함수의 존재성/유일성 보장

