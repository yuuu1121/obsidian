---
date: 2026-01-06
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 확률적 근사
  - SA
  - Robbins-Monro Algorithm
  - RM Algorithm
keywords:
  - Stochastic Approximation
  - Robbins-Monro
  - Dvoretzky
  - Step Size
  - SGD
  - Incremental Learning
  - Mean Estimation
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 6
  - title: "A Stochastic Approximation Method"
    authors: [Herbert Robbins, Sutton Monro]
    year: 1951
    journal: The Annals of Mathematical Statistics
author:
url:
---

# Stochastic Approximation

```ad-note
title: Summary
collapse: true

- ==함수의 명시적 표현 없이 noisy observation만으로 $g(w) = 0$의 근을 찾는 반복 알고리즘==
- ==Non-incremental (batch) → Incremental 전환의 이론적 기반==
- ==핵심 수렴 조건: $\sum \alpha_k = \infty$ (도달 가능), $\sum \alpha_k^2 < \infty$ (fluctuation 감소)==
- ==[[Stochastic Gradient Descent|SGD]], [[Temporal Difference Learning|TD]]는 Robbins-Monro 알고리즘의 특수 형태==
```

![[Pasted image 20260107091936.png|700]]

## Definition

==함수의 명시적 표현이나 도함수 없이, noisy observation만으로 방정식의 근을 찾는 반복 알고리즘 클래스==

$$w_{k+1} = w_k - \alpha_k \tilde{g}(w_k)$$

- $\tilde{g}(w_k) = g(w_k) + \eta_k$: noisy observation
- $g(w^*) = 0$의 근 $w^*$를 찾는 것이 목표

| | Model-Based | Model-Free (SA) |
|:---|:---|:---|
| **필요 정보** | $g(w)$, $\nabla g(w)$의 명시적 표현 | ==Noisy observation $\tilde{g}(w)$만== |
| **예시** | [[Gradient Descent]], [[Dynamic Programming]] | [[Temporal Difference Learning\|TD]], [[Q-Learning]] |

```ad-info
title: Note - Role of SA

==Batch → Incremental 전환 시 수렴을 보장==하는 이론적 기반

- **Batch** ([[Monte Carlo Methods]]): 모든 샘플 수집 후 일괄 계산
- **Incremental** ([[Temporal Difference Learning|TD]]): 샘플마다 즉시 업데이트 — SA가 수렴 보장
```

<br/><br/>

## Mean Estimation

==SA의 핵심 아이디어를 보여주는 motivating example==

**Problem**: 확률변수 $X$의 기대값 $\mathbb{E}[X]$를 i.i.d. 샘플 $\{x_i\}_{i=1}^n$로부터 추정

<br/>

### Non-Incremental (Batch)

모든 샘플 수집 후 일괄 계산:

$$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$

[[Law of Large Numbers]]에 의해 $\bar{x} \to \mathbb{E}[X]$ as $n \to \infty$

**단점**: 샘플 수가 많으면 ==모든 샘플 수집까지 오래 대기==해야 함

<br/>

### Incremental (SA)

샘플이 도착할 때마다 ==즉시 업데이트==하는 방식

$w_{k+1}$을 처음 $k$개 샘플의 평균으로 정의하면:

$$w_{k+1} \doteq \frac{1}{k} \sum_{i=1}^{k} x_i$$

이를 $w_k = \frac{1}{k-1} \sum_{i=1}^{k-1} x_i$로 표현하면:

$$\begin{aligned}
w_{k+1} &= \frac{1}{k} \left( (k-1) w_k + x_k \right) = w_k - \frac{1}{k}(w_k - x_k)
\end{aligned}$$

**일반화된 형태**:

$$w_{k+1} = w_k - \alpha_k (w_k - x_k)$$

- $\alpha_k = 1/k$: ==정확한 평균==과 동일
- 일반 $\alpha_k$: 수렴 조건 만족 시 $\mathbb{E}[X]$로 수렴

