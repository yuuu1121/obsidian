---
title: "Chapter 16 — 신뢰 영역 방법 (Trust Region Methods)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 16
tags: [DeepRL, 강화학습, 정책경사, PPO, TRPO, ACKTR, SAC, 연속제어]
---

# Chapter 16 · 신뢰 영역 방법 (Trust Region Methods)

> [!abstract] 이 챕터를 한 문장으로
> 정책을 학습시킬 때 "한 걸음을 너무 크게 내디디면 그동안 배운 걸 한순간에 망칠 수 있다"는 문제를 해결하기 위해, **정책이 한 번에 너무 많이 바뀌지 않도록 걸음의 폭 자체를 제한**하는 4가지 방법(PPO, TRPO, ACKTR, SAC)을 배우고, 두 다리 로봇(HalfCheetah)과 네 다리 로봇(Ant)을 직접 걷게 학습시켜 성능을 비교한다.

---

## 들어가며 — 왜 "걸음의 크기"가 문제인가?

경사하강법(SGD)으로 신경망을 학습시킬 때 우리는 늘 고민한다. *학습률(learning rate)을 크게 잡을까, 작게 잡을까?* 보통의 지도학습이라면 학습률이 조금 커도 "몇 스텝 손해 보고 다시 조정"하면 그만이다. 데이터셋은 그대로 있고, 다음 배치에서 다시 학습하면 되니까.

그런데 강화학습(RL)에서는 사정이 다르다. [[정책 경사 Policy Gradient|정책 경사법]]으로 정책 $\pi_\theta$를 업데이트할 때, 한 번의 큰 업데이트가 정책을 크게 망가뜨리면 어떻게 될까?

> [!warning] RL에서 '되돌릴 수 없는' 실수
> 지도학습은 데이터가 고정되어 있어 다음 스텝에서 실수를 만회할 기회가 있다. 하지만 RL에서는 **망가진 정책이 나쁜 행동을 하고, 그 나쁜 행동이 다시 나쁜 경험(샘플)을 만들어낸다.** 이 나쁜 경험으로 또 학습하면 정책은 더 나빠진다 — **악순환**이다. 자전거를 타다가 핸들을 확 꺾어버리면, 그 뒤로는 넘어진 채로 계속 이상한 방향으로만 페달을 밟게 되는 것과 비슷하다. 지도학습과 달리 "다음 배치에서 정신 차리자"가 통하지 않는다.

그래서 나온 가장 단순한 해법은 "학습률을 아주 작게 잡아서 아기 걸음(baby step)만 걷자"는 것이다. 하지만 이러면 학습이 지나치게 느려진다. 이 딜레마를 깨기 위해 연구자들은 **신뢰 영역 최적화(trust region optimization)**라는 접근을 고안했다.

> [!important] 신뢰 영역(Trust Region)이란?
> "지금 이 정도 범위 안에서는 우리가 계산한 개선 방향을 **믿고(trust)** 따라가도 안전하다"고 보장할 수 있는 **영역(region)**을 뜻한다. 구체적으로는, 정책을 업데이트하기 전과 후의 확률분포 사이의 [[KL 발산 Kullback-Leibler Divergence|KL 발산]]을 계산해서, 이 값이 일정 한계를 넘지 않도록 **업데이트의 크기 자체를 제약**한다. 즉 "얼마나 좋은 방향인지"뿐 아니라 "그 방향으로 얼마나 멀리 가도 안전한지"까지 함께 따지는 것이다.

이번 챕터에서는 이 아이디어를 서로 다르게 구현한 세 가지 방법 — **PPO(근접 정책 최적화)**, **TRPO(신뢰 영역 정책 최적화)**, **ACKTR(2차 최적화 기반)** — 을 A2C 베이스라인과 비교하고, 마지막에는 비교적 최근 방법인 **SAC**도 살펴본다.

---

## 1. 실험 환경 — 두 다리 치타와 네 다리 개미

이전 판에서는 OpenAI의 Roboschool 라이브러리를 썼지만, OpenAI가 이를 지원 중단했다. 이 책의 3판에서는 두 가지 대안을 쓴다.

- **PyBullet**: 15장에서 다뤘던 물리 시뮬레이터. 조금 오래됐지만(최신 릴리스가 2022년) 여전히 쓸 수 있다.
- **Farama Gymnasium의 MuJoCo 환경**: MuJoCo는 15장에서 다룬 물리 시뮬레이터로, 오픈소스가 된 뒤 Gymnasium을 포함한 여러 제품에 채택됐다.

이 챕터에서는 두 가지 문제를 다룬다.
- **HalfCheetah-v4**: 평평한 두 다리 생물을 흉내 낸 로봇.
- **Ant-v4**: 4개의 다리를 가진 3차원 "거미" 로봇.

두 환경 모두 15장에서 본 Minitaur 환경과 비슷하다 — **관측(state)**은 관절들의 여러 특성값이고, **행동(action)**은 그 관절들을 얼마나 움직일지에 대한 값이다. 목표는 **에너지 소모를 최소화하며 최대한 멀리 이동**하는 것이다.

![[fig_16_1.png]]
*그림 16.1 — 치타(HalfCheetah)와 개미(Ant) 환경의 스크린샷. 왼쪽이 개미, 오른쪽이 치타.*

MuJoCo 확장판을 설치하려면 다음 명령이 필요하다.
```
pip install gymnasium[mujoco]==0.29.0
```

> [!note] PyBullet vs MuJoCo, 공정한 비교는 아니다
> 두 시뮬레이터의 내부 구조와 관측 공간(PyBullet은 26개 파라미터, MuJoCo는 17개)이 다르기 때문에, 같은 알고리즘이라도 두 시뮬레이터에서의 학습 다이내믹스를 **직접 비교하기엔 무리가 있다.** 이 챕터의 실험은 "참고용" 비교이지, 엄밀한 벤치마크는 아니라는 점을 염두에 두자.

---

## 2. A2C 베이스라인

이후 방법들의 성능을 비교할 기준(baseline)으로, 15장과 비슷한 방식의 [[액터-크리틱과 어드밴티지|A2C]] 방법을 먼저 만든다. 전체 코드는 `Chapter16/01_train_a2c.py`와 `Chapter16/lib/model.py`에 있다. 이전 버전과의 차이는 두 가지다.

- **16개의 병렬 환경**을 동시에 돌려 경험을 모은다.
- **모델 구조**와 **탐험(exploration) 방식**이 다르다.

### 2.1 모델 구조

액터(정책)와 크리틱(가치 함수)은 가중치를 공유하지 않는 **완전히 분리된 네트워크**로 만든다. 15장 방식을 따라 크리틱이 행동의 **평균과 분산**을 함께 추정하지만, 이번엔 분산이 관측에 의존하는 별도의 신경망 출력이 아니라 **모델의 파라미터 하나**로 취급된다. 즉 학습 과정에서 SGD로 조정되긴 하지만, 관측값과 무관하게 **하나의 값**으로 유지된다.

```python
HID_SIZE = 64

class ModelActor(nn.Module):
    def __init__(self, obs_size: int, act_size: int):
        super(ModelActor, self).__init__()

        self.mu = nn.Sequential(
            nn.Linear(obs_size, HID_SIZE),
            nn.Tanh(),
            nn.Linear(HID_SIZE, HID_SIZE),
            nn.Tanh(),
            nn.Linear(HID_SIZE, act_size),
            nn.Tanh(),
        )
        self.logstd = nn.Parameter(torch.zeros(act_size))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mu(x)
```

