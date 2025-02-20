---
date: 2024-03-13, 14:38
status: Paper Review
tags:
  - PaperReview
  - PaperReview/Backbone
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
![[Pasted image 20240313144205.png]]

<center style='font-size:14;opacity:0.7;'>VGG-16(좌) ResNet-34(중간), SpineNet-49 architecture(우)</center>

![[Pasted image 20240313144245.png]]

<center style='font-size:14;opacity:0.7;'>EfficientNet의 Compound scaling(좌) CSPDarknet53의 Cross Stage Hierarchy 방법(우)</center>

- VGG16: 
	- 3x3 conv filter만을 사용하여 네트워크의 깊이를 크게 늘린 모델 
- ResNet-50: 
	- Residual Block을 통해 네트워크의 층 수를 획기적으로 늘린 모델 
	- Related Notes: [[ResNet - Main Ideas]]
- SpineNet: 
	- object detection에 보다 적합한 backbone network를 설계하기 위해 NAS를 활용하여 localization 및 multi-scale feature에 유리하도록 설계된 scale-permuted 모델 
- EfficientNet-B0/B7: 
	- width, depth, resolution라는 3가지 scaling factor를 모두 고려하는 compound scaling을 AutoML을 통해 적은 연산량과 높은 정확도를 가지도록 설계된 모델 
- CSPResNeXt50: 
	- ResNext-50 기반의 layer의 feature map을 분할 후 Cross-Stage Hierarchy 방법을 통해 결합하여 연산량을 획기적으로 낮춘 모델 
- CSPDarknet53: 
	- DenseNet 기반의 layer의 feature map을 분할 후 Cross-Stage Hierarchy 방법을 통해 결합하여 연산량을 획기적으로 낮춘 모델
	- Related Notes:
		- [[CSPNet - Main Ideas]]
		- [[YOLO v3 - DarkNet-53]]
---
