---
title: "개념정리 — Wrapper(래퍼) 패턴"
tags: [개념정리, DeepRL, Gym, 소프트웨어패턴]
related: [[Chapter 02 - OpenAI Gym API와 Gymnasium]]
---

# Wrapper(래퍼) 패턴

> [!abstract] 한 줄 요약
> **래퍼(Wrapper)** 는 원래 물건을 부수거나 새로 만들지 않고, **겉을 한 겹 감싸서** 기능을 추가하는 방법이다. 스마트폰 케이스를 씌우듯, 환경(`Env`) 을 그대로 두고 그 위에 "래퍼"라는 포장지를 씌워서 새 기능(관측 가공, 보상 조정, 행동 개입 등)을 추가한다.

## 1. 비유 — 스마트폰 케이스

스마트폰(원래 환경, `Env`) 자체를 뜯어고치지 않아도, **케이스를 씌우면** 기능이 추가된다.
- 방수 케이스 → 원래 안 되던 방수 기능 추가
- 배터리 케이스 → 배터리 용량 추가
- 케이스를 씌운 폰도 여전히 "폰"처럼 전화 걸고 받을 수 있다 (기존 기능은 그대로 유지)

Gym의 `Wrapper`도 마찬가지다. 원래 환경의 `step()`, `reset()` 같은 기능은 그대로 쓸 수 있으면서, 필요한 부분만 살짝 바꿔치기(가로채기)한다.

## 2. 왜 필요한가? — 구체적 상황들

- 환경이 주는 관측값(이미지 한 장)만으로는 부족해서, **최근 N장을 쌓아서** 에이전트에게 주고 싶을 때 (움직임 방향을 알려면 프레임 여러 장이 필요).
- 이미지를 자르거나(crop) 전처리하고 싶을 때.
- 보상 점수를 어떤 범위로 **정규화**하고 싶을 때.
- 탐험을 위해 에이전트의 행동을 가끔 무작위로 **바꿔치기**하고 싶을 때.

이런 "환경을 감싸서 무언가를 추가"하는 상황이 반복해서 나오기 때문에, Gym은 이를 위한 공통 틀인 `Wrapper` 클래스를 제공한다.

## 3. 클래스 구조

```
Env  (원본 환경)
 └─ Wrapper  (env를 감싸는 포장지, 자기 자신도 Env처럼 행동)
      ├─ ObservationWrapper   → observation(obs) 를 오버라이드
      ├─ ActionWrapper        → action(a) 를 오버라이드
      └─ RewardWrapper        → reward(r) 를 오버라이드
```

`Wrapper`는 `Env`를 **상속**한다([[API와 클래스·객체]]의 "상속" 참고). 그래서 래퍼로 감싼 결과물도 여전히 하나의 `Env`처럼 보이고 똑같이 쓸 수 있다 — 이것이 핵심이다. 래퍼를 씌운 환경에 또 다른 래퍼를 씌우는 것도 가능하다(케이스 위에 또 다른 케이스, 즉 **중첩**이 가능).

- `env`: 지금 감싸고 있는 바로 안쪽 환경(다른 래퍼일 수도 있음)
- `unwrapped`: 모든 래퍼를 다 벗겨낸, **진짜 원본** 환경

## 4. 세 가지 전문 래퍼

| 래퍼 종류 | 가로채는 대상 | 오버라이드할 메서드 |
|---|---|---|
| `ObservationWrapper` | 환경이 주는 관측값 | `observation(obs)` |
| `ActionWrapper` | 에이전트가 보내는 행동 | `action(a)` |
| `RewardWrapper` | 환경이 주는 보상 | `reward(r)` |

## 5. 예시 — 행동에 무작위성 섞기 (`ActionWrapper`)

```python
class RandomActionWrapper(gym.ActionWrapper):
    def __init__(self, env: gym.Env, epsilon: float = 0.1):
        super(RandomActionWrapper, self).__init__(env)  # 부모(Wrapper)의 초기화를 그대로 실행
        self.epsilon = epsilon   # 무작위 행동으로 바꿔치기할 확률(10%)

    def action(self, action: gym.core.WrapperActType) -> gym.core.WrapperActType:
        if random.random() < self.epsilon:              # 10% 확률로 주사위를 굴려
            action = self.env.action_space.sample()       # 원래 행동을 무시하고 무작위 행동으로 교체
            print(f"Random action {action}")
        return action                                     # 최종 행동을 환경에 전달
```

- `super().__init__(env)`: 부모 클래스(`Wrapper`)의 생성자를 호출해, "내가 감쌀 원본 환경이 이거야"라고 등록한다.
- `action()`: 에이전트가 보낸 행동을 가로채서, 10% 확률로 완전히 다른(무작위) 행동으로 바꿔치기한다.
- 이렇게 하면 에이전트가 원래 하려던 행동과 다른 행동을 가끔 하게 되어, [[상태 관측 에피소드 정책]]에서 다룬 **탐험(exploration)** 을 강제로 만들어낼 수 있다.

사용법은 원본 환경을 감싸주기만 하면 끝이다.

```python
env = RandomActionWrapper(gym.make("CartPole-v1"))
# 이제부터 env.step(action)을 호출하면, 내부적으로 10% 확률로 행동이 바뀐다.
```

## 세 줄 정리
- 래퍼 = 원본을 건드리지 않고 겉을 감싸 기능을 추가하는 포장지(스마트폰 케이스 비유)
- `ObservationWrapper`/`ActionWrapper`/`RewardWrapper` = 관측/행동/보상 중 하나만 골라 가로채는 전용 래퍼
- 래퍼로 감싼 결과물도 여전히 `Env`이므로, 여러 래퍼를 겹겹이 씌울 수 있다
