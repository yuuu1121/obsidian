---
date: 2024-10-20
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
```ad-tip
title: Recap) [[Support Vector Machine#Soft Margin SVM|Binary Soft Margin SVM]]
- Dual Problem
	- Objective function:
	  $$\max_{\alpha} \left( - \frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j \phi(x_i)^\top \phi(x_j) + \sum_{i=1}^{N} \alpha_i \right)$$
	- Constrain:
	  $$\sum_{i=1}^{N} \alpha_i y_i = 0\qquad 0 \leq \alpha_i \leq C \quad \forall i = 1, ..., N$$
	- Decision Boundary:
	  $$\text{sign}(w^\top \phi(x) + b) = \text{sign}\left( \sum_{n} \alpha_n \phi(x_n)^\top \phi(x) + b \right)$$
- Disadvantage:
	- 결정 경계와 최적해 모두 $\phi(x_i)^\top \phi(x_j)$에 의존하며, 이는 모든 데이터 쌍에 대해 고차원 특징 벡터의 내적을 계산해야 한다는 것을 의미
	- $\phi(x_i)^\top \phi(x_j)$에 의존하는 것은 고차원에서의 계산이 복잡

```

<br>


# Kernel Trick
- **Definition**
	- SVM이 고차원 공간에서 데이터를 효율적으로 처리하기 위한 방법.
	- 고차원 피처 공간으로 데이터를 **매핑(mapping)하지 않고도**, 그 공간에서의 내적(두 데이터 간의 유사도)을 계산
		- e.g., **RBF Kernel**은 무한 차원의 특성도 처리할 수 있음.

<br>

- **Advantage**
	- 커널 트릭을 사용하면, 피처 벡터 $\phi(x)$를 직접 계산하지 않고, 대신 커널 함수를 사용하여 유사도 계산을 통해 고차원에서의 연산을 단순화할 수 있음.


<br>

## Key Concepts
### Kernel Function
- **Definition**
	- 두 데이터 포인트 $x_i$, $x_j$ 사이의 내적을, 고차원으로 변환된 $\phi(x_i)$와 $\phi(x_j)$ 간의 내적으로 직접 계산하는 대신, 입력 공간에서 바로 계산하여 연산을 단순화하는 함수
	- 두 데이터 포인트 간의 유사도(similarity)를 측정하며, 모든 머신러닝 알고리즘에서 입력 간 내적을 활용.
	- $N$개의 데이터 포인트가 있으면, $N \times N$ 크기의 커널 행렬이 만들어 지며, 각 행렬의 원소 $K_{ij}$는 $x_i$와 $x_j$ 사이의 커널 함수 $\kappa(x_i, x_j)$의 값<br><br>
	- Equation:
	  $$\kappa : X \times X \to \mathbb{R}$$
	- Examples:
		
		```ad-example
		title: Soft Margin SVM
		collapse: true
		
		$$\begin{align*}
		&\max_{\alpha} \left( - \frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j \phi(x_i)^\top \phi(x_j) + \sum_{i=1}^{N} \alpha_i \right)\\\\
		\rightarrow&\max_{\alpha} \left( - \frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j \kappa(x_i, x_j) + \sum_{i=1}^{N} \alpha_i \right)
		\end{align*}$$
		- 학습 중에 피처 맵 $\phi$를 계산할 필요가 없음
		```
		
		```ad-example
		title: [[Gradient Descent]] with [[Lease Square Method]]
		collapse: true
		- 최소 제곱법을 위한 경사 하강법
		  $$\theta \leftarrow \theta + \eta \sum_{n=1}^{N} (y_n - \theta^\top \phi(x_n))\phi(x_n)$$
		- 여기서, $\theta$는 $\phi(x_1), ..., \phi(x_N)$의 선형 결합
		  $$\theta = \sum_{n=1}^{N} \alpha_n \phi(x_n)$$
		- 따라서, 업데이트 단계는 다음과 같이 다시 작성될 수 있음
		  $$\alpha_n \leftarrow \alpha_n + \eta(y_n - \theta^\top \phi(x_n))$$
		- 커널 함수를 사용하면 다음과 같음
			$$\alpha_i \leftarrow \alpha_i + \eta \left( y_i - \sum_{j=1}^{N} \alpha_j \kappa(x_i, x_j) \right)$$
		```

