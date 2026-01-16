---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - Q러닝
keywords:
  - Q-Learning
  - Off-Policy
  - TD Control
  - Bellman Optimality Equation
  - Optimal Action Value
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

# Q-Learning

```ad-note
title: Summary
collapse: true

- ==Q-Learning: 최적 Action Value $q^*(s,a)$를 추정하는 Off-Policy TD Control 알고리즘==
- ==TD Target $\bar{q}_t = r_{t+1} + \gamma \max_a q_t(s_{t+1}, a)$: 최적 행동 가정==
- ==[[Bellman Optimality Equation]]을 [[Stochastic Approximation|Robbins-Monro]]로 해결==
- ==RM 수렴 조건 + 모든 $(s,a)$ 무한 방문 시 $q^*$로 수렴 보장==
```

## Definition

==[[Bellman Optimality Equation]]을 직접 풀어 최적 action value $q^*(s,a)$를 추정하는 [[On-Policy vs Off-Policy#Off-Policy|Off-Policy]] TD Control==

$$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha \underbrace{[q_t(s_t, a_t) - (r_{t+1} + \gamma \max_a q_t(s_{t+1}, a))]}_{\text{TD Error } \delta_t}$$

- ==$q_t(s,a)$: 시간 $t$에서 $q^*(s,a)$의 추정치==
- BOE의 해 $q^*$는 ==정의상 최적 action value== → $q^*$를 알면 $\pi^*(s) = \arg\max_a q^*(s,a)$
- ==별도의 Policy Improvement 불필요== ([[Value Iteration]]과 유사)

| | [[Temporal Difference Learning\|TD(0)]] | [[Sarsa]] | Q-Learning |
|:---|:---|:---|:---|
| **추정 대상** | State value $v_\pi(s)$ | Action value $q_\pi(s,a)$ | ==최적 $q^*(s,a)$== |
| **해결 방정식** | [[Bellman Equation]] | [[Bellman Equation]] | ==[[Bellman Optimality Equation]]== |
| **Policy 유형** | On-Policy | On-Policy | ==Off-Policy== |
| **최적화 방식** | — | ==GPI== (PE + PI 반복) | ==BOE 직접 해결== |

```ad-info
title: Note - Name Origin

Q-Learning의 "Q"는 ==Quality==를 의미 — action의 quality (가치)를 추정
```

<br/><br/>

## Components

Q-Learning이 해결하는 [[Bellman Optimality Equation#Action Value Form|Action Value BOE]]:

$$q(s,a) = \mathbb{E}[R + \gamma \max_{a'} q(S', a') | s, a] \quad \text{for all } (s,a)$$

- $\max_{a'}$: 다음 상태에서 ==최적 행동을 선택한다고 가정==
- [[Sarsa]]의 [[Bellman Equation]]과 달리 ==직접 최적 가치 도출==

```ad-important
title: Proof - Equivalence to State Value BOE
collapse: true

위 Action Value 형태가 State Value BOE와 동치임을 보이는 유도:

---

**Step 1**: 기대값을 elementwise form으로 전개

$$q(s, a) = \sum_{r} p(r | s, a) r + \gamma \sum_{s'} p(s' | s, a) \max_{a' \in \mathcal{A}(s')} q(s', a')$$

---

**Step 2**: 양변에 $\max_{a \in \mathcal{A}(s)}$ 적용

$$\max_{a \in \mathcal{A}(s)} q(s, a) = \max_{a \in \mathcal{A}(s)} \left[ \sum_{r} p(r | s, a) r + \gamma \sum_{s'} p(s' | s, a) \max_{a' \in \mathcal{A}(s')} q(s', a') \right]$$

---

**Step 3**: $v(s) \doteq \max_{a \in \mathcal{A}(s)} q(s, a)$ 정의 후 대입

$$v(s) = \max_{a \in \mathcal{A}(s)} \left[ \sum_{r} p(r | s, a) r + \gamma \sum_{s'} p(s' | s, a) v(s') \right]$$

→ ==State value에 대한 Bellman Optimality Equation과 정확히 일치== $\square$
```

<br/>

### TD Target

$$\bar{q}_t = r_{t+1} + \gamma \max_a q_t(s_{t+1}, a)$$

- 즉각 보상 + 할인된 다음 상태의 ==최대 추정 가치==
- ==실제 선택한 $a_{t+1}$와 무관==하게 $\max$ 연산 (Off-Policy 특성)

<br/>

### TD Error

$$\delta_t = q_t(s_t, a_t) - (r_{t+1} + \gamma \max_a q_t(s_{t+1}, a))$$

- TD Target과 현재 추정치의 차이
- 학습 방향과 크기 결정

```ad-info
title: Note - TD Error from Contraction Mapping

[[Contraction Mapping Theorem]]에서 TD Error 형태가 자연스럽게 유도됨:

**BOE의 고정점 형태**:
$$q = \underbrace{r + \gamma \max_{a'} q(s', a')}_{T(q)} \quad \Rightarrow \quad T(q) = q$$

[[Contraction Mapping Theorem]]이 ==고정점 $q^*$의 존재와 유일성을 보장==

**Root-finding 변환**:
$$T(q) = q \quad \Rightarrow \quad q - T(q) = 0$$

→ ==TD Error $\delta = q - (r + \gamma \max q')$는 $q - T(q)$의 샘플 버전==

[[Stochastic Approximation]]으로 이 root를 찾으면 Q-Learning 알고리즘 도출
```

```ad-important
title: Proof - Algorithm Derivation
collapse: true

**Step 1**: BOE를 root-finding 형태로 변환

$$g(q(s,a)) \doteq q(s,a) - \mathbb{E}[R_{t+1} + \gamma \max_{a'} q(S_{t+1}, a') | s, a] = 0$$

---

**Step 2**: Noisy observation 구성

샘플 $(s_t, a_t, r_{t+1}, s_{t+1})$로부터:

$$\tilde{g}(q(s_t, a_t)) = q(s_t, a_t) - [r_{t+1} + \gamma \max_a q(s_{t+1}, a)]$$

---

**Step 3**: RM 알고리즘 적용

$$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha_t(s_t, a_t) \tilde{g}(q_t(s_t, a_t))$$

→ ==Q-Learning 알고리즘의 수식과 정확히 일치==
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Q-Learning

**입력**: 학습률 $\alpha > 0$, 탐색 파라미터 $\epsilon \in (0,1)$

**초기화**: $q_0(s,a)$ 임의 설정, $q_0$로부터 $\epsilon$-greedy 행동 정책 $\pi_b$ 유도

**For** each episode:
- 초기 상태 $s_0$ 관측
- **While** $s_t$가 종료 상태가 아닐 때:
   - **경험 샘플 수집** $(r_{t+1}, s_{t+1})$:
     - 행동 정책 $\pi_b$로 $a_t$ 선택 (e.g., $\epsilon$-greedy)
     - $(s_t, a_t)$에서 환경과 상호작용 → $(r_{t+1}, s_{t+1})$ 관측
   - **Q-value 업데이트**:
     $$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha[q_t(s_t, a_t) - (r_{t+1} + \gamma \max_a q_t(s_{t+1}, a))]$$
   - **미방문 상태-행동 유지**:
     $$q_{t+1}(s, a) = q_t(s, a) \quad \text{for all } (s, a) \neq (s_t, a_t)$$
   - **행동 정책 업데이트** ($\epsilon$-greedy):
     $$\pi_b(a|s_t) = \begin{cases} 1 - \frac{\epsilon}{|\mathcal{A}(s_t)|}(|\mathcal{A}(s_t)| - 1), & \text{if } a = \arg\max_a q_{t+1}(s_t, a) \\ \frac{\epsilon}{|\mathcal{A}(s_t)|}, & \text{otherwise} \end{cases}$$
   - $s_t \leftarrow s_{t+1}$

**출력**: 최적 정책 $\pi^*(s) = \arg\max_a q(s,a)$
```

```ad-warning
title: Note - Unvisited State-Action Update Rule

미방문 상태-행동 유지 수식은 간결함을 위해 자주 생략되지만, ==수학적 완전성을 위해 반드시 필요==:

- 시간 $t$에서 ==방문한 $(s_t, a_t)$만 업데이트==됨
- 미방문 $(s, a) \neq (s_t, a_t)$의 Q값은 ==변하지 않음==
```

```ad-info
title: Note - No Next Action Required

Q-Learning은 ==$(s_t, a_t, r_{t+1}, s_{t+1})$ 4-tuple만 필요== ($a_{t+1}$ 불필요):

- [[Sarsa]]: $(s_t, a_t, r_{t+1}, s_{t+1}, a_{t+1})$ 5-tuple 필요
- Q-Learning: $\max_a q(s_{t+1}, a)$ 계산에 ==실제 $a_{t+1}$ 선택 불필요==

→ 사전 수집된 데이터로도 학습 가능 ([[On-Policy vs Off-Policy#Off-Policy|Off-Policy]] 장점)
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - Q-Learning Convergence

Q-Learning 알고리즘에 의해 $q_t(s,a)$는 다음 조건 하에서 ==모든 $(s,a)$에 대해 $q^*(s,a)$로 almost surely 수렴==:

$$\sum_{t} \alpha_t(s,a) = \infty, \quad \sum_{t} \alpha_t^2(s,a) < \infty \quad \text{for all } (s,a)$$

**조건 해석**:
- $\alpha_t(s,a) > 0$ if $(s,a) = (s_t, a_t)$ (방문), $\alpha_t(s,a) = 0$ otherwise (미방문)
- $\sum \alpha_t(s,a) = \infty$: ==모든 상태-행동 쌍이 무한 번 방문==되어야 함
- [[Epsilon-Greedy Policy|ε-greedy]] 같은 exploratory behavior policy 필요
```

```ad-important
title: Proof - Q-Learning Convergence
collapse: true

[[Dvoretzky's Theorem]]를 사용하여 증명. 목표: 세 가지 조건이 만족됨을 보이면 $\Delta_t(s,a) \to 0$ a.s.

---

**Step 1**: 오차 정의

$$\Delta_t(s,a) \doteq q_t(s,a) - q^*(s,a)$$

---

**Step 2**: 오차 동역학

Q-Learning 알고리즘에서 $q^*(s,a)$를 양변에서 빼면:

**Case 1** ($(s,a) = (s_t, a_t)$, 방문):

$$\Delta_{t+1}(s,a) = (1 - \alpha_t(s,a))\Delta_t(s,a) + \alpha_t(s,a)\underbrace{(r_{t+1} + \gamma \max_{a'} q_t(s_{t+1}, a') - q^*(s,a))}_{\eta_t(s,a)}$$

**Case 2** ($(s,a) \neq (s_t, a_t)$, 미방문):

$$\Delta_{t+1}(s,a) = \Delta_t(s,a) = (1 - \alpha_t(s,a))\Delta_t(s,a) + \alpha_t(s,a)\eta_t(s,a)$$

($\alpha_t(s,a) = 0$, $\eta_t(s,a) = 0$이므로 Case 1과 ==동일한 형태==)

---

**Step 3**: Dvoretzky 조건 검증

**(a) Step size 조건**: $\sum_t \alpha_t(s,a) = \infty$, $\sum_t \alpha_t^2(s,a) < \infty$ — 가정에 의해 만족

**(b) Contraction 조건**: $\|\mathbb{E}[\eta_t(s,a) | H_t]\|_\infty \leq \gamma \|\Delta_t\|_\infty$

**Case 1** ($(s,a) \neq (s_t, a_t)$):

$\eta_t(s,a) = 0$이므로:

$$|\mathbb{E}[\eta_t(s,a)]| = 0 \leq \gamma \|\Delta_t\|_\infty$$

**Case 2** ($(s,a) = (s_t, a_t)$):

$$\begin{aligned}
\mathbb{E}[\eta_t(s_t, a_t)] &= \mathbb{E}[r_{t+1} + \gamma \max_{a'} q_t(s_{t+1}, a') - q^*(s_t, a_t) | s_t, a_t] \\
&= \mathbb{E}[r_{t+1} + \gamma \max_{a'} q_t(s_{t+1}, a') | s_t, a_t] - q^*(s_t, a_t)
\end{aligned}$$

BOE $q^*(s_t, a_t) = \mathbb{E}[r_{t+1} + \gamma \max_{a'} q^*(s_{t+1}, a') | s_t, a_t]$를 대입:

$$\begin{aligned}
\mathbb{E}[\eta_t(s_t, a_t)] &= \gamma \mathbb{E}[\max_{a'} q_t(s_{t+1}, a') - \max_{a'} q^*(s_{t+1}, a') | s_t, a_t]
\end{aligned}$$

$\max$ 연산의 non-expansion 성질 $|\max_a f(a) - \max_a g(a)| \leq \max_a |f(a) - g(a)|$에 의해:

$$\begin{aligned}
|\mathbb{E}[\eta_t(s_t, a_t)]| &\leq \gamma \mathbb{E}[\max_{a'} |q_t(s_{t+1}, a') - q^*(s_{t+1}, a')| | s_t, a_t] \\
&\leq \gamma \|\Delta_t\|_\infty
\end{aligned}$$

두 케이스를 종합하면 $\|\mathbb{E}[\eta_t(s,a)]\|_\infty \leq \gamma \|\Delta_t\|_\infty$

**(c) 유한 분산**: $\text{var}[\eta_t(s,a) | H_t] < \infty$

$r_{t+1}$이 bounded이므로 $\eta_t(s,a)$도 bounded → 분산 유한

---

**결론**: 세 조건 만족 → Dvoretzky's Theorem에 의해 $\Delta_t(s,a) \to 0$ a.s. for all $(s,a)$ $\square$
```

<br/>

### Practical Step Sizes

| Step Size | 조건 만족 | 특성 |
|:---|:---|:---|
| $\alpha_k = 1/k$ | ==만족== | 이론적 보장, 느린 수렴 |
| $\alpha_k = \alpha$ (상수) | ==불만족== | 빠른 적응, non-stationary에 유리 |

<br/><br/>

## Off-Policy Characteristic

==Q-Learning은 [[On-Policy vs Off-Policy#Off-Policy|Off-Policy]]: 행동 정책 $\pi_b$와 목표 정책 $\pi^*$가 다름==

| 정책 | 역할 | Q-Learning에서 |
|:---|:---|:---|
| **Behavior Policy $\pi_b$** | 경험 샘플 생성 | $\epsilon$-greedy 또는 임의 정책 |
| **Target Policy $\pi^*$** | 학습 목표 | Greedy: $\arg\max_a q(s,a)$ |

Q-Learning의 샘플 생성: $s_t \xrightarrow{\pi_b} a_t \xrightarrow{\text{model}} r_{t+1}, s_{t+1}$

- $a_t$만 $\pi_b$가 생성, ==$(r_{t+1}, s_{t+1})$은 환경 모델이 결정== ($\pi_b$ 무관)
- 최적 action value 추정이 ==$\pi_b$에 의존하지 않음== → $\pi_b \neq \pi^*$여도 학습 가능
- **근본적 이유**: ==[[Bellman Optimality Equation|BOE]]는 특정 정책에 의존하지 않음==

<br/>

### Off-Policy Advantages

- ==사전 수집 데이터== (다른 정책이 생성)로 학습 가능
- ==탐색 정책 분리==: 강한 탐색 $\pi_b$ 사용하면서 최적 $\pi^*$ 학습
- ==Human demonstration== 데이터 활용 가능

```ad-warning
title: Note - Exploration Requirement

Off-Policy라도 ==모든 $(s,a)$ 무한 방문== 조건은 필수:
- Behavior policy $\pi_b$가 충분히 탐색적이어야 함
- $\epsilon = 0$ (순수 Greedy)이면 ==수렴 보장 안 됨==
- [[Epsilon-Greedy Policy#ε-Decay|ε-Decay]]로 초기 탐색 → 후기 활용 전환
```

<br/>

### Implementation Fashions

Q-Learning ==알고리즘 자체==는 Off-Policy이지만, ==사용 방식==은 선택 가능:

| | On-Policy Fashion | Off-Policy Fashion |
|:---|:---|:---|
| **Behavior Policy** | ε-greedy | $\pi_b$ (임의) |
| **Target Policy** | ==ε-greedy (동일)== | ==Greedy (분리)== |
| **정책 관계** | $\pi_b = \pi_T$ | $\pi_b \neq \pi_T$ |

```ad-tldr
title: Algorithm - Q-Learning (On-Policy Fashion)
collapse: true

**입력**: $\alpha > 0$, $\epsilon \in (0,1)$, 초기 $q_0(s,a)$, 초기 ε-greedy 정책 $\pi_0$

**목표**: 초기 상태 $s_0$에서 목표 상태까지의 ==최적 경로 학습==

**For** each episode:
- **While** $s_t$가 종료 상태가 아닐 때:
  - **Collect experience**: $a_t \sim \pi_t(s_t)$ (==behavior = target = ε-greedy==), $(r_{t+1}, s_{t+1})$ 관측
  - **Update q-value**:
    $$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha[q_t(s_t, a_t) - (r_{t+1} + \gamma \max_a q_t(s_{t+1}, a))]$$
  - **Update policy** ($\epsilon$-greedy from $q_{t+1}$)
```

```ad-tldr
title: Algorithm - Q-Learning (Off-Policy Fashion)
collapse: true

**입력**: 초기 $q_0(s,a)$, ==behavior policy $\pi_b(a|s)$==, $\alpha > 0$

**목표**: $\pi_b$가 생성한 경험 샘플로부터 ==target policy $\pi_T$ 학습==

**For** each episode generated by ==$\pi_b$==:
- **For** each step $t$:
  - **Update q-value**:
    $$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha[q_t(s_t, a_t) - (r_{t+1} + \gamma \max_a q_t(s_{t+1}, a))]$$
  - **Update target policy** (==Greedy==):
    $$\pi_T(a|s_t) = \begin{cases} 1, & a = \arg\max_a q_{t+1}(s_t, a) \\ 0, & \text{otherwise} \end{cases}$$

**핵심**: ==Q-value 업데이트 수식 동일==, 정책 관계만 다름 ($\pi_b = \pi_T$ vs $\pi_b \neq \pi_T$)
```

<br/><br/>

## Comparison with Sarsa

| | Q-Learning | [[Sarsa]] |
|:---|:---|:---|
| **유형** | ==Off-Policy== | ==On-Policy== |
| **TD Target** | $r + \gamma \max_{a'} q(s', a')$ | $r + \gamma q(s', a')$ where $a' \sim \pi$ |
| **$a'$ 선택** | 최적 행동 (max) | 실제 선택한 행동 |
| **해결 방정식** | [[Bellman Optimality Equation]] | [[Bellman Equation]] |
| **수렴 대상** | 최적 정책의 $q^*$ | 현재 정책의 $q_\pi$ |
| **최적화 방식** | ==BOE 직접 해결== | ==GPI== (평가 + 개선 반복) |
| **탐색 영향** | Q값에 반영 안 됨 | Q값에 ==반영됨== |
| **안전성** | 낮음 (최적만 고려) | ==높음== (탐색 위험 고려) |

<br/><br/>

## Related Concepts

- [[Temporal Difference Learning]]: Q-Learning의 기반 — TD 방식으로 bootstrapping
- [[Sarsa]]: On-Policy TD Control, BE 해결 (Q-Learning은 BOE)
- [[Bellman Optimality Equation]]: Q-Learning이 해결하는 방정식
- [[Stochastic Approximation]]: Q-Learning 수렴의 이론적 기반 (Robbins-Monro)
- [[Dvoretzky's Theorem]]: Q-Learning 수렴 증명에 사용
- [[Value Iteration]]: Model-based BOE 해결 — Q-Learning과 유사한 최적화 방식
- [[On-Policy vs Off-Policy]]: Q-Learning은 Off-Policy
- [[Deep Q-Learning]]: Q-Learning의 FA 확장 — Neural Network + Target Network + Experience Replay
- [[Sarsa with Function Approximation]]: On-Policy FA 대안 (Deadly Triad 문제 없음)

