---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - n-step TD
  - Multi-step Sarsa
keywords:
  - n-step Sarsa
  - n-step Return
  - Bias Variance Tradeoff
  - TD
  - Monte Carlo
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 7
  - David Silver's RL Course
author:
url:
---

# n-step Sarsa

```ad-note
title: Summary
collapse: true

- ==n-step Sarsa: [[Sarsa]] ($n=1$)와 [[Monte Carlo Methods|MC]] ($n=\infty$) 사이의 일반화==
- ==n-step Return: n개의 실제 보상 + bootstrapping으로 bias-variance 조절==
- ==n이 작으면 High Bias / Low Variance, n이 크면 Low Bias / High Variance==
- ==[[Stochastic Approximation]] 수렴 조건 + 모든 $(s,a)$ 무한 방문 시 $q_\pi$로 수렴==
```

## Definition

시간 $t$부터 ==$n$ 스텝 동안의 실제 보상==을 수집하고, ==$n+1$번째 상태에서 bootstrapping==하여 action value를 업데이트하는 TD Control

$$q_{t+n}(s_t, a_t) = q_{t+n-1}(s_t, a_t) + \alpha \delta_t^{(n)}$$

- [[Sarsa]] ($n=1$): 1개 보상 + 즉시 [[Bootstrapping|bootstrapping]] → ==High Bias, Low Variance==
- [[Monte Carlo Methods|MC]] ($n=\infty$): 전체 보상, bootstrapping 없음 → ==Low Bias, High Variance==
- $n$을 조절하여 ==bias-variance trade-off 제어==

<br/><br/>

## n-step Return

[[Return]] $G_t$는 다양한 형태로 분해 가능하며, 모든 분해는 ==동일한 return==을 나타냄:

$$\begin{align*}
\text{Sarsa} \leftarrow \quad & G_t^{(1)} = R_{t+1} + \gamma q_\pi(S_{t+1}, A_{t+1}) \\[0.3em]
& G_t^{(2)} = R_{t+1} + \gamma R_{t+2} + \gamma^2 q_\pi(S_{t+2}, A_{t+2}) \\[0.3em]
& \vdots \\[0.3em]
\text{n-step Sarsa} \leftarrow \quad & G_t^{(n)} = \sum_{i=0}^{n-1} \gamma^i R_{t+i+1} + \gamma^n q_\pi(S_{t+n}, A_{t+n}) \\[0.3em]
& \vdots \\[0.3em]
\text{MC} \leftarrow \quad & G_t^{(\infty)} = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots
\end{align*}$$

```ad-warning
title: Note - $G_t = G_t^{(1)} = G_t^{(2)} = \cdots = G_t^{(\infty)}$

위첨자 $(n)$은 ==어디까지 실제 보상을 합하고, 어디서부터 추정치로 대체할지==를 나타냄:
- $G_t^{(1)}$: 1개 실제 보상 + $t+1$부터 추정치
- $G_t^{(n)}$: $n$개 실제 보상 + $t+n$부터 추정치
- $G_t^{(\infty)}$: 전체 실제 보상, 추정치 없음

**이론적으로** (true $q_\pi$ 사용 시): 모든 $n$에 대해 $\mathbb{E}[G_t^{(n)}] = q_\pi(s,a)$로 ==기댓값 동일==

**실제로** (추정치 $q$ 사용 시): $q \neq q_\pi$이므로 ==$n$에 따라 다른 값== → bias-variance trade-off
```

```ad-info
title: Note - Bias-Variance Trade-off

| n 값 | Bias | Variance | 특성 |
|:---|:---|:---|:---|
| **$n=1$ (Sarsa)** | ==높음== | 낮음 | 빠른 업데이트, 초기 불안정 |
| **중간 n** | 중간 | 중간 | ==가장 빠른 수렴== |
| **$n=\infty$ (MC)** | 없음 | ==높음== | 느린 업데이트, fluctuation |

- **Variance**: n-step return에 포함된 ==확률 변수의 수==에 비례
- **Bias**: ==bootstrapping 추정치==의 부정확성에서 발생
- 일반적으로 ==$n=4 \sim 8$==이 좋은 성능, 최적 $n$은 문제에 따라 실험적으로 결정
```

<br/><br/>

## Components

