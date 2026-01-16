---
date: 2026-01-04
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 정책 반복
  - PI
keywords:
  - Policy Iteration
  - Dynamic Programming
  - Policy Evaluation
  - Policy Improvement
  - Greedy Policy
  - Embedded Iteration
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

# Policy Iteration

```ad-note
title: Summary
collapse: true

- ==[[Policy Evaluation]] + Policy Improvement 반복으로 최적 정책 $\pi^*$ 탐색==
- ==$v_{\pi_k}$는 진짜 state value== — [[Bellman Equation]] 만족 ([[Value Iteration|VI]]의 $v_k$와 대비)
- ==Policy Improvement Lemma: greedy 정책은 항상 원래 정책보다 좋거나 같음==
- ==Monotone Convergence Theorem으로 수렴 보장==
```

![[Pasted image 20260104214853.png|700]]

## Definition

==[[Bellman Equation]]을 반복적으로 풀면서 정책을 점진적으로 개선하는 [[Dynamic Programming|DP]] 알고리즘==

==각 iteration은 두 단계로 구성==:

| 단계 | 수식 | 설명 |
|:---|:---|:---|
| **Policy Evaluation** | $v_{\pi_k} = r_{\pi_k} + \gamma P_{\pi_k} v_{\pi_k}$ | 현재 정책 $\pi_k$의 ==가치 계산== |
| **Policy Improvement** | $\pi_{k+1} = \arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_k})$ | $v_{\pi_k}$ 기반 ==greedy 정책 도출== |

$$\pi_0 \xrightarrow{\text{PE}} v_{\pi_0} \xrightarrow{\text{PI}} \pi_1 \xrightarrow{\text{PE}} v_{\pi_1} \xrightarrow{\text{PI}} \pi_2 \xrightarrow{\text{PE}} \cdots \to \pi^*$$

→ 임의의 초기 정책 $\pi_0$에서 시작해도 최적 정책 $\pi^*$로 수렴

```ad-info
title: Note - PI vs VI

| | Policy Iteration | [[Value Iteration]] |
|:---|:---|:---|
| **방정식** | [[Bellman Equation]] | [[Bellman Optimality Equation]] |
| **$v_k$ 의미** | ==진짜 state value== (BE 만족) | 중간값 (BE 불만족) |
| **수렴 보장** | [[Monotone Convergence Theorem\|단조 수렴]] | [[Contraction Mapping Theorem\|축약 사상]] |
```

<br/><br/>

## Components

### Policy Evaluation

현재 정책 $\pi_k$의 ==가치를 계산==하는 단계

**Elementwise Form**:

