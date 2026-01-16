# Law of Total Expectation (전체 기대값의 법칙)

## 개요
Law of Total Expectation(전체 기대값의 법칙, Adam's Law)은 조건부 기대값을 사용하여 무조건부 기대값을 계산하는 방법이다.

## 공식

### 이산 형태
$$E[X] = \sum_i E[X|A_i]P(A_i)$$

여기서 $\{A_i\}$는 표본 공간의 분할

### 연속 형태
$$E[X] = E[E[X|Y]]$$

또는

$$E[X] = \int E[X|Y=y] f_Y(y) dy$$

## 증명

$$E[E[X|Y]] = E\left[\sum_x x \cdot P(X=x|Y)\right] = \sum_x x \sum_y P(X=x|Y=y)P(Y=y)$$
$$= \sum_x x P(X=x) = E[X]$$

## 예시

### 예시 1: 두 단계 실험
주머니에서 공을 뽑고, 공의 색에 따라 주사위를 다르게 던짐

- 빨간 공 (P=0.3): 6면 주사위
- 파란 공 (P=0.7): 4면 주사위

$$E[X] = E[X|\text{빨강}]P(\text{빨강}) + E[X|\text{파랑}]P(\text{파랑})$$
$$= 3.5 \times 0.3 + 2.5 \times 0.7 = 2.8$$

### 예시 2: 복합 포아송 과정
$N \sim \text{Poisson}(\lambda)$, $X_i$ i.i.d.

$S = \sum_{i=1}^N X_i$의 기대값:

$$E[S] = E[E[S|N]] = E[N \cdot E[X_1]] = \lambda \cdot E[X_1]$$

## 관련 법칙

### Law of Total Variance
$$Var(X) = E[Var(X|Y)] + Var(E[X|Y])$$

### Law of Total Probability
$$P(A) = \sum_i P(A|B_i)P(B_i)$$

## 응용

1. **계층적 모델**: 베이지안 통계
2. **강화학습**: Value function 분해
3. **보험수학**: 복합 분포 기대값
4. **재무**: 위험 평가

## 관련 개념
- [[Conditional Probability]]
- [[Law of Total Probability]]
- [[Expectation and Moments]]
- [[Bayesian Inference]]
