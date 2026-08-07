---
title: "Chapter 4 — 교차 엔트로피 방법 (The Cross-Entropy Method)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 4
tags: [DeepRL, 강화학습, 교차엔트로피, CartPole, FrozenLake, 정책기반]
---

# Chapter 4 · 교차 엔트로피 방법

> [!abstract] 이 챕터를 한 문장으로
> **교차 엔트로피(cross-entropy) 방법**은 "여러 번 시도해 본 것 중 **잘한 것들만 골라서, 그것을 그대로 따라 하도록** 신경망을 훈련시키는" 아주 단순하지만 놀랍도록 잘 통하는 강화학습 방법이며, CartPole에서는 완벽하게 통하지만 FrozenLake처럼 보상이 희소한 환경에서는 한계를 드러낸다.

---

## 들어가며 — 왜 이 방법부터 배우는가?

3장까지 우리는 OpenAI Gym(환경을 다루는 법)과 PyTorch(신경망을 다루는 법)라는 **도구**를 배웠다. 이제 Part 1의 마지막 챕터로, 드디어 **첫 번째 진짜 강화학습 알고리즘**을 배운다.

교차 엔트로피 방법은 이 책에서 다룰 DQN(deep Q-network)이나 A2C(advantage actor-critic) 같은 유명한 방법들에 비하면 훨씬 덜 알려져 있다. 하지만 이 방법을 가장 먼저 배우는 데는 이유가 있다.

> [!tip] 교차 엔트로피 방법의 세 가지 강점
> 1. **아주 단순하다.** PyTorch로 구현하면 **100줄도 안 된다.**
> 2. **수렴이 잘 된다.** 복잡한 다단계 정책이 필요 없고, 에피소드가 짧고 보상이 자주 나오는 간단한 환경에서는 특히 잘 통한다.
> 3. 그런 간단한 문제가 실전에 은근히 많아서, **단독으로 쓰거나 더 큰 시스템의 일부로도 쓸모 있는 실전용 기본기(baseline)** 이다.

이번 챕터에서 배울 것:
- 교차 엔트로피 방법의 **실전 사용법** (직관적인 부분)
- Gym의 두 환경 — **CartPole**(익숙한 막대 균형 문제)과 **FrozenLake**(미끄러운 얼음 그리드 월드) — 에 적용해 보기
- 이 방법의 **이론적 배경** (선택 항목: 확률·통계 지식이 조금 필요하지만, "왜 되는지"를 알고 싶다면 도전해 볼 만하다)

---

## 1. 강화학습 방법들의 분류법 (The Taxonomy of RL Methods)

교차 엔트로피 방법은 **model-free**, **policy-based**, **on-policy** 세 가지 범주에 속한다. 이 용어들이 낯설 테니, 하나씩 짚어보자. 사실 RL 방법을 분류하는 방식은 이 밖에도 많지만, 지금 당장은 아래 세 가지 기준이 가장 중요하다. 문제의 특성에 따라 어떤 방법을 골라야 할지가 달라지기 때문이다.

### 1.1 모델 기반(model-based) vs 모델 프리(model-free)

| 구분 | 뜻 | 비유 |
|---|---|---|
| **model-free** | 환경이나 보상에 대한 **모델을 만들지 않는다.** 에이전트는 지금의 관측을 곧바로 행동(또는 행동과 관련된 값)으로 연결할 뿐이다. | 길을 몰라도 일단 걸어보고, 잘 됐던 길을 기억해서 다시 가는 사람 |
| **model-based** | **다음 관측이나 보상이 어떻게 될지 미리 예측**하려 시도한다. 이 예측을 바탕으로 최선의 행동을 고르며, 몇 수 앞을 내다보기 위해 이 예측을 여러 번 반복하기도 한다. | 지도를 보고 "이 길로 가면 이 다음엔 이렇게 되겠지"를 미리 계산하는 사람 |

두 방식 모두 장단점이 있다. 보통 **순수 모델 기반** 방법은 체스처럼 규칙이 엄격한 **결정론적(deterministic)** 환경에서 잘 쓰인다. 반면 **모델 프리** 방법은 복잡하고 정보가 풍부한 환경에서 좋은 모델을 만들기 어렵기 때문에 오히려 학습이 더 쉬운 경우가 많다.

> [!note] 이 책의 방향
> 이 책에서 다루는 방법은 대부분 **model-free**다. 지난 몇 년간 연구가 가장 활발했던 분야이기 때문이다. 최근에서야 두 방식을 섞으려는 시도(예: 20장의 AlphaGo Zero, MuZero — 보드게임과 아타리에 모델 기반 접근을 적용)가 등장하고 있다.

### 1.2 가치 기반(value-based) vs 정책 기반(policy-based)

다른 각도에서 보면, **policy-based** 방법은 에이전트의 **정책(policy)** — 즉 매 순간 어떤 행동을 해야 하는지 — 을 직접 근사한다. 이 정책은 보통 **가능한 행동들에 대한 확률 분포**로 표현된다.

반대로 **value-based** 방법에서는 에이전트가 확률 대신 **가능한 모든 행동 각각의 가치를 계산**하고, 그중 가치가 가장 좋은 행동을 선택한다.

두 방식 모두 널리 쓰인다. 가치 기반 방법은 이 책의 다음 파트(Part 2)에서, 정책 기반 방법은 Part 3에서 다룬다.

### 1.3 온-폴리시(on-policy) vs 오프-폴리시(off-policy)

세 번째 중요한 분류 기준은 **on-policy vs off-policy**다. 자세한 내용은 Part 2·3에서 더 깊이 다루지만, 지금은 이렇게 이해하면 된다.

- **off-policy**: **오래된 데이터**로도 학습할 수 있는 능력. 이 데이터는 과거 버전의 에이전트가 만든 것일 수도, 사람의 시연을 기록한 것일 수도, 심지어 같은 에이전트가 몇 에피소드 전에 겪은 것일 수도 있다.
- **on-policy**: 지금 훈련 중인 바로 그 정책이 만든 **신선한 데이터**가 반드시 필요하다. 낡은 데이터로 훈련하면 결과가 틀어진다. 그래서 환경과의 소통이 훨씬 잦아야 하므로 **데이터 효율이 떨어진다.** 다만 환경이 가볍고 빨라서 상호작용 비용이 적다면 큰 문제가 아닐 수도 있다.

> [!important] 교차 엔트로피 방법의 정체성
> 정리하면, 교차 엔트로피 방법은 **model-free, policy-based, on-policy** 다. 이는 다음을 뜻한다.
> - 환경의 모델을 만들지 않는다 — 매 순간 에이전트에게 "지금 뭘 해야 하는지"만 알려줄 뿐이다.
> - 에이전트의 정책을 근사한다.
> - 환경으로부터 얻은 **신선한 데이터**가 반드시 필요하다.

---

## 2. 교차 엔트로피 방법의 실전 사용법

교차 엔트로피 방법에 대한 설명은 성격이 다른 두 부분으로 나뉜다. **실전 부분**은 직관적이고, **이론 부분**(왜 되는지, 무슨 일이 일어나는지)은 조금 더 정교하다. 이 절에서는 실전 부분을 먼저 다룬다.

