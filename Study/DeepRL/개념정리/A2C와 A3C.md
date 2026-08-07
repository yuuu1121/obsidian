---
title: "A2C와 A3C (Advantage Actor-Critic, Asynchronous Advantage Actor-Critic)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
tags: [DeepRL, 개념정리, A2C, A3C, 액터크리틱]
---

# A2C와 A3C (Advantage Actor-Critic, Asynchronous Advantage Actor-Critic)

> [!abstract] 한 줄 요약
> **A2C**는 [[액터-크리틱과 어드밴티지]]의 아이디어를 실제 학습 알고리즘으로 정리한 것이고, **A3C**는 거기에 "여러 환경을 동시에(비동기로) 굴려서 데이터를 더 다양하게 모은다"는 병렬화를 더한 버전이다.

## A2C 학습 절차

A2C(advantage actor-critic)의 훈련 루프는 다음과 같이 진행된다:

1. 신경망 파라미터 $\theta$를 무작위 값으로 초기화한다.
2. 현재 정책 $\pi_\theta$로 환경에서 $N$스텝을 진행하며, 상태 $s_t$·행동 $a_t$·보상 $r_t$를 저장한다.
3. 에피소드가 끝났으면 $R \leftarrow 0$, 아니면 $R \leftarrow V_\theta(s_t)$로 설정한다.
4. $i = t-1 \ldots t_{start}$ 순서로(뒤에서부터 거꾸로) 다음을 반복한다:
   - $R \leftarrow r_i + \gamma R$
   - 정책 그래디언트 누적: $\partial\theta_\pi \leftarrow \partial\theta_\pi + \nabla_\theta \log \pi_\theta(a_i|s_i)(R - V_\theta(s_i))$
   - 가치 그래디언트 누적: $\partial\theta_v \leftarrow \partial\theta_v + \dfrac{\partial(R - V_\theta(s_i))^2}{\partial\theta_v}$
5. 누적된 그래디언트로 파라미터를 업데이트한다. 정책 그래디언트 방향으로는 **그대로**, 가치 그래디언트 방향으로는 **반대로**(손실을 줄이는 방향으로) 움직인다.
6. 수렴할 때까지 2번부터 반복한다.

여기서 $(R - V_\theta(s_i))$가 바로 [[액터-크리틱과 어드밴티지]]에서 배운 **어드밴티지**다 — 실제로 얻은 할인 보상 $R$에서, 크리틱이 예측한 상태 가치 $V_\theta(s_i)$를 뺀 값이다.

## 실전 추가 요소 — 엔트로피 보너스

위 알고리즘은 논문에 실리는 것과 비슷한 "뼈대"일 뿐이다. 실제로는 안정성을 높이기 위해 몇 가지가 더해지는데, 대표적인 것이 **엔트로피 보너스(entropy bonus)**다. 손실 함수에 다음 항을 추가한다:

$$\mathcal{L}_H = \beta \sum_i \pi_\theta(s_i) \log \pi_\theta(s_i)$$

이 함수는 정책의 확률 분포가 **균등(uniform)** 할 때 최솟값을 가진다. 이걸 손실에 더하면, 에이전트가 특정 행동에 너무 일찍 확신을 가지지 않도록(즉 계속 여러 행동을 탐험하도록) 밀어준다. $\beta$는 이 보너스의 크기를 조절하는 하이퍼파라미터로, 보통 상수로 두거나 학습이 진행되며 선형으로 줄인다.

최종 손실 함수는 **정책 손실 + 가치 손실 + 엔트로피 손실**, 세 요소를 합쳐서 만든다. 이때 부호에 주의해야 하는데, 정책 그래디언트는 "개선 방향"을 가리키지만 가치 손실과 엔트로피 손실은 (일반적인 손실 함수처럼) **최소화**해야 하는 값이기 때문이다.

## A2C가 이름에 "2"를 쓰는 이유

**A**dvantage **A**ctor-**C**ritic → A와 C가 각각 하나씩, 그리고 Advantage의 A까지 더해 "A"가 2개, "C"가 1개라서 **A2C**라고 줄여 부른다.

## A3C — 비동기(asynchronous) 확장

A2C는 안정성을 위해 **여러 환경을 동시에** 사용해 훈련 배치를 만드는 것이 좋다(왜 여러 환경이 필요한지는 [[상관관계와 표본 효율성]] 참고). 이렇게 여러 환경을 병렬로 다루는 A2C의 확장판을 **advantage asynchronous actor-critic**, 줄여서 **A3C**라고 부른다. RL 실무자들 사이에서 가장 널리 쓰이는 방법 중 하나다.

A3C를 구현하는 방식은 크게 두 가지다: [[동기·비동기 병렬화(데이터·그래디언트 병렬)]] 문서에서 자세히 다룬다.
1. **데이터 병렬(data parallelism)**: 여러 프로세스가 각자 환경과 통신해 데이터(transition)만 모으고, 손실 계산·업데이트는 중앙에서 한 번에 한다.
2. **그래디언트 병렬(gradient parallelism)**: 여러 프로세스가 각자 손실 계산과 그래디언트 계산까지 끝내고, 그래디언트만 중앙으로 보내 합산·업데이트한다.

## 세 줄 정리
- A2C는 액터(정책)와 크리틱(가치)을 결합해, 어드밴티지($R - V(s)$)를 스케일로 삼아 정책 경사를 계산하는 알고리즘이다.
- 실전에서는 엔트로피 보너스를 더해 탐험을 유지하고, 그래디언트 클리핑으로 학습을 안정시킨다.
- A3C는 A2C에 "여러 환경을 병렬로 굴려 데이터를 다양하게 모은다"는 비동기 실행을 더한 버전이다.
