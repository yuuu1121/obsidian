---
date: 2024-09-15
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes:
  - "[[Combination]]"
reference: 
author: 
url: 
dg-publish: false
---
# Bernoulli Distribution
- 베르누이 분포($\text{r.v. }X\sim Ber(p)$)는 **성공** 또는 **실패**와 같이 두 가지 결과만 존재하는 실험에서 사용되는 확률 분포
	- 성공 확률 $p$와 실패 확률 $1-p$로 정의
	- $p$는 $[0, 1]$사이 값
	- Support: $X\in \{0, 1\}$


$$P(X=x)=p^x(1-p)^{1-x}=
\begin{cases}
p&\text{if }x=1\\\\
1-p&\text{if }x=0
\end{cases}$$

- Mean: $\mathbb{E}[X]=p$
- Variance: $Var[X]=p(1-p)$

>[!tip]- Proof
>- Mean
>
> $$\begin{align*}
> \mathbb{E}[X]&=1\cdot P(X=1)+0\cdot P(X=0)\\\\
> &=1\cdot p+0\cdot (1-p)\\\\
> &=p
> \end{align*}$$
>
>- Variance
> $$\begin{align*}
> \sigma_X^2&=\mathbb{E}[X^2]-\left(\mathbb{E}[X]\right)^2\\\\
> &=\mathbb{E}[X]-(\mathbb{E}[X])^2\\\\
> &=p-p^2=p(1-p)
> \end{align*}$$

<br>

# Binomial Distribution
- 이항 분포(Binomial distribution)는 독립적인 베르누이 시행을 $n$번 반복할 때, 성공 횟수를 나타내는 확률 분포
	- 각 시행에서 성공할 확률은 $p$ 실패할 확률은 $1-p$
	- $\text{r.v. }X\sim Bin(p, n)$ where $p\in[0, 1]$ and $n\in \mathbb{N}$
	- Support: $X\in \left\{0, 1, \dots, n\right\}$
	$$P(X=x)={n\choose x}p^x(1-p)^{n-x}\qquad \text{where }{n\choose x}={n! \over {x!(n-x)!}}$$
	
  >$P(X=x)$ 는 독립적인 베르누이 시행을 $n$번 반복할 때, 정확히 $x$ 번 성공할 확률

- Mean: $\mathbb{E}[X]=np$
- Variance: $Var[X]=np(1-p)$

>[!info] Law of Large Number
>- Binomial R.V.는 $n$개의 독립적인 베르누이 시행의 결과(성공 횟수)의 합으로 대수의 법칙에 의해 시행 횟수 $n$이 증가할 수록 표본 평균은 기대값 $p$에 수렴하며, 분산은 0에 수렴함
>
>$$E\left[\frac{X}{n}\right] = p \quad \text{and} \quad \text{Var}\left[\frac{X}{n}\right] = \frac{p(1 - p)}{n} \to 0 \quad \text{as} \quad n \to \infty$$

<br>

# Beta Distribution
- 베타 분포(Beta distribution)는 두 개의 양수 매개변수 $\alpha$와 $\beta$를 가지는 확률분포
- $[0, 1]$ 사이 값 확률을 나타내는 분포
	- 특히, 베르누이 분포의 성공 확률 $p$를 모델링하는 데 자주 사용됨
	- $\text{r.v.} X \sim Beta(\alpha, \beta)$ where $\alpha\in (0, \infty)$ and $\beta\in (0, \infty)$
	- Support: $X\in[0, 1]$
	
	$$\begin{align*}
	P(X=x)&={x^{\alpha-1}(1-x)^{\beta-1}\over{B(\alpha,\beta)}}\\\\
	&\propto x^{\alpha-1}(1-x)^{\beta-1}
	\end{align*}$$
	
	- $\alpha$와 $\beta$: 성공과 실패의 정도를 나타내는 매개변수
	- $B(\alpha, \beta)$: 베타함수로, 분포를 정규화하는 상수
	
- Mean: $\mathbb{E}[x]={\alpha\over{\alpha+\beta}}$
- Variance: $Var[X]={\alpha \beta\over {(\alpha+\beta)^2(\alpha+\beta+1)}}$

![[Pasted image 20240922160819.png]]

>[!example] Tossing Coins
>- 동전 던지기 실험에서, 관찰된 결과는 "HHTHH"
>
>1. 빈도주의 추정
>	- 관찰된 결과만 가지고 계산하는 방식
>	- 5번 중 4번이 앞면이 나왔으므로, $p=4/5=0.8$로 추정
>2. [[Bayesian Inference|베이지안 추정]]
>	- 사전 정보를 바탕으로 확률을 예측하는 방식
>	- 성공확률 $p$가 1/2 근처일 것이라는 가정(사전적 경험)을 바탕으로 베타 분포로 모델링하면 $p\sim Beta(\alpha=2, \beta=2)$로 표현할 수 있음
>		- $\alpha$: 성공(앞면)의 횟수를 모델링
>		- $\beta$: 실패(뒷면)의 횟수를 모델링
>	- 즉, 사전적 경험에 의해 성공 횟수 $p$를 $p\sim Beta(\alpha=2, \beta=2)$로 모델링할 수 있으며, 이는 $p=0.5$일 확률이 $P(p=0.5)=1.5$로 가장 높다는 것을 의미

<br>

# Gaussian Distribution (Normal Distribution)

- 가우시안 분포는 평균 $\mu$와 분산 $\sigma^2$ 두 개의 파라미터로 정의되는 연속 확률 변수에서 가장 중요한 분포 중 하나
	- 자연 현상이나 데이터 분석에서 자주 나타나며, 수학적 성질이 매우 편리
	- $\text{r.v. }X\sim \mathcal{N}(\mu, \sigma^2)$
	- Support: $X\in \mathbb{R}$

