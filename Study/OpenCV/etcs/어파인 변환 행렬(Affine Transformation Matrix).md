---
date: 2025-02-26
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
어파인 변환(Affine Transformation)은 **이미지의 평행성을 유지하면서 이동, 회전, 확대/축소, 기울이기(Shearing) 등의 변환을 수행하는 방법**.

OpenCV에서 어파인 변환을 수행하려면 **2×3 변환 행렬**을 사용.

---

### **어파인 변환 행렬의 형태**

어파인 변환을 나타내는 행렬 **M**은 다음과 같다.

$M = \begin{bmatrix} a & b & tx \\ c & d & ty \end{bmatrix}$

📌 **각 요소의 의미**

- a,b,c,d → 회전, 크기 조절, 기울이기(Shear)
- tx,ty → x축과 y축 방향으로의 이동(Translation)

이 행렬을 원본 이미지의 좌표 (x, y)에 적용하면 변환된 좌표 (x', y')가 계산.

$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} a & b \\ c & d \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} + \begin{bmatrix} tx \\ ty \end{bmatrix}$

---