n-step Sarsa가 해결하는 [[Bellman Equation#Action Value Form|Action Value Bellman Equation]]:

$$q_\pi(s,a) = \mathbb{E}[R_{t+1} + \gamma R_{t+2} + \cdots + \gamma^{n-1} R_{t+n} + \gamma^n q_\pi(S_{t+n}, A_{t+n})|s,a]$$

[[Stochastic Approximation]]으로 풀면 Update Rule 유도

<br/>

### TD Target

$$g_t^{(n)} = \underbrace{r_{t+1} + \gamma r_{t+2} + \cdots + \gamma^{n-1} r_{t+n}}_{\text{n actual rewards}} + \underbrace{\gamma^n q(s_{t+n}, a_{t+n})}_{\text{bootstrapping}}$$

- ==$n$개의 실제 보상==을 합산 ([[Monte Carlo Methods|MC]]처럼)
- ==$t+n$ 시점의 추정치==로 이후 return 대체 ([[Temporal Difference Learning|TD]]처럼)
- $(r_{t+n}, s_{t+n}, a_{t+n})$은 시간 $t$에서 아직 수집되지 않음 → ==시간 $t+n$에서 업데이트==

<br/>

### TD Error

$$\delta_t^{(n)} = g_t^{(n)} - q_{t+n-1}(s_t, a_t)$$

- n-step TD Target과 현재 추정치의 차이
- 학습 방향과 크기 결정

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - n-step Sarsa

**입력**: 학습률 $\alpha > 0$, step 수 $n \geq 1$

**초기화**: $q_0(s,a)$ 임의 설정

**For** each episode:
- 초기 상태 $s_0$에서 $a_0 \sim \pi(s_0)$ 생성
- **For** $t = 0, 1, 2, \ldots$:
  - $s_t$가 종료 상태가 아니면 $(r_{t+1}, s_{t+1}, a_{t+1})$ 수집
  - **n-step Return 계산**:
    $$g_t^{(n)} = r_{t+1} + \gamma r_{t+2} + \cdots + \gamma^{n-1} r_{t+n} + \gamma^n q(s_{t+n}, a_{t+n})$$
  - **Q-value 업데이트** (시간 $t+n$에서 $(s_t, a_t)$ 업데이트):
    $$q_{t+n}(s_t, a_t) = q_{t+n-1}(s_t, a_t) + \alpha[g_t^{(n)} - q_{t+n-1}(s_t, a_t)]$$
  - **정책 개선** ($\epsilon$-greedy)

**출력**: 학습된 정책
```

```ad-info
title: Note - Implementation

**업데이트 시점**: 시간 $t$에서 $(s_t, a_t)$의 Q값을 업데이트하려면 ==시간 $t+n$까지 기다려야 함==
- $(r_{t+1}, s_{t+1}, a_{t+1}, \ldots, r_{t+n}, s_{t+n}, a_{t+n})$ 필요
- 에피소드 종료 시 마지막 n-1개 상태-행동 쌍 별도 처리 필요
- $n=1$: 매 스텝 업데이트 가능 / $n=\infty$: ==에피소드가 끝나야== $g_t$ 계산 가능

**Policy Evaluation vs Control**: 순수 n-step Sarsa는 ==policy evaluation==으로 $q_\pi$ 추정. 위 Algorithm은 $\epsilon$-greedy를 포함한 ==control 버전==
```

<br/><br/>

## Convergence

n-step Sarsa는 [[Stochastic Approximation]] 형태로, 다른 TD 알고리즘과 동일한 수렴 조건 적용

```ad-important
title: Theorem - n-step Sarsa Convergence

정책 $\pi$가 주어졌을 때, n-step Sarsa 알고리즘에 의해 $q_t(s,a)$는 다음 조건 하에서 ==모든 $(s,a)$에 대해 $q_\pi(s,a)$로 almost surely 수렴==:

$$\sum_{t} \alpha_t(s,a) = \infty, \quad \sum_{t} \alpha_t^2(s,a) < \infty \quad \text{for all } (s,a)$$

- $\sum \alpha_t(s,a) = \infty$: ==모든 상태-행동 쌍이 무한 번 방문==되어야 함
- exploratory policy ($\epsilon$-greedy 등) 필요
```

<br/><br/>

## Related Concepts

- [[Sarsa]]: $n=1$인 특수 케이스, On-Policy TD Control
- [[Monte Carlo Methods]]: $n=\infty$인 특수 케이스, 실제 return 사용
- [[Temporal Difference Learning]]: n-step의 기반 알고리즘
- [[Expected Sarsa]]: 분산 감소를 위한 기댓값 사용
- [[Q-Learning]]: Off-Policy TD Control
- [[Stochastic Approximation]]: 수렴의 이론적 기반
- [[Bellman Equation]]: n-step Sarsa가 해결하는 방정식

