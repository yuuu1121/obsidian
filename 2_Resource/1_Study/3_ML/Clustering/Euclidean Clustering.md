---
date: 2024-02-20, 14:36
status: Fleeting
tags:
  - Study/ML/Clustering
aliases: 
reference: 
author: 
url:
  - https://adioshun.gitbooks.io/3d_people_detection/content/ebook/part02/part02-chapter01/part02-chapter01-euclidean.html
related notes:
  - "[[Clustering Algorithms]]"
  - "[[Clustering]]"
---
# Euclidean Clustering
- 가장 간단한 군집화 방법으로, 두 점 사이의 거리를 계산 해서 특정 거리 이하일 경우 동일한 군집으로 간주하는 방법
- 군집의 개수가 정해지지 않은 [[Clustering Algorithms#계층적 군집 (Hierarchical Clustering]]|계층적%20군집)이며, 거리를 계산하는 거리 척도로 [[Distance#유클리디안 거리 (Euclidean Distance]]|유클리디안%20거리%20(Euclidean%20Distance))를 사용
## 동작 과정
1. 효율적인 계산을 위하여 포인트 클라우드의 [[KDTree]] 구조체 생성
2. 하나의 군집으로 간주하는 거리 정보 (Cluster Tolerance)를 설정
3. 근접한 포인트를 탐색 하면서 거리 내에 있을 경우 하나의 군집으로 설정
4. 근접한 포인트가 지정된 거리 내에 없을 경우 탐색하지 않은 새 포인트를 새 군집으로 선택하고 탐색

