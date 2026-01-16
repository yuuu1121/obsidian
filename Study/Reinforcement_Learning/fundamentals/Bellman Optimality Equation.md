---
date: 2025-01-11
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 벨만 최적 방정식
  - Bellman Optimality
  - BOE
keywords:
  - Bellman Optimality Equation
  - Optimal Policy
  - Optimal Value Function
  - Control Problem
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 3
  - David Silver's RL Course
author:
url:
---

# Bellman Optimality Equation

```ad-note
title: Summary
collapse: true

- ==최적 정책과 최적 가치를 분석하는 핵심 도구==
- ==비선형 방정식==이나 ==contraction property==로 해의 존재성/유일성/수렴 보장
- ==$v^*$는 유일, $\pi^*$는 여러 개 가능== (결정적 greedy 최적 정책 항상 존재)
- BOE를 푸는 반복 알고리즘이 [[Value Iteration]]
```

![[Pasted image 20251230171051.png|700]]

## Definition

<!-- Chapter 3.6-3.7 from Mathematical Foundations of RL -->

==$v^*$와 $\pi^*$를 동시에 결정하는 비선형 방정식== — 최적 정책 탐색의 핵심 도구

$$v(s) = \max_a q(s, a) = \max_a \left[ \sum_r p(r|s, a)r + \gamma \sum_{s'} p(s'|s, a)v(s') \right]$$

- $v(s)$: ==풀어야 할 미지수== (optimal state value)
- $q(s,a)$: 상태 $s$에서 행동 $a$의 action value
- $\max_a$: ==모든 행동 중 최대값== 선택 → 비선형

| 특성 | 설명 |
|:---|:---|
| **Existence** | [[Contraction Mapping Theorem]]으로 ==고정점 $v^*$ 존재 보장== |
| **Uniqueness** | ==$v^*$는 유일==, $\pi^*$는 ==여러 개 가능== |
| **Algorithm** | 비선형이라 직접 해법 없음 → ==[[#Solution\|반복 알고리즘]] 필요== |
| **Optimality** | $v^*$에서 ==greedy로 $\pi^*$ 도출==: $\pi^*(s) = \arg\max_a q^*(s,a)$ |

```ad-info
title: Note - BE vs BOE

| | [[Bellman Equation\|BE]] | BOE |
|:---|:---|:---|
| **목적** | [[Policy Evaluation]] | [[Value Iteration\|Policy Optimization]] |
| **연산** | $\sum_a \pi(a\|s)$ (==가중 평균==) | $\max_a$ (==최대값==) |
| **선형성** | 선형 방정식 | ==비선형 방정식== |
| **해법** | 직접 또는 반복 | ==반복만 가능== |

- **BE**: 정책 $\pi$가 ==주어지면== 그 가치를 평가
- **BOE**: 정책 ==없이== 최적 가치를 직접 계산

→ BOE는 ==corresponding policy가 optimal인 특수한 BE==
```

<br/><br/>

## Elementwise Form

### State Value

$$v(s) = \max_a \left[ \sum_r p(r|s, a)r + \gamma \sum_{s'} p(s'|s, a)v(s') \right]$$

<br/>

### Action Value

$$q(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) \max_{a'} q(s', a')$$

- $\max_{a'}$: 다음 상태에서 ==최적 행동 선택 가정==
- [[Q-Learning]]이 이 형태를 직접 해결

```ad-info
title: Note - State Value와 Action Value의 관계

$$v(s) = \max_a q(s,a), \quad q(s,a) = r(s,a) + \gamma \sum_{s'} p(s'|s,a) v(s')$$

→ ==상호 변환 가능== — 둘 중 하나만 알면 다른 하나 계산 가능
```

```ad-info
title: Note - Why Action Value is More Useful

| | $v^*$에서 정책 도출 | $q^*$에서 정책 도출 |
|:---|:---|:---|
| **수식** | $\pi^*(s) = \arg\max_a [\sum_r p(r\|s,a)r + \gamma \sum_{s'} p(s'\|s,a) v^*(s')]$ | $\pi^*(s) = \arg\max_a q^*(s,a)$ |
| **Model** | ==$p(r\|s,a)$, $p(s'\|s,a)$ 필요== | ==불필요== |

- $v^*$만 알면 최적 행동 선택에 ==환경 모델 필요== (Model-Based)
- $q^*$를 알면 ==단순 argmax만== 필요 (Model-Free)
	- [[Q-Learning]] 등 Model-Free 알고리즘은 $q$를 직접 학습
```

<br/>

## Matrix-Vector Form

모든 상태에 대한 방정식을 ==벡터 형태로 통합==:

$$v = \max_{\pi \in \Pi} (r_\pi + \gamma P_\pi v)$$

- $v \in \mathbb{R}^{|\mathcal{S}|}$: 모든 상태의 가치 벡터
- $\max_\pi$: ==elementwise==로 수행 (각 상태별 최대값)

$r_\pi$와 $P_\pi$의 정의는 [[Bellman Equation#Matrix-Vector Form|BE와 동일]]

<br/><br/>

## Contraction Property

### Bellman Optimality Operator

$\pi$에 대한 optimal value가 $v$에 의해 결정되므로, ==BOE 우변은 $v$만의 함수==:

$$T(v) \doteq \max_{\pi \in \Pi} (r_\pi + \gamma P_\pi v)$$

- BOE는 ==$v = T(v)$ 형태의 고정점 방정식==
- [[Value Iteration]]은 $v_{k+1} = T(v_k)$ 반복으로 고정점 탐색

<br/>

### Contraction Mapping

Bellman Optimality Operator $T(v)$는 ==[[Contraction Mapping Theorem|contraction mapping]]==

임의의 $v_1, v_2 \in \mathbb{R}^{|\mathcal{S}|}$에 대해:

$$\|T(v_1) - T(v_2)\|_\infty \leq \gamma \|v_1 - v_2\|_\infty$$

- $\gamma \in (0, 1)$: discount factor
- $\|\cdot\|_\infty$: ==maximum norm== (벡터 원소의 최대 절댓값)

```ad-info
title: Note - Why Contraction Property Matters

[[Contraction Mapping Theorem]]을 적용하여 BOE 분석 가능:
- **Existence**: $v^* = T(v^*)$를 만족하는 ==고정점 $v^*$ 존재==
- **Uniqueness**: 고정점은 ==유일==
- **Convergence**: $v_{k+1} = T(v_k)$ 반복 시 ==임의의 초기값에서 $v^*$로 수렴==

---

**Fixed Point와 Optimal Value의 관계**

$T(v)$는 "==한 스텝 최적 행동 + 이후 $v$를 따름=="의 가치

| 경우 | 상황 | 결과 |
|:---|:---|:---|
| $v < v^*$ (과소평가) | 실제로 더 좋은 return 가능 | $T(v) > v$ → 고정점 아님 |
| $v > v^*$ (과대평가) | 어떤 정책으로도 달성 불가 | $T(v) < v$ → 고정점 아님 |
| $v = v^*$ (정확) | 최적 행동해도 가치 유지 | ==$T(v) = v$ → 고정점!== |

→ $v = T(v)$는 =="더 이상 개선할 수 없는 상태"==를 의미
```

```ad-important
title: Proof - Contraction Property
collapse: true

**설정**: 임의의 $v_1, v_2 \in \mathbb{R}^{|\mathcal{S}|}$와 각각의 최적 정책 정의:
$$\pi_1^* \doteq \arg\max_\pi (r_\pi + \gamma P_\pi v_1), \quad \pi_2^* \doteq \arg\max_\pi (r_\pi + \gamma P_\pi v_2)$$

---

**Step 1: $T(v)$ 정의와 부등식 유도**

$T(v_1) = \max_\pi (r_\pi + \gamma P_\pi v_1) = r_{\pi_1^*} + \gamma P_{\pi_1^*} v_1$

$\pi_1^*$가 $v_1$에 대한 최적이므로, 다른 정책 $\pi_2^*$를 사용하면:
$$T(v_1) \geq r_{\pi_2^*} + \gamma P_{\pi_2^*} v_1$$

마찬가지로:
$$T(v_2) \geq r_{\pi_1^*} + \gamma P_{\pi_1^*} v_2$$

---

**Step 2: $T(v_1) - T(v_2)$의 상한/하한**

$$T(v_1) - T(v_2) = r_{\pi_1^*} + \gamma P_{\pi_1^*} v_1 - (r_{\pi_2^*} + \gamma P_{\pi_2^*} v_2)$$

$T(v_2) \geq r_{\pi_1^*} + \gamma P_{\pi_1^*} v_2$를 이용하면:
$$T(v_1) - T(v_2) \leq r_{\pi_1^*} + \gamma P_{\pi_1^*} v_1 - (r_{\pi_1^*} + \gamma P_{\pi_1^*} v_2) = \gamma P_{\pi_1^*}(v_1 - v_2)$$

마찬가지로: $T(v_2) - T(v_1) \leq \gamma P_{\pi_2^*}(v_2 - v_1)$

따라서:
$$\gamma P_{\pi_2^*}(v_1 - v_2) \leq T(v_1) - T(v_2) \leq \gamma P_{\pi_1^*}(v_1 - v_2)$$

---

**Step 3: 상한 벡터 $z$ 정의**

$$z \doteq \max\{|\gamma P_{\pi_2^*}(v_1 - v_2)|, |\gamma P_{\pi_1^*}(v_1 - v_2)|\} \in \mathbb{R}^{|\mathcal{S}|}$$

(모든 연산은 elementwise)

Step 2의 부등식에서: $|T(v_1) - T(v_2)| \leq z$

---

**Step 4: $\|z\|_\infty$ 상한 유도**

$z_i$를 $z$의 $i$번째 원소, $p_i^T$와 $q_i^T$를 $P_{\pi_1^*}$와 $P_{\pi_2^*}$의 $i$번째 행이라 하면:
$$z_i = \max\{\gamma|p_i^T(v_1 - v_2)|, \gamma|q_i^T(v_1 - v_2)|\}$$

$p_i$는 ==확률 벡터== (모든 원소 $\geq 0$, 합 = 1)이므로:
$$|p_i^T(v_1 - v_2)| \leq p_i^T|v_1 - v_2| \leq \|v_1 - v_2\|_\infty$$

마찬가지로 $|q_i^T(v_1 - v_2)| \leq \|v_1 - v_2\|_\infty$

따라서: $z_i \leq \gamma\|v_1 - v_2\|_\infty$

---

**결론**:
$$\|T(v_1) - T(v_2)\|_\infty \leq \|z\|_\infty = \max_i|z_i| \leq \gamma\|v_1 - v_2\|_\infty$$

$\gamma < 1$이므로 $T(v)$는 contraction mapping $\square$
```

<br/><br/>

## Solving Methods

<!-- Chapter 3.7 from Mathematical Foundations of RL -->

BOE를 풀면 ==최적 정책 $\pi^*$와 최적 가치 $v^*$ 획득== (Control Problem 해결)

<br/>

### Iterative Solution

BOE는 ==$\max$ 연산으로 인해 비선형== → ==Closed-form solution 없음==, 반복 알고리즘만 가능

$$v_{k+1} = \max_\pi (r_\pi + \gamma P_\pi v_k), \quad k = 0, 1, 2, \ldots$$

- **초기화**: $v_0$ 임의 설정
- **종료 조건**: $\|v_{k+1} - v_k\|_\infty < \theta$
- **수렴성**: [[Contraction Mapping Theorem]]에 의해 ==임의의 초기값에서 $v^*$로 수렴==

| 해의 항목 | 특성 | 설명 |
|:---|:---|:---|
| **$v^*$** | ==유일== | [[Contraction Mapping Theorem]]에 의해 고정점 유일 |
| **$\pi^*$** | 비유일 | 동일한 $q^*$를 주는 여러 action 존재 가능 |

**해결 절차**:
- **Step 1**: BOE 반복 적용으로 $v^*$ (또는 $q^*$) 계산
- **Step 2**: $v^*$에서 [[Greedy Policy|greedy 정책]] 추출 → $\pi^*(s) = \arg\max_a q^*(s,a)$

```ad-info
title: Note - BOE와 BE의 관계

$v^*$를 구한 후 greedy 정책 $\pi^*$를 추출하면:

$$v^* = r_{\pi^*} + \gamma P_{\pi^*} v^*$$

→ $v^* = v_{\pi^*}$, 즉 ==BOE는 $\pi^*$에 대응하는 특수한 [[Bellman Equation]]==
```

<br/>

### Solution Approaches

BOE를 직접 풀어 $v^*$, $q^*$에 ==한 번에 도달==하는 알고리즘들:

| 방법 | Model | 특징 |
|:---|:---|:---|
| **[[Value Iteration]]** | Model-Based | $v_{k+1}(s) = \max_a q_k(s,a)$ |
| **[[Q-Learning]]** | Model-Free | $q \leftarrow q + \alpha[r + \gamma \max_{a'} q(s',a') - q]$ |
| **DQN** | Model-Free | Neural Network로 $q^*$ 근사 |

```ad-info
title: Note - Alternative Approach

[[Policy#Optimal Policy|최적 정책]]에 도달하는 다른 방식으로 ==GPI (Generalized Policy Iteration)==가 있음:
- [[Bellman Equation|BE]]를 반복적으로 풀면서 정책을 점진적으로 개선
- [[Policy Iteration]], [[Sarsa]] 등이 이 방식을 사용
```

<br/><br/>

## Related Concepts

- [[Bellman Equation]]: BOE의 기반 — $\pi^*$에 대응하는 특수한 BE ($v^* = r_{\pi^*} + \gamma P_{\pi^*} v^*$)
- [[Value Function#Optimal Value Functions|Optimal Value Function]]: BOE의 해 $v^*, q^*$ — 유일하게 존재
- [[Policy#Optimal Policy|Optimal Policy]]: BOE에서 greedy 추출로 도출 — $\pi^*(s) = \arg\max_a q^*(s,a)$
- [[Greedy Policy]]: $v^*$에서 최적 정책 추출 — $\pi^*(a|s) = 1$ if $a = \arg\max_a q^*(s,a)$
- [[Value Iteration]]: BOE를 반복 적용하는 알고리즘 — $v_{k+1} = T(v_k)$
- [[Policy Iteration]]: BE로 PE + greedy PI 반복 — GPI 방식
- [[Truncated Policy Iteration]]: VI와 PI의 통합 — PE 반복 횟수를 유한하게 제한
- [[Q-Learning]]: BOE를 model-free로 해결 — $q(s,a) \leftarrow q + \alpha[r + \gamma \max_{a'} q(s',a') - q]$
- [[Contraction Mapping Theorem]]: BOE 해의 존재성/유일성/수렴 보장 — $\|T(v_1) - T(v_2)\|_\infty \leq \gamma\|v_1 - v_2\|_\infty$
- [[Return]]: Discount factor $\gamma$의 역할 — Contraction 계수로 수렴 속도 결정
