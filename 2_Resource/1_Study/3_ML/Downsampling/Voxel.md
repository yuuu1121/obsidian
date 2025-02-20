---
date: 2024-02-21, 15:10
status: Permanent
tags:
  - Study/Downsampling
aliases: 
reference: 
author: 
url:
  - https://pcl.gitbook.io/tutorial/part-1/part01-chapter02
related notes:
  - "[[Downsampling]]"
---
# Voxel 이란?
![[Pasted image 20240221150527.png|300]]
- 2D 이미지를 구성하는 최소 단위인 pixel을 3D로 확장한 것
	- 이미지 1x1 에서 깊이 정보를 포함한 1x1x1 로 표현하고, 이때의 최소 단위를 Voxel (Volume + Pixel)으로 정의
## 복셀화 방법 (Voxelization)
![[Pasted image 20240221150700.png|500]]
- 포인트 클라우드를 복셀로 변환하는 작업
	- PCL에서는 **Voxel Grid filter**를 이용하여 복셀화 수행
### 진행 방법
1. 사용자 정의로 적합한 복셀 크기 설정 (`leaf_size`)
2. 각 복셀의 중심점에서 `leaf_size` 내 포인트 (파란색) 유무 계산
3. 포인트들의 중심점 (빨간색)을 계산하고 나머지 포인트 제거