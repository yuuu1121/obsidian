---
date: 2024-05-06, 17:54
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases:
  - Probability Density Function
  - PDF
  - 확률밀도함수
  - 연속확률변수
keywords:
  - Probability Density Function
  - PDF
  - 확률밀도함수
  - 연속확률변수
related notes: 
reference: 
author: 
url:
---
# 연속 확률 변수 (Continuous Random Variable)

- 연속적인 변수에서 한 점의 확률은 항상 0이기 때문에 범위를 설정하고 확률을 계산해야 함
- **확률변수** ([[Random Variables]]) 의 **누적분포함수** ([[Cumulative Distribution Function, CDF|Cumulative Distribution Function]], CDF) 가 ==실수 공간의 모든 $x$ 에 대해 연속인 경우==

<br><br>


## 확률 밀도 함수 (Probability Density Function, PDF)
- 다음 조건을 만족하는 함수 $f:\mathbb{R}^D\mapsto \mathbb{R}$
>1. $\forall x \in \mathbb{R}^D:f(x)\ge 0$
>2. 적분이 존재하며, $\int_{\mathbb{R}^D}f(x)dx=1$
>$$P(a\le X\le b)=\int_a^b f(x)dx$$
>![[PMF]]
<br>

## PDF의 특징
- $p(x)$ 또는 $f(x)$로 표기
- ==확률 변수 $X$ 의 [[Cumulative Distribution Function, CDF|CDF]] 를 미분한 값==
  >$$f(x)=\frac{d}{dx}F_X(x)$$
  
	>[!tip]
	>- 이를 달리 표현하면 다음과 같음
	>  $$f(x) = \lim_{\Delta x \to 0} \frac{P(x \leq X \leq x + \Delta x)}{\Delta x}$$


- ==$x$ 가 [[Continuous RV|연속확률]]분포를 따를 때, 누적분포함수는 **연속 함수**이며, $P(X=x)=F_X(x)-F_X(x^-)=0$==
	- 즉, ==$P(X=x)$ 는 항상 0 이며, 이를 **질량점이 없다**고 표현==함 ([[Discrete RV]])
	>[!example]
	>0 에서 1 사이 실수중 **정확히** 0.5에 대응하는 값을 뽑을 확률
	>
	>$$P(0.5)=\frac{1}{\infty}\approx0$$
	
- ==확률 밀도 함수 또한 질량점이 없으므로, 확률은 **밀도함수의 적분**을 통해 구할 수 있음==
>$$\begin{align}P(a<X\le b)&=\int^b_a f(x)\cdot dx\\\\&=F_X(b)-F_X(a)\end{align}$$

<br>

## Discrete vs Continuous
![[IMG_C3939B88E421-1.jpeg]]