한 줄씩 뜯어보자.
- `HID_SIZE = 64`: 은닉층 뉴런 수. 두 은닉층 모두 64개.
- `self.mu`: 상태(observation)를 받아 **행동의 평균(mean)**을 출력하는 3층 신경망. 각 층 뒤에 **Tanh**(하이퍼볼릭 탄젠트) [[활성화함수|활성화함수]]를 붙여서, 최종 출력이 항상 $-1 \sim 1$ 범위 안에 들어오게 만든다(로봇 관절의 행동값이 보통 이 범위이기 때문).
- `self.logstd = nn.Parameter(torch.zeros(act_size))`: 표준편차의 **로그값**을 학습 가능한 파라미터로 직접 선언한다. 초깃값은 0이므로 $\exp(0)=1$, 즉 처음엔 표준편차가 1인 상태에서 시작한다. 로그로 표현하는 이유는, 표준편차는 항상 양수여야 하는데 로그를 취하면 음수·양수 아무 실수값이나 최적화해도 지수함수를 거쳐 항상 양수가 나오기 때문이다.
- `forward`: 상태를 넣으면 행동의 평균만 반환한다(분산은 `logstd`를 통해 별도로 접근).

크리틱 네트워크는 구조가 비슷하되, 최종적으로 **상태의 가치 $V(s)$**(할인된 가치 추정값) 하나만 출력한다.

```python
class ModelCritic(nn.Module):
    def __init__(self, obs_size: int):
        super(ModelCritic, self).__init__()

        self.value = nn.Sequential(
            nn.Linear(obs_size, HID_SIZE),
            nn.ReLU(),
            nn.Linear(HID_SIZE, HID_SIZE),
            nn.ReLU(),
            nn.Linear(HID_SIZE, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.value(x)
```

- 액터와 달리 활성화함수로 **ReLU**를 쓴다(출력값 $V(s)$는 $-1\sim1$로 제한할 이유가 없기 때문).
- 마지막 `nn.Linear(HID_SIZE, 1)`: 출력이 스칼라 하나(가치값).

### 2.2 에이전트 클래스 — 행동에 노이즈 섞기

```python
class AgentA2C(ptan.agent.BaseAgent):
    def __init__(self, net, device: torch.device):
        self.net = net
        self.device = device

    def __call__(self, states: ptan.agent.States, agent_states: ptan.agent.AgentStates):
        states_v = ptan.agent.float32_preprocessor(states)
        states_v = states_v.to(self.device)

        mu_v = self.net(states_v)
        mu = mu_v.data.cpu().numpy()
        logstd = self.net.logstd.data.cpu().numpy()
        rnd = np.random.normal(size=logstd.shape)
        actions = mu + np.exp(logstd) * rnd
        actions = np.clip(actions, -1, 1)
        return actions, agent_states
```

- `mu_v = self.net(states_v)`: 액터 신경망에서 행동의 **평균**을 얻는다.
- `rnd = np.random.normal(size=logstd.shape)`: 표준정규분포(평균 0, 표준편차 1)에서 무작위 노이즈를 뽑는다.
- `actions = mu + np.exp(logstd) * rnd`: **평균 + (표준편차) × (무작위 노이즈)** 공식으로 실제 행동을 만든다. `np.exp(logstd)`가 실제 표준편차값이다. 이렇게 하면 매번 조금씩 다른 행동이 나와서 자연스럽게 **탐험**이 이뤄진다.
- `np.clip(actions, -1, 1)`: 노이즈를 더하다 보면 $-1\sim1$ 범위를 벗어날 수 있으니 강제로 잘라준다.

### 2.3 A2C 결과

`01_train_a2c.py`는 PyBullet(기본) 또는 MuJoCo(`-mujoco` 옵션)로 실행할 수 있다. 기본은 HalfCheetah 환경이고, `-e ant` 옵션으로 Ant 환경으로 바꿀 수 있다.

**HalfCheetah on PyBullet**: 저자의 머신(GPU 사용)에서 초당 약 1,600프레임, 1억 스텝에 20시간 소요.

![[fig_16_2.png]]
*그림 16.2 — HalfCheetah on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

**HalfCheetah on MuJoCo**: MuJoCo는 초당 5,100프레임으로 PyBullet보다 3배 빠르며, 9천만 스텝(약 5시간)만에 보상 4,500을 달성했다.

![[fig_16_3.png]]
*그림 16.3 — HalfCheetah on MuJoCo의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

> [!note] 참고 수치
> 연구 논문들에 따르면 HalfCheetah의 최대 점수는 대략 4,000~5,000 정도다. 이 챕터의 실험은 방법 비교가 목적이라 시간을 짧게 잡았을 뿐, 더 오래 학습시키면 더 좋아질 수 있다.

**Ant on PyBullet / MuJoCo**: Ant는 3차원 구조라 관절이 더 많아 시뮬레이션이 더 느리다(PyBullet 약 1,400 프레임/초, MuJoCo 약 2,500 프레임/초).

![[fig_16_4.png]]
*그림 16.4 — Ant on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

![[fig_16_5.png]]
*그림 16.5 — Ant on MuJoCo의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

> [!warning] MuJoCo Ant의 "건강 체크"와 조기 종료 함정
> MuJoCo의 Ant 환경에는 로봇이 일정 각도 이상 기울어지면 에피소드를 강제 종료하는 **"건강함(healthiness)" 체크**가 기본으로 켜져 있다. 문제는 학습 **초기**에는 에이전트가 아직 서는 법조차 모르는데, 조금만 기울어져도 곧바로 에피소드가 끝나버려서 "어떻게 하면 더 걸을 수 있는지" 배울 기회 자체를 얻지 못한다는 것이다. 그 결과 학습이 **국소 최적(local minima)**에 영원히 갇혀버린다. 이를 피하려면 `-no-unhealthy` 옵션으로 이 체크를 꺼야 한다(MuJoCo 학습에서만 필요).
>
> 이런 상황을 근본적으로 개선하려면 15장의 OU 프로세스나 18장에서 다룰 더 발전된 탐험 기법을 추가로 적용할 수도 있다.

MuJoCo의 테스트 보상 그래프(그림 16.5)를 보면 처음 1억 스텝 동안은 거의 변화가 없다가, 이후 갑자기 5,000점까지 치솟는다(최고 기록은 5,380점). 참고로 `papers with code` 사이트 기준 Ant MuJoCo의 2021년 SOTA 기록은 IQ-Learn의 4,362.9점이었으니, 이 A2C 결과는 꽤 인상적이다.

### 2.4 학습된 모델 영상

`02_play.py` 유틸리티로 학습된 모델을 벤치마크하고 영상으로 기록할 수 있다. 이 도구는 이 챕터에서 다루는 모든 방법이 같은 액터 구조를 공유하므로 공통으로 사용 가능하다. `saves` 디렉터리의 모델 파일을 지정하고, MuJoCo를 쓰려면 `-mujoco` 옵션을 추가하면 된다(PyBullet과 MuJoCo는 관측 개수가 달라 반드시 학습 때와 같은 물리 엔진을 지정해야 한다).

가장 성능이 좋았던 A2C 모델 영상들:
- HalfCheetah on PyBullet (점수 2,189)
- HalfCheetah on MuJoCo (점수 4,718)
- Ant on PyBullet (점수 2,425)
- Ant on MuJoCo (점수 5,380)

