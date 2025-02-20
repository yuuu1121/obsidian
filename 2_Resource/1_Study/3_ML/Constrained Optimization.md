---
date: 2024-10-17
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
# Constrained Optimization
- **Definition**: 
	- 주어진 제약 조건을 만족하면서 목적 함수를 최소화하거나 최대화하는 문제를 해결하는 것.

<br>

###### Key Components

1. **Objective Function**
   - 최적화하려는 대상 (예: 비용, 손실 함수 등).

2. **Constraints**
   - 목적 함수를 최적화하는 동시에 반드시 만족해야 하는 조건들.
   - **Types**:
     - **등식 제약 조건 (Equality Constraint)**: $h(x) = 0$
     - **부등식 제약 조건 (Inequality Constraint)**: $g(x) \leq 0$

<br><br>

## Problem Definition
- **Primal Problem**:
  - **Definition**: 
    - 주어진 목적 함수와 제약 조건을 그대로 사용하여 최적화를 수행하는 원래의 문제. 
    - 즉, 제약을 만족하면서 해를 찾는 문제.
      >"제약을 만족시키면서 최적해를 찾는 문제."
      
  - **Goal**: 
    - 제약 조건을 만족하면서, 주어진 목적 함수를 최소화(또는 최대화)하는 최적의 해를 구하는 것.
  - **Characteristic**: 
    - 제약 조건이 복잡하거나 고차원 문제일 경우, Primal 문제는 직접 해결하기 어려울 수 있음. 

<br>


- **Dual Problem**:
  - **Definition**: 
    - Primal 문제의 제약 조건을 변형하여 정의된 문제. 
      >"제약을 위반하지 않으면서 최적화 목표를 달성할 수 있는 가장 효율적인 방법을 찾는 것."
      
  - **Goal**: 
    - Primal 문제의 제약 조건을 다른 방식으로 표현하여 문제를 단순화하거나 변수를 줄임으로써 해결하는 것.
  - **Characteristic**: 
    - Primal 문제에 비해 더 간단하거나 효율적으로 해결할 수 있는 경우가 많음. 
    - Dual 문제의 해는 Primal 문제의 해에 대한 하한값 또는 상한값을 제공함.
  - **Duality**: 
    - 강한 이중성 조건이 성립할 경우, Dual 문제에서 얻은 해는 Primal 문제의 해와 동일함.

<br>


- **Primal 문제와 Dual 문제의 관계**:
	- Primal 문제와 Dual 문제는 같은 본질을 가지지만 서로 다른 방식으로 최적화를 접근함.
	- **약한 이중성 (Weak Duality)**: 
		- Dual 문제의 해는 Primal 문제의 해보다 나쁘지 않다 (작거나 같다).
	- **강한 이중성 (Strong Duality)**: 
		- Primal 문제와 Dual 문제의 해가 동일할 때 성립함.

<br><br>

### Lagrangian Dual Problem
- **Definition**: 
	- 제약이 있는 Primal 문제를 풀기 위해 제약 조건을 목적 함수에 포함시키는 방식. 
	- 이를 통해 문제를 Dual 문제로 변환함으로써 Primal 문제를 간접적으로 해결 가능.

<br>

#### Lagrangian Function
- **Definition**
	- Primal 문제의 목적 함수와 제약 조건을 결합하여 정의된 함수로, 이를 통해 Dual 문제로 변환할 수 있음.

<br>

- **Primal Problem**:
	- **Objective function**: $\min J(w)$
	- **Constraints**:
		- **Inequality constraint**: $g_i(w) \leq 0$, $i = 1, ..., M$
		- **Equality constraint**: $h_j(w) = 0$, $j = 1, ..., L$

- **Primal Lagrangian Function**:
	- $L(w, \nu, \lambda) := J(w) + \sum_{i=1}^{M} \nu_i g_i(w) + \sum_{j=1}^{L} \lambda_j h_j(w)$
		- 여기서 $\nu_i$는 부등식 제약 조건을 다루며 $\nu_i \geq 0$을 만족해야 하고, $\lambda_j$는 등식 제약 조건을 다루며 부호에 제한이 없음.

