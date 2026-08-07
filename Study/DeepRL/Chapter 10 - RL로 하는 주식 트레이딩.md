---
title: "Chapter 10 — RL로 하는 주식 트레이딩 (Stocks Trading Using RL)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 10
tags: [DeepRL, 강화학습, DQN, 주식트레이딩, 금융, Gym환경직접구현, Dueling]
---

# Chapter 10 · RL로 하는 주식 트레이딩

> [!abstract] 이 챕터를 한 문장으로
> 지금까지 배운 **DQN**을 아타리 게임이 아닌 **주식 시장**이라는 완전히 다른 현실 문제에 적용해보는 챕터다. 새로운 RL 알고리즘은 등장하지 않는다 — 대신 **"관측·행동·보상을 어떻게 설계할 것인가"**라는, 실전에서 RL을 쓸 때 가장 먼저 부딪히는 질문을 처음부터 끝까지 직접 풀어본다.

---

## 들어가며 — 왜 굳이 트레이딩인가?

이 책을 여기까지 읽어온 여러분은 이제 "장난감 문제(toy problem)"를 푸는 법은 충분히 안다. 카트폴을 세우고, 아타리 게임의 벽돌을 깨고, 그 모든 걸 DQN으로 해냈다. 이번 챕터는 **새로운 알고리즘을 배우는 자리가 아니다.** 저자가 직접 밝히듯, 이 코드가 여러분을 주식으로 부자로 만들어줄 거란 약속은 절대 아니다. 목표는 훨씬 소박하다 — **"아타리를 벗어나서, RL을 전혀 다른 실전 영역에 어떻게 적용하는지"** 를 보여주는 것.

이번 챕터에서 할 일은 두 가지다.
1. 주식 시장을 흉내 내는 **나만의 OpenAI Gym 환경**을 직접 구현한다.
2. 6장·8장에서 배운 **DQN**을 그 환경에 적용해, 이익을 최대화하도록 에이전트를 학습시킨다.

> [!note] 왜 하필 트레이딩인가?
> 세상에는 매일 거래되는 금융 상품이 수없이 많다 — 상품(goods), 주식, 통화, 심지어 날씨조차 "날씨 파생상품"이라는 형태로 사고판다(농사를 짓는 사업이라면 미래 날씨가 곧 돈이니까!). 이 모든 것에는 시간에 따라 변하는 **가격**이 있다.
>
> **트레이딩(trading)**이란 이런 금융 상품을 사고파는 행위다. 목적은 다양하다 — 이익을 남기려는 **투자(investment)**, 미래 가격 변동의 위험을 줄이려는 **헤징(hedging)**, 아니면 그냥 필요해서 사는 것(철강을 사거나, 계약금을 내려고 원화를 달러로 바꾸거나). 사람들은 금융시장이 생긴 이래로 계속 "미래 가격이 어떻게 될까"를 맞히려고 애써왔다 — 그게 되면 "공짜로 돈을 버는" 것과 다름없으니까. 그래서 수많은 애널리스트·펀드·은행·개인 트레이더가 이 문제에 매달린다.

질문은 이거다: **이 문제를 RL의 시각으로 볼 수 있을까?** 시장에 대한 어떤 관측이 있고, 우리는 "사자(buy) / 팔자(sell) / 기다리자(wait)"를 결정해야 한다. 가격이 오르기 전에 샀다면 이익(양의 보상), 아니라면 손해(음의 보상)다. 최대한 많은 이익을 얻는 것이 목표. 트레이딩과 RL의 연결고리는 꽤 명백하다. 이제 문제를 더 정확히 정의해보자.

---

## 1. 문제 정의와 핵심 결정 사항 (Problem Statement and Key Decisions)

금융이라는 분야는 넓고 복잡해서, 파고들자면 매일 새로운 걸 배우며 몇 년을 보낼 수도 있다. 이 챕터에서는 딱 겉핥기만 한다 — **가격 하나만을 관측으로 삼는, 최대한 단순한 형태**로 문제를 만든다. 우리 에이전트가 배울 것은 "언제 주식 한 주를 사서, 언제 포지션을 닫아(팔아) 이익을 극대화할 것인가" 하나뿐이다. 이 예제의 목적은 RL 모델이 얼마나 유연한지, 그리고 실전 문제에 RL을 적용할 때 보통 어떤 첫걸음을 밟아야 하는지를 보여주는 데 있다.

> [!important] RL 문제를 만드는 3요소
> 어떤 문제든 RL로 풀려면 다음 3가지가 필요하다.
> 1. **환경에 대한 관측(observation)**
> 2. **가능한 행동(action)들**
> 3. **보상 시스템(reward system)**
>
> 지금까지의 챕터에서는 이 3가지가 이미 다 주어져 있었고, 환경 내부는 우리가 몰라도 되는 "블랙박스"였다. 하지만 이번엔 상황이 다르다. **이 3가지를 우리가 직접 설계해야 한다.** 보상 체계도 엄격한 규칙집이 아니라, 우리의 직관과 금융 도메인 지식을 바탕으로 스스로 정해야 한다.

이 자유로움(flexibility)은 양날의 검이다. 좋은 점은, 에이전트가 학습에 유용하다고 생각되는 정보를 뭐든 줄 수 있다는 것 — 가격뿐 아니라 뉴스나 중요한 통계치를 줄 수도 있다(실제로 이런 것들이 금융시장에 큰 영향을 준다고 알려져 있다). 나쁜 점은, 이 자유로움 때문에 좋은 에이전트를 찾으려면 **데이터 표현 방식을 여러 가지로 실험**해봐야 하고, 어느 것이 더 잘 통할지 미리 알기가 어렵다는 것이다.

### 1.1 관측·행동·보상 설계

이 책에서는 1장에서 논의했던 형태 그대로, **가장 단순한 형태의 트레이딩 에이전트**를 구현한다.

