---
title: "개념정리 — ExperienceSource와 리플레이 버퍼"
tags: [개념정리, DeepRL, PTAN, 리플레이버퍼]
related: ["[[Chapter 07 - 고수준 RL 라이브러리]]"]
---

# ExperienceSource와 리플레이 버퍼

> [!abstract] 한 줄 요약
> **ExperienceSource** 는 에이전트를 환경 속에서 계속 움직이게 하면서 "무슨 일이 일어났는지"를 조각조각(subtrajectory) 잘라서 건네주는 **자동 컨베이어 벨트**고, **리플레이 버퍼**는 그 조각들을 창고에 쌓아 두었다가 나중에 무작위로 꺼내 쓰는 **재고 창고**다.

## 1. ExperienceSource — 컨베이어 벨트

강화학습 훈련 루프의 뼈대는 항상 같다: 환경을 리셋하고 → 에이전트가 행동을 고르고 → 환경에 실행해서 보상과 다음 상태를 받고 → 이걸 반복하다가 에피소드가 끝나면 다시 리셋한다. `ExperienceSource`는 이 반복을 전부 대신해 준다. 파이썬의 **반복자(iterator)** 처럼 동작해서, `for exp in exp_source:` 형태로 순회하면 매번 새로운 경험 조각을 뱉어낸다.

```python
exp_source = ptan.experience.ExperienceSource(env=env, agent=agent, steps_count=2)
for idx, exp in zip(range(3), exp_source):
    print(exp)
```

- `steps_count=2`: 한 번에 **몇 스텝짜리 부분 궤적**을 만들지 지정한다. 2면 (상태, 행동, 보상, 상태, 행동, 보상) 두 스텝을 한 튜플로 묶어 준다.
- 매 반복마다 내부적으로는: 필요하면 `reset()` 호출 → 에이전트에게 행동을 물어봄 → `step()` 실행 → 결과를 기록 → 에피소드가 끝나면(`done_trunc=True`) 자동으로 다시 리셋, 이 과정이 계속된다.
- 튜플의 각 원소는 `Experience` [[데이터클래스 dataclass|dataclass]]이며 `state`(행동 전 상태), `action`(취한 행동), `reward`(즉시 보상), `done_trunc`(에피소드 종료 여부) 필드를 가진다.

> [!tip] 에이전트가 바뀌면 즉시 반영된다
> 신경망 가중치를 업데이트하거나 epsilon을 바꾸는 등 에이전트의 행동 방식이 바뀌면, 다음에 `ExperienceSource`에서 뽑는 경험도 **즉시 그 변화를 반영**한다. 학습이 진행될수록 더 똑똑한 행동에서 나온 경험을 얻게 되는 것.

### 여러 환경을 한 번에 돌리기

`env=[ToyEnv(), ToyEnv()]` 처럼 환경 리스트를 넘기면 **라운드로빈**(번갈아가며) 방식으로 여러 환경을 동시에 다룬다. 단, 반드시 **서로 독립된 환경 인스턴스**여야 한다 — 같은 인스턴스를 중복해서 넣으면 관측이 뒤섞여 엉망이 된다.

## 2. ExperienceSourceFirstLast — DQN에 딱 맞는 형태

`ExperienceSource`가 주는 전체 부분 궤적 `(s, a, r), (s', a', r'), ...`은 유연하지만, DQN 학습에는 조금 번거롭다. DQN의 벨만 근사에는 **(현재 상태, 행동, 보상, 다음 상태)** 딱 4개만 있으면 충분하기 때문이다.

`ExperienceSourceFirstLast`는 이를 위해 중간 스텝들을 접어서 하나의 `ExperienceFirstLast` 객체로 돌려준다:
- `state`: 행동을 결정할 때 봤던 상태 (궤적의 **첫** 상태)
- `action`: 그때 취한 행동
- `reward`: `steps_count` 스텝 동안 **누적(할인 합산)** 된 보상
- `last_state`: `steps_count` 스텝 뒤에 도달한 상태 (궤적의 **마지막** 상태). 에피소드가 그 사이에 끝났으면 `None`

```python
exp_source = ptan.experience.ExperienceSourceFirstLast(env, agent, gamma=1.0, steps_count=1)
```

`gamma`(할인율)를 넘기는 이유는, 여러 스텝을 하나로 접을 때 각 스텝의 보상을 **몇 스텝 전 것인지에 따라 할인해서 더해야** 하기 때문이다([[할인율 감마와 등비급수]] 참고). `last_state=None`인 샘플은 "에피소드가 여기서 끝났다"는 신호이므로, DQN 학습 시 이 상태 뒤에는 더 이상 미래 보상이 없다고 처리한다.

## 3. 리플레이 버퍼 — 재고 창고

DQN에서는 방금 얻은 경험을 바로 학습에 쓰지 않는다. 연속된 경험끼리는 서로 **너무 비슷해서(상관관계가 높아서)** 그대로 학습하면 훈련이 불안정해지기 때문이다. 그래서 경험을 **버퍼(창고)** 에 잔뜩 쌓아 두고, 학습할 때마다 그 안에서 **무작위로 한 묶음(batch)** 을 꺼내 쓴다.

PTAN이 제공하는 버퍼 종류:

| 클래스 | 특징 |
|---|---|
| `ExperienceReplayBuffer` | 정해진 크기의 단순 버퍼. 균등하게 무작위 샘플링 |
| `PrioReplayBufferNaive` | 우선순위 버퍼(중요한 경험을 더 자주 뽑음)의 간단한 구현. 샘플링 복잡도 $O(n)$이라 버퍼가 크면 느려짐 |
| `PrioritizedReplayBuffer` | 세그먼트 트리를 써서 $O(\log n)$ 복잡도로 빠르게 샘플링. 코드는 더 복잡함 |

사용법은 한결같다:
```python
buffer = ptan.experience.ExperienceReplayBuffer(exp_source, buffer_size=100)
buffer.populate(1)          # 경험 소스에서 1개 샘플을 뽑아 버퍼에 채워 넣기
batch = buffer.sample(4)    # 버퍼에서 4개짜리 배치를 무작위로 꺼내기
```

버퍼가 꽉 차면 오래된 샘플부터 자동으로 밀려난다. 훈련 루프는 이 두 메서드(`populate`, `sample`)만 반복 호출하면 된다 — 환경 리셋, 궤적 처리, 버퍼 용량 관리는 전부 자동이다.

> [!warning] 왜 이게 중요한가 — Atari 규모에서는 사소한 실수가 크게 번진다
> 장난감 문제에서는 버퍼 구현이 조금 비효율적이어도 티가 안 난다. 하지만 Atari처럼 샘플 하나하나가 이미지인 경우(수천만 개 샘플을 담아야 함), 작은 구현 실수가 **메모리 10~100배 증가**나 훈련 대폭 느려짐으로 이어질 수 있다.

## 세 줄 정리
- `ExperienceSource`는 에이전트-환경 상호작용을 자동 반복하며 부분 궤적을 뽑아 주는 반복자다.
- `ExperienceSourceFirstLast`는 DQN 학습에 바로 쓰기 좋게 (시작 상태, 행동, 누적 보상, 마지막 상태) 형태로 접어 준다.
- 리플레이 버퍼는 경험을 모아 뒀다가 무작위로 배치를 뽑아 학습 안정성을 높이는 창고 역할을 한다.
