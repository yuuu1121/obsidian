# Determinant (행렬식)

## 개요
Determinant(행렬식)는 정방행렬에 대해 정의되는 스칼라 값으로, 행렬의 여러 중요한 특성을 나타낸다.

## 정의

### 2x2 행렬
$$det\begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc$$

### 3x3 행렬 (Sarrus 법칙)
$$det\begin{pmatrix} a & b & c \\ d & e & f \\ g & h & i \end{pmatrix} = aei + bfg + cdh - ceg - bdi - afh$$

### 일반 nxn 행렬 (여인수 전개)
$$det(A) = \sum_{j=1}^{n} (-1)^{i+j} a_{ij} M_{ij}$$

## 성질

1. **전치 행렬**: $det(A^T) = det(A)$
2. **곱셈**: $det(AB) = det(A) \cdot det(B)$
3. **역행렬**: $det(A^{-1}) = \frac{1}{det(A)}$
4. **스칼라 곱**: $det(cA) = c^n \cdot det(A)$ (n은 행렬 크기)
5. **행/열 교환**: 부호 변경

## 기하학적 의미

### 2D
평행사변형의 넓이 (부호 있는)

### 3D
평행육면체의 부피 (부호 있는)

### 일반
선형 변환에 의한 부피 확대/축소 비율

## 응용

### 1. 역행렬 존재 여부
$$det(A) \neq 0 \Leftrightarrow A^{-1} \text{ 존재}$$

### 2. 선형 연립방정식
- $det(A) \neq 0$: 유일한 해 존재
- $det(A) = 0$: 해가 없거나 무수히 많음

### 3. 고유값
$$det(A - \lambda I) = 0$$

### 4. 야코비안
좌표 변환 시 적분 계산:
$$\int\int f(x,y) \, dx\,dy = \int\int f(u,v) |det(J)| \, du\,dv$$

## 계산 방법

### LU 분해
$$det(A) = det(L) \cdot det(U) = \prod_{i} u_{ii}$$

### Python
```python
import numpy as np
det = np.linalg.det(A)
```

## 관련 개념
- [[Jacobian Matrix]]
- [[Transformation]]
- [[Eigenvalue]]
