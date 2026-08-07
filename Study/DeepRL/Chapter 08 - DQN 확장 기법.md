---
title: "Chapter 8 — DQN 확장 기법 (DQN Extensions)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 8
tags: [DeepRL, 강화학습, DQN, Rainbow, DoubleDQN, NoisyNetworks, PrioritizedReplay, DuelingDQN, CategoricalDQN, DistributionalRL]
---

# Chapter 8 · DQN 확장 기법

> [!abstract] 이 챕터를 한 문장으로
> 2015년에 나온 기본 **DQN**은 여러 단점을 가지고 있었고, 그 뒤로 연구자들이 하나씩 문제를 짚어가며 개선안을 내놓았다. 이 챕터에서는 **N-step, Double DQN, Noisy Networks, 우선순위 리플레이(Prioritized Replay), Dueling DQN, Categorical(분포적) DQN**을 하나씩 뜯어보고, 마지막으로 이들을 모두 합친 **Rainbow**가 왜 그렇게 강력한지 확인한다.

---

## 들어가며 — 왜 "확장"이 필요한가?

6장에서 만든 DQN은 확실히 동작했다. 하지만 "동작한다"와 "잘 동작한다"는 다른 이야기다. 기본 DQN은 학습이 느리고, 불안정하고, 값을 과대평가(overestimate)하는 등 여러 고질병을 안고 있다.

2017년 10월, 딥마인드(DeepMind)의 Hessel 등은 *Rainbow: Combining Improvements in Deep Reinforcement Learning*이라는 논문에서, 그동안 따로따로 발표됐던 6가지 개선 기법을 **한 번에 결합**하면 얼마나 좋아지는지 보여주었다. 어떤 기법은 2015년만큼 오래됐고, 어떤 기법은 논문 발표 시점 기준으로 비교적 최신이었다. 이 여섯 기법을 무지개(Rainbow)처럼 겹쳐 쌓았다고 해서 이름이 Rainbow다.

> [!note] 2017년 이후에도 여전히 유효한가?
> 책 원문 저자는 이렇게 말한다 — "2017년 이후로 더 많은 논문이 나왔고 최신 기록은 더 갱신됐지만, Rainbow 논문에 실린 방법들은 지금도 여전히 관련성이 높고 널리 쓰인다." 실제로 2023년에는 이 챕터에서 다룰 방법 중 하나(분포적 RL)만 다루는 책이 따로 나올 정도다. 게다가 여기서 배울 기법들은 상대적으로 **간단하고 이해하기 쉬워서**, 기초를 다지기에 아주 좋은 재료다.

이 챕터에서 다룰 6가지 확장 기법은 다음과 같다.

- **N-step DQN**: 벨만 방정식을 살짝 풀어써서(unroll) 수렴 속도와 안정성을 높이는 방법. 왜 "만능 해결책"은 아닌지도 함께 본다.
- **Double DQN**: DQN이 행동 가치를 과대평가하는 문제를 어떻게 다루는가.
- **Noisy Networks**: 네트워크 가중치에 노이즈를 더해서 더 효율적으로 탐험(exploration)하는 방법.
- **우선순위 리플레이 버퍼 (Prioritized Replay Buffer)**: 네트워크 구조를 문제에 더 가깝게 만들어 수렴 속도를 높이는 방법 — 정확히는, 경험(experience)을 균등하게 뽑지 않고 "중요한" 경험을 더 자주 뽑는 방법.
- **Dueling DQN**: 네트워크 구조를 문제 자체에 더 가깝게 표현해서 수렴을 빠르게 하는 방법.
- **Categorical DQN**: 행동 가치를 숫자 하나(기댓값)로 뭉개지 않고, **분포(distribution)** 그 자체로 다루는 방법.

각 기법의 아이디어를 살펴보고, 어떻게 구현하는지, 그리고 기본 DQN과 비교했을 때 성능이 어떻게 달라지는지 확인한다. 마지막에는 이 모든 방법을 합친 시스템이 얼마나 강력한지 살펴본다.

---

## 1. Basic DQN — 출발선 다시 세우기

이 챕터의 모든 실험은 **같은 출발선**에서 시작해야 공정하게 비교할 수 있다. 그래서 먼저 6장과 똑같은 DQN을, 이번엔 7장에서 배운 고수준 도구(PTAN, Ignite)를 활용해서 다시 구현한다. 이렇게 하면 코드가 훨씬 간결해져서, 핵심 로직이 부수적인 디테일에 묻히지 않는다.

> [!tip] 왜 굳이 라이브러리를 안 쓰고 직접 구현을 배우나?
> "이 책의 목적은 기존 라이브러리 사용법을 가르치는 것이 아니라, RL 방법에 대한 직관을 기르고, 필요하면 처음부터 구현할 수 있게 하는 것"이라고 저자는 말한다. 라이브러리는 계속 바뀌지만, 도메인에 대한 진짜 이해는 남아서 남의 코드를 빠르게 파악하고 응용하는 능력을 준다.

기본 DQN 구현은 `Chapter08` 폴더에 3개 모듈로 나뉜다.
- `lib/dqn_model.py`: 6장과 똑같은 DQN 신경망(NN).
- `lib/common.py`: 이 챕터의 코드가 공유하는 공통 함수·선언들.
- `01_dqn_basic.py`: PTAN과 Ignite 라이브러리를 활용한 77줄짜리 기본 DQN 구현.

### 1.1 공통 라이브러리 (`common.py`)

먼저 하이퍼파라미터를 담는 `dataclass`를 정의한다. `dataclass`는 타입 주석이 붙은 데이터 필드 여러 개를 묶어서 저장하는 표준적인 방법이다.

```python
@dataclasses.dataclass
class Hyperparams:
    env_name: str
    stop_reward: float
    run_name: str
    replay_size: int
    replay_initial: int
    target_net_sync: int
    epsilon_frames: int

    learning_rate: float = 0.0001
    batch_size: int = 32
    gamma: float = 0.99
    epsilon_start: float = 1.0
    epsilon_final: float = 0.1

    tuner_mode: bool = False
    episodes_to_solve: int = 500
```

- `env_name`, `stop_reward` 등: 어떤 환경을 쓸지, 목표 보상은 얼마인지 등 환경별 설정값.
- `replay_size`, `replay_initial`: 리플레이 버퍼 크기, 학습 전 채워둘 최소 개수.
- `target_net_sync`: 타깃 네트워크를 몇 스텝마다 동기화할지.
- `= 0.0001`처럼 기본값이 붙은 필드는 여러 게임에 공통으로 쓸 수 있는 값이다.

이 하이퍼파라미터를 게임 이름으로 찾아 쓸 수 있게 딕셔너리로도 묶어둔다.

```python
GAME_PARAMS = {
    'pong': Hyperparams(
        env_name="PongNoFrameskip-v4",
        stop_reward=18.0,
        run_name="pong",
        replay_size=100_000,
        replay_initial=10_000,
        target_net_sync=1000,
        epsilon_frames=100_000,
        epsilon_final=0.02,
    ),
}
```

다음으로 배치 처리 함수 `unpack_batch`가 있다. `ExperienceSourceFirstLast`가 만들어주는 트랜지션(`ExperienceFirstLast`)은 다음 필드를 가진 dataclass다.

- `state`: 환경에서 얻은 관측(observation).
- `action`: 에이전트가 취한 정수 행동.
- `reward`: `steps_count=1`이면 즉시 보상 그대로. n-step이 더 크면 그 스텝 수만큼의 할인 합산 보상.
- `last_state`: 해당 트랜지션이 에피소드의 마지막 스텝이면 `None`, 아니면 마지막 관측.

```python
def unpack_batch(batch: tt.List[ExperienceFirstLast]):
    states, actions, rewards, dones, last_states = [],[],[],[],[]
    for exp in batch:
        states.append(exp.state)
        actions.append(exp.action)
        rewards.append(exp.reward)
        dones.append(exp.last_state is None)
        if exp.last_state is None:
            lstate = exp.state  # 어차피 마스킹되니 아무 값이나 넣어도 됨
        else:
            lstate = exp.last_state
        last_states.append(lstate)
    return np.asarray(states), np.array(actions), np.array(rewards, dtype=np.float32), \
        np.array(dones, dtype=bool), np.asarray(last_states)
```

**핵심 포인트**: 에피소드가 끝난(terminal) 트랜지션을 특별 취급하지 않으려고, `last_state`가 없을 땐 그냥 시작 상태(`exp.state`)를 임시로 채워 넣는다. 대신 나중에 손실 계산에서 `dones` 배열로 그 항목을 **마스킹**해서 값이 계산에 영향을 주지 않게 한다. (이렇게 안 하고 "종료된 트랜지션만 따로 값 계산을 생략"하는 방법도 있지만, 코드가 더 복잡해진다.)

DQN 손실 함수 `calc_loss_dqn`은 6장과 거의 동일하고, `torch.no_grad()`가 새로 추가됐다. 이건 타깃 네트워크(target net) 계산이 파이토치의 계산 그래프(연쇄법칙을 위해 미분 정보를 저장하는 구조)에 기록되지 않게 막는 역할이다 — 어차피 타깃 네트워크는 역전파 대상이 아니므로 그래프를 만들 필요가 없다.

```python
def calc_loss_dqn(
        batch: tt.List[ExperienceFirstLast], net: nn.Module, tgt_net: nn.Module,
        gamma: float, device: torch.device) -> torch.Tensor:
    states, actions, rewards, dones, next_states = unpack_batch(batch)

    states_v = torch.as_tensor(states).to(device)
    next_states_v = torch.as_tensor(next_states).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.BoolTensor(dones).to(device)

    actions_v = actions_v.unsqueeze(-1)
    state_action_vals = net(states_v).gather(1, actions_v)
    state_action_vals = state_action_vals.squeeze(-1)
    with torch.no_grad():
        next_state_vals = tgt_net(next_states_v).max(1)[0]
        next_state_vals[done_mask] = 0.0

    bellman_vals = next_state_vals.detach() * gamma + rewards_v
    return nn.MSELoss()(state_action_vals, bellman_vals)
```

한 줄씩 보면: `gather(1, actions_v)`로 각 상태에서 **실제로 취한 행동의 Q값**만 뽑아낸다. `tgt_net(next_states_v).max(1)[0]`으로 다음 상태에서 가장 좋은 행동의 값을 구하되, 그 값은 (`no_grad` 안이므로) 학습 대상이 아니다. `next_state_vals[done_mask] = 0.0`은 에피소드가 끝난 트랜지션은 "미래 가치 없음"으로 강제 처리하는 부분이다. 마지막으로 벨만 방정식대로 `보상 + γ × 다음상태값`을 만들어 MSE(평균제곱오차) 손실을 구한다.

### 1.2 학습 루프를 위한 유틸리티들

**입실론 감쇠(epsilon decay)**: 학습 초반엔 완전히 무작위(1.0)로 행동하다가 점점 그 확률을 줄여 0.02나 0.01 같은 작은 값으로 만든다. 거의 모든 DQN에 필요한 뻔한 로직이라 아래 작은 클래스로 제공된다.

```python
class EpsilonTracker:
    def __init__(self, selector: EpsilonGreedyActionSelector, params: Hyperparams):
        self.selector = selector
        self.params = params
        self.frame(0)

    def frame(self, frame_idx: int):
        eps = self.params.epsilon_start - frame_idx / self.params.epsilon_frames
        self.selector.epsilon = max(self.params.epsilon_final, eps)
```

`frame_idx`가 커질수록(=학습이 진행될수록) `eps`가 선형으로 줄어들다가 `epsilon_final` 아래로는 안 내려가게 `max()`로 하한선을 건다.

**배치 생성기 `batch_generator`**: `ExperienceReplayBuffer`(7장에서 배운 PTAN 클래스)를 받아 학습용 배치를 끝없이 만들어주는 제너레이터다. 시작할 때는 버퍼가 최소한의 샘플(`initial`)을 채울 때까지 기다린다.

```python
def batch_generator(buffer: ExperienceReplayBuffer, initial: int, batch_size: int) -> \
        tt.Generator[tt.List[ExperienceFirstLast], None, None]:
    buffer.populate(initial)
    while True:
        buffer.populate(1)
        yield buffer.sample(batch_size)
```

**Ignite 연결 함수 `setup_ignite`**: 길지만 매우 유용한 함수로, 학습 진행 상황을 보여주고 지표를 텐서보드(TensorBoard)에 기록하는 Ignite 핸들러들을 붙여준다.

- `EndOfEpisodeHandler`: 게임 에피소드가 끝날 때마다 Ignite 이벤트를 발생시킨다. 평균 보상이 목표치를 넘으면 "게임을 풀었다"는 이벤트도 발생시킨다.
- `EpisodeFPSHandler`: 에피소드가 걸린 시간과 환경과 상호작용한 횟수를 추적해서 **FPS**(초당 프레임 수, 성능을 재는 중요한 지표)를 계산한다.

```python
@engine.on(ptan_ignite.EpisodeEvents.EPISODE_COMPLETED)
def episode_completed(trainer: Engine):
    passed = trainer.state.metrics.get('time_passed', 0)
    print("Episode %d: reward=%.0f, steps=%s, speed=%.1f f/s, elapsed=%s" % (
        trainer.state.episode, trainer.state.episode_reward,
        trainer.state.episode_steps, trainer.state.metrics.get('avg_fps', 0),
        timedelta(seconds=int(passed))))

@engine.on(ptan_ignite.EpisodeEvents.BOUND_REWARD_REACHED)
def game_solved(trainer: Engine):
    passed = trainer.state.metrics['time_passed']
    print("Game solved in %s, after %d episodes and %d iterations!" % (
        timedelta(seconds=int(passed)), trainer.state.episode, trainer.state.iteration))
    trainer.should_terminate = True
    trainer.state.solved = True
```

