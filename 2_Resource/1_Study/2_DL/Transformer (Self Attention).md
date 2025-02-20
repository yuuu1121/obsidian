---
date: 2024-03-11, 15:56
status: Permanent
tags:
  - Study/DL
aliases: 
reference: 
author: 
url:
---
# Transformer
![[Pasted image 20240311160213.png|350]]

- Attention 만으로 이루어진 Encoder-Decoder 구조의 Sequence to sequence 모델
---
## Self Attention
![[Pasted image 20240311160320.png]]

- 말 그대로 Attention 을 자기 자신한테 취하는 방법
	- Attention 은 Input sequence 전체와 Target seq 단어 1개를 연결하는 반면, Self attention 은 Input seq 의 전체 단어들 사이를 연결
- 문장에서 단어들의 연관성을 알기 위해 사용
---
### Self Attention 과정
#### Query, Key, Value
![[Pasted image 20240311160513.png|+grid]]![[Pasted image 20240312091338.png|+grid]]

<center style='font-size:14;opacity:0.7;'>Query, Key and Value</center>

- Self attention 에는 Query, Key, Value 라는 3 가지 변수가 존재
	- Input seq 의 각 단어에 대해 Query, Key, Value vector 생성
	- 학습 과정에서 업데이트 되는 가중치 $W_Q, W_K, W_V$ 를 이용해 Input seq 의 각 단어 $X_n$ 에 대한 $q_n, k_n, v_n$ vector 생성
	- 실제 계산시엔 Input seq 전체 단어에 대한 행렬과 가중치 행렬을 사용하여 $Q, K, V$ 행렬로 계산
	- Self attention 에서 가장 중요한 개념은 Query, key, value 의 시작 값이 동일하다는 점
		- 때문에 Self 를 붙임
	- 중간에 학습 Weight 값에 의해 최종적인 Q, K, V 값은 서로 다르게 됨
- Query: 질문을 하는 주체 (문장의 단어, 이미지의 픽셀 등)
- Key: 답변을 해야하는 주체
	- $QK^T$ 는 한 단어와 모든 단어들의 Dot product 를 해줌으로써 Relation matrix 생성
- Value: 데이터의 값

---
![[Pasted image 20240311161401.png|500]]
![[Pasted image 20240311161409.png|500]]
![[Pasted image 20240312091722.png|300]]

---
#### Scaled Dot-product Attention
##### Attention Score
$$QK^T$$


- Query 와 Key 를 내적하여 둘 사이의 연관성을 나타내는 Relation matrix 계산
	- 이 Relation matrix 를 Attention score 라고 함

![[Pasted image 20240311174500.png|500]]

---
##### Scale
$$Score\over \sqrt{d_k}$$

- 만약 Query 와 Key 의 차원이 커지면 내적 값은 Attention score 도 커지게 되어 모델의 학습에 어려움이 생김
	- 이 문제를 해결하기 위해 차원 $\sqrt{d_k}$ 만큼 나누어 주는 스테일링 작업을 진행

---
#### Attention Value Matrix
$$softmax({score\over \sqrt{d_k}})V$$

- Attention score 를 정규화하기 위해 Softmax 활성 함수를 거치고, 마지막 보정을 위해 Score matrix 와 Value matrix 를 내적하여 Attention value matrix 생성
	- 집중하려는 단어의 값은 그대로 유지하고, 관련 없는 단어를 제외
---
## Multi-Head Attention
![[Pasted image 20240312093638.png]]

---
## 정리
- **Transformer**: Attention만으로 이루어진 encoder-decoder 구조의 seqence to seqence 모델. 현재 거의 모든 분야에서 최고의 성능을 자랑.

- **Attention**: 모델의 성능 향상을 위해 문맥에 따라 집중할 단어를 결정하는 방식.

- Self **Attention**: Attention중에서 자기 자신에게 Attention 메커니즘을 행하는 방식. (Query = Key = Value)

Self Attention

1. 원하는 문장을 임베딩하고 학습을 통해 각 Query, Key, Value에 맞는 weight들을 구해줌.

2. 각 단어의 임베딩의 Query, Key, Value(Query = Key = Value)와 weight를 점곱(내적)해 최종 Q, K, V를 구함.

3. Attention score 공식을 통해 각 단어별 Self Attention value를 도출

4. Self Attention value의 내부를 비교하면서 상관관계가 높은 단어들을 도출