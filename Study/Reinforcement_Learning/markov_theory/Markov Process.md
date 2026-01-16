---
date: 2025-07-27
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - MP
  - Markov Chain
  - 마르코프 과정
  - 마르코프 체인
  - DTMC
keywords:
  - Markov Process
  - Markov Chain
  - State Transition
  - Transition Probability Matrix
  - Sample Path
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

# Markov Process

```ad-note
title: Summary
collapse: true

- ==[[Markov Property]]를 만족하는 상태들의 확률적 시퀀스==
- ==$\mathcal{M} = \langle \mathcal{S}, P \rangle$ (상태 집합 + 전이 행렬)==
- ==Markov Chain: 이산 시간 + 이산 상태인 Markov Process==
- ==Reward/Action 없음 → MRP, MDP로 확장==
```

## Definition

<!-- Chapter 1, David Silver Lecture 2 -->

==[[Markov Property]]를 만족하는 상태들의 확률적 시퀀스==

→ 미래 상태가 ==현재 상태에만 의존==하고 과거와 독립인 확률 과정

$$\mathcal{M} = \langle \mathcal{S}, P \rangle$$

| 구성요소 | 정의 |
|:---|:---|
| $\mathcal{S}$ | 상태 집합 |
| $P$ | 상태 전이 행렬, $[P]_{ij} = p(s_j \mid s_i)$ |

**RL에서의 역할:**
- Action 없이 확률에 따라 상태 전이
- Reward 없어 가치 평가 불가 → [[Markov Reward Process|MRP]]로 확장

<br/>

### Markov Process vs Markov Chain

| | Markov Process | Markov Chain |
|:---|:---|:---|
| 시간 | 연속/이산 모두 가능 | ==이산 시간== (discrete-time) |
| 상태 공간 | 연속/이산 모두 가능 | ==이산 상태== (finite/countable) |
| 별칭 | - | DTMC (Discrete-Time Markov Chain) |

- **Markov Chain**: ==이산 시간 + 이산 상태==인 Markov Process의 특수한 경우
- RL에서는 주로 finite state, discrete-time을 다루므로 ==두 용어 혼용==

<br/><br/>

## State Transition Probability

==현재 상태 $s$에서 다음 상태 $s'$로 전이할 [[Transition Probability|확률]]==

$$p(s'|s) = P(S_{t+1} = s' \mid S_t = s)$$

- [[Markov Property]]에 의해 ==과거 이력 $S_0, \ldots, S_{t-1}$과 독립==
- 정규화: $\sum_{s' \in \mathcal{S}} p(s'|s) = 1$

### Transition Probability Matrix

$n \times n$ 크기의 ==Row Stochastic Matrix== ($n = |\mathcal{S}|$):

$$P = \begin{pmatrix}
p(s_1|s_1) & p(s_2|s_1) & \cdots & p(s_n|s_1) \\
p(s_1|s_2) & p(s_2|s_2) & \cdots & p(s_n|s_2) \\
\vdots & \vdots & \ddots & \vdots \\
p(s_1|s_n) & p(s_2|s_n) & \cdots & p(s_n|s_n)
\end{pmatrix}$$

- $[P]_{ij} = p(s_j|s_i)$: 상태 $s_i$에서 $s_j$로의 전이 확률
- ==각 행의 합 = 1== (확률의 정규화): $\sum_j [P]_{ij} = 1$
- ==$P^k$==: $k$-step 전이 확률 행렬 — $[P^k]_{ij} = p(s_j | s_i, k \text{ steps})$

```ad-info
title: Note - [[Rollout#Sample Path (Markov Process)|Sample Path]]
collapse: true

MP에서 생성된 ==상태 시퀀스==: $s_0 \to s_1 \to s_2 \to \ldots$

- 각 전이는 확률 $P$에 따라 확률적으로 결정
- [[Episode]]: Terminal state로 끝나는 유한 sample path
```

<br/><br/>

## Related Concepts

- [[Markov Property]]: MP의 정의적 성질 — 미래가 현재에만 의존
- [[Markov Reward Process]]: MP + Reward — 가치 평가 가능
- [[Markov Decision Process]]: MRP + Action — 최적 정책 탐색
- [[Transition Probability]]: 상태 전이 확률 $p(s'|s)$
- [[Stationary Distribution]]: MP의 장기 상태 분포 — $d^T P = d^T$
- [[Rollout]]: Sample path 생성 (trajectory)
- [[Episode]]: Terminal state로 끝나는 유한 sample path
