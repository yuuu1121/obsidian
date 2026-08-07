---
title: "Chapter 2 — OpenAI Gym API와 Gymnasium (OpenAI Gym API and Gymnasium)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 2
tags: [DeepRL, 강화학습, Gym, Gymnasium, API, CartPole, Wrapper]
---

# Chapter 2 · OpenAI Gym API와 Gymnasium

> [!abstract] 이 챕터를 한 문장으로
> **Gymnasium**(옛 OpenAI Gym의 후속 라이브러리)은 모든 강화학습 환경에 `reset()`과 `step()`이라는 **똑같은 사용설명서(API)** 를 붙여서, 환경이 CartPole이든 Atari 게임이든 **에이전트 코드를 하나도 안 바꾸고** 그대로 쓸 수 있게 해준다. 이 챕터에서는 이 API를 직접 손으로 만들어보고(순수 파이썬), 그다음 Gymnasium이 제공하는 진짜 API로 CartPole을 다루고, 마지막으로 환경을 감싸서 기능을 추가하는 **래퍼(Wrapper)** 까지 배운다.

---

## 들어가며 — 이론에서 실전으로

1장에서는 강화학습(RL)의 이론적 개념 — 에이전트, 환경, 보상, 마르코프 결정 과정(MDP), 정책 — 을 배웠다. 이 챕터부터는 **진짜로 코드를 짜서 실행**해본다.

이 챕터가 끝나면 다음을 이해하게 된다.
- RL 에이전트를 실제 프레임워크에 꽂아 넣기 위해 **최소한으로 필요한 것들**이 무엇인지
- **순수 파이썬만으로** 랜덤하게 행동하는 RL 에이전트를 직접 구현하는 법
- **OpenAI Gym API**와 그 구현체인 **Gymnasium** 라이브러리의 사용법

---

## 1. 에이전트의 해부학 (The Anatomy of the Agent)

1장에서 배운 RL의 핵심 개념을 다시 떠올려보자.

- **에이전트(agent)**: 능동적으로 행동하는 주체. 실전에서는 **어떤 정책(policy)을 구현한 코드 한 조각**이다. 이 정책이 매 시점(time step)마다 관측값을 보고 어떤 행동을 할지 결정한다.
- **환경(environment)**: 에이전트 바깥의 모든 것. 관측값을 제공하고 보상을 주는 책임을 진다. 에이전트의 행동에 따라 환경의 상태가 바뀐다.

이 둘을 파이썬으로 어떻게 구현하는지, 아주 단순한 상황으로 먼저 연습해보자. 여기서 만들 환경은 **에이전트가 무슨 행동을 하든 상관없이, 정해진 스텝 수 동안 무작위 보상**을 주는 환경이다. 실제로 쓸모는 없지만, 환경 클래스와 에이전트 클래스에 어떤 메서드가 필요한지에만 집중할 수 있게 해준다.

> [!tip] 참고
> 책의 코드 조각은 완전한 예제가 아니다. 전체 예제는 GitHub 저장소(`https://github.com/PacktPublishing/Deep-Reinforcement-Learning-Hands-On-Third-Edition`)에서 확인하고 직접 실행해볼 수 있다.

### 1.1 환경(Environment) 클래스 만들기

```python
class Environment:
    def __init__(self):
        self.steps_left = 10
```

- `class Environment:` — 환경이라는 **틀(클래스)** 을 정의한다. [[API와 클래스·객체]] 참고.
- `__init__(self)` — 이 클래스로 객체를 만들 때(`Environment()` 호출 시) 자동으로 실행되는 **생성자**다.
- `self.steps_left = 10` — 이 환경 객체만의 "내부 상태"로, **앞으로 몇 스텝 더 진행할 수 있는지**를 세는 카운터다. 여기서는 상태라고 해봐야 이 숫자 하나뿐인 아주 단순한 예다.

`get_observation()` 메서드는 환경이 에이전트에게 줄 **현재 관측값**을 반환한다. 보통 환경의 내부 상태를 가공한 함수로 구현된다.

```python
def get_observation(self) -> List[float]:
    return [0.0, 0.0, 0.0]
```

- `-> List[float]` 부분은 **타입 힌트(type annotation)** 다. "이 함수는 실수(float)들의 리스트를 반환한다"는 뜻을 코드에 명시적으로 적어둔 것으로, 파이썬 3.5부터 지원된다. 실행에는 영향을 주지 않고, 사람이 코드를 읽을 때(그리고 도구가 오류를 검사할 때) 도움을 준다.
- 이 예제에서는 환경이 내부 상태를 딱히 갖지 않으므로, 관측값은 그냥 **항상 0으로 채워진 벡터**를 돌려준다.

`get_actions()` 메서드는 에이전트가 실행할 수 있는 **행동들의 집합**을 알려준다.

```python
def get_actions(self) -> List[int]:
    return [0, 1]
```

- 보통 행동의 집합은 시간이 지나도 안 바뀌지만, 상황에 따라 일부 행동이 불가능해지는 경우도 있다(예: 틱택토에서 이미 채워진 칸에는 둘 수 없음).
- 이 단순한 예제에서는 정수 `0`과 `1`로 표현되는 두 가지 행동만 존재한다.

에피소드가 끝났는지 알려주는 메서드도 필요하다.

```python
def is_done(self) -> bool:
    return self.steps_left == 0
```

- 1장에서 배웠듯, 에이전트와 환경의 상호작용은 **에피소드**라는 단위로 나뉜다. 체스처럼 유한하게 끝날 수도 있고, 46년 전에 발사되어 태양계를 벗어난 우주 탐사선 보이저 2호처럼 사실상 무한히 이어질 수도 있다. 두 경우 모두를 다루기 위해, 환경은 "이제 더 이상 상호작용할 수 없다"는 신호를 보낼 방법이 필요하다.
- 여기서는 남은 스텝 수(`steps_left`)가 0이 되면 에피소드가 끝난 것으로 본다.

가장 중요한 메서드는 `action()`이다.

```python
def action(self, action: int) -> float:
    if self.is_done():
        raise Exception("Game is over")
    self.steps_left -= 1
    return random.random()
```

- 이 메서드가 환경 기능의 **핵심**이다. 에이전트의 행동을 처리하고, 그 행동에 대한 보상을 반환한다.
- `if self.is_done(): raise Exception(...)` — 이미 끝난 게임에 행동을 시도하면 오류를 낸다. (방어 코드)
- `self.steps_left -= 1` — 스텝을 하나 소모한다.
- `return random.random()` — 이 예제에서 보상은 **무작위 숫자**일 뿐이고, 실제로 어떤 행동을 했는지는 전혀 신경 쓰지 않는다(그냥 버려진다).

### 1.2 에이전트(Agent) 클래스 만들기

환경보다 에이전트 쪽이 훨씬 단순하다. 생성자와 "환경에서 한 스텝 진행하는" 메서드, 이 두 개만 있으면 된다.

```python
class Agent:
    def __init__(self):
        self.total_reward = 0.0
```

- `total_reward` — 에피소드 동안 누적된 보상 총합을 세는 카운터. 처음엔 0.0에서 시작.

