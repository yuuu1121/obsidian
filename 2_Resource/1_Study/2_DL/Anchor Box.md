---
date: 2024-02-25
status: Permanent
tags:
  - Study/DL/AnchorBox
aliases: 
reference: 
author:
  - 정이는 성장중
url:
  - https://velog.io/@qtly_u/Object-Detection-Architecture-1-or-2-stage-detector-%EC%B0%A8%EC%9D%B4#1-stage-detector
header-includes:
  - \usepackage{kotex}
---
![[Pasted image 20240225165029.png]]

# Anchor Box
- 미리 정의된 형태를 가진 여러 개의 Bounding Box
- **k-means clustering** 알고리즘에 의한 데이터로부터 생성됨
- 사전에 크기와 비율이 모두 결정되어 있는 박스를 기준으로, 학습을 통해서 이 박스의 위치나 크기를 세부 조정하여 객체를 탐지
- 객체가 탐지되었을 때 **어떤 Anchor box와 유사한지 판단**해서 벡터값을 할당하는 방법
	- 아래와 같이 Anchor box가 2개라면 벡터는 다음과 같이 생성됨
	  $[p_x, b_x, b_y, b_w, b_h, c_1, c_2, c_3, p_x, b_x, b_y, b_w, b_h, c_1, c_2, c_3]$
	- Detection을 할 때는 예측한 객체의 BBox가 Anchor box 1에 유사한지 2에 유사한지 **IoU를 비교**하여 높은 IoU를 갖는 Anchor box 자리에 할당
	  ![[409b0563b1083ce91ed856c97beeba62_MD5.png|500]]
- 이후, 이미지의 Feature map에서 **Anchor box의 offset**을 최적화
	- Offset: 예측된 bounding box의 위치 좌표 $(x, y, w, h)$의 offset