**관측(Observation)** — 다음 정보를 포함한다.
- 과거 N개 바(bar)의 시가(open)·고가(high)·저가(low)·종가(close)
- 지금 주식을 보유하고 있는지 여부(플래그)
- 현재 포지션에서 나고 있는 손익(수익률)

**행동(Action)** — 매 스텝(1분 봉이 끝날 때마다), 에이전트는 다음 중 하나를 고른다.
- **아무것도 안 함(Skip)**: 그냥 이번 바를 넘긴다.
- **주식 매수(Buy)**: 이미 주식을 갖고 있으면 아무 일도 안 일어난다. 아니라면 현재 가격의 일정 비율인 **수수료(commission)**를 낸다.
- **포지션 닫기(Close)**: 이전에 산 주식이 없으면 아무 일도 안 일어난다. 있다면 매도 수수료를 내고 판다.

**보상(Reward)** — 여러 방식으로 표현할 수 있다.
- **매 스텝마다 나눠 받기**: 주식을 보유하고 있는 동안, 매 스텝 그 바의 가격 변동만큼 보상을 준다.
- **한 번에 몰아서 받기**: Close 행동을 할 때만, 전체 포지션의 최종 손익을 한꺼번에 보상으로 준다.

> [!question] 두 보상 방식, 뭐가 다를까?
> 얼핏 보면 둘 다 결과는 같아야 할 것 같다 — 어차피 최종 누적 보상은 똑같으니까. 하지만 **수렴 속도**가 다를 수 있고, 실제로는 그 차이가 꽤 클 수 있다. 책의 구현체는 두 방식을 다 지원하니, 직접 바꿔가며 실험해볼 수 있다.
>
> 비유하자면: 한 학기 내내 시험마다 점수를 알려주는 것(즉시 보상)과, 학기 말에 최종 성적표 한 장만 보여주는 것(지연 보상) — 어느 쪽이 학생이 "무엇을 잘했는지" 더 빨리 배우게 할까? 대개는 즉각적인 피드백이 학습을 더 빠르게 만든다.

### 1.2 가격을 어떻게 표현할까 — 절대값이 아니라 상대값

마지막으로 정해야 할 것은 **가격을 관측에 어떻게 담을 것인가**다. 이상적으로는 에이전트가 **실제 가격 수치 자체가 아니라 상대적인 움직임**에 주목하길 바란다 — "이 주식이 최근 바 동안 1% 올랐다"거나 "5% 빠졌다" 같은 식으로. 이게 합리적인 이유는, 서로 다른 주식은 절대 가격대가 천차만별이어도 **움직이는 패턴은 비슷할 수 있기** 때문이다.

> [!note] 기술적 분석(technical analysis)
> 금융에는 이런 "패턴"을 연구해서 미래를 예측하려는 분야가 따로 있는데, 이를 **기술적 분석**이라 부른다. 우리 시스템도 (그런 패턴이 정말 존재한다면) 그 패턴을 스스로 발견하길 바란다.

이를 위해 각 바의 고가·저가·종가를 **시가 대비 백분율(percentage)** 3개 숫자로 바꿔서 넣는다.

이 표현 방식에도 단점은 있다 — 예컨대 **핵심 가격대(key price level)** 정보를 잃는다. 시장은 라운드 넘버(예: 비트코인 1개당 7만 달러처럼 딱 떨어지는 숫자)나 과거 전환점이었던 가격대에서 튕겨 나가는 경향이 있다고 알려져 있는데, 상대 표현은 그런 절대적 위치 정보를 지워버린다. 하지만 이 챕터는 어디까지나 개념을 실험해보는 자리이므로, 상대적 가격 움직임 표현이 (존재한다면) 반복되는 패턴을 찾는 데 도움이 될 것이라는 정도로 만족한다. 이론적으로는 신경망이 스스로 평균 가격을 빼서 배울 수도 있지만(그냥 절대 가격에서 평균을 빼면 되니까), 상대 표현으로 미리 가공해주면 신경망의 일을 덜어준다.

---

## 2. 데이터 (Data)

이 예제에서는 **2015~2016년 러시아 주식시장 가격**을 쓴다(`Chapter10/data/ch10-small-quotes.tgz`에 있으며, 학습 전에 압축을 풀어야 한다).

압축 안에는 **M1 바(bar)** 데이터를 담은 CSV 파일들이 있다. M1이란 각 행이 **1분** 동안의 가격 움직임을 나타낸다는 뜻이며, 그 1분 동안의 움직임은 4개의 가격으로 요약된다.

- **Open(시가)**: 그 1분이 시작될 때의 가격
- **High(고가)**: 그 1분 동안의 최고가
- **Low(저가)**: 그 1분 동안의 최저가
- **Close(종가)**: 그 1분이 끝날 때의 마지막 가격

이렇게 1분 단위로 묶인 구간 하나하나를 **바(bar)**라고 부르며, 이를 통해 그 구간 안에서 가격이 어떻게 움직였는지 짐작할 수 있다. 예를 들어 `YNDX_160101_161231.csv`(얀덱스Yandex사의 2016년 주가)는 13만 줄 정도로, 형식은 다음과 같다.

```
<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
20160104,100100,1148.90000,1148.90000,1148.90000,1148.90000,0
20160104,100200,1148.90000,1148.90000,1148.90000,1148.90000,50
20160104,100300,1149.00000,1149.00000,1149.00000,1149.00000,33
...
```

앞의 두 열은 날짜·시간, 다음 4열은 시가·고가·저가·종가, 마지막 값은 그 1분 동안 체결된 매수·매도 주문 수(**거래량, volume**이라고도 부른다)다. 거래량의 정확한 의미는 시장마다 다르지만, 보통은 "그 순간 시장이 얼마나 활발했는가"를 보여준다.

이런 가격을 시각화하는 대표적인 방식이 **캔들스틱 차트(candlestick chart)**로, 각 바를 하나의 "캔들(양초)" 모양으로 그린다. 2016년 2월 얀덱스 주가 일부를 보면 다음과 같다.

