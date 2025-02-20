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
![[Pasted image 20240225163954.png]]

- Localization 과 Classification 과 동시에 이루어지는 1-Stage detector
	- Region proposal 과정을 거치지 않고, CNN 의 결과인 Feature map 에서 Localization 과 Bounding box regression 수행
---
## Advantages of 1-Stage Detector
- Localization 과 Classification 이 Conv layer 에서 동시에 이루어지기 때문에 2-Stage detector 보다 속도가 빠름
- 통합된 Single neural network 이기 때문에 End-to-end 로 학습 가능
- Object detection 을 Regression problem 으로 다루기 때문에 복잡한 Pipeline 이 필요 없음
---
## Limitations of 1-Stage Detector
- 속도는 빠르지만 2-Stage detector 에 비해 정확도가 낮음
- Region proposal 과정 없이 전체 이미지를 빽빽하게 순회하면서 Sampling 을 하는 Dense sampling 방법을 수행하기 때문에 훨씬 더 많은 후보 영역 생성
	- 즉, [[Class Imbalance]] 문제가 2-Stage detector 보다 더 심각함
- [[2-Stage Detector#^s7ox99|Sample heuristic]] 방법을 적용해도 여전히 배경으로 쉽게 분류된 Sample 이 압도적으로 많기 때문에 학습이 비효율적
	- [[Focal Loss]] 를 사용하면 해당 문제를 완화할 수 있음
---
## Representative Model
### Anchor-Based
![[Pasted image 20240304091918.png|+grid]]![[Pasted image 20240304091928.png|+grid]]<center style='font-size: 14; opacity: 0.7;'>YOLO v1 (좌), YOLO v3 (우)</center>

![[Pasted image 20240304092037.png]]
<center style='font-size: 14; opacity: 0.7;'>SSD architecture</center>

![[Pasted image 20240304092106.png]]
<center style='font-size: 14; opacity: 0.7;'>RetinaNet architecture</center>

- **YOLO**: 
	- 하나의 통합된 네트워크를 기반으로 classification과 localization을 동시에 수행하여 빠른 추론 속도를 보인 모델 
- **SSD(Single Shot multibox Detector)**: 
	- multi-scale feature map을 활용하였으며, 다양한 scale과 aspect ratio를 가진 default box를 통해 높은 정확도와 빠른 추론 속도를 보인 모델 
- **RetinaNet**: 
	- Focal Loss를 도입하여 object detection task에서 발생하는 class imbalance 문제를 완화한 모델 
- **YOLO v3**: 
	- Darkent-53을 backbone network로 사용하며 multi-scale feature map을 사용하여 빠른 추론 속도를 보인 모델
---
### Anchor-Free
![[Pasted image 20240304092249.png|+grid]]![[Pasted image 20240304092301.png|+grid]]
<center style='font-size: 14; opacity: 0.7;'>CornerNet (좌), MatrixNet (우)</center>

![[Pasted image 20240304092348.png]]
<center style='font-size: 14; opacity: 0.7;'>CenterNet</center>

![[Pasted image 20240304092410.png]]
<center style='font-size: 14; opacity: 0.7;'>FCOS architecture</center>

- **CornerNet**: 
	- hourglass의 출력 결과를 두 개의 모듈을 입력하여 얻은 두 쌍의 keypoint를 사용하여 bbox를 예측하는 모델 
- **CenterNet**: 
	- Center pooling과 Cascade corner pooling을 통해 세 쌍의 keypoint를 사용하여 CornerNet의 단점을 개선한 모델 
- **MatrixNet**: 
	- 객체와 더불어 객체의 size와 aspect ratio에 대한 정보를 네트워크에 포함하여 keypoint를 예측하는 모델 
- **FCOS**: 
	- anchor를 사용하지 않고 중심점으로부터 bbox 경계까지의 거리를 예측하며, center-ness를 통해 중심점 거리를 normalize하여 low quality box를 제거하는 모델