---
date: 2024-03-12, 11:35
status: Permanent
tags:
  - Study/DL
aliases: 
keywords:
  - Network Depth
related notes: 
reference: 
author: 
url:
---
# Introduction

![[Pasted image 20240305124828.png]]
<center style='font-size:14;opacity:0.7;'>Layer 에 따른 Feature map 의 변화 도식도</center>

- Deep neural network 는 Low / mid / high level features 를 통합하고, 여러 개의 Layer 에서 end-to-end 방식으로 Class 를 분류함
- Neural network 의 Layer 수가 많아질수록 근사화 (Approximation) 가 강력해지며, High-level layer 에서 높은 추상화 특징을 얻을 수 있음
---
## Feature map 의 해상도와 각각 보유하고 있는 Representation 의 관계

![[Pasted image 20240311053601.png]]

- Convolutional network 에서 더 얕은, 즉 입력층에 보다 가까울수록 Feature map 은 높은 해상도 (High resolution) 을 가지며, 가장자리, 곡선 등과 같은 저수준 특징 (Low-level feature) 을 보유
- 반대로 더 깊은 Layer 에서 얻을 수 있는 Feature map 은 낮은 해상도 (Low resolution) 을 가지며, 질감과 물체의 일부분 등 Class 를 추론할 수 있는 고수준 특징 (High-level feature) 를 가짐

>Object detection 모델은 피라미드의 각 Level 의 Feature map 을 일부 혹은 전부 사용하여 예측을 수행

---
# Problem
## Information Loss
- Input 이 수 많은 Layer 를 거치면서, 정보가 손실됨
---
## Convergence Problem
- **Vanishing / exploding gradients** 로 발생
- 이는 학습 초기부터 Convergence 를 방해
- 이 문제는 *Normalized initialization 과 Intermediate normalization layer, SGD 등을 통해 대부분 해결됨*
---
## Degradation Problem

![[Pasted image 20240305142202.png]]
<center style='font-size:14;opacity:0.7;'>Layer 깊이에 따른 train (좌) / test (우) error 비교</center>

- Neural network 의 *깊이가 증가할수록, 정확도는 포화되다가 급격하게 정확도 감소*
- 이러한 저하 문제는 Overfitting 에 의해 발생되는 것이 아니며, *Layer 가 증가할 수록 최적화가 쉽지 않다는 것*을 보여줌
	- Overfitting 이면 깊은 Layer 의 Train error 는 낮고, Test error 는 높아야하는데 이건 위 그림에선 둘 다 깊은 모델의 error 가 높게 나옴

> *단순하게 Layer 수를 증가하는 것은 성능 향상을 위한 해결책이 아님*

---
## Computational Burden
- Neural network 는 깊고 넓어질 수록 강력한 성능을 내지만, 많은 Computation 이 필요