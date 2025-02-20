---
date: 2024-03-08, 10:47
status: Permanent
tags:
  - Study/DL
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
- 대다수의 Object detection algorithm은 object가 존재하는 위치 주변에 여러개의 score가 높은 Bounding box를 만든다는 문제점이 있음
- 이 중 가장 정확한 BBox를 선택하기 위해 Non-Max Suppression (NMS) 기법 사용

![[Pasted image 20240225225108.png]]

---
## NMS의 과정
1. 모든 BBox에 대하여 **threshold 이하의 Confidence score를 가지는 BBox 제거**
2. 남은 BBox들을 Confidence score을 기준으로 모두 **내림차순 정렬**
3. **맨 앞에 있는 BBox**를 기준으로 다른 BBox와 **IoU 값** 계산
4. **IoU가 threshold 이상**인 BBox 제거
   BBox끼리 IoU가 높을수록 같은 물체를 검출하고 있다고 판단하기 때문
5. 해당 과정을 순처적으로 시행하여 모든 BBox를 비교하고 제거
   **Confidence threshold가 높을수록, IoU threshold가 낮을수록 더 많은 BBox가 제거됨**

---
## NMS의 문제점과 Anchor box
- 객체들끼리 겹칠 때 다른 객체에 대한 BBox까지 제거될 수 있음
	- 현실에서는 객체끼리 겹치는 경우가 많기 때문에 자동차에 대해서 detection을 하면 트럭 같은 경우는 detection을 못하고 박스가 제거될 수 있음
	- 이 문제를 해결하기 위해 [[Anchor Box]]가 등장함

![[888ac9c19706d0b542f9a42c93699d62_MD5.png|300]]

- Context information 을 고려하지 않음
- Object occlusion 으로 인해 Confidence score 와 IoU score 가 저하될 수 있는 문제 고려
---
## Modified NMS Methods

![[Pasted image 20240229161300.png]]
<center style="font-size: 14; opacity: 0.7;">Soft NMS (좌), DIoU NMS (우)</center>

- Soft NMS
	- 일반적인 NMS 에서는 Object occlusion 으로 인해 Confidence score 와 IoU score 가 저하될 수 있는 문제 고려
	- Confidence score 가 높은 BBox 의 임계치 이상의 IoU 값을 가지는 BBox 에 대해 Confidence score 를 Decay 시켜 탐지 성능 하락을 방지하는 NMS 방법 
- **DIoU NMS**
	- 기존의 NMS 임계치에 DIoU penalty term 을 추가하여 겹친 객체에 대한 탐지 성능을 향상시킨 NMS 방법
