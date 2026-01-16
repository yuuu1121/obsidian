---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 에이전트와 환경
keywords:
  - Agent
  - Environment
  - Interaction Loop
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

# Agent and Environment

<!-- David Silver Lecture 1 -->

```ad-note
title: Summary
collapse: true

- ==Agent: 학습하고 의사결정을 수행하는 주체==
- ==Environment: 에이전트가 상호작용하는 외부 세계==
- ==Interaction Loop: 관찰 → 행동 → 보상 → 관찰 (반복)==
- ==목표: [[Return|누적 보상]]을 최대화하는 [[Policy|최적 정책]] 학습==
```

## Definition

| 구성요소 | 정의 |
|:---|:---|
| **Agent** | ==학습하고 의사결정을 수행하는 주체== — 시행착오로 학습 |
| **Environment** | ==에이전트가 상호작용하는 외부 세계== — [[Markov Decision Process]]로 모델링 |

<br/><br/>

## Interaction Loop

==시간 단계별 순환적 상호작용 과정==

- **Step 1**: 에이전트가 환경으로부터 [[State and Observation|관찰]] $o_t$ 수신
- **Step 2**: 관찰을 바탕으로 [[Action|행동]] $a_t$ 선택
- **Step 3**: 환경이 다음 상태 $s_{t+1}$로 [[Transition Probability|전이]]
- **Step 4**: [[Reward|보상]] $r_{t+1}$과 새 관찰 $o_{t+1}$ 제공
- **Step 5**: 종료 조건까지 반복

<br/><br/>

## Agent

==학습하고 의사결정을 수행하는 주체==

에이전트는 다음 중 하나 이상을 포함:

| 구성요소 | 정의 | 수식 |
|:---|:---|:---|
| **[[Policy]]** | 행동 선택 규칙 | $\pi(a\|s)$ |
| **[[Value Function]]** | 상태/행동의 가치 평가 | $v_\pi(s)$, $q_\pi(s,a)$ |
| **Model** | 환경 동역학의 내부 표현 | $p(s'\|s,a)$, $p(r\|s,a)$ |

**Objective**: [[Return|누적 보상]] 최대화

$$\max_\pi \mathbb{E}_\pi[G_t] = \max_\pi \mathbb{E}_\pi\left[\sum_{k=0}^{\infty} \gamma^k R_{t+k+1}\right]$$

<br/><br/>

## Environment

==에이전트가 존재하고 상호작용하는 외부 세계==

- 에이전트의 행동에 반응하여 [[Transition Probability|상태 전이]] 및 [[Reward|보상]] 제공

```ad-info
title: Note - Environment Classification

**By Observability**:
- **Fully Observable (MDP)**: $o_t = s_t$
- **Partially Observable (POMDP)**: $o_t \subset s_t$

**By Dynamics**:
- **Deterministic / Stochastic**: 전이의 결정성
- **Stationary / Non-stationary**: 시간에 따른 동역학 변화
```

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: 에이전트-환경 상호작용 기반 학습 패러다임
- [[State and Observation]]: 상태 $s$와 관찰 $o$의 구분
- [[Action]]: 에이전트가 선택하는 행동 $a \in \mathcal{A}$
- [[Policy]]: 상태에서 행동을 선택하는 규칙 $\pi(a|s)$
- [[Value Function]]: 상태/행동의 가치 평가 $v_\pi(s)$, $q_\pi(s,a)$
- [[Reward]]: 환경이 제공하는 스칼라 피드백 $r$
- [[Markov Decision Process]]: 환경의 수학적 모델
