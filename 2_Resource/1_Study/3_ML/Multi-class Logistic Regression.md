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
# Multi-class Logistic Regression
- **Definition**
	- 입력 데이터 $x$가 $K$개의 클래스 중 하나에 속할 확률을 예측하는 모델로, **다항 분포 모델**을 사용하여 각 클래스에 대한 확률을 계산.
- **Key Concepts**
	- Discriminant Function - [[Logistic Function|Softmax Function]]
		- 각 클래스에 대한 점수를 확률로 변환하여 예측
			$$p(y = k|x) = \frac{\exp(w_k^\top \phi(x))}{\sum_{j=1}^{K} \exp(w_j^\top \phi(x))}$$
		- 여기서,
			- $p(y = k|x)$: 데이터 $x$가 클래스 $k$에 속할 확률
			- $w_k$: 클래스 $k$에 대한 가중치 벡터
			- $\phi(x)$: 입력 데이터 $x$에 대한 [[Linear Regression#Basis (Feature]]%20Functions|Basis%20Function)
	- Classifier - [[Classification#Discriminant Function Bayes Decision Rule|Bayes Decision Rule]]
		- 분류기는 가장 높은 확률(점수)를 가진 클래스를 선택하여 데이터를 분류
		  $$\arg\max_k p(y = k|x) = \arg\max_k w_k^\top \phi(x)$$
	- Optimization - [[Maximum Likelihood Estimation]]
		- 가중치($w=(w_{(y)})_{y=1, \cdots, K}$) 학습은 log-MLE 방법을 사용
		  $$\arg\max_w \prod_{i=1}^{N} p(y = y_i | x^{(i)}) = \arg\min_w \left(- \log p\left(y = y_i | x^{(i)}\right)\right)$$
- **Example**
	- $\phi(x^{(i)}) = 1$ (상수 항)일 때, $K=2$ (이진 분류)인 경우, 만약 $w^{(1)} = -w^{(2)}$라면, **결정 경계**는 **선형**이 되며 **이진 로지스틱 회귀**와 유사하게 동작.
	
	![[Pasted image 20241021020518.png]]![[Pasted image 20241021020533.png]]