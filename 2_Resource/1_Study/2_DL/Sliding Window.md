---
date: 2024-02-25, 16:38
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
![[Pasted image 20240225163835.png]]

- 검출하고자하는 입력 이미지에서 정해진 크기의 Window를 만들어 방향을 이동하면서 물체가 있을 법한 Box나 영역을 추출
- 모든 영역을 탐색해야 하기 때문에 시간이 많이 소요되어 비효율적