---
date: 2024-10-19
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
# Support Vector Machine
- **Definition**
	- Classification 및 Regression 문제에서 사용되는 Supervised learning 알고리즘
	- 주로 Binary classification 문제에서 많이 사용되며, 데이터를 나누는 최적의 Hyperplane을 찾는 것이 목표
- **Components**
	- [[Maximizing Margin#Hyperplane|Hyperplane]]
		- SVM은 주어진 두 클래스를 가장 잘 구분할 수 있는 Hyperplane을 찾는 것이 목표
		- 이 Hyperplane은 두 클래스 간의 Margin을 최대화하는 방향으로 설정
	- [[Maximizing Margin#Margin|Margin]]
		- [[Classification#Decision Boundary|Decision boundary]]와 가장 가까운 데이터 포인트(Support vector) 사이의 거리
		- SVM은 이 마진을 최대화하는 방향으로 학습
		- 마진이 클수록 일반화 성능이 좋아지며, 새로운 데이터에 대해 더 잘 분류할 수 있게 됨 ([[Maximizing Margin#^l51e7s|마진의 중요성]])
	- Support Vector ^woow1r
		- Decision boundary에 가장 가까이 위치한 데이터 포인트들로, 결정 경계를 결정하는 데 핵심적인 역할을 함
			- 즉, $y_i(w^\top x_i + b) = 1$를 만족하는 데이터 포인트 ([[Maximizing Margin#^dj2dr3|Canonical Hyperplane]])
		- Support vector 외의 다른 데이터 포인트들은 Decision boundary에 영향을 미치지 않음
	- Hard Margin
		- 모든 데이터가 선형으로 완벽하게 분리될 수 있을 때 적용
		- 현실에서는 완벽하게 분리되지 않는 경우가 많음
	- Soft Margin
		- 선형으로 완벽하게 분리되지 않는 데이터를 처리하기 위해 약간의 오류를 허용하며 마진을 최대화하는 방식

<br>

## Constrained Optimization
### Hard Margin SVM
#### Primal Problem
- **[[Constrained Optimization|Problem Definition]]**
	- Maximum Margin Classifier:
	  선형으로 분리 가능한 데이터셋에서 가장 큰 마진을 가진 분류기를 찾는 문제<br><br>
	- Objective function:
	  $$\min_{w,b} J(w) = \frac{1}{2} ||w||^2$$
	- Constrain
		- 모든 데이터 포인트가 결정 경계에서 최소 1의 마진을 가지도록 제약
	  $$\begin{align*} y_i (w^\top x_i + b) \geq 1, \ i = 1, ..., N\\\\g_i(w)=1-y_i (w^\top x_i + b)\le0\end{align*}$$

<br>

- Primal Lagrangian Function
	- Objective function에 제약 조건을 포함하여 KKT 조건을 만족시키는 해를 찾음
	  $$L(w, b, \alpha) = \frac{1}{2} ||w||^2 + \sum_{i=1}^{N} \alpha_i \left( 1 - y_i (w^\top x_i + b) \right)$$
		- 여기서 $\alpha_i$는 Lagrangian multiplier

<br>

#### KKT Necessary Condition
- $\frac{\partial L}{\partial w} = 0$ 및 $\frac{\partial L}{\partial b} = 0$일 때,
	$$\begin{align*}
	&w = \sum_{i=1}^{N} \alpha_i y_i x_i\\\\
	&\sum_{i=1}^{N} \alpha_i y_i = 0
	\end{align*}$$
- 이를 Lagrangian Function에 대입하면 다음 식을 얻을 수 있음
  $$L(w, b, \alpha) = -\frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j x_i^\top x_j + \sum_{i=1}^{N} \alpha_i-\sum\limits_{i=1}^N\alpha_iy_ib$$
```ad-tip
title: Proof
collapse: true
$$\begin{align*}
w^\top &= \left(\sum\limits_{i=1}^N(\alpha_iy_ix_i)\right)\\\\
 &= \sum\limits_{i=1}^N(\alpha_iy_ix_i)^\top\\\\
 &= \sum\limits_{i=1}^N \alpha_iy_ix_i^\top\\\\\\
||w|| &= w^\top w\\\\
 &= \sum\limits_{i=1}^N\sum\limits_{j=1}^N\alpha_i\alpha_jy_iy_jx_i^\top x_j\\\\\\
\sum_{i=1}^{N} \alpha_i \left( 1 - y_i (w^\top x_i + b) \right) &= \sum\limits_{i=1}^N\alpha_i-\sum\limits_{i=1}^N\sum\limits_{j=1}^N\alpha_i\alpha_jy_iy_jx^\top x_j-\sum\limits_{i=1}^N\alpha_iy_ib
\end{align*}$$
```

- **Complementary Slackness**
  $$\alpha_i \left(1 - y_i (w^\top x_i + b)\right) = 0$$
  1. $y_i (w^\top x_i + b) \neq 1$
     - $\alpha_i=0$이며, $x_i$는 $w=\sum\limits_{i=1}^N\alpha_iy_ix_i$에 영향을 미치지 못하기 때문에 Support vector가 아님
	2. $y_i (w^\top x_i + b) = 1$
	   - 제약 조건이 활성화되며, $x_i$는 $w$ 계산에 영향을 미치는 Support vector

<br>

#### Dual Problem

- Lagrangian Dual Problem
	- Objective function:
		$$\max_{\alpha}\text{ }G(\alpha)=-\frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j x_i^\top x_j + \sum_{i=1}^{N} \alpha_i$$
		
	- Constrain:
	  $$\sum_{i=1}^{N} \alpha_i y_i = 0,\qquad \alpha_i \geq 0, \ i = 1, ..., N$$
	- 이 문제는 순차 최소 최적화(SMO) 알고리즘 등을 통해 해결 가능

<br>

- **Advantage**
	- Dual 문제는 차원과 무관한 복잡도를 가지며, 한 번 $x_i^\top x_j$를 계산한 후에는 효율적으로 계산될 수 있음.
	- 반면, Primal 문제는 제약 조건에서 $w^\top x_i$를 계산해야 하므로 차원에 따라 복잡도가 달라짐.

<br>

- **Implication**
	- $\alpha^*$가 Dual 문제를 해결한다고 가정하면, 선형으로 분리 가능한 학습 샘플 $D = \{(x_i, y_i)\}_{i=1}^{N}$이 주어졌을 때, 가중치 벡터 $w^* = \sum_{i=1}^{N} \alpha_i^* y_i x_i$는 기하학적 마진 $\rho = \frac{1}{||w||}$을 실현하는 최대 마진 초평면을 형성

<br>

##### Duality
- 선형으로 분리 가능한 데이터에서 Strong Duality가 성립
	- 즉, Primal 문제와 Dual 문제의 해가 동일함을 의미 ($J(w^*) = G(\alpha^*)$)
- [[Constrained Optimization#Slater's Sufficient Condition|Slater 조건]]
	- Slater 조건은 강한 이중성이 성립하기 위한 충분 조건이며, 선형으로 분리 가능한 데이터셋은 Slater 조건을 만족함

<br><br>

### Soft Margin SVM
- **Definition**
	- Support Vector Machine(SVM)이 선형적으로 완벽하게 분리되지 않는 데이터셋에 대해 적용될 수 있도록 확장된 형태
	- 실제 데이터는 노이즈가 포함되어 있을 수 있으며, 모든 데이터 포인트를 Decision boundary에 왑녁하게 맞추는 것은 불가능
	- 이때, Slack 변수 ($\zeta_i$)를 도입하여 제약 조건을 완화함으로써 일부 데이터 포인트가 결정 경계를 약간 넘을 수 있도록 허용하여 더 일반적인 데이터에 대해 유연하게 대응할 수 있게 함

<br>

#### L2 Norm
- **Problem Definition**
	- Slack 변수의 L2 Norm을 최소화하는 동시에 마진을 최대화하는 최적화 문제
	- 이로 인해 마진을 약간 위반하는 데이터에 대해 더 **부드럽게** 처리<br><br>
	- Objective Function:
	  $$\min_{w,b,\zeta} \frac{1}{2} ||w||^2 + C \sum_{i=1}^{N} \zeta_i^2$$
		- 여기서 $\zeta_i^2$는 각 슬랙 변수가 제곱된 형태로 들어가며, 슬랙 변수를 크게 위반한 데이터에 대해 더 큰 페널티를 부과
	- Constrain:
	$$y_i (w^\top x_i + b) \geq 1 - \zeta_i, \quad \zeta_i \geq 0, \ i = 1, \dots, N$$

<br>

- **Primal Lagrangian Function**
	$$L(w, b, \zeta, \alpha) = \frac{1}{2} ||w||^2 + C \sum_{i=1}^{N} \zeta_i^2 + \sum_{i=1}^{N} \alpha_i \left(1 - \zeta_i - y_i (w^\top x_i + b)\right)$$

<br>

- **KKT Necessary Condition**
	$$w = \sum_{i=1}^{N} \alpha_i y_i x_i\qquad \sum_{i=1}^{N} \alpha_i y_i = 0\qquad \zeta_i = \frac{\alpha_i}{C}$$

<br>

- **Lagrangian Dual Problem**
	- Objective Function:
	  $$\max_{\alpha}\text{ }G(\alpha) = \sum_{i=1}^{N} \alpha_i - \frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j x_i^\top x_j - \frac{1}{2C} \sum_{i=1}^{N} \alpha_i^2$$
		- **Dual 문제**에서 추가적으로 슬랙 변수 $\zeta_i$에 대한 제곱 항이 포함되어, 슬랙 변수가 큰 데이터에 대해 더 큰 벌칙을 부과
	- Constrain:
	  $$\sum_{i=1}^{N} \alpha_i y_i = 0, \quad \alpha_i \geq 0$$

<br>

#### L1 Norm
- **Problem Definition**
	- Slack 변수의 절대값을 사용하는 L1 Norm을 사용하여 마진 위반에 대한 벌칙을 부과<br><br>
	- Objective Function:
	  $$\min_{w,b,\zeta} \frac{1}{2} ||w||^2 + C \sum_{i=1}^{N} \zeta_i$$
	- Constrain:
	$$y_i (w^\top x_i + b) \geq 1 - \zeta_i, \quad \zeta_i \geq 0, \ i = 1, \dots, N$$

<br>

- **Primal Lagrangian Function**
	$$L(w, b, \zeta, \alpha, \beta) = \frac{1}{2} ||w||^2 + C \sum_{i=1}^{N} \zeta_i - \sum_{i=1}^{N} \alpha_i \left( y_i (w^\top x_i + b) - 1 + \zeta_i \right) - \sum_{i=1}^{N} \beta_i \zeta_i$$

<br>

- **Lagrangian Dual Problem**
	- Objective Function:
	  $$\max_{\alpha} G(\alpha) = \sum_{i=1}^{N} \alpha_i - \frac{1}{2} \sum_{i=1}^{N} \sum_{j=1}^{N} \alpha_i \alpha_j y_i y_j x_i^\top x_j$$
	- Constrain:
	  $$\sum_{i=1}^{N} \alpha_i y_i = 0, \quad 0 \leq \alpha_i \leq C, \quad i = 1, ..., N$$
		- Hard Margin SVM과의 차이점은 $\alpha_i$에 상한 $C$가 있다는 점
		- $C$는 마진 위반에 대한 페널티를 조절하는 역할을 하며, $C$가 클수록 마진 위반을 엄격하게 처리

<br>

- **Penalty Method**
	- L1 소프트 마진 SVM의 목적 함수는 작은 $C_0$ 값일 경우 하드 마진 SVM과 동일한 해를 제공
	  $$\min_{w,b,\zeta} \frac{C_0}{2} ||w||^2 + \sum_{i=1}^{N} \max(0, 1 - y_i (w^\top x_i + b))$$
	- $C_0$가 충분히 작을 경우, 슬랙 변수를 최소화하는 것이 큰 의미가 없어지며, 하드 마진과 동일하게 동작