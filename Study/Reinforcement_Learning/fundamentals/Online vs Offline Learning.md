---
date: 2026-01-14
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - Online Learning
  - Offline Learning
  - Batch RL
keywords:
  - Online Learning
  - Offline Learning
  - Batch RL
  - Distribution Shift
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 7
author:
url:
---

# Online vs Offline Learning

```ad-note
title: Summary
collapse: true

- ==Online Learning: 환경과 실시간 상호작용하며 데이터 수집 및 학습==
- ==Offline Learning (Batch RL): 사전 수집된 고정 데이터셋으로 학습==
- ==On-Policy는 Online만 가능, Off-Policy는 Online/Offline 모두 가능==
- ==Offline의 핵심 문제: Distribution shift==
```

## Definition

==데이터 수집 방식에 따른 RL 알고리즘 분류== — [[On-Policy vs Off-Policy]]와 혼동하기 쉬운 별개의 개념

| 구분 | 관점 | 핵심 질문 |
|:---|:---|:---|
| **On/Off-Policy** | ==정책 간 관계== ($\mu$와 $\pi$) | "누구의 경험으로 학습?" |
| **Online/Offline** | ==데이터 소스== | "언제 데이터 수집?" |

<br/><br/>

## Online Learning

==환경과 실시간 상호작용하며 학습==

$$\text{Agent} \xleftrightarrow{\text{action, reward}} \text{Environment}$$

- 학습 중 ==직접 환경과 상호작용==하여 새 데이터 수집
- 정책 업데이트 → 새 정책으로 추가 데이터 수집 → 반복
- ==실시간 적응== 가능: 환경 변화에 즉시 대응

**장점**: 실시간 적응, 최신 정책으로 데이터 수집
**단점**: 탐색 위험, 환경 접근 필요

**대표 알고리즘**: [[Sarsa]], [[Q-Learning]], [[Monte Carlo Methods|MC]], [[Deep Q-Learning|DQN]] (online mode), PPO, [[Advantage Actor-Critic|A2C]]

<br/><br/>

## Offline Learning

==사전 수집된 고정 데이터셋으로 학습== (Batch RL)

$$\mathcal{D} = \{(s_i, a_i, r_i, s'_i)\}_{i=1}^N \quad \text{(fixed dataset)}$$

- 학습 중 ==환경 상호작용 없음== — 이미 수집된 데이터만 사용
- 데이터 수집 정책 $\mu$와 학습 대상 정책 $\pi$가 ==완전히 분리==
- ==안전성==: 위험한 탐색 없이 학습 가능 (의료, 자율주행 등)

**장점**: 안전성 (위험한 탐색 없음), 환경 접근 불필요
**단점**: Distribution shift

**대표 알고리즘**: BCQ, CQL, IQL, Decision Transformer

```ad-warning
title: Note - Distribution Shift

Offline Learning의 핵심 문제: 학습 데이터 분포와 실제 실행 분포의 불일치

- 학습 데이터에 ==없는 상태 방문 시== 성능 저하
- 데이터 수집 정책 $\mu$가 방문하지 않은 영역에서 ==외삽(extrapolation) 오류==
- 해결: Conservative Q-Learning (CQL), 행동 제약 등
```

<br/><br/>

## Relationship with On/Off-Policy

| 알고리즘 유형 | Online | Offline |
|:---|:---|:---|
| **On-Policy** ([[Sarsa]], MC) | ✅ | ❌ |
| **Off-Policy** ([[Q-Learning]]) | ✅ | ✅ |

- **On-Policy** → ==Online만 가능==
  - 정책 변경 시 이전 데이터의 분포가 새 정책과 불일치
  - 이전 데이터로는 새 정책의 기대값 추정 불가
- **Off-Policy** → ==Online/Offline 모두 가능==
  - 누가 수집한 데이터든 학습에 활용 가능
  - [[Importance Sampling]] 또는 [[Bellman Optimality Equation|BOE]] 직접 해결로 분포 차이 극복

<br/><br/>

## Related Concepts

- [[On-Policy vs Off-Policy]]: 정책 간 관계에 따른 분류 — Online/Offline과 별개 개념
- [[Q-Learning]]: Off-Policy이므로 Online/Offline 모두 가능
- [[Sarsa]]: On-Policy이므로 Online만 가능
- [[Importance Sampling]]: Off-Policy에서 분포 차이 보정
- [[Experience Replay]]: Offline 데이터 활용의 기초 — 과거 경험 재사용
