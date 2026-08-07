---
title: "Chapter 22 — 다중 에이전트 RL (Multi-Agent RL)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 22
tags: [DeepRL, 강화학습, MARL, 다중에이전트, MAgent, DQN]
---

# Chapter 22 · 다중 에이전트 RL

> [!abstract] 이 챕터를 한 문장으로
> 지금까지는 **에이전트 한 명 vs 환경**만 다뤘지만, 현실에는 **여러 에이전트가 동시에 존재하며 서로 협력하거나 경쟁하는** 상황이 훨씬 많다. 이를 다루는 분야가 **다중 에이전트 강화학습(MARL)**이며, 이 챕터에서는 가볍고 빠른 **MAgent(MAgent2)** 환경 위에서 호랑이-사슴 사냥 시뮬레이션을 통해 MARL을 실습한다. 이 챕터가 이 책의 **마지막 장**이다.

---

## 들어가며 — 왜 "에이전트가 여럿"인 문제가 따로 필요한가?

1장에서 우리는 RL의 기본 형식을 배웠다: **에이전트(agent)** 하나, **환경(environment)** 하나, 그리고 그 사이를 오가는 **행동·보상·관측** 세 채널. 지금까지 20개 넘는 챕터에서 다룬 모든 알고리즘(DQN, 정책 경사, A2C, MCTS 등)은 전부 이 "1 대 1" 구도를 전제로 했다.

그런데 현실에는 이 구도로 딱 맞아떨어지지 않는 문제가 아주 많다.

> [!note] 대표적인 다중 에이전트 상황
> - **경매(auction)**: 여러 입찰자가 동시에 값을 부른다.
> - **광대역 통신망(broadband communication)**: 여러 기기가 같은 채널을 나눠 써야 한다.
> - **사물인터넷(IoT)**: 수많은 센서·기기가 동시에 판단을 내린다.

이런 상황을 다루는 강화학습의 갈래를 **다중 에이전트 강화학습**(Multi-Agent Reinforcement Learning, 줄여서 **MARL**)이라 부른다. 자세한 정의와 비유는 [[다중 에이전트 강화학습 MARL]] 참고.

이 챕터에서는 MARL을 깊게 파고들기보다는 **가볍게 맛보기**를 한다. 구체적으로는:
1. 단일 에이전트 RL과 MARL이 어떻게 같고 다른지 개괄한다.
2. Geek.AI UK/China 연구팀이 만들고 나중에 Farama Foundation이 이어받은 **MAgent** 환경을 살펴본다.
3. MAgent로 여러 그룹의 에이전트를 학습시켜 본다.

> [!tip] 이 챕터가 취하는 "간단한 접근"
> 여러 에이전트를 다루는 정교한 방법은 많지만, 이 챕터에서는 **에이전트들이 정책을 공유**하는 단순한 방식을 쓴다. 대신 각 에이전트가 받는 **관측은 그 에이전트 자신의 시점**에서 주어지고, 그 안에 다른 에이전트의 위치 정보도 포함된다. 이렇게 단순화하면 이미 배운 RL 알고리즘(DQN 등)은 그대로 재사용할 수 있고, **환경 쪽만 여러 에이전트를 다루도록 전처리**해주면 된다.

---

## 1. 다중 에이전트 RL이란 무엇인가?

다중 에이전트 구도는 1장에서 다룬 익숙한 RL 모델의 **자연스러운 확장**이다. 표준 RL에서는 에이전트 하나가 관측·보상·행동으로 환경과 소통한다. 하지만 현실 문제에는 **환경 안에 여러 에이전트가 함께 상호작용**하는 경우가 자주 있다. 구체적 예:

- **체스**: 내 프로그램이 상대를 이기려 한다.
- **시장 시뮬레이션**: 광고나 가격을 바꾸면, 다른 참가자들의 **대응(counter-action)** 이 뒤따른다.
- **Dota 2나 StarCraft II 같은 멀티플레이어 게임**: 에이전트가 여러 유닛을 조종해야 하는데, 이 유닛들이 다른 플레이어의 유닛과 **경쟁**하면서도, 한 플레이어가 조종하는 유닛들끼리는 목표 달성을 위해 **협력**해야 할 수도 있다.

### 1.1 "다른 에이전트 = 환경"으로 퉁칠 수 있을 때

만약 다른 에이전트들이 **내 통제 밖**에 있다면, 그들을 그냥 환경의 일부로 취급해서 지금까지 배운 단일 에이전트 RL을 그대로 쓸 수 있다. 실제로 20장에서 본 **자기 대전(self-play)** 학습이 이런 접근이며, 환경 쪽에 별다른 정교한 장치 없이도 좋은 정책을 만들어내는 강력한 기법이다. 하지만 어떤 상황에서는 이 정도로는 부족하고 부적합하다.

### 1.2 단순한 에이전트들이 만드는 놀랍도록 복잡한 행동

연구에 따르면, **단순한 에이전트들의 집단**이 예상보다 훨씬 복잡한 협력 행동을 만들어낼 수 있다. 대표적 사례가 OpenAI 블로그의 "숨바꼭질(hide-and-seek)" 실험과 논문 *Emergent tool use from multi-agent autocurricula*(Baker 외, 2020)다. 여러 에이전트가 서로 경쟁하며 점점 더 정교한 전략과 대응 전략을 발전시킨다 — 예를 들어 "주변 물건을 모아 담을 쌓아 숨는다", "트램펄린을 이용해 담 뒤에 숨은 상대를 잡는다" 같은 행동이 스스로 나타난다.

### 1.3 협력과 경쟁

에이전트들이 소통하는 방식은 크게 두 그룹으로 나뉜다. 자세한 내용과 실습 예시는 [[협력과 경쟁 MARL]] 참고.
- **경쟁(Competitive)**: 둘 이상의 에이전트가 자기 보상을 최대화하려고 겨룬다. 가장 단순한 형태는 체스·백개먼·아타리 퐁 같은 2인 게임.
- **협력(Collaborative)**: 여러 에이전트가 공동의 목표를 위해 힘을 합친다.

