---
date: 2024-03-11
status: Permanent
tags:
  - Study/DL
aliases: 
reference: 
author: 
url:
---
# Attention
![[Pasted image 20240311153327.png]]

- Attention 이란 문맥에 따라 집중할 단어를 결정하는 방식을 의미
---
## Attention 모델의 구조
### Encoder 와 Decoder
![[Pasted image 20240311153826.png]]

- Encoder: Input data 를 입력 받아 Context vector 로 압축하여 출력하는 역할
- Decoder: 압축된 Context vector 를 입력받아 Output data 를 출력

>정보를 압축해 연산량을 최소화

- Context vector 는 Encoder 의 마지막 RNN 셀에서만 나오므로, 그 전 RNN 셀들에 반영되지 않음
- Context vector 를 사용하면 연산량이 줄어든다는 장점이 있지만, 정보의 손실이 발생하는 문제 발생

>정보 손실 문제를 해결하기 위해 Attention 이라는 개념이 도입

![[Pasted image 20240311154132.png]]
![[Pasted image 20240311154137.png|350]]
<center style='font-size:14;opacity:0.7;'>RNN</center>

- RNN 은 Output 으로 Hidden state 가 출력되기 때문에 Encoder 와 Decoder 구조에서 각각의 Output 이 hidden state 형태로 출력됨
	- Encoder 의 경우 모든 RNN 셀의 Hidden state 들을 사용하는 반면, Decoder 의 경우 현재 RNN 셀의 Hidden state 만을 사용
	- 한/영 번역의 Attention 처럼 Target sequence 의 한 단어와 Source sequence 의 모든 단어의 Attention 상관관계를 비교하기 때문
- Encoder hidden state: Source sequence 의 Context vector (모든 문맥을 활용)
- Decoder hidden state: Target sequence 의 Context vector
---
## Attention Score
![[Pasted image 20240311154705.png]]

- Encoder hidden state 와 Decoder hidden state 를 Dot product 하여 Attention score 계산
	- RNN 셀 개수만큼 Score 나옴
---
## Attention Value
![[Pasted image 20240311154855.png]]

- 앞서 구한 Attention score 들을 Softmax 활성 함수에 대입하여 Attention distribution 을 생성
	- 각 Score 들의 중요도를 상대적으로 보기 쉽게 하기 위해
- Encoder hidden states 들을 방금 구한 Attention distribution 에 곱하고 전부 합하여 Attention value 행렬 계산 (Decoder 의 RNN 셀의 개수 만큼)

>즉, 각 문맥들 (Hidden state) 의 중요도 (Attention score) 를 반영하여 최종 문맥 (Attention value) 를 계산

![[Pasted image 20240311155427.png]]

- 마지막으로 Decoder 의 문맥을 추가하기 위해 Decoder hidden state 를 Attention value 와 Concatenation
- 추가적으로 성능을 향상하기 위해 tanh, softmax 활성화 함수를 이용해 학습을 시키면 최종적인 출력이 나옴

![[Pasted image 20240311155530.png]]

---
## 정리
- **Attention**: 모델의 성능 향상을 위해 문맥에 따라 집중할 단어를 결정하는 방식

- **Decoder hidden state**:  Target seqence의 문맥

- **Encoder hidden states**: Source seqence의 문맥(모든 문맥을 활용하겠다.)

1. Encoder hidden states들과 Decoder hidden state를 내적(dot product)하여 **Attention score**계산

2. Attention score에 softmax함수를 취하고 이를 다시 Encoder hidden states들과 곱한 다음 이를 합하여 **Attention value**계산

3. Attention value 행렬에 Decoder hidden state 행렬을 **쌓아 올리고(concatenate)** tanh, softmax함수를 통해 학습시키다.
