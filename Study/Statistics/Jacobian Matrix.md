# Jacobian Matrix (야코비안 행렬)

## 개요
Jacobian Matrix는 다변수 벡터 함수의 1차 편미분을 행렬로 나타낸 것이다. 비선형 변환의 국소적 선형 근사를 제공한다.

## 정의

함수 $\mathbf{f}: \mathbb{R}^n \rightarrow \mathbb{R}^m$가 있을 때:
$$\mathbf{f}(\mathbf{x}) = \begin{bmatrix} f_1(x_1, ..., x_n) \\ f_2(x_1, ..., x_n) \\ \vdots \\ f_m(x_1, ..., x_n) \end{bmatrix}$$

Jacobian Matrix $\mathbf{J}$는:
$$\mathbf{J} = \frac{\partial \mathbf{f}}{\partial \mathbf{x}} = \begin{bmatrix} \frac{\partial f_1}{\partial x_1} & \cdots & \frac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_m}{\partial x_1} & \cdots & \frac{\partial f_m}{\partial x_n} \end{bmatrix}$$

## 기하학적 의미

Jacobian은 변환에 의한 **부피 변화율**을 나타낸다:
$$dV' = |det(\mathbf{J})| \cdot dV$$

## 예시

### 극좌표 → 직교좌표
$$x = r\cos\theta, \quad y = r\sin\theta$$

$$\mathbf{J} = \begin{bmatrix} \frac{\partial x}{\partial r} & \frac{\partial x}{\partial \theta} \\ \frac{\partial y}{\partial r} & \frac{\partial y}{\partial \theta} \end{bmatrix} = \begin{bmatrix} \cos\theta & -r\sin\theta \\ \sin\theta & r\cos\theta \end{bmatrix}$$

$$det(\mathbf{J}) = r$$

## 응용

### 1. 적분 변수 변환
$$\int\int f(x,y) \, dx\,dy = \int\int f(r,\theta) |det(\mathbf{J})| \, dr\,d\theta$$

### 2. 로봇공학
엔드 이펙터 속도와 관절 속도의 관계:
$$\dot{\mathbf{x}} = \mathbf{J}(\mathbf{q})\dot{\mathbf{q}}$$

### 3. 최적화
Newton's Method에서 Hessian 계산

### 4. 확률 변환
확률 밀도 함수의 변환:
$$p_Y(y) = p_X(g^{-1}(y)) \cdot |det(\mathbf{J}_{g^{-1}})|$$

## 관련 개념
- [[Determinant]]
- [[Transformation]]
- [[Gradient Descent]]