하나는 에피소드가 끝날 때마다 콘솔에 정보를 찍고, 다른 하나는 평균 보상이 하이퍼파라미터로 정한 경계(퐁에서는 18.0)를 넘으면 "게임 풀림" 메시지를 찍고 학습을 멈춘다.

나머지 코드는 텐서보드 기록 관련이다. `TensorboardLogger`를 만들고, 손실값의 **이동평균(RunningAverage)**을 붙이고, `episodes`/`train`이라는 태그로 보상·스텝수·평균보상, 그리고 평균손실·FPS 같은 지표를 각각 다른 주기로 저장한다(매 이터레이션마다 저장하면 파일이 너무 커지므로 학습 지표는 100 이터레이션마다 저장).

### 1.3 구현 — `01_dqn_basic.py`

환경을 만들고 표준 래퍼(6·9장에서 다룸)를 씌운 뒤, DQN 모델과 타깃 네트워크를 만든다.

```python
env = gym.make(params.env_name)
env = ptan.common.wrappers.wrap_dqn(env)

net = dqn_model.DQN(env.observation_space.shape, env.action_space.n).to(device)
tgt_net = ptan.agent.TargetNet(net)
```

입실론-그리디(epsilon-greedy) 행동 선택기를 넣어 에이전트를 만든다.

```python
selector = ptan.actions.EpsilonGreedyActionSelector(epsilon=params.epsilon_start)
epsilon_tracker = common.EpsilonTracker(selector, params)
agent = ptan.agent.DQNAgent(net, selector, device=device)
```

학습 중에는 `EpsilonTracker`가 입실론을 서서히 줄여 무작위 선택 비중을 낮추고 신경망에 더 많은 권한을 넘긴다.

다음으로 트랜지션 소스와 리플레이 버퍼.

```python
exp_source = ptan.experience.ExperienceSourceFirstLast(
    env, agent, gamma=params.gamma, env_seed=common.SEED)
buffer = ptan.experience.ExperienceReplayBuffer(
    exp_source, buffer_size=params.replay_size)
```

`ExperienceSourceFirstLast`가 에이전트와 환경으로부터 게임 에피소드에 걸친 트랜지션을 만들고, 그것들이 리플레이 버퍼에 쌓인다.

옵티마이저와 배치 처리 함수를 정의한다.

```python
optimizer = optim.Adam(net.parameters(), lr=params.learning_rate)

def process_batch(engine, batch):
    optimizer.zero_grad()
```

```python
    loss_v = common.calc_loss_dqn(batch, net, tgt_net.target_model,
                                   gamma=params.gamma, device=device)
    loss_v.backward()
    optimizer.step()
    epsilon_tracker.frame(engine.state.iteration)
    if engine.state.iteration % params.target_net_sync == 0:
        tgt_net.sync()
    return {
        "loss": loss_v.item(),
        "epsilon": selector.epsilon,
    }
```

이 함수는 트랜지션 배치마다 한 번씩 호출된다. `common.calc_loss_dqn`을 불러 손실을 계산하고 역전파한 뒤, `EpsilonTracker`에게 입실론을 줄이라고 시키고, 주기적으로 타깃 네트워크를 동기화한다.

마지막으로 Ignite `Engine` 객체를 만들고 학습을 시작한다.

```python
engine = Engine(process_batch)
common.setup_ignite(engine, params, exp_source, NAME)
engine.run(common.batch_generator(buffer, params.replay_initial, params.batch_size))
```

### 1.4 하이퍼파라미터 튜닝 — 공정한 비교를 위한 준비

각 DQN 확장 기법을 공정하게 비교하려면 **같은 게임(퐁)이라도 방법마다 하이퍼파라미터를 따로 튜닝**해야 한다. 방법의 디테일이 달라지면 같은 고정 하이퍼파라미터 세트로도 최적의 결과가 안 나올 수 있기 때문이다.

원칙적으로 다음 모든 것이 튜닝 대상이 될 수 있다.

- 네트워크 구성: 레이어 개수·크기, 활성화 함수, 드롭아웃 등
- 최적화 파라미터: 옵티마이저 종류(바닐라 SGD, Adam, AdaGrad 등), 학습률
- 탐험 파라미터: 입실론 감쇠 속도, 최종 입실론 값
- 벨만 방정식의 할인율 γ

하지만 튜닝할 파라미터가 늘어날수록 시도해봐야 할 학습 횟수가 곱셈적으로 늘어난다. 구글이나 메타 같은 회사는 압도적으로 많은 GPU를 갖고 있지만 개인 연구자는 그렇지 않으므로 균형을 잡아야 한다. 이 책에서는 학습률, 할인율 γ, 그리고 해당 확장 기법 고유의 파라미터 정도만 탐색한다.

**Ray Tune** 라이브러리(Ray 프로젝트의 일부, 분산 컴퓨팅 프레임워크)를 쓴다. 크게 두 가지를 정의해야 한다.

1. 탐색하고 싶은 하이퍼파라미터 공간(범위, 혹은 시도할 값의 명시적 목록)
2. 특정 하이퍼파라미터 값들로 학습을 수행하고, 최적화하고 싶은 지표를 반환하는 함수

> [!note] 하이퍼파라미터 튜닝도 결국 최적화 문제
> 겉보기엔 신경망 학습(경사하강)과 비슷하지만 결정적 차이가 있다. **최적화 대상 함수가 미분 불가능**해서 경사하강으로 파라미터를 밀 수 없고, 최적화 공간이 **이산적**일 수도 있다(레이어 개수를 2.435로 만들 순 없으니까). 그래서 이 책에서는 가장 단순한 방법 — **무작위 탐색(random search)** — 을 쓴다. `ray.tune`이 하이퍼파라미터를 무작위로 여러 번 뽑아 함수를 호출하고, 가장 작은(또는 큰) 지표 값을 낸 조합이 최선으로 채택된다.

이 챕터에서 쓰는 지표는 **게임을 풀 때까지(퐁 평균 점수 18 초과) 필요한 게임 판수**다.

```python
BASE_SPACE = {
    "learning_rate": tune.loguniform(1e-5, 1e-4),
    "gamma": tune.choice([0.9, 0.92, 0.95, 0.98, 0.99, 0.995]),
}
```

학습률은 로그균등분포(loguniform)에서, 감마는 0.9~0.995 범위의 6가지 값 중에서 뽑는다.

```python
def tune_params(
        base_params: Hyperparams, train_func: TrainFunc, device: torch.device,
        samples: int = 10, extra_space: tt.Optional[tt.Dict[str, tt.Any]] = None,
):
    search_space = dict(BASE_SPACE)
    if extra_space is not None:
        search_space.update(extra_space)
    config = tune.TuneConfig(num_samples=samples)

    def objective(config: dict, device: torch.device) -> dict:
        keys = dataclasses.asdict(base_params).keys()
        upd = {"tuner_mode": True}
        for k, v in config.items():
            if k in keys:
                upd[k] = v
        params = dataclasses.replace(base_params, **upd)
        res = train_func(params, device, config)
        return {"episodes": res if res is not None else 10**6}
```

`objective` 함수가 샘플링된 딕셔너리로 `Hyperparams` 객체를 만들고, 학습 함수를 부른 뒤, `ray.tune`이 요구하는 형식(딕셔너리)으로 결과를 반환한다. 학습이 잘 수렴하지 않거나 너무 느리게 수렴하는 조합을 만나면 조기 종료해서 시간을 아낀다 — 이때 결과값은 매우 큰 상수(10⁶)가 되어 "나쁜 조합"임을 알려준다.

```python
    obj = tune.with_parameters(objective, device=device)
    if device.type == "cuda":
        obj = tune.with_resources(obj, {"gpu": 1})
    tuner = tune.Tuner(obj, param_space=search_space, tune_config=config)
    results = tuner.fit()
    best = results.get_best_result(metric="episodes", mode="min")
    print(best.config)
    print(best.metrics)
```

GPU가 있으면 자원을 할당해 병렬로 여러 학습을 돌리고, `Tuner` 객체를 만들어 탐색을 수행한다.

하이퍼파라미터 튜닝 모드일 때는 다음 이벤트 핸들러를 추가로 설치한다.

```python
if params.tuner_mode:
    @engine.on(ptan_ignite.EpisodeEvents.EPISODE_COMPLETED)
    def episode_completed(trainer: Engine):
        avg_reward = trainer.state.metrics.get('avg_reward')
        max_episodes = params.episodes_to_solve * 1.1
        if trainer.state.episode > tuner_reward_episode and \
                avg_reward < tuner_reward_min:
            trainer.should_terminate = True
            trainer.state.solved = False
        elif trainer.state.episode > max_episodes:
            trainer.should_terminate = True
            trainer.state.solved = False
```

두 조건을 확인한다.

- 평균 보상이 `tuner_reward_min`(기본값 −19)보다 낮으면(`tuner_reward_episode`, 기본 100게임 지난 뒤) — 수렴 가능성이 거의 없다고 보고 중단.
- `max_episodes`(기본 500게임)를 넘도록 아직 못 풀었으면 — 역시 중단.

두 경우 모두 `solved = False`로 설정해 튜닝 과정에서 큰 상수 값을 반환하게 만든다.

### 1.5 공통 파라미터로 결과 확인

`--params common` 인자로 실행하면 `common.py`의 하이퍼파라미터로 퐁을 학습한다. `--params best`로는 이 확장 기법에 대해 찾은 최적값으로 학습할 수 있다.

```
Chapter08$ ./01_dqn_basic.py --dev cuda --params common
```

매 게임 에피소드가 끝날 때마다 보상, 스텝 수, 속도, 누적 학습 시간을 콘솔에 찍는다. 기본 DQN·공통 하이퍼파라미터로는 보통 **약 70만 프레임, 약 400게임**이 지나야 평균 보상 18에 도달한다.

![[fig_8_1.png]]
*그림 8.1 — 보상(왼쪽)과 에피소드당 스텝 수(오른쪽) 그래프*

![[fig_8_2.png]]
*그림 8.2 — 학습 속도(왼쪽)와 평균 학습 손실(오른쪽) 그래프*

에피소드당 스텝 수가 학습 중 어떻게 변하는지도 눈여겨볼 만하다. 처음엔 신경망이 게임을 점점 더 잘 이기면서 스텝 수가 늘어나다가, 어느 시점을 지나면 2배로 줄어든 뒤 거의 일정해진다. 이건 γ 파라미터가 미래 보상을 할인하기 때문에 벌어지는 일이다 — 에이전트는 그냥 보상을 최대한 많이 쌓으려는 게 아니라, **가능한 한 효율적으로**(=빨리) 쌓으려고 하기 때문이다.

### 1.6 튜닝된 베이스라인 DQN

명령줄 인자 `-tune 30`으로 베이스라인 DQN을 튜닝한 결과(GPU 한 대로 약 하루 소요), 다음 파라미터로 340게임 만에 퐁을 풀 수 있었다(기존 360게임보다 개선).

```
learning_rate=9.932831968547505e-05,
gamma=0.98,
```

학습률은 원래 값(10⁻⁴)과 거의 같지만 γ는 더 작다(0.98 대 0.99). 이는 퐁이 "행동-보상 인과관계"가 상대적으로 짧다는 신호일 수 있다 — γ를 줄이면 학습이 좀 더 안정된다.

![[fig_8_3.png]]
*그림 8.3 — 튜닝 전(Untuned baseline)과 튜닝 후(Tuned baseline)의 보상(왼쪽)과 스텝 수(오른쪽) 비교. 차이는 크지 않다.*

이제 베이스라인 DQN이 준비됐으니, Hessel 등이 제안한 방법들을 하나씩 탐구해 보자.

---

## 2. N-step DQN

첫 번째로 다룰 개선은 꽤 오래된 아이디어다. Sutton이 1988년 논문 *Learning to Predict by the Methods of Temporal Differences*에서 처음 소개했다.

### 2.1 아이디어 — 벨만 방정식 풀어쓰기(unrolling)

Q-러닝에서 쓰는 벨만 업데이트를 다시 보자.

$$Q(s_t, a_t) = r_t + \gamma \max_a Q(s_{t+1}, a_{t+1})$$

이 식은 재귀적이다. 즉 $Q(s_{t+1}, a_{t+1})$을 자기 자신의 형태로 다시 펼칠 수 있다.

$$Q(s_t, a_t) = r_t + \gamma \max_a [r_{t+1} + \gamma \max_{a'} Q(s_{t+2}, a')]$$

여기서 $r_{a,t+1}$은 시각 $t+1$에서 행동 $a$를 취한 뒤 얻는 로컬 보상을 뜻한다. 그런데 만약 시각 $t+1$의 행동이 최적(또는 최적에 가깝게) 선택됐다고 가정하면, 안쪽의 `max` 연산을 생략할 수 있다.

$$Q(s_t, a_t) = r_t + \gamma r_{t+1} + \gamma^2 \max_{a'} Q(s_{t+2}, a')$$

이 값은 얼마든지 더 풀어쓸 수 있다. 이 풀어쓰기 작업을 그대로 DQN 업데이트에 적용해서 **한 스텝 트랜지션 샘플링을 N-스텝 트랜지션 시퀀스로 바꾸면**, 학습 속도를 높일 수 있다.

### 2.2 왜 풀어쓰면 학습이 빨라지는가 — 4상태 예시

이 풀어쓰기가 왜 도움이 되는지 이해하려고, 상태 4개($s_1, s_2, s_3, s_4$)로 된 단순한 환경 예시를 보자. 행동은 하나뿐이고 $s_4$만 종료 상태다.

