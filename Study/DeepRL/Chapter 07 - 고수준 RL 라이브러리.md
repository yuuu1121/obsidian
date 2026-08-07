---
title: "Chapter 7 — 고수준 RL 라이브러리 (Higher-Level RL Libraries)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 7
tags: [DeepRL, 강화학습, PTAN, DQN, 라이브러리]
---

# Chapter 7 · 고수준 RL 라이브러리

> [!abstract] 이 챕터를 한 문장으로
> [[Chapter 06]]에서 밑바닥부터 짰던 DQN 코드는, 사실 **거의 모든 RL 방법에서 반복되는 배관 작업**(행동 선택 · 환경과 주고받기 · 경험 저장 · 목표망 동기화)을 담고 있다. 이 챕터는 그 배관 작업을 **PTAN**이라는 고수준 라이브러리의 부품들(Agent, ActionSelector, ExperienceSource, 리플레이 버퍼, TargetNet)로 대체해, 앞으로는 "이 방법이 무엇을 하는지"에만 집중할 수 있게 한다.

---

## 들어가며 — 왜 고수준 라이브러리가 필요한가?

6장에서 만든 기본 DQN은 학습 코드 약 200줄에, 환경 래퍼 코드 50줄을 더한 정도였다. 처음 RL을 배울 때는 **모든 걸 직접 짜 보는 것**이 원리를 이해하는 데 매우 유용하다 — 그래서 6장까지는 일부러 그렇게 했다. 하지만 이 분야에 점점 익숙해질수록, 우리는 **같은 코드를 계속 반복해서 짜고 있다**는 사실을 깨닫게 된다.

> [!note] 왜 이렇게 반복이 심할까?
> [[Chapter 01 - 강화학습이란 무엇인가|1장]]에서 이야기했듯, RL은 매우 **유연한(general)** 틀이다. 관측(observation)과 행동(action)의 구체적인 형태에 대해 별로 가정을 두지 않기 때문에, CartPole용으로 짠 코드가 (약간의 수정만으로) Atari 게임에도 그대로 쓰인다. 즉 "환경-에이전트 상호작용"이라는 틀 자체가 재사용 가능하다는 뜻이고, 이는 곧 **틀을 담당하는 코드도 라이브러리로 뽑아낼 수 있다**는 뜻이다.

같은 코드를 매번 새로 짜는 것은 여러 면에서 손해다.

- **버그가 스며들기 쉽다.** 복사·붙여넣기를 반복하다 보면 어딘가에서 실수가 생긴다.
- **품질 저하.** 여러 프로젝트에서 두루 쓰이며 검증된 코드는 보통 성능·테스트·문서화 수준이 더 높다.

RL 실무의 역사는 아직 짧아서(컴퓨터과학의 다른 분야에 비해), 웹 개발처럼 Django·Flask 같은 성숙한 선택지가 많지는 않다. 그래도 몇몇 라이브러리들이 이 문제를 풀려고 노력해 왔고, 이 책의 저자도 그 중 하나인 **PTAN**을 직접 만들었다. 이 챕터에서는 PTAN을 자세히 다루고, 이후 챕터에서 계속 사용한다.

---

## 1. PTAN 라이브러리

[[PTAN 라이브러리 구조|PTAN(PyTorch AgentNet)]]은 GitHub에 공개된 라이브러리로, `pip install ptan==0.8`로 설치한다(이 책은 버전 0.8 기준).

### 1.1 설계 철학 — 두 극단 사이의 균형

RL 라이브러리는 보통 두 극단으로 나뉜다.

> [!important] 극단 1 vs 극단 2
> - **극단 1 — 너무 경직됨**: 라이브러리를 불러와 몇 줄만 쓰면 학습이 끝(예: OpenAI Baselines, Stable-Baselines3). 라이브러리가 의도한 대로 쓸 땐 편하지만, 조금이라도 특이한 걸 하려면 라이브러리 내부와 씨름하게 된다.
> - **극단 2 — 너무 자유로움**: 모든 로직(리플레이 버퍼, 궤적 처리 등)을 매번 처음부터 직접 짠다. 자유롭지만 지루하고 오류가 나기 쉽다.
>
> PTAN은 **고품질 빌딩 블록을 제공하되, 필요하면 언제든 새로 짜거나 바꿔 쓸 수 있게** 두 극단의 중간을 노린다.

### 1.2 PTAN이 제공하는 것들

| 구성요소 | 설명 |
|---|---|
| `Agent` | 관측(observation)들의 배치를 실행할 행동(action)들의 배치로 바꾼다. 필요하면 에피소드 동안의 내부 상태도 유지할 수 있다(예: 15장의 DDPG에서 쓰는 오른슈타인-울렌벡 탐험 과정) |
| `ActionSelector` | 신경망 출력에서 실제 행동을 골라내는 작은 로직. Agent와 함께 동작 |
| `ExperienceSource`와 하위 클래스들 | Agent 인스턴스와 Gym 환경으로부터 에이전트의 궤적 정보를 만들어 낸다 |
| `ExperienceSourceBuffer`와 하위 클래스들 | 다양한 특성의 리플레이 버퍼. 단순 버퍼와 우선순위 버퍼 두 종류 포함 |
| 다양한 유틸리티 | `TargetNet`, TensorBoard용 시계열 전처리 래퍼 등 |
| PyTorch Ignite 헬퍼 | PTAN을 Ignite 프레임워크와 통합할 때 사용 |
| Gym 환경용 래퍼 | 예: Atari 게임용 래퍼(6장에서 본 것과 비슷) |

이 각각을 아래에서 하나씩 자세히 살펴본다.

---

## 2. 행동 선택기 (Action Selectors)

PTAN 용어로 **action selector(행동 선택기)** 는, 신경망 출력을 실제 구체적인 행동 값으로 바꿔주는 객체다. 가장 흔한 두 가지 방식:

- **그리디(Greedy, argmax)**: Q-value 방법에서 흔히 쓰인다. 네트워크가 각 행동의 Q값을 예측하면, 그중 **가장 큰 $Q(s,a)$를 갖는 행동**을 고른다.
- **정책 기반(Policy-based)**: 네트워크가 행동에 대한 확률 분포(로짓 또는 정규화된 분포)를 출력하면, 그 분포에서 행동을 **샘플링**한다. [[Chapter 04]]의 교차 엔트로피 방법에서 이미 이런 방식을 봤다.

행동 선택기는 보통 `Agent`가 내부적으로 쓰며, 직접 손댈 일은 별로 없지만 원한다면 바꿔 쓸 수 있다. 라이브러리가 제공하는 구체 클래스:

- `ArgmaxActionSelector`: 전달된 텐서의 두 번째 축에 `argmax`를 적용한다. 배치 차원이 첫 번째 축이라고 가정한다.
- `ProbabilityActionSelector`: 이산 행동 집합의 확률 분포에서 샘플링한다.
- `EpsilonGreedyActionSelector`: `epsilon` 파라미터를 갖는다. 이 확률로 무작위 행동을 취하고, 그렇지 않으면 내부에 감싸 둔 다른 `ActionSelector`를 사용한다.

모든 클래스는 NumPy 배열을 입력으로 받는다고 가정한다. 코드로 직접 확인해 보자.

