---
date: 2024-10-13
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
# Classification
```ad-note
title: Recap Regression
- Regression
	- 연속적인 값(실수)을 예측하는 작업
	- 입력$x$과 출력$y$ 간의 관계를 학습하는 함수 $f$를 추정
	- 실제 값과 예측 값의 차이가 작을 수록 더 좋은 성능을 가진 모델로 평가됨
		- e.g., age prediction

- Approach for regression
	- Linear 또는 non-Linear 모델을 사용하여 매개변수 $w$로 $f_w(x) = y$를 예측
	- Training과 Evaluation에서 동일한 Loss function ($L_2$ distance) 사용
	  ([[Linear Regression#Loss Function Conditional Mean|Loss function of Linear regression]])
		- Training loss: $\mathbb{E}_{(x, y) \sim D_{train}} [\|y - f_w(x)\|^2]$
		- Evaluation metric: $\mathbb{E}_{(x, y) \sim D_{test}} [\|y - f_w(x)\|^2]$
	- [[Gradient Descent|Gradient-based optimizer]]를 사용하여 학습
```

- Classification
	- 입력 벡터 $\mathbf{x}$를 여러 클래서 $C$ 중 하나로 분류하는 문제
	- Regression과 달리 정확한 결과가 요구되며, 중간값을 허용하지 않음
	- Classification task도 Regression과 마찬가지로 Model, Loss function, Evaluation metric과 같은 기본 구성 요소가 필요하며, 몇 가지 매개화된 모델을 사용하여 학습

<br>

## Classification Model
### Decision Boundary
- 결정 경계
	- Decision region 간의 경계이며, 분류기 설계는 결정 경계를 그리는 것
		![[Pasted image 20241013171612.png]]
- 두 클래스 $C_1$, $C_2$가 있다고 가정
	- 새로운 데이터 포인트 $x$가 $C_1$에 할당되려면, $x$는 $C_1$의 결정 영역 $\mathcal{R}_1$에 있어야 함
	- 즉, 분류 함수 $h(x) = k$는 $x \in \mathcal{R}_k$일 때 클래스 $C_k$에 할당됨
- Decision boundary는 Discriminant function으로 부터 유도됨
	- $h(x) = \arg \max_k f_k(x)$
		- 즉, $x$를 점수($f_k(x)$)가 가장 높은 클래스 $C_k$로 할당

<br>


### Discriminant Function: Bayes Decision Rule
- 판별 함수(Discriminant function)
	- 각 클래스에 대해 점수나 확률을 계산하는 함수
	- 입력 데이터에 대해 각 클래스에 할당될 확률을 계산하며, 가장 높은 확률을 가진 클래스로 데이터를 분류
		- 모든 $j \neq k$에 대해 $f_k(x) > f_j(x)$일 때, $x$를 클래스 $C_k$에 할당
			- $\{f_k\}_{k=1,...,K}$: Discriminant function / Score
	- 만약 $f_k(·)$가 판별 함수라면, 단조 증가 함수 $g$를 사용해도 판별 함수로 적용 가능
		- e.g., $a\cdot f_k(x)+b$ for any $a>0$ and $b$
		- e.g., $\log{f_k(\cdot)}$

- Bayes Decision Rule
	- 분류 문제에서 가장 높은 사후 확률을 가진 클래스로 데이터를 분류하는 규칙
		$$f_k(x)=p(C_k|x)\propto p(x|C_k)p(C_k)\qquad \hat{C}=\arg\underset{k}{\max}\text{ }p(x|C_k)$$
	- 각 클래스에 대한 사전 확률(Prior probability, $p(C_k)$)를 기반으로 모델을 설계할 수 있음
		- e.g., 강아지와 고양이에 대한 사전 분포를 알면 해당 동물이 등장할 확률을 추정할 수 있음
	- 여기서 Likelihood($p_k(x|C_k)$)는 각 클래스별 특징이 분포화된 함수
		- e.g., 강아지와 고양이 클래스의 특징을 분포화하고, 강아지 클래스에서 해당 이미지가 나올 확률, 고양이 클래스에서 해당 이미지가 나올 확률을 계산
	- [[Optimality of Bayes Decision Rule]]

