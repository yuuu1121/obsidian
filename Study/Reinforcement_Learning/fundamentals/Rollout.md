---
date: 2025-01-10
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 롤아웃
  - Trajectory
keywords:
  - Rollout
  - Trajectory
  - Data Collection
  - Episode
related notes:
reference:
author:
url:
---

# Rollout

```ad-note
title: Summary
collapse: true

- ==Rollout: 현재 정책으로 환경에서 행동하며 데이터를 수집하는 과정==
- ==상태-행동-보상의 시퀀스(trajectory)를 생성, 정책 학습의 기본 데이터==
- ==Episode, trajectory와 유사하지만 데이터 수집 관점 강조==
- ==On-Policy rollout은 현재 정책, Off-Policy rollout은 다른 정책으로 수집==
```

## Definition

==Agent가 정책 $\pi$에 따라 행동 $a_t$를 선택하고, 환경에 적용해 다음 상태 $s_{t+1}$와 보상 $r_t$를 얻는 일련의 과정==

<br/><br/>

## Mathematical Formulation

### Rollout Process

시작 상태 $s_0$에서 정책 $\pi$를 따라 rollout 실행:

1. $a_0 \sim \pi(\cdot|s_0)$ (정책에서 행동 샘플링)
2. $(s_1, r_0) \sim p(\cdot, \cdot | s_0, a_0)$ (환경 전이)
3. 종료 조건까지 반복

<br/>

### Trajectory

Rollout 결과는 trajectory $\tau$ 형태:

$$\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \ldots, s_T, a_T, r_T)$$

간결한 표현: $\tau = \{(s_t, a_t, r_t)\}_{t=0}^T$

**예시 (Grid World):**

$$s_1 \xrightarrow[r=0]{a_2} s_2 \xrightarrow[r=0]{a_3} s_5 \xrightarrow[r=0]{a_3} s_8 \xrightarrow[r=1]{a_2} s_9$$

→ 상태 전이와 각 단계에서 받는 보상을 함께 표현

<br/>

### Sample Path (Markov Process)

[[Markov Process]]에서는 ==action 없이 상태만의 시퀀스==:

$$s_0 \to s_1 \to s_2 \to \ldots \to s_n$$

**Path Probability:**

$$\mathbb{P}(s_0, s_1, \ldots, s_n) = \mu_0(s_0) \prod_{t=0}^{n-1} p(s_{t+1}|s_t)$$

- $\mu_0(s_0)$: 초기 상태 분포
- $\prod p(s_{t+1}|s_t)$: [[Markov Property]]에 의한 체인 규칙

| 맥락 | 시퀀스 형태 | Action |
|:---|:---|:---|
| **MP (Sample Path)** | $s_0 \to s_1 \to \ldots$ | 없음 |
| **MDP (Trajectory)** | $(s_0, a_0, r_0, s_1, \ldots)$ | 있음 |

<br/><br/>

## Related Terms

| 용어 | 의미 | 강조점 |
|:---|:---|:---|
| **Trajectory** | Rollout과 거의 동의어 | 상태-행동 시퀀스 자체 |
| **Episode** | 하나의 시도 (터미널 상태까지) | 시도 단위 |
| **Timestep** | Rollout의 개별 단계 $(s_t, a_t, r_t)$ | 시간 단위 |

<br/><br/>

## Rollout Length

| 유형 | 설명 | Return |
|:---|:---|:---|
| **Finite Horizon** | 종료 시간 $T$ 고정 | $\sum_{t=0}^T r_t$ |
| **Infinite Horizon** | 무한히 계속 ($\gamma < 1$ 필요) | $\sum_{k=0}^\infty \gamma^k r_{t+k}$ |
| **Episode-based** | 터미널 상태 도달 시 종료 | 가변 길이 |

<br/><br/>

## Types of Rollouts

### On-Policy Rollout

현재 학습 중인 정책 $\pi$로 rollout 실행:

$$a_t \sim \pi(\cdot|s_t)$$

- **용도**: PPO, TRPO 등 on-policy 알고리즘
- **특징**: 정책 업데이트 시 새로운 rollout 필요

<br/>

### Off-Policy Rollout

다른 정책 (behavior policy) $\mu$로 rollout 실행:

$$a_t \sim \mu(\cdot|s_t)$$

- **용도**: DQN, SAC 등 off-policy 알고리즘
- **특징**: 과거 rollout 재사용 가능 (Experience Replay)

<br/>

### Exploratory Rollout

탐험을 위한 노이즈 추가:

$$a_t \sim \pi(\cdot|s_t) + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, \sigma^2)$$

<br/><br/>

## Applications

| 용도 | 설명 |
|:---|:---|
| **Policy Evaluation** | $J(\pi) = \mathbb{E}_{\tau \sim \pi}[\sum_{t=0}^T r_t]$ |
| **Policy Learning** | $\theta \leftarrow \theta + \alpha \nabla_\theta J(\pi_\theta)$ |
| **Model Learning** | $\hat{p}(s_{t+1}, r_t \| s_t, a_t) \approx p$ |
| **Value Estimation** | MC 방식: $V(s_0) \approx \frac{1}{N} \sum_{i=1}^N \sum_t r_t^{(i)}$ |

<br/><br/>

## Practical Considerations

### Number of Rollouts

| 방식 | 특징 |
|:---|:---|
| **On-Policy** | 매 업데이트마다 다수 rollout 수집 (예: 1000개) |
| **Off-Policy** | 소수 rollout을 buffer에 저장 후 재사용 |

<br/>

### Parallelization

효율성을 위해 여러 환경에서 동시 rollout:

- **Vectorized Environments**: 병렬 시뮬레이터
- **Distributed RL**: 여러 워커가 독립적으로 rollout

<br/>

### Rollout Buffer

Off-policy 알고리즘에서 rollout 저장:
- 용량: 보통 $10^5 \sim 10^6$ transitions
- 샘플링: 무작위 batch 추출하여 학습

<br/><br/>

## Return

Trajectory의 Return: 수집한 모든 보상의 합

| 통계량 | 정의 |
|:---|:---|
| **Return** | $G(\tau) = \sum_{t=0}^T r_t$ |
| **Discounted Return** | $G(\tau) = \sum_{t=0}^T \gamma^t r_t$ |

→ 자세한 내용은 [[Reward#Return (Cumulative Reward)|Reward - Return]] 참조

<br/><br/>

## Related Concepts

- [[Policy]]: Rollout을 생성하는 정책
- [[Action]]: Trajectory의 구성 요소
- [[Episode]]: Rollout과 유사 (시도 단위)
- [[Reward]]: Trajectory의 구성 요소
- [[Markov Process]]: Sample Path의 원천 — action 없는 상태 시퀀스
- [[Markov Property]]: Path Probability의 체인 규칙 기반
- [[On-Policy vs Off-Policy]]: Rollout 수집 방식의 차이
- [[Monte Carlo Methods]]: Rollout을 이용한 가치 추정

