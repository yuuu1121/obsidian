---
date: 2024-09-10
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
# Probability Space
- 확률 공간은 다음 세 가지 요소로 구성되어 있음
	- Sample space $\Omega$
	- $\sigma$-field $\mathcal{F}$
	- Probability (measure) $P : \mathcal{F}\mapsto [0, 1]$

<br><br>


## Sample Space and Events
- Sample space $\Omega$
  단일 실행(single execution)에서 나올 수 있는 모든 결과의 집합
	- e.g., two successive coin tosses: $\Omega=\{hh, tt, ht, th\}$
- Event $E$
  Sample space의 부분집합(subset)
	- e.g., $\{hh\}, \{ht, th\}, \dots$

<br><br>


## Field and $\sigma$-Field
### Field $\mathcal{F}$
- 어떤 표본 공간 $\Omega$의 **부분집합들의 모음**으로, 다음 성질들을 만족하는 집합
	- ==공집합과 전체 집합 포함==: $\varnothing\in \mathcal{F}$ and $\Omega\in \mathcal{F}$
	- ==합집합에 대해 [[닫혀 있음]]==: $\forall E_{1}, E_{2}\in \mathcal{F},\qquad E_{1}\cup E_2\in \mathcal{F}$
	- ==교집합에 대해 닫혀 있음==: $\forall E_1, E_2\in \mathcal{F},\qquad E_1\cap E_2\in \mathcal{F}$
	- ==여집합에 대해 닫혀 있음==: $\forall E_1, E_2\in \mathcal{F},\qquad \Omega\backslash E\in \mathcal{F}$
- **Field의 특징**
	- 필드는 **유한한 개수**의 사건들에 대해 닫혀 있음
	- 필드는 보통 확률론에서 유한한 사건들의 집합을 다루기 위해 사용

>- $\mathcal{F}\subset2^{\Omega}$ 
>- 멱집합 (Power set, $2^{\Omega}$)
>	- 어떤 집합에 대해 가능한 모든 부분집합들의 집합을 의미
>	- $\Omega$가 n개의 원소를 가지는 유한 집합일 경우 $2^{\Omega}$는 $\Omega$의 모든 부분집합들의 모음이며, 그 개수는 $2^n$ 

<br>

### $\sigma$-Field
- Field의 확장 개념으로, ==**유한한 사건**뿐만 아니라 **무한한 사건**들에 대해서도 닫혀 있는 집합==
- $\sigma$-Field는 주로 연속적인 확률 변수와 관련된 사건들을 다루기 위해 필요
	- 연속 확률 변수가 다루는 사건들은 무한히 많은 경우가 있기 때문에, 이를 처리하기 위해서는 $\sigma$-Field와 같은 구조가 필요

<br>

### Summary

| **필드 (Field)**                       | **σ-Field (시그마 필드)**                      |
| ------------------------------------ | ----------------------------------------- |
| **유한한 사건**들의 합집합과 교집합에 대해 **닫혀 있음**. | **유한 및 무한한 사건**들의 합집합과 교집합에 대해 **닫혀 있음**. |
| 주로 유한한 사건들을 다룰 때 사용됨.                | 무한한 사건이나 연속 확률 변수를 다룰 때 사용됨.              |
| 확률론에서 간단한 경우에 사용됨.                   | ==연속적인 사건이나 복잡한 확률 공간을 다룰 때 필요함==.        |

<br><br>

## Probability Measure $P$
- ==어떤 사건에 확률을 할당==하는 수학적 함수
- ==사건들이 발생할 가능성을 **수량화**==

<br>

### $\sigma$-Field and Probability Measure
- Probability measure는 $\sigma$-Field의 집합들에 대해 확률을 할당하기 때문에 먼저 $\sigma$-Field가 필요
	- 단일 사건(e.g., $P(\{hh\}$) 뿐만 아니라 여러 사건의 합(e.g., $P(\{hh\}\cup\{tt\}$)을 다루기 위해 $\sigma$-Field 사용

<br>

### Definition of Probability Measure
- Probability measure $P$는 $\sigma$-Field $\mathcal{F}$에 속하는 사건들에 확률을 할당하는 함수
	- 즉, $\sigma$-Field 내의 각 사건에 대해 값이 0과 1 사이의 실수인 확률을 부여
#### Properties of Prabability Measure
- $P: \mathcal{F}\mapsto [0, 1]$
	- $P(A)\ge0$ : 사건 $A\in \mathcal{F}$에 대한 확률은 항상 0 이상
	- $P(\varnothing)=0$: 공집합에 대한 확률은 0
	- $P(\Omega)=1$: 전체 표본 공간 $\Omega$의 확률은 항상 1

- 가산 가법성 (Countable Additivity)
	- 서로 Disjoint인 사건들에 대해 합집합의 확률이 각사건의 확률들의 합과 같음
	- 만약 사건들의 모임 $\{A_i\}_{i\in I}$에서 서로 다른 $A_i$와 $A_j$가 교집합이 없을 때($A_i\cap A_j=\varnothing$) 다음이 성립
	  $$P \left(\bigcup_{i\in I}A_i \right)=\sum\limits_{i\in I}P(A_i)$$
