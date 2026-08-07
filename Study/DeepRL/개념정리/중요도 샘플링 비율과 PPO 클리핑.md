---
title: "개념정리 — 중요도 샘플링 비율과 PPO 클리핑 (Importance Sampling Ratio & PPO Clipping)"
tags: [개념정리, DeepRL, 강화학습, 정책경사, PPO]
related: [[Chapter 16 - 신뢰 영역 방법 TRPO와 PPO]]
---

# 중요도 샘플링 비율과 PPO 클리핑 (Importance Sampling Ratio & PPO Clipping)

> [!abstract] 한 줄 요약
> **중요도 샘플링 비율** $r_t(\theta)$는 "새 정책이 이 행동을 옛 정책보다 얼마나 더(또는 덜) 선호하는가"를 나타내는 배수이고, **PPO 클리핑**은 이 배수가 너무 커지지 않도록 $[1-\epsilon, 1+\epsilon]$ 범위 밖으로 못 나가게 잘라버리는 안전장치다.

## 1. 중요도 샘플링이란? — 다른 사람 경험으로 내 기댓값 추정하기

**중요도 샘플링(importance sampling)**은 원래 통계학 개념으로, *"분포 $Q$에서 뽑은 샘플들을 가지고 분포 $P$에 대한 기댓값을 추정하고 싶을 때"* 쓰는 트릭이다. 각 샘플에 $\frac{P(x)}{Q(x)}$라는 **보정 가중치**를 곱해주면 된다.

> [!tip] 비유 — 다른 반 시험 점수로 우리 반 평균 추정하기
> 옆 반(정책 $Q$, 즉 옛 정책) 학생들의 시험 점수 데이터만 있는데, 우리 반(정책 $P$, 즉 새 정책)의 평균 점수를 추정하고 싶다고 하자. 옆 반과 우리 반의 학생 구성(성적 분포)이 다르다면, 그냥 옆 반 평균을 쓰면 틀린다. 대신 "이 점수대 학생이 우리 반에는 얼마나 더 많이/적게 있는가"라는 **비율**을 각 점수에 곱해서 보정하면, 옆 반 데이터만으로도 우리 반 평균을 (근사적으로) 추정할 수 있다.

## 2. RL에서의 정의 — 새 정책 / 옛 정책

PPO에서는 같은 궤적(trajectory) 데이터를 여러 에폭(epoch) 동안 재사용해서 학습한다(Chapter 16의 PPO_EPOCHES=10). 그런데 학습이 진행되면서 정책 $\pi_\theta$는 계속 바뀌고, 데이터를 수집했을 때의 정책 $\pi_{\theta_{old}}$와는 점점 달라진다. 이 **"데이터를 만든 정책"과 "지금 갱신 중인 정책"의 차이**를 보정하기 위해 비율을 정의한다.

$$r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{old}}(a_t \mid s_t)}$$

읽는 법: *"같은 상태 $s_t$에서 같은 행동 $a_t$를, 새 정책은 옛 정책보다 몇 배나 더(또는 덜) 선호하는가."*

- $r_t = 1$: 새 정책과 옛 정책이 이 행동을 똑같이 선호 (변화 없음)
- $r_t > 1$: 새 정책이 이 행동을 **더** 선호하게 됨
- $r_t < 1$: 새 정책이 이 행동을 **덜** 선호하게 됨

코드로는(로그 확률의 차이를 지수화 — $\log a - \log b = \log(a/b)$이므로):

```python
logprob_pi_v = model.calc_logprob(mu_v, net_act.logstd, actions_v)
ratio_v = torch.exp(logprob_pi_v - batch_old_logprob_v)   # = π_θ(a|s) / π_θold(a|s)
```

## 3. 왜 클리핑이 필요한가 — 보정값 폭주 방지

원래대로라면 목적함수에 $r_t(\theta) \cdot A_t$(어드밴티지로 가중)를 곱해서 그대로 최대화하면 된다. 하지만 이 방식은 [[교차 엔트로피 Cross-Entropy|Chapter 4의 크로스 엔트로피 방법]]에서 봤던 것과 같은 문제를 일으킬 수 있다: 만약 $r_t(\theta)$가 한없이 커지도록 내버려 두면, **딱 몇 개의 샘플이 통계치를 완전히 지배**해버려 학습이 한쪽으로 폭주할 수 있다.