대부분의 흥미롭고 현실적인 시나리오는 이 둘의 **혼합**이다. 동맹을 맺을 수 있는 보드게임부터, 100% 협력을 가정하지만 실제로는 훨씬 복잡한 현대 기업까지 예는 다양하다.

### 1.4 게임 이론과의 관계

이론적으로 파고들면 MARL은 **게임 이론(game theory)** 이라는, 협력과 경쟁 양쪽 모두에 대해 이미 상당히 발전한 학문 분야와 만난다. 예를 들어 20장에서 쓴 **미니맥스(minimax) 알고리즘**도 게임 이론의 잘 알려진 결과다. 이 책은 지면 관계상 게임 이론 자체를 깊이 다루지는 않지만, 궁금하다면 관련 책과 강의가 많으니 참고할 만하다.

MARL은 비교적 젊은 분야지만 활동이 계속 늘고 있어 앞으로도 지켜볼 만한 주제다.

---

## 2. 환경 준비하기

### 2.1 Gym 생태계의 한계

MARL을 실습하려면 여러 에이전트를 동시에 다룰 수 있는 환경이 필요하다. 그런데 Gym과 함께 제공되는 환경은 **전부 에이전트가 하나뿐**이다. 아타리 퐁을 2인용으로 바꾸는 패치가 존재하긴 하지만, 표준이라기보다는 예외적인 경우다.

DeepMind가 Blizzard와 함께 **StarCraft II**를 공개(`https://github.com/deepmind/pysc2`)해서 아주 흥미롭고 도전적인 실험 환경을 제공하지만, MARL에 처음 입문하는 사람에게는 지나치게 복잡할 수 있다.

### 2.2 MAgent — 이 챕터가 선택한 환경

이 챕터는 원래 Geek.AI가 개발한 **MAgent** 환경을 사용한다. 간단하고 빠르며 의존성이 적으면서도, 다양한 다중 에이전트 시나리오를 실험할 수 있어 입문에 적합하다. Gym과 완전히 호환되는 API는 아니지만, 이 챕터에서 우리가 직접 Gym 스타일 래퍼를 구현한다.

MARL을 더 깊이 파보고 싶다면 Farama Foundation의 **PettingZoo** 패키지(`https://pettingzoo.farama.org`)도 있다. 더 많은 환경과 통일된 통신 API를 제공하지만, 이 챕터에서는 MAgent에만 집중한다.

### 2.3 MAgent 한눈에 보기

MAgent는 **2D 그리드 월드**를 시뮬레이션한다. 이 그리드 안에 사는 에이전트들은:
- 자기 **지각 범위(perception length)** 안에서 주변을 관측하고,
- 일정 거리만큼 **이동**하고,
- 주변의 다른 에이전트를 **공격**할 수 있다.

환경 안에는 서로 다른 특성과 상호작용 규칙을 가진 **여러 그룹**의 에이전트가 있을 수 있다. 이 챕터의 첫 환경은 **포식자-피식자(predator-prey) 모델**로, "호랑이(tiger)"가 "사슴(deer)"을 사냥해서 보상을 얻는다. 환경 설정에서 각 그룹의 지각 범위, 이동 거리, 공격 거리, 초기 체력, 이동·공격에 쓰는 체력 소모량 등 다양한 항목을 지정할 수 있다. 에이전트 외에도, 에이전트가 통과할 수 없는 **벽(wall)** 을 환경에 넣을 수 있다.

> [!tip] MAgent의 강점 — 확장성
> MAgent는 내부적으로 **C++로 구현**되어 있고 Python은 그 인터페이스일 뿐이다. 그래서 그룹 하나에 **수천 마리**의 에이전트가 있어도 관측을 제공하고 행동을 처리하는 속도가 빠르다.

### 2.4 MAgent 설치하기

원본 MAgent 저장소는 한동안 관리되지 않고 있다. 다행히 Farama Foundation이 원본을 포크해 **MAgent2**라는 이름으로 대부분의 원래 기능을 유지·관리하고 있다(문서: `https://magent2.farama.org/`, 코드: `https://github.com/Farama-Foundation/MAgent2`). 설치 명령은 다음과 같다.

```bash
pip install magent2==0.3.3
```

---

## 3. 무작위 정책으로 환경 감 잡기

MAgent API와 동작 방식을 빠르게 이해하기 위해, 저자는 "tiger"와 "deer" 두 그룹이 **둘 다 무작위 정책**으로 움직이는 간단한 예제를 준비했다. RL 관점에서 딱히 흥미롭진 않지만, 나중에 Gym 스타일 래퍼를 만들 때 필요한 API 감각을 익히기엔 충분하다. 예제 코드는 `Chapter22/forest_random.py`에 있다.

### 3.1 ForestEnv 클래스 — 환경 정의

`lib/data.py`에 정의된 `ForestEnv`가 환경 자체다. MAgent 환경의 기반 클래스인 `magent_parallel_env`(이름이 소문자인 건 파이썬 스타일 가이드에 어긋나지만, 라이브러리가 원래 그렇게 정의했다)와 `EzPickle`을 상속한다.

```python
class ForestEnv(magent_parallel_env, EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "forest_v4",
        "render_fps": 5,
    }
```

이 클래스는 Gym API를 흉내 내지만 100% 호환되지는 않아서, 나중에 우리 코드에서 그 차이를 직접 처리해야 한다.

생성자에서는 저수준 MAgent C++ 라이브러리 API를 파이썬으로 감싸는 어댑터인 `GridWorld` 클래스를 만든다.

