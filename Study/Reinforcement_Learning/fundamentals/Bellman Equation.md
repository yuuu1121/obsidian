---
date: 2025-01-11
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 벨만 방정식
keywords:
  - Bellman Equation
  - Policy Evaluation
  - Value Function
  - Bootstrapping
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 3
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Bellman Equation

```ad-note
title: Summary
collapse: true

- ==[[Value Function]] 간의 재귀적 관계를 나타내는 선형 방정식==
- ==현재 가치 = 즉각 보상 + 할인된 미래 가치의 기댓값== ([[Bootstrapping]])
- ==주어진 정책 $\pi$에 대해 유일한 해 존재==
- ==풀이 = [[Policy Evaluation]]== (정책의 가치 계산)
```

![[Pasted image 20251230171026.png|700]]

## Definition

==특정 정책 $\pi$를 따를 때 [[Value Function]] 간의 재귀적 관계를 나타내는 선형 방정식==

- 모든 상태의 가치 간 관계를 나타내는 도구로, ==state value 분석의 핵심==
- ==무한한 미래를 직접 계산하는 대신, 한 스텝만 보고 나머지는 재귀로 해결== ([[Bootstrapping]])
- **선형성**: Expectation 연산만 포함 (max 없음) → [[Bellman Optimality Equation]]과 구분
- **유일성**: 주어진 정책 $\pi$에 대해 ==유일한 해 존재==
- **수렴성**: 반복 계산 시 수렴 보장 ($\gamma < 1$)

```ad-info
title: Note - BE vs BOE

| 방정식 | 역할 |
|:---|:---|
| **Bellman Equation** | ==주어진 정책 $\pi$의 가치 계산== ([[Policy Evaluation]]) |
| [[Bellman Optimality Equation]] | 최적 정책의 가치 계산 (정책이 최적) |

→ [[Bellman Optimality Equation|BOE]]는 ==corresponding policy가 optimal인 특수한 Bellman Equation==
```

```ad-info
title: Note - Bellman Equation in MRP
collapse: true

[[Markov Reward Process|MRP]]는 ==Action이 없는 특수한 경우==로, Bellman Equation이 단순화됨:

$$v(s) = r(s) + \gamma \sum_{s' \in \mathcal{S}} p(s'|s) v(s')$$

| 형태 | MRP | MDP |
|:---|:---|:---|
| **수식** | $v = r + \gamma P v$ | $v_\pi = r_\pi + \gamma P_\pi v_\pi$ |
| **정책** | 없음 | $\pi(a\|s)$로 가중 |
| **전이** | $p(s'\|s)$ | $p_\pi(s'\|s) = \sum_a \pi(a\|s) p(s'\|s,a)$ |

**Direct Solution**: $v = (I - \gamma P)^{-1} r$ — $O(n^3)$, 작은 MRP에만 실용적
```

<br/><br/>

## Elementwise Form

### State Value

