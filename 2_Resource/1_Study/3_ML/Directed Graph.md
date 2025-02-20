---
date: 2024-12-07
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
# Directed Graph a.k.a. Bayesian Network
- **Definition**
	- 확률 변수들 간의 인과 관계(Causality model)를 표현하는데 사용되는 그래프 모델
	- [[Bayes' Theorem]]를 기반으로 [[conditional independence)](Conditional Independence.md|조건부 독립성(conditional independence)]]과 결합 확률을 모델링하므로 Bayesian Netork라고도 불림
	- Directed graph는 일반적으로 사이클(cycle)이 없는 Directed Acyclic Graph (DAG)로 사용됨


<br>

- **Key Concepts**
	- Joint Probability Distribution
		- Directed graph는 결합 확률을 조건부 확률로 [[Factor Graph|Factorization]] 함
		  $$p(x_1, x_2, \dots, x_N) = \prod_{i \in [N]} p(x_i \mid \text{pa}(x_i))$$
			- 여기서 $\text{pa}(x_i)$는 $x_i$의 부모 집합.
			- 각 변수는 자신의 부모 노드(parent node)의 조건부로만 정의됨

<br><br>

## D-Separation
- **Definition**
	- Directed graph에서 조건부 독립성을 확인하는 기법
	- **독립(Independent)** 또는 **의존(Dependent)** 여부는 경로(Path)가 **차단(Blocked)**되었는지 여부에 따라 결정

<br>

![[Pasted image 20241207214358.png]]

- **Rules**
	- Non-Collider
		- $C$가 관찰되었을 때 해당 경로가 차단됨<br><br>
		- Head-to-Tail $P(A, B, C) = P(A)p(C\mid A)p(B\mid C)$
			$$P(A, B\mid C)={p(A)p(C\mid A)p(B\mid C)\over p(C)}=p(A\mid C)p(B\mid C)\Longrightarrow A \perp\!\!\!\perp B \mid C$$
		- Tail-to-Tail $P(A, B, C) = P(C)p(A\mid C)p(B\mid C)$
			$$P(A, B\mid C)={p(C)p(A\mid C)p(B\mid C)\over p(C)}=p(A\mid C)p(B\mid C)\Longrightarrow A \perp\!\!\!\perp B \mid C$$<br>

	- Collider (Head-to-Head) $P(A, B, C) = P(A)p(B)p(C\mid A, B)$
		- Collider의 노드 $C$ 자체가 관측되지 않고, $C$의 후손(Descendant)도 조건 변수에 포함되지 않을 때 경로가 차단됨<br>
			$$P(A, B)=p(A)p(B)\sum\limits_Cp(C\mid A, B)=p(A)p(B)\Longrightarrow A\perp\!\!\!\perp B$$
		- 단, $C$의 Descendant 노드가 관측될 경우 $A \not\!\perp\!\!\!\perp B \mid C$, $A \not\!\perp\!\!\!\perp B \mid D$