![[fig_10_1.png]]
*그림 10.1 — 2016년 2월 얀덱스(Yandex) 주가 데이터 (캔들스틱 차트)*

압축 파일에는 2016년, 2015년 두 해의 M1 데이터가 들어있다. **2016년 데이터는 모델 학습**에, **2015년 데이터는 검증(validation)**에 쓴다(순서는 임의이니 바꿔써도 되고, 다른 기간을 써도 된다).

---

## 3. 트레이딩 환경 구현 (The Trading Environment)

지금까지 우리가 짠 수많은 코드는 Gym API를 전제로 동작한다. 그러니 트레이딩 기능도 익숙한 **Gym의 `Env` 클래스**를 상속해 구현한다. 환경은 `Chapter10/lib/environ.py`의 `StocksEnv` 클래스에 들어있고, 내부적으로 상태(state)를 관리하고 관측을 만들어내는 몇 개의 헬퍼 클래스를 쓴다.

### 3.1 공개 API 클래스

```python
import typing as tt
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils import seeding
from gymnasium.envs.registration import EnvSpec
import enum
import numpy as np
from . import data

DEFAULT_BARS_COUNT = 10
DEFAULT_COMMISSION_PERC = 0.1
```
- `DEFAULT_BARS_COUNT = 10`: 관측에 몇 개의 과거 바를 담을지 — 기본 10개.
- `DEFAULT_COMMISSION_PERC = 0.1`: 매수·매도 시 내야 하는 수수료(중개인에게 내는 돈) — 기본 0.1%. ([[커미션과 거래비용]] 참고)

```python
class Actions(enum.Enum):
    Skip = 0
    Buy = 1
    Close = 2
```
가능한 행동을 열거형(enum)으로 인코딩한다. 아무것도 안 하기, 주식 한 주 사기, 기존 포지션 닫기 — 딱 3가지뿐이다.

> [!note] 일부러 단순하게 만든 시장 모델
> 이 시장 모델은 **한 번에 딱 한 주만 살 수 있다.** 이미 산 포지션을 더 늘리는 것도, "공매도(short position, 갖고 있지 않은 주식을 미리 팔았다가 나중에 가격이 내려가면 싸게 사서 갚는 방식)"도 지원하지 않는다. 예제를 단순하게 유지하려는 의도적인 선택이다. 여러분은 이 옵션들을 직접 확장해볼 수 있다.

```python
class StocksEnv(gym.Env):
    spec = EnvSpec("StocksEnv-v0")
```
`spec` 필드는 `gym.Env`와 호환되기 위해 반드시 필요하며, 우리 환경을 Gym의 내부 레지스트리에 등록한다.

이 클래스는 두 가지 방법으로 인스턴스를 만들 수 있다.

```python
@classmethod
def from_dir(cls, data_dir: str, **kwargs):
    prices = {
        file: data.load_relative(file)
        for file in data.price_files(data_dir)
    }
    return StocksEnv(prices, **kwargs)
```
`from_dir` 클래스 메서드는 데이터 디렉터리 경로를 인자로 받아, 그 안의 모든 CSV에서 시세를 불러와 환경을 만든다. 이런 가격 데이터를 다루는 헬퍼 함수들은 `Chapter10/lib/data.py`에 있다.

다른 방법은 클래스를 직접 생성하는 것 — 이때는 `data.py`에 선언된 `Prices` 데이터클래스로 매핑된 가격 딕셔너리를 넘겨야 한다. `Prices`는 시가·고가·저가·종가·거래량 시계열을 1차원 NumPy 배열 5개 필드로 담는다.

### 3.2 생성자 (Constructor)

```python
def __init__(
    self, prices: tt.Dict[str, data.Prices],
    bars_count: int = DEFAULT_BARS_COUNT,
    commission: float = DEFAULT_COMMISSION_PERC,
    reset_on_close: bool = True, state_1d: bool = False,
    random_ofs_on_reset: bool = True,
    reward_on_close: bool = False, volumes=False
):
```

여러 인자를 받아 환경의 동작과 관측 표현 방식을 조절한다.

| 인자 | 의미 |
|---|---|
| `prices` | 하나 이상의 종목 가격을 담은 딕셔너리(키=종목명, 값=`data.Prices`) |
| `bars_count` | 관측에 담을 과거 바 개수. 기본 10개 |
| `commission` | 매수·매도 시 브로커에게 내는 수수료 비율. 기본 0.1% |
| `reset_on_close` | `True`(기본)면 포지션을 닫을 때마다 에피소드를 끝낸다. `False`면 시계열 끝(1년치 데이터 끝)까지 계속 진행 |
| `state_1d` | 관측을 1D 합성곱에 맞는 2D 행렬로 만들지(`True`), 완전연결망에 맞는 1D 벡터로 만들지(`False`) 결정. 아래에서 자세히 설명 |
| `random_ofs_on_reset` | `True`(기본)면 리셋할 때마다 시계열 안에서 무작위 시작 지점을 고른다. `False`면 항상 맨 처음부터 |
| `reward_on_close` | `True`면 Close 행동을 할 때만 보상을 준다. `False`(기본)면 매 바마다 가격 변동만큼 조금씩 보상을 준다 |
| `volumes` | 거래량을 관측에 포함할지. 기본은 꺼져 있음(`False`) |

> [!tip] 두 가지 데이터 표현 방식 (Figure 10.2)
> `state_1d=False`면 모든 바의 성분(고가·저가·종가·거래량)을 한 줄로 쭉 이어붙인 **1차원 벡터**를 만든다 — 완전연결망(fully connected network)에 적합하다.
> `state_1d=True`면 고가는 첫 행, 저가는 둘째 행, 종가는 셋째 행... 이런 식으로 **2차원 행렬**을 만든다 — 아타리 이미지에서 R·G·B 색상 평면을 다루듯, 시계열에 **1D 합성곱(1D convolution)**을 적용하기 좋은 구조다.

