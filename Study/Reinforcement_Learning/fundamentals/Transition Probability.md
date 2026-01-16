---
date: 2025-01-11
tags:
  - Concepts/ReinforcementLearning/Fundamentals
  - Concepts/Fundamentals/Probability
aliases:
  - 전이 확률
  - State Transition Probability
keywords:
  - Transition Probability
  - Markov Property
  - State Transition
  - MDP
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
author:
url:
---

# Transition Probability

```ad-note
title: Summary
collapse: true

- ==현재 상태 $s$와 행동 $a$가 주어졌을 때 다음 상태 $s'$로 전이할 조건부 확률==
- ==[[Markov Property]] 만족: 과거 이력과 독립, 현재 상태와 행동에만 의존==
- ==[[Markov Decision Process|MDP]]의 핵심 구성 요소로 환경의 동역학(dynamics)을 모델링==
```

## Definition

<!-- Chapter 2 -->

==상태 $s$에서 행동 $a$를 선택했을 때, 다음 상태 $s'$로 전이할 조건부 확률==

$$p(s'|s, a) = P(S_{t+1} = s' \mid S_t = s, A_t = a)$$

- $s, s' \in \mathcal{S}$: 현재/다음 상태
- $a \in \mathcal{A}(s)$: 선택한 행동
- ==확률 공리 만족==: $p(s'|s, a) \geq 0$, $\sum_{s'} p(s'|s, a) = 1$

```ad-info
title: Note - MP vs MDP Context

| 맥락 | 표기 | 의존성 |
|:---|:---|:---|
| **[[Markov Process\|MP]]** | $p(s'\|s)$ | 현재 상태만 |
| **[[Markov Decision Process\|MDP]]** | $p(s'\|s, a)$ | 현재 상태 + 행동 |

- MP: 정책 없이 환경 자체의 전이 확률
- MDP: 행동에 따라 전이 확률이 달라짐
- Transition Matrix는 [[Markov Process#Transition Probability Matrix|Markov Process]]에서 상세히 다룸
```

<br/>

### Markov Property

==전이 확률의 핵심 가정==

$$P(S_{t+1} = s' \mid S_1, A_1, \ldots, S_t, A_t) = P(S_{t+1} = s' \mid S_t, A_t)$$

- 다음 상태는 ==현재 상태와 행동에만 의존==
- 과거 이력 $(S_1, A_1, \ldots, S_{t-1}, A_{t-1})$과 ==조건부 독립==
- 이 성질이 [[Dynamic Programming]]과 RL 알고리즘을 가능하게 함

<br/><br/>

## Properties

### Time-Homogeneous vs Time-Inhomogeneous

| 유형 | 정의 | 특징 |
|:---|:---|:---|
| **Time-Homogeneous** | $p_t(s'\|s, a) = p(s'\|s, a)$ | 시간에 무관하게 일정 |
| **Time-Inhomogeneous** | $p_t \neq p_{t'}$ for some $t \neq t'$ | 시간에 따라 변화 |

대부분의 RL 문제는 ==time-homogeneous== 가정

<br/>

### Deterministic vs Stochastic

| 유형 | 정의 | 표현 |
|:---|:---|:---|
| **Deterministic** | $p(s'\|s, a) = 1$ for unique $s'$ | $s_{t+1} = f(s_t, a_t)$ |
| **Stochastic** | $0 < p(s'\|s, a) < 1$ for multiple $s'$ | 환경에 불확실성 존재 |

```ad-example
title: Example - Slippery Grid World
collapse: true

4x4 그리드에서 확률적 전이:

| 전이 방향 | 확률 |
|:---|:---|
| 의도한 방향 | 80% |
| 직교 방향 (각각) | 10% |

상태 $(2, 2)$에서 "상" 행동 선택 시:
- $p((2, 3)|(2, 2), \text{상}) = 0.8$ — 의도한 방향
- $p((1, 2)|(2, 2), \text{상}) = 0.1$ — 좌측으로 미끄러짐
- $p((3, 2)|(2, 2), \text{상}) = 0.1$ — 우측으로 미끄러짐

→ Stochastic 환경에서 ==최적 정책이 결정론적 환경과 다를 수 있음==
```

<br/><br/>

## Related Concepts

- [[Markov Decision Process]]: 전이 확률을 핵심 구성 요소로 포함하는 프레임워크
- [[Markov Property]]: 전이 확률이 만족하는 조건부 독립 성질
- [[Markov Process]]: 정책 고정 시 전이 확률이 정의하는 확률 과정
- [[Bellman Equation]]: 전이 확률로 기댓값 계산
- [[Reward]]: 전이와 함께 MDP 동역학을 정의
- [[Dynamic Programming]]: Markov Property 기반 최적화 방법론
