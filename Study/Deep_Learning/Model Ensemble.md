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
# Model Ensemble
- **Definition**
	- 여러개의 모델을 결합하여 개별 모델보다 더 나은 예측 성능을 얻는 기법
	- 서로 다른 모델의 강점을 결합하여 일반화 성능을 높이고, 예측 오류를 줄임

<br>

## Adaptive Boosting (AdaBoost)

- **Definition**
	- 여러 약한 학습기(weak classifier)를 결합하여 강한 예측 성능을 얻는 기법.
	- 약한 학습기의 성능을 반복적으로 개선하여 높은 정확도를 가지는 강한 학습기 생성.

<br>

### **Key Components**
1. **Weak Classifier**: 
   - 약한 학습기 $f_t(x)$.
   - 예: 간단한 decision stump와 같은 약한 분류기.
     $$f_t(x) = \begin{cases} 
     -1 & \text{if } x_{it} < \theta_t \\ 
     1 & \text{otherwise} 
     \end{cases}$$
   
2. **Strong Classifier**: 
   - 여러 약한 학습기의 예측 결과에 모델 가중치($\alpha_t$)를 곱해 합산한 모델.
   - 최종 예측은 $F_T(x)$의 부호로 결정.
     $$F_T(x) = \sum_{t=1}^T \alpha_t f_t(x)$$
   
3. **Loss Factor ($\gamma$)**:
   - 데이터 포인트의 중요도를 나타내는 계수.
   - 학습 단계에서 오차 계수 $\gamma_t^{(i)}$는 데이터 포인트별로 업데이트:
     $$\gamma_1^{(i)} = 1, \quad \gamma_t^{(i)} = \exp(-y^{(i)} F_{t-1}(x^{(i)}))$$
   
4. **Model Weight ($\alpha$)**:
   - 각 약한 학습기의 모델 가중치.
   - 학습기의 성능(오차율 $\epsilon_t$)에 따라 계산되며, 성능이 좋을수록 높은 가중치를 가짐.
     $$\alpha_t = \frac{1}{2} \ln \left(\frac{1 - \epsilon_t}{\epsilon_t}\right)\qquad \epsilon_t = \frac{\sum_{i: y^{(i)} \neq f_t(x^{(i)})} \gamma_t^{(i)}}{\sum_{i} \gamma_t^{(i)}}$$

<br>

### **Mechanism**

1. **데이터 초기화**:
   - 데이터셋: $D = (x^{(i)}, y^{(i)})_{i=1,2,...,N}$.
     - $x^{(i)} \in \mathcal{X}$, $y^{(i)} \in \mathcal{Y} = \{-1, 1\}$.
   - 모든 데이터 포인트의 초기 오차 계수 $\gamma_1^{(i)} = 1$로 동일하게 설정.

2. **반복 학습 (t = 1, ..., T)**:
   - 약한 학습기 $f_t$를 학습하고, 오차율 $\epsilon_t$를 계산:
     $$\epsilon_t = \frac{\sum_{i: y^{(i)} \neq f_t(x^{(i)})} \gamma_t^{(i)}}{\sum_{i} \gamma_t^{(i)}}.$$
   - 오차율 $\epsilon_t$를 기반으로 모델 가중치 $\alpha_t$를 계산:
     $$\alpha_t = \frac{1}{2} \ln \left(\frac{1 - \epsilon_t}{\epsilon_t}\right).$$
   - 데이터 포인트 오차 계수 $\gamma_t^{(i)}$ 업데이트:
     $$\gamma_{t+1}^{(i)} = \gamma_t^{(i)} \cdot \exp\left(-\alpha_t y^{(i)} f_t(x^{(i)})\right).$$

4. **모델 업데이트**:
   - 강한 학습기 $F_t$는 이전 단계 결과에 현재 학습기의 결과를 가중치와 함께 추가:
     $$F_t(x) = F_{t-1}(x) + \alpha_t f_t(x).$$

5. **최종 예측**:
   - 최종 모델 $F_T(x)$를 생성.
   - 최종 예측은 $F_T(x)$의 부호로 결정:
     $$\text{sign}(F_T(x)).$$

<br>

### **Summary of Process**
1. 초기 가중치 설정: 모든 데이터 포인트에 동일한 $\gamma_1^{(i)} = 1$ 부여.
2. 약한 학습기를 학습하고, 오차율 $\epsilon_t$ 계산.
3. 오차율로 모델 가중치 $\alpha_t$ 계산.
4. 데이터 포인트 오차 계수 $\gamma_t^{(i)}$ 업데이트.
5. 최종 강한 학습기 $F_T(x)$ 생성 및 예측.

<br>

### **장점**
- 단순한 약한 학습기만으로도 높은 성능을 가진 강한 학습기를 생성 가능.
- 데이터 분포에 따라 동적으로 학습하며, 복잡한 데이터 분포에서도 효과적.

<br>

### General Observations on AdaBoost

$$\alpha_t = \frac{1}{2} \ln \left( \frac{1 - \epsilon_t}{\epsilon_t} \right)$$

