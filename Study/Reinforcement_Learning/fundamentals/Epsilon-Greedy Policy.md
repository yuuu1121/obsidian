---
date: 2026-01-05
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 엡실론 그리디 정책
  - ε-Greedy
  - Epsilon Greedy
keywords:
  - Epsilon-Greedy
  - Soft Policy
  - Exploration
  - Exploitation
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 5
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Epsilon-Greedy Policy

```ad-note
title: Summary
collapse: false

- ==Soft policy: 모든 action에 양의 확률을 부여하는 확률적 정책==
- ==Greedy action에 높은 확률, 나머지 action에 균등한 낮은 확률 배분==
- ==$\epsilon = 0$이면 greedy, $\epsilon = 1$이면 uniform random==
- ==Exploration-Exploitation trade-off 조절의 핵심 도구==
```

## Definition

==모든 action에 양의 확률을 부여하면서, greedy action에 가장 높은 확률을 주는 확률적 정책==

$$\pi(a|s) = \begin{cases} 1 - \epsilon + \frac{\epsilon}{|\mathcal{A}(s)|}, & a = a^* \text{ (greedy action)} \\ \frac{\epsilon}{|\mathcal{A}(s)|}, & a \neq a^* \end{cases}$$

where $a^* = \arg\max_a q(s,a)$, $\epsilon \in [0, 1]$

```ad-info
title: Note - Soft Policy

==모든 상태에서 모든 action에 양의 확률을 부여==하는 정책:

$$\pi(a|s) > 0, \quad \forall s \in \mathcal{S}, \forall a \in \mathcal{A}(s)$$

ε-greedy는 대표적인 soft policy로, deterministic greedy 정책과 달리 ==에피소드 진행 중 탐색 가능== → [[Monte Carlo Methods|MC Exploring Starts]]의 한계 극복
```

<br/><br/>

## Properties

| $\epsilon$ | 정책 특성 | Greedy action 확률 | Exploration | Exploitation |
|:---|:---|:---|:---|:---|
| $0$ | ==Greedy== | $1$ | 없음 | 최대 |
| $1$ | ==Uniform random== | $\frac{1}{\|\mathcal{A}(s)\|}$ | 최대 | 없음 |
| $0 < \epsilon < 1$ | 혼합 | $1 - \epsilon + \frac{\epsilon}{\|\mathcal{A}(s)\|}$ | 중간 | 중간 |

**Greedy Dominance**: 모든 $\epsilon \in [0, 1]$에서 greedy action 확률 $\geq$ 다른 action 확률

<br/>

### Action Selection

실제 구현에서의 action 선택 방법:

1. $[0,1]$ 균등분포에서 random number $x$ 생성
2. $x \geq \epsilon$: ==greedy action== $a^*$ 선택
3. $x < \epsilon$: $\mathcal{A}(s)$에서 ==uniform random== 선택 (greedy 포함)

→ 결과적으로 Definition의 확률 분포와 일치

<br/><br/>

## ε의 영향

[[Exploration vs Exploitation]] trade-off에서 ε는 균형을 조절:

| ε | Optimality | Exploration |
|:---|:---|:---|
| **작음** (→0) | ==높음== | 낮음 |
| **큼** (→1) | 낮음 | ==높음== |

```ad-example
title: Example - Optimality by ε
collapse: true

![[Pasted image 20260106022419.png|500]]

**설정**: 5×5 Grid World, $r_{\text{forbidden}} = -10$, $r_{\text{target}} = 1$, $\gamma = 0.9$

---

**Consistent ε-greedy policies의 state value 변화**:

| $\epsilon$ | Target state value | 전체 경향 |
|:---|:---|:---|
| $0$ | $10.0$ | 최대 |
| $0.1$ | $3.4$ | 높음 |
| $0.2$ | $-2.5$ | 감소 |
| $0.5$ | $-17.0$ | ==크게 감소== |

→ ε 증가 시 forbidden area 진입 확률 증가 → 음의 보상

---

**Optimal ε-greedy policies의 불일치**:

| $\epsilon$ | Optimal greedy와 일치 | 특징 |
|:---|:---|:---|
| $0$ | ✓ | 최적 정책 |
| $0.1$ | ✓ | 대부분 일치 |
| $0.2$ | ✗ | ==불일치 시작== |
| $0.5$ | ✗ | target에서 escape 선택 |
```

```ad-example
title: Example - Exploration Ability by ε
collapse: true

![[Pasted image 20260106022350.png|500]]

**설정**: 5×5 Grid World, 단일 에피소드 (1백만 step)

---

**ε = 1.0 (Uniform Random)**:
- 모든 $(s,a)$ 쌍 방문 횟수: ==거의 균등== (~8000회/쌍)

**ε = 0.5**:
- 방문 분포: ==극도로 불균등== (일부 250,000회 이상, 다수 수십~수백 회)
- Greedy action 편향으로 인한 불균형
```

<br/><br/>

## ε-Decay

실무에서는 ==ε를 점진적으로 감소==: 초기 exploration → 후기 exploitation/optimality

<br/><br/>

## Related Concepts

- [[Monte Carlo Methods]]: MC ε-Greedy 알고리즘에서 soft policy로 사용
- [[Sarsa]]: On-Policy TD Control에서 ε-greedy 사용
- [[Q-Learning]]: ε-greedy를 behavior policy로 사용
- [[Exploration vs Exploitation]]: ε-greedy가 해결하는 핵심 trade-off
- [[Bellman Optimality Equation]]: Greedy action $a^* = \arg\max_a q(s,a)$ 도출 근거