---

## 3. PPO (Proximal Policy Optimization, 근접 정책 최적화)

PPO는 OpenAI 팀이 만들었으며, TRPO(2015년) 이후에 나온 방법이다. 하지만 TRPO보다 훨씬 간단하므로 이 챕터에서는 PPO를 먼저 다룬다. 2017년 논문 *Proximal Policy Optimization Algorithms* (Schulman 등)에서 처음 제안됐다.

### 3.1 핵심 아이디어 — 목적함수를 바꾼다

A2C와 비교했을 때 PPO의 핵심 개선점은 **정책 경사를 추정하는 공식 자체를 바꾼 것**이다. 기존처럼 "선택한 행동의 로그 확률에 대한 그래디언트"를 쓰는 대신, PPO는 **새 정책과 옛 정책의 비율**을 어드밴티지로 가중한 새로운 목적함수를 쓴다.

A2C의 목적함수는 다음과 같이 쓸 수 있다.

$$J_\theta = \mathbb{E}_t[\nabla_\theta \log\pi_\theta(a_t|s_t)A_t]$$

말로 풀면: *"모델 $\theta$에 대한 그래디언트는, 정책 $\pi$의 로그값에 어드밴티지 $A$를 곱한 것의 기댓값으로 추정한다."*

PPO가 제안하는 새 목적함수는 다음과 같다.

$$J_\theta = \mathbb{E}_t\left[\frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}A_t\right]$$

이 비율 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$이 바로 **[[중요도 샘플링 비율과 PPO 클리핑|중요도 샘플링 비율]]** 이다. 목적함수를 이렇게 바꾸는 이유는 4장의 크로스 엔트로피 방법에서 본 것과 같은 이유(중요도 샘플링)다. 하지만 이 값을 아무 제약 없이 그대로 최대화하면 정책이 한 번에 너무 크게 바뀔 위험이 있다. 그래서 **클리핑된(잘린) 목적함수**를 쓴다. 비율을 $r_t(\theta)$로 두면:

$$J_\theta^{clip} = \mathbb{E}_t[\min(r_t(\theta)A_t,\ \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)A_t)]$$

이 목적함수는 새 정책과 옛 정책의 비율이 $[1-\epsilon, 1+\epsilon]$ 구간 안에 있도록 제한한다. $\epsilon$ 값을 조절해서 업데이트의 크기를 제어할 수 있다. (자세한 유도와 클리핑의 의미는 [[중요도 샘플링 비율과 PPO 클리핑]] 참고.)

### 3.2 어드밴티지 추정 방식의 차이

A2C 논문에서 쓰던 유한 지평(finite-horizon) 어드밴티지 추정은 다음 형태다.

$$A_t = -V(s_t) + r_t + \gamma r_{t+1} + \dots + \gamma^{T-t+1}r_{T-1} + \gamma^{T-t}V(s_T)$$

PPO 논문에서는 이를 일반화한 추정식을 쓴다.

$$A_t = \sigma_t + (\gamma\lambda)\sigma_{t+1} + (\gamma\lambda)^2\sigma_{t+2} + \dots + (\gamma\lambda)^{T-t+1}\sigma_{T-1}, \qquad \sigma_t = r_t + \gamma V(s_{t+1}) - V(s_t)$$

이것이 바로 **[[GAE 일반화된 어드밴티지 추정|GAE]]**다. 원래의 A2C 추정식은 $\lambda=1$일 때의 특수한 경우에 해당한다. PPO는 또한 조금 다른 학습 절차를 쓴다: 환경에서 긴 시퀀스의 샘플을 모은 다음, 그 어드밴티지를 추정하고 **여러 에폭에 걸쳐** 학습을 수행한다.

### 3.3 구현

`Chapter16/04_train_ppo.py`와 `Chapter16/lib/model.py`에 코드가 있다. 액터·크리틱·에이전트 클래스는 A2C 베이스라인과 완전히 동일하다. 차이는 **학습 절차**와 **어드밴티지 계산 방식**에 있다.

먼저 하이퍼파라미터.

```python
GAMMA = 0.99
GAE_LAMBDA = 0.95

TRAJECTORY_SIZE = 2049
LEARNING_RATE_ACTOR = 1e-5
LEARNING_RATE_CRITIC = 1e-4

PPO_EPS = 0.2
PPO_EPOCHES = 10
PPO_BATCH_SIZE = 64
```

- `GAMMA`: 익숙한 할인율.
- `GAE_LAMBDA = 0.95`: GAE의 $\lambda$ 값(논문에서 채택한 값).
- `TRAJECTORY_SIZE = 2049`: 학습 한 번에 쓸 궤적(trajectory)의 크기. 이만큼 샘플을 모은 뒤에 학습을 시작한다.
- `PPO_EPS = 0.2`: 새 정책/옛 정책 비율의 클리핑 범위 — $[0.8, 1.2]$.
- `PPO_EPOCHES = 10`: 모은 궤적 하나로 총 10번 반복 학습.
- `PPO_BATCH_SIZE = 64`: 각 에폭에서 미니배치 크기.
- 액터와 크리틱은 가중치를 공유하지 않으므로 **서로 다른 옵티마이저** 두 개를 쓴다.

**어드밴티지·기준값 계산 함수**: 크리틱을 훈련시키기 위한 기준값(reference value)과, 액터를 훈련시키기 위한 어드밴티지를 함께 계산한다.

```python
def calc_adv_ref(trajectory: tt.List[ptan.experience.Experience],
                  net_crt: model.ModelCritic, states_v: torch.Tensor, gamma: float,
                  gae_lambda: float, device: torch.device):
    values_v = net_crt(states_v)
    values = values_v.squeeze().data.cpu().numpy()
```

- 먼저 크리틱에게 궤적의 모든 상태를 넣어 가치 $V(s)$들을 한 번에 얻는다.

```python
    last_gae = 0.0
    result_adv = []
    result_ref = []
    for val, next_val, (exp,) in zip(
            reversed(values[:-1]), reversed(values[1:]), reversed(trajectory[:-1])):
```

- 궤적을 **뒤에서부터 거꾸로** 순회한다. GAE는 미래 시점의 값을 현재 시점에 누적해야 하므로, 역방향으로 훑으면 한 번의 순회로 계산을 끝낼 수 있다.

```python
        if exp.done_trunc:
            delta = exp.reward - val
            last_gae = delta
        else:
            delta = exp.reward + gamma * next_val - val
            last_gae = delta + gamma * gae_lambda * last_gae
```

- `done_trunc`(에피소드가 이 스텝에서 끝났는지 여부)가 참이면, 다음 상태가 없으므로 TD 오차는 그냥 "보상 − 현재 가치". 아니라면 벨만 방정식 형태로 "보상 + 할인된 다음 가치 − 현재 가치"를 계산한다.
- `last_gae`는 지금까지(뒤에서부터 봤을 때는 "이전에", 실제로는 "미래에") 누적된 GAE 값에 $\gamma\lambda$를 곱해 현재 델타에 더한 것 — GAE 공식 그 자체다.

```python
        result_adv.append(last_gae)
        result_ref.append(last_gae + val)

    adv_v = torch.FloatTensor(np.asarray(list(reversed(result_adv))))
    ref_v = torch.FloatTensor(np.asarray(list(reversed(result_ref))))
    return adv_v.to(device), ref_v.to(device)
```