$$v_\pi(s) = \sum_{a \in \mathcal{A}} \pi(a|s) \left[ \underbrace{\sum_{r \in \mathcal{R}} p(r|s, a) r}_{\text{immediate reward}} + \gamma \underbrace{\sum_{s' \in \mathcal{S}} p(s'|s, a) v_\pi(s')}_{\text{future reward}} \right]$$

| 요소 | 역할 |
|:---|:---|
| $v_\pi(s)$, $v_\pi(s')$ | ==미지수== (계산해야 할 state values) |
| $\pi(a\|s)$ | ==주어진 정책== → BE를 푸는 것이 [[Policy Evaluation]] |
| $p(r\|s,a)$, $p(s'\|s,a)$ | ==시스템 모델== (환경의 dynamics) |

```ad-important
title: Proof - Derivation of Bellman Equation
collapse: true

**Starting Point**: [[Value Function|State value]]의 정의에서 시작

$$\begin{aligned}
v_\pi(s) &= \mathbb{E}[G_t|S_t = s] \\
&= \mathbb{E}[R_{t+1} + \gamma G_{t+1}|S_t = s] \\
&= \mathbb{E}[R_{t+1}|S_t = s] + \gamma \mathbb{E}[G_{t+1}|S_t = s]
\end{aligned}$$

→ ==즉각 보상의 기댓값==과 ==미래 보상의 기댓값==으로 분해

---

**Expectation of Immediate Rewards**:

$$\begin{aligned}
\mathbb{E}[R_{t+1} | S_t = s] &= \sum_{a \in \mathcal{A}} \pi(a|s)\mathbb{E}[R_{t+1} | S_t = s, A_t = a] \\
&= \sum_{a \in \mathcal{A}} \pi(a|s) \sum_{r \in \mathcal{R}} p(r|s, a)r
\end{aligned}$$

- 정책 $\pi(a|s)$에 따라 행동 선택
- 각 행동에 대해 보상의 기댓값 계산

---

**Expectation of Future Rewards**:

$$\begin{aligned}
\mathbb{E}[G_{t+1}|S_t=s] &= \sum_{s'\in\mathcal{S}} \mathbb{E}[G_{t+1}|S_t=s, S_{t+1}=s']p(s'|s) \\
&= \sum_{s'\in\mathcal{S}} \mathbb{E}[G_{t+1}|S_{t+1}=s']p(s'|s) \\
&= \sum_{s'\in\mathcal{S}} v_\pi(s')p(s'|s) \\
&= \sum_{s'\in\mathcal{S}} v_\pi(s') \sum_{a\in\mathcal{A}} p(s'|s,a)\pi(a|s)
\end{aligned}$$

**핵심**: $\mathbb{E}[G_{t+1}|S_t=s, S_{t+1}=s'] = \mathbb{E}[G_{t+1}|S_{t+1}=s']$

→ ==Markov property==: 미래 보상은 현재 상태에만 의존, 이전 상태와 무관

---

**Final Result**: 두 기댓값을 합치면 Bellman Equation

$$v_\pi(s) = \sum_{a \in \mathcal{A}} \pi(a|s) \left[ \sum_{r \in \mathcal{R}} p(r|s, a) r + \gamma \sum_{s' \in \mathcal{S}} p(s'|s, a) v_\pi(s') \right]$$
```

```ad-example
title: Example - Policy and State Value
collapse: true

![[Pasted image 20251229170428.png]]

| 정책 | 행동 | State Value |
|:---|:---|:---|
| 왼쪽 | 아래 (금지구역 회피) | $v(s_1) = 0 + \gamma v(s_3)$ |
| 가운데 | 오른쪽 (금지구역 진입) | $v(s_1) = -1 + \gamma v(s_2)$ |
| 오른쪽 | 확률 0.5로 선택 | $v(s_1) = 0.5[0 + \gamma v(s_3)] + 0.5[-1 + \gamma v(s_2)]$ |

→ ==각 상태의 가치가 다른 상태의 가치에 의존== → 순환처럼 보이지만, ==연립방정식으로 해결 가능==
```

<br/>

### Action Value

$v \leftarrow q$를 $q \leftarrow v$에 대입:

$$q_\pi(s,a) = \sum_{r \in \mathcal{R}} p(r|s, a) r + \gamma \sum_{s' \in \mathcal{S}} p(s'|s,a) \sum_{a' \in \mathcal{A}} \pi(a'|s') q_\pi(s',a')$$

→ 모든 state-action pair에 대해 성립

```ad-info
title: Note - Alternative Notations
collapse: true

**Expectation Form** — [[Temporal Difference Learning]]이 해결하는 형태:

$$v_\pi(s) = \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s]$$

---

**Joint Distribution Form** — [[Law of Total Probability]] 적용:

$$v_{\pi}(s) = \sum_{a \in \mathcal{A}} \pi(a|s) \sum_{s' \in \mathcal{S}} \sum_{r \in \mathcal{R}} p(s', r|s, a) [r + \gamma v_{\pi}(s')]$$

---

**Compact Form** — 정책 가중 보상/전이 사용:

$$v_{\pi}(s) = r_{\pi}(s) + \gamma \sum_{s' \in \mathcal{S}} p_{\pi}(s'|s) v_{\pi}(s')$$

where:
$$r_{\pi}(s) \doteq \sum_{a \in \mathcal{A}} \pi(a|s) \sum_{r \in \mathcal{R}} p(r|s, a) r, \quad p_{\pi}(s'|s) \doteq \sum_{a \in \mathcal{A}} \pi(a|s) p(s'|s, a)$$
```

<br/><br/>

## Matrix-Vector Form

Bellman equation은 모든 상태에 대한 연립방정식 → ==matrix-vector form이 간결한 표현==

<br/>

### State Value

상태를 $s_i$ ($i = 1, \ldots, n$, $n = |\mathcal{S}|$)로 인덱싱하면:

$$v_\pi = r_\pi + \gamma P_\pi v_\pi$$

where:
$$\begin{aligned}
v_\pi &= [v_\pi(s_1), \ldots, v_\pi(s_n)]^T \in \mathbb{R}^n \\
r_\pi &= [r_\pi(s_1), \ldots, r_\pi(s_n)]^T \in \mathbb{R}^n \\
P_\pi &\in \mathbb{R}^{n \times n}, \quad [P_\pi]_{ij} = p_\pi(s_j|s_i)
\end{aligned}$$

- $v_\pi$: ==unknown== (계산 대상)
- $r_\pi$, $P_\pi$: ==known== (환경과 정책으로부터 결정)
- $P_\pi$는 ==확률 행렬== (비음수, 각 행의 합이 1)

<br/>

### Action Value

$$q_\pi = \tilde{r} + \gamma P \Pi q_\pi$$

**정의** ($n = |\mathcal{S}|$, $m = |\mathcal{A}|$):
- $q_\pi \in \mathbb{R}^{nm}$: action value 벡터, $[q_\pi]_{(s,a)} = q_\pi(s,a)$
- $\tilde{r} \in \mathbb{R}^{nm}$: 즉각 보상 벡터, $[\tilde{r}]_{(s,a)} = \sum_{r \in \mathcal{R}} p(r|s,a) r$
- $P \in \mathbb{R}^{nm \times n}$: 전이 확률 행렬, $[P]_{(s,a), s'} = p(s'|s,a)$
- $\Pi \in \mathbb{R}^{n \times nm}$: 블록 대각 행렬, $\Pi_{s', (s',a')} = \pi(a'|s')$

```ad-info
title: Note - Difference from State Value Form

- $\tilde{r}$, $P$: ==정책과 무관==, 시스템 모델에만 의존
- $\Pi$: ==정책이 여기에 포함==
- State value form에서는 $r_\pi$, $P_\pi$에 정책이 통합됨
```

<br/><br/>

## Contraction Property

### Bellman Operator

BE의 우변은 ==$v$만의 함수==로 표현 가능:

$$T_\pi(v) \doteq r_\pi + \gamma P_\pi v$$

- BE는 ==$v_\pi = T_\pi(v_\pi)$ 형태의 고정점 방정식==
- [[Policy Evaluation]]은 $v_{k+1} = T_\pi(v_k)$ 반복으로 고정점 탐색

<br/>

### Contraction Mapping

Bellman operator $T_\pi(v)$는 ==[[Contraction Mapping Theorem|contraction mapping]]==

임의의 $v_1, v_2 \in \mathbb{R}^{|\mathcal{S}|}$에 대해:

$$\|T_\pi(v_1) - T_\pi(v_2)\|_\infty \leq \gamma \|v_1 - v_2\|_\infty$$

```ad-info
title: Note - Why Contraction Property Matters

[[Contraction Mapping Theorem]]을 적용하여 BE 분석 가능:
- **Existence**: $v_\pi = T_\pi(v_\pi)$를 만족하는 ==고정점 $v_\pi$ 존재==
- **Uniqueness**: 고정점은 ==유일==
- **Convergence**: $v_{k+1} = T_\pi(v_k)$ 반복 시 ==임의의 초기값에서 $v_\pi$로 수렴==
```

```ad-important
title: Proof - Contraction Property
collapse: true

**설정**: 임의의 $v_1, v_2 \in \mathbb{R}^{|\mathcal{S}|}$

---

**Step 1**: $T_\pi(v_1) - T_\pi(v_2)$ 계산

$$T_\pi(v_1) - T_\pi(v_2) = (r_\pi + \gamma P_\pi v_1) - (r_\pi + \gamma P_\pi v_2) = \gamma P_\pi (v_1 - v_2)$$

---

**Step 2**: Maximum norm 적용

$i$번째 원소를 $p_i^T$를 $P_\pi$의 $i$번째 행이라 하면:

$$|[T_\pi(v_1) - T_\pi(v_2)]_i| = \gamma |p_i^T(v_1 - v_2)|$$

$p_i$는 ==확률 벡터== (모든 원소 $\geq 0$, 합 = 1)이므로:

$$|p_i^T(v_1 - v_2)| \leq p_i^T|v_1 - v_2| \leq \|v_1 - v_2\|_\infty$$

---

**결론**:

$$\|T_\pi(v_1) - T_\pi(v_2)\|_\infty = \max_i |[T_\pi(v_1) - T_\pi(v_2)]_i| \leq \gamma \|v_1 - v_2\|_\infty$$

$\gamma < 1$이므로 $T_\pi(v)$는 contraction mapping $\square$
```

```ad-info
title: Note - BE vs BOE Contraction

| | BE | [[Bellman Optimality Equation\|BOE]] |
|:---|:---|:---|
| **Operator** | $T_\pi(v) = r_\pi + \gamma P_\pi v$ | $T(v) = \max_\pi (r_\pi + \gamma P_\pi v)$ |
| **선형성** | ==선형== | 비선형 ($\max$ 연산) |
| **고정점** | $v_\pi$ (정책 $\pi$의 가치) | $v^*$ (최적 가치) |
| **Contraction** | $\gamma$-contraction | $\gamma$-contraction |

→ 둘 다 contraction이므로 ==유일한 고정점 존재, 반복 알고리즘 수렴 보장==
```

<br/><br/>

## Solving Methods

Bellman equation을 풀면 state value 획득 → 이 과정이 ==[[Policy Evaluation]]==

<br/>

### Closed-form Solution

$$v_\pi = (I - \gamma P_\pi)^{-1} r_\pi$$

- **존재 조건**: ==$\gamma < 1$이면 항상 역행렬 존재==
- **복잡도**: $O(n^3)$ — 대규모 문제에 비효율적

<br/>

### Iterative Solution

$$v_{k+1} = r_\pi + \gamma P_\pi v_k, \quad k = 0, 1, 2, \ldots$$

- **초기화**: $v_0$ 임의 설정 (보통 $\mathbf{0}$)
- **종료 조건**: $\|v_{k+1} - v_k\|_\infty < \theta$
- **수렴성**: ==$\gamma < 1$이면 기하급수적으로 수렴==

```ad-important
title: Proof - Convergence of Iterative Solution
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

<br/>

### Solution Approaches

BE를 반복적으로 풀면서 정책을 개선하는 ==GPI (Generalized Policy Iteration)== 방식으로 최적 정책에 도달:

| 방법 | Model | 특징 |
|:---|:---|:---|
| **[[Policy Iteration]]** | Model-Based | PE로 $v_\pi$ 계산 + greedy 개선 |
| **[[Sarsa]]** | Model-Free | TD로 $q_\pi$ 추정 + $\epsilon$-greedy |
| **[[Truncated Policy Iteration]]** | Model-Based | VI와 PI의 통합 |

```ad-info
title: Note - Alternative Approach

[[Policy#Optimal Policy|최적 정책]]에 도달하는 다른 방식으로 ==BOE 직접 방식==이 있음:
- [[Bellman Optimality Equation|BOE]]를 직접 풀어 $v^*$, $q^*$를 한 번에 계산
- [[Value Iteration]], [[Q-Learning]] 등이 이 방식을 사용
```

```ad-example
title: Example - Bellman Equation Calculation
collapse: true

### Example 1: Deterministic Policy

![[Pasted image 20251231112837.png|300]]

**설정**:
- 4개 상태 그리드 월드
- 금지구역: $r = -1$ (주황), 목표구역: $r = 1$ (파랑)
- $s_4$: absorbing state

각 상태에서 정책이 결정적이므로:
- $\pi(a_3|s_1) = 1$ (아래로), $p(s_3|s_1, a_3) = 1$, $p(r=0|s_1, a_3) = 1$

**Bellman Equation**:
$$\begin{aligned}
v_\pi(s_1) &= 0 + \gamma v_\pi(s_3) \\
v_\pi(s_2) &= 1 + \gamma v_\pi(s_4) \\
v_\pi(s_3) &= 1 + \gamma v_\pi(s_4) \\
v_\pi(s_4) &= 1 + \gamma v_\pi(s_4)
\end{aligned}$$

**풀이** ($s_4$부터 역순):
$$v_\pi(s_4) = \frac{1}{1-\gamma}$$
$$v_\pi(s_3) = 1 + \gamma \cdot \frac{1}{1-\gamma} = \frac{1}{1-\gamma}$$
$$v_\pi(s_2) = \frac{1}{1-\gamma}, \quad v_\pi(s_1) = \frac{\gamma}{1-\gamma}$$

**$\gamma = 0.9$ 대입**: $v_\pi(s_4) = v_\pi(s_3) = v_\pi(s_2) = 10, \quad v_\pi(s_1) = 9$

---

### Example 2: Stochastic Policy

![[Pasted image 20251231112911.png|300]]

**설정**: $s_1$에서 오른쪽/아래 각각 확률 0.5
- $\pi(a_2|s_1) = 0.5$, $\pi(a_3|s_1) = 0.5$

**$s_1$의 Bellman Equation**:
$$v_\pi(s_1) = \underbrace{0.5[0 + \gamma v_\pi(s_3)]}_{\text{Downward}} + \underbrace{0.5[-1 + \gamma v_\pi(s_2)]}_{\text{Rightward (forbidden)}}$$

**풀이**:
$$v_\pi(s_4) = v_\pi(s_3) = v_\pi(s_2) = \frac{1}{1-\gamma}$$
$$v_\pi(s_1) = 0.5 \cdot \gamma \cdot \frac{1}{1-\gamma} + 0.5 \left(-1 + \gamma \cdot \frac{1}{1-\gamma}\right) = -0.5 + \frac{\gamma}{1-\gamma}$$

**$\gamma = 0.9$ 대입**: $v_\pi(s_1) = -0.5 + 9 = 8.5$

**정책 비교**: Deterministic (9) > Stochastic (8.5) → 금지구역 회피 정책이 더 좋음

---

### Example 3: Matrix-Vector Form

**Stochastic Policy의 Matrix-Vector Form**:

$$\begin{bmatrix} v_\pi(s_1) \\ v_\pi(s_2) \\ v_\pi(s_3) \\ v_\pi(s_4) \end{bmatrix} = \underbrace{\begin{bmatrix} -0.5 \\ 1 \\ 1 \\ 1 \end{bmatrix}}_{r_\pi} + \gamma \underbrace{\begin{bmatrix} 0 & 0.5 & 0.5 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 0 & 1 \end{bmatrix}}_{P_\pi} \begin{bmatrix} v_\pi(s_1) \\ v_\pi(s_2) \\ v_\pi(s_3) \\ v_\pi(s_4) \end{bmatrix}$$

**$r_\pi$ 계산**: $r_\pi(s_1) = 0.5 \cdot 0 + 0.5 \cdot (-1) = -0.5$

**$P_\pi$ 특성**:
- $[P_\pi]_{ij} = p_\pi(s_j|s_i) = \sum_{a \in \mathcal{A}} \pi(a|s_i) p(s_j|s_i, a)$
- 각 행의 합이 1 (확률 행렬): $P_\pi \mathbf{1} = \mathbf{1}$

**Closed-form Solution**: $v_\pi = (I - \gamma P_\pi)^{-1} r_\pi$

---

### Example 4: Action Value

**정책이 선택하지 않는 행동도 action value 존재**

**$s_1$에서의 Action Values** (Stochastic policy 기준):

정책이 선택하는 행동:
$$q_\pi(s_1, a_2) = -1 + \gamma v_\pi(s_2) \quad \text{(오른쪽, 금지구역)}$$
$$q_\pi(s_1, a_3) = 0 + \gamma v_\pi(s_3) \quad \text{(아래)}$$

정책이 선택하지 않는 행동:
$$q_\pi(s_1, a_1) = -1 + \gamma v_\pi(s_1) \quad \text{(왼쪽, 벽)}$$
$$q_\pi(s_1, a_4) = -1 + \gamma v_\pi(s_1) \quad \text{(위, 벽)}$$
$$q_\pi(s_1, a_5) = 0 + \gamma v_\pi(s_1) \quad \text{(제자리)}$$

**State Value와의 관계**:
$$v_\pi(s_1) = \sum_{a \in \mathcal{A}} \pi(a|s_1) q_\pi(s_1, a) = 0.5 \cdot q_\pi(s_1, a_2) + 0.5 \cdot q_\pi(s_1, a_3)$$

**선택되지 않는 행동의 가치가 중요한 이유**:
- 현재 정책이 최적이 아닐 수 있음 → 더 좋은 행동을 놓치고 있을 가능성
- 최적 정책 탐색을 위해 모든 행동 탐색 필요
- $\pi^*(s) = \arg\max_a q^*(s,a)$ 계산에 모든 action value 필요
```

<br/><br/>

## Related Concepts

- [[Policy]]: BE가 평가하는 대상 — 주어진 $\pi$에 대해 $v_\pi$ 계산
- [[Value Function]]: BE로 계산되는 함수 — $v_\pi(s)$, $q_\pi(s,a)$
- [[Return]]: $v_\pi(s) = \mathbb{E}[G_t | S_t = s]$ — BE는 Return의 재귀적 분해
- [[Markov Reward Process]]: Action 없는 단순화된 BE — $v = r + \gamma P v$
- [[Bellman Optimality Equation]]: $v^*(s) = \max_a [r + \gamma \sum_{s'} p(s'|s,a) v^*(s')]$ — max 포함 비선형
- [[Policy Evaluation]]: BE를 푸는 과정 — 정책의 가치 계산
- [[Policy Iteration]]: BE + greedy 개선 반복 (GPI)
- [[Dynamic Programming]]: Model-based 해법 — 모델 $p$가 필요
- [[Temporal Difference Learning]]: Model-free BE 해결 — [[Stochastic Approximation]] 기반
- [[Sarsa]]: Action Value BE를 TD로 해결 — On-Policy GPI
- [[Monte Carlo Methods]]: Episode return 기반 BE 추정 — Unbiased but high variance
- [[Markov Property]]: BE 성립의 핵심 가정 — $\mathbb{E}[G_{t+1}|S_t, S_{t+1}] = \mathbb{E}[G_{t+1}|S_{t+1}]$

