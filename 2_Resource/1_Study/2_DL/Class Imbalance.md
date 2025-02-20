---
date: 2024-03-12
status: Permanent
tags:
  - Study/DL
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
# Introduction
- Detector 들은 이미지 당 1~10 만 개의 Candidate location (Region of Interest, RoI) 를 생성하지만, 그 중 검출해야하는 객체를 포함한 RoI 는 극 소수
	- 즉, Foreground (Object) 와 Background 의 Imbalance 를 Class imbalance problem 이라 함

>1. 대부분의 RoI 는 학습에 쓸모없는 배경 (Easy negative) 이기 때문에 학습이 비효율적
>2. 배경이 학습에 영향을 줘서 객체를 검출하지 못하거나, 배경으로 검출하는 오검출을 야기
>	- Easy negative sample 을 제대로 예측하여도 몇몇 Loss function 의 경우 Loss 가 상당히 남아있기 때문에 Hard sample 의 Gradient 를 압도

---
# Solutions
## Common Solution - Hard Negative Mining
- 학습 도중 Hard negative sample (배경인데 객체라고 예측하기 쉬운 Sample) 을 Sampling 하여 학습에 다시 사용
---
## For 2-Stage Detector
- Two-stage cascade
	- Region proposals 를 추려내는 방법을 적용하여 대부분의 Background sample 을 걸러주는 방법
	- eg., [[Selective Search]], Edge boxes, Deep mask, Region Proposal Network (RPN)
- Sampling heuristic
	- Positive / Negative sample 의 수를 적절하게 유지하는 방법
	- eg., Hard negative sample, OHEM
---
## For 1-Stage Detector
- 2-Stage detector 에서의 해결방법은 1-Stage detector 에 적용하기 어려움
- 1-Stage detector 는 Region proposal 과정 없이 전체 이미지를 빽빽하게 순회하면서 Sampling 하는 Dense sampling 방법을 수행하기 때문에 훨씬 더 많은 후보 영역 생성
	- 즉, Class imbalance 문제가 2-Stage detector 보다 더 심각함
- Sampling heuristic 방법을 적용해도 여전히 배경으로 쉽게 분류된 Sample 이 압도적으로 많기 때문에 학습이 비효율적
---
**Related Notes**
- [[Focal Loss - Method of Focal Loss|Focal Loss]]
---
