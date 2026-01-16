---
date: 2025-01-27
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - MRP
  - 마르코프 보상 과정
keywords:
  - Markov Reward Process
  - Value Function
  - Return
  - Bellman Equation
  - Reward Function
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 1
  - title: "RL Course"
    authors: [David Silver]
    year: 2015
author:
url:
---

# Markov Reward Process

```ad-note
title: Summary
collapse: true

- ==MP + Reward = 가치 평가 가능한 시스템==
- ==$\mathcal{M} = \langle \mathcal{S}, \mathcal{P}, \mathcal{R}, \gamma \rangle$==
- ==각 상태의 장기적 가치를 Value Function으로 계산==
- ==Action 없음 → 고정된 정책 평가용, 최적화는 MDP에서==
```

## Definition

<!-- Chapter 1, David Silver Lecture 2 -->

==[[Markov Process|MP]]에 [[Reward]] 신호를 추가한 모델==

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{P}, \mathcal{R}, \gamma \rangle$$

| 구성요소 | 정의 |
|:---|:---|
| $\mathcal{S}$ | 유한 상태 집합 |
| $\mathcal{P}(s, s')$ | 상태 전이 확률 |
| $\mathcal{R}$ | 보상 집합, 기대 보상: $r(s) = \sum_r p(r\|s) r = \mathbb{E}[R_{t+1} \mid S_t = s]$ |
| $\gamma$ | [[Reward#Discount Factor|할인 인자]] — Continuing tasks에서 Return 수렴 보장 |

**MRP의 특징**:
- 각 상태의 [[Value Function|가치]] 계산 가능: $v(s) = \mathbb{E}[G_t \mid S_t = s]$
  - $G_t$: [[Return]] — 시점 $t$부터의 누적 할인 보상 $\sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$
- ==같은 상태에서도 경로에 따라 Return이 다름== → 기댓값 사용
- **한계**: Action 선택 불가, ==고정된 정책 평가용== → [[Markov Decision Process|MDP]]에서 Action 도입으로 해결

<br/><br/>

```ad-info
title: Note - Bellman Equation for MRP

MRP에서 [[Bellman Equation]]은 ==Action이 없어 단순화==:

$$v(s) = r(s) + \gamma \sum_{s' \in \mathcal{S}} p(s'|s) v(s')$$

- ==즉각 보상 $r(s)$== + ==할인된 미래 가치 $\gamma \sum_{s'} p(s'|s) v(s')$==
- **Matrix Form**: $v = r + \gamma Pv$ → Direct solution: $v = (I - \gamma P)^{-1} r$
```

<br/><br/>

## Related Concepts

- [[Markov Process]]: MRP에서 Reward 제거 — $\langle \mathcal{S}, \mathcal{P} \rangle$
- [[Markov Decision Process]]: MRP에 Action 추가 — 최적 정책 탐색
- [[Markov Property]]: MRP의 기본 가정 — 미래가 현재에만 의존
- [[Value Function]]: 상태의 장기적 가치 $v(s)$
- [[Bellman Equation]]: 가치함수의 재귀적 관계
- [[Return]]: 누적 할인 보상 $G_t$
- [[Reward]]: 즉각 보상 $R_{t+1}$
- [[Transition Probability]]: 상태 전이 확률 $p(s'|s)$
- [[Dynamic Programming]]: Bellman Equation 기반 iterative 해법
