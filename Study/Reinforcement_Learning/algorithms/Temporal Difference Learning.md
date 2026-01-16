---
date: 2026-01-07
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 시간차 학습
  - TD Learning
  - Temporal Difference
  - TD(0)
keywords:
  - Temporal Difference
  - TD(0)
  - TD Target
  - Bootstrapping
  - TD Error
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

# Temporal Difference Learning

```ad-note
title: Summary
collapse: true

- ==TD Learning: [[Bellman Equation]]을 [[Stochastic Approximation|Robbins-Monro]]로 푸는 Model-Free 방법==
- ==TD Target $\bar{v}_t = r_{t+1} + \gamma v_t(s_{t+1})$: Bellman Expectation Equation의 샘플 기반 근사==
- ==Bootstrapping: 추정치 $v(s')$로 $v(s)$ 업데이트 — MC와의 핵심 차이==
- ==Incremental Update: 매 스텝 업데이트로 Continuing tasks에도 적용 가능==
```

![[Pasted image 20260108182252.png|700]]

## Definition
<!-- Chapter 7 -->

==State value $v_\pi(s)$를 추정==하는 ==Model-Free Policy Evaluation 방법==

- [[Sarsa]], [[Q-Learning]], [[n-step Sarsa]] 등 TD 알고리즘 클래스의 기반
- **입력**: 경험 샘플 $(s_0, r_1, s_1, r_2, \ldots)$ from policy $\pi$
- **출력**: 모든 $s \in \mathcal{S}$에 대한 $v_\pi(s)$

$$v_{t+1}(s_t) = v_t(s_t) - \alpha_t \underbrace{[v_t(s_t) - (r_{t+1} + \gamma v_t(s_{t+1}))]}_{\text{TD Error } \delta_t}$$

- $v_t(s)$: 시간 $t$에서 $v_\pi(s)$의 추정치

| 특성 | 설명 |
|:---|:---|
| **Incremental** | ==매 스텝== 업데이트로 경험 즉시 반영 — 에피소드 종료 불필요 ([[Stochastic Approximation]]) |
| **Continuing Tasks** | 종료 없는 환경, 긴 에피소드에서도 적용 가능 |
| **Bootstrapping** | 추정치 $v_t(s_{t+1})$로 $v_t(s_t)$ 업데이트 — ==biased==하나 ==variance가 낮음== |
| **초기값 의존** | 초기 추정치 $v_0$가 학습에 영향 |

```ad-info
title: Note - Terminology

- **"TD" (Temporal-Difference)**: 두 시점 $t$, $t+1$ 간의 ==추정치 불일치==를 의미 ($\delta_t$)
- **"Learning"**: 수학적 관점에서 ==estimation== — 샘플로부터 value를 추정하고 점진적으로 업데이트
```

<br/><br/>

## Components