- 어드밴티지는 `last_gae` 그대로, 크리틱 학습용 기준값(reference)은 `어드밴티지 + 현재 가치`(즉 원래의 리턴 추정치)로 저장한다.
- 뒤에서부터 계산했으므로 마지막에 다시 순서를 뒤집어(`reversed`) 원래 시간 순서로 되돌린다.

**학습 루프에서 궤적 모으기**: PTAN 라이브러리의 `ExperienceSource(steps_count=1)`를 사용해, 환경에서 한 스텝씩 개별 `Experience` 데이터클래스로 얻는다.

```python
        trajectory.append(exp)
        if len(trajectory) < TRAJECTORY_SIZE:
            continue

        traj_states = [t[0].state for t in trajectory]
        traj_actions = [t[0].action for t in trajectory]
        traj_states_v = torch.FloatTensor(np.asarray(traj_states))
        traj_states_v = traj_states_v.to(device)
        traj_actions_v = torch.FloatTensor(np.asarray(traj_actions))
        traj_actions_v = traj_actions_v.to(device)
        traj_adv_v, traj_ref_v = common.calc_adv_ref(
            trajectory, net_crt, traj_states_v, GAMMA, GAE_LAMBDA, device=device)
```

- `TRAJECTORY_SIZE`만큼 샘플이 쌓이면, 상태·행동을 텐서로 변환하고 앞서 만든 함수로 어드밴티지와 기준값을 계산한다.
- 이 환경들의 관측은 작아서 배치를 한 번에 처리해도 괜찮지만(아타리 프레임이었다면 GPU 메모리 부족이 날 수 있다).

**옛 정책의 로그 확률 저장, 어드밴티지 정규화**:

```python
        mu_v = net_act(traj_states_v)
        old_logprob_v = model.calc_logprob(mu_v, net_act.logstd, traj_actions_v)

        traj_adv_v = traj_adv_v - torch.mean(traj_adv_v)
        traj_adv_v /= torch.std(traj_adv_v)
```

- `old_logprob_v`: PPO 목적함수의 분모, 즉 $\pi_{\theta_{old}}$에 해당하는 값을 미리 계산해둔다(이후 여러 에폭 동안 정책이 바뀌어도 이 값은 고정된 채 비교 기준이 된다).
- 어드밴티지를 **평균 0, 표준편차 1**로 정규화해서 학습을 더 안정적으로 만든다.

```python
        trajectory = trajectory[:-1]
        old_logprob_v = old_logprob_v[:-1].detach()
```

- `calc_adv_ref`에서 값을 한 칸씩 밀어서(shift) 계산했기 때문에, 어드밴티지·기준값 배열이 궤적보다 한 칸 짧다. 그래서 궤적의 마지막 원소를 잘라내 길이를 맞춘다.

**에폭 반복 학습**: 준비가 끝나면 궤적 전체에 대해 여러 에폭을 반복하며, 크리틱과 액터를 각각 따로 학습시킨다.

```python
        for epoch in range(PPO_EPOCHES):
            for batch_ofs in range(0, len(trajectory), PPO_BATCH_SIZE):
                batch_l = batch_ofs + PPO_BATCH_SIZE
                states_v = traj_states_v[batch_ofs:batch_l]
                actions_v = traj_actions_v[batch_ofs:batch_l]
                batch_adv_v = traj_adv_v[batch_ofs:batch_l]
                batch_adv_v = batch_adv_v.unsqueeze(-1)
                batch_ref_v = traj_ref_v[batch_ofs:batch_l]
                batch_old_logprob_v = old_logprob_v[batch_ofs:batch_l]
```

- 궤적을 `PPO_BATCH_SIZE`(64개)씩 잘라 미니배치를 만들고, 이를 `PPO_EPOCHES`(10)번 반복한다.

**크리틱 학습** — 단순한 MSE(평균제곱오차) 손실:

```python
                opt_crt.zero_grad()
                value_v = net_crt(states_v)
                loss_value_v = F.mse_loss(value_v.squeeze(-1), batch_ref_v)
                loss_value_v.backward()
                opt_crt.step()
```

- 크리틱이 예측한 가치 `value_v`와, 미리 계산해둔 기준값(리턴 추정치) `batch_ref_v`의 차이를 MSE로 최소화한다. 지도학습의 회귀 문제와 똑같은 형태다.

**액터 학습** — 클리핑된 목적함수를 최소화(부호를 뒤집었으므로 실제로는 최대화):

```python
                opt_act.zero_grad()
                mu_v = net_act(states_v)
                logprob_pi_v = model.calc_logprob(mu_v, net_act.logstd, actions_v)
                ratio_v = torch.exp(logprob_pi_v - batch_old_logprob_v)
                surr_obj_v = batch_adv_v * ratio_v
                c_ratio_v = torch.clamp(ratio_v, 1.0 - PPO_EPS, 1.0 + PPO_EPS)
                clipped_surr_v = batch_adv_v * c_ratio_v
                loss_policy_v = -torch.min(surr_obj_v, clipped_surr_v).mean()
                loss_policy_v.backward()
                opt_act.step()
```

- `ratio_v = torch.exp(logprob_pi_v - batch_old_logprob_v)`: 로그 확률의 차이를 지수화해서 **중요도 샘플링 비율** $r_t(\theta)$를 얻는다.
- `surr_obj_v`: 클리핑 없는 원래 목적함수 값(어드밴티지 × 비율).
- `c_ratio_v`: 비율을 $[1-\epsilon, 1+\epsilon]$로 자른 값.
- `clipped_surr_v`: 클리핑된 비율로 계산한 목적함수 값.
- `torch.min(surr_obj_v, clipped_surr_v)`: 두 값 중 더 작은(비관적인) 쪽을 취해, 정책이 한쪽으로 과도하게 개선되는 것을 막는다. 손실은 이를 최대화해야 하므로 앞에 마이너스를 붙여 `.backward()`가 경사 **하강**으로 동작하게 만든다.

### 3.4 결과

두 환경 모두에서 학습한 결과, PPO는 A2C보다 **훨씬 빠른 수렴**을 보였다. PyBullet 위 HalfCheetah에서, PPO는 8시간·2,500만 스텝 학습으로 학습 보상 1,800·테스트 보상 2,500을 달성했다(A2C는 1억 1,000만 스텝·20시간이 걸렸다).

![[fig_16_6.png]]
*그림 16.6 — HalfCheetah on PyBullet의 A2C·PPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

하지만 MuJoCo 위 HalfCheetah에서는 반대였다 — PPO의 성장이 훨씬 느려서, 저자는 5,000만 스텝(12시간)에서 학습을 중단했다.

![[fig_16_7.png]]
*그림 16.7 — HalfCheetah on MuJoCo의 A2C·PPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

> [!example] "백플립 치타" — 국소 최적에 빠진 정책
> 학습된 모델의 영상을 확인해보니, 에이전트가 **치타를 뒤집어서(등을 대고) 그 자세로 전진하는 법**을 학습해버렸다. 학습 중 이 준최적(suboptimal) "국소 최댓값(local maximum)"에서 빠져나오지 못한 것이다. 초기 시드(seed)를 바꿔 여러 번 다시 학습시키면 더 나은 정책을 찾을 가능성이 높고, 하이퍼파라미터를 최적화하는 것도 방법이 될 수 있다.

