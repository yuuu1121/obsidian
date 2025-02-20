---
date: 2024-03-04, 16:37
status: Paper Review
tags:
  - PaperReview
  - Study/DL/DataAugmentation
aliases: 
related notes: 
reference: 
author: 
url:
---
# Introduction

![[image-8-x50-y438.png|350]]

- **입력 이미지의 다양성**을 늘려 Object detection model 의 Generalization 성능을 향상시키기 위해 사용
  (참고: [[Generalizability of YOLO v1|YOLO v1 의 Generalization 성능 실험]])
---
# Methods
## Simulating Object Occlusion
![[Pasted image 20240304102458.png|+grid]]![[Pasted image 20240304102535.png|+grid]]
<center style='font-size:14;opacity:0.7;'>Random Erase (좌), CutOut (우)</center>

- Random erase:
	- 하나의 물체가 다른 물체에 의해 부분적으로 가려져 보이지 않는 occlusion 문제를 해결하기 위해 이미지의 일부분을 랜덤한 값으로 채워 regularization 효과와 모델의 강건함을 향상시킨 data augmentation 기법 
- CutOut: 
	- Occlusion 문제를 해결하기 위해 이미지의 일부분을 0으로 채우는 data augmentation 기법 
---

![[Pasted image 20240304102711.png|+grid]]![[Pasted image 20240304102717.png|+grid]]
<center style='font-size:14;opacity:0.7;'>Hide-and-Seek(좌), Grid Mask(우)</center>

- Hide-and-seek:  
	- 이미지 패치를 랜덤하게 숨김으로써 네트워크가 가려지지 않은 객체의 일부분에 대해 학습하여 모델의 분류 성능을 향상시키는 방법 
- Grid mask: 
	- 고정된 크기의 grid로 이미지를 가려 이미지의 일부분을 제거하는 방법으로 인해 객체의 특징이 제대로 학습되지 못하는 단점을 보완한 data augmentation 기법
---

![[Pasted image 20240229110748.png]]

- MixUp: 
	- 두 데이터의 이미지와 label을 weighted linear interpolation하여 네트워크의 일반화 능력을 향상시키는 data augmentation 기법 
- **CutMix**: 
	- 이미지 내 특정 패치 영역에 label이 다른 학습 이미지를 잘라 붙여넣어 학습 픽셀을 효율적으로 사용하며 regularization 효과를 유지하는 data augmentation 기법
---

![[Pasted image 20240304134539.png|500]]

- **Mosaic**:
	- YOLO v4 에서 제안된 방법으로 한 이미지에 4개의 Class를 넣어 일반적인 맥락에서 벗어난 관점을 네트워크에 제공
	- Mini-batch size 를 효과적으로 줄일 수 있음
	- Related Notes: [[YOLO v4 - New Ideas and Modifications]]
---
## Self-Adversarial Training (SAT)
- YOLO v4 에서 제안된 방법으로 Forward, backward 두 번의 Stage 를 걸쳐 수행되는 Data augmentation 방법
- 첫 번째 Stage 에서 Network weight 대신 이미지를 변형시켜 이미지 내에 객체가 없는 것 처럼 보이게 Adversarial attack 을 가하고, 두 번째 Stage 에서 변형된 이미지로 학습
---
**Related Notes**
- [[YOLO v4 - New Ideas and Modifications]]
---
