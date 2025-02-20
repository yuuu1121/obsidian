---
date: 2024-02-25, 16:32
status: Permanent
tags:
  - Study/DL/RegionProposal
aliases: 
reference: 
author:
  - 정이는 성장중
url:
  - https://velog.io/@qtly_u/Object-Detection-Architecture-1-or-2-stage-detector-%EC%B0%A8%EC%9D%B4
---
![[Pasted image 20240225163528.png]]

- 이미지에서 동일한 질감, 색, 강도 등을 갖는 인접 픽셀을 찾아서 물체가 있을 법한 영역을 찾는 방법
- 이미지 전체를 Convolution 하지 않고 입력 이미지 중 초록색 영역만 가지고 검사하도록 하여 훨씬 효율적으로 Classification 수행