![[fig_8_4.png]]
*그림 8.4 — 단순한 4상태 환경의 전이 다이어그램*

**한 스텝(one-step)의 경우** — 총 3번의 업데이트가 가능하다(행동이 하나뿐이라 `max`는 안 씀).

1. $Q(s_1, a) \leftarrow r_1 + \gamma Q(s_2, a)$
2. $Q(s_2, a) \leftarrow r_2 + \gamma Q(s_3, a)$
3. $Q(s_3, a) \leftarrow r_3$

학습 초반, 이 세 업데이트를 순서대로 한 번씩 수행한다고 하자. 처음 두 업데이트는 사실 **쓸모가 없다** — 현재 $Q(s_2, a)$와 $Q(s_3, a)$가 아직 임의의 초기값이라 틀렸기 때문이다. 유일하게 의미 있는 업데이트는 3번뿐이다. 종료 상태 직전의 $s_3$에 올바른 보상 $r_3$을 정확히 대입할 수 있으니까.

이 업데이트들을 반복해서 다시 돌리면, 두 번째 반복에서는 $Q(s_2, a)$가 올바르게 세팅된다. 하지만 $Q(s_1, a)$는 여전히 잡음 낀 값이다. **세 번째 반복이 되어서야** 모든 $Q$ 값이 올바르게 채워진다. 즉 한 스텝 방식으로도 값이 전파되는 데는 3번의 반복이 필요하다.

**두 스텝(two-step)의 경우** — 다시 3개의 업데이트다.

1. $Q(s_1, a) \leftarrow r_1 + \gamma r_2 + \gamma^2 Q(s_3, a)$
2. $Q(s_2, a) \leftarrow r_2 + \gamma r_3$
3. $Q(s_3, a) \leftarrow r_3$

이번엔 **첫 번째 루프**에서 $Q(s_2, a)$와 $Q(s_3, a)$ 둘 다 올바른 값을 얻는다. **두 번째 반복**에서 $Q(s_1, a)$도 정확히 갱신된다. 즉 여러 스텝을 쓰면 값이 전파되는 속도가 빨라지고, 수렴이 개선된다.

### 2.3 그렇다면 무조건 스텝을 늘리면 좋을까? — 아니다

> [!warning] "100스텝을 풀어쓰면 100배 빨라지지 않을까?" — 함정
> 직관적으로는 그럴 것 같지만, 실제로는 **DQN이 아예 수렴하지 않을 수도 있다.** 원인을 이해하려면, 풀어쓰기 과정에서 중간 스텝의 `max` 연산을 생략했던 부분을 다시 봐야 한다. 이 생략이 항상 정당한가? 엄격히 말하면 **아니다.**

경험을 모으는 동안 우리 행동 선택(정책)이 항상 최적이었다는 보장이 없다 — 특히 학습 초반, 에이전트가 무작위로 행동할 때는 더더욱. 그런 경우 $Q(s_t, a_t)$의 계산값이 실제 최적값보다 작을 수 있다(일부 스텝이 무작위로 선택됐고, Q값을 최대화하는 경로를 따라가지 않았으므로). **벨만 방정식을 더 많은 스텝으로 풀어쓸수록, 업데이트가 부정확해질 위험도 커진다.**

큰 리플레이 버퍼를 쓰면 이 문제가 더 악화된다. 오래된(나쁜 정책으로 얻은) 데이터를 샘플링할 가능성이 커지기 때문이다. 이는 4장에서 잠깐 언급했던 RL 방법 분류 문제와 연결된다.

> [!important] Off-policy vs On-policy — 근본적 구분
> - **Off-policy 방법**: 학습에 쓰는 데이터가 "신선(fresh)"할 필요가 없다. 기본 DQN이 대표적 예다. 몇 백만 스텝 전에 모은 오래된 데이터도 여전히 유용한데, 우리는 그저 $Q(s_t, a_t)$를 즉시 보상 + 최선 행동의 현재 근사값으로 업데이트할 뿐이라, 그 행동 $a_t$가 무작위로 뽑혔더라도 이 특정 행동에 대한 업데이트는 정확하다. 덕분에 아주 큰 경험 버퍼를 쓸 수 있고, 데이터가 IID(독립항등분포)에 더 가까워진다. ([[IID 독립항등분포]])
> - **On-policy 방법**: 학습 데이터가 반드시 "현재 갱신 중인 정책"에 따라 샘플링되어야 한다. n-step DQN처럼 현재 정책을 간접적으로 개선하거나, 이 책 Part 3에서 다루는 방법들처럼 직접 개선하는 경우가 여기 속한다.

어느 쪽이 더 나은가? 상황에 따라 다르다. Off-policy는 과거의 대량 데이터, 심지어 사람의 시연 데이터로도 학습할 수 있지만 보통 수렴이 느리다. On-policy는 대체로 더 빠르지만, 환경에서 훨씬 더 신선한 데이터를 요구하고, 그 데이터를 얻는 비용이 클 수 있다. 자율주행차를 on-policy로 학습시킨다고 상상해 보라 — 시스템이 벽과 나무를 피해야 한다는 걸 배우기까지 얼마나 많은 차를 박살 낼 것인가!

그렇다면 왜 n-step DQN을 얘기하는가? 이 "n-스텝성"이 방법을 on-policy로 만들어서 대용량 경험 버퍼를 쓸모없게 만드는데도? 실전에서는 흑백논리가 아니다. n-step DQN이 학습 속도를 높여준다면, n을 **너무 크지 않게 신중히 골라서** 여전히 쓸 수 있다. 보통 2나 3 같은 작은 값이 잘 작동하는데, 리플레이 버퍼 속 궤적(trajectory)들이 한 스텝 트랜지션과 그리 다르지 않기 때문이다. 이런 경우 수렴 속도는 대체로 비례해서 좋아지지만, n이 너무 크면 학습 과정이 깨질 수 있다. 그래서 스텝 수는 튜닝 대상이지만, 튜닝할 가치가 있다.

### 2.4 구현

`ExperienceSourceFirstLast` 클래스는 이미 다중 스텝 벨만 풀어쓰기를 지원하므로, DQN을 n-step 버전으로 바꾸는 데는 **딱 두 군데**만 수정하면 된다.

- `ExperienceSourceFirstLast`를 만들 때 `steps_count` 파라미터로 풀어쓸 스텝 수를 넘긴다.
- `calc_loss_dqn` 함수에 올바른 γ를 넘긴다. 이 부분은 놓치기 쉬운데, 벨만 방정식이 이제 n스텝이 되었으므로 마지막 상태에 대한 할인 계수는 단순 γ가 아니라 **γⁿ**이어야 한다.

전체 예시는 `Chapter08/02_dqn_n_steps.py`에 있다. 수정된 부분만 보면:

```python
exp_source = ptan.experience.ExperienceSourceFirstLast(
    env, agent, gamma=params.gamma, env_seed=common.SEED,
    steps_count=n_steps
)
```

`n_steps` 값은 명령줄 인자로 넘긴다. 기본값은 4스텝.

또 다른 수정은 `calc_loss_dqn`에 넘기는 γ다.

```python
loss_v = common.calc_loss_dqn(
    batch, net, tgt_net.target_model,
    gamma=params.gamma**n_steps, device=device)
```

### 2.5 결과

`Chapter08/02_dqn_n_steps.py`는 이전과 똑같이 실행하되, 추가로 `-n` 옵션으로 벨만 방정식을 풀어쓸 스텝 수를 지정한다. n=2, 3일 때 베이스라인과 비교한 그래프는 다음과 같다.

![[fig_8_5.png]]
*그림 8.5 — 기본(1스텝) DQN과 n-step 버전의 보상·스텝 수 비교*

벨만 풀어쓰기가 눈에 띄는 수렴 속도 향상을 가져다준다. 그렇다면 n을 더 키우면 어떨까? n = 3…6 범위에서의 보상 변화를 보자.

![[fig_8_6.png]]
*그림 8.6 — 공통 하이퍼파라미터로 n=3…6일 때의 보상 변화*

3스텝에서 4스텝으로 늘리면 약간의 개선이 있지만 이전만큼 크지 않다. n=5는 오히려 더 나빠지고 n=2와 비슷해진다. n=6도 마찬가지다. 결국 이 경우엔 **n=3이 최적**으로 보인다.

### 2.6 하이퍼파라미터 튜닝

n을 2부터 7까지 각각 개별적으로 튜닝했다. 결과는 다음과 같다.

| n | 학습률 | γ | 게임 수 |
|---|---|---|---|
| 2 | 3.97·10⁻⁵ | 0.98 | 293 |
| 3 | 7.82·10⁻⁵ | 0.98 | 260 |
| 4 | 6.07·10⁻⁵ | 0.98 | 290 |
| 5 | 7.52·10⁻⁵ | 0.99 | 268 |
| 6 | 6.78·10⁻⁵ | 0.995 | 261 |
| 7 | 8.59·10⁻⁵ | 0.98 | 284 |
*표 8.1 — n별로 찾은 최적 하이퍼파라미터(학습률, 감마)*

이 표는 앞선 튜닝 안 된 버전 비교에서 내린 결론을 다시 확인해준다 — 2·3스텝으로 풀어쓰면 수렴이 개선되지만, n을 더 키우면 결과가 나빠진다. n=6은 n=3과 비슷한 결과를 내지만, n=4·n=5는 더 나쁘므로 n=3에서 멈추는 게 낫다.

![[fig_8_7.png]]
*그림 8.7 — 튜닝 후 베이스라인과 n=2, n=3 N-step DQN의 보상·스텝 수 비교*

---

## 3. Double DQN

기본 DQN을 개선할 두 번째 유용한 아이디어는 딥마인드 연구자들의 논문 *Deep Reinforcement Learning with Double Q-Learning*에서 나왔다. 저자들은 기본 DQN이 Q값을 **과대평가(overestimate)**하는 경향이 있고, 이것이 학습 성능을 해치며 때로는 준최적 정책으로 이어질 수 있음을 보였다.

### 3.1 근본 원인과 해결책

근본 원인은 벨만 방정식의 `max` 연산에 있다(엄밀한 증명은 원논문 참고). 기본 DQN에서 Q의 목표값은 이렇게 생겼다.

$$Q(s_t, a_t) = r_t + \gamma \max_a Q'(s_{t+1}, a)$$

여기서 $Q'(s_{t+1}, a)$는 **타깃 네트워크**로 계산한 Q값이다. 저자들은 다음 상태의 행동을 선택할 때는 **학습 중인 네트워크(trained network)**를 쓰되, 그 행동에 대한 값은 여전히 타깃 네트워크에서 가져오자고 제안했다. 새 목표 Q값 식은 다음과 같다.

$$Q(s_t, a_t) = r_t + \gamma \max_a Q'\left(s_{t+1}, \arg\max_a Q(s_{t+1}, a)\right)$$

저자들은 이 단순한 수정만으로 과대평가 문제가 완전히 해결됨을 증명했고, 이 새 아키텍처를 **double DQN**이라 불렀다.

### 3.2 구현

핵심 구현은 매우 단순하다. 손실 함수만 살짝 고치면 된다. 여기서 한 걸음 더 나아가, 기본 DQN과 double DQN이 만들어내는 행동 값을 직접 비교해 보자. 논문 저자들에 따르면 베이스라인 DQN은 double DQN보다 **꾸준히 더 높은 값**을 예측해야 한다. 이를 확인하기 위해, 무작위로 뽑아 고정해 둔 상태 집합에 대해 주기적으로 최선 행동의 평균 값을 계산한다.

전체 예시는 `Chapter08/03_dqn_double.py`에 있다. 먼저 손실 함수:

```python
def calc_loss_double_dqn(
        batch: tt.List[ptan.experience.ExperienceFirstLast],
        net: nn.Module, tgt_net: nn.Module, gamma: float, device: torch.device):
    states, actions, rewards, dones, next_states = common.unpack_batch(batch)

    states_v = torch.as_tensor(states).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.BoolTensor(dones).to(device)
```

이 함수는 `common.calc_loss_dqn` 대신 쓰며 코드 대부분을 공유한다. 핵심 차이는 다음 Q값을 추정하는 부분이다.

```python
    actions_v = actions_v.unsqueeze(-1)
    state_action_vals = net(states_v).gather(1, actions_v)
    state_action_vals = state_action_vals.squeeze(-1)
    with torch.no_grad():
        next_states_v = torch.as_tensor(next_states).to(device)
        next_state_acts = net(next_states_v).max(1)[1]
        next_state_acts = next_state_acts.unsqueeze(-1)
        next_state_vals = tgt_net(next_states_v).gather(1, next_state_acts).squeeze(-1)
        next_state_vals[done_mask] = 0.0
        exp_sa_vals = next_state_vals.detach() * gamma + rewards_v
    return nn.MSELoss()(state_action_vals, exp_sa_vals)
```

double DQN 버전에서는, 다음 상태에서 취할 최선의 행동은 **우리가 학습 중인 메인 네트워크**로 계산하고, 그 행동에 해당하는 값은 **타깃 네트워크**에서 가져온다.

> [!tip] 더 빠르게 짤 수도 있지만
> `next_states_v`와 `states_v`를 합쳐서 메인 네트워크를 딱 한 번만 호출하도록 구현하면 더 빠를 수 있지만, 코드의 명료함이 떨어진다.

나머지 로직은 동일하다 — 완료된 에피소드는 마스킹하고, 신경망이 예측한 Q값과 근사된 Q값 사이의 **평균제곱오차(MSE)**를 계산한다.

held-out(별도로 떼어둔) 상태 집합의 값을 계산하는 함수는 다음과 같다.

