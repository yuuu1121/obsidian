---
date: 2024-05-06, 17:34
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases:
  - RV
  - 확률 변수
keywords:
  - 확률 변수
related notes:
  - "[[Definition of Probability Space]]"
reference: 
author: 
url:
---
# 확률 변수 (Random Variables)
- 확률 실험 (Probability experiment)을 했을 때, ==표본공간 (Sample space, $\Omega$)에 속한 원소 ($\omega$) 를 실수값 ($\mathbb{R}$)로 바꾸는 과정==
	- 즉, ==표본공간에서의 각 원소 $\omega$ 에 오직 하나의 실수 $X(\omega)=x$ 를 대응시키는 함수==
	  >$$X: \omega\rightarrow\mathbb{R},\quad \omega\in \Omega$$

- 확률변수의 공간 $D$
	- ==$X(\omega)=x$ 를 만족하는 $x$ 의 집합==
	  >$$D=\{x:X(\omega)=x, \omega\in \Omega\}$$
	  
	- ==$D$ 가 가산형 집합 (Countable Set)== 이면 **이산확률변수** ([[Discrete RV]])
	  ==$D$ 가 실수의 구간 (Interval of Real Numbers)== 이면 **연속확률변수** ([[Continuous RV]])

- Support
	- Random variable의 범위

```ad-example
- 동전을 2번 던졌을 때 앞면 (H) 혹은 뒷면 (T) 조합을 확인하는 확률 실험<br>
표본 공간 $S$: $\{HH, HT, TH, TT\}$<br>
  확률 변수 $X$: 앞 면이 나온 횟수 $X({HH, HT, TH, TT})={2, 1, 1, 0}$

>$$\begin{matrix}P(0)={1\over 4},\quad P(1)={1\over 2}, \quad P(2)={1\over 4}\\\\
P(x\le1)=P(\{HT, TH, TT\})={3\over4}\end{matrix}$$
```