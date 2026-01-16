---
date: 2026-01-11
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - PBE
  - Projected BE
  - 투영된 벨만 오차
keywords:
  - Projected Bellman Error
  - Bellman Error
  - Projection Matrix
  - Function Approximation
  - TD-Linear
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
    chapter: 11
author:
url:
---

# Projected Bellman Error

```ad-note
title: Summary
collapse: true

- ==PBE: Bellman Error를 FA 공간으로 투영한 목적함수==
- ==핵심 아이디어==: $T_\pi(\hat{v})$가 FA 공간 밖이므로 투영하여 비교
- ==[[TD-Linear]]의 수렴점 $w^* = A^{-1}b$가 PBE를 최소화==
```

## Definition

==Bellman Error를 Function Approximation 공간으로 투영==한 목적함수

$$J_{PBE}(w) = \|\hat{v}(w) - M T_\pi(\hat{v}(w))\|_D^2$$

- $\hat{v}(w) = \Phi w$: 근사 가치 벡터 (FA 공간 내)
- $T_\pi(\cdot)$: [[Bellman Equation|Bellman operator]] — $T_\pi(v) = r_\pi + \gamma P_\pi v$
- $M$: FA 공간으로의 ==orthogonal projection matrix==
- $\|\cdot\|_D$: [[Stationary Distribution]] 가중 norm — $\|x\|_D^2 = x^T D x$

### Motivation

[[Value Function Approximation]]의 목표: true value $v_\pi$에 가까운 $\hat{v}(w)$ 찾기

가장 직관적인 목적함수:

$$J_E(w) = \|\hat{v}(w) - v_\pi\|_D^2$$

→ ==$v_\pi$를 모르므로 직접 최소화 불가능==

대안: Bellman equation 만족도를 측정하는 $J_{BE}$, $J_{PBE}$

<br/><br/>

## Objective Functions Comparison

| 목적함수 | 정의 | 최소화 가능 여부 | 비고 |
|:---|:---|:---|:---|
| **$J_E$ (MSVE)** | $\lVert\hat{v}(w) - v_\pi\rVert_D^2$ | ==$v_\pi$ 모름== | 직관적이나 구현 불가 |
| **$J_{BE}$** | $\lVert\hat{v}(w) - T_\pi(\hat{v}(w))\rVert_D^2$ | ==0 불가능== | $T_\pi(\hat{v})$가 FA 공간 밖 |
| **$J_{PBE}$** | $\lVert\hat{v}(w) - M T_\pi(\hat{v}(w))\rVert_D^2$ | ==0 가능== | 둘 다 FA 공간 내 |

$J_{BE} = 0$이 되려면 $\hat{v}(w) = T_\pi(\hat{v}(w))$여야 하지만:
- $\hat{v}(w) = \Phi w$는 항상 ==FA 공간== 내
- $T_\pi(\hat{v}(w)) = r_\pi + \gamma P_\pi \Phi w$는 일반적으로 ==FA 공간 밖==
- → 두 벡터가 같아질 수 없음

$J_{PBE}$는 projection $M$이 $T_\pi(\hat{v}(w))$를 FA 공간으로 가져오므로 ==비교 대상이 모두 FA 공간 내== → 같아지는 $w$ 존재

<br/><br/>

## Projection Matrix

$$M = \Phi (\Phi^T D \Phi)^{-1} \Phi^T D \in \mathbb{R}^{n \times n}$$

- $\Phi \in \mathbb{R}^{n \times m}$: [[Value Function Approximation|Feature matrix]]
- $D = \text{diag}(d_\pi) \in \mathbb{R}^{n \times n}$: [[Stationary Distribution]] 대각 행렬

### Properties

| 속성 | 설명 |
|:---|:---|
| **Orthogonal projection** | $D$-weighted inner product 기준으로 FA 공간에 투영 |
| **$\lVert M\rVert_D = 1$** | Projection matrix의 $D$-norm이 1 |
| **$M \Phi = \Phi$** | FA 공간 내의 벡터는 ==투영 후에도 그대로 유지== |
| **Non-expansion** | $\lVert M x\rVert_D \leq \lVert x\rVert_D$ for all $x$ |
| **$M^2 \neq M$** | $D$-weighted projection이므로 ==일반적인 idempotent 아님== |

<br/>

```ad-info
title: Note - Geometric Interpretation

$$v \xrightarrow{M} \text{range}(\Phi)$$

- **Range space of $\Phi$** (= FA 공간): $\{\Phi w : w \in \mathbb{R}^m\}$ — ==모든 가능한 linear approximation의 집합==
- $M v$: $v$에 가장 가까운 range$(\Phi)$ 내의 벡터 ($D$-norm 기준)
- $\|M v - v\|_D = \min_w \|\Phi w - v\|_D$
```

```ad-info
title: Note - Matrix Definitions

| 행렬/벡터 | 정의 | 차원 |
|:---|:---|:---|
| $\Phi$ | Feature matrix | $n \times m$ |
| $D$ | $\text{diag}(d_\pi)$ | $n \times n$ |
| $P_\pi$ | Transition matrix under $\pi$ | $n \times n$ |
| $r_\pi$ | Expected reward vector | $n \times 1$ |
| $A$ | $\Phi^T D (I - \gamma P_\pi) \Phi$ | $m \times m$ |
| $b$ | $\Phi^T D r_\pi$ | $m \times 1$ |
| $M$ | $\Phi (\Phi^T D \Phi)^{-1} \Phi^T D$ | $n \times n$ |
```

<br/><br/>

## TD-Linear Connection

[[TD-Linear]]의 수렴점이 ==$J_{PBE}$를 최소화==:

$$w^* = A^{-1}b = \arg\min_w J_{PBE}(w)$$

where:
- $A = \Phi^T D (I - \gamma P_\pi) \Phi \in \mathbb{R}^{m \times m}$
- $b = \Phi^T D r_\pi \in \mathbb{R}^{m}$

$J_{PBE}(w^*) = 0$일 때, $\hat{v}(w^*)$는 ==Bellman operator의 출력을 FA 공간에 투영한 결과와 정확히 일치==:

$$\hat{v}(w^*) = M T_\pi(\hat{v}(w^*))$$

```ad-info
title: Note - Relationship with MSVE

$J_{PBE} = 0$이라도 $J_E \neq 0$일 수 있음:
- $\hat{v}(w^*)$는 ==FA 공간 내 최선==이지만
- True value $v_\pi$가 FA 공간 밖이면 ==근사 오차 발생==

→ [[TD-Linear#Error Bound|TD-Linear Error Bound]] 참조
```

<br/><br/>

## Related Concepts

- [[TD-Linear]]: PBE를 최소화하는 알고리즘, 수렴점 $w^* = A^{-1}b$
- [[Least Squares TD|LSTD]]: $w^* = A^{-1}b$를 샘플로 직접 추정
- [[Value Function Approximation]]: FA의 기본 개념, Feature matrix $\Phi$ 정의
- [[Bellman Equation]]: Bellman operator $T_\pi$의 정의
- [[Stationary Distribution]]: 가중 norm $\|\cdot\|_D$의 가중치 $d_\pi(s)$
- [[Temporal Difference Learning]]: Tabular TD (FA 적용 전)

