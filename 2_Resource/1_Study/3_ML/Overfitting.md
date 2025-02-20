---
date: 2024-10-01
status: Permanent
tags:
  - Study/ML
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Overfitting
- 과적합은 매개변수의 수가 많아지거나 (모델의 복잡도가 높을 때) 매개변수의 크기가 지나치게 커질 경우 발생
	- 모델이 훈련 데이터에 지나치게 적합하여 새로운 데이터에 대한 일반화 성능이 떨어짐
	- 주어진 데이터에 대한 패턴을 학습하는 대신, 모델이 단순히 데이터를 암기하는 데 집중하여 발생
	- 과적합을 방지하기 위해선 [[Bayesian Inference|Bayesian Approach]]과 같이 사전 정보를 반영하거나, [[2_Resource/1_Study/3_ML/Regularization]] 처럼 학습 시 패널티를 추가하여 모델의 복잡도를 제어

![[Pasted image 20241001164405.png]]

