---
date: 2026-01-05
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 몬테카를로 방법
  - MC Methods
  - Monte Carlo
  - MC Basic
  - MC Exploring Starts
  - MC ε-Greedy
keywords:
  - Monte Carlo
  - Model-Free
  - Mean Estimation
  - Law of Large Numbers
  - Exploring Starts
  - First-Visit
  - Every-Visit
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 5
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
  - David Silver's RL Course
author:
url:
---

# Monte Carlo Methods

```ad-note
title: Summary
collapse: true

- ==Model-free RL의 첫 번째 방법: 시스템 모델 없이 경험으로 최적 정책 학습==
- ==핵심 원리: $q_\pi(s,a) = \mathbb{E}[G_t]$ → 샘플 평균으로 추정 ([[Law of Large Numbers]])==
- ==[[Policy Iteration]]의 PE 단계를 MC 추정으로 대체==
- ==MC Basic → MC Exploring Starts → MC ε-Greedy 순으로 발전==
```

![[Pasted image 20260105150030.png|700]]

<br/>

## Definition

==시스템 모델 없이 에피소드 샘플로 action value를 추정하여 최적 정책을 찾는 방법==

| 특성 | MC |
|:---|:---|
| **업데이트 시점** | ==에피소드 종료 후== (non-incremental) |
| **적용 범위** | ==Episodic tasks==만 (종료 상태 필요) |
| **Bias/Variance** | ==Unbiased==, high variance |
| **초기 추정치** | 불필요 ([[Bootstrapping]] 없음) |
| **On/Off-Policy** | ==[[On-Policy vs Off-Policy\|On-Policy]]== |

```ad-info
title: Note - [[MC vs TD]]

| | Monte Carlo | [[Temporal Difference Learning]] |
|:---|:---|:---|
| **추정 근거** | ==Return 정의== | ==[[Bellman Equation]]== |
| **수식** | $q(s,a) = \mathbb{E}[G_t]$ | $q(s,a) = \mathbb{E}[R + \gamma q(S', A')]$ |
| **방법** | 실제 $G_t$ 샘플링 후 평균 | BE로 bootstrapping |
```

<br/><br/>

## MC Estimation