```python
>>> import numpy as np
>>> import ptan
>>> q_vals = np.array([[1, 2, 3], [1, -1, 0]])
>>> q_vals
array([[ 1,  2,  3],
       [ 1, -1,  0]])
>>> selector = ptan.actions.ArgmaxActionSelector()
>>> selector(q_vals)
array([2, 0])
```

한 줄씩 뜯어보면:
- `q_vals`: 배치 크기 2, 행동 개수 3짜리 Q값 표. 첫 행 `[1,2,3]`은 첫 번째 샘플의 각 행동에 대한 Q값이다.
- `selector = ptan.actions.ArgmaxActionSelector()`: 그리디 선택기 객체 생성.
- `selector(q_vals)`: **가장 큰 값의 인덱스**를 각 행에서 찾는다 → 첫 행은 인덱스 2(값 3)가 최대, 둘째 행은 인덱스 0(값 1)이 최대. 결과 `array([2, 0])`.

다음은 `EpsilonGreedyActionSelector`다. 이는 다른 행동 선택기를 **"감싸서(wrap)"**, `epsilon` 확률로 감싼 선택기 대신 무작위 행동을 취한다. `epsilon`이 0.0이면 무작위 행동은 전혀 없다.

```python
>>> selector = ptan.actions.EpsilonGreedyActionSelector(epsilon=0.0,
selector=ptan.actions.ArgmaxActionSelector())
>>> selector(q_vals)
array([2, 0])
```

`epsilon`을 1로 바꾸면 행동은 완전히 무작위가 된다.

```python
>>> selector = ptan.actions.EpsilonGreedyActionSelector(epsilon=1.0)
>>> selector(q_vals)
array([0, 1])
```

`epsilon` 값은 객체의 속성으로 직접 바꿀 수도 있다. 이는 훈련 중 epsilon을 점점 줄여나가는(anneal) 상황에서 매우 유용하다.

```python
>>> selector.epsilon
1.0
>>> selector.epsilon = 0.0
>>> selector(q_vals)
array([2, 0])
```

`ProbabilityActionSelector`도 사용법은 같지만, 입력이 **정규화된 확률 분포**여야 한다는 점이 다르다.

```python
>>> selector = ptan.actions.ProbabilityActionSelector()
>>> for _ in range(10):
...     acts = selector(np.array([
...         [0.1, 0.8, 0.1],
...         [0.0, 0.0, 1.0],
...         [0.5, 0.5, 0.0]
...     ]))
...     print(acts)
```

세 개의 분포(행렬의 세 행)에서 각각 샘플링한다.
- `[0.1, 0.8, 0.1]`: 인덱스 1인 행동이 80% 확률로 뽑힌다.
- `[0.0, 0.0, 1.0]`: 항상 인덱스 2가 뽑힌다(확률 100%).
- `[0.5, 0.5, 0.0]`: 인덱스 0과 1이 각각 50% 확률로 뽑힌다.

---

## 3. 에이전트 (The Agent)

`Agent` 엔티티는 환경에서 온 관측(observation)과 우리가 실행할 행동(action)을 **이어주는 통합된 방법**을 제공한다. 지금까지 우리는 신경망으로 관측에서 행동 가치를 얻고, 그 값에 대해 그리디하게(epsilon-greedy 방식으로) 행동하는 단순한 DQN 에이전트만 봐 왔다.

실제 RL 분야에서는 이보다 복잡한 형태가 많다.

- **정책 에이전트(policy agent)**: 행동의 가치 대신 행동에 대한 **확률 분포**를 예측한다. Part 3에서 다룰 방법들이다.
- **상태를 기억하는 에이전트**: 어떤 상황에서는 관측 하나(또는 최근 $k$개)만으로 행동을 결정하기 부족할 수 있다. 이런 경우 관측이 부분적으로만 보이는 **부분 관측 마르코프 결정 과정(Partially Observable MDP, POMDP)** 이라는 RL의 하위 분야가 이 문제를 다룬다(6장에서 잠깐 언급했지만 이 책에서 깊게 다루진 않는다).
- **연속 제어 에이전트**: Part 4에서 다룬다. 행동이 더 이상 이산적인 인덱스가 아니라 **실수값**이며, 관측에서 이 값을 직접 예측해야 한다.

이 모든 변형을 다 담기 위해, PTAN에서 에이전트는 `ptan.agent.BaseAgent`라는 확장 가능한 추상 클래스를 최상위에 두고 계층 구조로 짜여 있다. 상위 레벨에서 보면, 에이전트는 (NumPy 배열이나 NumPy 배열 리스트 형태의) 관측 배치를 받아, 취하고자 하는 행동 배치를 돌려주는 존재다. 배치 단위로 처리하는 이유는, 여러 관측을 한 번에 처리하는 것이 **GPU**에서는 개별 처리보다 훨씬 빠르기 때문이다.

추상 기반 클래스는 입출력 타입을 정하지 않으므로 매우 유연하다. 예를 들어 연속 제어 문제에서는 행동이 이산 인덱스가 아니라 실수값이 된다.

> [!tip] 언제 직접 에이전트를 만들어야 할까?
> 실전에서는 커스텀 에이전트가 필요한 경우가 자주 있다.
> - 신경망 구조가 특이해서(연속/이산이 섞인 행동 공간, 텍스트+이미지처럼 여러 형태의 관측 등)
> - 표준이 아닌 탐험 전략을 쓰고 싶어서(예: 연속 제어에서 인기 있는 오른슈타인-울렌벡 과정)
> - POMDP 환경이라 관측이 아니라 에이전트 내부 상태로 결정을 내려야 해서
>
> 이런 경우 모두 `BaseAgent`를 상속해서 쉽게 대응할 수 있다.

이제 라이브러리가 기본 제공하는 두 표준 에이전트, `DQNAgent`와 `PolicyAgent`를 살펴보자.

### 3.1 DQNAgent

행동 공간이 그리 크지 않은 Q-러닝 문제(Atari 게임이나 여러 고전적인 문제들)에 적용할 수 있다. `DQNAgent`는 관측 배치(NumPy 배열)를 입력받아, 신경망을 적용해 Q값을 얻고, 지정된 `ActionSelector`로 Q값을 행동 인덱스로 바꾼다.

이해를 돕기 위한 작은 예제를 보자. 단순함을 위해, 네트워크가 입력이 뭐든 항상 같은 출력을 내도록 정의한다.

```python
class DQNNet(nn.Module):
    def __init__(self, actions: int):
        super(DQNNet, self).__init__()
        self.actions = actions

    def forward(self, x):
        # 항상 (batch_size, actions) 모양의 대각 텐서를 만든다
        return torch.eye(x.size()[0], self.actions)
```

- `torch.eye(n, m)`: $n \times m$ 크기의 (일반화된) 단위행렬을 만든다. 즉 배치의 $i$번째 샘플에 대해서는 행동 $i$에 해당하는 값만 1이고 나머지는 0인 벡터를 돌려준다는 뜻 — 예측값이 항상 고정되어 있어서 결과를 예측하기 쉬운 "장난감" 네트워크다.

```python
>>> net = DQNNet(actions=3)
>>> net(torch.zeros(2, 10))
tensor([[1., 0., 0.],
        [0., 1., 0.]])
```

이 네트워크를 DQN 모델로 사용해 보자. 먼저 단순한 argmax 정책(가장 큰 값을 갖는 행동을 고른다)을 쓴다.

