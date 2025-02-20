---
date: 2024-09-29
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords:
  - MAP
related notes:
  - "[[Parametric Density Estimation]]"
reference: 
author: 
url: 
dg-publish: false
---
# Maximum A Posteriori(MAP) Estimation
- MAP는 [[Maximum Likelihood Estimation|MLE]]와 유사하지만, 사전 확률 분포(prior distribution)을 추가로 고려
	- MLE는 주어진 데이터 $D$에 대해, 모델의 매개변수 $\theta$가 주어졌을 때 데이터가 발생할 가능성 $p(D|\theta)$를 최대화하는 매개변수 $\theta$를 찾는 과정
		- ==오직 데이터만을 기반==으로 하기 때문에, ==데이터가 적거나 편향된 경우 잘못된 결과를 초래==할 수 있음
	- MAP는 ==사전 정보를 확률 분포의 형태(사전 확률 분포, prior distribution) $p(\theta)$로 반영==하고, ==주어진 데이터 $D$가 있을 때 사후 확률 분포([[Bayes' Theorem|posterior distribution]]) $p(\theta|D)$를 최대화하는 $\theta$값==을 찾는 방법

$$p(\theta|D)={p(D|\theta)p(\theta)\over p(D)}$$

$$\hat{\theta}_{MAP}:=\underset{\theta}{\arg{\max}}\text{ }p(\theta|D)=\underset{\theta}{\arg{\max}}\text{ }[\log p(D|\theta)+\log p(\theta)]$$

- 이때, 사전 확률 분포 $p(\theta)$는 우리가 매개변수 $\theta$에 대해 가지는 사전 정보를 나타내며, 모델이 과적합([[Overfitting]]) 되는 것을 방지
	- 만약 사전 분포가 단순한 모델을 선호한다고 가정하면, 사전 분포는 너무 복잡한 모델을 규제([[2_Resource/1_Study/3_ML/Regularization]])하고 더 단순한 모델을 선호하게 함

<br>

## Examples of MAP
### Beta-Binomial Distribution
- 베타 분포([[Various Distributions#Beta Distribution|Beta Distribution]])는 [0, 1] 구간에서 정의된 확률 분포
	$$\begin{align*}
	p(\mu|\alpha, \beta)&={\Gamma(\alpha+\beta)\over \Gamma(\alpha)\Gamma(\beta)}\mu^{\alpha-1}(1-\mu)^{\beta-1}\\\\
	\mathbb{E}[\mu]&={\alpha\over \alpha+\beta}
	\end{align*}$$
	
	where $\Gamma(\cdot)$ is a gamma function
	$$\begin{align*}
	\Gamma(t)&:=\int^\infty_0x^{t-1}\exp{(-x)}dx,\qquad t>0\\\\
	\Gamma(t+1)&=t \Gamma(t)
	\end{align*}$$

![[Pasted image 20240922160819.png|300]]

- MLE 접근법에서는 $\mu$의 Maximum Likelihood를 계산하여 가장 그럴듯한 $\mu$값을 추정
- MAP 접근법에서는 $\mu$에 대한 사전 확률 분포를 베타 분포 $Beta(\mu|\alpha, \beta)$로 설정한 후, $\mu$의 사후 확률을 최대화하는 값을 찾음

$$\hat{\mu}_{MAP}={\alpha+x-1\over \alpha+\beta+n-2}$$

#### Tossing Coins
- 동전 던지기 실험에서 $x$번의 앞면을 관찰하고, 총 $n$번의 시도가 있다고 가정하고, 성공 횟수 $x$는 이항항분포([[Various Distributions#Binomial Distribution|Binomial Distribution]])를 따른다고 가정 ([[Maximum Likelihood Estimation#Binomial distribution|Examples of MLE: Binomial Distribution]])
- $\alpha=\beta=3, x=7, n=10$ 이라고 가정하면
	- $\hat{\mu}_{MAP}=0.64<\hat{\mu}_{MLE}=0.7$
	- 이는 사전 지식(동전이 공정하다는 믿음)이 MAP 추정 결과에 영향을 미쳤기 때문
	- 만약 $n\gg \alpha+\beta$, 즉 데이터가 매우 많을 때 사전 확률의 영향은 약해지며, MAP 추정값은 MLE 추정값과 거의 같아짐
	- 반면, 데이터가 적을 때는 사전 확률의 영향이 커져서 추정값이 사전 확률에 더 가까워짐

<br>

### Gaussian Distribution
- 데이터 $D$가 $\mathcal{N}(\mu, 1)$에서 독립적으로 추출되었다고 가정하고, $p(\mu|\alpha)\sim \mathcal{N(0, \alpha^2)}$라고 할 경우

$$\hat{\mu}_{MAP}={1\over (n+{1\over \alpha^2})}\sum\limits_{i=1}^nx_i$$
- 데이터가 매우 많은 경우 $n\gg {1\over \alpha^2}$
	- MAP 추정값은 MLE 추정값과 거의 동일해짐. 즉, $\hat{\mu}_{MAP}\approx \hat{\mu}_{MLE}$
- 데이터가 적을 경우 $n\ll {1\over \alpha^2}$
	- 사전 확률의 영향이 커져서 추정값이 $\mu=0$에 가까워짐