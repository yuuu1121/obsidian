---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - SARSA
  - State-Action-Reward-State-Action
keywords:
  - Sarsa
  - TD Control
  - On-Policy
  - Action Value
  - Stochastic Approximation
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

# Sarsa (State-Action-Reward-State-Action)

```ad-note
title: Summary
collapse: true

- ==Sarsa: 주어진 정책 $\pi$의 Action Value $q_\pi(s,a)$를 추정하는 On-Policy TD 알고리즘==
- ==TD Target $\bar{q}_t = r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1})$: 실제 선택한 다음 행동 사용==
- ==Sarsa 자체는 Policy Evaluation — 최적 정책을 위해 GPI와 결합 필요==
```

## Definition

주어진 정책 $\pi$의 action value $q_\pi(s,a)$를 추정하는 ==[[On-Policy vs Off-Policy|On-Policy]] TD 알고리즘==

$$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha \underbrace{[q_t(s_t, a_t) - (r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1}))]}_{\text{TD Error } \delta_t}$$

- ==$q_t(s,a)$: 시간 $t$에서 $q_\pi(s,a)$의 추정치==
- 현재 정책을 따라 ==실제 선택한 행동== $a_{t+1}$로 업데이트 (On-Policy)

| | [[Temporal Difference Learning\|TD(0)]] | Sarsa |
|:---|:---|:---|
| **추정 대상** | State value $v_\pi(s)$ | ==Action value $q_\pi(s,a)$== |
| **용도** | 정책 평가 | 정책 평가 + ==GPI== |

```ad-warning
title: Note - Sarsa is Policy Evaluation

==Sarsa 자체는 주어진 정책 $\pi$의 $q_\pi$만 추정== (Policy Evaluation):
- [[Q-Learning]]처럼 ==최적 $q^*$를 직접 추정하지 않음==
- 최적 정책을 찾으려면 ==Policy Improvement와 결합== 필요 ([[Policy Iteration#Generalized Policy Iteration|GPI]])
```

```ad-info
title: Note - Name Origin

==S==tate → ==A==ction → ==R==eward → ==S==tate → ==A==ction

각 업데이트에 $(s_t, a_t, r_{t+1}, s_{t+1}, a_{t+1})$ 5-tuple 필요
```

<br/><br/>

## Components

Sarsa가 해결하는 [[Bellman Equation#Action Value Form|Action Value Bellman Equation]]:

$$q_\pi(s,a) = \mathbb{E}[R + \gamma q_\pi(S', A') | s, a] \quad \text{for all } (s,a)$$

```ad-important
title: Proof - Bellman Equation Equivalence
collapse: true

**Elementwise form** 전개:

$$q_\pi(s,a) = \sum_r rp(r|s,a) + \gamma \sum_{s'} p(s'|s,a) \sum_{a'} q_\pi(s',a')\pi(a'|s')$$

---

**조건부 독립성**으로 joint probability 분해:

$$p(s', a' | s, a) = p(s' | s, a)\pi(a' | s')$$

- $a'$는 $s'$에서 정책 $\pi$에 의해 선택되므로, $(s, a)$와 ==[[Conditional Independence|조건부 독립]]==

---

**Expectation form으로 변환**:

$$q_\pi(s, a) = \sum_r rp(r | s, a) + \gamma \sum_{s'} \sum_{a'} q_\pi(s', a')p(s', a' | s, a)$$

기댓값 정의에 의해 $\mathbb{E}[R + \gamma q_\pi(S', A') | s, a]$와 동치 $\square$
```

<br/>

### TD Target

$$\bar{q}_t = r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1})$$

- 즉각 보상 + 할인된 다음 상태-행동의 추정 가치
- ==실제 정책이 선택한 $a_{t+1}$ 사용== (On-Policy 특성)

<br/>

### TD Error

$$\delta_t = q_t(s_t, a_t) - (r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1}))$$

