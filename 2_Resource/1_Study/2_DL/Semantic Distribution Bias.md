---
date: 2024-03-04, 16:46
status: Paper Review
tags:
  - PaperReview
  - Study/DL
aliases: 
related notes: 
reference: 
author: 
url:
---
# Introduction
- 데이터셋 내의 객체, 장면, 또는 개념들의 분포가 **현실 세계의 분포와 다를 때 발생**하는 편향
---
# Methods
## Class Imbalance
- 주로 **훈련 데이터셋의 구성이 특정 유형의 이미지나 개념에 치우칠 때** 발생
- 객체 탐지 시에 발생하는 Positive / Negative sample 사이에서 Class imbalance 문제 발생
---
**Related Notes**
- [[Class Imbalance]]
---
### 2-Stage Detector
![[Pasted image 20240304103944.png|+grid]]![[Pasted image 20240304103951.png|+grid]]
<center style='font-size:14;opacity:0.7;'>Hard negative example mining (좌), OHEM (우)</center>

- Hard negative example mining: 
	- 모델이 잘못 판단한 false positive sample을 학습 과정에 추가하여 재학습함으로써 모델을 강건하게 만들며, false positive라고 판단하는 오류를 감소시키는 방법 
- OHEM(Online Hard Example Mining): 
	- 모든 RoI를 forward pass한 후 loss를 계산하여 높은 loss를 가지는 RoI에 대해서만 backward pass를 수행하여 모델의 학습 속도 개선과 성능 향상을 이뤄낸 bootstrapping 방법
---
### 1-Stage Detector
- [[YOLO v1 - Loss Function#Class Imbalance|YOLO v1]]
	- Class imbalance 문제를 해결하기 위해 Easy negative 를 Down-weight 하여 Hard negative sample 에 집중하여 학습시키는 Loss function
---
## One-Hot Hard Representation
- One-hot hard representation:
	- Class 집합을 벡터로 표현하는 방법으로, 표현하고 싶은 Class 의 인덱스에 1의 값을 부여하고, 다른 인덱스에는 0을 부여
	- 각 Class 가 서로 배타적이며, 각 데이터 포인트가 오직 하나의 범주에만 속한다고 가정하기 때문에 서로 다른 Class 의 연관성을 표현하기 어려움
---

![[Pasted image 20240304104536.png|+grid]]![[Pasted image 20240304104543.png|+grid]]
<center style='font-size:14;opacity:0.7;'>label smoothing clustering 결과(좌) Label Refinement Network(우)</center>

- **Label smoothing**: 
	- Hard label (정답 인덱스는 1, 나머지는 0) 을 Soft label (라벨이 0과 1 사이 값)로 Smoothing 하여 모델을 더욱 강인하게 만드는 기법 ^ybbjd6
		- 잘못된 라벨링이 존재할 가능성을 고려하는 방법
		- Regularization 효과가 있으며, Overfitting 문제를 방지
- Label refinement network:
	- 서로 다른 해상도에 대하여 coarse한 label을 예측한 후 순차적으로 더 세밀한 label을 예측하도록 구성된 모델