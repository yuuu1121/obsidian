---
date: 2024-10-01
status: Permanent
tags:
  - Study/ML
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Regularization
- Parameter가 너무 큰 수가 되지 않게 패널티를 주는 것
	- Parameter의 크기가 너무 크면, 입력 데이터 값이 민감해져서 [[Overfitting]] 문제가 발생
	- Regularization을 사용하면 데이터의 미세한 변화에 강인한 모델 가능

>[!multi-column]
>>![[Pasted image 20241001165605.png]]
>
>>
|           | $L = 9$ | $L = 9$ | $L = 9$ | $L = 9$   |
| --------- | --------- | --------- | --------- | ----------- |
| $w_2^*$ | 0.19      | 0.82      | 0.31      | 0.35        |
| $w_2^*$ |           | -1.27     | 7.99      | 232.37      |
| $w_2^*$ |           |           | -25.43    | -5321.83    |
| $w_2^*$ |           |           | 17.37     | 48568.31    |
| $w_2^*$ |           |           |           | -231639.30  |
| $w_2^*$ |           |           |           | 640042.26   |
| $w_2^*$ |           |           |           | -1061800.52 |
| $w_2^*$ |           |           |           | 1042400.18  |
| $w_2^*$ |           |           |           | -557682.99  |
| $w_2^*$ |           |           |           | 125201.43   |


<br>

## Ridge Regression
- Ridge regression은 다음과 같은 Loss function을 최소화
	$$\varepsilon =  
	\underbrace{\frac{1}{2} \|\mathbf{y} - \Phi \mathbf{w}\|^2}_{\text{Fitting error}}
	+\underbrace{\frac{\lambda}{2} \|\mathbf{w}\|^2}_{\mathbf{Regularizer}}
	$$
	$$\mathbf{w}_{\text{ridge}} = (\lambda I + \Phi^\top \Phi)^{-1} \Phi^\top \mathbf{y}\qquad\text{when}\quad{\partial\varepsilon\over\partial\mathbf{w}}=0$$
	- $\lambda$: Fitting error와 Regularizer 사이의 균형을 조절하는 변수

![[Pasted image 20241001170520.png]]


<br>

### Example of Ridge Regression: MAP Perspective
- 관측 데이터로부터, 좋은 매개변수 $\mathbf{w}$는 작은 크기를 가질 것이라고 가정할 수 있음
	- 즉, $\mathbf{w}$의 평균이 0이고, 공분산이 $\Sigma$인 가우시안 사전 분포를 가정
- 또한, $\mathbf{y}=\Phi\mathbf{w}+\epsilon$이며, $\epsilon\sim\mathcal{N}(0, \sigma^2I)$라고 가정

$$\begin{align*}
p(\mathbf{w}) &= \mathcal{N}(\mathbf{w} | 0, \Sigma)\\\\
p(\mathbf{y} | \Phi, \mathbf{w}) &= \mathcal{N}(\mathbf{y} | \Phi \mathbf{w}, \sigma^2 I)
\end{align*}$$

- $\mathbf{w}$에 대한 Posterior은 다음과 같음

$$p(\mathbf{w} | \mathbf{y}, \Phi) = \frac{p(\mathbf{y} | \Phi, \mathbf{w})p(\mathbf{w})}{p(\mathbf{y} | \Phi)}$$

- Gaussian identities로 부터 Posterior는 여전히 평균과 [[Mode)](최빈값(Mode|최빈값(Mode)]].md)가 다음과 같은 가우스 분포임을 알 수 있음

$$\mathbf{w}_{\text{MAP}} = \left(\sigma^2 \Sigma^{-1} + \Phi^\top \Phi\right)^{-1} \Phi^\top \mathbf{y}$$

