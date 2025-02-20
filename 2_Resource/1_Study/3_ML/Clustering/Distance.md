---
date: 2024-02-21, 14:24
status: Permanent
tags:
  - Study/ML/Clustering
aliases:
  - 유클리디안 거리
  - 맨하튼 거리
  - 마할라노비스 거리
reference: 
author:
  - 조조링
  - clustering
url:
  - https://wkddmswh99.tistory.com/6
  - https://searle-j.tistory.com/2
related notes:
  - "[[Clustering]]"
---
# 유사도 척도
> *"어떤 거리 척도를 사용하여 유사도를 측정할 것인가?"*

## 유클리디안 거리 (Euclidean Distance)
![[Pasted image 20240221140556.png|300]]
- 가장 흔히 사용되는 거리 측도
- 두 데이터 사이의 직선거리
  $$d(X, Y)=\sqrt{\sum_{i=1}^P{(x_i-y_i)^2}}=||X-Y||_2$$
## 맨하튼 거리 (Manhattan Distance)
![[Pasted image 20240221142105.png|300]]
- X에서 Y로 이동 시 각 좌표축 방향으로만 이동할 경우에 계산되는 거리
$$d_{Manhattan}(X, Y)=\sum_{i=1}^P|x_i-y_i|$$
## 마할라노비스 거리 (Mahalanobis Distance)
![[Pasted image 20240221141331.png|500]]
- 데이터는 모종의 사건이 발생했을 때 **맥락**이 생기며, 이로 인해 평균과 분산이 달라짐
	- 이러한 맥락 때문에 거리 (유사도)에도 왜곡이 발생
	- eg. 100등과 99등, 2등과 1등 모두 1등수 밖에 차이가 나지 않지만, 실제로는 2등에서 1등으로 올라가는 것이 훨씬 어려움
- **맥락을 보정**하기 위해 변수 내 분산, 변수 간의 공분산을 모두 반영하여 거리를 계산하는 방식
$$d_{Mahalanobis}(X, Y)=\sqrt{(X-Y)^T{\sum}^{-1}(X-Y)}$$