```python
>>> selector = ptan.actions.ArgmaxActionSelector()
>>> agent = ptan.agent.DQNAgent(model=net, action_selector=selector)
>>> agent(torch.zeros(2, 5))
(array([0, 1]), [None, None])
```

- 배치 크기 2, 각 관측 5개 값짜리 입력을 넣었다.
- 출력은 튜플 두 개로 구성된다.
  - **행동 배열**: 우리 배치에 대해 실행할 행동들. 첫 샘플은 행동 0, 둘째는 행동 1.
  - **에이전트의 내부 상태 리스트**: 상태를 기억하는 에이전트(stateful agent)를 위한 것이며, 우리 예제는 상태가 없는(stateless) 에이전트라 `[None, None]`이다.

이제 epsilon-greedy 탐험 전략을 갖는 에이전트를 만들어 보자. 다른 action selector를 넘겨주기만 하면 된다.

```python
>>> selector = ptan.actions.EpsilonGreedyActionSelector(epsilon=1.0)
>>> agent = ptan.agent.DQNAgent(model=net, action_selector=selector)
>>> agent(torch.zeros(10, 5))[0]
array([2, 0, 0, 1, 2, 1, 2, 2, 1])
```

`epsilon`이 1.0이므로 네트워크 출력과 무관하게 모든 행동이 무작위다. 하지만 훈련 중 epsilon을 시간에 따라 서서히 줄여나갈 때(**anneal**), 이 값을 즉석에서 바꿀 수 있어 매우 편리하다.

```python
>>> selector.epsilon = 0.5
>>> agent(torch.zeros(10, 5))[0]
array([0, 1, 2, 2, 0, 0, 1, 2, 0, 2])
>>> selector.epsilon = 0.1
>>> agent(torch.zeros(10, 5))[0]
array([0, 1, 2, 0, 0, 0, 0, 0, 0, 0])
```

epsilon이 낮아질수록 네트워크가 실제로 선호하는 행동(여기선 각 행에서 대각선 위치, 즉 인덱스가 배치 순서를 따라가는 패턴)이 더 자주 나오는 것을 볼 수 있다.

### 3.2 PolicyAgent

`PolicyAgent`는 네트워크가 이산 행동 집합에 대한 **정책 분포**를 출력한다고 가정한다. 이 분포는 로짓(정규화 안 된 값)이거나 정규화된 분포일 수 있다. 실전에서는 수치 안정성을 위해 **항상 로짓**을 쓰는 것이 좋다.

앞의 예제를 정책 버전으로 다시 짜 보자.

```python
class PolicyNet(nn.Module):
    def __init__(self, actions: int):
        super(PolicyNet, self).__init__()
        self.actions = actions

    def forward(self, x):
        # 이제 처음 두 행동이 같은 로짓 점수를 갖는 텐서를 만든다
        shape = (x.size()[0], self.actions)
        res = torch.zeros(shape, dtype=torch.float32)
        res[:, 0] = 1
        res[:, 1] = 1
        return res
```

- 이번 네트워크는 배치의 모든 샘플에 대해, 행동 0과 1의 로짓만 1이고 나머지는 0인 벡터를 돌려준다.

```python
>>> net = PolicyNet(actions=5)
>>> net(torch.zeros(6, 10))
tensor([[1., 1., 0., 0., 0.],
        ...
        [1., 1., 0., 0., 0.]])
```

이제 `PolicyAgent`를 `ProbabilityActionSelector`와 함께 사용한다. 후자는 정규화된 확률을 기대하므로, `PolicyAgent`에게 네트워크 출력에 **소프트맥스([[소프트맥스 Softmax]])** 를 적용하라고 알려줘야 한다.

```python
>>> selector = ptan.actions.ProbabilityActionSelector()
>>> agent = ptan.agent.PolicyAgent(model=net, action_selector=selector,
apply_softmax=True)
>>> agent(torch.zeros(6, 5))[0]
array([2, 1, 2, 0, 2, 3])
```

소프트맥스는 로짓이 0인 항목에도 **0이 아닌 확률**을 부여한다는 점을 기억하자.

```python
>>> torch.nn.functional.softmax(torch.tensor([1., 1., 0., 0., 0.]))
tensor([0.3222, 0.3222, 0.1185, 0.1185, 0.1185])
```

로짓이 1인 두 행동(0, 1)의 확률이 각각 약 32%로 가장 높지만, 로짓이 0인 나머지 행동들도 약 12%의 확률로 여전히 뽑힐 수 있다 — 이것이 정책 기반 방법에서 **탐험(exploration)** 이 자연스럽게 일어나는 방식이다.

---

## 4. 경험 소스 (Experience Source)

앞서 본 에이전트 추상화 덕분에 환경과의 통신을 일반적인 방식으로 구현할 수 있다. 이 통신은 에이전트의 행동을 Gym 환경에 적용해서 만들어지는 **궤적(trajectory)** 의 형태로 이뤄진다.

[[ExperienceSource와 리플레이버퍼|`ExperienceSource` 계열 클래스]]는 상위 레벨에서, 에이전트 인스턴스와 환경을 받아서 궤적의 스텝별 데이터를 제공한다. 주요 기능:

- 여러 환경과 동시에 통신을 지원한다. 배치 단위로 관측을 처리하므로 GPU를 효율적으로 쓸 수 있다.
- 궤적을 전처리해서 편리한 형태로 제공한다. 예를 들어, 보상을 누적한 부분 궤적 롤아웃을 지원한다. DQN이나 n-step DQN처럼 부분 궤적의 중간 스텝 하나하나에 관심이 없을 때, 이 중간 스텝들을 생략함으로써 메모리와 코드량을 아낄 수 있다.
- Gymnasium의 벡터화된 환경(`AsyncVectorEnv`, `SyncVectorEnv`)도 지원한다(17장에서 다룰 예정).

즉 경험 소스 클래스는 환경과의 상호작용 및 궤적 처리의 복잡함을 감춰주는 "마법의 블랙박스" 역할을 한다. 그러면서도 PTAN의 철학대로, 필요하면 기존 클래스를 상속하거나 직접 구현할 수 있게 유연성을 유지한다.

세 가지 클래스가 제공된다.

- **`ExperienceSource`**: 에이전트와 환경 집합을 이용해, 모든 중간 스텝을 포함한 n-스텝 부분 궤적을 만든다.
- **`ExperienceSourceFirstLast`**: `ExperienceSource`와 같지만, 전체 부분 궤적 대신 **첫 스텝과 마지막 스텝만** 유지하고(보상은 그 사이에 적절히 누적) 돌려준다. n-step DQN이나 **어드밴티지 액터-크리틱(A2C)** 롤아웃에서 메모리를 크게 아낄 수 있다.
- **`ExperienceSourceRollouts`**: Mnih의 Atari 논문에서 설명된 **비동기 어드밴티지 액터-크리틱(A3C)** 롤아웃 방식을 따른다(12장에서 다룰 주제).

모든 클래스는 CPU와 메모리 양쪽에서 효율적으로 작성되어 있다. 장난감 문제에서는 별로 티가 안 나지만, 다음 챕터에서 훨씬 많은 데이터를 저장·처리해야 하는 Atari 게임을 다룰 때 그 진가가 드러난다.

### 4.1 장난감 환경 만들기