Ant 환경에서는 PPO가 PyBullet과 MuJoCo 양쪽 모두에서 A2C보다 **거의 2배 빠르게** 같은 수준의 보상에 도달했다.

![[fig_16_8.png]]
*그림 16.8 — Ant on PyBullet의 A2C·PPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

![[fig_16_9.png]]
*그림 16.9 — Ant on MuJoCo의 A2C·PPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

가장 성능이 좋았던 PPO 모델들:
- HalfCheetah on PyBullet (점수 2,567) — 뒷다리로 멀리뛰기를 학습함
- HalfCheetah on MuJoCo (점수 1,623) — 치타가 뒤집힌 채 전진(위에서 설명한 문제)
- Ant on PyBullet (점수 2,560) — A2C보다 훨씬 안정적으로 전진
- Ant on MuJoCo (점수 5,108) — 훨씬 빠르지만, 무게가 PyBullet보다 가볍게 느껴짐

---

## 4. TRPO (Trust Region Policy Optimization, 신뢰 영역 정책 최적화)

TRPO는 2015년 버클리 연구진(Schulman 등)이 제안했으며, PPO보다 먼저 나온 방법으로 확률적 정책 경사 최적화의 안정성과 일관성을 개선하는 방향으로 다양한 제어 문제에서 좋은 결과를 냈다.

> [!warning] 수학이 무겁다
> 이 논문과 방법은 상당히 수학적으로 무겁다. 세부 사항을 완벽히 이해하지 못해도 괜찮다 — 구현도 제약 최적화 문제를 효율적으로 풀기 위해 **켤레 그래디언트(conjugate gradient)** 방법을 쓰는데, 이 역시 쉽지 않다.

### 4.1 이론 — 방문 빈도와 대리 목적함수

TRPO는 먼저 정책 하의 **할인된 상태 방문 빈도(discounted visitation frequency)**를 다음과 같이 정의한다.

$$\rho_\pi(s) = P(s_0=s) + \gamma P(s_1=s) + \gamma^2 P(s_2=s) + \dots$$

여기서 $P(s_i=s)$는 샘플링된 궤적들에서 상태 $s$가 위치 $i$에 나타날 확률이다. 즉 *"이 정책을 따를 때, 각 상태를 (할인된 가중치로) 얼마나 자주 방문하는가"*를 나타낸다.

이어서 TRPO는 최적화 목적함수를 다음처럼 정의한다.

$$L_\pi(\tilde\pi) = \eta(\pi) + \sum_s \rho_\pi(s)\sum_a \tilde\pi(a|s)A_\pi(s,a)$$

여기서

$$\eta(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty}\gamma^t r(s_t)\right]$$

는 정책의 **기대 할인 보상**이고, $\tilde\pi = \arg\max_a A_\pi(s,a)$는 각 상태에서 어드밴티지가 가장 큰 행동을 고르는 **결정론적 정책**을 뜻한다.

큰 정책 업데이트 문제를 해결하기 위해, TRPO는 옛 정책과 새 정책 사이의 **최대 KL 발산**에 대한 추가 제약을 건다.

$$\bar D_{KL}(\pi_{\theta_{old}}, \pi_\theta) \le \delta$$

말로 풀면: *"목적함수 $L_\pi$를 최대화하되, 옛 정책과 새 정책의 차이(KL 발산)가 $\delta$를 넘지 않는 범위 안에서만 움직여라."* 이것이 바로 챕터 도입부에서 말한 **신뢰 영역** 제약 그 자체다. (KL 발산의 정의와 계산법은 [[KL 발산 Kullback-Leibler Divergence]] 참고. Chapter 4와 Chapter 11에서도 등장했다.)

$$D_{KL}(P\|Q) = -\sum_i p_i \log q_i$$

### 4.2 구현

깃허브에 공개된 대부분의 TRPO 구현체는, 원조인 John Schulman의 구현(`https://github.com/joschu/modular_rl`)에서 파생됐다. 이 책의 버전도 크게 다르지 않으며, 켤레 그래디언트 방법을 구현한 핵심 함수는 `https://github.com/ikostrikov/pytorch-trpo` 저장소의 것을 사용한다.

전체 예제는 `03_train_trpo.py`와 `lib/trpo.py`에 있고, 학습 루프는 PPO 예제와 매우 비슷하다 — 정해진 길이의 궤적을 샘플링하고, PPO 절에서 설명한 GAE 스무딩 어드밴티지 추정을 그대로 사용한다(역사적으로는 이 추정 방식이 TRPO 논문에서 먼저 제안됐다).

먼저 크리틱을 MSE 손실로 한 스텝 학습시키고, 이어서 TRPO 업데이트를 한 스텝 수행한다. TRPO 업데이트는 (1) 켤레 그래디언트로 개선 방향을 찾고, (2) 그 방향으로 라인서치(line search)를 수행해 원하는 KL 발산 제약을 지키는 스텝 크기를 찾는 과정으로 구성된다.

```python
opt_crt.zero_grad()
value_v = net_crt(traj_states_v)
loss_value_v = F.mse_loss(value_v.squeeze(-1), traj_ref_v)
loss_value_v.backward()
opt_crt.step()
```

- 크리틱 학습은 PPO와 완전히 동일한 MSE 방식.

TRPO 스텝을 수행하려면 두 함수가 필요하다. 하나는 **현재 액터 정책의 손실**(PPO와 같은 비율 × 어드밴티지 방식)을 계산하고, 다른 하나는 **옛 정책과 현재 정책 사이의 KL 발산**을 계산한다.

```python
def get_loss():
    mu_v = net_act(traj_states_v)
    logprob_v = model.calc_logprob(mu_v, net_act.logstd, traj_actions_v)
    dp_v = torch.exp(logprob_v - old_logprob_v)
    action_loss_v = -traj_adv_v.unsqueeze(dim=-1)*dp_v
    return action_loss_v.mean()
```

- `dp_v`: PPO에서 본 것과 똑같은 중요도 샘플링 비율 $r_t(\theta)$.
- `action_loss_v`: 어드밴티지 × 비율에 마이너스를 붙인 값(최대화하려는 목적함수를 손실로 바꾼 것). 단, TRPO는 이 값에 **클리핑을 적용하지 않는다** — 대신 아래의 KL 제약으로 스텝 크기를 통제한다.

```python
def get_kl():
    mu_v = net_act(traj_states_v)
    logstd_v = net_act.logstd
    mu0_v = mu_v.detach()
    logstd0_v = logstd_v.detach()
    std0_v = torch.exp(logstd0_v).detach()
    std_v = torch.exp(logstd_v).detach()
    v = (std0_v ** 2 + (mu0_v - mu_v) ** 2) / (2.0 * std_v ** 2)
    kl = logstd_v - logstd0_v + v - 0.5
    return kl.sum(1, keepdim=True)
```

- 두 정규분포(옛 정책과 새 정책, 둘 다 평균 `mu`·표준편차 `std`로 표현됨) 사이의 KL 발산을 **닫힌 형태(closed-form) 공식**으로 계산한다. `.detach()`로 옛 정책 쪽 값은 그래디언트가 흐르지 않도록 고정한다.

```python
trpo.trpo_step(net_act, get_loss, get_kl, args.maxkl, TRPO_DAMPING, device=device)
```

