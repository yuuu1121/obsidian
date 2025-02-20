---
date: 2024-12-09
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/ML
aliases: PCA
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Principal Component Analysis (PCA)
![[Pasted image 20241209025454.png|500]]
![[Pasted image 20241212081706.png]]

- **Definition**
	- 데이터를 새로운 basis로 표현하며, 고차원 데이터를 저차원으로 축소하는 방법
	- 새로운 basis는 데이터의 variance를 최대화하거나, 원래 데이터와 저차원 표현간의 근사 오차를 최소화하는 방식으로 정의
	- 이 과정에서 주성분(Principal Component)이라 불리는 새로운 축을 생성하며, 이 축들은 데이터의 최대 정보를 설명하는 방향

<br/><br/>

## Maximum Variance Formulation
- **Definition**
	- 데이터를 낮은 차원으로 투영하면서, 투영된 데이터의 분산(variance)을 최대화
	- 데이터의 분산은 데이터가 얼마나 흩어져 있는지를 나타내며, 분산이 크면 정보량([[Entropy|information]])이 많이 보존된 것으로 간주<br/><br/>
	- **Goal**
		- 데이터셋 $\{x_n\}_{n \in [N]}$은 $x_n \in \mathbb{R}^D$에 속하며, 이를 $M$ 차원($M < D$)으로 투영

<br/>

