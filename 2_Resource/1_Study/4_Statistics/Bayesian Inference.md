---
date: 2024-09-29
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
# Bayesian Inference
## MLE/MAP vs Bayesian Inference
- MLE/MAP
	- MLE와 MAP 모두 데이터 $D$를 대표하는 특정 매개변수 값 $\hat{\theta}$를 선택
	- 새로운 데이터를 학습할 때 마다 매개변수 값 $\hat{\theta}$를 새로 계산해야 함
		- [[Parametric Density Estimation#Unsupervised Learning|Unsupervised learning]]
			- $x_{new}$라는 새로운 입력 데이터가 주어졌을 때, MLE 또는 MAP로 추정한 $\hat{\theta}$를 사용하여 해당 데이터의 확률을 추정
			   $$p(x_{new}|D, \alpha)=p(x_{new}|\hat{\theta})$$
		- Supervised learning
			- $x_{new}$라는 새로운 입력 데이터가 주어졌을 때, MLE 또는 MAP로 추정한 $\hat{\theta}$를 사용하여 출력 $y_{new}$를 추정
			  $$p(y_{new}|x_{new}, D, \alpha)=p(y_{new}|x_{new}, \hat{\theta})$$

- Bayesian inference
	- 특정한 매개변수 값을 추정하는 것이 아닌, 매개변수 $\theta$에 대한 사후 확률 분포를 추정
	- 즉, 기존 데이터 $D$를 바탕으로 계산한 매개변수 $\theta$에 대한 사후 확률 $p(\theta|D;\alpha)$을 사용하여 새로운 데이터 $x_{new}$의 확률을 예측
		- Unsupervised learning
			- 새로운 데이터 $x_{new}$의 확률을 계산할 때, 매개변수 $\theta$에 대한 가중 평균을 사용
			  $$\begin{align*} \\
					p(x_{\text{new}} | D; \alpha) &= \int p(x_{\text{new}} | \theta, D; \alpha) \cdot p(\theta | D; \alpha) d\theta \\\\
					&= \int p(x_{\text{new}} | \theta) \cdot p(\theta | D; \alpha) d\theta \\\\\\
					p(x_{new}'|D\cup\{x_{new}\};\alpha)&=\int p(x_{new}'|\theta)\cdot p(\theta|D;\alpha)d \theta
					\end{align*}$$
				([[Law of Total Probability]])
		- Supervised learning
			- 새로운 입력 $x_{new}$와 함께 출력 $y_{new}$를 추정할 때, 동일하게 사후 확률 분포 $p(\theta|D;\alpha)$를 기반으로 가중 평균을 사용
			  $$p(y_{new}|x_{new}, D;\alpha)=\int p(y_{new}|x_{new}, \theta)\cdot p(\theta|D; \alpha)d\theta$$
	- Bayesian inference는 사후 확률 분포를 통해 매개변수의 모든 가능한 값을 고려하고, 그에 따른 예측을 수행
		- 즉, 매개변수에 대한 불확실성을 반영하는 방식

<br>

## Posterior Calculation
- 주어진 데이터 $D=\left\{x_1, \cdots, x_n\right\}$와 관련된 [[Maximum Likelihood Estimation#Maximum Likelihood Estimation (MLE]]|Likelihood)는 다음과 같이 주어짐
$$p(D|\theta)=\prod_{i=1}^np(x_i|\theta)$$

- Posterior distribution
$$\begin{align*} p(\theta | \mathcal{D}) &= \frac{p(\mathcal{D} | \theta) p(\theta)}{p(\mathcal{D})} \\\\ &= \frac{p(\theta) \prod_{i=1}^{n} p(x_i | \theta)}{\int p(D|\theta') p(\theta') d\theta'} \end{align*}$$

- Conjugate prior
	- 사전확률 $p(\theta)$를 선택했을 때, 관찰된 데이터 $D$에 대한 사후 확률 $p(\theta|D)$가 여전히 사전확률과 같은 함수 형태를 유지하는 경우
	- 사후 확률이 사전 확률과 동일한 함수 형태를 유지하게 되므로, 반복적으로 계산해야 하는 경우 계산이 용이해짐
	
	| Prior        | Likelihood | Posterior    |
	| ------------ | ---------- | ------------ |
	| **Beta**         | **Bernoulli**  | **Beta**         |
	| Beta         | Binomial   | Beta         |
	| **Normal**       | **Normal**     | **Normal**       |
	| Gamma        | Gamma      | Gamma        |
	| Gamma        | Poisson    | Gamma        |
	| Normal-Gamma | Normal     | Normal-Gamma |

<br>

## Beta-Bernoulli Conjugacy
- 동전 던지기와 같은 이항 실험에서 관찰된 결과 $x$에 대해 베르누이 분포([[Various Distributions#Bernoulli Distribution|Bernoulli distribution]])와 베타 분포([[Various Distributions#Beta Distribution|Beta distribution]])가 서로 Conjugate 관계를 형성하는 과정

1. Likelihood
   $$p(x|\mu )=Ber(x|\mu )=\mu ^x(1-\mu )^{1-x}$$
2. Prior Distribution
   $$p(\mu |\alpha, \beta)=Beta(\mu |\alpha, \beta)={\Gamma(\alpha+\beta)\over\Gamma(\alpha)\Gamma(\beta)}\mu ^{\alpha-1}(1-\mu )^{\beta-1}$$
3. Posterior Distribution
   $$\begin{align*}
	p(\mu |x, \alpha, \beta)={p(x|\mu )p(\mu |\alpha, \beta)\over p(x|\alpha, \beta)}&\propto p(x|\mu )p(\mu |\alpha, \beta)\\\\
	&\propto\mu ^{x+\alpha-1}(1-\mu )^{\beta-x}\\\\
	&\sim Beta(x+\alpha, \beta-x+1)
	\end{align*}$$

- Bayesian update
	- 동전 던지기와 같은 실험에서 새로운 데이터가 들어왔을 때, 기존에 가지고 있던 Posterior distribution을 Prior distribution으로 하여 매개변수 $\mu$의 분포를 업데이트 할 수 있음

<br>

## Normal-Normal Conjugacy
- 데이터 $D=\left\{x_i\right\}_{i=1}^n\qquad x_i\sim \mathcal{N}(\mu, \sigma^2)$

1. Likelihood
   $$p(x_i | \mu) = \frac{1}{\sqrt{2\pi \sigma^2}} \exp\left(-\frac{1}{2\sigma^2}(x_i - \mu)^2\right)$$
   
2. Prior Distribution
   분산 $\sigma^2$는 이미 알려져있고, 평균 $\mu$는 $\mathcal{N}(\mu_0, \sigma^2_0)$에서 추출되었다고 가정
  $$p_0(\mu ;\mu _0, \sigma^2_0)={1\over\sqrt{2\pi \sigma^2_0}}\exp \left(-{1\over2\sigma^2_0}(\mu -\mu _0)^2\right)$$

1. Posterior Distribution
	$$\begin{align*}
	p(\mu | D) = \frac{1}{\sqrt{2\pi\sigmã^2}} \exp\left(-\frac{1}{2\sigmã^2}(\mu - \mũ)^2\right)\qquad \text{where}\\\\
	\mũ = \frac{\mu_0/\sigma_0^2 + \sum_{i=1}^{n} x_i/\sigma^2}{1/\sigma_0^2 + n/\sigma^2}
	\quad \text{and}\quad
	\frac{1}{\sigmã^2} = \frac{1}{\sigma_0^2} + \frac{n}{\sigma^2}
	\end{align*}$$

- $n=0$ 일 때
	- 데이터가 없을 경우 사후 평균 $\tilde{\mu}$는 사전 평균 $\mu _0$에 수렴
	- 이는 데이터가 없을 때 사전 정보만을 기반으로 추론한다는 의미
- $n\rightarrow \infty$ 일 때
	- 데이터가 충분히 많아지면 사후 평균 $\tilde{\mu}$는 Maximum Likelihood으로 수렴
	- 이는 데이터가 충분히 많아지면 사전 정보의 영향을 거의 받지 않고, 데이터 자체에 기반한 추정이 이루어진다는 것을 의미