![[fig_10_2.png]]
*그림 10.2 — 신경망을 위한 두 가지 데이터 표현 방식(위: 1D 벡터, 아래: conv용 행렬)*

생성자의 나머지 부분을 보자.

```python
self._prices = prices
if state_1d:
    self._state = State1D(bars_count, commission, reset_on_close,
                           reward_on_close=reward_on_close, volumes=volumes)
else:
    self._state = State(bars_count, commission, reset_on_close,
                         reward_on_close=reward_on_close, volumes=volumes)
self.action_space = spaces.Discrete(n=len(Actions))
self.observation_space = spaces.Box(
    low=-np.inf, high=np.inf, shape=self._state.shape, dtype=np.float32)
self.random_ofs_on_reset = random_ofs_on_reset
```
`StocksEnv`의 실제 기능 대부분은 `State`와 `State1D`라는 두 내부 클래스에 들어있다. 이 둘은 관측을 준비하고, 우리가 산 주식의 상태와 보상을 관리한다 — 같은 데이터를 서로 다른 형태로 표현할 뿐이다(코드는 뒤에서 본다). 생성자에서는 이 상태 객체를 만들고, Gym이 요구하는 `action_space`와 `observation_space`를 설정한다. ([[관측공간과 행동공간(Space)]] 참고)

### 3.3 reset() — 에피소드 초기화

```python
def reset(self, *, seed: int | None = None, options: dict[str, tt.Any] | None = None):
    # make selection of the instrument and it's offset. Then reset the state
    super().reset(seed=seed, options=options)
    self._instrument = self.np_random.choice(list(self._prices.keys()))
    prices = self._prices[self._instrument]
    bars = self._state.bars_count
    if self.random_ofs_on_reset:
        offset = self.np_random.choice(prices.high.shape[0]-bars*10) + bars
    else:
        offset = bars
    self._state.reset(prices, offset)
    return self._state.encode(), {}
```
`gym.Env`의 관례에 따라, 여기서 우리가 다룰 시계열(종목)과 그 안의 시작 위치(offset)를 무작위로 고른다. 고른 가격 데이터와 시작 위치를 내부 상태 객체에 넘기고, 그 객체의 `encode()`를 호출해 첫 관측을 만든다.

### 3.4 step() — 한 스텝 진행

```python
def step(self, action_idx: int) -> tt.Tuple[np.ndarray, float, bool, bool, dict]:
    action = Actions(action_idx)
    reward, done = self._state.step(action)
    obs = self._state.encode()
    info = {
        "instrument": self._instrument,
        "offset": self._state._offset
    }
    return obs, reward, done, False, info
```
에이전트가 고른 행동을 처리하고, 다음 관측·보상·종료 여부를 돌려준다. 실제 로직은 전부 상태 클래스가 하므로, 이 메서드는 그저 상태 클래스의 메서드를 호출하는 **얇은 래퍼(wrapper)**일 뿐이다.

> [!note] render()는 왜 없을까?
> `gym.Env`의 API는 `render()` 메서드를 정의해, 사람이 보거나 기계가 읽을 수 있는 형태로 현재 상태를 시각화할 수 있게 해준다(에이전트가 무엇을 보는지 디버깅하거나 추적할 때 유용하다 — 예컨대 시장 환경이라면 현재 가격을 차트로 그려줄 수도 있다). 하지만 `render()`는 **선택 사항**이므로, 이 환경에서는 아예 정의하지 않는다.

### 3.5 State 클래스 — 환경의 핵심 로직

```python
class State:
    def __init__(self, bars_count: int, commission_perc: float, reset_on_close: bool,
                 reward_on_close: bool = True, volumes: bool = True):
        assert bars_count > 0
        assert commission_perc >= 0.0
        self.bars_count = bars_count
        self.commission_perc = commission_perc
        self.reset_on_close = reset_on_close
        self.reward_on_close = reward_on_close
        self.volumes = volumes
        self.have_position = False
        self.open_price = 0.0
        self._prices = None
        self._offset = None
```
생성자는 인자들을 검증하고 객체 필드에 저장하는 일만 한다.

```python
def reset(self, prices: data.Prices, offset: int):
    assert offset >= self.bars_count-1
    self.have_position = False
    self.open_price = 0.0
    self._prices = prices
    self._offset = offset
```
`reset()`은 환경이 리셋될 때마다 호출되며, 전달받은 가격 데이터와 시작 위치를 저장한다. 처음에는 아직 아무 주식도 안 샀으므로 `have_position=False`, `open_price=0.0`이다.

```python
@property
def shape(self) -> tt.Tuple[int, ...]:
    # [h, l, c] * bars + position_flag + rel_profit
    if self.volumes:
        return 4 * self.bars_count + 1 + 1,
    else:
        return 3 * self.bars_count + 1 + 1,
```
`shape` 프로퍼티는 인코딩된 상태의 NumPy 배열이 몇 차원인지 알려준다. `State` 클래스는 (거래량을 쓰면) 바마다 4개 숫자(고가·저가·종가·거래량)를 이어붙이고, 마지막에 "주식 보유 여부" 1개, "현재 포지션 수익률" 1개를 더한 **1차원 벡터** 하나로 인코딩된다(그림 10.2의 윗부분).

```python
def encode(self) -> np.ndarray:
    res = np.ndarray(shape=self.shape, dtype=np.float32)
    shift = 0
    for bar_idx in range(-self.bars_count+1, 1):
        ofs = self._offset + bar_idx
        res[shift] = self._prices.high[ofs]
        shift += 1
        res[shift] = self._prices.low[ofs]
        shift += 1
        res[shift] = self._prices.close[ofs]
        shift += 1
        if self.volumes:
            res[shift] = self._prices.volume[ofs]
            shift += 1
    res[shift] = float(self.have_position)
    shift += 1
    if not self.have_position:
        res[shift] = 0.0
    else:
        res[shift] = self._cur_close() / self.open_price - 1.0
    return res
```
`encode()`는 현재 위치(offset) 기준으로 가격들을 NumPy 배열에 채워 넣어, 에이전트가 볼 관측을 만든다. `have_position`이 참이면 마지막 값에 **현재까지의 수익률**(`현재가 / 매수가 - 1`)을 넣고, 아니면 0을 넣는다.

