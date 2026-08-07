---
title: "Chapter 6 — 심층 Q 네트워크 (Deep Q-Networks)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 6
tags: [DeepRL, 강화학습, DQN, Q러닝, CNN, 경험재생, 타깃네트워크, Atari]
---

# Chapter 6 · 심층 Q 네트워크 (DQN)

> [!abstract] 이 챕터를 한 문장으로
> **표(table)로는 감당 안 되는 거대한 상태 공간**(예: 아타리 게임 화면)에서도 좋은 행동을 배울 수 있도록, Q값을 저장하는 표 대신 **신경망으로 Q값을 근사**하는 방법이 DQN이다. 이 신경망 학습이 안정적으로 굴러가게 만드는 **세 가지 핵심 트릭** — 엡실론-그리디 탐험, 경험 재생, 타깃 네트워크 — 이 이번 챕터의 진짜 주인공이다.

---

## 들어가며 — 5장에서 여기까지

[[할인율 감마와 등비급수|5장]]에서 우리는 **벨만 방정식**과 그 실전 적용법인 **가치 반복(value iteration)** 을 배웠다. 이 방법으로 FrozenLake 환경을 빠르고 정확하게 풀 수 있었다. 그렇다면 이 방법을 그대로 더 어려운 문제, 예를 들어 아타리(Atari) 아케이드 게임에 적용하면 어떨까?

이번 챕터에서는:
1. **가치 반복 방법의 근본적인 한계**를 짚어보고, 그 개선판인 **Q-러닝(Q-learning)** 을 소개한다.
2. Q-러닝을 그리드 월드류 환경에 적용하는 **표 기반 Q-러닝(tabular Q-learning)** 을 실습한다.
3. Q-러닝을 **신경망(NN)** 과 결합한 **심층 Q 네트워크(DQN)** 를 만든다.

마지막에는 2013년에 발표되어 RL 연구의 새 시대를 연 논문 *Playing Atari with Deep Reinforcement Learning* [Mni13]의 DQN 알고리즘을 직접 재구현해, **Pong** 게임을 플레이하는 에이전트를 학습시킨다.

---

## 1. 현실의 가치 반복 — 왜 한계에 부딪히나

### 1.1 가치 반복 복습

가치 반복 방법은 다음을 반복한다: **모든 상태**를 순회하며, 각 상태의 가치를 벨만 근사식으로 업데이트한다. Q값 버전(행동에 대한 가치)도 원리는 같다 — 모든 (상태, 행동) 쌍의 값을 근사하고 저장한다.

여기서 문제가 되는 것은 **"모든 상태(또는 상태-행동 쌍)를 순회할 수 있는가"** 라는 전제다.

### 1.2 문제 ① — 상태 개수가 감당이 안 된다

가치 반복은 환경의 모든 상태를 미리 알고, 그 값을 저장할 수 있다고 가정한다. FrozenLake처럼 작은 그리드 월드라면 문제없다. 하지만 다른 문제들은 어떨까?

> [!example] 상태가 10억 개인 환경
> 31,600×31,600 크기의 FrozenLake를 상상해 보자. 상태 개수가 약 10억 개다. 32GB 메모리로 85억 개의 float 값을 저장할 수 있으니(1개 상태당 8.5개 저장 가능), **메모리 자체는 크게 문제 되지 않는다.** 진짜 문제는 **좋은 근삿값을 얻는 데 필요한 샘플(경험) 개수**다. 10억 개 상태 각각에 대해 대략적인 근사치라도 얻으려면 수천억 번의 전이(transition)가 골고루 필요한데, 이건 현실적으로 불가능하다.

이제 진짜 어려운 예시로 넘어가자. **아타리 2600** 게임 콘솔이다. 화면 해상도는 210×160 픽셀이고, 픽셀마다 128가지 색상이 가능하다. 한 프레임(화면)에 나올 수 있는 경우의 수는:

$$128^{210 \times 160} = 128^{33600} \approx 10^{70802}$$

> [!warning] 상상을 초월하는 숫자
> $10^{70802}$ 는 우주의 원자 개수($\sim 10^{80}$)보다도 압도적으로 크다. 이 모든 화면을 한 번씩이라도 순회하는 건, 세상에서 가장 빠른 슈퍼컴퓨터로도 **수십억×수십억 년**이 걸린다. 게다가 이 중 99.(9)%는 실제 게임 플레이 중에 절대 나오지 않을 조합이다 — 순전히 낭비인 시간이다. 그런데도 가치 반복은 "혹시 몰라서" 이 모든 경우를 다 훑으려 한다.

### 1.3 문제 ② — 연속 행동 공간을 다룰 수 없다

$Q(s,a)$와 $V(s)$를 근사하는 방식은 행동이 **서로 배타적인 유한 개의 이산 집합**이라는 가정에 의존한다. 하지만 자동차 핸들 각도, 액추에이터에 가하는 힘, 히터 온도처럼 **연속적인 값**을 갖는 행동에는 이 가정이 통하지 않는다. 이 문제는 책의 후반부(연속 행동 공간을 다루는 챕터들)에서 본격적으로 다룬다. 이번 챕터에서는 행동 개수가 그리 많지 않은(수십 개 수준) 이산 행동만 다룬다고 가정한다.

그럼 상태 공간 크기 문제는 어떻게 풀어야 할까?

---

## 2. 표 기반 Q-러닝 (Tabular Q-learning)

### 2.1 핵심 아이디어 — 필요한 상태만 다루자

가치 반복에서 정말로 모든 상태를 순회해야 할까? 우리에게는 **환경**이라는, 실제 삶의 표본(sample)을 얻을 수 있는 원천이 있다. 환경이 우리에게 보여주지 않는 상태라면, 애초에 그 값을 신경 쓸 이유가 없지 않은가? **환경에서 실제로 얻은 상태들만으로 가치를 갱신하면** 많은 수고를 덜 수 있다.

이 개선판이 바로 **Q-러닝(Q-learning)** 이다. 상태-값 매핑이 명시적인 경우, 다음 절차를 따른다.

1. **빈 표**로 시작한다. 상태를 행동들의 값에 매핑하는 표다.
2. 환경과 상호작용하며 튜플 $s, a, r, s'$(상태, 행동, 보상, 다음 상태)를 얻는다. 이 단계에서 **어떤 행동을 취할지 결정**해야 하는데, 정답은 하나가 아니다 — 이것이 [[Chapter 01 - 강화학습이란 무엇인가]]에서 논의한 **탐험 대 활용** 문제이며, 이번 챕터에서 자세히 다룬다.
3. 벨만 근사식으로 $Q(s,a)$ 값을 업데이트한다.

