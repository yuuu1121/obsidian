---
date: 2024-09-11
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases:
  - Prior
  - Likelihood
  - Posterior
keywords:
  - 베이즈 정리
related notes:
  - "[[Conditional Probability]]"
reference: 
author: 
url: 
dg-publish: false
---
# 베이즈 정리 (Baye's Theorem)

- ==경험을 통해 알고 있는 확률 $P(A)$== (사전 확률, **Prior probability**)와 ==조건부 확률 $P(B|A)$== (우도, **Likelihood**)를 알고 있을 때, ==반대 조건의 확률== (사후 확률, **Posterior probability**)을 추론하는 과정

$$P(A|B)=\frac{{P(B|A)P(A)}}{{P(B)}}\propto P(B|A)P(A) \quad \text{if }P(B)\ne 0$$
$$P(\text{unknown original}|\text{observation data})={{\text{Likelihood}\times \text{Prior}}\over {\text{Evidence}}}$$

<br>

![[drawing240503_0.excalidraw]]

<br>


## 구성 요소
- **Prior probability $P(A)$**
	- 새로운 데이터($B$)를 관측하기 전에 사건 $A$에 대한 사전 예측 값
		- 최종적으로 사건 $A$에 대한 확률을 구하고자 함
		- $A$는 관측으로 알 수 없는 값이며, $B$는 관측으로 알 수 있음
	- e.g., 암 진단에서 전체 인구의 암에 걸릴 확률 1%
		- $P(A)=0.01$
- **Likelihood $P(B|A)$**
	- 사건 $A$가 발생했을 때 사건 $B$가 발생할 [[Conditional Probability|조건부 확률]]
		- $A$가 발생했을 때 $B$가 발생한 사건들을 관측하여 얻을 수 있음
	- e.g., 암에 걸린 사람이 양성 판정을 받을 확률 95%
		- $P(B|A)=0.95$
- **Evidence $P(B)$**
	- 사건 $B$가 일어날 **전체적인 확률**
	- ==사건 $A$와 관련이 없는 다른 사건들도 모두 고려하여 계산==
	- $P(B)=P(B|A)P(A)+P(B|A^c)P(A^c)$
	- e.g., 검사 결과가 양성일 확률
		- $P(B)=0.95\times 0.01+0.05\times0.99=0.059$
- **Posterior probability $P(A|B)$**
	- 관측 데이터 $B$를 바탕으로 사건 $A$가 발생할 확률을 업데이트
	- ==최종적으로 계산하고자 하는 값==
	- e.g., 양성 판정을 받은 사람이 실제로 암에 걸렸을 확률
		- $P(A|B)=\frac{{0.95\times0.01}}{0.059}\approx0.16$
		- *이 결과는 암 발병률이 낮기 때문에, 양성 판정이 나왔더라도 실제로 암에 걸렸을 확률이 그렇게 높지 않다는 것을 보여줌*

<br>

## Baye's Theorem for Machine Learning
- 우리가 인과관계를 추론할 때 결과(latent $y$)를 바탕으로 원인(observation $x$)을 분석하는 것 $P(\text{observation }x \text{ }|\text{ latent }y)$ 이 자연스러우나 Machine learning에서는 원인을 보고 결과를 추론하는 과정 $P(\text{ latent } y \text{ }| \text{ obsdervation } x$)