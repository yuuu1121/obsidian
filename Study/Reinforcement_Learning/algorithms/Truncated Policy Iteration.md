---
date: 2026-01-04
tags:
  - Concepts/ReinforcementLearning/Algorithms
aliases:
  - 절단된 정책 반복
  - TPI
  - Modified Policy Iteration
keywords:
  - Truncated Policy Iteration
  - Value Iteration
  - Policy Iteration
  - Dynamic Programming
  - Generalized Policy Iteration
  - j_truncate
related notes:
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 4
author:
url:
---

# Truncated Policy Iteration

```ad-note
title: Summary
collapse: true

- ==[[Value Iteration]]과 [[Policy Iteration]]을 하나의 프레임워크로 통합==
- ==Policy Evaluation에서 $j_{\text{truncate}}$번만 반복 후 중단==
- ==$j_{\text{truncate}} = 1$이면 VI, $j_{\text{truncate}} = \infty$이면 PI==
- ==VI보다 빠르고 PI보다 효율적인 균형점 제공==
```

## Definition

==[[Policy Iteration]]의 Policy Evaluation 단계에서 유한 번만 반복하는 [[Policy Iteration#Generalized Policy Iteration|GPI]] 알고리즘==

PI의 Policy Evaluation은 이론적으로 $j \to \infty$ 반복이 필요하나, ==유한 번($j_{\text{truncate}}$)만 수행해도 최적 정책으로 수렴==

```ad-info
title: Note - Model Requirement

TPI는 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$를 ==필요로 함== ([[Dynamic Programming]])

→ Model-free 확장: [[Q-Learning]], [[Actor-Critic]]
```

<br/><br/>

## Unified Framework

```ad-info
title: Note - VI vs PI Background

두 알고리즘 모두 ==매 iteration마다 두 단계== 수행:

**절차 흐름**:

$$\begin{align*}
\text{Policy Iteration: } & \pi_0 \xrightarrow{\text{PE}} v_{\pi_0} \xrightarrow{\text{PI}} \pi_1 \xrightarrow{\text{PE}} v_{\pi_1} \xrightarrow{\text{PI}} \pi_2 \xrightarrow{\text{PE}} \cdots \\
\text{Value Iteration: } & \phantom{\pi_0 \xrightarrow{\text{PE}}} v_0 \xrightarrow{\text{PU}} \pi'_1 \xrightarrow{\text{VU}} v_1 \xrightarrow{\text{PU}} \pi'_2 \xrightarrow{\text{VU}} v_2 \xrightarrow{\text{PU}} \cdots
\end{align*}$$

| 측면 | Value Iteration | Policy Iteration |
|:---|:---|:---|
| **Value 성질** | ==$v_k$: 중간값== | ==$v_{\pi_k}$: 진짜 state value== |
| **PE 반복** | ==1회== | ==수렴까지 ($j \to \infty$)== |
| **단조 수렴** | 보장 안 됨 | $v_{\pi_{k+1}} \geq v_{\pi_k}$ 보장 |
```

PI의 Policy Evaluation을 상세히 전개하면 ==VI와 PI가 동일 프레임워크의 양 극단==임이 명확해짐:

$$\begin{align*}
&& v^{(0)}_{\pi_1} &= v_0 \\
\text{Value Iteration} &\leftarrow v_1 \leftarrow & v^{(1)}_{\pi_1} &= r_{\pi_1} + \gamma P_{\pi_1} v^{(0)}_{\pi_1} \\
&& v^{(2)}_{\pi_1} &= r_{\pi_1} + \gamma P_{\pi_1} v^{(1)}_{\pi_1} \\
&& &\vdots \\
\text{Truncated PI} &\leftarrow \bar{v}_1 \leftarrow & v^{(j)}_{\pi_1} &= r_{\pi_1} + \gamma P_{\pi_1} v^{(j-1)}_{\pi_1} \\
&& &\vdots \\
\text{Policy Iteration} &\leftarrow v_{\pi_1} \leftarrow & v^{(\infty)}_{\pi_1} &= r_{\pi_1} + \gamma P_{\pi_1} v^{(\infty)}_{\pi_1}
\end{align*}$$

- **$j_{\text{truncate}} = 1$**: $v^{(1)}_{\pi_1} = v_1$ → [[Value Iteration#Algorithm|Value Iteration]]
- **$j_{\text{truncate}} = j$**: $v^{(j)}_{\pi_1} = \bar{v}_1$ → **Truncated PI**
- **$j_{\text{truncate}} = \infty$**: $v^{(\infty)}_{\pi_1} = v_{\pi_1}$ → [[Policy Iteration#Algorithm|Policy Iteration]]

→ ==VI와 PI는 Truncated PI의 두 극단적 경우==

```ad-warning
title: Note - Comparison Condition

위 비교는 ==$v^{(0)}_{\pi_1} = v_0 = v_{\pi_0}$== 조건 하에서만 유효

→ 이 초기 조건 없이는 VI와 PI를 직접 비교할 수 없음
```

<br/><br/>

## Algorithm

```ad-tldr
title: Algorithm - Truncated Policy Iteration

**입력**: 시스템 모델 $p(r|s,a)$, $p(s'|s,a)$, 초기 정책 $\pi_0$, 반복 횟수 $j_{\text{truncate}}$

**While** $v_k$가 수렴하지 않음:

**1. Policy Evaluation** (truncated):
   - 초기화: $v^{(0)}_k = v_{k-1}$
   - **For** $j = 0, 1, \ldots, j_{\text{truncate}} - 1$:
     - **For** 모든 $s \in \mathcal{S}$:
       - $v^{(j+1)}_k(s) = \sum_a \pi_k(a|s) \left[ \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v^{(j)}_k(s') \right]$
   - $v_k = v^{(j_{\text{truncate}})}_k$

**2. Policy Improvement**:
   - **For** 모든 $s \in \mathcal{S}$:
     - **For** 모든 $a \in \mathcal{A}$:
       - $q_k(s,a) = \sum_r p(r|s,a)r + \gamma \sum_{s'} p(s'|s,a) v_k(s')$
     - $a^*_k(s) = \arg\max_a q_k(s,a)$
     - $\pi_{k+1}(a|s) = 1$ if $a = a^*_k$, else $0$

**출력**: 최적 가치 $v^*$, 최적 정책 $\pi^*$
```

```ad-warning
title: Note - $v_k$ is NOT a State Value

[[Value Iteration]]과 마찬가지로, Truncated PI의 $v_k$는 ==진정한 state value가 아님==
- 유한 번만 반복하므로 [[Bellman Equation]]을 만족하지 않음
- 진짜 state value $v_{\pi_k}$의 ==근사값==

→ $j_{\text{truncate}} = \infty$일 때만 $v_k = v_{\pi_k}$ (진짜 state value)
```

<br/><br/>

## Convergence

```ad-important
title: Theorem - Value Improvement

Policy Evaluation의 반복 알고리즘에서 초기값을 $v^{(0)}_{\pi_k} = v_{\pi_{k-1}}$로 설정하면:

$$v^{(j+1)}_{\pi_k} \geq v^{(j)}_{\pi_k} \quad \forall j \geq 0$$

→ 반복할수록 값이 ==단조 증가==
```

```ad-important
title: Proof - Value Improvement
collapse: true

**Step 1**: 차이 분석

$$v^{(j+1)}_{\pi_k} - v^{(j)}_{\pi_k} = \gamma P_{\pi_k} (v^{(j)}_{\pi_k} - v^{(j-1)}_{\pi_k}) = \gamma^j P^j_{\pi_k} (v^{(1)}_{\pi_k} - v^{(0)}_{\pi_k})$$

---

**Step 2**: 기저 조건 확인

$v^{(0)}_{\pi_k} = v_{\pi_{k-1}}$이고, $\pi_k = \arg\max_\pi (r_\pi + \gamma P_\pi v_{\pi_{k-1}})$이므로:

$$v^{(1)}_{\pi_k} = r_{\pi_k} + \gamma P_{\pi_k} v_{\pi_{k-1}} \geq r_{\pi_{k-1}} + \gamma P_{\pi_{k-1}} v_{\pi_{k-1}} = v_{\pi_{k-1}} = v^{(0)}_{\pi_k}$$

---

**Step 3**: 결론

$v^{(1)}_{\pi_k} \geq v^{(0)}_{\pi_k}$이고 $\gamma^j P^j_{\pi_k} \geq 0$이므로:

$$v^{(j+1)}_{\pi_k} - v^{(j)}_{\pi_k} \geq 0 \quad \forall j \geq 0$$ $\square$
```

```ad-warning
title: Note - Practical Limitation

위 정리는 ==$v^{(0)}_{\pi_k} = v_{\pi_{k-1}}$== (진짜 state value)를 가정

- 실제로는 $v_{\pi_{k-1}}$을 얻을 수 없음
	- Truncated PI는 근사값 $v_{k-1}$만 제공
- 그럼에도 정리가 Truncated PI 수렴에 대한 ==직관적 이해== 제공
```

<br/>

동일한 초기값에서 시작할 때 ==Truncated PI는 VI와 PI 사이==:

![[Pasted image 20260104212343.png|300]]

$$v_k \leq v_{\pi_k} \leq v^* \quad \forall k$$

- **VI보다 빠름**: PE에서 ==1회 이상 반복==하여 더 정확한 value 추정
- **PI보다 느림**: PE에서 ==유한 회만 반복==하여 완전 수렴 아님

<br/><br/>

## Related Concepts

- [[Value Iteration]]: $j_{\text{truncate}} = 1$인 특수 경우
- [[Policy Iteration]]: $j_{\text{truncate}} = \infty$인 특수 경우
- [[Policy Iteration#Generalized Policy Iteration|Generalized Policy Iteration]]: evaluation ↔ improvement 공통 구조
- [[Policy Evaluation]]: Truncated PI의 내부 루프
- [[Bellman Equation]]: Policy Evaluation이 푸는 방정식
- [[Bellman Optimality Equation]]: 수렴 목표
- [[Dynamic Programming]]: Truncated PI가 속한 패러다임

