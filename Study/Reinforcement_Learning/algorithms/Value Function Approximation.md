---
date: 2026-01-11
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 가치 함수 근사
  - Function Approximation
  - FA
  - Linear Function Approximation
  - Linear FA
keywords:
  - Value Function Approximation
  - Linear Approximation
  - Feature Vector
  - Generalization
  - Tabular Method
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 8
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
    chapter: 9
author:
url:
---

# Value Function Approximation

```ad-note
title: Summary
collapse: true

- ==FA: 테이블 대신 파라미터화된 함수로 가치 함수를 근사==
- ==핵심 수식: $\hat{v}(s,w) = \phi^T(s)w$ — Feature vector와 파라미터의 내적==
- ==일반화 능력: 한 상태의 경험이 유사한 상태들에 전파==
- ==Tabular는 FA의 특수 케이스== (one-hot encoding)
```

![[Pasted image 20260111071728.png|700]]

## Definition

상태 공간이 클 때 ==테이블 대신 파라미터화된 함수로 가치 함수를 근사==하는 방법

$$\hat{v}(s,w) = \phi^T(s)w \approx v_\pi(s)$$

- $\phi(s) \in \mathbb{R}^m$: ==Feature vector== (상태 표현, 수동 설계)
- $w \in \mathbb{R}^m$: ==파라미터 벡터== (학습 대상, $m \ll \lvert\mathcal{S}\rvert$)
- $\hat{v}(s,w)$: 근사된 state value

```ad-info
title: Note - Motivation and Trade-offs

**Tabular 방법의 한계** → FA의 동기:
- **메모리**: $\lvert\mathcal{S}\rvert$개 값 저장 — 대규모 상태 공간에서 불가능
- **샘플 효율성**: 방문하지 않은 상태는 학습 불가 — 일반화 없음
- **연속 공간**: 무한 상태에 대한 테이블 불가능

**FA의 Trade-offs**:

| 장점 | 단점 |
|:---|:---|
| ==메모리 효율==: $m \ll \lvert\mathcal{S}\rvert$ | ==근사 오차== 발생 |
| ==일반화==: 유사 상태 간 경험 공유 | ==Feature 설계== 필요 |
| ==연속 공간== 처리 가능 | ==수렴 보장== 약화 (특히 Off-Policy) |

**핵심**: Feature 차원 $m$이 ==저장 효율 ↔ 정확도== 결정 — 정보 손실은 불가피
```

```ad-info
title: Note - Extension to Action Value and Policy

동일한 아이디어가 action value와 policy로 확장:

- ==Action value==: $\hat{q}(s,a,w) = \phi^T(s,a)w$ — [[Sarsa with Function Approximation]], [[Deep Q-Learning|DQN]]
- ==Policy==: $\pi_\theta(a\vert s)$ — [[Policy Gradient]]의 기초
```

<br/><br/>

## Function Representation

![[Pasted image 20260111011411.png|700]]

### Tabular Representation

==모든 상태의 추정값을 배열 또는 벡터로 저장==:

| State | $s_1$ | $s_2$ | $\cdots$ | $s_n$ |
|:---|:---:|:---:|:---:|:---:|
| **Estimated value** | $\hat{v}(s_1)$ | $\hat{v}(s_2)$ | $\cdots$ | $\hat{v}(s_n)$ |

- **값 조회**: 테이블 인덱스로 직접 접근 → $v(s) = \text{table}[s]$
- **값 갱신**: $v(s) \leftarrow \text{new value}$
- **갱신 영향**: ==해당 상태만== — 다른 상태에 영향 없음
- **저장 공간**: $\lvert\mathcal{S}\rvert$개의 값
- **한계**: 대규모/연속 공간 불가, 방문한 상태만 학습

<br/>

### Function Representation

==$\hat{v}(s,w)$로 파라미터화==하여 가치 함수 근사:

- **값 조회**: 함수 계산 $\hat{v}(s,w) = \phi^T(s)w$
- **값 갱신**: 파라미터 $w$ 업데이트
- **갱신 영향**: ==$w$ 업데이트 시 모든 상태의 값 변경== — ==유사 상태에 경험 전파== (일반화)
- **저장 공간**: ==$m$개 파라미터== ($m \ll \lvert\mathcal{S}\rvert$)
- **장점**: 연속 공간 처리 가능

<br/><br/>

## Linear Function Approximation

![[Pasted image 20260111010811.png|300]]

==$w$에 대해 선형==인 가장 단순한 근사 방법:

$$\hat{v}(s,w) = \phi^T(s)w = \sum_{i=1}^{m} \phi_i(s) w_i$$

