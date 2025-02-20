---
date: 2024-02-21
status: Permanent
tags:
  - Study/ML/Clustering
  - Study/Lecture/Machine-Learning
aliases: 
reference: 
author: 
url: 
related notes: []
---
# Clustering
- **Definition**
	- 데이터를 유사한 특징을 가진 그룹(cluster)으로 분할하는 [[Unsupervised Learning]] 기법
		- 각 클러스터는 내부적으로 유사성이 높고 다른 클러스터와는 차이가 큼<br><br>
	- Objective: 데이터를 이해하고 분석하는 데 도움을 줄 수 있는 숨겨진 패턴 발견

<br>

- **Approaches**
	- Nonparametric Approach
		- 데이터 분포 가정 없이 단순히 데이터의 거리를 이용하는 방식
		- e.g., [[K-means Clustering]], [[K-means Clustering#Soft K-means Clustering|soft K-means clustering]]
	- Parametric Approach
		- 데이터가 가우시안 분포를 따른다고 가정하며, 해당 분포의 매개변수(평균과 분산)를 학습하는 방식
		- e.g., [[Expectation Maximization]] (EM), [[Gaussian Mixture Model]] (GMM)

<br><br>

## Loss Function
- Objective
	- 데이터 포인트 $\{x_i \in \mathbb{R}^D \}_{i=1}^{N}$와 클러스터 수 $K \in \mathbb{N}$가 주어졌을 때 데이터와 클러스터 중심 간의 거리를 최소화하는 것
	  $$\min_{\mu, r} \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \|x_i - \mu_k\|^2$$
		- 여기서:
			- $r_{ik}$: 데이터 $x_i$가 클러스터 $k$에 속하는지 나타내는 값 (0 또는 1).
			- $\mu_k$: 클러스터 $k$의 중심점.
			- 유사성 측정은 주로 [[Distance#유클리디안 거리 (Euclidean Distance]]|Euclidean%20Distance)를 주로 사용