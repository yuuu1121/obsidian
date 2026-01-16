---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - On-Policy
  - Off-Policy
  - On-Policy Learning
  - Off-Policy Learning
keywords:
  - On-Policy
  - Off-Policy
  - Behavior Policy
  - Target Policy
  - Sample Efficiency
  - Experience Replay
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 7
author:
url:
---

# On-Policy vs Off-Policy

```ad-note
title: Summary
collapse: true

- ==On-Policy: 학습 대상 정책과 샘플 생성 정책이 동일 ($\mu = \pi$)==
- ==Off-Policy: 학습 대상 정책(target)과 샘플 생성 정책(behavior)이 상이 ($\mu \neq \pi$)==
- ==On-Policy는 안정적이나 sample efficiency 낮음, Off-Policy는 반대==
- ==TD Control: [[Sarsa]]는 On-Policy, [[Q-Learning]]은 Off-Policy==
```

## Definition

==RL 알고리즘이 경험 샘플을 생성하는 정책과 학습 대상 정책의 관계에 따른 분류==

| 정책 | 역할 | 설명 |
|:---|:---|:---|
| **Behavior Policy $\mu$** | 샘플 생성 | 환경과 상호작용하여 ==경험 샘플을 생성== |
| **Target Policy $\pi$** | 학습 대상 | 학습을 통해 ==최적화하려는== 정책 |

두 정책의 관계가 On-Policy와 Off-Policy를 결정:
- ==$\mu = \pi$==: On-Policy
- ==$\mu \neq \pi$==: Off-Policy

<br/><br/>

## On-Policy

==On-Policy 학습: 현재 학습 중인 정책 $\pi$로 직접 샘플을 수집하고, 동일한 $\pi$를 개선==

$$\mu = \pi \quad \Rightarrow \quad a_t \sim \pi(\cdot|s_t)$$

- 정책 업데이트 후 ==기존 데이터 폐기== → 새 정책으로 재수집 필요
- 데이터 분포가 ==현재 정책과 일치== → 안정적 학습
- ==Sample efficiency 낮음== (데이터 재사용 불가)

**대표 알고리즘**: [[Sarsa]], [[Monte Carlo Methods|MC Control]], [[Expected Sarsa]], [[REINFORCE]], [[Advantage Actor-Critic|A2C]], PPO

```ad-info
title: Note - GPI Perspective

On-Policy 알고리즘 ([[Sarsa]], [[Monte Carlo Methods|MC]])의 매 iteration:

- **1단계 ([[Policy Evaluation]])**: 정책 $\pi$의 [[Bellman Equation|BE]]를 풀어 $q_\pi$ 추정 → ==$\pi$가 생성한 샘플 필요== → $\pi$가 behavior policy
- **2단계 ([[Policy Iteration#Policy Improvement|Policy Improvement]])**: 추정된 $q_\pi$로 정책 개선 → $\pi$가 target policy

→ ==평가 대상 정책 = 샘플 생성 정책== → On-Policy
```

```ad-info
title: Note - Why Discard Data?

정책 $\pi_k$로 수집한 데이터는 $\pi_k$의 분포를 따름:

$$\mathbb{E}_{(s,a) \sim \pi_k}[\cdot]$$

정책이 $\pi_{k+1}$로 업데이트되면 ==분포가 변함== → 이전 데이터는 새 정책의 기대값 추정에 부적합
```

<br/><br/>

## Off-Policy

==Off-Policy 학습: Behavior policy $\mu$로 샘플을 수집하고, 별도의 target policy $\pi$를 학습==

$$\mu \neq \pi \quad \Rightarrow \quad a_t \sim \mu(\cdot|s_t), \text{ but learn } \pi$$

**대표 알고리즘**: [[Q-Learning]], DQN, DDPG, SAC, TD3

<br/>

### Advantages

