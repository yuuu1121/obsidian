---
title: "개념정리 — 결정론적 정책 경사 (DDPG)"
tags: [개념정리, DeepRL, 연속행동, DDPG, 액터크리틱]
related: [[Chapter 15 - 연속 행동 공간]]
---

# 결정론적 정책 경사 (Deep Deterministic Policy Gradient, DDPG)

> [!abstract] 한 줄 요약
> DDPG는 [[액터-크리틱과 어드밴티지]]의 아이디어를 그대로 쓰되, **정책을 [[결정론적 정책 Deterministic Policy]]로 바꿔서** 크리틱의 Q값을 직접 미분해 정책을 개선하는 방법이다. 그 덕분에 DQN처럼 **오프-폴리시(off-policy)** 학습이 가능해져, 리플레이 버퍼를 마음껏 쓸 수 있다.

## 1. A2C와 무엇이 다른가

[[Chapter 15 - 연속 행동 공간]]에서 본 A2C는 정책이 **확률적**이었다 — 가우시안 분포의 평균·분산을 출력하고, 실제 행동은 거기서 샘플링했다. DDPG도 액터-크리틱 계열이지만, 정책이 **결정론적**이라는 점이 다르다.

- **액터** $\mu(s)$: 상태를 넣으면 행동 값을 그대로 반환한다(확률 분포가 아니라 숫자 벡터).
- **크리틱** $Q(s, a)$: 상태와 행동을 함께 입력받아, 그 조합의 Q값(할인된 미래 보상의 기대치) 하나를 출력한다.

DQN 시절 크리틱은 "상태 하나 → 모든 행동의 Q값"을 한 번에 출력했다(효율을 위해). 하지만 연속 행동은 개수를 셀 수 없으므로 그 방식이 불가능하다. 그래서 DDPG의 크리틱은 **상태와 행동을 둘 다 입력으로 받아 Q값 하나만** 낸다.

## 2. 핵심 아이디어 — 정책을 Q값으로 직접 미분

액터와 크리틱을 합치면 $Q(s, \mu(s))$라는 하나의 식이 된다. 신경망은 결국 함수이므로, 액터의 출력을 크리틱에 그대로 흘려 넣은 것이다.

우리가 원하는 것은 "액터의 가중치 $\theta_\mu$를 어느 방향으로 바꾸면 Q값(=총 보상 기대치)이 커지는가"이다. Silver 등의 **결정론적 정책 경사 정리(deterministic policy gradient theorem)**에 따르면, 확률적 정책 경사와 동치인 다음 식으로 이를 계산할 수 있다.

$$\nabla_a Q(s,\mu(s)) \cdot \nabla_{\theta_\mu}\mu(s)$$

말로 풀면: *"행동을 살짝 바꿨을 때 Q값이 얼마나 변하는지(첫 번째 항)"* 와 *"액터의 가중치를 살짝 바꿨을 때 행동이 얼마나 변하는지(두 번째 항)"* 를 체인 룰로 곱한 것 — 즉 **가중치를 바꿔서 결국 Q값을 최대화하는 방향**을 알려준다.

> [!note] 실전 구현은 훨씬 간단하다
> 수식은 복잡해 보이지만, PyTorch의 자동미분([[자동미분과 계산그래프]])이 체인 룰을 알아서 해주므로, 실제 코드는 "크리틱 출력을 음수로 뒤집어서 loss로 쓰고 `backward()`" 하면 끝이다(아래 4절 참고).

## 3. A2C의 크리틱과 DDPG의 크리틱 — 역할 차이

둘 다 "크리틱"이라 부르지만 쓰임이 다르다.

| | A2C의 크리틱 | DDPG의 크리틱 |
|---|---|---|
| 입력 | 상태만 | 상태 + 행동 |
| 역할 | 베이스라인(기준값) 제공, 없어도 학습은 됨([[REINFORCE 알고리즘]])—안정성 향상용 | 정책을 개선하는 **그래디언트의 원천**. 없으면 학습 자체가 안 됨 |
| 미분 경로 | 정책의 샘플링 단계 때문에 로그 확률로 우회 | 액터 → 크리틱까지 **끊김 없이 완전히 미분 가능** |