<br>

#### Lagrangian Dual Problem
- **Lagrangian Dual Function**:
	- Primal 문제의 라그랑지안 함수에서 $w$에 대한 최소값으로 정의된 함수:
	$$
	G(\nu, \lambda) = \inf_{w \in W} L(w, \nu, \lambda) := J(w) + \sum_{i=1}^{M} \nu_i g_i(w) + \sum_{j=1}^{L} \lambda_j h_j(w)
	$$
- **Lagrangian Dual Problem**:
	- Lagrangian dual function을 최대화하는 문제로, 다음과 같은 형태로 표현됨:
		- **Objective function**: $\max G(\nu, \lambda)$
		- **Constraints**: $\nu_i \geq 0$, $i = 1, ..., M$
	- 이 방식은 제약 조건의 위반을 강조하면서 Primal 문제를 간접적으로 해결하는 방식임.

<br><br>

### Duality
- **Definition**:
	- 하나의 최적화 문제(Primal 문제)를 Dual 문제로 변환하는 개념.
	- Primal 문제와 Dual 문제는 다른 방식으로 동일한 본질의 최적화를 다루며, 두 문제 간의 관계를 통해 최적해를 효율적으로 찾는 것을 목표로 함.

<br>

#### Weak Duality
- **Definition**: 
	- Primal 문제와 Dual 문제에서 구한 해를 비교할 수 있음.
- **Condition**: 
	- Dual 문제의 해가 Primal 문제의 해보다 항상 작거나 같음.
	  >$$ J(w^*) \geq G(\nu^*, \lambda^*) $$

- **Conclusion**: 
	- Dual 문제의 해는 Primal 문제보다 나쁜 해를 제공하지 않음을 보장함.
		- Primal 문제가 최소화 문제일 때: 
		  Dual 문제의 해는 Primal 문제에서 구할 수 있는 최적해보다 작거나 같음.
		- Primal 문제가 최대화 문제일 때: 
		  Dual 문제의 해는 Primal 문제에서 구할 수 있는 최적해보다 크거나 같음.
	- 단, Primal 문제와 Dual 문제 간에 해의 불일치가 있을 수 있음.

<br>

#### Strong Duality
- **Definition**: 
	- Primal 문제와 Dual 문제의 해가 완전히 동일할 때 성립.
- **Condition**:
	- **KKT 조건**을 만족해야 하며, 추가적으로 **Slater 조건**과 같은 조건을 충족해야 강한 이중성이 성립.
		- **Slater 조건**: 제약 조건이 엄격히 충족되는 내점(Strictly feasible point)이 존재하면 강한 이중성이 성립할 수 있음. 특히, convex 문제에서 이 조건이 충족되면 강한 이중성이 보장됨.
- **Conclusion**: 
	- Primal 문제와 Dual 문제 모두 같은 최적해에 도달하며, 두 문제의 해가 동일함을 의미.
	  >$$ J(w^*) = G(\nu^*, \lambda^*) $$

<br>

#### Karush-Kuhn-Tucker(KKT) Necessary Condition
- **Definition**: 
	- 제약이 있는 최적화 문제에서 최적해를 찾기 위한 필수 조건.
	- Primal 문제와 Dual 문제의 해가 동일하게 되는 강한 이중성이 성립하기 위한 필수 조건.
	- KKT 조건을 만족하는 해는 Primal 문제의 최적해를 의미

###### Key Components
1. **Optimality (최적성)**:
   - 목적함수 $J(w)$에 제약 조건을 포함한 라그랑지안 함수 $L(w, \nu, \lambda)$의 최적 조건을 의미:
     $$
     \nabla_w L = \nabla J(w) + \sum_{i=1}^{M} \nu_i \nabla g_i(w) + \sum_{j=1}^{L} \lambda_j \nabla h_j(w) = 0
     $$