```python
def _cur_close(self) -> float:
    open = self._prices.open[self._offset]
    rel_close = self._prices.close[self._offset]
    return open * (1.0 + rel_close)
```
이 헬퍼는 현재 바의 종가를 계산한다. `State` 클래스에 전달되는 가격은 시가 대비 **상대값(relative)** 형태다 — 고가·저가·종가가 모두 시가 대비 비율로 표현된다(앞서 데이터 표현에서 논의한 바로 그 방식이다). 이 상대 표현이 에이전트가 절대 가격과 무관하게 가격 패턴을 배우는 데 도움을 줄 것으로 (아마도) 기대된다.

### 3.6 step() — State 클래스의 심장

```python
def step(self, action: Actions) -> tt.Tuple[float, bool]:
    reward = 0.0
    done = False
    close = self._cur_close()
```
이 메서드는 `State` 클래스에서 **가장 복잡한 코드**다. 환경에서 한 스텝을 처리하는 역할을 하며, 종료 시점에는 퍼센트 단위 보상과 에피소드 종료 여부를 돌려줘야 한다.

```python
if action == Actions.Buy and not self.have_position:
    self.have_position = True
    self.open_price = close
    reward -= self.commission_perc
```
에이전트가 매수를 결정하면, 상태를 바꾸고 수수료를 낸다(보상에서 뺀다). 여기서는 **현재 바의 종가로 주문이 즉시 체결된다**고 가정한다 — 이는 우리가 단순화를 위해 도입한 가정이다. 실제로는 주문이 다른 가격에 체결될 수도 있는데, 이를 **가격 슬리피지(slippage)**라고 부른다.

```python
elif action == Actions.Close and self.have_position:
    reward -= self.commission_perc
    done |= self.reset_on_close
    if self.reward_on_close:
        reward += 100.0 * (close / self.open_price - 1.0)
    self.have_position = False
    self.open_price = 0.0
```
포지션을 보유한 상태에서 에이전트가 Close를 요청하면: 수수료를 또 내고, `reset_on_close` 모드라면 `done` 플래그를 켜고, `reward_on_close`가 켜져 있다면 이때 **포지션 전체의 최종 보상**을 한꺼번에 더해준다. 그리고 상태를 초기화한다.

```python
self._offset += 1
prev_close = close
close = self._cur_close()
done |= self._offset >= self._prices.close.shape[0]-1
if self.have_position and not self.reward_on_close:
    reward += 100.0 * (close / prev_close - 1.0)
return reward, done
```
나머지 부분에서는 현재 위치를 한 칸 옮기고, **마지막 바의 가격 변동만큼 보상**을 준다(단, `reward_on_close`가 꺼져 있어 스텝마다 보상을 나눠 받는 모드일 때만). `State` 클래스는 여기까지다.

### 3.7 State1D — 합성곱용 표현

```python
class State1D(State):
    @property
    def shape(self) -> tt.Tuple[int, ...]:
        if self.volumes:
            return 6, self.bars_count
        else:
            return 5, self.bars_count
```
`State1D`는 `State`를 상속하며 **행동은 똑같고**, 에이전트에게 전달되는 관측의 표현 방식만 다르다. 가격을 1D 합성곱 연산자에 적합한 **2D 행렬**로 인코딩한다.

```python
def encode(self) -> np.ndarray:
    res = np.zeros(shape=self.shape, dtype=np.float32)
    start = self._offset-(self.bars_count-1)
    stop = self._offset+1
    res[0] = self._prices.high[start:stop]
    res[1] = self._prices.low[start:stop]
    res[2] = self._prices.close[start:stop]
    if self.volumes:
        res[3] = self._prices.volume[start:stop]
        dst = 4
    else:
        dst = 3
    if self.have_position:
        res[dst] = 1.0
        res[dst+1] = self._cur_close() / self.open_price - 1.0
    return res
```
고가·저가·종가(그리고 필요하면 거래량)를 각각 **한 행씩** 채운다 — 그림 10.2 아랫부분처럼 "고가 행, 저가 행, 종가 행, 거래량 행"이 통째로 쌓인 행렬이 된다. 마지막 한두 행에는 포지션 보유 여부와 수익률을 채운다.

이게 우리 트레이딩 환경의 전부다. Gym API와 호환되도록 만들었기 때문에, 아타리 게임을 다룰 때 썼던 익숙한 클래스들에 그대로 꽂아 쓸 수 있다. 이제 그렇게 해보자.

---

## 4. 모델 (Models)

이 예제에서는 DQN 아키텍처를 두 가지 쓴다.

1. **단순한 완전연결(feed-forward) 신경망** — 3개 층
2. **1D 합성곱(1D convolution)을 특징 추출기로 쓰는 신경망** — 그 뒤에 완전연결 층 2개를 붙여 Q값을 출력

두 모델 모두 **8장에서 배운 듀얼링(Dueling) 아키텍처**를 사용한다. 더불어 **더블 DQN(Double DQN)**과 **2단계 벨만 언롤링(two-step Bellman unrolling)**도 함께 쓰인다. 나머지 과정은 6장의 고전적인 DQN과 동일하다.

두 모델은 모두 `Chapter10/lib/models.py`에 있으며 아주 단순하다.

### 4.1 완전연결(Feed-Forward) 모델