```python
@torch.no_grad()
def calc_values_of_states(states: np.ndarray, net: nn.Module, device: torch.device):
    mean_vals = []
    for batch in np.array_split(states, 64):
        states_v = torch.tensor(batch).to(device)
        action_values_v = net(states_v)
        best_action_values_v = action_values_v.max(1)[0]
        mean_vals.append(best_action_values_v.mean().item())
    return np.mean(mean_vals)
```

held-out 상태 배열을 같은 크기의 묶음으로 쪼개어 네트워크에 넣는다. 각 상태마다 값이 가장 큰 행동을 골라 평균을 계산한다. 이 상태 배열은 학습 내내 고정되어 있고 충분히 크므로(코드에서는 1,000개 상태를 저장), 두 DQN 변형에서 이 평균값이 어떻게 움직이는지 비교할 수 있다.

`03_dqn_double.py`의 나머지 부분은 거의 그대로다. 차이는 바뀐 손실 함수를 쓰는 것과, 주기적 평가를 위해 무작위로 뽑은 1,000개 상태를 유지하는 것뿐이다. 이는 `process_batch` 함수에서 일어난다.

```python
if engine.state.iteration % EVAL_EVERY_FRAME == 0:
    eval_states = getattr(engine.state, "eval_states", None)
    if eval_states is None:
        eval_states = buffer.sample(STATES_TO_EVALUATE)
        eval_states = [
            np.asarray(transition.state)
            for transition in eval_states
        ]
        eval_states = np.asarray(eval_states)
        engine.state.eval_states = eval_states
    engine.state.metrics["values"] = \
        common.calc_values_of_states(eval_states, net, device)
```

### 3.3 결과

실험 결과, 공통 하이퍼파라미터로는 double DQN이 보상 동학(dynamics)에 **부정적** 영향을 준다. 초기 동학이 더 좋아져서 더 빨리 이기는 법을 배우기도 하지만, 최종 목표 보상에 도달하는 데는 오히려 더 오래 걸리는 경우가 있다. 다른 게임이나 파라미터로 직접 실험해 볼 수 있다.

double DQN이 베이스라인보다 조금 더 나았던 실험의 보상 차트는 다음과 같다.

![[fig_8_8.png]]
*그림 8.8 — 기본 DQN과 double DQN의 보상 동학 비교*

held-out 상태의 평균 값도 함께 출력된다.

![[fig_8_9.png]]
*그림 8.9 — held-out 상태에 대해 신경망이 예측한 값*

기본 DQN이 값을 과대평가해서 일정 수준을 넘으면 값이 감소하는 반면, double DQN은 더 꾸준히 증가한다. 이번 실험에서는 double DQN이 학습 시간에 미치는 효과가 크지 않았지만, 그렇다고 double DQN이 쓸모없다는 뜻은 아니다 — 퐁은 단순한 환경이라, 더 복잡한 게임에서는 double DQN이 더 나은 결과를 줄 수 있다.

### 3.4 하이퍼파라미터 튜닝

double DQN에 대해서도 하이퍼파라미터 튜닝을 시도했지만 그리 성공적이지 않았다. 30회 시도 후 최선의 학습률·감마 값으로도 퐁을 412게임 만에 풀었는데, 이는 베이스라인보다 더 나쁜 결과다.

---

## 4. Noisy Networks

다음으로 살펴볼 개선안은 RL의 또 다른 근본 문제 — **환경 탐험(exploration)** — 을 다룬다. 여기서 소개할 논문은 *Noisy Networks for Exploration*이며, 학습 도중 탐험 특성을 스스로 익힐 수 있는 아주 단순한 아이디어를 담고 있다.

### 4.1 문제 — 입실론-그리디의 한계

고전적인 DQN은 특별히 정의된 하이퍼파라미터 **ε(입실론)**을 통해 무작위 행동을 선택함으로써 탐험을 달성한다. 학습 초반엔 완전 무작위(1.0)에서 시작해 점차 0.1이나 0.02처럼 작은 비율로 줄여나간다.

이 과정은 짧은 에피소드와 큰 비정상성(non-stationarity)이 없는 단순한 환경에서는 잘 작동하지만, 그런 단순한 환경에서조차 학습 과정을 효율적으로 만들려면 튜닝이 필요하다.

### 4.2 해결책 — 가중치에 노이즈를 더한다

*Noisy Networks* 논문의 저자들은 놀랍도록 단순하면서도 잘 작동하는 해법을 제안했다. 완전 연결(fully connected) 레이어의 **가중치에 노이즈를 더하고**, 이 노이즈의 파라미터를 학습 중 역전파(backpropagation)를 통해 함께 조정하는 것이다.

> [!note] 다른 접근법과의 혼동 주의
> 이 방법을 "네트워크가 스스로 어디를 더 탐험할지 결정한다"는 훨씬 더 복잡한 접근법(내재적 동기 부여, 카운트 기반 탐험 등)과 혼동하면 안 된다. 그 고급 탐험 기법들은 이 책의 21장에서 다룬다.

저자들은 노이즈를 더하는 두 가지 방식을 제안했고, 실험 결과 둘 다 잘 작동하지만 계산 비용이 다르다.

- **독립 가우시안 노이즈(Independent Gaussian noise)**: 완전 연결 레이어의 가중치 하나하나마다, 정규분포에서 뽑은 무작위 값을 갖는다. 이 노이즈의 파라미터 μ(뮤)와 σ(시그마)는 레이어 안에 저장되고, 표준 선형 레이어의 가중치처럼 역전파로 학습된다. 이런 "노이지 레이어"의 출력은 일반 선형 레이어와 같은 방식으로 계산된다.
- **분해된 가우시안 노이즈(Factorized Gaussian noise)**: 샘플링해야 할 무작위 값 개수를 줄이기 위해, 저자들은 두 개의 무작위 벡터만 유지하자고 제안했다 — 하나는 입력 크기만큼, 다른 하나는 출력 크기만큼. 그런 뒤 이 두 벡터의 **외적(outer product)**을 계산해 레이어 전체에 쓸 무작위 행렬을 만든다.

### 4.3 구현

파이토치에서 두 방법 모두 직관적으로 구현할 수 있다. 필요한 건 우리만의 커스텀 `nn.Linear` 레이어를 만들되, 가중치를 $w_{i,j} = \mu_{i,j} + \sigma_{i,j} \cdot \epsilon_{i,j}$로 계산하는 것이다. 여기서 μ와 σ는 학습 가능한 파라미터고, $\epsilon \sim \mathcal{N}(0, 1)$은 매 최적화 스텝마다 정규분포에서 새로 뽑는 무작위 노이즈다.

> [!tip] 직접 구현 대신 라이브러리 사용
> 이전 판에서는 저자가 직접 구현한 코드를 썼지만, 이번 판에서는 7장에서 소개한 TorchRL 라이브러리의 구현을 그대로 쓴다(`torchrl/modules/models/exploration.py`).

`NoisyLinear` 클래스의 생성자는 최적화에 필요한 모든 파라미터를 만든다.

```python
class NoisyLinear(nn.Linear):
    def __init__(
        self, in_features: int, out_features: int, bias: bool = True,
        device: Optional[DEVICE_TYPING] = None, dtype: Optional[torch.dtype] = None,
        std_init: float = 0.1,
    ):
        nn.Module.__init__(self)
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        self.std_init = std_init

        self.weight_mu = nn.Parameter(
            torch.empty(out_features, in_features, device=device, dtype=dtype, requires_grad=True)
        )
        self.weight_sigma = nn.Parameter(
            torch.empty(out_features, in_features, device=device, dtype=dtype, requires_grad=True)
        )
        self.register_buffer(
            "weight_epsilon",
            torch.empty(out_features, in_features, device=device, dtype=dtype),
        )
```

`nn.Linear`를 상속하지만, `nn.Module.__init__()`을 직접 호출해서 일반 `Linear`의 `weight`·`bias` 버퍼는 만들지 않는다. 새로 만든 행렬들을 학습 가능하게 만들려면 `nn.Parameter`로 감싸야 한다. `register_buffer`는 역전파로는 갱신되지 않지만 `nn.Module`이 관리하는(예: `cuda()` 호출 시 GPU로 함께 복사되는) 텐서를 만든다.

```python
        if bias:
            self.bias_mu = nn.Parameter(
                torch.empty(out_features, device=device, dtype=dtype, requires_grad=True)
            )
            self.bias_sigma = nn.Parameter(
                torch.empty(out_features, device=device, dtype=dtype, requires_grad=True)
            )
            self.register_buffer(
                "bias_epsilon", torch.empty(out_features, device=device, dtype=dtype),
            )
        else:
            self.bias_mu = None
        self.reset_parameters()
        self.reset_noise()
```

레이어의 편향(bias)에 대해서도 파라미터와 버퍼를 추가로 만든다. 끝으로 `reset_parameters()`와 `reset_noise()`를 호출해 학습 가능한 파라미터와 입실론 값 버퍼를 초기화한다.

논문에 따라 μ와 σ를 초기화하는 세 메서드는 다음과 같다.

```python
def reset_parameters(self) -> None:
    mu_range = 1 / math.sqrt(self.in_features)
    self.weight_mu.data.uniform_(-mu_range, mu_range)
    self.weight_sigma.data.fill_(self.std_init / math.sqrt(self.in_features))
    if self.bias_mu is not None:
        self.bias_mu.data.uniform_(-mu_range, mu_range)
        self.bias_sigma.data.fill_(self.std_init / math.sqrt(self.out_features))

def reset_noise(self) -> None:
    epsilon_in = self._scale_noise(self.in_features)
    epsilon_out = self._scale_noise(self.out_features)
    self.weight_epsilon.copy_(epsilon_out.outer(epsilon_in))
    if self.bias_mu is not None:
        self.bias_epsilon.copy_(epsilon_out)

def _scale_noise(
        self, size: Union[int, torch.Size, Sequence]) -> torch.Tensor:
    if isinstance(size, int):
        size = (size,)
    x = torch.randn(*size, device=self.weight_mu.device)
    return x.sign().mul_(x.abs().sqrt_())
```

μ 행렬은 균등분포(uniform)의 무작위 값으로 초기화되고, σ의 초기값은 레이어의 뉴런 개수에 따라 정해지는 상수다. 노이즈 초기화는 **분해된 가우시안 노이즈**를 쓴다 — 두 개의 무작위 벡터를 뽑고 외적을 계산해서 ε 행렬을 얻는다. (외적은 크기가 같은 두 벡터를 받아, 각 원소끼리의 모든 조합을 곱한 값으로 채운 정사각 행렬을 만드는 선형대수 연산이다.)

나머지는 단순하다. `nn.Linear` 레이어에서 기대하는 `weight`와 `bias` 프로퍼티를 재정의해서, `NoisyLinear`가 `nn.Linear`가 쓰이는 어디서든 대체될 수 있게 한다.

```python
@property
def weight(self) -> torch.Tensor:
    if self.training:
        return self.weight_mu + self.weight_sigma * self.weight_epsilon
    else:
        return self.weight_mu

@property
def bias(self) -> Optional[torch.Tensor]:
    if self.bias_mu is not None:
        if self.training:
            return self.bias_mu + self.bias_sigma * self.bias_epsilon
        else:
            return self.bias_mu
    else:
        return None
```

> [!warning] 놓치기 쉬운 미묘한 함정
> 이 구현은 단순하지만 아주 미묘한 문제가 하나 있다 — **ε 값이 매 최적화 스텝마다 자동으로 갱신되지 않는다**(문서에도 언급되어 있지 않다). 이 문제는 TorchRL 저장소에 이미 보고되어 있지만, 현재 안정 버전을 쓰려면 `reset_noise()` 메서드를 직접 명시적으로 호출해 줘야 한다. 언젠가 이 문제가 고쳐져서 `NoisyLinear` 레이어가 자동으로 노이즈를 갱신하게 되길 기대한다.

구현 관점에서는 이게 전부다. 이제 고전적인 DQN을 노이지 네트워크 변형으로 바꾸려면 `nn.Linear`(우리 DQN 네트워크의 마지막 두 레이어)를 `NoisyLinear` 레이어로 교체하기만 하면 된다. 물론 입실론-그리디 전략과 관련된 코드는 모두 제거해야 한다.

내부 노이즈 수준을 확인하려면 노이지 레이어의 **신호 대 잡음 비(signal-to-noise ratio, SNR)**를 모니터링할 수 있다. SNR은 $\text{RMS}(\mu)/\text{RMS}(\sigma)$로 정의되며, RMS는 해당 가중치들의 제곱평균제곱근(root mean square)이다. 이 값이 크면 노이지 레이어에서 고정된(안정적인) 성분이 주입된 노이즈보다 크다는 뜻이다.

### 4.4 결과

학습 후 텐서보드 차트를 보면 학습 동학이 훨씬 좋아졌다. 모델이 250게임 만에 평균 점수 18에 도달했는데, 이는 베이스라인 DQN의 350게임보다 개선된 결과다. 다만 노이지 네트워크는 추가 연산이 필요해서 학습이 조금 느리다(초당 194프레임 대 베이스라인 240프레임) — 그래서 시간 기준으로 보면 개선폭이 덜 인상적이다.

![[fig_8_10.png]]
*그림 8.10 — 노이지 네트워크와 베이스라인 DQN 비교*

SNR 차트(그림 8.11)를 확인해 보면, 두 레이어 모두의 노이즈 수준이 아주 빠르게 감소하는 것을 볼 수 있다.

![[fig_8_11.png]]
*그림 8.11 — 1번 레이어(왼쪽)와 2번 레이어(오른쪽)의 SNR 변화*