```python
def __init__(self, map_size: int = MAP_SIZE, max_cycles: int = MAX_CYCLES,
             extra_features: bool = False, render_mode: tt.Optional[str] = None,
             seed: tt.Optional[int] = None, count_walls: int = COUNT_WALLS,
             count_deer: int = COUNT_DEER, count_tigers: int = COUNT_TIGERS):
    EzPickle.__init__(self, map_size, max_cycles, extra_features, render_mode, seed)
    env = GridWorld(self.get_config(map_size), map_size=map_size)

    handles = env.get_handles()
    self.count_walls = count_walls
    self.count_deer = count_deer
    self.count_tigers = count_tigers

    names = ["deer", "tiger"]
    super().__init__(env, handles, names, map_size, max_cycles, [-1, 1],
                      False, extra_features, render_mode)
```

- `GridWorld(self.get_config(map_size), map_size=map_size)`: 실제 시뮬레이션 로직을 처리하는 저수준 그리드 월드 객체를 생성한다.
- `env.get_handles()`: 그룹별로 에이전트를 다루기 위한 "핸들(handle)"을 받아온다. 이 챕터의 환경엔 "deer"와 "tiger" 두 그룹이 있다.
- 마지막 `super().__init__(...)`은 부모 클래스(`magent_parallel_env`)를 초기화하며, 각 그룹 이름과 보상 스케일(`[-1, 1]`) 등을 넘긴다.

`GridWorld`는 `get_config` 함수가 반환하는 `Config` 인스턴스로 설정을 받는다.

```python
@classmethod
def get_config(cls, map_size: int):
    # 표준 forest 설정을 그대로 쓰되, 사슴은 매 스텝마다 보상을 받도록 수정
    cfg = forest_config(map_size)
    cfg.agent_type_dict["deer"]["step_reward"] = 1
    return cfg
```

이 함수는 `magent.builtin.config.forest` 패키지의 `forest_config` 함수를 가져와서, 사슴이 **매 스텝마다 보상 1**을 받도록 살짝 수정한다. 나중에 사슴 모델을 학습시킬 때, 이 보상이 "오래 살아남으라"는 신호로 쓰이기 때문에 중요하다.

전체 설정 코드는 대부분 그대로 두었기 때문에 이 챕터에는 포함하지 않았지만, 다음과 같은 세부사항을 담고 있다.

> [!note] 환경 설정이 담는 정보
> - 몇 개의 그룹이 있는가? (이 예제에서는 "deer"와 "tiger" 두 그룹)
> - 각 그룹의 특성 — 얼마나 멀리 볼 수 있는가(사슴은 1칸, 호랑이는 4칸까지), 얼마나 멀리 공격할 수 있는가, 초기 체력은 얼마인가, 데미지를 입으면 얼마나 빨리 회복하는가 등.
> - 다른 그룹을 어떻게 공격하고, 그 데미지는 얼마인가 — 예를 들어 포식자가 반드시 **짝을 지어서만** 사냥하도록 만들 수도 있다(이 챕터 뒷부분에서 실험). 기본 설정에서는 단순하게, 호랑이 한 마리가 제약 없이 사슴을 공격할 수 있다.

`ForestEnv`의 마지막 함수는 `generate_map`으로, 맵 위에 벽·사슴·호랑이를 무작위로 배치한다.

```python
def generate_map(self):
    env, map_size = self.env, self.map_size
    handles = env.get_handles()

    env.add_walls(method="random", n=self.count_walls)
    env.add_agents(handles[0], method="random", n=self.count_deer)
    env.add_agents(handles[1], method="random", n=self.count_tigers)
```

### 3.2 forest_random.py — 실행 스크립트

이제 실제로 환경을 돌려보는 `forest_random.py`를 보자. 먼저 필요한 것들을 가져온다.

```python
from gymnasium.wrappers.monitoring.video_recorder import VideoRecorder
from lib import data

RENDER_DIR = "render"
```

2장에서는 `RecordVideo` 래퍼(관련 개념: [[Wrapper 래퍼 패턴]])를 써서 관측을 자동으로 영상으로 남겼지만, MAgent 환경에서는 모든 메서드가 (단일 값이 아니라) **에이전트마다 하나씩 딕셔너리**를 반환하기 때문에 그 방식이 통하지 않는다. 대신 `VideoRecorder` 클래스를 직접 써서 `RENDER_DIR` 디렉터리에 영상을 저장한다.

먼저 `ForestEnv` 인스턴스와 영상 레코더를 만든다. 환경 객체는 `agents`라는 속성을 갖는데, 여기엔 환경 안 모든 에이전트의 문자열 ID(`deer_12`, `tiger_3` 같은 형태)가 들어 있다. 기본 설정(맵 크기 64×64)에서는 사슴 204마리, 호랑이 40마리 — 총 `env.agents` 리스트에 244개 항목이 있다.

```python
if __name__ == "__main__":
    env = data.ForestEnv(render_mode="rgb_array")
    recorder = VideoRecorder(env, RENDER_DIR + "/forest-random.mp4")
    sum_rewards = {agent_id: 0.0 for agent_id in env.agents}
    sum_steps = {agent_id: 0 for agent_id in env.agents}
```

환경을 `reset()`으로 초기화하는데, 이번엔 (Gym API처럼 두 개가 아니라) **값 하나만** 반환한다. 반환값은 에이전트 ID를 키로, 관측 텐서를 값으로 하는 딕셔너리다.

```python
    obs = env.reset()
    recorder.capture_frame()
    assert isinstance(obs, dict)
    print(f"tiger_0: obs {obs['tiger_0'].shape}, act: {env.action_space('tiger_0')}")
    print(f"deer_0: obs {obs['deer_0'].shape}, act: {env.action_space('deer_0')}\n")
    step = 0
```

실행하면 다음과 같은 출력이 나온다.

```
tiger_0: obs (9, 9, 5), act: Discrete(9)
deer_0: obs (3, 3, 5), act: Discrete(5)
```

행동 공간을 보면, 사슴은 **다섯 가지 서로 배타적인 행동**(상하좌우 네 방향 + "아무것도 안 함")을 할 수 있다. 호랑이도 똑같이 이동할 수 있는데, 여기에 **네 방향으로 공격**하는 행동이 추가된다.

관측 쪽을 보면, 호랑이는 **9×9 행렬**을, 사슴은 (더 시력이 약해서) **3×3 행렬**을 받는다. 두 경우 모두 관측의 다섯 개 평면(plane)은 다음과 같다.