```python
def step(self, env: Environment):
    current_obs = env.get_observation()
    actions = env.get_actions()
    reward = env.action(random.choice(actions))
    self.total_reward += reward
```

한 줄씩 뜯어보면:
- `def step(self, env: Environment):` — 이 메서드는 **환경 객체를 인자로 받는다**. `env: Environment`는 "`env`라는 매개변수가 `Environment` 타입이어야 한다"는 타입 힌트다.
- `current_obs = env.get_observation()` — 환경을 관찰한다 (지금 이 예제에서는 실제로 쓰이지 않고 그냥 받아만 둔다).
- `actions = env.get_actions()` — 가능한 행동 목록을 받아온다.
- `reward = env.action(random.choice(actions))` — `random.choice(actions)`로 가능한 행동 중 하나를 **무작위로** 고르고, 그것을 환경에 제출(`env.action(...)`)해서 보상을 받는다.
- `self.total_reward += reward` — 받은 보상을 누적한다.

즉 이 함수 하나로 에이전트는 다음 네 가지를 순서대로 해낸다: **① 환경을 관찰한다 → ② 관측을 바탕으로 행동을 결정한다 → ③ 행동을 환경에 제출한다 → ④ 이번 스텝의 보상을 받는다.** 여기서는 관측값을 아예 무시하고 무작위로 행동을 고르는, "멍청한" 에이전트다.

### 1.3 두 클래스를 연결하는 글루 코드(glue code)

```python
if __name__ == "__main__":
    env = Environment()
    agent = Agent()

    while not env.is_done():
        agent.step(env)

    print("Total reward got: %.4f" % agent.total_reward)
```

- `if __name__ == "__main__":` — 이 파이썬 파일을 **직접 실행했을 때만** 아래 코드를 실행하라는 관용적 표현이다(다른 파일에서 `import`만 할 때는 실행되지 않는다).
- `env = Environment()`, `agent = Agent()` — 각 클래스의 **객체(인스턴스)** 를 하나씩 생성한다.
- `while not env.is_done(): agent.step(env)` — 환경이 끝날 때까지, 에이전트가 계속 한 스텝씩 진행한다.
- 마지막에 누적 보상을 출력한다. 이 파일은 `Chapter02/01_agent_anatomy.py` 에서 전체 코드를 볼 수 있으며, 외부 의존성이 전혀 없어 어떤 파이썬 버전에서도 잘 작동한다. 실행할 때마다 무작위성 때문에 다른 값이 나온다.

```
Chapter02$ python 01_agent_anatomy.py
Total reward got: 5.8832
```

> [!important] 이 예제가 보여주는 핵심 패턴
> 환경은 굉장히 복잡한 물리 시뮬레이션일 수도 있고, 에이전트는 최신 RL 알고리즘을 구현한 거대한 **신경망(neural network, NN)** 일 수도 있다. 하지만 **기본 패턴은 언제나 똑같다.** 매 스텝마다 에이전트는 환경으로부터 관측을 받고, 계산을 하고, 행동을 고른다. 그 결과로 보상과 새 관측이 돌아온다.
>
> 그렇다면 이 패턴이 항상 같다면, 왜 매번 처음부터 새로 짜야 할까? 물론 이미 누군가 만들어놓은 라이브러리를 쓰면 된다 — 그것이 바로 Gym(Gymnasium)이다.

---

## 2. 하드웨어와 소프트웨어 요구사항

이 책의 예제는 **파이썬 3.11**로 작성되고 테스트되었다. 저자는 독자가 이미 파이썬 언어와 가상환경 같은 기본 개념에 익숙하다고 가정하고, 패키지 설치 방법은 자세히 다루지 않는다.

책에서 사용하는 주요 외부 라이브러리들:

| 라이브러리 | 역할 |
|---|---|
| **NumPy** | 과학 계산, 행렬 연산 |
| **OpenCV Python bindings** | 컴퓨터 비전(이미지 처리) |
| **Gymnasium** (Farama Foundation) | OpenAI Gym의 유지보수판 포크. 다양한 환경을 통일된 방식으로 제공하는 RL 프레임워크 |
| **PyTorch** | 유연하고 표현력 있는 딥러닝(DL) 라이브러리 (3장에서 크래시 코스 제공) |
| **PyTorch Ignite** | PyTorch 위에서 보일러플레이트 코드를 줄여주는 고수준 도구 |
| **PTAN** | 저자가 만든, 최신 딥 RL을 위한 OpenAI Gym API 확장 오픈소스 |

> [!note] GPU가 있어야 할까?
> 이 책의 상당 부분(Part 2, 3, 4)은 딥러닝을 많이 쓰는 최신 RL 방법을 다룬다. 최신 GPU는 CPU보다 10~100배 빠를 수 있어서, GPU가 없는 시스템에서는 **반나절 걸릴 학습이 일주일**씩 걸릴 수도 있다. 꼭 GPU가 있어야 하는 건 아니지만(느릴 뿐), 직접 실습해보려면 GPU 있는 환경(개인 GPU, 클라우드 인스턴스, Google Colab 무료 GPU 등)을 구하는 게 좋다.

`requirements.txt`에 명시된 정확한 버전들(파이썬 3.11 기준):

```text
gymnasium[atari]==0.29.1
gymnasium[classic-control]==0.29.1
gymnasium[accept-rom-license]==0.29.1
moviepy==1.0.3
numpy<2
opencv-python==4.10.0.84
torch==2.5.0
torchvision==0.20.0
pytorch-ignite==0.5.1
tensorboard==2.18.0
mypy==1.8.0
ptan==0.8.1
stable-baselines3==2.3.2
torchrl==0.6.0
ray[tune]==2.37.0
pytest
```

운영체제는 Linux나 macOS를 권장한다. Windows도 PyTorch와 Gymnasium이 지원하지만, 이 책의 예제가 Windows에서 완전히 테스트되지는 않았다.

---

## 3. OpenAI Gym API와 Gymnasium

### 3.1 Gym에서 Gymnasium으로 — 역사

파이썬 라이브러리 **Gym**은 **OpenAI**(`www.openai.com`)가 개발했다. 첫 버전은 2017년에 나왔고, 그 이후 수많은 환경이 이 API를 기준으로 만들어지거나 이식되면서 RL의 **사실상 표준(de facto standard)** 이 되었다.

2021년, Gym을 개발하던 팀이 개발을 **Gymnasium**(`github.com/Farama-Foundation/Gymnasium`)으로 옮겼다. Gymnasium은 원래 Gym 라이브러리의 **포크(fork, 원본에서 갈라져 나와 독자적으로 발전하는 사본)** 다. 똑같은 API를 제공하고, Gym의 **"드롭인 교체품(drop-in replacement)"** 이 되도록 설계되었다 — 즉 `import gymnasium as gym`이라고만 바꿔도 기존 코드가 대부분 그대로 작동한다는 뜻이다.