- **조건에 따른 $\alpha_t$의 변화**

	1. **$\epsilon_t > \frac{1}{2}$일 때 ($\alpha_t < 0$):**
		- 이 경우, 해당 가설의 결과 부호를 반전시키면 오차율이 $\frac{1}{2}$ 미만으로 감소.
		- 즉, 부호 반전을 통해 앙상블의 성능을 개선할 수 있음.
	
	2. **$\epsilon_t = 0$일 때 ($\alpha_t = \infty$):**
		- 오차가 0인 가설은 완벽한 예측을 수행.
		- 단일 가설만으로도 앙상블을 구성하는 것이 최적임.
	
	3. **$\epsilon_t = \frac{1}{2}$일 때 ($\alpha_t = 0$):**
		- 해당 가설은 앙상블에 기여하지 않음.
		- 데이터 가중치가 이후 라운드에서도 변하지 않으며, 학습 진행에 영향을 미치지 않음.
		- $\epsilon_t = \frac{1}{2}$이 지속되면, 약한 가설 집합으로는 학습 데이터를 적합할 수 없음.

<br><br>

## Decision Tree
- **Definition**
	- 데이터를 규칙적으로 분할하여, 최종적으로 리프 노드에서 예측 결과를 도출하는 트리 구조 기반의 학습 모델
	- 루트 노드에서 시작해 조건에 따라 데이터를 분기하며, 최종적으로 리프 노드에 도달하면 예측 결과를 제공

![[Pasted image 20241118015301.png|500]]

<br>

### Key Concepts
- 분할 (Splitting)
	- 데이터를 특정 기준에 따라 하위 그룹으로 나누는 과정
	- 각 노드는 하나의 분기 규칙을 표현하며, 데이터의 특징 값을 기준으로 분할
	- Splitting Criteria
		- Gini 불순도
		  $$I(\mathcal{D}) = 1 - \sum_{c=1}^{C} p(c|\mathcal{D})^2$$
		- 엔트로피
		  $$I(\mathcal{D}) = -\sum_{c=1}^{C} p(c|\mathcal{D}) \log p(c|\mathcal{D})$$
		- 분류 오차
		  $$I(\mathcal{D}) = 1 - \max_{c} p(c|\mathcal{D})$$

- 정보 (Information)
	- 확률 변수 $X$의 정보량
	  $$I(X)=-\log{p(X)}$$
	- 특정 사건이 발생했을 때, 해당 사건이 얼마나 드문지(혹은 예상 밖인지)를 측정한 값.
	- 사건이 발생할 **확률** $p(X)$가 작을수록, 해당 사건이 더 드물기 때문에 정보량($I(X)$)은 커짐.

	```ad-example
	- 사건의 발생 확률이 $p(X) = 0.1$인 경우, 정보량은:
	  $$I(X) = -\log(0.1) = 1$$
	- 이는 해당 사건이 드물게 발생하므로 정보량이 높음을 의미
	```

- 엔트로피 (Entropy)
	- 확률 변수 $X$의 기대 정보량으로, 불확실성을 측정하는 지표
	  $$H(X) = \mathbb{E}[I(X)] = -\sum_{x \in \mathcal{X}} p(x) \log p(x)$$
	- 엔트로피는 데이터의 평균 정보량을 나타내며, 값이 클수록 불확실성이 높음을 의미
	- 사건 하나하나의 정보량($I(X)$)의 **기대값(average)**으로 정의됨.
	- 모든 사건의 확률이 **균등**할 때 엔트로피가 최대.
	- 데이터 $X$를 표현하기 위한 최소 평균 비트 수

```ad-example
- 사건들이 발생할 확률이 각각 $p(1) = 0.5$, $p(2) = 0.5$인 경우,
  $$H(X) = -[0.5 \log(0.5) + 0.5 \log(0.5)] = 1$$
- 두 사건이 동일한 확률로 발생하므로 최대의 불확실성을 가짐
```

- 정보 이득 (Information Gain, IG)
	- 부모 노드와 자식 노드 간의 엔트로피 차이를 계산하여 분할의 효용성을 평가하는 지표
	  $$IG(\mathcal{D}, f) = I(\mathcal{D}) - \sum_{j=1}^{J} \frac{|\mathcal{D}_j|}{|\mathcal{D}|} I(\mathcal{D}_j)$$
	- 정보 이득을 최대화하여, 자식 노드의 엔트로피를 최소화

<br>

### Principle
- **일반적인 프레임워크**
	- 데이터 세트를 최적으로 분할할 변수를 선택
	- 선택된 규칙에 따라 데이터를 분할하고, 두 개의 노드를 추가하여 각 노드가 데이터 처리를 수행
	- 각 노드에 있는 데이터 포인트 수가 적당히 작아지면 리프 노드 통계를 계산하고 멈춤
- 정보와 엔트로피의 활용
	- 분할 전후의 엔트로피를 계산하여 분할의 효과를 평가
	- 엔트로피가 낮을수록 데이터의 불확실성이 감소하므로, 자식 노드의 엔트로피를 최소화하는 방향으로 분할
- 정보 이득 최대화
	- 정보 이득이 클수록 분할을 통해 얻은 이점이 크다는 것을 의미
	- 최적의 분할은 정보 이득을 최대화하는 분할