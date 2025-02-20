---
date: 2024-11-15
status: Permanent
tags:
  - Study/DL
  - Study/Lecture/Machine-Learning
aliases: 
keywords:
  - CNN
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Convolutional Neural Network
- **Background**
	- **Fully Connected Network (FC Network)의 한계**
		- 다층 퍼셉트론([[Perceptron#Multi-Layer Perceptron MLP|MLP]])은 각 픽셀 위치를 독립적으로 처리하며, **지역성(locality)**을 고려하지 않음.<br>
		  ![[Pasted image 20241115084342.png|500]]
	- **매개변수 비효율성**:
		- 100x100 픽셀 이미지를 입력으로 사용할 경우, 입력 노드는 10,000개가 필요.
		- 은닉층에 50개 노드가 있다면 매개변수 수는 엄청나게 증가.
		- 이러한 이유로 MLP는 이미지 처리 문제에 적합하지 않음.
	
	- **Convolutional Neural Network**
		- CNN은 픽셀 간의 **지역성(locality)**을 활용하여 효율적으로 학습 가능.
		- **파라미터 공유**: 
			- 동일한 필터를 여러 위치에 적용하여 유사한 패턴(예: 가장자리, 형태)을 탐지.
		- **합성곱 연산**: 
			- 신호 처리에서 온 합성곱 연산을 활용해 지역 패턴을 효과적으로 학습.

<br>

- **Definition**
	- CNN(Convolutional Neural Network)은 이미지나 시계열 데이터와 같은 **공간적, 시간적 패턴을 가진 데이터**에서 특징을 추출하는 딥러닝 모델.  
	- CNN의 패턴 인식 방식은 인간의 **시각 신경 시스템**과 유사하며, **복측 시각 경로(Ventral Visual Pathway)** 가설을 통해 설명 가능.  

	- **인간 시각 처리 과정**:  
		- 빛이 망막에 도달하면 간단한 신호로 변환되고, 이후 점차 복잡한 신호로 처리됨.  
		- 동물 실험 결과, 뇌의 얕은 부분은 **단순한 패턴(예: 선, 모양 등)**에 반응하고, 깊은 부분은 **더 복잡한 형태**에 반응하는 것이 관찰됨.  
	
	- **Convolutional Neural Network**:  
		- 초기 레이어에서는 단순한 필터가 적용되어 **기본적인 패턴(엣지, 선 등)**이 활성화됨.  
		- 깊은 레이어로 갈수록 더 복잡한 특징(예: 형태, 객체 등)이 활성화됨.<br>

![[Pasted image 20241115084454.png|500]]![[Pasted image 20241115084829.png|500]]
<br>

- Key Concepts
	- **Convolutional Operation**  
	- 입력 데이터에 **[[kernel)](Kernel Trick.md|커널(kernel)]]**을 적용해 **특징 맵(feature map)**을 생성.  
	- **커널(kernel)**는 CNN에서 학습되는 매개변수로, 특정 패턴(예: 엣지, 텍스처 등)을 인식하는 역할을 수행.  
	- **작동 원리**:  
		- 2차원 필터가 입력 이미지의 작은 영역(패치)에 적용됨.  
		- 필터와 패치의 값들을 요소별로 곱한 후 합산하여 하나의 값을 생성. 
		- 이 과정을 이미지 전체에 걸쳐 슬라이딩하면서 반복하여 특징 맵을 생성.  
	- 수식:  
	$$h^{[l]} = h^{[l-1]} * w^{[l]}$$
	```ad-example
	title: Edge Detecting Kernel
	- 특정 필터(예: $[1, 1, 1], [0, 0, 0], [-1, -1, -1]$)는 **수직 엣지**를 감지.  
	- 수평 방향에서 값의 차이가 큰 경우 높은 값을 생성하며, 수직 엣지가 있는 영역을 감지.  
	- 유사하게, **수평 엣지**나 **대각선 엣지**를 감지하는 필터도 설계 가능. 
	```
	<br>
	
	- **Pooling Operation**  
		- 특징 맵의 크기를 줄여 계산 효율을 높이고, 중요한 정보를 압축.  
		- **작은/지역적 변환에 대한 불변성(invariance)**을 제공하여, 입력 데이터의 작은 변화(노이즈, 위치 변동 등)가 출력에 큰 영향을 주지 않도록 함.  
	
		- **Pooling의 필요성**:  
			- CNN은 지역적 패턴을 탐지하지만, 중간 출력 차원이 높아질 수 있음.  
			- 최종 출력이 간단한 결과(예: 클래스 레이블)로 이어지도록, Pooling 레이어를 사용해 차원을 축소.  
	
		- **Pooling 방법**:  
			- **Max Pooling**:  
				- 각 패치에서 최대값을 선택해 출력, 노이즈 영향을 줄임.  
				- 예: 4x4 매트릭스를 2x2로 축소할 때, 각 섹션에서 최대값을 선택.
			- **Average Pooling**:  
				- 각 패치에서 평균값을 계산해 출력, 값을 분산 처리하여 안정성 증가.  

![[Pasted image 20241115085133.png|250]]  

<br>

- **Contributions**  
	- **지역성(locality)**을 활용하여 인접한 픽셀이나 데이터 포인트 간의 관계를 효과적으로 학습.  
	- CNN의 필터는 엣지나 형태와 같은 패턴을 감지하도록 설계되어, 효율적이고 효과적인 데이터 처리 가능.  
	- 파라미터 수를 줄임으로써 계산 효율을 높이고, 과적합을 방지.  