> [!tip] 표기법 안내
> 이 책의 예제 코드는 Gymnasium을 쓰지만, 본문 설명에서는 편의상 그냥 "Gym"이라고 부른다. 둘의 차이가 실제로 중요한 드문 경우에만 "Gymnasium"이라고 명시한다.

### 3.2 Gym의 핵심 목표 — `Env` 클래스

Gym의 핵심 목표는 **RL 실험을 위한 환경들을 통일된 인터페이스로 풍부하게 제공**하는 것이다. 그래서 이 라이브러리의 중심 클래스는 환경을 나타내는 **`Env`** 다. `Env` 클래스의 객체는 그 환경의 능력에 대한 정보를 담은 여러 메서드와 필드를 노출한다.

높은 수준에서, 모든 환경은 다음 정보와 기능을 제공한다.
- 환경에서 실행할 수 있는 **행동들의 집합**. Gym은 이산 행동과 연속 행동, 그리고 그 둘의 조합을 모두 지원한다. ([[이산 행동과 연속 행동]])
- 환경이 에이전트에게 주는 **관측값의 형태와 경계**.
- 행동을 실행하는 `step` 메서드. 현재 관측, 보상, 그리고 에피소드가 끝났는지 알려주는 플래그를 반환한다.
- 환경을 초기 상태로 되돌리고 첫 관측을 얻는 `reset` 메서드.

이 구성요소들을 하나씩 자세히 살펴보자.

### 3.3 행동공간 (The Action Space)

에이전트가 실행할 수 있는 행동은 **이산(discrete)**, **연속(continuous)**, 또는 이 둘의 조합일 수 있다. ([[이산 행동과 연속 행동]] 참고)

- **이산 행동**: 좌/우/상/하처럼 에이전트가 할 수 있는 **고정된 목록**. 버튼(눌림/떼짐)도 예가 될 수 있다. 두 상태가 서로 배타적이며, 이것이 이산 행동공간의 핵심 특징이다 — 한 순간에는 유한한 집합 중 딱 하나의 행동만 가능하다.
- **연속 행동**: 값이 붙은 행동. 예를 들어 조향 핸들은 특정 각도로 돌릴 수 있고, 이 값의 경계(boundary)에 대한 설명이 함께 필요하다. 핸들은 −720도~720도, 가속 페달은 보통 0~1 범위다.

물론 행동 하나로 제한되지 않는다. 여러 버튼을 동시에 누르거나, 핸들을 돌리면서 동시에 브레이크와 가속 페달을 밟는 경우처럼, Gym은 이런 경우를 위해 **여러 행동공간을 하나의 통일된 행동공간으로 중첩**할 수 있는 특수 컨테이너 클래스를 제공한다.

### 3.4 관측공간 (The Observation Space)

관측은 보상 외에, 환경이 매 타임스탬프마다 에이전트에게 제공하는 정보다. 단순한 숫자 몇 개일 수도 있고, 여러 카메라에서 받은 컬러 이미지처럼 복잡한 다차원 텐서일 수도 있다. 관측 역시 행동공간처럼 **이산**일 수 있다 — 예를 들어 전구가 켜짐/꺼짐 두 상태 중 하나인 불리언 값으로 주어지는 것이 이산 관측공간의 예다.

이렇게 보면 행동과 관측이 서로 닮아있음을 알 수 있고, 실제로 Gym의 클래스 구조에도 이 유사성이 그대로 반영되어 있다. 클래스 다이어그램을 보자.

![[fig_2_1_v3.png]]
*그림 2.1 — Gym의 `Space` 클래스 계층 구조*

`Space`라는 **추상 클래스**가 하나의 속성과 세 개의 메서드를 갖는다.
- `shape`: 공간의 형태(차원)를 담은 속성. NumPy 배열의 shape와 동일한 개념.
- `sample()`: 이 공간에서 무작위 샘플 하나를 반환한다.
- `contains(x)`: 인자 `x`가 이 공간에 속하는지 확인한다.
- `seed()`: 이 공간(및 모든 하위 공간)의 난수 생성기를 초기화한다. 여러 번 실행해도 같은 결과를 재현하고 싶을 때 유용하다.

이 메서드들은 모두 추상 메서드이며, `Space`의 각 하위 클래스에서 **다시 구현**된다.
- **`Discrete`**: 서로 배타적인 항목들의 집합으로, 0부터 n-1까지 번호가 매겨진다. 필요하면 생성자 인자 `start`로 시작 번호를 바꿀 수도 있다. `n`은 이 `Discrete` 객체가 나타내는 항목의 개수다. 예를 들어 `Discrete(n=4)`는 [좌, 우, 상, 하] 네 방향의 행동공간을 표현하는 데 쓸 수 있다.
- **`Box`**: `[low, high]` 구간에 속하는 실수들로 이루어진 n차원 텐서를 표현한다. 예를 들어 0.0~1.0 사이 값 하나를 갖는 가속 페달은 `Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)`로 인코딩할 수 있다. 여기서 `shape` 인자는 길이 1인 튜플로, 값 하나짜리 1차원 텐서를 만든다. `dtype`은 공간 값의 자료형을 지정하며, 여기서는 NumPy의 32비트 실수형이다. 또 다른 예로 Atari 화면 관측(크기 210×160의 RGB 이미지)은 `Box(low=0, high=255, shape=(210, 160, 3), dtype=np.uint8)`로 나타낼 수 있다. 이 경우 `shape`는 세 요소의 튜플로, 첫째는 이미지의 높이, 둘째는 너비, 셋째는 3(빨강·초록·파랑의 색상 평면 세 개에 대응)이다. 즉 모든 관측은 100,800바이트짜리 3차원 텐서다.
- **`Tuple`**: `Space`의 마지막 자식 클래스로, 여러 `Space` 클래스 인스턴스를 하나로 묶는다. 이를 이용해 원하는 만큼 복잡한 행동·관측 공간을 만들 수 있다. 예를 들어 자동차의 행동공간을 만든다고 하자. 자동차는 핸들 각도·브레이크 페달·가속 페달처럼 매 타임스탬프마다 바뀌는 여러 제어 장치가 있다. 이 셋은 하나의 `Box` 인스턴스 안에 세 개의 실수값으로 지정할 수 있다. 여기에 더해 방향지시등(끔/좌/우)이나 경적(끔/켬) 같은 이산 제어도 있다. 이 모두를 하나의 행동공간 명세로 합치려면 다음 코드를 쓴다.

```python
Tuple(spaces=(
  Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32),
  Discrete(n=3),
  Discrete(n=2)
))
```

이런 유연함은 실제로 잘 쓰이지 않는다. 이 책에서는 대부분 `Box`와 `Discrete` 행동·관측공간만 보게 될 것이지만, `Tuple` 클래스가 유용할 때도 있다.

이 밖에도 Gym에는 다른 `Space` 하위 클래스들이 정의되어 있다. 예를 들어 가변 길이 시퀀스를 나타내는 `Sequence`, 문자열을 나타내는 `Text`, 노드와 그 연결을 표현하는 `Graph` 등이다. 하지만 지금까지 설명한 세 가지(`Discrete`, `Box`, `Tuple`)가 가장 널리 쓰인다.

