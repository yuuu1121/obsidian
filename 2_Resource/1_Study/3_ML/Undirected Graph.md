---
date: 2024-12-07
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/DL
aliases:
  - Markov Random Field
  - MRF
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
![[Pasted image 20241206170513.png]]
<br>

# Undirected Graph a.k.a. Markov Random Field (MRF)
- **Definition**
	- 확률 변수들 간의 [[Conditional Independence|조건부 독립성]]을 표현하기 위해 사용하는 확률 모델
	- [[Markov Property]]를 항상 만족하기 때문에 Markov Random Field (MRF) 라고도 불림
	- Markov Random Field에서는 결합 확률 분포(Joint Probability Distribution)를 최대 클리크(maximal cliques)로 [[Factor Graph|Factorization]] 됨
	  $$p(x) = \frac{1}{Z} \prod_{C \in \mathcal{C}} \psi_C(x_C)=\frac{1}{Z} \psi_{wxy}(w, x, y) \psi_{xyz}(x, y, z)$$
		- $x$: 랜덤 변수들의 집합 $\{x_i\}_{i\in[N]}$
		- $\mathcal{C}$: 최대 클리크(maximal cliques) 집합
		- $\psi_C(x_C)$: 클리크 포텐셜(clique potential)
			- $x_C$: 변수들의 상관관계를 나타내는 비음수
		- $Z$: 정규화 상수(normalization constant)

<br>

- **Key Concepts**
	- Clique $C$
		- 무방향 그래프에서 완전히 연결된 노드의 부분집합
		- 즉, 클리크 내부의 모든 노드가 서로 간선으로 직접 연결된 상태
		- i.e., $wx, wy, yz, xz, xyz, wxy, xy$
	- Maximal Clique $\mathcal{C}$
		- 추가적인 노드를 포함할 수 없는 가장 큰 완전 연결된 클리크
		- 최대 클리크만 결합 확률식에서 사용됨
		- i.e., $xyz, wxy$
	- Clique Potential
		- 클리크 포텐셜 $\psi_C(x_C)$는 특정 클리크 $C$에 속한 변수들의 상관관계를 나타내는 함수
		- 클리크 내부 변수들의 상호작용 강도를 비음수 함수로 표현
		  $$\psi_C(x_C)\geq 0$$
		- 조건부 확률은 확률 자체를 나타내지만, 클리크 포텐셜은 상관관계만 나타냄
		- 클리크 포텐셜만으로 결합 확률을 계산할 수 없으며, 정규화 상수 $Z$를 통해 정규화하면 확률로 변환 가능
	- Normalization Constant $Z$
		- 확률 값을 1로 정규화하기 위해 모든 가능한 최대 클리크 조합의 클리크 포텐셜의 곱을 합한 값
		  $$Z=\sum\limits_x\prod_{C\in \mathcal{C}}\psi_C(x_C)=\sum_{w,x,y,z} \psi_{wxy}(w, x, y) \psi_{xyz}(x, y, z)$$

<br>

## Hammersley-Clifford Theorm
![[Pasted image 20241207220747.png]]

- **Definition**
	- 그래프의 특정 서브셋 $X, Y, Z \subset V$에서 $Z$가 $X$와 $Y$를 분리(separate)하면 다음이 성립
	  $$X \perp\!\!\!\perp Y \mid Z\iff p(X, Y, Z) = p(X \mid Z)p(Y \mid Z)$$
	- 이 정리는 무방향 그래프에서 조건부 독립성을 수학적으로 정의하는 기반이며, 확률분포 $p$는 클리크의 함수로 표현될 수 있음
	  $$p(X) \propto \prod_{C \in \mathcal{C}} \psi_C(x_C)$$