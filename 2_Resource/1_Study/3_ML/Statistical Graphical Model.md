---
date: 2024-12-06
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
# Statistical Graphical Model
- **Definition**
	- [[Random Variables]]간의 의존성(dependences)을 시각적으로 표현하는 도구
	- 복잡한 데이터 구조를 단순화하고 효율적인 추론을 가능하게 함
		- Sum-product 및 Max-product의 Belief propagation을 활용하여 ML 추론 및 MAP([[Maximum A Posterior Estimation|Maximum A Posterior]]) 추론을 수행

<br>

- **Key Concepts - Types of Dependence**
	- **Correlation (상관관계)**
	    - 효율적인 추론을 위해, 각 변수의 값뿐만 아니라 **변수들 간의 관계**를 활용하는 복합적인 추론이 필요.
	    - 상관관계는 **무방향 그래프([[Undirected Graph]])** 로 표현.
	- **Causality (인과 관계)**
	    - 관찰된 변수(**observed variable**)로부터 잠재 변수(**latent variable**)를 추정하려면 **인과 모델(causality model)** 을 설계해야 함.
	    - 인과 관계는 **방향 그래프([[Directed Graph]])** 로 표현.

<br>

## Convenient Notation

![[Pasted image 20241207154204.png|+grid]]![[Pasted image 20241207154218.png|+grid]]![[Pasted image 20241207154422.png|+grid]]

- **Definition**
	- 그래프 모델에서 반복적인 구조나 복잡한 확률 모델을 간단하게 표현하기 위해 사용되는 표기법

<br>

- **Principle**
	- Plate Notation
		- 반복적인 구조를 그래프 모델에서 간단하게 나타내는 도구
		- 같은 구조가 여러 번 반복되는 경우, 직사각형 박스를 사용해 간결하게 표현<br><br>
		- 수식 표현
		  $$p(\{x_i\}_{i \in [N]}, z) = p(z) \prod_{i \in [N]} p(x_i \mid z)$$
			- $\{x_i\}_{i \in [N]}$: $N$개의 관측치.
			- $z$: 잠재 변수(latent variable).
			- **$p(z)$**: 잠재 변수 $z$의 사전 확률(prior probability).
			- **$p(x_i \mid z)$**: 관측 변수 $x_i$가 $z$에 조건부 종속적.
			- **$\prod_{i \in [N]}$**: Plate 내부에서 $N$번 반복됨을 나타냄.<br><br>
	- 관측 변수와 잠재 변수
		- 관측 변수(observed variables)
			- 채워진 노드로 표시
			- 직접적으로 관측할 수 있는 변수
		- 잠재 변수(latent variables)
			- 빈 노드로 표시
			- 직접 관측할 수 없고, 추론 과정을 통해 값이 추정되는 변수

