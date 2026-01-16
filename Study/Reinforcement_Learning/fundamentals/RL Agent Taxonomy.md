---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - RL 에이전트 분류
keywords:
  - RL Agent Classification
  - Value-Based
  - Policy-Based
  - Actor-Critic
  - Model-Free
  - Model-Based
  - On-Policy
  - Off-Policy
related notes:
reference:
  - David Silver's RL Course
  - Sutton and Barto (2018)
author:
url:
---

# RL Agent Taxonomy

```ad-note
title: Summary
collapse: true

- ==학습 방식과 구성요소에 따른 RL 에이전트 분류==
- ==Value/Policy/Actor-Critic==: 무엇을 학습하는가
- ==Model-Free/Model-Based==: 환경 모델을 사용하는가
- ==On/Off-Policy==: 데이터를 어떻게 사용하는가
```

## Definition

==RL 에이전트를 학습 방식과 구성요소에 따라 분류하는 체계==

→ 문제 특성에 맞는 최적의 알고리즘 선택 가이드

<br/><br/>

## Components-Based Classification

==무엇을 학습하는가==에 따른 분류

| 분류 | 학습 대상 | 정책 도출 | 적합한 환경 |
|:---|:---|:---|:---|
| **Value-Based** | $Q(s,a)$ | $\pi(s) = \arg\max_a Q(s,a)$ | ==이산 행동== |
| **Policy-Based** | $\pi_\theta$ | 직접 학습 | ==연속 행동== |
| **Actor-Critic** | $\pi_\theta$ + $V(s)$ | Actor가 직접 출력 | 범용 |

### Value-Based

$$\pi(s) = \arg\max_a Q(s,a)$$

- [[Value Function]]을 학습하여 ==암시적으로 정책 도출==
- 연속 행동 공간에서는 $\arg\max$ 계산 어려움
- 대표: Q-Learning, DQN, SARSA

<br/>

### Policy-Based

$$\theta^* = \arg\max_\theta J(\pi_\theta)$$

- [[Policy]] 파라미터를 ==직접 최적화==
- 높은 분산, 느린 수렴
- 대표: REINFORCE, Policy Gradient

<br/>

### Actor-Critic

- ==Actor==(정책) + ==Critic==(가치함수) 동시 학습
- Value-Based의 안정성 + Policy-Based의 유연성
- 대표: [[Advantage Actor-Critic|A2C]], PPO, SAC, DDPG, TD3

<br/><br/>

## Model-Based vs Model-Free

![[Pasted image 20251230163401.png]]

==[[Markov Decision Process#Model (Dynamics)|환경 모델]]을 사용하는가==에 따른 분류

| | Model-Free | Model-Based |
|:---|:---|:---|
| 환경 모델 | ==사용 안 함== | ==학습하거나 알고 있음== |
| 학습 방법 | 경험에서 직접 학습 | 모델로 시뮬레이션 |
| 샘플 효율 | 낮음 | 높음 |
| 모델 오류 | 없음 | 누적 위험 |
| 대표 | DQN, PPO, SAC | AlphaZero, MuZero, Dyna |

<br/>

### Model-Free

- 경험 샘플 $(S_t, A_t, R_{t+1}, S_{t+1})$만 사용
- 구현 간단, 모델 오차 없음
- [[Monte Carlo Methods]], [[Temporal Difference Learning]]

<br/>

### Model-Based

$$\mathcal{M}: \mathcal{S} \times \mathcal{A} \rightarrow \mathcal{S} \times \mathcal{R}$$

- 환경 동작을 예측하는 모델 학습/활용
- Planning 가능, 샘플 효율적
- 복잡한 환경에서는 모델링 자체가 어려움

<br/><br/>

## On-Policy vs Off-Policy

==데이터를 어떻게 사용하는가==에 따른 분류

| | On-Policy | Off-Policy |
|:---|:---|:---|
| 정의 | 행동 정책 = 학습 정책 | 행동 정책 ≠ 학습 정책 |
| 데이터 재사용 | ==불가== | ==가능== (Experience Replay) |
| 샘플 효율 | 낮음 | 높음 |
| 안정성 | 높음 | 분포 불일치 문제 |
| 대표 | PPO, [[Advantage Actor-Critic|A2C]], TRPO | DQN, SAC, DDPG |

<br/><br/>

## Online vs Offline RL

==언제 환경과 상호작용하는가==에 따른 분류

| | Online RL | Offline RL |
|:---|:---|:---|
| 환경 상호작용 | ==실시간== | ==없음== (사전 수집 데이터) |
| 적용 상황 | 시뮬레이션, 안전한 환경 | 위험/비용 높은 환경 |
| 한계 | 실제 환경 시행착오 비용 | 데이터 분포 불일치 |
| 대표 | 대부분의 RL 알고리즘 | CQL, AWR, BEAR |

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: RL 기본 개념
- [[Policy]]: 정책 기반 에이전트
- [[Value Function]]: 가치 기반 에이전트
- [[Markov Decision Process]]: RL 문제의 수학적 프레임워크

