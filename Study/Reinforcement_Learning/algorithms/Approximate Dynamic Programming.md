---
date: 2025-12-18
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 근사동적계획법
  - ADP
  - Curse of Dimensionality
keywords:
  - Approximate Dynamic Programming
  - Curse of Dimensionality
  - Forward DP
  - Sampling
related notes:
reference:
  title: "Lecture 11 - Approximate DP"
  source: "IMEN 764: Dynamic Programming & Reinforcement Learning Applications"
author: Dong Gu Choi
url:
---

# Approximate Dynamic Programming

```ad-note
title: Summary
collapse: true

- ==**차원의 저주**: 상태/행동/전이 공간이 기하급수적 증가 → DP 적용 불가==
- ==**ADP가 해결하는 문제**: (1) 문제가 너무 큼, (2) MDP 모델 요소를 모름==
- ==**핵심 아이디어**: 모든 상태 순회 대신 **샘플링 + 시뮬레이션**으로 근사==
- ==**한계**: 방문 안 한 상태 추정 불가, 수렴 보장 없음 → RL로 발전==
```

## Definition

==차원의 저주로 인해 정확한 DP 적용이 불가능한 대규모 MDP에서, 샘플링과 시뮬레이션 기반으로 가치 함수를 근사하는 방법론==

<br/><br/>

## Curse of Dimensionality

### DP의 근본적 한계

기존 DP 알고리즘 ([[Value Iteration]], [[Policy Iteration]]):

$$V^{n+1}(s) = \max_{a \in \mathcal{A}_s} \left\{ g(s,a) + \gamma \sum_{s' \in \mathcal{S}} p(s'|s,a) V^n(s') \right\} \quad \text{for all } s \in \mathcal{S}$$

→ ==**"모든 상태 순회"**==가 필수

### Three Dimensions of Curse

| 차원 | 구조 | 복잡도 |
|:---|:---|:---|
| **State space** | $s = (s_1, s_2, \ldots, s_I)$, 각 $L$개 값 | $L^I$ 상태 |
| **Action space** | $a = (a_1, a_2, \ldots, a_K)$, 각 $N$개 값 | $N^K$ 행동 |
| **Transition space** | $w = (w_1, w_2, \ldots, w_J)$, 각 $M$개 값 | $M^J$ 전이 |

**예시**: 10차원 상태, 각 100개 값 → $100^{10} = 10^{20}$ 상태

<br/><br/>

## Two Issues ADP Addresses

| Issue | 문제 | 해결 방향 |
|:---|:---|:---|
| **Issue 1** | 문제가 너무 큼 (차원의 저주) | 샘플링으로 계산량 감소 |
| **Issue 2** | 전이 확률 $p(s'\|s,a)$의 명시적 수식 미지 | → RL (Model-Free) |

<br/><br/>

## ADP vs Reinforcement Learning

| | ADP (좁은 의미) | Reinforcement Learning |
|:---|:---|:---|
| **초점** | Issue 1: 큰 문제 | Issue 2: 모델 미지 |
| **가정** | MDP 모델(전이 확률) 알고 있음 | 전이 확률 수식 없음 (Model-Free) |
| **방법** | 샘플링으로 계산량 감소 | 환경 상호작용으로 직접 학습 |

<br/><br/>

## ADP Core Idea

| 방식 | 특징 |
|:---|:---|
| **기존 DP** (Backward, Exhaustive) | 모든 상태 순회, 미래→현재 계산 |
| **ADP** (Forward, Simulation-based) | 샘플 경로 생성, 현재→미래 진행, 일부 상태만 방문 |

```
기존 DP:  모든 상태 × 모든 행동 × 모든 전이 → 정확한 V
    ↓ (불가능)
ADP:      샘플 상태 × 최적 행동 × 샘플 전이 → 근사 V̂
```

<br/><br/>

## Basic Algorithm

### Assumptions

- $|\mathcal{A}| \ll |\mathcal{S}|$ (행동 공간 < 상태 공간)
- MDP 모델의 모든 요소 (전이 확률 $p$, 보상 $g$) 알고 있음

### Algorithm Steps

**(1) Initialization**: $V^0_t(s) = 0$ for all $s, t$

**(2) Sample Generation**: 초기 상태 $s_0$, 샘플 경로 $\omega$ 랜덤 생성

**(3) Forward Sweep**: $t = 0, 1, \ldots, T$

$$\hat{v}_t = \max_{a \in A_{s_t}} \left[ g_t(s_t, a) + \gamma \sum_{s'} p_t(s'|s_t, a) V^{k-1}_{t+1}(s') \right]$$

$$V^k_t(s) = \begin{cases} \hat{v}_t & \text{if } s = s_t \\ V^{k-1}_t(s) & \text{otherwise} \end{cases}$$

→ ==**방문한 상태만 업데이트**==, 나머지는 이전 값 유지

**(4) Iteration**: $k \leftarrow k + 1$, 반복

<br/><br/>

## Limitations

| 한계 | 설명 |
|:---|:---|
| **전이 확률 필요** | $\sum_{s'} p(s'\|s,a) V(s')$ 계산에 여전히 필요 |
| **방문 상태만 업데이트** | 미방문 상태의 가치는 $V^0 = 0$ 유지 |
| **Exploration 문제** | 방문 안 한 좋은 상태 발견 불가 |
| **수렴 보장 없음** | 기본 알고리즘은 수렴 미보장 |

### 기존 DP vs ADP

| | 기존 DP | ADP |
|:---|:---|:---|
| **상태 순회** | 모든 상태 | 샘플 상태만 |
| **전이 확률** | 필요 | 필요 (여전히) |
| **수렴 보장** | 보장됨 | 보장 안 됨 |
| **대규모 문제** | 불가능 | 가능 (근사) |

<br/><br/>

## Solution Directions

| ADP 한계 | 해결 방향 |
|:---|:---|
| 전이 확률 필요 | Model-Free RL ([[Monte Carlo Methods]], [[Temporal Difference Learning]]) |
| 미방문 상태 | Exploration 전략 |
| 수렴 보장 없음 | RTDP (Real-Time DP) |

<br/><br/>

## Key Insights

| 핵심 | 설명 |
|:---|:---|
| **차원의 저주** | DP의 "모든 상태 순회"가 실제 문제에서 불가능한 이유 |
| **ADP의 타협** | 정확성 포기, 계산 가능성 획득 (샘플링 기반) |
| **남은 한계** | 전이 확률 여전히 필요 → RL로 해결 |
| **DP → RL 연결** | ADP는 DP와 RL 사이의 중간 단계 |

<br/><br/>

## Related Concepts

- [[Value Iteration]]: 정확한 DP 알고리즘
- [[Policy Iteration]]: 또 다른 DP 알고리즘
- [[Monte Carlo Methods]]: Model-Free, 에피소드 기반 학습
- [[Temporal Difference Learning]]: Model-Free, 매 스텝 학습
- [[MC vs TD]]: Model-Free 방법론 비교
- [[Value Function Approximation]]: 테이블 → 함수 근사로의 전환 (차원의 저주 해결)

