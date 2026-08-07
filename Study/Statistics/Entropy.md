---
date: 2024-12-09
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/Statistics
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Information
- **Definition**
	- 특정 사건이 발생했을 때 얻는 정보의 양
	- 사건의 확률이 낮을수록 더 많은 정보 제공
		- $p(x) = 1$: 반드시 발생하는 사건의 정보량은 $I(x) = 0$

- **Equation**
	$$I(x) = -\log p(x)$$
	- $p(x)$: 사건 $x$가 발생할 확률.
	- $I(x)$: 사건 $x$가 발생했을 때 얻는 정보량.

<br><br>

# Entropy
- **Definition**
	- 확률 분포의 불확실성을 나타내는 값
	- 전체 분포에서 기대되는 정보량의 평균
	- 불확실성이 클수록(확률이 균등) 엔트로피 증가

<br>

- **Equation**
	$$H(p) = -\int p(x) \log p(x) dx$$

<br><br>

# Relative Entropy
- **Definition**
	- [[Maximum Likelihood Estimation#An Interpretation of MLE KL-Matching|KL-Divergence]]이라고도 하며, 두 확률 분포 간의 차이를 측정하는 값
	- 주어진 분포 $p(x)$와 근사 분포 $q(x)$간의 차이

<br>

- **Equation**
	$$D_{\text{KL}}(p \parallel q) = \int p(x) \log \frac{p(x)}{q(x)} dx$$


- **Properties**
	- KL-Divergence는 항상 0 이상 ([[Gibb's Inequality]])
	- 대칭적이지 않음: $D_{\text{KL}}(p \parallel q) \neq D_{\text{KL}}(q \parallel p)$
	  