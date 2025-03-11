---
date: 2025-03-11
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

커널(Kernel) 또는 **필터(Filter)**는 **이미지 처리를 위해 사용하는 작은 행렬(matrix).**
이미지의 특정 영역(픽셀 주변 값)을 조합하여 새로운 값을 생성하는 데 사용.

입력 이미지 예시 (5×5 크기)
```
10   20   30   40   50  
60   70   80   90  100  
110 120 130 140 150  
160 170 180 190 200  
210 220 230 240 250  
```
**픽셀 `(2,2)`의 값을 계산할 때, 3×3 커널을 해당 위치에 적용**
![[3_Archive/1_Attachments/eabd8ee9776263c515bdd3c179e5e50a_MD5.jpeg|700]]
즉, 픽셀 `(2,2)`의 새로운 값은 `120`이 됨
