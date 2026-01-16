# Contraction Mapping Theorem (축소 사상 정리)

## 개요
Contraction Mapping Theorem(축소 사상 정리, Banach Fixed Point Theorem)은 완비 거리 공간에서 축소 사상이 유일한 고정점을 가짐을 보장하는 정리이다. 강화학습의 수렴 증명에서 핵심적인 역할을 한다.

## 정의

### 축소 사상 (Contraction Mapping)
함수 $T: X \to X$가 축소 사상이면:

$$d(T(x), T(y)) \leq \gamma \cdot d(x, y)$$

모든 $x, y \in X$에 대해, 단 $0 \leq \gamma < 1$

$\gamma$: 축소 계수 (contraction factor)

## 정리

$(X, d)$가 완비 거리 공간이고 $T: X \to X$가 축소 사상이면:

1. **존재성**: $T$는 유일한 고정점 $x^*$를 가짐 ($T(x^*) = x^*$)
2. **수렴성**: 임의의 $x_0 \in X$에서 시작하여 $x_{n+1} = T(x_n)$으로 정의하면:
   $$\lim_{n \to \infty} x_n = x^*$$
3. **수렴 속도**: $d(x_n, x^*) \leq \frac{\gamma^n}{1-\gamma} d(x_1, x_0)$

## 증명 스케치

1. $\{x_n\}$이 Cauchy 수열임을 보임
2. 완비성에 의해 극한 $x^*$ 존재
3. $T$의 연속성에 의해 $x^* = T(x^*)$
4. 유일성은 축소 성질에서 도출

## 강화학습에서의 응용

### Bellman Operator
$$T[V](s) = \max_a \sum_{s'} P(s'|s,a)[R(s,a,s') + \gamma V(s')]$$

### 축소 사상 증명
$\gamma < 1$일 때 Bellman operator는 축소 사상:

$$\|T[V_1] - T[V_2]\|_\infty \leq \gamma \|V_1 - V_2\|_\infty$$

### 결론
- Value Iteration이 유일한 최적 가치 함수 $V^*$로 수렴
- Policy Iteration도 수렴

## 일반화

### Blackwell's Sufficient Conditions
연산자 $T$가 다음을 만족하면 축소 사상:
1. **단조성**: $V \leq W \Rightarrow T[V] \leq T[W]$
2. **할인**: $T[V + c] \leq T[V] + \gamma c$

## 예시
$f(x) = \frac{1}{2}x + 1$ on $\mathbb{R}$

$|f(x) - f(y)| = \frac{1}{2}|x - y|$ → 축소 사상 ($\gamma = 0.5$)

고정점: $x^* = 2$ ($f(2) = 2$)

## 관련 개념
- [[Dynamic Programming]]
- [[Value Iteration]]
- [[Bellman Equation]]
