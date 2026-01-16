---
date: 2025-12-29
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 행동
  - Action Space
keywords:
  - Action
  - Action Space
  - Discrete Action
  - Continuous Action
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 1
author:
url:
---

# Action

<!-- Chapter 1 -->

```ad-note
title: Summary
collapse: true

- ==Action $a$: 에이전트가 상태에서 선택하는 행동==
- ==Action Space $\mathcal{A}$: 모든 가능한 행동의 집합==
- ==State-dependent: $\mathcal{A}(s) \subseteq \mathcal{A}$==
- ==Discrete vs Continuous 분류==
```

## Definition

==에이전트가 특정 상태에서 환경에 대해 수행하는 선택==

$$a \in \mathcal{A}$$

- $\mathcal{A}$: Action Space — 가능한 모든 행동의 집합
- 선택된 행동은 [[Transition Probability|상태 전이]]와 [[Reward|보상]]에 영향
- [[Markov Decision Process]]의 핵심 구성 요소

<br/>

### Action Space ($\mathcal{A}$)

$$\mathcal{A} = \{a_1, a_2, \ldots, a_m\}$$

- **State-dependent**: 상태에 따라 가능한 행동이 다를 수 있음
  $$\mathcal{A}(s) \subseteq \mathcal{A}$$
- 일반적으로 $\mathcal{A}(s) = \mathcal{A}$로 설정

```ad-info
title: Note - Action Classification

| 유형 | 정의 | 예시 |
|:---|:---|:---|
| **Discrete** | ==유한개의 행동== $\|\mathcal{A}\| < \infty$ | 상/하/좌/우, 게임 버튼 |
| **Continuous** | ==연속적인 실수 범위== $\mathcal{A} \subset \mathbb{R}^d$ | 로봇 관절 각도, 조향각 |

- Discrete → Q-Learning, DQN
- Continuous → Policy Gradient, Actor-Critic
```

```ad-example
title: Example - Grid World Actions
collapse: true

| Action | Direction | Index |
|:---|:---|:---|
| $a_1$ | 상 (up) | 1 |
| $a_2$ | 우 (right) | 2 |
| $a_3$ | 하 (down) | 3 |
| $a_4$ | 좌 (left) | 4 |
| $a_5$ | 정지 (stay) | 5 |

- 전체: $\mathcal{A} = \{a_1, a_2, a_3, a_4, a_5\}$
- 모서리 상태 $s_1$: $\mathcal{A}(s_1) = \{a_2, a_3, a_5\}$ (경계 제외)
```

```ad-info
title: Note - Action Selection

행동 선택은 [[Policy|정책]] $\pi$에 의해 결정

- **Deterministic**: $a = \mu(s)$
- **Stochastic**: $a \sim \pi(\cdot|s)$, $\sum_{a} \pi(a|s) = 1$
```

<br/><br/>

## Related Concepts

- [[State and Observation]]: 행동 선택의 기반이 되는 상태
- [[Policy]]: 상태에서 행동을 선택하는 규칙 $\pi(a|s)$
- [[Reward]]: 행동 수행 후 받는 피드백
- [[Markov Decision Process]]: Action이 포함된 프레임워크 $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$
- [[Value Function]]: Action-Value Function $q_\pi(s,a)$
- [[Transition Probability]]: 행동에 따른 상태 전이 $p(s'|s,a)$
