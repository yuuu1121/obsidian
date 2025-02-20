---
date: 2024-02-13, 15:53
status: Permanent
tags:
  - Study/Filter
aliases:
  - Linear Filter
  - Kalman Filter
  - Recursive Filter
  - 선형 필터
  - 칼만 필터
  - 재귀 필터
reference: 
author:
  - Jbground
  - 미니맘바
  - 세인트 워터멜론
url:
  - https://blog.naver.com/ycpiglet/222139077774
  - https://pasus.tistory.com/104
  - https://jbground.tistory.com/82
---
# Kalman Filter란?
- 잡음이 포함되어 있는 과거와 현재의 측정치를 바탕으로 선형 시스템의 상태를 추정하는 재귀필터 (recursive filter)
  ![[Pasted image 20240213142628.png|300]]
- 최소 제곱법 (LSM, Least Square Method) 사용
  
- Assumption
	- 모션 모델과 측정 모델이 선형적 (linear)일 경우
	- 모션 모델과 측정 모델이 가우시안 분포를 따를 경우
	  ![[Pasted image 20240213143051.png|300]]
- 시스템이 선형이라는 가정하에 설계되었기 때문에 비선형 시스템에 적용하면 오차가 커지거나 발산해버리는 특성
	- 실제로 확장 칼만 필터 (Extended Kalman Filter)를 가장 많이 사용
	- 혹은 무향 칼만 필터 (UKF, Unscented Kalman Filter) 사용
	  ![[Pasted image 20240213143405.png|300]]
## Related Notes
- [[Filter를 사용하는 이유]]
- [[Bayes Filter]]
- [[Estimation Theory]]
# Principle of Kalman Filter
![[Pasted image 20240213144121.png|500]]
![[Pasted image 20240213143120.png|500]]

## Prediction Step 
- 이전 시간 $t-1$에 측정된 데이터 $\hat{x}_{t-1}$와 제어값 $u_t$를 이용해 다음 시간 $t$의 위치 추정값 $\hat{x}^-_t$를 예측
- 이전 시간의 추정값 $\hat{x}_{t-1}$이 얼마나 현재의 추정값 $\hat{x}^-_t$에 영향을 미칠 것 인가를 나타내는 **오차 공분산** $P_t^-$를 예측
	- 행렬 $A$: 노이즈가 없을 때 $\hat{x}_{t-1}$이 얼마나 $\hat{x}^-_t$에 영향을 미칠 것 인가를 나타내는 공분산 행렬
	- 행렬 $B$: 사용자 입력에 의한 상태 변화와 영향에 대한 보정값

$$\hat{x}_t^-=A\hat{x}_{t-1}+Bu_t$$
$$P_t^-=AP_{t-1}A^T+Q$$ ^LKFpred
## Measurement Update Step
- 예측값 $\hat{x}_t^-$와 오차 공분산 $P_t^-$, 칼만 이득 추정값 $K_t$를 바탕으로 추정값 $\hat{x}_t$ 계산
	- 칼만 이득
	  - 측정값 $\hat{x}_{t-1}$과 예측값 $\hat{x}_t^-$의 차이를 보상하기 위해 계산
	  - 측정값이 노이즈에 수렴하면 칼만 이득의 계산식에 의해 칼만 이득은 커지게 되며, 상태 추정 값의 계산에 칼만 이득 값이 많은 영향을 미치게 됨
- 예측한 값 $x_t$가 평균을 기준으로 어느 정도 분포되어있는지 오차 공분산 $P_t^-$를 통해 다음 시간의 $P_{t}$ 업데이트
- 추정값 $\hat{x}_t$와 오차 공분산 $P_{t}$는 칼만 필터의 **재귀적인 알고리즘**에 의해 다음 시간에 대한 위치 추정값을 구하는데 사용됨

$$K_t=P_t^-H^T(HP^-_kH^T+R)^{-1}$$
$$\hat{x}_t=\hat{x}_t^-+K_t(z_t-H\hat{x}_t^-)$$
$$P_t=(1-K_tH)P_t^-$$ ^LKFupdate
