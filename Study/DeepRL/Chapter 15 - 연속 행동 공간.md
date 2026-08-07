---
title: "Chapter 15 — 연속 행동 공간 (Continuous Action Space)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 15
tags: [DeepRL, 강화학습, 연속행동, DDPG, D4PG, 액터크리틱]
---

# Chapter 15 · 연속 행동 공간 (Continuous Action Space)

> [!abstract] 이 챕터를 한 문장으로
> 지금까지는 "좌/우/점프"처럼 **몇 개 중 하나를 고르는** 행동만 다뤘지만, 로봇 팔의 각도나 자동차 핸들처럼 **실수값을 정해야 하는** 문제에서는 DQN의 "모든 후보를 훑어 최고를 고른다"는 전략 자체가 불가능해진다. 이 챕터에서는 **A2C → [[결정론적 정책 경사 DDPG|DDPG]] → [[D4PG Distributed Distributional DDPG|D4PG]]** 순서로 세 가지 방법을 네발 로봇 시뮬레이션에 적용해 보고, D4PG가 가장 좋은 성능을 낸다는 것을 확인한다.

---

## 들어가며 — 이 챕터부터는 "고급 RL"이다

이 챕터는 책의 **심화(advanced) 파트**를 여는 장이다. 지금까지 본 예제는 전부 **이산 행동 공간**(discrete action space)이었다. 그래서 자칫 "RL = 이산 행동을 고르는 것"이라 착각하기 쉽지만, 이는 우리가 다룬 문제(아타리 게임, 간단한 고전 RL 문제)를 우연히 그렇게 골랐을 뿐이다. 실제로는 **선택지가 유한한 이산 행동보다 훨씬 많은 문제가 연속값을 다뤄야 한다.**

특히 **로봇공학, 제어 문제**처럼 **물리적인 대상과 상호작용**해야 하는 분야에서는 연속 행동 공간이 필수다. 예를 들어 관절이 하나뿐인 간단한 로봇도, "이 관절을 몇 도로 움직여라" 또는 "얼마만큼의 힘을 가해라"를 정해야 한다. 13.5도와 13.512도는 서로 다른 결과를 낳는, **잠재적으로 무한히 많은** 값 중 하나다. (물론 현실에는 물리적 한계가 있어 무한 정밀도까지는 못 쓰지만, 가능한 값의 범위 자체는 매우 크다.)

> [!tip] 익숙한 문제도 사실은 연속일 수 있다
> [[Chapter 14 - 웹 내비게이션]]에서 다룬 "브라우저에서 마우스 클릭하기"도, 클릭 좌표 $(x, y)$를 **두 개의 연속값**으로 볼 수 있다. 좌표 $(x+1, y+1)$을 클릭하는 것과 $(x, y)$를 클릭하는 것은 대부분의 작업에서 결과가 거의 같으므로, 이런 표현이 오히려 더 자연스럽고 압축적이다.

이 챕터에서 배울 것:
1. 연속 행동 공간이 무엇이고, 왜 중요하며, 이산 행동 공간과 어떻게 다른지, Gym API에서 어떻게 표현되는지
2. RL로 하는 **연속 제어(continuous control)**의 전반적인 흐름
3. **네발 로봇**을 걷게 만드는 문제에 **세 가지 알고리즘**(A2C, DDPG, D4PG)을 직접 적용해 비교

---

## 1. 왜 연속 공간이 필요한가?

지금까지 본 예제들은 전부 **이산적이고 상호 배타적인** 선택지(예: `{좌, 우}`) 중 하나를 고르는 문제였다. 하지만 물리적인 조인트를 제어하는 로봇, 냉난방 조절기 등 **연속 행동 공간**이 훨씬 자연스러운 문제가 많다.

RL 방법(A2C나 DQN 등)을 이런 문제에 적용할 수는 있지만, 그 전에 **몇 가지 고려할 세부사항**이 있다. 이 챕터는 바로 그 세부사항들을 다룬다.

## 2. 행동 공간 (The Action Space)

**이산 행동 공간**과 **연속 행동 공간**의 근본적 차이는 바로 "연속성"이다([[이산 행동과 연속 행동]] 참고).

- 이산 행동: 서로 배타적인 옵션들의 집합에서 하나를 고름 (예: `{left, right}`, 원소 2개).
- 연속 행동: 어떤 범위(예: $[0, 1]$) 안의 **값**을 가짐. 이 범위 안에는 $0.5$, $\frac{\sqrt{3}}{2}$, $\frac{\pi^3}{e^7}$처럼 무한히 많은 원소가 있다. 매 타임스텝마다 에이전트는 **구체적인 값**을 정해서 환경에 넘겨야 한다.

Gym에서 연속 행동 공간은 `gym.spaces.Box` 클래스로 표현된다. 이는 [[관측공간과 행동공간(Space)]]에서 봤던, 값의 집합을 형태(shape)와 범위(bounds)로 나타내는 그 클래스다. 예를 들어 아타리 에뮬레이터의 관측값은 `Box(low=0, high=255, shape=(210, 160, 3))` — 즉 0~255 범위의 값 100,800개(210×160×3 텐서)로 표현됐다.

이 챕터에서 쓸 네발 로봇 환경은 **8개의 연속 행동**을 갖는다(다리마다 2개, 다리가 4개). 행동 공간은 `Box(low=-1, high=1, shape=(8,))` — 즉 매 타임스텝마다 $-1$~$1$ 범위의 값 8개를 정해야 로봇을 제어할 수 있다.

이 경우 `env.step()`에 넘기는 행동은 더 이상 정수 하나가 아니라, **어떤 형태(shape)를 가진 NumPy 벡터**가 된다. 참고로 이산 행동과 연속 행동이 섞인 더 복잡한 경우는 `gym.spaces.Tuple` 클래스로 표현할 수 있다.

## 3. 환경 (Environments)

연속 행동 공간을 포함하는 환경 대부분은 **물리적 세계**와 관련이 있어서, 보통 **물리 시뮬레이션(physics simulation)** 을 사용한다. 간단한 오픈소스 도구부터 복잡한(유체·연소·강도 시뮬레이션까지 가능한) 상용 패키지까지 다양하다.