- TD Target과 현재 추정치의 차이
- 학습 방향과 크기 결정

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Sarsa (Optimal Policy Learning)

**입력**: 학습률 $\alpha > 0$, 탐색 파라미터 $\epsilon \in (0,1)$

**초기화**: $q_0(s,a)$ 임의 설정, $q_0$로부터 $\epsilon$-greedy 정책 $\pi_0$ 유도

**For** each episode:
- 초기 상태 $s_0$에서 $a_0 \sim \pi_0(s_0)$ 생성
- **While** $s_t$가 종료 상태가 아닐 때:
   - **경험 샘플 수집**: $(s_t, a_t)$에서 $(r_{t+1}, s_{t+1})$ 관측, $a_{t+1} \sim \pi_t(s_{t+1})$ 선택
   - **Policy Evaluation** (Q-value 업데이트):
     $$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha[q_t(s_t, a_t) - (r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1}))]$$
   - **Policy Improvement** ($\epsilon$-greedy):
     $$\pi_{t+1}(s_t) = \epsilon\text{-greedy}(q_{t+1})$$
   - $s_t \leftarrow s_{t+1}$, $a_t \leftarrow a_{t+1}$

**출력**: 학습된 정책 $\pi^*$
```

```ad-info
title: Note - GPI Structure

PE와 PI를 ==매 스텝 교대 수행==하여 점진적으로 최적 정책에 수렴

- [[Dynamic Programming|DP]]의 [[Policy Iteration]]은 PE를 ==완전히 수렴==시킨 후 PI
- Sarsa는 ==단일 $(s_t, a_t)$만 부분 업데이트== 후 즉시 PI
```

```ad-info
title: Note - Exploration

On-Policy이므로 정책이 ==샘플 생성에도 사용==됨

- 수렴 조건: ==모든 $(s,a)$가 무한 번 방문==되어야 함
	- 탐색 부족 시 ==지역 최적(locally optimal)==에 수렴 가능
