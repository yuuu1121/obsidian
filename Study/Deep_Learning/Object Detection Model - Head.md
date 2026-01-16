---
date: 2024-03-13, 14:51
status: Paper Review
tags:
  - PaperReview
  - PaperReview/Head
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
# Introduction

![[3_Archive/4_Zotero/Literature Notes/@BochkovskiyEtAl2020/image-2-x49-y461.png]]

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
- [[Study/Deep_Learning/1-Stage Detector|Dense Prediction (one-stage)]]: 일반적으로 인코더와 디코더로 분리된 네트워크
	- **Anchor based**: Region Proposal Network (RPN), SSD, [[2_Resource/0_Paper Review/YOLO/2_YOLO 9000/Methodology/YOLO v2 - DarkNet-19#DarkNet-19 for Detection Task|YOLO v2]], RetinaNet
	- **Anchor free**: CornerNet, CenterNet, MatrixNet, FCOS, YOLO v1
- [[Study/Deep_Learning/2-Stage Detector|Sparse Prediction (two-stage)]]: 
	- **Anchor based**: Faster R-CNN, R-FCN, Mask RCNN
	- **Anchor free**: RepPoints
---