> [!note] 관측의 다섯 정보 평면
> - **벽(walls)**: 이 칸에 벽이 있으면 1, 아니면 0
> - **그룹 1(자기 그룹)**: 이 칸에 내 그룹의 에이전트가 있으면 1, 아니면 0
> - **그룹 1 체력**: 이 칸에 있는 우리 편 에이전트의 상대적 체력
> - **그룹 2(상대 그룹)**: 이 칸에 적이 있으면 1, 아니면 0
> - **그룹 2 체력**: 이 칸에 있는 적의 상대적 체력, 없으면 0

관측은 항상 **관측 주체 에이전트 자신이 중앙**에 오도록 만들어진다 — 즉 그 에이전트를 중심으로 한 주변 그리드를 보여준다. 그룹이 더 많이 설정되면 관측 텐서에 평면이 더 늘어난다.

MAgent에는 "미니맵(minimap)" 기능도 있다 — 각 그룹의 에이전트 위치를 "축소된 전체 지도"로 알려주는 기능인데, 이 예제들에서는 비활성화되어 있다. 미니맵이 없으면 에이전트는 자기 주변의 제한된 범위만 볼 수 있지만, 미니맵을 켜면 환경 전체를 좀 더 넓게 볼 수 있다.

그룹 1·2는 항상 **관측하는 에이전트의 그룹 기준으로 상대적**이다. 그래서 사슴의 관측에서 그룹 1은 다른 사슴, 호랑이의 관측에서 그룹 1은 다른 호랑이가 된다. 이 덕분에 관측이 **그룹에 독립적**이 되어, 필요하면 양쪽 그룹에 **같은 정책 하나**를 학습시킬 수도 있다.

관측에 추가로 넣을 수 있는 선택적 정보로 "extra features"가 있는데, 여기엔 에이전트의 ID, 마지막 행동, 마지막 보상, 정규화된 위치 등이 포함된다. 자세한 내용은 MAgent 소스 코드에서 확인할 수 있지만, 이 예제들에서는 사용하지 않는다.

### 3.3 시뮬레이션 루프

이제 살아있는 에이전트가 있는 동안 반복되는 루프를 보자. 매 반복마다, 모든 에이전트에 대해 **무작위 행동을 뽑아** 환경에서 실행한다.

```python
    while env.agents:
        actions = {agent_id: env.action_space(agent_id).sample() for agent_id in
                   env.agents}
        all_obs, all_rewards, all_dones, all_trunc, all_info = env.step(actions)
        recorder.capture_frame()
```

`env.step()`이 반환하는 모든 값은 **에이전트 ID를 키로 하는 딕셔너리**다. MAgent 환경에서 중요한 특징 하나는 **에이전트 집합 자체가 변한다(volatile)** 는 것 — 에이전트가 죽으면 그 순간 사라진다. 이 "forest" 환경에서는 호랑이가 매 스텝 체력 0.1을 잃고(굶주림), 사슴을 먹으면 체력을 회복한다. 사슴은 (아마 풀을 뜯어먹는 것으로) 매 스텝 체력을 회복하고, 공격당했을 때만 체력을 잃는다.

에이전트가 죽으면(호랑이는 굶어서, 사슴은 호랑이에게 공격당해서) 해당 항목의 `all_dones` 딕셔너리 값이 `True`가 되고, 다음 반복부터 그 에이전트는 모든 딕셔너리와 `env.agents` 리스트에서 사라진다. 즉, 한 에이전트가 죽어도 **에피소드 전체는 계속 진행**되며, 학습 코드를 짤 때 이 점을 반드시 고려해야 한다.

앞의 예제에서는 호랑이와 사슴이 둘 다 무작위로 행동하기 때문에(그리고 호랑이는 매 스텝 체력을 잃으므로), 거의 확실히 모든 호랑이가 굶어 죽고 살아남은 사슴들은 행복하게 무한히 오래 산다. 다만 환경은 호랑이가 더 이상 없으면 남은 사슴을 자동으로 제거하도록 설정되어 있어서, 실제로는 프로그램이 30~40스텝 만에 끝난다.

루프가 끝나면 에이전트별로 얻은 보상 합과 살아있던 스텝 수를 기록한다.

```python
        for agent_id, r in all_rewards.items():
            sum_rewards[agent_id] += r
            sum_steps[agent_id] += 1
        step += 1
```

그 다음 보상 기준 상위 20개 에이전트를 출력한다.

```python
    final_rewards = list(sum_rewards.items())
    final_rewards.sort(key=lambda p: p[1], reverse=True)
    for agent_id, r in final_rewards[:20]:
        print(f"{agent_id}: got {r:.2f} in {sum_steps[agent_id]} steps")
    recorder.close()
```

실행 결과 예시:

```
$ ./forest_random.py
tiger_0: obs (9, 9, 5), act: Discrete(9)
deer_0: obs (3, 3, 5), act: Discrete(5)

tiger_5: got 34.80 in 37 steps
tiger_37: got 19.70 in 21 steps
...
```

저자의 실행에서는 `tiger_5`가 유독 운이 좋아 다른 호랑이들보다 오래 살았다. 프로그램이 끝나면 에피소드 영상이 저장된다.

*그림 22.1*에는 게임 시작 시점과 거의 끝나갈 때, 두 가지 상태가 나온다. 호랑이는 파란 점(흑백으로 보면 더 진한 점), 사슴은 빨간 점, 벽은 회색 점으로 표시된다.

![[fig_22_1.png]]
*그림 22.1 — forest 환경의 두 상태: 에피소드 시작(왼쪽)과 거의 끝(오른쪽). 왼쪽은 호랑이(파랑) 40마리 vs 사슴(빨강) 204마리, 오른쪽은 호랑이 대부분이 굶어 죽어 1마리만 남고 사슴은 201마리가 남은 모습.*

