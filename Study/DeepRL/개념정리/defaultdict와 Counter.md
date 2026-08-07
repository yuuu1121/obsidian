---
title: "defaultdict와 Counter (파이썬 collections)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
tags: [DeepRL, 개념정리, 파이썬, 자료구조]
---

# defaultdict와 Counter

> [!abstract] 한 줄 요약
> 파이썬 표준 라이브러리 `collections` 모듈이 제공하는 딕셔너리 도구. **`defaultdict`는 "없는 키에 접근해도 에러 대신 기본값을 자동으로 채워주는" 딕셔너리**이고, **`Counter`는 "무언가를 셀 때 쓰는 전용 딕셔너리"** 다.

## 비유로 이해하기 — 자동으로 새 서랍을 만들어 주는 캐비닛

보통의 딕셔너리는 서랍장과 같다. 없는 서랍(키)을 열려고 하면 "그런 서랍 없음(`KeyError`)"이라고 에러를 낸다. 반면 `defaultdict`는 **없는 서랍에 손을 대는 순간 자동으로 빈 서랍을 만들어 주는 마법의 캐비닛**이다. 그래서 "이 서랍이 있는지 미리 확인하고, 없으면 만들고, 그다음에 값을 넣는" 번거로운 코드를 안 써도 된다.

## defaultdict — 없는 키는 자동으로 기본값

```python
from collections import defaultdict

values: dict = defaultdict(float)
print(values["아직없는키"])   # KeyError 대신 0.0 이 자동으로 나온다
values["아직없는키"] += 1.0   # 이런 식의 누적도 바로 가능
```

`defaultdict(float)`처럼 만들 때 **"기본값을 만드는 함수"**(여기선 `float`, 즉 `float()` → `0.0`)를 넣어준다. 이 챕터 코드에서는 이렇게 쓰인다.

```python
self.rewards: tt.Dict[RewardKey, float] = defaultdict(float)
self.values: tt.Dict[State, float] = defaultdict(float)
```

`self.values[state]`에 아직 한 번도 값을 넣은 적 없는 `state`로 접근해도, 에러 없이 그냥 `0.0`이 나온다. 즉 **"모든 상태의 초기 가치는 0"** 이라는 [[가치 반복 Value Iteration]]의 초기화 규칙을 코드 한 줄로 자연스럽게 구현한 것이다.

## Counter — 개수를 세는 전용 딕셔너리

`Counter`는 "어떤 것이 몇 번 나왔는지"를 세기 위한 특수한 딕셔너리다. 이 챕터에서는 **어떤 상태에서 어떤 행동을 했을 때, 실제로 어느 다음 상태로 도착했는지의 횟수**를 세는 데 쓰인다.

```python
from collections import defaultdict, Counter

self.transits: tt.Dict[TransitKey, Counter] = defaultdict(Counter)

# 상태 0에서 행동 1을 했더니 상태 4로 10번, 상태 5로 7번 도착했다면:
self.transits[(0, 1)][4] += 10   # 실제로는 매 스텝마다 1씩 누적
self.transits[(0, 1)][5] += 7
print(self.transits[(0, 1)])   # Counter({4: 10, 5: 7})
```

여기서 재미있는 점은 `defaultdict(Counter)` 처럼 **`defaultdict`의 기본값 자체가 또 다른 `Counter`(딕셔너리)** 라는 것이다. 그래서 `self.transits[state, action][new_state] += 1`처럼, 중첩된 키에 곧바로 값을 누적해도 에러가 나지 않는다.

> [!tip] 왜 이 조합이 편리한가?
> 이 챕터의 목표는 **환경과 상호작용한 경험만으로 전이 확률을 추정**하는 것이다(실제 확률표를 모르니까). `defaultdict(Counter)`로 "얼마나 자주 어디로 갔는지"를 셀 수 있으면, 그 값을 총합으로 나누기만 해도 바로 확률 추정치가 된다: `count / total`. 만약 일반 딕셔너리를 썼다면 "이 키가 있는지 먼저 확인" 하는 코드를 매번 추가해야 했을 것이다.

## 세 줄 정리
- `defaultdict`는 없는 키에 접근해도 에러 대신 지정한 기본값을 자동으로 채워주는 딕셔너리다.
- `Counter`는 개수를 세기에 특화된 딕셔너리이며, `defaultdict(Counter)`처럼 중첩해서 "여러 카테고리별로 각각 세기"에 자주 쓰인다.
- 이 챕터에서는 이 조합으로 상태 가치 초기값(0)과 전이 횟수 카운트를 간결하게 구현한다.
