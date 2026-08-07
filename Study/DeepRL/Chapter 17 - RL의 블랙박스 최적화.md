---
title: "Chapter 17 — RL의 블랙박스 최적화 (Black-Box Optimizations in RL)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 17
tags: [DeepRL, 강화학습, 블랙박스최적화, 진화전략, 유전알고리즘, ES, GA]
---

# Chapter 17 · RL의 블랙박스 최적화

> [!abstract] 이 챕터를 한 문장으로
> **그래디언트(경사)를 아예 계산하지 않고도** 좋은 정책을 찾을 수 있다 — **진화 전략(ES)** 은 파라미터에 무작위 노이즈를 뿌려 점수가 오른 방향으로 옮기고, **유전 알고리즘(GA)** 은 성적 좋은 정책들만 살아남겨 자식을 낳게 한다. 두 방법 모두 "역전파가 필요 없다"는 이유 하나만으로 엄청나게 빠르게 병렬화되며, 놀랍게도 DQN·정책 경사법과 경쟁할 만한 성능을 낸다.

---

## 들어가며 — 관점을 완전히 바꿔보기

지금까지 이 책에서 배운 방법들은 전부 같은 뼈대를 공유했다. 신경망으로 정책이나 가치를 표현하고, 손실 함수를 정의하고, 그 손실을 **미분**해서 **그래디언트**를 구하고, 경사하강법(SGD)으로 파라미터를 조금씩 고쳐나간다. DQN도, [[정책 경사 Policy Gradient|정책 경사법]]도, [[액터-크리틱과 어드밴티지|액터-크리틱]]도 결국 이 틀 안에 있었다.

이 챕터에서는 완전히 다른 질문을 던진다. **"그래디언트를 아예 구하지 않고도 좋은 정책을 찾을 수 있을까?"** 답은 "그렇다"이며, 그런 방법들을 통틀어 **블랙박스 최적화(black-box optimization)** 라고 부른다. 이 방법들은 최소 10년은 된 오래된 아이디어지만, 최근 몇 년 사이 여러 연구에서 **대규모 RL 문제에도 통한다**는 것이 증명되었고, 상황에 따라서는 기존 방법보다 더 효율적이기까지 하다. 이 챕터에서는 두 대표 주자를 다룬다.

- **진화 전략(Evolution Strategies, ES)**
- **유전 알고리즘(Genetic Algorithms, GA)**

---

## 1. 블랙박스 방법이란 무엇인가

[[블랙박스 최적화와 적합도 함수|블랙박스 최적화]]는 최적화하려는 대상(여기서는 정책 $\pi(a\mid s)$)을 **"열어볼 수 없는 상자"** 로 취급하는 일반적인 접근법이다. 목적 함수가 미분 가능한지, 매끄러운지(smooth) 같은 가정을 **전혀 하지 않는다.** 유일하게 요구하는 것은 어떤 파라미터 후보를 넣었을 때 **얼마나 좋은지 알려주는 숫자 하나** — 바로 **적합도 함수(fitness function)** 를 계산할 수 있다는 것뿐이다.

### 가장 단순한 예 — 무작위 탐색 (Random Search)

이 계열에서 가장 단순한 방법은 **무작위 탐색**이다. 원리는 이렇다: 정책 $\pi(a\mid s)$를 무작위로 하나 뽑는다 → 그 적합도(예: 에피소드 누적 보상)를 재본다 → 기준에 맞을 만큼 좋으면 끝. 아니면 또 무작위로 뽑아서 반복한다.

너무 단순하고 순진해 보이지만, 그래서 오히려 블랙박스 방법의 핵심 아이디어를 보여주기 좋은 예시다. 몇 가지 변형을 가하면 이 단순한 접근도 DQN이나 정책 경사법과 **효율성·성능을 비교할 수 있는 수준**까지 발전한다 — 그것이 바로 뒤에 나올 ES와 GA다.

> [!important] 블랙박스 방법의 세 가지 매력
> - **최소 2배는 빠르다** — 역전파 단계를 아예 수행하지 않으므로.
> - **가정이 거의 없다** — 보상 함수가 매끄럽지 않거나 정책 안에 무작위 선택이 섞여 있어도 전통적 방법과 달리 문제없다.
> - **병렬화가 매우 쉽다** — 예컨대 무작위 탐색은 수천 개의 CPU·GPU에 아무 의존성 없이 나눠 돌릴 수 있다. 반면 DQN이나 정책 경사법은 그래디언트를 계속 누적하고 최신 정책을 모든 워커에 전파해야 해서 병렬성이 떨어진다.

> [!warning] 공짜 점심은 없다 — 낮은 표본 효율성
> 이 모든 장점의 대가는 보통 **표본 효율성(sample efficiency)의 저하**다. 특히 파라미터가 50만 개나 되는 신경망을 순수 무작위 탐색으로 찾으려 하면 성공 확률은 거의 0에 가깝다. 그래서 "무작위로 찔러보되, 점수가 좋은 방향을 기억해서 다음 시도에 반영하는" 더 영리한 방법이 필요하다.

---

## 2. 진화 전략 (Evolution Strategies, ES)

[[진화 전략 Evolution Strategies|ES]]는 블랙박스 최적화 방법군의 한 갈래로, **진화 과정에서 영감**을 얻었다. 핵심 규칙: 가장 성공적인 개체가 전체 탐색 방향에 가장 큰 영향을 미친다. ES 계열에는 여러 방법이 있는데, 이 챕터에서는 OpenAI 연구자 Salimans 등이 2017년 3월 발표한 논문 *Evolution strategies as a scalable alternative to reinforcement learning* [Sal+17]에서 다룬 접근을 따른다.

### 2.1 ES의 밑그림

매 반복(iteration)마다 다음을 한다.
1. 현재 정책 파라미터를 **무작위로 살짝 흔든다(perturbation)**.
2. 그 결과 정책의 **적합도 함수(=리턴)** 를 계산한다.
3. **상대적인 적합도 값에 비례해서** 정책 가중치를 조정한다.