$$p(X=x)={1\over{\sqrt{2\pi \sigma^2}}}\exp{\left(-{1\over2\sigma^2}(x-\mu)^2\right)}$$

- Mean: $\mathbb{E}[X]=\mu$
- Variance: $Var[X]=\sigma^2$

<br>

- 가우시안 분포는 머신러닝과 통계학에서 널리 사용됨
	- 수학적으로 다루기 쉬우며, 다양한 계산에서 사용
	- 데이터의 노이즈나 불확실성을 모델링하는 데 적합
		- 예를들어, 가우시안 잡음(Gaussian Noise)은 측정 오차나 센서의 불확실성을 모델링하는데 사용
	- 중앙 극한 정리에 의해 많은 실제 데이터가 가우시안 분포에 가까운 형태를 가짐

<br>

## Standard Normal Distribution
- 표준 정규 분포는 가우시안 분포에서 $\mu=0, \sigma^2=1$일 때로 정의되며, $Z$-분포라고도 불림

$$P(Z=z)={1\over\sqrt{2\pi}}\exp{\left(-{z^2\over 2}\right)}$$
- 표준 정규 분포는 다양한 문제에서 데이터를 표준화(standardization)할 때 사용
- 데이터 $X$를 표준화하면 다음과 같음

$$Z={X-\mu\over \sigma}$$

<br>

## Properties of Gaussian Distribution
1. 대칭성
	- 가우시안 분포는 평균을 기준으로 완전히 대칭적
	- 많은 자연 현상에서 데이터가 평균 주위로 대칭적으로 분포하는 패턴을 반영
2. Empirical Rule (68-95-99.7 규칙)
	- 정규 분포에서 데이터가 어떻게 분포하는지에 대한 직관을 제공하는 규칙
	- 데이터가 얼마나 평균 주변에 집중되어 있는지, 분포가 얼마나 넓게 퍼져 있는지에 대한 이해를 도움
		- 데이터의 약 68%가 평균에서 $\pm1$ [[표준 편차]] 내에 위치
		- 약 95%는 평균에서 $\pm2$ 표준 편차 내에 위치
		- 약 99.7%는 평균에서 $\pm3$ 표준 편차 내에 위치
3. 최대 엔트로피 분포
	- 가우시안 분포는 주어진 제약 조건(평균과 분산) 하에서 가장 불확실성이 큰 분포
		- 즉, 정보가 가장 없을 때 가우시안 분포 사용
	- 이는 가우시안 분포가 불확실성을 최대로 반영하는 분포라는 의미에서 최적의 선택일 수 있다는 것을 의미

<br>

## Central Limit Theorem, CLT
- 많은 독립적이고 동일한 분포를 따르는 확률 변수들의 합은 그 원래의 분포와 관계없이 가우시안 분포에 수렴
	- 즉, 샘플의 크기가 커질수록, 그 샘플들의 평균은 가우시안 분포에 가까워짐

$$\sqrt{n}\left(\bar{X}_n-\mu\right)=\sqrt{n}\left( \frac{1}{n} \sum_{i=1}^{n} X_i - \mu \right) \xrightarrow{\text{D}} N(0, \sigma^2)\quad \text{as}\quad n\rightarrow \infty$$

- $X_1, X_2, \cdots, X_n$: 독립적이고 동일한 분포를 따르는 확률 변수
- $\bar{X}_n={1\over n}\sum\limits_{i=1}^nX_i$: 표본 평균
- $\mu$: 모집단의 참평균
- $\sigma^2$: 모집단의 참분산

- Standardized CLT
  $${\bar{X}_n-\mu\over{\sigma\over\sqrt{n}}} \xrightarrow{\text{D}} N(0,1)\quad \text{as}\quad n\rightarrow \infty$$

>[!example] 대한민국 인구의 평균 나이 추정
>- $X$는 사람의 나이를 나타내는 확률변수라고 가정할 때, 대략적으로 다음과 같음
>	- $X\in \left\{1,2, \cdots, 100\right\}$
>	- $\bar{X}_n$: $n$명의 사람을 샘플링했을 때 나이의 평균
>	- $\mu$: 대한민국 전체 인구의 참된 평균 나이
>		- 일반적으로 알 수 없는 값이며, 샘플링을 통해 추정해야 함
>- 예를들어 $\bar{X}_n=50$이라는 표본 평균이 나왔고, $n$이 충분히 크다면 실제 모집단 평균 $\mu$가 50일 확률이 가장 높음

<br>

## Multivariate Gaussian Distribution
- 다변량 가우시안 분포는 여러 개의 확률 변수를 동시에 설명하는 분포로, 평균 벡터 $\mu$와 공분산 행렬 $\Sigma$로 정의

$$P(\mathbf{X}|\boldsymbol{\mu}, \Sigma)={1\over (2\pi)^{D/2}|\Sigma|^{1/2}}\exp{\left(-{1\over2}(x-\mu)^T \Sigma ^{-1}(x-\boldsymbol{\mu})\right)}$$

- $\mathbf{X}$: $D$-차원의 랜덤 벡터([[Random Vector and Covariance|random vector]])
- $\boldsymbol{\mu}$: $D$-차원의 평균 벡터
- $\Sigma$: $D\times D$ 크기의 공분산 행렬로, 각 변수 간의 관계를 설명
	- 대각선 요소: 각 변수의 분산
	- 비대각선 요소: 두 변수 간의 공분산을 나타내며, 두 변수가 얼마나 상관관계가 있는지 보여줌