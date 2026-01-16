---
date: 2026-01-11
tags:
  - Concepts/ReinforcementLearning/MarkovTheory
aliases:
  - 정상 분포
  - Steady-State Distribution
  - Invariant Distribution
keywords:
  - Stationary Distribution
  - Markov Chain
  - Limiting Distribution
  - Ergodic
related notes:
reference:
  - title: "Lecture 6 - Short Review on Discrete Time Markov Chain"
    source: "IMEN 764: Dynamic Programming & Reinforcement Learning Applications"
    author: Dong Gu Choi
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8
author:
url:
---

# Stationary Distribution

```ad-note
title: Summary
collapse: true

- ==Markov Chain의 전이 행렬 $P$ 하에서 불변인 확률 분포: $\mu P = \mu$==
- ==정상 분포에 도달하면 시간에 관계없이 분포 유지 (시간 불변)==
- ==Irreducible + Aperiodic → 유일한 정상 분포로 수렴==
- ==물리적 의미: 상태의 장기 방문 빈도, 평균 재방문 시간의 역수==
- ==RL에서: $d_\pi(s)$로 표기, 목적함수의 가중치로 활용==
```

## Definition

<!-- Lecture 6, Section 8.1 -->

==Markov Chain의 전이 행렬 $P$ 하에서 불변인 확률 분포==

$$\mu P = \mu, \quad \sum_{s \in \mathcal{S}} \mu(s) = 1$$

성분별 표현:

$$\sum_{s \in \mathcal{S}} \mu(s) p(s'|s) = \mu(s') \quad \forall s' \in \mathcal{S}$$

