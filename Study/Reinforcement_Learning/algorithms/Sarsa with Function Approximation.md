---
date: 2026-01-11
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Sarsa with FA
  - Sarsa-Linear
  - 함수 근사 Sarsa
keywords:
  - TD Control
  - Function Approximation
  - Sarsa
  - On-Policy
  - Linear FA
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
    chapter: 10, 11
author:
url:
---

# Sarsa with Function Approximation

```ad-note
title: Summary
collapse: true

- ==[[Sarsa]]의 action value를 FA로 근사==: $\hat{q}(s,a,w) = \phi^T(s,a)w$
- ==On-Policy==: 행동 정책이 선택한 $a_{t+1}$ 사용 → Linear FA에서 ==수렴 보장==
- ==GPI 구조==: 매 스텝 value estimation과 policy improvement 교대 수행
```

## Definition

[[Sarsa]]의 action value를 ==파라미터화된 함수로 근사==:

$$\hat{q}(s, a, w) \approx q_\pi(s, a)$$

- ==On-Policy==: 실제 정책이 선택한 $a_{t+1}$을 TD target에 사용
- [[Value Function Approximation|State value FA]]와 달리 ==Control 가능== (정책 개선에 직접 활용)

```ad-info
title: Note - State Value vs Action Value FA

| 측면 | State Value FA | Action Value FA |
|:---|:---|:---|
| **근사 대상** | $\hat{v}(s,w) \approx v_\pi(s)$ | $\hat{q}(s,a,w) \approx q_\pi(s,a)$ |
| **Feature** | $\phi(s)$ | ==$\phi(s,a)$== |
| **용도** | Policy evaluation | ==Control== |
```

<br/><br/>

## Linear Function Approximation

$$\hat{q}(s, a, w) = \phi^T(s, a) w = \sum_{i=1}^{m} \phi_i(s, a) w_i$$

- $\phi(s, a) \in \mathbb{R}^m$: 상태-행동 쌍의 ==feature vector==
- $\nabla_w \hat{q}(s, a, w) = \phi(s, a)$

```ad-info
title: Note - Feature Vector Construction

State feature $\phi(s) \in \mathbb{R}^d$를 action value용 $\phi(s,a) \in \mathbb{R}^m$로 확장하는 방법:

**One-hot action encoding** (가장 일반적):

$$\phi(s,a) = \phi(s) \otimes e_a = [\mathbf{0}, \ldots, \underbrace{\phi(s)}_{\text{action } a}, \ldots, \mathbf{0}]^T \in \mathbb{R}^{d \cdot |\mathcal{A}|}$$

- $e_a$: 행동 $a$의 one-hot vector
- 결과: 각 행동마다 ==독립적인 파라미터 세트== 사용
- Feature 차원: $m = d \cdot |\mathcal{A}|$

**직접 설계**: 상태와 행동 정보를 수동으로 결합한 feature 설계
```

<br/><br/>

## Components

### TD Target

$$\bar{q}_t = r_{t+1} + \gamma \hat{q}(s_{t+1}, a_{t+1}, w_t)$$

- 즉각 보상 + 할인된 다음 상태-행동의 추정 가치
- ==실제 정책이 선택한 $a_{t+1}$ 사용== (On-Policy 특성)

<br/>

### TD Error

$$\delta_t = \hat{q}(s_t, a_t, w_t) - (r_{t+1} + \gamma \hat{q}(s_{t+1}, a_{t+1}, w_t))$$

- 현재 추정치와 TD Target의 차이
- ==양수==: 현재 추정이 과대 → $w$ 감소 방향 / ==음수==: 과소 → $w$ 증가 방향

<br/>

### Update Rule

$$w_{t+1} = w_t - \alpha_t \delta_t \phi(s_t, a_t)$$

- [[TD-Linear]]의 state value 업데이트와 동일한 형태
- Linear FA에서 $\nabla_w \hat{q}(s,a,w) = \phi(s,a)$이므로 ==Semi-gradient descent==

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Sarsa with FA

**입력**: Feature vector $\phi(s,a)$, 초기 파라미터 $w_0$, step size $\alpha$, 탐색률 $\varepsilon$

**초기화**: $w_0$로부터 $\varepsilon$-greedy 정책 $\pi_0$ 유도

**For** 각 에피소드:
- 초기 상태 $s_0$ 관측, $a_0 \sim \pi_0(s_0)$ 선택
- **While** $s_t$가 종료 상태가 아닐 때:
  - **경험 샘플 수집**: $(s_t, a_t)$에서 $(r_{t+1}, s_{t+1})$ 관측, $a_{t+1} \sim \pi_t(s_{t+1})$ 선택
  - **Q-value 업데이트**:
    $$w_{t+1} = w_t - \alpha \delta_t \phi(s_t, a_t)$$
    where $\delta_t = \hat{q}(s_t, a_t, w_t) - (r_{t+1} + \gamma \hat{q}(s_{t+1}, a_{t+1}, w_t))$
  - **정책 업데이트** ($\varepsilon$-greedy):
    $$\pi_{t+1}(s) = \varepsilon\text{-greedy}(\hat{q}(\cdot, \cdot, w_{t+1}))$$
  - $s_t \leftarrow s_{t+1}$, $a_t \leftarrow a_{t+1}$

**출력**: 학습된 파라미터 $w$, 근사 정책 $\pi$
```

```ad-info
title: Note - GPI Structure

==단 한 번의 업데이트 후 바로 Policy Improvement==로 전환하는 [[Policy Iteration#Generalized Policy Iteration|GPI]] 구조:
- Value estimation과 policy improvement를 ==매 스텝 교대 수행==
- [[Truncated Policy Iteration]]과 유사
```

```ad-example
title: Example - Grid World with Sarsa FA
collapse: true

![[Pasted image 20260111074312.png|500]]

**설정**: 5×5 Grid World, Fourier feature (order 5), $\gamma = 0.9$, $\varepsilon = 0.1$, $\alpha = 0.001$

**결과**: Linear FA로 최적 경로 학습 성공
```

```ad-warning
title: Note - Exploration Limitation

위 알고리즘은 ==특정 시작 상태에서 목표까지의 경로==에 초점 — 모든 상태의 최적 정책을 찾으려면 다양한 시작 상태에서 학습 필요 (Exploring Starts)
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - On-Policy Convergence

On-policy Sarsa with Linear FA는 다음 조건 하에서 수렴:

- 정책이 GLIE (Greedy in the Limit with Infinite Exploration)
- Step size: $\sum_t \alpha_t = \infty$, $\sum_t \alpha_t^2 < \infty$
- Feature vectors가 linearly independent

수렴점은 ==optimal policy의 근사==에 해당
```

On-policy이므로 behavior policy와 target policy가 같아 ==안정적== — [[Deep Q-Learning]]의 Deadly Triad 문제 없음

<br/><br/>

## Related Concepts

- [[Temporal Difference Learning]]: TD 기반 학습의 기초
- [[Sarsa]]: Tabular Sarsa (FA 적용 전)
- [[Value Function Approximation]]: FA의 기본 개념
- [[TD-Linear]]: State value 버전의 Linear FA
- [[Truncated Policy Iteration]]: GPI 구조의 이론적 기반
- [[Deep Q-Learning]]: Off-policy Q-Learning with FA (Neural Network + 안정화 기법)
- [[Q-Learning]]: Tabular Q-Learning — Off-policy TD Control