**Experience Replay**: 과거 경험 $(s, a, r, s')$을 buffer에 저장하고 무작위 샘플링하여 학습
- ==데이터 효율성== 증가 (같은 경험 여러 번 학습)
- ==상관관계 감소== (연속 샘플 대신 무작위 샘플)

**Exploration/Learning 분리**: Behavior policy $\mu$를 ==강한 탐색 정책==으로 설정 가능
- 모든 state-action 쌍을 충분히 방문
- 인간 조작자나 기존 정책의 경험도 활용 가능
- Target policy $\pi$는 탐색과 무관하게 ==최적 정책으로 수렴==

<br/>

### Challenges

**Distribution Mismatch**: behavior policy $\mu$의 분포가 target policy $\pi$와 다름

$$\mathbb{E}_{(s,a) \sim \mu}[\cdot] \neq \mathbb{E}_{(s,a) \sim \pi}[\cdot]$$

| 해결 방법 | 설명 |
|:---|:---|
| [[Q-Learning]] | [[Bellman Optimality Equation\|BOE]]를 직접 풀어 ==정책 독립적==으로 학습 |
| [[Importance Sampling]] | 분포 비율 $\frac{\pi(a\|s)}{\mu(a\|s)}$로 보정 |
| Target Network | 학습 안정화 |

```ad-info
title: Note - Why BOE Enables Off-Policy

[[Q-Learning]]이 Off-Policy인 ==근본적 이유==: [[Bellman Optimality Equation|BOE]]는 특정 정책에 의존하지 않음

$$s_t \xrightarrow{\pi_b} a_t \xrightarrow{\text{model}} r_{t+1}, s_{t+1}$$

- $a_t$만 $\pi_b$가 생성, ==$(r_{t+1}, s_{t+1})$은 환경 모델이 결정== — $\pi_b$ 무관
- 따라서 어떤 $\pi_b$를 사용해도 동일한 $q^*$로 수렴
- 반면 [[Sarsa]]는 BE를 풀어 $q_\pi$를 추정하므로, ==샘플 생성 정책에 의존==
```

<br/><br/>

## Comparison

| | On-Policy | Off-Policy |
|:---|:---|:---|
| **정책 관계** | $\mu = \pi$ | $\mu \neq \pi$ |
| **데이터 재사용** | ==불가== (폐기) | ==가능== (Experience Replay) |
| **Sample Efficiency** | 낮음 | ==높음== |
| **학습 안정성** | ==높음== | 낮음 (distribution mismatch) |
| **구현 복잡도** | 낮음 | 높음 (IS, target network 등) |
| **적용 상황** | 실시간 상호작용 저렴 | 데이터 수집 비용 높음 |

<br/>

### TD Control

| 알고리즘 | 유형 | 해결 방정식 | TD Target의 $a'$ |
|:---|:---|:---|:---|
| **[[Sarsa]]** | ==On-Policy== | [[Bellman Equation]] | $a' \sim \pi$ (실제 선택) |
| **[[Q-Learning]]** | ==Off-Policy== | [[Bellman Optimality Equation]] | $\arg\max_a q(s', a)$ |

```ad-info
title: Note - How to Determine On/Off-Policy

알고리즘의 On/Off-Policy 여부를 판단하는 ==두 가지 관점==:

**1. 해결하려는 수학적 문제**
- [[Bellman Equation]] → 주어진 정책 $\pi$ 평가 → ==On-Policy==
- [[Bellman Optimality Equation]] → 정책 독립적으로 $q^*$ 추정 → ==Off-Policy==

**2. 필요한 경험 샘플**
- Sarsa: $(s_t, a_t, r_{t+1}, s_{t+1}, a_{t+1})$ — ==$a_{t+1}$도 behavior policy가 생성==
- Q-Learning: $(s_t, a_t, r_{t+1}, s_{t+1})$ — ==$a_{t+1}$ 불필요== (max 연산으로 대체)
```

<br/><br/>

## Related Concepts

- [[Online vs Offline Learning]]: 데이터 수집 방식에 따른 분류 — On/Off-Policy와 별개 개념
- [[Sarsa]]: On-Policy TD Control — BE 해결
- [[Q-Learning]]: Off-Policy TD Control — BOE 해결
- [[Expected Sarsa]]: On-Policy TD (greedy 시 Q-Learning과 동일)
- [[Monte Carlo Methods]]: On-Policy 학습 방법
- [[Temporal Difference Learning]]: TD 알고리즘의 On/Off-Policy 구분
- [[Bellman Equation]]: On-Policy 알고리즘이 해결하는 방정식
- [[Bellman Optimality Equation]]: Off-Policy (Q-Learning)가 해결하는 방정식
- [[Importance Sampling]]: Off-Policy에서 distribution mismatch 보정 — 분포 비율로 가중치 조절
- [[Policy]]: 정책의 기본 개념
- [[Rollout]]: 데이터 수집 과정
- [[Exploration vs Exploitation]]: On-Policy의 탐색 영향
