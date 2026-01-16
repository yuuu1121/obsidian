---
date: 2026-01-11
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - LSTD
  - Least-Squares TD
  - LSTD(0)
  - 최소제곱 TD
keywords:
  - LSTD
  - Least-Squares TD
  - Sample Efficiency
  - Matrix Inversion
  - Sherman-Morrison
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
    chapter: 9.8
author:
url:
---

# Least Squares TD

```ad-note
title: Summary
collapse: true

- ==LSTD: $w^* = A^{-1}b$를 샘플로 직접 추정== — 최적해 형태를 활용
- ==[[TD-Linear]]보다 샘플 효율적==, step size 불필요
- ==Sherman-Morrison 공식==으로 $O(m^2)$ 복잡도 달성
```

## Definition

==[[Projected Bellman Error]]의 최적해 $w^* = A^{-1}b$를 샘플로 직접 추정하는 알고리즘==

$$w_t = \hat{A}_t^{-1} \hat{b}_t$$

- $A = \Phi^T D(I - \gamma P_\pi)\Phi$, $b = \Phi^T D r_\pi$ — [[TD-Linear]]의 수렴점
- [[TD-Linear]]와 달리 ==점진적 업데이트 없이 직접 계산==, step size 불필요

```ad-info
title: Note - Key Idea

$A$와 $b$가 ==기대값 형태==로 표현 가능:

$$A = \mathbb{E}\left[\phi(s_t)(\phi(s_t) - \gamma\phi(s_{t+1}))^T\right], \quad b = \mathbb{E}\left[r_{t+1}\phi(s_t)\right]$$

→ 기대값이므로 ==샘플 평균으로 추정 가능== → $w^* \approx \hat{A}^{-1}\hat{b}$
```

<br/><br/>

## Sample Estimation

경험 trajectory $(s_0, r_1, s_1, \ldots)$로부터 $A$, $b$를 샘플로 추정:

$$\hat{A}_t = \sum_{k=0}^{t-1} \phi(s_k) \left(\phi(s_k) - \gamma\phi(s_{k+1})\right)^T, \quad \hat{b}_t = \sum_{k=0}^{t-1} r_{k+1} \phi(s_k)$$

- $\hat{A}_t$: $A = \Phi^T D(I - \gamma P_\pi)\Phi$의 샘플 추정
- $\hat{b}_t$: $b = \Phi^T D r_\pi$의 샘플 추정

```ad-info
title: Note - Missing 1/t Coefficient

$\hat{A}_t$와 $\hat{b}_t$ 정의에서 ==계수 $\frac{1}{t}$가 생략==됨:

$$w_t = \hat{A}_t^{-1} \hat{b}_t = \left(\frac{1}{t}\hat{A}_t\right)^{-1} \left(\frac{1}{t}\hat{b}_t\right)$$

분자와 분모에서 $\frac{1}{t}$가 상쇄되므로 결과는 동일
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - LSTD

**입력**: Feature vector $\phi(s)$, 정책 $\pi$, 정규화 파라미터 $\sigma > 0$

**초기화**: $\hat{A}_0 = \sigma I$, $\hat{b}_0 = 0$

**For** $t = 0, 1, 2, \ldots$:
- 정책 $\pi$에 따라 행동 $a_t$ 선택
- 보상 $r_{t+1}$, 다음 상태 $s_{t+1}$ 관측
- 행렬/벡터 업데이트:
  - $\hat{A}_{t+1} = \hat{A}_t + \phi(s_t)(\phi(s_t) - \gamma\phi(s_{t+1}))^T$
  - $\hat{b}_{t+1} = \hat{b}_t + r_{t+1}\phi(s_t)$
- 파라미터 계산: $w_{t+1} = \hat{A}_{t+1}^{-1} \hat{b}_{t+1}$

**출력**: 학습된 파라미터 $w$
```

```ad-warning
title: Note - Regularization

$\hat{A}_t$는 특히 $t$가 작을 때 ==invertible하지 않을 수 있음==

해결책: $\hat{A}_0 = \sigma I$로 초기화 ($\sigma > 0$: 작은 양수) → $\hat{A}_t$가 항상 invertible하도록 보장
```

