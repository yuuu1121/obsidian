---
title: "Chapter 12 — 액터-크리틱: A2C와 A3C (Actor-Critic Method: A2C and A3C)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 12
tags: [DeepRL, 강화학습, 액터크리틱, A2C, A3C, 정책경사, 병렬화]
---

# Chapter 12 · 액터-크리틱: A2C와 A3C

> [!abstract] 이 챕터를 한 문장으로
> 정책 경사(policy gradient)의 가장 큰 골칫거리인 **"학습이 널뛰는 문제(분산이 큰 문제)"** 를, 상태마다 다른 기준값을 예측하는 **크리틱(critic) 신경망**을 하나 더 붙여서 해결한 것이 **A2C**이고, 여기에 여러 환경을 동시에 굴리는 **비동기 병렬 실행**을 더한 것이 **A3C**다. 이 두 가지는 딥 RL에서 가장 널리 쓰이는 방법 중 하나다.

---

## 들어가며 — 11장에서 무엇이 부족했나

11장에서 우리는 정답표(라벨) 없이 학습하는 정책 기반 방법 **REINFORCE**와, 할인된 총보상을 그래디언트의 스케일로 쓰는 방식을 배웠다. CartPole처럼 작고 단순한 문제에서는 잘 작동했지만, 더 복잡한 **Pong** 환경에서는 아무리 학습시켜도 수렴하지 않았다.

이번 챕터에서는 정책 경사 방법에 **아주 작은 수정 하나**를 더한다. 그런데 이 수정이 학습의 안정성과 수렴 속도를 극적으로 개선시켜서, 아예 새로운 이름 — **액터-크리틱(actor-critic)** — 이 붙었다. 이 방법은 딥 강화학습(RL)에서 가장 강력한 방법 중 하나로 꼽힌다.

이 챕터에서 다룰 내용:
- 베이스라인이 통계량과 그래디언트의 수렴에 미치는 영향
- 베이스라인 아이디어의 확장판(어드밴티지)
- **어드밴티지 액터-크리틱(A2C)** 방법을 구현하고 Pong 환경에서 확인
- A2C에 **비동기 실행**을 두 가지 다른 방식(데이터 병렬, 그래디언트 병렬)으로 추가하기

---

## 1. 분산 줄이기 (Variance Reduction)

### 1.1 분산이란 무엇이고 왜 문제인가

앞 챕터에서 정책 경사 방법의 안정성을 높이는 방법 중 하나가 **그래디언트의 분산을 줄이는 것**이라고 잠깐 언급했다. 이제 왜 이게 중요한지, 그리고 "분산을 줄인다"는 게 정확히 무슨 뜻인지 이해해 보자.

통계학에서 **분산(variance)** 은 어떤 확률 변수가 평균에서 얼마나 멀리 흩어져 있는지를 재는 값이다:

$$\text{Var}[x] = \mathbb{E}[(x - \mathbb{E}[x])^2]$$

분산이 크면 값이 평균에서 넓게 벗어날 수 있다. 다음 그래프는 평균 $\mu = 10$은 똑같지만 분산이 다른 세 개의 정규(가우시안) 분포를 보여준다.

![[fig_12_1.png]]
*그림 12.1 — 분산이 정규분포 모양에 미치는 영향. 분산이 작을수록(실선) 값이 평균 근처에 뾰족하게 몰리고, 분산이 클수록(점선) 넓게 퍼진다*

> [!tip] 고등학생 눈높이 비유
> 시험 점수가 항상 79~81점 사이인 학생(분산 작음)과, 어떤 날은 20점 어떤 날은 100점을 받는 학생(분산 큼)을 생각해 보자. 평균은 둘 다 80점일 수 있지만, 앞 학생의 "80점"이 훨씬 믿을 만한 정보다. 신경망 학습도 마찬가지다 — 그래디언트(어느 방향으로 파라미터를 고칠지 알려주는 신호)의 분산이 크면, 그 신호를 믿고 따라가기가 어렵다.

### 1.2 정책 경사 복습과 문제 상황

정책 경사는 다음과 같이 쓴다:

$$\nabla J \approx \mathbb{E}[Q(s,a)\nabla \log \pi(a|s)]$$

여기서 스케일링 인자 $Q(s,a)$는 "그 상태에서 그 행동을 얼마나 더/덜 선호하도록 밀어붙일지"를 정한다. REINFORCE에서는 이 자리에 **할인된 총보상**을 그대로 넣었다. REINFORCE의 안정성을 높이기 위해, 우리는 **그래디언트 스케일에서 평균 보상을 빼는** 트릭을 이미 썼었다 — 이것이 바로 **베이스라인(baseline)** 이다.

세 단계짜리 행동 시퀀스로, 총 할인 보상이 각각 $Q_1, Q_2, Q_3$라고 하자.

**예 1**: $Q_1, Q_2$는 작은 양수, $Q_3$은 큰 음수라고 하자. 첫째·둘째 스텝은 어느 정도 성공했지만 셋째 스텝은 크게 실패한 셈이다. 이 경우 결합된 그래디언트는 셋째 스텝의 행동에서는 멀리, 첫째·둘째 스텝의 행동 쪽으로는 살짝 밀어준다. **합리적인 결과다.**

**예 2**: 이번엔 보상이 **항상 양수**이고 값만 다르다고 하자. 앞의 예에 상수를 더한 것과 같다. 이제 $Q_1, Q_2$는 큰 양수, $Q_3$는 작은 양수가 된다. 정책은 세 행동 **모두를** 강하게 선호하는 쪽으로 업데이트되는데, 첫째·둘째 스텝 쪽을 셋째보다 훨씬 강하게 밀어준다. **엄밀히 말하면 셋째 스텝의 행동을 더 이상 회피하려 하지 않는다** — 상대적 순위는 예 1과 똑같은데도!

이렇게 보상에 더해진 **상수**가 정책 업데이트에 영향을 줄 수 있다는 것이 문제다. 학습이 이 상수의 효과를 "평균으로 상쇄"할 때까지 훨씬 더 많은 샘플을 요구하게 되어 학습 속도가 느려진다. 심지어 총 할인 보상이 학습이 진행되며 계속 바뀌기 때문에(에이전트가 점점 더 잘하게 되므로) 정책 경사의 분산도 시간에 따라 변한다. 예를 들어 Atari Pong에서 초반 평균 보상은 −21 ~ −20 정도라, **모든 행동이 거의 똑같이 나빠 보인다.**

이 문제를 해결하려고 11장에서 **총 보상의 평균(베이스라인)** 을 Q값에서 빼는 트릭을 썼다. 이렇게 하면 정책 그래디언트가 정규화된다 — 평균 보상이 −21일 때, −20이라는 보상을 받으면 (원래는 나쁜 성적이지만) 베이스라인을 뺀 뒤엔 마치 승리처럼 보여서, 정책을 그 방향으로 밀어붙이게 된다. 이 트릭의 자세한 통계적 근거는 [[정책 경사와 베이스라인]] 참고.

### 1.3 CartPole로 분산 확인하기

이 이론적 결론을 실제로 확인해 보자. CartPole에서 베이스라인 버전과 베이스라인 없는 버전 각각에 대해 정책 경사의 분산을 측정한다. 전체 예제는 `Chapter12/01_cartpole_pg.py`이며, 대부분의 코드는 11장과 같다. 이 버전에서 달라진 점:

- `-baseline` 명령줄 옵션이 추가되었다. 이 옵션을 켜면 보상에서 평균을 빼는 기능이 활성화된다. 기본값은 베이스라인을 쓰지 않는 것이다.
- 매 훈련 루프마다 **정책 손실에서 나온 그래디언트만** 모아서 분산을 계산한다.

**정책 손실만의 그래디언트를 뽑아내는 방법**: 엔트로피 보너스(탐험을 위해 손실에 추가되는 항, 뒤에서 다시 설명)의 그래디언트는 섞이지 않도록, 그래디언트 계산을 두 단계로 나눈다.

```python
optimizer.zero_grad()
logits_v = net(states_v)
log_prob_v = F.log_softmax(logits_v, dim=1)
log_p_a_v = log_prob_v[range(BATCH_SIZE), batch_actions_t]
log_prob_actions_v = batch_scale_v * log_p_a_v
loss_policy_v = -log_prob_actions_v.mean()
```

한 줄씩 보면:
- `optimizer.zero_grad()`: 이전 스텝에서 쌓여있던 그래디언트를 0으로 초기화한다.
- `logits_v = net(states_v)`: 신경망이 상태를 받아 (아직 확률로 정규화되지 않은) 로짓(logits)을 출력한다.
- `log_prob_v = F.log_softmax(...)`: 로짓을 로그 확률로 바꾼다. `softmax` 후 `log`를 따로 계산하는 것보다 **수치적으로 더 안정적**이라 이 방식을 쓴다.
- `log_p_a_v`: 실제로 취한 행동(`batch_actions_t`)에 해당하는 로그 확률만 골라낸다.
- `log_prob_actions_v = batch_scale_v * log_p_a_v`: 로그 확률에 정책 스케일(베이스라인을 뺀, 또는 안 뺀 총 할인 보상)을 곱한다.
- `loss_policy_v = -log_prob_actions_v.mean()`: 정책 경사는 "개선 방향"인데 손실 함수는 "최소화"해야 하므로 부호를 뒤집어 평균 낸다.

