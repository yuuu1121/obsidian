---
date: 2024-12-08
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
# K-means Clustering
- **Definition**
	- 데이터를 $K$개의 클러스터로 분할하는 [[Unsupervised Learning]] 알고리즘
	- 각 클러스터는 중심점(centroid)을 기준으로 데이터 포인트를 그룹화<br><br>
	- Objective
		- 데이터 포인트와 클러스터 중심 간의 거리(오차)를 최소화
		  $$L = \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \|x_i - \mu_k\|^2$$

<br>

## K-means Algorithm

![[Pasted image 20241208171333.png|+grid]]![[Pasted image 20241208171350.png|+grid]]

1. Initialization
	- $K$개의 초기 중심점 $\mu = \{\mu_k\}_{k=1}^K$을 랜덤으로 설정
		- 이 중심점들은 각 클러스터의 초기 대표 값 역할을 함
2. Assignment Step
	- 각 데이터 포인트 $x_i$를 가장 가까운 중심점 $\mu_k$에 할당
		- 거리의 기준은 [[Distance#유클리디안 거리 (Euclidean Distance]]|Euclidean%20Distance)로 계산<br>
			$$r_{ik} =
			
			\begin{cases}
			
			1, & \text{if } k = \arg\min_\ell \|x_i - \mu_\ell\|^2 \\
			
			0, & \text{otherwise}.
			
			\end{cases}$$
			- 여기서 $r_{ik}$는 $x_i$가 클러스터 $k$에 속하면 1, 아니면 0.
3. Update Step
	- 각 클러스터의 중심점을 데이터 포인트의 평균으로 갱신
	  $$\mu_k = \frac{\sum_{i \in [N]} r_{ik} x_i}{\sum_{i \in [N]} r_{ik}}$$
	- 위 단계를 반복하여 수렴
4. Convergence Check
	- 중심점의 변화가 거의 없거나(즉, $\|\mu_k^{\text{new}} - \mu_k^{\text{old}}\| < \epsilon$) 클러스터 할당이 더 이상 바뀌지 않으면 알고리즘 종료.

<br><br>

## Properties of K-menas
- Initialization
	- 중심점을 랜덤으로 초기화하기 때문에 결과가 초기화에 따라 달라질 수 있음
	- K-means++ 알고리즘은 초기 중심점을 데이터 간 최대 거리를 고려하여 선택
- Convergence
	- 유한한 시간안에 수렴 보장
	- 그러나 Outlier에 민감하며, global optimum이 아닌 local optimum에 빠질 수 있음
- Computational complexity per iteration
	- Assignment: $O(KND)$
	- Update Step: $O(N)$<br><br>
	- 여기서:
		- $K$: 클러스터 수.
		- $N$: 데이터 수.
		- $D$: 데이터 차원.

<br><br>

# K-medoids Clustering

![[Pasted image 20241208172744.png]]

- **Definition**
	- Clustering 기법 중 하나로, K-means와 유사하지만, 중심점 대신 데이터 포인트 자체를 글러스터의 대표 값(medoid)으로 선택
	- K-menas 보다 outlier에 더 강인함
	- e.g., Partitioning Around Medoids (PAM)<br><br>
	- Objective
		- 클러스터 내 데이터와 대표 값 간의 총 거리 비용을 최소화

<br><br>

# Soft K-means Clustering
- **Definition**
	- K-means 알고리즘의 확장된 버전으로, 각 데이터 포인트가 하나의 클러스터에만 할당되지 않고, 여러 클러스터에 속할 확률을 가짐
	- 클러스터링의 결과로 확률적 소속을 제공하며, 데이터가 여러 클러스터 간 경계에 있을 때 더 유연한 결과를 제공

<br>

- **Key Concepts**
	- Objective
		- 데이터 포인트와 클러스터 중심 간의 거리(오차)를 최소화하고, 데이터가 특정 클러스터에만 치우치지 않고 조화롭게 분포하도록 함
		  $$J = \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \|x_i - \mu_k\|^2 - \frac{1}{\beta} \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \log r_{ik}$$
		- 첫번째 항: 데이터와 클러스터 중심 간 거리 최소화
			- 데이터 포인트 $x_i$와 클러스터 중심 $\mu_k$ 사이의 거리 $\|x_i - \mu_k\|^2$를 가중치 $r_{ik}$로 조합하여 계산.
			- $r_{ik}$: 데이터 $x_i$가 클러스터 $k$에 속할 확률(책임도, responsibility).
		- 두번째 항: 소속 확률의 엔트로피 최대화
			- $r_{ik}$를 로그에 넣어 확률의 분포를 부드럽게 만드는 항.
			- 엔트로피(entropy)를 계산하여, 데이터가 특정 클러스터에만 치우치지 않고 조화롭게 분포되도록 유도.
	- Parameter $\beta$
		- $\beta$ 값이 크면
			- $-\frac{1}{\beta}$가 작아져, 두 번째 항의 영향력이 약해짐.
			- Soft K-means는 Hard K-means에 가까워지며, 데이터는 특정 클러스터에만 집중적으로 속하게 됨.
		- $\beta$ 값이 작으면
			- $-\frac{1}{\beta}$가 커져, 두 번째 항의 영향력이 강해짐.
			- 데이터 포인트는 여러 클러스터에 걸쳐 고르게 확률적으로 분포.
<br>

## Soft K-means Algorithm
1. Initialization
	- $K$개의 초기 중심점 $\mu = \{\mu_k\}_{k=1}^K$을 랜덤으로 설정
		- 이 중심점들은 각 클러스터의 초기 대표 값 역할을 함
2. Assignment Step
	- 각 데이터 포인트가 클러스터 $k$에 속할 확률 $r_{ik}$를 계산.
	  $$r_{ik} = \frac{\exp(-\beta \|x_i - \mu_k\|^2)}{\sum_{\ell \in [K]} \exp(-\beta \|x_i - \mu_\ell\|^2)}$$
	- 확률은 거리와 $\beta$에 따라 결정.
3. Update Step
	- $r_{ik}$를 바탕으로 각 클러스터 중심 $\mu_k$를 재계산.
	  $$\mu_k = \frac{\sum_{i \in [N]} r_{ik} x_i}{\sum_{i \in [N]} r_{ik}}$$
	- 위 단계를 반복하여 수렴
4. Convergence Check
	- 중심점의 변화가 거의 없거나(즉, $\|\mu_k^{\text{new}} - \mu_k^{\text{old}}\| < \epsilon$) 클러스터 할당이 더 이상 바뀌지 않으면 알고리즘 종료.