Salimans 등이 실제로 쓴 구체적 방법은 **CMA-ES(covariance matrix adaptation evolution strategy)** 라 불린다. 뿌리는 노이즈는 평균 0, 항등 분산(identity variance)을 갖는 정규분포에서 뽑는다. 원래 정책의 가중치에 이 노이즈를 스케일해서 더한 파라미터로 적합도를 계산하고, 얻은 값에 비례해서 **원래 가중치에 (노이즈 × 적합도)를 더해** 적합도가 더 높아지는 방향으로 정책을 밀어낸다. 안정성을 위해, 서로 다른 무작위 노이즈로 얻은 배치(batch) 전체를 평균 내어 갱신한다.

### 2.2 알고리즘 (수식으로)

1. 학습률 $\alpha$, 노이즈 표준편차 $\sigma$, 초기 정책 파라미터 $\theta_0$을 초기화한다.
2. $t = 0, 1, \dots$ 마다:
   - (a) 파라미터와 같은 모양의 노이즈 배치를 샘플링한다: $\epsilon_1,\dots,\epsilon_n \sim \mathcal{N}(0, I)$
   - (b) 리턴을 계산한다: $F_i = F(\theta_t + \sigma\epsilon_i)$, $i = 1,\dots,n$
   - (c) 가중치를 갱신한다:
$$\theta_{t+1} \leftarrow \theta_t + \alpha \frac{1}{n\sigma}\sum_{i=1}^{n} F_i \epsilon_i$$

말로 풀면: *"파라미터 주변을 여러 방향($\epsilon_i$)으로 살짝 찔러보고, 점수가 좋았던 방향일수록 크게 가중치를 줘서 다 더한 다음, 그 방향으로 파라미터를 옮긴다."* 논문에는 이 핵심 알고리즘 외에도 실전 성능을 끌어올리는 여러 테크닉이 추가되어 있지만, 뼈대는 이 수식 하나다.

---

## 3. ES를 CartPole에 구현하기

책의 예제는 `Chapter17/01_cartpole_es.py`에 있다. 우리의 "실험용 초파리" CartPole 환경으로, 노이즈를 섞은 신경망의 적합도를 확인한다. 적합도 함수는 **에피소드의 무할인 누적 보상**이다.

### 3.1 임포트와 하이퍼파라미터

```python
import gymnasium as gym
import time
import numpy as np
import typing as tt

import torch
import torch.nn as nn

from torch.utils.tensorboard.writer import SummaryWriter
```

여기서 눈여겨볼 점: **PyTorch 옵티마이저를 쓰지 않는다.** 역전파를 전혀 수행하지 않기 때문이다. 사실 PyTorch 없이 NumPy만으로도 구현할 수 있지만, 신경망의 순전파(forward pass)와 출력 계산을 편하게 하려고 PyTorch를 쓴다.

```python
MAX_BATCH_EPISODES = 100
MAX_BATCH_STEPS = 10000
NOISE_STD = 0.001
LEARNING_RATE = 0.001

TNoise = tt.List[torch.Tensor]
```

- `MAX_BATCH_EPISODES`, `MAX_BATCH_STEPS`: 학습에 쓸 에피소드·스텝 수의 상한.
- `NOISE_STD`: 가중치를 흔들 때 쓰는 노이즈의 표준편차 $\sigma$.
- `LEARNING_RATE`: 학습 스텝에서 가중치를 조정할 때 쓰는 계수 $\alpha$.
- `TNoise`: 파라미터별 노이즈 텐서 리스트를 가리키는 타입 별칭. 이후 코드에서 노이즈를 자주 다루므로 미리 이름을 붙여둔다.

### 3.2 신경망

```python
class Net(nn.Module):
    def __init__(self, obs_size: int, action_size: int):
        super(Net, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_size, 32),
            nn.ReLU(),
            nn.Linear(32, action_size),
            nn.Softmax(dim=1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
```

은닉층 하나짜리 아주 단순한 신경망으로, 관측(observation)을 받아 행동을 출력한다. 여기서 PyTorch NN 기능은 **순전파만 편하게 쓰려는 용도**이며, 원한다면 행렬 곱셈과 비선형 함수 적용으로 완전히 대체할 수 있다.

### 3.3 적합도 계산 — evaluate()

```python
def evaluate(env: gym.Env, net: Net) -> tt.Tuple[float, int]:
    obs, _ = env.reset()
    reward = 0.0
    steps = 0
    while True:
        obs_v = torch.FloatTensor(np.expand_dims(obs, 0))
        act_prob = net(obs_v)
        acts = act_prob.max(dim=1)[1]
        obs, r, done, is_tr, _ = env.step(acts.data.numpy()[0])
        reward += r
        steps += 1
        if done or is_tr:
            break
    return reward, steps
```

주어진 정책으로 에피소드 하나를 끝까지 진행하고, **총 보상과 스텝 수**를 반환한다. 총 보상이 곧 적합도 값으로 쓰인다. 스텝 수는 배치를 만드는 데 걸리는 시간을 제한하는 용도로 쓰인다. 행동 선택은 확률분포에서 샘플링하지 않고 `max(dim=1)`으로 **결정론적으로(argmax)** 고른다 — 어차피 파라미터에 노이즈를 더해서 탐험 효과를 이미 넣었으므로, 행동 선택 자체는 결정론적이어도 충분하기 때문이다.

### 3.4 노이즈 생성 — sample_noise()와 미러드 샘플링

```python
def sample_noise(net: Net) -> tt.Tuple[TNoise, TNoise]:
    pos = []
    neg = []
    for p in net.parameters():
        noise = np.random.normal(size=p.data.size())
        noise_t = torch.FloatTensor(noise)
        pos.append(noise_t)
        neg.append(-noise_t)
    return pos, neg
```

네트워크 파라미터와 같은 모양(shape), 평균 0·분산 1인 무작위 노이즈를 만든다. 함수는 노이즈 두 세트 — **양의 노이즈**와 **부호만 반대인 음의 노이즈**를 함께 반환한다. 이 기법을 **[[진화 전략 Evolution Strategies|미러드 샘플링(mirrored sampling)]]** 이라 부르며, 배치에서 이 둘을 독립적인 샘플처럼 함께 사용해 수렴 안정성을 높인다.

> [!warning] 왜 음의 노이즈도 필요한가
> 음의 노이즈 없이 양의 노이즈만 쓰면, 우연히 한쪽으로 치우친 노이즈들이 가중치를 계속 같은 방향으로만 밀어붙여 **수렴이 매우 불안정해진다.**

