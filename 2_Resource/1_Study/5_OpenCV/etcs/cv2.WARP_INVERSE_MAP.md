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
- 기본적으로 `cv2.warpAffine()` 함수는 변환 행렬 `M`을 **직접 적용**하여 변환을 수행.
- 그러나 `cv2.WARP_INVERSE_MAP`을 사용하면, `M`의 역행렬을 자동으로 계산하여 적용.
- `cv2.WARP_INVERSE_MAP`을 설정하면 **M을 직접 역행렬로 만들 필요 없이** OpenCV가 내부적으로 자동 변환.
