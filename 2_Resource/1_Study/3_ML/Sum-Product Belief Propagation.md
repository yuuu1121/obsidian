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
# Marginalization
- **Definition**
	- 주어진 데이터 $\mathcal{D}$를 기반으로 특정 변수의 확률 $p(x_i)$를 계산하는 방법 ([[Law of Total Probability]])<br><br>
	- Equation
	  $$p(x_i \mid \mathcal{D}) = \sum_{x_{-i}} p(x_1, \ldots, x_N \mid \mathcal{D})$$
		- 여기서 $x_{-i}$는 $x_i$를 제외한 모든 변수:
		  $$x_{-i} = (x_1, \ldots, x_{i-1}, x_{i+1}, \ldots, x_N)$$

<br>

- Naive Approach
	- 위 작업을 직접 계산하려면 지수적인 시간 복잡도가 필요: $O(L^{N-1})$
		- $L$: 각 변수의 가능한 값의 수.
		- $N$: 변수의 개수.

<br><br>

## Marginalization via Factorization
![[Pasted image 20241208000850.png]]

- [[Factor Graph|Factorization]]
	- 다섯 개 변수 $(x_1, x_2, x_3, x_4, x_5)$의 결합 확률이 아래와 같이 팩터화됨:
	  $$p(x_1, \ldots, x_5) = f_a(x_1, x_2) f_b(x_2, x_3) f_c(x_3, x_4) f_d(x_4, x_5)$$

<br>

- Marginal Probability
	$$\begin{align*}
	p(x_1)&=\sum\limits_{x_2}\sum\limits_{x_3}\sum\limits_{x_4}\sum\limits_{x_5}f_a(x_1, x_2)f_b(x_2, x_3)f_c(x_3, x_4)f_d(x_4, x_5)\\\\
	&=\underbrace{\sum\limits_{x_2}f_a(x_1, x_2)\sum\limits_{x_3}f_b(x_2, x_3)\sum\limits_{x_4}f_c(x_3, x_4)\sum\limits_{x_5}f_d(x_4, x_5)}_{\textcolor{red}{\mu_{a\rightarrow1}(x_1)}=\sum\limits_{x_2}f_a(x_1, x_2)\textcolor{red}{\mu_{b\to 2}(x_2)}}\\\\\\
	p(x_2)&=\underbrace{\left(\sum\limits_{x_1}f_a(x_1, x_2)\right)}_{\textcolor{blue}{\mu_{a\rightarrow2}(x_2)}}\underbrace{\left(\sum\limits_{x_3}f_b(x_2, x_3)\sum\limits_{x_4}f_c(x_3, x_4)\sum\limits_{x_5}f_d(x_4, x_5)\right)}_{\textcolor{red}{\mu_{b\rightarrow2}(x_2)}=\sum\limits_{x_3}f_b(x_2, x_3)\textcolor{red}{\mu_{c\to 3}(x_3)} }\\\\\\
	p(x_3) &= \underbrace{\left( \sum_{x_2} f_b(x_2, x_3) \textcolor{blue}{\mu_{a \to 2}(x_2)} \right)}_{\textcolor{blue}{\mu_{b\rightarrow3}(x_3)}} \underbrace{\left( \sum_{x_4} f_c(x_3, x_4) \sum_{x_5} f_d(x_4, x_5) \right)}_{\textcolor{red}{\mu_{c\rightarrow3}(x_3)}=\sum\limits_{x_4}f_c(x_3, x_4)\textcolor{red}{\mu_{d\to 4}(x_4)}}\\\\\\
	p(x_4) &= \underbrace{\left( \sum_{x_3} f_c(x_3, x_4) \textcolor{blue}{\mu_{b \to 3}(x_3)} \right)}_{\textcolor{blue}{\mu_{c\to 4}(x_4)}} \underbrace{\left( \sum_{x_5} f_d(x_4, x_5) \right)}_\textcolor{red}{\mu_{d\to 4}(x_4)}\\\\\\
	p(x_5) &= \underbrace{\left( \sum_{x_4} f_d(x_4, x_5) \textcolor{blue}{\mu_{c \to 4}(x_4)} \right)}_{\textcolor{blue}{\mu_{d\to 5}(x_5)}}
	\end{align*}$$