[[Value Function#Action Value Function (Q-Function)|Action value]]의 정의가 ==기대값==이라는 점을 활용하여 ==샘플 평균으로 $q$ 직접 추정==:

$$q_{\pi_k}(s,a) = \mathbb{E}[G_t | S_t = s, A_t = a] \approx \frac{1}{n} \sum_{i=1}^{n} g^{(i)}_{\pi_k}(s,a)$$

- ==시스템 모델 불필요== — 경험 샘플만으로 추정
- [[Law of Large Numbers]]에 의해 $n \to \infty$일 때 수렴
- ==[[Policy Iteration|PI]]의 [[Policy Evaluation|model-based PE]]를 model-free MC 추정으로 대체==

```ad-info
title: Note - Model-Based vs Model-Free

**Model-Based** ([[Dynamic Programming]]):

$$q_{\pi_k}(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_{\pi_k}(s')$$

- [[Bellman Equation]]을 풀어 $v_{\pi_k}$ 계산 후, ==시스템 모델 $p(r|s,a)$, $p(s'|s,a)$==로 $q$ 변환
- 모델을 알아야 하므로 ==실제 환경에서 적용 어려움==

**Model-Free** (MC):
- $q$를 ==직접 추정== → 모델 없이 greedy 정책 도출 가능: $\pi(s) = \arg\max_a q(s,a)$
- $v$ 대신 $q$를 추정하는 이유: $v$만 알면 정책 도출에 ==여전히 모델 필요==
```

```ad-warning
title: Note - i.i.d. Sample Condition

샘플은 ==독립이고 동일하게 분포(i.i.d.)==되어야 함

- 샘플 간 상관이 있으면 기대값 추정 불가
- 극단적 예: 모든 샘플이 첫 샘플과 동일 → 샘플 수를 늘려도 수렴 안 함
```

<br/><br/>

## MC Basic

==[[Policy Iteration]]의 [[Policy Evaluation|PE]]를 MC 추정으로 대체한 가장 단순한 알고리즘==

| 특성 | MC Basic |
|:---|:---|
| **Visit 전략** | Initial-visit (에피소드 시작점만 사용) |
| **Policy Update** | Batch (모든 에피소드 수집 후) |
| **정책 유형** | Greedy |
| **Exploring Starts** | ==필요== |

```ad-warning
title: Note - Exploring Starts Requirement

**Exploring Starts**: ==모든 $(s,a)$ 쌍에서 시작하는 에피소드를 충분히 수집==

**왜 필요한가?**
- [[Greedy Policy|Greedy 정책]]은 ==deterministic== → 각 상태에서 항상 같은 action만 선택
- 에피소드 진행 중 ==다른 action 탐색 불가== (greedy action만 반복)
- [[Law of Large Numbers]] 수렴 조건: 모든 $(s,a)$를 충분히 방문해야 함
→ 유일한 탐색 기회는 ==에피소드 시작점==

**한계**: 물리적 환경에서는 임의 상태에서 시작 불가 → MC ε-Greedy로 해결
```

```ad-info
title: Note - Limitations

MC Basic은 ==샘플 효율성이 낮아 실용적이지 않음==:
- **Initial-visit**: 에피소드당 시작점 $(s_0,a_0)$만 사용 → 나머지 방문 ==버림==
- **Batch update**: 모든 $(s,a)$ 에피소드 수집 후 정책 업데이트 → ==즉시 반영 안 됨==

→ 효율 기법 없이 MC의 핵심 아이디어를 명확히 전달하는 ==이론적 기초==
```

<br/>

### Algorithm

```ad-tldr
title: Algorithm - MC Basic

**초기화**: 초기 정책 $\pi_0$

- **For** $k = 0, 1, 2, \ldots$:
	- **For** 모든 $s \in \mathcal{S}$
		- **For** 모든 $a \in \mathcal{A}$
			- $(s,a)$에서 시작, $\pi_k$를 따르는 에피소드 충분히 수집
			- **Policy Evaluation**: 
			  $$q_{\pi_k}(s, a) \approx q_k(s,a) = \text{mean of return}$$
		- **Policy Improvement**: 
		  $$\pi_{k+1}(a|s) = 1, \quad \text{if} \quad a = \arg\max_a q_k(s,a), \quad \text{else} \quad0$$

**출력**: 최적 정책 $\pi^*$
```

<br/>

### Convergence

**수렴 근거**:
- [[Law of Large Numbers]] → action value 정확 추정
- [[Policy Iteration]] 수렴 → 최적 정책 도달

```ad-example
title: Example - MC Basic 3×3 Grid World
collapse: true

![[Pasted image 20260105173449.png|300]]

**설정**:
- 3×3 Grid World
- $r_{\text{boundary}} = r_{\text{forbidden}} = -1$, $r_{\text{target}} = 1$
- $\gamma = 0.9$
- 초기 정책 $\pi_0$: $s_1$, $s_3$에서 비최적

---

**$s_1$에서의 Action Value 계산** (deterministic policy이므로 단일 에피소드로 충분):

$$\begin{align*}
s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_4} s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \dots && \text{[original episode]} \\
& s_2 \xrightarrow{a_4} s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \dots && \text{[subepisode starting from }(s_2, a_4)\text{]} \\
&& s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \dots && \text{[subepisode starting from }(s_1, a_2)\text{]} \\
&&& s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \dots && \text{[subepisode starting from }(s_2, a_3)\text{]} \\
&&&& s_5 \xrightarrow{a_1} \dots && \text{[subepisode starting from }(s_5, a_1)\text{]}
\end{align*}$$

---

**Return 계산**:

$$\begin{align*}
q_{\pi_0}(s_1, a_1) &= -1 + \gamma(-1) + \gamma^2(-1) + \cdots = \frac{-1}{1-\gamma} = -10 \\
q_{\pi_0}(s_1, a_2) &= 0 + \gamma \cdot 0 + \gamma^2 \cdot 0 + \gamma^3 \cdot 1 + \gamma^4 \cdot 1 + \cdots = \frac{\gamma^3}{1-\gamma} = 7.29 \\
q_{\pi_0}(s_1, a_3) &= 0 + \gamma \cdot 0 + \gamma^2 \cdot 0 + \gamma^3 \cdot 1 + \cdots = \frac{\gamma^3}{1-\gamma} = 7.29 \\
q_{\pi_0}(s_1, a_4) &= \frac{-1}{1-\gamma} = -10 \\
q_{\pi_0}(s_1, a_5) &= 0 + \gamma(-1) + \gamma^2(-1) + \cdots = \frac{-\gamma}{1-\gamma} = -9
\end{align*}$$

---

**Action Value 요약**:

| Action | Episode 방향 | Return 공식 | $q_{\pi_0}(s_1, a)$ |
|:---|:---|:---|:---|
| $a_1$ (←) | 벽 충돌 반복 | $\frac{-1}{1-\gamma}$ | ==-10== |
| $a_2$ (→) | target 도달 | $\frac{\gamma^3}{1-\gamma}$ | ==7.29== |
| $a_3$ (↓) | target 도달 | $\frac{\gamma^3}{1-\gamma}$ | ==7.29== |
| $a_4$ (↑) | 벽 충돌 반복 | $\frac{-1}{1-\gamma}$ | ==-10== |
| $a_5$ (stay) | 제자리 후 벽 충돌 | $\frac{-\gamma}{1-\gamma}$ | ==-9== |

---

**Policy Improvement**:

$$a^*_0(s_1) = \arg\max_a q_{\pi_0}(s_1, a) = a_2 \text{ or } a_3$$

$$\pi_1(a_2|s_1) = 1 \quad \text{또는} \quad \pi_1(a_3|s_1) = 1$$

→ ==1회 iteration으로 $s_1$에서 최적 정책 도출== (다른 상태는 이미 최적이었음)
```

<br/><br/>

## MC Exploring Starts

MC Basic의 ==효율성 개선==: (1) Every-visit, (2) Episode-by-episode 업데이트

| 특성 | MC Exploring Starts |
|:---|:---|
| **Visit 전략** | ==Every-visit== (모든 방문 활용) |
| **Policy Update** | ==Episode-by-episode== (즉시 업데이트) |
| **정책 유형** | Greedy |
| **Exploring Starts** | ==필요== |

<br/>

### Visit Strategies

| 전략 | 설명 | 효율성 |
|:---|:---|:---|
| **Initial-visit** | 에피소드 시작 $(s_0,a_0)$만 | 낮음 |
| **First-visit** | 각 $(s,a)$의 첫 방문만 | 중간 |
| **Every-visit** | 모든 방문 | ==높음== |

하나의 에피소드에서 ==여러 subepisode를 추출==하여 샘플 효율성 극대화:

$$\begin{array}{rl}
s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_4} s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \cdots & \text{[original episode]} \\
s_2 \xrightarrow{a_4} s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \cdots & \text{[subepisode from } (s_2, a_4)\text{]} \\
s_1 \xrightarrow{a_2} s_2 \xrightarrow{a_3} s_5 \xrightarrow{a_1} \cdots & \text{[subepisode from } (s_1, a_2)\text{]} \\
\end{array}$$

→ 하나의 에피소드로 ==모든 방문 $(s_t,a_t)$에서 시작하는 return== 획득

```ad-info
title: Note - Backward Traversal Implementation

==Backward Traversal + 매 Step 업데이트==가 every-visit의 핵심 구현:

- **Backward Traversal**: 에피소드 끝→시작 순회하며 ==재귀적 return 계산==
  $$g \leftarrow \gamma g + r_{t+1}$$
- **매 Step PE/PI**: 각 시점마다 $q$ 업데이트 (PE) → $\pi$ 업데이트 (PI) 즉시 수행

→ 에피소드 종료 후 ==모든 방문 지점에서 정책이 개선된 상태==
```

```ad-warning
title: Note - Every-visit Sample Correlation

Every-visit 샘플은 ==상관됨== (i.i.d. 조건 위반):
- 두 번째 방문의 trajectory는 첫 번째의 ==부분집합==
- 하지만 두 방문이 멀리 떨어져 있으면 상관성이 ==약함==
- 실무에서는 충분히 긴 에피소드로 상관성 완화
```

<br/>

### Algorithm

```ad-tldr
title: Algorithm - MC Exploring Starts

**초기화**: $q(s,a)$, $\text{Returns}(s,a) = 0$, $\text{Num}(s,a) = 0$

- **For** each episode:
	- **Episode generation**:
		- 시작 $(s_0,a_0)$ 선택 (==모든 쌍이 선택될 수 있도록==)
		- $\pi$를 따라 에피소드 생성: $s_0,a_0,r_1,\ldots,s_{T-1},a_{T-1},r_T$
	- **Initialization**: $g \leftarrow 0$<br/><br/>
	- **For** $t = T-1, T-2, \ldots, 0$:
	  - $g \leftarrow \gamma g + r_{t+1}$
	  - $\text{Returns}(s_t,a_t) \leftarrow \text{Returns}(s_t,a_t) + g$
	  - $\text{Num}(s_t,a_t) \leftarrow \text{Num}(s_t,a_t) + 1$
	  - **Policy Evaluation**:
	    $$q(s_t,a_t) \leftarrow \text{Returns}(s_t,a_t) / \text{Num}(s_t,a_t)$$
	  - **Policy Improvement**:
	    $$\pi(a|s_t) = 1, \quad \text{if} \quad a = \arg\max_a q(s_t,a), \quad \text{else} \quad 0$$

**출력**: $\pi^*$, $q^*$
```

<br/>

### Convergence

**수렴 조건**: ==Exploring Starts + 무한 에피소드== → 최적 정책 수렴

**이론적 근거**:
- Exploring Starts → 모든 $(s,a)$ 무한 방문
- [[Law of Large Numbers]] → action value 정확 추정
- [[Policy Iteration]] 수렴 → 최적 정책 도달

→ Exploring Starts의 실용적 한계를 극복하기 위해 ==MC ε-Greedy== 등장

<br/><br/>

## MC ε-Greedy

==Exploring Starts 조건 제거==: [[Exploration vs Exploitation|ε-greedy 정책]]으로 에피소드 내 탐색

| 특성 | MC ε-Greedy |
|:---|:---|
| **Visit 전략** | Every-visit |
| **Policy Update** | Episode-by-episode |
| **정책 유형** | ==ε-Greedy== |
| **Exploring Starts** | ==불필요== |

[[Epsilon-Greedy Policy|ε-greedy]] = 대표적 ==soft policy== (모든 action에 양의 확률 부여)
- 에피소드 진행 중 ==non-greedy action도 확률적으로 선택== 가능
- 충분히 긴 에피소드면 모든 $(s,a)$ 방문 가능 → ==Exploring Starts 조건 제거==

<br/>

### Policy Improvement

Greedy 대신 ==ε-greedy로 개선==:

$$\pi_{k+1} = \arg\max_{\pi \in \Pi_\epsilon} \sum_a \pi(a|s) q_{\pi_k}(s,a)$$

$$\therefore \pi_{k+1}(a|s) = \begin{cases} 1 - \frac{|\mathcal{A}(s)|-1}{|\mathcal{A}(s)|}\epsilon, & a = a^* \\ \frac{\epsilon}{|\mathcal{A}(s)|}, & a \neq a^* \end{cases}$$

where $a^* = \arg\max_a q(s,a)$

<br/>

### Algorithm

```ad-tldr
title: Algorithm - MC ε-Greedy

**초기화**: $q(s,a)$, $\text{Returns}(s,a) = 0$, $\text{Num}(s,a) = 0$, $\epsilon \in (0,1]$

- **For** each episode:
	- **Episode generation**:
		- 시작 $s_0$ 선택 (Exploring Starts ==불필요==)
		- ε-greedy 정책 $\pi$를 따라 에피소드 생성: $s_0,a_0,r_1,\ldots,s_{T-1},a_{T-1},r_T$
	- **Initialization**: $g \leftarrow 0$<br/><br/>
	- **For** $t = T-1, T-2, \ldots, 0$:
	  - $g \leftarrow \gamma g + r_{t+1}$
	  - $\text{Returns}(s_t,a_t) \leftarrow \text{Returns}(s_t,a_t) + g$
	  - $\text{Num}(s_t,a_t) \leftarrow \text{Num}(s_t,a_t) + 1$
	  - **Policy Evaluation**: 
	    $$q(s_t,a_t) \leftarrow \text{Returns}(s_t,a_t) / \text{Num}(s_t,a_t)$$
	  - **Policy Improvement**: ε-greedy 정책으로 업데이트
	    $$a^* = \arg\max_a q(s_t,a)$$

**출력**: 최적 ε-greedy 정책 $\pi^*_\epsilon$
```

```ad-example
title: Example - Single Episode Learning
collapse: true

![[Pasted image 20260105165454.png|700]]

**설정**: 5×5 Grid World, $r_{\text{boundary}} = r_{\text{forbidden}} = -1$, $r_{\text{target}} = 1$, $\gamma = 0.9$

**극단적 조건**: 매 iteration마다 ==단일 에피소드== (1백만 step)만 사용

---

**초기 정책**: Uniform ($\pi(a|s) = 0.2$ for all $a$)

**결과** ($\epsilon = 0.5$):
- ==2 iterations 만에 최적 ε-greedy 정책 도달==
- 단일 에피소드만으로도 모든 $(s,a)$ 방문 → action value 정확 추정

→ Soft policy의 탐색 능력으로 ==Exploring Starts 없이 학습 가능==
```

### Convergence

**수렴 조건**: ==모든 $(s,a)$ 무한 방문== → $\Pi_\epsilon$ 내 최적 정책 수렴

| 조건 | 수렴 대상 |
|:---|:---|
| 무한 에피소드 | $\pi^*_\epsilon$ ($\Pi_\epsilon$ 내 최적) |
| $\epsilon \to 0$ | $\pi^*$ ($\Pi$ 내 최적) |

→ 실무에서는 [[Epsilon-Greedy Policy#ε-Decay|ε-Decay]]로 ==초기 exploration → 후기 exploitation== 전환

```ad-warning
title: Note - Optimality in $\Pi_\epsilon$

MC ε-Greedy는 ==$\Pi_\epsilon$ 내에서 최적==:
- 전체 $\Pi$에서 최적 아닐 수 있음
- ε가 충분히 작으면 $\Pi$의 최적과 ==일관==

**ε가 클 때 inconsistency 발생 이유**:
- ε가 크면 ==위험 상태로 이탈 확률== 증가
- 예: target state에서 forbidden area로 이탈 → 음의 보상
- 최적 정책이 "stay"가 아니라 =="escape"==가 됨
```

<br/><br/>

## Algorithm Comparison

$$\text{MC Basic} \xrightarrow{\text{Efficiency}} \text{MC Exploring Starts} \xrightarrow{\text{Relaxation}} \text{MC } \epsilon\text{-Greedy}$$

| 알고리즘 | Visit | Update | Exploring Starts | 정책 |
|:---|:---|:---|:---|:---|
| **MC Basic** | Initial | Batch | ==필요== | Greedy |
| **MC Exploring Starts** | Every | Episode | ==필요== | Greedy |
| **MC ε-Greedy** | Every | Episode | ==불필요== | ε-Greedy |

<br/><br/>

## Related Concepts

- [[Policy Iteration]]: MC가 model-free로 변환한 알고리즘
- [[Policy Evaluation]]: MC 추정이 대체하는 단계
- [[Policy Iteration#Generalized Policy Iteration|GPI]]: 부정확한 추정으로도 정책 개선 가능
- [[Temporal Difference Learning]]: MC와 달리 bootstrapping 사용
- [[Sarsa]]: On-Policy TD Control (MC의 TD 버전)
- [[n-step Sarsa]]: MC↔Sarsa 스펙트럼의 일반화 (MC는 $n=\infty$인 특수 케이스)
- [[MC vs TD]]: MC와 TD 상세 비교
- [[Value Function Approximation]]: Tabular → FA 확장 (Gradient MC)
- [[On-Policy vs Off-Policy]]: MC는 On-Policy
- [[Epsilon-Greedy Policy]]: MC ε-Greedy에서 사용하는 soft policy
- [[Exploration vs Exploitation]]: ε-greedy의 탐색-활용 trade-off
- [[Law of Large Numbers]]: MC 추정의 이론적 기반
- [[Return]]: MC가 사용하는 실제 return
- [[Episode]]: MC는 episodic tasks 전용
- [[Dynamic Programming]]: MC가 대체하는 model-based 방법