TD는 [[Bellman Equation#Bellman Expectation Form|Bellman Expectation Equation]]을 [[Stochastic Approximation#Robbins-Monro Algorithm|Robbins-Monro]]로 푸는 알고리즘

$$v_\pi(s) = \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s], \quad s \in \mathcal{S}$$

- 기대값 $\mathbb{E}[\cdot]$을 정확히 계산하려면 시스템 모델 $p(s'|s,a)$, $p(r|s,a)$가 필요
- TD는 ==Model-free==라서 모델을 모름 → ==기대값을 직접 계산할 수 없음==
- [[Stochastic Approximation]]: 기대값 대신 ==샘플 $(s_t, r_{t+1}, s_{t+1})$로 방정식의 해를 점진적으로 근사==

```ad-info
title: Note - Model-Free vs Model-Based

Model-based [[Policy Evaluation]]은 $p(s'|s,a)$, $p(r|s,a)$를 직접 사용해 기대값 계산:

$$v_\pi(s) = \sum_a \pi(a|s) \left[ \sum_r p(r|s,a) r + \gamma \sum_{s'} p(s'|s,a) v_\pi(s') \right]$$

TD는 시스템 모델을 모르므로, 환경에서 얻은 샘플을 직접 사용:

$$v(s) \leftarrow r_{t+1} + \gamma v(s_{t+1})$$

샘플은 이미 $p(r|s,a)$, $p(s'|s,a)$에 따라 ==샘플링된 결과==이므로, 시스템 모델이 암묵적으로 반영됨. 많은 샘플의 평균 → 기대값으로 수렴 ([[Law of Large Numbers]])
```

<br/>

### TD Target

$$\bar{v}_t \doteq r_{t+1} + \gamma v_t(s_{t+1})$$

- ==즉각 보상 + 할인된 다음 상태의 추정 가치==
- Bellman Expectation Equation의 ==샘플 기반 근사==
- [[Bootstrapping]]: 추정치 $v_t(s_{t+1})$로 $v_t(s_t)$ 업데이트

```ad-info
title: Note - Why Called "Target"

업데이트 수식 $v_{t+1}(s_t) = v_t(s_t) - \alpha_t \delta_t$에서 양변에 $\bar{v}_t$를 빼면:

$$v_{t+1}(s_t) - \bar{v}_t = (1 - \alpha_t)[v_t(s_t) - \bar{v}_t]$$

$0 < \alpha_t < 1$이므로 $0 < 1 - \alpha_t < 1$, 따라서:

$$|v_{t+1}(s_t) - \bar{v}_t| < |v_t(s_t) - \bar{v}_t|$$

→ ==새 추정치 $v_{t+1}(s_t)$가 이전 추정치 $v_t(s_t)$보다 $\bar{v}_t$에 더 가까움==. 알고리즘이 $v(s_t)$를 $\bar{v}_t$로 수렴시키므로 "target"
```

<br/>

### TD Error

$$\delta_t = v_t(s_t) - \bar{v}_t = v_t(s_t) - (r_{t+1} + \gamma v_t(s_{t+1}))$$

- ==현재 추정치와 TD target의 차이==
- 두 시점 $t$, $t+1$ 간 불일치를 반영 → "Temporal-Difference"
- 학습 방향과 크기 결정

```ad-info
title: Note - Interpretation of TD Error

**정확한 추정 시 TD error의 기대값은 0**

$v_t = v_\pi$일 때:

$$\begin{aligned}
\mathbb{E}[\delta_t | S_t = s_t] &= \mathbb{E}[v_\pi(S_t) - (R_{t+1} + \gamma v_\pi(S_{t+1})) | S_t = s_t] \\
&= v_\pi(s_t) - \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s_t] \\
&= 0 \quad \text{(Bellman Expectation Equation)}
\end{aligned}$$

→ TD error는 ==두 시점 간의 불일치==뿐 아니라, ==추정치 $v_t$와 진짜 state value $v_\pi$ 간의 불일치==도 반영

**Innovation 해석**

TD error는 경험 샘플 $(s_t, r_{t+1}, s_{t+1})$로부터 얻은 ==새로운 정보(innovation)==를 나타냄. TD learning의 핵심 아이디어는 새로 얻은 정보를 바탕으로 현재 추정치를 수정하는 것
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - TD(0) Prediction

**입력**: 정책 $\pi$, 학습률 $\alpha_t(s)$, 할인율 $\gamma$

**초기화**: $v_0(s)$ 임의 설정 for all $s \in \mathcal{S}$

**For** each episode:
- 초기 상태 $s_0$ 관측
- **While** $s_t$가 종료 상태가 아닐 때:
   - 행동 $a_t \sim \pi(s_t)$ 선택
   - $(r_{t+1}, s_{t+1})$ 관측
   - **Value 업데이트**:
     $$v_{t+1}(s_t) = v_t(s_t) - \alpha_t(s_t) \underbrace{[v_t(s_t) - (r_{t+1} + \gamma v_t(s_{t+1}))]}_{\delta_t}$$
   - **미방문 상태 유지**:
     $$v_{t+1}(s) = v_t(s) \quad \text{for all } s \neq s_t$$

**출력**: 추정된 $v_\pi$
```

```ad-warning
title: Note - Unvisited State Update Rule

미방문 상태 유지 수식은 간결함을 위해 자주 생략되지만, ==수학적 완전성을 위해 반드시 필요==:

- 시간 $t$에서 ==방문한 상태 $s_t$만 업데이트==됨
- 미방문 상태 $s \neq s_t$의 값은 ==변하지 않음==
- 이 수식 없이는 알고리즘이 ==수학적으로 불완전==
```

<br/><br/>

## Convergence
<!-- Section 7.2 -->

```ad-info
title: Note - TD as Stochastic Approximation

[[Stochastic Approximation#Robbins-Monro Algorithm|Robbins-Monro]]는 $f(v^*) = 0$의 해를 noisy observation으로 찾는 알고리즘:

$$v_{t+1} = v_t - \alpha_t \tilde{f}(v_t)$$

TD에서 $f(v) = 0$은 [[Bellman Equation|Bellman Expectation Equation]]:

$$f(v) = v - \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s] = 0 \implies v^* = v_\pi(s)$$

| | 우변의 $v(s_{t+1})$ | 가정 |
|:---|:---|:---|
| **RM 유도** | $v_\pi(s_{t+1})$ | 다른 상태의 값은 ==이미 알려짐== |
| **TD 알고리즘** | $v_t(s_{t+1})$ | ==모든 상태를 동시에 추정== |

RM 유도는 $s_t$만 추정하고 $v_\pi(s_{t+1})$는 알려졌다고 가정. TD는 ==모든 상태를 동시에 추정==하므로 $v_\pi(s_{t+1})$를 현재 추정치 $v_t(s_{t+1})$로 대체
```

```ad-important
title: Theorem - TD(0) Convergence

정책 $\pi$가 주어졌을 때, TD 알고리즘에 의해 $v_t(s)$는 다음 조건 하에서 ==모든 $s \in \mathcal{S}$에 대해 $v_\pi(s)$로 almost surely 수렴==:

$$\sum_{t} \alpha_t(s) = \infty, \quad \sum_{t} \alpha_t^2(s) < \infty \quad \text{for all } s \in \mathcal{S}$$

**조건 해석**:
- $\alpha_t(s) > 0$ if $s = s_t$ (방문), $\alpha_t(s) = 0$ otherwise (미방문)
- $\sum \alpha_t(s) = \infty$: ==상태 $s$가 무한 번 방문==되어야 함
- Exploring Starts 또는 exploratory policy로 모든 상태-행동 쌍의 충분한 방문 보장 필요
```

```ad-important
title: Proof - Derivation of TD Algorithm
collapse: true

**Step 1**: Bellman Equation을 root-finding 형태로 변환

$$g(w) \doteq w - \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s_t]$$

$g(w^*) = 0$의 해: $w^* = v_\pi(s_t)$

---

**Step 2**: Noisy observation 구성

$r_{t+1}$, $s_{t+1}$은 $R_{t+1}$, $S_{t+1}$의 샘플이므로:

$$\begin{align*}
\tilde{g}(w) &= w - [r_{t+1} + \gamma v_\pi(s_{t+1})] \\
&= \underbrace{\left(w - \mathbb{E}[R_{t+1} + \gamma v_\pi(S_{t+1}) | S_t = s_t]\right)}_{g(w)} + \underbrace{\left(\mathbb{E}[\cdot] - [r_{t+1} + \gamma v_\pi(s_{t+1})]\right)}_{\eta} \\
&= g(w) + \eta
\end{align*}$$

---

**Step 3**: RM 알고리즘 적용

RM 형태 $w_{t+1} = w_t - \alpha_t \tilde{g}(w_t)$에서 $w_t = v_t(s_t)$ (현재 추정치):

$$v_{t+1}(s_t) = v_t(s_t) - \alpha_t [v_t(s_t) - (r_{t+1} + \gamma v_\pi(s_{t+1}))]$$

---

**Step 4**: $v_\pi(s_{t+1})$ → $v_t(s_{t+1})$ 대체

위 수식은 $s_t$만 추정하고 $v_\pi(s_{t+1})$는 알려졌다고 가정. ==모든 상태를 동시에 추정==하려면 $v_\pi(s_{t+1})$를 $v_t(s_{t+1})$로 대체 → TD 알고리즘
```

```ad-important
title: Proof - TD Convergence
collapse: true

[[Dvoretzky's Theorem]]를 사용하여 증명. 목표: 세 가지 조건이 만족됨을 보이면 $\Delta_t(s) \to 0$ a.s.

---

**Step 1**: 오차 정의

$$\Delta_t(s) \doteq v_t(s) - v_\pi(s)$$

---

**Step 2**: 오차 동역학

TD 알고리즘에서 $v_\pi(s)$를 양변에서 빼면:

**Case 1** ($s = s_t$, 방문):

$$\Delta_{t+1}(s) = (1 - \alpha_t(s))\Delta_t(s) + \alpha_t(s)\underbrace{(r_{t+1} + \gamma v_t(s_{t+1}) - v_\pi(s))}_{\eta_t(s)}$$

**Case 2** ($s \neq s_t$, 미방문):

$$\Delta_{t+1}(s) = \Delta_t(s) = (1 - \alpha_t(s))\Delta_t(s) + \alpha_t(s)\eta_t(s)$$

($\alpha_t(s) = 0$, $\eta_t(s) = 0$이므로 Case 1과 ==동일한 형태==)

---

**Step 3**: Dvoretzky 조건 검증

**(a) Step size 조건**: $\sum_t \alpha_t(s) = \infty$, $\sum_t \alpha_t^2(s) < \infty$ — 가정에 의해 만족

**(b) Contraction 조건**: $\|\mathbb{E}[\eta_t(s) | H_t]\|_\infty \leq \gamma \|\Delta_t\|_\infty$

Markov property에 의해 $\mathbb{E}[\eta_t(s) | H_t] = \mathbb{E}[\eta_t(s)]$

**Case 1** ($s \neq s_t$):

$\eta_t(s) = 0$이므로:

$$|\mathbb{E}[\eta_t(s)]| = 0 \leq \gamma \|\Delta_t\|_\infty$$

**Case 2** ($s = s_t$):

$$\begin{aligned}
\mathbb{E}[\eta_t(s_t)] &= \mathbb{E}[r_{t+1} + \gamma v_t(s_{t+1}) - v_\pi(s_t) | s_t] \\
&= \mathbb{E}[r_{t+1} + \gamma v_t(s_{t+1}) | s_t] - v_\pi(s_t)
\end{aligned}$$

Bellman equation $v_\pi(s_t) = \mathbb{E}[r_{t+1} + \gamma v_\pi(s_{t+1}) | s_t]$를 대입:

$$\begin{aligned}
\mathbb{E}[\eta_t(s_t)] &= \mathbb{E}[r_{t+1} + \gamma v_t(s_{t+1}) | s_t] - \mathbb{E}[r_{t+1} + \gamma v_\pi(s_{t+1}) | s_t] \\
&= \gamma \mathbb{E}[v_t(s_{t+1}) - v_\pi(s_{t+1}) | s_t]
\end{aligned}$$

기대값을 전개하고 부등식 유도:

$$\begin{aligned}
|\mathbb{E}[\eta_t(s_t)]| &= \gamma \left| \sum_{s' \in \mathcal{S}} p(s'|s_t)[v_t(s') - v_\pi(s')] \right| \\
&\leq \gamma \sum_{s' \in \mathcal{S}} p(s'|s_t) |v_t(s') - v_\pi(s')| \\
&\leq \gamma \sum_{s' \in \mathcal{S}} p(s'|s_t) \max_{s''} |v_t(s'') - v_\pi(s'')| \\
&= \gamma \max_{s''} |v_t(s'') - v_\pi(s'')| \cdot \underbrace{\sum_{s'} p(s'|s_t)}_{=1} \\
&= \gamma \|\Delta_t\|_\infty
\end{aligned}$$

두 케이스를 종합하면 $\|\mathbb{E}[\eta_t(s)]\|_\infty \leq \gamma \|\Delta_t\|_\infty$

**(c) 유한 분산**: $\text{var}[\eta_t(s) | H_t] < \infty$

$r_{t+1}$이 bounded이므로 $\eta_t(s) = r_{t+1} + \gamma v_t(s_{t+1}) - v_\pi(s)$도 bounded → 분산 유한

---

**결론**: 세 조건 만족 → Dvoretzky's Theorem에 의해 $\Delta_t(s) \to 0$ a.s. for all $s \in \mathcal{S}$ $\square$
```

<br/>

### Practical Step Sizes

| Step Size | 조건 만족 | 특성 |
|:---|:---|:---|
| $\alpha_k = 1/k$ | ==만족== | 이론적 보장, 느린 수렴 |
| $\alpha_k = \alpha$ (상수) | ==불만족== | 빠른 적응, non-stationary에 유리 |

```ad-warning
title: Note - Constant Step Size

상수 $\alpha$는 $\sum_t \alpha_t^2(s) < \infty$ 조건 불만족이지만 ==실무에서 널리 사용==:
- 정책이 계속 변하는 (non-stationary) 상황에서 유리
- Decaying $\alpha$는 정책 변화를 반영하기엔 ==너무 작아짐==
- Almost sure 수렴 대신 ==기대값 의미에서 수렴== (mean convergence)
- 정확한 $v^*$가 아닌 ==$v^*$ 근방에서 fluctuation== (충분히 작은 $\alpha$면 무시 가능)
```

<br/><br/>

## Extension to Action Value

TD(0)는 ==state value $v_\pi$ 추정==에 사용. ==Action value $q_\pi$로 확장==하면 정책 개선에 직접 활용 가능

$$q_{t+1}(s_t, a_t) = q_t(s_t, a_t) - \alpha_t(s_t, a_t)[q_t(s_t, a_t) - \bar{q}_t]$$

- 알고리즘 간 차이는 오직 ==TD target $\bar{q}_t$의 정의==
- 모든 알고리즘이 $q(s,a) = \mathbb{E}[\bar{q}_t | s, a]$를 해결

| 알고리즘 | TD Target $\bar{q}_t$ | 해결 방정식 |
|:---|:---|:---|
| **[[Sarsa]]** | $r_{t+1} + \gamma q_t(s_{t+1}, a_{t+1})$ | BE |
| **[[n-step Sarsa]]** | $\sum_{i=0}^{n-1} \gamma^i r_{t+i+1} + \gamma^n q_t(s_{t+n}, a_{t+n})$ | BE |
| **[[Q-Learning]]** | $r_{t+1} + \gamma \max_a q_t(s_{t+1}, a)$ | ==BOE== |
| **[[Monte Carlo Methods\|MC]]** | $\sum_{i=0}^{\infty} \gamma^i r_{t+i+1}$ (전체 return) | BE |

- ==[[Q-Learning]]만 [[Bellman Optimality Equation|BOE]]를 해결== → Off-Policy
- 나머지는 [[Bellman Equation|BE]] 해결 → On-Policy
- MC는 $\alpha_t = 1$인 특수 케이스: $q_{t+1}(s_t, a_t) = \bar{q}_t$

<br/><br/>

## Related Concepts

- [[Bootstrapping]]: 추정치로 추정치 업데이트 — TD의 핵심 특성
- [[Stochastic Approximation]]: TD 수렴의 이론적 기반 (Robbins-Monro)
- [[Dvoretzky's Theorem]]: TD 수렴 증명에 사용되는 일반화된 SA 정리
- [[Bellman Equation]]: TD가 해결하는 방정식
- [[Monte Carlo Methods]]: Episode return 기반 학습 (bootstrapping 없음)
- [[MC vs TD]]: Monte Carlo와 TD 상세 비교
- [[On-Policy vs Off-Policy]]: TD Control 알고리즘 분류 기준
- [[Sarsa]]: TD를 action value로 확장한 On-Policy Control
- [[Q-Learning]]: Off-Policy TD Control, BOE 직접 해결
- [[Expected Sarsa]]: 기댓값 기반 TD Control
- [[n-step Sarsa]]: MC↔TD 스펙트럼의 일반화
- [[Value Function]]: TD로 추정하는 대상
- [[Value Function Approximation]]: 테이블 → 함수로의 확장
- [[TD-Linear]]: TD + Linear Function Approximation
