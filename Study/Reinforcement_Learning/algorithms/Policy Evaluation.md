---
date: 2025-01-11
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 정책 평가
  - Prediction
keywords:
  - Policy Evaluation
  - Bellman Expectation
  - Iterative Algorithm
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 4
author:
url:
---

# Policy Evaluation

```ad-note
title: Summary
collapse: true

- ==고정된 정책 $\pi$의 value function $v_\pi$를 계산하는 과정 (Prediction)==
- ==Bellman Expectation Equation을 반복 적용하여 $v_\pi$로 수렴==
- ==Policy Iteration의 핵심 구성 요소==
```

## Definition

<!-- Chapter 4 from Mathematical Foundations of RL -->

==[[Bellman Equation]]을 풀어 주어진 정책 $\pi$의 [[Value Function|가치]] $v_\pi$를 계산하는 과정== (Prediction Problem)

| 항목 | 설명 |
|:---|:---|
| **입력** | 정책 $\pi$, 환경 모델 $p(r\|s,a)$, $p(s'\|s,a)$ |
| **출력** | State value function $v_\pi$ |
| **목적** | ==정책의 성능을 수치화== |

$$v_\pi(s) = \sum_{a \in \mathcal{A}} \pi(a|s) \left( \sum_{r \in \mathcal{R}} p(r|s,a) r + \gamma \sum_{s' \in \mathcal{S}} p(s'|s,a) v_\pi(s') \right)$$

```ad-info
title: Note - Model Requirement

Policy Evaluation은 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$를 ==필요로 함== ([[Dynamic Programming]])

→ Model-free 확장: [[Monte Carlo Methods]] (episode return 평균), [[Temporal Difference Learning]] (bootstrap)
```

```ad-info
title: Note - BE vs BOE

| | Policy Evaluation | [[Value Iteration]] |
|:---|:---|:---|
| **방정식** | [[Bellman Equation]] | [[Bellman Optimality Equation]] |
| **연산** | $\sum_a \pi(a\|s)$ (==가중 평균==) | $\max_a$ (==최대값==) |
| **계산 대상** | $v_\pi$ (고정된 정책의 가치) | $v^*$ (최적 가치) |
| **선형성** | 선형 방정식 | 비선형 방정식 |

- **PE**: 정책 $\pi$가 ==주어지면== 그 가치를 평가
- **VI**: 정책 ==없이== 최적 가치를 직접 계산
```

<br/><br/>

## Algorithm

==임의의 초기값 $v^{(0)}_\pi$에서 시작해 Bellman Equation을 반복 적용==하여 $v_\pi$로 수렴:

$$v^{(j+1)}_{\pi} = r_{\pi} + \gamma P_{\pi} v^{(j)}_{\pi}, \quad j = 0, 1, 2, \ldots$$

```ad-tldr
title: Algorithm - Iterative Policy Evaluation

**입력**: 정책 $\pi$, 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$

**초기화**: $v^{(0)}(s)$ = 임의의 값 for all $s \in \mathcal{S}$

**While** 종료 조건 미충족:
- **For** 모든 $s \in \mathcal{S}$:
  - $v^{(j+1)}(s) = \sum_a \pi(a|s) \left[ \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v^{(j)}(s') \right]$

**종료 조건** (택 1):
- $\|v^{(j+1)} - v^{(j)}\| < \theta$ (threshold)
- $j > j_{\max}$ (최대 반복 횟수)

**출력**: $v_\pi \approx v^{(j)}$
```

```ad-info
title: Note - Closed-form Solution

Bellman Equation은 [[Bellman Equation#Closed-form Solution|closed-form]]으로도 해결 가능:

$$v_\pi = (I - \gamma P_\pi)^{-1} r_\pi$$

- 이론적 분석에 유용하나 ==행렬 역연산 $O(n^3)$== 필요로 실용적이지 않음
- 실제로는 항상 ==Iterative Algorithm 사용==
```

```ad-info
title: Note - Effect of Finite Iterations

이론적으로 무한 반복이 필요하나 실제로는 유한 반복으로 종료:
- ==부정확한 $v_\pi$ 추정치를 사용해도 문제 없음==
- [[Truncated Policy Iteration]]이 유한 반복에서도 수렴하는 이유를 증명
```

```ad-example
title: Example - 2-State MDP
collapse: true

![[Pasted image 20260109092141.png]]

**설정**:
- 상태: $s_1$, $s_2$ (목표)
- 행동: $\mathcal{A} = \{a_\ell, a_0, a_r\}$ (왼쪽, 제자리, 오른쪽)
- 보상: $r_{\text{boundary}} = -1$, $r_{\text{target}} = 1$
- 할인율: $\gamma = 0.9$
- ==평가할 정책 $\pi_0$: $s_1$에서 왼쪽, $s_2$에서 왼쪽 (나쁜 정책)==

---

**1. Bellman Equation 설정**

정책 $\pi_0$ 하에서:
- $s_1$에서 왼쪽 → 경계 충돌 → 보상 $-1$, 다시 $s_1$
- $s_2$에서 왼쪽 → $s_1$로 이동 → 보상 $0$

$$v_{\pi_0}(s_1) = -1 + \gamma \cdot v_{\pi_0}(s_1)$$
$$v_{\pi_0}(s_2) = 0 + \gamma \cdot v_{\pi_0}(s_1)$$

---

**2. Closed-form Solution**

첫 번째 식에서:
$$v_{\pi_0}(s_1) = \frac{-1}{1 - \gamma} = \frac{-1}{0.1} = -10$$

두 번째 식에 대입:
$$v_{\pi_0}(s_2) = 0.9 \times (-10) = -9$$

→ ==나쁜 정책이므로 음수 value==

---

**3. Iterative Solution**

초기값 $v^{(0)}(s_1) = v^{(0)}(s_2) = 0$에서 시작:

| $j$ | $v^{(j)}(s_1)$ | $v^{(j)}(s_2)$ | 계산 과정 |
|:---|:---|:---|:---|
| 0 | 0 | 0 | 초기값 |
| 1 | -1 | 0 | $-1 + 0.9(0) = -1$ |
| 2 | -1.9 | -0.9 | $-1 + 0.9(-1) = -1.9$ |
| 3 | -2.71 | -1.71 | $-1 + 0.9(-1.9) = -2.71$ |
| $\vdots$ | $\vdots$ | $\vdots$ | |
| $\infty$ | ==-10== | ==-9== | 수렴 |

→ $j \to \infty$일 때 closed-form solution과 일치
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - Convergence of Iterative Policy Evaluation

Iterative Policy Evaluation $v_{k+1} = r_\pi + \gamma P_\pi v_k$는 ==$\gamma < 1$일 때 임의의 초기값 $v_0$에서 $v_\pi$로 수렴==
```

```ad-important
title: Proof - Convergence
collapse: true

**목표**: $v_k \to v_\pi$ as $k \to \infty$

**오차 정의**: $\delta_k \doteq v_k - v_\pi$

$\delta_k \to 0$임을 보이면 됨.

---

**Step 1**: $v_{k+1} = r_\pi + \gamma P_\pi v_k$에 $v_{k+1} = \delta_{k+1} + v_\pi$, $v_k = \delta_k + v_\pi$ 대입:

$$\delta_{k+1} + v_\pi = r_\pi + \gamma P_\pi (\delta_k + v_\pi)$$

---

**Step 2**: 정리:

$$\begin{aligned}
\delta_{k+1} &= -v_\pi + r_\pi + \gamma P_\pi \delta_k + \gamma P_\pi v_\pi \\
&= \gamma P_\pi \delta_k - v_\pi + (r_\pi + \gamma P_\pi v_\pi) \\
&= \gamma P_\pi \delta_k
\end{aligned}$$

마지막 등호: $v_\pi = r_\pi + \gamma P_\pi v_\pi$ ([[Bellman Equation]])

---

**Step 3**: 재귀적 적용:

$$\delta_{k+1} = \gamma P_\pi \delta_k = \gamma^2 P_\pi^2 \delta_{k-1} = \cdots = \gamma^{k+1} P_\pi^{k+1} \delta_0$$

---

**Step 4**: 수렴 분석

- $P_\pi$의 모든 원소는 비음수이고 1 이하 → $0 \leq P_\pi^k \leq 1$ (모든 $k$)
- $\gamma < 1$이므로 $\gamma^k \to 0$ as $k \to \infty$

**결론**: $\delta_{k+1} = \gamma^{k+1} P_\pi^{k+1} \delta_0 \to 0$ as $k \to \infty$ $\square$
```

<br/><br/>

## Related Concepts

- [[Policy Iteration]]: PE + PI 반복으로 최적 정책 탐색 — PE는 PI의 핵심 구성요소
- [[Truncated Policy Iteration]]: PE 반복 횟수 제한 — 유한 반복에서도 수렴 보장
- [[Policy Iteration#Policy Improvement|Policy Improvement]]: PE로 계산한 $v_{\pi_k}$를 사용해 greedy 정책 도출
- [[Bellman Equation]]: PE가 푸는 방정식 — $v_\pi = r_\pi + \gamma P_\pi v_\pi$
- [[Value Function]]: PE의 계산 대상 — $v_\pi(s)$
- [[Value Iteration]]: PE 없이 BOE를 직접 해결 — $v_k$는 state value 아님
- [[Monte Carlo Methods]]: Model-free PE — Episode return 평균
- [[Temporal Difference Learning]]: Model-free PE — Bootstrap 기반

