# Stochastic Gradient Descent (SGD)

## 개요
Stochastic Gradient Descent(확률적 경사 하강법)는 전체 데이터셋 대신 무작위로 선택된 샘플(또는 미니배치)을 사용하여 가중치를 업데이트하는 최적화 알고리즘이다.

## 종류

### 1. Batch Gradient Descent
전체 데이터셋을 사용하여 gradient 계산
$$w = w - \eta \nabla_w L(w; X, y)$$

### 2. Stochastic Gradient Descent (SGD)
단일 샘플을 사용
$$w = w - \eta \nabla_w L(w; x_i, y_i)$$

### 3. Mini-batch Gradient Descent
미니배치(보통 32, 64, 128)를 사용
$$w = w - \eta \nabla_w L(w; X_{batch}, y_{batch})$$

## SGD 변형

### Momentum
이전 업데이트 방향을 기억하여 관성 추가
$$v_t = \gamma v_{t-1} + \eta \nabla_w L$$
$$w = w - v_t$$

### Nesterov Momentum
미래 위치에서 gradient 계산
$$v_t = \gamma v_{t-1} + \eta \nabla_w L(w - \gamma v_{t-1})$$

### AdaGrad
학습률을 파라미터별로 적응적으로 조절
$$w = w - \frac{\eta}{\sqrt{G_t + \epsilon}} \nabla_w L$$

### RMSprop
AdaGrad의 급격한 학습률 감소 문제 해결
$$E[g^2]_t = \gamma E[g^2]_{t-1} + (1-\gamma)g_t^2$$
$$w = w - \frac{\eta}{\sqrt{E[g^2]_t + \epsilon}} g_t$$

### Adam
Momentum + RMSprop
$$m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$$
$$w = w - \frac{\eta}{\sqrt{\hat{v}_t} + \epsilon}\hat{m}_t$$

## 비교

| Optimizer | 장점 | 단점 |
|-----------|------|------|
| SGD | 단순, 일반화 good | 느림, local minima |
| Momentum | 빠름, 진동 감소 | 하이퍼파라미터 필요 |
| Adam | 빠름, 적응적 학습률 | 일반화 성능 이슈 |

## 사용 예시 (PyTorch)
```python
import torch.optim as optim

# SGD with momentum
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
for epoch in range(epochs):
    optimizer.zero_grad()
    loss = criterion(model(x), y)
    loss.backward()
    optimizer.step()
```

## 관련 개념
- [[Back Propagation]]
- [[Loss Function]]
- [[Regularization]]