2. **Feasibility (타당성)**:
   - 주어진 제약 조건을 만족하는 해:
     - $g_i(w) \leq 0, \forall i = 1, ..., M$
     - $h_j(w) = 0, \forall j = 1, ..., L$
   - Primal 문제의 제약 조건을 Dual problem에서도 만족해야 함.

1. **Complementary Slackness (상보성 여유 조건)**:
	- Definition
		- 부등식 제약 조건과 Lagrangian multiplier $\nu_i$ 간의 관계를 나타내는 조건
		- 제약 조건이 얼마나 강하게 적용되는지에 따라 Lagrangian multiplier $\nu_i$가 결정됨을 나타냄
		- [[Activation of Constraint|제약이 활성화되었는지]] 또는 비활성화되었는지를 결정하는 기준
	- Condition
	  $$\nu_i g_i(w) = 0$$
		1. $g_i(w)=0$
			- 제약 조건이 정확히 경계에 있을 때, $\nu_i > 0$으로 Lagrangian multiplier는 0이 아닌 값을 가짐.
			- 부등식 제약 조건이 정확히 제약 경계에 있을 때만 Lagrangian multiplier $\nu_i$가 0이 아닌 값을 가질 수 있음을 나타냄.
			- 해당 데이터 포인트는 결정 경계에 위치하고, **[[Support Vector Machine#^woow1r|Support Vector]]**로 불림.
		2. $g_i(w) < 0$
			- 제약 조건이 엄격히 만족될 때, $\nu_i = 0$이 되어야 함.
			- 이 경우, 해당 데이터는 **Support Vector가 아님**.

<br>

###### Relationship Between KKT Conditions and Duality
- **Weak Duality**:
   - Dual 문제의 해가 Primal 문제에서 얻는 최적해의 하한값을 제공함을 보장하며, 최적해가 존재하거나 Primal 문제와 동일한 해를 제공하는 것을 보장하지 않음.
   - 즉, 약한 이중성이 성립하기 위해 KKT 조건이 필수적이지 않음.

- **Strong Duality**:
   - Primal 문제와 Dual 문제의 해가 동일할 때 성립하며, 강한 이중성이 성립하기 위해서는 KKT 조건을 필수적으로 만족해야 함.

<br><br>

#### Slater's Sufficient Condition
- **Definition**:
	- Slater 조건은 **강한 이중성**을 보장하기 위한 **충분 조건**으로, Primal 문제가 **Convex(볼록)** 최적화 문제일 때 적용됨.
	- 특히 부등식 제약 조건을 가진 Convex 최적화 문제에서 **강한 이중성**을 성립시키기 위한 중요한 역할을 함.
		- 즉, Slater 조건이 성립하면, KKT 조건을 만족하는 해를 찾을 수 있으며, 이를 통해 강한 이중성이 성립됨.

- **Condition**:
	- Convex 최적화 문제에서 부등식 제약 조건 $g_i(w) \leq 0$가 있을 때, **엄격한 내부점(strict interior point)**이 존재해야 함.
		- 즉, 최소한 하나의 점에서 $g_i(w) < 0$인 경우가 있어야 Slater 조건이 성립함.
		- 이는 Primal 문제의 제약 조건이 **경계(boundary)에 있지 않고**, 내부에서 엄격하게 충족되는 경우를 의미함.

- **Conclusion**:
	- Slater 조건이 성립하면, **강한 이중성**이 성립하여 **Primal 문제**와 **Dual 문제**의 최적해가 **동일**해짐.
	- Convex 최적화 문제에서 Slater 조건을 만족하면, Dual 문제를 풀어서도 Primal 문제의 최적해를 구할 수 있음.
	- 단, Slater 조건이 성립하지 않더라도 일부 상황에서는 강한 이중성이 성립할 수 있음.