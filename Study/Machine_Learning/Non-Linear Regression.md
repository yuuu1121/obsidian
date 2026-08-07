---
date: 2024-10-01
status: Permanent
tags:
  - Study/ML
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes:
  - "[[Linear Regression]]"
reference: 
author: 
url: 
dg-publish: false
---
# Continuous Optimization
- 많은 매개변수 추정 문제는 연속 최적화 문제로 공식화될 수 있음
	- Loss function의 최댓값 또는 최소값을 찾는 과정

$$\arg \min_{\theta} L(\theta) = \arg \min_{\theta} \sum_{i=1}^{N} \ell(y_i, f(x_i, \theta))$$

![[Pasted image 20241001181645.png]]

<br>

## Example
- 경험적인 Loss function이 매개변수 $\theta$로 parameterized된 함수라고 가정

$$L(\theta) = \sum_{i=1}^{N} \ell(y_i, f(x_i, \theta)) = \theta^4 + 7\theta^3 + 5\theta^2 - 17\theta + 3$$

- 이 경우, Loss를 최소화하는 매개변수 $\theta$를 찾기 위해, 경사가 0인 지점을 찾아야 하며, 2차 도함수를 사용하여 이를 확인할 수 있음

$$\frac{\partial L(\theta)}{\partial \theta} = 0$$


<br>

## Limitation
- 일부 Loss function에서는 $\frac{\partial L(\theta)}{\partial \theta} = 0$를 찾는 것이 불가능할 정도로 어려움
	- Abel-Ruffini 정리에 따르면, 5차 이상의 다항식에 대해서는 대수적 해를 찾을 수 없음
	- 즉, 일부 복잡한 함수에서는 수치적 방법(e.g., [[Gradient Descent]])이 필요