`ExperienceSource` 클래스들이 어떻게 동작하는지 보여주기 위해, 관측이 예측 가능한 정수인 아주 단순한 Gym 환경을 구현한다. 관측은 0부터 4까지 증가하는 정수, 행동도 정수, 보상은 취한 행동값과 같다. 모든 에피소드는 정확히 10스텝으로 끝난다.

```python
class ToyEnv(gym.Env):
    def __init__(self):
        super(ToyEnv, self).__init__()
        self.observation_space = gym.spaces.Discrete(n=5)
        self.action_space = gym.spaces.Discrete(n=3)
        self.step_index = 0

    def reset(self):
        self.step_index = 0
        return self.step_index, {}

    def step(self, action: int):
        is_done = self.step_index == 10
        if is_done:
            return self.step_index % self.observation_space.n, 0.0, is_done, False, {}
        self.step_index += 1
        return self.step_index % self.observation_space.n, float(action), \
            self.step_index == 10, False, {}
```

- `observation_space`, `action_space`: 각각 5개, 3개짜리 이산 공간([[관측공간과 행동공간(Space)]] 참고).
- `step_index`: 몇 번째 스텝인지 세는 내부 카운터. `reset()`에서 0으로 초기화.
- `step(action)`: 카운터를 하나 늘리고, `(관측, 보상, done, truncated, info)` 5-튜플을 돌려준다. 관측은 `step_index`를 5로 나눈 나머지(0~4 반복), 보상은 **취한 행동값을 그대로** 돌려준다는 점이 이 장난감 환경의 특징이다. 10스텝째에 `is_done=True`가 된다.

여기에 더해, 관측과 상관없이 항상 고정된 행동만 내놓는 에이전트도 함께 정의한다.

```python
class DullAgent(ptan.agent.BaseAgent):
    def __init__(self, action: int):
        self.action = action

    def __call__(self, observations: tt.List[int], state: tt.Optional[list] = None) -> \
            tt.Tuple[tt.List[int], tt.Optional[list]]:
        return [self.action for _ in observations], state
```

- `BaseAgent`를 상속해 만든 가장 단순한 커스텀 에이전트다. `__call__`은 관측이 몇 개가 오든 항상 같은 `self.action`을 반환한다.

### 4.2 ExperienceSource 클래스

`ptan.experience.ExperienceSource`는 주어진 길이의 에이전트 궤적 조각을 만들어 낸다. 에피소드 종료(환경의 `step()`이 `is_done=True`를 돌려줄 때)를 자동으로 처리하고 환경을 리셋해 준다. 생성자는 다음 인자를 받는다.

- 사용할 Gym 환경(혹은 환경 리스트)
- 에이전트 인스턴스
- `steps_count=2`: 생성할 부분 궤적의 길이

이 클래스의 인스턴스는 표준 파이썬 반복자 인터페이스를 제공하므로, 그냥 순회하면 부분 궤적을 얻을 수 있다.

```python
>>> env = ToyEnv()
>>> agent = DullAgent(action=1)
>>> exp_source = ptan.experience.ExperienceSource(env=env, agent=agent, steps_count=2)
>>> for idx, exp in zip(range(3), exp_source):
...     print(exp)
(Experience(state=0, action=1, reward=1.0, done_trunc=False), Experience(state=1,
action=1, reward=1.0, done_trunc=False))
(Experience(state=1, action=1, reward=1.0, done_trunc=False), Experience(state=2,
action=1, reward=1.0, done_trunc=False))
(Experience(state=2, action=1, reward=1.0, done_trunc=False), Experience(state=3,
action=1, reward=1.0, done_trunc=False))
```

매 반복마다 `ExperienceSource`는 에이전트-환경 궤적의 한 조각을 돌려준다. 겉보기엔 단순해 보이지만 내부에서는 다음이 일어난다.

1. 환경에서 초기 상태를 얻기 위해 `reset()`이 호출된다.
2. 그 상태에서 실행할 행동을 고르라고 에이전트에게 물어본다.
3. `step()` 메서드가 실행되어 보상과 다음 상태를 얻는다.
4. 이 다음 상태가 다시 에이전트에게 전달되어 다음 행동을 결정한다.
5. 한 상태에서 다음 상태로의 전이 정보가 반환된다.
6. 환경이 에피소드 종료 플래그를 돌려주면, 남은 궤적을 방출하고 환경을 처음부터 다시 리셋한다.
7. 3번부터 과정이 계속 반복된다(경험 소스를 계속 순회하는 동안).

에이전트가 행동을 만드는 방식이 바뀌면(가중치 업데이트, epsilon 감소 등), 그 변화가 **즉시 경험 궤적에도 반영**된다는 점이 중요하다.

`ExperienceSource`가 돌려주는 튜플의 길이는 생성자에 넘긴 `step_count` 이하다(위 예에서 `steps_count=2`였으므로 튜플 길이는 2 또는 1이다 — 에피소드 끝에서는 1이 될 수 있다). 튜플의 각 원소는 `ptan.experience.Experience`라는 [[데이터클래스 dataclass]]의 인스턴스이며, 다음 필드를 갖는다.

- `state`: 행동을 취하기 전에 관측했던 상태
- `action`: 완료한 행동
- `reward`: 환경으로부터 받은 즉시 보상
- `done_trunc`: 에피소드가 끝났는지(done) 혹은 잘렸는지(truncated)

에피소드가 끝에 도달하면 부분 궤적은 더 짧아지고, 환경은 자동으로 리셋되므로 우리가 신경 쓸 필요 없이 계속 순회하면 된다.

```python
>>> for idx, exp in zip(range(15), exp_source):
...     print(exp)
...
(Experience(state=0, action=1, reward=1.0, done_trunc=False), Experience(state=1,
action=1, reward=1.0, done_trunc=False))
.......
(Experience(state=3, action=1, reward=1.0, done_trunc=False), Experience(state=4,
action=1, reward=1.0, done_trunc=True))
(Experience(state=4, action=1, reward=1.0, done_trunc=True),)
(Experience(state=0, action=1, reward=1.0, done_trunc=False), Experience(state=1,
action=1, reward=1.0, done_trunc=False))
(Experience(state=1, action=1, reward=1.0, done_trunc=False), Experience(state=2,
action=1, reward=1.0, done_trunc=False))
```

`ExperienceSource`에는 원하는 길이의 부분 궤적을 요청할 수도 있다.

```python
>>> exp_source = ptan.experience.ExperienceSource(env=env, agent=agent, steps_count=4)
>>> next(iter(exp_source))
(Experience(state=0, action=1, reward=1.0, done_trunc=False), Experience(state=1,
action=1, reward=1.0, done_trunc=False), Experience(state=2, action=1, reward=1.0,
done_trunc=False), Experience(state=3, action=1, reward=1.0, done_trunc=False))
```

여러 개의 `gym.Env` 인스턴스를 전달할 수도 있다. 이 경우 **라운드로빈 방식**으로 여러 환경을 번갈아 처리한다.

```python
>>> exp_source = ptan.experience.ExperienceSource(env=[ToyEnv(), ToyEnv()],
agent=agent, steps_count=4)
>>> for idx, exp in zip(range(5), exp_source):
...     print(exp)
```

> [!warning] 주의 — 반드시 독립된 환경 인스턴스를 넘겨라
> 여러 환경을 `ExperienceSource`에 넘길 때는 반드시 **서로 독립된 인스턴스**여야 한다. 같은 환경 객체 하나를 중복해서 넘기면 관측이 뒤섞여 엉망이 된다.