RL에서 가장 중요하고도 다루기 까다로운 존재는 바로 **에이전트**다. 에이전트는 환경과 소통하며 최대한 많은 누적 보상을 모으려 애쓴다. 실전에서는 흔한 머신러닝(ML) 접근법을 그대로 따라, 에이전트의 복잡한 내부 로직을 **어떤 비선형 학습 가능 함수**로 대체한다. 이 함수는 에이전트의 입력(환경으로부터의 관측)을 어떤 출력에 매핑한다. 출력이 정확히 무엇인지는 어떤 방법군(가치 기반이냐 정책 기반이냐)을 쓰느냐에 달려 있다.

교차 엔트로피 방법은 **정책 기반**이므로, 우리의 비선형 함수(**신경망, NN**)는 **정책**을 만들어낸다. 정책은 모든 관측에 대해 에이전트가 어떤 행동을 취해야 하는지를 알려준다. 연구 논문에서는 정책을 $\pi(a|s)$ 로 표기하는데, $a$ 는 행동(action), $s$ 는 현재 상태(state)다.

![[fig_4_1_v3.png]]
*그림 4.1 — 정책 기반 RL의 상위 수준(high-level) 흐름도*

이 그림을 말로 풀면 다음과 같다.

1. **환경(Environment)** 이 **관측 $s$** 를 내놓는다.
2. **학습 가능한 함수(신경망, NN)** 가 이 관측을 받아 **정책 $\pi(a|s)$** — 즉 행동들에 대한 확률 분포 — 를 출력한다.
3. 이 확률 분포에서 **행동을 하나 샘플링**한다 ($a \sim \pi(a|s)$).
4. 그 **행동 $a$** 를 환경에 실행하고, 다시 새로운 관측을 받는다.

실전에서는 정책을 보통 **행동들에 대한 확률 분포**로 표현하는데, 이는 마치 **분류(classification) 문제**와 매우 비슷하다. 클래스의 개수가 곧 우리가 할 수 있는 행동의 개수가 되는 셈이다.

> [!important] 에이전트를 아주 단순하게 만드는 추상화
> 이 추상화 덕분에 우리 에이전트는 매우 단순해진다. 할 일은 딱 세 가지다.
> 1. 환경의 관측을 신경망에 전달한다.
> 2. 행동들에 대한 확률 분포를 얻는다.
> 3. 이 확률 분포를 이용해 **무작위로 샘플링**해서 실제로 취할 행동을 정한다.
>
> 이 무작위 샘플링은 에이전트에 **무작위성(randomness)** 을 더해주는데, 이는 오히려 좋은 일이다. 훈련 초기, 가중치가 아직 무작위일 때 에이전트가 무작위로 행동하게 만들어주기 때문이다. ([[확률분포로부터 샘플링]] 참고)

행동을 실행하면 에이전트는 다음 관측과, 방금 한 행동에 대한 보상을 받는다. 그리고 이 루프가 계속 반복된다.

### 2.1 에피소드와 총 보상

에이전트가 살아가는 동안의 경험은 **에피소드(episode)** 들로 표현된다. 각 에피소드는 에이전트가 환경으로부터 받은 관측들, 자신이 취한 행동들, 그 행동들에 대한 보상들의 **연속된 나열**이다.

이런 에피소드를 여러 번 플레이했다고 하자. 각 에피소드마다 에이전트가 얻은 **총 보상**을 계산할 수 있다. 할인($\gamma$)을 적용할 수도, 안 할 수도 있는데, 단순화를 위해 여기서는 **할인율 $\gamma = 1$** 이라 하자. 이는 그냥 에피소드의 모든 지역적(local) 보상을 **할인 없이 그대로 합산**한다는 뜻이다. ([[할인율 감마와 등비급수]] 복습)

![[fig_4_2_v3.png]]
*그림 4.2 — 관측·행동·보상으로 구성된 예시 에피소드 4개*

이 그림은 서로 다른 4개의 에피소드를 보여준다(각 에피소드마다 관측 $o_i$, 행동 $a_i$, 보상 $r_i$ 값이 다르다는 점에 주목하자). 각 칸은 에이전트가 에피소드 안에서 밟은 한 스텝을 나타낸다. 환경의 무작위성과 에이전트가 행동을 고르는 방식 때문에, 어떤 에피소드는 다른 에피소드보다 더 좋을 수밖에 없다.

> [!important] 교차 엔트로피 방법의 핵심 아이디어 — "잘한 것만 골라서 따라 하기"
> 교차 엔트로피 방법의 핵심은 **나쁜 에피소드는 버리고, 더 나은 에피소드로만 훈련하는 것**이다.
>
> 비유하자면 이렇다. 수학 시험을 반 학생 30명이 봤는데, 상위 30%의 답안지만 골라서 "이렇게 풀면 점수가 잘 나오는구나"를 다 함께 베껴 배운다고 생각해 보자. 하위 70%의 답안은 그냥 버린다. 이렇게 몇 번 반복하면, 반 전체의 평균 실력이 계속 상위권 수준으로 끌어올려진다. 교차 엔트로피 방법이 신경망에게 시키는 일이 정확히 이것이다 — **좋은 성적을 낸 에피소드들의 "풀이 과정"(관측→행동 매핑)을 그대로 흉내 내도록** 신경망을 훈련시킨다.

방법의 절차는 다음과 같다.

1. 현재 모델과 환경을 이용해 **$N$개의 에피소드**를 플레이한다.
2. 모든 에피소드의 **총 보상을 계산**하고, **보상 경계값(reward boundary)** 을 정한다. 보통 전체 보상들의 **백분위수(percentile)**, 예를 들어 50번째나 70번째 백분위수를 사용한다. ([[백분위수 필터링]] 참고)
3. 보상 경계값보다 낮은 모든 에피소드는 **버린다.**
4. 남은 "**엘리트(elite)**" 에피소드들(경계값보다 보상이 높은 것들)로 훈련한다. 이때 **관측을 입력**, **취했던 행동을 정답(desired output)** 으로 사용한다.
5. 결과에 만족할 때까지 1단계부터 반복한다.

이렇게 하면 신경망은 **점점 더 큰 보상으로 이어지는 행동을 반복하는 법**을 배우게 되고, 그 결과 경계값은 계속 위로 올라간다. 방법 자체가 단순하고 구현이 쉬우며, 하이퍼파라미터 변화에도 꽤 강건(robust)하다는 점에서 시도해 볼 만한 이상적인 기본기(baseline) 방법이다. 이제 CartPole 환경에 적용해 보자.

---

## 3. CartPole에서의 교차 엔트로피 방법

전체 코드는 `Chapter04/01_cartpole.py` 에 있다. 여기서는 가장 중요한 부분만 짚는다. 우리 모델의 핵심은 **은닉층 1개짜리 신경망**이고, **ReLU(rectified linear unit)** 활성함수와 **128개의 은닉 뉴런**을 쓴다(이 숫자는 순전히 임의로 고른 것이다 — 늘리거나 줄여서 실험해 봐도 좋다). 나머지 하이퍼파라미터들도 거의 무작위로 정해졌고 딱히 튜닝하지 않았다. 이 방법이 워낙 강건하고 빠르게 수렴하기 때문이다.

### 3.1 상수와 임포트

```python
import typing as tt
import torch
import torch.nn as nn
import torch.optim as optim

HIDDEN_SIZE = 128
BATCH_SIZE = 16
PERCENTILE = 70
```