```ad-info
title: Note - Mean Estimation as RM

Mean estimation이 [[#Robbins-Monro Algorithm|RM]]의 ==특수 사례==임을 증명

$g(w) \doteq w - \mathbb{E}[X] = 0$의 근 찾기로 변환

**Noisy observation**: $\tilde{g}(w, \eta) = w - x = g(w) + \eta$, where $\eta = \mathbb{E}[X] - x$

**조건 검증**:
- (a): $\nabla_w g(w) = 1$ → $c_1 = c_2 = 1$ 만족
- (b): $\sum \alpha_k = \infty$, $\sum \alpha_k^2 < \infty$ 만족 시
- (c): $\{x_k\}$ i.i.d.이면 $\mathbb{E}[\eta_k | H_k] = 0$

→ RM Theorem에 의해 $w_k \to \mathbb{E}[X]$ ==almost surely==. 수렴은 ==$X$의 분포에 대한 가정 불필요== (distribution-free)
```

<br/><br/>

## Robbins-Monro Algorithm

==SA의 원형이자 핵심 알고리즘== (1951)

<br/>

### Problem Setup

**목표**: $g(w) = 0$의 근 $w^*$ 찾기

**제약**:
- $g(w)$의 수식을 ==모름== (black-box)
- Noisy observation만 가능: $\tilde{g}(w, \eta) = g(w) + \eta$

![[Pasted image 20260106055026.png|400]]

**Optimization**: $\min_w J(w)$ → $g(w) \doteq \nabla_w J(w) = 0$으로 변환 가능

```ad-info
title: Note - Equation $g(w) = c$

$g(w) = c$ 형태의 방정식도 $\tilde{g}(w) \doteq g(w) - c = 0$으로 변환하면 RM 적용 가능
```

<br/>

### Algorithm

```ad-tldr
title: Algorithm - Robbins-Monro

**입력**: 초기값 $w_1$, step size sequence $\{\alpha_k\}$

**For** $k = 1, 2, 3, \ldots$:
- 현재 추정치 $w_k$에서 noisy observation $\tilde{g}(w_k, \eta_k)$ 획득
- 업데이트:
  $$w_{k+1} = w_k - \alpha_k \tilde{g}(w_k, \eta_k)$$

**출력**: $w_k \to w^*$ (수렴 시)
```

<br/>

### Convergence

```ad-important
title: Theorem - Robbins-Monro Convergence

다음 조건 만족 시 $w_k \xrightarrow{\text{a.s.}} w^*$:

**(a)** $0 < c_1 \leq \nabla_w g(w) \leq c_2$ for all $w$

**(b)** $\displaystyle\sum_{k=1}^{\infty} \alpha_k = \infty$ and $\displaystyle\sum_{k=1}^{\infty} \alpha_k^2 < \infty$

**(c)** $\mathbb{E}[\eta_k | H_k] = 0$ and $\mathbb{E}[\eta_k^2 | H_k] < \infty$

where $H_k = \{w_k, w_{k-1}, \ldots\}$
```

```ad-info
title: Note - Convergence Conditions

**(a) Bounded Gradient**: $0 < c_1 \leq \nabla_w g(w) \leq c_2$

- $\nabla_w g(w) > 0$: $g(w)$가 ==단조 증가== → ==유일한 근 존재== 보장
- $\nabla_w g(w) \leq c_2$: gradient가 ==상한 bounded==
- **Optimization 응용**: 단조 증가 $g$는 ==$J(w)$ convex==에 해당

**위반 시**:
- $\nabla_w g(w) \to 0$: 근 근처에서 ==수렴 속도 극도로 저하==
- $\nabla_w g(w) \to \infty$: 업데이트가 불안정, ==발산 가능==
- $\nabla_w g(w) < 0$ 구간 존재: ==다중 근== 발생

---

**(b) Step Size**: [[#Step Size Conditions]] 참조

---

**(c) Noise Conditions**: $\mathbb{E}[\eta_k | H_k] = 0$, $\mathbb{E}[\eta_k^2 | H_k] < \infty$

==Mild condition== — Gaussian일 필요 없음

**Unbiased 위반 시** ($\mathbb{E}[\eta_k | H_k] = b \neq 0$):

실제로 풀고 있는 방정식이 $g(w) + b = 0$, 즉 ==$w^*$가 아닌 다른 점==으로 수렴
```