### 4.3 ExperienceSourceFirstLast 클래스

`ExperienceSource`는 주어진 길이의 전체 부분 궤적을 `(s, a, r)` 객체의 리스트로 제공한다. 다음 상태 $s'$은 다음 튜플에 담겨 오는데, 이게 항상 편리한 것은 아니다. 예를 들어 DQN 훈련에서는 벨만 근사를 한 스텝 단위로 계산하기 위해 $(s, a, r, s')$ 형태의 튜플이 필요하다. 또 n-step DQN 같은 확장에서는 여러 스텝의 관측을 (첫 상태, 행동, n스텝 누적 보상, n스텝 후 상태) 형태로 접고 싶어 한다.

이를 일반적인 방식으로 지원하기 위해 `ExperienceSource`의 간단한 서브클래스인 `ExperienceSourceFirstLast`가 구현되어 있다. 생성자 인자는 거의 같지만, 반환되는 데이터가 다르다.

```python
>>> exp_source = ptan.experience.ExperienceSourceFirstLast(env, agent, gamma=1.0,
steps_count=1)
>>> for idx, exp in zip(range(11), exp_source):
...     print(exp)
...
ExperienceFirstLast(state=0, action=1, reward=1.0, last_state=1)
ExperienceFirstLast(state=1, action=1, reward=1.0, last_state=2)
ExperienceFirstLast(state=2, action=1, reward=1.0, last_state=3)
ExperienceFirstLast(state=3, action=1, reward=1.0, last_state=4)
ExperienceFirstLast(state=4, action=1, reward=1.0, last_state=0)
...
ExperienceFirstLast(state=4, action=1, reward=1.0, last_state=None)
ExperienceFirstLast(state=0, action=1, reward=1.0, last_state=1)
```

이제 순회할 때마다 튜플이 아니라 **단일 객체**를 돌려주는데, 이 객체도 dataclass이며 다음 필드를 가진다.

- `state`: 행동을 결정할 때 썼던 상태
- `action`: 이 스텝에서 취한 행동
- `reward`: `steps_count` 스텝 동안의 부분 누적 보상 (여기선 `steps_count=1`이라 즉시 보상과 같다)
- `last_state`: 행동 실행 후 도달한 상태. 에피소드가 끝났다면 `None`

이 형태는 DQN 훈련에 훨씬 편리하다. 벨만 근사를 바로 적용할 수 있기 때문이다.

스텝 수를 늘려서 결과를 확인해 보자.

```python
>>> exp_source = ptan.experience.ExperienceSourceFirstLast(env, agent, gamma=1.0,
steps_count=2)
>>> for idx, exp in zip(range(11), exp_source):
...     print(exp)
...
ExperienceFirstLast(state=0, action=1, reward=2.0, last_state=2)
ExperienceFirstLast(state=1, action=1, reward=2.0, last_state=3)
ExperienceFirstLast(state=2, action=1, reward=2.0, last_state=4)
ExperienceFirstLast(state=3, action=1, reward=2.0, last_state=0)
ExperienceFirstLast(state=4, action=1, reward=2.0, last_state=1)
ExperienceFirstLast(state=0, action=1, reward=2.0, last_state=2)
ExperienceFirstLast(state=1, action=1, reward=2.0, last_state=3)
ExperienceFirstLast(state=2, action=1, reward=2.0, last_state=4)
ExperienceFirstLast(state=3, action=1, reward=2.0, last_state=None)
ExperienceFirstLast(state=4, action=1, reward=1.0, last_state=None)
ExperienceFirstLast(state=0, action=1, reward=2.0, last_state=2)
```

이제 매 반복마다 두 스텝을 하나로 접고, 즉시 보상을 계산한다(그래서 대부분 `reward=2.0`이다 — 각 스텝의 보상이 1.0씩이고 `gamma=1.0`이므로 그대로 더해진다). 흥미로운 샘플은 에피소드 끝부분에 있다.

```
ExperienceFirstLast(state=3, action=1, reward=2.0, last_state=None)
ExperienceFirstLast(state=4, action=1, reward=1.0, last_state=None)
```

에피소드가 끝나는 지점에서는 `last_state=None`이 되고, 동시에 에피소드 꼬리 부분의 보상도 정확히 계산해 준다. 이런 세세한 부분은, 직접 궤적 처리를 짠다면 실수하기 아주 쉬운 지점이다.

---

## 5. 경험 리플레이 버퍼 (Experience Replay Buffers)

DQN에서는 방금 얻은 경험을 곧바로 학습에 쓰지 않는다. 경험끼리 강하게 상관되어 있어서(non-IID, [[IID 독립항등분포]] 참고) 훈련이 불안정해지기 때문이다. 대신 큰 **리플레이 버퍼**를 두고 경험 조각들로 채운 뒤, 버퍼를 (무작위로 또는 우선순위 가중치로) 샘플링해서 훈련 배치를 만든다. 버퍼는 보통 최대 용량을 가지며, 한계에 도달하면 오래된 샘플이 밀려난다.

여기엔 몇 가지 구현 상의 요령이 있는데, 큰 문제를 다룰 때 매우 중요해진다.

- 큰 버퍼에서 어떻게 **효율적으로 샘플링**할 것인가
- 오래된 샘플을 어떻게 버퍼에서 **효율적으로 밀어낼** 것인가
- 우선순위 버퍼의 경우, 우선순위를 어떻게 **효율적으로 유지·갱신**할 것인가

Atari 게임처럼 샘플 하나하나가 이미지이고 1,000만~1억 개 규모를 다뤄야 한다면, 이는 결코 사소한 문제가 아니다. 작은 구현 실수 하나가 메모리 10~100배 증가나 훈련 속도의 대폭 저하로 이어질 수 있다.

[[ExperienceSource와 리플레이버퍼|PTAN이 제공하는 클래스]]는 `ExperienceSource`, `Agent`와 매끄럽게 통합된다.

- `ExperienceReplayBuffer`: 정해진 크기의 단순 리플레이 버퍼. 균등(무작위) 샘플링.
- `PrioReplayBufferNaive`: 단순하지만 효율이 낮은 우선순위 리플레이 버퍼. 샘플링 복잡도가 $O(n)$이라 버퍼가 크면 문제가 될 수 있다. 대신 코드가 훨씬 단순하며, 중간 크기 버퍼에서는 성능이 여전히 쓸 만해서 이 책의 일부 예제에서 사용한다.
- `PrioritizedReplayBuffer`: 세그먼트 트리(segment tree)를 이용해 샘플링한다. 코드는 난해해지지만 $O(\log n)$의 샘플링 복잡도를 갖는다.

다음은 리플레이 버퍼 사용 예다.

```python
>>> exp_source = ptan.experience.ExperienceSourceFirstLast(env, agent, gamma=1.0,
steps_count=1)
>>> buffer = ptan.experience.ExperienceReplayBuffer(exp_source, buffer_size=100)
>>> len(buffer)
0
>>> buffer.populate(1)
>>> len(buffer)
1
```

- `ExperienceReplayBuffer(exp_source, buffer_size=100)`: 최대 100개 샘플을 담는 버퍼를, 위에서 만든 `exp_source`를 소스로 삼아 생성한다.
- `buffer.populate(1)`: 경험 소스에서 샘플 1개를 뽑아 버퍼에 채운다.