첫 번째 레이어는 노이즈 비율이 $\frac{1}{2}$에서 거의 $\frac{1}{2.6}$까지 줄어든다. 두 번째 레이어는 더 흥미롭다 — 초반의 $\frac{1}{4}$에서 $\frac{1}{16}$까지 줄어들지만, 약 450K 프레임 지점(원시 보상이 20점 근처로 오른 시점과 얼추 일치)부터는 노이즈 수준이 **다시 증가**하기 시작한다. 이는 상당히 말이 되는 현상이다 — 높은 점수 수준에 도달하고 나면, 에이전트는 이미 좋은 수준으로 플레이하는 법을 알지만 그 결과를 더 "다듬기" 위해 환경을 좀 더 탐험할 필요가 있기 때문이다.

### 4.5 하이퍼파라미터 튜닝

튜닝 후 최선의 파라미터 세트는 게임을 273라운드 만에 풀 수 있었고, 이는 베이스라인 대비 개선이다.

```
learning_rate=7.142520950425814e-05,
gamma=0.99,
```

![[fig_8_12.png]]
*그림 8.12 — 튜닝된 베이스라인 DQN과 튜닝된 노이지 네트워크 비교*

두 차트 모두에서 노이지 네트워크가 가져다준 개선을 볼 수 있다. 점수 21에 도달하는 데 필요한 게임 수가 줄었고, 학습 중 게임당 스텝 수도 더 작다.

---

## 5. 우선순위 리플레이 버퍼 (Prioritized Replay Buffer)

DQN 학습을 개선할 다음의 아주 유용한 아이디어는 2015년 논문 *Prioritized Experience Replay*에서 제안됐다. 이 방법은 학습 손실에 따라 리플레이 버퍼 속 샘플에 우선순위를 매겨서 샘플 효율을 개선하려 한다.

### 5.1 문제 — 균등 샘플링의 낭비

기본 DQN은 리플레이 버퍼를 이용해 에피소드 내 연속된 트랜지션 간의 상관관계를 끊는다. 6장에서 논의했듯, 우리가 경험하는 샘플들은 매우 상관관계가 높다 — 환경이 대개 "매끄럽고(smooth)" 우리 행동에 따라 크게 달라지지 않기 때문이다. 그런데 **확률적 경사하강(SGD)** 방법은 학습에 쓰는 데이터가 IID 속성을 갖는다고 가정한다. 이를 해결하려고 고전적 DQN은 무작위·균등하게 다음 학습 배치를 뽑는 큰 트랜지션 버퍼를 쓴다.

논문 저자들은 이 균등 무작위 샘플링 정책에 의문을 던지고, 버퍼 샘플에 학습 손실에 따라 우선순위를 부여해서 버퍼를 그 우선순위에 비례해 샘플링하면 DQN의 수렴 속도와 정책 품질을 크게 개선할 수 있음을 증명했다. 이 아이디어를 한마디로 요약하면 **"당신을 놀라게 하는 데이터를 더 많이 학습하라"**다. 여기서 까다로운 부분은 "특이한(unusual)" 샘플에 대한 학습과 버퍼의 나머지 부분에 대한 학습 사이의 **균형**을 맞추는 것이다. 만약 버퍼의 작은 일부만 집중해서 학습하면, IID 속성을 잃고 그 부분집합에 과적합될 수 있다.

### 5.2 수학적 정의

버퍼 안 각 샘플의 우선순위는 다음과 같이 계산된다.

$$P(i) = \frac{p_i^\alpha}{\sum_k p_k^\alpha}$$

여기서 $p_i$는 버퍼 속 i번째 샘플의 우선순위이고, α는 우선순위에 얼마나 무게를 둘지 나타내는 숫자다. α=0이면 샘플링은 고전 DQN처럼 균등해진다. α 값이 클수록 우선순위 높은 샘플에 더 강한 스트레스(비중)를 준다. 논문에서 제안한 초기 α값은 0.6이다.

우선순위를 정의하는 데는 여러 방법이 제안됐는데, 가장 인기 있는 방법은 벨만 업데이트에서의 **해당 샘플의 손실에 비례**하게 만드는 것이다. 버퍼에 새로 추가된 샘플에는 곧 샘플링되도록 최댓값의 우선순위를 부여한다.

샘플들의 우선순위를 조정함으로써 데이터 분포에 **편향(bias)**을 도입하는 셈이다(어떤 트랜지션은 다른 것보다 훨씬 자주 샘플링된다). SGD가 제대로 작동하려면 이 편향을 보상해야 한다. 이를 위해 저자들은 각 샘플의 개별 손실에 곱해줄 **샘플 가중치(sample weight)**를 사용했다. 각 샘플의 가중치는 다음과 같이 정의된다.

$$w_i = (N \cdot P(i))^{-\beta}$$

여기서 β는 0과 1 사이여야 하는 또 다른 하이퍼파라미터다. β=1일 때는 샘플링으로 도입된 편향이 완전히 보상되지만, 저자들은 학습 시작 시점엔 β를 0과 1 사이 값으로 두고 학습이 진행되면서 서서히 1로 늘려나가는 편이 수렴에 좋다는 것을 보였다.

### 5.3 구현

이 방법을 구현하려면 코드에 몇 가지 변경이 필요하다.

- 먼저, 우선순위를 추적하고, 우선순위에 따라 배치를 샘플링하고, 가중치를 계산하고, 손실을 알게 된 후 우선순위를 갱신할 수 있는 **새 리플레이 버퍼**가 필요하다.
- 두 번째 변경은 손실 함수 그 자체다. 이제는 모든 샘플에 대한 가중치를 반영해야 할 뿐 아니라, 손실 값을 다시 리플레이 버퍼에 넘겨서 샘플링된 트랜지션의 우선순위를 조정해야 한다.

`05_dqn_prio_replay.py`에 이 모든 변경 사항이 구현돼 있다. 단순함을 위해, 새 우선순위 리플레이 버퍼 클래스는 기존 리플레이 버퍼와 매우 비슷한 저장 방식을 쓴다. 아쉽게도 우선순위 요구사항 때문에 샘플링을 **O(1)** 시간에 구현하는 게 불가능해진다(다시 말해, 버퍼 크기가 커질수록 샘플링 시간도 늘어난다). 매번 새 배치를 뽑을 때마다 모든 우선순위를 훑어야 해서, 샘플링이 버퍼 크기에 비례하는 **O(N)** 시간 복잡도를 갖는다. 10만 개처럼 작은 버퍼라면 큰 문제가 아니지만, 실전에서 수백만 개 트랜지션을 담는 대형 버퍼에서는 문제가 될 수 있다. **세그먼트 트리(segment tree)** 자료구조를 쓰면 O(log N) 시간에 샘플링을 지원하는 저장 방식도 있는데, TorchRL 등 여러 라이브러리에서 이런 최적화된 버퍼를 제공한다.

> [!note] PTAN도 효율적인 구현을 제공
> PTAN 라이브러리는 `ptan.experience.PrioritizedReplayBuffer` 클래스로 더 효율적인 우선순위 리플레이 버퍼를 제공한다. 이 예제를 그 버전으로 바꿔서 학습 성능에 미치는 영향을 직접 확인해 볼 수 있다.

여기서는 우선 `lib/dqn_extra.py`에 있는 **단순(naïve) 버전**을 살펴본다. 먼저 β 증가 속도에 대한 파라미터를 정의한다.

```python
BETA_START = 0.4
BETA_FRAMES = 100_000
```

β는 처음 10만 프레임 동안 0.4에서 1.0으로 서서히 바뀐다.

우선순위 리플레이 버퍼 클래스:

```python
class PrioReplayBuffer(ExperienceReplayBuffer):
    def __init__(self, exp_source: ExperienceSource, buf_size: int,
                 prob_alpha: float = 0.6):
        super().__init__(exp_source, buf_size)
        self.experience_source_iter = iter(exp_source)
        self.capacity = buf_size
        self.pos = 0
        self.buffer = []
        self.prob_alpha = prob_alpha
        self.priorities = np.zeros((buf_size, ), dtype=np.float32)
        self.beta = BETA_START
```

우선순위 리플레이 버퍼 클래스는 PTAN의 단순 리플레이 버퍼를 상속한다. 이 클래스는 샘플을 **순환 버퍼(circular buffer)**에 저장해서, 재할당 없이 고정된 개수의 항목만 유지할 수 있게 해준다. 우리 서브클래스는 우선순위를 담을 넘파이 배열을 추가로 유지한다.

```python
    def update_beta(self, idx: int) -> float:
        v = BETA_START + idx * (1.0 - BETA_START) / BETA_FRAMES
        self.beta = min(1.0, v)
        return self.beta

    def populate(self, count: int):
        max_prio = self.priorities.max(initial=1.0)
        for _ in range(count):
            sample = next(self.experience_source_iter)
            if len(self.buffer) < self.capacity:
                self.buffer.append(sample)
            else:
                self.buffer[self.pos] = sample
            self.priorities[self.pos] = max_prio
            self.pos = (self.pos + 1) % self.capacity
```

`update_beta()` 메서드는 스케줄에 따라 β를 늘리기 위해 주기적으로 호출되어야 한다. `populate()` 메서드는 `ExperienceSource` 객체에서 정해진 개수만큼 트랜지션을 뽑아 버퍼에 저장한다. 트랜지션 저장을 순환 버퍼로 구현했으므로 두 가지 상황을 나눠 처리한다 — 버퍼가 아직 최대 용량에 못 미쳤으면 새 트랜지션을 그냥 뒤에 붙이고, 버퍼가 이미 가득 찼으면 `pos` 필드가 가리키는 가장 오래된 트랜지션을 덮어쓰고 그 위치를 버퍼 크기로 나눈 나머지로 조정한다.

`sample` 메서드에서는 α 하이퍼파라미터를 이용해 우선순위를 확률로 변환한다.

```python
    def sample(self, batch_size: int) -> tt.Tuple[
        tt.List[ExperienceFirstLast], np.ndarray, np.ndarray
    ]:
        if len(self.buffer) == self.capacity:
            prios = self.priorities
        else:
            prios = self.priorities[:self.pos]
        probs = prios ** self.prob_alpha
        probs /= probs.sum()
```

그 확률을 이용해 버퍼를 샘플링해서 배치를 얻는다.

```python
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[idx] for idx in indices]
```

마지막 단계로 배치 속 샘플들의 가중치를 계산한다.

```python
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-self.beta)
        weights /= weights.max()
        return samples, indices, np.array(weights, dtype=np.float32)
```

이 함수는 배치·인덱스·가중치, 세 가지를 반환한다. 샘플링된 항목의 우선순위를 갱신하려면 배치 샘플들의 인덱스가 필요하다.

우선순위 리플레이 버퍼의 마지막 함수는 처리된 배치의 새 우선순위를 갱신하는 역할을 한다.

```python
    def update_priorities(self, batch_indices: np.ndarray, batch_priorities: np.ndarray):
        for idx, prio in zip(batch_indices, batch_priorities):
            self.priorities[idx] = prio
```

계산된 배치 손실 값과 함께 이 함수를 호출하는 것은 호출자의 책임이다.

다음으로 손실 계산 함수다. 파이토치의 `MSELoss` 클래스는 (분류 손실에서 흔히 쓰는) 가중치를 지원하지 않으므로(당연히 그렇다, MSE는 회귀 문제에서 쓰이는 손실이니까), MSE를 직접 계산하고 그 결과에 명시적으로 가중치를 곱해야 한다.

```python
def calc_loss(batch: tt.List[ExperienceFirstLast], batch_weights: np.ndarray,
              net: nn.Module, tgt_net: nn.Module, gamma: float,
              device: torch.device) -> tt.Tuple[torch.Tensor, np.ndarray]:
    states, actions, rewards, dones, next_states = common.unpack_batch(batch)

    states_v = torch.as_tensor(states).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.BoolTensor(dones).to(device)
    batch_weights_v = torch.tensor(batch_weights).to(device)

    actions_v = actions_v.unsqueeze(-1)
    state_action_vals = net(states_v).gather(1, actions_v)
```

```python
    state_action_vals = state_action_vals.squeeze(-1)
    with torch.no_grad():
        next_states_v = torch.as_tensor(next_states).to(device)
        next_s_vals = tgt_net(next_states_v).max(1)[0]
        next_s_vals[done_mask] = 0.0
        exp_sa_vals = next_s_vals.detach() * gamma + rewards_v
    l = (state_action_vals - exp_sa_vals) ** 2
    losses_v = batch_weights_v * l
    return losses_v.mean(), (losses_v + 1e-5).data.cpu().numpy()
```

손실 계산의 마지막 부분에서, 라이브러리를 쓰지 않고 같은 MSE 손실을 직접 식으로 풀어써서, 각 샘플의 가중치를 반영하고 샘플별 개별 손실 값을 유지한다. 이 값들이 나중에 우선순위 리플레이 버퍼에 전달되어 우선순위를 갱신한다. 모든 손실에 작은 값을 더하는 이유는, 손실이 정확히 0이 되면 그 버퍼 항목의 우선순위도 0이 되어 다시는 뽑히지 않는 상황을 막기 위해서다.

메인 프로그램에서는 리플레이 버퍼 생성과 배치 처리 함수, 딱 두 부분만 바뀐다. 버퍼 생성은 단순하니 새 처리 함수만 살펴보자.

```python
def process_batch(engine, batch_data):
    batch, batch_indices, batch_weights = batch_data
    optimizer.zero_grad()
    loss_v, sample_prios = calc_loss(
        batch, batch_weights, net, tgt_net.target_model,
        gamma=params.gamma, device=device)
    loss_v.backward()
    optimizer.step()
    buffer.update_priorities(batch_indices, sample_prios)
    epsilon_tracker.frame(engine.state.iteration)
    if engine.state.iteration % params.target_net_sync == 0:
        tgt_net.sync()
    return {
        "loss": loss_v.item(),
        "epsilon": selector.epsilon,
        "beta": buffer.update_beta(engine.state.iteration),
    }
```

