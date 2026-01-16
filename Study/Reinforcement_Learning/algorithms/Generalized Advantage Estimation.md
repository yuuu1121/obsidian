---
date: 2026-01-14
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - GAE
  - Generalized Advantage Estimator
keywords:
  - GAE
  - Generalized Advantage Estimation
  - Advantage Function
  - TD(λ)
  - Bias-Variance Tradeoff
related notes:
  - "[[Actor-Critic]]"
  - "[[Advantage Actor-Critic]]"
  - "[[Temporal Difference Learning]]"
  - "[[MC vs TD]]"
  - "[[Bootstrapping]]"
  - "[[Policy Gradient]]"
reference:
  - title: "High-Dimensional Continuous Control Using Generalized Advantage Estimation"
    authors: [John Schulman, Philipp Moritz, Sergey Levine, Michael I. Jordan, Pieter Abbeel]
    year: 2016
    journal: "ICLR 2016"
    doi: "arXiv:1506.02438"
author: John Schulman, Philipp Moritz, Sergey Levine, Michael I. Jordan, Pieter Abbeel
url:
  - https://arxiv.org/abs/1506.02438
---

# Generalized Advantage Estimation

```ad-note
title: Summary
collapse: true

- ==TD residual의 지수 가중 합==으로 advantage를 추정하는 기법
- ==$\lambda \in [0,1]$로 bias-variance 트레이드오프 조절== — TD(λ)의 advantage 버전
- ==$\lambda=0$: low variance, high bias== / ==$\lambda=1$: high variance, low bias==
- PPO, TRPO 등 현대 policy gradient 알고리즘의 ==핵심 구성 요소==
```

## Definition

<!-- Section 3 from GAE paper (arXiv:1506.02438) -->

==TD residual $\delta_t$의 지수 가중 합==으로 [[Advantage Actor-Critic#Advantage Function|advantage function]] $A^\pi(s,a)$를 추정하는 기법

$$\hat{A}_t^{GAE(\gamma,\lambda)} = \sum_{l=0}^{\infty} (\gamma\lambda)^l \delta_{t+l}$$

- $\delta_t = r_t + \gamma v(s_{t+1}) - v(s_t)$: TD residual (1-step TD error)
- $\gamma$: discount factor
- $\lambda \in [0,1]$: ==bias-variance 조절 파라미터==
- $v(s)$: 학습된 value function (baseline)

<br/>

### Motivation

[[Policy Gradient]] 방법의 ==높은 variance 문제==를 해결하기 위해 제안

- **문제**: Policy gradient 추정의 variance가 크면 학습 불안정
- **해결**: Value function을 baseline으로 사용하여 variance 감소
- **트레이드오프**: Bias를 도입하되 ==조절 가능하게== 설계

<br/><br/>

## Bias-Variance Tradeoff

<!-- Section 3 from GAE paper -->

$\lambda$ 값에 따른 GAE의 특성 변화:

| $\lambda$ | 수식 | Bias | Variance | 특성 |
|:---|:---|:---|:---|:---|
| $\lambda = 0$ | $\hat{A}_t = \delta_t$ | ==높음== | ==낮음== | TD(0) 스타일 |
| $\lambda = 1$ | $\hat{A}_t = \sum_{l=0}^{\infty} \gamma^l \delta_{t+l}$ | ==낮음== | ==높음== | MC 스타일 |
| $0 < \lambda < 1$ | 지수 가중 평균 | 중간 | 중간 | ==실용적 선택== |

<br/>

### Extreme Cases

**$\lambda = 0$ (TD(0) 스타일)**:

$$\hat{A}_t^{GAE(\gamma,0)} = \delta_t = r_t + \gamma v(s_{t+1}) - v(s_t)$$

- ==1-step만 사용== → low variance
- Value function 오차가 직접 bias로 전파

**$\lambda = 1$ (MC 스타일)**:

$$\hat{A}_t^{GAE(\gamma,1)} = \sum_{l=0}^{\infty} \gamma^l \delta_{t+l} = \sum_{l=0}^{\infty} \gamma^l r_{t+l} - v(s_t)$$

- ==전체 trajectory 사용== → high variance
- Value function이 정확하면 ==unbiased==

```ad-info
title: Note - Practical Choice

PPO 등 실제 구현에서는 ==$\lambda = 0.95 \sim 0.97$== 사용

- $\gamma = 0.99$, $\lambda = 0.95$가 일반적인 기본값
- 환경 특성에 따라 튜닝 필요
```

<br/><br/>

## Connection to TD(λ)

<!-- Section 4 from GAE paper -->

GAE는 ==TD(λ)의 advantage 버전==으로 해석 가능

| 개념 | TD(λ) | GAE |
|:---|:---|:---|
| **추정 대상** | Value $v(s)$ | [[Advantage Actor-Critic#Advantage Function\|Advantage]] $A(s,a)$ |
| **기본 단위** | TD error $\delta_t$ | TD residual $\delta_t$ |
| **가중치** | $(\gamma\lambda)^l$ | $(\gamma\lambda)^l$ |
| **용도** | Value function 학습 | [[Policy Gradient]] variance 감소 |

<br/>

### k-step Advantage Estimator

GAE는 ==k-step advantage estimator들의 지수 가중 평균==:

$$\hat{A}_t^{(k)} = \sum_{l=0}^{k-1} \gamma^l \delta_{t+l} = -v(s_t) + r_t + \gamma r_{t+1} + \dots + \gamma^{k-1} r_{t+k-1} + \gamma^k v(s_{t+k})$$

$$\hat{A}_t^{GAE} = (1-\lambda)(\hat{A}_t^{(1)} + \lambda \hat{A}_t^{(2)} + \lambda^2 \hat{A}_t^{(3)} + \dots)$$

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - GAE Computation

**Input**: Trajectory $(s_0, a_0, r_0, s_1, \dots, s_T)$, value function $v$, $\gamma$, $\lambda$

**For** $t = T-1, T-2, \dots, 0$: (역순 계산)
- $\delta_t = r_t + \gamma v(s_{t+1}) - v(s_t)$
- $\hat{A}_t = \delta_t + \gamma\lambda \hat{A}_{t+1}$ (재귀적 계산)

**Output**: Advantage estimates $\{\hat{A}_0, \hat{A}_1, \dots, \hat{A}_{T-1}\}$
```

```ad-info
title: Note - Efficient Computation

==역순 재귀==로 $O(T)$ 시간에 계산 가능

$$\hat{A}_t = \delta_t + \gamma\lambda \hat{A}_{t+1}$$

- $\hat{A}_{T-1} = \delta_{T-1}$ (초기값)
- 뒤에서 앞으로 누적하며 계산
```

<br/><br/>

## Applications

GAE를 사용하는 주요 알고리즘:

- **PPO (Proximal Policy Optimization)**: 기본 advantage estimator로 GAE 사용
- **TRPO (Trust Region Policy Optimization)**: GAE 논문에서 함께 제안
- **A3C/A2C**: Asynchronous/Advantage Actor-Critic에서 사용

<br/><br/>

## Related Concepts

- [[Actor-Critic]]: GAE가 Critic의 출력을 활용하여 advantage 추정
- [[Advantage Actor-Critic]]: Advantage 기반 Actor-Critic — GAE로 advantage 계산
- [[Temporal Difference Learning]]: TD residual $\delta_t$의 이론적 기반
- [[MC vs TD]]: $\lambda$로 MC와 TD 사이를 보간하는 GAE의 핵심 아이디어
- [[Bootstrapping]]: TD 방식의 value 추정 — bias 발생 원인
- [[Policy Gradient]]: GAE가 variance를 감소시키는 대상