모든 리플레이 버퍼는 다음 인터페이스를 제공한다.

- 버퍼의 모든 샘플을 순회할 수 있는 파이썬 반복자 인터페이스
- `populate(N)` 메서드: 경험 소스에서 $N$개의 샘플을 얻어 버퍼에 채운다.
- `sample(N)` 메서드: 버퍼에서 $N$개짜리 경험 배치를 얻는다.

따라서 일반적인 DQN 훈련 루프는 다음 스텝의 무한 반복으로 요약된다.

1. `buffer.populate(1)`을 호출해 환경에서 새 샘플을 하나 얻는다.
2. `batch = buffer.sample(BATCH_SIZE)`를 호출해 버퍼에서 배치를 얻는다.
3. 샘플링된 배치에 대해 손실을 계산한다.
4. 역전파(backpropagate)한다.
5. (바라건대) 수렴할 때까지 반복한다.

나머지는 전부 자동으로 처리된다 — 환경 리셋, 부분 궤적 처리, 버퍼 크기 유지 등.

```python
>>> for step in range(6):
...     buffer.populate(1)
...     if len(buffer) < 5:
...         continue
...     batch = buffer.sample(4)
...     print(f"Train time, {len(batch)} batch samples")
...     for s in batch:
...         print(s)
```

- `buffer.populate(1)`: 매 스텝 새 샘플 하나를 채운다.
- `if len(buffer) < 5: continue`: 버퍼가 아직 충분히 안 채워졌으면(여기선 최소 5개) 학습을 건너뛴다. 실전 DQN에서도 버퍼가 어느 정도 채워질 때까지는 학습을 시작하지 않는다.
- `buffer.sample(4)`: 버퍼가 충분히 찼으면 4개짜리 무작위 배치를 뽑아 훈련에 쓴다.

---

## 6. TargetNet 클래스

[[Chapter 06]]에서 이야기한 **부트스트래핑 문제**를 떠올려 보자. 훈련 중인 신경망이 다음 상태의 Q값 예측에도 쓰이면서, 정답으로 삼는 값 자체가 계속 흔들려 학습이 불안정해지는 문제였다. 이를 해결하기 위해, 현재 학습 중인 신경망을 다음 상태 Q값 예측에 쓰이는 신경망과 **분리**했다.

[[TargetNet 클래스|`TargetNet`]]은 같은 구조를 가진 두 신경망을 동기화하도록 도와주는 작고 유용한 클래스다. 두 가지 동기화 모드를 지원한다.

- `sync()`: 원본(source) 신경망의 가중치를 목표(target) 신경망으로 그대로 복사한다.
- `alpha_sync()`: 원본 신경망의 가중치를 0과 1 사이의 alpha 가중치로 **블렌딩**해서 목표 신경망에 반영한다.

첫 번째 모드는 Atari, CartPole처럼 **이산 행동 공간** 문제에서 목표망을 동기화하는 표준적인 방식이며, [[Chapter 06]]에서 우리가 했던 것과 같다. 두 번째 모드는 **연속 제어** 문제(Part 4에서 다룸)에서 쓰인다. 이런 문제에서는 두 신경망 파라미터 사이의 전이가 부드러워야 하므로, alpha 블렌딩을 쓴다. 공식은 다음과 같다.

$$w_i = w_i \cdot \alpha + s_i \cdot (1-\alpha)$$

여기서 $w_i$는 목표 신경망의 $i$번째 파라미터, $s_i$는 원본 신경망의 가중치다.

다음 신경망이 있다고 하자.

```python
class DQNNet(nn.Module):
    def __init__(self):
        super(DQNNet, self).__init__()
        self.ff = nn.Linear(5, 3)
    def forward(self, x):
        return self.ff(x)
```

목표 신경망은 다음과 같이 만든다.

```python
>>> net = DQNNet()
>>> net
DQNNet(
  (ff): Linear(in_features=5, out_features=3, bias=True)
)
>>> tgt_net = ptan.agent.TargetNet(net)
```

목표 신경망 객체는 두 필드를 가진다: `model`(원본 신경망 참조)과 `target_model`(원본의 깊은 복사본, deep copy). 두 신경망의 가중치를 비교하면 처음엔 동일하다.

```python
>>> net.ff.weight
Parameter containing:
tensor([[ 0.2039,  0.1487,  0.4420, -0.0210, -0.2726],
        ...
>>> tgt_net.target_model.ff.weight
Parameter containing:
tensor([[ 0.2039,  0.1487,  0.4420, -0.0210, -0.2726],
        ...
```

하지만 둘은 완전히 독립적이다. 원본을 바꿔도 목표망은 그대로다.

```python
>>> net.ff.weight.data += 1.0
>>> net.ff.weight
Parameter containing:
tensor([[1.2039, 1.1487, 1.4420, 0.9790, 0.7274],
        ...
>>> tgt_net.target_model.ff.weight
Parameter containing:
tensor([[ 0.2039,  0.1487,  0.4420, -0.0210, -0.2726],
        ...
```

다시 동기화하려면 `sync()`를 호출한다.

```python
>>> tgt_net.sync()
>>> tgt_net.target_model.ff.weight
Parameter containing:
tensor([[1.2039, 1.1487, 1.4420, 0.9790, 0.7274],
        ...
```

블렌딩된 동기화는 `alpha_sync()`로 한다.

```python
>>> net.ff.weight.data += 1.0
>>> tgt_net.alpha_sync(0.1)
>>> tgt_net.target_model.ff.weight
Parameter containing:
tensor([[2.1039, 2.0487, 2.3420, 1.8790, 1.6274],
        ...
```

`alpha=0.1`을 넘기면, 목표망 값의 10%는 그대로 유지하고 원본망의 새 값을 90% 반영한다는 뜻이다 — 급격한 변화 대신 서서히 따라가게 만든다.

---

## 7. Ignite 헬퍼

[[Chapter 03]]에서 살짝 언급했던 **PyTorch Ignite**는 이 책의 나머지 부분에서 훈련 루프 코드를 줄이기 위해 계속 사용된다. PTAN은 `ptan.ignite` 패키지에 Ignite 통합을 쉽게 해 주는 작은 헬퍼들을 제공한다.

- `EndOfEpisodeHandler`: `ignite.Engine`에 붙여서 `EPISODE_COMPLETED` 이벤트를 발생시키고, 엔진의 메트릭에 보상과 스텝 수를 기록한다. 또한 최근 에피소드들의 평균 보상이 미리 정한 목표치에 도달했을 때 이벤트를 발생시켜, 훈련을 멈추는 용도로도 쓸 수 있다.
- `EpisodeFPSHandler`: 에이전트와 환경 사이에 일어난 상호작용 수를 추적하고, **초당 프레임 수(FPS)** 로 성능 지표를 계산한다. 훈련 시작 이후 경과 시간(초)도 함께 추적한다.
- `PeriodicEvents`: 10, 100, 1,000 훈련 반복마다 해당하는 이벤트를 발생시킨다. TensorBoard에 기록되는 데이터 양을 줄이는 데 유용하다.

이 클래스들이 실제로 어떻게 쓰이는지는 다음 챕터에서 6장의 DQN 훈련을 다시 구현하고, 여러 DQN 확장·기법으로 수렴 속도를 개선해 볼 때 자세히 보게 된다.

