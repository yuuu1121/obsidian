---
date: 2024-05-06, 17:55
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases:
  - Cumulative Distribution Function
  - CDF
  - 누적 분포 함수
keywords:
  - Cumulative Distribution Function
  - CDF
  - 누적 분포 함수
related notes: 
reference: 
author: 
url:
---
# 누적 분포 함수 (Cumulative Distribution Function, CDF)
![[Pasted image 20240506181259.png]]

- [[Random Variables|확률 변수]]가 특정 값보다 작거나 같을 확률을 나타내는 함수
- 다변량 함수(multivariate real-valued variable $X,\quad x\in R^D$)에 대하여 정의된 확률을 $P$ 라고 할 때, 다음과 같이 정의되는 함수 $F_X(x)$ 를 $X$ 의 누적 분포 함수라고 정의

  >$$F_X(x)=P(X_1 \le x_1,\dots, X_D\le x_D)$$

---
## 누적 분포 함수 특징
<br>

>$$\begin{align}(1)\quad&x_1<x_2\rightarrow F_X(x_1)\le F_X(x_2)\\\\(2)\quad& 0\le F_X(x)\le1\\\\(3)\quad&\lim_{x \to \infty}F_X(x)=1\\\\(4)\quad&\lim_{x\to-\infty}F_X(x)=0\\\\(5)\quad&P(a<X\le b)=F_X(b)-F_X(a)\\\\(6)\quad&P(X>a)=1-F_X(a)\end{align}$$

<br>

- CDF는 [[Continuous RV#확률 밀도 함수 (Probability Density Function, PDF]]|PDF)를 적분함으로써 구할 수 있음
$$F_X (x)=\int_{-\infty}^{x_1}\dots\int_{-\infty}^{x_D}f(z_1,\dots,z_D)dz_1,\dots,dz_D$$