$$v_{\pi_k}(s) = \sum_{a \in \mathcal{A}} \pi_k(a|s) \left( \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_{\pi_k}(s') \right), \quad s \in \mathcal{S}$$

[[Bellman Equation]]을 만족하는 고정점 방정식이므로 ==반복 알고리즘==으로 해결:

$$v^{(j+1)}_{\pi_k} = r_{\pi_k} + \gamma P_{\pi_k} v^{(j)}_{\pi_k}, \quad j = 0, 1, 2, \ldots$$

```ad-warning
title: Note - Nested Loop Structure

| 루프 | 인덱스 | 역할 |
|:---|:---|:---|
| **외부** | $k$ | PE → PI 반복 |
| **내부** | $j$ | $v^{(j)}_{\pi_k}$ 수렴까지 반복 |

이론적으로 $j \to \infty$가 필요하나, 실제로는 ==유한 반복으로 충분== ([[Truncated Policy Iteration]])
```

<br/>

### Policy Improvement

$v_{\pi_k}$를 바탕으로 ==더 나은 정책을 도출==하는 단계

**Elementwise Form**:

$$\pi_{k+1}(s) = \arg\max_{\pi} \sum_{a \in \mathcal{A}} \pi(a|s) \, q_{\pi_k}(s,a), \quad s \in \mathcal{S}$$

where $q_{\pi_k}(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_{\pi_k}(s')$

→ [[Greedy Policy]]가 최적:

$$\pi_{k+1}(a|s) = \begin{cases} 1, & a = \arg\max_a q_{\pi_k}(s,a) \\ 0, & \text{otherwise} \end{cases}$$

```ad-important
title: Lemma - Policy Improvement

$\pi_{k+1} = \arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_k})$이면:

$$v_{\pi_{k+1}} \geq v_{\pi_k}$$

→ ==Greedy 개선은 항상 정책을 개선하거나 유지== (악화 없음)
```

```ad-important
title: Proof - Policy Improvement Lemma
collapse: true

**Step 1**: $v_{\pi_{k+1}}$와 $v_{\pi_k}$는 각각의 [[Bellman Equation]] 만족:

$$v_{\pi_{k+1}} = r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_{k+1}}$$
$$v_{\pi_k} = r_{\pi_k} + \gamma P_{\pi_k} v_{\pi_k}$$

---

**Step 2**: $\pi_{k+1} = \arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_k})$이므로:

$$r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_k} \geq r_{\pi_k} + \gamma P_{\pi_k} v_{\pi_k}$$

---

**Step 3**: 차이 계산:

$$\begin{aligned}
v_{\pi_k} - v_{\pi_{k+1}} &= (r_{\pi_k} + \gamma P_{\pi_k} v_{\pi_k}) - (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_{k+1}}) \\
&\leq (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_k}) - (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_{k+1}}) \\
&= \gamma P_{\pi_{k+1}} (v_{\pi_k} - v_{\pi_{k+1}})
\end{aligned}$$

---

**Step 4**: 재귀적 적용:

$$v_{\pi_k} - v_{\pi_{k+1}} \leq \gamma^n P^n_{\pi_{k+1}} (v_{\pi_k} - v_{\pi_{k+1}})$$

$n \to \infty$일 때 $\gamma^n \to 0$이므로:

$$v_{\pi_k} - v_{\pi_{k+1}} \leq 0 \implies v_{\pi_{k+1}} \geq v_{\pi_k} \quad \square$$
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Policy Iteration

**입력**: 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$, 초기 정책 $\pi_0$

**While** $v_{\pi_k}$가 수렴하지 않음:

**1. Policy Evaluation**:
   - 초기화: $v^{(0)}_{\pi_k}$ 임의 설정
   - **While** $v^{(j)}_{\pi_k}$가 수렴하지 않음:
     - **For** 모든 $s \in \mathcal{S}$:
       - $v^{(j+1)}_{\pi_k}(s) = \sum_a \pi_k(a|s) \left[ \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v^{(j)}_{\pi_k}(s') \right]$

**2. Policy Improvement**:
   - **For** 모든 $s \in \mathcal{S}$:
     - **For** 모든 $a \in \mathcal{A}$:
       - $q_{\pi_k}(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_{\pi_k}(s')$
     - $a^*_k(s) = \arg\max_a q_{\pi_k}(s,a)$
     - $\pi_{k+1}(a|s) = 1$ if $a = a^*_k$, else $0$

**출력**: 최적 가치 $v^*$, 최적 정책 $\pi^*$
```

```ad-example
title: Example - 5x5 Grid World
collapse: true

![[Pasted image 20260104182920.png]]

**설정**:
- 5x5 grid world, 금지구역/목표구역 존재
- $r_{\text{boundary}} = -1$, $r_{\text{forbidden}} = -10$, $r_{\text{target}} = 1$
- $\gamma = 0.9$
- 랜덤 초기 정책 $\pi_0$에서 시작 → 최적 정책으로 수렴

---

**관찰 1: 정책의 공간적 전파**

==목표에 가까운 상태가 먼저 최적 정책을 찾음==:
- 가까운 상태가 먼저 목표로 가는 경로 발견
- 그 후 먼 상태들이 가까운 상태를 경유하는 경로 발견

---

**관찰 2: State Value의 공간적 분포**

==목표에 가까울수록 state value가 높음==:
- 먼 상태에서 시작 → 양의 보상을 받기까지 많은 step 필요
- 많은 step → 심한 할인 적용 → 상대적으로 낮은 value
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - Convergence of Policy Iteration

Policy Iteration이 생성하는 state value sequence $\{v_{\pi_k}\}_{k=0}^\infty$는 ==최적 state value $v^*$로 수렴==

결과적으로 policy sequence $\{\pi_k\}_{k=0}^\infty$도 ==최적 정책 $\pi^*$로 수렴==

**수렴 근거**: [[Monotone Convergence Theorem]] 적용
- ==Nondecreasing==: Policy Improvement Lemma에 의해 $v_{\pi_{k+1}} \geq v_{\pi_k}$
- ==Upper bound==: optimal value 정의에 의해 $v_{\pi_k}(s) \leq v^*(s)$ for all $s$, $k$
```

```ad-important
title: Proof - Convergence of Policy Iteration
collapse: true

**전략**: PI가 VI보다 빠르게 수렴함을 보임

$v_k \leq v_{\pi_k} \leq v^*$ for all $k$를 증명하면, VI가 $v^*$로 수렴하므로 PI도 수렴

---

**Step 1**: Value Iteration sequence 정의

$$v_{k+1} = T(v_k) = \max_\pi (r_\pi + \gamma P_\pi v_k)$$

[[Contraction Mapping Theorem]]에 의해 $v_k \to v^*$

---

**Step 2**: 초기 조건

공정한 비교를 위해 ==동일한 초기값 사용==: $v_0 = v_{\pi_0}$

---

**Step 3**: 귀납법 — $v_{\pi_{k+1}} \geq v_{k+1}$

**귀납 가정**: $v_{\pi_k} \geq v_k$

$$\begin{aligned}
v_{\pi_{k+1}} - v_{k+1} &= (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_{k+1}}) - \max_\pi (r_\pi + \gamma P_\pi v_k) \\
&\geq (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_k}) - \max_\pi (r_\pi + \gamma P_\pi v_k) \\
&\quad (\because\ v_{\pi_{k+1}} \geq v_{\pi_k} \text{ by Policy Improvement Lemma, } P_{\pi_{k+1}} \geq 0) \\
&= (r_{\pi_{k+1}} + \gamma P_{\pi_{k+1}} v_{\pi_k}) - (r_{\pi'_k} + \gamma P_{\pi'_k} v_k) \\
&\quad (\text{let } \pi'_k = \arg\max_\pi (r_\pi + \gamma P_\pi v_k)) \\
&\geq (r_{\pi'_k} + \gamma P_{\pi'_k} v_{\pi_k}) - (r_{\pi'_k} + \gamma P_{\pi'_k} v_k) \\
&\quad (\because\ \pi_{k+1} = \arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_k})) \\
&= \gamma P_{\pi'_k} (v_{\pi_k} - v_k) \geq 0 \quad (\text{by induction hypothesis})
\end{aligned}$$

| | $\pi'_k$ | $\pi_{k+1}$ |
|:---|:---|:---|
| **정의** | $\arg\max_\pi (r_\pi + \gamma P_\pi v_k)$ | $\arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_k})$ |
| **Greedy 대상** | $v_k$ (VI의 중간값) | $v_{\pi_k}$ (PI의 진짜 state value) |

→ 일반적으로 $v_k \neq v_{\pi_k}$이므로 ==$\pi'_k \neq \pi_{k+1}$==

---

**Step 4**: 결론

$$v_k \leq v_{\pi_k} \leq v^* \quad \forall k \geq 0$$

$v_k \to v^*$이고 $v_{\pi_k}$가 $v_k$와 $v^*$ 사이에 있으므로, $v_{\pi_k} \to v^*$ $\square$
```

```ad-info
title: Note - Model Requirement

PI는 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$를 ==필요로 함== ([[Dynamic Programming]])
- Policy Evaluation: 모델로 [[Bellman Equation]] 풀이
- Policy Improvement: 모델로 $q_{\pi_k}(s,a)$ 계산

→ Model-free 확장: [[Monte Carlo Methods]], [[Temporal Difference Learning]]
```

<br/><br/>

## Generalized Policy Iteration

==Evaluation과 improvement의 상호작용==이라는 공통 구조를 **Generalized Policy Iteration (GPI)**라 함

$$\text{evaluation} \leftrightarrow \text{improvement}$$

| 알고리즘 | Evaluation | Improvement |
|:---|:---|:---|
| **Policy Iteration** | [[Bellman Equation\|BE]] 완전 수렴 | Greedy |
| **[[Truncated Policy Iteration]]** | BE 유한 반복 | Greedy |
| **[[Sarsa]]** | TD로 $q_\pi$ 추정 | $\epsilon$-greedy |
| **[[Monte Carlo Methods\|MC Control]]** | Episode return 평균 | $\epsilon$-greedy |

```ad-info
title: Note - GPI vs BOE Direct

[[Bellman Optimality Equation|BOE]]를 직접 푸는 [[Value Iteration]], [[Q-Learning]]은 엄밀히 GPI가 아님:
- GPI: 정책을 ==평가한 뒤== 개선
- BOE 직접: 정책 평가 ==없이== 최적 가치를 바로 계산
```

<br/><br/>

## Related Concepts

- [[Value Iteration]]: Value만 업데이트, $v_k$는 state value 아님 (PI와 대비)
- [[Truncated Policy Iteration]]: PE 반복 횟수 제한으로 VI-PI 통합
- [[Policy Evaluation]]: Policy Iteration의 평가 단계 상세
- [[Greedy Policy]]: Policy Improvement 단계에서 greedy 정책 도출
- [[Bellman Equation]]: Evaluation에서 푸는 방정식
- [[Bellman Optimality Equation]]: 수렴 조건, greedy 정책 도출의 이론적 근거
- [[Value Function]]: 계산 대상 ($v_\pi$, $q_\pi$)
- [[Dynamic Programming]]: Policy Iteration이 속한 패러다임
- [[Contraction Mapping Theorem]]: VI와의 비교에서 사용
- [[Monotone Convergence Theorem]]: PI 수렴 증명의 핵심 도구
- [[Markov Decision Process]]: PI가 적용되는 프레임워크
