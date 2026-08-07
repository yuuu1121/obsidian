---
date: 2024-10-21
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
title: Recap) [[Classification#Evaluation for Classification Model|Loss Function for Binary Classification]]
collapse: true
1. **Linear Regression**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \frac{1}{2} \left(1 - y^{(i)} w^\top \phi(x^{(i)}) \right)^2 $$

2. **Logistic Regression**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \log\left(1 + \exp\left(-y^{(i)} w^\top \phi(x^{(i)})\right)\right) $$

3. **Binary SVM**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \max\left(0, 1 - y^{(i)} w^\top \phi(x^{(i)})\right) $$

4. **General Binary Classification**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \epsilon \log\left(1 + \exp\left(\frac{L - y^{(i)} w^\top \phi(x^{(i)})}{\epsilon}\right)\right) $$
```

```ad-tip
title: Recap) Using Parameterized Feature
collapse: true
- $\theta$: Parameterized feature
<br>

1. **Linear Regression**:
   $$ \min_{w, \theta} \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \frac{1}{2} \left(1 - y^{(i)} w^\top \phi_\theta(x^{(i)}) \right)^2 $$

2. **Logistic Regression**:
   $$ \min_{w, \theta} \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \log\left(1 + \exp\left(-y^{(i)} w^\top \phi_\theta(x^{(i)})\right)\right) $$

3. **Binary SVM**:
   $$ \min_{w, \theta} \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \max\left(0, 1 - y^{(i)} w^\top \phi_\theta(x^{(i)})\right) $$

4. **General Binary Classification**:
   $$ \min_{w, \theta} \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \epsilon \log\left(1 + \exp\left(\frac{L - y^{(i)} w^\top \phi_\theta(x^{(i)})}{\epsilon}\right)\right) $$
```

```ad-tip
title: General Framework
collapse: true
- $f_w(x)$: [[Classification#Discriminant Function Bayes Decision Rule|Discriminant Function]]
<br>

1. **Linear Regression**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \frac{1}{2} \left(1 - y^{(i)} f_w(x^{(i)}) \right)^2 $$

2. **Logistic Regression**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \log\left(1 + \exp\left(-y^{(i)} f_w(x^{(i)})\right)\right) $$

3. **Binary SVM**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \max\left(0, 1 - y^{(i)} f_w(x^{(i)})\right) $$

4. **General Binary Classification**:
   $$ \min_w \frac{C'}{2} \|w\|^2 + \sum_{i=1}^{N} \epsilon \log\left(1 + \exp\left(\frac{L - y^{(i)} f_w(x^{(i)})}{\epsilon}\right)\right) $$
```

<br>

# Neural Network
- **Definition**
	- 인간의 뇌에서 영감을 받은 기계 학습 모델로, 입력 데이터와 출력 데이터 간의 복잡한 비선형 관계를 학습
	- 여러개의 인공 뉴런([[Perceptron]])으로 구성되며, 각 뉴런은 입력 데이터를 처리한 후 활성화 함수를 통해 출력값을 생성

<br>

- **Components**
	- Input layer
		- 모델에 입력되는 데이터를 받는 층
	- Hidden layers
		- 입력 데이터를 처리하고 변환하는 층
		- 비선형성을 학습하는 역할
		- 여러 개의 은닉층을 쌓아 복잡한 패턴을 학습할 수 있음
	- Output layer
		- 모델의 예측 결과를 출력하는 층
		- 문제의 종류(Classification, Regression)에 따라 다른 형태의 출력을 생성
	- Weights
		- 각 뉴런 간 연결의 강도
		- 학습을 통해 최적화되는 값
	- Activation Function
		- 뉴런이 활성화되는 방식을 결정하는 함수
		- e.g., ReLU, Sigmoid, Tanh