### 3.5 노이즈를 더해 평가하기 — eval_with_noise()

```python
def eval_with_noise(env: gym.Env, net: nn.Module, noise: TNoise, noise_std: float,
        get_max_action: bool = True, device: torch.device = torch.device("cpu")):
    old_params = net.state_dict()
    for p, p_n in zip(net.parameters(), noise):
        p.data += NOISE_STD * p_n
    r, s = evaluate(env, net)
    net.load_state_dict(old_params)
    return r, s
```

네트워크 파라미터에 노이즈를 실제로 더한 뒤 `evaluate()`를 호출해 보상과 스텝을 얻는다. 평가가 끝나면 `load_state_dict()`로 **원래 가중치를 복원**해서, 다음 노이즈 평가에 영향을 주지 않게 한다.

### 3.6 파라미터 갱신 — train_step()

가장 중심이 되는 함수로, 다음 갱신식을 그대로 구현한다.
$$\theta_{t+1} \leftarrow \theta_t + \alpha \frac{1}{n\sigma}\sum_{i=1}^{n} F_i \epsilon_i$$

```python
def train_step(net: Net, batch_noise: tt.List[TNoise], batch_reward: tt.List[float],
               writer: SummaryWriter, step_idx: int):
    weighted_noise = None
    norm_reward = np.array(batch_reward)
    norm_reward -= np.mean(norm_reward)
    s = np.std(norm_reward)
    if abs(s) > 1e-6:
        norm_reward /= s
```

먼저 배치의 보상을 **평균 0, 분산 1로 정규화**한다. 값의 스케일이 매번 들쭉날쭉하면 학습이 불안정해지기 때문에 이렇게 표준화해 안정성을 높인다.

```python
    for noise, reward in zip(batch_noise, norm_reward):
        if weighted_noise is None:
            weighted_noise = [reward * p_n for p_n in noise]
        else:
            for w_n, p_n in zip(weighted_noise, noise):
                w_n += reward * p_n
```

배치의 (노이즈, 보상) 쌍을 순회하며, **정규화된 보상을 가중치로 삼아 노이즈를 누적**한다. 파라미터별로 "보상 × 노이즈"를 다 더하는 것 — 위 수식의 $\sum_i F_i \epsilon_i$에 해당한다.

```python
    m_updates = []
    for p, p_update in zip(net.parameters(), weighted_noise):
        update = p_update / (len(batch_reward) * NOISE_STD)
        p.data += LEARNING_RATE * update
        m_updates.append(torch.norm(update))
    writer.add_scalar("update_l2", np.mean(m_updates), step_idx)
```

누적된 노이즈를 배치 크기 $n$과 노이즈 표준편차 $\sigma$로 나누어 정규화한 뒤, 학습률 $\alpha$를 곱해 실제 파라미터에 더한다. `update_l2`는 매 스텝의 업데이트 크기를 텐서보드에 기록해, 학습이 잘 진행되는지 모니터링하는 용도다.

> [!note] 이것은 사실 "그래디언트 상승"이다
> 겉으로는 역전파를 전혀 하지 않았지만, 결과적으로 하는 일은 **적합도 함수에 대한 경사 상승(gradient ascent)** 과 매우 비슷하다. 다른 점은 그래디언트를 **어떻게 얻는가**뿐이다 — 여기서는 역전파가 아니라 **무작위 샘플링(몬테카를로)** 으로 그래디언트를 추정한다. Salimans 등도 CMA-ES가 정책 경사법과 본질적으로 비슷하며 그래디언트 "추정" 방식만 다르다는 것을 논문에서 보였다.

### 3.7 메인 학습 루프

```python
if __name__ == "__main__":
    writer = SummaryWriter(comment="-cartpole-es")
    env = gym.make("CartPole-v1")

    net = Net(env.observation_space.shape[0], env.action_space.n)
    print(net)
```

환경과 네트워크를 준비한다. 매 반복은 노이즈를 뽑고 양·음 노이즈 모두에 대한 보상을 얻는 배치 생성으로 시작한다.

```python
    step_idx = 0
    while True:
        t_start = time.time()
        batch_noise = []
        batch_reward = []
        batch_steps = 0
        for _ in range(MAX_BATCH_EPISODES):
            noise, neg_noise = sample_noise(net)
            batch_noise.append(noise)
            batch_noise.append(neg_noise)
            reward, steps = eval_with_noise(env, net, noise)
            batch_reward.append(reward)
            batch_steps += steps
            reward, steps = eval_with_noise(env, net, neg_noise)
            batch_reward.append(reward)
            batch_steps += steps
            if batch_steps > MAX_BATCH_STEPS:
                break
```

에피소드 상한(`MAX_BATCH_EPISODES`) 또는 스텝 상한(`MAX_BATCH_STEPS`)에 도달하면 배치 수집을 멈추고 학습 업데이트로 넘어간다.

```python
        step_idx += 1
        m_reward = float(np.mean(batch_reward))
        if m_reward > 199:
            print("Solved in %d steps" % step_idx)
            break

        train_step(net, batch_noise, batch_reward, writer, step_idx)
```

`train_step()`을 호출해 네트워크 파라미터를 실제로 갱신하고, 마지막으로 보상 평균·표준편차·최댓값, 배치 크기, 배치 스텝 수, 초당 처리 속도 등을 텐서보드에 기록한다.

### 3.8 CartPole 결과

프로그램을 인자 없이 그냥 실행하면 이런 로그가 나온다.

```
Net(
  (net): Sequential(
    (0): Linear(in_features=4, out_features=32, bias=True)
    (1): ReLU()
    (2): Linear(in_features=32, out_features=2, bias=True)
    (3): Softmax(dim=1)
  )
)
1: reward=10.00, speed=7458.03 f/s
2: reward=11.93, speed=8454.54 f/s
...
```

저자의 실험으로는 ES가 CartPole을 푸는 데 보통 **40~60번의 배치**가 걸린다. 아래 두 그림은 이 실행의 수렴 과정을 보여준다.