- $\mu = (\mu(s_1), \mu(s_2), \ldots)$: 확률 분포 (행 벡터)
- $P = [p(s'|s)]$: 전이 행렬
- $\mu(s) \geq 0$: 상태 $s$의 정상 확률

```ad-info
title: Note - Notation Convention

| 맥락 | 표기 | 의미 |
|:---|:---|:---|
| **Markov Chain** | $\mu$, $P$ | 일반적인 정상 분포, 전이 행렬 |
| **RL (MDP + Policy)** | $d_\pi$, $P_\pi$ | 정책 $\pi$ 하에서의 정상 분포, 전이 행렬 |

RL에서는 $\pi$가 정책을 나타내므로, 정상 분포는 ==$d_\pi(s)$로 표기==하여 혼동 방지
```

<br/><br/>

## Existence and Uniqueness

<!-- Lecture 6 -->

### Existence

==유한 상태 공간의 모든 Discrete-Time Markov Chain (DTMC)는 최소 하나의 정상 분포 보유==

<br/>

### Uniqueness Conditions

DTMC가 ==Irreducible + Aperiodic==이면:
- ==유일한 정상 분포 $\mu$ 존재==
- ==모든 초기 분포에서 $\mu$로 수렴==

| 조건 | 정의 |
|:---|:---|
| **Irreducible** | 모든 상태 쌍이 서로 소통 ($i \leftrightarrow j$) |
| **Aperiodic** | 모든 상태의 주기 = 1 |

```ad-important
title: Lemma - Condition Definitions
collapse: true

**Accessible (도달 가능)**:

상태 $s_j$가 상태 $s_i$에서 accessible ⟺ $\exists k \geq 1$ s.t. $[P_\pi^k]_{ij} > 0$

- ==유한 스텝 내에 $s_i$에서 $s_j$로 도달 가능==
- $k$의 값은 상태 쌍마다 다를 수 있음

**Communicate (소통)**:

두 상태 $s_i$, $s_j$가 소통 ($s_i \leftrightarrow s_j$) ⟺ ==상호 도달 가능==

- $s_i$에서 $s_j$로 도달 가능 AND
- $s_j$에서 $s_i$로 도달 가능

**Irreducible (기약)**:

Markov process가 irreducible ⟺ ==모든 상태 쌍이 서로 소통==

- 임의의 상태에서 출발하여 유한 스텝 내에 다른 모든 상태에 도달 가능
- 수학적 표현: $\forall i, j$, $\exists k \geq 1$ s.t. $[P_\pi^k]_{ij} > 0$ (단, $k$는 $i, j$에 따라 다를 수 있음)

**Regular (정칙)**:

Markov process가 regular ⟺ $\exists k \geq 1$ s.t. $P_\pi^k > 0$ (모든 원소가 양수)

- ==모든 상태 쌍에 대해 동일한 $k$ 스텝 이내에 도달 가능==
- Irreducible보다 강한 조건
```

```ad-important
title: Proof - Regular and Irreducible Relationship
collapse: true

**Regular → Irreducible**:

$P_\pi^k > 0$이면 모든 $[P_\pi^k]_{ij} > 0$ → 모든 상태 쌍이 소통 → Irreducible $\square$

**역은 성립하지 않음**: Irreducible이지만 Regular가 아닌 경우 존재 (주기적 chain)

**Irreducible + Self-loop → Regular**:

Irreducible + $\exists i: [P_\pi]_{ii} > 0$ → Regular

- Self-loop이 존재하면 aperiodic
- Irreducible + Aperiodic → Regular

**$P_\pi^k > 0$의 유지**:

$P_\pi^k > 0$이면 $P_\pi^{k'} > 0$ for all $k' \geq k$

- $P_\pi \geq 0$ (비음수 행렬)이고 $P_\pi^k > 0$이면
- $P_\pi^{k+1} = P_\pi^k \cdot P_\pi$의 모든 원소가 양수 $\square$
```

<br/><br/>

## Convergence

<!-- Lecture 6 -->

### State Distribution Evolution

초기 분포 $d_0$에서 시작하여 $k$ 스텝 후의 상태 분포:

$$d^T_k = d^T_0 P^k$$

- $[P^k]_{ij}$는 상태 $s_i$에서 $s_j$로 ==정확히 $k$ 스텝== 후 전이할 확률

```ad-important
title: Proof - State Distribution Evolution
collapse: true

**해석**: $k$ 스텝 후 상태 $s_i$에 있을 확률

$$d_k(s_i) = \sum_{j=1}^{n} d_0(s_j)[P^k]_{ji}$$

- $d_0(s_j)$: 초기에 상태 $s_j$에 있을 확률
- $[P^k]_{ji}$: $s_j$에서 $s_i$로 정확히 $k$ 스텝 전이할 확률
- ==모든 가능한 시작 상태 $s_j$에서 $s_i$로 전이하는 확률의 합==

**행렬-벡터 형태 유도**:

$$d_k(s_i) = \sum_{j=1}^{n} d_0(s_j)[P^k]_{ji} = [d_0^T P^k]_i$$

모든 $i$에 대해 성립하므로:

$$d^T_k = d^T_0 P^k \quad \square$$
```

```ad-important
title: Proof - k-step Transition Probability
collapse: true

**Case $k=1$**: 정의에 의해

$$[P]_{ij} = p^{(1)}_{ij}$$

**Case $k=2$**: 행렬 곱셈 전개

$$[P^2]_{ij} = [PP]_{ij} = \sum_{q=1}^{n} [P]_{iq}[P]_{qj}$$

- $[P]_{iq}$: $s_i$에서 $s_q$로 1스텝 전이 확률
- $[P]_{qj}$: $s_q$에서 $s_j$로 1스텝 전이 확률
- $[P]_{iq}[P]_{qj}$: $s_i \to s_q \to s_j$로 전이하는 ==joint probability==
- 모든 중간 상태 $s_q$에 대해 합산 → 정확히 2스텝으로 $s_i$에서 $s_j$로 전이할 확률

**일반화**: 귀납법으로 확장

$$[P^k]_{ij} = p^{(k)}_{ij} \quad \square$$
```

<br/>

### Limiting Distribution

Irreducible + Aperiodic (또는 Regular) DTMC에서:

$$\lim_{k \to \infty} P^k = \mathbf{1}_n \mu^T$$

- $\mathbf{1}_n = [1, \ldots, 1]^T \in \mathbb{R}^n$
- $\mathbf{1}_n \mu^T$는 ==모든 행이 $\mu^T$와 같은 상수 행렬==

```ad-important
title: Theorem - Convergence to Stationary Distribution

임의의 초기 분포 $d_0$에서 시작하면:

$$\lim_{k \to \infty} d^T_k = \mu^T$$

==초기 분포 $d_0$와 무관하게== 동일한 정상 분포 $\mu$로 수렴
```

```ad-important
title: Proof - Convergence to Stationary Distribution
collapse: true

**Step 1**: 상태 분포 진화 적용

$$d^T_k = d^T_0 P^k$$

**Step 2**: 극한 취하기

$$\lim_{k \to \infty} d^T_k = d^T_0 \lim_{k \to \infty} P^k = d^T_0 \mathbf{1}_n \mu^T$$

**Step 3**: $d^T_0 \mathbf{1}_n = 1$ (확률의 합) 적용

$$= 1 \cdot \mu^T = \mu^T \quad \square$$
```

```ad-important
title: Proof - Stationary from Limiting
collapse: true

$d^T_k = d^T_{k-1} P$의 양변에 극한 적용:

$$\lim_{k \to \infty} d^T_k = \lim_{k \to \infty} d^T_{k-1} P$$

$$\mu^T = \mu^T P \quad \square$$

**결론**: $\mu$는 ==$P$의 고유값 1에 대응하는 좌 고유벡터==
```

```ad-important
title: Proof - Why $d_\pi(s) > 0$ for All States
collapse: true

**조건**: Regular Markov process ($\exists k$ s.t. $P^k > 0$)

**Step 1**: Limiting distribution 존재

$$\lim_{k \to \infty} P^k = \mathbf{1}_n \mu^T$$

**Step 2**: $P^k > 0$이면 $P^{k'} > 0$ for all $k' \geq k$

**Step 3**: 극한 취하기

$$\lim_{k \to \infty} P^k = \mathbf{1}_n \mu^T > 0$$

**결론**: $\mathbf{1}_n \mu^T$의 모든 원소가 양수 → ==$\mu(s) > 0$ for all $s$== $\square$

**의미**: Regular Markov process에서는 정상 분포의 ==모든 상태 확률이 strictly positive== (단순히 $\geq 0$이 아님)
```

<br/>

### Time-Invariant Property

초기 분포가 $\mu$이면 ($X_0 \sim \mu$):

$$X_n \sim \mu \quad \forall n \geq 0$$

==정상 분포에 도달하면 모든 시간에서 분포 유지== (평형 상태)

```ad-info
title: Note - Stationary vs Limiting Distribution

| 개념 | 정의 | 조건 |
|:---|:---|:---|
| **Stationary** | $\mu^T = \mu^T P$ (고정점 조건) | 항상 존재 (유한 상태) |
| **Limiting** | $\lim_{k \to \infty} d_k = \mu$ (수렴값) | Irreducible + Aperiodic |

**관계**: Limiting → Stationary 성립, 역은 추가 조건 필요
```

<br/><br/>

## Physical Interpretation

<!-- Section 8.1 -->

### Long-Run Frequency

$$\lim_{n \to \infty} \frac{1}{n} \sum_{k=1}^n \mathbf{1}_{X_k = s} = \mu(s) \quad \text{a.s.}$$

==정상 확률 $\mu(s)$는 상태 $s$의 장기 방문 빈도== (Ergodic Theorem)

<br/>

### Mean Return Time

$$\mu(s) = \frac{1}{\mathbb{E}_s[\tau_s]}$$

==정상 확률은 평균 재방문 시간의 역수==

- $\tau_s$: 상태 $s$에서 출발하여 $s$로 돌아오는 시간

```ad-example
title: Example - Two-State Chain Computation
collapse: true

**전이 행렬**:

$$P = \begin{pmatrix} 1-\alpha & \alpha \\ \beta & 1-\beta \end{pmatrix}$$

**정상 분포 계산** ($\mu P = \mu$ 풀이):

$$\mu = \left( \frac{\beta}{\alpha + \beta}, \frac{\alpha}{\alpha + \beta} \right)$$

**해석**:
- 상태 1의 장기 방문 확률 $\propto \beta$ (상태 2 → 1 전이율)
- 상태 2의 장기 방문 확률 $\propto \alpha$ (상태 1 → 2 전이율)

**계산 방법**:

| 방법 | 수식 | 복잡도 |
|:---|:---|:---|
| **Linear System** | $\mu(P - I) = 0$, $\sum_s \mu(s) = 1$ | $O(\|\mathcal{S}\|^3)$ |
| **Power Iteration** | $\mu \approx v P^n$ | $O(\|\mathcal{S}\|^2 \times n)$ |
| **Iterative** | $\mu^{(k+1)} = \mu^{(k)} P$ | 수렴까지 반복 |
```

<br/><br/>

## Application in RL

<!-- Section 8.1.4 -->

### MDP with Policy

정책 $\pi$ 하에서 MDP는 Markov Chain이 되고, ==전이 행렬 $P_\pi$와 정상 분포 $d_\pi(s)$== 유도:

$$d_\pi(s') = \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \pi(a|s) p(s'|s,a)$$

행렬 형태: $d^T_\pi = d^T_\pi P_\pi$

==Exploratory policy== (예: $\varepsilon$-greedy)는 유일한 정상 분포를 유도:
- 모든 상태에서 모든 행동에 ==양의 확률== 부여 → 상태들이 서로 소통
- 결과적으로 ==Regular Markov process== 유도 → 유일한 $d_\pi$ 존재, $d_\pi(s) > 0$ for all $s$

```ad-info
title: Note - Practical Implication

$d_\pi$를 명시적으로 계산할 필요 없음 — 정책 $\pi$를 따라 샘플링하면 자연스럽게 $d_\pi$에 따라 상태 방문
```

```ad-example
title: Example - ε-Greedy Grid World
collapse: true

**설정**: 2×2 Grid World, $\varepsilon$-greedy 정책 ($\varepsilon = 0.5$)

상태 인덱싱: $s_1, s_2, s_3, s_4$ (top-left, top-right, bottom-left, bottom-right)

**전이 행렬** (전치):

$$P^T_\pi = \begin{bmatrix} 0.3 & 0.1 & 0.1 & 0 \\ 0.1 & 0.3 & 0 & 0.1 \\ 0.6 & 0 & 0.3 & 0.1 \\ 0 & 0.6 & 0.6 & 0.8 \end{bmatrix}$$

**Irreducibility 및 Regularity 검증**:
- 모든 상태가 서로 소통 → Irreducible
- 모든 상태가 자기 자신으로 전이 가능 ($[P_\pi]_{ii} > 0$) → Regular

**정상 분포 계산**:
$P^T_\pi$의 고유값: $\{-0.0449, 0.3, 0.4449, 1\}$

고유값 1에 대응하는 고유벡터 (정규화 후):

$$d_\pi = \begin{bmatrix} 0.0345 \\ 0.1084 \\ 0.1330 \\ 0.7241 \end{bmatrix}$$

**수치적 검증**:
임의의 초기 상태에서 정책을 1,000 스텝 실행하여 방문 비율 측정

![[Pasted image 20260111022330.png|500]]

**결과**: 수백 스텝 후 방문 비율이 이론적 $d_\pi$ 값으로 수렴
- $s_4$ (bottom-right)에 가장 높은 방문 확률 (0.7241)
- $s_1$ (top-left)에 가장 낮은 방문 확률 (0.0345)
```

<br/>

### Value Function Approximation

[[Value Function Approximation]]에서 $d_\pi(s)$는 ==목적함수의 가중치==로 사용:

$$J(w) = \sum_{s \in \mathcal{S}} d_\pi(s) (v_\pi(s) - \hat{v}(s,w))^2$$

- ==자주 방문하는 상태에 더 큰 중요도== 부여
- 가중 Norm 정의: $\|x\|_D^2 = x^T D x$ where $D = \text{diag}(d_\pi)$
- [[TD-Linear]]의 수렴 조건에서 핵심 역할

```ad-info
title: Note - Average Reward Criterion

무한 지평 MDP에서 ==평균 보상 기준==에도 정상 분포 사용:

$$\rho(\pi) = \sum_{s \in \mathcal{S}} d_\pi(s) \sum_{a \in \mathcal{A}} \pi(a|s) r(s,a)$$
```

<br/><br/>

## Related Concepts

- [[Markov Process]]: 정상 분포를 가지는 확률 과정
- [[Markov Property]]: Markov Chain의 기본 성질
- [[Transition Probability]]: 정상 분포를 정의하는 전이 행렬
- [[Markov Decision Process]]: 정책 하에서 정상 분포 유도
- [[TD-Linear]]: $d_\pi$가 목적함수 가중치로 사용
- [[Projected Bellman Error]]: 가중 norm $\|\cdot\|_D$ 정의에 사용