## 4. 구조 (Figure 15.5)

![[fig_15_5.png]]
*그림 15.5 — DDPG의 액터(왼쪽)와 크리틱(오른쪽) 신경망 구조*

**액터**(`DDPGActor`): 3개의 선형(Linear)층 + ReLU, 마지막에 Tanh로 출력을 −1~1 범위로 눌러준다.

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
- `obs_size` → 400 → 300 → `act_size` 순으로 차원이 줄어드는 전형적인 피드포워드망.
- 마지막 `Tanh()`가 핵심이다. 행동 범위가 −1…1이어야 하므로(PyBullet 환경 규칙), 값을 그 범위로 강제로 눌러준다.

**크리틱**(`DDPGCritic`): 상태와 행동을 **각자 다른 경로**로 받다가 중간에 하나로 합친다.

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
- `obs_net`: 상태만 먼저 400차원으로 변환.
- `forward`: 변환된 상태(`obs`)와 행동(`a`)을 `torch.cat`으로 이어붙인 뒤(`400 + act_size`차원), 다시 300차원을 거쳐 **Q값 스칼라 하나**를 낸다.
- 왜 상태를 먼저 따로 처리할까? 상태만으로도 어느 정도 특징을 뽑아둔 다음 행동 정보를 "나중에" 섞는 구조가, 처음부터 다 이어붙이는 것보다 학습이 잘 되는 경우가 많기 때문이다(원 논문의 설계).

## 5. 탐험 — 스테이트풀 에이전트와 OU 노이즈

DDPG의 정책은 결정론적이라 스스로 탐험하지 못한다. 그래서 [[오른슈타인-울렌벡 노이즈 OU Process]]를 행동에 더한다. 이를 위해 PTAN 에이전트가 **상태(agent_states)를 기억하는** 방식으로 구현된다.

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
- 생성자는 OU 프로세스의 하이퍼파라미터(원 논문 기본값)를 그대로 받는다.
- `initial_state()`는 `BaseAgent`가 요구하는 메서드로, **에피소드 시작 시 에이전트의 내부 상태**를 정해준다. 아직 노이즈 값이 없으므로 `None`을 돌려주고, 실제 초기화는 미룬다.

```python
def __call__(self, states: ptan.agent.States, agent_states: ptan.agent.AgentStates):
    states_v = ptan.agent.float32_preprocessor(states)
    states_v = states_v.to(self.device)
    mu_v = self.net(states_v)
    actions = mu_v.data.cpu().numpy()

    if self.ou_enabled and self.ou_epsilon > 0:
        new_a_states = []
        for a_state, action in zip(agent_states, actions):
            if a_state is None:
                a_state = np.zeros(shape=action.shape, dtype=np.float32)
            a_state += self.ou_teta * (self.ou_mu - a_state)
            a_state += self.ou_sigma * np.random.normal(size=action.shape)

            action += self.ou_epsilon * a_state
            new_a_states.append(a_state)
    else:
        new_a_states = agent_states
    actions = np.clip(actions, -1, 1)
    return actions, new_a_states
```
- 먼저 액터 `self.net`으로 결정론적 행동 `actions`를 구한다.
- `agent_states`(각 환경의 이전 OU 노이즈 값들)를 하나씩 순회하며, 처음이면(`a_state is None`) 0으로 초기화하고, [[오른슈타인-울렌벡 노이즈 OU Process]]의 두 줄짜리 갱신식을 적용한다.
- 만든 노이즈를 행동에 더한 뒤, `np.clip(actions, -1, 1)`으로 환경이 요구하는 범위 안으로 강제로 자른다(벗어나면 PyBullet이 예외를 던진다).

## 6. 학습 — 오프-폴리시 + 리플레이 버퍼 + 타깃 네트워크

정책이 결정론적이라는 성질 덕분에, DDPG는 **DQN과 똑같이 오프-폴리시**로 학습할 수 있다. 즉 과거에 모아둔 경험(리플레이 버퍼)을 재사용해도 문제가 없다. 이는 매번 새로 모은 데이터만 써야 하는 A2C류(온-폴리시)에 비해 큰 이점이다([[오프폴리시와 온폴리시]] 참고).