변경 사항은 다음과 같다.

- 배치가 이제 세 가지 요소를 담는다 — 데이터 배치, 샘플링된 항목의 인덱스, 샘플들의 가중치.
- 새 손실 함수를 호출한다. 이 함수는 가중치를 받아 추가로 각 샘플의 우선순위를 반환한다. 이 우선순위 값들을 `buffer.update_priorities()` 함수에 넘겨서 방금 뽑은 항목들의 우선순위를 재조정한다.
- 스케줄에 따라 β 파라미터를 바꾸기 위해 버퍼의 `update_beta()` 메서드를 호출한다.

### 5.4 결과

이 예제는 평소처럼 학습시킬 수 있다. 저자의 실험에 따르면, 우선순위 리플레이 버퍼는 거의 같은 절대 시간(약 한 시간)이 걸려 환경을 풀었다. 그러나 학습 이터레이션과 에피소드 수는 더 적게 걸렸다. 즉 벽시계 시간 기준으로는 거의 비슷한 이유가, 덜 효율적인 리플레이 버퍼 때문이다 — 물론 이는 O(log N) 구현으로 제대로 풀 수 있는 문제다.

베이스라인과 우선순위 리플레이 버퍼의 보상 동학 비교(x축은 게임 에피소드)는 다음과 같다.

![[fig_8_13.png]]
*그림 8.13 — 우선순위 리플레이 버퍼와 기본 DQN의 보상 동학 비교*

텐서보드 차트에서 눈에 띄는 또 다른 차이는 우선순위 리플레이 버퍼의 **손실이 훨씬 낮다**는 점이다.

![[fig_8_14.png]]
*그림 8.14 — 학습 중 손실 비교*

낮은 손실 값은 기대했던 대로이며, 구현이 제대로 작동한다는 좋은 신호다. 우선순위화의 아이디어는 손실 값이 높은 샘플에 더 집중해서 학습을 더 효율적으로 만드는 것이다. 하지만 여기엔 위험도 있다 — 학습 중 손실 값 자체가 최적화의 최종 목표는 아니다. 손실이 매우 낮더라도 탐험 부족으로 인해 학습된 정책이 최적과는 거리가 멀 수도 있다.

### 5.5 하이퍼파라미터 튜닝

우선순위 리플레이 버퍼의 하이퍼파라미터 튜닝은 α에 대한 추가 파라미터를 함께 진행했으며, 0.3부터 0.9까지 0.1 간격의 고정된 값 목록에서 뽑았다. 최선의 조합은 330 에피소드 만에 퐁을 풀었고, α=0.6(논문과 동일)이었다.

```
learning_rate=8.839010139505506e-05,
gamma=0.99,
```

![[fig_8_15.png]]
*그림 8.15 — 튜닝된 베이스라인 DQN과 튜닝된 우선순위 리플레이 비교*

여기서는 우선순위 리플레이 버퍼가 게임플레이 개선이 더 빨랐지만, 점수 21에 도달하는 데는 비슷한 게임 수가 걸렸다. 오른쪽 차트(게임 스텝 수 기준)를 보면 우선순위 리플레이 버퍼가 살짝 더 나았다.

---

## 6. Dueling DQN

이 개선은 2015년 논문 *Dueling Network Architectures for Deep Reinforcement Learning*에서 제안됐다. 이 논문의 핵심 통찰은, 우리 네트워크가 근사하려는 Q값 $Q(s,a)$를, 상태의 가치 $V(s)$와 그 상태에서 행동들의 이점(advantage) $A(s,a)$ 두 가지로 나눌 수 있다는 것이다.

### 6.1 아이디어 — 상태의 가치와 행동의 이점 분리

$V(s)$라는 개념은 5장의 가치반복(value iteration) 방법에서 이미 봤다. 이는 해당 상태로부터 얻을 수 있는 할인된 기대 보상과 같다. 이점 $A(s,a)$는 $V(s)$와 $Q(s,a)$ 사이의 간극을 메우는 값으로 정의된다 — 정의상 $Q(s,a) = V(s) + A(s,a)$이기 때문이다. 다시 말해, 이점 $A(s,a)$는 상태에서 특정 행동을 선택했을 때 **추가로** 얻는 보상이 얼마인지를 말해준다. 이점은 양수일 수도 음수일 수도 있으며, 일반적으로 어떤 크기든 될 수 있다. 예를 들어, 어떤 결정적인 순간에는 한 행동을 다른 행동 대신 고르는 선택이 전체 보상에 큰 손실을 가져올 수도 있다.

*Dueling* 논문의 기여는 네트워크 아키텍처에서 가치와 이점을 **명시적으로 분리**한 것으로, 학습 안정성 향상, 더 빠른 수렴, 그리고 아타리(Atari) 벤치마크에서 더 좋은 결과를 가져왔다. 고전 DQN 네트워크와의 구조적 차이는 다음 그림과 같다. 고전적인 DQN 네트워크(위)는 컨볼루션 레이어에서 나온 특징(feature)을 받아 완전 연결 레이어들로 변환해서, 각 행동에 대한 Q값 벡터를 만든다.

![[fig_8_16.png]]
*그림 8.16 — 기본 DQN(위)과 dueling 아키텍처(아래)*

반면 dueling DQN(아래)은 컨볼루션 특징을 받아서 **두 개의 독립된 경로**로 처리한다. 한 경로는 $V(s)$ 예측을 담당하며, 이는 그냥 숫자 하나다. 다른 경로는 개별 이점 값들을 예측하는데, 고전적인 경우의 Q값과 같은 차원을 갖는다. 그런 뒤 $V(s)$를 모든 $A(s,a)$ 값에 더해서 $Q(s,a)$를 얻고, 이 값을 평소와 같이 사용하고 학습시킨다.

### 6.2 제약 조건이 필요한 이유

이런 아키텍처 변화만으로는 네트워크가 우리가 원하는 대로 $V(s)$와 $A(s,a)$를 학습한다는 보장이 없다. 예를 들어 네트워크가 어떤 상태에 대해 $V(s) = 0$, $A(s) = [1,2,3,4]$를 예측했다고 하자. 이는 완전히 잘못된 예측이다 — 예측된 $V(s)$가 그 상태의 기대값이 아니기 때문이다. 우리는 **어떤 상태에서든 이점의 평균값이 0**이어야 한다는 또 하나의 제약을 걸어야 한다. 그 경우, 앞선 예시의 올바른 예측은 $V(s) = 2.5$, $A(s) = [-1.5, -0.5, 0.5, 1.5]$가 되어야 한다.

이 제약을 강제하는 방법은 여러 가지가 있다 — 예컨대 손실 함수를 통해서도 가능하지만, *Dueling* 논문에서 저자들은 아주 우아한 해법을 제안했다. 네트워크의 Q값 표현식에서 **이점의 평균값을 빼는 것**이다. 이렇게 하면 사실상 이점의 평균이 0으로 밀리는 효과가 있다.

$$Q(s,a) = V(s) + A(s,a) - \frac{1}{N}\sum_k A(s,k)$$

이렇게 하면 고전적인 DQN을 dueling DQN으로 바꾸는 데 필요한 변경이 매우 단순해진다 — 다른 구현 요소는 건드리지 않고 **네트워크 아키텍처만** 바꾸면 된다.

### 6.3 구현

전체 예시는 `Chapter08/06_dqn_dueling.py`에 있다. 모든 변경 사항이 네트워크 아키텍처에 있으므로, 여기서는 네트워크 클래스(`lib/dqn_extra.py` 모듈)만 보여준다. 컨볼루션 부분은 기존과 완전히 동일하다.

```python
class DuelingDQN(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int):
        super(DuelingDQN, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten()
        )
```

단일 경로의 완전 연결 레이어를 정의하는 대신, 이점 경로와 가치 예측 경로, **두 개의 서로 다른 변환**을 만든다.

```python
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.fc_adv = nn.Sequential(
            nn.Linear(size, 256),
            nn.ReLU(),
            nn.Linear(256, n_actions)
        )
        self.fc_val = nn.Sequential(
            nn.Linear(size, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
```

모델의 파라미터 개수를 원래 네트워크와 비슷하게 유지하려고, 두 경로 모두 내부 차원을 512에서 256으로 줄였다.

`forward()` 함수의 변경도 파이토치의 표현력 덕분에 아주 단순하다.

```python
    def forward(self, x: torch.ByteTensor):
        adv, val = self.adv_val(x)
        return val + (adv - adv.mean(dim=1, keepdim=True))

    def adv_val(self, x: torch.ByteTensor):
        xx = x / 255.0
        conv_out = self.conv(xx)
        return self.fc_adv(conv_out), self.fc_val(conv_out)
```

여기서 배치 속 샘플들에 대해 가치와 이점을 계산하고 그 둘을 더하되, 이점의 평균을 빼서 최종 Q값을 얻는다. 미묘하지만 중요한 부분은, 텐서의 **두 번째 차원**을 따라 평균을 계산한다는 것이다. 이렇게 해야 배치 속 각 샘플마다 이점의 평균 벡터가 만들어진다.

### 6.4 결과

dueling DQN을 학습시킨 뒤, 우리 퐁 벤치마크에서 고전적인 DQN 수렴과 비교할 수 있다. dueling 아키텍처가 기본 DQN 버전보다 **더 빠르게 수렴**한다.

![[fig_8_17.png]]
*그림 8.17 — dueling DQN의 보상 동학과 베이스라인 버전 비교*

우리 예제는 고정된 상태 집합에 대한 이점과 가치도 함께 출력한다.

![[fig_8_18.png]]
*그림 8.18 — 고정된 상태 집합에 대한 평균 이점(왼쪽)과 평균 가치(오른쪽)*

기대했던 대로다 — 이점은 0에서 크게 벗어나지 않지만, 가치는 시간이 지날수록 개선된다(그리고 Double DQN 절에서 봤던 값과 비슷한 형태를 보인다).

### 6.5 하이퍼파라미터 튜닝

하이퍼파라미터 튜닝은 그리 성과가 없었다. 30회 튜닝 반복 후에도, 공통 파라미터 세트보다 더 빠르게 수렴하는 학습률·감마 조합을 찾지 못했다.

---

## 7. Categorical DQN — 분포적 강화학습

우리 DQN 개선 도구상자에서 마지막이자 가장 복잡한 방법은 2017년 6월 딥마인드가 발표한 논문 *A Distributional Perspective on Reinforcement Learning*에서 나왔다. 몇 년이 지났지만 이 논문은 여전히 매우 유의미하며, 이 분야에서 연구가 활발히 이어지고 있다. 2023년에는 같은 저자들이 이 방법을 더 깊이 다루는 책 *Distributional Reinforcement Learning*을 출간하기도 했다.

### 7.1 아이디어 — 숫자 하나가 아니라 분포로

논문에서 저자들은 Q-러닝의 근본적인 구성요소인 **Q값 그 자체**에 의문을 제기하고, 그것을 더 일반적인 **Q값 확률분포**로 대체하려 했다. Q-러닝과 가치반복 방법 모두 행동이나 상태의 값을 단순한 숫자 하나로 다루고, 그 값이 그 상태(또는 상태-행동)로부터 얻을 수 있는 전체 보상을 얼마나 나타내는지를 보여준다. 하지만 미래의 모든 가능한 보상을 숫자 하나에 우겨넣는 게 정말 실용적일까? 복잡한 환경에서는 미래가 확률적(stochastic)이어서, 서로 다른 확률로 서로 다른 값들을 우리에게 안겨줄 수 있다.

### 7.2 비유 — 자동차 vs 기차 통근

예를 들어, 매일 규칙적으로 집에서 회사까지 차로 출퇴근하는 상황을 상상해 보자. 대부분의 경우 교통이 그렇게 막히지 않아서 목적지까지 약 30분이 걸린다.

정확히 30분은 아니지만, 평균적으로는 30분이다. 가끔은 도로 공사나 사고 때문에 교통 정체로 세 배나 더 오래 걸리기도 한다. 통근 시간의 확률을 "통근 시간"이라는 확률 변수의 분포로 나타낼 수 있고, 이는 다음 차트로 표현된다.

![[fig_8_19.png]]
*그림 8.19 — 자동차 통근 시간의 확률분포*

정확히 30분은 아니지만 평균은 30분이다. 가끔 도로 공사나 사고로 인한 정체가 생겨 세 배나 더 걸릴 때도 있다.

이제 대안 통근 수단인 기차가 있다고 상상해 보자. 집에서 역까지, 역에서 회사까지 이동해야 해서 조금 더 오래 걸리지만, 훨씬 신뢰도가 높다(적어도 몇몇 나라 — 독일은 아닐지 몰라도 스위스 기차라면). 예컨대 기차 통근 시간이 평균 40분이고, 20분이 더 걸리는 기차 지연이 발생할 작은 확률이 있다고 하자. 기차 통근 시간의 분포는 다음과 같다.

![[fig_8_20.png]]
*그림 8.20 — 기차 통근 시간의 확률분포*

이제 어떻게 통근할지 결정한다고 하자. 두 수단의 **평균 시간**만 안다면, 자동차가 더 매력적으로 보인다 — 평균적으로 자동차가 35.43분, 기차가 40.54분이 걸리니 자동차가 더 낫다.

