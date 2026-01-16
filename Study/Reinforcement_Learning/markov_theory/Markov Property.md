---
date: 2025-07-16
tags:
  - Concepts/ReinforcementLearning/Fundamentals
  - Concepts/Fundamentals/Probability
aliases:
  - 마르코프 특성
  - Memoryless Property
keywords:
  - Markov Property
  - Memoryless Property
  - State Sufficiency
  - Conditional Independence
reference:
  - title: "Mathematical Foundations of Reinforcement Learning"
    authors: [Shiyu Zhao]
    year: 2024
    chapter: 2
  - title: "Reinforcement Learning: An Introduction"
    authors: [Richard S. Sutton, Andrew G. Barto]
    year: 2018
author:
url:
---

# Markov Property

```ad-note
title: Summary
collapse: true

- =="The future is independent of the past given the present"==
- ==$P(S_{t+1} | S_t) = P(S_{t+1} | S_1, \ldots, S_t)$== — 현재 상태만으로 미래 예측 가능
- ==State = 과거의 모든 유용한 정보를 압축한 충분 통계량==
- ==[[Bellman Equation]], [[Dynamic Programming]] 등 RL 알고리즘의 핵심 가정==
```

## Definition

<!-- Chapter 2,Erta and Barto Chapter 3.5 -->

=="The future is independent of the past given the present"==

$$P(S_{t+1} | S_t) = P(S_{t+1} | S_1, \ldots, S_t)$$

- $S_t$: 시점 $t$의 ==현재 상태==
- $S_1, \ldots, S_{t-1}$: ==과거 상태== 히스토리
- $S_{t+1}$: ==미래 상태==
- 현재 상태 $S_t$가 주어지면 ==미래 $S_{t+1}$은 과거 $(S_1, \ldots, S_{t-1})$와 독립==
- State는 미래 예측에 필요한 ==충분 통계량 (sufficient statistic)==

<br/>

### Conditional Independence

[[Conditional Independence|조건부 독립]]으로 표현:

$$S_{t+1} \perp\!\!\!\perp (S_1, \ldots, S_{t-1}) \mid S_t$$

- 현재 상태 $S_t$를 ==조건으로== 미래와 과거가 독립
- 히스토리 전체를 저장할 필요 없이 ==현재 상태만 유지==

```ad-info
title: Note - Computational Significance

| Aspect | With Markov Property | Without |
|:---|:---|:---|
| **Complexity** | $O(\|\mathcal{S}\|^2)$ | $O(\|\mathcal{S}\|^t)$ — 지수적 증가 |
| **Memory** | 현재 상태만 저장 | 전체 히스토리 저장 |
| **Algorithm** | [[Bellman Equation]], [[Dynamic Programming]] 적용 가능 | 적용 불가 |

→ Markov Property가 ==RL을 계산 가능하게 만드는 핵심 가정==
```

```ad-warning
title: Note - Non-Markovian Cases

실제 문제에서 Markov Property가 성립하지 않는 경우 해결 방법:

| Method | Description |
|:---|:---|
| **State Augmentation** | 위치 → (위치, 속도, 가속도) 등 ==과거 정보를 상태에 포함== |
| **History Window** | 최근 $k$개 관측을 상태로: $s_t = (o_{t-k+1}, \ldots, o_t)$ |
| **Belief State (POMDP)** | $b(s) = P(S = s \| \text{observations})$ — Markov 만족 |
| **RNN/LSTM** | 은닉 상태가 히스토리 정보 압축 |
```

<br/><br/>

## Markov Processes Hierarchy

Markov Property를 기반으로 한 ==확률 과정의 확장==:

$$\text{MP} \xrightarrow{+\text{Reward}} \text{MRP} \xrightarrow{+\text{Action}} \text{MDP}$$

| Process                              | Tuple                                                                        | 추가 요소            | 목적                             |
| :----------------------------------- | :--------------------------------------------------------------------------- | :--------------- | :----------------------------- |
| **[[Markov Process\|MP]]**           | $\langle \mathcal{S}, \mathcal{P} \rangle$                                   | —                | ==상태 전이 패턴 모델링== (순수 확률 과정)    |
| **[[Markov Reward Process\|MRP]]**   | $\langle \mathcal{S}, \mathcal{P}, \mathcal{R}, \gamma \rangle$              | Reward, Discount | ==고정된 정책의 가치 평가== ($v_\pi$ 계산) |
| **[[Markov Decision Process\|MDP]]** | $\langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$ | Action           | ==최적 정책 탐색== ($\pi^*$ 도출)      |

<br/><br/>

## Related Concepts

- [[Markov Process]]: Markov Property를 만족하는 확률 과정 $\langle \mathcal{S}, \mathcal{P} \rangle$
- [[Markov Reward Process]]: MP + Reward — 가치 평가 가능
- [[Markov Decision Process]]: MRP + Action — 최적화 문제 정의
- [[Transition Probability]]: Markov Property 하에서 $p(s'|s,a)$로 단순화
- [[Bellman Equation]]: Markov Property 기반 재귀 관계
- [[Dynamic Programming]]: Markov Property를 활용한 최적화 기법
- [[Conditional Independence]]: Markov Property의 수학적 표현
- [[State and Observation]]: Markov State (Information State) 정의
