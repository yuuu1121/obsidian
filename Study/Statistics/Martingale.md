# Martingale (마팅게일)

## 개요
Martingale은 조건부 기대값이 현재 값과 같은 확률 과정이다. "공정한 게임"을 수학적으로 모델링하며, 확률론과 금융 수학에서 중요한 역할을 한다.

## 정의

확률 과정 $\{X_n\}$이 filtration $\{\mathcal{F}_n\}$에 대해 martingale이면:

1. $X_n$은 $\mathcal{F}_n$-measurable
2. $E[|X_n|] < \infty$
3. $E[X_{n+1} | \mathcal{F}_n] = X_n$ (a.s.)

## 변형

### Submartingale
$$E[X_{n+1} | \mathcal{F}_n] \geq X_n$$
기대값이 증가하는 경향

### Supermartingale
$$E[X_{n+1} | \mathcal{F}_n] \leq X_n$$
기대값이 감소하는 경향

## 예시

### 1. 공정한 도박
동전 던지기 (앞면 +1, 뒷면 -1)
$$X_n = X_0 + \sum_{i=1}^{n} Y_i$$
$E[X_{n+1}|X_1,...,X_n] = X_n$

### 2. Random Walk
$S_n = \sum_{i=1}^n X_i$, $X_i$ i.i.d. with $E[X_i]=0$

### 3. 주가 모델
$S_t = S_0 e^{\sigma W_t - \frac{\sigma^2 t}{2}}$ (위험 중립 측도 하에서)

## 중요 정리

### Optional Stopping Theorem
정지 시간 $\tau$에 대해 조건 만족 시:
$$E[X_\tau] = E[X_0]$$

### Martingale Convergence Theorem
Bounded martingale은 a.s. 수렴

### Doob's Inequality
$$P\left(\max_{1 \leq k \leq n} X_k \geq \lambda\right) \leq \frac{E[X_n^+]}{\lambda}$$

## 응용

### 금융 수학
- 옵션 가격 결정
- 무차익 거래 이론
- 위험 중립 가격 결정

### 확률론
- 수렴 정리 증명
- 최적 정지 문제
- [[Law of Large Numbers]] 증명

### 강화학습
- TD 학습의 수렴 분석
- Value function 추정

## 관련 개념
- [[Stochastic Convergence]]
- [[Conditional Probability]]
- [[Random Variables]]
