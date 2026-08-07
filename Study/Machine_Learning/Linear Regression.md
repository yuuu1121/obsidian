---
date: 2024-09-29
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/ML
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Regression
- 출력 변수 $y$가 입력 변수 $x$에 의존하는 관계를 모델링하는 방법
  $$y=f(x)+\epsilon$$
	- 출력 $y$가 입력 $x$에 어떻게 의존하는지는 조건부 분포 $p(y|x)$로 표현

<br>

## Loss Function: Conditional Mean
- 평균 제곱 오차(MSE)를 최소화하는 문제 ([[Least Square Method]])
	- MSE는 예측 $f(x)$와 실제 출력 $y$간의 오차를 제곱한 값의 평균
	$$\begin{align*}
	\mathcal{E}(f) &= \mathbb{E}\left[ \| y - f(x) \|^2 \right] \\\\
	&= \int \int \| y - f(x) \|^2 p(x, y) \, dx \, dy \\\\
	&= \int \int \| y - f(x) \|^2 p(x) p(y | x) \, dx \, dy \\\\
	 &= \int p(x) \underbrace{\int \| y - f(x) \|^2 p(y | x) \, dy}_{\text{to be minimized}} \, dx
	 \end{align*}$$
	- 즉, ${\partial\over\partial f(x)}\left(\int||y-f(x)||^2p(y|x)dy\right)=0$ 을 만족하는 $f(x)$를 구하는 문제

$$f(x)=\int y\cdot p(y|x)\cdot dy=\mathbb{E}[y|x]$$

>[!note]-
>$$\begin{align*}
{\partial\int||y-f(x)||^2p(y|x)dy\over\partial f(x)}&=\int \left({\partial||y-f(x)||^2p(y|x)\over \partial f(x)}\right)dy\\\\
&=\int \left(2(y-f(x))\cdot(-1)\cdot p(y|x)\right) dy=0\\\\\
&\rightarrow\int y\cdot p(y|x)dy=\int f(x)p(y|x)dy=f(x)\int p(y|x)dy=f(x)\\\\
f(x)&=\int y\cdot p(y|x) dy=\mathbb{E}[y|x]
\end{align*}$$

<br>

## Function Approximation and Curve Fitting
- Regression는 주어진 입력 $x$에 대해 출력 $y$가 어떻게 변하는지 (기대값, $\mathbb{E}[y|x]$)를 구하는 방법으로, $\mathbb{E}[y|x]$의 근사 함수인 $f(x)$를 사용
	- Linear function
	  $$f(\mathbf{x})=\mathbf{w}^\top \mathbf{x}\approx\mathbb{E}[\mathbf{y}|\mathbf{x}]$$
		- $\mathbf{w}$: 가중치 (매개변수) 벡터로, $x$와 $y$사이의 관계를 설명
	- [[Neural Network]]
	  $$f(\mathbf{x})=G_w(\mathbf{x})=\mathbf{W}_L\mathbf{W}_{L-1}\cdots\mathbf{W}_1\cdot \mathbf{x}$$
		- $\mathbf{W}_l$: $d_l\times d_{l-1}$ 크기의 행렬로, 각 계층의 가중치
		- 신경망을 사용한 함수는 비선형적인 입력-출력 관계를 학습할 수 있는 방법으로, 선형 모델보다 복잡한 데이터 패턴을 학습하는데 사용

<br>

# Linear Regression
## Linear Models
- 선형 회귀에서는 입력 $x$와 출력 $y$간의 관계가 선형이라고 가정
- 즉, $x$와 $y$는 가중치 벡터 $w$를 통해 직선 또는 평면 형태로 연결됨

$$y=\mathbf{w}^\top\mathbf{x}=\mathbf{x}^\top\mathbf{w}\qquad\text{where}\quad x\in \mathbb{R}^d\text{ and }y\in \mathbb{R}$$

- 주어진 데이터셋 $D=\left\{(\mathbf{x}_1, y_1), \cdots, (\mathbf{x}_N, y_N)\right\}$이 있을 때, 다음과 같은 행렬 형식으로 표현 가능

$$\mathbf{y}=\mathbf{X}\mathbf{w}\qquad\text{where}\quad \mathbf{y}\in\mathbb{R}^N\text{,}\quad\mathbf{X}\in\mathbb{R}^{N\times d}\quad\text{and}\quad\mathbf{w}\in\mathbb{R}^d$$

<br>

## Basis (Feature) Functions
- 입력 데이터 $x$에서 유용한 정보를 추출하는 함수
- 각 도메인에 맞춰 기저 함수를 설계해야 하며, 이를 통해 입력과 출력 사이의 더 복잡한 관계를 모델링할 수 있음
	- 예를들어, 다음과 같은 기저함수 $\phi(x)$가 주어진다면
	  $$\phi(x)=\begin{bmatrix}1\\x\\x^2\\x^3\end{bmatrix}$$
	  Linear model은 다음과 같이 표현될 수 있음
	  $$f(\mathbf{x})=\mathbf{w}^\top\phi(x)=\sum\limits_{l=1}^Lw_l\phi_l(x)=w_1+w_2x+w_3x^2+w_4x^3$$
	- Non-linear basis function을 사용함으로써, $f(x)$는 입력 $x$에 대해서는 비선형 관계를 가질 수 있지만, 여전히 가중치 벡터 $w$에 대해서는 선형 관계를 유지
		- 즉, 기저 함수를 사용하면 선형 모델이 복잡한 데이터 패턴도 설명할 수 있음

<br>

### Various Basis Functions
- Polynomial Basis Function
  $$\phi_l(x)=x^{l-1}$$

	![[Pasted image 20240929221325.png]]

- Gaussian Basis Function
  $$\phi_\ell(x) = \exp\left(-\frac{(x - \mu_l)^2}{2\sigma^2}\right)$$
  - 가우시안 분포를 따르는 형태로, 특정 중심 $\mu$ 주의의 값을 강조하고, 그로부터 멀어질수록 값이 급격하게 감소
  - 입력 공간을 국소적으로 표현하는데 유용하며, 데이터가 특정 구역에 집중되어 있을 때 효과적
- Spline Basis Function
	- 구간별 다항식 (Piecewise Polynomials)
		- 입력 공간을 여러 구역으로 나눈 뒤, 각 구역에서 다른 다항식을 사용하여 모델링
		- 이를 통해 전체적인 데이터 분포에 맞게 더 세밀한 Fitting을 할 수 있으며, 부드러운 연결을 유지하면서도 복잡한 패턴을 설명할 수 있음

<br>

### Design Matrix
- Design matrix $\Phi$:
	- 각 입력 데이터 $x_n$에 대한 Basis function $\phi_l(x_n)$이 적용된 값을 모아 만든 행렬
	$$\Phi = \begin{bmatrix} \phi_1(x_1) & \phi_2(x_1) & \dots & \phi_L(x_1) \\ \phi_1(x_2) & \phi_2(x_2) & \dots & \phi_L(x_2) \\ \vdots & \vdots & \ddots & \vdots \\ \phi_1(x_N) & \phi_2(x_N) & \dots & \phi_L(x_N) \end{bmatrix}$$
	- 입력 데이터를 Basis function으로 변환한 후, 그 결과를 Design matrix에 모아두면, 회귀 모델에서 이 매트릭스를 사용해 입력과 출력 간의 관계를 학습할 수 있음
	- 특히 다수의 입력 데이터를 한꺼번에 처리할 수 있기 때문에, 계산의 효율성을 높일 수 있음