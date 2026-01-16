---
date: 2025-12-17
tags:
  - Concepts/ReinforcementLearning/MarkovTheory
aliases:
  - 제어 동적 시스템
  - Controlled Dynamic Systems
  - System Equation Approach
keywords:
  - Controlled Dynamic System
  - System Equation
  - Random Disturbance
  - State Update Function
related notes:
reference:
  title: "Lecture 7-8 - Finite-Horizon MDP"
  source: "IMEN 764: Dynamic Programming & Reinforcement Learning Applications"
author: Dong Gu Choi
url:
---

# Controlled Dynamic System

```ad-note
title: Summary
collapse: true

- ==MDP를 전이 확률 대신 시스템 방정식 $s_{t+1} = f_t(s_t, a_t, w_t)$으로 정의하는 접근법==
- ==시스템 진화는 제어(행동)와 무작위 교란(random disturbance) 두 요인에 의해 결정==
- ==전이 확률은 교란 변수 $w_t$의 분포로부터 유도==
```

## Definition

==MDP를 전이 확률 대신 시스템 방정식으로 정의하는 접근법==

$$s_{t+1} = f_t(s_t, a_t, w_t)$$

| 기호 | 의미 |
|:---|:---|
| $s_t \in \mathcal{S}$ | 시점 $t$의 상태 |
| $a_t \in \mathcal{A}_{s_t}$ | 시점 $t$의 **제어 (Control)** = 행동 |
| $w_t \in W$ | 시점 $t$의 **무작위 교란 (Random Disturbance)** |
| $f_t: \mathcal{S} \times \mathcal{A} \times W \to \mathcal{S}$ | 상태 업데이트 함수 |

<br/><br/>

## Two Factors of System Evolution

시스템 $s_0, s_1, s_2, \ldots$는 ==결정론적 동역학이 두 가지 요인에 의해 섭동(perturb)==:

| 요인 | 결정 주체 |
|:---|:---|
| **제어 $a_t$** | 의사결정자 |
| **교란 $w_t$** | 자연/환경 (통제 불가) |

<br/><br/>

## Assumptions

| 가정 | 설명 |
|:---|:---|
| **공간** | $\mathcal{S} \subseteq \mathbb{R}^k$, $\mathcal{A} \subseteq \mathbb{R}^m$, $W \subseteq \mathbb{R}^l$ |
| **함수** | $f_t$는 상태-행동-교란을 다음 상태로 매핑 |
| **독립성** | $w_t$는 $w_\tau$ ($\tau < t$)와 독립 |
| **분포** | $q_t(\cdot)$는 $W_t$의 분포, 상태/행동에 무관 |

<br/><br/>

## Transition Probability Derivation

==전이 확률은 시스템 방정식과 교란 분포로부터 유도==:

$$p_t(s'|s, a) = \sum_{w \in W: f_t(s,a,w) = s'} q_t(w)$$

<br/><br/>

## MDP vs Dynamic Systems Approach

| 관점 | MDP (전이 확률) | Dynamic Systems (시스템 방정식) |
|:---|:---|:---|
| **정의** | $p(s'\|s, a)$ 직접 정의 | $s_{t+1} = f(s_t, a_t, w_t)$ |
| **무작위성** | 전이 확률에 포함 | 교란 분포 $q_t(\cdot)$에서 유도 |
| **적합 상황** | 확률 직접 추정 가능 | 동역학이 알려진 공학/물리 시스템 |

==두 접근법은 표현 방식만 다를 뿐 본질적으로 동일==

<br/><br/>

## When to Use

| 상황 | 권장 접근법 |
|:---|:---|
| 이산 상태, 확률 직접 추정 가능 | MDP (전이 확률) |
| 물리 법칙이 알려진 시스템 | Dynamic Systems |
| 연속 상태 공간 | Dynamic Systems |
| 교란의 물리적 의미가 명확 | Dynamic Systems |

<br/><br/>

## Related Concepts

- [[Markov Decision Process]]: MDP의 기본 정의
- [[Transition Probability]]: 전이 확률 정의

