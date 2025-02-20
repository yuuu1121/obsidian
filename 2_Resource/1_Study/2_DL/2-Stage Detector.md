---
date: 2024-03-08
status: Permanent
tags:
  - Study/DL
aliases: 
keywords: 
related notes: 
reference: 
author:
  - 정이는 성장중
url:
  - https://velog.io/@qtly_u/Object-Detection-Architecture-1-or-2-stage-detector-%EC%B0%A8%EC%9D%B4
---
![[Pasted image 20240225162412.png]]

- Localization 과 Classification 이 2-Stage 로 분리되어 있는 Object detector
	- First stage: 
		- Region proposal 을 사용하여 이미지 안에 객체가 있을 법한 영역 (Region of Interest, ROI) 를 대략적으로 생성
		- 대표적인 Region proposal 기법: [[Selective Search]], [[Sliding Window]]
	- Second stage:
		- 해당 Proposal 에 대해 CNN 을 이용하여 Classification 수행
---
## Advantages of 2-Stage Detector
- 객체가 존재할 확률이 높은 Proposal 을 생성하기 때문에 [[Clas Imbalance]] 문제에 덜 민감
	- Two-stage cascade, 즉 Region proposal 를 추려내는 방법을 적용하기 때문에 대부분의 Background sample 을 거를 수 있음
	- Positive / Negative sample 의 수를 적절하게 유지하는 Sampling heuristic 방법 적용
		- eg., Hard negative mining, OHEM ^s7ox99
---
## Limitations of 2-Stage Detector
- 1-stage detector 방식에 비해 **시간이 많이 소요**되고, 각각의 모듈들이 개별적으로 학습되어야하기 때문에 **최적화가 어려움**
---
## Representative Models
### Anchor-Based
![[Pasted image 20240304092603.png|+grid]]![[Pasted image 20240304092610.png|+grid]]
<center style='font-size: 14; opacity: 0.7;'>Fast R-CNN (좌), Faster R-CNN (우)</center>

![[Pasted image 20240304092659.png|+grid]]![[Pasted image 20240304092710.png|+grid]]

<center style='font-size: 14; opacity: 0.7;'>R-FCN (좌), Libra R-CNN (우)</center>

![[Pasted image 20240304092741.png]]

<center style='font-size: 14; opacity: 0.7;'>Mask R-CNN</center>

- **Fast R-CNN**: 
	- 단일 이미지를 CNN에 입력하여 RoI(Region of Interest)를 얻은 후 RoI pooling을 통해 고정된 크기의 feature vector를 fc layer에 전달하여 R-CNN에 비해 학습 및 추론 속도이 향상된 모델 
- **Faster R-CNN**: 
	- RPN(Region Proposal Network)을 추가하여 모델의 동작 과정에서 발생하는 병목 현상을 최소화하여 Fast R-CNN에 비해 학습 및 추론 속도, 정확도가 향상된 모델  
- **R-FCN**: 
	- RoI끼리 연산을 공유하며 객체의 위치 정보를 포함하는 Position sensitive score map & RoI pooling을 도입하여 Translation invariance dilemma 문제를 해결한 모델 
- **Mask R-CNN**: 
	- RoI pooling을 통해 얻은 feature와 RoI가 어긋나는 misalignment를 해결하기 위해 RoI Align 방법을 도입한 Instance Segmentation 모델  
- **Libra R-CNN**: 
	- IoU-based sampling, Balanced Feature Pyramid, Balanced L1 loss를 도입하여 객체 탐지 모델 학습 시 발생하는 imbalance 문제를 완화한 모델
---
### Anchor-Free

![[Pasted image 20240304092925.png|500]]

<center style='font-size: 14; opacity: 0.7;'>RePoints</center>

- **RePoints**: deformable convolution을 활용하여 객체의 둘레에 점을 찍어 얻은 reppoints를 기반으로 anchor 없이 객체 탐지를 수행하는 모델