![[fig_17_1.png]]
*그림 17.1 — CartPole에서 ES의 최대 보상(왼쪽)과 정책 업데이트 크기(오른쪽) 변화*

![[fig_17_2.png]]
*그림 17.2 — CartPole에서 ES의 평균 보상(왼쪽)과 보상 표준편차(오른쪽) 변화*

30초 만에 환경을 풀어내는 것은, 4장에서 본 **교차 엔트로피 방법**과 견줄 만한 수준의 결과다.

---

## 4. ES를 HalfCheetah에 적용하기 — 대규모 병렬화

이번엔 가장 단순한 ES 구현을 넘어서, Salimans 등이 제안한 **공유 시드(shared seed)** 전략으로 이 방법을 효율적으로 병렬화하는 법을 살펴본다. 이전 챕터에서 다뤘던 MuJoCo 물리 시뮬레이터의 **HalfCheetah** 환경을 사용한다(`gymnasium[mujoco]` 패키지 설치 필요).

### 4.1 공유 시드 아이디어

ES 알고리즘의 성능은 대부분 **배치를 모으는 속도**로 결정된다 — 노이즈를 샘플링하고 그 노이즈로 얻은 총 보상을 확인하는 과정이다. 이 배치의 각 항목은 서로 **독립적**이므로, 원격 머신의 워커 여러 대에 쉽게 병렬화할 수 있다(12장에서 A3C 워커로 그래디언트를 모으던 것과 비슷하다).

문제는 순진하게 구현하면 워커가 마스터로 보내야 할 데이터가 너무 크다는 것이다. 대부분은 **노이즈 벡터**인데, 그 크기는 정책 파라미터 전체의 크기와 같다. Salimans 등이 제안한 우아한 해법은 이렇다 — **노이즈가 의사난수 생성기(pseudo-random number generator)로 만들어진다는 점**을 이용해, 워커는 노이즈를 생성할 때 쓴 **난수 시드(seed)만** 마스터에 보낸다. 그러면 마스터는 같은 시드로 **똑같은 노이즈를 다시 만들어낼 수 있다.** 물론 매 워커의 시드는 무작위 최적화 과정을 유지하기 위해 여전히 무작위로 생성되어야 한다.

이 방법은 워커→마스터로 전송되는 데이터양을 극적으로 줄여, 방법의 확장성을 크게 개선한다. 실제로 Salimans 등은 클라우드의 CPU 1,440개를 사용한 실험에서 **선형적인 속도 향상**을 보고했다.

### 4.2 구현 — 워커 쪽

코드는 `Chapter17/02_cheetah_es.py`에 있으며, CartPole 버전과 겹치는 부분이 많아 **차이점만** 짚는다.

워커는 별도의 프로세스로 실행되며(PyTorch의 멀티프로세싱 래퍼 사용), 역할은 단순하다 — 매 반복마다 마스터로부터 네트워크 파라미터를 받고, 정해진 횟수만큼 반복하며 노이즈를 뽑아 보상을 평가한 뒤, **무작위 시드와 함께** 결과를 큐(queue)로 마스터에 보낸다.

```python
@dataclass(frozen=True)
class RewardsItem:
    seed: int
    pos_reward: float
    neg_reward: float
    steps: int
```

워커가 마스터로 결과를 보낼 때 쓰는 데이터클래스다. 무작위 시드, 양·음 노이즈로 얻은 보상, 두 테스트에서 소모한 총 스텝 수를 담는다. (`dataclass`에 대해서는 [[데이터클래스 dataclass]] 참고)

```python
def worker_func(params_queue: mp.Queue, rewards_queue: mp.Queue,
                 device: torch.device, noise_std: float):
    env = make_env()
    net = Net(env.observation_space.shape[0], env.action_space.shape[0]).to(device)
    net.eval()

    while True:
        params = params_queue.get()
        if params is None:
            break
        net.load_state_dict(params)
```

매 학습 반복마다 워커는 마스터가 방송(broadcast)한 네트워크 파라미터를 기다린다. `params`가 `None`이면 마스터가 워커를 멈추고 싶다는 뜻이다.

```python
        for _ in range(ITERS_PER_UPDATE):
            seed = np.random.randint(low=0, high=65535)
            np.random.seed(seed)
            noise, neg_noise = common.sample_noise(net, device=device)
            pos_reward, pos_steps = common.eval_with_noise(env, net, noise, noise_std,
                get_max_action=False, device=device)
            neg_reward, neg_steps = common.eval_with_noise(env, net, neg_noise,
                noise_std, get_max_action=False, device=device)
            rewards_queue.put(RewardsItem(seed=seed, pos_reward=pos_reward,
                neg_reward=neg_reward, steps=pos_steps+neg_steps))
```

핵심 차이는 **노이즈를 생성하기 전에 무작위 시드를 만들고 그걸로 `np.random.seed()`를 호출**한다는 점이다. 이렇게 하면 마스터가 이 시드만으로 워커와 **똑같은 노이즈**를 재생성할 수 있다.

### 4.3 구현 — 마스터 쪽 학습 함수

```python
def train_step(optimizer: optim.Optimizer, net: Net, batch_noise: tt.List[common.TNoise],
                batch_reward: tt.List[float], writer: SummaryWriter, step_idx: int,
                noise_std: float):
    weighted_noise = None
    norm_reward = compute_centered_ranks(np.array(batch_reward))
```

CartPole 예제에서는 보상을 평균·표준편차로 정규화했다. Salimans 등에 따르면 **실제 값 대신 순위(rank)를 쓰면 더 좋은 결과**를 얻을 수 있다. ES는 적합도 함수(=보상)에 아무 가정도 하지 않는 블랙박스 방법이므로, 보상 값을 우리 마음대로 재배열해도 된다 — DQN이라면 불가능했을 자유다.

> [!tip] 랭크 변환(rank transformation)이란
> 배열을 그 값의 **정렬 순위**로 바꾸는 것이다. 예를 들어 `[0.1, 10, 0.5]`는 순위 `[0, 2, 1]`이 된다. `compute_centered_ranks` 함수는 배치의 총 보상 배열을 받아 각 항목의 순위를 계산하고, 그 순위를 다시 정규화한다. 예를 들어 입력 `[21.0, 5.8, 7.0]`은 순위 `[2, 0, 1]`이 되고, 최종 중심화된 순위는 `[0.5, -0.5, 0.0]`이 된다.

