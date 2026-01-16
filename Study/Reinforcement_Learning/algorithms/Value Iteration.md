---
date: 2025-01-11
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 가치 반복
  - VI
keywords:
  - Value Iteration
  - Dynamic Programming
  - Bellman Optimality
  - Iterative Algorithm
  - Policy Update
  - Value Update
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 4
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Value Iteration

```ad-note
title: Summary
collapse: true

- ==[[Bellman Optimality Equation]] 반복 적용으로 최적 value function $v^*$ 계산==
- ==매 iteration마다 **Policy Update** → **Value Update** 두 단계 수행==
- ==$v_k$는 state value가 아님== — Bellman equation을 만족하지 않는 중간값
- ==[[Contraction Mapping Theorem]]이 수렴 보장==
```

![[Pasted image 20260104214842.png|700]]

## Definition

==[[Bellman Optimality Equation|BOE]]를 풀기 위해 [[Contraction Mapping Theorem]]이 제시하는 반복 알고리즘==

==각 iteration은 두 단계로 구성==:

| 단계 | 수식 | 설명 |
|:---|:---|:---|
| **Policy Update** | $\pi_{k+1} = \arg\max_\pi (r_\pi + \gamma P_\pi v_k)$ | $v_k$ 기반 ==greedy 정책 도출== |
| **Value Update** | $v_{k+1} = r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_k$ | $\pi_{k+1}$에 대해 ==$v_{k+1}$ 계산== |

$$v_0 \xrightarrow{\text{PU}} \pi'_1 \xrightarrow{\text{VU}} v_1 \xrightarrow{\text{PU}} \pi'_2 \xrightarrow{\text{VU}} v_2 \xrightarrow{\text{PU}} \cdots \to v^*$$

→ 임의의 초기값 $v_0$에서 시작해도 최적 가치 $v^*$로 수렴

```ad-info
title: Note - VI vs PI

| | Value Iteration | [[Policy Iteration]] |
|:---|:---|:---|
| **방정식** | [[Bellman Optimality Equation]] | [[Bellman Equation]] |
| **$v_k$ 의미** | ==중간값== (BE 불만족) | ==진짜 state value== (BE 만족) |
| **수렴 보장** | [[Contraction Mapping Theorem\|축약 사상]] | [[Monotone Convergence Theorem\|단조 수렴]] |
```

```ad-info
title: Note - Model Requirement

VI는 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$를 ==필요로 함== ([[Dynamic Programming]])

→ Model-free 확장: [[Q-Learning]]
```

<br/><br/>

## Components

### Policy Update

현재 $v_k$를 기반으로 ==greedy 정책을 도출==하는 단계

**Elementwise Form**:

$$\pi_{k+1}(s) = \arg\max_{\pi} \sum_{a \in \mathcal{A}} \pi(a|s) \, q_k(s,a), \quad s \in \mathcal{S}$$