하지만 **전체 분포**를 본다면 기차를 선택하게 될 수도 있다. 최악의 경우 시나리오라 하더라도 자동차의 최악의 경우(1시간 30분)보다 기차의 최악의 경우(1시간)가 더 낫기 때문이다. 통계적으로 말하면, 자동차 분포는 **분산(variance)**이 훨씬 크므로, 60분 안에 반드시 도착해야 하는 상황이라면 기차가 더 낫다.

이 상황은 **마르코프 결정 과정(MDP)** 시나리오에서 훨씬 더 복잡해진다. 결정을 여러 번 연속으로 내려야 하고, 각 결정이 미래 상황에 영향을 미치기 때문이다. 통근 예시로 치면, 언제 도착할지에 따라 중요한 회의 시간을 잡아야 하는 상황이 될 수 있다. 그런 경우 평균 보상 값만 다루면 근본적인 환경 동학에 대한 많은 정보를 잃게 될 수 있다.

정확히 이런 생각을 *Distributional Perspective on Reinforcement Learning* 논문의 저자들이 제안했다. 왜 굳이 행동의 값을 평균 하나로 예측하려고 스스로를 제한하는가, 그 실제 값의 밑에는 복잡한 분포가 깔려 있을 수 있는데? 어쩌면 그 분포 자체를 직접 다루는 게 도움이 될지도 모른다.

### 7.3 분포적 벨만 방정식

논문에서 제시한 결과는, 실제로 이 아이디어가 도움이 될 수 있지만, 그 대가로 더 복잡한 방법을 도입해야 한다는 것이다. 여기서 엄밀한 수학적 정의를 다루진 않지만, 전체적인 아이디어는 매 행동에 대한 값의 분포를 예측하는 것이며, 이는 우리 자동차/기차 예시의 분포들과 비슷하다. 다음 단계로, 저자들은 벨만 방정식이 분포 케이스로 일반화될 수 있음을 보였다. 그 형태는 다음과 같다.

$$Z(x,a) \overset{D}{=} R(x,a) + \gamma Z(x',a')$$

이는 익숙한 벨만 방정식과 매우 비슷하지만, 이제 $Z(x,a)$와 $R(x,a)$는 단일 숫자가 아니라 **확률분포**다. 표기 $A \overset{D}{=} B$는 분포 A와 B가 동일함을 나타낸다.

이렇게 나온 분포는, Q-러닝과 정확히 같은 방식으로 우리 네트워크가 각 행동에 대한 값 분포를 더 잘 예측하도록 학습시키는 데 쓸 수 있다. 유일한 차이는 손실 함수에 있는데, 이제는 **분포 비교**에 적합한 무언가로 바꿔야 한다. 여기엔 몇 가지 대안이 있다. 예컨대 분류 문제에서 쓰이는 **쿨백-라이블러(Kullback-Leibler, KL) 발산**(교차 엔트로피 손실이라고도 함, [[교차 엔트로피 Cross-Entropy]] 참고)이나 **바서슈타인 거리(Wasserstein metric)**가 있다. 논문에서는 바서슈타인 거리를 쓸 이론적 근거를 제시했지만, 실제로 시도해 보니 한계가 있어서 결국 논문에서는 KL 발산을 사용했다.

### 7.4 구현

앞서 언급했듯 이 방법은 상당히 복잡해서, 저자도 구현하고 제대로 동작하는지 확인하는 데 시간이 꽤 걸렸다고 밝혔다. 전체 코드는 `Chapter08/07_dqn_distrib.py`에 있고, `lib/dqn_extra.py`의 `distr_projection` 함수를 이용해 분포 투영(distribution projection)을 수행한다. 코드를 보기 전에, 구현 로직에 대해 몇 마디 설명이 필요하다.

이 방법의 핵심은 우리가 근사하려는 확률분포 그 자체다. 이를 표현하는 방법은 여러 가지가 있는데, 논문 저자들은 상당히 일반적인 파라메트릭 분포를 골랐다 — 값의 범위 위에 일정한 간격으로 놓인 고정 개수의 값들이다. 이 값들의 범위는 얻을 수 있는 누적 할인 보상의 범위를 커버해야 한다. 논문에서는 원자(atom)의 개수를 다양하게 실험했는데, 최고의 결과는 값 범위를 51개 구간(`N_ATOMS=51`)으로 나누고 $V_{min}=-10$부터 $V_{max}=10$까지의 범위를 썼을 때 나왔다.

각 원자(모두 51개)마다, 우리 네트워크는 미래의 할인된 값이 그 원자의 구간에 들어갈 확률을 예측한다. 이 방법의 핵심 부분은 다음 상태의 최선 행동에 대한 분포를 감마로 **수축(contraction)**하고, 로컬 보상을 분포에 더하고, 결과를 원래 원자들로 다시 투영하는 코드다. 이 로직은 `dqn_extra.distr_projection` 함수에 구현돼 있다. 함수 시작 부분에서 투영 결과를 담을 배열을 할당한다.

```python
def distr_projection(next_distr: np.ndarray, rewards: np.ndarray,
                      dones: np.ndarray, gamma: float):
    batch_size = len(rewards)
    proj_distr = np.zeros((batch_size, N_ATOMS), dtype=np.float32)
    delta_z = (Vmax - Vmin) / (N_ATOMS - 1)
```

이 함수는 형태가 `(batch_size, N_ATOMS)`인 분포들의 배치, 보상 배열, 완료된 에피소드를 나타내는 플래그, 그리고 우리 하이퍼파라미터인 `Vmin`, `Vmax`, `N_ATOMS`, `gamma`를 인자로 받는다. `delta_z` 변수는 우리 값 범위에서 원자 하나가 차지하는 너비다.

다음 코드에서는 원래 분포의 원자를 하나씩 순회하면서, 벨만 연산자를 적용해 그 원자가 투영될 위치를 계산한다. 우리 값 범위(`Vmin`, `Vmax`)를 고려하면서 말이다.

```python
    for atom in range(N_ATOMS):
        v = rewards + (Vmin + atom * delta_z) * gamma
        tz_j = np.minimum(Vmax, np.maximum(Vmin, v))
```

예를 들어, 인덱스 0인 첫 번째 원자는 값 $V_{min} = -10$에 해당하는데, 보상 +1을 받는 샘플이라면 값 $-10 \cdot 0.99 + 1 = -8.9$로 투영된다. 즉 오른쪽으로 밀린다(γ=0.99를 가정). 만약 값이 $V_{min}$과 $V_{max}$로 정해진 범위를 벗어나면, 그 경계값으로 잘라낸다(clip).

다음 줄에서는 우리 샘플들이 투영된 원자 번호를 계산한다.

```python
        b_j = (tz_j - Vmin) / delta_z
```

당연히 샘플들이 원자와 원자 사이로 투영될 수도 있다. 그런 상황에서는 원래 분포의 값을 그 값이 떨어지는 두 원자 사이에 나눠 퍼뜨려야 한다. 이 퍼뜨림은 조심스럽게 처리해야 하며, 우리 목표 원자가 정확히 어떤 원자의 위치에 정확히 떨어지는 경우도 있을 수 있다. 그런 경우엔 그냥 소스 분포 값을 목표 원자에 더해주면 된다.

다음 코드는 투영된 원자가 목표 원자에 정확히 떨어지는 상황을 처리한다. 그렇지 않은 경우에는, `b_j`가 정수값이 아니게 되고, 변수 `l`과 `u`(투영된 지점 아래·위 원자의 인덱스에 해당)를 쓴다.

```python
        l = np.floor(b_j).astype(np.int64)
        u = np.ceil(b_j).astype(np.int64)
        eq_mask = u == l
        proj_distr[eq_mask, l[eq_mask]] += next_distr[eq_mask, atom]
```

투영된 지점이 원자와 원자 사이에 떨어지면, 그 원자 아래와 위로 소스 원자의 확률을 나눠 퍼뜨려야 한다. 다음 두 줄이 이를 수행한다.

```python
        ne_mask = u != l
        proj_distr[ne_mask, l[ne_mask]] += next_distr[ne_mask, atom] * (u - b_j)[ne_mask]
        proj_distr[ne_mask, u[ne_mask]] += next_distr[ne_mask, atom] * (b_j - l)[ne_mask]
```

물론 에피소드의 마지막 트랜지션도 제대로 처리해야 한다. 이런 경우엔 투영이 다음 분포를 고려하지 않아야 하고, 그저 받은 보상에 해당하는 확률 1을 가져야 한다. 이번에도 원자들을 고려해서, 만약 보상 값이 원자와 원자 사이에 떨어지면 이 확률을 적절히 나눠 퍼뜨려야 한다. 이 경우는 아래 코드 블록에서 처리한다. 완료 플래그가 설정된 샘플들에 대해서는 결과 분포를 0으로 초기화한 뒤 투영을 계산한다.

```python
    if dones.any():
        proj_distr[dones] = 0.0
        tz_j = np.minimum(Vmax, np.maximum(Vmin, rewards[dones]))
        b_j = (tz_j - Vmin) / delta_z
        l = np.floor(b_j).astype(np.int64)
        u = np.ceil(b_j).astype(np.int64)
        eq_mask = u == l
        eq_dones = dones.copy()
        eq_dones[dones] = eq_mask
        if eq_dones.any():
            proj_distr[eq_dones, l[eq_mask]] = 1.0
        ne_mask = u != l
        ne_dones = dones.copy()
        ne_dones[dones] = ne_mask
        if ne_dones.any():
            proj_distr[ne_dones, l[ne_mask]] = (u - b_j)[ne_mask]
            proj_distr[ne_dones, u[ne_mask]] = (b_j - l)[ne_mask]
    return proj_distr
```

이 함수가 실제로 무엇을 하는지 감을 잡으려면, 함수에 인위적으로 만든 분포를 넣어서 살펴본 결과(그림 8.21)를 보면 도움이 된다. 저자는 이 그림들을 함수를 디버깅하고 의도대로 작동하는지 확인하는 데 썼다. 이 확인용 코드는 `Chapter08/adhoc/distr_test.py`에 있다.

![[fig_8_21.png]]
*그림 8.21 — 정규분포에 확률분포 변환을 적용한 예시*

그림 8.21의 위쪽 차트(Source)는 μ=0, σ=3인 정규분포다. 아래쪽 차트(Projected)는 γ=0.9, `reward=2`로 분포 투영을 적용한 결과이며, 오른쪽으로 이동했다.

같은 데이터에 `done=True`를 함께 넘기면 결과가 달라지는데, 이는 그림 8.22에서 보여준다. 이런 경우 소스 분포는 완전히 무시되고, 결과는 오직 투영된 보상만을 갖는다.

![[fig_8_22.png]]
*그림 8.22 — 에피소드 마지막 스텝에 대한 분포 투영*

이 메서드의 구현은 `Chapter08/07_dqn_distrib.py`에 있으며, 선택적인 명령줄 파라미터 `-img-path`를 받는다. 이 옵션을 주면, 학습 중 고정된 상태 집합에 대한 확률분포를 그린 플롯이 지정한 디렉터리에 저장된다. 이는 모델이 학습 초반의 균등 확률에서 시작해 점점 더 뾰족한(spiked) 확률 질량 분포로 수렴해 가는 과정을 관찰하는 데 유용하다. 저자의 실험에서 뽑은 예시 이미지는 그림 8.24, 8.25에서 볼 수 있다.

여기서는 구현의 핵심 부분만 다룬다. `distr_projection` 함수는 이미 다뤘고, 가장 복잡한 부분이다. 아직 안 본 것은 네트워크 아키텍처와 수정된 손실 함수다.

네트워크는 `lib/dqn_extra.py`의 `DistributionalDQN` 클래스에 있다.

```python
Vmax = 10
Vmin = -10
N_ATOMS = 51
DELTA_Z = (Vmax - Vmin) / (N_ATOMS - 1)

class DistributionalDQN(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int):
        super(DistributionalDQN, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten()
        )
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.fc = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, n_actions * N_ATOMS)
        )
```

핵심 차이는 완전 연결 레이어의 출력이다. 이제 `n_actions * N_ATOMS`개의 값을 출력하는데, 퐁의 경우 $6 \times 51 = 306$이다. 각 행동마다, 51개 원자에 대한 확률분포를 예측해야 한다.

```python
        sups = torch.arange(Vmin, Vmax + DELTA_Z, DELTA_Z)
        self.register_buffer("supports", sups)
        self.softmax = nn.Softmax(dim=1)
```

이 원자들의 보상값은 -10부터 10까지 균등하게 분포하며, 간격은 0.4다. 이 값들(support)은 네트워크의 버퍼에 저장된다.

`forward()` 메서드는 예측된 확률분포를 3D 텐서(배치, 행동, support)로 반환한다.

```python
    def forward(self, x: torch.ByteTensor) -> torch.Tensor:
        batch_size = x.size()[0]
        xx = x / 255
        fc_out = self.fc(self.conv(xx))
        return fc_out.view(batch_size, -1, N_ATOMS)

    def both(self, x: torch.ByteTensor) -> tt.Tuple[torch.Tensor, torch.Tensor]:
        cat_out = self(x)
        probs = self.apply_softmax(cat_out)
        weights = probs * self.supports
        res = weights.sum(dim=2)
        return cat_out, res
```

`forward()` 외에도, 원자들에 대한 확률분포와 Q값을 한 번의 호출로 계산해 주는 `both()` 메서드를 정의한다.

네트워크는 Q값 계산과 확률분포에 소프트맥스를 적용하는 계산을 간단히 해주는 헬퍼 함수도 몇 개 더 정의한다.

```python
    def qvals(self, x: torch.ByteTensor) -> torch.Tensor:
        return self.both(x)[1]

    def apply_softmax(self, t: torch.Tensor) -> torch.Tensor:
        return self.softmax(t.view(-1, N_ATOMS)).view(t.size())
```