공격 방향은 작은 검은 화살표로 표시된다. 이 예제는 두 그룹이 모두 무작위로 움직여서 RL 관점에서는 별로 흥미롭지 않다. 다음 절부터는 **DQN**을 적용해 호랑이의 사냥 실력을 개선해 본다.

---

## 4. 호랑이를 위한 심층 Q 네트워크 (DQN)

이제 호랑이 그룹에 DQN 모델을 적용해서, 사냥을 더 잘 배울 수 있는지 확인한다. 모든 호랑이 에이전트가 **네트워크 하나를 공유**하므로 행동 방식은 다 같아진다. 이 예제에서는 단순함을 위해 사슴 그룹은 계속 무작위로 행동하게 두고(사슴 학습은 챕터 뒷부분에서 다룬다), 학습 코드는 `Chapter22/forest_tigers_dqn.py`에 있으며 이전 챕터들의 다른 DQN 버전과 크게 다르지 않다.

### 4.1 MAgentExperienceSourceFirstLast — 다중 에이전트용 경험 소스

MAgent 환경이 우리 클래스들과 맞물려 동작하도록, [[ExperienceSource와 리플레이버퍼]]에서 다룬 `ExperienceSourceFirstLast`의 특화 버전을 구현했다. 이름은 `MAgentExperienceSourceFirstLast`이고 `lib/data.py`에 있다.

7장에서 다뤘듯, `ExperienceSourceFirstLast`가 만들어내는 항목(`ExperienceFirstLast`)에는 다음 필드가 있다.

- `state`: 현재 스텝에서 환경으로부터 받은 관측
- `action`: 우리가 실행한 행동
- `reward`: 얻은 보상의 양
- `last_state`: 행동을 실행한 뒤의 관측

다중 에이전트 설정에서는 모든 에이전트가 **같은 종류의 데이터**를 만들어내지만, 이 경험이 어느 그룹(이 예에서는 호랑이인지 사슴인지) 소속인지도 구분할 수 있어야 한다. 이를 위해 그룹 이름을 담는 새 필드를 추가한 서브클래스 `ExperienceFirstLastMARL`을 정의한다.

```python
@dataclass(frozen=True)
class ExperienceFirstLastMARL(ExperienceFirstLast):
    group: str


class MAgentExperienceSourceFirstLast:
    def __init__(self, env: magent_parallel_env, agents_by_group: tt.Dict[str,
    BaseAgent],
                 track_reward_group: str, env_seed: tt.Optional[int] = None,
                 filter_group: tt.Optional[str] = None):
```

([[데이터클래스 dataclass]]에서 `@dataclass(frozen=True)`가 하는 일을 복습할 수 있다.) 생성자에 넘기는 인자는 다음과 같다.

> [!note] MAgentExperienceSourceFirstLast 생성자 인자
> - `magent_parallel_env`: MAgent 병렬 환경(앞 절에서 실습한 것).
> - `agents_by_group`: 그룹별 PTAN `BaseAgent` 객체. 이 호랑이 DQN 예제에서는 호랑이는 신경망(`ptan.agent.DQNAgent`)으로, 사슴은 무작위로 행동한다.
> - `track_reward_group`: 어느 그룹의 에피소드 보상을 추적할지 지정하는 파라미터.
> - `filter_group`: 경험을 생성할 그룹을 제한하는 선택적 필터. 이 예제에서는 (호랑이만 학습하므로) 호랑이 관측만 필요하지만, 다음 절에서 호랑이와 사슴을 모두 학습시킬 때는 이 필터를 비활성화한다.

생성자 안에서는 인자들을 저장하고, 에이전트를 위한 두 가지 유용한 매핑을 만든다 — **에이전트 ID → 그룹 이름**, 그리고 그 역방향.

```python
        self.env = env
        self.agents_by_group = agents_by_group
        self.track_reward_group = track_reward_group
        self.env_seed = env_seed
        self.filter_group = filter_group
        self.total_rewards = []
        self.total_steps = []

        # agent_id -> group 순방향·역방향 매핑
        self.agent_groups = {
            agent_id: self.agent_group(agent_id)
            for agent_id in self.env.agents
        }
        self.group_agents = collections.defaultdict(list)
        for agent_id, group in self.agent_groups.items():
            self.group_agents[group].append(agent_id)

    @classmethod
    def agent_group(cls, agent_id: str) -> str:
        a, _ = agent_id.split("_", maxsplit=1)
        return a
```

`agent_group`은 에이전트의 숫자 ID를 잘라내고 그룹 이름(`tiger` 또는 `deer`)만 남기는 유틸리티 메서드다. `collections.defaultdict(list)`를 쓰는 이유는 [[defaultdict와 Counter]]에서 복습할 수 있다 — 키가 처음 나올 때 자동으로 빈 리스트를 만들어주기 때문에 매번 존재 여부를 확인하지 않아도 된다.

### 4.2 반복자(iterator) 인터페이스 — 실제 경험 생성

이 클래스의 핵심 메서드는 환경으로부터 경험 항목을 만들어내는 반복자 인터페이스다.

```python
    def __iter__(self) -> tt.Generator[ExperienceFirstLastMARL, None, None]:
        # 에피소드를 계속 반복
        while True:
            # 초기 관측
            cur_obs = self.env.reset(self.env_seed)

            # 에이전트 상태는 그룹별로 유지
            agent_states = {
                prefix: [self.agents_by_group[prefix].initial_state() for _ in group]
                for prefix, group in self.group_agents.items()
            }
```

여기서 환경을 초기화하고, 에이전트별 초기 상태를 만든다(이 챕터 예제의 에이전트들은 상태 없는(stateless) 정책이지만, 만약 RNN처럼 상태가 있는 에이전트라면 대비가 필요하기 때문이다).

그 다음, 살아있는 에이전트가 있는 동안 에피소드를 반복한다(앞 절 예제와 같은 방식). 이 루프에서는 에이전트 ID를 행동에 매핑하는 딕셔너리를 채운다. PTAN `BaseAgent` 인스턴스는 관측의 **배치(batch)** 단위로 동작하므로, 그룹 전체의 행동을 한 번에 매우 효율적으로 만들어낼 수 있다.

