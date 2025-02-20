---
date: 2024-03-04, 17:10
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
![[Pasted image 20240313160901.png|500]]![[Pasted image 20240313160921.png|500]]

- Overfitting
	- 네트워크 Optimization 중 학습 데이터에만 존재하는 특징들이 모델에 과하게 반영되어 Loss function 이 필요 이상으로 작아지게 되는 현상
- Regularization
	- 모델의 Loss function 이 너무 작아지지 않도록 특정한 값 또는 함수를 추가하는 방법
	- 이를 통해 특정한 Weight 값이 과도하게 커져서 일부 특징에 의존하는 현상을 방지하고, 데이터의 일반적인 특징 (Generalization) 을 잘 반영하도록 만드는 방법
---
# Methods
![[Pasted image 20240304102816.png|+grid]]![[Pasted image 20240304102823.png|+grid]]
<center style='font-size:14;opacity:0.7;'>DropOut (좌), DropConnect (우)</center>

![[Pasted image 20240304102911.png]]

<center style='font-size:14;opacity:0.7;'>DropBlock</center>

- DropOut: 
	- 네트워크에서 무작위로 일부 뉴런을 학습에서 배제하여 regularization 효과를 주는 방법 
- DropConnect: 
	- 네트워크에서 뉴런 사이의 connection을 학습에서 배제하여 모델의 표현력을 살리면서 regularization 효과를 주는 방법 
- DropBlock: 
	- feature map 내에서 연속하는 영역의 activation을 0으로 만들어 네트워크에 regularization 효과를 주는 방법