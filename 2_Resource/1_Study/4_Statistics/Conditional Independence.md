---
date: 2024-12-07
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
# Conditional Independence
- **Definition**
	- 세 확률 변수 $X$, $Y$, $Z$에 대해 $Z$가 주어졌을 때 $X$와 $Y$가 서로 독립임을 의미
	  $$X \perp\!\!\!\perp Y \mid Z \iff P(x,y \mid z) = P(x \mid z) P(y \mid z)$$
	- $X$와 $Y$가 $Z$를 조건으로 독립일 때:
		$$p(x \mid y, z) = p(x \mid z) \quad \text{or} \quad p(y \mid z) = 0$$

<br>

- **Properties**
	- $Z$를 알고 있다면, $X$와 $Y$는 서로 독립
	- $Z$는 $X$와 $Y$ 사이의 모든 의존성을 "차단"하는 역할

<br>

## Marginal Independence
- **Definition**
	- 확률 변수 $X$, $Y$에 대해 $X$와 $Y$가 서로 독립임을 의미
	  $$X \perp\!\!\!\perp Y \quad \text{or} \quad X \perp\!\!\!\perp Y \mid \emptyset\iff p(x, y) = p(x)p(y)$$