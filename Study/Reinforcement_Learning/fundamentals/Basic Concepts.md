---
date: 2025-12-29
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - RL 기본 개념
  - 강화학습 기초
keywords:
  - Basic Concepts
  - Reinforcement Learning
  - MDP
  - State
  - Action
  - Reward
  - Policy
related notes:
  - [[State and Observation]]
  - [[Action]]
  - [[Policy]]
  - [[Reward]]
  - [[Markov Decision Process]]
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 1
author:
url:
---

# Basic Concepts

```ad-note
title: Summary
collapse: true

- ==강화학습 핵심 용어들의 간단한 정의와 개별 노트 링크==
- ==Agent가 Environment와 상호작용하며 Reward를 최대화하는 Policy 학습==
- ==State, Action, Reward, Policy, Return, Value Function이 핵심 구성 요소==
- ==Value Function: 정책의 좋고 나쁨을 평가하는 기준==
- ==MDP 프레임워크로 모든 개념 통합==
```

![[Pasted image 20251230170941.png|700]]

<br/>

## State and Action

**[[State and Observation|State]]** ($s$)
- ==에이전트의 현재 상황==
- State Space: $S = \{s_1, s_2, ..., s_n\}$

**[[Action]]** ($a$)
- ==에이전트가 선택하는 행동==
- Action Space: $A = \{a_1, a_2, ..., a_m\}$
- ==상태별로 가능한 행동이 다를 수 있음==: $A(s) \subseteq A$
  - 예: 경계 상태 $s_1$에서 $a_1$(상), $a_4$(좌) 선택 시 충돌 → $A(s_1) = \{a_2, a_3, a_5\}$로 제한 가능
  - 일반적으로는 $A(s_i) = A$ for all $i$로 설정 (가장 일반적인 경우)

**[[Transition Probability|State Transition]]**
- ==행동에 따른 상태 변화==
- 확률로 표현: $p(s'|s, a)$

<br/><br/>

## Policy

**[[Policy]]** ($\pi$)
- ==각 상태에서 행동 선택 규칙==
- **Deterministic**: $a = \mu(s)$ — 상태마다 ==하나의 행동==을 확정적으로 선택
- **Stochastic**: $\pi(a|s)$ — 상태에서 행동을 ==확률 분포==로 선택

<br/><br/>

## Reward and Return

**[[Reward]]** ($r$)
- ==행동 후 환경이 주는 즉각적 피드백==

**[[Return]]** ($G_t$)
- ==trajectory를 따라 받는 총 보상==
- $G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + ...$
- ==즉각적 보상이 최대인 행동이 최적 행동은 아님== → Return(총 보상)을 기준으로 판단

**[[Reward#Discount Factor|Discount Factor]]** ($\gamma$)
- ==미래 보상의 현재 가치==, $\gamma \in (0, 1)$
- $\gamma = 0$: 근시안적
- $\gamma \to 1$: 원시안적

<br/><br/>

## Value Function

**[[Value Function]]**
- ==정책 $\pi$를 따를 때 기대되는 Return==

**State Value** $v_\pi(s)$
- 상태 $s$에서 시작하여 $\pi$를 따를 때의 ==기대 Return==
- $v_\pi(s) = \mathbb{E}_\pi[G_t | S_t = s]$

**Action Value** $q_\pi(s, a)$
- 상태 $s$에서 행동 $a$를 취한 후 $\pi$를 따를 때의 ==기대 Return==
- $q_\pi(s, a) = \mathbb{E}_\pi[G_t | S_t = s, A_t = a]$

<br/><br/>

## Trajectory and Episode

**[[Rollout|Trajectory]]** ($\tau$)
- ==상태-행동-보상의 연속 시퀀스==
- $\tau = (s_0, a_0, r_0, s_1, a_1, r_1, ...)$

**[[Episode]]**
- ==시작부터 종료 상태까지의 완전한 trajectory==
- 무한 trajectory → $\gamma < 1$ 필수

<br/><br/>

## Markov Decision Process

**[[Markov Decision Process|MDP]]**
- ==위 개념들을 통합하는 수학적 프레임워크==
- $\mathcal{M} = \langle S, A, P, R, \gamma \rangle$

**[[Markov Property]]**
- ==미래는 현재 상태와 행동에만 의존, 과거와 독립==
- $p(s_{t+1}|s_t, a_t) = p(s_{t+1}|s_0, a_0, ..., s_t, a_t)$

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: RL 개요 및 핵심 개념
- [[State and Observation]]: 상태와 관찰의 정의
- [[Action]]: 행동과 행동 공간
- [[Policy]]: 정책의 종류와 표현
- [[Reward]]: 보상 신호의 정의
- [[Return]]: 누적 보상과 할인율
- [[Value Function]]: 상태/행동 가치 함수 — 기대 Return
- [[Bellman Equation]]: 가치 함수의 재귀적 관계
- [[Rollout]]: Trajectory와 샘플 생성
- [[Episode]]: 에피소드와 Absorbing State
- [[Transition Probability]]: 상태 전이 확률
- [[Markov Decision Process]]: MDP 상세 정의
- [[Markov Property]]: 마르코프 특성
