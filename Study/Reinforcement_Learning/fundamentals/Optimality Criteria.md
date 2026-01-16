---
date: 2025-12-28
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 최적성 기준
  - 정책 평가 기준
keywords:
  - Optimality Criteria
  - Policy Comparison
  - Expected Return
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
author:
url:
---

# Optimality Criteria

```ad-note
title: Summary
collapse: true

- ==정책을 비교하기 위한 기준== — "어떤 정책이 더 좋은가?"
- ==보상 시퀀스는 확률적 → 직접 비교 불가 → 단일 스칼라로 변환 필요==
- ==Expected Return $\mathbb{E}[G_t]$가 표준 기준== → [[Value Function|State Value]]
```

## Definition

==[[Markov Decision Process|MDP]]에서 정책을 비교하기 위한 기준==

```ad-info
title: Note - Scalar Metric Necessity

정책 $\pi$를 선택하면 ==확률적 보상 시퀀스==를 수신:

$$R = (R_1, R_2, \ldots, R_T)$$

- 정책 A → $(5, 3, 8, 2, \ldots)$
- 정책 B → $(4, 6, 1, 9, \ldots)$

시퀀스 직접 비교 불가 → ==단일 스칼라로 변환하는 기준 필요==
```

<br/><br/>

## Expected Return

==표준 기준: [[Return]]의 기댓값==

$$v_\pi(s) = \mathbb{E}_\pi[G_t | S_t = s] = \mathbb{E}_\pi \left[ \sum_{k=0}^{\infty} \gamma^k R_{t+k+1} \mid S_t = s \right]$$

- 보상 시퀀스 → 할인 합 ([[Return]]) → 기댓값 ([[Value Function|State Value]])
- ==확률 변수를 단일 스칼라로 변환==하여 정책 비교 가능

```ad-info
title: Note - Alternative Criteria

| 기준 | 정의 | 특징 |
|:---|:---|:---|
| **Expected Return** | $\mathbb{E}[G_t]$ | ==표준, 가장 널리 사용== |
| **Average Reward** | $\lim_{T \to \infty} \frac{1}{T} \mathbb{E}[\sum_{t=1}^T R_t]$ | Continuing tasks |
| **Risk-sensitive** | $\mathbb{E}[G_t] - \lambda \text{Var}[G_t]$ | 위험 고려 |

대부분의 RL 알고리즘은 Expected Return 기준 사용
```

<br/><br/>

## Policy Ordering

Expected Return 기준으로 ==정책 간 부분 순서== 정의:

$$\pi \geq \pi' \quad \Leftrightarrow \quad v_\pi(s) \geq v_{\pi'}(s), \quad \forall s \in \mathcal{S}$$

- ==모든 상태에서 더 높은 가치를 주는 정책이 더 좋은 정책==
- [[Policy#Optimal Policy|Optimal Policy]] $\pi^*$: 이 순서에서 ==모든 정책보다 크거나 같음==

<br/><br/>

## Related Concepts

- [[Return]]: 보상 시퀀스의 할인 합 $G_t$ — optimality criteria의 구성 요소
- [[Value Function]]: Return의 기댓값 $v_\pi(s) = \mathbb{E}[G_t]$ — 정책 비교의 실제 지표
- [[Policy#Optimal Policy|Optimal Policy]]: Expected Return을 최대화하는 정책 $\pi^*$
- [[Bellman Equation]]: Expected Return의 재귀적 관계 — $v_\pi(s) = \mathbb{E}[R + \gamma v_\pi(S')]$
- [[Bellman Optimality Equation]]: 최적 정책을 찾기 위한 방정식