```python
            episode_steps = 0
            episode_rewards = 0.0
            # 살아있는 에이전트가 있는 동안 반복
            while self.env.agents:
                # 그룹 전체의 행동을 계산하고 다시 풀어헤친다
                actions = {}
                for prefix, group in self.group_agents.items():
                    gr_obs = [
                        cur_obs[agent_id]
                        for agent_id in group if agent_id in cur_obs
                    ]
                    gr_actions, gr_states = self.agents_by_group[prefix](
                        gr_obs, agent_states[prefix])
                    agent_states[prefix] = gr_states
                    idx = 0
                    for agent_id in group:
                        if agent_id not in cur_obs:
                            continue
                        actions[agent_id] = gr_actions[idx]
                        idx += 1
```

행동을 다 만들면 환경에 보내고, 새로운 관측·보상·종료(done)·중단(truncation) 플래그가 담긴 딕셔너리를 받는다. 그 다음 현재 살아있는 모든 에이전트에 대해 경험 항목을 생성한다.

```python
            new_obs, rewards, dones, truncs, _ = self.env.step(actions)

            for agent_id, reward in rewards.items():
                group = self.agent_groups[agent_id]
                if group == self.track_reward_group:
                    episode_rewards += reward
                if self.filter_group is not None:
                    if group != self.filter_group:
                        continue
                last_state = new_obs[agent_id]
                if dones[agent_id] or truncs[agent_id]:
                    last_state = None
                yield ExperienceFirstLastMARL(
                    state=cur_obs[agent_id], action=actions[agent_id],
                    reward=reward, last_state=last_state, group=group
                )
                cur_obs = new_obs
                episode_steps += 1
```

에피소드가 끝나면 걸린 스텝 수와 그룹의 평균 보상을 기록한다.

```python
        self.total_steps.append(episode_steps)
        tr_group = self.group_agents[self.track_reward_group]
        self.total_rewards.append(episode_rewards / len(tr_group))
```

이 클래스만 있으면, DQN 학습 코드 자체는 단일 에이전트 RL과 거의 그대로다. 전체 소스는 `forest_tigers_dqn.py`에 있다. 여기서는 PTAN 에이전트와 경험 소스가 만들어지는 부분만 발췌해서 어떻게 `MAgentExperienceSourceFirstLast`를 쓰는지 보자.

```python
action_selector = \
    ptan.actions.EpsilonGreedyActionSelector(epsilon=PARAMS.epsilon_start)
epsilon_tracker = common.EpsilonTracker(action_selector, PARAMS)
tiger_agent = ptan.agent.DQNAgent(net, action_selector, device)
deer_agent = data.RandomMAgent(env, env.handles[0])
exp_source = data.MAgentExperienceSourceFirstLast(
    env,
    agents_by_group={'deer': deer_agent, 'tiger': tiger_agent},
    track_reward_group="tiger",
    filter_group="tiger",
)
buffer = ptan.experience.ExperienceReplayBuffer(exp_source, PARAMS.replay_size)
```

([[엡실론-그리디 탐험]], [[경험 재생 Experience Replay]] 참고.) 보다시피 호랑이는 신경망(아주 단순한 2층 합성곱 + 2층 완전연결 네트워크)이 조종하고, 사슴 그룹은 난수 생성기가 조종한다. 리플레이 버퍼는 `filter_group="tiger"` 인자 덕분에 호랑이의 경험만으로 채워진다.

### 4.3 학습과 결과

학습을 시작하려면 `./forest_tigers_dqn.py -n run_name --dev cuda`를 실행한다. **1시간 학습** 후, 호랑이의 테스트 보상은 최고 **82점**에 도달했다 — 무작위 기준선 대비 상당한 개선이다. 무작위로 행동하면 대부분의 호랑이가 20스텝 안에 죽고 몇몇 운 좋은 개체만 더 오래 산다.

이 점수를 얻기 위해 사슴이 몇 마리나 사냥당했는지 계산해 보자. 처음에 각 호랑이는 체력 10을 갖고, 매 스텝 체력 0.5를 소모한다. 맵에는 호랑이 40마리, 사슴 204마리가 있다(명령행 인자로 이 수를 바꿀 수 있다). 사슴 한 마리를 먹을 때마다 호랑이는 체력 8을 얻는데, 이는 16스텝을 더 살 수 있게 해준다. 매 스텝 각 호랑이는 보상 1을 얻으므로, 40마리 호랑이가 사슴을 먹어서 얻은 "초과 보상"은 $82 \cdot 40 - 20 \cdot 40 = 2480$이다. 사슴 한 마리당 체력 8을 주고, 이는 수명 16스텝으로 환산되므로, 잡아먹힌 사슴 수는 $2480/16 = 155$마리다. 즉 최선의 정책으로 전체 사슴의 거의 **76%**가 사냥당했다 — 사슴이 무작위로 배치되고 호랑이가 직접 접근해서 공격해야 하는 걸 생각하면 나쁘지 않은 결과다.

정책 개선이 멈춘 이유는 아마도 호랑이의 **시야가 제한적**이기 때문일 가능성이 크다. 궁금하다면 환경 설정에서 미니맵을 켜고 실험해 볼 수 있다. 먹이의 위치 정보가 더 많아지면 정책이 더 좋아질 가능성이 있다.

*그림 22.2*는 학습 중 평균 보상과 스텝 수를 보여준다. 여기서 볼 수 있듯, 주요 성장은 처음 300 에피소드 동안 일어났고 그 이후로는 학습 진전이 거의 없었다.

![[fig_22_2.png]]
*그림 22.2 — 학습 에피소드의 평균 보상(왼쪽)과 스텝 수(오른쪽)*

하지만 *그림 22.3*의 **테스트 보상과 스텝 수** 그래프를 보면, 300 에피소드(약 0.4시간 학습) 이후에도 정책이 계속 개선되었음을 알 수 있다.