- Decision Boundary
	- 각 클래스의 사후 확률이 같아지는 지점에 Decision boundary를 형성하여 최적의 분류 모델을 생성할 수 있음

	![[Pasted image 20241013183814.png|450]] ^8yvmro


<br>

### How to Define the Posterior Probability - Regression
- Bayes Decision Rule의 최적성을 바탕으로 분류기 $h$보다 판별 함수 $f_k\approx p(C_k|x)$를 사용해 데이터를 특정 클래스에 할당하는 방식으로 모델링
	- 이를 통해 Classification task를 Regression task로 변환할 수 있음
	  (왜 변환해야 하는가)
- 하지만, 이를 위해선 $f_k\in \left\{0, 1\right\}$를 잘 근사할 수 있는 확률적 모델이 필요하며, Logistic Regression 모델을 사용

<br>

#### Linear vs. Logistic Regression for Classification
![[Pasted image 20241013200548.png|500]]
##### [[Linear Regression]] for Classification
- 연속적인 값을 예측하기 위해 선형 함수를 사용
  $$y = w^T x + b$$
- 평균 제곱 오차 (MSE, Mean Squared Error)를 최소화하는 방식으로 매개변수 $w$를 학습
  $$L(w) = \sum_{n=1}^{N} \left( y_n - w^T x_n \right)^2$$

- 분류 문제에서의 문제점
	- 확률 예측이 불가능
		- 선형 회귀는 확률이 아닌 실수 값을 예측하므로, 분류 문제에 적합하지 않음
			- Classification task에서 확률은 [0, 1] 사이 값을 가져야 함
			- Linear regression은 Unbounded value를 가짐
	- [[Overfitting]]
		- Linear regression은 일부 데이터 포인트에 과적합되기 쉬움
		  ![[Pasted image 20241013215911.png]]
	- MSE는 분류 문제에 적합하지 않음
		- MSE는 분류기에서 올바르게 예측된 경우에도 높은 오차를 줄 수 있음
		- 특히, 확률 값이 매우 작은 경우에는 큰 패널티를 부여하지 못함

<br>