또 다른 큰 차이는 **PyTorch 옵티마이저를 실제로 사용**한다는 점이다.

```python
    for noise, reward in zip(batch_noise, norm_reward):
        if weighted_noise is None:
            weighted_noise = [reward * p_n for p_n in noise]
        else:
            for w_n, p_n in zip(weighted_noise, noise):
                w_n += reward * p_n
    m_updates = []
    optimizer.zero_grad()
    for p, p_update in zip(net.parameters(), weighted_noise):
        update = p_update / (len(batch_reward) * noise_std)
        p.grad = -update
        m_updates.append(torch.norm(update))
    writer.add_scalar("update_l2", np.mean(m_updates), step_idx)
    optimizer.step()
```

> [!important] ES가 왜 PyTorch 옵티마이저를 쓸 수 있는가
> 보통 [[옵티마이저와 경사하강법 변형|SGD]]는 손실 함수를 신경망 파라미터에 대해 미분해서 그래디언트를 얻고, 그 그래디언트로 파라미터를 갱신한다. 이건 손실·신경망이 **미분 가능**해야 한다는 제약을 만든다. ES는 다르게 동작한다 — 현재 파라미터 주변에 노이즈를 무작위로 뿌려 적합도 함수를 계산하고, 그 변화량으로 파라미터를 조정한다. 결과는 그래디언트 기반 방법과 매우 비슷하지만, 요구되는 조건은 훨씬 느슨하다(적합도 함수를 계산할 수만 있으면 된다). 즉 **무작위 샘플링으로 그래디언트를 "추정"** 하고 있는 것이므로, 그 추정값을 파라미터의 `grad` 필드에 (부호를 반대로 — 옵티마이저는 보통 손실을 *최소화*하지만 우리는 적합도를 *최대화*하고 싶으므로) 넣어주기만 하면 표준 옵티마이저로 갱신할 수 있다. 이는 12장의 액터-크리틱에서 정책 그래디언트에 마이너스 부호를 붙였던 것과 같은 맥락이다.

마스터의 학습 루프는 큐에서 워커 데이터를 기다리고, 파라미터 업데이트를 수행한 뒤, 결과를 워커들에게 다시 방송한다. 마스터는 결과와 함께 온 시드로 `common.sample_noise(net)`를 호출해 **워커와 동일한 노이즈**를 재생성한 다음, 이를 `train_step()`에 넘긴다.

### 4.4 HalfCheetah 결과

```
$ ./02_cheetah_es.py
Net(
  (mu): Sequential(
    (0): Linear(in_features=17, out_features=64, bias=True)
    (1): Tanh()
    (2): Linear(in_features=64, out_features=6, bias=True)
    (3): Tanh()
  )
)
All started!
0: reward=-505.09, speed=17621.60 f/s, data_gather=6.792, train=0.018
1: reward=-440.50, speed=20609.56 f/s, data_gather=5.815, train=0.007
...
```

저자의 실험 환경에서는 GPU 없이 돌렸을 때 초당 20,000~21,000개의 관측을 처리했지만, CUDA를 켜면 오히려 초당 9,000개로 **느려지는** 역설적인 결과가 나왔다. 신경망과 배치가 워낙 작아서 GPU로 데이터를 옮기는 오버헤드가 계산 이득보다 크기 때문으로 보인다.

학습 초반에는 정책이 매우 빠르게 좋아졌다 — **9분(100번의 업데이트)** 만에 보상 1,500~1,600에 도달했고, **30분** 뒤 최고 보상 **2,833**을 찍었다. 다만 더 학습을 계속하니 오히려 정책 성능이 **퇴화**했다.

![[fig_17_3.png]]
*그림 17.3 — HalfCheetah에서 ES의 최대 보상(왼쪽)과 정책 업데이트 크기(오른쪽)*

![[fig_17_4.png]]
*그림 17.4 — HalfCheetah에서 ES의 평균 보상(왼쪽)과 보상 표준편차(오른쪽)*

---

## 5. 유전 알고리즘 (Genetic Algorithms, GA)

또 다른 인기 있는 블랙박스 방법군이 **[[유전 알고리즘 Genetic Algorithm|유전 알고리즘(GA)]]** 이다. 20년이 넘는 역사를 가진 최적화 방법으로, 핵심 아이디어는 단순하다 — $N$개의 개체(구체적인 모델 파라미터)로 이루어진 **개체군(population)** 을 만들고, 각각을 적합도 함수로 평가한 뒤, 상위 성적을 낸 일부를 이용해 다음 세대의 개체군을 만든다(이 과정을 **돌연변이, mutation**이라 부른다). 만족스러운 성능이 나올 때까지 이 과정을 반복한다.

GA 계열에는 자식 세대를 어떻게 돌연변이시킬지, 성적을 어떻게 줄 세울지 등에 대해 매우 다양한 방법이 있다. 여기서는 Such 등의 논문 *Deep neuroevolution: Genetic algorithms are a competitive alternative for training deep neural networks for reinforcement learning* [Suc+17]에서 다룬 몇 가지 확장이 포함된 **단순 GA(simple GA)** 방법을 다룬다. 이 논문의 저자들은 부모의 가중치에 **가우시안 노이즈로 돌연변이**를 일으키는 단순한 GA 방법을 분석했다. 매 반복마다 최고 성적자는 아무 수정 없이 그대로 복사된다(**엘리트, elite**).

### 5.1 단순 GA 알고리즘

1. 돌연변이 강도 $\sigma$, 개체군 크기 $N$, 선택할 개체 수 $T$, 그리고 $N$개의 무작위 초기화된 정책과 그 적합도로 이루어진 초기 개체군 $P^0 = \{F(P_i^0) \mid i=1\dots N\}$을 초기화한다.
2. 세대 $g = 1 \dots G$마다:
   - (a) 이전 세대 $P^{g-1}$을 적합도 함수 값 $F^{g-1}$의 내림차순으로 정렬한다.
   - (b) 엘리트를 복사한다: $P_1^g = P_1^{g-1}$, $F_1^g = F_1^{g-1}$
   - (c) 개체 $i = 2 \dots N$에 대해:
     - i. $1 \dots T$ 중에서 무작위 부모를 고른다.
     - ii. 노이즈 $\epsilon \sim \mathcal{N}(0,I)$를 뽑는다.
     - iii. 부모를 돌연변이시킨다: $P_i^g = P_i^{g-1} + \sigma\epsilon$
     - iv. 그 적합도를 얻는다: $F_i^g = F(P_i^g)$

