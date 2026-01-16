---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 상태
  - State
keywords:
  - State
  - Observation
  - Fully Observed
  - Partially Observed
related notes:
reference:
  - title: "RL Course"
    authors: [David Silver]
    year: 2015
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# State and Observation

```ad-note
title: Summary
collapse: true

- ==State $s$: 에이전트의 현재 상황을 나타내는 정보==
- ==Observation $o$: 에이전트가 실제로 관측하는 정보==
- ==Fully Observed: $o = s$, Partially Observed: $o \subset s$==
- ==[[Markov Property]] 만족 시 현재 상태만으로 미래 예측 가능==
```

## State

<!-- David Silver Lecture 2 -->

==에이전트의 현재 상황을 나타내는 정보==

$$s \in \mathcal{S}$$

- $\mathcal{S}$: 상태 공간 (State Space) — 가능한 모든 상태의 집합
- [[Markov Property]] 만족 시: 현재 상태만으로 미래 예측 가능

```ad-info
title: Note - Environment State vs Agent State
collapse: true

| 구분 | 정의 | 특징 |
|:---|:---|:---|
| **Environment State** | 환경의 내부 표현 | 항상 Markov, 에이전트에게 보이지 않을 수 있음 |
| **Agent State** | 에이전트가 사용하는 표현 | 알고리즘이 설계, Markov 아닐 수 있음 |

→ RL에서 "상태"는 보통 Agent State를 의미
```

<br/><br/>

## Observation

==에이전트가 환경으로부터 받는 감각 정보==

$$o \in \mathcal{O}$$

| 유형 | 조건 | 설명 |
|:---|:---|:---|
| **Fully Observed** | $o = s$ | 환경 상태 전체 관측 → MDP |
| **Partially Observed** | $o \subset s$ | 일부만 관측 → POMDP |

- Partially Observed 시: 과거 관측 히스토리나 belief state로 상태 추정 필요

<br/><br/>

## Related Concepts

- [[Markov Property]]: 상태의 핵심 가정 — 미래가 현재에만 의존
- [[Markov Decision Process]]: Fully Observed 환경의 프레임워크
- [[Action]]: 상태에서 선택하는 행동
- [[Policy]]: 상태에서 행동을 선택하는 규칙 $\pi(a|s)$
- [[Value Function]]: 상태의 가치 $v_\pi(s)$
- [[Rollout]]: 상태-행동-보상 시퀀스 (trajectory)
