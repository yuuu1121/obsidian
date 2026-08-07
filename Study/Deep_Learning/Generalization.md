---
date: 2024-11-15
status: Permanent
tags:
  - Study/DL
  - Study/Lecture/Machine-Learning
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Generalization
![[Pasted image 20241115080343.png]]

- **Definition**
    - 모델이 새로운 데이터를 잘 예측하는 능력
    - 학습 데이터와 분리된 테스트 데이터에서의 성능을 통해 평가
    - 일반화 성능은 모델 구조, 학습률, 최적화 방법 등 하이퍼파라미터에 크게 의존함
        - 모델의 복잡도가 증가하면 훈련 데이터에 대한 적합도는 높아지지만, 과적합 문제가 발생하여 일반화 성능이 떨어질 수 있음
- **Key Concept**
    - 과적합을 방지하고 일반화 성능을 높이기 위해, 학습 도중 **검증(Validation) 데이터셋**을 사용하여 모델의 성능을 평가함
        - 모델은 검증 데이터셋에서의 성능을 최대화하도록 학습을 진행함
        - 이렇게 검증된 모델은 테스트 데이터셋에서 높은 성능을 낼 가능성이 큼

<br>

## Hyperparameter Selection
### Cross Validation
![[Pasted image 20241115081312.png|500]]

- **Definition**
	- 데이터셋을 여러 분할로 나누어 각 분할마다 테스트를 수행하고, 결과를 평균하여 일반화 성능을 평가하는 방법
- **Limitation**
	- 테스트 셋에 하이퍼파라미터를 맞추는 문제가 발생할 수 있음

<br>

### Nested Cross Validation
![[Pasted image 20241115081502.png|300]]

- **Definition**
    - **검증(Validation) 데이터셋**에 맞춰 하이퍼파라미터를 조정하는 방법
    - 최종 테스트 셋은 모델이 절대 관측할 수 없기 때문에 일반화 성능을 보장
- **Limitation**
	- **Nested cross validation**은 데이터셋이 클 경우 시간이 많이 소요됨

<br>

### Train / Validation / Test
- **Definition**
	- 데이터셋이 매우 클 때 사용할 수 있는 간단한 해결책
		- 데이터를 **Train/Validate/Test** 세트로 나눔
		- **Validate** 세트를 기반으로 하이퍼파라미터를 선택
		- **Test** 세트에서 모델 성능 최종 평가

<br>

## Network Pruning

![[Pasted image 20241206152255.png|500]]

- **Definition**  
	- 각 레이어에서 중요도가 낮은 뉴런이나 시냅스를 가지치기(pruning)하여 모델을 경량화하는 기법.  
	- 모델 구조를 단순화하고 계산량, 메모리 사용량을 줄이며 추론 속도를 개선함.  

- **Key Concepts**  
	- 가지치기를 통해 과적합(Overfitting)을 방지하며, 적절히 수행된 가지치기는 테스트 성능을 향상시킬 수 있음.  
	- **Lottery Ticket Hypothesis**:  
		- Frankle & Carbin, "The lottery ticket hypothesis: Finding sparse, trainable neural networks" (2019).  
		- 가지치기된 모델 내부에는 학습 성능을 발휘하는 특정 중요한 가중치와 뉴런("복권 티켓")이 존재.  
		- 남은 가중치 비율이 적절하면 모델 성능이 초기의 복잡한 신경망과 동일하거나 더 우수할 수 있음.  

<br>

## Data Augmentation

- **Definition**  
	- 데이터셋을 확장하여 모델의 일반화 성능을 높이는 기법.  
	- 학습 데이터의 다양성을 인위적으로 증가시켜 과적합을 방지하고 새로운 데이터에 대한 성능을 개선.  

- **Key Concepts**  
	- **Image Augmentation**:  
		- 다양한 이미지 변환 기법을 통해 데이터셋을 확장.  
			- 예: 자르기, 대칭, 회전, 스케일 조정, 색상 변화 등.  
		- 데이터의 다양성을 증가시켜 모델이 새로운 데이터에 더 강건한 성능을 보이도록 도움.<br> 
		![[Pasted image 20241206152435.png|+grid]]![[Pasted image 20241206152444.png|+grid]]<br>
	- **Natural Language Augmentation**:  
		- 문장 내 단어를 유사한 의미를 가진 단어로 대체하여 데이터셋을 확장.  
			- 단어 임베딩(Word Embedding)을 활용하여 유사 단어로 대체. 
				- 예: "awesome" → "amazing", "fantastic".  
		- 데이터의 다양성을 높여 모델이 다양한 표현에 대해 더 잘 일반화되도록 도움.<br>
		![[Pasted image 20241206152510.png|+grid]]![[Pasted image 20241206152524.png|+grid]]