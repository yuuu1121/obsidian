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
# Maximization
- **Definition**
	- 주어진 데이터 $\mathcal{D}$를 기반으로 모든 변수 $(x_1, \ldots, x_N)$의 값을 최적화하는 방법<br><br>
	- Equation
	  $$(\hat{x}_1, \ldots, \hat{x}_N) = \arg \max_{x_1, \ldots, x_N} p(x_1, \ldots, x_N \mid \mathcal{D})$$

<br><br>

# Max-Product Belief Propagation (BP)
![[Pasted image 20241208005831.png|+grid]]![[Pasted image 20241208005842.png|+grid]]

- **Definition**
	- 주어진 그래프에서 각 변수의 최적 구성(maximum likelihood configuration)을 찾기 위한 알고리즘
	  $$(\hat{x}_1, \ldots, \hat{x}_N) = \arg \max_{x_1, \ldots, x_N} p(x_1, x_2, \dots, x_N)$$

<br>

- **Principles**
	- [[Factor Graph|Factorization]]
	  $$p(x, \dots, x_N)=f_1(x_1, x_2)\cdots f_M(x_{N-1}, x_N)$$<br><br>
	- $\partial(a)$: 그래프에서 노드 $a$와 직접 연결된 이웃 노드(neighbors)의 집합
	- $\backslash\{a\}$: 집합에서 특정 원소 $a$를 제외하는 연산자<br><br>
	- Definition of Message
		- From **Factor node $f_u$** to **Variable node $x_i$**
		  $$\textcolor{red}{\mu_{u \to i}(x_i)} \overset{\text{def}}{=} \max_{x_{\partial u\backslash \left\{ i \right\}}} \left\{ \textcolor{green}{f_u(x_{\partial u})} \textcolor{blue}{\prod_{j \in \partial u \setminus \{i\}} \nu_{j \to u}(x_j)} \right\}$$
		- From **Variable node $x_i$** to **Factor node $f_u$**
		  $$\textcolor{blue}{\nu_{i \to u}(x_i)} \overset{\text{def}}{=} \textcolor{red}{\prod_{v \in \partial i \setminus \{u\}} \mu_{v \to i}(x_i)}$$
	- Marginal Probability
		$$p_{\max}=\max_{x_i}\prod_{v\in\partial i}\mu_{v\rightarrow i}(x_i)$$

<br><br>

## Max-Sum BP
- **Definition**
	- Max-Product BP 알고리즘에 로그 변환을 적용한 알고리즘

<br>

- **Principles**
	- Definition of Message
		- From **Factor node $f_u$** to **Variable node $x_i$**
		  $$\textcolor{red}{\mu_{u \to i}(x_i)} \overset{\text{def}}{=} \max_{x_{\partial u\backslash \left\{ i \right\}}} \left\{ \textcolor{green}{\log f_u(x_{\partial u})} +\textcolor{blue}{\sum\limits_{j \in \partial u \setminus \{i\}} \nu_{j \to u}(x_j)} \right\}$$
		- From **Variable node $x_i$** to **Factor node $f_u$**
		  $$\textcolor{blue}{\nu_{i \to u}(x_i)} \overset{\text{def}}{=} \textcolor{red}{\sum\limits_{v \in \partial i \setminus \{u\}} \mu_{v \to i}(x_i)}$$
	- Marginal Probability
		$$p_{\max}=\max_{x_i}\sum\limits_{v\in\partial i}\mu_{v\rightarrow i}(x_i)$$