```python
class SimpleFFDQN(nn.Module):
    def __init__(self, obs_len: int, actions_n: int):
        super(SimpleFFDQN, self).__init__()
        self.fc_val = nn.Sequential(
            nn.Linear(obs_len, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )
        self.fc_adv = nn.Sequential(
            nn.Linear(obs_len, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, actions_n)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        val = self.fc_val(x)
        adv = self.fc_adv(x)
        return val + (adv - adv.mean(dim=1, keepdim=True))
```
- `fc_val`: 관측 하나를 받아 **상태 자체의 가치(state value)** 하나(숫자 1개)를 예측하는 네트워크.
- `fc_adv`: 같은 관측을 받아 **각 행동의 우위(advantage)** — "이 행동이 평균보다 얼마나 더 좋은가" — 를 예측하는 네트워크.
- `forward()`: 최종 Q값은 `가치 + (우위 − 우위의 평균)`으로 계산한다. 평균을 빼주는 이유는, 가치와 우위를 분리해서 학습해도 둘 사이에 유일한 해가 정해지도록 만들기 위함이다([[벨만 방정식 Bellman Equation]]과 함께 [[듀얼링 DQN Dueling Architecture]] 참고).

완전연결 모델은 Q값 예측과 우위(advantage) 예측에 서로 **독립적인 두 개의 네트워크**를 쓴다.

### 4.2 1D 합성곱(Conv1D) 모델

```python
class DQNConv1D(nn.Module):
    def __init__(self, shape: tt.Tuple[int, ...], actions_n: int):
        super(DQNConv1D, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(shape[0], 128, 5),
            nn.ReLU(),
            nn.Conv1d(128, 128, 5),
            nn.ReLU(),
            nn.Flatten(),
        )
        size = self.conv(torch.zeros(1, *shape)).size()[-1]
        self.fc_val = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )
        self.fc_adv = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, actions_n)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        conv_out = self.conv(x)
        val = self.fc_val(conv_out)
        adv = self.fc_adv(conv_out)
        return val + (adv - adv.mean(dim=1, keepdim=True))
```
- `self.conv`: `Conv1d` 층 두 개(커널 크기 5)로 이루어진 **공통 특징 추출기(feature extractor)**. 입력은 `State1D`가 만든 2D 행렬(행=고가/저가/종가/거래량, 열=시간)이며, 이 위를 1D 커널이 시간축을 따라 훑으며 패턴을 뽑아낸다. ([[1D 합성곱과 시계열]] 참고)
- `size = self.conv(torch.zeros(1, *shape)).size()[-1]`: 더미 입력을 한 번 흘려보내서, 합성곱을 통과한 뒤의 출력 크기를 자동으로 계산한다 — 층 구조가 바뀌어도 이 크기를 손으로 다시 계산할 필요가 없게 하는 실용적인 트릭이다.
- 이후 `fc_val`, `fc_adv`는 완전연결 모델과 마찬가지로 가치·우위를 나눠 예측하고, 합쳐서 Q값을 만든다.

보다시피 이 모델은 아타리 예제에서 썼던 **듀얼링 DQN 아키텍처**와 매우 비슷하다.

---

## 5. 학습 코드 (Training Code)

이 예제에는 서로 매우 비슷한 학습 모듈이 두 개 있다 — 완전연결 모델용, 1D 합성곱용. 둘 다 **8장에서 봤던 것과 새로 추가된 내용은 없다.**

- **입실론-그리디(epsilon-greedy)** 행동 선택으로 탐험한다. 입실론은 학습 첫 100만 스텝 동안 1.0에서 0.1로 선형으로 줄어든다.
- 크기 **10만(100k)**짜리 단순한 경험 재생 버퍼(replay buffer)를 쓰며, 처음에 1만(10k) 개의 전이로 미리 채워둔다.
- **1,000 스텝마다** 고정된 상태 집합에 대한 평균 Q값을 계산해, 학습 중 Q값이 어떻게 변하는지 살펴본다.
- **10만(100k) 스텝마다** 검증을 수행한다 — 학습 데이터와, 한 번도 본 적 없는 시세 양쪽에서 각각 100번의 에피소드를 플레이한다. 검증 결과(평균 이익, 평균 보유 바 수, 주식 보유 비율 등)는 TensorBoard에 기록된다. 이 과정은 **과적합(overfitting)**이 일어나는지 확인하는 데 쓰인다. ([[과적합과 검증데이터]] 참고)

학습 모듈은 `Chapter10/train_model.py`(완전연결 모델)와 `Chapter10/train_model_conv.py`(1D 합성곱)에 있으며, 둘 다 같은 커맨드라인 옵션을 받는다.

학습을 시작하려면 `--data` 옵션으로 학습 데이터를 넘겨야 한다(개별 CSV 파일이나 CSV들이 든 디렉터리 모두 가능). 기본값은 얀덱스 2016년 시세(`data/YNDX_160101_161231.csv`)다. 검증 데이터는 `--val` 옵션으로 지정하며 기본값은 얀덱스 2015년 시세다. 그리고 실행(run)의 이름을 지정하는 `-r` 옵션이 필수다 — 이 이름은 TensorBoard 실행 이름과 모델을 저장할 디렉터리 이름에 쓰인다.

---

## 6. 결과 (Results)

두 모델을 각각 학습시킨 뒤 성능을 비교해보자. 먼저 완전연결(feed-forward) 모델부터다.

### 6.1 완전연결 모델

학습 동안 에이전트가 얻는 **평균 보상**은 느리지만 꾸준히 증가했다. 30만(300k) 에피소드가 지난 뒤로는 증가 속도가 둔화됐다. 다음은 학습 중 원본(raw) 보상과, 최근 15개 값을 이동평균한 값을 나란히 보여주는 차트다.

![[fig_10_3.png]]
*그림 10.3 — 학습 중 보상. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

다음은 (무작위 행동 없이, ε=0으로) 학습 데이터에 대해 테스트를 수행한 결과의 보상 차트다.

![[fig_10_4.png]]
*그림 10.4 — 테스트에서 얻은 보상. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

학습·테스트 보상 차트 모두, 에이전트가 시간이 지날수록 이익을 늘리는 법을 배우고 있음을 보여준다.

![[fig_10_5.png]]
*그림 10.5 — 에피소드 길이. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

