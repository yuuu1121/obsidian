---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Monte Carlo vs Temporal Difference
  - MC TD 비교
keywords:
  - Monte Carlo
  - Temporal Difference
  - Bias Variance Tradeoff
  - n-step
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

# MC vs TD

```ad-note
title: Summary
collapse: true

- ==MC: 에피소드 종료 후 실제 Return $G_t$로 업데이트 — Unbiased, High Variance==
- ==TD: 매 스텝 TD Target $r + \gamma v(s')$로 업데이트 — Biased, Low Variance==
- ==n-step Return으로 MC↔TD 스펙트럼 구성, Bias-Variance 조절 가능==
```

## Definition

==Model-Free RL에서 가치 함수를 추정하는 두 가지 접근법==

$$v_{t+1}(s_t) = v_t(s_t) - \alpha_t[v_t(s_t) - \bar{v}_t]$$

| 방법 | Target $\bar{v}_t$ | 특징 |
|:---|:---|:---|
| [[Monte Carlo Methods]] | $G_t$ (실제 Return) | 에피소드 종료 후 업데이트 |
| [[Temporal Difference Learning]] | $r_{t+1} + \gamma v_t(s_{t+1})$ | 매 스텝 업데이트 |

<br/><br/>

## Core Comparison

| | Monte Carlo | Temporal Difference |
|:---|:---|:---|
| **업데이트 형태** | Non-incremental (에피소드 후) | ==Incremental== (매 스텝) |
| **적용 환경** | Episodic tasks만 | ==Continuing tasks 포함== |
| **[[Bootstrapping]]** | 없음 | ==있음== ($v_t(s')$ 사용) |
| **Bias** | ==Unbiased== | Biased (초기 추정치 의존) |
| **Variance** | High | ==Low== |
| **초기 추정치** | 불필요 | ==필요== ($v_0$ 설정) |
| **유리한 상황** | 짧은 에피소드, non-Markov 환경 | ==긴/무한 에피소드==, Markov 환경 |

```ad-info
title: Note - Information Propagation

TD는 $v_t(s')$를 통해 ==이웃 상태 정보를 즉시 활용==

| | MC | TD |
|:---|:---|:---|
| **전파 방향** | ==Backward== (에피소드 종료 후) | ==Forward== (매 스텝) |
| **전파 시점** | 에피소드 끝 → 시작 | 즉시 인접 상태에 반영 |
```

<br/><br/>

## Bias-Variance Tradeoff

추정에 관여하는 ==random variables 개수==가 다름:

| | MC | TD |
|:---|:---|:---|
| **관여 변수** | 전체 에피소드 $R_{t+1}, R_{t+2}, \ldots$ | $R_{t+1}, S_{t+1}, A_{t+1}$ ==3개== |
| **Bias** | ==없음== | 있음 (초기 $v_0$ 의존) |
| **Variance** | ==높음== | 낮음 |

- **TD의 Bias**: ==[[Bootstrapping]]으로 인해 초기 추정치 $v_0$에 의존== → 수렴 시 사라짐
- **MC의 Variance**: 에피소드가 길수록 ==더 많은 확률 변수가 누적==

```ad-info
title: Note - Why MC Has High Variance

MC의 return $G_t = \sum_{k=0}^{T-t-1} \gamma^k R_{t+k+1}$는 ==여러 랜덤 변수의 합==

- 에피소드 길이 $L$, action 수 $\lvert\mathcal{A}\rvert$일 때 soft policy 하에서 ==$\lvert\mathcal{A}\rvert^L$개의 가능한 경로== 존재
- 같은 $(s_t, a_t)$에서 시작해도 이후 trajectory에 따라 $G_t$가 크게 달라짐
```

<br/><br/>

## n-step Spectrum

==MC와 TD는 n-step return의 양 극단==

$$G_t^{(n)} = \sum_{i=0}^{n-1} \gamma^i R_{t+i+1} + \gamma^n v(S_{t+n})$$

| $n$ | 알고리즘 | Bias | Variance |
|:---|:---|:---|:---|
| $n=1$ | TD | ==높음== | 낮음 |
| 중간 $n$ | [[n-step Sarsa]] | 중간 | 중간 |
| $n=\infty$ | MC | 없음 | ==높음== |

- [[n-step Sarsa]]로 중간 $n$ 값을 사용하여 ==bias-variance 절충==
- TD(λ)는 eligibility traces로 여러 n-step의 ==가중 평균==을 계산

```ad-info
title: Note - Function Approximation Extension

[[Value Function Approximation]]으로 확장 시 차이:

| | MC + FA | TD + FA |
|:---|:---|:---|
| **Gradient** | ==True gradient== | ==Semi-gradient== |
| **수렴** | SGD 수렴 보장 | [[Projected Bellman Error]] 최소화 |

- MC: target $G_t$가 파라미터 $w$와 ==무관== → 표준 SGD
- TD: target이 $w$에 ==의존== → target의 gradient 무시 (semi-gradient)
```

<br/><br/>

## Related Concepts

- [[Bootstrapping]]: TD의 핵심 특성 — MC와의 주요 차이점
- [[Monte Carlo Methods]]: 실제 Return 기반 학습 ($n=\infty$, bootstrapping 없음)
- [[Temporal Difference Learning]]: TD Target 기반 학습 ($n=1$, bootstrapping 사용)
- [[n-step Sarsa]]: MC↔TD 스펙트럼의 일반화
- [[Value Function Approximation]]: Tabular → FA 확장 (MC: true gradient, TD: semi-gradient)
- [[Sarsa]]: On-Policy TD Control
- [[Q-Learning]]: Off-Policy TD Control
- [[Expected Sarsa]]: 기댓값 기반 TD (분산 감소)
- [[Stochastic Approximation]]: TD 수렴의 이론적 기반
- [[Bellman Equation]]: TD가 해결하는 방정식 (MC는 Return 정의 직접 사용)
- [[Return]]: MC가 샘플링하는 대상
- [[Law of Large Numbers]]: MC 수렴의 이론적 기반