```ad-important
title: Proof - RM Theorem using Dvoretzky
collapse: true

**Step 1**: RM 알고리즘 변환

$$w_{k+1} = w_k - a_k [g(w_k) + \eta_k]$$

$$w_{k+1} - w^* = w_k - w^* - a_k [g(w_k) - g(w^*) + \eta_k]$$

---

**Step 2**: Mean Value Theorem 적용

$g(w_k) - g(w^*) = \nabla_w g(w'_k) (w_k - w^*)$ where $w'_k \in [w_k, w^*]$

$\Delta_k \doteq w_k - w^*$로 정의:

$$\begin{aligned}
\Delta_{k+1} &= [1 - a_k \nabla_w g(w'_k)] \Delta_k + a_k (-\eta_k) \\
&= (1 - \alpha_k) \Delta_k + a_k (-\eta_k)
\end{aligned}$$

where $\alpha_k = a_k \nabla_w g(w'_k)$

→ ==[[Dvoretzky's Theorem]] 형태와 일치==

---

**Step 3**: 조건 검증

$0 < c_1 \leq \nabla_w g(w) \leq c_2$이고 $\sum a_k = \infty$, $\sum a_k^2 < \infty$이므로:

$$\sum \alpha_k = \infty, \quad \sum \alpha_k^2 < \infty$$

→ Dvoretzky 정리에 의해 $\Delta_k \to 0$ a.s. $\square$
```

```ad-example
title: Example - RM Convergence ($g(w) = \tanh(w-1)$)
collapse: true

![[Pasted image 20260106070206.png|500]]

**설정**:
- $g(w) = \tanh(w - 1)$, true root $w^* = 1$
- $w_1 = 3$, $\alpha_k = 1/k$
- Noise 없음: $\eta_k \equiv 0$

**수렴 직관**:

| 현재 위치 | $g(w_k)$ | 결과 |
|:---|:---|:---|
| $w_k > w^*$ | $> 0$ | $w^* < w_{k+1} < w_k$ |
| $w_k < w^*$ | $< 0$ | $w^* > w_{k+1} > w_k$ |

→ 두 경우 모두 ==$w_{k+1}$이 $w_k$보다 $w^*$에 더 가까움==
```

```ad-example
title: Example - Root Finding with Noise ($g(w) = w^3 - 5$)
collapse: true

![[Pasted image 20260106055150.png|500]]

**설정**:
- $g(w) = w^3 - 5$, true root $w^* = 5^{1/3} \approx 1.71$
- Noisy observation: $\tilde{g}(w) = g(w) + \eta$, $\eta \sim N(0, 1)$
- $w_1 = 0$, $\alpha_k = 1/k$

**결과**: Noise에도 불구하고 $w_k \to w^*$ 수렴

**참고**: $g(w) = w^3 - 5$는 조건 (a)의 $\nabla_w g(w) \leq c_2$ 불만족 (unbounded gradient)
- 조건 불만족 시: ==임의의 초기값==에서 수렴 보장 불가
- 하지만 ==적절한 초기값==에서는 수렴 가능
```

<br/><br/>

## Step Size Conditions

$$\sum_{k=1}^{\infty} \alpha_k = \infty, \quad \sum_{k=1}^{\infty} \alpha_k^2 < \infty$$

