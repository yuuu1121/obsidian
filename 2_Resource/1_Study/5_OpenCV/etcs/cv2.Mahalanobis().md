---
date: 2025-02-27
status: Permanent
tags: 
  - Study/OpenCV
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---


- **데이터의 분포를 고려한 거리 측정 방법**으로, **데이터가 정규 분포를 따를 때 이상값(Outlier) 탐지에 사용**됨.
- 일반적인 **유클리드 거리(Euclidean Distance)** 와 달리 **공분산을 고려하여 거리 측정**.

### **마할라노비스 거리 공식**

$D_M(\mathbf{x}, \mathbf{y}) = \sqrt{(\mathbf{x} - \mathbf{y})^T \mathbf{S}^{-1} (\mathbf{x} - \mathbf{y})}$

- x\mathbf{x}x : 첫 번째 벡터 ( `v1 = [0, 0]` )
- y\mathbf{y}y : 두 번째 벡터 ( `v2 = [0, 50]` )
- S\mathbf{S}S : 공분산 행렬 ( `cov` )
- S−1\mathbf{S}^{-1}S−1 : 공분산 행렬의 역행렬 ( `icov` )

### **마할라노비스 거리 계산 과정**

1. **두 벡터의 차이 계산** $d = v1 - v2 = \begin{bmatrix} 0 \\ 0 \end{bmatrix} - \begin{bmatrix} 0 \\ 50 \end{bmatrix} = \begin{bmatrix} 0 \\ -50 \end{bmatrix}$
2. **차이를 전치 행렬로 변환** $d^T = \begin{bmatrix} 0 & -50 \end{bmatrix}$
3. **역공분산 행렬 적용** $d^T \cdot icov \cdot d$
4. **최종 마할라노비스 거리 계산** $D_M = \sqrt{d^T \cdot icov \cdot d}$