- 여기서 $\Sigma={\sigma^2\over\lambda}I$ 일 때, $\mathbf{w}_{MAP}=\mathbf{w}_{ridge}$
	- 즉, Ridge regression은 [[Maximum A Posterior Estimation|MAP]]의 특수한 경우로 해석될 수 있으며, Prior를 통해 매개변수의 크기를 제어하여 과적합을 방지하는 방식
	- Posterior를 최대화하는 $\mathbf{w}_{MAP}$는 데이터와 Prior를 결합하여 최적의 매개변수를 찾는 방식으로, Ridge regression의 역할과 동일

<br>

#### Lemma (Gaussian Identities)
- $x, y$가 가우시안 분포를 따를 때, Conditional distribution을 구하는 공식
- 다음과 같은 랜덤 벡터 $\mathbf{z}=[\mathbf{x}^\top, \mathbf{y}^\top]^\top$를 고려
	$$\mathbf{z} \sim \mathcal{N}\left(\begin{bmatrix} a \\ b \end{bmatrix}, \begin{bmatrix} \mathbf{A} & \mathbf{C} \\ \mathbf{C}^\top & \mathbf{B} \end{bmatrix}\right)$$
	- 여기서 $\mathbf{C}=\mathbb{E}[\mathbf{x}\mathbf{y}^\top]$인 교차 공분산이며, $\mathbf{x}\sim\mathcal{N(a, \mathbf{A})},\quad \mathbf{y}\sim\mathcal{N}(b\mathbf{B})$
- 조건부 분포는 다음과 같음
	$$\begin{align*}
	p(\mathbf{x} | \mathbf{y}) &= N(\mathbf{x} | a + \mathbf{CB}^{-1}(\mathbf{y} - b), \mathbf{A} - \mathbf{CB}^{-1}\mathbf{C}^\top)\\\\
	p(\mathbf{y} | \mathbf{x}) &= N(\mathbf{y} | b + \mathbf{C}^\top \mathbf{A}^{-1}(\mathbf{x} - a), \mathbf{B} - \mathbf{C}^\top \mathbf{A}^{-1} \mathbf{C})
	\end{align*}$$

<br>

##### Calculate the MAP Equation
- Condition
	
$$\begin{align*}
\mathbf{w}&\sim \mathcal{N}(0, \Sigma)=\mathcal{N}(a, \mathbf{A})\\\\
\mathbf{y}&\sim \mathcal{N}(0, \sigma^2I)=\mathcal{N}(b, \mathbf{B})
\end{align*}$$

$$\begin{align*}
p(\mathbf{y} | \Phi, \mathbf{w}) &= \mathcal{N}(\mathbf{y} | \Phi \mathbf{w}, \sigma^2 I)\\\\
\mathbb{E}[\mathbf{y}|\mathbf{w}]&=\Phi \mathbf{w}\\\\
\mathbb{E}\mathbf{_w}[\mathbb{E}[\mathbf{y}|\mathbf{w}]]&=\mathbb{E}[\Phi \mathbf{w}]=0
\end{align*}$$

- Lemma

$$\begin{align*}
\mathbf{C}&=\mathbb{E}[\mathbf{w}\cdot\mathbf{y}^\top]=\mathbb{E}_w[\mathbb{E}_y[\mathbf{w}\cdot\mathbf{y}^\top|\mathbf{w}]]\\\\
&=\mathbb{E}[\mathbf{w} \cdot\mathbb{E}_y[\mathbf{y}^\top|\mathbf{w}]]=\mathbb{E}_w[\mathbf{w}\cdot\mathbf{w}^\top \Phi^\top]\\\\
&=\Sigma \Phi^\top
\end{align*}$$

$$\begin{align*}
\mathbf{w}_{MAP}=(\sigma^2 \Sigma^{-1}+\Phi^\top \Phi)^{-1}\Phi^\top\mathbf{y}\\\\
\mathbf{w}_{ridge}=(\lambda I+\Phi^\top \Phi)^{-1}\Phi^\top\mathbf{y}
\end{align*}$$

