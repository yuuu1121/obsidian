---
date: 2026-01-09
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - Greedy Optimal Policy
  - 탐욕적 정책
keywords:
  - Greedy Policy
  - Optimal Policy
  - Policy Extraction
  - Deterministic Policy
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 3
author:
url:
---

# Greedy Policy

```ad-note
title: Summary
collapse: true

- ==Greedy policy: 주어진 value function에서 $q(s,a)$를 최대화하는 행동을 선택하는 결정적 정책==
- ==Greedy optimal policy: $q^*$에 대해 greedy한 정책 — BOE에서 최적임이 증명됨==
- ==$q^*$만 알면 모델 없이 최적 정책 추출 가능== → [[Q-Learning]]의 핵심
- ==일반적 greedy는 local optimum 위험이 있으나, $q^*$가 미래 보상을 반영하므로 global optimum 보장==
```

## Definition

==주어진 action value $q(s,a)$를 최대화하는 행동을 확률 1로 선택하는 결정적 정책==

$$\pi_{\text{greedy}}(a|s) = \begin{cases} 1, & a = \arg\max_a q(s, a) \\ 0, & \text{otherwise} \end{cases}$$

- =="Greedy"==: 현재 value function 기준으로 ==즉각적으로 최선==인 행동 선택
- ==Deterministic==: 각 상태에서 항상 동일한 행동 선택 (확률 1)
- ==임의의 $q$에 대해 정의 가능== — $q$가 $q^*$일 필요 없음

```ad-warning
title: Note - Exploration Problem

==Deterministic policy의 한계==: 각 상태에서 ==항상 동일한 행동만 선택==하므로:

- ==사각지대 발생==: greedy action이 아닌 행동의 가치를 평가할 기회 없음
- ==탐색 불가==: 에피소드 진행 중 다른 action 시도 불가능
- ==초기 추정치 의존==: $q$ 추정이 부정확하면 suboptimal action에 고착

→ 해결책: [[Epsilon-Greedy Policy]] — $1-\epsilon$ 확률로 greedy, $\epsilon$ 확률로 ==랜덤 탐색==
```

```ad-warning
title: Note - Greedy Policy vs Greedy Optimal Policy

| 용어 | Value Function | 최적 보장 |
|:---|:---|:---|
| **Greedy Policy** | 임의의 $q$ (예: $q_{\pi_k}$) | ==보장 안 됨== |
| **Greedy Optimal Policy** | ==$q^*$ (최적 action value)== | ==최적 보장== |

- [[Policy Iteration]]의 Policy Improvement: $q_{\pi_k}$에 대해 greedy → 현재보다 ==개선된== 정책
- [[Value Iteration]], [[Q-Learning]]: $q^*$에 대해 greedy → ==최적== 정책
```

<br/><br/>

## Greedy Optimal Policy

==$q^*$에 대해 greedy한 정책은 최적 정책==

$$\pi^*(a|s) = \begin{cases} 1, & a = \arg\max_a q^*(s, a) \\ 0, & \text{otherwise} \end{cases}$$

<br/>

### Optimality

[[Bellman Optimality Equation|BOE]]:

$$v(s) = \max_{\pi(s) \in \Pi(s)} \sum_{a \in \mathcal{A}} \pi(a|s) q(s, a)$$

$\sum_a \pi(a|s) q(s,a)$는 ==가중 평균==이므로 상한은 $\max_a q(s,a)$

→ $a^* = \arg\max_a q(s,a)$에 확률 1을 부여하면 ==상한 달성== → ==Greedy policy가 BOE를 최대화==

```ad-important
title: Proof - Greedy Policy Maximizes BOE
collapse: true

**Goal**: $\sum_a \pi(a|s) = 1$, $\pi(a|s) \geq 0$ 제약 하에서 $\sum_a \pi(a|s) q(s,a)$를 최대화하는 $\pi$ 찾기

---

**Step 1**: 상한 설정

$q_{\max} \doteq \max_a q(s,a)$라 하면:

$$\sum_a \pi(a|s) q(s,a) \leq \sum_a \pi(a|s) q_{\max} = q_{\max} \cdot \underbrace{\sum_a \pi(a|s)}_{=1} = q_{\max}$$

---

**Step 2**: 등호 조건

등호가 성립하려면 $\pi(a|s) > 0$인 모든 $a$에 대해 $q(s,a) = q_{\max}$

→ $a^* = \arg\max_a q(s,a)$에 $\pi(a^*|s) = 1$ 부여 시 등호 성립

**결론**: Greedy policy가 BOE를 최대화 $\square$
```

```ad-important
title: Theorem - Optimality of Greedy Policy

$q^*$에 대한 greedy 정책 $\pi^*(s) = \arg\max_a q^*(s, a)$는 ==최적 정책==

임의의 정책 $\pi$에 대해: $v^* = v_{\pi^*} \geq v_\pi$
```

