---
date: 2024-02-13, 16:28
status: Permanent
tags:
  - Study/Statistics
aliases:
  - State estimation
  - 추정 이론
reference: 
author: 
url:
---
# 추정 이론 (Estimation Theory)
- 측정 또는 관찰된 자료에 기반하여 모집단을 대표하는 값 (모수)를 추정하는 이론
- $t$ 라는 시간에서 로봇의 상태 $x$를 로봇의 관찰값 (observation, $z$)와 로봇의 제어값 (control command, $u$)에 의해서 결정하는 이론
> $$P(x_t|z_{1:t}, u_{1:t})$$
- 1부터 $t$까지 주어진 observation $z_{1:t}$와 control command $u_{1:t}$를 고려하여 $t$ 번째 로봇의 상태 $x_t$를 추정
- 위 식에 recursive의 의미를 붙여 로봇의 상태 $x_{t-1}$를 활용해 $x_t$를 추정