마지막 변경은 새 손실 함수인데, 이제는 벨만 방정식 대신 분포 투영을 적용하고, 예측된 분포와 투영된 분포 사이의 **KL 발산**을 계산해야 한다.

```python
def calc_loss(batch: tt.List[ExperienceFirstLast], net: dqn_extra.DistributionalDQN,
              tgt_net: dqn_extra.DistributionalDQN, gamma: float,
              device: torch.device) -> torch.Tensor:
    states, actions, rewards, dones, next_states = common.unpack_batch(batch)
    batch_size = len(batch)

    states_v = torch.as_tensor(states).to(device)
    actions_v = torch.tensor(actions).to(device)
```

```python
    next_states_v = torch.as_tensor(next_states).to(device)

    # next state distribution
    next_distr_v, next_qvals_v = tgt_net.both(next_states_v)
    next_acts = next_qvals_v.max(1)[1].data.cpu().numpy()
    next_distr = tgt_net.apply_softmax(next_distr_v)
    next_distr = next_distr.data.cpu().numpy()

    next_best_distr = next_distr[range(batch_size), next_acts]
    proj_distr = dqn_extra.distr_projection(next_best_distr, rewards, dones, gamma)

    distr_v = net(states_v)
    sa_vals = distr_v[range(batch_size), actions_v.data]
    state_log_sm_v = F.log_softmax(sa_vals, dim=1)
    proj_distr_v = torch.tensor(proj_distr).to(device)

    loss_v = -state_log_sm_v * proj_distr_v
    return loss_v.sum(dim=1).mean()
```

앞의 코드는 그리 복잡하지 않다. `distr_projection`을 호출할 준비를 하고, KL 발산을 계산할 뿐이다. KL 발산의 정의는 다음과 같다.

$$D_{KL}(P \| Q) = -\sum_i p_i \log q_i$$

확률의 로그를 계산할 때는, `log`와 `softmax`를 수치적으로 안정적인 방식으로 합쳐 계산해 주는 파이토치의 `log_softmax` 함수를 쓴다.

### 7.5 결과

저자의 실험에 따르면, 분포적 DQN은 원래 DQN보다 조금 더 느리고 덜 안정적으로 수렴했는데, 이는 놀라운 일이 아니다 — 네트워크 출력이 이제 51배 커졌고 손실 함수도 바뀌었기 때문이다. 하이퍼파라미터 튜닝 없이는, 분포적 버전이 게임을 풀기까지 20% 더 많은 에피소드를 필요로 한다.

또 한 가지 중요할 수 있는 요인은, 퐁이 결론을 도출하기엔 너무 단순한 게임이라는 점이다. *A Distributional Perspective* 논문에서 저자들은 (2017년 발표 당시 기준) 아타리 벤치마크 게임 절반 이상에서 최고 기록(state-of-the-art)을 달성했다고 보고했지만, 그 목록에 퐁은 없었다.

베이스라인 DQN과 비교한 보상 동학과 손실 차트는 다음과 같다. 보시다시피, 분포적 방법의 보상 동학은 베이스라인 DQN보다 나쁘다.

![[fig_8_23.png]]
*그림 8.23 — 보상 동학(왼쪽)과 손실 감소(오른쪽)*

학습 중 확률분포가 어떻게 변해가는지 살펴보는 것도 흥미로울 수 있다. `-img-path` 파라미터로 학습을 시작하면, 고정된 상태 집합에 대한 확률분포 플롯이 저장된다. 예를 들어, 다음 그림은 학습 시작 시점(3만 프레임 뒤)에서 하나의 상태에 대한 6가지 행동 모두의 확률분포를 보여준다.

![[fig_8_24.png]]
*그림 8.24 — 학습 시작 시점의 확률분포*

모든 분포가 매우 넓게 퍼져 있다(네트워크가 아직 수렴하지 않았으므로). 가운데 있는 봉우리는 네트워크가 자신의 행동으로부터 얻으리라 기대하는 음의 보상에 해당한다. 같은 상태를 학습 50만 프레임 뒤에 보면 다음 그림과 같다.

![[fig_8_25.png]]
*그림 8.25 — 학습된 네트워크가 만들어낸 확률분포*

이제 서로 다른 행동들이 서로 다른 분포를 갖는 것을 볼 수 있다. 첫 번째 행동(NOOP, 아무것도 하지 않는 행동)은 분포가 왼쪽으로 치우쳐 있다. 즉 이 상태에서 아무것도 안 하면 보통 지는 결과로 이어진다는 뜻이다. 다섯 번째 행동인 RIGHTFIRE는 평균값이 오른쪽으로 치우쳐 있으며, 이 행동이 더 나은 점수로 이어진다는 뜻이다.

### 7.6 하이퍼파라미터 튜닝

하이퍼파라미터 튜닝도 그리 성과가 없었다. 30회 튜닝 시도 후에도, 공통 파라미터 세트보다 더 빠르게 수렴하는 학습률·감마 조합을 찾지 못했다.

---

## 8. 모든 걸 합치기 — Rainbow

지금까지 논문 *Rainbow: Combining Improvements in Deep Reinforcement Learning*에서 언급된 모든 DQN 개선 기법을 살펴봤다. 하지만 하나씩 따로따로 봤는데, 이는 각 개선의 아이디어와 구현을 이해하는 데는 도움이 됐을 것이다(그러길 바란다). 그 논문의 진짜 핵심은 이 개선들을 **결합**해서 결과를 확인하는 데 있었다.

### 8.1 어떤 기법을 결합할까

이 최종 예시에서는, 우리의 "실험용 쥐" 환경(퐁)에서 큰 개선을 보여주지 못했던 **Categorical DQN**과 **Double DQN**은 최종 시스템에서 제외하기로 했다. 다른 게임에 적용하고 싶다면 얼마든지 다시 추가해서 시도해 볼 수 있다. 전체 예시는 `Chapter08/08_dqn_rainbow.py`에 있다.

먼저 네트워크 아키텍처와, 그 아키텍처에 기여하는 방법들을 정의해야 한다.

- **Dueling DQN**: 우리 네트워크는 상태 가치 분포와 이점 분포를 위해 두 개의 독립된 경로를 갖는다. 출력에서는 두 경로를 더해서 최종 행동 가치 확률분포를 만든다. 이점 분포가 평균 0을 갖도록 강제하려고, 매 원자마다 이점의 평균값을 빼준다.
- **Noisy networks**: 가치·이점 경로의 선형 레이어들을 `nn.Linear`의 노이지 변형으로 쓴다.

네트워크 아키텍처 변경 외에도, 환경 트랜지션을 유지하고 MSE 손실에 비례해서 샘플링하기 위해 **우선순위 리플레이 버퍼**를 사용한다.

마지막으로, 벨만 방정식을 **n스텝**으로 풀어쓴다.

개별 기법들의 코드는 이미 앞선 절들에서 모두 다뤘으므로, 여기서 모든 코드를 다시 반복하진 않는다 — 이 방법들을 결합한 최종 결과가 어떻게 생겼을지는 이미 충분히 짐작할 수 있을 것이다. 문제가 생기면 GitHub에서 전체 코드를 찾을 수 있다.

### 8.2 결과

다음은 베이스라인 DQN과 스무딩된 보상·스텝 수를 비교한 차트다. 두 지표 모두에서, 필요한 게임 판수 측면에서 눈에 띄는 개선을 볼 수 있다.

![[fig_8_26.png]]
*그림 8.26 — 베이스라인 DQN과 결합 시스템(Combined) 비교*

스무딩된 보상 외에, 원시 보상(raw reward) 차트를 확인하는 것도 의미가 있다 — 스무딩된 보상보다 훨씬 극적인 모습을 보여준다. 우리 시스템이 부정적인 결과에서 긍정적인 결과로 아주 빠르게 뛰어오른 것을 볼 수 있다 — 100게임 만에 거의 모든 게임을 이겼다. 스무딩된 보상이 +18에 도달하는 데는 그로부터 100게임이 더 걸렸다.

![[fig_8_27.png]]
*그림 8.27 — 결합 시스템의 원시 보상*

단점도 있다 — 결합된 시스템은 더 복잡한 신경망 아키텍처와 우선순위 리플레이 버퍼 때문에 베이스라인보다 **더 느리다.** FPS 차트를 보면, 결합 시스템은 170 FPS로 시작해서 버퍼의 O(n) 복잡도 때문에 130 FPS까지 떨어진다.

![[fig_8_28.png]]
*그림 8.28 — 성능 비교(초당 프레임 수)*

### 8.3 하이퍼파라미터 튜닝

튜닝은 이전과 같은 방식으로 진행했으며, 게임을 풀 때까지 필요한 게임 판수 측면에서 결합 시스템의 학습을 더 개선할 수 있었다. 다음은 튜닝된 베이스라인 DQN과 튜닝된 결합 시스템을 비교한 차트다.

![[fig_8_29.png]]
*그림 8.29 — 튜닝된 베이스라인 DQN과 튜닝된 결합 시스템 비교*

튜닝의 효과를 보여주는 또 다른 차트는, 튜닝 전후의 원시 게임 보상을 비교한 것이다. 튜닝된 시스템은 최고 점수에 훨씬 더 빨리 도달한다 — 겨우 40게임 만에 도달하는데, 이는 상당히 인상적인 결과다.

![[fig_8_30.png]]
*그림 8.30 — 튜닝 전(Untuned)과 튜닝 후(Tuned) 결합 DQN의 원시 보상*

---

## 9. 요약

이 챕터에서 우리는:

1. **N-step DQN**으로 벨만 방정식을 여러 스텝 풀어써서 수렴을 빠르게 하는 법과, 스텝을 너무 늘리면 off-policy 안정성이 깨지는 이유를 배웠다.
2. **Double DQN**으로 `max` 연산이 만드는 값 과대평가 문제와, 행동 선택과 값 평가를 분리해서 이를 고치는 법을 배웠다.
3. **Noisy Networks**로 입실론-그리디를 대체해, 네트워크 가중치 자체에 학습 가능한 노이즈를 심어 탐험을 자동화하는 법을 배웠다.
4. **우선순위 리플레이 버퍼**로 "놀라운" 샘플을 더 자주 학습해 샘플 효율을 높이는 법과, 그로 인한 편향을 가중치로 보정하는 법을 배웠다.
5. **Dueling DQN**으로 Q값을 상태 가치와 행동 이점으로 나누는 아키텍처, 그리고 이점의 평균을 0으로 강제하는 트릭을 배웠다.
6. **Categorical(분포적) DQN**으로 기대값 하나 대신 값 분포 전체를 예측하고, 벨만 방정식을 분포에 대해 적용하는 법(분포 투영, KL 발산)을 배웠다.
7. 이 모든 기법을 결합한 **Rainbow**가 개별 기법 어느 것보다도 훨씬 빠르고 극적으로 수렴한다는 것을 확인했다.

각 기법은 기본 DQN이 가진 서로 다른 약점(느린 값 전파, 값 과대평가, 비효율적 탐험, 균등 샘플링의 낭비, Q값의 단순한 구조, 기댓값으로의 뭉갬)을 겨냥한다. 다음 챕터에서는 방법 자체를 건드리지 않고도 DQN 성능을 개선하는 엔지니어링 관점의 실전 기법들을 계속 다룬다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[N-step DQN과 벨만 방정식 풀어쓰기]]
- [[오프폴리시와 온폴리시]]
- [[Double DQN]]
- [[노이지 네트워크]]
- [[우선순위 경험 리플레이]]
- [[듀얼링 DQN Dueling Architecture]]
- [[분포적 강화학습과 Categorical DQN]]
- [[Rainbow DQN]]
- [[교차 엔트로피 Cross-Entropy]]
- [[IID 독립항등분포]]

## 한눈에 보는 개념 지도
| 개념 | 기호/핵심 | 한 줄 뜻 |
|---|---|---|
| N-step 리턴 | $r_t + \gamma r_{t+1} + \cdots + \gamma^{n}\max_a Q$ | 벨만 방정식을 n스텝 풀어써 값 전파를 빠르게 함 |
| Off-policy | 오래된 데이터 재사용 가능 | 학습 데이터가 현재 정책과 달라도 됨(기본 DQN) |
| On-policy | 신선한 데이터 필요 | 학습 데이터가 현재 정책에서 나와야 함(n-step 등) |
| Double DQN | $Q'(s',\arg\max_a Q(s',a))$ | 행동 선택은 메인망, 값 평가는 타깃망으로 분리해 과대평가 완화 |
| Noisy Networks | $w = \mu + \sigma\cdot\epsilon$ | 가중치에 학습되는 노이즈를 더해 탐험을 자동화 |
| 우선순위 리플레이 | $P(i) = p_i^\alpha / \sum_k p_k^\alpha$ | 손실이 큰(놀라운) 샘플을 더 자주 학습 |
| 샘플 가중치 | $w_i = (N\cdot P(i))^{-\beta}$ | 우선순위 샘플링이 만든 편향을 보정 |
| Dueling DQN | $Q=V(s)+A(s,a)-\frac{1}{N}\sum_k A(s,k)$ | Q값을 상태 가치와 행동 이점으로 분리 |
| 분포적 벨만 방정식 | $Z(x,a)\overset{D}{=}R(x,a)+\gamma Z(x',a')$ | 기대값 대신 값의 확률분포 자체를 다룸 |
| KL 발산 | $D_{KL}(P\|Q)=-\sum_i p_i\log q_i$ | 분포적 DQN의 손실 함수(두 분포의 차이) |
| Rainbow | 6가지 기법 결합 | N-step + Double + Noisy + Prio Replay + Dueling + Categorical |
