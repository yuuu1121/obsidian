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
# Logistic Function
- 입력된 실수 값을 0과 1 사이의 값으로 변환하는 함수
- 주로 확률을 표현하기 위해 사용되며, 입력 값이 매우 큰 경우 1에 가까운 값, 매우 작은 경우 0에 가까운 값을 반환

<br>

## Sigmoid Function

- **수식**:  
  $$ \sigma(x) = \frac{1}{1 + e^{-x}} $$
- **설명**:  
  - 입력 값을 0과 1 사이의 값으로 변환.
  - $x \to \infty$ 일 때 출력은 1, $x \to -\infty$ 일 때 출력은 0.
  - **사용처**: Logistic regression, 인공신경망에서 활성화 함수로 자주 사용.

<br>


## Softmax Function

- **수식**:  
  $$ \text{Softmax}(z_k) = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}} $$

- **설명**:  
  - **입력 벡터** $z = [z_1, z_2, ..., z_K]$의 각 원소를 **확률 값**으로 변환하여 **확률 분포**를 만듦.
  - 각 $z_k$는 **클래스 $k$에 속할 가능성**을 나타내는 **점수** 또는 **로짓(logit)** 값. 이 점수는 클래스 $k$에 속하는지 아닌지를 나타내는 **binary classification**의 결과로 이해할 수 있음.
  - **Softmax 함수**는 이 점수들을 0과 1 사이의 **확률 값**으로 변환하며, 변환된 값들의 **합은 1**이 됨.
  - **큰 값일수록** 해당 클래스에 속할 확률이 높아짐.

- **사용처**:  
  - **[[Multi-class Classification]]**에서 각 클래스에 속할 확률을 계산.
  - **신경망**의 출력층에서 사용되며, **다중 클래스 분류** 문제에서 각 클래스에 속할 확률을 반환.


<br>


## Properties of the Logistic Function
$$f(x)=\sigma(wx+b)={1\over 1+e^{1(wx+b)}}$$

- Parameter $w$
  ![[Pasted image 20241013201142.png]]
	- 큰 $w$값은 가파른 곡선을, 작은 $w$값은 완만한 곡선을 만듦

<br>


- Bias $b$
  ![[Pasted image 20241013201217.png]]
	- $b=0$일 때 곡선은 $x=0$에서 0.5를 통과하며, $b$값을 통해 Decision boundary를 쉽게 조절할 수 있음

$$\sigma(t)={1\over 1+e^{-t}}$$

- $\sigma(t) \to 0 \text{ as } t \to -\infty$
- $\sigma(t) \to 1 \text{ as } t \to \infty$
- $\sigma(-t) = 1 - \sigma(t)$
- $\frac{d}{dt} \sigma(t) = \sigma(t) \sigma(-t) = \sigma(t)(1 - \sigma(t))$