- `HIDDEN_SIZE = 128`: 은닉층 뉴런 개수.
- `BATCH_SIZE = 16`: 매 반복(iteration)마다 플레이할 에피소드 개수.
- `PERCENTILE = 70`: 엘리트 에피소드를 거를 때 쓰는 **백분위수**. 70번째 백분위수를 쓴다는 것은, 보상 기준 상위 30%의 에피소드만 남기고 나머지는 버린다는 뜻이다.

### 3.2 신경망 정의

```python
class Net(nn.Module):
    def __init__(self, obs_size: int, hidden_size: int, n_actions: int):
        super(Net, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, n_actions)
        )

    def forward(self, x: torch.Tensor):
        return self.net(x)
```

이 신경망에는 특별한 게 없다. 환경에서 온 **관측 하나를 입력 벡터**로 받아서, **각 행동에 대한 숫자(점수) 하나씩**을 출력한다.

> [!note] 왜 마지막에 softmax를 안 붙일까?
> 신경망의 출력은 행동들에 대한 **확률 분포**여야 하므로, 마지막 층 뒤에 **softmax** 비선형 함수를 붙이는 게 직관적으로 자연스러워 보인다. ([[소프트맥스 Softmax]] 참고)
>
> 하지만 코드에서는 그렇게 하지 **않는다.** 훈련 과정의 **수치적 안정성(numerical stability)** 을 높이기 위해서다. Softmax(지수함수를 씀)를 먼저 계산하고 그 다음에 [[교차 엔트로피 Cross-Entropy]] 손실(로그를 씀)을 계산하는 대신, 나중에 PyTorch의 `nn.CrossEntropyLoss` 클래스를 쓸 것이다. 이 클래스는 softmax와 교차 엔트로피를 **하나의, 수치적으로 더 안정적인 식**으로 합쳐준다. `CrossEntropyLoss` 는 신경망의 **가공되지 않은(raw), 정규화 안 된 값**(이를 **로짓, logits** 이라 부른다)을 입력으로 요구한다. 대신 이 방식의 단점은, 신경망 출력에서 실제 확률값이 필요할 때마다 **직접 softmax를 적용해 줘야 한다**는 걸 기억해야 한다는 것이다.

### 3.3 데이터클래스 두 개

```python
@dataclass
class EpisodeStep:
    observation: np.ndarray
    action: int

@dataclass
class Episode:
    reward: float
    steps: tt.List[EpisodeStep]
```

- **`EpisodeStep`**: 에이전트가 에피소드 안에서 밟은 **한 스텝**을 나타낸다. 그 스텝에서의 관측과, 에이전트가 취한 행동을 저장한다. 엘리트 에피소드의 스텝들을 **훈련 데이터**로 쓸 것이다.
- **`Episode`**: 에피소드 하나를 나타내며, **할인 없는 총 보상**과 `EpisodeStep` 들의 모음을 담는다.

### 3.4 배치를 생성하는 `iterate_batches` 함수

```python
def iterate_batches(env: gym.Env, net: Net, batch_size: int) -> \
        tt.Generator[tt.List[Episode], None, None]:
    batch = []
    episode_reward = 0.0
    episode_steps = []
    obs, _ = env.reset()
    sm = nn.Softmax(dim=1)
```

이 함수는 환경(Gym 라이브러리의 `Env` 클래스 인스턴스), 우리의 신경망, 그리고 매 반복마다 생성할 에피소드 개수를 인자로 받는다. `batch` 변수에 배치(`Episode` 인스턴스들의 리스트)를 누적한다. 또한 현재 에피소드의 보상 누적 카운터와 스텝 리스트(`EpisodeStep` 객체들)를 선언한다. 그런 다음 환경을 리셋해 첫 관측을 얻고, 신경망 출력을 행동들에 대한 확률 분포로 바꿔줄 **softmax 층**을 만든다. 이제 준비가 끝났으니 환경 루프를 시작하자.

```python
    while True:
        obs_v = torch.tensor(obs, dtype=torch.float32)
        act_probs_v = sm(net(obs_v.unsqueeze(0)))
        act_probs = act_probs_v.data.numpy()[0]
```

매 반복마다, 현재 관측을 PyTorch 텐서로 변환해 신경망에 전달하여 **행동 확률**을 얻는다. 여기서 짚고 넘어가야 할 것들이 있다.

- PyTorch의 모든 `nn.Module` 인스턴스는 **데이터의 배치(batch)** 를 기대하고, 우리 신경망도 예외가 아니다. 그래서 관측(CartPole에서는 숫자 4개짜리 벡터)을 크기 $1 \times 4$ 텐서로 바꿔야 한다. 이를 위해 텐서에 `unsqueeze(0)` 함수를 호출해서, 모양(shape)의 0번 위치에 차원을 하나 더 추가한다.
- 신경망 출력에는 비선형 함수를 적용하지 않았으므로, **가공되지 않은 행동 점수**가 나온다. 이를 확률로 바꾸려면 softmax 함수를 거쳐야 한다.
- 신경망과 softmax 층 모두 **기울기(gradient)를 추적하는 텐서**를 반환한다. 그래서 `tensor.data` 필드에 접근해 이를 풀어내고, 텐서를 NumPy 배열로 변환해야 한다. 이 배열은 입력과 같은 2차원 구조를 가지며 배치 차원이 0번 축에 있으므로, 배치의 첫 번째 원소를 가져와야 1차원 벡터인 행동 확률을 얻을 수 있다.

```python
        action = np.random.choice(len(act_probs), p=act_probs)
        next_obs, reward, is_done, is_trunc, _ = env.step(action)
```

이제 행동들에 대한 확률 분포가 생겼으니, 이를 이용해 현재 스텝에서 실제로 취할 행동을 얻는다. NumPy의 `random.choice()` 함수를 이용해 이 분포에서 샘플링한다. 그런 다음 이 행동을 환경에 전달해 다음 관측, 보상, 에피소드가 끝났는지 여부, 그리고 잘림(truncation) 플래그를 받는다. `step()` 함수가 반환하는 마지막 값은 추가 정보이며 여기서는 버린다.

```python
        episode_reward += float(reward)
        step = EpisodeStep(observation=obs, action=action)
        episode_steps.append(step)
```

보상은 현재 에피소드의 총 보상에 더해지고, 우리의 스텝 리스트에도 **(관측, 행동)** 쌍이 추가된다.

> [!warning] 아주 사소하지만 중요한 디테일
> 여기서 저장하는 관측은 **행동을 고를 때 썼던 관측**이지, 그 행동의 **결과로 환경이 반환한 새 관측이 아니다.** 이런 사소하지만 중요한 디테일을 꼭 기억해 두자.

```python
        if is_done or is_trunc:
            e = Episode(reward=episode_reward, steps=episode_steps)
            batch.append(e)
            episode_reward = 0.0
            episode_steps = []
            next_obs, _ = env.reset()
            if len(batch) == batch_size:
                yield batch
                batch = []
```

현재 에피소드가 끝났을 때의 처리다. 완성된 에피소드를 배치에 추가하면서, 총 보상(에피소드가 끝났으니 이미 모든 보상을 다 합산한 값)과 그동안 밟은 스텝들을 저장한다. 그런 다음 총 보상 누적기를 리셋하고 스텝 리스트를 비운다. 그 후 환경을 리셋해서 다시 처음부터 시작한다.

