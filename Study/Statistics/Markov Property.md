---
date: 2024-12-07
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/Statistics
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Markov Property
- **Definition**
	- 확률 과정이나 [[Statistical Graphical Model|그래프 모델]]에서 잠재 변수(latent variable)를 예측하는데 특정 변수만 필요하며, 나머지 다른 변수들과 독립적임을 설명하는 핵심 개념
	- 확률 변수 간의 [[Conditional Independence]]을 기반으로 함<br><br>
	- Time-based Markov Property
		- 현재 상태만으로 미래 상태를 예측할 수 있으며, 과거 상태는 필요하지 않다고 가정
		  $$P(X_{t+1} \mid X_t, X_{t-1}, \dots, X_0) = P(X_{t+1} \mid X_t)$$
	- Graph-based Markov Property
		- Directed Graph
			- 변수 $X_i$는 그 **부모 변수들(Parents)**에 대해서만 의존
			  $$P(X_1, \dots, X_N) = \prod_{i=1}^N P(X_i \mid \text{Pa}(X_i))$$<br>
		- Undirected Graph
			- 변수 $X_i$는 직접 연결된 **이웃 변수들**만 알면 나머지 변수들과 독립
			  $$X_i \perp\!\!\!\perp \text{Rest} \mid \text{Neighbors}(X_i)$$

<br>

- **Key Concepts**
	- Local Independence
		- 변수는 직접 연결된 변수 또는 부모 변수를 통해서만 다른 변수들과 관계를 맺음
		- e.g., $P(X_3 \mid X_1, X_2) = P(X_3 \mid X_1)$ (만약 $X_1$이 $X_3$의 유일한 이웃인 경우).
	- [[Factor Graph|Factorization]]
		- Markov Property를 사용하면 결합 확률 분포를 더 작은 조건부 확률들로 나눌 수 있음
		- e.g., $P(X_1, X_2, X_3) = P(X_1) P(X_2 \mid X_1) P(X_3 \mid X_2)$
	- Markov Blanket
		- 특정 노드 $X_i$가 나머지 모든 변수들 $\{X - X_i\}$와 조건부 독립(independent)을 이루기 위해 필요한 최소 변수 집합 $M_i$
		- i.e., $X_i$와 나머지 변수들은 $M_i$를 조건으로 독립이며, Markov blanket에 포함된 변수들을 알고 있으면, 나머지 모든 변수들은 특정 노드($X_i$)에 영향을 주지 않음
		  $$X_i \perp\!\!\!\perp \{X - X_i - M_i\} \mid M_i$$
		- e.g., Directed Graph
			- **부모 (Parents)**: $X_i$에 직접 영향을 주는 변수들.
			- **자식 (Children)**: $X_i$가 직접 영향을 미치는 변수들.
			- **공부모 (Co-Parents)**: $X_i$의 자식에게 영향을 주는 다른 변수들.
		- e.g., Undirected Graph
			- $X_i$의 Markov Blanket은 **직접 연결된 이웃 노드들**로만 구성