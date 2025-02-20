---
date: 2024-02-13
status: Permanent
tags:
  - Study/Filter
aliases:
  - 확장 칼만 필터
  - Extended Kalman Filter
  - EKF
reference: 
author:
  - 짜장범벅
url:
  - https://velog.io/@zajangbumbuck/%EC%B9%BC%EB%A7%8C-%ED%95%84%ED%84%B0%EB%8A%94-%EC%96%B4%EB%A0%B5%EC%A7%80-%EC%95%8A%EC%95%84-12-%ED%99%95%EC%9E%A5-%EC%B9%BC%EB%A7%8C-%ED%95%84%ED%84%B0
---
# Extended Kalman Filter란?
- 칼만필터를 비선형 시스템까지 확장한 필터
	- 비선형 시스템을 하나의 기준점 주위에서 선형화[^linearlization]시켜 얻은 선형 모델 $A$와 $H$ 사용
- 기준점 근처에서만 실제 시스템과 비슷한 특성
- 발산할 위험이 있음

[^linearlization]: Talyer Expension을 사용 (교차 검증 필요)
## Related Notes
- [[Filter를 사용하는 이유]]
- [[Estimation Theory]]
- [[Linear Kalman Filter]]
# Principle of Extended Kalman Filter
## Non-linear System Model
$$x_t=f(x_{t-1})+g(u_t)+w_{t-1}$$
$$z_t=h(x_t)+v_t$$
### Linear Kalman Filter
![[Linear Kalman Filter#^LKFpred]]
![[Linear Kalman Filter#^LKFupdate]]
## Extended Kalman Filter
**$$\hat{x}_t^-=f(\hat{x}_{t-1})+g(u_t)$$**$$P_t^-=AP_{t-1}A^T+Q$$ $$K_t=P_t^-H^T(HP^-_kH^T+R)^{-1}$$
**$$\hat{x}_t=\hat{x}_t^-+K_t(z_t-h(\hat{x}_t^-))$$**$$P_t=(1-K_tH)P_t^-$$ ^EKF
- 선형 알고리즘의 모델식 $Ax_t$와 $H_t$자리에 비선형 모델의 관계식 사용
	- 단 시스템의 행렬 $A$와 $H$는 시스템의 모델에서 받아와야 함
	- 즉, 비선형 모델을 이용해 행렬을 유도해야 함
$$A=\frac{\partial f}{\partial x}|_{\hat{x}_t}\qquad H=\frac{\partial h}{\partial x}|_{\hat{x}_t}$$