---
date: 2024-05-03, 19:38
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords:
  - 전체 확률 법칙
  - marginalization
related notes:
  - "[[Conditional Probability]]"
reference: 
author: 
url:
---
## Law of Total Probability (a.k.a. Marginalization)
- **Law of total probability**:
	- **분할된 사건들의 조건부 확률**을 사용하여 **특정 사건의 전체 확률**을 구하는 과정
	- [[marginal probability)](주변 확률(marginal probability|주변 확률(marginal probability)]].md)(e.g., $P(A)$)을 조건부 확률을 통해 구하는 과정으로, 특정 정보나 변수를 고려하지 않고 전체 확률을 구할 수 있게 해줌
- **Marginalization**:
	- ==관심 있는 사건$A$에 대한 [[marginal probability)](주변 확률(marginal probability|주변 확률(marginal probability)]].md) $P(A)$를 구하는 과정==
	- **불필요한 변수를 제거**하고, 사건에 대한 종합적인 확률을 계산할 수 있음
	- 각 변수들의 Marginal probability를 통해 **중요도**를 알 수 있음

<br>


![[drawing240503.excalidraw]]

<center style="font-size: 12; opacity: 0.7">Example of Total Probability</center>

<br>

- 수식:
	- $\{B_i \}_{i=1, \dots, n}$이 $\Omega$의 [[Partition]] 일 때 다음이 성립함

$$P(A)=\sum\limits_{i=1}^nP(A, B_i)=\sum\limits_{i=1}^nP(A|B_i)P(B_i)$$