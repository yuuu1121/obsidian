---
date: 2024-12-09
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/ML
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Dimensionality Reduction
![[Pasted image 20241209025142.png]]

- **Definition**
	- 데이터를 더 간결하고 효율적으로 표현하기 위해 원래의 고차원 데이터를 저차원으로 변환하는 과정
	- 데이터의 주요 정보는 최대한 유지하되, 불필요한 노이즈나 중복된 정보 제거
	- e.g., [[Principal Component Analysis]] (PCA), [[Factor Analysis]] (FA)

<br/>

- **Curse of Dimensionality**
	- 데이터의 차원이 증가함에 따라 분석 및 학습이 어려워지는 현상
		- 데이터 희소성
			- 차원이 증가하면 데이터가 고차원 공간에서 매우 희소해져서 데이터 간의 거리가 모두 유사하게 변하고 모델이 패턴을 학습하기 어려워짐
		- 과적합 위험
			- 고차원에서는 모델이 데이터의 노이즈까지 학습하면서 일반화 성능이 떨어질 가능성이 커짐