<br/><br/>

## Sherman-Morrison Optimization

매 step에서 $\hat{A}_t^{-1}$ 계산 → ==$O(m^3)$ 복잡도== 문제

**해결책**: $\hat{A}_t$가 아닌 ==$\hat{A}_t^{-1}$을 직접 저장하고 업데이트==

$\hat{A}_{t+1}$은 ==rank-1 업데이트== 형태:

$$\hat{A}_{t+1} = \hat{A}_t + \underbrace{\phi(s_t)}_{u}\underbrace{(\phi(s_t) - \gamma\phi(s_{t+1}))^T}_{v^T}$$

**Sherman-Morrison 공식** 적용:

$$\hat{A}_{t+1}^{-1} = \hat{A}_t^{-1} - \frac{\hat{A}_t^{-1} \phi(s_t) (\phi(s_t) - \gamma\phi(s_{t+1}))^T \hat{A}_t^{-1}}{1 + (\phi(s_t) - \gamma\phi(s_{t+1}))^T \hat{A}_t^{-1} \phi(s_t)}$$

| 특성 | 설명 |
|:---|:---|
| **저장 대상** | $\hat{A}_t^{-1}$ (행렬 역연산 불필요) |
| **복잡도** | ==$O(m^2)$ per step== (행렬-벡터 연산) |
| **Step size** | ==불필요== |
| **초기값** | $\hat{A}_0^{-1} = \frac{1}{\sigma} I$ |

<br/><br/>

## Comparison with TD-Linear

| 측면 | TD-Linear | LSTD |
|:---|:---|:---|
| **업데이트 방식** | Incremental: $w_{t+1} = w_t - \alpha_t \delta_t \phi(s_t)$ | Direct: $w_t = \hat{A}_t^{-1} \hat{b}_t$ |
| **수렴 속도** | 느림 (점진적) | ==빠름 (샘플 효율적)== |
| **계산 복잡도** | ==$O(m)$ per step== | $O(m^2)$ per step |
| **저장 공간** | ==$O(m)$== | $O(m^2)$ (행렬 저장) |
| **Step size** | 필요 ($\alpha_t$) | ==불필요== |
| **비선형 FA** | 가능 | ==불가능== |
| **Action value** | 확장 가능 | ==확장 어려움== |

<br/>

### Usage Guidelines

**LSTD 선호 상황**:
- ==샘플이 귀한 환경== (simulation 비용이 높은 경우)
- Feature 차원 $m$이 ==작은== 경우
- State value 추정만 필요한 경우

**TD-Linear 선호 상황**:
- ==샘플이 풍부한 환경==
- Feature 차원 $m$이 ==큰== 경우
- ==Action value 추정== 또는 control 필요
- ==비선형 FA== 사용 시

```ad-info
title: Note - LSTD Limitations

- ==Linear FA 전용==: $A, b$의 형태가 linear FA에서만 유도됨
- ==State value 전용==: Action value로 확장 시 행렬 차원 급증 ($|\mathcal{A}|m \times |\mathcal{A}|m$)
- ==On-policy 전용==: Off-policy에서는 importance sampling 등 correction 필요
- Neural Network 같은 비선형 근사기 사용 시 ==TD 방식이 유일한 선택==
```

<br/><br/>

## Related Concepts

- [[TD-Linear]]: 같은 해 $w^* = A^{-1}b$를 점진적으로 찾음 (SGD 방식)
- [[Projected Bellman Error]]: LSTD가 최소화하는 목적함수
- [[Value Function Approximation]]: Feature vector $\phi(s)$ 정의
- [[Stationary Distribution]]: $A, b$의 기대값 정의에 사용되는 $d_\pi(s)$
- [[Stochastic Approximation]]: TD-Linear의 수렴 기반 (RM algorithm)
- [[Temporal Difference Learning]]: Tabular TD (FA 적용 전)