![[fig_22_3.png]]
*그림 22.3 — 테스트 에피소드의 평균 보상(왼쪽)과 스텝 수(오른쪽)*

마지막으로 *그림 22.4*는 학습 중의 손실(loss)과 엡실론(epsilon)을 보여준다. 두 그래프는 서로 연관되어 있는데, 이는 학습 중 대부분의 새로움(novelty)이 **탐험 단계**에서 얻어졌음을 시사한다(손실 값이 높다는 건 학습 중 새로운 상황이 계속 나타난다는 뜻이다). 이는 더 나은 탐험 방법이 최종 정책에 도움이 될 수 있다는 힌트다.

![[fig_22_4.png]]
*그림 22.4 — 학습 중 평균 손실(왼쪽)과 엡실론(오른쪽)*

여느 때처럼 저자는 학습된 모델을 실제로 확인해볼 수 있는 도구도 구현했다 — `forest_tigers_play.py`로, 학습된 모델을 불러와 에피소드를 실행하며 관측을 영상으로 기록한다. 최고 점수(82.89) 모델의 영상을 보면, 호랑이의 사냥 실력이 무작위 정책보다 훨씬 좋아져서, 에피소드가 끝날 때 처음 204마리였던 사슴 중 겨우 53마리만 남는다.

---

## 5. 호랑이들의 협력

두 번째 실험은 호랑이의 삶을 **더 어렵게** 만들어서, 호랑이끼리 **협력**하도록 유도하는 것이다. 학습·실행 코드는 그대로이고, 차이는 오직 MAgent 환경 설정에 있다.

훈련 유틸리티에 `--mode double_attack` 인자를 넘기면, `data.DoubleAttackEnv` 환경이 쓰인다. 유일한 차이는 설정 객체이며, 여기서 호랑이의 공격 방식에 추가 제약이 걸린다. 새 설정에서는 호랑이가 **오직 짝을 지어서, 동시에** 공격해야만 사슴을 잡을 수 있다. 호랑이 한 마리만으로는 공격이 아무 효과가 없다. 이는 사슴을 잡아 보상을 얻는 일을 훨씬 어렵게 만들어, 학습과 사냥 모두를 확실히 복잡하게 만든다.

학습을 시작하려면 같은 유틸리티에 추가 명령행 인자를 넘긴다.

```bash
./forest_tigers_dqn.py -n run_name --dev cuda --mode double_attack
```

*그림 22.5*는 `double_attack` 모드의 학습 에피소드에 대한 보상과 스텝 플롯을 보여준다. 2시간 학습 후에도 보상은 여전히 개선되고 있고, 에피소드 스텝 수는 300을 넘지 않는다 — 이는 호랑이 주변에 사냥할 사슴이 마땅치 않아 굶어 죽는 경우가 많다는 뜻일 수도 있고, 그저 환경 자체의 내부 스텝 제한일 수도 있다.

![[fig_22_5.png]]
*그림 22.5 — double_attack 모드 학습 에피소드의 평균 보상(왼쪽)과 스텝 수(오른쪽)*

단일 호랑이 사냥 모드와 대조적으로, *그림 22.6*처럼 학습 중 손실이 잘 줄어들지 않는다 — 이는 학습 하이퍼파라미터를 개선할 여지가 있음을 시사한다.

![[fig_22_6.png]]
*그림 22.6 — double_attack 모드 학습 중 평균 손실*

모델을 실제로 테스트하려면 같은 유틸리티에 `--mode double_attack` 인자를 넘기면 된다. 저자가 얻은 최고 모델의 영상을 보면, 호랑이들이 이제는 **짝을 지어 움직이며 사슴을 함께 공격**하는 모습을 확인할 수 있다.

---

## 6. 호랑이와 사슴을 함께 학습시키기

다음 예제는 호랑이와 사슴 **둘 다** 서로 다른 DQN 모델로 제어되며 **동시에 학습**되는 시나리오다. 호랑이는 오래 살수록 보상을 받는데, 이는 (매 스텝 체력을 잃으므로) 사슴을 더 많이 먹도록 자극한다. 사슴도 매 타임스텝마다 보상을 받는다.

코드는 `forest_both_dqn.py`에 있고, 이전 예제를 확장한 것이다. 두 그룹 각각에 대해 별도의 `DQNAgent` 클래스 인스턴스가 있으며, 서로 다른 신경망으로 관측을 행동으로 바꾼다. 경험 소스는 그대로지만, 이제 호랑이 그룹으로만 필터링하지 않는다(`filter_group=None`). 이 때문에 리플레이 버퍼에는 환경의 **모든** 에이전트로부터 온 관측이 담기게 된다. 학습 중에는 배치를 샘플링한 뒤, 사슴과 호랑이 경험을 두 개의 별도 배치로 나눠서 각자의 네트워크를 학습시킨다.

세부 사항이 이전 예제와 크게 다르지 않아서 여기서는 전체 코드를 싣지 않는다(궁금하면 깃허브 저장소의 소스를 확인할 것). *그림 22.7*은 호랑이의 학습 보상과 스텝을 보여준다. 처음에는 호랑이가 꾸준히 보상을 늘려가지만, 나중에는 성장이 멈춘다.

![[fig_22_7.png]]
*그림 22.7 — 호랑이의 학습 평균 보상(왼쪽)과 학습 에피소드 스텝 수(오른쪽)*

*그림 22.8*은 테스트 중 호랑이와 사슴의 보상을 보여준다.

![[fig_22_8.png]]
*그림 22.8 — 테스트 중 호랑이(왼쪽)와 사슴(오른쪽)의 보상*

여기서는 뚜렷한 추세가 보이지 않는다 — 두 그룹이 서로 경쟁하며 상대를 이기려 하고 있다. *그림 22.8*에서 보듯 **사슴이 호랑이보다 훨씬 성공적**인데, 이는 놀랍지 않다. 둘의 이동 속도가 같으므로, 사슴은 그냥 계속 움직이면서 호랑이가 굶어 죽기를 기다리기만 하면 되기 때문이다. 원한다면 호랑이의 속도를 높이거나 벽의 밀도를 높여서 환경 설정을 실험해 볼 수 있다.