이 논문에는 이 단순 방법에 대한 몇 가지 개선안도 있는데, 뒤에서 다룬다. 우선 핵심 알고리즘의 구현부터 보자.

### 5.2 GA를 CartPole에 구현하기

소스 코드는 `Chapter17/03_cartpole_ga.py`이며 ES 예제와 공통점이 많다. 다른 점은 **경사 상승(gradient ascent) 코드가 없다는 것**이다 — 대신 네트워크 돌연변이 함수가 그 자리를 대신한다.

```python
def mutate_parent(net: Net) -> Net:
    new_net = copy.deepcopy(net)
    for p in new_net.parameters():
        noise = np.random.normal(size=p.data.size())
        noise_t = torch.FloatTensor(noise)
        p.data += NOISE_STD * noise_t
    return new_net
```

주어진 정책을 **복사한 뒤** 모든 가중치에 무작위 노이즈를 더해 **돌연변이 자식**을 만드는 함수다. 부모의 가중치 자체는 손대지 않는다 — 부모는 (복원 추출로) 나중에 다시 뽑혀 쓰일 수도 있기 때문이다.

하이퍼파라미터는 ES보다도 더 적다. 돌연변이에 쓰는 노이즈의 표준편차, 개체군 크기, 다음 세대를 만드는 데 쓸 상위 성적자 수뿐이다.

```python
NOISE_STD = 0.01
POPULATION_SIZE = 50
PARENTS_COUNT = 10
```

학습 루프 전에 무작위로 초기화된 네트워크들로 개체군을 만들고 적합도를 구한다.

```python
if __name__ == "__main__":
    env = gym.make("CartPole-v1")
    writer = SummaryWriter(comment="-cartpole-ga")

    gen_idx = 0
    nets = [
        Net(env.observation_space.shape[0], env.action_space.n)
        for _ in range(POPULATION_SIZE)
    ]
    population = [
        (net, common.evaluate(env, net))
        for net in nets
    ]
```

매 세대의 시작에서, 이전 세대를 적합도로 정렬해 다가올 부모들의 통계를 기록한다.

```python
    while True:
        population.sort(key=lambda p: p[1], reverse=True)
        rewards = [p[1] for p in population[:PARENTS_COUNT]]
        reward_mean = np.mean(rewards)
        reward_max = np.max(rewards)
        reward_std = np.std(rewards)

        writer.add_scalar("reward_mean", reward_mean, gen_idx)
        writer.add_scalar("reward_std", reward_std, gen_idx)
        writer.add_scalar("reward_max", reward_max, gen_idx)
        print("%d: reward_mean=%.2f, reward_max=%.2f, reward_std=%.2f" % (
            gen_idx, reward_mean, reward_max, reward_std))
        if reward_mean > 199:
            print("Solved in %d steps" % gen_idx)
            break
```

새로 생성할 개체들을 도는 별도 루프에서, **부모를 무작위로 뽑고 돌연변이시켜서 적합도를 평가**한다.

```python
        prev_population = population
        population = [population[0]]
        for _ in range(POPULATION_SIZE-1):
            parent_idx = np.random.randint(0, PARENTS_COUNT)
            parent = prev_population[parent_idx][0]
            net = mutate_parent(parent)
            fitness = common.evaluate(env, net)
            population.append((net, fitness))
        gen_idx += 1
```

새 개체군은 이전 세대의 1등(엘리트)으로 시작해서, 나머지 `POPULATION_SIZE - 1`개는 상위 `PARENTS_COUNT`명 중 무작위로 고른 부모의 돌연변이 자식으로 채운다.

### 5.3 GA CartPole 결과

```
Chapter17$ ./03_cartpole_ga.py
0: reward_mean=29.50, reward_max=109.00, reward_std=27.86
1: reward_mean=65.50, reward_max=111.00, reward_std=27.61
2: reward_mean=149.10, reward_max=305.00, reward_std=57.76
3: reward_mean=175.00, reward_max=305.00, reward_std=47.35
4: reward_mean=200.50, reward_max=305.00, reward_std=39.98
Solved in 4 steps
```

보다시피 **GA 방법이 ES보다도 더 효율적**이다 — 세대(반복) 수가 무작위성에 따라 조금씩 다를 수는 있지만, 단 4세대 만에 CartPole을 풀었다.

---

## 6. GA에 대한 두 가지 확장

Such 등은 기본 GA 알고리즘에 대해 두 가지 개선안을 제안했다.

- **딥 GA(deep GA)**: 구현의 확장성을 높이려는 시도. 뒤의 *GA on HalfCheetah* 절에서 구현한다.
- **노벨티 서치(novelty search, NS)**: 에피소드를 평가하는 척도를 보상이 아닌 다른 것으로 바꾸려는 시도. 이 챕터에서는 **연습 문제로 남겨둔다.**

### 6.1 딥 GA (Deep GA)

GA는 그래디언트가 필요 없는 방법이라, 잠재적으로 CPU 수를 늘리는 속도 확장 면에서 ES보다도 더 유리하다. 하지만 앞서 본 단순 GA 알고리즘에는 ES와 같은 병목이 있다 — **정책 파라미터를 워커 사이에서 계속 주고받아야 한다.** Such 등(저자들)은 [[진화 전략 Evolution Strategies|공유 시드]] 방식과 비슷하지만 그것을 극단까지 밀어붙인 트릭을 제안했다. 이를 **딥 GA**라 부르며, 핵심은 **정책 파라미터를 그것을 만들어낸 무작위 시드들의 리스트로 표현**하는 것이다.

실제로 최초 개체군에서는 신경망 가중치가 무작위로 생성되므로, 리스트의 첫 시드가 이 초기화를 결정한다. 각 세대의 돌연변이 역시 무작위 시드로 완전히 결정된다. 그래서 워커가 파라미터를 재구성하는 데 필요한 것은 **시드 그 자체**뿐이다. 이 방식으로는 매 워커에서 가중치를 다시 계산해야 하지만, 보통 이 오버헤드는 네트워크 전체를 전송하는 오버헤드보다 훨씬 작다.