| 조건 | 의미 | 위반 시 |
|:---|:---|:---|
| $\sum \alpha_k = \infty$ | ==도달 가능성== | 초기값이 멀면 $w^*$에 도달 불가 |
| $\sum \alpha_k^2 < \infty$ | ==Fluctuation 감소== | 수렴 후에도 계속 진동 |

<br/>

**$\sum \alpha_k = \infty$ (도달 가능성)**:

업데이트 합산: $w_1 - w_\infty = \sum_{k=1}^{\infty} \alpha_k \tilde{g}(w_k, \eta_k)$

$\sum \alpha_k < \infty$이면 $|w_1 - w_\infty| \leq b$ (유한 상한) → 초기값이 $w^*$에서 $b$보다 멀면 ==도달 불가==

<br/>

**$\sum \alpha_k^2 < \infty$ (Fluctuation 감소)**:

$\sum \alpha_k^2 < \infty$ → $\alpha_k \to 0$ → $w_{k+1} - w_k = -\alpha_k \tilde{g}(w_k, \eta_k) \to 0$

→ $k \to \infty$에서 ==수렴 후 fluctuation 감소==

```ad-example
title: Example - Step Size Sequences
collapse: true

==어떤 step size가 두 조건을 동시에 만족하는가?==

| Step Size | $\sum \alpha_k$ | $\sum \alpha_k^2$ | 조건 |
|:---|:---|:---|:---|
| $\alpha_k = 1/k$ | $\infty$ | $\pi^2/6$ | ==만족== |
| $\alpha_k = 1/(k+c)$ | $\infty$ | $< \infty$ | ==만족== |
| $\alpha_k = c_k/k$ ($c_k$ bounded) | $\infty$ | $< \infty$ | ==만족== |
| $\alpha_k = \alpha$ (상수) | $\infty$ | $\infty$ | ==불만족== |

---

**Harmonic series** (조화급수):

$$\sum_{k=1}^{\infty} \frac{1}{k} = \infty$$

각 항 $1/k \to 0$이지만, 합은 ==발산==. Euler-Mascheroni constant: $\lim_{n \to \infty} \left( \sum_{k=1}^{n} \frac{1}{k} - \ln n \right) = \kappa \approx 0.577$

**Basel problem**:

$$\sum_{k=1}^{\infty} \frac{1}{k^2} = \frac{\pi^2}{6} < \infty$$
```

```ad-warning
title: Note - Constant Step Size

상수 step size $\alpha_k = \alpha$는 $\sum \alpha_k^2 = \infty$로 이론적 조건 불만족

그러나 ==non-stationary 환경==에서 실용적으로 널리 사용:

| | Decaying $\alpha_k$ | Constant $\alpha$ |
|:---|:---|:---|
| **목표** | 고정된 $w^*$로 정확한 수렴 | ==Tracking== (이동하는 목표 추적) |
| **환경 변화** | 업데이트가 작아져 ==적응 불가== | ==적응 가능== |
| **결과** | $w^*$에 수렴 | $w^*$ 근방에서 진동 |

**RL에서 non-stationary 상황**:
- 정책이 계속 바뀜 → 목표 $w^*$가 ==계속 이동== (moving target)
- Decaying $\alpha_k = 1/k$: 시간이 지나면 업데이트가 너무 작아져 변화 반영 불가

→ 이론적 수렴 보장 포기, ==변화에 대한 적응성== 택하는 trade-off
```

<br/><br/>

## Related Concepts

- [[Dvoretzky's Theorem]]: RM보다 일반적인 SA 수렴 정리
- [[Stochastic Gradient Descent]]: RM의 특수 형태 (optimization)
- [[Temporal Difference Learning]]: RM의 특수 형태 (RL)
- [[Q-Learning]]: Dvoretzky 기반 수렴 증명 (RL)
- [[Monte Carlo Methods]]: Batch estimation (SA의 non-incremental 대응)
- [[Law of Large Numbers]]: Mean estimation 수렴의 통계적 근거