만약 배치가 원하는 개수의 에피소드에 도달했다면, `yield` 를 통해 배치를 호출자에게 반환하여 처리하게 한다. 우리 함수는 **제너레이터(generator)** 이므로, `yield` 연산자가 실행될 때마다 제어권이 바깥의 반복 루프로 넘어갔다가, `yield` 줄 다음부터 다시 이어서 실행된다. Python 제너레이터 함수가 낯설다면 [Python 공식 문서](https://wiki.python.org/moin/Generators)를 참고하자. 처리가 끝나면 배치를 다시 비운다.

```python
        obs = next_obs
```

루프의 마지막이지만 매우 중요한 스텝은, 환경에서 얻은 관측을 현재 관측 변수에 대입하는 것이다. 이후 모든 게 무한히 반복된다 — 관측을 신경망에 넘기고, 행동을 샘플링하고, 환경에 그 행동을 처리하도록 요청하고, 그 결과를 기억한다.

> [!important] 훈련과 에피소드 생성이 동시에 일어난다
> 이 함수의 로직에서 이해해야 할 아주 중요한 사실이 있다. **신경망의 훈련과 에피소드의 생성이 동시에 진행된다는 것**이다. 완전히 병렬은 아니지만, 루프가 충분한 에피소드(16개)를 모을 때마다 `yield` 로 제어권을 호출자에게 넘기고, 호출자는 경사하강법으로 신경망을 훈련시킨다. `yield` 가 다시 반환될 때쯤이면 신경망은 (바라건대) 조금 더 나은 행동을 하도록 바뀌어 있다.
>
> 챕터 시작에서 언급했듯 교차 엔트로피 방법은 **on-policy**에 속하므로, 신선한 훈련 데이터를 쓰는 것이 방법이 제대로 작동하기 위해 중요하다. 훈련과 데이터 수집이 같은 스레드에서 일어나므로 별도의 동기화(synchronization)는 필요 없다. 다만 신경망 훈련과 사용 사이를 자주 오간다는 점은 인지하고 있어야 한다.

### 3.5 엘리트 에피소드를 골라내는 `filter_batch` 함수

```python
def filter_batch(batch: tt.List[Episode], percentile: float) -> \
        tt.Tuple[torch.FloatTensor, torch.LongTensor, float, float]:
    rewards = list(map(lambda s: s.reward, batch))
    reward_bound = float(np.percentile(rewards, percentile))
    reward_mean = float(np.mean(rewards))
```

이 함수가 바로 교차 엔트로피 방법의 **핵심**이다 — 주어진 에피소드 배치와 백분위수 값으로부터, 훈련할 엘리트 에피소드를 걸러내는 데 쓰일 **경계 보상값**을 계산한다. 경계 보상값을 얻기 위해 NumPy의 `percentile` 함수를 쓰는데, 이 함수는 값들의 리스트와 원하는 백분위수로부터 그 백분위수에 해당하는 값을 계산해 준다. 그런 다음 (모니터링 용도로만 쓰이는) 평균 보상도 계산한다.

```python
    train_obs: tt.List[np.ndarray] = []
    train_act: tt.List[int] = []
    for episode in batch:
        if episode.reward < reward_bound:
            continue
        train_obs.extend(map(lambda step: step.observation, episode.steps))
        train_act.extend(map(lambda step: step.action, episode.steps))
```

다음으로 에피소드들을 걸러낸다. 배치 안 각 에피소드에 대해, 그 총 보상이 우리 경계값보다 높은지 확인하고, 높다면 관측과 행동 리스트에 그 에피소드의 스텝들을 채워 넣는다.

```python
    train_obs_v = torch.FloatTensor(np.vstack(train_obs))
    train_act_v = torch.LongTensor(train_act)
    return train_obs_v, train_act_v, reward_bound, reward_mean
```

마지막으로, 엘리트 에피소드들의 관측과 행동을 텐서로 변환하고, **네 값으로 이루어진 튜플**을 반환한다 — 관측, 행동, 보상 경계값, 평균 보상. 뒤의 두 값은 훈련 자체에는 쓰이지 않고, TensorBoard에 기록해서 에이전트의 성능을 확인하는 용도로만 쓴다.

### 3.6 모든 것을 이어붙이는 훈련 루프

```python
if __name__ == "__main__":
    env = gym.make("CartPole-v1")
    assert env.observation_space.shape is not None
    obs_size = env.observation_space.shape[0]
    assert isinstance(env.action_space, gym.spaces.Discrete)
    n_actions = int(env.action_space.n)

    net = Net(obs_size, HIDDEN_SIZE, n_actions)
    print(net)
    objective = nn.CrossEntropyLoss()
    optimizer = optim.Adam(params=net.parameters(), lr=0.01)
    writer = SummaryWriter(comment="-cartpole")
```

맨 처음에는 필요한 모든 객체 — 환경, 신경망, 목적함수(objective), 옵티마이저, TensorBoard용 요약 기록기(writer) — 를 만든다.

```python
    for iter_no, batch in enumerate(iterate_batches(env, net, BATCH_SIZE)):
        obs_v, acts_v, reward_b, reward_m = filter_batch(batch, PERCENTILE)
        optimizer.zero_grad()
        action_scores_v = net(obs_v)
        loss_v = objective(action_scores_v, acts_v)
        loss_v.backward()
        optimizer.step()
```

훈련 루프에서는 배치들(`Episode` 객체들의 리스트)을 순회한다. `filter_batch` 함수로 엘리트 에피소드를 걸러내고 나면, 관측과 취한 행동에 대한 텐서, 필터링에 쓰인 보상 경계값, 평균 보상을 얻는다. 그 후 신경망의 기울기를 0으로 초기화하고, 관측을 신경망에 넘겨 **행동 점수**를 얻는다. 이 점수들은 `objective` 함수로 전달되어, **신경망 출력**과 **에이전트가 실제로 취했던 행동** 사이의 **교차 엔트로피**를 계산한다. 여기 담긴 아이디어는, **좋은 보상으로 이어졌던 엘리트 행동들을 신경망이 그대로 수행하도록 강화(reinforce)** 하는 것이다. 이어서 손실에 대한 기울기를 계산하고, 옵티마이저에게 신경망을 조정하도록 요청한다.

```python
        print("%d: loss=%.3f, reward_mean=%.1f, rw_bound=%.1f" % (
            iter_no, loss_v.item(), reward_m, reward_b))
        writer.add_scalar("loss", loss_v.item(), iter_no)
        writer.add_scalar("reward_bound", reward_b, iter_no)
        writer.add_scalar("reward_mean", reward_m, iter_no)
```

루프의 나머지 부분은 대부분 진행 상황을 모니터링하는 것이다. 콘솔에는 반복 횟수, 손실, 배치의 평균 보상, 보상 경계값을 출력한다. TensorBoard에도 같은 값을 기록해서, 에이전트 학습 성능을 보여주는 예쁜 그래프를 얻을 수 있다.

```python
        if reward_m > 475:
            print("Solved!")
            break
    writer.close()
```

루프의 마지막 체크는 배치 에피소드들의 **평균 보상**을 비교하는 것이다. 평균 보상이 475보다 커지면 훈련을 멈춘다.

> [!question] 왜 하필 475일까?
> Gym에서 **CartPole-v1** 환경은 **최근 100개 에피소드의 평균 보상이 475보다 크면** 풀린 것으로 간주한다. 그런데 우리 방법은 워낙 빠르게 수렴해서, 사실 100개까지 필요하지 않다. 제대로 훈련된 에이전트는 막대를 무한히 오래 균형 잡을 수 있지만(점수는 무한정 쌓일 수 있지만), CartPole-v1 환경 자체가 한 에피소드의 길이를 **최대 500스텝**으로 제한하고 있다(Farama Foundation의 Gymnasium 소스코드 `gymnasium/envs/__init__.py` 에서 `max_episode_steps=500` 으로 등록되어 있음을 확인할 수 있다). 이런 사정을 감안해서, 배치의 평균 보상이 475를 넘으면 훈련을 멈추기로 한 것이다. 이는 에이전트가 막대를 프로처럼 잘 다룬다는 충분한 신호다.

### 3.7 실행 결과

```text
Chapter04$ ./01_cartpole.py
Net(
  (net): Sequential(
    (0): Linear(in_features=4, out_features=128, bias=True)
    (1): ReLU()
    (2): Linear(in_features=128, out_features=2, bias=True)
  )
)
0: loss=0.683, reward_mean=25.2, rw_bound=24.0
1: loss=0.669, reward_mean=34.3, rw_bound=39.0
2: loss=0.648, reward_mean=37.6, rw_bound=40.0
3: loss=0.647, reward_mean=41.9, rw_bound=43.0
4: loss=0.634, reward_mean=41.2, rw_bound=50.0
....
38: loss=0.537, reward_mean=431.8, rw_bound=500.0
39: loss=0.529, reward_mean=450.1, rw_bound=500.0
40: loss=0.533, reward_mean=456.4, rw_bound=500.0
41: loss=0.526, reward_mean=422.0, rw_bound=500.0
42: loss=0.531, reward_mean=436.8, rw_bound=500.0
43: loss=0.526, reward_mean=475.5, rw_bound=500.0
Solved!
```

보통 에이전트가 문제를 풀기까지 **50배치를 넘기지 않는다.** 저자의 실험에서는 30~60 에피소드 정도 걸렸는데, 배치마다 16 에피소드만 플레이한다는 걸 감안하면 아주 훌륭한 학습 성능이다. TensorBoard를 보면 에이전트가 (가끔 롤백되는 구간은 있어도) 거의 매 배치마다 상단 경계값을 계속 밀어 올리며 꾸준히 진전하고 있음을 알 수 있다.

![[fig_4_3_v3.png]]
*그림 4.3 — 훈련 중 평균 보상(왼쪽)과 손실(오른쪽)*

![[fig_4_4_v3.png]]
*그림 4.4 — 훈련 중 보상 경계값의 변화*

> [!tip] 학습 과정을 영상으로 보고 싶다면
> 환경을 만들 때 렌더링 모드를 설정하고 `RecordVideo` 래퍼를 추가하면, 훈련 중 에이전트의 행동을 담은 MP4 영상들을 만들 수 있다.
> ```python
> env = gym.make("CartPole-v1", render_mode="rgb_array")
> env = gym.wrappers.RecordVideo(env, video_folder="video")
> ```
> 이렇게 하면 `video` 폴더에 여러 개의 MP4 영상이 만들어져, 훈련이 진행됨에 따라 에이전트의 실력이 어떻게 좋아지는지 비교해 볼 수 있다.

![[fig_4_5_v3.png]]
*그림 4.5 — CartPole 에피소드를 담은 영상 재생 화면*

잠시 멈추고 방금 무슨 일이 일어났는지 생각해 보자. 우리 신경망은 **관측과 보상만으로**, 그 값이 무엇을 의미하는지에 대한 아무런 해석 없이 이 환경을 플레이하는 법을 배웠다. 환경이 굳이 막대가 달린 카트일 필요는 없다 — 예를 들어 상품 수량이 관측이고 벌어들인 돈이 보상인 **창고 관리 모델**일 수도 있다. 우리 구현은 환경에 특화된 세부사항에 전혀 의존하지 않는다. 이것이 바로 RL 모델의 아름다움이며, 다음 절에서는 완전히 똑같은 방법을 Gym의 다른 환경에 적용해 본다.

---

## 4. FrozenLake에서의 교차 엔트로피 방법

이번에 교차 엔트로피 방법으로 풀어볼 두 번째 환경은 **FrozenLake**다. 이 세계는 이른바 **그리드 월드(grid world)** 범주에 속하는데, 에이전트가 $4 \times 4$ 크기의 격자 안에 살면서 상/하/좌/우 네 방향으로 움직일 수 있다. 에이전트는 항상 왼쪽 위 칸에서 시작하고, 목표는 오른쪽 아래 칸에 도달하는 것이다. 격자의 정해진 칸 몇 개에는 **구멍(hole)** 이 있어서, 거기 빠지면 에피소드가 끝나고 보상은 0이 된다. 목적지 칸에 도달하면 보상 1.0을 받고 에피소드가 끝난다.

인생을 더 복잡하게 만들려는 듯, 이 세계는 **미끄럽다**(얼어붙은 호수니까 그럴 만도 하다). 그래서 에이전트의 행동이 항상 의도한 대로 되지는 않는다 — **33%의 확률로 오른쪽이나 왼쪽으로 미끄러진다.** 예를 들어 에이전트가 왼쪽으로 이동하려 하면, 33% 확률로 정말 왼쪽으로 가고, 33% 확률로 위 칸으로, 33% 확률로 아래 칸으로 가게 된다. 이 절 끝에서 보겠지만, 이런 미끄러짐이 진전을 매우 어렵게 만든다.

![[fig_4_6_v3.png]]
*그림 4.6 — human 렌더링 모드로 표시한 FrozenLake 환경*

### 4.1 Gym API에서 이 환경이 어떻게 표현되는가

```python
>>> e = gym.make("FrozenLake-v1", render_mode="ansi")
>>> e.observation_space
Discrete(16)
>>> e.action_space
Discrete(4)
>>> e.reset()
(0, {'prob': 1})
>>> print(e.render())

SFFF
FHFH
FFFH
HFFG
```

우리의 관측 공간은 **이산(discrete)** 이다. 즉 0부터 15까지의 숫자 하나일 뿐이다. 분명히 이 숫자는 격자 안 현재 위치를 나타낸다. 행동 공간 역시 이산이며, 0부터 3까지 값을 가질 수 있다.

행동 공간은 CartPole과 비슷하지만, **관측 공간이 다른 방식으로 표현**된다는 점이 다르다. 우리 구현에 필요한 변경을 최소화하기 위해, 이산 입력에 대한 전통적인 **원-핫 인코딩(one-hot encoding)** 을 적용할 수 있다. 이는 신경망 입력이 16개의 실수(float) 값을 가지고, 우리 현재 위치를 표현하는 인덱스만 빼고 나머지는 전부 0이 된다는 뜻이다. ([[원-핫 인코딩]] 참고)

### 4.2 `DiscreteOneHotWrapper` — 관측을 원-핫으로 바꾸는 래퍼

이 변환은 환경의 **관측**에만 영향을 주므로, 2장에서 다뤘던 것처럼 `ObservationWrapper` 로 구현할 수 있다. 이 래퍼를 `DiscreteOneHotWrapper` 라 부르자.

```python
class DiscreteOneHotWrapper(gym.ObservationWrapper):
    def __init__(self, env: gym.Env):
        super(DiscreteOneHotWrapper, self).__init__(env)
        assert isinstance(env.observation_space, gym.spaces.Discrete)
        shape = (env.observation_space.n, )
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape, dtype=np.float32)

    def observation(self, observation):
        res = np.copy(self.observation_space.low)
        res[observation] = 1.0
        return res
```

`__init__` 에서는 원래 관측 공간이 정말로 이산인지 확인한 뒤, 새 관측 공간을 **16차원 벡터**(값의 범위는 0.0~1.0)로 다시 정의한다. `observation` 메서드가 실제 변환을 담당한다. 입력으로 들어온 정수 위치 하나를, 그 위치에 해당하는 인덱스만 1.0이고 나머지는 전부 0.0인 벡터로 바꿔준다.

이 래퍼를 적용하면 관측 공간과 행동 공간 모두 우리의 CartPole 솔루션과 **100% 호환**된다. 그런데 이 상태로 실행해 보면(소스코드 `Chapter04/02_frozenlake_naive.py`), 훈련 과정에서 점수가 전혀 개선되지 않는 것을 볼 수 있다.

![[fig_4_7_v3.png]]
*그림 4.7 — FrozenLake 환경에서의 평균 보상(왼쪽)과 손실(오른쪽)*

![[fig_4_8_v3.png]]
*그림 4.8 — 훈련 중 보상 경계값의 변화 (계속 0.0에 머무르는 지루한 그래프)*

### 4.3 왜 실패했는가 — 두 환경의 보상 구조 차이

무슨 일이 일어나고 있는지 이해하려면, 두 환경의 **보상 구조**를 더 깊이 들여다봐야 한다.

**CartPole**에서는 환경의 매 스텝마다 보상 1.0을 받는다. 막대가 쓰러지는 순간까지 말이다. 그래서 에이전트가 막대를 오래 균형 잡을수록 더 많은 보상을 얻는다. 에이전트 행동의 무작위성 때문에 에피소드들의 길이가 제각각이었고, 이 덕분에 에피소드 보상들이 꽤 정상적인(normal) 분포를 이루었다. 보상 경계값을 고르고 나면, 우리는 성적이 나쁜 에피소드들을 걸러내고 더 나은 에피소드들의 데이터로 학습해서 그것을 반복하는 법을 배울 수 있었다.

이 상황은 다음 그림으로 나타난다.

![[fig_4_9_v3.png]]
*그림 4.9 — CartPole 환경에서 보상의 분포*

**FrozenLake**에서는 에피소드와 그 보상이 다르게 생겼다. 우리는 목표에 도달했을 때만 1.0의 보상을 받고, 이 보상은 **각 에피소드가 얼마나 좋았는지에 대해서는 아무것도 말해주지 않는다.** 빠르고 효율적으로 도달했을까, 아니면 호수를 네 바퀴나 돌다가 우연히 마지막 칸에 발을 들인 걸까? 우리는 알 수 없다 — 그냥 1.0이라는 보상 하나가 있을 뿐이다.

에피소드 보상들의 분포 역시 문제다. 가능한 에피소드는 **두 종류뿐**이다 — 보상 0(실패)과 보상 1(성공). 그리고 훈련 초기, 에이전트가 무작위로 행동할 때는 **실패한 에피소드가 압도적으로 많다.** 그래서 우리의 백분위수 기반 엘리트 에피소드 선택 방식이 **완전히 잘못된 방향**으로 작동하고, 학습할 나쁜 예시들만 골라주게 된다. 이것이 훈련이 실패하는 이유다.

![[fig_4_10_v3.png]]
*그림 4.10 — FrozenLake 환경에서 보상의 분포*

이 예시는 교차 엔트로피 방법의 **한계**를 보여준다.

> [!warning] 교차 엔트로피 방법이 잘 통하기 위한 조건
> - 훈련을 위해서는 우리 에피소드가 **유한**해야 한다(일반적으로는 무한할 수도 있지만), **가급적 짧아야** 좋다.
> - 에피소드들의 총 보상은 **좋은 에피소드와 나쁜 에피소드를 구분할 만큼 충분한 변동성(variability)** 을 가져야 한다.
> - 에피소드가 끝날 때만 보상을 받는 것보다는, 에피소드 도중에도 **중간 보상**이 있는 편이 유리하다.

책의 뒷부분에서는 이런 한계를 극복하는 다른 방법들을 배우게 될 것이다. 하지만 지금 당장 FrozenLake를 교차 엔트로피 방법으로 풀 수 있는지 궁금하다면, 코드에 적용할 수 있는 몇 가지 조정 방법이 있다(전체 예제는 `Chapter04/03_frozenlake_tweaked.py`).

### 4.4 FrozenLake를 위한 코드 조정

- **더 큰 배치(더 많은 에피소드를 플레이)**: CartPole에서는 반복마다 16개 에피소드로 충분했지만, FrozenLake는 성공한 에피소드 몇 개라도 얻으려면 **최소 100개**는 필요하다.
- **보상에 할인율 적용**: 에피소드 총 보상이 그 **길이에 의존**하도록 만들기 위해, $\gamma = 0.9$ 또는 $0.95$ 의 할인율을 적용한 총 보상을 쓸 수 있다. 이렇게 하면 짧은 에피소드의 보상이 긴 에피소드의 보상보다 높아진다. 이는 보상 분포의 변동성을 높여서, 그림 4.10에서 봤던 것 같은 상황을 피하는 데 도움이 된다.
- **엘리트 에피소드를 더 오래 유지하기**: CartPole 훈련에서는 환경에서 얻은 에피소드로 훈련하고 나면 곧바로 버렸다. FrozenLake에서는 성공적인 에피소드가 훨씬 드문 존재라서, **여러 반복에 걸쳐 계속 보관**하며 훈련에 써야 한다.
- **학습률 낮추기**: 이렇게 하면 신경망이 새로운 데이터의 영향을 덜 받으면서, **더 많은 훈련 샘플을 평균**낼 시간을 벌 수 있다.
- **훨씬 더 긴 훈련 시간**: 성공적인 에피소드의 희소함과 우리 행동의 무작위적 결과 때문에, 신경망이 어떤 상황에서든 최선의 행동에 대한 감을 잡기가 훨씬 어려워진다. 50%의 성공 에피소드에 도달하려면 약 **5,000번의 훈련 반복**이 필요하다.

이 모든 것을 코드에 반영하려면, 할인된 보상을 계산하고 엘리트 에피소드를 우리를 위해 보관해 반환하도록 `filter_batch` 함수를 바꿔야 한다.

```python
def filter_batch(batch: tt.List[Episode], percentile: float) -> \
        tt.Tuple[tt.List[Episode], tt.List[np.ndarray], tt.List[int], float]:
    reward_fun = lambda s: s.reward * (GAMMA ** len(s.steps))
    disc_rewards = list(map(reward_fun, batch))
    reward_bound = np.percentile(disc_rewards, percentile)

    train_obs: tt.List[np.ndarray] = []
    train_act: tt.List[int] = []
    elite_batch: tt.List[Episode] = []

    for example, discounted_reward in zip(batch, disc_rewards):
        if discounted_reward > reward_bound:
```

첫 부분에서는 `reward_fun` 이라는 람다로, 각 에피소드의 원래 보상에 $\gamma^{(\text{에피소드 길이})}$ 를 곱해 **할인된 보상**을 계산한다. 에피소드가 길수록 할인이 크게 적용되어 보상이 더 깎인다. 그런 다음 이 할인된 보상들의 리스트로부터 백분위수 경계값을 구한다.

```python
            train_obs.extend(map(lambda step: step.observation, example.steps))
            train_act.extend(map(lambda step: step.action, example.steps))
            elite_batch.append(example)

    return elite_batch, train_obs, train_act, reward_bound
```

경계값을 넘는 할인 보상을 가진 에피소드만 관측·행동을 훈련 데이터에 추가하고, 그 에피소드 자체도 `elite_batch` 에 보관한다. 이 `elite_batch` 를 반환값에 포함시키는 이유는, 다음 반복에서도 계속 이 엘리트 에피소드들을 재사용하기 위해서다.

이어서 훈련 루프에서는 이전 엘리트 에피소드들을 저장해 두었다가, 다음 훈련 반복에서 앞의 함수에 함께 넘긴다.

```python
    full_batch = []
    for iter_no, batch in enumerate(iterate_batches(env, net, BATCH_SIZE)):
        reward_mean = float(np.mean(list(map(lambda s: s.reward, batch))))
        full_batch, obs, acts, reward_bound = filter_batch(full_batch + batch,
                                                            PERCENTILE)
        if not full_batch:
            continue
        obs_v = torch.FloatTensor(obs)
        acts_v = torch.LongTensor(acts)
        full_batch = full_batch[-500:]
```

`full_batch` 는 지금까지 모아온 엘리트 에피소드들을 누적하는 저장소다. 매 반복마다 새로 얻은 배치를 `full_batch` 와 합쳐서 다시 필터링하고, 걸러진 엘리트 에피소드들을 다시 `full_batch` 에 채워 넣는다. 만약 `full_batch` 가 아직 비어 있다면(엘리트 에피소드가 하나도 없다면) 이번 반복은 그냥 건너뛴다. 메모리가 무한정 불어나는 걸 막기 위해, 가장 최근의 500개 엘리트 에피소드만 남기고 나머지는 버린다(`full_batch[-500:]`).

나머지 코드는 동일하지만, **학습률을 10배 낮췄고** `BATCH_SIZE` 를 100으로 설정했다. (새 버전은 10,000번의 반복을 끝내는 데 약 50분이 걸린다.) 인내심을 갖고 기다려 보면, 모델의 훈련이 **약 55%의 에피소드 성공률** 부근에서 개선을 멈추는 것을 볼 수 있다.

![[fig_4_11_v3.png]]
*그림 4.11 — 조정된(tweaked) 버전의 평균 보상(왼쪽)과 손실(오른쪽)*

![[fig_4_12_v3.png]]
*그림 4.12 — 조정된 버전의 보상 경계값 변화*

> [!note] 이 정체 현상을 해결하는 방법
> 이런 정체를 해결하는 방법들이 있는데(예를 들어 **엔트로피 손실 정규화**를 적용하는 것), 이런 기법들은 다음 챕터들에서 다룰 것이다.

### 4.5 미끄러움의 효과 — nonslippery 버전과 비교

여기서 짚고 넘어갈 마지막 포인트는 FrozenLake 환경에서 **미끄러움(slipperiness)** 의 효과다. 우리의 각 행동은 33% 확률로 **90도 회전된 행동**으로 대체된다(예를 들어 *up* 행동은 0.33 확률로 성공하고, 0.33 확률로 *left* 행동으로, 0.33 확률로 *right* 행동으로 대체된다).

미끄럽지 않은(nonslippery) 버전은 `Chapter04/04_frozenlake_nonslippery.py` 에 있으며, 유일한 차이는 환경을 만드는 부분이다.

```python
env = DiscreteOneHotWrapper(gym.make("FrozenLake-v1", is_slippery=False))
```

효과는 극적이다! 미끄럽지 않은 버전의 환경은 **120~140번의 배치 반복**만으로 풀 수 있는데, 이는 미끄럽고 시끄러운(noisy) 환경보다 **100배나 빠른** 속도다.

```text
Chapter04$ ./04_frozenlake_nonslippery.py
2: loss=1.436, rw_mean=0.010, rw_bound=0.000, batch=1
3: loss=1.410, rw_mean=0.010, rw_bound=0.000, batch=2
4: loss=1.391, rw_mean=0.050, rw_bound=0.000, batch=7
5: loss=1.379, rw_mean=0.020, rw_bound=0.000, batch=9
6: loss=1.375, rw_mean=0.010, rw_bound=0.000, batch=10
7: loss=1.367, rw_mean=0.040, rw_bound=0.000, batch=14
8: loss=1.361, rw_mean=0.000, rw_bound=0.000, batch=14
9: loss=1.356, rw_mean=0.010, rw_bound=0.000, batch=15
...
134: loss=0.308, rw_mean=0.730, rw_bound=0.478, batch=93
136: loss=0.440, rw_mean=0.710, rw_bound=0.304, batch=70
137: loss=0.298, rw_mean=0.720, rw_bound=0.478, batch=106
139: loss=0.337, rw_mean=0.790, rw_bound=0.430, batch=65
140: loss=0.295, rw_mean=0.720, rw_bound=0.478, batch=99
142: loss=0.433, rw_mean=0.670, rw_bound=0.000, batch=67
143: loss=0.287, rw_mean=0.820, rw_bound=0.478, batch=114
Solved!
```

아래 그래프에서도 이를 확인할 수 있다.

![[fig_4_13_v3.png]]
*그림 4.13 — 미끄럽지 않은(nonslippery) 버전의 평균 보상(왼쪽)과 손실(오른쪽)*

![[fig_4_14_v3.png]]
*그림 4.14 — 미끄럽지 않은 버전의 보상 경계값 변화*

이 비교는 매우 중요한 교훈을 준다. **똑같은 목표, 똑같은 격자 크기**라도 환경의 **무작위성(확률적 전이)** 이 얼마나 학습을 어렵게 만드는지 극명하게 보여준다. 미끄러움이 있으면, 에이전트가 아무리 좋은 행동을 골라도 결과가 33% 확률로 엉뚱하게 나오기 때문에, "좋은 행동"과 "좋은 결과" 사이의 연결고리가 훨씬 약해진다.

---

## 5. 교차 엔트로피 방법의 이론적 배경 (선택 항목)

> [!note] 이 절은 선택 항목이다
> 이 절은 **왜 이 방법이 통하는지** 이해하고 싶은 독자를 위한 것이다. 확률과 통계에 대한 배경지식이 조금 필요하다. 원 논문을 직접 보고 싶다면 Kroese가 쓴 논문 "Cross-entropy method" [Kro+11] 을 참고하라.

교차 엔트로피 방법의 기반에는 **중요도 샘플링 정리(importance sampling theorem)** 가 있다. 이 정리는 다음과 같다.

$$\mathbb{E}_{x\sim p(x)}[H(x)] = \int_x p(x)H(x)dx = \int_x q(x)\frac{p(x)}{q(x)}H(x)dx = \mathbb{E}_{x\sim q(x)}\left[\frac{p(x)}{q(x)}H(x)\right]$$

말로 풀면 이렇다. 어떤 분포 $p(x)$ 아래에서 $H(x)$ 의 기댓값을 구하고 싶은데, 직접 $p(x)$ 에서 샘플링하기 어렵거나 비효율적일 때, 대신 **다른 분포 $q(x)$ 에서 샘플링**하고 그 결과에 **가중치 $\frac{p(x)}{q(x)}$** 를 곱해서 원래 원하던 기댓값과 **똑같은 값**을 얻을 수 있다는 뜻이다.

우리 RL의 경우, $H(x)$ 는 어떤 정책 $x$ 로 얻은 **보상값**이고, $p(x)$ 는 **가능한 모든 정책들의 분포**다. 우리는 모든 가능한 정책을 다 탐색해서 보상을 최대화하고 싶지 않다 — 대신 $p(x)H(x)$ 를 $q(x)$ 로 근사하면서, 그 둘 사이의 **거리를 반복적으로 좁혀나가는** 방법을 원한다. 두 확률 분포 사이의 거리는 **쿨백-라이블러(Kullback-Leibler, KL) 발산**으로 계산한다.

$$KL(p_1(x) \| p_2(x)) = \mathbb{E}_{x \sim p_1(x)} \log \frac{p_1(x)}{p_2(x)} = \mathbb{E}_{x\sim p_1(x)}[\log p_1(x)] - \mathbb{E}_{x\sim p_1(x)}[\log p_2(x)]$$

KL 발산 식의 **첫 번째 항**은 **엔트로피(entropy)** 라 불리며, $p_2(x)$ 에 의존하지 않으므로 최소화 과정에서 생략할 수 있다. **두 번째 항**이 바로 **교차 엔트로피**라 불리는 것으로, 딥러닝에서 아주 흔히 쓰이는 최적화 목표다. ([[교차 엔트로피 Cross-Entropy]] 참고)

두 식을 결합하면, $q_0(x) = p(x)$ 에서 시작해 매 스텝마다 개선해 나가는 **반복 알고리즘**을 얻을 수 있다. 이는 $p(x)H(x)$ 를 다음과 같이 갱신하며 근사하는 것이다.

$$q_{i+1}(x) = \underset{q_{i+1}(x)}{\arg\min} -\mathbb{E}_{x\sim q_i(x)}\frac{p(x)}{q_i(x)}H(x)\log q_{i+1}(x)$$

이것이 일반적인 형태의 교차 엔트로피 방법이며, 우리 RL 상황에서는 크게 단순화할 수 있다. $H(x)$ 를 **지시함수(indicator function)** 로 바꾸는데, 이 함수는 에피소드의 보상이 임계값보다 높으면 1, 낮으면 0이 되는 함수다.

우리의 정책 갱신 식은 다음과 같은 모습이 된다.

$$\pi_{i+1}(a|s) = \underset{\pi_{i+1}}{\arg\min} -\mathbb{E}_{z\sim\pi_i(a|s)}\left[R(z) \geq \psi_i\right]\log\pi_{i+1}(a|s)$$

엄밀히 말하면 앞의 식에는 **정규화 항**이 빠져 있지만, 그것 없이도 실전에서는 잘 작동한다. 그러니 방법은 아주 명확하다 — 현재 정책(처음에는 무작위 초기 정책에서 시작)으로 에피소드들을 샘플링하고, **가장 성공적인 샘플들과 우리 정책 사이의 음의 로그 가능도(negative log likelihood)** 를 최소화한다.

> [!tip] 더 깊이 공부하고 싶다면
> 관심이 있다면 Reuven Rubinstein과 Dirk P. Kroese가 쓴, 이 방법에 온전히 헌정된 책 [RK04] 을 참고하라. 더 짧은 설명은 위에서 언급한 "Cross-entropy method" 논문([Kro+11])에서 찾을 수 있다.

---

## 요약

이 챕터에서 우리는:

1. **강화학습 방법의 분류법** — model-free vs model-based, value-based vs policy-based, on-policy vs off-policy — 을 배웠고, 교차 엔트로피 방법이 **model-free, policy-based, on-policy** 임을 확인했다.
2. **교차 엔트로피 방법의 핵심 아이디어** — "좋은 에피소드만 골라 그대로 따라 배우기" — 를 비유와 함께 익혔다.
3. **CartPole 환경**에서 이 방법이 100줄도 안 되는 코드로 완벽하게 통하는 것을 보았다. 신경망, `Episode`/`EpisodeStep` 데이터클래스, `iterate_batches`(에피소드 생성), `filter_batch`(엘리트 선별), 훈련 루프까지 코드 한 줄 한 줄을 뜯어보았다.
4. **FrozenLake 환경**에서는 같은 방법이 초기에 완전히 실패하는 것을 보았고, 그 원인이 **보상 구조(희소하고 이진적인 보상)** 에 있음을 이해했다. 배치 크기 확대, 할인율 적용, 엘리트 에피소드 장기 보관, 학습률 감소, 긴 훈련 시간 같은 조정으로 55% 정도까지 성능을 끌어올릴 수 있었지만 완벽하지는 않았다.
5. 환경의 **미끄러움(확률적 전이)** 이 학습 속도에 얼마나 큰 영향을 주는지, `is_slippery=False` 비교 실험으로 확인했다.
6. (선택) 이 방법의 **이론적 배경** — 중요도 샘플링 정리와 KL 발산으로부터 교차 엔트로피가 어떻게 유도되는지 — 을 살펴보았다.

이것으로 이 책의 **Part 1(입문부)** 이 끝난다. 다음 파트에서는 더 체계적으로 RL 방법들을 공부하며, **가치 기반(value-based)** 방법군을 본격적으로 다룬다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)

