---
date: 2024-12-08
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
# Expectation Maximization (EM) Algorithm
- **Definition**
	- 잠재 변수(latent variable)가 포함된 확률 모델에서 [[Maximum Likelihood Estimation]] 또는 [[Maximum A Posterior Estimation]]을 수행하기 위한 반복 최적화 알고리즘
	- 데이터 $x$가 관측 가능하지만, $z$ (잠재 변수)는 관측되지 않을 때 $z$의 숨겨진 정보를 추정하고 이를 활용해 $\theta$를 점진적으로 최적화.
	- Log-likelihood를 직접 최대화하지 않고, 하한선을 최대화하는 방식

<br>

- **Motivation**
	- Latent Variable
		$$\mathcal{L}(\theta) = \log p(x \mid \theta) = \log \int p(x, z \mid \theta) dz$$
		- $x$: 관측 데이터. 
		- $z$: 잠재 변수.
		- $\theta$: 모델의 파라미터.<br><br>
		- $z$는 직접 관측되지 않는 숨겨진 변수로, 확률 분포 $p(z \mid x, \theta)$를 계산해야 함
		- 로그와 적분이 결합되어 있어 직접 최적화가 불가능
		- Log-likelihood를 최대화하기 위해선 잠재 변수 $z$를 적분(marginalization)으로 제거해야 함

<br>

- **Objective**
	- Log-likelihood $\mathcal{L}(\theta)$를 최대화하는 모델 파라미터 $\theta$를 추정
	- 지를 위해 하한선을 정의하고, 반복적으로 하한선을 강화하여 최적화 수행

<br>

- **Algorithm**
	1. Define a lower bound of the log-likelihood
	   $$\mathcal{L}(\theta) = \log p(x \mid \theta) = \log \int p(x, z \mid \theta) dz$$
		- $q(z)$를 도입하여 로그와 적분을 분리
		  $$\mathcal{L}(\theta) = \log \int q(z) \frac{p(x, z \mid \theta)}{q(z)} dz$$
		- [[Jensen's Inequality]]를 적용하여 하한선을 정의
		  $$\mathcal{L}(\theta) \geq \mathcal{F}(q, \theta) = \int q(z) \log \frac{p(x, z \mid \theta)}{q(z)} dz$$
			- Log 함수는 볼록 함수이므로, Jensen's inequality에 의해 위 공식이 성립<br><br>
	2. E-step (Expectation step)
		- 현재 파라미터 $\theta^{(k)}$를 기반으로 **잠재 변수 $z$의 분포**를 추정
		- 하한선을 정의하기 위해 $q(z)$를 $p(z \mid x, \theta^{(k)})$로 설정
		  $$q^{(k+1)}(z) = p(z \mid x, \theta^{(k)})$$
		- 이를 통해 하한선 $\mathcal{F}(q, \theta)$를 강화<br><br>
	3. M-step (Maximization step)
		- E-step에서 추정한 $q(z)$를 기반으로 파라미터 $\theta$를 갱신
		- $q^{(k+1)}$를 고정하고, $\theta$를 갱신하여 log-likelihood의 하한선을 최대화
		  $$\theta^{(k+1)} = \arg \max_\theta \mathcal{F}(q^{(k+1)}, \theta)$$<br>
	4. [[Maximum Likelihood Estimation#An Interpretation of MLE KL-Matching|KL-Divergence]]로 해석
		- [[Gibb's Inequality]]를 통해 KL-divergence가 0에 수렴하면, $q(z) = p(z \mid x, \theta)$가 되고, 이때 log-likelihood $\mathcal{L}(\theta)$가 최대화
		  $$\mathcal{L}(\theta) - \mathcal{F}(q, \theta) = \text{KL}(q(z) \parallel p(z \mid x, \theta)) \geq 0$$

<br>

- **Convergence of EM Algorithm**
	- EM 알고리즘은 반복적으로 하한선을 강화하며, log-likelihood를 단조 증가시킴 (Monotonicity)
	  $$\mathcal{L}(\theta^{(k+1)}) \geq \mathcal{L}(\theta^{(k)})$$
	- 즉, 하한선 $\mathcal{F}(q, \theta)$를 정의 함으로써 수렴성 보장

<br>

- **Generalized EM**
	- Generalized EM에서는 M-step 에서 $\mathcal{F}(q, \theta)$를 부분적으로만 최적화하여 계산량을 줄이며, log-likelihood의 단조 증가를 보장
	  $$\mathcal{F}(q^{(k+1)}, \theta^{(k+1)}) > \mathcal{F}(q^{(k+1)}, \theta^{(k)})$$