- 순수 Greedy는 ==탐색 불가== → ε-greedy로 탐색과 활용 균형
- **[[Epsilon-Greedy Policy#ε-Decay|ε-Decay]]**: $\epsilon$을 점진적으로 0으로 감소시켜 간헐적 성능 저하 해결
```

```ad-example
title: Example - Grid World Path Finding
collapse: true

![[Pasted image 20260108091231.png|700]]

**Task**: 시작 상태(좌상단)에서 목표 상태(파란 셀)까지 ==최적 경로 탐색==

**Setup**:
- $r_{\text{target}} = 0$, $r_{\text{forbidden}} = r_{\text{boundary}} = -10$, $r_{\text{other}} = -1$
- $\alpha = 0.1$, $\epsilon = 0.1$, $q_0(s,a) = 0$

**Results**:
- Episode 진행에 따라 total reward 증가, episode length 감소
- 간헐적 성능 저하: $\epsilon$-greedy의 무작위 행동으로 발생
```

<br/><br/>

## Convergence

==Sarsa는 Action Value [[Bellman Equation]]을 [[Stochastic Approximation#Robbins-Monro Algorithm|Robbins-Monro]]로 푸는 것==

```ad-important
title: Theorem - Sarsa Convergence

정책 $\pi$가 주어졌을 때, Sarsa 알고리즘에 의해 $q_t(s,a)$는 다음 조건 하에서 ==모든 $(s,a)$에 대해 $q_\pi(s,a)$로 almost surely 수렴==:

$$\sum_{t} \alpha_t(s,a) = \infty, \quad \sum_{t} \alpha_t^2(s,a) < \infty \quad \text{for all } (s,a)$$

**조건 해석**: ==모든 상태-행동 쌍이 무한 번 방문==되어야 함 → $\epsilon$-greedy 같은 exploratory policy 필요
```

```ad-important
title: Proof - Sarsa Convergence
collapse: true

[[Dvoretzky's Theorem]]를 사용하여 증명. 목표: 세 가지 조건이 만족됨을 보이면 $\Delta_t(s,a) \to 0$ a.s.

---

**Step 1**: 오차 정의

$$\Delta_t(s,a) \doteq q_t(s,a) - q_\pi(s,a)$$

---

**Step 2**: 오차 동역학

Sarsa 알고리즘에서 $q_\pi(s,a)$를 양변에서 빼면:

$$\Delta_{t+1}(s,a) = (1 - \alpha_t(s,a))\Delta_t(s,a) + \alpha_t(s,a)\eta_t(s,a)$$

where $\eta_t(s,a) = r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1}) - q_\pi(s,a)$

---

**Step 3**: Dvoretzky 조건 검증

**(a) Step size 조건**: 가정에 의해 만족

**(b) Contraction 조건**: $\|\mathbb{E}[\eta_t(s,a) | H_t]\|_\infty \leq \gamma \|\Delta_t\|_\infty$

Bellman equation 대입 후:

$$|\mathbb{E}[\eta_t(s_t, a_t)]| = \gamma |\mathbb{E}[q_t(s_{t+1}, a_{t+1}) - q_\pi(s_{t+1}, a_{t+1})]| \leq \gamma \|\Delta_t\|_\infty$$

**(c) 유한 분산**: $r_{t+1}$이 bounded이므로 만족

---

**결론**: Dvoretzky's Theorem에 의해 $\Delta_t(s,a) \to 0$ a.s. $\square$
```

| Step Size | 조건 만족 | 특성 |
|:---|:---|:---|
| $\alpha_k = 1/k$ | ==만족== | 이론적 보장, 느린 수렴 |
| $\alpha_k = \alpha$ (상수) | ==불만족== | 빠른 적응, non-stationary에 유리 |

<br/><br/>

## Comparison with Q-Learning

| | Sarsa | [[Q-Learning]] |
|:---|:---|:---|
| **유형** | ==On-Policy== | ==Off-Policy== |
| **TD Target** | $r + \gamma q(s', a')$ where $a' \sim \pi$ | $r + \gamma \max_{a'} q(s', a')$ |
| **해결 방정식** | [[Bellman Equation]] | [[Bellman Optimality Equation]] |
| **수렴 대상** | 현재 정책의 $q_\pi$ | 최적 정책의 $q^*$ |
| **최적화 방식** | ==GPI== (평가 + 개선 반복) | ==BOE 직접 해결== |
| **탐색 영향** | Q값에 ==반영됨== | Q값에 반영 안 됨 |
| **안전성** | ==높음== (탐색 위험 고려) | 낮음 (최적만 고려) |

```ad-info
title: Note - On-Policy Characteristic

Sarsa의 샘플 생성: $s_t \xrightarrow{\pi} a_t \to r_{t+1}, s_{t+1} \xrightarrow{\pi} a_{t+1}$

- $a_t$와 $a_{t+1}$ ==모두 동일한 정책 $\pi$가 생성== → ==평가 정책 = 샘플 생성 정책== (On-Policy)
- 탐색으로 인한 위험이 Q값에 반영됨 → 안전성이 중요한 환경에 적합
```

<br/><br/>

## Related Concepts

- [[Temporal Difference Learning]]: TD(0)의 action value 확장이 Sarsa
- [[Q-Learning]]: Off-Policy TD Control, BOE 직접 해결
- [[Expected Sarsa]]: 기댓값 TD Target으로 분산 감소
- [[n-step Sarsa]]: MC↔Sarsa 스펙트럼의 일반화
- [[Stochastic Approximation]]: Sarsa 수렴의 이론적 기반 (Robbins-Monro)
- [[Dvoretzky's Theorem]]: Sarsa 수렴 증명에 사용
- [[Bellman Equation]]: Sarsa가 해결하는 방정식
- [[On-Policy vs Off-Policy]]: Sarsa는 On-Policy
