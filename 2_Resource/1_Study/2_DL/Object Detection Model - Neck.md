---
date: 2024-03-13, 14:44
status: Paper Review
tags:
  - PaperReview
  - PaperReview/Neck
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
# Introduction

![[image-2-x49-y461.png]]

- 일반적인 Detector 는 Backbone 과 Neck 그리고 Head 로 구성
	- **Backbone**:
		- 입력 이미지에서 Feature 를 추출
		- ImageNet 으로 Pre-trained 시킨 VGG-16, ResNet-50 등이 대표적인 Backbone
	- **Neck**:
		- Backbone 과 Head 를 연결하는 부분으로 Feature map 을 정제 (refinement), 재구성 (reconfiguration) 함
	- **Head**:
		- Backbone 에서 추출한 Feature map 에서 Classification 과 Localization 작업 (Bounding box 예측) 을 수행하는 부분
		- 크게 Dense prediction (1-stage) 과 Sparse prediction (2-stage) 으로 나뉨
---
# Methods
## Additional Blocks
### Enhancement of Receptive Field
![[Pasted image 20240304095110.png|+grid]]![[Pasted image 20240304095120.png|+grid]]
<center style='font-size:14;opacity:0.7;'>SPP layer (좌), ASPP layer (우)</center>

![[Pasted image 20240304095157.png|+grid]]![[Pasted image 20240304191334.png|+grid]]
<center style='font-size:14;opacity:0.7;'>RFB module (좌), Dilated convolution (우)</center>

- Spatial Pyramid Pooling (SPP):
	- Spatial Pyramid Matching (SPM):
		- Conv layer 의 마지막 Feature map 을 여러 개의 고정된 크기의 Grid 로 분할한 후 Spatial pyramid 를 형성하여 Bag-of-Word (BoW) 연산으로 Feature 추출
	- SPP 는 SPM 을 CNN 에 통합하고, BoW 연산 대신 Max-pooling 연산을 이용
	- 다양한 크기의 입력을 처리할 수 있는 장점이 있지만, 1-dim vector 를 출력으로 얻기 때문에 Fully Convolutional Network (FCN) 에 사용될 수 없음
	- Related Notes: [[SPP - Main Ideas]]
- Improved SPP:
	- YOLO v3 에서 설계 된 k x k Kernel size 와 Stride 가 1인 Max-pooling 출력들을 Concatenation 하는 방식으로 SPP module 을 수정하여 사용
	- 큰 Kernel size 의 Max-pooling 은 Backbone feature 의 Receptive field 를 증가시킬 수 있음
	- Related Notes: [[YOLO v3 - Prediction across Scales]]
- Astrous Spatial Pyramid Pooling (ASPP):
	- Filter 의 각 픽셀 사이에 간격을 두어서 넓은 영역의 특징을 추출 (Dilated convolution)
- Receptive Field Block (RFB):
	- ASPP 보다 더 포괄적인 공간 정보를 얻기 위해 여러 개의 k x k Kernel 의 Dilated convolution 사용
	- 경량화된 CNN 모델에서 학습된 Feature 를 강조하여, 빠른 추론 속도와 더불어 향상된 정확도에 기여한 구조
---
### Attention Module
![[Pasted image 20240304110433.png]]
<center style='font-size:14;opacity:0.7'>Squeeze-and-Excitation module</center>

![[Pasted image 20240304095203.png]]
<center style='font-size:14;opacity:0.7'>CBAM module</center>

- Squeeze-and Excitation (SE):
	- Feature map 을 그대로 이용하는 것이 아니라 Channel 별로 Global Average Pooling 을 수행 하여 1 x 1 x C Feature vector 로 만든 후, 이에 Activation function 을 적용하여 Channel 별 가중치를 계산
	- 이 후, 이 가중치들을 원래의 Feature map 과 Channel-wise 로 곱하여 각 채널의 중요도가 반영된 Feature map 생성
	- 모델이 중요한 정보를 담고 있는 Feature map 에 집중할 수 있게 함
	- CPU 를 사용할 땐 Inference time 이 2% 가량 증가하지만, GPU 를 사용할 땐 10% 가량 증가하기 때문에 Mobile device 에 적합
- Self-Attention Module (SAM):
	- 대표적인 Point-wise attention module
	- Conv feature 를 Refine 시켜 상대적으로 중요한 값을 강조하여 매우 적은 연산량의 증가로 유의미한 정확도 성능 향상 
	- Related Notes:
		- [[CBAM - Main Ideas]]
		- [[YOLO v4 - New Ideas and Modifications#PAN & SAM|YOLO v4 - Modified SAM]]
---
## Feature Integration Modules
![[Pasted image 20240304095340.png|+grid]]![[Pasted image 20240304095348.png|+grid]]
<center style='font-size:14;opacity:0.7;'>FPN(좌), PAN 프레임워크(우)</center>

- Feature Pyramid Network (FPN)
	- Low-level feature map 과 High-level feature map 의 특징을 Top-down, Bottom-up, Lateral connection 을 통해 유의미하게 활용하여 객체 탐지 성능 향상에 기여한 네트워크
	- Related Notes: [[FPN - Main Ideas]]

- Path Augmented Network (PAN)
	- Bottom-up path augmentation 을 통해 Low-level feature 의 정보를 High-level feature 에 효과적으로 전달함으로써 객체 탐지 시 Localization 성능을 향상시킨 네트워크 
	- Related Notes: 
		- [[PAN - Main Ideas]]
		- [[YOLO v4 - New Ideas and Modifications#PAN & SAM|YOLO v4 - Modified PAN]]
---

![[Pasted image 20240304095422.png|+grid]]![[Pasted image 20240304095431.png|+grid]]![[Pasted image 20240304095453.png|+grid]]
<center style='font-size:14;opacity:0.7;'>NAS-FPN with RetinaNet(좌), Fully-connected FPN(중간), BiFPN(우)</center>

- Neural Architecture Search-FPN (NAS-FPN)
	- NAS를 통해 효율적인 Feature Pyramid Network 탐색하여 얻은 최적의 FPN 구조 

- Fully-connected FPN
	- 서로 다른 Level 의 Feature map 간의 정보를 Fully connect 하여 통합하는 방식의 Feature pyramid

- BiFPN
	- Scale-wise level 의 re-weighting 을 수행한 후 서로 다른 Scale 의 Feature map 들을 추가하기 위해 Multi-input 의 Weighted residual connection 가 제안됨
---

![[Pasted image 20240304095507.png|+grid]]![[Pasted image 20240304095513.png|+grid]]
<center style='font-size:14;opacity:0.7;'>ASFF(좌), SFAM(우)</center>

- Adaptively Spatial Feature Fusion (ASFF)
	- Feature pyramid 에서 다른 Level 의 Feature 과 정보 통합 시 Softmax 를 사용하여 Point-wise level 의 re-weighting 을 수행하고, 서로 다른 Feature map 들과 통합

- Scale-wise Feature Aggregation Module (SFAM)
	- SE 모듈을 사용하여 Multi-scale 의 Concatenated feature map 상에서 Channel-wise level 의 re-weighting 수행