모든 환경은 `Space` 타입인 두 멤버를 갖는다: `action_space`와 `observation_space`. 이 덕분에 어떤 환경에도 통하는 **범용 코드**를 짤 수 있다. 물론 화면 픽셀을 다루는 것과 이산 관측을 다루는 것은 방식이 다르므로(전자는 합성곱 신경망 같은 컴퓨터 비전 도구로 전처리하고 싶을 수 있다), 대부분의 경우 특정 환경(또는 환경 그룹)에 맞춰 코드를 최적화하게 되지만, Gym이 범용 코드를 짜는 것을 막지는 않는다.

### 3.5 환경 (The Environment)

환경은 Gym에서 `Env` 클래스로 표현되며, 다음 멤버를 갖는다.
- `action_space`: `Space` 클래스의 필드로, 이 환경에서 허용되는 행동의 명세를 제공한다.
- `observation_space`: 같은 `Space` 클래스이지만, 환경이 제공하는 관측을 명세한다.
- `reset()`: 환경을 초기 상태로 리셋하고, 초기 관측 벡터와 환경으로부터의 추가 정보를 담은 dict를 반환한다.
- `step()`: 에이전트가 행동을 실행하게 하고, 그 행동의 결과에 대한 정보를 반환한다.
  - 다음 관측
  - 지역적(local) 보상
  - 에피소드 종료 플래그
  - 에피소드가 **잘렸는지(truncated)** 를 나타내는 플래그
  - 환경으로부터의 추가 정보를 담은 딕셔너리

`step()` 메서드는 조금 복잡해서 뒤에서 자세히 다룬다.

`Env` 클래스에는 `render()`처럼 관측을 사람이 보기 좋은 형태로 얻을 수 있게 해주는 유틸리티 메서드도 더 있지만, 이 책에서는 자주 쓰지 않는다. 전체 목록은 Gym 문서에서 볼 수 있으며, 여기서는 핵심 메서드인 `reset()`과 `step()`에 집중한다.

#### reset() — 더 단순한 쪽부터

`reset()` 메서드는 인자가 없다. 환경에게 "초기 상태로 리셋하고 초기 관측을 얻어라"라고 지시한다. **환경을 만든 직후에는 반드시 `reset()`을 호출해야 한다**는 점을 기억하자. 1장에서 배웠듯, 에이전트와 환경의 상호작용에는 끝("게임 오버" 화면 같은)이 있을 수 있고, 이런 세션을 **에피소드**라 부른다. 에피소드가 끝나면 에이전트는 처음부터 다시 시작해야 한다. 이 메서드가 반환하는 값은 환경의 **첫 관측**이다.

관측 외에, `reset()`은 두 번째 값도 반환한다 — 환경별 추가 정보를 담은 딕셔너리다. 대부분의 표준 환경은 이 딕셔너리에 아무것도 넣지 않지만, 더 복잡한 환경(예: 나중에 살펴볼 대화형 소설 게임 에뮬레이터인 TextWorld)은 표준 관측에 담기지 않는 추가 정보를 여기에 넣을 수도 있다.

#### step() — 환경 기능의 핵심

`step()` 메서드는 환경 기능의 핵심이다. 이 한 번의 호출로 다음 일들이 한꺼번에 일어난다.
- 다음 스텝에서 실행할 행동을 환경에게 알려주기
- 이 행동을 반영한 새 관측을 환경으로부터 받기
- 이번 스텝으로 얻은 보상을 받기
- 에피소드가 끝났는지 알려주는 신호를 받기
- 에피소드가 **잘렸는지(truncated)** 알려주는 플래그 받기 (예: 시간 제한이 걸려있는 경우)
- 환경별 추가 정보를 담은 딕셔너리 받기

목록의 첫 항목(행동)이 `step()` 메서드의 **유일한 인자**이고, 나머지는 이 메서드가 **반환**하는 값이다. 정확히는, 다섯 개 요소(`observation`, `reward`, `done`, `truncated`, `info`)로 이루어진 **파이썬 튜플**이다(앞서 본 `Tuple` 클래스와는 다른, 그냥 파이썬 기본 튜플이다).

각 요소의 타입과 의미는 다음과 같다.

| 요소 | 타입/의미 |
|---|---|
| `observation` | 관측 데이터를 담은 NumPy 벡터 또는 행렬 |
| `reward` | 보상의 float 값 |
| `done` | 에피소드가 끝났으면 `True`인 불리언. `True`이면 더 이상 행동을 못 하므로 반드시 `reset()`을 호출해야 한다 |
| `truncated` | 에피소드가 **잘렸을** 때 `True`인 불리언. 대부분의 환경에서는 에피소드 길이를 제한하는 `TimeLimit`을 의미하지만, 환경에 따라 다른 뜻일 수 있다. "에이전트가 에피소드 끝에 도달했다"와 "에이전트가 환경의 시간 제한에 도달했다"를 구분하고 싶을 때 유용하도록, `done`과 별도로 분리되어 있다. `truncated`가 `True`인 경우에도 `done`과 마찬가지로 `reset()`을 호출해야 한다 |
| `info` | 환경별 추가 정보를 담은 딕셔너리. 무엇이든 될 수 있다. 일반적인 RL 방법에서는 보통 이 값을 무시하는 것이 관례다 |

에이전트 코드에서 환경을 사용하는 방식이 대략 감이 왔을 것이다 — 루프를 돌면서, `done` 또는 `truncated` 플래그가 `True`가 될 때까지 행동을 넣어 `step()` 메서드를 호출한다. 그 후 `reset()`을 호출해 다시 시작한다. 이제 딱 한 가지 빠진 조각이 남았다 — **애초에 `Env` 객체를 어떻게 만드는가?**

### 3.6 환경 만들기 (Creating an Environment)

모든 환경은 `EnvironmentName-vN` 형태의 고유한 이름을 갖는다. 여기서 `N`은 같은 환경의 서로 다른 버전을 구분하는 번호다(예를 들어 버그가 수정되었거나 주요 변경이 생겼을 때 번호가 올라간다). 환경을 만들려면, `gymnasium` 패키지가 제공하는 `make(name)` 함수를 쓴다. 이 함수의 유일한 인자는 환경 이름의 문자열이다.

이 글을 쓰는 시점 기준, Gymnasium 0.29.1 버전(`[atari]` 확장을 포함해 설치했을 때)은 서로 다른 이름의 환경을 **1,003개** 담고 있다. 물론 이 전부가 유일한 환경은 아니다 — 이 목록에는 한 환경의 모든 버전이 다 들어있기 때문이다. 게다가 같은 환경이라도 설정과 관측공간에 여러 변형이 있을 수 있다. 예를 들어 Atari 게임 Breakout은 다음과 같은 환경 이름들을 갖는다.