where $q_k(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_k(s')$

→ [[Greedy Policy]]가 최적:

$$\pi_{k+1}(a|s) = \begin{cases} 1, & a = \arg\max_a q_k(s,a) \\ 0, & \text{otherwise} \end{cases}$$

<br/>

### Value Update

$\pi_{k+1}$를 기반으로 ==$v_{k+1}$을 계산==하는 단계

**Elementwise Form**:

$$v_{k+1}(s) = \max_a q_k(s,a) = \max_a \left( \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_k(s') \right)$$

→ Greedy 정책 대입 시 $v_{k+1}(s) = \sum_a \pi_{k+1}(a|s) q_k(s,a) = \max_a q_k(s,a)$

```ad-warning
title: Note - $v_k$ is NOT a State Value

$v_k$는 ==Bellman equation을 만족하지 않는 중간값==:
- $v_k \neq r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_k$ (일반적으로)
- $v_k \neq r_{\pi_k} + \gamma P_{\pi_k} v_k$ (일반적으로)

$v_k$는 ==알고리즘의 중간 산출물==이며, 최종 수렴값 $v^*$만이 진정한 (최적) state value

→ 마찬가지로 $q_k$도 action value가 아닌 중간값
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Value Iteration

**입력**: 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$, 초기값 $v_0$, 수렴 threshold $\theta$

**While** $\|v_k - v_{k-1}\|_\infty > \theta$:
- **For** 모든 $s \in \mathcal{S}$:
	- **For** 모든 $a \in \mathcal{A}(s)$:
		- $q_k(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_k(s')$
	- **Policy Update (PU)**
		- $a^*_k(s) = \arg\max_a q_k(s,a)$
		- $\pi_{k+1}(a|s) = 1$ if $a = a^*_k$, else $0$
	- **Value Update (VU)**
		- $v_{k+1}(s) = \max_a q_k(s,a)$

**출력**: 최적 가치 $v^* \approx v_k$, 최적 정책 $\pi^* = \pi_k$
```

```ad-example
title: Example - 2x2 Grid World
collapse: true

![[Pasted image 20260104163936.png]]

**설정**:
- 4개 상태: $s_1, s_2, s_3, s_4$
- 금지구역 ($s_2$): $r_{\text{forbidden}} = -1$
- 목표구역 ($s_4$): $r_{\text{target}} = 1$
- 경계 충돌: $r_{\text{boundary}} = -1$
- 할인율: $\gamma = 0.9$

---

**q-table 표현식** (상태-행동별):

| | $a_1$ (←) | $a_2$ (→) | $a_3$ (↓) | $a_4$ (↑) | $a_5$ (stay) |
|:---|:---|:---|:---|:---|:---|
| $s_1$ | $-1 + \gamma v(s_1)$ | $-1 + \gamma v(s_2)$ | $0 + \gamma v(s_3)$ | $-1 + \gamma v(s_1)$ | $0 + \gamma v(s_1)$ |
| $s_2$ | $-1 + \gamma v(s_2)$ | $-1 + \gamma v(s_2)$ | $1 + \gamma v(s_4)$ | $0 + \gamma v(s_1)$ | $-1 + \gamma v(s_2)$ |
| $s_3$ | $0 + \gamma v(s_1)$ | $1 + \gamma v(s_4)$ | $-1 + \gamma v(s_3)$ | $-1 + \gamma v(s_3)$ | $0 + \gamma v(s_3)$ |
| $s_4$ | $-1 + \gamma v(s_2)$ | $-1 + \gamma v(s_4)$ | $-1 + \gamma v(s_4)$ | $0 + \gamma v(s_3)$ | $1 + \gamma v(s_4)$ |

---

**Iteration k=0**:

초기값: $v_0(s_1) = v_0(s_2) = v_0(s_3) = v_0(s_4) = 0$

q-table에 대입:

| | $a_1$ | $a_2$ | $a_3$ | $a_4$ | $a_5$ | **max** |
|:---|:---|:---|:---|:---|:---|:---|
| $s_1$ | -1 | -1 | ==0== | -1 | ==0== | **0** |
| $s_2$ | -1 | -1 | ==1== | 0 | -1 | **1** |
| $s_3$ | 0 | ==1== | -1 | -1 | 0 | **1** |
| $s_4$ | -1 | -1 | -1 | 0 | ==1== | **1** |

정책: $\pi_1 = [a_3, a_3, a_2, a_5]$ (또는 $[a_5, a_3, a_2, a_5]$)

값: $v_1 = [0, 1, 1, 1]$

→ $\pi_1$은 최적이 아님 ($s_1$에서 제자리 머무름 가능)

---

**Iteration k=1**:

$v_1 = [0, 1, 1, 1]$ 대입:

| | $a_1$ | $a_2$ | $a_3$ | $a_4$ | $a_5$ | **max** |
|:---|:---|:---|:---|:---|:---|:---|
| $s_1$ | $-1+0$ | $-1+0.9$ | ==$0+0.9$== | $-1+0$ | $0+0$ | **0.9** |
| $s_2$ | $-1+0.9$ | $-1+0.9$ | ==$1+0.9$== | $0+0$ | $-1+0.9$ | **1.9** |
| $s_3$ | $0+0$ | ==$1+0.9$== | $-1+0.9$ | $-1+0.9$ | $0+0.9$ | **1.9** |
| $s_4$ | $-1+0.9$ | $-1+0.9$ | $-1+0.9$ | $0+0.9$ | ==$1+0.9$== | **1.9** |

정책: $\pi_2 = [a_3, a_3, a_2, a_5]$

값: $v_2 = [0.9, 1.9, 1.9, 1.9]$

→ ==$\pi_2$는 이미 최적 정책!== (단 2번의 iteration으로 수렴)

---

**수렴까지**: $v_k$가 수렴할 때까지 계속 반복 ($\|v_{k+1} - v_k\| < \theta$)
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - Convergence of Value Iteration

Value Iteration이 생성하는 sequence $\{v_k\}_{k=0}^\infty$는 ==최적 state value $v^*$로 수렴==

**수렴 근거**: [[Contraction Mapping Theorem]] 적용
- **Bellman Optimality Operator**: $T(v) = \max_\pi (r_\pi + \gamma P_\pi v)$
- **Contraction**: $\|T(v_1) - T(v_2)\|_\infty \leq \gamma \|v_1 - v_2\|_\infty$
- **Fixed Point**: 유일한 $v^*$ 존재, $T(v^*) = v^*$

**수렴 속도**:

$$\|v_k - v^*\|_\infty \leq \gamma^k \|v_0 - v^*\|_\infty$$

→ 기하급수적 수렴, $\gamma$ 작을수록 빠름
```

```ad-warning
title: Note - Non-Monotonic Convergence

[[Policy Iteration]]과 달리, VI는 ==$v_{k+1} \geq v_k$ 보장 안 됨==:
- $v_k$는 [[Bellman Equation]]을 만족하지 않는 중간값
- 수렴은 보장되나, ==단조 증가는 아님==
- 초기값 $v_0$에 따라 위/아래에서 $v^*$로 접근

**비교**: PI는 $v_{\pi_{k+1}} \geq v_{\pi_k}$ 보장 (Policy Improvement Lemma)
```

<br/><br/>

## BOE Direct vs GPI

VI는 [[Bellman Optimality Equation|BOE]]를 ==직접 반복==하여 $v^*$에 도달:

| 방식 | 알고리즘 | 푸는 방정식 |
|:---|:---|:---|
| **BOE 직접 해결** | Value Iteration, [[Q-Learning]] | [[Bellman Optimality Equation\|BOE]] |
| **GPI (BE 반복 + 개선)** | [[Policy Iteration]], [[Sarsa]] | [[Bellman Equation\|BE]] |

BOE 직접 방식은 ==한 번에 최적 가치==를 찾고, GPI는 ==점진적 정책 개선==으로 최적에 도달

```ad-info
title: Note - VI is NOT GPI

[[Policy Iteration#Generalized Policy Iteration|GPI]]는 정책을 ==평가한 뒤== 개선하는 구조:
- PI: PE로 $v_{\pi_k}$ 완전 계산 → PI로 $\pi_{k+1}$ 도출

VI는 정책 평가 ==없이== 최적 가치를 바로 계산:
- VI: $v_k$는 어떤 정책의 가치도 아닌 ==중간값==
```

<br/><br/>

## Related Concepts

- [[Policy Iteration]]: Policy와 value 번갈아 개선, $v_{\pi_k}$는 진짜 state value
- [[Truncated Policy Iteration]]: VI와 PI의 통합 알고리즘
- [[Bellman Optimality Equation]]: VI가 푸는 방정식
- [[Greedy Policy]]: $v^*$에서 최적 정책 추출 — $\pi^*(s) = \arg\max_a q^*(s,a)$
- [[Value Function]]: VI가 계산하는 함수
- [[Dynamic Programming]]: VI가 속한 패러다임
- [[Q-Learning]]: VI의 model-free 버전
- [[Markov Decision Process]]: VI가 적용되는 프레임워크
- [[Contraction Mapping Theorem]]: VI 수렴의 이론적 근거

