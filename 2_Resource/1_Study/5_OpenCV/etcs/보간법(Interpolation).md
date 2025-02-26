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
이미지를 변환(회전,이동,확대,축소 등)할 때, 새로운 픽셀 값을 어떻게 계산할지를 결정하는 방법.
OpenCV에서는 다음과 같은 보간법을 제공:
- `cv2.INTER_NEAREST` : 최근접 이웃 보간 (빠르지만 품질이 낮음)
- `cv2.INTER_LINEAR` : 선형 보간 (기본값, 속도와 품질이 균형 잡힘)
- `cv2.INTER_CUBIC` : 3차 회선 보간 (품질이 더 좋지만 느림)
- `cv2.INTER_LANCZOS4` : Lanczos 보간 (고품질 확대/축소)