- **Breakout-v0, Breakout-v4**: 공의 초기 위치와 방향이 무작위인 원조 Breakout.
- **BreakoutDeterministic-v0, BreakoutDeterministic-v4**: 공의 초기 배치와 속도 벡터가 항상 같은 Breakout.
- **BreakoutNoFrameskip-v0, BreakoutNoFrameskip-v4**: 프레임 스킵 없이 모든 프레임이 에이전트에게 보여지는 Breakout. (이게 없으면 매 행동이 여러 연속 프레임 동안 그대로 실행된다.)
- **Breakout-ram-v0, Breakout-ram-v4**: 화면 픽셀 대신 아타리 에뮬레이션 메모리 전체(128바이트)를 관측으로 주는 Breakout.
- **Breakout-ramDeterministic-v0, Breakout-ramDeterministic-v4**: 초기 상태가 같은, 메모리 관측 버전.
- **Breakout-ramNoFrameskip-v0, Breakout-ramNoFrameskip-v4**: 프레임 스킵이 없는, 메모리 관측 버전.

즉 게임 하나에 총 **12개**의 환경이 존재하는 셈이다. Breakout을 본 적이 없다면 아래 화면을 보자.

![[fig_2_2_v3.png]]
*그림 2.2 — Breakout 게임 플레이 화면*

이런 중복을 제거하고 나면, Gymnasium은 인상적이게도 **198개의 고유한 환경**을 제공하며, 다음과 같은 몇 그룹으로 나뉜다.

- **고전 제어 문제(Classic control problems)**: 최적 제어 이론과 RL 논문의 벤치마크·데모용으로 쓰이는 장난감 수준의 과제들. 대개 저차원의 관측·행동공간을 갖고, 알고리즘을 구현했을 때 빠르게 점검해보는 용도로 유용하다. RL계의 "MNIST"라 생각하면 된다(MNIST는 얀 르쿤이 만든 손글씨 숫자 인식 데이터셋).
- **아타리 2600(Atari 2600)**: 1970년대 고전 게임기의 게임들. 63개의 고유한 게임이 있다.
- **알고리즘(Algorithmic)**: 관측한 시퀀스를 복사하거나 숫자를 더하는 것 같은 작은 계산 과제를 수행하는 문제들.
- **Box2D**: Box2D 물리 시뮬레이터를 이용해 걷기나 자동차 조종을 학습하는 환경.
- **MuJoCo**: 여러 연속 제어 문제에 쓰이는 또 다른 물리 시뮬레이터.
- **파라미터 튜닝(Parameter tuning)**: 신경망 파라미터를 최적화하는 데 RL을 쓰는 문제.
- **토이 텍스트(Toy text)**: 단순한 격자 세계 텍스트 환경.

물론 Gym API를 지원하는 RL 환경의 총 개수는 이보다 훨씬 많다. 예를 들어 Farama Foundation은 멀티 에이전트 RL, 3D 내비게이션, 로보틱스, 웹 자동화 같은 특수 주제와 관련된 여러 저장소를 별도로 관리한다. 이 밖에도 수많은 서드파티(third-party) 저장소가 있다. 감을 잡고 싶다면 Gymnasium 문서의 `https://gymnasium.farama.org/environments/third_party_environments`를 참고하자.

이제 이론은 이쯤 하고, Gym 환경 하나를 다루는 실제 파이썬 세션을 살펴보자.

---

## 4. CartPole 세션 (The CartPole Session)

지금까지 배운 지식을 적용해, Gym이 제공하는 가장 단순한 RL 환경 중 하나를 탐험해보자.

```python
$ python
>>> import gymnasium as gym
>>> e = gym.make("CartPole-v1")
```

- `import gymnasium as gym`: `gymnasium` 패키지를 불러오되, 코드에서는 짧게 `gym`이라는 이름으로 쓴다.
- `e = gym.make("CartPole-v1")`: `CartPole`이라는 환경을 만든다. 이 환경은 고전 제어 그룹에 속하며, 핵심은 **막대가 붙은 플랫폼을 제어**하는 것이다 (아래 그림 참고).

플랫폼에 붙은 막대는 오른쪽이나 왼쪽으로 쓰러지려는 성질이 있고, 매 스텝마다 플랫폼을 좌우로 움직여서 막대가 넘어지지 않게 균형을 잡아야 하는 것이 까다로운 점이다.

![[fig_2_3_v3.png]]
*그림 2.3 — CartPole 환경. 검은 카트 위에 막대가 세워져 있고, 이 막대가 좌우로 쓰러지지 않도록 균형을 잡아야 한다.*

이 환경의 관측값은 **네 개의 부동소수점 숫자**로, 막대 무게중심의 x좌표, 그 속도, 플랫폼에 대한 각도, 각속도에 대한 정보를 담고 있다. 물론 수학과 물리학 지식을 적용하면 이 숫자들을 행동으로 변환해 막대 균형 잡는 일이 그렇게 어렵지 않겠지만, 우리의 문제는 다르다 — **이 숫자들이 정확히 무엇을 뜻하는지 전혀 모른 채로**, 오직 보상만으로 어떻게 이 시스템의 균형을 잡는 법을 배울 수 있을까? 이 환경의 보상은 **매 타임스텝마다 1**이며, 막대가 쓰러질 때까지 에피소드가 계속된다. 그러니 더 많은 누적 보상을 받으려면, 막대가 쓰러지지 않도록 플랫폼의 균형을 잘 잡아야 한다.

이 문제는 어려워 보일 수 있지만, 딱 두 챕터 뒤에는 관측된 숫자들이 무엇을 뜻하는지 전혀 모른 채로, 오직 시행착오와 약간의 RL 마법만으로 CartPole을 손쉽게 푸는 알고리즘을 만들게 될 것이다.

세션을 계속 이어가자.

```python
>>> obs, info = e.reset()
>>> obs
array([ 0.02100407,  0.02762252, -0.01519943, -0.0103739 ], dtype=float32)
>>> info
{}
```

- 환경을 리셋해서 첫 관측을 얻었다. (새로 만든 환경에서는 항상 리셋을 먼저 호출해야 한다.) 관측이 네 개의 숫자라는 것도 확인했다.
- `info`는 빈 딕셔너리 `{}` — CartPole은 추가 정보를 따로 주지 않는다.

이제 환경의 행동공간과 관측공간을 살펴보자.

```python
>>> e.action_space
Discrete(2)
>>> e.observation_space
Box([-4.8000002e+00 -3.4028235e+38 -4.1887903e-01 -3.4028235e+38], [4.8000002e+00
3.4028235e+38 4.1887903e-01 3.4028235e+38], (4,), float32)
```

- `action_space`는 `Discrete` 타입이므로, 우리가 취할 수 있는 행동은 **0 또는 1**뿐이다. 여기서 0은 플랫폼을 왼쪽으로 미는 것, 1은 오른쪽으로 미는 것을 뜻한다. ([[관측공간과 행동공간(Space)]] 참고)
- `observation_space`는 `Box(4,)` — 즉 네 숫자로 이루어진 벡터다. `observation_space` 필드에 표시된 첫 번째 리스트는 **하한**, 두 번째는 **상한**이다.

문서화 문자열(docstring)에서 `CartPole` 클래스가 관측값의 의미를 자세히 설명해준다.

