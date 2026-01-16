---
date: 2024-02-13, 16:14
status: Permanent
tags:
  - Study/Filter
aliases:
  - Filter
  - 필터
reference: 
author: 
url:
---
## Filter를 사용해야하는 이유
- 자율주행을 위해선 주행 중 변수 감지와 주행 제어를 해야함
	- 이를 위해선 정확한 **지도 (map)**과 **위치 추정 (localization)**이 필요
- 문제는 확률 기반의 방법으로 차량의 위치를 추정하기 때문에 **오차**가 존재
	- 이 **오차를 줄이기 위해 필터 사용**