이전처럼 `forest_both_play.py` 유틸리티로 학습된 정책을 시각화할 수 있는데, 이번엔 모델 파일을 두 개(사슴용, 호랑이용) 넘겨야 한다. 저자가 만든 영상을 보면, 모든 사슴이 화면 왼쪽으로만 계속 이동하는 단순한 정책을 쓰는 것을 볼 수 있다 — 아마 호랑이들이 이 단순한 패턴을 자기에게 유리하게 이용(exploit)할 수 있을 것이다.

---

## 7. 전투(battle) 환경

호랑이-사슴 환경 외에도, MAgent에는 `magent2.builtin.config`와 `magent2.environment` 패키지에 여러 사전 정의된 설정이 더 있다. 이 챕터의 마지막 예제로, 두 그룹이 (잡아먹지 않고, 다행히도) **서로 싸우는** "전투(battle)" 설정을 살펴본다.

코드는 `battel_dqn.py`(원문 그대로의 파일명)에서 찾을 수 있다. 이 설정에서 양쪽 그룹 모두 체력 10을 갖고, 공격 한 번마다 체력 2를 잃는다 — 즉 연속으로 5번 공격해야 보상을 받는다. 한쪽 그룹은 무작위로 행동하고, 다른 쪽은 DQN으로 정책을 개선한다. 학습에 2시간이 걸렸고, DQN은 꽤 괜찮은 정책을 찾아냈지만, 끝에 가서 학습 과정이 **발산**했다. *그림 22.9*는 학습과 테스트 보상 플롯을 보여준다.

![[fig_22_9.png]]
*그림 22.9 — battle 시나리오에서 학습(왼쪽)과 테스트(오른쪽) 중 평균 보상*

영상 기록(도구 `battle_play.py`로 제작)을 보면, 파란 팀은 무작위로 움직이고 빨간 팀은 DQN이 조종한다.

---

## 요약

이 챕터에서 우리는 MARL이라는 매우 흥미롭고 역동적인 분야를 살짝 맛보았다. 이 분야는 트레이딩 시뮬레이션, 통신망 등 실전 응용이 다양하다. MAgent 환경(또는 PySC2 같은 다른 환경)으로 스스로 실험해 볼 수 있는 것들이 아주 많다.

이 책 전체를 마치며, 다음과 같은 흐름을 되짚어볼 만하다.
1. **RL이 무엇인지**부터 시작해, 지도학습·비지도학습과의 차이(1장)를 배웠다.
2. **표 기반 학습, DQN, 정책 경사, 액터-크리틱** 등 여러 핵심 알고리즘 계열을 익혔다.
3. **트레이딩, 텍스트 게임, 웹 내비게이션, 이산 최적화, 자기 대전** 같은 다양한 실전 응용을 다뤘다.
4. 마지막으로 이번 챕터에서 **다중 에이전트**라는 새로운 차원을 소개했다.

아직 다루지 못한 매우 흥미로운 주제들도 많다 — 환경 관측이 마르코프 성질을 만족하지 않는 **부분 관측 마르코프 결정 과정([[POMDP 부분관측 마르코프결정과정]])**, 최근 각광받는 **카운트 기반 탐험(count-based exploration)** 방법, 여러 에이전트가 공통 문제를 함께 풀도록 조율하는 심화 MARL 기법, 그리고 에이전트가 지식과 경험을 기억으로 유지하는 **메모리 기반 RL** 접근 등이다. RL의 표본 효율성(sample efficiency)을 인간 수준에 가깝게 끌어올리려는 노력도 계속되고 있지만, 아직은 요원한 목표다. 새 아이디어가 거의 매일 나타나는 분야이니만큼, 책 한 권으로 전체 도메인을 다 담는 것은 애초에 불가능하다.

이 책의 목표는 이 분야의 **실용적인 토대**를 제공해서, 각자 스스로 새로운 방법을 익혀나갈 수 있도록 돕는 것이었다. Volodymyr Mnih이 2017년 Deep RL Bootcamp(Berkeley) 강연 *Recent Advances, Frontiers and Future of Deep RL*에서 남긴 말로 마무리한다 — 지금도 여전히 유효한 말이다: *"딥 RL이라는 분야는 아직 매우 새롭고, 모든 것이 여전히 흥미진진하다. 말 그대로 아무것도 아직 다 풀리지 않았다!"*

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[다중 에이전트 강화학습 MARL]]
- [[협력과 경쟁 MARL]]
- [[Wrapper 래퍼 패턴]]
- [[데이터클래스 dataclass]]
- [[defaultdict와 Counter]]
- [[ExperienceSource와 리플레이버퍼]]
- [[경험 재생 Experience Replay]]
- [[엡실론-그리디 탐험]]
- [[POMDP 부분관측 마르코프결정과정]]

## 한눈에 보는 개념 지도
| 개념 | 기호/이름 | 한 줄 뜻 |
|---|---|---|
| 다중 에이전트 RL | MARL | 환경 안에 에이전트가 여러 명 있는 강화학습 |
| 협력 | Collaborative | 여러 에이전트가 공동 목표를 위해 힘을 합침 |
| 경쟁 | Competitive | 에이전트끼리 서로 이기려고 겨룸 |
| MAgent(2) | - | C++ 기반의 가볍고 확장성 좋은 다중 에이전트 그리드 월드 환경 |
| 그룹(group) | tiger/deer | 서로 다른 특성·역할을 가진 에이전트 집단 |
| ExperienceFirstLastMARL | - | 경험 항목에 소속 그룹 이름을 추가한 데이터클래스 |
| filter_group | - | 리플레이 버퍼에 어느 그룹의 경험만 남길지 지정하는 필터 |
| double_attack | - | 호랑이가 반드시 짝을 지어 동시 공격해야 하는 협력 유도 설정 |
