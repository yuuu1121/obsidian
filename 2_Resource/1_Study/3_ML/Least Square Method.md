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
# Least Square Method
- Training data $\{x_n\in \mathbb{R}^D, y_n\in\mathbb{R}\}_{n\in[N]}$에서, 가중치 벡터 $\mathbf{w}=\left[w_1, \cdots, w_L\right]^\top$를 결정하여 다음과 같은 손실 함수를 최소화하는 방법
- 즉, 예측값 $\hat{y}_n=\mathbf{w}^\top\phi(x_n)$와 실제 값 $y_n$사이의 오차를 최소화하는 과정을 통해 가중치 벡터 $\mathbf{w}$를 학습
	$$\varepsilon_{\text{LS}}(\mathbf{w}) = \frac{1}{2} \sum_{n=1}^{N} \left( y_n - \mathbf{w}^\top \phi(x_n) \right)^2 = \frac{1}{2} \| \mathbf{y} - \Phi \mathbf{w} \|^2$$
	- $\mathbf{y}=[y_1, \cdots, y_N]^\top$
	- $\Phi$: Design matrix

<br>

## Least Square Estimation
- 최소 제곱법의 해 $\underset{\mathbf{w}}{\arg\max}\text{ }\varepsilon_{LS}(\mathbf{w})$를 구하기 위해, 다음과 같은 식을 사용
	$$\frac{\partial \varepsilon_{\text{LS}}(\mathbf{w})}{\partial \mathbf{w}} = 0 \implies \Phi^\top \Phi \mathbf{w} = \Phi^\top \mathbf{y}$$

- 최소 제곲 추정값 $\mathbf{w}_{LS}$는 다음을 통해 구할 수 있음
	$$\mathbf{w}_{\text{LS}} = (\Phi^\top \Phi)^{-1} \Phi^\top \mathbf{y} = \Phi^\dagger \mathbf{y}$$
	- $\Phi^\dagger$: 무어-펜로즈 의사행렬 (Moore-Penrose Pseudo-inverse)
		- 일반 역행렬이 존재하지 않을 때 사용하는 기법으로, 데이터 기반의 최적의 해를 찾는데 사용

<br>

## Example of LS: Maximum Likelihood Estimation
- 주어진 출력값 $y_n$을 다음과 같이 가정
	-  deterministic function $f(\mathbf{x_n})=\mathbf{w}^\top \phi(\mathbf{x}_n)$에 가우시안 노이즈 $\epsilon\sim \mathcal{N}(0, \sigma^2I)$가 추가된 형태 
	$$\mathbf{y}=\Phi\mathbf{w}+\epsilon$$
- [[Maximum Likelihood Estimation]]
  $$\begin{align*}
\mathcal{L} &= \log p(\mathbf{y} | \Phi, \mathbf{w}) = \sum_{n=1}^{N} \log p(y_n | \phi(\mathbf{x}_n), \mathbf{w})\\\\
&=-\frac{N}{2} \log \sigma^2 - \frac{N}{2} \log 2\pi - \frac{1}{\sigma^2} 
\underbrace{\left({1\over 2}\sum_{n=1}^{N} (y_n - w^T \phi(x_n))^2\right)}_{=\epsilon_{LS}}
\end{align*}$$
- 즉, 가우시안 노이즈를 가정할 경우 LS는 MLE와 동일
	$$\mathbf{w}_{LS}=\mathbf{w}_{MLE}$$


