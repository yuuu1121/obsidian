---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 강화학습
  - RL
keywords:
  - Reinforcement Learning
  - Sequential Decision Making
  - Trial and Error
  - Reward Signal
  - Agent-Environment Interaction
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 1
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
  - David Silver's RL Course
author:
url:
---

# Reinforcement Learning

```ad-note
title: Summary
collapse: true

- ==순차적 의사결정 문제를 시행착오를 통해 해결하는 학습 방법론==
- ==Agent가 Environment와 상호작용하며 Return $G_t$를 최대화하는 Policy 학습==
- ==핵심 도전: Exploration-Exploitation, Delayed Reward, Credit Assignment==
- ==Supervised/Unsupervised Learning과 달리 환경과의 상호작용으로 데이터 생성==
```

## Definition

==순차적 의사결정(Sequential Decision Making) 문제를 시행착오(Trial and Error)를 통해 해결==하는 학습 방법론

- **목표**: 장기적 누적 보상 ([[Return]] $G_t$)를 최대화하는 최적 [[Policy]] $\pi^*$ 학습
- **학습 신호**: 환경으로부터 받는 스칼라 [[Reward]] $R_t$
- **특징**: 정답을 알려주는 감독자 없이, ==환경과의 상호작용으로 경험을 생성==하며 학습

| 학습 패러다임 | 학습 신호 | 데이터 | 특징 |
|:---|:---|:---|:---|
| Supervised Learning | 정답 레이블 | 고정 데이터셋 | 데이터 품질 = 성능 상한 |
| Unsupervised Learning | 없음 | 고정 데이터셋 | 패턴/구조 발견 |
| **Reinforcement Learning** | ==보상 신호== | ==상호작용으로 생성== | 데이터 한계를 넘어설 수 있음 |

<br/><br/>

## Agent-Environment Framework

![[Pasted image 20251230170941.png|500]]

RL의 기본 구조: [[Agent and Environment|Agent]]가 [[Agent and Environment|Environment]]와 상호작용

$$S_t \xrightarrow{\pi} A_t \xrightarrow{\text{Env}} R_{t+1}, S_{t+1}$$

- **Agent**: 상태 $S_t$를 관측하고 정책 $\pi$에 따라 행동 $A_t$ 선택
- **Environment**: 행동을 받아 다음 상태 $S_{t+1}$과 보상 $R_{t+1}$ 반환
- **Trajectory**: $(S_0, A_0, R_1, S_1, A_1, R_2, \ldots)$ → [[Episode]] 형성

```ad-info
title: Note - RL vs Dynamic Programming

| | Dynamic Programming | Reinforcement Learning |
|:---|:---|:---|
| **모델** | $p(s',r\|s,a)$ ==알려짐== | ==모름== (Model-Free) |
| **학습** | 계산으로 해결 | ==경험으로 학습== |
| **대표** | [[Value Iteration]], [[Policy Iteration]] | [[Q-Learning]], [[Temporal Difference Learning\|TD]], [[Monte Carlo Methods\|MC]] |

RL은 환경 모델 없이 ==샘플 기반 학습==을 수행하는 것이 핵심
```

<br/><br/>

## Learning Objective

==기대 Return의 최대화==:

$$\pi^* = \arg\max_\pi \mathbb{E}_\pi[G_t], \quad G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$$