##### Logistic Regression for Classification
- Binary classification task를 해결하기 위한 Regression 방법
- [[Logistic Function#Sigmoid Function|Logistic Function]]을 사용하여 입력 데이터가 클래스 1에 속할 확률을 0~1 사이 값으로 예측
	- 즉, $y\in \left\{0, 1\right\}$인 경우의 확률을 모델링
	- Linear regression은 Boundary가 없기 때문에 {0, 1} 사이로 조정하기 위해 사용
		```ad-note
		title: Logistic regression with sigmoid function $\sigma(\cdot)$
		
		$$p(y = 1 | x) = \sigma(\xi(x)) = \frac{1}{1 + \exp(-\xi(x))}$$
		$$\sigma(\xi) \to 1 \text{ as } \xi \to \infty, \quad \sigma(\xi) \to 0 \text{ as } \xi \to -\infty$$
		```
- 로그 손실(Log loss) 또는 크로스 엔트로피(Cross entropy)를 사용하여 모델을 최적화
	- Log loss는 잘못된 예측에 대해 더 큰 패널티를 부여하며, 확률이 0에 가까울 때 매우 큰 패널티 부여

```ad-note
title: Logistic regression for classification

- 데이터셋 $D = (x_n, y_n)_{n \in [N]}$에서 $x_n \in \mathbb{R}$, $y_n \in \{-1, +1\}$
	
	$$\begin{align*}
	p(y_n = 1 | x_n, w) &= \frac{1}{1 + \exp(-w^T x_n)}\\\\
	p(y_n = -1 | x_n, w) &= 1 - p(y_n = 1 | x_n) = \frac{1}{1 + \exp(w^T x_n)}\\\\\\
	\text{In other words}\quad p(y_n|x_n, w)&={1\over 1+\exp(-y_nw^T x_n)}
	\end{align*}$$
	- 여기서 $x_n$은 $\phi(x_n)$로 대체될 수 있음
```

- 분류 문제에서의 장점
	- 과적합 문제 해결
		- Logistic regression은 Linear regression에 비해 과적합 문제가 덜 발생
	- 확률적 해석
		- 결과를 확률로 예측하기 때문에, 분류 문제에서 보다 직관적인 결과를 제공

<br>

## Evaluation for Classification Model
### 0-1 Loss Function
$$L(w, b)=\text{ }{1\over m}\sum\limits_{i=1}^N\mathbb{1}\left[y^{(i)}\ne\mathbb{1}\left[f_{w, b}\left(x^{(i)}\right)>0.5\right]\right]$$

- 분류기가 예측한 값 $f_{w, b}(x)$가 실제 값 $y$와 다른 경우에만 오류로 간주
- Zero gradient problem ^ux4jxs
	- 분류 문제는 클래스 $K$ 중 하나로 결정되어야 하는 특성 때문에 대부분의 Gradient가 0이 되는 문제가 발생

![[Pasted image 20241013223326.png]]

<br>

### MSE (Mean Square Error)
([[Least Square Method]])
$$L(w, b)={1\over m}\sum\limits _{i=1}^N\left(f_{w, b}\left(x^{(i)}\right)-y^{(i)}\right)^2$$

- 분류기가 예측한 값과 실제 값 사이의 유클리드 거리 ($L2$ distance)를 사용
- 미분이 가능하지만, 잘못된 예측에 대해 큰 처벌을 하지 않으며, 적합하지 않은 모델을 선택할 가능성이 있음
	- Loss function이 분류 정확도에 초점이 맞춰진 것이 아닌 예측 값과 실제 값의 차이에만 초점을 둠

<br>


### Log Loss
```ad-note
title: Log loss 유도 과정
collapse: true

$$\begin{align*}
p(y_n = 1 \mid x_n, w) &= \frac{1}{1 + \exp(-w^T x_n)}\\\\
p(y_n = 0 \mid x_n, w) &= 1 - p(y_n = 1 \mid x_n, w) = \frac{1}{1 + \exp(w^T x_n)}
\end{align*}$$

- Logistic regression의 확률 모델을 최대화하기 위해서 [[Maximum Likelihood Estimation]] 방법을 사용

$$\log{p(y_n|x_n, w)}=\sum_{n=1}^N \log p(y_n \mid x_n, w)$$
- 이 때, 두 가지 경우가 발생
	- $y=1$인 경우 (즉, $p(y_n=1|x_n, w)$를 최대화)
	  $$\ell(f_{w,b}(x), 1) = -\log(f_{w,b}(x))$$
		- If $f_{w, b}(x)\rightarrow 1$, then $-\log{f_{w. b}(x)}\rightarrow 0$
		- If $f_{w, b}(x)\rightarrow 0$, then $-\log{f_{w. b}(x)}\rightarrow \infty$
	- $y=0$인 경우 (즉, $p(y_n=0|x_n, w)$를 최대화)
	  $$ \ell(f_{w,b}(x), 0) = -\log(1 - f_{w,b}(x)) $$
		- If $f_{w, b}(x)\rightarrow 1$, then $-\log{f_{w. b}(x)}\rightarrow \infty$
		- If $f_{w, b}(x)\rightarrow 0$, then $-\log{f_{w. b}(x)}\rightarrow 0$
```

$$\begin{align*}
 L(w, b) &= \frac{1}{m} \sum_{i=1}^{m} \ell(f_{w,b}(x^{(i)}), y^{(i)})\\\\
&= \frac{1}{m} \sum_{i=1}^{m} -\left(y^{(i)}\log{f_{w. b}(x)}+\left(1-y^{(i)}\right)\log{(1-f_{w. b}(x))}\right)
\end{align*}$$

- Log loss는 잘못된 예측에 대해 더 큰 처벌을 부여
- Loss function이 예측 값과 실제 값의 차이가 아닌 분류 정확도에 초점을 두고 있기 때문에 Classification task에 적합

![[Pasted image 20241013233325.png]]

<br>

### 0-1 vs. MSE vs. Log Loss

![[Pasted image 20241013232443.png]]

|       | MSE loss                                                       | 0-1 loss | log loss                                              |
| ----- | -------------------------------------------------------------- | -------- | ----------------------------------------------------- |
| green | $\left(\frac{1}{3}\right)^2 \cdot \frac{50}{50} = \frac{1}{9}$ | $0$      | $\log{{3\over 2}\cdot {50\over 50}}=\log{{3\over 2}}$ |
| pink  | $\approx \frac{1}{50}$                                         | $1$      | $\approx {-\log 0 \over 50 }= \infty$                 |


<br><br>

## Optimization for Classification
- Logistic regression은 다음과 같은 Loss function $L(w)$를 최소화
  $$ \text{arg min}_w \sum_{n=1}^{N} \log(1 + \exp(-y_n w^T x_n)) $$
- 하지만, 이 Loss function은 해석적인 해가 존재하지 않기 때문에 [[Gradient Descent]] 방법을 사용하여 최적화 진행

<br>

### Gradient Descent for Classification
- Gradient
  $$ \nabla_w L(w) = - \sum_{n=1}^{N} \frac{-y_n \exp(-y_n w^T x_n)}{1 + \exp(-y_n w^T x_n)} x_n $$
- Gradient descent
  $$ w^{(t+1)} = w^{(t)} - \alpha \nabla_w L(w) $$

<br>

#### Alternative form: Gradient Ascent
- Likelihood
  $$ \prod_{n=1}^Np(y_n|x_n, w)=\prod_{n=1}^{N} \sigma(w^T x_n)^{y_n} (1 - \sigma(w^T x_n))^{1 - y_n} $$
- log-MLE
  $$ \arg\underset{w}{\max}\text{ }\sum_{n=1}^{N} \left[ y_n \log \sigma(w^T x_n) + (1 - y_n) \log (1 - \sigma(w^T x_n)) \right] $$
- Gradient
  $$ \nabla_w L(w) = \sum_{n=1}^{N} \left[ y_n - \sigma(w^T x_n) \right] x_n $$
- Gradient ascent
  $$ w^{\text{new}} = w^{\text{old}} + \eta \nabla_w L(w) $$


<br><br>

## Summary
- **Aim of Classification**
	- $\phi(x_i)$가 입력 점 $x_i$의 특징을 나타낼 때 Classification task는 $y_i w^\top \phi(x_i) > 0$이 되는 것을 목표로 하며, 이는 0/1 Loss를 최소화 하는 것을 의미
	  $$\sum_{i=1}^{N} \mathbb{1}\left[ y_i w^\top \phi(x_i) > 0 \right] \quad \text{(0/1 loss)}$$
- **Methods**
	- Linear Regression
	  $$\min_{w, b} \frac{C_0}{2} ||w||^2 + \sum_{i=1}^{N} \left(1 - y_i w^\top \phi(x_i)\right)^2 \quad \text{(Quadratic loss)}$$
	- Logistic Regression
	  $$\min_{w, b} \frac{C_0}{2} ||w||^2 + \sum_{i=1}^{N} \log\left(1 + \exp\left(-y_i w^\top \phi(x_i)\right)\right) \quad \text{(Log loss)}$$
	- [[Support Vector Machine|Binary SVM]]
	  $$\min_{w, b} \frac{C_0}{2} ||w||^2 + \sum_{i=1}^{N} \max\left(0, 1 - y_i \left(w^\top \phi(x_i) + b\right)\right) \quad \text{(Hinge loss)}$$
	- General Classification
	  $$\min_{w,b} \frac{C'}{2} ||w||^2 + \sum_{i=1}^{N} \epsilon \log \left( 1 + \exp \left( \frac{L - y_i w^\top \phi(x_i)}{\epsilon} \right) \right)$$