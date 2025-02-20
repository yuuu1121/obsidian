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
# Chow-Liu Algorithm
- **Definition**
	- 데이터에서 얻은 경험적 분포 $p(x)$를 가장 잘 근사하는 트리 그래프 $T^*$를 학습하는 알고리즘
	- 하지만 $p(X)$는 고차원 변수 $X = (X_1, X_2, \dots, X_N)$를 포함하므로, 모든 변수의 조합에 대해 저장하거나 계산하기엔 너무 복잡하므로, 이를 단순화하기 위해 **트리 구조**로 근사<br><br>
	- Optimization Problem
		- $p_T(x)$: 트리 구조로 근사된 분포
		- $T^*$: 경험적 분포와 가장 유사한 트리를 찾는 문제<br><br>
		- Objective
		  $$T^* = \arg\min_{T:\text{tree}} \text{KL}(p \| p_T)\overset{\text{def}}{=} \sum_{x \in \mathcal{X}} p(x) \log \frac{p(x)}{p_T(x)}$$
			- 여기서 
				- $\text{KL}(p \| p_T)$: [[Maximum Likelihood Estimation#An Interpretation of MLE KL-Matching|KL-Divergence]]
				- $\mathcal{X}$: 모든 가능한 $X$의 상태 집합.

<br>

- **Key Concepts**
	- Empirical Distribution
		- 데이터 $X = (X_1, \dots, X_N)$는 $K$개의 샘플로 구성
		  $$\mathcal{D} = \{x^{(1)}, x^{(2)}, \dots, x^{(K)}\}, \quad x^{(k)} = (x_1^{(k)}, \dots, x_N^{(k)})$$
		- 경험적 분포 $p(x)$는 다음과 같이 정의
		  $$p(x) \overset{\text{def}}{=} \frac{1}{K} \sum_{k=1}^{K} \mathbb{1}[x^{(k)} = x]$$
	- Approximate Distribution
		- Chow-Liu 알고리즘은 Directed Tree 구조를 사용하여 경험적 분포 $p(x)$를 $p_T(x)$로 근사
		  $$p_T(x) \overset{\text{def}}{=} \prod_{j \in V} p(x_j \mid x_{\text{pa}(j)})= p(x_{\text{root}}) \prod_{(i,j) \in E} p(x_j \mid x_i)= \left( \prod_{i \in V} p(x_i) \right) \left( \prod_{(i,j) \in E} \frac{p(x_j, x_i)}{p(x_i) p(x_j)} \right)$$
			- 여기서 :
				- $E$: 트리의 엣지 집합 (부모-자식 관계).
				- $x_{\text{root}}$: 트리의 루트 노드.<br>
		- e.g., 주어진 분포 $p(x_1, x_2, x_3, x_4, x_5, x_6)$는 다음과 같이 근사 ([[Factor Graph|Factorization]])<br>
		  ![[Pasted image 20241208133944.png]]
		  $$p(x_6 \mid x_5) \cdot p(x_5 \mid x_2) \cdot p(x_4 \mid x_2) \cdot p(x_3 \mid x_1) \cdot p(x_2 \mid x_1) \cdot p(x_1)$$

<br>

- **Principles**
	- 문제 정의
		- 목표: **최적의 트리 분포** $T^*$를 찾아, 경험적 분포 $p$를 가장 잘 근사하도록 함
		- Optimization Problem
		  $$T^* = \arg\min_{T:\text{tree}} \text{KL}(p\|p_T)$$<br>
	- 최대화 문제로 변환
		$$\begin{align*}
		\text{KL}(p\|p_T) &= \sum_{x \in \mathcal{X}} p(x) \log \frac{p(x)}{p_T(x)}\\\\
		&= - \sum_{x \in \mathcal{X}} p(x) \log p_T(x) + \text{constant}\\\\\\
		T^* &= \arg\max_{T:\text{tree}} \sum_{x \in \mathcal{X}} p(x) \log p_T(x)
		\end{align*}$$
	- 트리 분포의 인수 분해(factorization)
		$$\begin{align*}
		p_T(x) &= \prod_{i \in V} p(x_i) \prod_{(i,j) \in E} \frac{p(x_i, x_j)}{p(x_i)p(x_j)}\\\\
		T^* &= \arg\max_{T:\text{tree}} \sum_{i \in V} -H(X_i) + \sum_{(i,j) \in E} I(X_i, X_j)
		\end{align*}$$
		- 여기서
			- $H(X_i)$: 변수 $X_i$의 엔트로피.
			- $I(X_i, X_j)$: $X_i$와 $X_j$ 간 상호정보량.
	- MWST (Maximum Weighted Spanning Tree)
		- 최적화 문제를 가중치 $w(i,j) = I(X_i, X_j)$를 가지는 **최대 가중 스패닝 트리** 문제로 변환
		  $$T^* = \arg\max_{T:\text{tree}} \sum_{(i,j) \in E} I(X_i, X_j)$$

<br>

- **Algorithm**
	1. 상호 정보량 계산
		- 모든 변수 쌍 $(i,j)$에 대해 $I(X_i, X_j)$를 계산
		  $$I(X_i, X_j) = \sum_{x_i, x_j} p(x_i, x_j) \log \frac{p(x_i, x_j)}{p(x_i)p(x_j)}$$
	2. Kruskal의 탐욕 알고리즘 적용
		- $w(i,j) = I(X_i, X_j)$를 기준으로 엣지를 내림차순 정렬
			- 초기화: $E = \emptyset$.
		- 가장 높은 가중치를 가진 엣지를 $E$에 추가.
		- 사이클이 생성되지 않을 경우에만** 다음 엣지를 추가.
		- $|E| = N-1$일 때 알고리즘 종료 ($N$은 변수 노드 수).
	3. 트리 방향 설정
		- 임의의 노드를 루트로 선택하고, 방향성을 부여.

<br>

- **Example**
	- Problem Define
		- Objective: 
			- 손글씨 숫자 데이터를 분류하는 시스템 개발.
			- 새로운 입력 $x^{\text{new}}$에 대해 적합한 숫자 $\ell^{\text{new}}$를 예측:
			  $$\arg \max_{\ell \in \{0, \dots, 9\}} p_\ell \cdot p(x^{\text{new}} \mid \ell^{\text{new}} = \ell)$$
				- 여기서 $p_\ell$은 사전 확률, $p(x^{\text{new}} \mid \ell)$은 조건부 확률.
		- Dataset: $19,000+$ 개의 손글씨 이미지, 각 이미지가 $96$개의 바이너리 특징 ($12 \times 8$ 격자)으로 구성.
	- Chow-Liu Algorithm
		- $2^{96}$개의 가능한 이미지 경우의 수를 모두 다루는 것은 불가능.
		- Chow-Liu 알고리즘을 통해 데이터의 패턴을 트리 구조로 근사.<br>
		- Application
			- 숫자 $\ell \in \{0, \dots, 9\}$별로 조건부 분포 $p(x^{(k)} \mid \ell)$을 경험적으로 학습.
			- Chow-Liu 알고리즘으로 트리 기반 분포 $p_{T_\ell}(x)$ 생성.
			- 최종 분류 규칙:
			  $$\arg \max_{\ell \in \{0, \dots, 9\}} p_\ell \cdot p_{T_\ell}(x^{\text{new}})$$
				- 여기서 $T_\ell$은 Chow-Liu 알고리즘으로 생성된 트리 그래프.
	- Advantage
		- 복잡한 분포를 단순화하면서도 정확하게 근사.
		- 제한된 데이터에서도 실질적인 패턴 인식 가능.
		- 최적 트리 모델로 낮은 에러율을 달성.