- $G_t$: [[Return]] — 할인된 누적 보상
- $\gamma \in [0, 1)$: [[Reward#Discount Factor|Discount Factor]] — 미래 보상의 현재 가치
- $\pi^*$: 최적 정책 — 모든 상태에서 최대 가치를 달성

**학습 과정**:
1. **Policy Evaluation**: 현재 정책 $\pi$의 [[Value Function|가치 함수]] $v_\pi(s)$, $q_\pi(s,a)$ 추정
2. **Policy Improvement**: 가치 함수를 기반으로 더 나은 정책 도출
3. **반복**: 수렴할 때까지 1-2 반복 → $\pi^*$ 획득

<br/><br/>

## Key Challenges

RL이 다른 학습 방법과 구별되는 ==핵심 도전 과제==

<br/>

### Exploration vs Exploitation

새로운 지식 탐색과 현재 지식 활용 사이의 ==균형== ([[Exploration vs Exploitation]])

- **Exploration**: 더 나은 정책을 찾기 위해 새로운 행동 시도
- **Exploitation**: 현재까지 최선으로 알려진 행동 선택

<br/>

### Delayed Reward

행동의 결과가 ==즉시 나타나지 않음==

- 체스에서 한 수가 게임 종료 후에야 평가됨
- 로봇 보행에서 넘어지기 전 여러 행동 중 어떤 것이 원인인지 불명확

<br/>

### Credit Assignment

과거 행동 중 ==어떤 것이 현재 보상에 기여==했는지 결정

- 긴 trajectory에서 각 행동의 공로 배분 문제
- [[Temporal Difference Learning]]이 이 문제를 효과적으로 해결

<br/>

### Non-Stationarity

Agent의 학습이 ==환경 데이터 분포를 변화==시킴

- 정책이 개선되면 방문하는 상태 분포가 달라짐
- 고정 데이터셋 가정의 Supervised Learning과 근본적 차이

<br/><br/>

## Solution Approaches

RL 문제 해결을 위한 ==주요 접근법==

### By Learning Target

==무엇을 학습하는가==에 따른 분류:

| 접근법 | 학습 대상 | 정책 도출 | 대표 알고리즘 |
|:---|:---|:---|:---|
| **Value-Based** | $q(s,a)$ | $\pi(s) = \arg\max_a q(s,a)$ | [[Q-Learning]], [[Sarsa]] |
| **Policy-Based** | $\pi_\theta(a\|s)$ | 직접 출력 | [[Policy Gradient]], REINFORCE |
| **Actor-Critic** | $\pi_\theta$ + $v(s)$ | Actor 출력 | PPO, SAC, [[Advantage Actor-Critic|A2C]] |

<br/>

### By Environment Model

==환경 모델 사용 여부==에 따른 분류:

| | Model-Free | Model-Based |
|:---|:---|:---|
| **모델** | ==사용 안 함== | ==학습 또는 주어짐== |
| **학습** | 경험에서 직접 | 모델로 시뮬레이션 |
| **샘플 효율** | 낮음 | 높음 |
| **대표** | DQN, PPO, SAC | Dyna, MuZero |

<br/>

### By Data Usage

==행동 정책과 학습 정책의 관계==에 따른 분류:

| | On-Policy | Off-Policy |
|:---|:---|:---|
| **정의** | 행동 정책 = 학습 정책 | 행동 정책 ≠ 학습 정책 |
| **데이터 재사용** | 불가 | 가능 (Experience Replay) |
| **대표** | [[Sarsa]], PPO | [[Q-Learning]], DQN, SAC |

<br/><br/>

## Algorithm Landscape

RL 알고리즘의 계보:

```
                    RL Algorithms
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Value-Based     Policy-Based    Actor-Critic
         │               │               │
    ┌────┴────┐         │          ┌────┴────┐
    │         │         │          │         │
Tabular   Function      │       A2C/A3C    PPO
  TD      Approx.       │          │       SAC
    │         │         │          │      DDPG
    │    ┌────┴───┐     │          │       TD3
    │    │        │     │          │
 Sarsa  DQN    TD-Linear REINFORCE │
Q-Learn                  PG        │
                                   │
                         ┌─────────┴─────────┐
                      On-Policy          Off-Policy
```

**핵심 알고리즘**:
- **Tabular**: [[Monte Carlo Methods]], [[Temporal Difference Learning]], [[Sarsa]], [[Q-Learning]]
- **Function Approximation**: [[TD-Linear]], [[Deep Q-Learning|DQN]], [[Policy Gradient]]
- **Modern**: PPO, SAC, TD3

<br/><br/>

## Mathematical Framework

RL 문제는 [[Markov Decision Process|MDP]]로 형식화:

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, p, r, \gamma \rangle$$

- $\mathcal{S}$: 상태 공간
- $\mathcal{A}$: 행동 공간
- $p(s'|s,a)$: 전이 확률
- $r(s,a)$: 보상 함수
- $\gamma$: 할인율

**핵심 방정식**:
- [[Bellman Equation]]: $v_\pi(s) = \mathbb{E}_\pi[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s]$
- [[Bellman Optimality Equation]]: $v^*(s) = \max_a [r(s,a) + \gamma \sum_{s'} p(s'|s,a) v^*(s')]$

<br/><br/>

## Related Concepts

- [[Basic Concepts]]: RL 핵심 용어 요약
- [[Agent and Environment]]: Agent-Environment 상호작용 상세
- [[Markov Decision Process]]: RL의 수학적 프레임워크
- [[Policy]]: 행동 선택 전략
- [[Value Function]]: 상태/행동의 가치 평가
- [[Bellman Equation]]: 가치 함수의 재귀적 관계
- [[RL Agent Taxonomy]]: 에이전트 분류 체계
- [[Temporal Difference Learning]]: Bootstrapping 기반 학습
- [[Monte Carlo Methods]]: Episode return 기반 학습

