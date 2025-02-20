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
# Multi-class Support Vector Machine
- **Definition**
	- Binary SVM은 하나의 Hyperplane을 사용하여 두 클래스를 구분
	- $K>3$ 인 경우에는 여러 개의 클래스를 구분하기 위해 여러 개의 Hyperplane이 필요
	- 이를 해결하기 위해 여러가지 방법을 사용할 수 있음

<br>


- **Method**
	- **One-vs-Rest (OvR)**
		- **각 클래스**와 **나머지 모든 클래스**를 구분하는 $K$개의 Binary Classifier를 학습.
			- 각 SVM은 **하나의 클래스**를 "1"로, 나머지 모든 클래스를 "0"으로 구분.
			- 각 분류기는 **가중치** $w_k$와 **바이어스** $b_k$로 표현됨.
		![[Pasted image 20241021020644.png|300]]<br><br>
		- **Prediction**
		  $$\arg\max_{k\in[K]}\text{ }\left(w^\top_k\phi(x)+b_k\right)$$
		- **Advantage**
			- 간단하고 구현이 쉬움.
		- **Disadvantage**
			- 데이터 불균형 문제가 발생할 수 있으며, 과적합을 유발할 수 있음
				- e.g., 1,000개의 클래스가 있을 경우, 하나의 클래스를 나머지 999개와 구분하는 것은 어려울 수 있음<br><br>
	- **One-vs-One (OvO)**
		- 각 클래스 $j$와 $k$를 구분하는 $K(K-1)/2$개의 Binary SVM을 학습
			- 각 SVM은 두 클래스를 비교하여 구분.
			- 각 분류기는 **가중치** $w_{jk}$와 **바이어스** $b_{jk}$로 표현됨.
			![[Pasted image 20241021020738.png|300]]<br><br>
		- **Prediction**
			- SVM 결과 중 다수결을 통해 분류
			- 동률일 경우 규칙에 따라 분류
		- **Advantage**
			- 클래스 간 불균형 문제를 해결
			- 각 분류기가 비교적 작은 데이터셋에서 학습할 수 있어 학습 속도가 빠름
		- **Disadvantage**
			- 분류기 개수가 많아지기 때문에 계산 비용이 높음<br><br>
	- **Directed Acyclic Graph SVM (DAG SVM)**
		- $K(K-1)/2$개의 Binary SVM을 계층적 트리 구조로 구성
			- 각 SVM은 두 클래스를 비교하여 구분
			![[Pasted image 20241021020812.png]]<br><br>
		- **Prediction**
			- SVM을 순차적으로 통과하며, 각 SVM에서 두 클래스 중 하나를 제외
		- **Advantage**
			- 여러 클래스를 순차적으로 제거하기 때문에 효율적
		- **Disadvantage**
			- 그래프 구조를 구성하고 관리하는데 추가적인 복잡성<br><br>
	- **Weston & Watkins (WW-SVM)**
		- 다중 클래스 분류 문제를 하나의 최적화 문제로 해결하는 방식
			- Objective Function:
			  $$\min_{w,b,\zeta \geq 0} \frac{1}{2} \sum_k \|w_k\|^2 + C \sum_i \sum_{k \neq y_i} \zeta_k^{(i)}$$
			- Constrain:
			  $$w_{y_i}^\top \phi(x^{(i)}) + b_{y_i} - (w_k^\top \phi(x^{(i)}) + b_k) \geq 2 - \zeta_k^{(i)}$$
		- **Prediction**
		  $$\arg\max_k (w_k^\top \phi(x) + b_k)$$
		- **Advantage**
			- 여러 SVM을 동시에 최적화하여, OvR의 데이터 불균형 문제와 OvO의 지역적 문제를 해결
			- 모든 데이터 포인트를 한 번에 학습하여 더 나은 성능
		- **Disadvantage**
			- 최적화가 복잡하며, 문제의 크기가 커질 수 있음

