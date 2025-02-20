---
date: 2024-11-13
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
# Perceptron
```ad-tip
title: Recap) [[Classification#Linear Regression for Classification|Linear Binary Classification]]
collapse: true
![[Pasted image 20241021050651.png]]

- Discriminant function
  $$f(x) = w^\top x + b$$
	- $w \in \mathbb{R}^D$: 가중치 벡터
	- $b \in \mathbb{R}$: 바이어스
	- $f(x)$: 입력 데이터 $x$에 대해 선형 결합을 계산

<br>

- Decision rule
	- $f(x) \geq 0$: 클래스 1
	- $f(x) < 0$: 클래스 -1
	- 즉, $sign(f(x))$에 따라 분류를 수행.
```

<br>

## Single Perceptron
- **Definition**
	- 신경망의 기본 모델로, Thresholding 활성화 함수를 사용하는 뉴런 모델
		$$ y = \text{sign}(w^\top x + b) $$
- **Training Strategy**
	- Online learning과 Mistake-driven 절차를 따름
		- 잘못 분류된 데이터 포인트가 있을 때마다 가중치 벡터 $w$를 업데이트.
		- [[선형적으로 구분 가능한 데이터]]에 대해서는 **수렴 보장**(Perceptron Convergence Theorem).

<br>

### Perceptron Criterion
- Objective
	- 모든 입력 데이터 $x$에 대해 가중치 벡터 $w$가 다음 목표를 달성하도록 함
		$$ y_n = \begin{cases} 
		1 & \text{if } x_n \in C_1 \\ 
		-1 & \text{if } x_n \in C_2 
		\end{cases} $$
	- 모든 $n$에 대해 $y_n=\text{sign}(w^Tx_n)$을 만족하는 $w$를 찾는 것, 즉  
  $$y_nw^Tx_n>0\quad\forall n$$ 
- Objective function
  $$\mathcal{J}(w)=-\sum_{n\in\mathcal{M}(w)}y_nw^Tx_n$$
	- $\mathcal{M}(w)=\{n:y_nw^Tx_n<0\}$: 잘못 분류된 데이터 포인트들의 집합.

<br>

- [[Gradient Descent]]
	- Gradient
	  $$\nabla_w\mathcal{J}(w)=-\sum_{n\in\mathcal{M}(w)}y_nx_n$$
	- Optimization
	  $$w\leftarrow w+\alpha\sum_{n\in\mathcal{M}(w)}y_nx_n$$

<br>

- Stochastic Gradient Descent
	1. 임의의 훈련 샘플 $(x_m, y_m)$을 선택.
	2. 잘못 분류된 경우에만 가중치 업데이트: 
		$$w^{(t+1)} = w^{(t)} + \alpha y_m x_m$$
	1. 수렴할 때까지 1, 2단계 반복.

<br>

- **Limitation**
	- **선형적으로 구분 가능한 데이터**에 대해서는 수렴이 보장되지만, **XOR**와 같은 선형적으로 구분 불가능한 문제에 대해서는 성능이 떨어짐.
	  ![[Pasted image 20241021050846.png]]

<br>

## Multi-Layer Perceptron (MLP)
- **Definition**
	- 다수의 Hidden layer과 Non-linear [[Activation Function|activation function]]을 포함한 신경망
	- e.g., **XOR** 문제는 두 AND와 하나의 OR 연산으로 해결 가능하며, MLP를 사용하면 해결할 수 있음 ($a \oplus b = ab + āb̄$)
	  ![[Pasted image 20241021051137.png]]
- **Key Concepts**
	- Flexible Function Approximator
		- Perceptron은 단순한 빌딩 블록이지만, 여러 개의 Perceptron을 결합하여, 복잡한 모델을 표현할 수 있음
		  ![[Pasted image 20241021051450.png]]
	- Universal Approximation Theorem
	  - 단일 넓은 은닉층만으로도 모든 연속적인 함수를 근사할 수 있음
	    - 임의의 곡선 함수는 양자화를 통해 근사 가능
	      ![[Pasted image 20241113035405.png|300]]
	    - 다층 퍼셉트론은 이러한 양자화 과정을 통해 임의의 함수를 근사하여, 범용 함수 근사기로 작동함
	  - 그러나, 이 경우 단순히 데이터를 암기하는 역할에 그칠 수 있음
	  - 또한, 모델이 특정 데이터셋에 대한 근사 성능을 보장할 뿐, 일반화 능력을 보장하지는 않음

<br>

- **Limitations**
	- Overfitting
		- MLP는 훈련 데이터에 대해 적합하게 학습할 수 있지만, 새로운 데이터에 대해 일반화가 보장되지 않음
	- Vanishing Gradient
		- Perceptron은 $w^\top x_n$의 부호($sign$)를 출력하지만, 부호 함수에 대한 미분을 시도하면 [[Classification#^ux4jxs|Zero gradient 문제]]가 발생

