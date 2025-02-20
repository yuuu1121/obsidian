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
# Mixture Model
- **Definition**
	- 데이터가 여러 확률 분포(probability distribution)의 조합으로 생성되었다고 가정하는 통계 모델
	- 즉, 데이터 전체를 단일 분포로 설명하는 대신, 여러 하위 분포의 혼합으로 설명
	- 각 데이터 포인트는 특정 하위 분포에서 생성되었다고 간주하며, 이를 나타내는 잠재 변수(latent variable)를 도입

<br>

- **Key Concepts**
	- Finite Mixture Model
		- 데이터 포인트 $x_i$가 $K$개의 하위 분포 중 하나에서 생성되었다고 가정<br><br>
		- [[Continuous RV|Probability Density Function]]
		  $$p(x) = \sum\limits_{k\in[K]}p(x, z=k)=\sum\limits_{k\in[K]}p_k(x)p(z=k)$$
			- $\{\pi_k := p(z = k)\}_{k \in [K]}$: $k$번째 하위 분포의 혼합 비율(믹싱 계수, mixing coefficient), $\sum_{k=1}^K \pi_k = 1$, $\pi_k \in [0, 1]$
			- $p_k(x)$: $k$번째 하위 분포의 확률 밀도 함수.

<br><br>

# Gaussian Mixture Model (GMM)
- **Definition**
	- 각 하위 분포가 [[Various Distributions#Gaussian Distribution (Normal Distribution]]|Gaussian%20Distribution)을 따르는 Mixture Model의 일종
	- 각 데이터 포인트가 특정 가우시안 분포에서 생성되었다고 가정
	- 가우시안 분포는 평균($\mu$), 공분산($\sigma$), 혼합 비율($\pi$)로 정의
	- 데이터는 여러 클러스터에 걸쳐 확률적으로 속할 수 있음

<br>

- **Key Concepts**
	- Latent Variable $z_i$
		- $z_i$는 데이터 $x_i$가 어느 가우시안 컴포넌트에서 생성되었는지를 나타내는 **잠재 변수(latent variable)**
		- $p(z_i = k) = \pi_k$: $z_i$가 $k$번째 컴포넌트를 선택할 확률.<br><br>
	- Marginal Distribution
	  $$p(x\mid \theta) = \sum_{k=1}^K \pi_k \mathcal{N}(x \mid \mu_k, \sigma_k)$$
		- $\theta = \{\pi_k, \mu_k, \sigma_k\}_{k=1}^K$: 
			- GMM의 모델 매개 변수
			- 마진 분포의 형태를 결정하며, 데이터가 어떻게 혼합된 가우시안 분포로 표현되는지를 정의
			- EM 알고리즘을 통해 $\theta$를 학습하여 데이터를 가장 잘 설명하는 모델을 생성
		- $\pi_k$: $k$번째 가우시안 분포의 혼합 비율, $\sum_{k=1}^K \pi_k = 1$.
		- $\mathcal{N}(x \mid \mu_k, \sigma_k)$: $k$번째 가우시안 분포의 확률 밀도 함수.
		- $\mu_k$: 평균 벡터.
		- $\sigma_k$: 공분산 행렬.
		- $K$: 가우시안 컴포넌트의 개수.<br><br>
	- Conditional Distribution
	  $$p(x_i \mid z_i) = \prod_{k \in [K]} \mathcal{N}(x_i \mid \mu_k, \sigma_k)^{\mathbb{1}[z_i=k]}$$
		- $\mathbb{1}[z_i=k]$: $z_i$가 $k$번째 컴포넌트를 선택했을 때 1, 그렇지 않으면 0인 지시 함수.
		- 이 식은 $x_i$가 선택된 가우시안 컴포넌트 $k$에서 생성되었음을 의미

<br>

## Learning GNN
- **Objective**
	- GMM의 모델 파라미터 $\theta = \{\pi_k, (\mu_k, \sigma_k)\}_{k \in [[Maximum Likelihood Estimation|K]] 수행
	  $$L(\theta) = \log p(\mathcal{D} \mid \theta) = \sum_{n=1}^N \log \sum_{k=1}^K \pi_k \mathcal{N}(x_n \mid \mu_k, \sigma_k)$$
		- 직접적으로 해석적인 해를 구할 수 없으므로 EM 알고리즘을 사용.
		- EM 알고리즘을 통해 $\theta$를 반복적으로 갱신.<br><br>
	- Latent variable $z_i$의 사후 확률 계산
	  $$r_{ik} = p(z_i = k \mid x_i;\theta')=\mathbb{E}_{z_i\mid x_i, \theta'}[z_{ik}]$$
		- $r_{ik}$는 데이터 포인트 $x_i$가 클러스터 $k$에 속할 확률.

<br>

### [[Expectation Maximization]] (EM) Algorithm
1. Initialization
	- 초기 매개변수 $\theta^{(0)}= \{\pi_k, \mu_k, \sigma_k^2\}_{k \in [K]}$를 임의로 설정
	- 관측 데이터 $x$에 대한 log-likelihood
	  $$L(\theta) = \log \prod_{i=1}^N p(x_i \mid \theta) = \sum_{i=1}^N \log \sum_{k=1}^K \pi_k \mathcal{N}(x_i \mid \mu_k, \sigma_k)$$<br><br>
1. E-step (Expectation Step)
	- 현재 매개변수 $\theta^{(t)}$를 기준으로 잠재변수 $z$의 분포 $p(z\mid x, \theta^{(t)})$를 계산
	  $$r_{ik} = p(z_i = k \mid x_i, \theta^{(t)}) = \frac{\pi_k^{(t)} \mathcal{N}(x_i \mid \mu_k^{(t)}, \sigma_k^{(t)})}{\sum_{\ell=1}^K \pi_\ell^{(t)} \mathcal{N}(x_i \mid \mu_\ell^{(t)}, \sigma_\ell^{(t)})}$$
	- $Q$ function
		$$\begin{align*}
		Q(\theta; \theta^{(t)}) &= \mathbb{E}_{z \sim p(z \mid x, \theta^{(t)})}[\log p(x, z \mid \theta)]\\\\
		&= \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \left[ \log \pi_k - \frac{D}{2} \log \sigma_k^2 - \frac{1}{2\sigma_k^2} \|x_i - \mu_k\|^2 \right] + \text{const}.
		\end{align*}$$
		- $Q(\theta; \theta^{(t)})$: 현재 매개변수를 기준으로 계산된 전체 데이터의 log-likelihood의 기대값
		- $p(z \mid x, \theta^{(t)})$: 잠재 변수 $z$의 조건부 분포.<br><br>
3. M-step (Maximization Step)
	- E-step에서 계산된 $Q(\theta; \theta^{(t)})$를 최대화하여 새로운 매개변수 $\theta^{(t+1)}$를 업데이트
	  $$\theta^{(t+1)} = \arg\max_\theta Q(\theta; \theta^{(t)})$$
	- Mean Update
		$$\begin{align*}
		\frac{\partial Q}{\partial \mu_k} &= -\frac{1}{\sigma_k^2} \sum_{i \in [N]} r_{ik}(x_i - \mu_k) = 0\\\\
		&\implies \mu_{k}^{(t+1)} = \frac{\sum_{i \in [N]} r_{ik} x_i}{\sum_{i \in [N]} r_{ik}}.
		\end{align*}$$
	- Variance Update
		$$\begin{align*}
		\frac{\partial Q}{\partial \sigma_k^2} &= \sum_{i \in [N]} r_{ik} \left[ -\frac{D}{\sigma_k^2} + \frac{1}{\sigma_k^4} \|x_i - \mu_k\|^2 \right] = 0\\\\
		&\implies {\sigma_{k}^2}^{(t+1)} = \frac{1}{D} \frac{\sum_{i \in [N]} r_{ik} \|x_i - \mu_{k}^{(t+1)}\|^2}{\sum_{i \in [N]} r_{ik}}
		\end{align*}$$
	- Latent Variable Update
		- Objective Function
		  $$Q(\theta) = \sum_{i \in [N]} \sum_{k \in [K]} r_{ik} \left[ \log \pi_k - \frac{D}{2} \log \sigma_k^2 - \frac{1}{2\sigma_k^2} \|x_i - \mu_k\|^2 \right] + \text{const}$$
		- Constraint
		  $$\sum_{k \in [K]} \pi_k = 1$$<br><br>
		- [[Constrained Optimization#Lagrangian Dual Problem|Lagrangian Dual Problem]]
		  $$Q'(\theta, \lambda) = Q(\theta) + \lambda \left( 1 - \sum_{k \in [K]} \pi_k \right)$$
		  $$\frac{\partial Q'}{\partial \pi_k} = 0\implies \pi_{k}^{(t+1)} = \frac{1}{N} \sum_{i \in [N]} r_{ik}$$

<br>

```ad-tip
title: K-means: Special Case of EM for GMM
GMM의 모델 파라미터를 $\pi_k = \frac{1}{K}$, $\sigma_k^2 = \sigma^2$, $\sigma^2 \to 0$로 설정하면, [[K-means Clustering]] 알고리즘과 동일한 동작 수행
```