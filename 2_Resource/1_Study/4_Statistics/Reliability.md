---
date: 2024-05-06, 17:16
status: Permanent
tags:
  - Study/Statistics
aliases: 
keywords:
  - 신뢰도
related notes: 
reference: 
author: 
url:
---
# 신뢰도 (Reliability)
- <mark class="hltr-red">동일한 검사를 반복 시행했을 때 얼마나 안정적으로 일관성 있게 측정되었는 지에 대한 정도</mark><br>
  $R(t)$: $t$ 시간 후에도 시스템이 정상적으로 동작할 확률

---
## 직렬 연결 (Series Connection)
![[drawing240506_1.excalidraw]]

- 모든 모듈이 직렬로 연결되어 있으며 서로 기능 자체에 영향을 주지 않는다고 가정

>$$R(t)=R_1(t)\times R_2(t)\times\cdots\times \prod_{i=1}^nR_i(t)$$

---
## 병렬 연결 (Parallel Connection)
<br>

![[drawing240506_2.excalidraw|200]]

>$$R(t)=1-\prod_{i=1}^n(1-R_i(t))$$