- [[지도학습 비지도학습 강화학습]]
- [[교차 엔트로피 Cross-Entropy]]
- [[소프트맥스 Softmax]]
- [[확률분포로부터 샘플링]]
- [[원-핫 인코딩]]
- [[몬테카를로식 에피소드]]
- [[백분위수 필터링]]
- [[상태 관측 에피소드 정책]]
- [[신경망 경사하강 역전파 기초]]
- [[기댓값 Expectation]]

## 한눈에 보는 개념 지도

| 개념 | 기호/코드 | 한 줄 뜻 |
|---|---|---|
| 정책 | $\pi(a\mid s)$ | 상태별 행동 선택 확률 분포 |
| 엘리트 에피소드 | `elite_batch` | 보상이 경계값보다 높은 에피소드 |
| 보상 경계값 | `reward_bound` | 백분위수로 정한 필터링 기준 |
| 백분위수 | `PERCENTILE = 70` | 상위 몇 %만 남길지 정하는 기준 |
| 원-핫 인코딩 | `DiscreteOneHotWrapper` | 이산 상태를 벡터로 표현하는 방식 |
| 교차 엔트로피 손실 | `nn.CrossEntropyLoss` | softmax + 로그손실을 합친 안정적 손실함수 |
| 할인율 | $\gamma$ | 에피소드 길이에 따라 보상을 깎는 정도 |
| KL 발산 | $KL(p_1\|p_2)$ | 두 확률분포 사이의 거리 |
