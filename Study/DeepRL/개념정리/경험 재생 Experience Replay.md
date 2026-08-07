---
title: "개념정리 — 경험 재생(Experience Replay)"
tags: [개념정리, DeepRL, 강화학습, DQN]
related: [[Chapter 06 - 심층 Q 네트워크 DQN]]
---

# 경험 재생 (Experience Replay)

> [!abstract] 한 줄 요약
> **경험 재생**은 에이전트가 겪은 (상태, 행동, 보상, 다음 상태) 경험들을 큰 저장소(리플레이 버퍼)에 쌓아두고, 학습할 때마다 그중 일부를 **무작위로** 뽑아 쓰는 기법이다. 최신 경험만 순서대로 학습시키면 생기는 문제를 해결한다.

## 1. 왜 필요한가 — SGD가 원하는 것과 RL이 주는 것의 충돌

신경망을 학습시키는 표준 방법인 **확률적 경사하강법(SGD)** 은 학습 데이터가 **[[IID 독립항등분포]]** (서로 독립이고 같은 분포에서 뽑힘)이길 기대한다. 그런데 강화학습 에이전트가 매 순간 얻는 데이터는 이 가정을 두 가지 방식으로 깨뜨린다.

1. **독립이 아니다.** 방금 겪은 경험과 그다음 경험은 같은 에피소드 안에서 서로 이어져 있어 매우 비슷하다(예: 공이 조금 움직인 화면 두 장).
2. **분포가 계속 바뀐다.** 지금 데이터는 "지금의 정책"으로 얻은 것인데, 정책은 학습되면서 계속 변한다. 즉 데이터를 뽑아온 분포 자체가 시시각각 달라진다.

> [!tip] 비유 — 벼락치기 vs 복습 카드 상자
> 시험 공부를 어제 배운 내용만 계속 순서대로 읽으면, 바로 앞뒤 내용이 너무 비슷해서 뇌가 "아, 이건 다 똑같은 얘기구나" 하고 착각하기 쉽다. 좋은 학습법은 그동안 배운 내용을 **카드 상자에 모아두고, 무작위로 섞어서** 복습하는 것이다. 그래야 새로 배운 것과 예전에 배운 것을 골고루, 편향 없이 익히게 된다. 경험 재생 버퍼가 바로 이 카드 상자다.

## 2. 구현 방식

이 챕터의 `ExperienceBuffer` 클래스는 파이썬 표준 라이브러리의 `collections.deque`(양방향 큐)를 이용한다.

```python
class ExperienceBuffer:
    def __init__(self, capacity: int):
        self.buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def append(self, experience: Experience):
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> tt.List[Experience]:
        indices = np.random.choice(len(self), batch_size, replace=False)
        return [self.buffer[idx] for idx in indices]
```

- `maxlen=capacity`: 버퍼가 꽉 차면 **가장 오래된 경험부터 자동으로 밀려나며 삭제**된다. 즉 최근 일정 개수의 경험만 유지하는 "고정 크기 큐"다.
- `append()`: 매 스텝 새 경험 하나를 저장.
- `sample()`: `np.random.choice`로 인덱스를 **중복 없이(replace=False)** 무작위로 뽑아, 그 인덱스에 해당하는 경험들을 리스트로 반환. 이렇게 뽑은 배치는 서로 다른 시점, 다른 에피소드에서 온 경험들이 뒤섞여 있으므로 원래 데이터보다 훨씬 IID에 가깝다.

이 책의 Pong 예제에서는 버퍼 크기(`REPLAY_SIZE`)를 10,000으로 설정한다. DeepMind의 원 논문은 백만 개짜리 버퍼(약 20GB)를 썼지만, Pong 하나만 풀기에는 그렇게 크지 않아도 충분하다.

## 3. 학습을 언제 시작할까

버퍼가 텅 비었거나 너무 적은 상태에서 샘플링하면 의미 있는 배치를 만들 수 없다. 그래서 `REPLAY_START_SIZE`(예: 10,000 프레임) 만큼 경험이 쌓일 때까지는 학습을 시작하지 않고, 그동안은 그냥 환경과 상호작용만 하며 버퍼를 채운다.

## 세 줄 정리
- RL 데이터는 서로 이어져 있고(비독립) 정책이 변하며 분포도 바뀌어(비정상) SGD의 IID 가정을 깬다.
- 경험을 버퍼(고정 크기 큐)에 모아두고, 학습 시 무작위로 뽑아 써서 이 문제를 완화한다.
- 오래된 경험은 자동으로 밀려나 삭제되며, 버퍼가 충분히 찰 때까지는 학습을 시작하지 않는다.
