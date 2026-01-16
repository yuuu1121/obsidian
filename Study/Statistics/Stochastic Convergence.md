# Stochastic Convergence (확률적 수렴)

## 개요
Stochastic Convergence는 확률 변수의 수열이 어떤 값이나 다른 확률 변수로 수렴하는 다양한 방식을 정의한다.

## 수렴의 종류

### 1. Almost Sure Convergence (거의 확실한 수렴)
$$P\left(\lim_{n \rightarrow \infty} X_n = X\right) = 1$$

표기: $X_n \xrightarrow{a.s.} X$

가장 강한 형태의 수렴

### 2. Convergence in Probability (확률 수렴)
$$\lim_{n \rightarrow \infty} P(|X_n - X| > \epsilon) = 0 \quad \forall \epsilon > 0$$

표기: $X_n \xrightarrow{P} X$

### 3. Convergence in Distribution (분포 수렴)
$$\lim_{n \rightarrow \infty} F_{X_n}(x) = F_X(x)$$

모든 연속점 $x$에서

표기: $X_n \xrightarrow{d} X$

### 4. Convergence in Mean (평균 수렴)
$$\lim_{n \rightarrow \infty} E[|X_n - X|^r] = 0$$

표기: $X_n \xrightarrow{L^r} X$

$r=2$일 때: Mean Square Convergence

## 수렴 관계

```
Almost Sure → Probability → Distribution
     ↓
  Mean (L^r)
```

강한 수렴은 약한 수렴을 포함:
- a.s. → P (역은 성립 안 함)
- P → d (역은 일반적으로 성립 안 함)
- L^r → P (r ≥ 1)

## 중요 정리

### 대수의 법칙
- **약한 대수의 법칙**: $\bar{X}_n \xrightarrow{P} \mu$
- **강한 대수의 법칙**: $\bar{X}_n \xrightarrow{a.s.} \mu$

### 중심극한정리
$$\frac{\sqrt{n}(\bar{X}_n - \mu)}{\sigma} \xrightarrow{d} N(0,1)$$

### Slutsky's Theorem
$X_n \xrightarrow{d} X$이고 $Y_n \xrightarrow{P} c$이면:
- $X_n + Y_n \xrightarrow{d} X + c$
- $X_n Y_n \xrightarrow{d} cX$

## 예시

### 확률 수렴하지만 a.s. 수렴 안 함
$X_n = 1$ with prob $1/n$, $X_n = 0$ otherwise

$P(X_n \neq 0) = 1/n \rightarrow 0$ (확률 수렴)

하지만 무한히 많은 $n$에서 $X_n = 1$ (a.s. 수렴 안 함)

## 관련 개념
- [[Law of Large Numbers]]
- [[Central Limit Theorem]]
- [[Martingale]]
