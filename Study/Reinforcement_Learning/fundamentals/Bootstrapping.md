---
date: 2026-01-09
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 부트스트래핑
keywords:
  - Bootstrapping
  - TD Learning
  - Bias
  - Variance
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 7
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Bootstrapping

```ad-note
title: Summary
collapse: true

- ==Bootstrapping: 추정치를 사용해 추정치를 업데이트하는 방법==
- ==TD는 bootstrapping 사용 (biased, low variance), MC는 미사용 (unbiased, high variance)==
- ==초기 추정치 $v_0$에 의존하여 bias 발생, 수렴 시 사라짐==
```

## Definition

==추정치(estimate)를 사용해 또 다른 추정치를 업데이트==하는 방법

$$v(s) \leftarrow r + \gamma \underbrace{v(s')}_{\text{estimate}}$$

- "자기 자신을 들어올린다(pull oneself up by one's bootstraps)"에서 유래
- [[Bellman Equation]]의 재귀 구조를 활용

| | Bootstrapping ([[Temporal Difference Learning\|TD]]) | Non-Bootstrapping ([[Monte Carlo Methods\|MC]]) |
|:---|:---|:---|
| **Target** | $r + \gamma v(s')$ | $G_t$ (실제 Return) |
| **필요 정보** | 다음 상태 추정치 | 에피소드 전체 |
| **업데이트 시점** | ==매 스텝== | 에피소드 종료 후 |
| **초기 추정치** | ==필요== | 불필요 |

<br/><br/>

## Bias-Variance Tradeoff

Bootstrapping은 ==bias를 도입하는 대신 variance를 줄임==

| | Bootstrapping (TD) | Non-Bootstrapping (MC) |
|:---|:---|:---|
| **Bias** | ==Biased== (초기 추정치 의존) | Unbiased |
| **Variance** | ==Low== | High |
| **관여 변수** | $R_{t+1}, S_{t+1}$ (2~3개) | 전체 에피소드 |

- **Bias 원인**: 초기 추정치 $v_0$가 부정확하면 업데이트에 전파 → ==수렴 시 bias 사라짐== (asymptotically unbiased)
- **Variance 감소 원인**: MC는 에피소드 전체 보상 합산으로 variance 누적, TD는 ==한 스텝만 사용해 관여 변수 수가 적음==

<br/><br/>

## Bootstrapping Spectrum

[[n-step Sarsa]], TD(λ)로 ==bootstrapping 정도 조절== 가능

| n-step | Bootstrapping | 특성 |
|:---|:---|:---|
| $n = 1$ | ==최대== (TD) | Low variance, biased |
| $1 < n < \infty$ | 중간 | Bias-Variance 절충 |
| $n = \infty$ | ==없음== (MC) | High variance, unbiased |

$$G_t^{(n)} = R_{t+1} + \gamma R_{t+2} + \cdots + \gamma^{n-1} R_{t+n} + \gamma^n v(S_{t+n})$$

- $n$ 증가 → 실제 보상 비중 증가 → bias 감소, variance 증가
- $n$ 감소 → 추정치 비중 증가 → bias 증가, variance 감소

<br/><br/>

## Related Concepts

- [[Temporal Difference Learning]]: Bootstrapping을 사용하는 대표 알고리즘
- [[Monte Carlo Methods]]: Bootstrapping을 사용하지 않는 방법
- [[MC vs TD]]: Bootstrapping 유무에 따른 알고리즘 비교
- [[Bellman Equation]]: Bootstrapping의 이론적 근거 (재귀 구조)
- [[n-step Sarsa]]: n-step으로 bootstrapping 정도 조절