<br>

### Mercer's Theorem
- **Definition**
	- 유효한 커널 함수 $\kappa$가 있는 한, 피처 함수 $\phi$를 명시적으로 정의할 필요 없음.
	- 모든 함수가 유효한 커널이 될 수는 없으며, 커널이 유효하려면 $\kappa(x_i, x_j)$로 이루어진 **커널 행렬**이 **대칭성(Symmetricity)** 및 **양의 준정부호(Positive semi-definiteness)** 조건을 만족해야 함.<br><br>
	- **Key Concepts**
		- **Symmetricity**
			- 커널 함수 $\kappa(x_i, x_j)$가 **두 데이터 포인트를 바꿔도 값이 변하지 않는** 성질
			  $$\kappa(x_i, x_j) = \kappa(x_j, x_i)$$
		- **Positive semi-definiteness**
			- 모든 벡터에 대해 커널 함수가 양수 값을 가져야 함
			  $$ v^\top K v \geq 0 $$
			- 양의 준정부호 성질은 **커널 행렬**이 **유효한 피처 맵**에 대응된다는 것을 보장

<br>

### Kernel Generation Methods
1. Positive scaling
   $$\kappa(x^{(i)}, x^{(j)}) = c\kappa_1(x^{(i)}, x^{(j)})$$

1. Exponentiation
   $$\kappa(x^{(i)}, x^{(j)}) = \exp(\kappa_1(x^{(i)}, x^{(j)}))$$

1. Addition
   $$\kappa(x^{(i)}, x^{(j)}) = \kappa_1(x^{(i)}, x^{(j)}) + \kappa_2(x^{(i)}, x^{(j)})$$

1. Multiplication with function
   $$\kappa(x^{(i)}, x^{(j)}) = f(x^{(i)})\kappa_1(x^{(i)}, x^{(j)})f(x^{(j)})$$

1. Multiplication
   $$\kappa(x^{(i)}, x^{(j)}) = \kappa_1(x^{(i)}, x^{(j)})\kappa_2(x^{(i)}, x^{(j)})$$

<br>

## Examples of Kernel
### Gaussian kernel
- **Definition**
	- $\phi(x_i)$와 $\phi(x_j)$의 거리가 가까울수록 $\kappa(x_i, x_j)$가 커지고, 반대로 거리가 멀면 작아짐.
		$$\kappa(x_i, x_j) = \exp\left(-\frac{\|x_i - x_j\|^2}{2\sigma^2}\right)$$
	- 이 커널을 Gaussian kernel 혹은 무한 차원의 피처 공간을 처리하는 Radial Basis Function (RBF) kernel 이라고 부름
	  $$\phi(x) = \left[ \exp\left( -\frac{x^2}{2\sigma^2} \right), \frac{x}{\sigma}, \frac{x^2}{\sigma^2}, \frac{x^3}{\sigma^3}, \dots \right]$$

<br>

### Polynomial Kernel
- **Definition**
	- 두 벡터 간의 내적을 다항식으로 확장하여 고차원 공간의 피처를 암시적으로 계산하는 방법.
	  $$\kappa(x, x') = (\langle x, x' \rangle + 1)^p = \phi(x)^\top \phi(x')\qquad \text{degree}\quad p$$
- **Example**
	- $x = [x_1, x_2]^\top \in \mathbb{R}^2$, $p = 2$일 때 대응하는 피처 맵
	  $$\phi(x) = [1, \sqrt{2}x_1, \sqrt{2}x_2, \sqrt{2}x_1x_2, x_1^2, x_2^2]^\top$$
	- 피처 $\phi(x)$로 변환 후 내적을 계산하는 대신, 커널 함수를 직접 계산하는 것이 훨씬 빠름.

<br>

### Others
- **선형 커널 (Linear Kernel)**:
   $$\kappa(x^{(i)}, x^{(j)}) = x^{(i)\top} x^{(j)}$$

- **시그모이드 커널 (Sigmoid Kernel)**:
   $$\kappa(x^{(i)}, x^{(j)}) = \tanh(a \cdot x^{(i)\top} x^{(j)} + b)$$