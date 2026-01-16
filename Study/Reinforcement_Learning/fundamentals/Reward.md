---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 보상
  - Reward Signal
keywords:
  - Reward
  - Reward Hypothesis
  - Reward Probability
  - Immediate Reward
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Reward

```ad-note
title: Summary
collapse: true

- ==환경이 에이전트에게 제공하는 스칼라 피드백 신호 $r_t$==
- ==Reward Hypothesis: 모든 목표는 기대 누적 보상 최대화로 표현 가능==
- ==상대적 크기가 정책을 결정== — 아핀 변환에 대해 최적 정책 불변
```

## Definition

==환경이 에이전트에게 제공하는 스칼라 피드백 신호==

$$R_{t+1} \sim p(\cdot | S_t, A_t)$$

- $R_{t+1}$: 시간 $t$에서 행동 후 받는 reward
- $p(r|s, a)$: ==reward probability== — 상태 $s$에서 행동 $a$ 후 보상 $r$을 받을 확률
- 정규화 조건: $\sum_{r} p(r|s, a) = 1$

| Property | Description |
|:---|:---|
| **Scalar** | 단일 숫자로 행동의 좋고 나쁨 평가 |
| **Environment-determined** | ==에이전트가 아닌 환경이 결정== |
| **Delayed** | 보상이 즉시 주어지지 않을 수 있음 |
| **Relative** | ==상대적 크기가 정책 결정== (아핀 변환 불변) |

<br/>

### Reward Hypothesis

==모든 목표는 기대 누적 보상의 최대화로 표현 가능==

- 강화학습의 철학적 기반이자 기본 가정
- 복잡한 목표도 적절한 reward 설계로 표현 가능

<br/><br/>

## Immediate vs Future Rewards

==즉각적 보상이 최대인 행동 ≠ 최적 행동==

| 구분 | 설명 |
|:---|:---|
| **Immediate Reward** | 행동 직후 받는 보상 $R_{t+1}$ |
| **Future Rewards** | 이후 받는 모든 보상의 합 |

- Immediate reward는 ==단일 행동의 즉각적 결과==만 반영
- 좋은 정책은 ==장기적 총 보상 ([[Return]])을 최대화==해야 함

<br/><br/>

## Reward Transformation Invariance

==보상 함수의 아핀 변환에 대해 최적 정책 불변==:

$$r' = \alpha r + \beta \quad (\alpha > 0)$$

| Transformation | Policy | Value |
|:---|:---|:---|
| Scaling ($r \to \alpha r$) | ==불변== | $v^* \to \alpha v^*$ |
| Constant shift ($r \to r + \beta$) | ==불변== | $v^* \to v^* + \frac{\beta}{1-\gamma}$ |

→ Reward shaping 시 아핀 변환은 안전

```ad-example
title: Example - Reward Magnitude Effect
collapse: true

![[figure 3.4 d.png]]

아핀 변환이 아닌 ==특정 보상만 변경==하면 정책이 달라질 수 있음:

$r_{\text{forbidden}} = -1 \to -10$: 금지 영역 완전 회피

→ 처벌 강화는 해당 영역 회피를 유도
```

<br/><br/>

## Related Concepts

- [[Return]]: 보상의 누적 합 (할인된 trajectory 보상)
- [[Value Function]]: Return의 기댓값으로 정책 평가
- [[Bellman Equation]]: Return의 재귀적 관계, reward probability 사용
- [[Agent and Environment]]: 환경이 에이전트에게 제공하는 피드백 신호
- [[Markov Reward Process]]: Reward probability가 정의되는 프레임워크
- [[Transition Probability]]: 동역학의 다른 구성 요소 (어디로 가는가?)