- $\phi(s)$: ==[[Linear Regression#Basis Function|기저 함수 (basis)]]== — 어떤 형태의 value function을 표현할 수 있는지 결정
- $w$: ==계수 (coefficients)== — 데이터로 학습

```ad-info
title: Note - Linear in $w$, Nonlinear in $s$

$\hat{v}(s,w) = \phi^T(s)w$는 ==$w$에 대해 선형==이지만, ==$s$에 대해서는 비선형==일 수 있음

- $w$에 대해: 선형 (각 $w_i$가 1차로만 등장)
- $s$에 대해: 비선형 가능 (feature vector $\phi(s)$가 $s$의 비선형 함수)

**다항식 예시**:

| 차수 | Feature Vector $\phi(s)$ | 근사 함수 형태 |
|:---|:---|:---|
| 1차 | $[1, s]^T$ | $w_1 + w_2 s$ (직선) |
| 2차 | $[1, s, s^2]^T$ | $w_1 + w_2 s + w_3 s^2$ (포물선) |

$$\hat{v}(s, w) = as^2 + bs + c = \underbrace{[s^2, s, 1]}_{\phi^T(s)} \underbrace{\begin{bmatrix} a \\ b \\ c \end{bmatrix}}_{w} = \phi^T(s)w$$

→ $\phi(s) = [s^2, s, 1]^T$가 $s$의 ==비선형 함수==이지만, $w$에 대해서는 ==선형==
```

```ad-info
title: Note - Tabular as Special Case

==Tabular 방법은 Linear FA의 특수 케이스== — One-hot encoding $\phi(s) = e_s \in \mathbb{R}^{\lvert\mathcal{S}\rvert}$ 사용

$$\hat{v}(s,w) = e_s^T w = w(s)$$

- $e_s$: 상태 $s$에 해당하는 위치만 1, 나머지 0 → $w$가 곧 ==테이블 자체==
- **Tabular TD**: $v_{t+1}(s_t) = v_t(s_t) + \alpha_t \delta_t$
- **TD-Linear with $\phi(s) = e_s$**: $w_{t+1} = w_t + \alpha_t \delta_t e_{s_t}$ → ==$w$의 $s_t$번째 원소만 업데이트==
```

<br/><br/>

## Feature Vector

$$\phi(s) = [\phi_1(s), \phi_2(s), \ldots, \phi_m(s)]^T \in \mathbb{R}^m$$

==Value function을 근사하기 위한 기저 함수== ([[Linear Regression#Basis Function|Basis Function]] 참조)

| 설계 방법 | 형태 | 특징 |
|:---|:---|:---|
| **Polynomial** | $[1, x, y, x^2, \ldots]^T$ | 간단, 전역적 |
| **Fourier** | $[\cos(\pi c_1 x), \ldots]^T$ | 주기적 패턴 |
| **Tile Coding** | 겹치는 타일로 분할 | 국소적 |
| **RBF** | Gaussian 기반 | 국소적, 매끄러운 |

**Feature Matrix**: 모든 상태의 feature vector를 행렬로 표현

$$\Phi = \begin{bmatrix} \phi^T(s_1) \\ \vdots \\ \phi^T(s_n) \end{bmatrix} \in \mathbb{R}^{n \times m}, \quad \hat{v} = \Phi w \in \mathbb{R}^n$$

```ad-warning
title: Note - Feature Design and Neural Network

**Linear FA의 한계**: $\phi(s)$를 ==어떻게 설계해야 할지 사전에 모름== → 도메인 지식 필요

**Neural Network의 해결책**: ==$\phi(s)$도 함께 학습==

| | Linear FA | Neural Network |
|:---|:---|:---|
| **기저함수 $\phi$** | ==고정== (수동 설계) | ==학습== (hidden layers) |
| **파라미터** | $w$만 학습 | 전체 $\theta$ 학습 |
| **표현력** | $\phi$ 설계에 의존 | 데이터에서 자동 추출 |

$$\text{Linear FA: } s \xrightarrow{\text{fixed } \phi} \phi(s) \xrightarrow{w^T} \hat{v}(s,w)$$

$$\text{Neural Net: } s \xrightarrow{\text{learned } \phi_\theta} \phi_\theta(s) \xrightarrow{w^T} \hat{v}(s,\theta)$$

Neural Network에서 hidden layers가 ==학습 가능한 기저함수== $\phi_\theta(s)$ 역할 → "어떤 feature를 추출할지"를 ==데이터로부터 자동 학습== → [[Deep Q-Learning]]
```

<br/><br/>

## Optimal Parameter

$v_\pi(s)$를 알고 있다면, ==Least Squares 문제==로 최적 파라미터를 찾을 수 있음

**목적함수**:

$$J(w) = \|\Phi w - v_\pi\|^2 = \sum_{i=1}^{n} \left(\hat{v}(s_i, w) - v_\pi(s_i)\right)^2$$

**[[Linear Regression#Optimal Solution|최적해]]**:

$$w^* = (\Phi^T \Phi)^{-1} \Phi^T v_\pi$$

```ad-warning
title: Note - Practical Challenge

실제로는 ==$v_\pi(s)$를 모름== → 샘플 기반 학습 필요

- [[TD-Linear]]: TD target으로 $v_\pi$ 대체 (Semi-gradient)
- [[Least Squares TD|LSTD]]: $w^* = A^{-1}b$를 샘플로 직접 추정
```

<br/><br/>

## Related Concepts

- [[Temporal Difference Learning]]: FA 적용 전의 Tabular TD
- [[Monte Carlo Methods]]: FA 적용 전의 Tabular MC
- [[MC vs TD]]: FA 확장 시 Semi-gradient(TD) vs True gradient(MC) 비교
- [[TD-Linear]]: TD + Linear FA (Semi-gradient 방식)
- [[Projected Bellman Error]]: FA에서 최소화하는 목적함수
- [[Least Squares TD|LSTD]]: FA에서 샘플 효율적 알고리즘
- [[Sarsa with Function Approximation]]: On-Policy Control with FA
- [[Deep Q-Learning]]: Off-Policy Control with FA (Neural Network)
- [[Stationary Distribution]]: 목적함수의 가중치 $d_\pi(s)$
- [[Linear Regression]]: Basis function 개념 공유
- [[Value Function]]: 근사 대상
- [[Policy Gradient]]: Policy function approximation 기반 최적화

