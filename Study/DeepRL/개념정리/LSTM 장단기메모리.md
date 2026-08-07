---
title: "개념정리 — LSTM(장단기 메모리, Long Short-Term Memory)"
tags: [개념정리, DeepRL, NLP, 신경망]
related: [[Chapter 13 - TextWorld 환경]]
---

# LSTM (장단기 메모리, Long Short-Term Memory)

> [!abstract] 한 줄 요약
> **LSTM**은 [[RNN 순환신경망]]의 개선판으로, "중요한 정보는 오래 기억하고 필요 없는 정보는 잊어버리는" 내부 게이트(문)를 추가해 긴 문장에서도 정보가 잘 전달되도록 만든 모델이다.

## 1. 기본 RNN의 한계 — 건망증

[[RNN 순환신경망]]은 문장이 길어지면 문제가 생긴다. 앞부분의 정보가 뒷부분까지 전달되는 동안 계속 "덮어써지면서" 점점 흐려지기 때문이다. 마치 전달 게임(귓속말 전달)에서 사람을 많이 거칠수록 처음 말이 왜곡되는 것과 비슷하다.

> [!tip] 비유 — 메모장과 형광펜
> 일반 RNN은 매번 메모장을 **통째로 다시 쓰는** 사람과 같다. 새 정보가 들어올 때마다 이전 메모가 뒤섞여 흐려진다. LSTM은 형광펜과 지우개를 가진 사람이다. "이 부분은 중요하니 계속 남겨두자(기억)", "이건 이제 필요 없으니 지우자(망각)", "이건 새로 적어 넣자(입력)"를 **각각 따로 판단**해서 메모장을 관리한다.

## 2. 게이트(gate) — LSTM의 핵심 아이디어

LSTM은 RNN과 마찬가지로 hidden state를 주고받지만, 내부에 **세 가지 게이트**를 추가로 둔다.

- **망각 게이트(forget gate)**: 이전 기억 중 무엇을 버릴지 결정
- **입력 게이트(input gate)**: 새로 들어온 정보 중 무엇을 기억에 추가할지 결정
- **출력 게이트(output gate)**: 지금 기억 중 무엇을 이번 출력으로 내보낼지 결정

각 게이트는 0~1 사이 값을 내는 작은 신경망으로, "얼마나 통과시킬지"를 조절하는 밸브 역할을 한다. 이 구조 덕분에 중요한 정보는 여러 단어를 거쳐도 손상되지 않고 오래(long) 유지되면서도, 최근의 단기(short-term) 정보도 함께 다룰 수 있다 — 그래서 이름이 "장단기(Long Short-Term) 메모리"다.

> [!note] LSTM의 역사
> LSTM은 1995년 Sepp Hochreiter와 Jürgen Schmidhuber가 처음 제안했고, 1996년 NIPS(현재의 NeurIPS) 학회에서 정식 발표되었다. RNN의 여러 문제(학습 불안정, 정보 소실)를 해결하기 위해 고안된, NLP 분야에서 오랫동안 표준으로 쓰인 모델이다.

## 3. 코드에서의 LSTM — 인코더로 쓰기

이 챕터의 `Encoder` 클래스는 `nn.LSTM`을 그대로 감싸서, 가변 길이 시퀀스를 고정 크기 벡터로 바꾸는 역할을 한다.

```python
class Encoder(nn.Module):
    def __init__(self, emb_size: int, out_size: int):
        super(Encoder, self).__init__()
        # emb_size: 입력 임베딩 벡터 크기, out_size: 출력(hidden state) 벡터 크기
        self.net = nn.LSTM(input_size=emb_size, hidden_size=out_size, batch_first=True)

    def forward(self, x):
        self.net.flatten_parameters()
        _, hid_cell = self.net(x)   # 시퀀스 전체를 LSTM에 통과
        return hid_cell[0].squeeze(0)  # 마지막 hidden state만 꺼내 반환
```

`self.net(x)`는 시퀀스의 매 단어마다 게이트 연산을 반복하며 hidden state를 갱신하고, 마지막 단어까지 처리한 뒤 **최종 hidden state**(`hid_cell[0]`)를 돌려준다. 이 벡터 하나가 "문장 전체를 압축한 고정 크기 표현"이 되어 DQN에 입력된다.

## 세 줄 정리
- LSTM은 RNN에 **망각·입력·출력 게이트**를 추가해, 무엇을 기억하고 무엇을 잊을지 스스로 조절한다.
- 이 덕분에 긴 문장에서도 중요한 정보가 잘 전달되어, RNN보다 안정적으로 학습된다.
- TextWorld 예제에서는 LSTM을 "인코더"로 써서, 방 설명·인벤토리 같은 가변 길이 텍스트를 고정 크기 벡터로 압축한다.
