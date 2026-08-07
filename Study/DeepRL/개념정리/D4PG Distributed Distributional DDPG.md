---
title: "개념정리 — D4PG (Distributed Distributional DDPG)"
tags: [개념정리, DeepRL, 연속행동, DDPG, 분포적강화학습]
related: [[Chapter 15 - 연속 행동 공간]]
---

# D4PG (Distributed Distributional Deep Deterministic Policy Gradients)

> [!abstract] 한 줄 요약
> D4PG는 [[결정론적 정책 경사 DDPG]]에 [[분포적 강화학습과 Categorical DQN]]의 아이디어(Q값을 숫자 하나 대신 **확률 분포**로 예측)를 접목하고, 몇 가지 개선을 더해 **DDPG보다 훨씬 안정적이고 빠르게 수렴**하도록 만든 방법이다.

## 1. DDPG에서 무엇을 바꿨나 — 세 가지 개선

논문 *Distributed distributional deterministic policy gradients*(Barth-Maron et al., 2018)는 DDPG를 아래 세 방향으로 개선했다.

1. **크리틱의 출력을 분포로 바꿈**: 단일 Q값 대신, [[분포적 강화학습과 Categorical DQN]](Bellemare et al., 2017)에서 쓴 것과 같은 방식으로 **"보상이 어느 구간에 속할 확률"의 분포**를 예측한다.
2. **N-스텝 벨만 방정식**: 한 스텝이 아니라 여러 스텝을 미리 내다보고 부트스트래핑([[N-step DQN과 벨만 방정식 풀어쓰기]] 참고)해서 수렴을 앞당긴다.
3. **우선순위 경험 리플레이**: 균등하게 샘플링하는 대신, [[우선순위 경험 리플레이]]([[Rainbow DQN]]에서 쓴 기법)를 가져와 중요한 경험을 더 자주 재사용한다.

책 구현에서는 1번과 2번만 적용하고(간단한 리플레이 버퍼 사용), 그래도 DDPG보다 확실히 좋은 결과를 보였다.

## 2. 탐험 방식 차이

DDPG는 [[오른슈타인-울렌벡 노이즈 OU Process]]를 썼지만, D4PG 저자들은 "OU를 쓰든 단순 가우시안 노이즈를 쓰든 결과가 비슷했다"고 보고했다. 그래서 D4PG는 더 **간단한 가우시안 노이즈**를 쓴다.

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
- 액터(`DDPGActor`, DDPG와 완전히 같은 구조)로 결정론적 행동을 구한 뒤, `epsilon` 배율의 정규분포 난수를 그냥 더한다.
- OU처럼 이전 스텝의 노이즈를 기억할 필요가 없으므로 `agent_states`는 그대로 돌려주기만 한다 — **스테이트리스(상태 없는)** 에이전트라 코드가 훨씬 간단하다.

## 3. 크리틱 구조 — Q값 하나 대신 분포

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

    def forward(self, x: torch.Tensor, a: torch.Tensor):
        obs = self.obs_net(x)
        return self.out_net(torch.cat([obs, a], dim=1))

    def distr_to_q(self, distr: torch.Tensor):
        weights = F.softmax(distr, dim=1) * self.supports
        res = weights.sum(dim=1)
        return res.unsqueeze(dim=-1)