- **카트 위치(Cart position)**: −4.8 ~ 4.8 범위의 값
- **카트 속도(Cart velocity)**: −∞ ~ ∞ 범위의 값
- **막대 각도(Pole angle)**: 라디안 단위 −0.418 ~ 0.418 범위의 값
- **막대 각속도(Pole angular velocity)**: −∞ ~ ∞ 범위의 값

파이썬은 무한대를 나타낼 때 `float32`의 최댓값·최솟값을 쓰는데, 그래서 경계 벡터의 일부 항목이 $10^{38}$ 규모의 값으로 나타난다. 이런 내부적인 세부 사항은 알아두면 흥미롭지만, RL 방법으로 이 환경을 푸는 데는 **전혀 필요하지 않다.**

궁금하다면 Gymnasium 저장소의 `cartpole.py` 파일(`https://github.com/Farama-Foundation/Gymnasium/blob/main/gymnasium/envs/classic_control/cartpole.py#L40`)에서 이 환경의 소스 코드를 직접 들여다볼 수 있다.

한 걸음 더 나아가, 환경에 행동을 보내보자.

```python
>>> e.step(0)
(array([-0.01254663, -0.22985364, -0.01435183,  0.24902613], dtype=float32), 1.0, False,
False, {})
```

행동 `0`을 실행해서 플랫폼을 왼쪽으로 밀었고, 다섯 요소의 튜플을 받았다.

- 네 숫자로 된 새 관측 벡터
- 보상 `1.0`
- `done` 플래그 값 `False` — 에피소드가 아직 끝나지 않았고, 막대 균형 잡기가 그럭저럭 잘 되고 있다는 뜻
- `truncated` 플래그 값 `False` — 잘리지 않았다는 뜻
- 추가 정보가 담긴 빈 딕셔너리

다음으로, `Space` 클래스의 `sample()` 메서드를 `action_space`와 `observation_space`에 각각 사용해보자. ([[관측공간과 행동공간(Space)]]의 샘플링 설명 참고)

```python
>>> e.action_space.sample()
0
>>> e.action_space.sample()
1
>>> e.observation_space.sample()
array([-4.05354548e+00, -1.13992760e+38, -1.21235274e-01,  2.89040989e+38],
      dtype=float32)
>>> e.observation_space.sample()
array([-3.6149189e-01, -1.0301251e+38, -2.6193827e-01, -2.6395525e+36],
      dtype=float32)
```

이 메서드는 그 공간에 속한 **무작위 샘플**을 반환한다. 우리의 `Discrete` 행동공간에서는 0 또는 1 중 하나가 무작위로 나오고, 관측공간에서는 네 숫자로 된 무작위 벡터가 나온다. 관측공간의 무작위 샘플은 그다지 쓸모가 없지만, **행동공간의 무작위 샘플**은 어떻게 행동해야 할지 확신이 없을 때 유용하게 쓸 수 있다.

> [!tip] 왜 유용할까?
> 아직 아무런 RL 방법도 배우지 않았지만, Gym 환경을 가지고 그냥 실험해보고 싶을 때 특히 편리하다. 지금부터 배울 내용이 바로 이것이다 — CartPole용 랜덤 에이전트를 만들 만큼 충분히 알게 되었으니, 직접 만들어보자.

---

## 5. 랜덤 CartPole 에이전트 (The Random CartPole Agent)

환경이 앞선 절의 첫 예제보다 훨씬 복잡해졌음에도, 에이전트의 코드는 오히려 **훨씬 짧다.** 이것이 바로 **재사용성, 추상화, 서드파티 라이브러리의 힘**이다.

전체 코드는 `Chapter02/02_cartpole_random.py` 에 있다.

```python
import gymnasium as gym

if __name__ == "__main__":
    env = gym.make("CartPole-v1")
    total_reward = 0.0
    total_steps = 0
    obs, _ = env.reset()
```

- `env = gym.make("CartPole-v1")`: 환경을 생성한다.
- `total_reward`, `total_steps`: 각각 누적 보상과 누적 스텝 수를 세는 카운터. 0에서 시작.
- `obs, _ = env.reset()`: 환경을 리셋해 첫 관측을 얻는다. `_`는 파이썬 관례로, "이 값은 필요 없으니 버린다"는 뜻이다 — 여기서는 `info` 딕셔너리를 그냥 무시한다는 표시다. 우리 에이전트는 어차피 확률적으로(무작위로) 행동하므로, 이 첫 관측 자체도 실제로는 쓰지 않는다.

```python
    while True:
        action = env.action_space.sample()
        obs, reward, is_done, is_trunc, _ = env.step(action)
        total_reward += reward
        total_steps += 1
        if is_done:
            break

    print("Episode done in %d steps, total reward %.2f" % (total_steps, total_reward))
```

- `action = env.action_space.sample()`: 행동공간에서 무작위로 행동 하나를 뽑는다.
- `obs, reward, is_done, is_trunc, _ = env.step(action)`: 그 행동을 환경에 제출하고, 새 관측·보상·종료 플래그·잘림 플래그를 받는다(마지막 `info`는 다시 버린다).
- `total_reward += reward`, `total_steps += 1`: 누적값을 갱신한다.
- `if is_done: break`: 에피소드가 끝나면 루프를 빠져나온다.
- 마지막에 몇 스텝 만에 끝났는지, 누적 보상이 얼마였는지 출력한다.

이 루프를 요약하면: 무작위 행동을 샘플링한 뒤 환경에 실행해 달라고 요청하고, 그 결과로 다음 관측(`obs`)과 보상, `is_done`, `is_trunc` 플래그를 받는다. 에피소드가 끝나면 루프를 멈추고, 몇 스텝이 걸렸는지·보상이 얼마나 쌓였는지 보여준다. 이 예제를 실행하면 다음과 비슷한 결과를 보게 된다 (에이전트가 무작위이므로 정확히 같지는 않다).

```
Chapter02$ python 02_cartpole_random.py
Episode done in 12 steps, total reward 12.00
```

평균적으로, 우리의 랜덤 에이전트는 막대가 쓰러지고 에피소드가 끝나기까지 **12~15 스텝** 정도를 버틴다. Gym의 대부분 환경에는 "**보상 경계(reward boundary)**"라는 것이 있는데, 이는 환경을 "풀었다(solve)"고 인정받으려면 **연속 100 에피소드 동안 평균적으로 얼마의 보상**을 얻어야 하는지를 나타낸다. CartPole의 경우 이 경계는 **195**다 — 즉 평균적으로 195 타임스텝 이상 막대를 버텨야 한다. 이 기준으로 보면 우리의 랜덤 에이전트 성능은 형편없어 보인다. 하지만 실망할 필요는 없다. 우리는 이제 막 시작했을 뿐이고, 곧 CartPole은 물론 훨씬 더 흥미롭고 도전적인 환경들도 풀게 될 것이다.

---

## 6. 추가 Gym API 기능 (Extra Gym API Functionality)

지금까지 다룬 내용은 Gym 핵심 API의 **3분의 2 정도**와, 에이전트를 짜는 데 필요한 필수 기능을 다룬 것이다. 나머지 API 없이도 지낼 수는 있지만, 알아두면 삶이 편해지고 코드가 깔끔해진다. 이제 나머지를 간단히 살펴보자.

