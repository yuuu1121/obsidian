---
date: 2025-12-18
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 딥큐러닝
  - DQN
  - Deep Q-Network
keywords:
  - Deep Q-Learning
  - DQN
  - Experience Replay
  - Target Network
  - Q-Network
  - Deadly Triad
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8.4
  - title: "Lecture 13 - Deep Q-Learning"
    source: "IMEN 764: Dynamic Programming & Reinforcement Learning Applications"
    author: Dong Gu Choi
author:
url:
---

# Deep Q-Learning

```ad-note
title: Summary
collapse: true

- ==Deep Neural Network로 Q 함수를 근사==하여 대규모/연속 상태 공간에서 Q-Learning 적용
- ==Squared Bellman Optimality Error== 최소화: $J(w) = \mathbb{E}[(\hat{q}(S, A, w) - (R + \gamma \max_a \hat{q}(S', a, w)))^2]$
- ==Target Network==: gradient 계산 단순화 및 학습 안정화
- ==Experience Replay==: 균등 분포 가정 만족 및 데이터 효율 향상
```

## Definition

==Q-Table 대신 Deep Neural Network로 [[Value Function Approximation|Q 함수를 근사]]==하여, 대규모 또는 연속 상태 공간에서 [[Q-Learning]]을 적용할 수 있게 하는 알고리즘

$$\hat{q}(s, a, w) \approx q^*(s, a)$$

- $w$: 신경망 파라미터
- Tabular 방식은 $|\mathcal{S}| \times |\mathcal{A}|$개의 값을 저장해야 하고, 연속 공간에 적용 불가하며, 유사 상태 간 일반화가 없음
- DQN은 파라미터 $w$만 저장하여 ==메모리 효율적==이고, ==연속 공간에서도 적용 가능==하며, ==유사 상태 일반화== 가능

```ad-info
title: Note - Network Depth

Neural network가 반드시 deep할 필요는 없음:
- 간단한 task (Grid World 등): ==1-2개의 hidden layer==로 충분
- 복잡한 task (Atari 등): deeper network 필요
```

<br/><br/>

## Derivation

==Squared Bellman Optimality Error (SBOE)== 최소화 문제에서 출발:

