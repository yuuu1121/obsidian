---
date: 2024-09-22
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Motivation
- 동전 던지기에서 앞면이 나올 확률 $\mu$를 추정하는 문제
	- 만약 동전을 10번 던져 7번 앞면이 나왔다면, $\mu=0.7$로 추정할 수 있음
		- 만약 한 번 던져서 앞면이 나왔다면, $\mu=1$로 추정할 수 있는가?
	- 무관측 상태에서는 사전적 경험(prior)에 의해 $\mu=0.5$로 추정하는 것이 일반적

>[[Bayes' Theorem|확률론적 관점]](Probabilistic perspective)에서 관측된 데이터(observation)을 바탕으로, 사전 확률(prior)과 결합하여 매개변수(parameter)를 추정하는 방법

<br>

# Statistical Model

- 여러 확률 모델 또는 통계적 모델 중에서 관찰된 데이터를 가장 잘 설명하는 모델을 찾는 과정
	- 주어진 데이터를 가장 잘 설명하는 확률 분포
- 데이터를 기반으로 확률 밀도 함수 (PMF 또는 PDF)를 학습하거나 추정

<br>

## Typical Setup
- Problem:
	- 랜덤 변수 $X_1, \cdots, X_n$이 동일한 분포에서 독립적으로 샘플링된 경우
		- 즉, $X_i$는 i.i.d. (독립적이고 동일한 분포를 따름)
	- 통계적 모델의 목표는 랜덤 변수 $X$의 분포를 학습하는 것
		- 예를들어 형제의 수를 조사하는 경우, 각 샘플 $X$는 형제의 수
- Parametric method:
	- 모든 가능한 확률 값들을 학습하지 않고, Single parameter를 통해 데이터를 간단하게 설명하는 모델을 사용
		- 예를 들어, 랜덤 변수 $X$가 Poisson distribution ($X\sim Poisson(\lambda)$)을 따른다고 가정하면, 해당 분포의 Single parameter $\lambda$를 학습하는 방식으로 모델링 할 수 있음

<br>

## Machine Learning
- [[Machine Learning 이란|머신러닝]]은 데이터를 기반으로 패턴을 추출하거나 추론을 수행하는 방법론
- 이때, 통계적 모델을 사용하여 고나측된 데이터를 가장 잘 설명할 수 있은 확률 분포를 찾음

<br>

### Supervised Learning
- 지도 학습은 입력 $x$와 출력 $y$의 샘플 Pair가 주어진 상황에서, 관측된 데이터$\mathcal{D}$를 통해 입력에서 출력으로의 Mapping을 학습하는 과정
	- $\mathcal{D}=\{(x_i, y_i)\}^n_{i=1}$
- 지도 학습에서 확률 모델은 $p(y|x)$의 형태로 표현
	- 즉, 입력 $x$가 주어졌을 때 출력 $y$가 발생할 확률을 모델링
- 또한, 지도 학습에서 확률 모델은 종종 Parametrized model $p(y|x, \theta)$로 표현됨
	- $p(y|x, \theta)$는 파라미터 $\theta$를 이용해 설명하는 확률 모델
	- 여기서 $\theta$는 모델의 파라미터로, 데이터를 통해 학습

>[[Linear Regression|!example]]
>- 선형 회귀에서는 입력 $x$와 출력 $y$ 사이의 관계를 선형 함수 $y=wx+b$로 모델링
>	- 여기서 $w$와 $b$는 학습을 통해 결정되는 파라미터


<br>

### Unsupervised Learning
- 비지도 학습은 출력 $y$ 없이 입력 데이터 $x$만 주어진 상황에서, 입력 데이터의 패턴을 학습하는 과정
	- $\mathcal{D}=\{x_i\}^n_{i=1}$
- 비지도 학습에서 확률 모델은 $p(x)$ 또는 $p(x|\theta)$로 표현

>[!example] Clsutering
>- 군집화와 같은 비지도 학습에서 데이터의 분포를 설명하는 모델을 사용
>	- 예를 들어, 가우시안 혼합 모델(Gaussian Mixture Model, GMM)은 데이터가 여러 개의 가우시안 분포로 이루어졌다고 가정하고 각 분포의 파라미터를 학습하는 방법


<br>

# Density Estimation
- 주어진 유한한 데이터 포인트 $\left\{x_i\right\}^n_{i=1}$ 로 부터 확률 밀도 함수 $p(x)$를 모델링하는 문제

<br>

## Parametric Estimation
- 특정 함수 형태를 가정하고, 해당 함수가 데이터를 가장 잘 설명할 수 있도록 파라미터를 찾는 방법 (i.e., model fitting)
- 주어진 데이터로부터 Statistical model의 파라미터($p(y|x, \theta)$ 혹은 $p(x|\theta)$)를 추정하는 과정

### Formal Definition
- 샘플 $X_1, X_2, \cdots, X_n$은 독립적이고 동일한 분포([[Independent and Identically Distributed|i.i.d.]])의 확률 변수
- 이 통계적 실험에 대한 모델은 $\left(\Omega, (p_\theta)_{\theta\in \Theta}\right)$로 정의
	- $\Omega$: Sample space
	- $(p_\theta)_{\theta\in \Theta}$: A family of [[Various Distributions|statistical model]] on $\Omega$ (e.g., Bernoulli, Gaussian,...)
	- $\Theta\subseteq \mathbb{R}^d$
	  Parameter set 
	  $\theta$는 다변량 변수 일 수 있음 (e.g., Gaussian - $\theta=(\mu, \sigma^2$)
- 모델 설정
	- 모델이 잘 설정되었다고 가정할 경우 $p=p_{\theta^*}$를 만족하는 true parameter $\theta^*$가 존재하며, $\theta^*$에 가까운 추정치 $\hat{\theta}$를 찾는 것이 목표
	- 편향(Bias)과 분산(Variance)으로 추정치의 품질을 평가
		- Bias: $\mathbb{E}_D[\hat{\theta}]-\theta^*$
		- Variance: $\mathbb{E}_D[(\mathbb{E}_D[\hat{\theta}]-\hat{\theta})^2]$

<br>

#### Bias-Variance Tradeoff
- 추정치의 품질을 측정하기 위해 Risk를 사용하며, 이는 편향의 제곱과 분산의 합으로 계산

$$Risk=Bias^2+Variance$$

>[[Least Square Method|!example]], MSE
>$$\mathbb{E}[(\hat{\theta}-\theta)^2] = \underbrace{\left(\mathbb{E}[\hat{\theta}]-\theta\right)^2}_{Bias^2} + \underbrace{\mathbb{E}[\hat{\theta}^2] - \left(\mathbb{E}[\hat{\theta}]\right)^2}_{Var(\hat{\theta})}$$


<br>

## Approaches to Parametric Estimation
- MLE ([[Maximum Likelihood Estimation]])
	- 주어진 데이터에 대해 특정 파라미터를 가진 확률 분포에서 나왔을 가능성이 가장 높은 파라미터를 찾는 방법
- MAP ([[Maximum A Posterior Estimation]])
	- MLE와 비슷하지만, 사전 확률(prior probability)을 고려해 파라미터 추정
	- 베이지안 추론을 기반으로 하되, 특정 파라미터 분포의 사후 확률을 최대화하는 파라미터를 찾는 방법
- [[Bayesian Inference]]
	- 데이터와 사전 확률을 결합하여 파라미터의 분포를 추정하는 방법
	- 특정한 확률 모델을 가정하고, 그 모델의 파라미터를 추정