- 이 한 줄이 실제 TRPO의 핵심 로직을 수행한다: 켤레 그래디언트로 개선 방향을 구하고, `args.maxkl`(최대 허용 KL 발산, 즉 $\delta$)을 넘지 않도록 라인서치로 실제 스텝 크기를 찾아 정책을 업데이트한다.

> [!tip] PPO는 결국 "간소화된 TRPO"
> 저자가 정리하듯, **PPO는 사실상 TRPO의 아이디어를 그대로 가져오되, 복잡한 켤레 그래디언트·라인서치 대신 정책 비율을 그냥 클리핑하는 훨씬 단순한 방법으로 정책 업데이트 크기를 제한한 것**이다. 같은 목표(신뢰 영역 유지)를 서로 다른 난이도의 도구로 이룬 셈이다.

### 4.3 결과

HalfCheetah 환경에서 TRPO는 PPO와 A2C보다 더 나은 보상에 도달했다. MuJoCo에서는 특히 인상적이었다 — 최고 보상이 5,000을 넘겼다.

![[fig_16_10.png]]
*그림 16.10 — HalfCheetah on PyBullet의 A2C·TRPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

![[fig_16_11.png]]
*그림 16.11 — HalfCheetah on MuJoCo의 A2C·TRPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

하지만 Ant 환경에서는 수렴이 훨씬 불안정했다.

![[fig_16_12.png]]
*그림 16.12 — Ant on PyBullet의 A2C·TRPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

![[fig_16_13.png]]
*그림 16.13 — Ant on MuJoCo의 A2C·TRPO 학습 보상(왼쪽)과 테스트 보상(오른쪽) 비교*

가장 성능이 좋았던 TRPO 모델들:
- HalfCheetah on PyBullet (점수 2,419) — 앞다리 관절을 쓰지 않음
- HalfCheetah on MuJoCo (점수 5,753) — 정말 빠른 치타!
- Ant on PyBullet (점수 834) — 학습이 "제자리에 가만히 서기" 국소 최적에 갇힘
- Ant on MuJoCo (점수 993) — PyBullet과 마찬가지로 에이전트가 그냥 서서 움직이지 않음

---

## 5. ACKTR (Kronecker-factored Trust Region, 크로네커 인수분해 신뢰 영역)

세 번째로 비교할 방법인 ACKTR는 SGD 안정성 문제를 **다른 각도**에서 접근한다. Wu 등의 2017년 논문 *Scalable trust-region method for deep reinforcement learning using Kronecker-factored approximation*에서, 저자들은 **2차 최적화 방법**과 **신뢰 영역 접근**을 결합했다.

### 5.1 2차 최적화란?

2차 최적화 방법의 아이디어는, 함수의 **곡률(curvature)**, 즉 2차 도함수 정보를 활용해 SGD의 전통적인 1차 그래디언트 방식보다 더 나은 수렴을 얻는 것이다. 문제는 2차 도함수를 다루려면 보통 **헤시안 행렬(Hessian matrix)**을 만들고 역행렬을 구해야 하는데, 이 행렬이 지나치게 커질 수 있어서 실전에서는 어떤 형태로든 근사가 필요하다.

그 근사 방법 중 하나가 **크로네커 인수분해 근사 곡률(Kronecker-Factored Approximate Curvature, K-FAC)**이다. Martens와 Grosse가 2015년 논문 *Optimizing neural networks with Kronecker-factored approximate curvature*에서 제안했다. 이 방법의 자세한 설명은 이 책의 범위를 벗어난다.

### 5.2 구현

K-FAC 최적화기의 PyTorch 구현체는 많지 않다(안타깝게도 PyTorch 공식에는 포함돼 있지 않다). 저자가 아는 한 두 가지 정도가 있는데, Ilya Kostrikov의 것(`https://github.com/ikostrikov/pytorch-a2c-ppo-acktr`)과 Nicholas Gao의 것(`https://github.com/n-gao/pytorch-kfac`)이다. 저자는 전자만 실험해봤다.

Kostrikov의 K-FAC 구현을 가져와 기존 코드에 맞게 수정했고, Fisher 정보를 모으기 위해 추가로 `backward()` 호출이 필요했다. 크리틱은 A2C와 동일한 방식으로 학습된다. 전체 예제는 `05_train_acktr.py`에 있으며, A2C와 거의 동일하고 **옵티마이저만 다르다.**

### 5.3 결과

전반적으로 ACKTR는 두 환경, 두 물리 엔진 모두에서 **매우 불안정**했다. 하이퍼파라미터가 충분히 튜닝되지 않았거나, 구현에 버그가 있을 가능성도 있다.

![[fig_16_14.png]]
*그림 16.14 — HalfCheetah on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

![[fig_16_15.png]]
*그림 16.15 — HalfCheetah on MuJoCo의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

Ant 환경에서는 PyBullet에서 나쁜 결과를 보였고, MuJoCo에서는 보상 개선이 거의 없었다.

![[fig_16_16.png]]
*그림 16.16 — Ant on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

> [!warning] ACKTR는 이 챕터의 "반면교사"
> 이론적으로는 그럴듯한 2차 최적화 접근이지만, 실전 구현·튜닝의 난이도 때문에 결과가 가장 불안정했다. "이론이 우아하다고 실전에서도 항상 잘 되는 건 아니다"라는 교훈을 준다.

---

## 6. SAC (Soft Actor-Critic, 소프트 액터-크리틱)

마지막으로, 비교적 최근 방법인 **SAC**를 살펴본다. 버클리 연구진이 2018년 논문 *Soft actor-critic: Off-policy maximum entropy deep reinforcement learning*(Haarnoja 등)에서 제안했다. 현재 연속 제어(continuous control) 문제에서 가장 뛰어난 방법 중 하나로 널리 쓰인다.

SAC의 핵심 아이디어는 [[액터-크리틱과 어드밴티지|A2C 계열의 정책 경사]]보다는 **오히려 15장에서 다룬 DDPG 방법에 더 가깝다.**

### 6.1 엔트로피 정규화 (Entropy Regularization)

SAC의 중심 아이디어는 **엔트로피 정규화**다. 매 타임스텝마다, 그 시점의 정책의 [[엔트로피 보너스|엔트로피]]에 비례하는 **보너스 보상**을 추가로 준다. 수식으로는 다음과 같다.

$$\pi^* = \arg\max_\pi \mathbb{E}_{\tau\sim\pi}\left[\sum_{t=0}^{\infty}\gamma^t\big(R(s_t,a_t,s_{t+1}) + \alpha H(\pi(\cdot|s_t))\big)\right]$$

여기서 $H(P) = \mathbb{E}_{x\sim P}[-\log P(x)]$는 분포 $P$의 엔트로피다. 즉 **에이전트가 엔트로피(무작위성·다양성)가 최대인 상황에 놓이도록 보너스를 주는 것**인데, 이는 18장에서 다룰 발전된 탐험 기법들과 매우 비슷한 발상이다.

> [!tip] 비유 — "다양한 선택지를 유지하는 것 자체에 보상을 준다"
> 한 가지 정답만 고집하는 학생보다, 여러 풀이법을 골고루 시도해보는 학생에게 가산점을 주는 것과 비슷하다. 이렇게 하면 정책이 너무 일찍 한 가지 행동에만 확신을 갖고 굳어버리는 것을 막아, 자연스럽게 탐험이 유지된다.

### 6.2 클리핑된 더블-Q 트릭