```ad-important
title: Proof - Optimality
collapse: true

**Step 1**: BOE에서 $\pi^*$가 최대화하므로:

$$v^* = \max_\pi (r_\pi + \gamma P_\pi v^*) \geq r_\pi + \gamma P_\pi v^*$$

---

**Step 2**: 임의의 정책 $\pi$에 대해 [[Bellman Equation]] $v_\pi = r_\pi + \gamma P_\pi v_\pi$이므로:

$$v^* - v_\pi \geq (r_\pi + \gamma P_\pi v^*) - (r_\pi + \gamma P_\pi v_\pi) = \gamma P_\pi (v^* - v_\pi)$$

---

**Step 3**: 반복 적용:

$$v^* - v_\pi \geq \gamma^n P_\pi^n (v^* - v_\pi) \xrightarrow{n \to \infty} 0$$

($\gamma < 1$, $P_\pi^n$ 유계)

**결론**: $v^* \geq v_\pi$ for any $\pi$ $\square$
```

```ad-info
title: Note - Why Greedy on $q^*$ Guarantees Global Optimum

일반적으로 greedy는 ==local optimum== 위험이 있으나, $q^*$는 ==미래 보상의 기대값==을 이미 반영:

$$q^*(s,a) = \mathbb{E}[R_{t+1} + \gamma R_{t+2} + \cdots | S_t = s, A_t = a]$$

→ $q^*$에 대해 greedy하면 ==global optimum== 보장
```

<br/><br/>

## Policy Extraction

$v^*$ 또는 $q^*$를 구한 후, ==greedy policy 추출==로 최적 정책 도출

### Elementwise Form

$$\pi^*(s) = \arg\max_{a \in \mathcal{A}} q^*(s, a)$$

$v^*$만 아는 경우, action value 계산 필요:

$$q^*(s, a) = \sum_{r \in \mathcal{R}} p(r|s, a)r + \gamma \sum_{s' \in \mathcal{S}} p(s'|s, a)v^*(s')$$

### Matrix-Vector Form

$$\pi^* = \arg\max_{\pi \in \Pi} (r_\pi + \gamma P_\pi v^*)$$

<br/>

### Model Requirement

| 조건 | 필요 정보 | 알고리즘 예시 |
|:---|:---|:---|
| $v^*$만 아는 경우 | ==환경 모델 필요== | [[Value Iteration]], [[Policy Iteration]] |
| $q^*$를 아는 경우 | ==모델 불필요== | [[Q-Learning]] |

```ad-info
title: Note - Why Q-Learning Learns $q^*$ Directly

$q^*$를 직접 학습하면:
- 정책 추출 시 $\pi^*(s) = \arg\max_a q^*(s,a)$만 계산
- ==환경 모델 $p(r|s,a)$, $p(s'|s,a)$ 불필요==

→ Model-free RL에서 $q^*$ 학습이 핵심인 이유
```

<br/><br/>

## Uniqueness

```ad-info
title: Note - $v^*$ is Unique, $\pi^*$ May Not Be

**$v^*$의 유일성**: [[Contraction Mapping Theorem]]에 의해 BOE의 고정점은 ==유일==

**$\pi^*$의 비유일성**: 동일한 최대 $q^*$를 가진 action이 여러 개일 때 ==다수의 최적 정책 존재==

$$\text{예: } q^*(s, a_1) = q^*(s, a_2) = \max_a q^*(s, a)$$

이 경우 $\pi^*(a_1|s) = 1$ 또는 $\pi^*(a_2|s) = 1$ 모두 최적

→ 알고리즘에서는 보통 ==tie-breaking rule== 적용 (예: 첫 번째 최대값 선택)
```

<br/><br/>

## Applications

| 알고리즘 | Value Function | Greedy Policy 역할 |
|:---|:---|:---|
| [[Value Iteration]] | $q_k$ → $q^*$ | 매 iteration greedy 업데이트로 $v^*$ 수렴 |
| [[Policy Iteration]] | $q_{\pi_k}$ | Policy Improvement: 현재 정책보다 ==개선== |
| [[Q-Learning]] | $q^*$ | 학습된 $q^*$에서 ==최적== 정책 추출 |
| [[Sarsa]] | $q_\pi$ | [[Epsilon-Greedy Policy]]로 탐색-활용 균형 |

<br/><br/>

## Related Concepts

- [[Bellman Optimality Equation]]: Greedy policy가 최적임을 유도하는 방정식
- [[Policy#Optimal Policy|Optimal Policy]]: Greedy optimal policy의 상위 개념
- [[Value Function#Optimal Value Functions|Optimal Value Function]]: Greedy policy 도출의 기반 ($v^*$, $q^*$)
- [[Value Iteration]]: BOE 반복으로 $v^*$ 계산 후 greedy 추출
- [[Policy Iteration#Policy Improvement|Policy Improvement]]: $q_{\pi_k}$에 대해 greedy → 정책 개선
- [[Q-Learning]]: $q^*$ 직접 학습 → 모델 없이 greedy 추출
- [[Epsilon-Greedy Policy]]: Greedy + $\epsilon$ 확률 랜덤 탐색
- [[Contraction Mapping Theorem]]: $v^*$ 유일성 보장

