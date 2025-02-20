---
date: 2024-10-21
status: Permanent
tags:
  - Study/Lecture/Machine-Learning
  - Study/DL
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Deep Learning
- **Definition**
	- 다층 신경망(Multi-Layer [[Neural Network]])을 기반으로 한 기계 학습 방법론
	- 미분 가능한 함수들의 조합으로 구성되어 함수를 근사함
	$$F(x) \approx f_{W_L}(f_{W_{L-1}}(...f_{W_1}(x)...))$$
	- ReLU와 같은 [[Activation Function]]을 사용하여 **Vanishing Gradient 문제**를 완화하고, 비선형성을 높여 더 깊은 층을 쌓을 수 있게 된 모델

<br>

## Backpropagation
- **Definition**
	- 신경망에서 오차를 최소화하기 위해 기울기(gradient)를 역전파하여 가중치를 조정하는 학습 알고리즘
	- 복잡한 모델에서도 계산이 가능하도록 연쇄 법칙(chain rule)을 사용하여 효율적으로 기울기를 계산
- **Process**
  1. Forward Propagation: 
     입력 데이터를 신경망을 통해 예측값으로 변환
  2. Loss Calculation: 
     예측값과 실제값 사이의 오차(loss)를 계산
  3. Backward Propagation: 
     오차를 각 층으로 역전파하여 각 가중치에 대한 기울기를 계산
  4. Weight Update: 
     기울기를 이용해 경사 하강법으로 가중치를 조정하여 오차를 줄임

<br>

```ad-tip
title: **Vector derivatives**

- Scalar to Scalar
	- $x, y \in \mathbb{R}$
	  $$\frac{\partial y}{\partial x} \in \mathbb{R}$$


- Vector to Scalar
	- $x \in \mathbb{R}^N, y \in \mathbb{R}$
	  $$\frac{\partial y}{\partial x} \in \mathbb{R}^N, \quad \left( \frac{\partial y}{\partial x} \right)_n = \frac{\partial y}{\partial x_n}$$

- Vector to Vector
	- $x \in \mathbb{R}^N, y \in \mathbb{R}^M$
	  $$\frac{\partial y}{\partial x} \in \mathbb{R}^{N \times M}, \quad \left( \frac{\partial y}{\partial x} \right)_{nm} = \frac{\partial y_m}{\partial x_n}$$
```

```ad-tip
title: **Patterns in gradient flow**

- **Add** gate: gradient distributor #mcl/list-grid
  ![[Pasted image 20241113052929.png|300]]
- **Mul** gate: swap multiplier
  ![[Pasted image 20241113052953.png|300]]
- **Copy** gate: gradient adder
  ![[Pasted image 20241113053015.png|300]]
- **Max** gate: gradient router
  ![[Pasted image 20241113053033.png|300]]
```

```ad-example
title: Example 1
collapse: true

![[ezgif.com-animated-gif-maker 1.gif]]
```

```ad-example
title: Example 2
collapse: true

![[1).gif](ezgif.com-animated-gif-maker (1|ezgif.com-animated-gif-maker (1).gif]].gif)
```

```ad-example
title: Backpropagation with vectors
collapse: true

![[ezgif.com-animated-gif-maker 2.gif]]
```

```ad-example
title: Backpropagation with mactrices
collapse: true

![[1) 1.gif](ezgif.com-animated-gif-maker (1|ezgif.com-animated-gif-maker (1) 1.gif]]%201.gif)
```