### 6.2 노벨티 서치 (Novelty Search, NS)

GA를 위한 또 다른 수정안은 **노벨티 서치(NS)** 로, Lehman과 Stanley가 2011년 논문 *Abandoning objectives: Evolution through the search for novelty alone* [LS11]에서 제안했다.

NS의 아이디어는 최적화의 목표 자체를 바꾸는 것이다 — 환경에서 얻는 총 보상을 늘리려 하는 대신, **한 번도 확인해본 적 없는(즉 새로운, novel) 행동을 하도록** 에이전트에게 보상을 준다. 함정이 많은 미로 탐색 문제로 실험한 저자들에 따르면, 이런 상황에서는 NS가 다른 보상 기반 접근법보다 훨씬 잘 작동한다.

NS를 구현하려면 정책의 행동을 설명하는 이른바 **행동 특성(behavior characteristic, BC)** $\pi$와, 두 BC 사이의 거리를 정의해야 한다. 그런 다음 **k-최근접 이웃(k-nearest neighbors)** 방법을 써서 새 정책이 얼마나 참신한지 확인하고, 그 거리로 GA를 이끈다. Such 등의 논문에서는 에이전트의 충분한 탐험이 필요했던 경우에 NS가 ES, GA, 그리고 더 전통적인 RL 접근법들을 크게 앞섰다고 보고했다.

---

## 7. GA를 HalfCheetah에 적용하기

이 챕터의 마지막 예제는 **병렬화된 딥 GA**를 HalfCheetah 환경에 구현하는 것이다. 완전한 코드는 `Chapter17/04_cheetah_ga.py`에 있으며, 아키텍처는 병렬 ES 버전과 매우 비슷하다 — 마스터 프로세스 하나와 여러 워커로 구성되고, 워커는 각자 맡은 네트워크 배치를 평가해 마스터로 결과를 보낸다. 마스터는 부분 결과들을 모아 전체 개체군을 구성하고, 얻은 보상 순으로 순위를 매긴 뒤 워커들이 평가할 다음 개체군을 생성한다.

모든 개체는 **초기 네트워크 가중치를 만드는 시드와, 그 뒤에 적용된 모든 돌연변이의 시드를 모은 리스트**로 인코딩된다. 이 표현법은 정책 파라미터 수가 그리 많지 않을 때도 매우 압축률이 좋다. 예를 들어 이 챕터에서 쓰는 은닉층 뉴런 64개짜리 네트워크는 float 파라미터가 $17 \times 64 + 64 + 64 \times 6 + 6 = 1{,}542$개다(입력 17개, 행동 6개). float 하나가 4바이트이고 무작위 시드(정수) 하나도 같은 4바이트이므로, 이 논문에서 제안한 딥 GA 표현법은 **최대 1,542세대까지는** 가중치 전체보다 더 작은 크기로 정책을 표현할 수 있다.

### 7.1 구현

이 예제에서는 로컬 CPU들로만 병렬화하기 때문에 데이터 전송량이 크게 문제되지 않는다. 다만 수백 개의 코어를 가진 환경이라면 시드 표현의 재구성 오버헤드가 유의미해질 수 있다.

하이퍼파라미터는 CartPole 예제와 같되, 개체군 크기가 더 크다.

```python
NOISE_STD = 0.01
POPULATION_SIZE = 2000
PARENTS_COUNT = 10
WORKERS_COUNT = 6
SEEDS_PER_WORKER = POPULATION_SIZE // WORKERS_COUNT
MAX_SEED = 2**32 - 1
```

시드 리스트로 네트워크를 만드는 함수 두 개가 있다. 첫 번째는 이미 만들어진 네트워크에 돌연변이 하나를 적용한다.

```python
def mutate_net(net: Net, seed: int, copy_net: bool = True) -> Net:
    new_net = copy.deepcopy(net) if copy_net else net
    np.random.seed(seed)
    for p in new_net.parameters():
        noise = np.random.normal(size=p.data.size())
        noise_t = torch.FloatTensor(noise)
        p.data += NOISE_STD * noise_t
    return new_net
```

인자에 따라 대상 네트워크를 **복사해서** 돌연변이시킬 수도 있고 **그 자리에서(in-place)** 시킬 수도 있다(복사는 최초 세대를 만들 때 필요하다).

두 번째 함수는 시드 리스트만으로 네트워크를 처음부터 만든다.

```python
def build_net(env: gym.Env, seeds: tt.List[int]) -> Net:
    torch.manual_seed(seeds[0])
    net = Net(env.observation_space.shape[0], env.action_space.shape[0])
    for seed in seeds[1:]:
        net = mutate_net(net, seed, copy_net=False)
    return net
```

여기서 **첫 번째 시드**는 PyTorch의 네트워크 초기화(가중치 랜덤 초기화)에 영향을 주도록 쓰이고, **나머지 시드들**은 순서대로 돌연변이를 적용하는 데 쓰인다.

워커 함수는 평가할 시드 리스트들을 받아, 결과마다 `OutputItem` 데이터클래스를 출력한다.

```python
@dataclass
class OutputItem:
    seeds: tt.List[int]
    reward: float
    steps: int

def worker_func(input_queue: mp.Queue, output_queue: mp.Queue):
    env = gym.make("HalfCheetah-v4")
    cache = {}

    while True:
        parents = input_queue.get()
        if parents is None:
            break
        new_cache = {}
        for net_seeds in parents:
            if len(net_seeds) > 1:
                net = cache.get(net_seeds[:-1])
                if net is not None:
                    net = mutate_net(net, net_seeds[-1])
                else:
                    net = build_net(env, net_seeds)
            else:
                net = build_net(env, net_seeds)
            new_cache[net_seeds] = net
            reward, steps = common.evaluate(env, net, get_max_action=False)
            output_queue.put(OutputItem(seeds=net_seeds, reward=reward, steps=steps))
        cache = new_cache
```