```python
loss_policy_v.backward(retain_graph=True)
```

정책 손실만 역전파해서 그래디언트를 계산하고 신경망 파라미터의 버퍼에 쌓아 둔다. 이미 `optimizer.zero_grad()`를 했으므로, 지금 버퍼에는 **정책 손실만의 그래디언트**만 들어있다. 여기서 `retain_graph=True` 옵션이 중요한 디테일이다 — 보통 `backward()`를 호출하면 계산 그래프가 파괴되지만, 이번엔 그래프 구조를 유지해야 한다(뒤에서 엔트로피 손실에 대해 `backward()`를 한 번 더 호출해야 하기 때문이다). 손실을 여러 번 역전파해야 할 때 흔히 쓰는 기법이지만, 일반적으로 자주 쓰이는 상황은 아니다.

```python
grads = np.concatenate([p.grad.data.numpy().flatten()
                         for p in net.parameters()
                         if p.grad is not None])
```

신경망의 모든 파라미터(각각이 그래디언트를 가진 텐서)를 순회하며, 그 `grad` 필드를 꺼내 1차원으로 펼친(flatten) 뒤 하나의 긴 NumPy 배열로 이어 붙인다. 이렇게 하면 모델의 모든 변수에 대한 그래디언트를 담은 배열 하나가 만들어진다. 하지만 우리의 실제 파라미터 업데이트는 정책 그래디언트뿐 아니라 엔트로피 보너스가 주는 그래디언트도 함께 반영해야 한다.

```python
prob_v = F.softmax(logits_v, dim=1)
entropy_v = -(prob_v * log_prob_v).sum(dim=1).mean()
entropy_loss_v = -ENTROPY_BETA * entropy_v
entropy_loss_v.backward()

optimizer.step()
```

- `entropy_v`: 정책의 [[소프트맥스 Softmax|소프트맥스]] 확률 분포에 대한 **엔트로피**를 계산한다. $H(\pi) = -\sum \pi \log \pi$.
- `entropy_loss_v`: 엔트로피에 음수 부호와 스케일 $\beta$(`ENTROPY_BETA`)를 곱한다. 엔트로피가 커질수록(정책이 골고루 무작위에 가까울수록) 이 손실은 작아지므로, 최소화하면 정책이 너무 확신에 차 있지 않게(탐험을 유지하도록) 유도한다.
- `entropy_loss_v.backward()`: 두 번째 `backward()` 호출. 이번엔 엔트로피 손실을 역전파해서, **기존 정책 손실 그래디언트에 더해준다.** 이때도 그래프가 필요해서 앞서 `retain_graph=True`가 필요했던 것이다.
- `optimizer.step()`: 지금까지 누적된(정책 + 엔트로피) 그래디언트를 사용해 실제로 파라미터를 업데이트한다.

이후 TensorBoard에 통계를 기록한다:

```python
g_l2 = np.sqrt(np.mean(np.square(grads)))
g_max = np.max(np.abs(grads))
writer.add_scalar("grad_l2", g_l2, step_idx)
writer.add_scalar("grad_max", g_max, step_idx)
writer.add_scalar("grad_var", np.var(grads), step_idx)
```

`grad_l2`(그래디언트 벡터의 L2 노름, 즉 전체적인 크기), `grad_max`(그래디언트 성분 중 절댓값이 가장 큰 값), `grad_var`(그래디언트 값들의 분산)을 각각 계산해 TensorBoard로 기록한다.

이 예제를 `-baseline` 옵션을 켠 채로, 그리고 끈 채로 각각 실행하면 정책 그래디언트의 분산을 비교한 그래프를 얻는다. 아래는 보상(왼쪽, 최근 100 에피소드 평균으로 스무딩)과 그래디언트 분산(오른쪽, 로그 스케일, 20구간 스무딩)이다:

![[fig_12_2.png]]
*그림 12.2 — 베이스라인 없음(No baseline)과 베이스라인 있음(Baseline) 버전의 보상(왼쪽)과 그래디언트 분산(오른쪽, 로그 스케일) 비교*

![[fig_12_3.png]]
*그림 12.3 — 그래디언트의 L2 노름(왼쪽)과 최댓값(오른쪽) 비교*

> [!success] 결론
> 베이스라인을 쓴 버전은 안 쓴 버전보다 그래디언트 **분산이 100~1000배(자릿수로 2~3자리) 낮다.** 이렇게 분산이 낮아지면 시스템이 더 빠르고 안정적으로 수렴하는 데 도움이 된다.

---

## 2. 어드밴티지 액터-크리틱 (A2C)

분산을 줄이는 다음 단계는 우리의 베이스라인을 **상태에 의존하도록(state-dependent)** 만드는 것이다. 사실 이건 아주 좋은 아이디어다. 어떤 상태냐에 따라 적절한 베이스라인의 값이 크게 다를 수 있기 때문이다.

### 2.1 왜 상태 가치를 베이스라인으로 써야 할까

어떤 상태에서 취할 행동이 얼마나 좋은지 결정하기 위해, 우리는 그 행동의 **할인된 총보상**을 쓴다. 그런데 이 총보상 자체는 그 **상태의 가치** $V(s)$에, 그 상태에서 그 행동을 고른 것이 주는 추가적인 **어드밴티지(advantage)** $A(s,a)$를 더한 것으로 표현할 수 있다. 8장(DQN의 여러 개선, 특히 듀얼링 DQN)에서 이미 본 형태다:

$$Q(s,a) = V(s) + A(s,a)$$

그렇다면 왜 그냥 $V(s)$를 베이스라인으로 쓰면 안 될까? 사실 될 뿐만 아니라, 매우 좋은 아이디어다! 그렇게 하면 그래디언트의 스케일은 단순히 어드밴티지 $A(s,a)$가 되는데, 이 값은 그 행동이 **평균적인 상태 가치에 비해 얼마나 더/덜 좋은지**를 보여준다. 문제는 우리가 **할인된 총보상 $Q(s,a)$에서 빼줄 $V(s)$의 값을 모른다**는 것이다.

이를 풀기 위해, $V(s)$를 근사하는 **또 다른 신경망**을 쓴다. 이 신경망을 훈련시키는 데는 DQN에서 썼던 것과 똑같은 절차를 활용한다 — 벨만 스텝을 수행하고, 평균제곱오차를 최소화해 $V(s)$ 근사치를 개선한다.

일단 (적어도 근사적으로라도) 어떤 상태의 가치를 알게 되면, 이를 이용해 정책 그래디언트를 계산하고 정책 신경망을 업데이트할 수 있다 — 좋은 어드밴티지 값을 가진 행동의 확률은 올리고, 나쁜 어드밴티지 값을 가진 행동의 확률은 낮춘다.

### 2.2 액터와 크리틱

행동에 대한 확률 분포를 반환하는 정책 신경망을 **액터(actor)** 라고 부른다 — 무엇을 할지 알려주기 때문이다. 다른 신경망은 $V(s)$를 반환해서 우리 행동이 얼마나 좋았는지 이해하게 해 주므로 **크리틱(critic)** 이라고 부른다. 이 개선판은 별도의 이름을 가지는데, 바로 **어드밴티지 액터-크리틱 방법**이며 흔히 **A2C**로 줄여 부른다. 아래 그림은 이 구조를 보여준다.

![[fig_12_4.png]]
*그림 12.4 — A2C 구조. 관측(Observations)이 정책망(Policy net, 액터)과 가치망(Value net, 크리틱)에 각각 들어가서 $\pi(a|s)$와 $V(s)$를 출력한다*

실전에서는 효율성과 수렴 속도를 위해 정책망과 가치망이 부분적으로 **겹치는** 경우가 많다. 이 경우 정책과 가치를 서로 다른 head로 구현하고, 공통 몸통(body)에서 나온 출력을 각 head가 받아 확률 분포와 상태 가치(단일 숫자)로 바꾼다. 이렇게 하면 두 신경망이 저수준 특징(예: Atari 에이전트라면 합성곱 필터)을 공유하면서도, 그것들을 서로 다른 방식으로 조합할 수 있다. 다음 그림은 이 구조를 보여준다:

![[fig_12_5.png]]
*그림 12.5 — 공통 신경망 몸통(Common net, body)을 공유하는 A2C 구조*

이 두 개념(어드밴티지, 액터-크리틱)에 대한 더 자세한 설명은 [[액터-크리틱과 어드밴티지]] 참고.

### 2.3 A2C 훈련 절차 (알고리즘)

훈련 관점에서, 완성된 절차는 다음 단계로 이루어진다:

1. 신경망 파라미터 $\theta$를 무작위 값으로 초기화한다.
2. 현재 정책 $\pi_\theta$를 사용해 환경에서 $N$스텝을 진행하며, 상태 $s_t$, 행동 $a_t$, 보상 $r_t$를 저장한다.
3. 에피소드 끝에 도달했으면 $R \leftarrow 0$, 아니면 $R \leftarrow V_\theta(s_t)$로 설정한다.
4. $i = t-1 \ldots t_{start}$에 대해(스텝들을 **거꾸로** 처리한다는 점에 주의):
   - $R \leftarrow r_i + \gamma R$
   - 정책 그래디언트를 누적:
     $$\partial\theta_\pi \leftarrow \partial\theta_\pi + \nabla_\theta \log \pi_\theta(a_i|s_i)(R - V_\theta(s_i))$$
   - 가치 그래디언트를 누적:
     $$\partial\theta_v \leftarrow \partial\theta_v + \frac{\partial(R - V_\theta(s_i))^2}{\partial\theta_v}$$
5. 누적된 그래디언트를 사용해 신경망 파라미터를 업데이트한다 — 정책 그래디언트 $\partial\theta_\pi$ 방향으로는 그대로, 가치 그래디언트 $\partial\theta_v$의 **반대** 방향으로 움직인다.
6. 수렴할 때까지 2번부터 반복한다.

이 알고리즘은 하나의 개요이자, 연구 논문에 흔히 실리는 형태와 비슷하다. 실전에서는 방법의 안정성을 높이려고 여러 확장을 함께 사용한다:

- **엔트로피 보너스**: 탐험을 개선하기 위해 보통 손실 함수에 엔트로피 값을 더해준다.
  $$\mathcal{L}_H = \beta \sum_i \pi_\theta(s_i) \log \pi_\theta(s_i)$$
  이 함수는 확률 분포가 균등(uniform)할 때 최솟값을 가진다. 손실에 더해주면, 에이전트가 자신의 행동에 지나치게 확신을 가지지 않도록(탐험을 유지하도록) 밀어준다. $\beta$는 엔트로피 보너스의 크기를 조절하고 탐험의 우선순위를 정하는 하이퍼파라미터로, 보통은 상수이거나 훈련 중 선형으로 줄어든다.
- **그래디언트 누적을 손실 함수로 구현**: 실전에서는 정책 손실, 가치 손실, 엔트로피 손실 세 요소를 결합한 손실 함수로 그래디언트 누적을 구현하는 경우가 많다. 다만 부호에 주의해야 하는데, 정책 그래디언트는 정책 개선의 방향을 알려주지만 가치 손실과 엔트로피 손실은 **최소화**해야 하기 때문이다.
- **여러 환경 사용**: 안정성을 개선하려면 여러 환경을 함께 쓰는 것이 좋다. 여러 환경이 있으면 관측들로부터 훈련 배치를 만들 수 있기 때문이다. 이 챕터 뒤쪽에서 A3C 방법을 논의할 때 여러 방식을 더 살펴본다.

앞의 두 항목(엔트로피 보너스, 그래디언트 클리핑 포함)은 [[A2C와 A3C]]와 [[그래디언트 클리핑]]에서 더 자세히 다룬다.

---

## 3. A2C를 Pong에 적용하기

11장에서 우리는 (그다지 성공적이지 못한) 정책 경사 방법으로 Pong 환경을 풀어보려 했다. 이번엔 손에 쥔 액터-크리틱 방법으로 다시 도전한다. 전체 소스 코드는 `Chapter12/02_pong_a2c.py`에 있다.

### 3.1 하이퍼파라미터

```python
GAMMA = 0.99
LEARNING_RATE = 0.001
ENTROPY_BETA = 0.01
BATCH_SIZE = 128
NUM_ENVS = 50

REWARD_STEPS = 4
CLIP_GRAD = 0.1
```

이 값들은 튜닝된 값이 아니며(독자를 위한 연습 과제로 남겨둠), 여기 새로운 값 하나가 있다: `CLIP_GRAD`다. 이 하이퍼파라미터는 최적화 단계에서 그래디언트가 너무 커지지 않도록 잘라내는(clip) 임계값을 정한다. 클리핑은 PyTorch 기능으로 구현하지만 아이디어는 단순하다 — 그래디언트의 L2 노름이 이 하이퍼파라미터보다 크면, 그래디언트 벡터를 이 값에 맞춰 잘라낸다.

`REWARD_STEPS` 하이퍼파라미터는 각 행동에 대해 할인된 총보상을 근사할 때 몇 스텝을 앞서 볼지 정한다. 앞선 정책 경사 방법들에서는 약 10스텝을 썼지만, A2C에서는 가치 근사($V(s)$)를 이용해 더 먼 스텝의 상태 가치를 얻으므로 스텝 수를 줄여도 괜찮다.

### 3.2 신경망 구조

```python
class AtariA2C(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int):
        super(AtariA2C, self).__init__()

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
        self.policy = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, n_actions)
        )
        self.value = nn.Sequential(
            nn.Linear(size, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )
```

한 줄씩 뜯어보면:
- `self.conv`: 3개의 합성곱 레이어(`Conv2d`)와 [[활성화함수|ReLU 활성화함수]]로 구성된 **공통 몸통(body)**. 이미지(게임 화면) 관측을 저수준 특징 벡터로 변환한다. 마지막에 `nn.Flatten()`으로 다차원 텐서를 1차원으로 펼친다.
- `size = self.conv(torch.zeros(1, *input_shape)).size()[-1]`: 더미(가짜) 입력을 한 번 흘려보내서, 합성곱을 통과한 출력의 크기를 자동으로 계산한다. 입력 이미지 크기가 바뀌어도 이 코드가 알아서 맞는 크기를 찾아준다.
- `self.policy`: 액터(정책) head. 은닉층 512개, 출력층은 `n_actions`개 — 각 행동에 대한 (아직 정규화되지 않은) 로짓을 반환한다.
- `self.value`: 크리틱(가치) head. 마찬가지로 은닉층 512개를 거쳐, 출력층은 딱 **1개**의 숫자 — 그 상태의 가치 $V(s)$ 근사값 — 를 반환한다.

이 구조는 8장의 [[듀얼링 DQN Dueling Architecture|듀얼링 DQN]] 구조와 비슷해 보일 수 있지만, **훈련 절차가 다르다**(듀얼링 DQN은 여전히 하나의 Q값을 만들기 위해 두 head를 합치지만, A2C는 정책과 가치를 별도 목적으로 각각 학습시킨다).

```python
def forward(self, x: torch.ByteTensor) -> tt.Tuple[torch.Tensor, torch.Tensor]:
    xx = x / 255
    conv_out = self.conv(xx)
    return self.policy(conv_out), self.value(conv_out)
```

순전파(forward)는 두 개의 텐서 — 정책(로짓)과 가치 — 를 튜플로 반환한다. `x / 255`는 화면 픽셀 값(0~255의 정수)을 0~1 사이의 실수로 정규화하는 흔한 전처리다.

### 3.3 배치 언패킹 — Q값 계산

다음으로 다뤄야 할 크고 중요한 함수는, 환경 전이(transition)들의 배치를 받아서 상태·행동·Q값, 세 개의 텐서를 반환하는 함수다. Q값은 다음 공식으로 계산된다:

$$Q(s,a) = \sum_{i=0}^{N-1} \gamma^i r_i + \gamma^N V(s_N)$$

이 Q값은 두 군데에서 쓰인다 — DQN과 같은 방식으로 가치 근사를 개선하는 **평균제곱오차(MSE) 손실**을 계산하는 데, 그리고 행동의 어드밴티지를 계산하는 데.

```python
def unpack_batch(batch: tt.List[ExperienceFirstLast], net: AtariA2C,
                  device: torch.device, gamma: float, reward_steps: int):
    states = []
    actions = []
    rewards = []
    not_done_idx = []
    last_states = []
    for idx, exp in enumerate(batch):
        states.append(np.asarray(exp.state))
        actions.append(int(exp.action))
        rewards.append(exp.reward)
        if exp.last_state is not None:
            not_done_idx.append(idx)
            last_states.append(np.asarray(exp.last_state))
```

처음엔 그냥 배치의 각 transition을 순회하며 필드들을 리스트로 복사한다. `exp.reward`는 이미 `ptan.ExperienceSourceFirstLast` 클래스를 쓰기 때문에 `REWARD_STEPS`만큼의 **할인 보상이 미리 합산되어** 들어있다는 점에 주목하자. 에피소드가 끝난 상황도 함께 처리하고, 끝나지 않은(non-terminal) 배치 항목의 인덱스도 기억해 둔다(`not_done_idx`).

```python
states_t = torch.FloatTensor(np.asarray(states)).to(device)
actions_t = torch.LongTensor(actions).to(device)
```

모아둔 상태와 행동을 PyTorch 텐서로 바꾸고 필요하면 GPU로 옮긴다. 여기서 `np.asarray()`를 굳이 한 번 더 호출하는 게 불필요해 보일 수 있지만, 이걸 빼면 텐서 생성 성능이 5~10배 나빠진다. 이는 PyTorch의 issue #13918로 알려진 문제이며, 이 책을 쓰는 시점까지도 해결되지 않았다. 해결책 중 하나는 배열들의 리스트 대신 단일 NumPy 배열을 넘기는 것이다.