- Message Passing
	$$\begin{align*}
	p(x_i) &= \textcolor{blue}{\mu^-_i(x_i)} \cdot \textcolor{red}{\mu^+_i(x_i)}\\\\\\
	\text{Forward pass}\quad\textcolor{blue}{\mu^-_i(x_i)} &= \sum_{x_{i-1}} f_{i-1}(x_{i-1}, x_i) \textcolor{blue}{\mu^-_{i-1}(x_{i-1})}\\\\
	\text{Backward pass}\quad\textcolor{red}{\mu^+_i(x_i)} &= \sum_{x_{i+1}} f_i(x_i, x_{i+1}) \textcolor{red}{\mu^+_{i+1}(x_{i+1}})
	\end{align*}$$
	$$\mu_1^-(x_1)\overset{\text{def}}{=}1,\quad\mu_N^+(x_N)\overset{\text{def}}{=1}$$

<br>

- Advantage
	- 메시지 전달을 통해 지수적 시간 복잡도 $O(L^{N-1})$가 다항식 시간 복잡도 $O((N-1) \cdot L^2)$로 줄어듦.

<br><br>

# Sum-Product Belief Propagation (BP)
![[Pasted image 20241208005831.png|+grid]]![[Pasted image 20241208005842.png|+grid]]

- **Definition**
	- 그래프 구조에서 marginal probability를 계산하기 위해 사용되는 메시지 전달 알고리즘
	- 변수 간의 직접적인 관계 대신, 간접적인 계산으로 전체 구조의 확률 분포를 계산
	- 메시지 전달은 리프 노드에서 시작하여 점진적으로 중심 노드로 모아지는 방식

<br>

- **Principles**
	- $\partial(a)$: 그래프에서 노드 $a$와 직접 연결된 이웃 노드(neighbors)의 집합
	- $\backslash\{a\}$: 집합에서 특정 원소 $a$를 제외하는 연산자
	- Definition of Message
		- From **Factor node $f_u$** to **Variable node $x_i$**
		  $$\textcolor{red}{\mu_{u \to i}(x_i)} \overset{\text{def}}{=} \underbrace{\textcolor{green}{\sum_{x_{\partial u \backslash \{i\}}} f_u(x_{\partial u})}}_{\text{Marginal Probability}} \textcolor{blue}{\prod_{j \in \partial u \setminus \{i\}} \nu_{j \to u}(x_j)}$$

		- From **Variable node $x_i$** to **Factor node $f_u$**
		  $$\textcolor{blue}{\nu_{i \to u}(x_i)} \overset{\text{def}}{=} \textcolor{red}{\prod_{v \in \partial i \setminus \{u\}} \mu_{v \to i}(x_i)}$$
	- Marginal Probability
	  $$p(x_i) = \prod_{v \in \partial i} \mu_{v \to i}(x_i)$$

<br>

- Advantage
	- 트리 구조에서는 모든 메시지가 독립적으로 계산되므로 병렬 처리 가능.
	- 계산 복잡도를 줄여, 전통적인 마지널라이제이션 방식의 $O(L^{N-1})$에서 $O(N \cdot L^2)$로 개선.

<br><br>

## Loopy Sum-Product BP
- **Definition**
	- Loop를 포함하는 그래프에서 marginal probability를 계산하기 위한 메시지 전달 알고리즘
	- 트리 구조에서 사용하는 Sum-Product BP 알고리즘의 확장
	- 루프가 존재하는 그래프에서 반복적으로 메시지 전달을 통해 근사 추론을 수행

<br>

- **Algorithm**
	1. Initialization
		- 모든 간선(edge)에 메시지 값 $\mu^{(0)}$와 $\nu^{(0)}$를 초기화.
		- 초기 값은 보통 **1**로 설정하거나, 무작위 값으로 설정 가능.
	2. Iterative Update
		- 메시지를 계속해서 업데이트하여 정보를 개선<br><br>
		- Factor ▶ Variable
		  $$\mu_{u \to i}^{(k+1)}(x_i) \propto \sum_{x_{\partial u \setminus \{i\}}} f_u(x_{\partial u}) \prod_{j \in \partial u \setminus \{i\}} \nu_{j \to u}^{(k)}(x_j)$$
		- Variable ▶ Factor
			$$\nu_{i \to u}^{(k)}(x_i) \propto \prod_{v \in \partial i \setminus \{u\}} \mu_{v \to i}^{(k)}(x_i)$$
	3. Belief Calculation
		- 각 변수 $x_i$의 신뢰값(belief)을 근사적으로 계산:
		  $$b_i^{(k)}(x_i) \propto \prod_{v \in \partial i} \mu_{v \to i}^{(k)}(x_i)$$
		- 주변 노드에서 전달된 메시지들을 곱하여 marginal probability를 추정
	4. Iteration
		- 위 과정을 정해진 횟수 $k$만큼 반복하거나, 변화량이 작아질 때까지 계속 실행
