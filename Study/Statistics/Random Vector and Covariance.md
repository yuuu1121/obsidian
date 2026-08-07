---
date: 2024-09-22
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Random Vector
- $\mathbf{X}\in \mathbb{R}^n$
	- $n$개의 확률 변수 ($X_1, X_2, \cdots X_n$)로 이루어진 집합
	- 확률 분포 $P(X)$: ($X_1, \cdots, X_n$)의 결합 분포(joint distribution)
		- 즉, 각 확률 변수 $X_i$들이 함께 어떻게 분포하는지를 설명

<br>

# Covariance
- [[Expectation and Moments|Expectation]] vector $\boldsymbol{\mu}:=\mathbb{E}[\mathbf{X}]$
	- 확률 변수의 기대값을 모은 벡터
	- $\boldsymbol{\mu}=(\mathbb{E}[X_1], \cdots, \mathbb{E}[X_n])$
- [[Expectation and Moments#Moments of RV|Covariance]] matrix $\boldsymbol{\Sigma}\in \mathbb{R}^{n\times n}$  ^hknq01
	- $\boldsymbol{\Sigma}:=\mathbb{E}[(\mathbf{X}-\boldsymbol{\mu})(\mathbf{X}-\boldsymbol{\mu})^T]=\sum\limits_x{(\mathbf{x}-\boldsymbol{\mu})(\mathbf{x}-\boldsymbol{\mu})^TP(\mathbf{X}=\mathbf{x})}$
	- 공분산 행렬의 각 성분 $\boldsymbol{\Sigma}_{i, j}$는 두 확률 변수 $X_i$와 $X_j$의 공분산을 나타내며, 다음과 같이 정의
		- $\boldsymbol{\Sigma}_{i, j}=cov(X_i, X_j):=\mathbb{E}[(X_i-\mathbb{E}[X_i])(X_j-\mathbb{E}[X_j])]$
	- 공분산과 상관관계
		- 공분산 행렬의 대각선 성분: 각 확률 변수의 분산
		- 공분산 행렬의 비대각선 성분: 두 확률 변수 간의 공분산

![[Pasted image 20240922175345.png]]
<br>

# Correlation
- 상관계수 $corr(X, Y)$는 공분산을 정규화한 값
- 상관계수는 [-1, 1] 사이 값을 가지며, 두 변수 간의 선형적인 상관관계를 설명

$$corr(X, Y)={cov(X, Y)\over\sqrt{Var(X)Var(Y)}}\in \left[-1, 1\right]$$