나머지 함수는 종료 에피소드를 고려해 Q값을 계산한다:

```python
rewards_np = np.array(rewards, dtype=np.float32)
if not_done_idx:
    last_states_t = torch.FloatTensor(
        np.asarray(last_states)).to(device)
    last_vals_v = net(last_states_t)[1]
    last_vals_np = last_vals_v.data.cpu().numpy()[:, 0]
    last_vals_np *= gamma ** reward_steps
    rewards_np[not_done_idx] += last_vals_np
```

앞의 코드는 전이 사슬의 마지막 상태를 담은 변수를 준비하고, 우리 신경망에 $V(s)$ 근사값을 물어본다. 그런 다음 이 값에 할인 계수를 곱해(`gamma ** reward_steps`) 즉시 보상에 더한다.

```python
    ref_vals_t = torch.FloatTensor(rewards_np).to(device)
    return states_t, actions_t, ref_vals_t
```

마지막으로 계산된 Q값을 텐서로 포장해 반환한다.

### 3.4 벡터화된 환경 (SyncVectorEnv)

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default="cpu", help="Device to use, default=cpu")
    parser.add_argument("--use-async", default=False, action='store_true',
                         help="Use async vector env (A3C mode)")
    parser.add_argument("-n", "--name", required=True, help="Name of the run")
    args = parser.parse_args()
    device = torch.device(args.dev)

    env_factories = [
        lambda: ptan.common.wrappers.wrap_dqn(gym.make("PongNoFrameskip-v4"))
        for _ in range(NUM_ENVS)
    ]
    if args.use_async:
        env = gym.vector.AsyncVectorEnv(env_factories)
    else:
        env = gym.vector.SyncVectorEnv(env_factories)
    writer = SummaryWriter(comment="-pong-a2c_" + args.name)
```

새로운 방식으로 환경을 만드는 코드가 보인다: `gym.vector.SyncVectorEnv` 클래스에는, 환경을 만드는 람다 함수들의 리스트를 넘겨준다. `gym.vector.SyncVectorEnv`는 [[Wrapper 래퍼 패턴|Gymnasium]]이 제공하는 클래스로, 여러 환경을 하나의 "벡터화된" 환경으로 감싸는 역할을 한다. 감싸지는 환경들은 반드시 동일한 행동·관측 공간을 가져야 하며, 이 벡터화된 환경은 행동들의 벡터를 받아 관측·보상들의 배치를 반환한다. 자세한 내용은 Gymnasium 문서(`https://gymnasium.farama.org/api/vector/`)를 참고하자.

동기화된 벡터 환경(`SyncVectorEnv` 클래스)은 9장 "여러 환경(Several environments)" 절에서 여러 gym 환경을 실험 소스에 넘겨 DQN 훈련 성능을 높였던 것과 거의 같은 최적화다.

하지만 벡터화된 환경의 경우엔 다른 실험 소스 클래스가 필요하다: `VectorExperienceSourceFirstLast`인데, 이는 벡터화와 에이전트가 관측에 적용되는 방식을 고려해 최적화한 클래스다. 겉에서 보는 인터페이스는 이전과 완전히 똑같다.

명령줄 인자 `-use-async`(래퍼 클래스를 `SyncVectorEnv`에서 `AsyncVectorEnv`로 바꾼다)는 지금은 중요하지 않다 — 나중에 A3C 방법을 논의할 때 쓴다.

### 3.5 신경망, 에이전트, 실험 소스 만들기

```python
net = common.AtariA2C(env.single_observation_space.shape,
                       env.single_action_space.n).to(device)
print(net)

agent = ptan.agent.PolicyAgent(lambda x: net(x)[0], apply_softmax=True,
                                device=device)
exp_source = VectorExperienceSourceFirstLast(
    env, agent, gamma=GAMMA, steps_count=REWARD_STEPS)

optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE, eps=1e-3)
```

한 가지 매우 중요한 디테일은 옵티마이저에 `eps` 파라미터를 넘긴다는 점이다. **Adam** 알고리즘에 익숙하다면, 엡실론(epsilon)이 0으로 나누는 상황을 막기 위해 분모에 더해지는 작은 숫자라는 걸 알 것이다. 보통은 $10^{-8}$이나 $10^{-10}$처럼 아주 작은 값을 쓰지만, 우리 경우엔 이런 값이 지나치게 작아서 문제가 됐다. 저자도 수학적으로 엄밀한 설명은 없다고 밝히지만, **매우 그럴듯한 이유는** 기본 엡실론 값이 너무 작으면 아주 작은 값으로 나누는 연산이 그래디언트를 너무 크게 만들어 학습 안정성에 치명적이라는 것이다.

또 다른 디테일은 `ExperienceSourceFirstLast` 대신 `VectorExperienceSourceFirstLast`를 쓴다는 점이다. 이는 여러 개의 일반 Atari 환경을 감싼 벡터화된 환경 때문에 필요하다. 벡터화된 환경은 `single_observation_space`와 `single_action_space` 속성도 노출하는데, 이는 개별 환경 하나의 관측·행동 공간이다.

### 3.6 훈련 루프

```python
batch = []

with common.RewardTracker(writer, stop_reward=18) as tracker:
    with TBMeanTracker(writer, batch_size=10) as tb_tracker:
        for step_idx, exp in enumerate(exp_source):
            batch.append(exp)

            new_rewards = exp_source.pop_total_rewards()
            if new_rewards:
                if tracker.reward(new_rewards[0], step_idx):
                    break

            if len(batch) < BATCH_SIZE:
                continue
```

이 훈련 루프에서는 두 개의 래퍼를 쓴다. `common.RewardTracker`는 이미 익숙할 것이다 — 최근 100 에피소드의 평균 보상을 계산하고, 그 평균이 목표 임계값(`stop_reward=18`)을 넘으면 알려준다. 다른 래퍼인 `TBMeanTracker`는 PTAN 라이브러리 소속으로, 측정한 파라미터들의 **최근 10스텝 평균**을 TensorBoard에 기록한다. 훈련이 수백만 스텝에 이를 수 있는데 그 모든 점을 TensorBoard에 하나하나 쓰기보다, **스무딩된 값**을 매 10스텝마다 쓰는 게 도움이 된다.

배치 크기(`BATCH_SIZE`)에 도달할 때까지는 그냥 transition을 배치에 쌓기만 하고 계속 진행한다.

### 3.7 손실 계산 — A2C 방법의 핵심

```python
states_t, actions_t, vals_ref_t = common.unpack_batch(
    batch, net, device=device, gamma=GAMMA, reward_steps=REWARD_STEPS)
batch.clear()

optimizer.zero_grad()
logits_t, value_t = net(states_t)
```

앞서 만든 함수로 배치를 언패킹하고, 신경망에 상태를 흘려보내 정책(로짓)과 가치를 얻는다. 정책은 정규화되지 않은 형태로 반환되므로, 확률 분포로 바꾸려면 소프트맥스를 적용해야 한다. 정책 손실은 확률 분포의 로그가 필요하므로, `softmax`를 부른 뒤 `log`를 부르는 대신 수치적으로 더 안정적인 함수 `log_softmax`를 쓴다.

**가치 손실**은 신경망이 반환한 가치와, 벨만 방정식을 4스텝 앞서 풀어서 얻은 근사치 사이의 MSE로 계산한다:

```python
loss_value_t = F.mse_loss(value_t.squeeze(-1), vals_ref_t)
```

다음으로 정책 손실을 계산해 정책 그래디언트를 구한다:

```python
log_prob_t = F.log_softmax(logits_t, dim=1)
adv_t = vals_ref_t - value_t.detach()
log_act_t = log_prob_t[range(BATCH_SIZE), actions_t]
log_prob_actions_t = adv_t * log_act_t
loss_policy_t = -log_prob_actions_t.mean()
```

한 줄씩 짚어보면:
- `log_prob_t`: 정책의 로그 확률.
- `adv_t = vals_ref_t - value_t.detach()`: **어드밴티지**를 계산한다 — $A(s,a) = Q(s,a) - V(s)$. `value_t.detach()` 호출이 중요한데, 정책 그래디언트를 우리의 가치 근사 head로 전파시키고 싶지 않기 때문이다(`detach()`는 계산 그래프에서 이 텐서를 "떼어내" 역전파가 여기서 멈추게 한다).
- `log_act_t`: 실제로 취한 행동에 대한 로그 확률만 골라낸다.
- `log_prob_actions_t = adv_t * log_act_t`: 취한 행동의 로그 확률에 어드밴티지를 곱해서 스케일한다.
- `loss_policy_t = -log_prob_actions_t.mean()`: 정책 그래디언트 손실값은 이 스케일된 로그 확률의 음수 평균이다 — 정책 그래디언트는 정책 개선 방향을 알려주지만, 손실값은 최소화되어야 하기 때문이다.

마지막 조각은 **엔트로피 손실**이다:

```python
prob_t = F.softmax(logits_t, dim=1)
entropy_loss_t = ENTROPY_BETA * (prob_t * log_prob_t).sum(dim=1).mean()
```

엔트로피 손실은 정책의 엔트로피를 스케일하되 **부호를 반대로** 취한 값과 같다(엔트로피 자체는 $H(\pi) = -\sum \pi \log \pi$로 계산된다).

다음 코드에서는 우리 정책의 그래디언트를 계산하고 추출하는데, 이는 최대 그래디언트·분산·L2 노름을 추적하는 데 쓰인다:

```python
loss_policy_t.backward(retain_graph=True)
grads = np.concatenate([
    p.grad.data.cpu().numpy().flatten()
    for p in net.parameters() if p.grad is not None
])
```

훈련의 마지막 단계로, 엔트로피 손실과 가치 손실을 역전파하고, 그래디언트를 클리핑한 뒤 옵티마이저에게 신경망을 업데이트하도록 요청한다:

```python
loss_v = entropy_loss_t + loss_value_t
loss_v.backward()
nn_utils.clip_grad_norm_(net.parameters(), CLIP_GRAD)
optimizer.step()
loss_v += loss_policy_t
```

`nn_utils.clip_grad_norm_(net.parameters(), CLIP_GRAD)`가 바로 [[그래디언트 클리핑]]이 적용되는 지점이다 — 그래디언트의 L2 노름이 `CLIP_GRAD(=0.1)`보다 크면, 방향은 유지한 채 크기만 그 값으로 줄인다. 마지막 줄 `loss_v += loss_policy_t`는 (이미 역전파는 끝났으므로) TensorBoard에 기록할 **총 손실 값**을 합쳐 완성하는 용도다.

훈련 루프의 끝에서, TensorBoard로 모니터링할 모든 값을 기록한다:

```python
tb_tracker.track("advantage", adv_t, step_idx)
tb_tracker.track("values", value_t, step_idx)
tb_tracker.track("batch_rewards", vals_ref_t, step_idx)
tb_tracker.track("loss_entropy", entropy_loss_t, step_idx)
tb_tracker.track("loss_policy", loss_policy_t, step_idx)
tb_tracker.track("loss_value", loss_value_t, step_idx)
tb_tracker.track("loss_total", loss_v, step_idx)
tb_tracker.track("grad_l2", np.sqrt(np.mean(np.square(grads))), step_idx)
tb_tracker.track("grad_max", np.max(np.abs(grads)), step_idx)
tb_tracker.track("grad_var", np.var(grads), step_idx)
```

모니터링할 값이 많은데, 이건 다음 절에서 자세히 살펴본다.

### 3.8 결과

훈련을 시작하려면 `02_pong_a2c.py`를 `-dev`(GPU를 쓰려면) 옵션과, TensorBoard 실행 이름을 지정하는 `-n` 옵션과 함께 실행한다:

```
Chapter12$ ./02_pong_a2c.py --dev cuda -n tt
A.L.E: Arcade Learning Environment (version 0.8.1+53f58b7)
[Powered by Stella]
AtariA2C(
  (conv): Sequential(
    (0): Conv2d(4, 32, kernel_size=(8, 8), stride=(4, 4))
    (1): ReLU()
    (2): Conv2d(32, 64, kernel_size=(4, 4), stride=(2, 2))
    (3): ReLU()
    (4): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1))
    (5): ReLU()
    (6): Flatten(start_dim=1, end_dim=-1)
  )
  (policy): Sequential(
    (0): Linear(in_features=3136, out_features=512, bias=True)
    (1): ReLU()
    (2): Linear(in_features=512, out_features=6, bias=True)
  )
  (value): Sequential(
    (0): Linear(in_features=3136, out_features=512, bias=True)
    (1): ReLU()
    (2): Linear(in_features=512, out_features=1, bias=True)
  )
)
37850: done 1 games, mean reward -21.000, speed 1090.79 f/s
```

> [!warning] 훈련은 오래 걸린다
> 원래 하이퍼파라미터 그대로면 약 1000만 프레임이 필요한데, GPU 기준으로 약 3시간이 걸린다.

훈련이 끝나면(A3C 절에서 환경을 별도 프로세스에서 실행하는 방법을 다루기 전에 먼저 A2C 자체의 TensorBoard 그래프를 확인하자):

![[fig_12_6.png]]
*그림 12.6 — 스무딩된 보상(왼쪽)과 평균 배치 가치(오른쪽). 왼쪽 그래프는 최근 100 에피소드 평균 보상이고, 오른쪽 "batch value"는 벨만 방정식으로 근사한 Q값이 시간에 따라 대체로 증가하는 양상을 보여준다 — 훈련이 꾸준히 개선되고 있다는 뜻이다*

11장의 예제보다 보상 그래프가 훨씬 좋아졌다. 다음 4개 그래프는 손실과 관련된 것들이다:

![[fig_12_7.png]]
*그림 12.7 — 엔트로피 손실(왼쪽)과 정책 손실(오른쪽)*

![[fig_12_8.png]]
*그림 12.8 — 가치 손실(왼쪽)과 총 손실(오른쪽)*

여기서 주목할 점들:
- **가치 손실**(그림 12.8 왼쪽)이 꾸준히 감소한다 — $V(s)$ 근사가 훈련 중 계속 좋아지고 있다는 뜻이다.
- **엔트로피 손실**(그림 12.7 왼쪽)이 훈련 중반에 커진다. 하지만 총 손실에서 지배적인 비중을 차지하지는 않는다. 이건 기본적으로 에이전트가 자신의 행동에 점점 더 확신을 가지게 되어(정책이 균등 분포에서 멀어져) 간다는 뜻이다.
- **정책 손실**(그림 12.7 오른쪽)은 대부분의 구간에서 감소하고, 총 손실과 상관관계를 보인다 — 좋은 신호다. 우리가 가장 관심 있는 것은 정책에 대한 그래디언트이기 때문이다.

마지막 그래프 세트는 어드밴티지 값과 정책 그래디언트 관련 지표들이다:

![[fig_12_9.png]]
*그림 12.9 — 어드밴티지(왼쪽)와 그래디언트의 L2 노름(오른쪽)*

![[fig_12_10.png]]
*그림 12.10 — 그래디언트의 최댓값(왼쪽)과 그래디언트 분산(오른쪽)*

**어드밴티지**는 정책 그래디언트의 스케일이며 $Q(s,a) - V(s)$와 같다. 평균적으로 단일 행동이 상태의 가치에 미치는 영향이 크지 않으므로, 값이 0 근처에서 진동할 것으로 기대되는데, 그래프가 정확히 그렇게 보여준다. 그래디언트 그래프들은 우리 그래디언트가 너무 작지도, 너무 크지도 않다는 것을 보여준다. 그래디언트 분산은 훈련 초반 2백만 프레임 동안은 매우 작다가, 이후 커지기 시작하는데 이는 정책이 계속 변화하고 있다는 뜻이다.

---

## 4. 비동기 어드밴티지 액터-크리틱 (A3C)

이제 A2C 방법을 확장해 보자. 이 확장은 **진짜 비동기** 환경 상호작용을 더해주며, **비동기 어드밴티지 액터-크리틱(asynchronous advantage actor-critic)**, 즉 **A3C**라고 부른다. RL 실무자들이 가장 널리 쓰는 방법 중 하나다.

A2C에 비동기 동작을 추가하는 두 가지 접근법을 살펴본다: **데이터 수준(data-level)** 병렬화와 **그래디언트 수준(gradient-level)** 병렬화다. 둘은 자원 요구 사항과 특성이 달라, 서로 다른 상황에 적합하다. 두 방식의 배경 이론은 [[동기·비동기 병렬화(데이터·그래디언트 병렬)]]에서 더 자세히 다루고, 여기서는 이 챕터의 흐름에 맞춰 핵심만 정리한다.

### 4.1 상관관계와 표본 효율성

정책 경사 계열 방법의 안정성을 개선하는 접근법 중 하나는 **여러 환경을 병렬로** 쓰는 것이다. 그 배경에는 6장에서 다뤘던 근본적인 문제 — **샘플 간 상관관계**가 있다. 이는 확률적 경사 하강법(SGD) 최적화에 핵심적인 [[IID 독립항등분포|IID(독립 항등 분포)]] 가정을 깬다. 이런 상관관계의 부정적 결과는 그래디언트의 **매우 높은 분산**이다 — 훈련 배치가 서로 비슷한 예시들로 채워져서, 모두가 신경망을 같은 방향으로 밀어붙이지만, 그게 전역적으로는 완전히 틀린 방향일 수도 있다.

DQN에서는 이 문제를 이전 상태들을 대량으로 리플레이 버퍼에 저장하고 훈련 배치를 거기서 샘플링하는 방식으로 풀었다. 버퍼가 충분히 크면, 무작위 샘플이 전체 상태 분포를 훨씬 잘 대표한다. 안타깝게도 이 해법은 정책 경사 방법에는 통하지 않는다. 이들 대부분이 **온폴리시(on-policy)** 라서, 현재 정책이 만든 샘플로 학습해야 하기 때문이다. 옛 전이를 재사용할 수도 있지만, 그 결과 나오는 정책 그래디언트는 업데이트하려는 현재 정책이 아니라 옛 정책에 대한 것이 되어버린다.

