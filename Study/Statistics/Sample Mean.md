---
date: 2024-09-15
status: Permanent
tags:
  - Study/Statistics
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Sample Mean
- 표본 평균은 모집단의 [[Sample Mean|평균]]($\mathbb{E}[X]$)을 추정하기 위해 **샘플링**한 데이터들의 평균을 계산한 것
- 실제 평균(기대값)을 추정하는 중요한 방법중 하나

$$\text{Sample mean}=\frac{1}{n}\sum\limits_{i=1}^nx_i$$

<br>

# Law of Large Number
- 대수의 법칙은 **표본 평균**이 모집단의 기대값에 점점 가까워진다는 것을 보장하는 법칙
	1. 표본의 개수 $n$이 커질수록 표본 평균이 실제 평균 $\mathbb{E}[X]$에 가까워짐
	2. 모든 샘플이 서로 독립적이고, 분산([[Expectation and Moments#^zw2g48|variance]])이 유한하다면 수렴이 보장됨

$$\frac{1}{n} \sum_{i=1}^{n} x_i \xrightarrow{\text{probability}} E[X] \quad \text{as} \quad n \to \infty$$