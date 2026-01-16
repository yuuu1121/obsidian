# Monotone Convergence Theorem (단조 수렴 정리)

## 개요
Monotone Convergence Theorem(단조 수렴 정리)은 측도론과 적분론에서 적분과 극한의 교환 조건을 제시하는 중요한 정리이다.

## 정리

### Lebesgue의 단조 수렴 정리
$\{f_n\}$이 비음수 가측 함수의 증가 수열이고 $f_n \uparrow f$ (점별 수렴)이면:

$$\lim_{n \to \infty} \int f_n \, d\mu = \int \lim_{n \to \infty} f_n \, d\mu = \int f \, d\mu$$

### 조건
1. $f_n \geq 0$ (비음수)
2. $f_n \leq f_{n+1}$ (단조 증가)
3. $f_n \to f$ (점별 수렴)

## 의미
적분과 극한의 순서를 바꿀 수 있음:
$$\lim_{n \to \infty} \int f_n = \int \lim_{n \to \infty} f_n$$

## 관련 정리

### Fatou's Lemma
$\{f_n\}$이 비음수 가측 함수열이면:
$$\int \liminf_{n \to \infty} f_n \leq \liminf_{n \to \infty} \int f_n$$

### Dominated Convergence Theorem
$f_n \to f$ 점별 수렴하고, $|f_n| \leq g$ (적분 가능한 $g$)이면:
$$\lim_{n \to \infty} \int f_n = \int f$$

## 비교

| 정리 | 조건 | 결론 |
|------|------|------|
| 단조 수렴 | 비음수, 증가 | 등호 성립 |
| Fatou's Lemma | 비음수 | 부등호 |
| 지배 수렴 | 지배 함수 존재 | 등호 성립 |

## 응용

### 급수와 적분의 교환
$$\int \sum_{n=1}^{\infty} f_n = \sum_{n=1}^{\infty} \int f_n$$

(부분합이 단조 증가일 때)

### 기대값 계산
확률론에서:
$$E\left[\sum_{n=1}^{\infty} X_n\right] = \sum_{n=1}^{\infty} E[X_n]$$

(비음수 확률 변수에 대해)

## 예시

$f_n(x) = x \cdot \mathbf{1}_{[0,n]}(x)$ on $[0, \infty)$

$f_n \uparrow f(x) = x$

$$\lim_{n \to \infty} \int_0^n x \, dx = \int_0^\infty x \, dx$$

(무한대로 발산하지만 등호는 성립)

## 관련 개념
- [[Lebesgue Integration]]
- [[Measure Theory]]
- [[Stochastic Convergence]]
