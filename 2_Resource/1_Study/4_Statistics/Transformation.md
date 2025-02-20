---
date: 2024-05-23, 19:12
status: Permanent
tags:
  - Study/Statistics
aliases:
  - 확률변수의 변환
keywords:
  - CDF Technique
  - Jacobian Technique
related notes: 
reference: 
author: 
url:
---
# 확률변수의 변환 (Transformation)

- ==[[Random Variables|확률 변수]] $X$ 의 분포를 알고 있을 때 $X$ 와 연관된 확률변수 $Y=g(X)$ 의 분포를 구할 수 있다는 개념==

---
## [[Discrete RV|이산확률변수]]의 변환

- $X$: Discrete RV with space $D_X$, then
- $Y$: Discrete RV with space $D_Y=\{g(x):x\in D_X\}$
<br>

- ==$g(\cdot)$ 가 1-1 대응 함수인 경우==
  >$$\begin{align}P_Y(y)=P(Y=y)&=P(g(X)=y)\\\\&=P(X=g^{-1}(y))\\\\&=P_X(g^{-1}(y))\end{align}$$
	
	- 즉, ==$Y=g(X)$ 를 안다면 역함수 $g^{-1}(Y)=X$ 를 구하여 기존 확률변수의 PMF 에 대입하여 변환==할 수 있음

- ==$g(\cdot)$ 가 1-1 대응 함수가 아닌 경우==
	- 각 이산적인 값에 따라 일일이 PMF 를 구해줘야 함
---
## [[Continuous RV|연속확률변수]]의 변환

- $X$: Continuous RV with PDF $f_X(x)$ and $S_X$
- $Y=g(X)$, ==$g(\cdot)$: 1-1 / differentiable function==
<br>
---
### CDF Technique

- $Y$ 의 CDF $F_Y$ 를 구하고, ==CDF 의 미분은 PDF== 임을 이용하여 $Y$ 의 PDF $f_Y$ 를 구하는 기법

>$$\begin{align}F_Y(y)=P(Y\le y)&=P(g(x)\le y)\\\\&=P(X\le g^{-1}(y))=F_X(g^{-1}(y))\\\\\\f_Y(y)&=\frac{d}{dy}F_X(g^{-1}(y))\end{align}$$

---
### Jacobian Technique

- ==자코비안 행렬 ([[Jacobian Matrix]]) 의 행렬식 ([[Determinant]])== 을 이용하여 새로운 확률변수 $Y$ 의 PDF 를 구하는 기법

>$$\begin{align}F_Y(y)=P(Y\le y)&=P(g(X)\le y)\\\\&=P(X\le g^{-1}(y))=F_X(g^{-1}(y))\\\\\\f_Y(y)=\frac{d}{dy}F_X(g^{-1}(y))&=f_X(g^{-1}(y)) \left|\frac{dx}{dy}\right|
>\end{align}$$

