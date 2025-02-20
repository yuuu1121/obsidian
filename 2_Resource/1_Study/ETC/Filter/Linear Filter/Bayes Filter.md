---
date: 2024-02-13
status: Permanent
tags:
  - Study/Filter
aliases:
  - Linear Filter
  - Bayes Filter
  - 선형 필터
  - 베이즈 필터
reference: 
author:
  - JINSOL KIM
  - TaeYoung Kim
url:
  - https://gaussian37.github.io/autodrive-ose-bayes_filter/
  - https://taeyoung96.github.io/slam/SLAM_06/
  - https://slamwithme.oopy.io/8b08070b-2452-4ac0-8553-d0564644d7a7
---
# Bayes' Filter란?
- 베이즈 필터 (Bayes Filter)
	- [[Linear Kalman Filter|Kalman Filter]]와 Particle Filter 개념의 기초가 되는 필터
	- Bayes Theorem을 반복적으로 사용하여 시스템의 상태 (state)[^state]를 추정하는 확률 기반의 재귀 필터 (Recursive[^recursive] Filter)

[^state]: 우리가 추적하거나 예측하고자 하는 대상의 변수
[^recursive]: 지금 구한 Posterior가 다음 스템에서 Prior로 사용됨
## Related Notes
- [[Filter를 사용하는 이유]]
- [[Bayes' Theorem|Bayes' theorem]]
- [[Estimation Theory]]
- [[Law of Total Probability|Law of total probability]]
- [[Marginalization]]
- [[Markov Assumption]]
# Principle of Bayes' Filter
## Prediction Step
- 시스템의 **이전 상태** ($bel(x_{t-1})$)와 시스템 **제어값** ($u_t$)을 바탕으로 **현재 상태** ($x_t$)의 **사전 확률 분포** ($P(x_t|z_{1:t-1}, u_{1:t})$) 예측
	- 과거 정보를 바탕으로 미래 상태를 추정하는 단계
		$$P(x_t|z_{1:t-1}, u_{1:t})=\int P(x_t|u_t, x_{t-1})\cdot bel(x_{t-1}) dx$$
		- $x_t$: 시간 $t$에서의 상태
		- $z_{1:t}$: 시간 1부터 $t$ 까지의 모든 관찰 값
		- $u_{1:t}$: 시간 1부터 $t$ 까지의 모든 시스템 제어값
		- $P(x_t|u_t, x_{t-1})$: 상태 전이 확률, 이전 상태에서 제어값 $u_t$가 주어졌을 때 현재 상태로 변할 확률
		- $bel(x_{t-1})$: 이전 시간 단계에서의 사후 확률 (Posterior probability)
## Correction Step
- 새로운 관찰값 ($z_t$)를 사용하여 현재 상태의 사후 확률 분포를 업데이트
	- 새로운 정보를 통합하여 추정을 정제하는 과정
	  $$bel(x_t)=\eta P(z_t|x_t)P(x_t|z_{1:t-1}, u_{1:t})$$
		- $P(z_t|x_t)$: 관찰 likelihood로, 현재 상태가 주어졌을 때 새로운 관찰 데이터가 나타날 확률
## Example of Bayes' Filter
![[Pasted image 20240213140723.png|500]]
![[Pasted image 20240213140738.png|500]]
![[Pasted image 20240213140759.png|500]]
![[Pasted image 20240213140816.png|500]]
![[Pasted image 20240213140830.png|500]]


![[Pasted image 20240213140844.png]]
