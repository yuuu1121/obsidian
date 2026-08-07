---
title: "LSTM과 패킹된 시퀀스"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
tags: [DeepRL, 개념정리, LSTM, RNN, PackedSequence, 임베딩]
---

# LSTM과 패킹된 시퀀스

> [!abstract] 한 줄 요약
> **LSTM(Long Short-Term Memory)** 은 문장처럼 순서가 있는 데이터를 "기억하며" 처리하는 신경망이고, **패킹된 시퀀스(packed sequence)** 는 길이가 제각각인 문장들을 효율적으로 한 번에 처리하기 위한 PyTorch의 데이터 형식이다.

## LSTM이란?

일반 신경망은 입력을 한 번에 통째로 본다. 하지만 문장은 **순서가 중요**하다. "나는 밥을 먹었다"와 "밥을 나는 먹었다 을"은 완전히 다른 문장이다. 이런 순서 있는 데이터(시퀀스)를 처리하기 위한 신경망이 **RNN(순환 신경망, Recurrent Neural Network)** 이고, LSTM은 그중 가장 널리 쓰이는 개선된 버전이다.

> [!example] 비유
> 책을 한 글자씩 읽어나가는 사람을 생각해 보자. 매 순간 지금 읽은 글자뿐 아니라 "지금까지 읽은 내용에 대한 기억"을 머릿속에 유지하면서 다음 글자를 읽는다. LSTM도 마찬가지로, 문장을 단어(토큰) 하나씩 읽으면서 "지금까지의 문맥을 요약한 은닉 상태(hidden state)"를 계속 갱신해 나간다. 예를 들어 "Select Egypt, Puerto Rico"라는 지시문을 다 읽고 나면, LSTM의 최종 은닉 상태에는 "이집트와 푸에르토리코를 골라야 한다"는 의미가 압축되어 담긴다.

## 임베딩(Embedding)

컴퓨터는 "Truman"이나 "Egypt" 같은 글자를 그대로 계산할 수 없다. 그래서 먼저 각 단어(토큰)를 정수 ID로 바꾸고(`token_to_id`), 그 ID를 **임베딩 레이어**(`nn.Embedding`)에 통과시켜 **의미를 담은 숫자 벡터**로 변환한다. 마치 사전에서 단어를 찾아 그 단어의 "좌표"를 얻어오는 것과 비슷하다. 비슷한 의미의 단어일수록 벡터 공간에서 가까운 위치에 놓이도록 학습된다.

## 패킹된 시퀀스(Packed Sequence)가 필요한 이유

한 배치(batch) 안에는 "Click ONE"처럼 짧은 문장도 있고 "Select 10/18/2016 as the date and hit submit"처럼 긴 문장도 있다. 신경망은 보통 배치 안의 모든 데이터가 **같은 크기**이길 요구하므로, 짧은 문장 뒤에 빈 자리를 채우는 **패딩(padding)** 을 한다.

문제는 패딩으로 채운 빈 자리까지 그대로 계산하면 **낭비**라는 점이다. `pack_padded_sequence` 함수는 "이 배치는 원래 이런 길이들이었다"는 정보를 따로 담아, RNN이 실제 데이터가 있는 부분만 효율적으로 계산하도록 도와준다. 이를 위해 먼저 **문장 길이가 긴 순서대로 정렬**해야 한다(`tokens_batch.sort(key=lambda p: len(p[1]), reverse=True)`) — 이것이 cuDNN 라이브러리가 요구하는 처리 방식이다.

```python
seq_v = torch.LongTensor(seq_arr).to(self.device)
seq_p = rnn_utils.pack_padded_sequence(seq_v, lens, batch_first=True)
```
이 코드는 정수 ID로 채워진 행렬(`seq_arr`, 크기: 배치 크기 × 가장 긴 문장 길이)을 텐서로 바꾸고, 각 문장의 실제 길이(`lens`)와 함께 패킹된 형태로 묶는다.

## 세 줄 정리

- LSTM은 문장처럼 순서 있는 데이터를 한 토큰씩 읽으며 문맥을 기억하는 신경망이다.
- 임베딩은 단어(정수 ID)를 의미를 담은 숫자 벡터로 바꿔주는 변환이다.
- 패킹된 시퀀스는 길이가 다른 문장들을 패딩 낭비 없이 배치로 묶어 RNN에 효율적으로 넣기 위한 PyTorch 데이터 형식이다.