### 1-dimensional Principal Subspace
- **Problem**
	- **Definition**
		- 단위 벡터 $u_1 \in \mathbb{R}^D$를 사용하여 데이터 포인트 $x_n$을 1차원으로 투영
		  $$u_1^\top x_n \in \mathbb{R}^1$$
	- **Goal**
		- 투영된 데이터의 분산이 최대화되는 최적의 단위 벡터(basis vector) $\left\{ u_i \right\}_{i\in \left[ M \right]}$ <br/><br/>
		- Variance
		  $$\frac{1}{N} \sum_{n=1}^N (u_1^\top x_n - u_1^\top \bar{x})^2 = u_1^\top S u_1$$
			- Mean vector: $\bar{x} \overset{\text{def}}{=} \frac{1}{N} \sum_{n=1}^N x_n$
			- [[Random Vector and Covariance#^hknq01|Covariance matrix]]: $S \overset{\text{def}}{=} \frac{1}{N} \sum_{n=1}^N (x_n - \bar{x})(x_n - \bar{x})^\top$<br/><br/>
	- **Optimization Problem**
		- Objective function: $\underset{u_1 \in \mathbb{R}^D}{\max} \, u_1^\top S u_1$
		- Constraint: $u_1^\top u_1=1$ ($u_1$이 단위 벡터임을 보장)

<br/>

- **Principle**
	- [[Constrained Optimization#Lagrangian Function|Lagrangian Function]]
		- 제약 조건을 포함하여 최적화를 수행하기 위해 라그랑지 함수를 정의
		  $$\mathcal{L}(u_1, \lambda_1) = u_1^\top S u_1 + \lambda_1 (1 - u_1^\top u_1)$$<br/>
	- **Optimal Solution**
		- 결과적으로, 해는 다음을 만족해야 함
		  $${\partial\mathcal{L}(u_1, \lambda_1)\over \partial u_1}=0\quad\implies\quad Su_1=\lambda_1u_1$$
			- $u_1$: $S$의 고유 벡터(eigenvector)
			- $\lambda_1$: $S$의 고유 값(eigenvalue)<br/><br/>
		- 따라서, 분산을 최대화하려면 $S$의 가장 큰 고유값 $\lambda_1$에 해당하는 고유벡터 $u_1$을 선택해야 함
		  $$u_1^\top S u_1 = \lambda_1 u_1^\top u_1 = \lambda_1$$

<br/><br/>

### $M$-dimensional Principal Subspace
- **Problem**
	- **Definition**
		- $M$개의 직교 기저 벡터(basis vector) $u_1, u_2, \dots, u_M \in \mathbb{R}^D$를 사용하여 데이터를 $M$차원으로 투영
		  $$U = [u_1, u_2, \dots, u_M] \in \mathbb{R}^{D \times M}, \quad U^\top x_n \in \mathbb{R}^M$$
	- **Optimization Problem**
		- Objective function: $\underset{U \in \mathbb{R}^{D \times M}}{\max} \, \sum_{i=1}^M u_i^\top S u_i$
		- Constraint: $u_i^\top u_j = \delta_{ij}\overset{\text{def}}{=}\begin{cases}1 & \text{if } i = j \\0 & \text{if } i \neq j\end{cases}$

<br/>

- **Principle**
	- **Lagrangian Function**
	  $$\mathcal{L}(U, \Lambda) = \sum_{i=1}^M u_i^\top S u_i - \sum_{i=1}^M \sum_{j=1}^M \lambda_{ij} (u_i^\top u_j - \delta_{ij})\quad\text{where}\quad \Lambda = \{\lambda_{ij}\}$$
	- **Optimal Solution**
	  $${\partial\mathcal{L}(U, \Lambda)\over \partial u_i}=0\quad\implies\quad S u_i = \sum_{j=1}^M \lambda_{ij} u_j, \quad \forall i \in [M]$$
		- 이는 $u_i$가 $S$의 고유벡터이며, $M$개의 고유벡터가 상호 직교함을 의미<br/><br/>
		- $S$는 [[positive semidefinite)](Positive Semi-definite.md|반양의 정부호(positive semidefinite)]] 행렬로, 모든 고유값 $\{\lambda_i\}$는 비음수
		  $$v^\top S v \geq 0 \quad \forall v \in \mathbb{R}^D$$
		- 따라서, $S$는 비음수 고유값(non-negative eigenvalues, $\left\{ \lambda_i \right\}_{i\in D}$)를 가지며, 최대 총 분산은 다음과 같음
		  $$\sum_{i=1}^M u_i^\top S u_i = \sum_{i=1}^M \lambda_i$$
		- 즉, PCA는 공분산 행렬 $S$의 상위 $M$개의 고유값과 고유벡터를 사용하여 $M$차원 공간으로 데이터를 투영

<br/>

```ad-tip
title: **Eigen vector and Eigen value**

- 고유값과 고유벡터의 의미
	- 고유값 $\lambda_i$: 데이터의 분산 크기
	- 고유벡터 $u_i$: 분산이 큰 방향(축)
- 최대 분산 방향 선택
	- 데이터를 저차원으로 투영할 때, **가장 분산이 큰 방향**으로 데이터를 투영하면 정보 손실을 최소화 가능
	- 이를 위해 $S$의 **가장 큰 고유값에 해당하는 고유벡터**를 선택
		- $M$차원으로 투영하려면 상위 $M$개의 고유값과 고유벡터를 선택
```

<br/><br/>

## Minimum Error Formulation

- **Problem**
	- 데이터를 낮은 차원으로 투영하면서, 투영된 데이터의 오차(error)를 최소화<br/><br/>
	- **Definition**
		- 투영된 데이터의 오차가 최소화되는 최적의 단위 벡터(basis vector) $\left\{ u_i \right\}_{i\in \left[ M \right]}$<br/><br/>
		- **$D$-dimensional Basis Vector**
			- $D$ 차원의 기저 벡터들의 완전 직교 단위 벡터 $\left\{ u_i \right\}_{i\in \left[ D \right]}$에 대해 각 $x_n$은 다음과 같이 표현
			  $$x_n = \sum_{i \in [D]} \alpha_{ni} u_i \quad \text{where} \quad \alpha_{ni} \overset{\text{def}}{=} x_n^\top u_i$$
				- $\alpha_{ni}$: $x_n$을 $u_i$ 방향으로 투영한 값<br/><br/>
		- **$M$-dimensional Linear Subspace**
			- $x_n$을 $M$개의 주요 기저 벡터 $\{u_i\}_{i\in[M]}$로 표현하고, 나머지 $D-M$개의 기저 벡터는 잔차를 모델링
			  $$\tilde{x}_n = \sum_{i=1}^M z_{ni} u_i + \sum_{i=M+1}^D b_i u_i$$
		- **Projection Factor**
			- $z_{ni}$: $M$차원 기저 벡터에 투영된 값.
			  $${\partial J\over \partial z_{ni}}=0\quad\implies\quad z_{ni}=x_n^\top u_i\overset{\text{def}}{=}\alpha_{ni}\quad\text{where}\quad \left\{ z_{ni} \right\}_{n\in[N], i=1, \dots, M}$$
			- $b_i$: 데이터 평균 $\bar{x}$에 의해 결정되는 값.
			  $${\partial J\over\partial b_i}=0\quad\implies\quad b_i=\bar{x}^\top u_i\quad\text{where}\quad \left\{ b_i \right\}_{i=M+1,\dots, D}$$
		- **Projected Error**
			- 모든 데이터에서 잔차의 제곱합으로 계산
			  $$J = \frac{1}{N} \sum_{n=1}^N \|x_n - \tilde{x}_n\|^2$$
			  $$x_n-\tilde{x}_n=\sum\limits_{i=M+1}^D\left( x_n^\top u_i - \bar{x}^\top u_i  \right) u_i$$
			$$\begin{align*}
			J =\sum\limits_{i=M+1}^D u_i^\top S u_i
			\end{align*}$$
	- **Optimization Problem**
		- Objective function: $\underset{\left\{ u_i \right\}_{i\in[D]}}{\min} \, \sum_{i=M+1}^D u_i^\top S u_i$
		- Constraint: $u_i^\top u_j = \delta_{ij}\overset{\text{def}}{=}\begin{cases}1 & \text{if } i = j \\0 & \text{if } i \neq j\end{cases}$

<br/>

```ad-tip
title: **Minimum Error Formulation**
- $J$를 최소화하려면, $D-M$개의 고유값이 가장 작은 고유벡터를 잔차로 선택하고, 상위 $M$개의 고유값이 해당하는 고유벡터로 데이터를 표현
- 데이터를 $M$차원으로 압축하면서, $D-M$차원의 잔차(설명되지 않은 정보)를 최소화하는 방식
```

<br/><br/>

## PCA for High-dimensional Data
- **Definition**
	- 데이터의 **차원 수($D$)**가 **데이터 포인트 수($N$)**보다 큰 고차원 데이터를 다룰 때 계산 복잡도가 높아지는 문제를 해결하기 위한 최적화 방된 방법<br/><br/>
	- **계산 복잡도**
		- 공분산 행렬 $S \in \mathbb{R}^{D \times D}$를 계산하고 고유분해(eigen decomposition)하는 비용: $O(D^3)$
		- $D$가 매우 크다면 계산이 **비현실적(computationally intractable)**
	- **차원 축소의 한계**
		- 최소 $D - N + 1$개의 고유값은 $0$이므로, $N$차원으로만 의미 있는 정보가 존재

<br/>

- **Key Concepts**
	- Covariance Matrix
		- $X \in \mathbb{R}^{N \times D}$: $N$개의 데이터 포인트를 포함하는 행렬.
		- $n$번째 행은 $(x_n - \bar{x})^\top$로 표현<br/><br/>
		- Covariance Matrix: $S = \frac{1}{N} X^\top X$<br/><br/>
	- Eigenvector equation
	  $$S u_i = \lambda_i u_i, \quad u_i \in \mathbb{R}^D$$
		$$\begin{align*}
		\frac{1}{N} X^\top X u_i &= \lambda_i u_i\\\\
		\frac{1}{N} XX^\top (Xu_i) &= \lambda_i (Xu_i)\\\\
		\frac{1}{N} XX^\top v_i &= \lambda_i v_i,\quad v_i=X u_i\in\mathbb{R^N}
		\end{align*}$$
		- $XX^\top$의 고유값 $\lambda_i$와 고유벡터 $v_i$를 계산
			- $XX^\top\in\mathbb{R}^{N\times N}$은 $X^\top X\in\mathbb{R}^{D\times D}$보다 훨씬 작은 행렬
			- 계산 복잡도: $O(N^3)$<br/><br/>
		- $S$의 고유벡터 $u_i$는 다음과 같이 계산:
		  $$u_i = \frac{1}{\sqrt{N \lambda_i}} X^\top v_i$$
