---
date: 2025-02-27
status: Permanent
tags: Study/OpenCV
  - 
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---

### **PCA 투영 개념**

1. **PCA는 원본 데이터에서 가장 분산(Variance)이 큰 방향을 찾는다.**
2. **이 방향을 주성분 벡터(Principal Component Vector, eVects)라고 한다.**
3. **원본 데이터를 이 주성분 벡터(새로운 좌표축)로 변환하는 과정이 PCA 투영(Projection)이다.**

## **PCA는 2D 행렬을 입력으로 받는다.**

PCA(Principal Component Analysis)는 **행렬 연산(Matrix Operations)** 을 기반으로 한다.  
즉, PCA를 수행하려면 **N개의 샘플(데이터 포인트)과 M개의 특성(Feature)** 으로 구성된 **2D 행렬(데이터셋)** 이 필요해.

✅ **PCA 입력 형식:**

$X = \begin{bmatrix} x_{11} & x_{12} & x_{13} \\ x_{21} & x_{22} & x_{23} \\ x_{31} & x_{32} & x_{33} \\ \vdots & \vdots & \vdots \\ x_{N1} & x_{N2} & x_{N3} \end{bmatrix}$
- **각 행(Row)** = 하나의 샘플(픽셀)
- **각 열(Column)** = 하나의 특성(채널 값: R, G, B)

📌 **즉, PCA는 샘플들이 행(Row)로 나열된 2차원 행렬을 필요로 한다.**  
그러면, 3차원 이미지 데이터를 어떻게 2차원으로 변환할까?

---

## **📌 2️⃣ 이미지 데이터는 기본적으로 3차원 (Height × Width × 3)**

OpenCV에서 이미지를 읽으면 기본적으로 **(Height × Width × 3)** 형태의 3D 행렬이다.

`src.shape = (512, 512, 3)  # 512x512 크기의 RGB 이미지`

즉, `src`는 512x512 픽셀의 **3채널(RGB)** 이미지로 구성되어 있다.

하지만 **PCA는 2D 행렬을 입력으로 받기 때문에, 3D 행렬을 2D로 변환해야 한다.**

---

## **📌 3️⃣ 3D 이미지 데이터를 2D로 변환하는 이유**

`X = src.reshape(-1, 3)`

- `-1` → 자동으로 행 개수를 계산함 (**512×512 = 262144 개의 행**)
- `3` → **각 픽셀의 R, G, B 값을 각각 특성(feature)으로 변환**

📌 **즉, X는 (픽셀 개수, 3) 형태의 2D 행렬이 됨.**


`X.shape = (262144, 3)  # 512×512 개의 픽셀, 각 픽셀마다 3개 채널 (R, G, B)`

✅ **변환 후 데이터 구조**

$X = \begin{bmatrix} R_1 & G_1 & B_1 \\ R_2 & G_2 & B_2 \\ R_3 & G_3 & B_3 \\ \vdots & \vdots & \vdots \\ R_N & G_N & B_N \end{bmatrix}$
이제 각 행(Row)이 **한 개의 픽셀 데이터(샘플)** 가 되고,  
각 열(Column)이 **특성(feature) 값(R, G, B)** 가 되어 **PCA 적용 가능!** 🚀

---

## **📌 4️⃣ 고유벡터(Eigenvector) 행렬이 `3x3`인 이유**

PCA를 수행하면 **각 채널(R, G, B)의 분산을 분석하여 새로운 좌표축(주성분)을 찾음.**  
이 과정에서 **고유값(Eigenvalues)과 고유벡터(Eigenvectors)를 계산**하게 된다.

`mean, eVects = cv2.PCACompute(X, mean=None)`

- `eVects` → **주성분 벡터(고유벡터) 행렬**
- `eVects.shape = (3, 3)` → **3차원(RGB) 데이터이므로, 3개의 주성분(PC1, PC2, PC3)을 가짐.**

✅ **고유벡터 행렬의 구조**

$eVects = \begin{bmatrix} PC1_x & PC1_y & PC1_z \\ PC2_x & PC2_y & PC2_z \\ PC3_x & PC3_y & PC3_z \end{bmatrix}$

즉, **RGB 3채널을 새로운 좌표계(주성분 공간)로 변환하는 과정이기 때문에 `3x3` 행렬이 나오는 것!**

---

## **📌 5️⃣ PCA 투영 후 데이터 구조**

PCA 투영을 수행하면 원래 3D 데이터가 PCA 주성분 공간으로 변환됨.

`Y = cv2.PCAProject(X, mean, eVects)`

- `Y.shape = (262144, 3)` → **각 픽셀이 PC1, PC2, PC3로 변환됨.**
- **즉, 원래 RGB 채널이 새로운 PCA 좌표계(PC1, PC2, PC3)로 바뀐 것!**

📌 **PCA 좌표계에서 표현된 데이터**
$Y = \begin{bmatrix} PC1_1 & PC2_1 & PC3_1 \\ PC1_2 & PC2_2 & PC3_2 \\ PC1_3 & PC2_3 & PC3_3 \\ \vdots & \vdots & \vdots \\ PC1_N & PC2_N & PC3_N \end{bmatrix}$
---

## **📌 6️⃣ 왜 PCA 적용을 위해 데이터가 2D이어야 하는가?**

1. PCA는 **행렬 연산 기반 알고리즘**이며, **2차원 행렬(N×M) 형태로 데이터를 입력받아야 함**.
2. 원본 이미지(3D)는 **각 픽셀이 RGB 값(3차원 특징 벡터)을 가지므로, 이를 2D 행렬(N×3)로 변환해야 함**.
3. PCA를 적용하면 **RGB 채널이 새로운 PCA 좌표계(PC1, PC2, PC3)로 변환됨**.
4. PCA 결과로 **3x3 크기의 고유벡터 행렬이 생성되며, 각 RGB 채널이 새로운 주성분 방향으로 투영됨.**