$$Q(s,a) \leftarrow r + \gamma \max_{a' \in A} Q(s', a')$$

4. 2단계부터 반복한다.

가치 반복과 마찬가지로, 종료 조건은 업데이트가 어떤 임계값 이하로 작아지거나, 테스트 에피소드로 기대 보상을 확인하는 방식이 될 수 있다.

> [!note] 가치 반복과의 차이, 한 문장으로
> 가치 반복은 "**내가 아는 모든** 상태를 순회하며 값을 갱신"하고, Q-러닝은 "**환경이 실제로 보여준** 상태만 값을 갱신"한다. 후자는 낭비를 줄이는 대신, 아직 안 가본 상태에 대해서는 정보가 없다는 대가를 치른다.

### 2.2 Q값 갱신을 더 부드럽게 — 블렌딩(blending)

여기서 짚어야 할 세부사항이 하나 있다. 환경에서 샘플을 뽑을 때, 새 값을 기존 값 위에 그냥 덮어쓰는 건 좋은 생각이 아니다. 환경이 노이즈가 있거나 확률적이면 학습이 불안정해질 수 있기 때문이다.

실전에서 흔히 쓰는 방법은 새 값과 옛 값을 **학습률(learning rate) α**(0~1 사이 값)로 평균 내는(블렌딩하는) 것이다.

$$Q(s,a) \leftarrow (1-\alpha)Q(s,a) + \alpha\left(r + \gamma \max_{a' \in A} Q(s', a')\right)$$

> [!tip] 비유 — 새 정보를 조심스럽게 반영하기
> 여러분이 어떤 식당의 평점을 "지금까지 방문 경험의 평균"으로 매기고 있다고 하자. 오늘 한 번 갔다 온 경험이 아무리 강렬해도, 그 한 번으로 평점을 완전히 새로 덮어쓰지는 않는다. 대신 **"기존 평점의 (1-α) + 오늘 경험의 α"** 처럼 조금씩만 반영해야, 어쩌다 생긴 예외적인 하루(웨이터가 아팠던 날 등)에 평점이 확 흔들리지 않는다. α가 작을수록 신중하게, α가 클수록 최신 경험을 강하게 반영한다.

이를 반영한 최종 알고리즘은 다음과 같다.

1. $Q(s,a)$에 대한 빈 표로 시작한다.
2. 환경에서 $(s, a, r, s')$을 얻는다.
3. 벨만 업데이트를 수행한다: $Q(s,a) \leftarrow (1-\alpha)Q(s,a) + \alpha(r + \gamma \max_{a' \in A} Q(s',a'))$
4. 수렴 조건을 확인한다. 만족하지 않으면 2단계부터 반복한다.

이 방법을 **표 기반 Q-러닝(tabular Q-learning)** 이라 부르는 이유는, 상태들을 그 Q값과 함께 표로 유지하기 때문이다.

### 2.3 FrozenLake에 적용해 보기

전체 예제 코드는 `Chapter06/01_frozenlake_q_learning.py`에 있다. 먼저 패키지와 상수, 타입을 정의한다.

```python
import typing as tt
import gymnasium as gym
from collections import defaultdict
from torch.utils.tensorboard.writer import SummaryWriter

ENV_NAME = "FrozenLake-v1"
GAMMA = 0.9
ALPHA = 0.2
TEST_EPISODES = 20

State = int
Action = int
ValuesKey = tt.Tuple[State, Action]

class Agent:
    def __init__(self):
        self.env = gym.make(ENV_NAME)
        self.state, _ = self.env.reset()
        self.values: tt.Dict[ValuesKey] = defaultdict(float)
```

- `GAMMA = 0.9`: 할인율. [[할인율 감마와 등비급수]] 참고.
- `ALPHA = 0.2`: 위에서 설명한 블렌딩 학습률 — 새 값을 20%만 반영한다.
- `self.values`: `(상태, 행동)` 쌍을 키로 하는 딕셔너리. `defaultdict(float)`이라 없는 키를 조회하면 자동으로 0.0을 반환한다 — 표가 무한히 크다고 가정해도 실제로는 방문한 상태만 딕셔너리에 채워지는 셈이다.
- 이전 챕터들과 달리 **보상과 전이 횟수를 따로 기록할 필요가 없다.** 값 표 하나만 유지하면 되므로 메모리 사용이 더 가볍다. FrozenLake에서는 큰 차이가 없지만, 더 큰 환경에서는 중요해진다.

환경에서 한 스텝을 얻는 메서드:

```python
def sample_env(self) -> tt.Tuple[State, Action, float, State]:
    action = self.env.action_space.sample()
    old_state = self.state
    new_state, reward, is_done, is_tr, _ = self.env.step(action)
    if is_done or is_tr:
        self.state, _ = self.env.reset()
    else:
        self.state = new_state
    return old_state, action, float(reward), new_state
```

무작위 행동을 뽑아 실행하고, 이전 상태·행동·보상·새 상태를 튜플로 반환한다. 이 튜플은 이후 학습 루프에서 사용된다.

주어진 상태에서 최선의 행동을 찾는 메서드:

```python
def best_value_and_action(self, state: State) -> tt.Tuple[float, Action]:
    best_value, best_action = None, None
    for action in range(self.env.action_space.n):
        action_value = self.values[(state, action)]
        if best_value is None or best_value < action_value:
            best_value = action_value
            best_action = action
    return best_value, best_action
```

표에 있는 값 중 가장 큰 것을 가진 행동을 찾는다(값이 없으면 0으로 취급). 이 메서드는 두 곳에서 쓰인다: 정책의 품질을 평가하는 테스트 메서드, 그리고 다음 상태의 값을 구하는 값 업데이트 메서드.

한 스텝의 경험으로 값 표를 갱신하는 메서드:

```python
def value_update(self, state: State, action: Action, reward: float, next_state: State):
    best_val, _ = self.best_value_and_action(next_state)
    new_val = reward + GAMMA * best_val
    old_val = self.values[(state, action)]
    key = (state, action)
    self.values[key] = old_val * (1-ALPHA) + new_val * ALPHA
```

먼저 상태 $s$, 행동 $a$에 대한 벨만 근사값을 계산한다(즉시 보상 + 다음 상태의 할인된 가치). 그다음 표에 있던 기존값을 가져와, 학습률로 두 값을 블렌딩한 결과를 새 근사치로 저장한다.

테스트 환경에서 한 에피소드 전체를 플레이하는 메서드:

```python
def play_episode(self, env: gym.Env) -> float:
    total_reward = 0.0
    state, _ = env.reset()
    while True:
        _, action = self.best_value_and_action(state)
        new_state, reward, is_done, is_tr, _ = env.step(action)
        total_reward += reward
        if is_done or is_tr:
            break
        state = new_state
    return total_reward
```

매 스텝 지금의 Q값 표를 이용해 최선의 행동을 선택한다. 이 메서드는 현재 정책을 평가하는 데만 쓰이며, **값 표를 바꾸지 않는다** — 오직 최선의 행동을 찾는 데만 표를 참조한다.

나머지는 학습 루프다. 5장과 매우 비슷하다: 테스트용 환경, 에이전트, summary writer를 만들고, 루프 안에서 환경 한 스텝 → 값 갱신 → 테스트 에피소드 여러 번 플레이 → 좋은 보상이면 학습 종료.

```python
if __name__ == "__main__":
    test_env = gym.make(ENV_NAME)
    agent = Agent()
    writer = SummaryWriter(comment="-q-learning")

    iter_no = 0
    best_reward = 0.0
    while True:
        iter_no += 1
        state, action, reward, next_state = agent.sample_env()
        agent.value_update(state, action, reward, next_state)

        test_reward = 0.0
        for _ in range(TEST_EPISODES):
            test_reward += agent.play_episode(test_env)
        test_reward /= TEST_EPISODES
        writer.add_scalar("reward", test_reward, iter_no)
        if test_reward > best_reward:
            print("%d: Best test reward updated %.3f -> %.3f" % (iter_no, best_reward,
                test_reward))
            best_reward = test_reward
        if test_reward > 0.80:
            print("Solved in %d iterations!" % iter_no)
            break
    writer.close()
```

실행 결과는 다음과 같다.

```
Chapter06$ ./01_frozenlake_q_learning.py
1149: Best test reward updated 0.000 -> 0.500
1150: Best test reward updated 0.500 -> 0.550
1164: Best test reward updated 0.550 -> 0.600
1242: Best test reward updated 0.600 -> 0.650
2685: Best test reward updated 0.650 -> 0.700
2988: Best test reward updated 0.700 -> 0.750
3025: Best test reward updated 0.750 -> 0.850
Solved in 3025 iterations!
```

이 버전은 [[할인율 감마와 등비급수|5장]]의 가치 반복보다 더 많은 반복이 필요했다(실험마다 스텝 수는 다를 수 있다). 이유는 **테스트 중 얻은 경험을 더 이상 활용하지 않기 때문**이다. 5장의 `02_frozenlake_q_iteration.py`에서는 주기적인 테스트가 Q표의 통계를 함께 갱신했지만, 여기서는 테스트 중에는 Q값을 건드리지 않으므로 환경이 풀리기까지 더 오래 걸린다. 다만 환경에서 필요로 하는 전체 샘플 수는 거의 비슷하다.

![[fig_6_1.png]]
*그림 6.1 — FrozenLake의 보상 다이나믹스(TensorBoard 기록). 5장의 가치 반복과 비슷하게 좋은 학습 추세를 보인다.*

다음 절에서는 이 Q-러닝 방법을 **신경망으로 환경 상태를 전처리**하도록 확장한다. 이는 이 방법의 유연성과 적용 범위를 크게 넓혀준다.

---

## 3. 심층 Q-러닝 (Deep Q-learning)

### 3.1 표가 감당 못 하는 상황

방금 다룬 Q-러닝 방법은 관측 가능한 상태 집합 전체를 순회하는 문제는 해결했지만, **관측 가능한 상태의 개수가 매우 크거나 사실상 무한한** 상황에서는 여전히 어려움을 겪는다. 예를 들어 아타리 게임은 원본 픽셀을 개별 상태로 쓰면 상태가 너무 많아져 감당이 안 된다.

CartPole 같은 환경에서도 마찬가지다. 이 환경은 4개의 부동소수점 숫자로 이루어진 상태를 준다. 값의 조합 개수는 유한하지만(bit로 표현되므로), $2^{4 \times 32} \approx 3.4 \times 10^{38}$ 정도로 여전히 어마어마하게 크다. 실제로는 상태값에 한계가 있어 모든 bit 조합이 가능하지는 않지만, 그래도 상태 공간은 지나치게 크다. 값들을 구간(bin)으로 나누어 이산화할 수도 있지만, 이는 대개 문제를 해결하기보다 더 많은 문제(어떤 구간이 중요한지, 어떻게 묶을지 결정해야 하는 문제)를 만든다. 게다가 우리는 환경 내부를 들여다보지 않는 **일반적인** 방식으로 RL 방법을 구현하고 싶으므로, 이는 그다지 유망한 방향이 아니다.

### 3.2 비슷한 상태를 비슷하게 취급하기

아타리의 경우, 픽셀 하나가 바뀌었다고 해서 큰 차이가 생기지는 않는다. 그래서 **비슷한 이미지를 하나의 상태로 취급**하고 싶어진다. 하지만 동시에 일부 상태는 여전히 구별해야 한다.

![[fig_6_2.png]]
*그림 6.2 — Pong 관측의 모호성. 왼쪽 이미지에서는 공이 오른쪽(우리 라켓 방향)으로 움직이고, 오른쪽 이미지에서는 그 반대로 움직인다.*

우리는 상대 AI(왼쪽 라켓)와 대결하며 오른쪽 라켓을 조종해 Pong을 플레이한다고 하자. 목표는 튕기는 공을 상대의 라켓 뒤로 넘기고, 우리 쪽 라켓 뒤로는 공이 넘어가지 않게 막는 것이다. 그림의 오른쪽 상황은 공이 상대 쪽에 가까이 있으니 여유 있게 지켜봐도 되지만, 왼쪽 상황은 공이 우리 쪽으로 다가오는 중이라 급히 라켓을 움직여야 한다. 두 상황은 $10^{70802}$개의 가능한 화면 중 딱 두 장에 불과하지만, 에이전트가 이 둘에 서로 다르게 반응하기를 원한다.

이 문제의 해결책은 **상태와 행동을 하나의 값으로 매핑하는 비선형 표현**을 쓰는 것이다. 머신러닝에서는 이를 "회귀 문제(regression problem)"라 부른다. 구체적인 표현·학습 방법은 다양하지만, 특히 관측이 화면 이미지로 표현될 때는 **심층 신경망(deep NN)** 을 쓰는 것이 가장 인기 있는 선택지다. 이를 염두에 두고, Q-러닝 알고리즘을 다음처럼 수정하자.

1. $Q(s,a)$를 어떤 초기 근사값으로 초기화한다.
2. 환경과 상호작용하며 $(s,a,r,s')$를 얻는다.
3. 손실을 계산한다:

$$\mathcal{L} = (Q(s,a) - r)^2 \quad \text{(에피소드가 끝난 경우)}$$
$$\mathcal{L} = \left(Q(s,a) - \left(r + \gamma \max_{a' \in A} Q_{s',a'}\right)\right)^2 \quad \text{(그 외의 경우)}$$

4. **확률적 경사하강법(SGD)** 을 이용해, 모델 파라미터에 대해 손실을 최소화하도록 $Q(s,a)$를 갱신한다.
5. 수렴할 때까지 2단계부터 반복한다.

언뜻 간단해 보이지만, 안타깝게도 이대로는 잘 작동하지 않는다. 여기서부터 잘못될 수 있는 여러 측면과, 그것을 다루는 방법을 하나씩 짚어보자.

---

## 4. 환경과의 상호작용 — 다시 보는 탐험 vs 활용

먼저, 학습에 쓸 데이터를 얻으려면 환경과 어떻게든 상호작용해야 한다. FrozenLake처럼 단순한 환경에서는 무작위로 행동해도 되지만, 이게 최선의 전략일까? Pong 게임을 떠올려 보자. 라켓을 무작위로 움직여서 한 점을 딸 확률은 얼마일까? 0은 아니지만 극히 작다 — 이런 희귀한 상황이 나올 때까지 무한정 기다려야 한다는 뜻이다.

대안으로, (5장의 가치 반복에서 테스트 중 얻은 경험을 기억했던 것처럼) **Q함수 근사치 자체를 행동의 원천**으로 쓸 수 있다.

Q의 근사가 좋다면, 환경에서 얻는 경험은 에이전트가 학습할 만한 관련성 높은 데이터를 보여줄 것이다. 하지만 문제가 생긴다 — 근사가 아직 완벽하지 않을 때(특히 학습 초기)는, 에이전트가 어떤 상태에 대해 **다른 행동을 한 번도 시도해 보지 못한 채** 나쁜 행동에 갇혀버릴 수 있다. 이것이 [[Chapter 01 - 강화학습이란 무엇인가]]에서 짧게 언급했던 **탐험 대 활용(exploration versus exploitation)** 딜레마다. 이제 이걸 자세히 다뤄보자. 한편으로 에이전트는 전이와 행동 결과의 완전한 그림을 그리기 위해 환경을 **탐험**해야 한다. 다른 한편으로는, 이미 시도해서 결과를 알고 있는 행동을 무의미하게 반복하며 시간을 낭비하지 않도록 상호작용을 **효율적으로** 활용해야 한다.

학습 초반에는 Q 근사가 형편없으므로, 무작위 행동이 더 유리하다. 환경 상태에 대해 더 고르게 분포된 정보를 주기 때문이다. 학습이 진행될수록 무작위 행동은 비효율적이 되고, Q 근사에 의존해 어떻게 행동할지 결정하고 싶어진다.

이 두 극단적인 행동을 섞는 방법이 바로 **엡실론-그리디(epsilon-greedy) 방법** 이다 — 하이퍼파라미터 확률 ε를 이용해 무작위 행동과 Q 정책 사이를 전환한다. ε을 조절하면 무작위 행동의 비율을 정할 수 있다. 흔한 관행은 ε=1.0(100% 무작위 행동)으로 시작해, 5% 또는 2%처럼 작은 값까지 서서히 줄이는 것이다. 자세한 원리와 비유는 [[엡실론-그리디 탐험]]에 정리했다.

엡실론-그리디 방법을 쓰면 학습 초반에는 환경을 탐험하고, 학습 후반에는 좋은 정책을 고수할 수 있다. 탐험 대 활용 문제에는 다른 해결책들도 있으며, 이 책 3부에서 몇 가지를 더 다룬다. 이 문제는 RL의 근본적인 미해결 질문 중 하나이며, 완전히 풀리지 않은 활발한 연구 분야다.

---

## 5. SGD 최적화

Q-러닝 절차의 핵심은 지도학습에서 빌려온 것이다. 실제로 우리는 복잡한 비선형 함수 $Q(s,a)$를 NN으로 근사하려 한다. 이를 위해 벨만 방정식으로 이 함수의 목표값을 계산하고, 지도학습 문제인 척 취급한다. 그런데 SGD 최적화의 근본 요구사항 중 하나는, 학습 데이터가 **[[IID 독립항등분포]]** (iid) 여야 한다는 것이다 — 즉 학습 데이터가 우리가 배우려는 기저 분포에서 **무작위로 독립적으로** 뽑혀야 한다.

우리 경우, SGD 업데이트에 쓰려는 데이터는 이 기준을 만족하지 않는다.

1. **샘플들이 독립적이지 않다.** 큰 배치로 데이터를 모아도, 같은 에피소드에 속해 있으므로 서로 매우 가깝게 붙어 있다.
2. **학습 데이터의 분포가 우리가 배우고 싶은 최적 정책의 표본 분포와 같지 않다.** 우리가 가진 데이터는 지금의 정책(현재 정책, 무작위 정책, 또는 엡실론-그리디의 경우 둘 다)의 결과인데, 우리가 배우고 싶은 것은 **무작위로 플레이하는 방법이 아니라** 최고의 보상을 얻는 최적 정책이다.

이 골칫거리를 해결하기 위해, 보통 과거 경험을 담은 **큰 버퍼**를 두고, 최신 경험 대신 거기서 학습 데이터를 샘플링한다. 이 기법을 **리플레이 버퍼(replay buffer)** 라 부른다. 가장 단순한 구현은 고정 크기의 버퍼로, 새 데이터를 끝에 추가하면서 가장 오래된 경험을 밀어낸다. 리플레이 버퍼 덕분에 어느 정도 독립적인 데이터로 학습할 수 있으면서도, 최근 정책이 만들어낸 신선한 샘플로 계속 학습할 수 있다. 8장에서는 더 정교한 샘플링 방식인 **우선순위 리플레이 버퍼(prioritized replay buffer)** 를 다룬다. 자세한 원리는 [[경험 재생 Experience Replay]]를 참고하라.

---

## 6. 스텝 사이의 상관관계

기본 학습 절차의 또 다른 실질적인 문제는 iid 데이터 부족과 관련이 있지만, 조금 다른 측면이다. 벨만 방정식은 $Q(s',a')$을 통해 $Q(s,a)$의 값을 제공한다(이 과정을 **[[타깃 네트워크와 부트스트래핑|부트스트래핑(bootstrapping)]]** 이라 부르며, 공식을 재귀적으로 사용하는 것을 뜻한다). 그런데 상태 $s$와 $s'$는 **한 스텝**밖에 차이가 나지 않는다. 이 둘은 매우 비슷해서, NN이 이 둘을 구별하기가 매우 어렵다. NN 파라미터를 업데이트해 $Q(s,a)$를 원하는 결과에 더 가깝게 만들면, 간접적으로 $Q(s',a')$와 그 근방의 다른 상태들에 대한 값도 바뀌어 버릴 수 있다.

이는 학습을 매우 불안정하게 만들 수 있다 — 마치 제 꼬리를 쫓는 것처럼, 상태 $s$의 $Q$를 갱신하면 다음 상태들에서 $Q(s',a')$가 더 나빠졌다는 것을 발견하고, 그러면 이를 고치려는 시도가 $Q(s,a)$ 근사를 더 망칠 수 있으며, 이런 식으로 계속된다.

이 문제를 안정시키기 위한 트릭이 있는데, **타깃 네트워크(target network)** 라 불린다. 이 방법에서는 우리 네트워크의 사본을 하나 유지해, 벨만 방정식에서 $Q(s',a')$ 값을 계산하는 데 사용한다. 이 네트워크는 오직 주기적으로만(예를 들어 N 스텝마다 한 번씩, N은 보통 1k나 10k처럼 상당히 큰 하이퍼파라미터다) 우리의 메인 네트워크와 동기화된다. 원리와 코드는 [[타깃 네트워크와 부트스트래핑]]에 자세히 정리했다.

---

## 7. 마르코프 성질

우리의 RL 방법들은 **마르코프 결정 과정(MDP)** 형식을 기반으로 삼고 있으며, 이는 환경이 마르코프 성질을 따른다고 가정한다 — 즉 환경으로부터 얻는 관측만으로 최적으로 행동하는 데 충분해야 한다는 뜻이다(다시 말해, 관측만으로 상태들을 서로 구별할 수 있어야 한다).

앞서 그림 6.2의 Pong 스크린샷에서 보았듯이, 아타리 게임의 이미지 한 장만으로는 중요한 정보(공과 상대 라켓의 속도와 방향 같은)를 담기에 충분하지 않다. 이는 명백히 마르코프 성질을 위반하고, 우리의 단일 프레임 Pong 환경을 **부분관측 MDP(partially observable MDP, POMDP)** 영역으로 밀어넣는다. POMDP는 근본적으로 마르코프 성질이 없는 MDP다. 실전에서 매우 중요한 개념인데, 예를 들어 상대의 카드를 볼 수 없는 대부분의 카드 게임은 POMDP다 — 현재의 관측(즉 여러분의 카드와 테이블 위의 카드)이 상대 손에 있는 서로 다른 카드들에 대응될 수 있기 때문이다.

이 책에서는 POMDP를 자세히 다루지 않지만, 환경을 다시 MDP 영역으로 밀어 넣는 작은 기법 하나를 쓴다. 해결책은 **과거의 여러 관측을 함께 유지**해 이를 상태로 쓰는 것이다. 아타리 게임의 경우, 보통 연속된 $k$개의 프레임을 함께 쌓아 매 상태의 관측으로 사용한다. 이렇게 하면 에이전트가 현재 상태의 다이나믹스(예를 들어 공의 속도와 방향)를 유추할 수 있다. 아타리에서 흔히 쓰는 "고전적인" $k$ 값은 4다. 물론 이는 하나의 편법일 뿐이며, 환경에는 그보다 더 긴 의존관계가 있을 수 있지만, 대부분의 게임에서는 잘 작동한다. 프레임 스태킹과 그 밖의 전처리 래퍼에 대해서는 [[프레임 스태킹과 아타리 전처리]]를 참고하라.

---

## 8. DQN 학습의 최종 형태

연구자들이 DQN 학습을 더 안정적이고 효율적으로 만들기 위해 발견한 팁과 트릭은 훨씬 더 많으며, 8장에서 그중 최고를 다룰 것이다. 하지만 **엡실론-그리디, 리플레이 버퍼, 타깃 네트워크**, 이 세 가지가 DeepMind가 49개 아타리 게임 세트에서 DQN을 성공적으로 학습시킬 수 있었던 기초를 이룬다. 이는 이 접근법이 복잡한 환경에 적용될 때 얼마나 효율적인지 보여준다.

타깃 네트워크 없이 발표된 원 논문 *Playing Atari with Deep Reinforcement Learning* [Mni13]은 2013년 말에 발표되었고 7개 게임으로 테스트되었다. 이후 2015년 초, *Human-level control through deep reinforcement learning* [Mni+15]라는 제목의 개정판 논문이 49개의 서로 다른 게임과 함께 *Nature*에 게재되었다.

앞선 논문들이 제시한 DQN 알고리즘은 다음 단계로 이루어진다.

1. $Q(s,a)$와 $\hat{Q}(s,a)$의 파라미터를 무작위 가중치로 초기화하고, $\epsilon \leftarrow 1.0$으로, 리플레이 버퍼는 비운다.
2. 확률 $\epsilon$로 무작위 행동 $a$를 선택하고, 그렇지 않으면 $a = \arg\max_a Q(s,a)$로 선택한다.
3. 에뮬레이터에서 행동 $a$를 실행하고, 보상 $r$과 다음 상태 $s'$를 관측한다.
4. 전이 $(s,a,r,s')$을 리플레이 버퍼에 저장한다.
5. 리플레이 버퍼에서 전이들의 무작위 미니배치를 샘플링한다.
6. 버퍼 안의 모든 전이에 대해 목표값을 계산한다:

$$y = r \quad \text{(에피소드가 끝난 경우)}$$
$$y = r + \gamma \max_{a' \in A} \hat{Q}(s', a') \quad \text{(그 외의 경우)}$$

7. 손실을 계산한다: $\mathcal{L} = (Q(s,a) - y)^2$
8. 모델 파라미터에 대해 손실을 최소화하는 방향으로 SGD 알고리즘을 이용해 $Q(s,a)$를 업데이트한다.
9. $N$ 스텝마다 $Q$의 가중치를 $\hat{Q}$로 복사한다.
10. 수렴할 때까지 2단계부터 반복한다.

이제 이 알고리즘을 구현해, 아타리 게임 몇 개를 실제로 이겨보자!

---

## 9. Pong에서의 DQN

코드로 들어가기 전에 몇 가지 소개할 내용이 있다. 예제들은 점점 더 어렵고 복잡해지고 있는데, 이는 우리가 다루려는 문제의 복잡도가 점점 커지고 있으니 놀랄 일은 아니다. 예제는 최대한 단순하고 간결하게 유지되었지만, 처음에는 코드 일부가 이해하기 어려울 수 있다.

또 하나 짚어야 할 것은 **성능**이다. FrozenLake나 CartPole 같은 이전 예제들은 리소스 관점에서 크게 부담이 없었다 — 관측이 작았고, NN 파라미터가 작았으며, 학습 루프에서 몇 밀리초를 아끼는 것이 중요하지 않았다. 하지만 지금부터는 다르다. 아타리 환경의 관측 하나가 10만 개의 값이며, 이를 전처리하고 다시 스케일링해서 리플레이 버퍼에 저장해야 한다. 이 데이터 배열을 복사하는 추가 작업 하나만으로도 학습 속도가 초·분 단위가 아니라 **최상급 GPU에서도 시간 단위**로 늘어날 수 있다.

NN 학습 루프 자체도 병목이 될 수 있다. 물론 RL 모델은 최신 대형 언어 모델(LLM)만큼 거대한 괴물은 아니지만, 2015년의 DQN 모델조차 150만 개가 넘는 파라미터를 가지고 있고, 이를 수백만 번 조정해야 한다.

> [!important] 성능이 중요한 이유
> 특히 하이퍼파라미터를 실험할 때, 모델 하나가 아니라 수십 개를 학습시켜야 할 때가 많으므로 성능이 중요하다. PyTorch는 표현력이 좋아서, 최적화된 TensorFlow 그래프보다 훨씬 덜 난해한 코드로도 효율적인 처리가 가능하지만, 그래도 느리고 실수하기 쉬운 부분이 많다. 예를 들어 매 배치 샘플을 순회하는 나이브한 DQN 손실 계산은 병렬화된 버전보다 약 2배 느리다. 그런데 배치 데이터를 한 번 더 복사하는 것만으로도 같은 코드가 13배까지 느려질 수 있다 — 상당히 큰 차이다.

이 예제는 길이·논리 구조·재사용성 때문에 세 개의 모듈로 나뉘어 있다.

- `Chapter06/lib/wrappers.py`: 아타리 환경 래퍼들로, 대부분 **Stable Baselines3(SB3)** 프로젝트(https://github.com/DLR-RM/stable-baselines3)에서 가져왔다.
- `Chapter06/lib/dqn_model.py`: DeepMind의 *Nature* 논문과 같은 구조를 가진 DQN NN 레이어.
- `Chapter06/02_dqn_pong.py`: 학습 루프, 손실 함수 계산, 경험 리플레이 버퍼가 담긴 메인 모듈.

### 9.1 래퍼 (Wrappers)

RL로 아타리 게임을 다루는 것은 리소스 관점에서 매우 부담이 크다. 속도를 높이기 위해 아타리 플랫폼 상호작용에 여러 변환이 적용되며, 이는 DeepMind의 논문에 설명되어 있다. 이 변환 중 일부는 성능에만 영향을 주지만, 일부는 학습을 오래 걸리고 불안정하게 만드는 아타리 플랫폼의 특성을 다룬다. 이러한 변환들은 여러 종류의 [[Wrapper 래퍼 패턴|Gym 래퍼]]로 구현된다. 전체 목록은 상당히 길고, 여러 저장소에 비슷한 래퍼들의 구현이 흩어져 있다. 저자가 가장 선호하는 것은 SB3 저장소로, OpenAI Baselines 코드의 발전된 버전이다.

가장 널리 쓰이는 아타리 변환들의 목록, 그리고 그것들이 필요한 이유는 [[프레임 스태킹과 아타리 전처리]]의 표에 정리했다. 요약하면 다음과 같다.

- **개별 목숨을 별도 에피소드로 취급** (`EpisodicLifeEnv`, 이번 구현에서는 생략)
- **게임 시작 시 무작위 횟수만큼 아무 것도 안 하기** (`NoopResetEnv`) — 인트로 화면 건너뛰기
- **K 스텝마다 한 번씩만 행동을 결정하고 반복 적용** (`MaxAndSkipEnv`) — 매 프레임 NN을 돌리는 부담을 줄임
- **최근 두 프레임의 픽셀별 최댓값을 관측으로 사용** — 아타리 특유의 깜빡임(flickering) 현상 보정
- **게임 시작 시 FIRE 버튼 누르기** (`FireResetEnv`) — 일부 게임은 FIRE를 눌러야 시작됨
- **화면을 흑백 84×84로 축소** (`WarpFrame`)
- **여러(보통 4개) 연속 프레임을 쌓기** (`BufferWrapper`) — 물체의 다이나믹스 정보 제공
- **보상을 -1, 0, 1로 클리핑** (`ClipRewardEnv`) — 게임마다 다른 점수 스케일 통일
- **관측 차원을 PyTorch가 기대하는 형식으로 재배열** (`ImageToPyTorch`) — (H, W, C) → (C, H, W)

대부분의 래퍼는 `stable-baseline3` 라이브러리에 구현되어 있으며, 이 라이브러리는 필요한 순서대로 래퍼들을 적용하는 `AtariWrapper` 클래스를 제공한다. 이 클래스는 환경의 기저 속성을 감지해 필요하면 `FireResetEnv`를 자동으로 활성화한다. 모든 래퍼가 모든 게임에 필요한 것은 아니지만(Pong에는 다 필요하지 않다), 다른 게임을 실험할 계획이라면 어떤 래퍼들이 있는지 알아두는 것이 좋다.

> [!warning] "학습이 안 될 때, 범인은 코드가 아니라 래퍼일 수 있다"
> 저자는 DQN이 수렴하지 않을 때 문제가 코드가 아니라 **잘못 래핑된 환경**인 경우가 많다고 경고한다. 실제로 게임 시작 시 FIRE 버튼을 누르는 처리를 빠뜨려서 며칠을 디버깅에 쓴 경험이 있다고 언급한다.

먼저 `stable-baseline3`가 제공하는 클래스부터 살펴보자.

```python
class FireResetEnv(gym.Wrapper[np.ndarray, int, np.ndarray, int]):
    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        assert env.unwrapped.get_action_meanings()[1] == "FIRE"
        assert len(env.unwrapped.get_action_meanings()) >= 3

    def reset(self, **kwargs) -> AtariResetReturn:
        self.env.reset(**kwargs)
        obs, _, terminated, truncated, _ = self.env.step(1)
        if terminated or truncated:
            self.env.reset(**kwargs)
        obs, _, terminated, truncated, _ = self.env.step(2)
        if terminated or truncated:
            self.env.reset(**kwargs)
        return obs, {}
```

이 래퍼는 게임 시작에 FIRE를 눌러야 하는 환경에서 **FIRE 버튼**을 눌러준다. FIRE를 누르는 것 외에도, 이 래퍼는 일부 게임에서 나타날 수 있는 몇 가지 예외 상황(reset 직후 바로 종료 상태가 되는 경우 등)을 확인한다.

$K$ 프레임 동안 행동을 반복하고, 최근 두 프레임의 픽셀을 합치는 래퍼:

```python
class MaxAndSkipEnv(gym.Wrapper[np.ndarray, int, np.ndarray, int]):
    def __init__(self, env: gym.Env, skip: int = 4) -> None:
        super().__init__(env)
        self._obs_buffer = np.zeros((2, *env.observation_space.shape),
            dtype=env.observation_space.dtype)
        self._skip = skip

    def step(self, action: int) -> AtariStepReturn:
        total_reward = 0.0
        terminated = truncated = False
        for i in range(self._skip):
            obs, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            if i == self._skip - 2:
                self._obs_buffer[0] = obs
            if i == self._skip - 1:
                self._obs_buffer[1] = obs
            total_reward += float(reward)
            if done:
                break
        # Note that the observation on the done=True frame
        # doesn't matter
        max_frame = self._obs_buffer.max(axis=0)

        return max_frame, total_reward, terminated, truncated, info
```

한 번 `step()`이 호출될 때마다, 안쪽 `for` 루프가 동일한 `action`으로 실제 환경 `step`을 최대 `skip`(기본 4)번 반복한다. 매 서브스텝의 보상은 `total_reward`에 누적되고, 마지막 두 프레임(`self._skip - 2`, `self._skip - 1` 인덱스)만 버퍼에 저장해두었다가 픽셀별 **최댓값**을 취한다. 도중에 에피소드가 끝나면(`done`) 바로 루프를 멈춘다.

다음으로, 에뮬레이터의 입력 관측(210×160 RGB 색상 채널)을 흑백 84×84 이미지로 변환하는 래퍼다. CV2 라이브러리의 `cvtColor` 함수를 사용하는데, 이는 단순 색상 채널 평균보다 사람의 색 지각에 더 가까운 색측정학적(colorimetric) 흑백 변환을 수행하고, 이후 이미지 크기를 조정한다.

```python
class WarpFrame(gym.ObservationWrapper[np.ndarray, int, np.ndarray]):
    def __init__(self, env: gym.Env, width: int = 84, height: int = 84) -> None:
        super().__init__(env)
        self.width = width
        self.height = height
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.height, self.width, 1),
            dtype=env.observation_space.dtype,
        )

    def observation(self, frame: np.ndarray) -> np.ndarray:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = cv2.resize(frame, (self.width, self.height),
            interpolation=cv2.INTER_AREA)
        return frame[:, :, None]
```

여기까지는 `stable-baseline3`의 래퍼를 이용했다(다소 복잡하고 크게 관련 없다고 판단해 `EpisodicLifeEnv` 래퍼는 생략했다). 이제 `lib/wrappers.py`에 있는 두 개의 래퍼를 살펴보자.

```python
class BufferWrapper(gym.ObservationWrapper):
    def __init__(self, env, n_steps):
        super(BufferWrapper, self).__init__(env)
        obs = env.observation_space
        assert isinstance(obs, spaces.Box)
        new_obs = gym.spaces.Box(
            obs.low.repeat(n_steps, axis=0), obs.high.repeat(n_steps, axis=0),
            dtype=obs.dtype)
        self.observation_space = new_obs
        self.buffer = collections.deque(maxlen=n_steps)

    def reset(self, *, seed: tt.Optional[int] = None, options: tt.Optional[dict[str,
        tt.Any]] = None):
        for _ in range(self.buffer.maxlen-1):
            self.buffer.append(self.env.observation_space.low)
        obs, extra = self.env.reset()
        return self.observation(obs), extra

    def observation(self, observation: np.ndarray) -> np.ndarray:
        self.buffer.append(observation)
        return np.concatenate(self.buffer)
```

`BufferWrapper` 클래스는 `deque` 클래스로 구현된, 첫 번째 축을 따라 연속된 프레임들의 스택을 만들고, 이를 관측으로 반환한다. 목적은 네트워크에게 물체(예: Pong의 공, 적의 움직임 방향)의 다이나믹스에 대한 정보를 주는 것이다. 이 정보는 단일 이미지에서는 얻을 수 없다.

> [!note] `.copy()`가 필요한 이유
> 이 래퍼에 대해 아주 중요하지만 눈에 잘 안 띄는 세부사항 하나: `observation` 메서드는 버퍼링된 관측의 **복사본**을 반환한다는 점이다. 이는 매우 중요한데, 우리가 관측을 리플레이 버퍼에 계속 보관할 것이므로, 미래 환경 스텝에서 버퍼가 수정되는 것을 막기 위해 복사가 필요하다. 원칙적으로는 에피소드의 관측과 인덱스를 함께 관리하는 훨씬 정교한 데이터 구조를 쓰면 복사를 피할 수 있고(메모리 사용량도 4분의 1로 줄일 수 있다), 다만 그러려면 훨씬 복잡한 데이터 구조 관리가 필요하다.

현재 중요한 점은, 이 래퍼가 환경에 적용되는 래퍼 체인의 **맨 마지막**에 와야 한다는 것이다.

마지막 래퍼는 `ImageToPyTorch`로, 관측의 모양을 **높이, 너비, 채널(HWC)** 에서 PyTorch가 요구하는 **채널, 높이, 너비(CHW)** 형식으로 바꾼다.

```python
class ImageToPyTorch(gym.ObservationWrapper):
    def __init__(self, env):
        super(ImageToPyTorch, self).__init__(env)
        obs = self.observation_space
        assert isinstance(obs, gym.spaces.Box)
        assert len(obs.shape) == 3
        new_shape = (obs.shape[-1], obs.shape[0], obs.shape[1])
        self.observation_space = gym.spaces.Box(
            low=obs.low.min(), high=obs.high.max(),
            shape=new_shape, dtype=obs.dtype)

    def observation(self, observation):
        return np.moveaxis(observation, 2, 0)
```

입력 텐서 모양은 색상 채널이 마지막 차원으로 되어 있지만, PyTorch의 합성곱 레이어는 채널 차원이 첫 번째로 오길 요구한다.

파일 마지막에는, 이름으로 환경을 만들고 필요한 모든 래퍼를 적용하는 간단한 함수가 있다.

```python
def make_env(env_name: str, **kwargs):
    env = gym.make(env_name, **kwargs)
    env = atari_wrappers.AtariWrapper(env, clip_reward=False, noop_max=0)
    env = ImageToPyTorch(env)
    env = BufferWrapper(env, n_steps=4)
    return env
```

보다시피, `stable-baseline3`의 `AtariWrapper` 클래스를 사용하면서 일부 불필요한 래퍼는 비활성화하고 있다.

이것으로 래퍼는 끝이다. 이제 우리 모델을 살펴보자.

### 9.2 DQN 모델

*Nature*에 실린 모델은 **3개의 합성곱층**과 그 뒤를 잇는 **2개의 완전연결층**으로 이루어져 있다. 모든 층은 **ReLU(rectified linear unit)** 비선형 함수로 구분된다. 모델의 출력은 환경에서 가능한 모든 행동에 대한 Q값이며, 마지막에는 비선형 함수가 적용되지 않는다(Q값은 어떤 값이든 가질 수 있기 때문이다). 합성곱 구조 원리는 [[합성곱 신경망 CNN]]을 참고하라.

모든 Q값을 신경망 **한 번의 순전파**로 계산하는 이 방식은, 관측과 행동을 둘 다 네트워크에 입력해 문자 그대로 $Q(s,a)$를 계산하는 방식에 비해 속도를 크게 높여준다.

모델 코드는 `Chapter06/lib/dqn_model.py`에 있다.

```python
import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, input_shape, n_actions):
        super(DQN, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.fc = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, n_actions)
        )
```

네트워크를 범용적으로 작성할 수 있도록, 두 부분으로 나누어 구현했다: 합성곱 부분과 선형(완전연결) 부분이다. 합성곱 부분은 입력 이미지(4×84×84 텐서)를 처리한다. 마지막 합성곱 필터의 출력은 1차원 벡터로 펼쳐져(flatten), 두 개의 `Linear` 층에 입력된다.

작은 문제 하나는, 주어진 입력 모양에 대해 합성곱 층이 만들어내는 출력값의 정확한 개수를 우리가 미리 알지 못한다는 점이다. 그런데 이 숫자를 첫 번째 완전연결층 생성자에게 넘겨줘야 한다. 한 가지 해결책은 이 숫자를 하드코딩하는 것이다(84×84 입력이면 합성곱층의 출력이 3,136개 값을 가진다) — 하지만 이는 입력 모양이 바뀌면 코드의 견고성이 떨어지므로 최선의 방법은 아니다. 더 나은 해법은 **가짜 입력 텐서를 합성곱 부분에 실제로 통과시켜, 런타임에 그 결과의 차원을 얻는 것**이다. 이 호출은 모델 생성 시 딱 한 번만 이루어지므로 빠르며, 코드를 범용적으로 만들어준다.

모델의 마지막 조각은 `forward()` 함수로, 4차원 입력 텐서를 받는다. 첫 번째 차원은 배치 크기이고, 두 번째는 색상 채널(여기서는 연속 프레임 스택)이며, 세 번째와 네 번째는 이미지 차원이다.

```python
def forward(self, x: torch.ByteTensor):
    # scale on GPU
    xx = x / 255.0
    return self.fc(self.conv(xx))
```

여기서는 네트워크를 적용하기 전에 입력 데이터의 스케일 조정과 타입 변환을 수행하는데, 여기에는 약간의 설명이 필요하다.

아타리 이미지의 각 픽셀은 0~255 값을 갖는 부호 없는 바이트(unsigned byte)로 표현된다. 이는 두 가지 측면에서 편리하다. 리플레이 버퍼가 수천 개의 관측을 유지하므로 메모리 사용 관점에서 관측을 최대한 작게 유지해야 하는데, 학습 중에는 이 관측들을 GPU 메모리로 옮겨 그래디언트를 계산하고 네트워크 파라미터를 갱신해야 한다. 메인 메모리와 GPU 사이의 대역폭은 제한된 자원이므로, 관측을 최대한 작게 유지하는 것이 합리적이다.

그래서 관측을 `dtype=uint8`인 numpy 배열로 유지하고, 네트워크로 들어가는 입력 텐서는 `ByteTensor`다. 하지만 `Conv2d` 층은 float 텐서를 입력으로 기대하므로, 입력 텐서를 255.0으로 나누어 0~1 범위로 스케일 조정하면서 타입 변환까지 함께 수행한다. 입력 바이트 텐서가 이미 GPU 메모리 안에 있는 상태이므로 이 연산은 빠르다. 이후 우리 네트워크의 두 부분(합성곱, 완전연결)을 스케일된 텐서에 순서대로 적용한다.

### 9.3 학습 (Training)

세 번째 모듈에는 경험 리플레이 버퍼, 에이전트, 손실 함수 계산, 그리고 학습 루프 자체가 담겨 있다. 코드로 들어가기 전에, 학습 하이퍼파라미터에 대해 짚어야 할 것이 있다.

DeepMind의 *Nature* 논문에는 모델을 **모든** 49개 아타리 게임에서 학습시키는 데 쓰인 하이퍼파라미터가 표로 정리되어 있다. DeepMind는 이 파라미터를 모든 게임에서 동일하게 유지했는데(단, 게임마다 개별 모델을 학습시켰다), 이는 다양한 복잡도·행동 공간·보상 구조를 가진 많은 게임을 하나의 모델 구조와 하이퍼파라미터로 풀 수 있을 만큼 이 방법이 견고하다는 것을 보여주려는 의도였다. 하지만 우리 목표는 훨씬 소박하다 — Pong 게임 하나만 풀면 된다.

Pong은 다른 아타리 테스트 게임들에 비해 꽤 단순하고 직관적이라, 논문의 하이퍼파라미터는 우리 과제에 과한 사양이다. 예를 들어, 49개 게임 모두에서 최고 성능을 얻기 위해 DeepMind는 100만 개의 관측을 담는 리플레이 버퍼를 썼는데, 이를 저장하려면 약 20GB의 RAM과 이를 채우기 위한 많은 환경 샘플이 필요하다.

에서 사용한 엡실론 감소 스케줄도 Pong 하나만 풀기에는 최선이 아니다. 학습에서 DeepMind는 환경에서 얻은 첫 백만 프레임 동안 엡실론을 1.0에서 0.1까지 선형으로 감소시켰다. 하지만 저자의 실험에 따르면, Pong에서는 첫 15만 프레임에 걸쳐 엡실론을 감소시킨 뒤 그 값을 유지하는 것으로 충분하다. 리플레이 버퍼도 훨씬 작아도 된다 — 1만 개의 전이면 충분하다.

다음 예제에서는 저자의 파라미터를 사용한다. 논문의 파라미터와는 다르지만, Pong을 약 10배 빠르게 풀 수 있게 해준다. GeForce GTX 1080 Ti에서 다음 버전은 약 50분 만에 평균 점수 19.0으로 수렴하지만, DeepMind의 하이퍼파라미터로는 최소 하루가 걸린다.

> [!note] 이 속도 향상의 대가
> 이런 속도 향상은 특정 환경 하나에 맞춘 미세 조정을 포함하며, 다른 게임에서는 수렴이 깨질 수 있다. 다른 아타리 세트의 옵션과 게임들을 자유롭게 실험해 보라.

먼저 필요한 모듈을 임포트한다.

```python
import gymnasium as gym
from lib import dqn_model
from lib import wrappers

from dataclasses import dataclass
import argparse
import time
import numpy as np
import collections
import typing as tt

import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.tensorboard.writer import SummaryWriter
```

이제 하이퍼파라미터를 정의한다.

```python
DEFAULT_ENV_NAME = "PongNoFrameskip-v4"
MEAN_REWARD_BOUND = 19
```

이 두 값은 학습할 기본 환경과, 최근 100개 에피소드에 대한 학습 종료 기준(보상 경계)을 정한다. 원하면 명령줄 인자 `--env`로 환경 이름을 다시 지정할 수 있다.

```python
GAMMA = 0.99
BATCH_SIZE = 32
REPLAY_SIZE = 10000
LEARNING_RATE = 1e-4
SYNC_TARGET_FRAMES = 1000
REPLAY_START_SIZE = 10000
```

앞의 파라미터들이 정의하는 값은 다음과 같다.

- **GAMMA**: 벨만 근사에 쓰이는 할인율 γ 값.
- **BATCH_SIZE**: 리플레이 버퍼에서 샘플링하는 배치 크기.
- **REPLAY_SIZE**: 버퍼의 최대 용량.
- **REPLAY_START_SIZE**: 학습을 시작하기 전, 리플레이 버퍼를 채우기 위해 기다리는 프레임 수.
- **LEARNING_RATE**: 이 예제에서 사용하는 Adam 옵티마이저의 학습률.
- **SYNC_TARGET_FRAMES**: 학습 모델의 가중치를 타깃 모델로 동기화하는 빈도. 벨만 근사에서 다음 상태의 값을 얻는 데 타깃 모델이 사용된다.

```python
EPSILON_DECAY_LAST_FRAME = 150000
EPSILON_START = 1.0
EPSILON_FINAL = 0.01
```

마지막 하이퍼파라미터 묶음은 엡실론 감소 스케줄과 관련이 있다. 적절한 탐험을 달성하기 위해, 학습 초기에는 $\epsilon = 1.0$으로 시작해 모든 행동이 무작위로 선택되게 한다. 그다음, 첫 15만 프레임 동안 $\epsilon$을 선형으로 0.01까지 감소시키는데, 이는 스텝의 1%가 무작위 행동으로 선택된다는 뜻이다. 원 DeepMind 논문에서도 비슷한 방식을 썼지만, 감소 구간이 약 10배 더 길었다(백만 프레임 후에야 $\epsilon=0.01$에 도달).

이제 리플레이 버퍼에 항목을 저장하는 데 쓰이는 타입 별칭과 `Experience` 데이터클래스를 정의한다. 현재 상태, 취해진 행동, 얻어진 보상, 종료 또는 트렁케이션 플래그, 새 상태를 담는다.

```python
State = np.ndarray
Action = int
BatchTensors = tt.Tuple[
    torch.ByteTensor,           # current state
    torch.LongTensor,           # actions
    torch.Tensor,               # rewards
    torch.BoolTensor,           # done || trunc
    torch.ByteTensor            # next state
]

@dataclass
class Experience:
    state: State
    action: Action
    reward: float
    done_trunc: bool
    new_state: State
```

다음 코드 블록은 환경에서 얻은 전이를 보관하는 목적을 가진 경험 리플레이 버퍼를 정의한다.

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

환경에서 한 스텝을 수행할 때마다, 우리는 그 전이를 버퍼에 밀어 넣고 고정된 개수(우리 경우 1만 개)의 스텝만 유지한다. 학습을 위해서는, 환경 내 연속된 스텝 사이의 상관관계를 끊기 위해 버퍼에서 배치를 무작위로 샘플링한다. 자세한 원리는 [[경험 재생 Experience Replay]]를 참고하라.

경험 리플레이 버퍼 코드 대부분은 매우 단순하다 — 기본적으로 버퍼 안에 주어진 개수의 항목을 유지할 수 있는 `deque` 클래스의 기능을 활용한다. `sample()` 메서드에서는 무작위 인덱스 목록을 만들고, 이를 재조합해 텐서로 변환할 `Experience` 항목들의 리스트를 반환한다.

다음으로 필요한 클래스는 `Agent`로, 환경과 상호작용하며 그 결과를 방금 본 경험 리플레이 버퍼에 저장한다.

```python
class Agent:
    def __init__(self, env: gym.Env, exp_buffer: ExperienceBuffer):
        self.env = env
        self.exp_buffer = exp_buffer
        self.state: tt.Optional[np.ndarray] = None
        self._reset()

    def _reset(self):
        self.state, _ = env.reset()
        self.total_reward = 0.0
```

에이전트를 초기화하는 동안, 환경과 경험 리플레이 버퍼에 대한 참조를 저장해야 하며, 현재 관측과 지금까지 누적된 총 보상을 추적한다.

에이전트의 주 메서드는 환경에서 한 스텝을 수행하고 그 결과를 버퍼에 저장하는 것이다. 이를 위해 먼저 행동을 선택해야 한다.

```python
@torch.no_grad()
def play_step(self, net: dqn_model.DQN, device: torch.device,
              epsilon: float = 0.0) -> tt.Optional[float]:
    done_reward = None

    if np.random.random() < epsilon:
        action = env.action_space.sample()
    else:
        state_v = torch.as_tensor(self.state).to(device)
        state_v.unsqueeze_(0)
        q_vals_v = net(state_v)
        _, act_v = torch.max(q_vals_v, dim=1)
        action = int(act_v.item())
```

확률 엡실론(인자로 전달됨)으로 무작위 행동을 선택하고, 그렇지 않으면 모델을 이용해 가능한 모든 행동에 대한 Q값을 얻어 최선의 행동을 선택한다. 이 메서드에서는 어차피 필요 없으므로 메서드 전체에서 PyTorch의 `no_grad()` 데코레이터를 이용해 그래디언트 추적을 비활성화한다. 자세한 원리는 [[엡실론-그리디 탐험]]을 참고하라.

행동이 선택되면, 이를 환경에 전달해 다음 관측과 보상을 얻고, 이 데이터를 경험 버퍼에 저장한 뒤, 에피소드 종료 상황을 처리한다.

```python
    new_state, reward, is_done, is_tr, _ = self.env.step(action)
    self.total_reward += reward

    exp = Experience(
        state=self.state, action=action, reward=float(reward),
        done_trunc=is_done or is_tr, new_state=new_state
    )
    self.exp_buffer.append(exp)
    self.state = new_state
    if is_done or is_tr:
        done_reward = self.total_reward
        self._reset()
    return done_reward
```

이 함수의 결과는, 이 스텝으로 에피소드의 끝에 도달했다면 누적된 총 보상이고, 그렇지 않으면 `None`이다.

함수 `batch_to_tensors`는 `Experience` 객체들의 배치를 받아, 상태·행동·보상·종료 플래그·새 상태를 해당하는 타입의 PyTorch 텐서로 재조합한 튜플을 반환한다.

```python
def batch_to_tensors(batch: tt.List[Experience], device: torch.device) -> BatchTensors:
    states, actions, rewards, dones, new_state = [], [], [], [], []
    for e in batch:
        states.append(e.state)
        actions.append(e.action)
        rewards.append(e.reward)
        dones.append(e.done_trunc)
        new_state.append(e.new_state)
    states_t = torch.as_tensor(np.asarray(states))
    actions_t = torch.LongTensor(actions)
    rewards_t = torch.FloatTensor(rewards)
    dones_t = torch.BoolTensor(dones)
    new_states_t = torch.as_tensor(np.asarray(new_state))
    return states_t.to(device), actions_t.to(device), rewards_t.to(device), \
        dones_t.to(device),  new_states_t.to(device)
```

상태를 다룰 때는 (`np.asarray()` 함수를 이용해) **메모리 복사를 피하려고** 노력한다. 이는 중요한데, 아타리 관측은 크고(4개 프레임마다 84×84 바이트), 배치 하나에 그런 객체가 32개나 있기 때문이다. 이 최적화가 없다면 성능이 약 20배 떨어진다.

이제 학습 모듈의 마지막 함수 — 샘플링된 배치의 손실을 계산하는 함수 — 를 볼 차례다. 이 함수는 GPU 병렬성을 최대한 활용하도록 배치 샘플 전체를 벡터 연산으로 처리하는 형태로 작성되어 있으며, 이는 배치에 대한 명시적인 반복문과 비교했을 때 이해하기는 더 어렵지만, 이 최적화는 그만한 값어치를 한다 — 병렬 버전이 명시적 반복문보다 두 배 넘게 빠르다.

상기하자면, 계산해야 할 손실식은 다음과 같다.

$$\mathcal{L} = \left(Q(s,a) - \left(r + \gamma \max_{a' \in A} \hat{Q}(s',a')\right)\right)^2$$

에피소드의 끝이 아닌 스텝에는 앞의 식을, 마지막 스텝에는 다음 식을 사용한다.

$$\mathcal{L} = (Q(s,a) - r)^2$$

```python
def calc_loss(batch: tt.List[Experience], net: dqn_model.DQN, tgt_net: dqn_model.DQN,
              device: torch.device) -> torch.Tensor:
    states_t, actions_t, rewards_t, dones_t, new_states_t = batch_to_tensors(batch,
        device)
```

인자로 배치, 학습 대상인 네트워크, 그리고 주기적으로 학습된 네트워크와 동기화되는 타깃 네트워크를 전달받는다. 함수 시작 부분에서 `batch_to_tensors`를 호출해 배치를 개별 텐서 변수들로 재조합한다.

다음 줄은 다소 까다롭다.

```python
    state_action_values = net(states_t).gather(
        1, actions_t.unsqueeze(-1)
    ).squeeze(-1)
```

여기서는 관측을 첫 번째 모델(net)에 전달하고, `gather()` 텐서 연산을 사용해 실제로 취해진 행동에 해당하는 특정 Q값들만 추출한다. `gather()` 호출의 첫 번째 인자는 gather를 수행할 차원 인덱스(여기서는 1, 즉 행동에 해당)다.

두 번째 인자는 선택할 원소들의 인덱스로 이루어진 텐서다. 추가로 붙은 `unsqueeze()`와 `squeeze()` 호출은 각각 `gather()` 함수에 필요한 인덱스 인자를 계산하고, 우리가 만들었던 여분의 차원을 제거하기 위해 필요하다(인덱스는 우리가 처리 중인 데이터와 같은 개수의 차원을 가져야 한다). 상세한 원리와 그림은 [[텐서 gather 연산]]을 참고하라.

![[fig_6_3.png]]
*그림 6.3 — DQN 손실 계산 중 텐서 변환 과정. `gather()`가 배치의 각 샘플마다 실제 선택된 행동의 Q값만 뽑아낸다.*

`gather()`가 텐서에 적용되었을 때 그 결과는 **미분 가능한 연산**이며, 최종 손실값에 대한 모든 그래디언트를 유지한다는 점을 기억해 두자.

다음으로, 그래디언트 계산을 비활성화하고(작은 속도 향상을 얻는다), 타깃 네트워크를 다음 상태 관측에 적용해, 같은 행동 차원(1)을 따라 최대 Q값을 계산한다.

```python
    with torch.no_grad():
        next_state_values = tgt_net(new_states_t).max(1)[0]
```

`max()` 함수는 최댓값과 그 값들의 인덱스(즉 max와 argmax를 둘 다) 반환하는데, 이는 매우 편리하다. 하지만 여기서는 값에만 관심이 있으므로 결과의 첫 번째 항목(max 값)만 취한다.

다음 줄은 다음과 같다.

```python
        next_state_values[dones_t] = 0.0
```

여기서는 한 가지 단순하지만 매우 중요한 변환을 수행한다. 배치 안의 전이가 에피소드의 마지막 스텝이라면, 우리가 갖고 있는 행동의 값에는 다음 상태에 대한 할인된 보상이 없다. 다음 상태로부터 얻을 보상 자체가 없기 때문이다. 사소해 보일 수 있지만, 실전에서는 매우 중요하다 — 이걸 빼먹으면 학습이 수렴하지 않는다(저자도 이 상황을 디버깅하느라 몇 시간을 허비했다고 밝히고 있다).

다음 줄에서는, 다음 상태들의 Q 근사를 계산하는 데 쓰인 NN으로 그래디언트가 흘러 들어가는 것을 막기 위해 계산 그래프에서 값을 분리(detach)한다.

```python
        next_state_values = next_state_values.detach()
```

이는 중요한데, 이게 없으면 손실의 역전파가 현재 상태에 대한 예측값과 다음 상태에 대한 예측값 **둘 다**에 영향을 주기 시작하기 때문이다. 하지만 우리는 다음 상태에 대한 예측을 건드리고 싶지 않다 — 이 값은 벨만 방정식에서 참조 Q값을 계산하는 데 쓰이기 때문이다. 이 그래프의 가지로 그래디언트가 흘러 들어가는 것을 막기 위해, 텐서의 `detach()` 메서드를 사용하는데, 이는 계산 이력과의 연결 없이 텐서를 반환한다. 이 부분의 자세한 원리는 [[타깃 네트워크와 부트스트래핑]]을 참고하라.

마지막으로 벨만 근사값과 평균 제곱 오차 손실을 계산한다.

```python
    expected_state_action_values = next_state_values * GAMMA + rewards_t
    return nn.MSELoss()(state_action_values, expected_state_action_values)
```

손실 함수 계산 코드의 전체 그림을 파악하기 위해, 이 함수를 통째로 다시 보자.

```python
def calc_loss(batch: tt.List[Experience], net: dqn_model.DQN, tgt_net: dqn_model.DQN,
              device: torch.device) -> torch.Tensor:
    states_t, actions_t, rewards_t, dones_t, new_states_t = batch_to_tensors(batch,
        device)

    state_action_values = net(states_t).gather(
        1, actions_t.unsqueeze(-1)
    ).squeeze(-1)
    with torch.no_grad():
        next_state_values = tgt_net(new_states_t).max(1)[0]
        next_state_values[dones_t] = 0.0
        next_state_values = next_state_values.detach()

    expected_state_action_values = next_state_values * GAMMA + rewards_t
    return nn.MSELoss()(state_action_values, expected_state_action_values)
```

이것으로 손실 함수 계산이 끝났다. 이제 남은 코드는 학습 루프다. 먼저 명령줄 인자 파서를 만든다.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default="cpu", help="Device name, default=cpu")
    parser.add_argument("--env", default=DEFAULT_ENV_NAME,
                        help="Name of the environment, default=" + DEFAULT_ENV_NAME)
    args = parser.parse_args()
    device = torch.device(args.dev)
```

이 스크립트는 계산에 사용할 디바이스를 지정할 수 있게 해 주고, 기본값과 다른 환경으로도 학습할 수 있게 해 준다.

여기서 환경을 만든다.

```python
    env = wrappers.make_env(args.env)
    net = dqn_model.DQN(env.observation_space.shape, env.action_space.n).to(device)
    tgt_net = dqn_model.DQN(env.observation_space.shape, env.action_space.n).to(device)
```

우리 환경은 필요한 모든 래퍼가 적용된 상태이고, 우리가 학습시킬 NN, 그리고 같은 구조를 가진 타깃 네트워크가 준비되었다. 이 둘은 처음에는 서로 다른 무작위 가중치로 초기화되지만, 1k 프레임마다(대략 Pong 한 에피소드에 해당) 동기화될 것이므로 큰 문제가 되지 않는다.

그다음, 필요한 크기의 경험 리플레이 버퍼를 만들어 에이전트에 전달한다.

```python
    writer = SummaryWriter(comment="-" + args.env)
    print(net)
    buffer = ExperienceBuffer(REPLAY_SIZE)
    agent = Agent(env, buffer)
    epsilon = EPSILON_START
```

엡실론은 초기에 1.0으로 초기화되지만, 반복마다 감소한다.

학습 루프 시작 전, 마지막으로 할 일들이 있다.

```python
    optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE)
    total_rewards = []
    frame_idx = 0
    ts_frame = 0
    ts = time.time()
    best_m_reward = None
```

옵티마이저, 전체 에피소드 보상을 담을 버퍼, 프레임 개수 카운터, 속도 측정을 위한 여러 변수, 그리고 지금까지 달성한 최고 평균 보상을 만든다. 평균 보상이 기록을 갱신할 때마다 모델을 파일에 저장할 것이다.

학습 루프의 시작 부분에서는 완료된 반복 횟수를 세고, 스케줄에 따라 엡실론을 감소시킨다.

```python
    while True:
        frame_idx += 1
        epsilon = max(EPSILON_FINAL, EPSILON_START - frame_idx /
            EPSILON_DECAY_LAST_FRAME)
```

엡실론은 주어진 프레임 수(`EPSILON_DECAY_LAST_FRAME`=150k) 동안 선형으로 하락한 뒤, `EPSILON_FINAL`=0.01 수준으로 유지된다. 자세한 원리는 [[엡실론-그리디 탐험]]을 참고하라.

이 코드 블록에서는, 에이전트에게 현재 네트워크와 엡실론 값을 사용해 환경에서 한 스텝을 수행하도록 요청한다.

```python
        reward = agent.play_step(net, device, epsilon)
        if reward is not None:
            total_rewards.append(reward)
            speed = (frame_idx - ts_frame) / (time.time() - ts)
            ts_frame = frame_idx
            ts = time.time()
            m_reward = np.mean(total_rewards[-100:])
            print(f"{frame_idx}: done {len(total_rewards)} games, reward {m_reward:.3f}, "
                f"eps {epsilon:.2f}, speed {speed:.2f} f/s")
            writer.add_scalar("epsilon", epsilon, frame_idx)
            writer.add_scalar("speed", speed, frame_idx)
            writer.add_scalar("reward_100", m_reward, frame_idx)
            writer.add_scalar("reward", reward, frame_idx)
```

이 함수는 이 스텝이 에피소드의 마지막 스텝일 때만 float 값을 반환한다. 그런 경우, 진행 상황을 출력한다. 구체적으로는 콘솔과 TensorBoard 둘 다에 다음 값들을 계산하고 보여준다: 초당 처리된 프레임 수(속도), 플레이한 에피소드 수, 최근 100개 에피소드에 대한 평균 보상, 현재 엡실론 값.

최근 100개 에피소드에 대한 평균 보상이 최댓값을 갱신할 때마다, 이를 보고하고 모델 파라미터를 저장한다.

```python
            if best_m_reward is None or best_m_reward < m_reward:
                torch.save(net.state_dict(), args.env + "-best_%.0f.dat" % m_reward)
                if best_m_reward is not None:
                    print(f"Best reward updated {best_m_reward:.3f} -> {m_reward:.3f}")
                best_m_reward = m_reward
            if m_reward > MEAN_REWARD_BOUND:
                print("Solved in %d frames!" % frame_idx)
                break
```

평균 보상이 지정된 경계를 넘어서면, 학습을 멈춘다. Pong에서 이 경계는 19.0인데, 이는 21판 중 19판 넘게 이겼다는 뜻이다.

여기서는 버퍼가 학습을 시작할 만큼 충분히 큰지 확인한다.

```python
        if len(buffer) < REPLAY_START_SIZE:
            continue
        if frame_idx % SYNC_TARGET_FRAMES == 0:
            tgt_net.load_state_dict(net.state_dict())
```

먼저 충분한 데이터가 쌓일 때까지 기다려야 하는데, 우리 경우 1만 개의 전이다. 다음 조건은 `SYNC_TARGET_FRAMES`(기본값 1k)마다 우리 메인 네트워크의 파라미터를 타깃 네트워크로 동기화한다. 자세한 원리는 [[타깃 네트워크와 부트스트래핑]]을 참고하라.

학습 루프의 마지막 조각은 매우 단순하지만, 실행에 가장 많은 시간이 걸린다.

```python
        optimizer.zero_grad()
        batch = buffer.sample(BATCH_SIZE)
        loss_t = calc_loss(batch, net, tgt_net, device)
        loss_t.backward()
        optimizer.step()
```

여기서는 그래디언트를 0으로 초기화하고, 경험 리플레이 버퍼에서 데이터 배치를 샘플링하고, 손실을 계산한 다음, 손실을 최소화하는 최적화 스텝을 수행한다.

### 9.4 실행과 성능

이 예제는 리소스 소모가 크다. Pong에서는 평균 보상 17(80% 이상의 승률을 뜻함)에 도달하는 데 약 40만 프레임이 필요하다. 17에서 19까지 가는 데도 비슷한 프레임 수가 필요한데, 학습 진행이 포화 상태에 가까워지면서 모델이 정책을 "다듬는" 것이 점점 어려워지기 때문이다. 그래서 평균적으로 완전히 학습시키려면 백만 게임 프레임이 필요하다. GTX 1080Ti에서는 초당 약 250프레임의 속도가 나오는데, 이는 약 1시간의 학습에 해당한다. CPU(i5-7600k)에서는 훨씬 느려서, 초당 약 40프레임이며 약 7시간이 걸린다. 이는 상대적으로 풀기 쉬운 Pong 기준이며, 다른 게임들은 수억 프레임과 100배 더 큰 경험 리플레이 버퍼가 필요할 수 있다.

![[fig_6_4.png]]
*그림 6.4 — 최근 100개 에피소드에 대한 평균 보상의 학습 과정. 초반에는 -20 근처(거의 매번 패배)에서 시작해, 약 0.3~0.5시간 지점에서 가파르게 상승하며 결국 19 근처까지 도달한다.*

학습 프로세스의 콘솔 출력(시작 부분)을 살펴보자.

```
Chapter06$ ./02_dqn_pong.py --dev cuda
A.L.E: Arcade Learning Environment (version 0.8.1+53f58b7)
[Powered by Stella]
DQN(
  (conv): Sequential(
    (0): Conv2d(4, 32, kernel_size=(8, 8), stride=(4, 4))
    (1): ReLU()
    (2): Conv2d(32, 64, kernel_size=(4, 4), stride=(2, 2))
    (3): ReLU()
    (4): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1))
    (5): ReLU()
    (6): Flatten(start_dim=1, end_dim=-1)
  )
  (fc): Sequential(
    (0): Linear(in_features=3136, out_features=512, bias=True)
    (1): ReLU()
    (2): Linear(in_features=512, out_features=6, bias=True)
  )
)
940: done 1 games, reward -21.000, eps 0.99, speed 1214.95 f/s
1946: done 2 games, reward -20.000, eps 0.99, speed 1420.09 f/s
Best reward updated -21.000 -> -20.000
```

첫 1만 스텝 동안은 학습을 전혀 하지 않기 때문에 속도가 매우 빠르다(학습이 코드 안에서 가장 비용이 큰 연산이다). 1만 스텝이 지나면 학습 배치를 샘플링하기 시작하고, 성능이 좀 더 현실적인 수치로 떨어진다. 학습 중에는 엡실론이 감소하기 때문에 성능도 조금씩 더 떨어진다 — 엡실론이 클 때는 행동이 무작위로 선택되지만, 엡실론이 0에 가까워질수록 행동 선택을 위해 Q값을 얻는 추론(inference)을 수행해야 하므로 여기에도 비용이 든다.

수십 판이 더 지나면, 우리 DQN이 21판 중 1~2판을 이기는 법을 알아내기 시작하고, 평균 보상이 오르기 시작한다(보통 엡실론이 0.5 근처일 때 시작된다).

```
66024: done 68 games, reward -20.162, eps 0.56, speed 260.89 f/s
...
84841: done 82 games, reward -19.878, eps 0.43, speed 254.80 f/s
```

훨씬 더 많은 게임이 지난 후, 우리 DQN은 마침내 (그다지 정교하지 않은) 내장 Pong AI 상대를 압도할 수 있게 된다.

```
737860: done 371 games, reward 18.540, eps 0.01, speed 225.22 f/s
...
755958: done 380 games, reward 19.030, eps 0.01, speed 228.71 f/s
Best reward updated 18.920 -> 19.030
Solved in 755958 frames!
```

> [!warning] 학습이 항상 매끄럽게 되지는 않는다
> 학습 과정의 무작위성 때문에, 실제 다이나믹스가 여기 나온 것과 다를 수 있다. 저자의 실험에 따르면, 드문 경우(대략 10번 중 1번)에는 학습이 전혀 수렴하지 않으며, 이는 -21이라는 보상이 오래도록 계속 이어지는 것처럼 보인다. 이는 딥러닝에서 흔한 상황이 아니지만(학습의 무작위성 때문에), RL에서는(환경과의 통신에 추가된 무작위성 때문에) 더 자주 나타날 수 있다. 만약 첫 10만~20만 반복 동안 긍정적인 다이나믹스가 전혀 보이지 않는다면, 다시 시작해야 한다.

### 9.5 실전에서 모델 사용하기

학습 과정은 전체 그림의 절반에 불과하다. 최종 목표는 모델을 학습시키는 것만이 아니라, 좋은 결과로 게임을 실제로 플레이하는 것이다. 학습 중에는 최근 100개 게임의 평균 최댓값을 갱신할 때마다, 모델을 `PongNoFrameskip-v4-best_<score>.dat` 파일에 저장한다. `Chapter06/03_dqn_play.py` 파일에는 이 모델 파일을 불러와 한 에피소드를 플레이하며 모델의 움직임을 보여주는 프로그램이 있다.

코드는 매우 단순하지만, 겨우 백만 개의 파라미터를 가진 몇 개의 행렬이 오직 픽셀만 관찰해서 초인적인 정확도로 Pong을 플레이할 수 있다는 사실은 마치 마법처럼 보일 수 있다.

먼저 익숙한 PyTorch와 Gym 모듈을 임포트한다.

```python
import gymnasium as gym
import argparse
import numpy as np

import typing as tt

import torch
from lib import wrappers
from lib import dqn_model

import collections

DEFAULT_ENV_NAME = "PongNoFrameskip-v4"
```

이 스크립트는 저장된 모델의 파일명을 받고, Gym 환경을 지정할 수 있게 해 준다(당연히 모델과 환경은 서로 일치해야 한다).

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", required=True, help="Model file to load")
    parser.add_argument("-e", "--env", default=DEFAULT_ENV_NAME,
                        help="Environment name to use, default=" + DEFAULT_ENV_NAME)
    parser.add_argument("-r", "--record", required=True, help="Directory for video")
    args = parser.parse_args()
```

추가로 `-r` 옵션에 아직 존재하지 않는 디렉터리 이름을 전달해야 하며, 이 디렉터리는 게임 영상을 저장하는 데 쓰인다.

이어지는 코드도 그리 복잡하지 않다.

```python
    env = wrappers.make_env(args.env, render_mode="rgb_array")
    env = gym.wrappers.RecordVideo(env, video_folder=args.record)
    net = dqn_model.DQN(env.observation_space.shape, env.action_space.n)
    state = torch.load(args.model, map_location=lambda stg, _: stg)
    net.load_state_dict(state)

    state, _ = env.reset()
    total_reward = 0.0
    c: tt.Dict[int, int] = collections.Counter()
```

환경을 만들고, `RecordVideo` 래퍼로 감싼 뒤, 모델을 만들고, 인자로 넘어온 파일에서 가중치를 불러온다. `torch.load()` 함수에 전달되는 `map_location` 인자는, 불러온 텐서의 위치를 GPU에서 CPU로 다시 매핑하는 데 필요하다. 기본적으로 torch는 저장될 당시와 같은 디바이스에 텐서를 불러오려 시도하는데, 만약 학습에 쓴 머신(GPU 있음)에서 노트북(GPU 없음)으로 모델을 복사해왔다면 위치를 다시 매핑해야 한다.

이 예제에서는 GPU를 전혀 쓰지 않는데, 추론은 가속 없이도 충분히 빠르기 때문이다.

이는 학습 코드의 `Agent` 클래스의 `play_step()` 메서드와 거의 똑같지만, 엡실론-그리디 행동 선택이 빠져 있다.

```python
    while True:
        state_v = torch.tensor([state])
        q_vals = net(state_v).data.numpy()[0]
        action = int(np.argmax(q_vals))
        c[action] += 1
```

관측을 에이전트에 전달하고 가장 큰 값을 가진 행동을 선택하기만 하면 된다.

나머지 코드도 단순하다.

```python
        state, reward, is_done, is_tr, _ = env.step(action)
        total_reward += reward
        if is_done or is_tr:
            break
    print("Total reward: %.2f" % total_reward)
    print("Action counts:", c)
    env.close()
```

행동을 환경에 전달하고, 총 보상을 누적하며, 에피소드가 끝나면 루프를 멈춘다. 에피소드가 끝나면 총 보상과 에이전트가 각 행동을 실행한 횟수를 보여준다.

다음 유튜브 재생목록에서 여러 학습 단계의 게임 플레이 녹화를 확인할 수 있다: https://www.youtube.com/playlist?list=PLMVwuZENsfJklt4vCltrWq0KV9aEZ3ylu

---

## 10. 직접 시도해 볼 것들

이 챕터의 내용을 스스로 실험해 보고 싶다면, 다음 방향들을 시도해 보라. 시간이 꽤 걸릴 수 있고 다소 답답한 순간들도 있을 수 있지만, 이런 실험은 내용을 실전적으로 완전히 익히는 매우 효율적인 방법이다.

- 아타리 세트의 다른 게임(예: Breakout, Atlantis, River Raid)으로 시도해 보라. 하이퍼파라미터 조정이 필요할 수 있다.
- FrozenLake의 대안으로, 승객을 태워 목적지에 데려다주는 택시 운전기사를 모사한 또 다른 표 기반 환경인 Taxi가 있다.
- Pong의 하이퍼파라미터를 가지고 놀아보라. 더 빠르게 학습시킬 수 있을까? OpenAI는 비동기 어드밴티지 액터-크리틱(asynchronous advantage actor-critic, 이 책 3부의 주제) 방법으로 Pong을 30분 만에 풀 수 있다고 주장한다. DQN으로도 가능할지 모른다.
- DQN 학습 코드를 더 빠르게 만들 수 있는가? OpenAI Baselines 프로젝트는 GTX 1080Ti에서 TensorFlow로 350 FPS를 달성했다. 즉 PyTorch 코드도 최적화할 여지가 있어 보인다. 이 주제는 9장에서 다루지만, 그동안 스스로 실험해 봐도 좋다.
- 녹화 영상을 보면, 평균 점수가 0 근처인 모델이 10~19점 사이인 모델보다 더 잘 플레이하는 것처럼 보일 수도 있다. 실제로 특정 게임 상황에 과적합된 결과일 수 있다 — 이를 고칠 수 있을까? 생성적 적대 신경망(GAN) 스타일로 한 모델이 다른 모델과 겨루게 만드는 접근이 가능할지도 모른다.
- 평균 점수 21을 받는 "얼티밋 퐁 도미네이터" 모델을 만들 수 있을까? 그리 어렵지 않을 것이다 — 학습률 감소가 시도해 볼 만한 뻔한 방법이다.

---

## 요약

이 챕터에서는 새롭고 복잡한 내용을 많이 다루었다. 대규모 관측 공간을 가진 환경에서 가치 반복이 겪는 한계를 확인했고, 이를 **Q-러닝**으로 극복하는 방법을 살펴보았다. FrozenLake 환경에서 Q-러닝 알고리즘을 확인했고, NN으로 Q값을 근사하는 데서 생기는 추가적인 복잡함들을 논의했다.

DQN의 학습 안정성과 수렴성을 높이는 여러 트릭 — **경험 리플레이 버퍼, 타깃 네트워크, 프레임 스태킹** — 을 다루었다. 마지막으로 이 확장 기법들을 하나의 DQN 구현으로 결합해, 아타리 게임 세트의 Pong 환경을 풀어냈다.

다음 챕터에서는 고수준 RL 라이브러리를 잠깐 살펴본 다음, 2015년 이후 연구자들이 DQN의 수렴과 품질을 개선하기 위해 발견한 여러 트릭을 다룬다. 이 트릭들을 조합하면 (새로 추가된) 54개 아타리 게임 대부분에서 최신(state-of-the-art) 결과를 낼 수 있다. 이 트릭 모음은 2017년에 발표되었으며, 우리는 이를 분석하고 모두 재구현해 볼 것이다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[합성곱 신경망 CNN]]
- [[엡실론-그리디 탐험]]
- [[경험 재생 Experience Replay]]
- [[타깃 네트워크와 부트스트래핑]]
- [[프레임 스태킹과 아타리 전처리]]
- [[텐서 gather 연산]]
- [[IID 독립항등분포]]
- [[Wrapper 래퍼 패턴]]
- [[할인율 감마와 등비급수]]
- [[손실함수의 종류]]
- [[옵티마이저와 경사하강법 변형]]
- [[활성화함수]]

## 한눈에 보는 개념 지도

| 개념 | 기호/코드 | 한 줄 뜻 |
|---|---|---|
| Q값 | $Q(s,a)$ | 상태 s에서 행동 a를 했을 때 기대되는 누적 보상 |
| 표 기반 Q-러닝 | `defaultdict(float)` | 방문한 (상태,행동)만 표에 기록해 값 근사 |
| DQN | `class DQN(nn.Module)` | 신경망으로 $Q(s,a)$를 근사 |
| 엡실론-그리디 | $\epsilon$ | 확률 ε로 무작위, 1-ε로 최선의 행동 |
| 경험 리플레이 버퍼 | `ExperienceBuffer` | 과거 경험을 모아두고 무작위로 샘플링해 학습 |
| 타깃 네트워크 | `tgt_net` | 목표값 계산 전용, 주기적으로만 동기화되는 복사본 |
| 부트스트래핑 | — | 다음 상태의 값으로 지금 상태의 값을 갱신하는 재귀적 구조 |
| 프레임 스태킹 | `BufferWrapper` | 최근 k개 프레임을 겹쳐 속도·방향 정보 제공 |
| 손실 함수 | $\mathcal{L}=(Q(s,a)-y)^2$ | 예측 Q값과 목표값의 평균 제곱 오차 |
| gather 연산 | `.gather(1, actions.unsqueeze(-1))` | 배치의 각 행에서 실제 선택된 행동의 Q값만 추출 |
