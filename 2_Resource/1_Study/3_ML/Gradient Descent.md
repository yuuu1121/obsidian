---
date: 2024-10-01
status: Permanent
tags:
  - Study/ML
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Gradient Descent (GD)
- Loss function $L(\mathbf{w})$를 최소화시키기 위해 $\mathbf{w}$를 반복적으로 업데이트하는 방법
	- $L$이 미분 가능하지만, 해를 해석적으로 구할 수 없을 때 사용되는 수치적 최적화 방법 ([[Non-Linear Regression#Limitation|Non-linear regression]])
	$$\mathbf{w}_{t+1} = \mathbf{w}_t - \gamma_t \nabla L(\mathbf{w}_t)$$
	- 즉, $L(w+\boldsymbol{\epsilon})-L(w)$을 보고 업데이트를 결정
		- Graident 증가 ▶ $w$ 감소
		- Gradient 감소 ▶ $w$ 증가

![[Pasted image 20241001182945.png|500]]

<br>

## Step Size
- Gradient Descent에서 스텝 크기(step size)는 수렴 속도와 성능에 중요한 영향을 미치는 변수
- 좋은 스텝 크기를 찾기 위한 휴리스틱(Heuristics)
	- 경사 하강 후 Loss가 증가했다면, 스텝 크기가 너무 크다는 의미
		- 스텝을 되돌리고 스텝 크기를 줄인다
	- 경사 하강 후 Loss가 감소했다면, 스텝 크기가 더 커질 수 있다는 의미
		- 스텝 크기를 늘린다
	- 하지만, Loss 함수 평가에 시간이 너무 많이 걸린다면 이 방식은 비효율적일 수 있음

<br>

# Momentum
![[Pasted image 20241002144058.png]]

- Gradient Descent는 경사에 따라 매개변수를 업데이트하는 기법이지만, 진동과 느린 수렴속도가 문제가 될 수 있음
- Momentum(관성 효과)은 이러한 문제를 해결하기 위한 기법으로, 이전 단계의 경사 정보를 기억하여, 매개변수 업데이트 시 이를 반영
	
	$$\mathbf{x}_{i+1} = \overbrace{\mathbf{x}_i - \gamma_i \nabla f(\mathbf{x}_i)}^{\text{GD}} + \overbrace{\alpha \Delta \mathbf{x}_i}^{\mathbf{momentum}}\qquad\alpha\in[0, 1]$$
	$$\Delta \mathbf{x}_i = \mathbf{x}_i - \mathbf{x}_{i-1} = \alpha \Delta \mathbf{x}_{i-1} - \gamma_{i-1} \nabla f(\mathbf{x}_{i-1})$$
- Momentum의 효과:
	- 진동 억제: 
	  경사가 급변하는 구간에서 매개변수의 진동을 줄여 안정적으로 최적화.
	- 빠른 수렴:
	  반복적인 계산에서 수렴 속도를 가속.
	- 안정성 향상:
	  Local minima에 빠질 가능성을 줄여 더 나은 최적화 경로를 제공.

<br>

# Stochastic Gradient Descent (SGD)
- Batch Gradient Descent:
	- 전체 데이터셋에 대해 경사를 계산하는 방법
	- 데이터셋이 클 경우 느리고 비효율적
	$$L(\theta) = \sum_{i=1}^{N} \ell(y_i, f_\theta(x_i))\qquad\frac{\partial L(\theta)}{\partial \theta} = \sum_{i=1}^{N} \frac{\partial L_i(\theta)}{\partial \theta}$$

- Stochastic Gradient Descent(SGD)
	- 데이터셋의 일부(mini-batch)를 사용하여 경사를 근사하는 방법
	- Mini-batch로 계산된 Gradient는 데이터 분포 $p(x, y)$에 대한 기대값을 근사
	$$\frac{\partial L_B(\theta)}{\partial \theta} = \sum_{i : x_i \in B} \frac{\partial L_i(\theta)}{\partial \theta}$$
	- 즉, 데이터셋의 Gradient 기대값을 Mini-batch로부터 근사할 수 있음
	$${1\over N}\cdot\mathbb{E}\left[{\partial L(\theta)\over\partial\theta}\right]\approx{1\over|B|}\cdot\mathbb{E} \left[{\partial L_\mathcal{B}(\theta)\over\partial\theta}\right]$$
	>[!note]-
	>$$\begin{align*}\mathbb{E}\left[{\partial L(\theta)\over\partial\theta}\right]&=\mathbb{E} \left[\sum\limits_{i=1}^N{\partial L_i(\theta)\over\partial\theta}\right] =N\cdot\mathbb{E} \left[{\partial L_i(\theta)\over\partial\theta}\right]\\\\&=N\cdot\mathbb{E} \left[{1\over|B|}\sum\limits_{i:x_i\in \mathcal{B}}{\partial L_i(\theta)\over\partial\theta}\right]={N\over|B|}\cdot\mathbb{E} \left[\sum\limits_{i:x_i\in\mathcal{B}}{\partial L_i(\theta)\over\partial\theta}\right]\end{align*}$$


- SGD의 장점:
	- 빠른 계산:
	  전체 데이터를 사용하지 않고 데이터를 여러 mini-batch로 나눠 Gradient를 근사함으로써 계산 비용 감소
	- 노이즈 활용:
	  SGD는 Gradient 계산 시 노이즈가 포함되는데, 이 노이즈는 종종 Local minima에서 탈출하도록 도와줌
	- 메모리 효율성:
	  대규모 데이터셋을 사용하면서도 적은 메모리로 최적화 수행