---

## 8. PTAN CartPole 솔버

이제 PTAN의 부품들(아직 Ignite는 빼고)을 모아, 첫 환경이었던 CartPole을 풀어 보자. 전체 코드는 `Chapter07/06_cartpole.py`에 있다. 여기서는 방금 다룬 내용과 관련된 중요한 부분만 보여준다.

먼저 신경망(CartPole에 썼던 것과 같은 단순한 2층 순전파 신경망)을 만들고, 목표망·epsilon-greedy 행동 선택기·`DQNAgent`를 만든다. 그다음 경험 소스와 리플레이 버퍼를 만든다.

```python
net = Net(obs_size, HIDDEN_SIZE, n_actions)
tgt_net = ptan.agent.TargetNet(net)
selector = ptan.actions.ArgmaxActionSelector()
selector = ptan.actions.EpsilonGreedyActionSelector(epsilon=1, selector=selector)
agent = ptan.agent.DQNAgent(net, selector)
exp_source = ptan.experience.ExperienceSourceFirstLast(env, agent, gamma=GAMMA)
buffer = ptan.experience.ExperienceReplayBuffer(exp_source, buffer_size=REPLAY_SIZE)
```

한 줄씩 보면:
- `Net(obs_size, HIDDEN_SIZE, n_actions)`: 은닉층 크기 `HIDDEN_SIZE`인 2층 신경망. 입력은 관측 크기, 출력은 행동 개수만큼의 Q값.
- `TargetNet(net)`: 목표망 생성.
- `ArgmaxActionSelector()` → `EpsilonGreedyActionSelector(epsilon=1, selector=selector)`: 그리디 선택기를 epsilon-greedy로 감싼다. 초기 epsilon=1로 완전 무작위에서 시작.
- `DQNAgent(net, selector)`: 신경망과 선택기를 묶어 에이전트 완성.
- `ExperienceSourceFirstLast(env, agent, gamma=GAMMA)`: DQN 학습에 바로 쓸 수 있는 (시작상태, 행동, 누적보상, 마지막상태) 형태로 경험을 생성.
- `ExperienceReplayBuffer(exp_source, buffer_size=REPLAY_SIZE)`: 이 경험 소스를 채워 넣을 리플레이 버퍼.

이 몇 줄만으로 **데이터 파이프라인** 구성이 끝났다는 점을 눈여겨보자. 6장에서는 이 배관 작업에 훨씬 많은 코드가 필요했다.

이제 버퍼에 `populate()`를 호출하고, 거기서 훈련 배치를 샘플링하기만 하면 된다.

```python
while True:
    step += 1
    buffer.populate(1)

    for reward, steps in exp_source.pop_rewards_steps():
        episode += 1
        print(f"{step}: episode {episode} done, reward={reward:.2f}, "
              f"epsilon={selector.epsilon:.2f}")
        solved = reward > 150
    if solved:
        print("Whee!")
        break
    if len(buffer) < 2*BATCH_SIZE:
        continue
    batch = buffer.sample(BATCH_SIZE)
```

- `buffer.populate(1)`: 매 반복마다 환경에서 새 샘플 하나를 얻어 버퍼에 채운다.
- `exp_source.pop_rewards_steps()`: `ExperienceSource` 클래스가 제공하는 메서드로, 마지막 호출 이후 **완료된 에피소드들**의 (보상, 스텝 수) 튜플 리스트를 돌려준다.
- `solved = reward > 150`: CartPole에서 에피소드 보상이 150을 넘으면 충분히 학습됐다고 판단해 훈련을 멈춘다.
- `if len(buffer) < 2*BATCH_SIZE: continue`: 버퍼가 배치 크기의 2배만큼 채워지기 전까지는 학습을 건너뛴다.

훈련 루프의 나머지 부분에서는, `ExperienceFirstLast` 객체들의 배치를 DQN 훈련에 알맞은 텐서로 변환한다.

```python
batch = buffer.sample(BATCH_SIZE)
states_v, actions_v, tgt_q_v = unpack_batch(batch, tgt_net.target_model, GAMMA)
optimizer.zero_grad()
q_v = net(states_v)
q_v = q_v.gather(1, actions_v.unsqueeze(-1)).squeeze(-1)
loss_v = F.mse_loss(q_v, tgt_q_v)
loss_v.backward()
optimizer.step()
selector.epsilon *= EPS_DECAY

if step % TGT_NET_SYNC == 0:
    tgt_net.sync()
```

한 줄씩:
- `unpack_batch(...)`: 배치를 상태·행동·목표 Q값 텐서로 변환하는 헬퍼(아래에서 자세히 설명).
- `q_v = net(states_v)`: 현재 학습망으로 상태 배치의 Q값을 예측한다.
- `q_v.gather(1, actions_v.unsqueeze(-1)).squeeze(-1)`: 예측된 Q값들(행동 개수만큼) 중, **실제로 취했던 행동**에 해당하는 값만 뽑아낸다. `gather`는 인덱스로 값을 골라내는 PyTorch 연산이다.
- `F.mse_loss(q_v, tgt_q_v)`: 예측 Q값과 목표 Q값 사이의 평균제곱오차 손실.
- `loss_v.backward()`, `optimizer.step()`: 역전파와 파라미터 갱신([[신경망 경사하강 역전파 기초]]).
- `selector.epsilon *= EPS_DECAY`: 매 스텝 epsilon을 조금씩 줄여 탐험을 줄여 나간다. 이 하이퍼파라미터들로는 훈련 스텝 500쯤에 epsilon이 거의 0이 된다.
- `if step % TGT_NET_SYNC == 0: tgt_net.sync()`: 10번의 훈련 반복마다 목표망을 학습망과 동기화한다.

마지막 조각은 `unpack_batch` 함수다.

```python
@torch.no_grad()
def unpack_batch(batch: tt.List[ExperienceFirstLast], net: Net, gamma: float):
    states = []
    actions = []
    rewards = []
    done_masks = []
    last_states = []
    for exp in batch:
        states.append(exp.state)
        actions.append(exp.action)
        rewards.append(exp.reward)
        done_masks.append(exp.last_state is None)
        if exp.last_state is None:
            last_states.append(exp.state)
        else:
            last_states.append(exp.last_state)

    states_v = torch.as_tensor(np.stack(states))
    actions_v = torch.tensor(actions)
    rewards_v = torch.tensor(rewards)
    last_states_v = torch.as_tensor(np.stack(last_states))
    last_state_q_v = net(last_states_v)
    best_last_q_v = torch.max(last_state_q_v, dim=1)[0]
    best_last_q_v[done_masks] = 0.0
    return states_v, actions_v, best_last_q_v * gamma + rewards_v
```

이 함수는 `ExperienceFirstLast` 객체들의 배치를 받아 세 개의 텐서(상태, 행동, 목표 Q값)로 바꾼다.

