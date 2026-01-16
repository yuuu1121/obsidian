---
date: 2025-12-29
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 반환값
  - Cumulative Reward
  - Total Reward
keywords:
  - Return
  - Cumulative Reward
  - Discount Factor
  - Bootstrapping
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
author:
url:
---

# Return

```ad-note
title: Summary
collapse: true

- ==[[Rollout|Trajectory]]를 따라 수집한 모든 보상의 할인 합==
- ==에이전트가 실제로 최대화하려는 값==
- ==확률 변수==: trajectory마다 다른 값 → [[Value Function|State Value]]는 기댓값
- ==Discount Factor $\gamma$: 미래 보상의 현재 가치 결정==
```

## Definition

<!-- Chapter 2 -->

==[[Rollout|Trajectory]]를 따라 수집한 모든 보상의 할인 합==

$$G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1} = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots$$

- $R_{t+k+1}$: 시점 $t+k$에서 $t+k+1$로 전이할 때 받는 [[Reward|즉각 보상]]
- $\gamma \in [0, 1]$: [[#Discount Factor|할인 인자]]
- Discounted return이라고도 함 (할인된 누적 보상)
- ==에이전트가 실제로 최대화하려는 값==
- ==확률 변수==: trajectory마다 다른 값

<br/><br/>

## Return vs State Value

| | **Return ($G_t$)** | **[[Value Function#State Value Function\|State Value]] ($v_\pi(s)$)** |
|:---|:---|:---|
| **정의** | 하나의 trajectory에서 얻은 보상의 할인 합 | 특정 상태에서 시작했을 때 Return의 **기댓값** |
| **성질** | ==확률 변수== (trajectory마다 다름) | ==기댓값== (하나의 숫자) |
| **수식** | $G_t = R_{t+1} + \gamma R_{t+2} + \cdots$ | $v_\pi(s) = \mathbb{E}[G_t \| S_t = s]$ |

- **Deterministic**: trajectory가 하나뿐 → ==Return = State Value==
- **Stochastic**: 여러 trajectory 가능 → ==State Value = Return들의 평균==

<br/><br/>

## Policy Evaluation via Return

==같은 상태에서 시작해도 정책에 따라 Return이 다름 → Return으로 정책 비교 가능==

![[Pasted image 20251229170428.png]]

- 주황색: 금지구역 ($r = -1$)
- 파란색: 목표구역 ($r = 1$)
- $s_4$: 목표 상태 (원으로 표시)

| 정책 | $s_1$에서의 행동 | Trajectory | Return |
|:---|:---|:---|:---|
| 왼쪽 | 아래로 이동 | $s_1 \to s_3 \to s_4 \to \cdots$ | $\frac{\gamma}{1-\gamma}$ |
| 가운데 | 오른쪽으로 이동 | $s_1 \to s_2 \to s_4 \to \cdots$ | $-1 + \frac{\gamma}{1-\gamma}$ |
| 오른쪽 | 확률 0.5로 선택 | 두 경로의 평균 | $-0.5 + \frac{\gamma}{1-\gamma}$ |

→ ==Return: 왼쪽 > 오른쪽 > 가운데== → 금지구역을 피하는 정책이 가장 좋음

```ad-example
title: Example - Return Calculation
collapse: true

**설정**:
- 4개 상태: $s_1, s_2, s_3, s_4$
- 금지구역 (주황): $r = -1$
- 목표구역 (파랑): $r = 1$
- $s_4$: 목표 상태 (absorbing state)

**정책 1** (결정적, 아래로):
$$s_1 \to s_3 \to s_4 \to s_4 \to \cdots$$
$$G_1 = 0 + \gamma \cdot 1 + \gamma^2 \cdot 1 + \cdots = \frac{\gamma}{1-\gamma}$$

**정책 2** (결정적, 오른쪽):
$$s_1 \to s_2 \to s_4 \to s_4 \to \cdots$$
$$G_2 = -1 + \gamma \cdot 1 + \gamma^2 \cdot 1 + \cdots = -1 + \frac{\gamma}{1-\gamma}$$

**정책 3** (확률적, 0.5씩):
$$G_3 = 0.5 \cdot G_1 + 0.5 \cdot G_2 = -0.5 + \frac{\gamma}{1-\gamma}$$

**비교 결과**:
$$G_1 > G_3 > G_2 \quad \text{(모든 } \gamma \text{에 대해)}$$

→ 금지구역을 피하는 정책 1이 가장 좋음 (직관과 수학적 결론 일치)
```

<br/><br/>

## Discount Factor

==할인 인자 $\gamma \in [0, 1]$: 미래 보상의 현재 가치 결정==

| $\gamma$ | 특성 | Effective Horizon | 용도 |
|:---|:---|:---|:---|
| 0 | Myopic (근시안적) | 1 step | - |
| 0.9 | 단기적 | 10 step | 빠른 학습 |
| 0.99 | 균형적 | 100 step | 일반적 |
| 0.999 | Far-sighted | 1000 step | 장기 문제 |

**필요한 이유:**
- ==Continuing tasks에서 무한 합의 수렴 보장==: $G_t \leq \frac{r_{\max}}{1 - \gamma}$ ($r_{\max}$: 최대 보상)
- [[Episode|Episodic tasks]]에서는 $\gamma = 1$ 가능
- Effective Horizon: $H_{\text{eff}} = \frac{1}{1 - \gamma}$ — 이후 보상은 사실상 무시됨

**최적 정책에 대한 영향:**

| $\gamma$ 값 | 정책 특성 | 설명 |
|:---|:---|:---|
| **높음** (0.9) | ==Far-sighted== | 장기적 누적 보상 극대화, 단기 손해 감수 가능 |
| **낮음** (0.5) | ==Short-sighted== | 단기 보상에 집중, 위험 회피 |
| **0** | ==Extremely short-sighted== | 즉각 보상만 고려, 장기적 목표 도달 불가 |

```ad-example
title: Example - Discount Factor에 따른 최적 정책 변화
collapse: true

![[figure 3.4 a.png]]
> (a) $\gamma = 0.9$: 금지 영역 통과해도 장기 보상 극대화

![[figure 3.4 b.png]]
> (b) $\gamma = 0.5$: 위험 회피, 우회 경로 선택

![[figure 3.4 c.png]]
> (c) $\gamma = 0$: 즉각 보상만 고려, 목표 도달 불가

→ ==목표에 가까운 상태일수록 높은 가치== (긴 trajectory → 더 많은 할인 적용)
```

<br/><br/>

## Recursive Structure

Return은 ==재귀적으로 분해== 가능:

$$G_t = R_{t+1} + \gamma G_{t+1}$$

- 현재 보상 + 할인된 미래 Return
- 이 재귀 구조가 [[Bellman Equation]]의 핵심

<br/>

### From Return to State Value

Return $G_t$는 확률 변수이므로 직접 계산이 어려움 → ==기댓값인 [[Value Function#State Value Function|State Value]]로 변환==:

$$v_\pi(s) = \mathbb{E}[G_t | S_t = s] = \mathbb{E}[R_{t+1} + \gamma G_{t+1} | S_t = s]$$

이 관계가 [[Bellman Equation]]으로 이어짐:

$$v_\pi(s) = \sum_a \pi(a|s) \left[ \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_\pi(s') \right]$$

<br/>

### Estimation Methods

| 방법 | Return 사용 | 특징 |
|:---|:---|:---|
| **[[Monte Carlo Methods]]** | ==실제 $G_t$== | 에피소드 종료 필요, unbiased |
| **[[Temporal Difference Learning]]** | ==추정 $r + \gamma v(s')$== | 매 스텝 업데이트, biased but low variance |

→ [[MC vs TD]]에서 두 방식의 bias-variance trade-off 상세 비교

<br/><br/>

## Related Concepts

- [[Policy]]: Return을 최대화하는 최적 정책 $\pi^*$ 탐색이 RL의 목표
- [[Value Function]]: Return의 기댓값 $v_\pi(s) = \mathbb{E}[G_t]$ — Return → State Value 변환
- [[Bellman Equation]]: Return의 재귀 구조 $G_t = R_{t+1} + \gamma G_{t+1}$을 기댓값으로 확장
- [[Reward]]: Return을 구성하는 즉각적 피드백 신호
- [[Rollout|Trajectory]]: Return이 정의되는 상태-행동 시퀀스
- [[Monte Carlo Methods]]: 실제 Return $G_t$를 샘플링하여 학습
- [[Temporal Difference Learning]]: Return을 추정값으로 근사 ([[Bootstrapping]])
- [[MC vs TD]]: Return 사용 방식에 따른 알고리즘 비교
- [[Episode]]: Episodic tasks에서 $\gamma=1$ 가능, Continuing tasks에서 $\gamma<1$ 필수

