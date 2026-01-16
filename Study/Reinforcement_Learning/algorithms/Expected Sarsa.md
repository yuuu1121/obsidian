---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Expected SARSA
keywords:
  - Expected Sarsa
  - TD Control
  - Variance Reduction
  - Expectation
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 7
author:
url:
---

# Expected Sarsa

```ad-note
title: Summary
collapse: true

- ==Expected Sarsa: TD Target에서 $a_{t+1}$ 샘플 대신 기댓값 사용==
- ==TD Target: $\bar{q}_t = r_{t+1} + \gamma \mathbb{E}[q_t(s_{t+1}, A)] = r_{t+1} + \gamma v_t(s_{t+1})$==
- ==[[Sarsa]]보다 분산 감소, 계산 비용 $O(|\mathcal{A}|)$ 증가==
- ==$\pi$가 greedy이면 [[Q-Learning]]과 동일==
```

## Definition

[[Sarsa]]의 TD Target에서 ==다음 행동 $a_{t+1}$의 샘플 대신 기댓값을 사용==하여 분산을 줄인 TD Control

$$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) + \alpha_t \delta_t$$

- [[Sarsa]]: $a_{t+1} \sim \pi(s_{t+1})$ 샘플 사용 → ==High Variance==
- Expected Sarsa: $\mathbb{E}[q_t(s_{t+1}, A)]$ 기댓값 사용 → ==Low Variance==
- 정책 $\pi$가 greedy이면 ==[[Q-Learning]]과 동일==

```ad-info
title: Note - Expected Value as State Value

$$\mathbb{E}[q_t(s_{t+1}, A)] = \sum_a \pi_t(a|s_{t+1}) q_t(s_{t+1}, a) \triangleq v_t(s_{t+1})$$

정책 $\pi_t$ 하에서 $q_t(s_{t+1}, a)$의 기댓값은 ==state value 추정치 $v_t(s_{t+1})$와 동일==
```

<br/><br/>

## Components

Expected Sarsa가 해결하는 [[Bellman Equation]]:

$$q_\pi(s, a) = \mathbb{E}\left[ R_{t+1} + \gamma \mathbb{E}[q_\pi(S_{t+1}, A_{t+1}) | S_{t+1}] \mid S_t = s, A_t = a \right]$$

```ad-important
title: Proof - Bellman Equation Equivalence
collapse: true

내부 기댓값 전개:

$$\mathbb{E}[q_\pi(S_{t+1}, A_{t+1}) | S_{t+1}] = \sum_{a'} q_\pi(S_{t+1}, a') \pi(a' | S_{t+1}) = v_\pi(S_{t+1})$$

대입하면:

$$q_\pi(s, a) = \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s, A_t = a]$$

→ ==[[Bellman Equation]]의 또 다른 형태== $\square$
```

<br/>

### TD Target

$$\bar{q}_t = r_{t+1} + \gamma \mathbb{E}[q_t(s_{t+1}, A)] = r_{t+1} + \gamma \sum_a \pi_t(a|s_{t+1}) q_t(s_{t+1}, a)$$

| 알고리즘 | TD Target $\bar{q}_t$ | 특징 |
|:---|:---|:---|
| **[[Sarsa]]** | $r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1})$ | 샘플 $a_{t+1}$ 사용 |
| **Expected Sarsa** | $r_{t+1} + \gamma \mathbb{E}[q_t(s_{t+1}, A)]$ | ==기댓값 사용== |
| **[[Q-Learning]]** | $r_{t+1} + \gamma \max_a q_t(s_{t+1}, a)$ | 최대값 사용 |

```ad-info
title: Note - Relationship with Q-Learning

$\pi$가 ==[[Greedy Policy|greedy policy]]==일 때:

$$\sum_a \pi(a|s_{t+1}) q_t(s_{t+1}, a) = \max_a q_t(s_{t+1}, a)$$

→ ==Expected Sarsa = Q-Learning==
```

