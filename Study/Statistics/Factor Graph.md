---
date: 2024-12-07
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/Statistics
aliases:
  - Factorization
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Factor Graph
![[Pasted image 20241207204136.png|+grid]]![[Pasted image 20241207205435.png|+grid]]

- **Definition**
	- [[Statistical Graphical Model|그래프 기반 확률 모델]]에서 결합 확률 분포(joint probability distribution)를 팩터(factor) 형태로 표현하는 특별한 형태의 그래프
	- [[Directed Graph]]와 [[Undirected Graph]]를 모두 일반화한 구조
		- Undirected Graph
			- Undirected graph에서는 최대 클리크(maximal clique)를 기반으로 결합 확률을 표현하지만, factor graph에서는 이를 팩터 노드로 표현
		- Directed Graph
			- Directed graph에서는 부모-자식 관계를 기반으로 조건부 확률을 표현하지만, factor graph에서는 모든 관계를 팩터 노드로 일반화

<br>

- **Key Concepts**
	- Bipartite Graph
		- Factor graph는 두 종류의 노드로 구성된 이분 그래프(bipartite graph)
			- Variable Node: $x_1, x_2, \dots, x_N$
			- Factor Note: $f_1, f_2, \dots, f_M$
		- 변수 노드(variable node)끼리는 직접 연결되지 않고, 팩터 노드(factor node)를 통해 간접적으로 연결됨
	- Joint Probability Distribution
	  $$p(x_1, x_2, \dots, x_N) = \prod_{j=1}^M f_j(\text{Nei}_j)$$
		- $\text{Nei}_j$: 팩터 $f_j$에 연결된 변수 노드들의 집합.
		- $f_j$: 특정 변수들의 상관관계를 나타내는 **팩터 함수(Factor Function)**.
	- **Factorization**
		- Factor graph에서는 결합확률 분포를 그래프 구조에 따라 분해하여 표현
		- e.g., 변수 $x_1, x_2, x_3$가 있고 팩터 노드 $f_1, f_2, f_3, f_4$가 연결된 경우
			$$p(x_1, x_2, x_3) = f_1(x_1, x_2) f_2(x_1, x_2, x_3) f_3(x_2, x_3) f_4(x_3)$$
	- [[Conditional Independence]] $X \perp\!\!\!\perp Y \mid Z$
		- 경로 상의 모든 팩터 노드들이 $Z$에 의해 차단되면, $X$와 $Y$는 $Z$에 대해 조건부 독립

<br>

- **Advantages**
	- Generalization
		- Directed graph와 undirected graph를 모두 포함하는 표현력
	- Efficient Computation
		- ![[Pasted image 20241206173449.png]] #mcl/list-grid
		- Factorization in Directed Graph : <br><br>$p(L, D, I, E, S, G) = p(L)p(D)p(I)p(E \mid I)p(S \mid D, L, E)p(G \mid S)$<br><br>
			- Reduce parameter number
				- 전체 결합 확률 분포를 저장하려면 모든 가능한 변수 조합에 대한 확률을 저장해야함
					- Factorization 전: $2^6-1=63$
				- Factorization을 통해 각 조건부 확률만 저장하면 파라미터의 수가 매우 감소함
					- Factorization 후: $1+1+1+2^1+2^3+2^1=15$
	- Application
		- [[Sum-Product Belief Propagation]]
			- 결합 확률의 **주변화(Marginalization)**를 효율적으로 계산
		- [[Max-Product Belief Propagation]]
			- 확률 분포의 **최대화(Maximization)**를 통해 MAP 추론 수행
		- 데이터 기반 그래프 생성
			- e.g., [[Chow-Liu Algorithm]](1968)을 사용해 데이터에서 그래프 구조 학습.