### 6.1 래퍼(Wrappers)

아주 자주, 환경의 기능을 **일반적인 방식으로** 확장하고 싶을 때가 있다. 예를 들어 환경이 관측을 주는데, 이를 버퍼에 누적해서 에이전트에게 **최근 N개의 관측**을 함께 주고 싶은 경우가 있다 — 동적인 컴퓨터 게임에서는 한 프레임만으로는 게임 상태를 온전히 파악할 수 없는 경우가 흔해서 자주 나오는 상황이다. 또 다른 예로는 이미지 픽셀을 잘라내거나 전처리해서 에이전트가 더 다루기 쉽게 만들고 싶은 경우, 혹은 보상 점수를 어떤 식으로든 정규화하고 싶은 경우가 있다. 이렇게 **같은 구조를 갖는 상황**이 많다 — 기존 환경을 "감싸서(wrap)" 무언가를 하는 로직을 추가하고 싶은 것이다. Gym은 이를 위한 편리한 프레임워크를 제공한다 — 바로 `Wrapper` 클래스다. 자세한 설명은 [[Wrapper 래퍼 패턴]]에서 이어간다.

클래스 구조는 아래 그림과 같다.

![[fig_2_4_v3.png]]
*그림 2.4 — Gym의 `Wrapper` 클래스 계층 구조*

`Wrapper` 클래스는 `Env` 클래스를 **상속**한다. 그 생성자는 인자를 딱 하나만 받는다 — "감쌀(wrap)" 대상인 `Env` 클래스의 인스턴스다. 추가 기능을 더하려면, 확장하고 싶은 메서드(예: `step()`이나 `reset()`)를 **재정의(redefine)** 하면 된다. 유일한 요구사항은 상위 클래스의 원래 메서드를 호출해야 한다는 것이다. 감싸는 환경에 편하게 접근할 수 있도록, `Wrapper`는 두 가지 프로퍼티를 갖는다. `env`는 우리가 지금 감싸고 있는 바로 안쪽 환경(이 역시 또 다른 래퍼일 수 있다)이고, `unwrapped`는 어떤 래퍼도 없는 순수한 `Env`다.

관측만, 또는 행동만 다루고 싶은 것처럼 더 구체적인 요구사항을 다루기 위해, `Wrapper`의 특정 정보만 걸러내는 서브클래스들이 있다.

- `ObservationWrapper`: 부모의 `observation(obs)` 메서드를 재정의해야 한다. `obs` 인자는 감싸인 환경으로부터 온 관측이고, 이 메서드는 에이전트에게 줄 관측을 반환해야 한다.
- `RewardWrapper`: `reward(rew)` 메서드를 노출하며, 에이전트에게 주어지는 보상 값을 수정할 수 있다. 예를 들어 필요한 범위로 스케일을 조정하거나, 이전 행동을 바탕으로 할인을 추가하는 등의 작업이 가능하다.
- `ActionWrapper`: `action(a)` 메서드를 재정의해야 하며, 에이전트가 보낸 행동을 감싸인 환경에 전달하기 전에 조정할 수 있다.

조금 더 실전적인 예로, 에이전트가 보내는 행동 스트림에 개입해서, **10% 확률로** 현재 행동을 무작위 행동으로 바꿔치기하는 상황을 상상해보자. 현명하지 않은 일처럼 보일 수 있지만, 이 단순한 트릭은 1장에서 언급한 **탐험/활용(exploration/exploitation) 문제**를 푸는 데 가장 실전적이고 강력한 방법 중 하나다. 무작위 행동을 이따금 섞음으로써, 우리 에이전트가 환경을 탐험하게 만들고, 가끔은 정책이 정해준 길에서 벗어나게(drift) 만든다. 이는 `ActionWrapper` 클래스를 이용하면 손쉽게 구현할 수 있다 (전체 예제는 `Chapter02/03_random_action_wrapper.py`).

```python
import gymnasium as gym
import random

class RandomActionWrapper(gym.ActionWrapper):
    def __init__(self, env: gym.Env, epsilon: float = 0.1):
        super(RandomActionWrapper, self).__init__(env)
        self.epsilon = epsilon
```

- `class RandomActionWrapper(gym.ActionWrapper):` — `ActionWrapper`를 상속하는 새 래퍼 클래스를 정의한다.
- `super(RandomActionWrapper, self).__init__(env)`: 부모의 `__init__` 메서드를 호출해서, "내가 감쌀 환경은 이거야"라고 등록한다.
- `self.epsilon = epsilon`: 무작위 행동으로 바꿔치기할 확률(기본값 0.1, 즉 10%)을 저장한다.

부모 클래스로부터 재정의해야 하는 메서드는 다음과 같다. 이 메서드가 에이전트의 행동을 살짝 비틀어놓는다.

```python
    def action(self, action: gym.core.WrapperActType) -> gym.core.WrapperActType:
        if random.random() < self.epsilon:
            action = self.env.action_space.sample()
            print(f"Random action {action}")
            return action
        return action
```

- `if random.random() < self.epsilon:`: 매번 주사위를 굴려서, `epsilon`의 확률로 조건이 참이 된다.
- `action = self.env.action_space.sample()`: 조건이 참이면, 에이전트가 우리에게 보낸 행동 대신 **행동공간에서 무작위로 뽑은 행동**으로 교체한다.
- 콘솔에 메시지를 출력하는 부분은 우리 래퍼가 잘 작동하는지 눈으로 확인하기 위한 것으로, 실제 프로덕션 코드에서는 필요 없다.
- 마지막에 (교체됐든 안 됐든) 최종 `action`을 반환한다.

이제 래퍼를 적용할 차례다. 평범한 CartPole 환경을 만들어서 우리 `Wrapper` 생성자에 넘겨주기만 하면 된다.

```python
if __name__ == "__main__":
    env = RandomActionWrapper(gym.make("CartPole-v1"))
```

여기서부터는 원래 CartPole 대신, **우리의 래퍼**를 평범한 `Env` 인스턴스처럼 쓰면 된다. `Wrapper` 클래스가 `Env` 클래스를 상속하고 같은 인터페이스를 그대로 노출하므로, 원하는 만큼 래퍼를 겹겹이 **중첩**할 수 있다. 강력하고 우아하며 범용적인 해법이다.

랜덤 에이전트 코드와 거의 똑같지만, 이번에는 매번 똑같은 행동 `0`을 보낸다는 점이 다르다. 즉 이 에이전트 자체는 "멍청하게" 항상 같은 일을 한다.

```python
    obs = env.reset()
    total_reward = 0.0

    while True:
        obs, reward, done, _, _ = env.step(0)
        total_reward += reward
        if done:
            break

    print(f"Reward got: {total_reward:.2f}")
```

코드를 실행해보면, 래퍼가 실제로 작동하고 있음을 확인할 수 있다.

```
Chapter02$ python 03_random_action_wrapper.py
Random action 0
Random action 0
Reward got: 9.00
```