추가로 SAC는 **클리핑된 더블-Q 트릭**을 쓴다 — 가치 함수 하나 외에, **Q값을 예측하는 신경망 두 개**를 학습시키고 벨만 근사에는 그중 **더 작은 값**을 사용한다. 이는 8장에서 다룬 Q값 과대추정(overestimation) 문제를 다루는 또 다른 방식이다.

결과적으로 SAC는 총 **네 개의 네트워크**를 학습시킨다: 정책 $\pi(s)$, 가치 $V(s,a)$, 그리고 두 개의 Q-네트워크 $Q_1(s,a)$, $Q_2(s,a)$.

- **Q-네트워크들**: 타깃 가치 네트워크를 이용한 벨만 근사로 MSE 목적함수로 학습. $y_q(r,s') = r + \gamma V_{tgt}(s')$ (에피소드가 끝나지 않은 스텝에 대해)
- **V-네트워크**: 다음 타깃으로 MSE 목적함수 학습. $y_v(s) = \min_{i=1,2}Q_i(s,\tilde a) - \alpha\log\pi_\theta(\tilde a|s)$, 여기서 $\tilde a$는 정책 $\pi_\theta(\cdot|s)$에서 샘플링한 행동.
- **정책 네트워크** $\pi_\theta$: DDPG 방식으로, 다음 목적함수를 최대화하도록 학습. $Q_1(s,\tilde a_\theta(s)) - \alpha\log\pi_\theta(\tilde a_\theta(s)|s)$, 여기서 $\tilde a_\theta$는 $\pi_\theta(\cdot|s)$에서 샘플링.

### 6.3 구현

`06_train_sac.py`에 구현이 있고, 모델은 `lib/model.py`에 정의된다.

- **ModelActor**: 이 챕터의 이전 예제들과 같은 정책. 다만 정책의 분산이 상태에 의존하지 않는 텐서 하나(`logstd`)라서, SAC의 학습 목적함수와 100% 맞아떨어지진 않는다. SAC의 핵심 아이디어인 엔트로피 정규화는 원래 **분산이 상태에 따라 파라미터화**되어야 온전히 구현되기 때문이다. 대신 모델 파라미터 수는 줄어든다. 궁금하다면 분산을 상태에 의존하게 확장해 "제대로 된" SAC를 구현해볼 수 있다.
- **ModelCritic**: 이전 예제들과 같은 가치 네트워크.
- **ModelSACTwinQ**: 상태와 행동을 입력받아 Q값을 예측하는 두 개의 네트워크.

**배치 언패킹 함수**: `lib/common.py`의 `unpack_batch_sac()` 함수가 궤적 배치를 받아 V-네트워크와 트윈 Q-네트워크의 타깃값을 계산한다.

```python
@torch.no_grad()
def unpack_batch_sac(batch: tt.List[ptan.experience.ExperienceFirstLast],
                      val_net: model.ModelCritic, twinq_net: model.ModelSACTwinQ,
                      policy_net: model.ModelActor, gamma: float, ent_alpha: float,
                      device: torch.device):
    states_v, actions_v, ref_q_v = unpack_batch_a2c(batch, val_net, gamma, device)

    mu_v = policy_net(states_v)
    act_dist = distr.Normal(mu_v, torch.exp(policy_net.logstd))
    acts_v = act_dist.sample()
    q1_v, q2_v = twinq_net(states_v, acts_v)
    ref_vals_v = torch.min(q1_v, q2_v).squeeze() - \
                 ent_alpha * act_dist.log_prob(acts_v).sum(dim=1)
    return states_v, actions_v, ref_vals_v, ref_q_v
```

- `@torch.no_grad()`: 이 함수 안의 계산은 타깃값을 만드는 용도라 그래디언트가 필요 없으므로, 계산 그래프를 만들지 않아 메모리·속도를 절약한다.
- `unpack_batch_a2c(...)`: 기존에 정의된 함수를 재사용해 상태·행동을 텐서로 바꾸고, Q-네트워크용 벨만 근사 기준값 `ref_q_v`를 얻는다.
- `act_dist = distr.Normal(mu_v, torch.exp(policy_net.logstd))`: 정책이 만드는 정규분포를 명시적으로 만든다.
- `acts_v = act_dist.sample()`: 이 분포에서 행동을 하나 샘플링한다.
- `q1_v, q2_v = twinq_net(states_v, acts_v)`: 두 Q-네트워크로 이 (상태, 행동) 쌍의 Q값을 각각 얻는다.
- `ref_vals_v = torch.min(q1_v, q2_v).squeeze() - ent_alpha * act_dist.log_prob(acts_v).sum(dim=1)`: **두 Q값 중 더 작은 값**에서, **엔트로피 보너스**(로그 확률에 비례, 계수 `ent_alpha`)를 빼서 V-네트워크의 타깃값을 만든다. 확률이 낮은(즉 엔트로피가 높은 쪽으로 다양한) 행동일수록 로그 확률이 더 음수라, 이를 빼주면 값이 더 커진다 — 즉 다양성에 보너스를 주는 것.

**학습 루프**: 위 함수를 이용해 V, Q, 정책까지 총 세 가지 다른 최적화 스텝을 수행한다.

```python
batch = buffer.sample(BATCH_SIZE)
states_v, actions_v, ref_vals_v, ref_q_v = common.unpack_batch_sac(
    batch, tgt_crt_net.target_model, twinq_net, act_net, GAMMA,
    SAC_ENTROPY_ALPHA, device)
```

- 리플레이 버퍼에서 배치를 뽑고, 타깃 크리틱 네트워크(`tgt_crt_net.target_model`)를 이용해 앞서 정의한 타깃값들을 계산한다.

**트윈 Q-네트워크 학습** — 같은 타깃값으로 두 네트워크 모두 최적화:

```python
twinq_opt.zero_grad()
q1_v, q2_v = twinq_net(states_v, actions_v)
q1_loss_v = F.mse_loss(q1_v.squeeze(), ref_q_v.detach())
q2_loss_v = F.mse_loss(q2_v.squeeze(), ref_q_v.detach())
q_loss_v = q1_loss_v + q2_loss_v
q_loss_v.backward()
twinq_opt.step()
```

- 두 Q-네트워크 각각의 MSE 손실을 합쳐서 동시에 역전파한다.

**크리틱(V) 학습** — 역시 단순 MSE:

```python
crt_opt.zero_grad()
val_v = crt_net(states_v)
v_loss_v = F.mse_loss(val_v.squeeze(), ref_vals_v.detach())
v_loss_v.backward()
crt_opt.step()
```

**액터(정책) 학습**:

```python
act_opt.zero_grad()
acts_v = act_net(states_v)
q_out_v, _ = twinq_net(states_v, acts_v)
act_loss = -q_out_v.mean()
act_loss.backward()
act_opt.step()
```

> [!warning] 이 구현은 엔트로피 항이 빠진 "사실상 DDPG"
> 위에서 제시한 공식대로라면 정책 손실에도 엔트로피 정규화 항이 들어가야 한다. 하지만 이 구현에서는 정책의 분산이 상태에 의존하지 않기 때문에(위 3절 참고), 정책 최적화 단계에서는 엔트로피 항을 생략해도 된다 — 그 결과 이 액터 학습 코드는 사실상 DDPG 학습과 동일하다.

### 6.4 결과