- `@torch.no_grad()`: 이 함수 안에서는 그레이디언트를 계산하지 않는다는 표시. 목표 Q값 계산은 역전파 대상이 아니므로, 이렇게 명시해서 불필요한 계산 그래프 저장을 막는다([[자동미분과 계산그래프]] 참고).
- `done_masks.append(exp.last_state is None)`: `last_state`가 `None`이면(에피소드가 그 스텝에서 끝났으면) `True`를 기록. 나중에 목표 Q값을 0으로 만드는 데 쓰인다.
- `if exp.last_state is None: last_states.append(exp.state)`: `last_state`가 `None`인 경우, 텐서 계산에 쓸 자리 채우기용으로 임시로 원래 `state`를 넣는다(어차피 `done_masks`로 나중에 0 처리되므로 값 자체는 상관없다).
- `last_state_q_v = net(last_states_v)`: 목표망으로 **다음 상태**의 Q값을 예측한다.
- `best_last_q_v = torch.max(last_state_q_v, dim=1)[0]`: 각 다음 상태에서 **가장 큰 Q값**(그리디 행동의 가치)만 뽑는다.
- `best_last_q_v[done_masks] = 0.0`: 에피소드가 끝난 자리는 "미래 보상이 없다"는 뜻이므로 강제로 0으로 만든다.
- `best_last_q_v * gamma + rewards_v`: 벨만 방정식 그대로 — 즉시 보상 + 할인된 다음 상태의 최선 가치. 이것이 바로 우리가 신경망 예측이 맞춰야 할 **목표(target)** 값이다.

이 코드는 2,000~3,000 훈련 반복 안에 수렴한다.

```
Chapter07$ python 06_cartpole.py
26: episode 1 done, reward=25.00, epsilon=1.00
52: episode 2 done, reward=26.00, epsilon=0.82
...
2786: episode 116 done, reward=192.00, epsilon=0.00
Whee!
```

### 직접 짠 코드 vs PTAN 라이브러리 대응표

6장에서 직접 짠 배관 코드가, 이번 챕터의 PTAN 부품 어디에 대응하는지 정리하면 다음과 같다.

| 6장에서 직접 짠 것 | PTAN의 대응 부품 |
|---|---|
| epsilon-greedy 로직을 담은 `if random.random() < epsilon: ...` 분기 | `EpsilonGreedyActionSelector` |
| 신경망 출력에서 Q값이 최대인 행동 고르기 | `ArgmaxActionSelector` + `DQNAgent` |
| 환경 리셋·스텝 실행·에피소드 종료 처리 루프 | `ExperienceSource` / `ExperienceSourceFirstLast` |
| 직접 만든 리스트/deque 기반 리플레이 버퍼 | `ExperienceReplayBuffer` (또는 우선순위 버전) |
| `target_net = copy.deepcopy(net)` 후 수동 동기화 | `TargetNet` (`sync()` / `alpha_sync()`) |
| `(s, a, r, s')` 튜플을 직접 배치로 변환하는 코드 | `unpack_batch` (경험 데이터클래스 기반) |

---

## 9. 다른 RL 라이브러리들

TensorFlow가 PyTorch보다 더 인기 있던 시절도 있었지만, 요즘은 PyTorch가 이 분야를 주도하고 있고, 최근에는 성능이 더 좋다는 이유로 JAX를 쓰는 추세도 늘고 있다. 저자가 참고할 만하다고 추천하는 라이브러리 목록은 다음과 같다.

- **stable-baselines3**: OpenAI Stable Baselines의 포크. 검증된 RL 알고리즘 모음을 제공해, 자신이 짠 방법을 검증하는 기준(baseline)으로 쓰기 좋다.
- **TorchRL**: PyTorch용 RL 확장 라이브러리. 비교적 최근(2022년 말) 나왔지만, 유연한 클래스들을 조합·확장하는 설계 철학이 PTAN과 매우 비슷하다. 저자는 이 책의 나머지 부분에서도 TorchRL의 클래스를 함께 쓸 것이며, 다음 판(edition)에서는 아예 PTAN 대신 TorchRL 기반으로 바뀔 가능성이 높다고 언급한다.
- **Spinning Up**: OpenAI가 만든, 최신 RL 방법들에 대한 교육 자료 성격이 강한 저장소. 유지보수는 몇 년째 멈춰 있지만 학습 자료로서 가치가 있다.
- **Keras-RL**: 2016년 시작된 라이브러리. Keras(TensorFlow의 고수준 래퍼) 기반이며, 2019년 이후 업데이트가 없어 사실상 방치된 상태다.
- **Dopamine**: 구글이 2018년 공개한 TensorFlow 전용 라이브러리.
- **Ray**: 분산 머신러닝 실행을 위한 라이브러리로, RL 관련 유틸리티도 포함한다.
- **TF-Agents**: 역시 구글이 2018년 공개.
- **ReAgent**: Facebook Research가 만든 PyTorch 기반 라이브러리. JSON 설정 파일로 문제를 선언하는 방식이라 확장성은 다소 제한적. 최근 archive(보관) 처리되었고, 같은 팀의 후속 라이브러리 **Pearl**로 대체되었다.

---

## 10. 요약

이 챕터에서 우리는:
1. 고수준 RL 라이브러리가 왜 필요한지 — 반복되는 배관 코드를 줄이고 버그를 줄이며 품질을 높이기 위해서라는 동기를 배웠다.
2. **PTAN 라이브러리**를 깊이 살펴봤다. 다섯 부품 — Action Selector, Agent(DQNAgent, PolicyAgent), ExperienceSource(및 FirstLast 변형), 리플레이 버퍼, TargetNet — 을 하나씩 코드로 확인했다.
3. 이 부품들을 조합해 **CartPole용 DQN**을 6장보다 훨씬 짧은 코드로 다시 구현했다.
4. stable-baselines3, TorchRL을 비롯한 **다른 RL 라이브러리들**의 지형도 훑어봤다.

이 챕터에서 익힌 도구는 앞으로 이 책 전체에서 계속 쓰인다. 그래서 다음 챕터부터는 "환경과 어떻게 데이터를 주고받는지" 대신, **각 방법이 실제로 무엇을 새롭게 하는지**에 집중할 수 있게 된다. 다음 챕터에서는 DQN으로 다시 돌아가, 고전적인 DQN 소개 이후 연구자·실무자들이 발견해 온 여러 확장 기법들을 통해 안정성과 성능을 개선하는 방법을 살펴본다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[PTAN 라이브러리 구조]]
- [[ExperienceSource와 리플레이버퍼]]
- [[TargetNet 클래스]]
- [[데이터클래스 dataclass]]
- [[API와 클래스·객체]]
- [[소프트맥스 Softmax]]
- [[관측공간과 행동공간(Space)]]
- [[IID 독립항등분포]]
- [[신경망 경사하강 역전파 기초]]
- [[자동미분과 계산그래프]]

## 한눈에 보는 개념 지도
| 개념 | PTAN 클래스 | 한 줄 뜻 |
|---|---|---|
| 행동 선택기 | `ArgmaxActionSelector`, `EpsilonGreedyActionSelector`, `ProbabilityActionSelector` | 네트워크 출력 → 실제 행동 |
| 에이전트 | `DQNAgent`, `PolicyAgent`, `BaseAgent` | 관측 배치 → 행동 배치 |
| 경험 소스 | `ExperienceSource`, `ExperienceSourceFirstLast` | 에이전트+환경 → 궤적 조각 |
| 리플레이 버퍼 | `ExperienceReplayBuffer`, `PrioritizedReplayBuffer` | 경험 저장·무작위 샘플링 |
| 목표망 동기화 | `TargetNet` (`sync`, `alpha_sync`) | 학습망 → 목표망 가중치 복사 |
