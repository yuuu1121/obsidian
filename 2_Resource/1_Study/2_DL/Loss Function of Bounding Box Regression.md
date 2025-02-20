---
date: 2024-03-13, 15:23
status: Paper Review
tags:
  - PaperReview
  - Study/DL/LossFunction
  - PaperReview/YOLO/v4
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
## Limitations of Previous Works
### Anchor-based Loss Function
- Mean Squared Error (MSE):
	- 전통적인 객체 검출에 사용되는 Loss function (eg., [[YOLO v1 - Loss Function]])
	- 직접적으로 BBox 의 좌표 혹은 사전 정의된 Anchor box 의 Offset 예측
	- BBox 의 각 점의 좌표 값을 직접 추정하는 것은 그 점들을 독립적인 변수로 취급하는 것이기 때문에 객체의 Integrity 를 고려하지 않음
		- Integrity 
			- 각 객체가 지닌 고유한 형태, 크기, 구조 등을 전체적으로 고려하는 것을 의미
			- 즉, 객체의 온전한 상태를 고려하는 것을 의미
---
**Related Notes**
- [[Loss Function#Mean Squared Error (MSE]])
---
## Inspirations from Previous Works
### IoU-based Loss Function
- 객체의 Integrity 를 고려하기 위해 예측된 BBox 와 Ground truth BBox 의 연관성을 포함하는 IoU loss 사용
- IoU 는 **Scale invariant** 하기 때문에 L1, L2 loss 와 같이 Loss 가 Scale 에 비례하는 문제 발생하지 않음 (참고: [[YOLO v1 - Limitations#Loss Function|YOLO v1 - Limitations - Loss Function]])
---
#### Interest of Union (IoU) Loss
![[Pasted image 20240304165450.png]]

- GT 와의 IoU 를 높이는 방법으로 학습
- IoU 가 0 인 경우에 한해서 BBox 가 얼마나 떨어져있던 IoU 가 모두 0으로 나옴
	- BBox 간의 거리가 고려되지 않음
---
#### Generalized IoU (GIoU)
![[Pasted image 20240304170232.png]]
![[Pasted image 20240304170243.png]]

- 예측된 BBox 와 GT BBox 를 동시에 포함할 수 있는 최소 크기의 BBox **C** 를 구하고, 이 최소 영역 BBox 를 기존 IoU loss 의 분모에 사용
- 이를 통해, 겹치는 객체 간의 IoU 를 기반으로 Scale invariant 한 속성을 유지하면서 객체의 Shape 와 Orientation 까지 고려할 수 있음
- 여전히 수렴 속도가 느리고 부정확하게 박스를 예측
---
#### Distance IoU (DIoU)
![[Pasted image 20240304170457.png|+grid]]![[Pasted image 20240304170507.png|+grid]]
- GIoU loss 에 두 객체 사이의 중심점 거리에 해당하는 Penalty term 을 추가하여 수렴 속도를 향상시킨 Loss function
- GT 와 BBox 가 겹쳐진 영역이 동일하고, BBox 의 위치만 달라졌을 때 IoU, GIoU 는 위치정보를 포함하지 않기 때문에 동일하게 나타지만, DIOU는 중심점의 좌표를 고려하기에 값이 달라짐

---
**Related Notes**
- 
---
# Novel Methodology
## Complete IoU (CIoU)
- Overlapped area, Central point distance, Aspect ratio 3 가지 요소를 모두 고려하여 **객체가 겹치지 않은 경우 더 빠른 수렴을 가능**하도록 한 Loss function

---
**Related Notes**
- 
---
