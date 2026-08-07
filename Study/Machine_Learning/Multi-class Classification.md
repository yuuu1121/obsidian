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
# Multi-class Classification
- **Definition**
	- 주어진 입력 데이터를 세 개 이상의 클래스 중 하나로 분류하는 문제

<br>


- **Challenges**
	- **데이터 불균형 문제**: 
		- 클래스 간 데이터 분포가 불균형할 경우, 특정 클래스에 대해 잘못된 예측이 발생
	- **모델의 복잡도 증가**: 
		- OvO와 같은 방법에서는 클래스가 많아질수록 분류기의 수가 급격히 증가하므로, 계산 비용과 모델 복잡도가 크게 늘어남
	- **클래스 간 관계**: 
		- 클래스 간의 관계나 상관성을 고려하여 모델을 설계

<br>


## Methods
```ad-tip
title: Recap) [[Classification#Discriminant Function Bayes Decision Rule|Discriminant Function]]
collapse: true
- **Definition**
	- 입력 데이터($x$)에 대해 **각 클래스**에 속할 **확률**이나 **점수**를 계산하는 함수.
	- 각 클래스에 대해 계산된 값 중 **가장 높은 값**을 가진 클래스로 **데이터를 분류**함.
		- 분류 기준: $f_k(x) > f_j(x)$, $j \neq k$일 때 $x$를 $C_k$로 할당
- **Key Concepts**
	- **Classifier**
		- 판별 함수를 사용하여 **최고 점수를 가진 클래스**로 $x$를 분류하는 함수.
		  $$h(x) = \text{arg max}_k f_k(x)$$
	- **Bayes Decision Rule**
		- 각 클래스에 대한 **사후 확률**($p(C_k | x)$)을 계산하고, **가장 높은 사후 확률**을 가진 클래스로 데이터를 분류함.<br><br>
			$$\begin{align*}
			f_k(x) &= p(C_k | x) \propto p(x | C_k) p(C_k)\\\\
			\hat{C} &= \arg \max_k p(C_k | x)
			\end{align*}$$
		- Normalization Factor
		  $$p(C_k | x) = \frac{p(x | C_k) p(C_k)}{\sum_{j=1}^{K} p(x | C_j) p(C_j)}$$
- **Implication**
	- **분류** 문제에서 판별 함수는 입력 데이터 $x$가 각 클래스에 속할 **확률**이나 **점수**를 계산하고, **가장 높은 값**을 가진 클래스로 $x$를 분류
	- **베이즈 의사결정 규칙**은 각 클래스의 사후 확률을 기반으로 **최적의 분류**를 제공하며, **사전 확률**과 **클래스 조건부 확률**을 통해 이를 계산
```
<br>

- **[[Multi-class Logistic Regression]]**
	- **Definition**
		- 주어진 데이터 $x$에 대해 각 클래스 $C_k$에 속할 확률 $p(C_k | x)$를 예측하고, 가장 높은 확률을 가진 클래스로 데이터를 분류하는 방법.
		- **[[Logistic Function#Softmax Function|Softmax 함수]]**를 사용하여 입력 데이터를 각 클래스의 확률 분포로 변환하고, 가장 확률이 높은 클래스를 선택함.

<br>


- **[[Multi-class SVM]]**
	- **Definition**
		- 이진 분류기인 **[[Support Vector Machine|SVM]]**을 다중 클래스 분류 작업에 적용하기 위한 방법.
		- 일반적으로 SVM은 두 개의 클래스를 구분하는 [[Maximizing Margin#Hyperplane|Hyperplane]]을 학습하지만, 다중 클래스 분류에서는 여러 클래스를 구분하기 위한 추가적인 방법이 필요함.
	- **Methods**
		- **One-vs-Rest (OvR)**: 
			- 각 클래스를 나머지 모든 클래스와 구분하는 방식.
		- **One-vs-One (OvO)**: 
			- 각 클래스 간 쌍으로 구분하는 방식.
		- **Weston-Watkins SVM (WW-SVM)**: 
			- 여러 클래스를 동시에 구분하는 다중 클래스 SVM의 확장.
	- **Advantage**
		- SVM은 고전적인 기법이지만, 여전히 유용하고 간단하면서도 효과적인 기법
		- 자원 소모가 적고 여러 작업에 쉽게 적용할 수 있음
	- **Disadvantage**
		- SVM은 여전히 선형 Hyperplane으로만 데이터를 구분하기 때문에 비선형적인 데이터에는 한계가 있음.
	- **Approaches**
		- 선형적으로 분리되지 않는 데이터셋에 **슬랙 변수([[Support Vector Machine#Soft Margin SVM|soft-margin SVM]])**를 도입하여 유연한 분류를 허용.
		- **커널 트릭**을 사용하거나 추가적인 특징을 추출하여 비선형 데이터를 처리함.
		  ![[Pasted image 20241021020851.png]]

<br>


- **[[Kernel Trick]]**
	- **Definition**
		- SVM이 고차원 공간에서 비선형적으로 분리되지 않는 데이터를 선형적으로 분리할 수 있도록 돕는 방법.
		- 데이터를 고차원 공간으로 매핑하지 않고도 그 공간에서 **커널 함수**를 통해 효율적으로 계산함.
	- **Advantage**
		- 고차원 공간에서의 계산을 효율적으로 수행하며, 메모리와 계산 자원을 절약
	- **Disadvantage**
		- 문제에 맞는 커널 함수를 선택하지 못할 경우 성능이 저하