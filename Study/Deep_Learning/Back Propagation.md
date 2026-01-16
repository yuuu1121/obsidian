# Back Propagation (역전파)

## 개요
Back Propagation(역전파)은 신경망 학습에서 가중치를 업데이트하기 위해 사용되는 핵심 알고리즘이다. 출력층에서 계산된 오차를 입력층 방향으로 전파하면서 각 가중치의 기울기(gradient)를 계산한다.

## 원리

### 1. Forward Pass (순전파)
입력 데이터가 신경망을 통과하며 출력값을 계산한다.

$$y = f(Wx + b)$$

### 2. Loss 계산
예측값과 실제값의 차이를 [[Loss Function]]으로 계산한다.

$$L = \frac{1}{2}(y - \hat{y})^2$$

### 3. Backward Pass (역전파)
Chain Rule을 사용하여 각 가중치에 대한 손실 함수의 기울기를 계산한다.

$$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial w}$$

### 4. 가중치 업데이트
계산된 기울기를 사용하여 가중치를 업데이트한다.

$$w_{new} = w_{old} - \eta \frac{\partial L}{\partial w}$$

여기서 $\eta$는 learning rate이다.

## Chain Rule

다층 신경망에서 역전파는 Chain Rule을 반복 적용한다:

$$\frac{\partial L}{\partial w^{(l)}} = \frac{\partial L}{\partial a^{(L)}} \cdot \frac{\partial a^{(L)}}{\partial a^{(L-1)}} \cdots \frac{\partial a^{(l+1)}}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial w^{(l)}}$$

## Vanishing/Exploding Gradient 문제

- **Vanishing Gradient**: 기울기가 점점 작아져 학습이 느려짐
  - 해결: [[Activation Function|ReLU]], Batch Normalization
- **Exploding Gradient**: 기울기가 폭발적으로 커짐
  - 해결: Gradient Clipping, 적절한 가중치 초기화

## 관련 개념
- [[Stochastic Gradient Descent]]
- [[Activation Function]]
- [[Loss Function]]
- [[Neural Network]]