$$J(w) = \mathbb{E}\left[\left(\hat{q}(S, A, w) - (R + \gamma \max_{a \in \mathcal{A}(S')} \hat{q}(S', a, w))\right)^2\right]$$

- $(S, A, R, S')$: 상태, 행동, 보상, 다음 상태를 나타내는 ==확률변수==
- [[Bellman Optimality Equation]]이 만족되면 괄호 안이 0 → ==squared error 최소화로 $q^*$에 수렴==

### Step 1: SGD 적용

**Gradient** (SGD로 최소화):

$$\nabla_w J \approx \delta_t \nabla_w \hat{q}(s_t, a_t, w_t)$$

- $\delta_t = \hat{q}(s_t, a_t, w_t) - (r_{t+1} + \gamma \max_a \hat{q}(s_{t+1}, a, w_t))$: TD Error

→ **문제**: 파라미터 $w_t$가 ==prediction과 target 양쪽에 등장== → [[TD-Linear#Semi-gradient|Semi-gradient]]와 동일한 문제, 학습 불안정

<br/>

### Step 2: Target Network 도입

$w_t$가 target에도 등장 → ==매 업데이트마다 target이 변경== → 학습 발산 가능

**해결**: ==두 개의 분리된 네트워크== 사용

| Network | 역할 | 업데이트 |
|:---|:---|:---|
| **Main Network** ($w_t$) | prediction $\hat{q}(s_t, a_t, w_t)$ | ==매 iteration== |
| **Target Network** ($w_T$) | target $\max_{a'} \hat{q}(s_{t+1}, a', w_T)$ | ==$C$ iterations마다 $w_T \leftarrow w_t$== |

**수정된 업데이트 규칙** ($w_T$ 고정):

$$w_{t+1} = w_t - \alpha_t \delta_t \nabla_w \hat{q}(s_t, a_t, w_t)$$

- $\delta_t = \hat{q}(s_t, a_t, w_t) - (r_{t+1} + \gamma \max_a \hat{q}(s_{t+1}, a, w_T))$
- $w_T$가 ==고정==되어 있으므로 target의 gradient를 계산할 필요 없음 → Semi-gradient 문제 해결

<br/>

### Step 3: Experience Replay 도입

목적함수의 기대값이 ==$(S, A)$가 균등 분포==를 따른다고 가정하지만, 실제 샘플은 behavior policy에 따라 ==순차적으로 생성==되어 시간적 상관관계 존재

**해결**: ==Replay Buffer $\mathcal{B} = \{(s, a, r, s')\}$에 경험을 저장하고 균등 샘플링==

| 효과 | 설명 |
|:---|:---|
| **균등 분포 만족** | uniform sampling으로 목적함수의 가정 충족 |
| **상관성 제거** | 순차적 샘플의 시간적 상관관계 제거 |
| **데이터 효율** | ==같은 경험 여러 번 재사용== 가능 |

```ad-info
title: Note - Experience Replay in Tabular Q-Learning

Experience Replay는 DQN 전용 기법이 아님 — ==Tabular [[Q-Learning]]에서도 사용 가능==

- Q-Learning의 ==Off-Policy 특성==: TD target이 behavior policy와 무관
- 과거 경험 $(s, a, r, s')$을 어떤 정책으로 수집했든 학습에 사용 가능
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Deep Q-Learning (Off-Policy)

**입력**: Behavior policy $\pi_b$, 학습률 $\alpha$, target 업데이트 주기 $C$

**초기화**: Main network $w_0$, Target network $w_T \leftarrow w_0$, Replay buffer $\mathcal{B}$

**경험 수집**: $\pi_b$로부터 $(s_t, a_t, r_{t+1}, s_{t+1})$을 $\mathcal{B}$에 저장

**For** 각 iteration $t$:
- $\mathcal{B}$에서 mini-batch 샘플링
- **For** 각 샘플 $(s, a, r, s')$:
  - **TD Error 계산**: $\delta = \hat{q}(s, a, w_t) - (r + \gamma \max_{a'} \hat{q}(s', a', w_T))$
- **손실 최소화**: $L = \sum \delta^2$
- **Main network 업데이트**: $w_{t+1} = w_t - \alpha \delta \nabla_w \hat{q}$
- **매** $C$ iterations: $w_T \leftarrow w_t$

**출력**: 학습된 network $w$
```

```ad-info
title: Note - On-Policy Adaptation

위 알고리즘은 ==Off-Policy== 버전으로, behavior policy $\pi_b$와 독립적으로 학습

==On-Policy==로 변환 가능: 현재 policy로 경험 수집, experience replay 대신 on-policy 샘플 사용
```

<br/><br/>

## Deadly Triad

Off-Policy Q-Learning with Function Approximation은 ==세 가지 요소가 결합==될 때 학습이 불안정해지며, 이를 **Deadly Triad**라 함:

| 요소 | 문제 | DQN 해결책 |
|:---|:---|:---|
| **Off-Policy** | 분포 $d_b(s)$로 수집, $d_\pi(s)$에서 최적화 → ==분포 불일치== | **Experience Replay** |
| **Function Approximation** | 한 상태의 업데이트가 ==다른 상태에 영향== | (완전 해결 아님) |
| **Bootstrapping** | TD target이 ==부정확한 추정값==에 의존 → 오차 증폭 | **Target Network** |

→ DQN은 Target Network와 Experience Replay로 ==Off-Policy + FA + Bootstrapping의 불안정성==을 완화

```ad-info
title: Note - Alternative Solutions

Deadly Triad의 각 요소를 제거하는 대안:

| 해결 방법 | 제거 요소 | 대안 |
|:---|:---|:---|
| **On-Policy 사용** | Off-Policy | [[Sarsa with Function Approximation]] |
| **Tabular 사용** | FA | [[Q-Learning]] (상태 수 적을 때) |
| **MC 사용** | Bootstrapping | [[Monte Carlo Methods]] (편향 없음) |
```

<br/><br/>

## Convergence

DQN은 ==수렴이 보장되지 않음== — Deadly Triad로 인해 이론적 수렴 증명이 어려움

```ad-warning
title: Note - Loss vs Value Error

==Loss 수렴 ≠ Value error 수렴==

- Loss 수렴: network가 주어진 샘플을 fit
- Value error 수렴: optimal value를 정확히 추정

→ ==충분한 경험 데이터== 없이는 정확한 value 추정 불가
```

```ad-example
title: Example - Grid World with Deep Q-Learning
collapse: true

**설정**: 5×5 Grid World, $\gamma = 0.9$, 1 hidden layer (100 neurons)

**Case 1: 1,000 steps** (batch size 100)

![[Pasted image 20260111080336.png|700]]

- Loss → 0, ==State value error → 0== → ==Optimal policy 획득==
- Tabular Q-Learning (100,000 steps) 대비 ==100배 효율적==

**Case 2: 100 steps** (batch size 50)

![[Pasted image 20260111080349.png|700]]

- Loss → 0 (network가 샘플을 잘 fit)
- ==State value error는 수렴하지 않음== → 샘플 부족
```

<br/><br/>

## Related Concepts

- [[Q-Learning]]: Tabular Q-Learning 기본 알고리즘 — DQN의 tabular 버전
- [[TD-Linear]]: State value FA — Semi-gradient 문제와 Target Network의 이론적 배경
- [[Sarsa with Function Approximation]]: On-Policy FA — Deadly Triad 문제 없이 안정적
- [[Value Function Approximation]]: 함수 근사의 기본 개념
- [[Temporal Difference Learning]]: TD 학습 기반
- [[Bellman Optimality Equation]]: 목적함수의 이론적 기반
- [[Policy Gradient]]: 다른 Deep RL 접근법
- [[Monte Carlo Methods]]: Bootstrapping 없는 대안