> [!warning] 왜 위험한가?
> 어드밴티지 $A_t$가 큰 양수인 행동에 대해 $r_t(\theta)$를 계속 키우는 방향으로 그래디언트가 흐르면, 정책이 그 행동 하나에 극단적으로 쏠려버릴 수 있다. 이는 [[벨만 방정식 Bellman Equation|MDP]]가 요구하는 "적당히 탐험하며 골고루 개선"이라는 전제를 깨뜨린다.

그래서 PPO는 비율을 $[1-\epsilon, 1+\epsilon]$ 구간(보통 $\epsilon=0.2$, 즉 $[0.8, 1.2]$) 밖으로 못 나가게 **자르고(clip)**, 원래 값과 자른 값 중 **더 비관적인(작은) 쪽**을 취한다.

$$J_\theta^{clip} = \mathbb{E}_t\big[\min(r_t(\theta)A_t,\ \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)A_t)\big]$$

```python
ratio_v = torch.exp(logprob_pi_v - batch_old_logprob_v)
surr_obj_v = batch_adv_v * ratio_v                                  # 원래 목적함수 값
c_ratio_v = torch.clamp(ratio_v, 1.0 - PPO_EPS, 1.0 + PPO_EPS)       # 비율을 [0.8, 1.2]로 자름
clipped_surr_v = batch_adv_v * c_ratio_v                             # 잘린 목적함수 값
loss_policy_v = -torch.min(surr_obj_v, clipped_surr_v).mean()        # 더 비관적인 쪽 선택(부호 반전은 경사 상승→하강 변환용)
```

> [!important] `min`을 쓰는 이유 — "좋은 방향이면 적당히만 인정, 나쁜 방향이면 가감 없이 반영"
> - 어드밴티지 $A_t>0$(좋은 행동)일 때: 비율을 무한정 키워 보상받는 걸 막기 위해, 비율이 $1+\epsilon$을 넘으면 그 이상 커진 값은 무시(클리핑된 값이 더 작으므로 `min`이 그걸 선택).
> - 어드밴티지 $A_t<0$(나쁜 행동)일 때: 비율이 $1-\epsilon$ 아래로 떨어져도 클리핑하지 않고 원래 값을 그대로 반영해, "이 행동은 확실히 줄여라"라는 신호를 억누르지 않는다.
>
> 결과적으로 **한 번의 업데이트로 정책이 옛 정책에서 너무 멀리 벗어나는 것을 원천적으로 막는** 매우 단순하면서도 효과적인 안전장치가 된다.

## 4. TRPO의 KL 제약과 비교

TRPO는 같은 목적("정책이 너무 크게 안 바뀌게")을 [[KL 발산 Kullback-Leibler Divergence|KL 발산]] 제약 $D_{KL}(\pi_{\theta_{old}}, \pi_\theta) \le \delta$ 으로 명시적으로 걸고, 이를 만족시키기 위해 켤레 그래디언트(conjugate gradient)와 라인서치라는 복잡한 최적화를 수행한다. PPO는 이 복잡한 제약 최적화를, **비율을 그냥 잘라버리는(clip) 훨씬 단순한 방법**으로 대체한 것이다 — 그래서 PPO가 TRPO보다 구현이 훨씬 쉽다.

## 세 줄 정리
- 중요도 샘플링 비율 $r_t(\theta)=\pi_\theta(a|s)/\pi_{\theta_{old}}(a|s)$는 새 정책과 옛 정책이 같은 행동을 얼마나 다르게 선호하는지 나타낸다.
- PPO는 이 비율을 $[1-\epsilon, 1+\epsilon]$로 클리핑하고 원래 값과 클리핑 값 중 더 비관적인 쪽을 택해, 한 번의 업데이트가 정책을 너무 크게 바꾸지 못하게 막는다.
- 이는 TRPO의 복잡한 KL 제약·켤레 그래디언트 최적화를 훨씬 단순한 방식으로 대체한 것이다.
