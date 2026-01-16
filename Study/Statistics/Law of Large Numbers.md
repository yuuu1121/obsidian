# Law of Large Numbers (대수의 법칙)

## 개요
Law of Large Numbers(대수의 법칙)는 표본의 크기가 커질수록 표본 평균이 모평균에 수렴한다는 확률론의 기본 정리이다.

## 종류

### 약한 대수의 법칙 (Weak LLN)
확률 수렴 (convergence in probability)

$$P\left(\left|\bar{X}_n - \mu\right| > \epsilon\right) \rightarrow 0 \text{ as } n \rightarrow \infty$$

또는

$$\bar{X}_n \xrightarrow{P} \mu$$

### 강한 대수의 법칙 (Strong LLN)
거의 확실한 수렴 (almost sure convergence)

$$P\left(\lim_{n \rightarrow \infty} \bar{X}_n = \mu\right) = 1$$

또는

$$\bar{X}_n \xrightarrow{a.s.} \mu$$

## 조건

- $X_1, X_2, ..., X_n$이 i.i.d. (독립 항등 분포)
- $E[X_i] = \mu$ (유한한 기대값)
- (Strong LLN) $Var(X_i) < \infty$

## 직관적 이해

동전을 $n$번 던질 때:
- $n$이 작으면: 앞면 비율이 0.5에서 크게 벗어날 수 있음
- $n$이 크면: 앞면 비율이 0.5에 가까워짐

## 예시

### Monte Carlo 적분
$$\int_a^b f(x)dx \approx \frac{b-a}{n}\sum_{i=1}^{n}f(x_i)$$

$n \rightarrow \infty$일 때 실제 적분값으로 수렴

### 보험
개별 보험금은 불확실하지만, 많은 가입자의 평균 보험금은 예측 가능

## 중심극한정리와의 관계

| 대수의 법칙 | 중심극한정리 |
|-------------|--------------|
| 평균이 $\mu$로 수렴 | 분포가 정규분포로 수렴 |
| 점 추정 | 구간 추정의 근거 |

$$\bar{X}_n \xrightarrow{d} N\left(\mu, \frac{\sigma^2}{n}\right)$$

## 관련 개념
- [[Central Limit Theorem]]
- [[Expectation and Moments]]
- [[Sample Mean]]
- [[Stochastic Convergence]]
