---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 정책
  - Policy Function
keywords:
  - Policy
  - Deterministic Policy
  - Stochastic Policy
  - Optimal Policy
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Policy

```ad-note
title: Summary
collapse: true

- ==에이전트가 상태에서 행동을 선택하는 규칙==: $\pi(a|s) = P(A_t = a | S_t = s)$
- ==Deterministic==: $a = \mu(s)$, ==Stochastic==: $a \sim \pi(\cdot|s)$
- ==모든 MDP에 deterministic optimal policy 존재==
- ==목표==: 누적 보상을 최대화하는 $\pi^*$ 찾기
```

## Definition

==[[Agent and Environment|에이전트]]가 각 [[State and Observation|상태]]에서 어떤 행동을 선택할지 결정하는 규칙==

$$\pi(a|s) = P(A_t = a | S_t = s)$$

- 상태 $s$에서 행동 $a$로의 ==매핑== (확률적 표현)
- 확률 조건: $\pi(a|s) \geq 0$, $\sum_{a \in \mathcal{A}} \pi(a|s) = 1$
- 에이전트의 ==행동을 완전히 결정==하는 핵심 구성요소
- 정책 $\pi$가 주어지면 [[Value Function]] $v_\pi$, $q_\pi$가 결정됨 → ==$\pi$가 다르면 가치도 다름==

<br/><br/>

## Types

### Deterministic vs Stochastic

| 유형 | 정의 | 표기 |
|:---|:---|:---|
| **Deterministic** | 각 상태에서 ==하나의 행동 확정== | $a = \mu(s)$ |
| **Stochastic** | 각 상태에서 ==확률적으로 행동 선택== | $a \sim \pi(\cdot\|s)$ |

<br/>

### Stationary vs Non-Stationary

| 유형 | 정의 | 적용 |
|:---|:---|:---|
| **Stationary** | ==시간에 무관하게 동일한 규칙== | 무한 지평 문제 |
| **Non-Stationary** | ==시간에 따라 규칙 변화== | 유한 지평 문제 |

대부분의 RL 알고리즘은 ==stationary policy== 가정

<br/><br/>

## Optimal Policy

==모든 상태에서 최대 기대 보상을 달성하는 정책==

$$\pi^* = \arg\max_\pi v_\pi(s) \quad \text{for all } s \in \mathcal{S}$$

정책 간 우열은 ==모든 상태에서의 가치 비교==로 정의:

$$\pi \geq \pi' \quad \text{iff} \quad v_\pi(s) \geq v_{\pi'}(s), \quad \forall s \in \mathcal{S}$$

→ Optimal policy $\pi^*$는 이 partial ordering에서 ==모든 정책보다 크거나 같음==

<br/>

### Properties

| Property | Description |
|:---|:---|
| **Existence** | [[Bellman Optimality Equation#Bellman Optimality Operator\|Bellman optimality operator]]의 ==[[Contraction Mapping Theorem\|contraction]] 속성==으로 $v^*$ 존재 보장 |
| **Deterministic** | ==모든 MDP에 deterministic optimal policy 존재== (stochastic optimal도 가능) |
| **Uniqueness** | ==$v^*$는 유일==하나, $\pi^*$는 ==여러 개 가능== (tie-breaking) |

<br/>

### Deriving Optimal Policy

$q^*$를 얻으면 ==[[Greedy Policy|greedy]] 추출==로 최적 정책 도출:

$$\pi^*(a|s) = \begin{cases}
1 & \text{if } a = \arg\max_a q^*(s,a) \\
0 & \text{otherwise}
\end{cases}$$

```ad-info
title: Note - From Definition to Computation

**정의에서 계산 방법 유도**:

$$\pi^* = \arg\max_\pi v_\pi(s) \xrightarrow{\max_\pi v_\pi = v^*} \arg\max_\pi v^*(s) \xrightarrow{v^* = \max_a q^*} \arg\max_a q^*(s,a)$$

- 정의와 계산은 ==논리적으로 동치==
- **실용적 차이**: 정의는 ==정책 공간 전체== 탐색, 계산은 ==$q^*$만 알면 행동 공간만== 탐색
- **Model-Free**: ==$q^*$만 있으면 환경 모델 없이== 최적 행동 선택 가능 ($v^*$는 $p(s'|s,a)$ 필요)
```

<br/>

### Algorithms for Optimal Policy

$q^*$를 구하는 ==두 가지 접근법==:

| 접근법 | 방정식 | 방식 |
|:---|:---|:---|
| **BOE 직접** | [[Bellman Optimality Equation\|BOE]] | $v^*$, $q^*$를 ==한 번에== 계산 |
| **GPI** | [[Bellman Equation\|BE]] | PE + 정책 개선으로 ==점진적== 도달 |

<br/>

**BOE 직접 방식** — [[Bellman Optimality Equation|BOE]]를 직접 풀어 $v^*$, $q^*$에 도달:

| 방법 | Model | 특징 |
|:---|:---|:---|
| **[[Value Iteration]]** | Model-Based | $v_{k+1}(s) = \max_a q_k(s,a)$ |
| **[[Q-Learning]]** | Model-Free | $q \leftarrow q + \alpha[r + \gamma \max_{a'} q(s',a') - q]$ |
| **DQN** | Model-Free | Neural Network로 $q^*$ 근사 |

<br/>

**GPI (Generalized Policy Iteration)** — [[Bellman Equation|BE]] 반복 + 정책 개선:

| 방법 | Model | 특징 |
|:---|:---|:---|
| **[[Policy Iteration]]** | Model-Based | PE로 $v_\pi$ 계산 + greedy 개선 |
| **[[Sarsa]]** | Model-Free | TD로 $q_\pi$ 추정 + $\epsilon$-greedy |
| **[[Truncated Policy Iteration]]** | Model-Based | VI와 PI의 통합 |

→ BOE 직접 방식은 ==한 번에 $v^*$==를, GPI는 ==점진적 개선==으로 최적에 도달

<br/><br/>

## Related Concepts

- [[Reinforcement Learning]]: 최적 정책 $\pi^*$를 학습하는 프레임워크
- [[Value Function]]: 정책의 가치 평가 ($v_\pi$, $q_\pi$)
- [[Bellman Equation]]: 정책 하에서 가치함수의 재귀적 관계
- [[Bellman Optimality Equation]]: 최적 정책 $\pi^*$ 도출의 이론적 기반
- [[Policy Evaluation]]: 주어진 정책의 가치 계산
- [[Policy Iteration]]: 평가 + 개선 반복으로 최적 정책 탐색
- [[Markov Decision Process]]: 정책이 정의되는 프레임워크
- [[Epsilon-Greedy Policy]]: 탐색을 위한 stochastic policy
- [[Return]]: 정책 최적화의 목표 (누적 보상)