가장 흔히 쓰이는 해법은 **여러 개의 병렬 환경**에서 전이를 함께 모으는 것이다. 이렇게 하면 한 에피소드 안의 상관관계는 깨지면서, 여전히 현재 정책을 쓴다. 이 방식의 큰 단점은 **표본 비효율성**이다 — 한 번 훈련에 쓴 경험은 통째로 버려진다. 예를 들어 DQN이 리플레이 버퍼 100만 개, 훈련 배치 크기 32를 쓴다면, 새 프레임마다 하나의 전이가 리플레이에서 제거되기 전까지 평균 약 32번 재사용된다. [[우선순위 경험 리플레이|우선순위 리플레이 버퍼]]라면 샘플 확률이 균등하지 않으므로 이 숫자는 더 클 수도 있다. 반면 정책 경사 방법에서는 환경으로부터 얻은 각 경험을 **한 번만** 쓸 수 있는데, 이는 새로운(신선한) 데이터가 필요하기 때문이다. 따라서 정책 경사 방법의 데이터 효율은 값 기반, 오프폴리시 방법보다 한 자릿수 정도 낮을 수 있다.

반면, A2C 에이전트는 Pong을 800만 프레임에 수렴시켰는데, 이는 6장·8장의 기본 DQN이 쓴 100만 프레임보다 겨우 8배 많은 정도다. 이는 정책 경사 방법이 완전히 쓸모없지는 않다는 것을 보여준다 — 각자의 특성이 있고, 방법을 선택할 때 이를 고려해야 한다. 여러분의 환경이 (에이전트와의 상호작용이 빠르고, 메모리 사용량이 적고, 병렬화가 잘 되는 등) "값싸다"면, 정책 경사 방법이 더 나은 선택일 수 있다. 반대로 환경이 "비싸서" 많은 경험을 얻는 게 훈련 과정을 느리게 만든다면, 값 기반 오프폴리시 방법이 더 똑똑한 길일 수 있다.

### 4.2 A2C에 "A" 하나 더 추가하기

실용적인 관점에서, 여러 병렬 환경과 통신하는 것은 단순하다. 사실 9장과 이 챕터 앞부분에서 이미 이걸 했었지만 명시적으로 언급하지는 않았다. A2C 에이전트에서, 우리는 gym 환경들의 배열을 `ExperienceSource` 클래스에 넘겼고, 이 클래스는 **라운드로빈(round-robin) 데이터 수집 모드**로 전환되었다. 즉 실험 소스에게서 전이를 요청할 때마다, 이 클래스는 배열의 다음 환경을 사용한다(물론 환경마다 상태는 유지하면서). 이 단순한 접근법은 환경들과의 병렬 통신과 동등한 효과를 내지만, 딱 한 가지 차이가 있다 — **엄밀한 의미의 병렬은 아니고, 순차적인 방식으로 수행된다.** 다만 우리 실험 소스에서 나오는 샘플들은 섞여(shuffled) 있다. 이 아이디어는 다음 그림이 보여준다:

![[fig_12_11.png]]
*그림 12.11 — 여러 환경으로부터 훈련하는 에이전트(순차적 처리 방식)*

이 방식은 A2C 방법에서 잘 작동해 수렴을 얻어냈지만, 계산 자원 활용 측면에서는 아직 완벽하지 않다 — 모든 처리가 순차적으로 이뤄지기 때문이다. 요즘엔 소박한 워크스테이션도 여러 개의 CPU 코어를 갖고 있어, 훈련과 환경 상호작용 같은 계산에 이를 활용할 수 있다. 반면 병렬 프로그래밍은 전통적인 순차적 실행 흐름보다 어렵다. 다행히 파이썬은 매우 표현력 있고 유연한 언어라서, 큰 어려움 없이 병렬 프로그래밍을 할 수 있는 여러 서드파티 라이브러리가 있다. 우리는 이미 9장에서 DQN 훈련 중 에이전트 실행을 병렬화하는 데 `torch.multiprocessing` 라이브러리 예제를 봤다. 그 밖에도 `ray`처럼 코드 실행을 병렬화해 저수준 통신 디테일을 감춰주는 더 상위 수준의 라이브러리도 있다.

액터-크리틱 병렬화에 관해서는 두 가지 접근법이 있다:

1. **데이터 병렬(data parallelism)**: 여러 프로세스를 두고, 각각 하나 이상의 환경과 통신하며 전이 $(s,r,a,s')$를 우리에게 제공한다. 이 모든 샘플이 하나의 훈련 프로세스로 모여서, 그곳에서 손실을 계산하고 SGD 업데이트를 수행한다. 그런 다음 업데이트된 신경망 파라미터는 미래의 환경 통신에 쓰이도록 다른 모든 프로세스에 전파(broadcast)되어야 한다. 이 모델은 그림 12.12에 나타나 있다.
2. **그래디언트 병렬(gradient parallelism)**: 훈련 과정의 목표는 신경망을 업데이트할 그래디언트를 계산하는 것이므로, 여러 프로세스가 자신의 훈련 샘플로 각자 그래디언트를 계산하게 할 수 있다. 그런 다음 이 그래디언트들을 하나의 프로세스에서 합산해 SGD 업데이트를 수행한다. 물론 업데이트된 신경망 가중치도 모든 워커에게 다시 전파되어야 온폴리시 상태를 유지할 수 있다. 이 방식은 그림 12.13에 나타나 있다.

![[fig_12_12.png]]
*그림 12.12 — 액터-크리틱 병렬화의 첫 번째 접근법. 분산된 훈련 표본 수집에 기반한다*

![[fig_12_13.png]]
*그림 12.13 — 병렬화의 두 번째 접근법. 모델의 그래디언트를 모은다*

두 방식의 차이는 다이어그램만 봐서는 그리 커 보이지 않을 수 있지만, **계산 비용**을 인식할 필요가 있다. A2C 최적화에서 가장 무거운 연산은 훈련 과정 그 자체다 — 데이터 표본으로부터 손실을 계산(순전파)하고, 이 손실에 대한 그래디언트를 계산(역전파)하는 것. SGD 최적화 단계는 상당히 가볍다 — 사실상 스케일된 그래디언트를 신경망 가중치에 더하기만 하면 된다. 두 번째 접근법(그래디언트 병렬화)에서 손실과 그래디언트 계산을 중앙 프로세스로부터 옮김으로써, 우리는 주요 잠재적 병목을 제거했고 전체 프로세스를 훨씬 더 확장 가능하게 만들었다.

실전에서는 방법의 선택이 주로 자원과 목표에 달려 있다. 하나의 최적화 문제와 네트워크에 분산된 수십 개의 GPU 같은 많은 분산 계산 자원을 갖고 있다면, 그래디언트 병렬화가 훈련 속도를 높이는 최선의 접근법이다. 반면 GPU 한 대만 있는 경우, 두 방식은 비슷한 성능을 낼 것이지만, 첫 번째 접근법이 일반적으로 구현이 더 간단하다 — 저수준 그래디언트 값을 다룰 필요가 없기 때문이다. 이 챕터에서는 두 방법을 우리가 좋아하는 게임 Pong에서 비교해 보고 PyTorch의 멀티프로세싱 기능을 살펴본다.

---

## 5. A3C — 데이터 병렬 구현

우리가 확인할 A3C 병렬화의 첫 번째 버전(그림 12.12에 정리한 방식)은, 훈련을 담당하는 하나의 메인 프로세스와, 환경들과 통신하며 훈련용 경험을 모으는 여러 자식 프로세스로 구성된다.

사실 이 버전은 이미 9장에서 DQN 모델을 훈련할 때 여러 에이전트를 서브프로세스에서 실행하며 구현한 적이 있다(당시 FPS 기준 27% 속도 향상을 얻었다). 이번 절에서는 A3C 방법으로 같은 접근법을 다시 구현하지는 않고, 대신 "**라이브러리의 힘**"을 보여주고자 한다.

앞서 Gymnasium의 `gym.vector.SyncVectorEnv` 클래스(오리지널 OpenAI Gym이 아니라 **Farama fork**에만 존재)와, "벡터화된" 환경을 지원하는 PTAN 실험 소스 `VectorExperienceSourceFirstLast`를 잠깐 언급했었다. `SyncVectorEnv` 클래스는 감싸인 환경들을 **순차적으로** 처리하지만, 이를 그대로 대체할 수 있는 클래스 `AsyncVectorEnv`가 있는데, 이건 하위 환경들에 대해 `mp.multiprocessing`을 사용한다. 즉 A2C 방법의 데이터 병렬 버전을 얻으려면, `SyncVectorEnv`를 `AsyncVectorEnv`로 **바꿔 끼우기만** 하면 끝난다!

`Chapter12/02_pong_a2c.py`의 코드는 이미 이 교체를 지원한다. 명령줄 옵션 `-use-async`를 넘기면 된다.

### 5.1 결과

50개 환경으로 실행한 비동기 버전은 **2000 FPS**의 성능을 보였는데, 이는 순차 버전 대비 **2배 개선**이다. 다음 그래프는 두 버전의 성능과 보상 다이내믹스를 비교한다:

![[fig_12_14.png]]
*그림 12.14 — A2C와 (데이터 병렬) A3C의 보상(왼쪽)과 속도(오른쪽) 비교*

---

## 6. A3C — 그래디언트 병렬 구현

A2C 구현을 병렬화하는 다음 접근법에서는 여러 자식 프로세스가, 중앙 훈련 루프에 훈련 데이터를 공급하는 대신 **자신의 로컬 훈련 데이터로 그래디언트를 계산**해, 그 그래디언트를 중앙의 마스터 프로세스로 보낸다. 이 프로세스는 그 그래디언트들을 결합(기본적으로 그냥 합산)해 공유 신경망에 SGD 업데이트를 수행하는 책임을 진다.

이 차이는 사소해 보일 수 있지만, 특히 여러 GPU를 갖춘 여러 개의 강력한 노드가 네트워크에 연결된 경우 **훨씬 더 확장성이 좋은** 접근법이다. 이 경우 데이터 병렬 모델에서는 중앙 프로세스가 금세 병목이 되는데, 손실 계산과 역전파가 계산량이 많은 작업이기 때문이다. 그래디언트 병렬화는 부하를 여러 GPU로 분산시키고, 중앙에서는 비교적 단순한 그래디언트 결합 연산만 수행하게 해준다.

### 6.1 구현

완전한 예제는 `Chapter12/03_a3c_grad.py` 파일에 있으며, 이미 살펴본 `Chapter12/lib/common.py` 모듈을 그대로 쓴다. 먼저 하이퍼파라미터를 정의한다:

```python
GAMMA = 0.99
LEARNING_RATE = 0.001
ENTROPY_BETA = 0.01
REWARD_STEPS = 4
CLIP_GRAD = 0.1

PROCESSES_COUNT = 4
NUM_ENVS = 8
GRAD_BATCH = 64
TRAIN_BATCH = 2

ENV_NAME = "PongNoFrameskip-v4"
NAME = 'pong'
REWARD_BOUND = 18
```

앞의 예제와 대체로 같지만, `BATCH_SIZE`가 두 개의 파라미터로 대체됐다: `GRAD_BATCH`와 `TRAIN_BATCH`. `GRAD_BATCH` 값은 자식 프로세스가 손실을 계산하고 그래디언트 값을 얻는 데 쓰는 배치 크기를 정의한다. 두 번째 파라미터 `TRAIN_BATCH`는 매 SGD 반복마다 자식 프로세스들로부터 얼마나 많은 그래디언트 배치를 결합할지 지정한다. 자식 프로세스가 만드는 각 항목은 우리 신경망 파라미터와 같은 모양(shape)을 가지며, 우리는 `TRAIN_BATCH`개의 값을 합산한다.

즉 매 최적화 스텝마다 `TRAIN_BATCH * GRAD_BATCH`개의 훈련 샘플을 사용하는 셈이다. 손실 계산과 역전파가 상당히 무거운 연산이므로, 이를 효율적으로 만들려고 큰 `GRAD_BATCH`를 쓴다. 이렇게 배치가 크다 보니, 신경망 업데이트를 온폴리시로 유지하려면 `TRAIN_BATCH`는 상대적으로 낮게 유지해야 한다.

이제 두 개의 함수가 있다 — 감싸진 Pong 환경을 만드는 `make_env()`, 그리고 훈련 루프에서 보통 하던 일 대부분을 구현하는 훨씬 복잡한 `grads_func()`다. 그 대가로 메인 프로세스의 훈련 루프는 거의 사소해진다:

```python
def make_env() -> gym.Env:
    return ptan.common.wrappers.wrap_dqn(gym.make("PongNoFrameskip-v4"))


def grads_func(proc_name: str, net: common.AtariA2C, device: torch.device,
                train_queue: mp.Queue):
    env_factories = [make_env for _ in range(NUM_ENVS)]
    env = gym.vector.SyncVectorEnv(env_factories)

    agent = ptan.agent.PolicyAgent(lambda x: net(x)[0], device=device,
                                    apply_softmax=True)
    exp_source = VectorExperienceSourceFirstLast(
        env, agent, gamma=GAMMA, steps_count=REWARD_STEPS)

    batch = []
    frame_idx = 0
    writer = SummaryWriter(comment=proc_name)
```

자식 프로세스를 생성할 때, `grads_func()` 함수에 여러 인자를 넘긴다:
- 프로세스의 이름. TensorBoard 작성기를 만드는 데 쓰인다. 이 예제에서는 각 자식 프로세스가 자기만의 TensorBoard 데이터셋을 쓴다.
- 공유되는 신경망(NN).
- 계산 장치를 지정하는 `torch.device` 인스턴스.
- 계산된 그래디언트를 중앙 프로세스에 전달하는 데 쓰이는 큐(queue).

우리 자식 프로세스 함수는 데이터 병렬 버전의 메인 훈련 루프와 매우 비슷해 보인다 — 이는 놀랍지 않은 게, 자식 프로세스의 책임이 늘어났기 때문이다. 그런데 옵티마이저에게 신경망을 업데이트해 달라고 요청하는 대신, **그래디언트를 모아서 큐로 보낸다.**

```python
with common.RewardTracker(writer, REWARD_BOUND) as tracker:
    with TBMeanTracker(writer, 100) as tb_tracker:
        for exp in exp_source:
            frame_idx += 1
            new_rewards = exp_source.pop_total_rewards()
            if new_rewards and tracker.reward(new_rewards[0], frame_idx):
                break

            batch.append(exp)
            if len(batch) < GRAD_BATCH:
                continue
```

여기까지는 배치에 전이들을 모으고, 에피소드 종료 시 보상을 처리한다.

다음 부분에서는 훈련 데이터로부터 결합된 손실을 계산하고 손실의 역전파를 수행한다:

```python
            data = common.unpack_batch(batch, net, device=device, gamma=GAMMA,
                                        reward_steps=REWARD_STEPS)
            states_v, actions_t, vals_ref_v = data
            batch.clear()

            net.zero_grad()
            logits_v, value_v = net(states_v)
            loss_value_v = F.mse_loss(value_v.squeeze(-1), vals_ref_v)

            log_prob_v = F.log_softmax(logits_v, dim=1)
            adv_v = vals_ref_v - value_v.detach()
            log_p_a = log_prob_v[range(GRAD_BATCH), actions_t]
            log_prob_actions_v = adv_v * log_p_a
            loss_policy_v = -log_prob_actions_v.mean()

            prob_v = F.softmax(logits_v, dim=1)
            ent = (prob_v * log_prob_v).sum(dim=1).mean()
            entropy_loss_v = ENTROPY_BETA * ent

            loss_v = entropy_loss_v + loss_value_v + loss_policy_v
            loss_v.backward()
```

이 부분은 A2C 버전과 거의 똑같다. 다만 여기서는 정책 손실·가치 손실·엔트로피 손실을 **한 번에 합쳐** `loss_v`로 만든 뒤 한 번에 역전파한다는 점만 다르다(A2C 버전에서는 정책 손실의 그래디언트를 분산 통계 목적으로 따로 계산하려고 두 번 나눠 `backward()`를 호출했지만, 여기서는 그럴 필요가 없다).

이후 관찰하려는 중간 값들을 TensorBoard로 보낸다:

```python
            tb_tracker.track("advantage", adv_v, frame_idx)
            tb_tracker.track("values", value_v, frame_idx)
            tb_tracker.track("batch_rewards", vals_ref_v, frame_idx)
            tb_tracker.track("loss_entropy", entropy_loss_v, frame_idx)
            tb_tracker.track("loss_policy", loss_policy_v, frame_idx)
            tb_tracker.track("loss_value", loss_value_v, frame_idx)
            tb_tracker.track("loss_total", loss_v, frame_idx)
```

루프의 끝에서는 그래디언트를 클리핑하고, 이를 신경망 파라미터의 별도 버퍼로 추출한다(다음 루프 반복에서 값이 오염되지 않도록 하기 위해서다). 여기서 이렇게 하는 이유는, 우리 신경망 파라미터가 공유되어 있으므로, 다른 워커와의 동기화를 신경 쓰지 않고도 이 작업을 할 수 있기 때문이다 — 그래디언트는 각 프로세스가 **로컬로** 할당하기 때문이다:

```python
            nn_utils.clip_grad_norm_(net.parameters(), CLIP_GRAD)
            grads = [
                param.grad.data.cpu().numpy() if param.grad is not None else None
                for param in net.parameters()
            ]
            train_queue.put(grads)

    train_queue.put(None)
```

`grads_func` 함수의 마지막 줄은 큐에 `None`을 넣는데, 이는 이 자식 프로세스가 **게임 해결(game solved)** 상태에 도달했으니 훈련을 멈춰야 함을 알리는 신호다.

메인 프로세스는 신경망 생성과 그 가중치의 공유로부터 시작한다:

```python
if __name__ == "__main__":
    mp.set_start_method('spawn')
    os.environ['OMP_NUM_THREADS'] = "1"
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default="cpu", help="Device to use, default=cpu")
    parser.add_argument("-n", "--name", required=True, help="Name of the run")
    args = parser.parse_args()
    device = torch.device(args.dev)

    env = make_env()
    net = common.AtariA2C(env.observation_space.shape, env.action_space.n).to(device)
    net.share_memory()
```

여기서는 이전 절과 마찬가지로 `torch.multiprocessing`을 위한 시작 방식(start method)을 설정해야 하고, OpenMP가 실행할 스레드 수도 제한해야 한다. 이는 환경변수 `OMP_NUM_THREADS`를 설정해서 이뤄지는데, 이 값은 OpenMP 라이브러리에게 시작할 수 있는 스레드 수를 알려준다. OpenMP는 Gym과 OpenCV 라이브러리에서 멀티코어 시스템에서 속도 향상을 위해 많이 쓰이며, 대체로 좋은 일이다. 기본적으로 OpenMP를 사용하는 프로세스는 시스템의 코어마다 스레드를 하나씩 시작한다. 하지만 우리 경우엔 그 효과가 정반대다 — 우리가 자체적으로 여러 프로세스를 실행하여 병렬화를 구현하고 있으므로, 추가 스레드가 코어에 과부하를 일으켜 잦은 컨텍스트 전환으로 성능을 떨어뜨린다. 이를 피하려고 명시적으로 스레드 개수를 1개로 제한한다. 저자의 시스템에서는 이 환경변수 설정 없이는 성능이 3~4배 떨어지는 것을 경험했다고 한다.

`net.share_memory()`는 신경망 파라미터를 여러 프로세스가 공유할 수 있는 메모리에 올린다.

이제 통신용 큐를 만들고 필요한 개수만큼 자식 프로세스를 생성한다:

```python
    optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE, eps=1e-3)

    train_queue = mp.Queue(maxsize=PROCESSES_COUNT)
    data_proc_list = []
    for proc_idx in range(PROCESSES_COUNT):
        proc_name = f"-a3c-grad_pong_{args.name}#{proc_idx}"
        p_args = (proc_name, net, device, train_queue)
        data_proc = mp.Process(target=grads_func, args=p_args)
        data_proc.start()
        data_proc_list.append(data_proc)
```

이제 훈련 루프로 넘어갈 수 있다:

```python
    batch = []
    step_idx = 0
    grad_buffer = None

    try:
        while True:
            train_entry = train_queue.get()
            if train_entry is None:
                break
```

그래디언트 병렬 버전의 A3C에서 가장 큰 차이는 **훈련 루프**에 있다 — 자식 프로세스들이 무거운 계산을 이미 다 해줬기 때문에 여기가 훨씬 단순하다. 루프의 초입에서는, 프로세스 중 하나가 원하는 평균 보상에 도달한 상황(큐에 `None`이 들어온 경우)을 처리한다. 이 경우 그냥 루프를 빠져나와 훈련을 중단한다.

신경망의 모든 파라미터에 대해 그래디언트를 함께 합산한다:

```python
            step_idx += 1

            if grad_buffer is None:
                grad_buffer = train_entry
            else:
                for tgt_grad, grad in zip(grad_buffer, train_entry):
                    tgt_grad += grad
```

충분한 그래디언트 조각이 모이면, 그 합계를 PyTorch `FloatTensor`로 변환해 신경망 파라미터의 `grad` 필드에 대입한다. 서로 다른 자식들의 그래디언트를 평균 내려면, 얻은 `TRAIN_BATCH`개의 그래디언트 배치마다 옵티마이저의 `step()` 함수를 호출한다. 중간 스텝에서는 그냥 해당하는 그래디언트끼리 더한다:

```python
            if step_idx % TRAIN_BATCH == 0:
                for param, grad in zip(net.parameters(), grad_buffer):
                    param.grad = torch.FloatTensor(grad).to(device)

                nn_utils.clip_grad_norm_(net.parameters(), CLIP_GRAD)
                optimizer.step()
                grad_buffer = None
```

그다음 필요한 건 신경망 파라미터를 누적된 그래디언트로 업데이트하도록 옵티마이저의 `step()` 메서드를 부르는 것뿐이다.

훈련 루프를 빠져나올 때(`Ctrl + C`로 최적화를 멈춘 경우까지 포함해서), 모든 자식 프로세스를 확실히 종료시켜 준다:

```python
    finally:
        for p in data_proc_list:
            p.terminate()
            p.join()
```

이 단계는 좀비 프로세스가 GPU 자원을 계속 점유하는 것을 막기 위해 필요하다.

### 6.2 결과

이 예제는 이전 예제와 같은 방식으로 시작할 수 있고, 잠시 뒤 속도와 평균 보상을 표시하기 시작한다. 다만 표시되는 정보가 **각 자식 프로세스에 대해 로컬(local)** 이라는 점을 알아둬야 한다 — 즉 속도, 완료된 게임 수, 프레임 수 모두 프로세스 개수만큼 곱해서 이해해야 한다. 저자의 벤치마크에서는 자식마다 약 500~600 FPS 정도가 나와, 총 2000~2400 FPS를 냈다.

수렴 다이내믹스도 이전 버전과 매우 비슷하다. 총 관측 개수는 약 800만~1000만 개이며, 완료까지 약 1.5시간이 걸린다. 아래 왼쪽 보상 그래프는 개별 프로세스들을 보여주고, 오른쪽 속도 그래프는 모든 프로세스의 합계를 보여준다. 그래디언트 병렬화가 데이터 병렬화보다 약간 더 높은 성능을 낸다는 것을 알 수 있다:

![[fig_12_15.png]]
*그림 12.15 — A2C와 (그래디언트 병렬) A3C의 보상(왼쪽)과 속도(오른쪽) 비교*

---

## 7. 요약

이 챕터에서 우리는:
1. **분산(variance)** 이 정책 경사 방법의 학습 안정성에 어떤 악영향을 미치는지, 그리고 **베이스라인**이 왜 이를 완화하는지 이론과 CartPole 실험으로 확인했다.
2. 베이스라인을 상태별로 정교화한 **어드밴티지** $A(s,a) = Q(s,a) - V(s)$ 개념을 배우고, 이를 계산하는 크리틱(가치) 신경망과 행동을 고르는 액터(정책) 신경망을 결합한 **A2C(어드밴티지 액터-크리틱)** 를 배웠다.
3. A2C를 Pong 환경에 적용해, 11장의 정책 경사 방법보다 훨씬 안정적인 수렴을 얻어냈다. 엔트로피 보너스와 그래디언트 클리핑 같은 실전 안정화 기법도 함께 익혔다.
4. 왜 정책 경사 방법이 여러 병렬 환경을 필요로 하는지(온폴리시 특성 때문에 리플레이 버퍼를 못 쓰기 때문) 이해하고, 이를 진짜 병렬로 구현하는 두 가지 방식 — **데이터 병렬**과 **그래디언트 병렬** — 로 A3C를 구현하며 비교했다.

이렇게 결합한 액터-크리틱 방법은 딥 RL에서 가장 널리 쓰이는 방법 중 하나이며, 다음 두 챕터에서 정책 경사 방법으로 풀 수 있는 실전 문제들을 살펴보며 정책 경사 방법 파트를 마무리한다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[정책 경사와 베이스라인]]
- [[액터-크리틱과 어드밴티지]]
- [[A2C와 A3C]]
- [[상관관계와 표본 효율성]]
- [[동기·비동기 병렬화(데이터·그래디언트 병렬)]]
- [[그래디언트 클리핑]]
- [[듀얼링 DQN Dueling Architecture]]
- [[IID 독립항등분포]]
- [[소프트맥스 Softmax]]
- [[우선순위 경험 리플레이]]

## 한눈에 보는 개념 지도
| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 베이스라인 | $b$ | 정책 경사 스케일에서 빼주는 기준값(분산 감소용) |
| 상태 가치 | $V(s)$ | 그 상태에서 기대되는 평균 리턴(크리틱이 예측) |
| 어드밴티지 | $A(s,a)$ | $Q(s,a)-V(s)$, 평균 대비 이 행동이 얼마나 나은가 |
| 액터 | — | 행동 확률 $\pi(a\mid s)$를 출력하는 정책 신경망 |
| 크리틱 | — | 상태 가치 $V(s)$를 출력하는 가치 신경망 |
| 엔트로피 보너스 | $\mathcal{L}_H$ | 정책이 너무 확신에 차지 않도록(탐험 유지) 손실에 더하는 항 |
| 그래디언트 클리핑 | — | 그래디언트 L2 노름이 임계값 넘으면 방향 유지한 채 크기만 축소 |
| 데이터 병렬 | — | 자식은 데이터만 모으고, 손실·그래디언트 계산은 중앙이 담당 |
| 그래디언트 병렬 | — | 자식이 손실·그래디언트까지 계산해 중앙은 합산만 담당 |
