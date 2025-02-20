---
date: 2024-12-09
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
# Convex Function
- **Definition**
	- 함수 $f: C \to \mathbb{R}$가 convex하려면 다음 조건을 만족
	  $$f(\lambda x + (1-\lambda) y) \leq \lambda f(x) + (1-\lambda) f(y), \quad \forall x, y \in C, \, \forall \lambda \in [0, 1]$$
	- 즉, $f$의 그래프가 두 점 $(x, f(x))$와 $(y, f(y))$를 잇는 선분 아래에 위치.

<br><br>

# Jensen's Inequality
- **Definition**
	- Convex function과 확률 변수의 기대값 사이의 관계를 나타내는 부등식

<br>

- **Key Concepts**
	- $f(x)$가 **convex**라면
	  $$\mathbb{E}[f(X)] \geq f(\mathbb{E}[X])$$
	- $f(x)$가 **concave**라면
	  $$\mathbb{E}[f(X)] \leq f(\mathbb{E}[X])$$