> [!tip] 캐시는 왜 필요한가
> 이 함수는 매 세대 파라미터를 처음부터 다시 계산하는 시간을 줄이려고 **네트워크 캐시**를 유지한다. 부모의 시드 리스트(마지막 시드를 뺀 것)가 캐시에 있으면, 그 네트워크에 **마지막 시드 하나만** 추가로 적용해서 자식을 만든다 — 시드 리스트 전체로 처음부터 재구성할 필요가 없어진다. 이 캐시는 매 세대 새로 만들어지는데, 현재 세대의 승자로부터만 다음 세대가 생성되므로 이전 세대의 네트워크가 재사용될 확률이 거의 없기 때문이다.

마스터 프로세스의 코드는 비교적 단순하다.

```python
    batch_steps = 0
    population = []
    while len(population) < SEEDS_PER_WORKER * WORKERS_COUNT:
        out_item = output_queue.get()
        population.append((out_item.seeds, out_item.reward))
        batch_steps += out_item.steps
    if elite is not None:
        population.append(elite)
    population.sort(key=lambda p: p[1], reverse=True)
    elite = population[0]
    for worker_queue in input_queues:
        seeds = []
        for _ in range(SEEDS_PER_WORKER):
            parent = np.random.randint(PARENTS_COUNT)
            next_seed = np.random.randint(MAX_SEED)
            s = list(population[parent][0]) + [next_seed]
            seeds.append(tuple(s))
```

매 세대마다 마스터는 현재 개체군의 시드 리스트를 워커에 보내 평가를 맡기고 결과를 기다린다. 그런 다음 결과를 정렬해 다음 개체군을 만든다. 마스터 쪽에서는 돌연변이가 그저 **무작위로 생성된 시드 하나를 부모의 시드 리스트 끝에 덧붙이는 것**일 뿐이다.

### 7.2 결과

이 예제는 MuJoCo의 HalfCheetah 환경을 쓰는데, 이 환경은 내부적으로 아무런 건강 체크(health check)가 없어서 **매 에피소드가 2,000 스텝씩** 걸린다. 그래서 학습 스텝 하나에 약 1분이 걸리므로 인내심이 필요하다. **300번의 돌연변이 라운드**(약 7시간 소요) 뒤, 최고 정책은 보상 **6,454**를 얻었다 — 매우 좋은 결과다. 앞 챕터의 실험을 떠올려보면, MuJoCo HalfCheetah에서 이보다 더 높은 보상(7,063)을 얻은 것은 **SAC 방법**뿐이었다. HalfCheetah가 그리 어려운 환경은 아니지만, 그럼에도 이것은 훌륭한 결과다.

![[fig_17_5.png]]
*그림 17.5 — HalfCheetah에서 GA의 최대 보상(왼쪽)과 평균 보상(오른쪽)*

![[fig_17_6.png]]
*그림 17.6 — HalfCheetah에서 GA의 보상 표준편차*

---

## 8. 요약

이 챕터에서 우리는:
1. 지금까지와 완전히 다른 관점 — **블랙박스 최적화**로 RL 문제에 접근하는 법을 배웠다. 그래디언트, 미분 가능성, 매끄러움 같은 가정을 전혀 요구하지 않는 이 계열의 방법들이 왜 빠르고 병렬화가 쉬운지 이해했다.
2. **진화 전략(ES)** — 파라미터를 무작위로 흔들어보고 점수가 좋은 방향으로 옮기는 방법을 CartPole과 HalfCheetah에 구현했다. 미러드 샘플링, 랭크 변환, 공유 시드를 통한 대규모 병렬화까지 다뤘다.
3. **유전 알고리즘(GA)** — 개체군·엘리트·돌연변이라는 진화 아이디어로 정책을 최적화하는 법을 배우고, 딥 GA(시드 표현)와 노벨티 서치라는 두 확장까지 살펴봤다.
4. 실험 결과, ES와 GA 모두 그래디언트 기반 방법들과 **경쟁할 만한 성능**을 냈고, 특히 GA는 CartPole에서 ES보다도 더 빠르게 수렴했다.

이 방법들의 강점은 **다른 자원(대규모 병렬성)으로 표본 효율성의 약점을 상쇄**할 수 있다는 데 있다 — 즉 "느리게 배우지만, 아주 많은 자원으로 아주 빠르게 시도해볼 수 있다"는 트레이드오프다. 다음 챕터에서는 RL의 또 다른 중요한 축인 **고급 탐험(advanced exploration) 방법**을 다룬다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[블랙박스 최적화와 적합도 함수]]
- [[진화 전략 Evolution Strategies]]
- [[유전 알고리즘 Genetic Algorithm]]
- [[옵티마이저와 경사하강법 변형]]
- [[정책 경사 Policy Gradient]]
- [[액터-크리틱과 어드밴티지]]
- [[동기·비동기 병렬화(데이터·그래디언트 병렬)]]
- [[데이터클래스 dataclass]]

## 한눈에 보는 개념 지도
| 개념 | 기호/용어 | 한 줄 뜻 |
|---|---|---|
| 적합도 함수 | $F(\theta)$ | 파라미터 후보의 좋음을 알려주는 숫자 |
| 노이즈 표준편차 | $\sigma$ | 파라미터를 얼마나 세게 흔들지 |
| 학습률 | $\alpha$ | 파라미터를 얼마나 크게 옮길지 |
| ES 갱신식 | $\theta_{t+1}=\theta_t+\alpha\frac{1}{n\sigma}\sum F_i\epsilon_i$ | 노이즈 방향을 적합도로 가중해 옮기기 |
| 미러드 샘플링 | $\pm\epsilon$ | 양·음 노이즈를 쌍으로 써서 편향 상쇄 |
| 랭크 변환 | rank | 보상 값을 순위로 바꿔 정규화 |
| 공유 시드 | seed | 노이즈 벡터 대신 시드 정수만 통신 |
| 개체군 | population | 그 세대의 정책들의 집합 |
| 엘리트 | elite | 무수정으로 보존되는 최우수 개체 |
| 돌연변이 | mutation | 부모 파라미터 + 가우시안 노이즈 |
| 딥 GA | deep GA | 정책 = 시드 리스트로 초압축 표현 |
| 노벨티 서치 | NS | 보상 대신 "참신함"으로 개체 평가 |

