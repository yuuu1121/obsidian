---
date: 2024-09-25
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
# Maximum Likelihood Estimation (MLE)
- 주어진 데이터 $D$가 특정 매개변수 $\theta$를 가질 때 가장 가능성 있는 $\theta$값을 찾는 방법
	- 경험적 데이터 분포와 모델 분포간의 차이를 최소화하는 방법
	- 즉, MLE는 주어진 데이터에 가장 적합한 모델을 찾기 위한 방법
- Likelihood (우도 함수, $\mathcal{L}(\theta; D$)): 
  매개변수 $\theta$가 주어졌을 때, 데이터 $D$가 발생할 확률

$$\begin{align*}
\mathcal{L}(\theta;D)&:=p(D|\theta)=p_\theta(D)\\\\
&=\prod_{i=1}^Np(x_i|\theta)
\end{align*}$$


- MLE는 Likelihood를 최대화하는 $\hat{\theta}_{MLE}$를 찾는 과정

$$\hat {\theta}_{MLE}:=\underset{\theta}{\arg{\max}}\text{ }\mathcal{L}(\theta;D)$$

## An Interpretation of MLE: KL-Matching
- Kullback-Leibler (KL) divergence
	- 두 확률 분포 간의 차이를 측정하는 방식 중 하나로, 주어진 실제 데이터의 분포화 [[Parametric Density Estimation#Statistical Model|통계적 모델]]의 분포 사이의 차이를 최소화하는 방법
	- 두 확률 분포 $p(x)$와 $q(x)$ 사이의 비대칭적 거리로 정의
	$$KL(p||q):=\int p(x)\log{p(x)\over q(x)}dx$$
	- $p(x)$: 실제 데이터의 경험적 분포
	- $q(x)$: 추정한 통계적 모델의 분포, 매개변수 $\theta$에 따라 달라짐

- MLE는 경험적 분포 $\tilde{p}(x)$와 통계적 모델 분포 $p_\theta(x)$간의 KL divergence를 최소화하는 매개변수 $\theta$를 찾는 문제
	- $\tilde{p}(x)$: 데이터에 의해 관찰된 경험적 분포
	  $$\tilde{p}(x)={1\over n}\sum\limits_{i=1}^n \delta(x-x_i)$$
	  - $\delta(x-x_i)$: $x_i$ 위치에서만 값을 가지는 분포. 즉, 데이터 샘플 $x_1, \cdots, x_n$에서 관찰된 값에 기반한 분포

$$\underset{\theta}{\arg{\min}}\text{ }KL(\tilde{p}||p_\theta)=\underset{\theta}{\arg{\max}}\sum\limits_{i=1}^n\log{p_\theta(x_i)}=\hat{\theta}_{MLE}$$

<br>

# Maximum log-Likelihood Estimation
- 로그 함수는 단조 증가(monotonically increasing) 함수이기 때문에 원래 Likelihood 함수를 최대화하는 것과 같은 결과를 도출함

![[0df58b832bdf6af03f37d26f3662174a_MD5.webp|300]]

$$\hat{\theta}_{MLE}:=\underset{\theta}{\arg{\max}}\text{ }\mathcal{L}(\theta;D)=\underset{\theta}{\arg{\max}}\text{ }\mathcal{l}(\theta;D)$$

- $D={x_1, \cdots, x_n}$이 $p(\cdot|\theta)$ 에서 독립적으로 표본 추출되었을 때
  $$p(D|\theta)=\prod_{i=1}^np(x_i|\theta)$$
  이며, 따라서 log-Likelihood는 다음과 같이 표현될 수 있음
  
$$\mathcal{l}(\theta;D)=\sum\limits_{i=1}^n\log{(p(x_i|\theta))}$$ 
<br>

## Advantage of log-Likelihood
1. Meaningful value
   - 일반 Likelihood 함수는 $p(D|\theta)$의 값이 표본 수 $n$이 증가할수록 점점 작아지기 때문에 우도 함수의 값은 0에 근접
   - 반면 log-Likelihood 함수는 곱셈을 덧셈으로 변환하여 0으로 수렴하는 속도를 늦추고, 계산의 안정성을 높일 수 있음
2. Easy computation
	- Likelihood를 최대화하는 $\theta$를 구하기 위해선 Likelihood의 Gradient를 구해야하는데, 이 과정에서 곱연선인 일반 Likelihood는 계산이 복잡함
	- 반면, log-Likelihood는 합연산이기 때문에 훨씬 간단하게 Gradient를 구할 수 있음

<br>

## Examples of MLE
### Binomial Distribution
- 동전 던지기 실험에서 $x$번의 앞면을 관찰하고, 총 $n$번의 시도가 있다고 가정
- 이때, 동전이 앞면이 나올 확률인 $\mu$에 대한 MLE 추정은 다음 과정을 통해 이루어짐

1. Likelihood 함수 설정
	- 동전 던지기의 경우, 성공 횟수 $x$는 이항분포([[Various Distributions#Binomial Distribution|Binomial Distribution]])를 따름
	$$\mathcal{L}(\mu;x, n)=\begin{pmatrix}n\\x\end{pmatrix}\mu^x(1-\mu)^{n-x}$$
2. log-Likelihood 함수로 변환
	$$\mathcal{l}(\mu;x, n)=x\log{(\mu)}+(n-x)\log{(1-\mu)}$$
3. Maximization of log-Likelihood
	$$\underset{\mu}{\arg{\max}}\text{ }\mathcal{l}_{MLE}(\mu)=\underset{\mu}{\arg{\max}}\text{ }x\log{\mu}+(n-x)\log{(1-\mu)}$$
	$$\hat{\mu}_{MLE}={x\over n}\qquad \text{when}\quad{\partial \mathcal{L}_{MLE}\over\partial \mu}=0$$

- 즉, MLE $\hat{\mu}_{MLE}$는 성공한 횟수 $x$를 총 시도 횟수 $n$으로 나눈 값, 즉 성공률

<br>

### Gaussian Distribution
- 정규 분포([[Various Distributions#Gaussian Distribution (Normal Distribution]]|Gaussian%20Distribution))에서 $\mu$와 $\sigma^2$를 추정하는 MLE 과정

1. Likelihood 함수 설정
   $$\begin{align*}
	p(x_i|\mu, \sigma^2)&={1\over \sqrt{2\pi \sigma^2}}\exp{\left(-{(x_i-\mu)^2\over 2\sigma^2}\right)}\\\\
	\mathcal{L}(\mu,\sigma^2; D)&=\prod_{i=1}^np(x_i|\mu, \sigma^2)
	\end{align*}$$
2. log-Likelihood 함수로 변환
   with $\theta=(\theta_1, \theta_2)=(\mu, \sigma^2)$
   $$\begin{align*}
	\mathcal{l}(\theta)&=\sum\limits_{i=1}^n\log{p(x_i|\theta)}\\\\
	&=-{n\over2}\log(2\pi \theta_2)-{1\over 2\theta_2}\sum\limits_{i=1}^n(x_i-\theta_1)^2
	\end{align*}$$
3. Maximization of log-Likelihood
	$$\begin{align*}
	\hat{\theta}_{MLE, 1}&={1\over n}\sum\limits_{i=1}^nx_i\approx \mu&\text{when}\quad {\partial \mathcal{l}(\theta)\over\partial \theta_1}=0\\\\
	\hat{\theta}_{MLE, 2}&={1\over n}\sum\limits_{i=1}^n(x_i-\hat{\theta}_{MLE, 2})^2\approx \sigma^2&\text{when}\quad{\partial \mathcal{l}(\theta)\over\partial \theta_2}=0
	\end{align*}$$

<br>

#### A Comparative Analysis of Two Estimators in Gaussian MLE
- Estimator 1
	- 추정방법: 첫 번째 샘플 $x_1$만 사용하여 평균 $\mu$
	  $$\hat{\mu}_1=x_1$$
	- 기대값
	  $$\mathbb{E}[\hat{\mu}_1]=\mu$$
		- 이 추정 방법은 Unbiased estimator ($\mathbb{E}[\hat{\mu}_1]-\mu=0$)
		- 즉, 평균적으로 올바른 $\mu$값을 추정
	- 분산
	  $$\text{Var}(\hat{\mu}_1)=\sigma^2$$
		- 그러나, 단 하나의 샘플만 사용하기 때문에 분산이 큼
- Estimator 2
	- 추정방법: 모든 샘플 $x_1, \cdots, x_n$을 평균 내어 $\mu$를 추정
	  $$\hat{\mu}_2={1\over n}\sum\limits_{i=1}^nx_i$$
	- 기대값
	  $$\mathbb{E}[\hat{\mu}_2]=\mu$$
		- 역시 Unbiased estimator으로, 평균적으로 올바른 $\mu$값을 추정
	- 분산
	  $$\text{Var}(\hat{\mu}_2)={\sigma^2\over n}$$
		- 모든 샘플을 사용하기 때문에 분산이 더 작음
- Risk
  $$\text{Risk}(\hat{\mu}_1)=0^2+\sigma^2>\text{Risk}(\hat{\mu}_2)=0^2+{\sigma^2\over n}$$