저자는 HalfCheetah와 Ant 환경에서 500만 관측(observation)을 기준으로 9~13시간 SAC를 학습시켰다. 결과는 다소 엇갈렸다.

- **샘플 효율성**은 PPO보다 좋았다. 예를 들어 HalfCheetah에서 SAC는 50만 관측만으로 보상 900에 도달했지만, PPO는 같은 정책에 도달하는 데 100만 관측 이상이 필요했다.
- MuJoCo 환경에서는 보상 **7,063**을 달성했는데, 이는 이 환경에서 사실상 **최고 기록(SOTA급)**에 해당한다.
- 반면 SAC는 **오프폴리시** 방법이라([[오프폴리시와 온폴리시|오프폴리시와 온폴리시]] 참고) 온폴리시 방법(PPO 등)보다 계산량이 훨씬 많아, 학습 **속도** 자체는 훨씬 느렸다. 저자의 머신에서 HalfCheetah 500만 프레임에 10시간이 걸린 반면, A2C는 같은 시간에 5,000만 관측을 처리했다.

> [!important] 온폴리시 vs 오프폴리시 — 속도와 샘플 효율의 트레이드오프
> 이 결과는 이 책 전체에서 여러 번 봐온 트레이드오프를 다시 보여준다. **환경과의 상호작용(관측 수집)이 빠르고 값싸다면** PPO 같은 온폴리시 방법이 최선일 수 있다. 하지만 **관측을 얻기 어렵거나 비싸다면**(예: 실제 로봇을 움직여야 하는 경우), 오프폴리시 방법이 더 적은 데이터로도 좋은 성능을 내지만 계산은 더 많이 필요하다.

HalfCheetah의 보상 다이내믹스:

![[fig_16_17.png]]
*그림 16.17 — HalfCheetah on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

![[fig_16_18.png]]
*그림 16.18 — HalfCheetah on MuJoCo의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

Ant 환경에서의 결과는 훨씬 나빴다 — 점수를 보면 학습된 정책이 거의 제대로 서지도 못하는 수준이다.

![[fig_16_19.png]]
*그림 16.19 — Ant on PyBullet의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

![[fig_16_20.png]]
*그림 16.20 — Ant on MuJoCo의 학습 보상(왼쪽)과 테스트 보상(오른쪽)*

가장 성능이 좋았던 SAC 모델들:
- HalfCheetah on PyBullet (점수 1,765) — 다소 어설픈 움직임
- HalfCheetah on MuJoCo (점수 7,063) — 매우 인상적인, 초고속 치타
- Ant on PyBullet (점수 630) — 몇 걸음 걷다가 멈춰버림

---

## 7. 전체 결과 종합

저자가 정리한, 각 방법이 얻은 최고 보상을 모은 표는 다음과 같다.

| 방법 | HalfCheetah – PyBullet | HalfCheetah – MuJoCo | Ant – PyBullet | Ant – MuJoCo |
|---|---|---|---|---|
| A2C | 2,189 | 4,718 | 2,425 | **5,380** |
| PPO | **2,567** | 1,623 | **2,560** | 5,108 |
| TRPO | 2,419 | **5,753** | 834 | 993 |
| ACKTR | 250 | 3,100 | 1,820 | — |
| SAC | 1,765 | **7,063** | 630 | — |

*표 16.1 — 요약 표(원서 Table 16.1). 굵게 표시된 값이 각 환경별 최고 기록.*

이 표에서 볼 수 있듯, **어느 하나가 모든 환경에서 압도적으로 이기는 "만능 승자"는 없다.** 어떤 방법은 어떤 환경에서 잘 되고, 다른 환경에서는 나쁜 결과를 보인다. 다만 A2C와 PPO는 비교적 **일관되게(consistently)** 좋은 결과를 낸다고 볼 수 있다 — 모든 환경에서 그럭저럭 괜찮은 성적을 냈기 때문이다. (MuJoCo에서 PPO가 "백플립 치타"로 낮은 점수를 받은 건 나쁜 초기 시드 탓일 가능성이 있고, 재학습하면 더 좋은 정책이 나올 수 있다.)

---

## 8. 요약

이 챕터에서는 확률적 정책 경사의 **안정성을 개선**하기 위한 세 가지 방법(PPO, TRPO, ACKTR)을 A2C 구현과 비교했다. 15장에서 다룬 DDPG·D4PG와 함께, 이 방법들은 **연속 제어(continuous control) 문제**를 다루는 기본 도구 상자를 이룬다. 마지막으로 DDPG의 확장인 비교적 최근 오프폴리시 방법 **SAC**도 살펴봤다 — 이 주제의 표면만 살짝 훑었지만, 더 깊이 파고들고 싶다면 좋은 출발점이 될 것이다. 이런 방법들은 로보틱스와 관련 분야에서 폭넓게 쓰인다.

핵심을 정리하면:
1. 정책 업데이트가 너무 크면 되돌릴 수 없는 악순환에 빠질 수 있어, **신뢰 영역(trust region)**이라는 개념으로 업데이트 크기를 제한한다.
2. **PPO**는 새·옛 정책의 비율을 클리핑하는 간단한 방법으로 이를 구현한다.
3. **TRPO**는 KL 발산 제약을 명시적으로 걸고, 켤레 그래디언트·라인서치로 이를 정확히 만족시킨다(더 정교하지만 훨씬 복잡하다).
4. **ACKTR**는 2차 최적화(K-FAC)로 다른 각도에서 접근하지만, 실전에서는 불안정했다.
5. **SAC**는 엔트로피 정규화와 트윈-Q 트릭을 결합한 오프폴리시 방법으로, 샘플 효율은 좋지만 계산 비용이 크다.

다음 챕터에서는 완전히 다른 종류의 RL 방법인 **블랙박스(black-box)** 또는 **그래디언트-프리(gradient-free)** 방법으로 넘어간다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[GAE 일반화된 어드밴티지 추정]]
- [[중요도 샘플링 비율과 PPO 클리핑]]
- [[KL 발산 Kullback-Leibler Divergence]]
- [[액터-크리틱과 어드밴티지]]
- [[오프폴리시와 온폴리시]]
- [[엔트로피 보너스]]
- [[정책 경사 Policy Gradient]]
- [[활성화함수]]
- [[벨만 방정식 Bellman Equation]]

## 한눈에 보는 개념 지도
| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 신뢰 영역 | — | 업데이트를 믿고 따라가도 안전하다고 보장되는 범위 |
| 중요도 샘플링 비율 | $r_t(\theta)$ | 새 정책이 옛 정책보다 이 행동을 얼마나 더/덜 선호하는가 |
| PPO 클리핑 계수 | $\epsilon$ | 비율을 자를 범위 $[1-\epsilon, 1+\epsilon]$ (보통 0.2) |
| GAE 람다 | $\lambda$ | 어드밴티지 추정의 분산-편향 절충 정도 (보통 0.95) |
| KL 발산 제약 | $\delta$ | TRPO가 허용하는 최대 정책 변화량 |
| 어드밴티지 | $A_t$ | 이 행동이 평균보다 얼마나 더 좋았는가 |
| 엔트로피 보너스 계수 | $\alpha$ | SAC에서 다양성(엔트로피)에 주는 보상 가중치 |
| Q-네트워크 | $Q_1, Q_2$ | SAC의 트윈 Q값 추정 네트워크(과대추정 방지용 최솟값 사용) |
