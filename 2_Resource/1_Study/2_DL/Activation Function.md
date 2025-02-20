---
date: 2024-02-25
status: Permanent
tags:
  - Study/DL/ActivationFunction
aliases: 
reference: 
author:
  - 하루에 빵코 한입
  - Daehee YUN
url:
  - https://bbangko.tistory.com/5
  - https://076923.github.io/posts/AI-6/
---
# Activation Function
- 인공 신경망( Neural Network)에서 사용되는 은닉층 (Hidden Layer)를 활성화하기 위한 함수
	- 최종출력 신호를 다음 layer로 **보내줄지 말지를 결정**하는 역할
- 가중치 Weight와 편향 Bias를 업데이트하기 위해 사용되는 주요한 함수
- 활성화 함수는 비선형 Non-linear 구조를 가져 [[Back Propagation|역전파 과정]]에서 미분값을 통해 학습이 진행될 수 있게 함
- 활성화 함수는 입력을 [[Normalization|정규화]]하는 과정으로 볼 수 있음
- 좋은 Activation function 은 Gradient 를 더 효율적으로 전파하는 동시에 너무 많은 계산 비용이 들지 않아야 함

![[Pasted image 20241113040445.png]]

---
## Linear Function
- 말그대로 직선적인 함수 $y=x$
- Linear Function을 [[Activation Function|활성화 함수]]로 사용하면 **Deep**한 네트워크의 이점이 전혀 없음

![[Pasted image 20240225205146.png]]
- 위 2-Layer 모델을 보면 $X$에 곱해지는 항들은 $W$로 치환이 가능하고, 입력과 무관한 상수들은 전체를 $B$로 치환이 가능하기 때문에 $WX+B$라는 Single layer perception과 동일한 결과를 냄
- 즉, [[Back Propagation|역전파 과정]]에서 미분을 진행할 때, 항상 같은 상수 $W$를 반환하게 되므로 학습이 진행되지 않고, 네트워크를 **Deep**하게 쌓는 의미가 없어짐

![[Pasted image 20240225205346.png|500]]

---
## Rectified Linear Unit (ReLU)
![[Pasted image 20240304192615.png|500]]
<center style='font-size:14; opacity:0.7;'>Comparison between ReLU series</center>

---
![[Pasted image 20240229144832.png|+grid]]![[Pasted image 20240229144908.png|+grid]]![[Pasted image 20240229144929.png|+grid]]
<center style="font-size: 14; opacity: 0.7">Leaky ReLU / PReLU (좌), ReLU6, SeLU</center>

### ReLU
$$ReLU(x)=\max(0, x)$$

- Sigmoid 의 Gradient vanishing 문제를 해결하기 위해 등장하였으나, 음수 값을 전혀 학습하지 못함
### Leaky ReLU (LReLU)
$$LeakyReLU(x)=\begin{cases}
x, & \mbox{if }x>0 \\
\mbox{negative\_slope}\times x, & \mbox{otherwise} \end{cases}$$

- Dying ReLU 문제를 해결하기 위해 기존 ReLU 함수에서 음수 값에 대하여 Gradient 가 0이 되지 않도록 작은 값을 곱해준 Activation function
- 음수 기울기 (Negative slope)를 제어하여 Dying ReLU 현상을 방지하기 위해 사용
- 양수인 경우 ReLU 와 동일하지만, 음수인 경우 작은 값이라도 출력시켜 기울기를 갱신
### Parametric ReLU (PReLU)
- 기존 ReLU 함수에서 음수값의 계수를 학습 가능한 파라미터로 지정한 Activation function 
### ReLU6
- 기존 ReLU 함수의 최대값을 6으로 지정하여 효율적인 최적화가 가능한 Activation function 
### Scaled Exponential Linear Unit (SELU)
- Self-normalizing 효과가 있어 Gradient exploding, Vanishing 문제를 방지하는 Activation function 
---

![[Pasted image 20240229154554.png|+grid]]![[Pasted image 20240229154606.png|+grid]]![[Pasted image 20240229154615.png|+grid]]
<center style="font-size: 14; opacity: 0.7;">Swish (좌), hard Swish (중간), Mish (우)</center>

### Swish
![[Pasted image 20240311143657.png|500]]

$$f(x)=x\cdot sigmoid(x)$$

- Sigmoid 함수에 입력값을 곱해준 형태로, 깊은 layer를 학습시킬 때 좋은 성능을 보이는 Activation function 
- 매우 깊은 신경망에서 ReLU 보다 높은 정확도를 달성
- 모든 배치 크기에 대해 Swish 는 ReLU 를 능가하며, 모든 $x<0$ 에 대해 함수를 감소시키거나 증가시키지 않음
- Bounded below, unbounded above 특징을 가짐
---
#### Hard-Swish
- 임베디드 기기에서는 Swish 함수에서 Sigmoid 에 대한 연산량이 높기 때문에 이러한 문제를 해결하기 위해 적용한 activation function 
---
### Mish
![[Pasted image 20240311143902.png|500]]

$$f(x)=x\tanh(softplus(x))=x\tanh(\ln(1+e^x))$$

- 약간의 음수를 허용하기 때문에 ReLU zero bound 보다 Gradient 를 더 잘 흐르게  함
- 연속적으로 미분이 가능하여 기울기 기반 최적화를 수행할 때 Loss 값이 Smoothing 되는 효과
- Unbounded above: 
	- 양의 값에 대해서 제한이 없기 때문에 Saturation 을 방지
	- Gradient vanishing 으로 인해 발생하는 학습 지연 문제를 해결
- Bounded below:
	- 음의 값이 -0.31 로 제한되어 있기 때문에 Strong regularization 효과가 있으며, Overfitting 을 감소시킬 수 있음
---
![[Pasted image 20240311145335.png|500]]

- Mish 의 Loss 값이 부드럽게 형성되어 있어 더 쉬운 최적화와 더 나은 일반화를 도와줌
- 넓은 Minima 구역을 갖고 있으며, 가장 낮은 Loss 값을 가짐
---
#### Comparison between Swish and Mish
![[Pasted image 20240311144214.png]]

$$\begin{align}
f'(x)&=sech^2(softplus(x))\cdot x\cdot sigmoid(x)+{f(x)\over x} \\\\
&=\Delta(x)\cdot swish(x)+{f(x)\over x}
\end{align}$$

- Mish 함수를 미분하면 Swish 함수 형태로 유도할 수 있음
- 기울기 값을 그대로 보존하는 ReLU 함수와 달리 Mish 함수는 $\Delta(x)$ 가 최적화 과정에서 기울기를 Smooth 하게 만들어 수렴을 더욱 쉽게 해주는 Preconditioner 로서 동작
- 수학적으로 무거운 모델인 Mish 는 Swish 확성화 함수의 시간 복잡성에 비해 계산 비용이 많이 든다는 단점 있음
---
### Comparison of ReLU series
![[Pasted image 20240311144020.png]]
![[Pasted image 20240311144025.png]]
![[Pasted image 20240311144030.png]]

- Swish 와 Mish 에 비해 ReLU 의 좌표의 스칼라 크기 사이의 Sharp transition 을 보여줌
- Smoother transition 은 보다 부드러운 최적화 기능을 제공하여 손실을 줄이면서 신경망을 일반화