**에피소드 길이**도 10만(100k) 에피소드 이후 늘어났다 — 에이전트가 "주식을 계속 들고 있는 것이 이익이 될 수 있다"는 걸 학습했기 때문이다.

또한 무작위로 뽑은 상태 집합에 대해 신경망이 예측하는 값도 함께 모니터링한다.

![[fig_10_6.png]]
*그림 10.6 — 무작위로 뽑은 상태 집합에 대해 예측된 가치*

다음 차트는 학습이 진행될수록 네트워크가 그 상태들에 대해 점점 더 **낙관적**으로 변한다는 것을 보여준다.

여기까지는 모두 좋아 보이지만, 전부 **학습 데이터**로 얻은 결과다. 우리 에이전트가 과거 데이터에서 이익 내는 법을 배우는 건 훌륭하다. 하지만 **한 번도 본 적 없는 데이터**에서도 통할까? 이를 확인하려고 2015년 시세로 검증했고, 그 보상은 그림 10.7과 같다.

![[fig_10_7.png]]
*그림 10.7 — 검증 데이터셋에서의 보상. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

> [!warning] 실망스러운 결과 — 과적합의 신호
> 이 차트는 조금 실망스럽다. 보상이 **상승 추세를 보이지 않는다.** 스무딩된 버전을 보면 오히려 첫 시간 이후로 보상이 **서서히 줄어드는** 것처럼 보인다(이 시점은 그림 10.5에서 학습 에피소드 길이가 크게 늘어난 시점과 겹친다).
>
> 이는 학습 100만 스텝 이후로 에이전트에게 **과적합(overfitting)**이 시작됐다는 신호일 수 있다. ([[과적합과 검증데이터]] 참고) 그래도 학습 첫 4시간 동안은 보상이 -0.2%보다 위에 있는데, 이는 우리 환경의 브로커 수수료(매수 0.1% + 매도 0.1% = 0.2%)와 비슷한 수준이라, 우리 에이전트가 최소한 무작위로 사고파는 "원숭이"보다는 낫다는 뜻이다.

학습 도중 코드는 나중에 실험할 수 있도록 모델을 저장한다. 저장 시점은 (홀드아웃 상태 집합에 대한) 평균 Q값이 새 최댓값을 갱신할 때, 또는 검증 세트의 보상이 이전 기록을 넘어설 때다.

학습된 모델을 불러와 지정한 가격 데이터로 거래를 재현하고, 시간에 따른 이익 변화를 그래프로 그려주는 도구가 `Chapter10/run_model.py`다. 사용법은 다음과 같다.

```
Chapter10$ ./run_model.py -d data/YNDX_160101_161231.csv -m saves/simple-t1/mean_value-0.277.data -b 10 -n YNDX16
```

옵션 정리:

| 옵션 | 의미 |
|---|---|
| `-d` | 사용할 시세 파일 경로. 위 예시는 학습에 썼던 데이터를 그대로 적용 |
| `-m` | 모델 파일 경로. 기본적으로 학습 코드는 `saves` 디렉터리에 저장 |
| `-b` | 모델에 넘길 컨텍스트 바 개수. 학습 때 쓴 값과 일치해야 함(기본 10, 학습 코드에서 변경 가능) |
| `-n` | 생성되는 이미지 파일명에 붙일 접미사 |
| `--commission` | 브로커 수수료를 재정의(기본 0.1%) |

이 도구는 마지막에 전체 이익 변화(퍼센트 단위)를 차트로 그려준다. 다음은 학습에 썼던 얀덱스 2016년 시세에 대한 보상 차트다.

![[fig_10_8.png]]
*그림 10.8 — 학습 데이터(왼쪽)와 검증 데이터(오른쪽)에서의 트레이딩 이익*

학습 데이터에서의 결과는 놀랍다 — **1년 만에 150% 이익**. 하지만 검증 데이터셋에서의 결과는 훨씬 나쁘다 — TensorBoard의 검증 그래프에서 이미 봤던 그대로다.

우리 시스템이 **수수료가 없다면** 정말 수익성이 있는지 확인하기 위해, 같은 데이터에 `--commission 0.0` 옵션을 주고 다시 실행해보자.

![[fig_10_9.png]]
*그림 10.9 — 브로커 수수료 없이 검증 데이터에서의 트레이딩 이익*

며칠은 손실(drawdown)을 보기도 하지만, 전체적으로는 결과가 나쁘지 않다 — **수수료가 없다면 우리 에이전트는 수익을 낼 수 있다.** 물론 수수료만이 문제는 아니다. 우리의 주문 시뮬레이션은 매우 단순화되어 있어서, 실제 상황에서 발생하는 **가격 스프레드**나 **주문 체결 시 슬리피지** 같은 요소는 반영하지 않는다.

검증 세트에서 가장 보상이 좋았던 모델을 골라 보면, 보상의 흐름이 조금 더 낫다. 수익성은 낮아지지만, 처음 보는 시세에서의 낙폭(drawdown)은 훨씬 작다(다음 차트들은 수수료를 켠 상태다).

![[fig_10_10.png]]
*그림 10.10 — 검증 보상이 가장 좋았던 모델의 보상 흐름. 학습 데이터(왼쪽)와 검증 데이터(오른쪽)*

> [!warning] 검증 결과로 모델을 고르는 건 "반칙"이다
> 물론 검증 데이터에서의 결과를 기준으로 모델을 고르는 것은 일종의 **속임수**다 — 검증 결과를 모델 선택에 쓰는 순간, 검증이라는 개념 자체의 취지(한 번도 보지 않은 데이터로 일반화 성능을 확인하는 것)가 무너지기 때문이다. 위 차트들은 "운 좋게도 처음 보는 데이터에서도 그럭저럭 통하는 모델이 존재할 수 있다"는 걸 보여주기 위한 예시일 뿐이다.

### 6.2 합성곱 모델

