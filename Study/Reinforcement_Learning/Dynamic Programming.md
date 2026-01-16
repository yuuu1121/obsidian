# Dynamic Programming (동적 프로그래밍)

## 개요
Dynamic Programming(DP)은 복잡한 문제를 더 작은 하위 문제로 분해하여 해결하는 방법이다. 강화학습에서는 MDP의 최적 정책을 찾는 데 사용된다.

## 핵심 원리

### 1. Optimal Substructure
최적 해가 하위 문제의 최적 해로 구성됨

### 2. Overlapping Subproblems
동일한 하위 문제가 반복적으로 계산됨

## 강화학습에서의 DP

### Bellman Equation

#### State Value Function
$$V^\pi(s) = \sum_a \pi(a|s) \sum_{s',r} p(s',r|s,a)[r + \gamma V^\pi(s')]$$

#### Action Value Function
$$Q^\pi(s,a) = \sum_{s',r} p(s',r|s,a)[r + \gamma \sum_{a'}\pi(a'|s')Q^\pi(s',a')]$$

### Bellman Optimality Equation
$$V^*(s) = \max_a \sum_{s',r} p(s',r|s,a)[r + \gamma V^*(s')]$$

## 알고리즘

### 1. Policy Evaluation
주어진 정책 $\pi$에 대해 $V^\pi$ 계산
```
반복:
  for each s:
    V(s) ← Σ_a π(a|s) Σ_{s',r} p(s',r|s,a)[r + γV(s')]
  until 수렴
```

### 2. Policy Improvement
현재 가치 함수를 기반으로 정책 개선
$$\pi'(s) = \arg\max_a \sum_{s',r} p(s',r|s,a)[r + \gamma V^\pi(s')]$$

### 3. Policy Iteration
Policy Evaluation + Policy Improvement 반복

### 4. Value Iteration
$$V_{k+1}(s) = \max_a \sum_{s',r} p(s',r|s,a)[r + \gamma V_k(s')]$$

## 비교

| 알고리즘 | 특징 |
|----------|------|
| Policy Iteration | 정책 수렴 보장, 느림 |
| Value Iteration | 빠름, 직접 최적 가치 계산 |

## DP의 한계

1. **환경 모델 필요**: $p(s',r|s,a)$를 알아야 함
2. **계산 비용**: 상태 공간이 크면 비효율적
3. **차원의 저주**: 연속 상태 공간에서 어려움

→ Model-free 방법 필요: [[Monte Carlo]], [[Temporal Difference]]

## 관련 개념
- [[Markov Decision Process]]
- [[Bellman Equation]]
- [[Policy Gradient]]