로보틱스 분야에서 가장 유명한 패키지 중 하나가 **MuJoCo**(Multi-Joint dynamics with Contact, https://www.mujoco.org)다. 이 물리 엔진은 시스템의 구성요소와 그 상호작용·속성을 정의하면, 시뮬레이터가 알아서 (위치·속도·가속도 등의) 값을 계산해 준다. 그래서 다리 여러 개 달린 로봇, 로봇 팔, 인간형 로봇처럼 복잡한 시스템을 정의하고, 그 관측값을 RL 에이전트에 넘겨주고 행동을 받아올 수 있는 이상적인 놀이터다.

> [!note] MuJoCo의 역사
> MuJoCo는 오랫동안 **유료 상용 패키지**였다(체험판·교육용 라이선스는 있었지만 대중적으로 쓰이긴 힘들었다). 그런데 2022년 **DeepMind가 MuJoCo를 인수해서 소스 코드를 전면 공개**했다. Farama Gymnasium은 `gymnasium[mujoco]` 패키지만 설치하면 여러 MuJoCo 환경을 기본으로 제공한다.

MuJoCo 외에도 다른 물리 시뮬레이터들이 있다. 그중 유명한 것이 **처음부터 오픈소스였던 PyBullet**(https://pybullet.org/)이다. 이 챕터의 실험은 PyBullet으로 진행하고, 책 뒷부분에서 MuJoCo도 다뤄볼 것이다. PyBullet 설치는 다음과 같다.

```
pip install pybullet==3.2.6
```

> [!warning] 버전 호환성 주의
> PyBullet은 아직 Gymnasium API로 업데이트되지 않았다. 그래서 호환을 위해 **구버전 OpenAI Gym**도 함께 설치해야 한다.
> ```
> pip install gym==0.25.1
> ```
> 0.25.1을 쓰는 이유는, 그보다 최신 버전의 OpenAI Gym은 최신 PyBullet과 호환되지 않기 때문이다.

### 환경 확인해 보기 (`01_check_env.py`)

다음 코드는 PyBullet이 잘 동작하는지 확인하고, 이 챕터의 실험 대상인 환경을 화면에 띄워 본다.

```python
import gymnasium as gym

ENV_ID = "MinitaurBulletEnv-v0"
ENTRY = "pybullet_envs.bullet.minitaur_gym_env:MinitaurBulletEnv"
RENDER = True

if __name__ == "__main__":
    gym.register(ENV_ID, entry_point=ENTRY, max_episode_steps=1000,
                  reward_threshold=15.0, disable_env_checker=True)
    env = gym.make(ENV_ID, render=RENDER)

    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)
    print(env)
    print(env.reset())
    input("Press any key to exit\n")
    env.close()
```

한 줄씩 설명하면:
- PyBullet의 `MinitaurBulletEnv`는 Gymnasium에 자동 등록되어 있지 않으므로, `gym.register()`로 직접 등록해야 한다. `entry_point`는 실제 환경 클래스가 어디 있는지 알려주는 경로다.
- `max_episode_steps=1000`: 한 에피소드가 아무리 길어도 1,000스텝이면 강제로 끝난다는 시간 제한.
- `reward_threshold=15.0`: 이 보상 이상을 얻으면 "문제를 풀었다"고 인정하는 기준값.
- `disable_env_checker=True`: Gymnasium이 새 환경마다 하는 엄격한 API 검사를 꺼서, 구버전 PyBullet 환경과의 호환 문제를 피한다.
- 나머지는 익숙한 패턴이다 — 관측·행동 공간을 출력해 보고, `env.reset()`으로 초기 상태를 확인한다.

이 유틸리티를 실행하면 GUI 창이 뜨고, 우리가 걷게 만들 **네발 로봇**을 볼 수 있다.

![[fig_15_1.png]]
*그림 15.1 — PyBullet GUI 안의 Minitaur 환경. 네 다리 로봇이 평평한 바닥 위에 놓여 있다*

이 환경은 관측값으로 **28개의 숫자**를 준다. 각각 로봇의 다양한 물리량(속도·위치·가속도)에 대응한다(자세한 내용은 `MinitaurBulletEnv-v0`의 소스 코드 참고). 행동 공간은 모터를 제어하는 **8개의 숫자**다 — 다리마다 2개씩(무릎 관절 하나씩), 다리는 4개이므로 총 8개. 이 환경의 **보상**은 "로봇이 이동한 거리 − 사용한 에너지"로 정의된다. 즉 **에너지를 아끼면서 멀리 갈수록** 보상이 커진다.

---

## 4. 첫 번째 방법 — A2C

가장 먼저 시도해 볼 방법은 [[A2C와 A3C]]다. Part III에서 이미 다뤄본 방법이라, 연속 행동 영역으로 옮기기가 매우 쉽다는 장점이 있다.

### 4.1 정책을 어떻게 표현할까

**A2C의 핵심 아이디어**를 복습하면, 정책의 그래디언트를 $\nabla J = \nabla_\theta \log \pi_\theta(a|s)(R - V_\theta(s))$로 추정하는 것이었다. 정책 $\pi_\theta(s)$는 상태가 주어졌을 때 행동들의 확률 분포를 내놓아야 하고, $V_\theta(s)$는 상태 가치를 추정하는 [[액터-크리틱과 어드밴티지|크리틱]]으로, 벨만 방정식으로 추정한 값과의 [[손실함수의 종류|MSE 손실]]로 학습된다. 탐험을 돕기 위해 보통 엔트로피 보너스 $L_H = \pi_\theta(s)\log\pi_\theta(s)$가 손실에 더해진다([[엔트로피 보너스]] 참고).

이 골격 자체는 연속 행동에서도 그대로 유지된다. **크리틱(가치 head)은 전혀 바뀌지 않는다.** 바뀌는 것은 오직 **정책(policy)을 어떻게 표현하느냐**뿐이다.

이산 행동 문제에서는 "행동에 대한 확률 분포"라는 표현이 자연스러웠다. 그런데 연속 행동은 보통 **여러 개의 행동**이 있고, 각각 어떤 범위의 값을 가질 수 있다. 이때 가장 단순한 방법은 그냥 **각 행동의 값을 그대로 출력**하는 것이다. 하지만 이 값은 [[벨만 방정식 Bellman Equation|상태의 가치]] $V(s)$와는 완전히 다른 개념임을 주의해야 한다 — 자동차 조향의 예를 들면, **행동값**은 "핸들을 몇 도 꺾을지"이고, **상태 가치**는 "그 상태에서 앞으로 얼마나 더 갈 수 있는가(할인된 기대 보상)"다. 서로 전혀 다른 것이다.

앞서 [[Chapter 11 - 정책 경사법]]의 "정책 표현" 절에서 다뤘듯, 행동을 하나의 확정된 값으로만 내놓는 표현은 **탐험(exploration)** 측면에서 불리하다. 그보다 훨씬 나은 선택은 **확률적인 표현**이다 — 즉 신경망이 **가우시안(정규) 분포**의 파라미터를 출력하게 만드는 것이다. 행동이 $N$개라면, 신경망은 **평균값 벡터** $\mu$(크기 $N$)와 **분산 벡터** $\sigma^2$(크기 $N$)를 출력한다. 이러면 우리 정책은 서로 독립인(uncorrelated) $N$개의 정규분포 확률변수로 표현되고, 신경망이 각 변수의 평균·분산을 결정하게 된다.

정규분포의 확률밀도함수(PDF)는 정의상 다음과 같다.

$$f(x|\mu,\sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}}e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

이 식을 직접 써서 확률을 구할 수도 있지만, **수치적 안정성**을 위해 로그를 취해서 $\log\pi_\theta(a|s)$를 미리 간단히 정리해 두는 편이 낫다. 정리하면 다음과 같다.

$$\log \pi_\theta(a|s) = -\frac{(x-\mu)^2}{2\sigma^2} - \log\sqrt{2\pi\sigma^2}$$

읽는 법: 첫째 항은 "실제 취한 행동 $x$가 평균 $\mu$에서 얼마나 멀리 떨어져 있는지"를 분산으로 정규화해 나타낸 것(가까울수록 로그확률이 커짐), 둘째 항은 분포의 폭에 따른 정규화 상수다.

또한 가우시안 분포의 **엔트로피**(탐험 보너스에 쓰이는)는 미분 엔트로피 정의로부터 $\ln\sqrt{2\pi e \sigma^2}$로 구할 수 있다.

이제 A2C를 구현하는 데 필요한 준비가 다 됐다.

### 4.2 구현

전체 소스는 `02_train_a2c.py`, `lib/model.py`, `lib/common.py`에 있다. 기존과 겹치는 부분은 생략하고, 다른 부분만 살펴본다.

**모델**(`lib/model.py`):

```python
HID_SIZE = 128

class ModelA2C(nn.Module):
    def __init__(self, obs_size: int, act_size: int):
        super(ModelA2C, self).__init__()

        self.base = nn.Sequential(
            nn.Linear(obs_size, HID_SIZE),
            nn.ReLU(),
        )
        self.mu = nn.Sequential(
            nn.Linear(HID_SIZE, act_size),
            nn.Tanh(),
        )
        self.var = nn.Sequential(
            nn.Linear(HID_SIZE, act_size),
            nn.Softplus(),
        )
        self.value = nn.Linear(HID_SIZE, 1)

    def forward(self, x: torch.Tensor):
        base_out = self.base(x)
        return self.mu(base_out), self.var(base_out), self.value(base_out)
```

한 줄씩 뜯어보면:
- 이산 행동 A2C와 달리, 이번 신경망은 **head가 3개**다. 처음 두 개는 행동의 **평균값**과 **분산**을, 마지막은 [[액터-크리틱과 어드밴티지|크리틱]] head로 상태 가치를 낸다.
- `self.mu`의 마지막 활성화함수는 **Tanh**([[활성화함수]] 참고)다. 출력을 $-1$~$1$ 범위로 눌러주는데, 마침 이 환경의 행동 범위와 정확히 일치한다.
- `self.var`의 마지막은 **Softplus**, 즉 $\log(1+e^x)$로 계산되는, ReLU를 매끄럽게 만든 모양의 함수다. 분산은 반드시 **양수**여야 하는데, Softplus가 이 조건을 자연스럽게 만족시켜 준다.
- `forward()`는 그냥 공통 몸통(`base`)을 거친 뒤 세 head에 각각 통과시키는 것뿐이다.

**PTAN 에이전트**(행동 변환 담당):

```python
class AgentA2C(ptan.agent.BaseAgent):
    def __init__(self, net: ModelA2C, device: torch.device):
        self.net = net
        self.device = device

    def __call__(self, states: ptan.agent.States, agent_states: ptan.agent.AgentStates):
        states_v = ptan.agent.float32_preprocessor(states)
        states_v = states_v.to(self.device)

        mu_v, var_v, _ = self.net(states_v)
        mu = mu_v.data.cpu().numpy()
        sigma = torch.sqrt(var_v).data.cpu().numpy()
        actions = np.random.normal(mu, sigma)
        actions = np.clip(actions, -1, 1)
        return actions, agent_states
```

이산 행동 문제에서는 `ptan.agent.DQNAgent`나 `ptan.agent.PolicyAgent`를 그대로 가져다 썼지만, 연속 행동 문제는 우리만의 에이전트 클래스를 새로 만들어야 한다. 어렵지 않다 — `ptan.agent.BaseAgent`를 상속받아 `__call__` 메서드만 오버라이드하면 된다.

- 신경망에서 평균(`mu`)과 분산(`var_v`)을 얻는다.
- **분산의 제곱근**을 취해 표준편차 `sigma`를 구한다(정규분포의 정의가 표준편차를 요구하기 때문).
- `np.random.normal(mu, sigma)`로 실제 행동을 **샘플링**한다 — 즉 정규분포에서 주사위를 굴려 행동을 뽑는 것이다.
- `np.clip(actions, -1, 1)`: 뽑힌 값이 환경의 허용 범위 $-1$~$1$을 벗어나지 않도록 잘라낸다.
- `agent_states`는 이번엔 쓰지 않지만, `BaseAgent`가 에이전트의 상태(state)를 유지할 수 있게 지원하는 자리라서 그대로 반환해 둔다. 이 기능은 다음 절의 DDPG에서 [[오른슈타인-울렌벡 노이즈 OU Process|OU 프로세스]]로 무작위 탐험을 구현할 때 요긴하게 쓰인다.

모델과 에이전트가 준비됐으니, 이제 학습 과정(`02_train_a2c.py`)을 보자. 학습 루프와 두 함수로 구성된다. 먼저 **테스트 함수**부터 본다 — 모델을 주기적으로 별도의 테스트 환경에서 평가한다. 테스트할 때는 탐험이 필요 없으므로, 무작위 샘플링 없이 **신경망이 돌려주는 평균값을 그대로** 행동으로 쓴다.

```python
def test_net(net: model.ModelA2C, env: gym.Env, count: int = 10,
             device: torch.device = torch.device("cpu")):
    rewards = 0.0
    steps = 0
    for _ in range(count):
        obs, _ = env.reset()
        while True:
            obs_v = ptan.agent.float32_preprocessor([obs])
            obs_v = obs_v.to(device)
            mu_v = net(obs_v)[0]
            action = mu_v.squeeze(dim=0).data.cpu().numpy()
            action = np.clip(action, -1, 1)
            obs, reward, done, is_tr, _ = env.step(action)
            rewards += reward
            steps += 1
            if done or is_tr:
                break
    return rewards / count, steps / count
```

- `net(obs_v)[0]`: 신경망의 세 출력(`mu`, `var`, `value`) 중 첫 번째, 즉 평균값만 취한다. 탐험용 무작위성은 필요 없으니 분산은 아예 무시.
- 나머지는 익숙한 에피소드 진행 루프다. `count`(기본 10)개의 에피소드를 돌려 평균 보상·평균 스텝 수를 반환한다.

두 번째 함수는 취한 행동의 로그 확률을 계산하는 것으로, 앞서 유도한 공식을 그대로 코드로 옮긴 것이다.

$$\log \pi_\theta(a|s) = -\frac{(x-\mu)^2}{2\sigma^2} - \log\sqrt{2\pi\sigma^2}$$

```python
def calc_logprob(mu_v: torch.Tensor, var_v: torch.Tensor, actions_v: torch.Tensor):
    p1 = - ((mu_v - actions_v) ** 2) / (2*var_v.clamp(min=1e-3))
    p2 = - torch.log(torch.sqrt(2 * math.pi * var_v))
    return p1 + p2
```

- `p1`: 공식의 첫 항. `torch.clamp(min=1e-3)`로 분산이 너무 작아져 **0으로 나누는 사고**가 나지 않도록 하한선을 걸어둔다.
- `p2`: 공식의 둘째 항.
- 둘을 더하면 그대로 로그확률이 된다.

훈련 루프는 액터·에이전트를 만들고, 2-스텝 경험 소스와 옵티마이저를 초기화한다. 하이퍼파라미터는 다음과 같다(크게 조정하지 않았으므로 개선의 여지가 많다).

```python
GAMMA = 0.99
REWARD_STEPS = 2
BATCH_SIZE = 32
LEARNING_RATE = 5e-5
ENTROPY_BETA = 1e-4

TEST_ITERS = 1000
```

수집된 배치에 대해 최적화 스텝을 수행하는 코드는 [[Chapter 12 - 액터-크리틱 A2C와 A3C]]에서 구현한 A2C 학습과 거의 같다. 차이는 오직 `calc_logprob()` 함수를 쓴다는 것과, 엔트로피 보너스의 계산식이 다르다는 점뿐이다.

```python
states_v, actions_v, vals_ref_v = common.unpack_batch_a2c(
    batch, net, device=device, last_val_gamma=GAMMA ** REWARD_STEPS)
batch.clear()

optimizer.zero_grad()
mu_v, var_v, value_v = net(states_v)

loss_value_v = F.mse_loss(value_v.squeeze(-1), vals_ref_v)
adv_v = vals_ref_v.unsqueeze(dim=-1) - value_v.detach()
log_prob_v = adv_v * calc_logprob(mu_v, var_v, actions_v)
loss_policy_v = -log_prob_v.mean()
ent_v = -(torch.log(2*math.pi*var_v) + 1)/2
entropy_loss_v = ENTROPY_BETA * ent_v.mean()

loss_v = loss_policy_v + entropy_loss_v + loss_value_v
loss_v.backward()
optimizer.step()
```

- `loss_value_v`: 크리틱의 예측(`value_v`)과 벨만 방정식으로 계산한 목표값(`vals_ref_v`) 사이의 [[손실함수의 종류|MSE]].
- `adv_v`: [[액터-크리틱과 어드밴티지|어드밴티지]] $A = R - V(s)$. 여기서 `value_v.detach()`로 크리틱 쪽 그래디언트를 끊어, 정책 손실이 크리틱 가중치에 영향을 주지 않게 한다.
- `log_prob_v`: 어드밴티지에 로그확률을 곱한 것 — 정책 그래디언트의 핵심 항.
- `loss_policy_v`: 부호를 뒤집어(경사 상승 → 경사 하강으로) 최종 정책 손실을 만든다.
- `entropy_loss_v`: 앞서 유도한 가우시안 엔트로피 공식을 이용한 탐험 보너스.
- 셋을 모두 더한 `loss_v`로 역전파 후 옵티마이저가 한 스텝 갱신한다.

`TEST_ITERS` 프레임마다 모델을 테스트하고, 그때까지의 최고 보상을 갱신하면 가중치를 저장한다.

### 4.3 결과

이 챕터에서 다룰 세 방법 중 A2C가 **최종 보상·수렴 속도 모두 가장 나쁘다.** 이는 아마도 **하나의 환경**만으로 경험을 모으기 때문일 것이다 — 이는 [[정책 경사 Policy Gradient|정책 경사(PG)]] 계열 방법의 약점 중 하나다. 그러니 A2C에 **여러 환경을 병렬로 돌리는** 것이 어떤 효과를 내는지 직접 확인해 보는 것도 좋은 연습이다.

학습은 `-n` 인자로 실행 이름을 주어 시작하며, 텐서보드에 기록할 새 디렉터리가 만들어진다. `--dev` 옵션으로 GPU를 쓸 수도 있지만, 입력 차원과 네트워크 크기가 워낙 작아서 속도 향상은 미미하다.

900만 프레임(16시간의 최적화)을 학습한 뒤, 테스트에서 최고 점수 **0.35**를 얻었다 — 그리 인상적이지 않은 결과다. 며칠 더 돌리면 조금 더 나아질 수도 있다. 훈련·테스트 동안의 보상과 에피소드 스텝 수는 다음 그래프와 같다.

![[fig_15_2.png]]
*그림 15.2 — 훈련 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

![[fig_15_3.png]]
*그림 15.3 — 테스트 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

> [!note] 에피소드 스텝 그래프가 말해주는 것
> "에피소드 스텝" 그래프(양쪽 다 오른쪽)는 학습에 쓴 에피소드의 평균 길이를 보여준다. 환경의 시간 제한이 1,000스텝이므로, 그보다 낮은 값은 대부분 **환경 내부의 안전 점검(self-damage check)** 때문에 에피소드가 도중에 중단됐다는 뜻이다. 대부분의 PyBullet 환경은 로봇이 스스로를 망가뜨리는 자세가 되면 내부적으로 시뮬레이션을 멈추도록 구현돼 있다.

### 4.4 모델 사용과 영상 기록

물리 시뮬레이터는 환경의 상태를 렌더링할 수 있으므로, 학습된 모델이 실제로 어떻게 움직이는지 볼 수 있다. A2C 모델을 위한 유틸리티가 `03_play_a2c.py`이며, 로직은 앞서 본 `test_net()` 함수와 같다.

실행할 때는 `-m` 옵션으로 모델 파일을, 선택적으로 `-r` 옵션으로 영상을 저장할 디렉터리 이름을 넘긴다(영상 저장은 [[Wrapper 래퍼 패턴|Chapter 2에서 다룬]] `RecordVideo` 래퍼를 사용).

시뮬레이션이 끝나면 스텝 수와 누적 보상이 출력된다. 저자가 학습한 최고의 A2C 모델은 보상 0.312를 얻었고, 영상은 단 2초짜리였다(https://youtu.be/s9BReDUtpQs). 마지막 프레임을 보면, 로봇이 균형을 잡는 데 어려움을 겪고 있음을 알 수 있다.

![[fig_15_4.png]]
*그림 15.4 — A2C 모델 시뮬레이션의 마지막 프레임. 로봇이 넘어져 있다*

---

## 5. 두 번째 방법 — 결정론적 정책 경사 (DDPG)

다음으로 볼 방법은 [[결정론적 정책 경사 DDPG|딥 결정론적 정책 경사(DDPG)]]다. 이는 액터-크리틱 방법이지만, **오프-폴리시(off-policy)** 라는 아주 좋은 성질을 갖고 있다. 여기서는 엄밀한 증명 대신 **간략화된 해석**을 다룬다. 방법의 핵심을 깊게 이해하고 싶다면 Silver 등의 논문 *Deterministic policy gradient algorithms*(2014)와 Lillicrap 등의 *Continuous control with deep reinforcement learning*(2015)을 참고하라.

### 5.1 A2C와 비교해서 이해하기

가장 쉬운 이해 방법은 이미 익숙한 A2C와 비교하는 것이다. A2C에서 액터는 **확률적 정책**을 추정한다 — 이산 행동이든, 방금 다룬 정규분포의 파라미터든, 결과적으로 **행동은 그 분포에서 샘플링**된다.

결정론적 정책 경사도 A2C 계열에 속하지만, 정책이 **결정론적**([[결정론적 정책 Deterministic Policy]])이다. 즉 상태로부터 취할 행동을 **바로 알려준다.** 이렇게 하면 [[벨만 방정식 Bellman Equation|Q값]]에 체인 룰을 적용할 수 있게 되고, **Q값을 최대화함으로써 정책도 함께 개선**할 수 있다. 이를 이해하려면, 연속 행동 영역에서 액터와 크리틱이 어떻게 연결되는지 봐야 한다.

먼저 **액터**부터 보자 — 둘 중 더 간단하다. 우리가 액터에게 원하는 것은, 주어진 각 상태에 대해 취할 행동이다. 연속 행동 영역에서는 모든 행동이 숫자이므로, 액터 신경망은 상태를 입력받아 $N$개의 값(행동 개수만큼)을 반환한다. 이 매핑은 결정론적이다 — 입력이 같으면 항상 같은 출력을 낸다(우리는 드롭아웃 같은 확률적 요소를 전혀 쓰지 않는, 평범한 피드포워드 신경망을 쓸 것이기 때문이다).

이제 **크리틱**을 보자. 크리틱의 역할은 **Q값**, 즉 어떤 상태에서 취한 행동에 대한 할인된 보상을 추정하는 것이다. 하지만 우리 행동은 숫자들의 벡터이므로, 크리틱 신경망은 **두 개의 입력**(상태와 행동)을 받는다. 크리틱의 출력은 **Q값에 해당하는 숫자 하나**다. 이 구조는 이산 행동 공간에서 (효율을 위해) 모든 행동에 대한 값을 한 번에 반환했던 DQN과는 다르다. 이 매핑 역시 결정론적이다.

정리하면 우리는 두 함수를 갖는다.
- **액터**, $\mu(s)$라 부르자. 상태를 행동으로 변환한다.
- **크리틱**, 상태와 행동을 통해 Q값 $Q(s,a)$를 준다.

액터 함수를 크리틱에 대입하면, 오직 상태 하나만 입력으로 받는 식 $Q(s, \mu(s))$를 얻는다. 결국 신경망은 그저 함수일 뿐이다.

이제 크리틱의 출력, 즉 우리가 **가장 궁극적으로 최대화하고 싶은 값(할인된 총 보상)**의 근사값을 보자. 이 값은 입력 상태뿐 아니라 액터의 파라미터 $\theta_\mu$와 크리틱의 파라미터 $\theta_Q$에도 달려 있다. 매 최적화 스텝마다, 우리는 **총 보상을 개선하는 방향으로 액터의 가중치를 바꾸고 싶다** — 다시 말해, 우리 정책의 그래디언트를 원한다.

Silver 등은 결정론적 정책 경사 정리에서, **확률적 정책 경사가 결정론적 정책 경사와 동치**임을 증명했다. 즉 정책을 개선하려면 그냥 $Q(s,\mu(s))$ 함수의 그래디언트를 계산하기만 하면 된다. 체인 룰을 적용하면 다음 그래디언트를 얻는다: $\nabla_a Q(s,\mu(s))\nabla_{\theta_\mu}\mu(s)$.

> [!important] A2C와 DDPG — 둘 다 "액터-크리틱"이지만 크리틱의 역할이 다르다
> A2C와 DDPG 둘 다 A2C 계열에 속하지만, **크리틱이 쓰이는 방식은 다르다.** A2C에서는 경험된 궤적으로부터 얻은 보상에 대한 **베이스라인(기준값)** 으로 크리틱을 쓴다. 그래서 크리틱은 선택적인 부품이다(없으면 [[REINFORCE 알고리즘|REINFORCE]] 방법이 되며, 학습 안정성 향상을 위해 쓴다). A2C의 정책이 확률적이라는 점이, 역전파 능력에 장벽을 만든다 — 무작위 샘플링 스텝은 미분할 수 없기 때문이다.
>
> DDPG에서는 크리틱이 다른 방식으로 쓰인다. 우리 정책이 결정론적이므로, 이제는 크리틱 네트워크에서 얻어지는 $Q$로부터 그래디언트를 계산할 수 있다(액터가 만든 행동을 사용하므로, Figure 15.5 확인). 그래서 전체 시스템이 미분 가능해지고, **확률적 경사 하강법(SGD)**으로 처음부터 끝까지 최적화할 수 있다. 크리틱을 업데이트하려면 벨만 방정식을 써서 $Q(s,a)$의 근사값을 구하고 MSE 목적함수를 최소화하면 된다.
>
> 다소 난해해 보일 수 있지만, 그 뒤에 있는 아이디어는 꽤 단순하다: 크리틱은 A2C에서 했던 방식 그대로 업데이트되고, 액터는 크리틱의 출력을 최대화하는 방향으로 업데이트된다. 이 방법의 아름다움은 **오프-폴리시**라는 점이다 — 즉 이제 거대한 리플레이 버퍼와 DQN 학습에서 썼던 다른 트릭들을 쓸 수 있다.

### 5.2 탐험

이 모든 좋은 점의 대가는, 정책이 이제 결정론적이라서 **환경을 어떻게든 탐험해야 한다**는 것이다. 액터가 반환하는 행동에 노이즈를 더하는 방식으로 해결할 수 있다. 몇 가지 방법이 있다.

가장 단순한 방법은 그냥 행동에 무작위 노이즈를 더하는 것이다: $\mu(s) + \epsilon\mathcal{N}$. 이 방법은 이 챕터의 다음 방법([[D4PG Distributed Distributional DDPG|D4PG]])에서 쓸 것이다.

좀 더 발전된(그리고 때로 더 나은 결과를 주는) 탐험 방법은, 금융 분야를 비롯해 확률 과정을 다루는 다른 영역에서 매우 인기 있는 [[오른슈타인-울렌벡 노이즈 OU Process|오른슈타인-울렌벡(OU) 프로세스]]를 쓰는 것이다. 이 과정은 마찰의 영향을 받는 거대한 브라운 입자의 속도를 모델링하며, 다음 확률미분방정식으로 정의된다.

$$\partial x_t = \theta(\mu - x_t)\partial t + \sigma \partial W$$

여기서 $\theta$, $\mu$, $\sigma$는 이 프로세스의 파라미터이고, $W_t$는 위너 프로세스다. 이산 시간 경우로 쓰면 OU 프로세스는 다음처럼 쓸 수 있다.

$$x_{t+1} = x_t + \theta(\mu - x) + \sigma\mathcal{N}$$

이 식은 이전 노이즈 값을 통해 다음 값을 생성하며, 정규 노이즈 $\mathcal{N}$이 더해진다. 우리의 탐험에서는, 액터가 반환한 행동에 이 OU 프로세스의 값을 더할 것이다.

### 5.3 구현

이 예제는 세 개의 소스 파일로 구성된다.
- `lib/model.py`: 모델과 PTAN 에이전트
- `lib/common.py`: 배치를 언팩하는 함수
- `04_train_ddpg.py`: 시작 코드와 학습 루프

여기서는 중요한 부분만 보여준다. 모델은 액터와 크리틱을 위한 **두 개의 개별 신경망**으로 구성되며, Lillicrap 등의 논문에 나온 구조를 그대로 따른다. 액터는 매우 단순한, 은닉층 2개짜리 피드포워드 네트워크다. 입력은 관측 벡터이고, 출력은 행동 개수만큼($N$개)의 벡터다. 출력 행동은 하이퍼볼릭 탄젠트 비선형 함수로 변환되어 $-1$~$1$ 범위로 눌린다.

크리틱은 조금 특이한데, **관측값과 행동을 위한 두 개의 별도 경로**를 갖고, 그 경로들이 합쳐져서(concatenate) 크리틱 출력(숫자 하나)으로 변환된다. Figure 15.5는 두 네트워크의 구조를 보여준다.

![[fig_15_5.png]]
*그림 15.5 — DDPG의 액터(왼쪽)와 크리틱(오른쪽) 신경망 구조*

액터의 코드는 행동 값을 만드는 3층짜리 네트워크다.

```python
class DDPGActor(nn.Module):
    def __init__(self, obs_size: int, act_size: int):
        super(DDPGActor, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(obs_size, 400),
            nn.ReLU(),
            nn.Linear(400, 300),
            nn.ReLU(),
            nn.Linear(300, act_size),
            nn.Tanh()
        )

    def forward(self, x: torch.Tensor):
        return self.net(x)
```

크리틱에 쓰이는 코드는 다음과 같다.

```python
class DDPGCritic(nn.Module):
    def __init__(self, obs_size: int, act_size: int):
        super(DDPGCritic, self).__init__()

        self.obs_net = nn.Sequential(
            nn.Linear(obs_size, 400),
            nn.ReLU(),
        )

        self.out_net = nn.Sequential(
            nn.Linear(400 + act_size, 300),
            nn.ReLU(),
            nn.Linear(300, 1)
        )

    def forward(self, x: torch.Tensor, a: torch.Tensor):
        obs = self.obs_net(x)
        return self.out_net(torch.cat([obs, a], dim=1))
```

크리틱의 `forward()` 함수는 먼저 관측값을 자신의 작은 네트워크로 변환한 뒤, 그 출력과 주어진 행동을 이어붙여(concat) Q값 하나로 변환한다.

액터 네트워크를 PTAN 경험 소스와 함께 쓰려면, 관측값을 행동으로 변환하는 에이전트 클래스를 정의해야 한다.

이 클래스는 우리의 OU 탐험 프로세스를 넣기에 가장 적합한 자리다. 하지만 이를 제대로 하려면, 지금까지 써보지 않은 PTAN 에이전트의 기능을 써야 한다 — 바로 **선택적 상태 유지(optional statefulness)** 다.

아이디어는 간단하다: 우리 에이전트는 관측값을 행동으로 변환한다. 그런데 만약 관측값들 **사이에서 무언가를 기억해야 한다면?** 지금까지의 모든 예제는 상태가 없었지만(stateless), 때로는 이것으로 충분치 않다. OU의 문제는, **관측값들 사이에서 OU 값을 추적해야 한다**는 점이다.

상태를 갖는 에이전트가 유용한 또 다른 사례는 **부분관측 마르코프 결정 과정(POMDP)**이다. [[POMDP 부분관측 마르코프결정과정|POMDP]]는 [[Chapter 06]]과 [[Chapter 14 - 웹 내비게이션]]에서 짧게 언급됐다. POMDP는 에이전트가 관측하는 상태가 마르코프 성질을 만족하지 않아, 상태들을 서로 구분할 수 있는 완전한 정보를 담지 못하는 마르코프 결정 과정이다. 그런 경우 에이전트는 행동을 취하기 위해 궤적을 따라 상태를 추적해야 한다.

OU를 위한 탐험을 구현하는 에이전트의 코드는 다음과 같다.

```python
class AgentDDPG(ptan.agent.BaseAgent):
    def __init__(self, net: DDPGActor, device: torch.device = torch.device('cpu'),
                 ou_enabled: bool = True, ou_mu: float = 0.0, ou_teta: float = 0.15,
                 ou_sigma: float = 0.2, ou_epsilon: float = 1.0):
        self.net = net
        self.device = device
        self.ou_enabled = ou_enabled
        self.ou_mu = ou_mu
        self.ou_teta = ou_teta
        self.ou_sigma = ou_sigma
        self.ou_epsilon = ou_epsilon

    def initial_state(self):
        return None
```

생성자는 많은 파라미터를 받는데, 대부분 논문 *Continuous Control with Deep Reinforcement Learning*에서 가져온 OU 프로세스의 기본 하이퍼파라미터다.

`initial_state()` 메서드는 `BaseAgent` 클래스에서 파생된 것으로, 새 에피소드가 시작될 때 에이전트의 초기 상태를 반환해야 한다. 우리 초기 상태는 행동과 같은 차원을 가져야 하므로(모든 행동마다 개별적인 탐험 궤적을 원하므로), 초기화는 뒤로 미루고 `None`을 초기 상태로 반환한다.

`__call__` 메서드에서 이 부분을 다음처럼 처리한다.

```python
def __call__(self, states: ptan.agent.States, agent_states: ptan.agent.AgentStates):
    states_v = ptan.agent.float32_preprocessor(states)
    states_v = states_v.to(self.device)
    mu_v = self.net(states_v)
    actions = mu_v.data.cpu().numpy()
```

이 메서드가 이 에이전트의 핵심이며, 목적은 관측된 상태와 내부 에이전트 상태를 행동으로 변환하는 것이다. 첫 단계로, 관측값을 알맞은 형태로 변환하고 액터 네트워크에 넣어 결정론적 행동으로 변환한다. 나머지 메서드는 OU 프로세스를 적용해 탐험 노이즈를 더하는 부분이다.

```python
    if self.ou_enabled and self.ou_epsilon > 0:
        new_a_states = []
        for a_state, action in zip(agent_states, actions):
            if a_state is None:
                a_state = np.zeros(shape=action.shape, dtype=np.float32)
            a_state += self.ou_teta * (self.ou_mu - a_state)
            a_state += self.ou_sigma * np.random.normal(size=action.shape)

            action += self.ou_epsilon * a_state
            new_a_states.append(a_state)
```

이 루프에서 우리는 (배치의) 관측값들과, 이전 호출에서 넘어온 에이전트 상태들의 리스트를 순회하며, 이미 보여준 공식을 그대로 구현해 OU 프로세스 값을 갱신한다.

마지막으로 루프를 마무리하며, OU 프로세스의 노이즈를 우리 행동에 더하고, 다음 스텝을 위해 노이즈 값을 저장한다.

```python
    else:
        new_a_states = agent_states
    actions = np.clip(actions, -1, 1)
    return actions, new_a_states
```

행동이 환경의 $-1$~$1$ 범위 안에 들어가도록 클리핑한다. 그렇지 않으면 PyBullet이 예외를 던진다.

DDPG 구현의 마지막 조각은 `04_train_ddpg.py`의 학습 루프다. 안정성을 개선하기 위해, 100,000개의 전이를 담는 리플레이 버퍼와, 액터·크리틱 양쪽을 위한 타깃 네트워크를 사용한다([[Chapter 06]]에서 둘 다 다뤘다).

```python
act_net = model.DDPGActor(env.observation_space.shape[0],
                           env.action_space.shape[0]).to(device)
crt_net = model.DDPGCritic(env.observation_space.shape[0],
                            env.action_space.shape[0]).to(device)
print(act_net)
print(crt_net)
tgt_act_net = ptan.agent.TargetNet(act_net)
tgt_crt_net = ptan.agent.TargetNet(crt_net)

writer = SummaryWriter(comment="-ddpg_" + args.name)
agent = model.AgentDDPG(act_net, device=device)
exp_source = ptan.experience.ExperienceSourceFirstLast(
    env, agent, gamma=GAMMA, steps_count=1)
buffer = ptan.experience.ExperienceReplayBuffer(exp_source, buffer_size=REPLAY_SIZE)
act_opt = optim.Adam(act_net.parameters(), lr=LEARNING_RATE)
crt_opt = optim.Adam(crt_net.parameters(), lr=LEARNING_RATE)
```

액터와 크리틱을 위해 서로 다른 옵티마이저를 두 개 쓰는데, 이는 각각의 그래디언트 처리를 단순화하기 위해서다. 학습 루프 안의 가장 중요한 코드는 다음과 같다. 매 이터레이션마다, 경험을 리플레이 버퍼에 저장하고 학습용 배치를 샘플링한다.

```python
batch = buffer.sample(BATCH_SIZE)
states_v, actions_v, rewards_v, dones_mask, last_states_v = \
    common.unpack_batch_ddqn(batch, device)
```

이후 크리틱을 학습시키는 두 개의 개별 학습 스텝이 이어진다. 크리틱을 학습시키려면, [[벨만 방정식 Bellman Equation|일-스텝 벨만 방정식]]으로 목표 Q값을 계산해야 하며, 타깃 크리틱 네트워크를 다음 상태의 근사값으로 사용한다.

```python
crt_opt.zero_grad()
q_v = crt_net(states_v, actions_v)
last_act_v = tgt_act_net.target_model(last_states_v)
q_last_v = tgt_crt_net.target_model(last_states_v, last_act_v)
q_last_v[dones_mask] = 0.0
q_ref_v = rewards_v.unsqueeze(dim=-1) + q_last_v * GAMMA
```

목표값을 얻었다면, MSE 손실을 계산해 크리틱의 옵티마이저에게 가중치를 조정하도록 요청할 수 있다. DQN 학습 과정과 매우 비슷하므로 새로울 것은 없다.

```python
critic_loss_v = F.mse_loss(q_v, q_ref_v.detach())
critic_loss_v.backward()
crt_opt.step()
tb_tracker.track("loss_critic", critic_loss_v, frame_idx)
tb_tracker.track("critic_ref", q_ref_v.mean(), frame_idx)
```

액터의 학습 스텝에서는, 크리틱의 출력을 늘리는 방향으로 액터의 가중치를 업데이트해야 한다. 액터와 크리틱 둘 다 미분 가능한 함수로 표현되므로, 우리가 해야 할 일은 액터의 출력을 크리틱에 넘긴 뒤 크리틱이 반환하는 값의 **부호를 뒤집어** 최소화하는 것뿐이다.

```python
act_opt.zero_grad()
cur_actions_v = act_net(states_v)
actor_loss_v = -crt_net(states_v, cur_actions_v)
actor_loss_v = actor_loss_v.mean()
```

이렇게 부호를 뒤집은 크리틱의 출력을 크리틱 네트워크로 역전파하는 데 손실로 쓸 수 있고, 최종적으로 액터에게까지 전달된다. 우리는 크리틱의 가중치는 건드리고 싶지 않으므로, **액터의 옵티마이저에게만** 최적화 스텝을 요청하는 것이 중요하다. 크리틱의 가중치는 이 호출로부터 그래디언트를 여전히 유지하고 있겠지만, 다음 최적화 스텝에서 버려질 것이다.

```python
actor_loss_v.backward()
act_opt.step()
tb_tracker.track("loss_actor", actor_loss_v, frame_idx)
```

학습 루프의 마지막 단계로, 타깃 네트워크의 업데이트를 다소 색다른 방식으로 수행한다.

```python
tgt_act_net.alpha_sync(alpha=1 - 1e-3)
tgt_crt_net.alpha_sync(alpha=1 - 1e-3)
```

이전에는 최적화된 네트워크의 가중치를 타깃 네트워크에 **주기적으로** 통째로 동기화했다. 연속 행동 문제에서는 이런 동기화가 잘 작동하지 않는다. 대신, 이른바 **"소프트 동기화(soft sync)"** 를 쓴다. 소프트 동기화는 **매 스텝마다** 수행되지만, 최적화된 네트워크의 가중치 중 아주 작은 비율만 타깃 네트워크에 더해진다. 이 덕분에 오래된 가중치에서 새 가중치로 **부드럽고 느린 전환**이 이뤄진다.

### 5.4 결과 및 영상

코드는 A2C 예제와 같은 방식으로 시작할 수 있다 — 실행 이름과 선택적 `-dev` 플래그를 넘기면 된다. 저자의 실험에서는 GPU를 쓸 때 대략 30%의 속도 향상이 있었으니, 급하다면 CUDA를 쓰는 것도 좋은 생각이다. 다만 아타리 게임에서 봤던 것만큼 극적인 향상은 아니다.

**500만 관측치**(약 20시간)를 학습한 뒤, DDPG 알고리즘은 테스트 10개 에피소드에서 **평균 보상 4.5**에 도달했다 — A2C 결과보다 개선된 수치다. 학습 다이내믹스는 다음 그래프들에서 볼 수 있다.

![[fig_15_6.png]]
*그림 15.6 — 훈련 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

![[fig_15_7.png]]
*그림 15.7 — 훈련 중 액터 손실(왼쪽)과 크리틱 손실(오른쪽)*

"에피소드 스텝" 그래프는 학습에 쓰인 에피소드의 평균 길이를 보여준다. 크리틱 손실은 MSE 손실이므로 낮아야 정상이지만, 액터 손실은 앞서 봤듯 **크리틱 출력의 부호를 뒤집은 값**이므로, **작을수록(더 음수일수록)** 액터가 (잠재적으로) 더 높은 보상을 달성할 수 있다는 뜻이다.

Figure 15.8은 테스트(10개 에피소드에 대한 평균값) 중 얻어진 값을 보여준다.

![[fig_15_8.png]]
*그림 15.8 — 테스트 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

저장된 모델을 테스트하고 영상을 기록하려면, A2C 때와 같은 방식으로 `05_play_ddpg.py` 유틸리티를 쓸 수 있다. 명령줄 옵션도 동일하지만, DDPG 모델을 불러오도록 되어 있다. Figure 15.9는 저자가 저장한 영상의 마지막 프레임이다.

![[fig_15_9.png]]
*그림 15.9 — DDPG 모델 시뮬레이션의 마지막 프레임*

테스트 중 점수는 3.033이었고, 영상은 https://youtu.be/vVnd0Nu1d9s 에서 볼 수 있다(11초 길이). 이 모델은 앞으로 넘어지면서 실패한다.

---

## 6. 세 번째 방법 — 분포적 정책 경사 (D4PG)

이 챕터의 마지막 방법으로, Barth-Maron 등의 논문 *Distributed distributional deterministic policy gradients*(2018)를 살펴본다.

이 방법의 정식 이름은 **Distributed Distributional Deep Deterministic Policy Gradients**, 줄여서 **[[D4PG Distributed Distributional DDPG|D4PG]]**다. 저자들은 DDPG 방법에 안정성·수렴성·표본 효율성을 개선하기 위한 몇 가지 향상을 제안했다.

첫째, 저자들은 Bellemare 등의 *A distributional perspective on reinforcement learning*(2017)에서 제안된 Q값의 **분포적 표현**을 채택했다. 이 접근법은 [[분포적 강화학습과 Categorical DQN|Chapter 8]]에서 DQN 개선을 다룰 때 이미 논의했으니, 자세한 내용은 그쪽 노트나 원 Bellemare 논문을 참고하라. 핵심 아이디어는, 크리틱이 반환하는 단일 Q값을 **확률 분포**로 대체하는 것이다. 벨만 방정식도 비슷한 방식으로 **벨만 연산자**로 대체된다.

둘째, **n-스텝 벨만 방정식**을 사용해 수렴 속도를 높였다. 이 역시 Chapter 8에서 자세히 다뤘다([[N-step DQN과 벨만 방정식 풀어쓰기]]).

원래 DDPG 방법과의 또 다른 차이는, 균등하게 샘플링하는 리플레이 버퍼 대신 **우선순위 경험 리플레이**를 사용했다는 점이다. 즉 엄밀히 말하면, 저자들은 Hassel 등의 *Rainbow: Combining Improvements in Deep Reinforcement Learning*(2017) 논문에서 관련 개선점을 가져와 DDPG 방법에 적용한 것이다. 그 결과는 인상적이었다 — 이 조합은 연속 제어 문제 집합에서 **최첨단(state-of-the-art) 결과**를 보였다. 이제 이 방법을 다시 구현해 직접 결과를 확인해 보자.

### 6.1 아키텍처

D4PG와 DDPG 사이에서 가장 눈에 띄는 변화는 **크리틱의 출력**이다. 주어진 상태와 행동에 대해 단일 Q값을 반환하는 대신, 이제는 **`N_ATOMS`개의 값**을 반환한다. 이는 미리 정해둔 범위 안의 값들에 대한 확률에 해당한다. 저자의 코드에서는 `N_ATOMS=51`, 분포 범위는 `Vmin=-10`, `Vmax=10`을 썼다. 즉 크리틱은 **51개의 숫자**를 반환하며, 이는 할인된 보상이 $[-10, -9.6, -9.2, \ldots, 9.6, 10]$의 경계를 갖는 구간(bin)들에 속할 확률을 나타낸다.

D4PG와 DDPG의 또 다른 차이는 **탐험 방식**이다. DDPG는 탐험을 위해 OU 프로세스를 사용했지만, D4PG 저자들에 따르면 OU와 단순한 무작위 노이즈를 둘 다 시도해 봤을 때 **결과가 같았다**고 한다. 그래서 그들은 논문에서 더 간단한 방법을 사용했다.

### 6.2 구현

마지막으로 눈에 띄는 코드 차이는 **학습**과 관련이 있다. D4PG는 크리틱이 반환한 확률 분포와 벨만 연산자로 얻은 확률 분포, 두 확률 분포 사이의 차이를 계산하기 위해 **교차 엔트로피 손실**을 사용한다. 두 분포를 같은 지지점(supporting atoms)에 정렬하기 위해, 원 Bellemare 논문과 같은 방식으로 **분포 투영(distribution projection)** 을 사용한다.

전체 소스 코드는 `06_train_d4pg.py`, `lib/model.py`, `lib/common.py`에 있다. 늘 그랬듯 모델 클래스부터 본다. 액터 클래스는 DDPG와 정확히 같은 구조를 가지므로, 학습 클래스에서도 `DDPGActor`를 그대로 사용한다. 크리틱은 은닉층 크기와 개수는 같지만, 출력이 숫자 하나가 아니라 `N_ATOMS`다.

```python
class D4PGCritic(nn.Module):
    def __init__(self, obs_size: int, act_size: int,
                 n_atoms: int, v_min: float, v_max: float):
        super(D4PGCritic, self).__init__()

        self.obs_net = nn.Sequential(
            nn.Linear(obs_size, 400),
            nn.ReLU(),
        )

        self.out_net = nn.Sequential(
            nn.Linear(400 + act_size, 300),
            nn.ReLU(),
            nn.Linear(300, n_atoms)
        )

        delta = (v_max - v_min) / (n_atoms - 1)
        self.register_buffer("supports", torch.arange(v_min, v_max + delta, delta))
```

또한 보상의 지지점(supports)을 담은 헬퍼용 PyTorch 버퍼를 만든다. 이는 확률 분포로부터 단일 평균 Q값을 얻는 데 쓰인다.

```python
    def forward(self, x: torch.Tensor, a: torch.Tensor):
        obs = self.obs_net(x)
        return self.out_net(torch.cat([obs, a], dim=1))

    def distr_to_q(self, distr: torch.Tensor):
        weights = F.softmax(distr, dim=1) * self.supports
        res = weights.sum(dim=1)
        return res.unsqueeze(dim=-1)
```

보다시피, `softmax()` 적용은 네트워크의 `forward()` 메서드에 포함되지 않는다. 이는 학습 중에 더 수치적으로 안정적인 `log_softmax()` 함수를 쓸 것이기 때문이다. 이런 이유로, 실제 확률이 필요한 곳에서는 `softmax()`를 적용해 줘야 한다.

D4PG의 에이전트 클래스는 훨씬 단순하며, **추적할 상태가 없다.**

```python
class AgentD4PG(ptan.agent.BaseAgent):
    def __init__(self, net: DDPGActor, device: torch.device = torch.device("cpu"),
                 epsilon: float = 0.3):
        self.net = net
        self.device = device
        self.epsilon = epsilon

    def __call__(self, states: ptan.agent.States, agent_states: ptan.agent.AgentStates):
        states_v = ptan.agent.float32_preprocessor(states)
        states_v = states_v.to(self.device)
        mu_v = self.net(states_v)
        actions = mu_v.data.cpu().numpy()
        actions += self.epsilon * np.random.normal(size=actions.shape)
        actions = np.clip(actions, -1, 1)
        return actions, agent_states
```

각 상태를 행동으로 변환할 때마다, 에이전트는 액터 네트워크를 적용하고 행동에 가우시안 노이즈를 더한다. 학습 코드에서는 다음 하이퍼파라미터들을 쓴다.

```python
GAMMA = 0.99
BATCH_SIZE = 64
LEARNING_RATE = 1e-4
REPLAY_SIZE = 100000
REPLAY_INITIAL = 10000
REWARD_STEPS = 5

TEST_ITERS = 1000

Vmax = 10
Vmin = -10
N_ATOMS = 51
DELTA_Z = (Vmax - Vmin) / (N_ATOMS - 1)
```

저자는 리플레이 버퍼로 (논문에서 쓴 100만 대신) 더 작은 10만 개를 사용했으며, 그래도 잘 작동했다. 버퍼는 환경으로부터 얻은 1만 개의 샘플로 미리 채워지고, 그 뒤에 학습이 시작된다.

매 학습 루프마다, 이전과 같은 두 스텝(크리틱 학습, 액터 학습)을 수행한다. 다른 점은 **크리틱의 손실을 계산하는 방식**이다.

```python
batch = buffer.sample(BATCH_SIZE)
states_v, actions_v, rewards_v, dones_mask, last_states_v = \
    common.unpack_batch_ddqn(batch, device)

crt_opt.zero_grad()
crt_distr_v = crt_net(states_v, actions_v)
last_act_v = tgt_act_net.target_model(last_states_v)
last_distr_v = F.softmax(
    tgt_crt_net.target_model(last_states_v, last_act_v), dim=1)
```

크리틱을 학습시키는 첫 단계로, 취한 상태와 행동에 대한 확률 분포를 반환하도록 요청한다. 이 확률 분포는 교차 엔트로피 손실 계산에 입력으로 쓰인다. 목표 확률 분포를 얻으려면, 배치 내 마지막 상태들로부터 분포를 계산하고 그 분포에 벨만 투영을 수행해야 한다.

```python
proj_distr = distr_projection(
    last_distr_v.detach().cpu().numpy(),
    rewards_v.detach().cpu().numpy(),
    dones_mask.detach().cpu().numpy(), gamma=GAMMA**REWARD_STEPS)
proj_distr_v = torch.tensor(proj_distr).to(device)
```

이 투영 함수는 다소 복잡하며, [[Chapter 08]]에서 설명한 구현과 정확히 같다. 간단히 복습하면, `last_states`의 확률 분포를 즉시 보상만큼 이동시키고 할인율에 맞춰 스케일한 변환을 계산한다. 그 결과가, 우리 네트워크가 반환하기를 바라는 목표 확률 분포다.

PyTorch에는 일반적인 교차 엔트로피 손실 함수가 없으므로(두 확률 분포 사이의 교차 엔트로피를 계산하고 싶다), 입력 확률의 로그값을 목표 확률과 곱해서 수동으로 계산한다.

```python
prob_dist_v = -F.log_softmax(crt_distr_v, dim=1) * proj_distr_v
critic_loss_v = prob_dist_v.sum(dim=1).mean()
critic_loss_v.backward()
crt_opt.step()
```

액터의 학습은 DDPG 방식과 크게 다르지 않다. 유일한 차이는 모델의 `distr_to_q()` 메서드를 사용해 **확률 분포를 단일 평균 Q값**으로 변환한다는 점이다.

```python
act_opt.zero_grad()
cur_actions_v = act_net(states_v)
crt_distr_v = crt_net(states_v, cur_actions_v)
actor_loss_v = -crt_net.distr_to_q(crt_distr_v)
actor_loss_v = actor_loss_v.mean()
actor_loss_v.backward()
act_opt.step()
```

### 6.3 결과

D4PG 방법은 이 챕터에서 다룬 세 방법 중 **수렴 속도와 최종 보상 모두에서 가장 좋은 결과**를 보였다. 20시간의 학습 후 약 350만 관측치를 거치며, 테스트 평균 보상 **17.912**에 도달했다. "환경이 해결됐다"고 간주하는 기준 점수가 15.0이므로, 이는 훌륭한 결과다. 게다가 (환경의 시간 제한인 1,000스텝보다) 스텝 수가 적으므로 **더 개선될 여지가 있다** — 즉 우리 모델이 내부 환경 점검 때문에 조기에 종료되고 있다는 뜻이다. Figure 15.10과 Figure 15.11은 훈련·테스트 지표를 보여준다.

![[fig_15_10.png]]
*그림 15.10 — 훈련 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

![[fig_15_11.png]]
*그림 15.11 — 테스트 에피소드의 보상(왼쪽)과 스텝 수(오른쪽)*

세 방법을 비교하기 위해, Figure 15.12는 세 방법 모두의 테스트 에피소드 지표를 담고 있다.

![[fig_15_12.png]]
*그림 15.12 — A2C·DDPG·D4PG 세 방법의 테스트 보상(왼쪽)과 에피소드 스텝(오른쪽) 비교. D4PG(점선)가 가장 빠르고 높게 올라간다*

모델을 실제로 동작하는 모습으로 확인하려면, DDPG와 같은 도구인 `05_play_ddpg.py`를 쓸 수 있다(액터가 DDPG와 같은 네트워크 구조를 갖기 때문이다). 최고 모델이 만든 영상은 33초 길이이며, 최종 점수는 17.827이었다. 영상은 https://youtu.be/XZdVrGPaI0M 에서 볼 수 있다.

---

## 7. 더 해볼 것들 (Things to try)

이 주제에 대한 이해를 넓히기 위해 시도해 볼 수 있는 목록이다.
- D4PG 코드에서는 단순한 리플레이 버퍼를 썼다. [[Chapter 08]]에서 했던 것처럼 **우선순위 경험 리플레이**로 예제를 바꿔 보라.
- 흥미롭고 도전적인 환경이 많이 있다. 다른 PyBullet 환경들, DeepMind Control Suite(Tassa 등, arXiv 1801.00690, 2018), Gym의 MuJoCo 기반 환경 등으로 시작해 볼 수 있다.
- NIPS-2017의 매우 도전적인 *Learning to Run* 대회(2018·2019년에도 더 어려운 문제로 다시 열렸다)에 도전해 볼 수도 있다. 인간 신체의 시뮬레이터가 주어지고, 에이전트가 스스로 걷는 법을 알아내야 한다.

---

## 8. 요약

이 챕터에서는 **연속 제어**라는 매우 흥미로운 RL 영역을 빠르게 훑어보고, 네발 로봇 하나의 문제에 **세 가지 다른 알고리즘**을 적용해 봤다. 실제로 이 로봇과 같은 물리적 로봇이 Ghost Robotics사에 의해 만들어졌다(유튜브에서 https://youtu.be/bnK0eMoibLg 영상을 확인해 보라). 우리는 이 환경에 **A2C, DDPG, D4PG**(가장 좋은 결과를 보인) 세 가지 학습 방법을 적용했다.

- A2C는 정책을 **가우시안 분포의 평균·분산**으로 표현하는 방식으로 연속 행동에 손쉽게 적응했지만, 단일 환경만으로 경험을 모은다는 정책 경사 계열의 약점 때문에 결과가 가장 나빴다.
- DDPG는 정책을 **결정론적**으로 만들어 크리틱의 Q값을 직접 미분함으로써 정책을 개선하고, 그 결과 **오프-폴리시**로 학습할 수 있게 됐다. 탐험은 [[오른슈타인-울렌벡 노이즈 OU Process|OU 프로세스]]로 보완했다.
- D4PG는 DDPG에 **분포적 크리틱**과 n-스텝 벨만 방정식을 더해, 셋 중 가장 빠르고 안정적인 수렴을 보였다.

다음 챕터에서는 연속 행동 영역을 계속 탐구하며, **신뢰 영역(trust region)** 확장이라는 또 다른 개선 방법들을 살펴본다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[이산 행동과 연속 행동]]
- [[관측공간과 행동공간(Space)]]
- [[액터-크리틱과 어드밴티지]]
- [[결정론적 정책 Deterministic Policy]]
- [[결정론적 정책 경사 DDPG]]
- [[오른슈타인-울렌벡 노이즈 OU Process]]
- [[D4PG Distributed Distributional DDPG]]
- [[분포적 강화학습과 Categorical DQN]]
- [[벨만 방정식 Bellman Equation]]
- [[타깃 네트워크와 부트스트래핑]]
- [[오프폴리시와 온폴리시]]
- [[손실함수의 종류]]
- [[교차 엔트로피 Cross-Entropy]]
- [[활성화함수]]
- [[POMDP 부분관측 마르코프결정과정]]
- [[N-step DQN과 벨만 방정식 풀어쓰기]]
- [[우선순위 경험 리플레이]]

## 한눈에 보는 개념 지도
| 개념 | 기호/이름 | 한 줄 뜻 |
|---|---|---|
| 연속 행동 공간 | `Box(low, high, shape)` | 실수값 범위를 갖는 행동 표현 |
| 확률적 정책 | $\pi_\theta(a\mid s)$ | 행동을 분포에서 샘플링(A2C) |
| 결정론적 정책 | $\mu(s)$ | 행동값을 바로 반환(DDPG, D4PG) |
| 가우시안 정책 | $\mu, \sigma^2$ | 평균·분산으로 행동 분포 표현 |
| 크리틱(A2C) | $V(s)$ | 상태 가치, 베이스라인 |
| 크리틱(DDPG) | $Q(s,a)$ | 상태+행동 → Q값, 정책 개선의 원천 |
| 결정론적 정책 경사 | $\nabla_a Q(s,\mu(s))\nabla_{\theta_\mu}\mu(s)$ | 정책을 Q값 방향으로 직접 개선 |
| 탐험 노이즈 | OU / 가우시안 | 결정론적 정책의 탐험 부족을 보완 |
| 소프트 동기화 | `alpha_sync` | 타깃 네트워크를 매 스텝 조금씩 갱신 |
| 분포적 크리틱 | `N_ATOMS`개 확률 | Q값을 확률 분포로 예측(D4PG) |