이 예제의 두 번째 모델은 **1D 합성곱 필터**를 써서 가격 데이터에서 특징을 뽑아낸다. 이 덕분에 네트워크 크기를 크게 늘리지 않고도 에이전트가 보는 **컨텍스트 윈도우(맥락 창)의 바 개수를 늘릴 수 있다.** 기본값으로 합성곱 모델 예제는 **50개 바**를 컨텍스트로 사용한다. 학습 코드는 `Chapter10/train_model_conv.py`에 있으며, 완전연결 버전과 동일한 커맨드라인 옵션을 받는다.

학습 흐름은 거의 동일하지만, 검증 세트에서 얻는 보상이 조금 더 높고, 과적합이 시작되는 시점도 조금 더 늦다.

![[fig_10_11.png]]
*그림 10.11 — 학습 중 보상. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

![[fig_10_12.png]]
*그림 10.12 — 검증 데이터셋에서의 보상. 원본값(왼쪽)과 스무딩된 값(오른쪽)*

---

## 7. 더 시도해볼 만한 것들 (Things to Try)

앞서 말했듯 금융시장은 크고 복잡한 영역이며, 이 챕터에서 시도한 방법은 정말 시작 단계에 불과하다. RL로 완전하고 수익성 있는 트레이딩 전략을 만드는 건 몇 달을 들여야 하는 큰 프로젝트다. 그래도 이 주제를 더 깊이 이해하기 위해 시도해볼 만한 것들이 있다.

- **데이터 표현을 개선하기.** 지금 표현은 확실히 완벽하지 않다 — 지지선·저항선(support and resistance) 같은 핵심 가격대, 라운드 넘버, 기타 시장 정보를 전혀 반영하지 않는다. 이런 정보를 관측에 녹여내는 건 도전적인 문제다.
- **여러 시간 프레임에서 가격을 분석하기.** 1분 봉 같은 저수준 데이터는 개별 거래로 인한 잡음(noise)이 많아서, 마치 시장을 현미경으로 들여다보는 것과 같다. 1시간 봉·1일 봉처럼 더 큰 스케일에서는 가격 예측에 중요한 큰 흐름(트렌드)이 보인다. 원칙적으로 에이전트는 최근의 미세한 움직임과 전체적인 흐름을 **동시에** 볼 수도 있다 — 최근 자연어 처리(NLP) 기법인 트랜스포머, 어텐션, 긴 문맥 창(long context window) 등이 여기서 도움이 될 수 있다.
- **더 많은 학습 데이터.** 한 종목의 1년치 데이터는 겨우 13만 개 바에 불과해서, 시장의 다양한 상황을 다 담기엔 부족할 수 있다. 실전에서는 수백 종목의 10년 이상 데이터로 학습하는 것이 이상적이다.
- **네트워크 구조를 실험하기.** 합성곱 모델이 완전연결 모델보다 수렴이 조금 더 빨랐지만, 층 개수·커널 크기·잔차 구조(residual architecture)·어텐션 메커니즘 등 최적화할 여지가 많다.
- **NLP와의 유사성을 활용하기.** NLP와 금융 데이터 분석은 둘 다 사람이 만들어낸, 길이가 가변적인 시퀀스 데이터를 다룬다는 공통점이 있다. 가격 바를 어떤 "금융 언어"의 "단어"로 표현해볼 수도 있다(예: "1% 상승" → 토큰 A, "2% 상승" → 토큰 B). 이렇게 만든 "문장"으로 임베딩을 학습해 금융시장의 구조를 포착하거나, 트랜스포머나 LLM을 데이터 예측·분류에 써볼 수도 있다.

---

## 8. 요약

이 챕터에서는 RL의 실전 예제로 **트레이딩 에이전트와 커스텀 Gym 환경**을 직접 구현했다. 두 가지 아키텍처(가격 이력을 입력으로 받는 완전연결 네트워크, 1D 합성곱 네트워크)를 시도했고, 둘 다 8장에서 배운 확장 기법이 적용된 **DQN**을 사용했다.

이 챕터는 이 책 **Part 2의 마지막 챕터**였다. Part 3에서는 전혀 다른 계열의 RL 방법인 **정책 경사(policy gradient)**를 다룬다. 이 접근법을 살짝 맛보긴 했지만, 앞으로는 **REINFORCE 방법**과 이 계열 최고의 방법으로 꼽히는 **비동기 어드밴티지 액터-크리틱(Asynchronous Advantage Actor-Critic, A3C)**까지 훨씬 깊이 파고든다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[커미션과 거래비용]]
- [[과적합과 검증데이터]]
- [[듀얼링 DQN Dueling Architecture]]
- [[1D 합성곱과 시계열]]
- [[벨만 방정식 Bellman Equation]]
- [[관측공간과 행동공간(Space)]]

## 한눈에 보는 개념 지도
| 개념 | 기호/이름 | 한 줄 뜻 |
|---|---|---|
| 바(bar) | 1분봉 등 | 일정 시간 동안의 시가·고가·저가·종가 요약 |
| 커미션 | commission | 매수·매도 시 브로커에게 내는 수수료(%) |
| 상대 가격 표현 | high/low/close as % of open | 절대가격 대신 시가 대비 비율로 표현해 패턴 학습을 돕는 방식 |
| 포지션(position) | have_position | 현재 주식을 보유 중인지 여부 |
| 리셋온클로즈 | reset_on_close | 포지션을 닫을 때 에피소드도 끝낼지 여부 |
| 리워드온클로즈 | reward_on_close | 보상을 매 스텝 나눠줄지, Close 시 한 번에 줄지 |
| 듀얼링 아키텍처 | Dueling DQN | Q값을 가치(Value)+우위(Advantage)로 분리해 학습 |
| 1D 합성곱 | Conv1D | 시계열 방향으로 슬라이딩하며 특징을 뽑는 합성곱 |
| 과적합 | overfitting | 학습 데이터엔 잘 맞지만 새 데이터엔 성능이 떨어지는 현상 |
| 슬리피지 | slippage | 주문이 기대한 가격이 아닌 다른 가격에 체결되는 현상 |