**크리틱 학습** — [[벨만 방정식 Bellman Equation]]으로 목표 Q값을 만들고, [[타깃 네트워크와 부트스트래핑]]으로 안정화한다.

```python
crt_opt.zero_grad()
q_v = crt_net(states_v, actions_v)
last_act_v = tgt_act_net.target_model(last_states_v)
q_last_v = tgt_crt_net.target_model(last_states_v, last_act_v)
q_last_v[dones_mask] = 0.0
q_ref_v = rewards_v.unsqueeze(dim=-1) + q_last_v * GAMMA

critic_loss_v = F.mse_loss(q_v, q_ref_v.detach())
critic_loss_v.backward()
crt_opt.step()
```
- `tgt_act_net`(타깃 액터)으로 "다음 상태에서 어떤 행동을 했을지"를 구하고, `tgt_crt_net`(타깃 크리틱)으로 그 Q값을 구한다 — 학습 중인 네트워크가 아니라 **일부러 뒤처진(target) 네트워크**를 써서 목표값이 너무 빨리 출렁이지 않게 한다.
- 에피소드가 끝난 전이는 `q_last_v[dones_mask] = 0.0`으로 미래 보상을 0 처리한다(더 이상 다음 상태가 없으므로).
- 실제 크리틱 출력 `q_v`와 목표값 `q_ref_v` 사이의 **평균제곱오차(MSE)**를 최소화 — DQN 학습과 본질적으로 같다.

**액터 학습** — 크리틱이 매긴 점수를 최대화하는 방향으로 액터를 바로 업데이트한다.

```python
act_opt.zero_grad()
cur_actions_v = act_net(states_v)
actor_loss_v = -crt_net(states_v, cur_actions_v)
actor_loss_v = actor_loss_v.mean()
actor_loss_v.backward()
act_opt.step()
```
- 액터가 낸 행동 `cur_actions_v`를 크리틱에 넣어 Q값을 얻는다.
- Q값을 **최대화**하고 싶은데, 옵티마이저는 항상 손실(loss)을 **최소화**하도록 만들어졌다. 그래서 `-crt_net(...)`처럼 **부호를 뒤집어서** "손실을 최소화 = Q값을 최대화"가 되도록 만든다.
- `act_opt.step()`만 호출해 **액터의 가중치만** 갱신한다. 크리틱을 통해 그래디언트가 흘러가긴 하지만, 크리틱 자신의 옵티마이저(`crt_opt`)는 이 스텝에서 건드리지 않으므로 크리틱 가중치는 바뀌지 않는다.

## 7. 소프트 타깃 업데이트

DQN에서는 타깃 네트워크를 몇 스텝마다 한꺼번에 통째로 복사했다. 연속 행동 문제에서는 이 방식이 잘 안 통해서, 대신 **매 스텝마다 아주 조금씩** 옮기는 "소프트 동기화(soft sync)"를 쓴다.

```python
tgt_act_net.alpha_sync(alpha=1 - 1e-3)
tgt_crt_net.alpha_sync(alpha=1 - 1e-3)
```
- 매 스텝, 타깃 네트워크 가중치의 99.9%는 그대로 유지하고 0.1%만 최신 네트워크 쪽으로 끌어온다.
- 그 결과 타깃값이 **부드럽고 느리게** 갱신되어, 학습이 훨씬 안정적이다.

## 8. 결과

책의 실험에서 A2C는 900만 프레임·16시간 학습 후 최고 보상 0.35에 그쳤지만, DDPG는 **500만 관측치·약 20시간 학습 후 평균 보상 4.5**를 달성해 확실히 더 나은 성능을 보였다.

## 세 줄 정리
- DDPG = [[결정론적 정책 Deterministic Policy]] + 크리틱 Q값을 직접 미분해 정책 개선.
- 오프-폴리시라서 리플레이 버퍼·타깃 네트워크(소프트 동기화)를 DQN처럼 활용할 수 있다.
- 탐험은 [[오른슈타인-울렌벡 노이즈 OU Process]]로 행동에 노이즈를 더해 해결한다.
