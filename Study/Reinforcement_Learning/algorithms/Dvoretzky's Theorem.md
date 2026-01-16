---
date: 2026-01-06
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Dvoretzky 정리
  - Dvoretzky's Convergence Theorem
keywords:
  - Dvoretzky
  - Stochastic Approximation
  - Convergence
  - Q-Learning
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 6
author:
url:
---

# Dvoretzky's Theorem

```ad-note
title: Summary
collapse: true

- ==[[Stochastic Approximation|RM]]보다 일반적인 SA 수렴 정리==
- 핵심 차이: $\alpha_k$, $\beta_k$가 ==stochastic== (history에 의존 가능)
- ==[[Stochastic Approximation|RM 정리]] 증명==과 ==[[Q-Learning]] 수렴 증명==에 사용
```

## Definition

[[Stochastic Approximation|Robbins-Monro]]보다 ==일반적인 SA 수렴 정리==

**핵심 차이점**:

| 항목 | RM | Dvoretzky |
|:---|:---|:---|
| $\alpha_k$ | ==Deterministic== sequence | ==$H_k$에 의존하는 random variable== 가능 |
| 적용 범위 | 고정된 step size sequence | $\alpha_k$가 $\Delta_k$의 함수인 경우에도 적용 |

<br/>

## Theorem

```ad-important
title: Theorem - Dvoretzky's Convergence

Stochastic process ($\alpha_k \geq 0$, $\beta_k \geq 0$):

$$\Delta_{k+1} = (1 - \alpha_k) \Delta_k + \beta_k \eta_k$$

다음 조건 만족 시 $\Delta_k \xrightarrow{\text{a.s.}} 0$:

**(a)** $\sum \alpha_k = \infty$, $\sum \alpha_k^2 < \infty$, $\sum \beta_k^2 < \infty$ (uniformly a.s.)

**(b)** $\mathbb{E}[\eta_k | H_k] = 0$, $\mathbb{E}[\eta_k^2 | H_k] \leq C$ (a.s.)

where $H_k = \{\Delta_k, \Delta_{k-1}, \ldots, \eta_{k-1}, \ldots, \alpha_{k-1}, \ldots, \beta_{k-1}, \ldots\}$
```

```ad-info
title: Note - Uniformly Almost Surely

- $\alpha_k$, $\beta_k$가 ==random variable==일 수 있으므로 극한의 정의가 확률적
- $H_k$가 random variable sequence이므로 조건부 기대값도 ==almost sure sense==로 정의
```

```ad-important
title: Proof - Dvoretzky's Theorem
collapse: true

**Quasimartingale** 기반 증명 ([[Martingale]] 참조)

**Step 1**: $h_k \doteq \Delta_k^2$로 정의

$$\mathbb{E}[h_{k+1} - h_k | H_k] = -\alpha_k(2 - \alpha_k)\Delta_k^2 + \beta_k^2 \mathbb{E}[\eta_k^2 | H_k]$$

($\mathbb{E}[\eta_k | H_k] = 0$이므로 cross term 소거)

**Step 2**: $\sum \alpha_k^2 < \infty$ → $\alpha_k \to 0$ → 충분히 큰 $k$에서 $\alpha_k \leq 1$

$$\mathbb{E}[h_{k+1} - h_k | H_k] \leq \beta_k^2 C$$

**Step 3**: Quasimartingale convergence → $h_k = \Delta_k^2$ 수렴

**Step 4**: $\sum \alpha_k \Delta_k^2 < \infty$이고 $\sum \alpha_k = \infty$이므로 $\Delta_k \to 0$ a.s.
```

<br/>

## Applications

### Mean Estimation

[[Stochastic Approximation|Mean estimation]]을 ==Dvoretzky로 직접 증명== (RM 거치지 않음):

$$\Delta_{k+1} = (1 - \alpha_k)\Delta_k + \alpha_k \underbrace{(x_k - w^*)}_{\eta_k}$$

$\{x_k\}$ i.i.d.이므로 $\mathbb{E}[\eta_k | H_k] = \mathbb{E}[x_k] - w^* = 0$

### RM Theorem Proof

[[Stochastic Approximation|RM 알고리즘]]을 Dvoretzky 형태로 변환:

$$\Delta_{k+1} = (1 - \underbrace{a_k \nabla_w g(w'_k)}_{\alpha_k})\Delta_k + a_k(-\eta_k)$$

$\alpha_k$는 $w_k$에 의존하는 ==stochastic sequence== → Dvoretzky의 강점

<br/>

## Extension (Theorem 6.3)

==다중 변수 버전== — [[Q-Learning]] 수렴 증명에 사용

```ad-important
title: Theorem - Dvoretzky Extension

유한 집합 $\mathcal{S}$에 대해:

$$\Delta_{k+1}(s) = (1 - \alpha_k(s))\Delta_k(s) + \beta_k(s)\eta_k(s)$$

다음 조건 만족 시 모든 $s \in \mathcal{S}$에서 $\Delta_k(s) \to 0$ a.s.:

**(a)** $\sum \alpha_k(s) = \infty$, $\sum \alpha_k^2(s) < \infty$, $\sum \beta_k^2(s) < \infty$, $\mathbb{E}[\beta_k(s)|H_k] \leq \mathbb{E}[\alpha_k(s)|H_k]$

**(b)** $\|\mathbb{E}[\eta_k(s)|H_k]\|_\infty \leq \gamma \|\Delta_k\|_\infty$ where $\gamma \in (0, 1)$

**(c)** $\text{var}[\eta_k(s)|H_k] \leq C(1 + \|\Delta_k(s)\|_\infty)^2$
```

```ad-info
title: Note - Extension vs Basic Dvoretzky

| 항목 | Basic Dvoretzky | Extension |
|:---|:---|:---|
| 변수 | 단일 $\Delta_k$ | ==다중 $\Delta_k(s)$== for $s \in \mathcal{S}$ |
| Noise 조건 | $\mathbb{E}[\eta_k\|H_k] = 0$ | $\|\mathbb{E}[\eta_k(s)\|H_k]\|_\infty \leq \gamma\|\Delta_k\|_\infty$ |
| 분산 조건 | $\mathbb{E}[\eta_k^2\|H_k] \leq C$ | $\text{var}[\eta_k(s)\|H_k] \leq C(1 + \|\Delta_k\|_\infty)^2$ |

→ Extension은 ==기대값과 분산이 error $\Delta_k$에 bounded==되면 충분 (더 완화된 조건)
```

```ad-info
title: Note - Maximum Norm

$\|\cdot\|_\infty$는 집합 $\mathcal{S}$에 대한 maximum norm:

$$\|\Delta_k(s)\|_\infty = \max_{s \in \mathcal{S}} |\Delta_k(s)|$$

RL에서 $s$는 ==state 또는 state-action pair==를 나타냄

→ 모든 $s$에서 수렴하려면 ==모든 $s$에서 조건 만족== 필요
```

<br/><br/>

## Related Concepts

- [[Stochastic Approximation]]: Dvoretzky는 RM의 일반화
- [[Q-Learning]]: Dvoretzky Extension으로 수렴 증명
- [[Stochastic Convergence]]: Almost sure convergence 개념
- [[Martingale]]: Quasimartingale 증명의 이론적 기반
