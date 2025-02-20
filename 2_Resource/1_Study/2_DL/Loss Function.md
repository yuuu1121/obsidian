---
date: 2024-03-13, 13:47
status: Permanent
tags:
  - Study/DL/LossFunction
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
# Introduction
- 지도 학습 (Supervised learning) 시 알고리즘이 예측한 값과 실제 정답의 차이를 비교하기 위한 함수
- 최적화 (Optimization) 를 위해 최소화하는 것이 목적인 함수

---
# Methods
## Sum of Squared Error (SSE)
- 잔차의 제곱합

$$SSE=\sum^n_{i=1}{(y_i-\hat{y}_i)^2}$$
- 선형 회귀는 **SSE**를 **최소화**하는 방법으로 회귀 계수를 추정
  즉, SSE가 작으면 작을수록 좋은 모델
---
### Mean Squared Error (MSE)
- SSE를 표준화한 개념

$$RSE=MSE=\sqrt{{SSE\over {n-2}}}$$

---
## KL-Divergence
- 두 분포 $p$(데이터의 실제 분포)와 $q$(모델이 예측한 분포)를 비교하는 지표
- 두 분포가 같은 경우 0이되며, 분포가 다를수록 값이 커짐

$$KL(p, q) = \sum_x p(x) \log \frac{p(x)}{q(x)}$$

## Cross-Entropy Loss
- Classification 에 사용되는 Loss function
- KL divergence에서 $p$를 상수로 간주

$$\begin{align}
CE(p, y)=\begin{cases}
-\log(p)&\text{if }y=1\\\\
-\log(1-p)&\text{otherwise}
\end{cases}&\quad&
p_t=\begin{cases}
p&\text{if }y=1\\\\
1-p&\text{otherwise}
\end{cases}
\end{align}$$
<br/>

$$CE(p, y)=CE(p_t)=-\log(p_t)\qquad \mathcal{E}=-\sum\limits_xy_n\log{p}$$<br/>

- $p_t$: 해당 Class 가 존재할 확률
- $y$: ground truth class
- $p$: 모델이 $y=1$ 이라고 예측한 확률
---
**Related Notes**
- [[Focal Loss - Method of Focal Loss#Cross Entropy|Cross-Entropy Loss]]
---
```ad-note
title: Corss Entropy Loss for Multi-class Classification

- For binary class
  $$\mathcal{E} = \sum_{n=1}^{N} \left[ - y_n \log \hat{y}_n - (1 - y_n) \log (1 - \hat{y}_n) \right]$$
- For $K$ classes
  $$\mathcal{E} = \sum_{n=1}^{N} \sum_{k=1}^{K} \left[ - y_{k,n} \log \hat{y}_{k,n} \right]$$
```

### Balanced Cross-Entropy Loss
- Class Imbalance 문제를 해결하기 위해 일반적으로 CE 에 Weighting factor alpha 를 적용한 것
	- $y=1$ 일 때 $\alpha$ 를 곱해주고, $y=-1$ 일 때 $1-\alpha$ 곱해줌
	- Object 에 대한 Loss 는 작게 하고, Background 에 대한 Loss 는 크게 설정

$$CE(p_t)=-\alpha_t\log(p_t)$$

> - 장점: Positive / Negative example 의 차별성 표현 가능
> - 단점: Easy ($p_t > 0.5$) / Hard ($p_t < 0.5$) 의 차별성 표현 불가능

---
**Related Notes**
- [[Focal Loss - Method of Focal Loss#Balanced Cross Entropy Loss|Balanced Cross-Entropy Loss]]
---
## Focal Loss
![[image-1-x47-y380.png|+grid]]![[Pasted image 20240307200310.png|+grid]]
$$FL(p_t)=-(1-p_t)^{\gamma}\log(p_t)$$

- Focal loss 는 Easy sample 에 대한 가중치를 줄이고 Hard negative sample 의 학습에 초점을 맞추도록 CE loss 수정
	- CE loss 에 Modulating factor $(1-p_t)^{\gamma}$ 를 추가 ($\gamma\in [0, 5]$, Focusing parameter)
- Focal Loss 의 두 가지 특징
	1. $p_t$ 값이 작을 때, Modulating factor 는 거의 1에 근접하여 Loss 값이 커짐
	   $p_t$ 값이 클 때, Modulating factor 는 거의 0에 근접하여 Well-classified example ($p_t>0.6$) 의 Loss 값이 작아짐
	2. Focusing parameter 감마 값이 커질 수록 Modulating factor 의 영향이 커짐
	   ($\gamma=2$ 가 가장 좋은 성능)
---
**Related Notes**
- [[Focal Loss - Method of Focal Loss#Focal Loss|Focal Loss]]
---
#### Backpropagation
$$\begin{align}
{d\text{CE}\over dx}&=y(p_t-1)\\\\
{d\text{FL}\over dx}&=y(1-p_t)^{\gamma}(\gamma p_t\log(p_t)+p_t-1)
\end{align}$$
---
### Balanced Focal Loss
- alpha-balanced 를 적용한 Focal loss 형태
	- alpha-balanced Focal loss 가 일반 Focal loss 보다 성능 좋음

$$FL(p_t)=-\alpha_t(1-p_t)^{\gamma}\log(p_t)$$

---
**Related Notes**
- [[Focal Loss - Method of Focal Loss#Alpha-balanced Variant of the Focal Loss|Balanced Focal Loss]]
---