<br/>

### TD Error

$$\delta_t = q_t(s_t, a_t) - (r_{t+1} + \gamma \mathbb{E}[q_t(s_{t+1}, A)])$$

- TD Target과 현재 추정치의 차이
- 학습 방향과 크기 결정

```ad-info
title: Note - Variance Reduction

| | Sarsa | Expected Sarsa |
|:---|:---|:---|
| **확률 변수** | $R_{t+1}, S_{t+1}, A_{t+1}$ | $R_{t+1}, S_{t+1}$ |
| **Variance** | ==높음== | ==낮음== |
| **계산 비용** | $O(1)$ | $O(\lvert\mathcal{A}\rvert)$ |

- ==$a_{t+1}$을 확률 변수에서 제거==하여 분산 감소
- 기댓값 계산을 위해 ==모든 행동에 대해 합산== 필요
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Expected Sarsa

**입력**: 학습률 $\alpha > 0$, 탐색 파라미터 $\epsilon \in (0,1)$

**초기화**: $q_0(s,a)$ 임의 설정, $q_0$로부터 $\epsilon$-greedy 정책 $\pi_0$ 유도

**For** each episode:
- 초기 상태 $s_0$ 관측
- **While** $s_t$가 종료 상태가 아닐 때:
  - $a_t \sim \pi_t(s_t)$ 생성, $(r_{t+1}, s_{t+1})$ 관측
  - **기댓값 계산**:
    $$\mathbb{E}[q_t(s_{t+1}, A)] = \sum_a \pi_t(a|s_{t+1}) q_t(s_{t+1}, a)$$
  - **Q-value 업데이트**:
    $$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha[q_t(s_t, a_t) - (r_{t+1} + \gamma \mathbb{E}[q_t(s_{t+1}, A)])]$$
  - **미방문 상태-행동 유지**:
    $$q_{t+1}(s, a) = q_t(s, a) \quad \text{for all } (s, a) \neq (s_t, a_t)$$
  - **[[Policy Iteration#Policy Improvement|Policy 업데이트]]** ($\epsilon$-greedy)

**출력**: 학습된 정책
```

<br/><br/>

## Convergence

Expected Sarsa는 [[Stochastic Approximation]] 형태로, [[Sarsa]]와 동일한 수렴 조건 적용

```ad-important
title: Theorem - Expected Sarsa Convergence

정책 $\pi$가 주어졌을 때, Expected Sarsa 알고리즘에 의해 $q_t(s,a)$는 다음 조건 하에서 ==모든 $(s,a)$에 대해 $q_\pi(s,a)$로 almost surely 수렴==:

$$\sum_{t} \alpha_t(s,a) = \infty, \quad \sum_{t} \alpha_t^2(s,a) < \infty \quad \text{for all } (s,a)$$

- $\sum \alpha_t(s,a) = \infty$: ==모든 상태-행동 쌍이 무한 번 방문==되어야 함
- exploratory policy ($\epsilon$-greedy 등) 필요
```

```ad-info
title: Note - Comparison with Sarsa Convergence

수렴 조건은 동일하나, Expected Sarsa는 ==분산 감소로 인해 더 빠르고 안정적으로 수렴==하는 경향

- Sarsa: $a_{t+1}$ 샘플의 확률성으로 인한 fluctuation
- Expected Sarsa: 기댓값 사용으로 fluctuation 감소
```

<br/><br/>

## Related Concepts

- [[Sarsa]]: Expected Sarsa의 샘플 기반 버전
- [[Q-Learning]]: $\pi$가 greedy일 때 동일
- [[Temporal Difference Learning]]: TD 알고리즘의 기반
- [[n-step Sarsa]]: MC↔TD 스펙트럼의 일반화
- [[Bellman Equation]]: Expected Sarsa가 해결하는 방정식
- [[Stochastic Approximation]]: 수렴의 이론적 기반