에이전트가 항상 `0`을 보내려 했지만, 콘솔 출력을 보면 래퍼가 이따금 그 행동을 가로채 무작위 행동으로 바꿔치기했다는 것을 알 수 있다.

### 6.2 환경 렌더링하기 (Rendering the Environment)

또 하나 알아둘 만한 기능은 **실행 중 환경을 렌더링(그림으로 보여주는 것)** 하는 것이다. 이는 두 가지 래퍼로 구현된다: `HumanRendering`과 `RecordVideo`.

이 두 클래스는 원래 OpenAI Gym 라이브러리에 있던 `Monitor` 래퍼(현재는 제거됨)를 대체한다. `Monitor`는 에이전트의 성능 정보를 파일에 기록하고, 선택적으로 에이전트가 움직이는 모습을 영상으로 남길 수도 있었다.

Gymnasium 라이브러리에서는 환경 내부에서 무슨 일이 벌어지는지 확인할 수 있는 두 클래스가 있다. 첫 번째는 `HumanRendering`으로, 환경에서 나온 이미지를 대화형으로 보여주는 별도의 그래픽 창을 연다. 이 렌더링을 사용하려면, 환경을 만들 때 `render_mode="rgb_array"` 인자로 초기화해야 한다. 이 인자는 환경에게 "`render()` 메서드가 픽셀을 반환하도록 하라"고 알려주고, 그 픽셀을 `HumanRendering` 래퍼가 받아서 보여준다.

`HumanRenderer` 래퍼를 사용하려면, 랜덤 에이전트 코드를 다음과 같이 바꾸면 된다 (전체 코드는 `Chapter02/04_cartpole_random_monitor.py`).

```python
if __name__ == "__main__":
    env = gym.make("CartPole-v1", render_mode="rgb_array")
    env = gym.wrappers.HumanRendering(env)
```

- `render_mode="rgb_array"`: 환경이 픽셀 배열을 만들어내도록 지시한다.
- `env = gym.wrappers.HumanRendering(env)`: 원래 환경을 `HumanRendering` 래퍼로 감싸서, 그 픽셀을 화면에 보여주는 창을 연다.

코드를 실행하면, 환경이 렌더링되는 창이 나타난다. 우리 에이전트는 막대를 오래 버티지 못하므로(최대 10~30스텝 정도), `env.close()` 메서드가 호출되는 즉시 창이 금방 사라진다.

![[fig_2_5_v3.png]]
*그림 2.5 — `HumanRendering`으로 렌더링된 CartPole 환경*

또 하나 유용할 수 있는 래퍼는 `RecordVideo`다. 이 래퍼는 환경에서 픽셀을 캡처해 에이전트가 활동하는 모습을 담은 **영상 파일**을 만든다. 사용법은 human renderer와 비슷하지만, 영상 파일을 저장할 디렉터리를 지정하는 인자가 추가로 필요하다. 그 디렉터리가 없으면 자동으로 생성된다.

```python
if __name__ == "__main__":
    env = gym.make("CartPole-v1", render_mode="rgb_array")
    env = gym.wrappers.RecordVideo(env, video_folder="video")
```

코드를 실행하면, 어떤 영상 파일이 만들어졌는지 보고한다.

```
Chapter02$ python 04_cartpole_random_monitor.py
MoviePy - Building video Chapter02/video/rl-video-episode-0.mp4.
MoviePy - Writing video Chapter02/video/rl-video-episode-0.mp4

MoviePy - Done !
MoviePy - video ready Chapter02/video/rl-video-episode-0.mp4
Episode done in 30 steps, total reward 30.00
```

이 래퍼는 특히 **GUI 없이 원격 머신**에서 에이전트를 돌릴 때 유용하다 — 화면에 직접 띄우는 대신 영상 파일로 남겨서 나중에 확인할 수 있기 때문이다.

### 6.3 더 많은 래퍼들 (More Wrappers)

Gymnasium은 이 밖에도 다양한 래퍼를 제공한다. 앞으로 나올 챕터에서 많이 쓰게 될 것이다. Atari 게임 이미지의 표준화된 전처리, 보상 정규화, 관측 프레임 쌓기(stacking), 환경의 벡터화(vectorization), 시간 제한 걸기 등 훨씬 더 많은 기능을 제공한다.

사용 가능한 래퍼의 전체 목록은 문서(`https://gymnasium.farama.org/api/wrappers/`)와 소스 코드에서 확인할 수 있다.

---

## 7. 요약

이 챕터에서 우리는 RL의 **실전적인 측면**을 배우기 시작했다.

1. **에이전트/환경의 최소 구조**를 순수 파이썬으로 직접 구현해보며, RL 프레임워크에 꼭 필요한 부품이 무엇인지 몸으로 익혔다.
2. **Gymnasium**(Gym의 후속 라이브러리)을 다뤄보며, 그 방대한 환경 목록을 살펴보고, 핵심 API(`Env` 클래스, `reset()`, `step()`)를 익혔다.
3. `Discrete`, `Box`, `Tuple`로 대표되는 **`Space` 클래스** 체계를 통해, 행동공간과 관측공간을 어떻게 표현하는지 배웠다.
4. `CartPole-v1` 환경에서 실제로 무작위로 행동하는 에이전트를 만들어 실행해봤다.
5. 환경 기능을 확장하는 표준 방법인 **래퍼(Wrapper)** — 그중에서도 `ActionWrapper`로 탐험을 강제하는 방법과, `HumanRendering`/`RecordVideo`로 에이전트의 활동을 시각화하는 방법을 배웠다.

다음 챕터에서는 **PyTorch**를 이용한 딥러닝 크래시 코스를 빠르게 훑어본다. PyTorch는 이 책 전체에서 가장 널리 쓰이는 딥러닝 툴킷 중 하나다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[API와 클래스·객체]]
- [[관측공간과 행동공간(Space)]]
- [[Wrapper 래퍼 패턴]]
- [[이산 행동과 연속 행동]]
- [[상태 관측 에피소드 정책]]

## 한눈에 보는 개념 지도
| 개념 | 코드/기호 | 한 줄 뜻 |
|---|---|---|
| 환경 | `Env` | 관측·보상을 주는 모든 것을 표현하는 Gym의 핵심 클래스 |
| 리셋 | `env.reset()` | 환경을 초기 상태로 되돌리고 첫 관측을 얻음 |
| 스텝 | `env.step(action)` | 행동을 실행하고 (관측, 보상, done, truncated, info) 반환 |
| 행동공간 | `env.action_space` | 가능한 행동들의 형태·범위 (`Discrete`, `Box` 등) |
| 관측공간 | `env.observation_space` | 관측값의 형태·범위 |
| 샘플링 | `Space.sample()` | 그 공간에서 값 하나를 무작위로 뽑음 |
| 래퍼 | `Wrapper`, `ObservationWrapper`, `ActionWrapper`, `RewardWrapper` | 환경을 감싸 기능을 추가하는 클래스 |
| 렌더링 | `HumanRendering`, `RecordVideo` | 환경 화면을 창에 띄우거나 영상으로 저장 |