```
- 전체 골격은 `DDPGCritic`과 거의 같다. 다만 마지막 층이 **숫자 하나가 아니라 `n_atoms`개**(책에서는 51개)를 출력한다. 이 51개 값은 각각 "보상이 특정 구간(bin)에 속할 확률"을 나타낸다.
- `v_min=-10`, `v_max=10`: 예상되는 보상값의 범위를 미리 정해두고, 그 사이를 51개 구간으로 잘게 쪼갠다. `delta`는 구간 하나의 폭이다.
- `register_buffer("supports", ...)`: 각 구간을 대표하는 값들(−10, −9.6, −9.2, …, 10)을 미리 계산해 저장해 둔다. 학습 대상은 아니지만 모델과 함께 저장·이동(GPU 등)되어야 하므로 버퍼로 등록한다.
- `distr_to_q()`: 51개 확률 분포를 다시 **하나의 평균 Q값**으로 되돌리는 함수. `softmax`로 확률로 만든 뒤, 각 구간 대표값(`supports`)과 곱해서 더하면 **기댓값(평균)**이 된다 — 이것이 [[기댓값 Expectation]]의 정의 그대로다.

> [!note] 왜 softmax를 forward에 넣지 않았을까
> 학습 때는 더 수치적으로 안정적인 `log_softmax()`를 쓸 것이기 때문에, `forward()`는 정규화 전의 원값(logit)만 반환하고, 실제 확률이 필요한 곳(`distr_to_q`)에서만 `softmax`를 적용한다.

## 4. 학습 — 분포 간의 교차 엔트로피

크리틱이 이제 분포를 출력하므로, 손실 함수도 [[손실함수의 종류]] 중 [[교차 엔트로피 Cross-Entropy]]로 바뀐다. DDPG처럼 MSE로 숫자 하나를 맞추는 게 아니라, "예측한 확률 분포"와 "정답 확률 분포"를 **최대한 비슷하게** 만드는 것이 목표다.

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
- 지금 크리틱이 예측한 분포 `crt_distr_v`를 먼저 구한다.
- 타깃 액터·타깃 크리틱으로 "다음 상태에서의 분포"(`last_distr_v`)를 구한다. DDPG와 마찬가지로 타깃 네트워크를 써서 안정성을 확보한다.

```python
proj_distr = distr_projection(
    last_distr_v.detach().cpu().numpy(),
    rewards_v.detach().cpu().numpy(),
    dones_mask.detach().cpu().numpy(), gamma=GAMMA**REWARD_STEPS)
proj_distr_v = torch.tensor(proj_distr).to(device)
```
- `distr_projection`: [[분포적 강화학습과 Categorical DQN]](Chapter 8)에서 쓴 것과 똑같은 **벨만 투영(projection)** 함수다. "다음 상태 분포"를 즉시 보상만큼 옮기고 할인율만큼 오므린 뒤, 다시 정해진 51개 구간(atom)에 맞춰 재분배한다. 이렇게 만든 것이 크리틱이 배워야 할 **목표 분포**다.
- `gamma=GAMMA**REWARD_STEPS`: N-스텝 벨만 방정식을 쓰므로, 할인율도 스텝 수만큼 거듭제곱된다.

```python
prob_dist_v = -F.log_softmax(crt_distr_v, dim=1) * proj_distr_v
critic_loss_v = prob_dist_v.sum(dim=1).mean()
critic_loss_v.backward()
crt_opt.step()
```
- PyTorch에는 "두 확률 분포 사이의" 일반적인 교차 엔트로피 함수가 없어서, 정의대로 직접 계산한다: $-\sum (\text{목표 확률}) \times \log(\text{예측 확률})$.
- `log_softmax`가 예측 확률의 로그, `proj_distr_v`가 목표 확률이다. 구간별로 곱해서 더하면(`sum(dim=1)`) 샘플 하나의 교차 엔트로피 손실이 되고, 배치 평균(`mean()`)을 최종 손실로 쓴다.

**액터 학습**은 DDPG와 거의 같다. 다만 분포를 다시 하나의 Q값으로 바꿔야 하므로 `distr_to_q()`를 거친다.

```python
act_opt.zero_grad()
cur_actions_v = act_net(states_v)
crt_distr_v = crt_net(states_v, cur_actions_v)
actor_loss_v = -crt_net.distr_to_q(crt_distr_v)
actor_loss_v = actor_loss_v.mean()
actor_loss_v.backward()
act_opt.step()
```

## 5. 결과 — 셋 중 최고

책의 세 방법(A2C, DDPG, D4PG) 비교 실험에서, D4PG가 **수렴 속도와 최종 보상 모두 압도적으로 우세**했다. 약 350만 관측치(20시간) 만에 테스트 평균 보상 17.912를 달성했는데, 이는 환경이 "풀렸다"고 인정하는 기준점 15.0을 넘는 수치다.

![[fig_15_12.png]]
*그림 15.12 — A2C·DDPG·D4PG 세 방법의 테스트 보상(왼쪽)·에피소드 스텝(오른쪽) 비교. D4PG(점선)가 가장 빠르고 높게 올라간다*

## 세 줄 정리
- D4PG = DDPG + [[분포적 강화학습과 Categorical DQN]]의 분포적 크리틱 + N-스텝 벨만 + (선택적으로) 우선순위 리플레이.
- 크리틱이 Q값 하나 대신 51개 구간의 확률 분포를 예측하고, 손실은 MSE 대신 교차 엔트로피를 쓴다.
- 실험에서 A2C·DDPG보다 훨씬 빠르고 안정적으로 수렴해 최고 성능을 보였다.
