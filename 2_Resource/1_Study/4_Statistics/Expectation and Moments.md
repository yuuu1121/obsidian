---
date: 2024-05-23, 20:08
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases:
  - 기댓값
keywords: 
related notes: 
reference:
  - "[[Random Variables|RV]]"
author: 
url:
---
# Expectation of RV

- 어떤 확률 과정을 무한히 반복했을 때 얻을 수 있는 값의 ==평균으로서 기대할 수 있는 값==
	- 확률변수의 **중심 경향**

>$$E(X)=\left\{\begin{align}&\sum\limits_ix_iP(X=x_i)&\quad\text{Discrete}\\\\&\int^{\infty}_{-\infty}xf(X=x)\cdot dx&\quad\text{Continuous}\end{align}\right.$$

>[!seealso]
>Q: **평균 (Average)** 와 **기댓값 (Expectation)** 은 같을까?<br>
>A: ==같을수도 있고==, ==다를수도 있다==.

<br>

## Expectation Properties
>Consider random variables $X$, $Y$ and constant $c$

1. $\mathbb{E}[c]=c$
2. $\mathbb{E}[cX]=c \mathbb{E}[x]$
3. $\mathbb{E}[\mathbb{E}[X]]=\mathbb{E}[X]$
4. $\mathbb{E}[X+Y]=\mathbb{E}[X]+\mathbb{E}[Y]$
5. $\mathbb{E}[[Independence|XY]]
   if not, then $\mathbb{E}[XY]\ne \mathbb{E}[X]\mathbb{E}[Y]$

<br><br>

# Moments of RV
>$$E(X^k)=\left\{\begin{align}&\sum\limits_ix_i^kP(X=x_i)&\quad\text{Discrete}\\\\&\int^{\infty}_{-\infty}x^kf(X=x)\cdot dx&\quad\text{Continuous}\end{align}\right.$$

- Mean (a.k.a. the first moment, average, expected value)
$$\mu_x:=\mathbb{E}[X]=\sum\limits_i x_iP(X=x_i)$$
- Variance (a.k.a. the second central moment)
$$\sigma_x^2=\mathbb{E}\left[(X-\mu_x)^2\right]=\mathbb{E}\left[X^2\right]-\mu^2_x$$

```ad-tip
title: Properties of Variance
collapse: true
1. $Var(c)=0$
2. $Var(cX)=c^2Var(X)$
3. $Var(X+Y)=Var(X)+Var(Y)$
4. $Var(XY)=Var(X)Var(Y)+\mathbb{E}[X]^2Var(X)+\mathbb{E}[Y]^2Var(Y)$
```

^zw2g48
- Covariance (a measure of correlation)
  $$cov(X, Y)=\mathbb{E}[(X-\mathbb{E}[X])(Y-\mathbb{E}[Y])]$$
	- where if $X$ and $Y$ are independent, $cov(X, Y)=0$
