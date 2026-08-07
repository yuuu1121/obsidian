---
date: 2024-10-17
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
# Hyperplane
- Hyperplane
	- 수학적 정의
		- 다차원 공간에서 데이터를 두 그룹으로 나누는 경계면을 의미
	- 수식:
	  $$ w^\top x + b = 0 $$
		- 여기서,
			- $w$: Hyperplane의 수직 벡터(normal vector). Hyperplane의 방향을 나타냄
			- $x$: 데이터 포인트(벡터). 즉, 주어진 공간의 한 점
			- $b$: 편향(bias)으로, Hyperplane이 원점에서 얼마나 떨어져 있는지를 나타냄
	- Classification에서의 역할
		- Hyperplane은 Classification task에서 두 클래스를 구분하는 경계 역할을 수행
		- 목적: Hyperplane은 데이터를 두 개의 그룹으로 나누어, 각 그룹이 서로 다른 클래스로 분류되도록 함
			- 연속성 가정: 서로 비슷한 데이터는 유사한 레이블로 분류된다고 가정
			- e.g., [[Support Vector Machine]] (SVM) 같은 알고리즘에서는 데이터를 두 그룹으로 나누는 최적의 Hyperplane을 찾는 것이 목표


```ad-tip
title: Recap) [[Classification#Logistic Regression for Classification|Regression for Classification]]
- 데이터셋 $D = (x_i, y_i)_{i=1,...,N}$, $y_i \in \{-1, 1\}$에서 $p(y = 1 | x)$를 근사
	- **선형 회귀**: $p(y = 1 | x) \approx w^\top \phi(x)$
	- **로짓 회귀**: $p(y = 1 | x) \approx \frac{1}{1 + \exp(-w^\top \phi(x))}$
	- 이러한 분류기는 모두 Hyperplane을 그림

![[Pasted image 20241013200548.png|500]]
```

<br><br>


# Margin
- **Definition**
	- 데이터 포인트와 Hyperplane, 즉 결정 경계 사이의 최소 거리를 의미

- **Components**
	- [[Classification#^8yvmro|Decision Boundary]]
		- 두 클래스를 나누는 Hyperplane으로 정의됨
		  $$ f(x) := w^\top x + b = 0 \quad (단, \ b > 0) $$

- **Key Concepts**
	- 점 $x$에서 결정 경계까지의 거리
		- 가중치 벡터 $w$는 Hyperplane에 수직이므로 다음과 같이 계산
		  $$ \frac{|f(x)|}{||w||} $$
	- Margin
		- 마진은 결정 경계에서 가장 가까운 데이터 포인트까지의 최소 거리로 계산되며, 다음과 같이 계산
		  $$ \min_i \frac{|f(x_i)|}{||w||} $$
	- Geometric Margin
		- 기하학적 마진은 다음과 같이 주어짐
		  $$ \rho = \frac{1}{2} \left( \frac{f(x^+) - f(x^-)}{||w||} \right) = \frac{1}{||w||} $$
		- 즉, 마진을 최대화하는 것은 가중치 벡터 $w$의 [[Norm]]을 최소화하는 것과 같음

- **Implications**
	- 작은 마진을 가진 Hyperplane은 과적합(overfitting)될 수 있으며, 새로운 데이터에 대해 성능이 떨어질 가능성이 있음
	- 마진을 최대화하면 Hyperplane에서 과적합을 방지하고, 일반화 성능을 높일 수 있음
![[Pasted image 20241017070924.png|+grid]]![[Pasted image 20241017074520.png|+grid]]

<br><br>

## Maximizing Margin
- Canonical Hyperplane ^dj2dr3
	- Identical Hyperplane
		- 임의의 $\lambda \neq 0$에 대해, $(\lambda w, \lambda b)$는 $(w, b)$와 동일한 Hyperplane
		  $$\{x | w^\top x + b = 0\} = \{x | \lambda(w^\top x + b) = 0\}$$
		- 이는 $w$와 $b$의 크기를 임의로 조정하더라도 같은 Hyperplane을 나타낸다는 것을 의미
	- Canonical 조건
		- $(w, b)$가 표준(canonical) 형태의 Hyperplane이 되기 위해서는 다음 조건을 만족해야 함
		  $$ \min_i |w^\top x_i + b| = 1 $$
	- 의미:
		- Canonical hyperplane은 Margin이 1이 되도록 $w$와 $b$의 크기를 고정된 형태
		- $w$와 $b$의 크기(scale)를 적절히 조정하여 마진 최대화 문제를 해결할 수 있는 기준이 됨

![[Pasted image 20241017074957.png|500]]


<br>

- [[Constrained Optimization]]
	- 제약 조건이 있는 상황에서 최적의 해를 찾는 문제
		- 즉, 어떤 목적 함수를 최소화하거나 최대화하면서 동시에 주어진 제약 조건을 만족해야 하는 문제
	- Objective function
		- 최적화하려는 대상(예: 비용, 손실 함수)
	- Constraints
		- 목적 함수를 최적화하는 동시에 만족해야 하는 제한 사항
		 - Equality constraint (등식 제약 조건): $h(x) = 0$

		 - Inequality constraint (부등식 제약 조건): $g(x) \leq 0$

```ad-example
title: Support Vector Machine
- Canonical Hyperplane을 고려할 때 마진 $\left(\frac{1}{||w||}\right)$을 고려하는 문제는 다음과 같이 공식화 할 수 있음
	- Objective function: $\min_{w,b} \frac{1}{2} ||w||^2$
	- Constraint: $y_i (w^\top x_i + b) \geq 1$ (모든 $i = 1, ..., N$에 대해)
		- 이 조건은 각 데이터 포인트가 정확히 분류함
		- $y_i$가 1인 경우 결정 경계의 오른쪽에, $y_i$가 -1인 경우 왼쪽에 있어야 하며, 그 사이에는 최소한의 마진이 있어야 함
- 이 공식을 (Hard-margin) binary [[Support Vector Machine]]이라고 함
```