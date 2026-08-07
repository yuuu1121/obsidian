---
title: "Chapter 5 — 표 기반 학습과 벨만 방정식 (Tabular Learning and the Bellman Equation)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 5
tags: [DeepRL, 강화학습, 벨만방정식, 가치반복, Q러닝, FrozenLake, MDP]
---

# Chapter 5 · 표 기반 학습과 벨만 방정식

> [!abstract] 이 챕터를 한 문장으로
> 상태의 가치 $V(s)$와 행동의 가치 $Q(s,a)$를 **재귀적으로 계산**하게 해 주는 **벨만 방정식**을 배우고, 이를 실제로 반복 계산하는 **가치 반복(value iteration)** 알고리즘으로 FrozenLake 환경을 (거의 즉시!) 풀어낸다. 이것이 다음 챕터의 주인공인 **딥 Q-러닝(Deep Q-Network)** 을 이해하기 위한 마지막 준비 단계다.

---

## 들어가며 — 왜 이 챕터가 필요한가?

지난 챕터(교차 엔트로피 방법)에서 우리는 첫 RL 알고리즘을 만나봤다. 신경망이 상태를 보고 행동의 확률을 뱉어내게 하고, "성적이 좋았던 에피소드만 골라서" 그 행동들을 더 자주 하도록 학습시키는 방식이었다. 꽤 그럴듯하게 작동했지만, **하나의 완전한 에피소드가 끝나야만** 학습할 수 있었고, FrozenLake 같은 확률적(미끄러지는) 환경에서는 시간이 오래 걸렸다.

이 챕터에서는 훨씬 더 유연하고 강력한 방법론의 뿌리, 즉 **Q-러닝(Q-learning)** 계열 방법들이 공유하는 **이론적 배경**을 세운다. 그 배경의 핵심이 바로 **벨만 방정식(Bellman equation)** 이다. 이 챕터가 다루는 것은 다음 네 가지다:

1. 상태의 가치와 행동의 가치를 복습하고, 간단한 경우에 손으로 계산해 본다.
2. 벨만 방정식이 무엇이고, 상태들의 가치를 알면 왜 최적 정책을 알 수 있는지 이야기한다.
3. 가치 반복(value iteration) 방법을 배우고 FrozenLake에 적용해 본다.
4. 같은 것을 Q-값 버전(Q-iteration)으로도 해 본다.

이 챕터의 환경들은 단순하지만, 여기서 다지는 기초는 다음 챕터의 **딥 Q-러닝**으로 곧장 이어진다.

---

## 1. 가치, 상태, 최적성 (Value, State, and Optimality)

### 1.1 상태의 가치, 다시 보기

[[상태 관측 에피소드 정책]]에서 이미 상태의 가치 개념을 다뤘다. 이 책 전체(특히 이 부분)는 **"상태의 가치를 어떻게 근사할 것인가"** 를 중심으로 돌아간다고 해도 과언이 아니다. 공식으로 다시 쓰면:

$$V(s) = \mathbb{E}\left[\sum_{t=0}^{\infty} r_t \gamma^t\right]$$

여기서 $r_t$는 에피소드의 $t$ 스텝에서 얻는 **국소적인(local)** 보상이다. 즉, *"상태 $s$에서 시작해서 앞으로 받을 모든 보상을, 미래로 갈수록 $\gamma$(할인율)를 거듭제곱해 깎아가며 다 더한 값의 평균(기댓값)"* 이 상태의 가치다. 이 총 보상은 $0 < \gamma < 1$로 할인할 수도 있고, $\gamma=1$이라서 할인하지 않을 수도 있다 — 어떻게 정의할지는 우리 마음이다.

> [!note] 가치는 항상 "어떤 정책 아래"에서 계산된다
> 가치는 **정책(policy)** 없이는 정의될 수 없다. 에이전트가 어떻게 행동하느냐에 따라 같은 상태라도 가치가 완전히 달라지기 때문이다.

### 1.2 세 상태짜리 장난감 환경

이 말을 구체적으로 보여주기 위해, 그림 5.1처럼 아주 단순한 3상태 환경을 생각해 보자.

![[fig_5_1.png]]
*그림 5.1 — 보상이 붙은 상태 전이를 보여주는 간단한 환경의 예*

- 상태 $S=1$: 에이전트의 시작 상태
- 상태 $S=2$: "right"(오른쪽) 행동을 했을 때 도달하는 종료 상태. 보상은 1.
- 상태 $S=3$: "down"(아래) 행동을 했을 때 도달하는 종료 상태. 보상은 2.

이 환경은 **완전히 결정론적**이다 — 모든 행동이 100% 성공하고, 항상 상태 1에서 시작한다. 상태 2나 3에 도달하면 에피소드가 끝난다. 이제 질문: **상태 1의 가치는 얼마인가?**

이 질문은 에이전트의 행동 방식, 즉 **정책**을 모르면 답할 수 없다. 몇 가지 정책을 예로 들어 값을 직접 계산해 보자.

- 항상 오른쪽으로 가는 에이전트: 가치 = **1.0** (매번 1을 얻고 끝난다)
- 항상 아래로 가는 에이전트: 가치 = **2.0**
- 50% 확률로 오른쪽, 50% 확률로 아래로 가는 에이전트: $1.0 \cdot 0.5 + 2.0 \cdot 0.5 = $ **1.5**
- 10% 확률로 오른쪽, 90% 확률로 아래로 가는 에이전트: $1.0 \cdot 0.1 + 2.0 \cdot 0.9 = $ **1.9**

RL의 목표는 총 보상을 최대한 많이 얻는 것이므로, 이 1스텝짜리 환경에서는 총 보상이 곧 상태 1의 가치이고, 이 값을 최대화하는 것은 분명히 **정책 2(항상 아래로)** 다.

> [!note] "무조건 보상이 큰 행동을 택하면 되는 것 아닌가?"
> 이런 단순한 환경에서는 최적 정책이 뻔해 보인다. 하지만 실제로는 그렇게 간단하지 않다. 이걸 보여주기 위해 환경을 조금 확장해 보자.

### 1.3 함정이 있는 환경 — 눈앞의 이득만 보면 안 되는 이유

상태 3에서 그대로 끝나는 대신, 상태 3에서 상태 4로 가는 전이를 하나 추가한다고 하자. 이 전이의 보상은 **−20**이다.

![[fig_5_2.png]]
*그림 5.2 — 같은 환경에 상태 하나가 추가된 모습*

상태 1에서 일단 "아래로" 행동을 선택하면, 상태 3에서는 상태 4로 가는 길밖에 없다. 즉 **한 번 아래로 내려가면 −20의 나쁜 보상을 피할 수 없는 함정**이 기다리고 있다. 이 새 환경에서 값을 다시 계산해 보면:

- 항상 오른쪽: 그대로 **1.0**
- 항상 아래로: $2.0 + (-20) = $ **−18**
- 50%/50%: $0.5 \cdot 1.0 + 0.5 \cdot (2.0 + (-20)) = $ **−8.5**
- 10%/90%: $0.1 \cdot 1.0 + 0.9 \cdot (2.0+(-20)) = $ **−16.1**

이제 최선의 정책은 **정책 1(항상 오른쪽)** 로 완전히 뒤바뀐다! "당장 보상이 큰 쪽(아래, 보상 2)"을 무작정 택했다가는 나중에 큰 손해(−20)를 보는 함정에 빠진 것이다.

> [!important] 이 예시가 말해주는 것
> 순진하고 사소한 환경으로 시간을 들인 이유는, **최적성 문제가 얼마나 복잡할 수 있는지** 체감하기 위해서다. 이 복잡함을 수학적으로 깔끔하게 풀어낸 사람이 미국의 수학자 **리처드 벨만(Richard Bellman)** 이며, 그가 정립하고 증명한 것이 바로 **벨만 방정식**이다.

---

## 2. 벨만 최적 방정식 (The Bellman Equation of Optimality)

벨만 방정식을 설명하려면 조금 추상적으로 접근하는 편이 낫다. 겁먹지 말 것 — 뒤에 구체적인 예시가 이어진다! 자세한 유도와 비유는 [[벨만 방정식 Bellman Equation]] 노트에 정리했다. 여기서는 핵심만 짚는다.

### 2.1 결정론적인 경우

모든 행동이 100% 확실한 결과로 이어지는 결정론적인 경우부터 시작하자. 에이전트가 상태 $s_0$에 있고 $N$개의 행동을 선택할 수 있으며, 각 행동은 각자 다른 상태 $s_1 \dots s_N$으로, 각각 보상 $r_1 \dots r_N$과 함께 이어진다고 하자. 그리고 $s_0$과 연결된 모든 상태의 가치 $V_i$를 이미 알고 있다고 가정하자. 이때 $s_0$에서 최선의 행동은 무엇일까?

![[fig_5_3.png]]
*그림 5.3 — 초기 상태에서 도달 가능한 N개의 상태를 가진 추상적인 환경*

특정 행동 $a_i$를 골랐을 때 얻는 가치는 $V_0(a=a_i) = r_i + V_i$다. 최선의 행동을 고르려면, **모든 행동에 대해 이 값을 계산하고 그중 최댓값**을 택하면 된다:

$$V_0 = \max_{a \in 1 \dots N}(r_a + V_a)$$

할인율 $\gamma$까지 고려하면, 다음 상태의 가치에도 $\gamma$를 곱해야 한다:

$$V_0 = \max_{a \in 1 \dots N}(r_a + \gamma V_a)$$

이는 앞서 본 "탐욕적으로 보상 큰 쪽만 고르는" 방식과 비슷해 보이지만 결정적인 차이가 있다: **즉시 보상만 보는 게 아니라, 즉시 보상 + 그 뒤의 장기적 가치를 함께 본다.** 그래서 즉시 보상은 크지만 그 이후 가치가 나쁜 함정(앞서 본 −20 사례처럼)을 피할 수 있다.

벨만이 증명한 것은, **이 방식을 따르면 우리 행동이 최적의 결과를 낸다**는 것이다. 그래서 이 식을 (결정론적 경우의) **가치의 벨만 방정식**이라 부른다.

### 2.2 확률적인 경우

이제 행동의 결과가 여러 상태 중 하나로 확률적으로 정해지는 경우로 확장하자. 상태 $s_0$에서 행동 하나를 선택했을 때, 세 가지 다른 결과로 이어질 수 있다고 하자.

![[fig_5_4.png]]
*그림 5.4 — 확률적인 경우, 어떤 상태에서의 전이를 보여주는 예*

행동 1을 선택하면, 확률 $p_1$로 상태 $s_1$에, 확률 $p_2$로 $s_2$에, 확률 $p_3$으로 $s_3$에 도달한다($p_1+p_2+p_3=1$). 각 목적지 상태는 각자의 보상 $r_1, r_2, r_3$을 가진다. 행동 1의 기대 가치를 구하려면, **모든 값을 각자의 확률로 가중해서 더해야** 한다:

$$V_0(a=1) = p_1(r_1 + \gamma V_1) + p_2(r_2+\gamma V_2) + p_3(r_3+\gamma V_3)$$

또는 더 형식적으로:

$$V_0(a) = \mathbb{E}_{s \sim S}[r_{s,a} + \gamma V_s] = \sum_{s \in S} p_{a,0\to s}(r_{s,a}+\gamma V_s)$$

여기서 $\mathbb{E}_{s\sim S}$는 상태 공간 $S$ 전체에 대한 기댓값을 취한다는 뜻이다([[기댓값 Expectation]] 참고).

결정론적인 경우의 벨만 방정식(최댓값 취하기)과 확률적 행동의 가치(기댓값 취하기)를 결합하면, 일반적인 경우의 **벨만 최적 방정식**이 완성된다:

$$V_0 = \max_{a \in A} \mathbb{E}_{s \sim S}[r_{s,a}+\gamma V_s] = \max_{a\in A}\sum_{s\in S}p_{a,0\to s}(r_{s,a}+\gamma V_s)$$

여기서 $p_{a,i\to j}$는 *"상태 $i$에서 행동 $a$를 했을 때 상태 $j$에 도달할 확률"* 을 뜻한다.

> [!important] 해석은 동일하다
> 상태의 최적 가치는, **가능한 최대의 기대 즉시 보상 + 다음 상태의 할인된 장기 보상**을 주는 행동에 대응한다. 눈여겨볼 점은 이 정의가 **재귀적(recursive)** 이라는 것이다 — 어떤 상태의 가치는 바로 다음에 도달 가능한 상태들의 가치로 정의된다. 마치 "우리가 이미 정답을 안다고 치고" 정답을 정의하는 것처럼 보여 순환 논리처럼 느껴질 수 있다. 하지만 이는 컴퓨터과학·수학에서 매우 강력하고 흔한 기법이다(수학적 귀납법도 같은 트릭을 쓴다). 벨만 방정식은 RL뿐 아니라 훨씬 더 일반적인 **동적 계획법(dynamic programming)** 의 토대이기도 하다.

이 가치들은 최고의 보상을 알려줄 뿐 아니라, **사실상 최적 정책 그 자체**를 알려준다. 에이전트가 모든 상태의 가치를 알고 있다면, 각 상태에서 "즉시 보상 + 한 스텝 할인된 장기 가치"의 합이 최대인 행동을 고르기만 하면 되기 때문이다.

---

## 3. 행동의 가치 (The Value of the Action) — Q함수

이 값을 계산하는 실용적인 방법을 소개하기 전에, 편의를 위한 수학 표기를 하나 더 도입해야 한다. 상태의 가치만큼 근본적인 개념은 아니지만, 실전에서는 오히려 더 자주 쓰인다.

**행동의 가치**, 즉 $Q(s,a)$는 상태 $s$에서 행동 $a$를 실행해서 얻을 수 있는 총 보상으로 정의되며, $V(s)$를 이용해 다음처럼 정의할 수 있다:

$$Q(s,a) = \mathbb{E}_{s'\sim S}[r(s,a)+\gamma V(s')] = \sum_{s'\in S}p_{a,s\to s'}(r(s,a)+\gamma V(s'))$$

$Q$는 상태 $s$와 행동 $a$에 대해, **즉시 보상 + 도착한 상태의 할인된 장기 보상의 기댓값**과 같다. 이 값들에 특별히 이름을 붙인 이유가 있는데, 바로 이 $Q$값을 중심으로 삼는 방법들의 집합을 통틀어 **Q-러닝(Q-learning)** 이라 부르기 때문이다. 이 방법들에서 우리의 주된 목표는 상태-행동 쌍마다 $Q$값을 구하는 것이다.

$V(s)$도 $Q(s,a)$로 정의할 수 있다:

$$V(s) = \max_{a\in A} Q(s,a)$$

말로 풀면: *"어떤 상태의 가치는, 그 상태에서 취할 수 있는 행동들 중 가치가 가장 큰 행동의 가치와 같다."*

마지막으로 $Q(s,a)$ 자신을 재귀적으로도 표현할 수 있다(6장에서 쓰인다):

$$Q(s,a) = r(s,a) + \gamma \max_{a'} Q(s',a')$$

> [!note] 보상의 인덱스에 대한 미묘한 차이
> 위 식에서 즉시 보상의 인덱스 $(s,a)$는 환경의 세부 사항에 따라 달라진다. 행동 $a$를 실행한 직후 보상이 주어지면 위 식 그대로 쓰면 되고, 만약 어떤 상태 $s'$에 행동 $a'$로 "도착"할 때 보상이 주어진다면 인덱스가 $(s',a')$로 옮겨져 $\max$ 연산 안으로 들어가야 한다: $Q(s,a) = \max_{a'}(r(s',a') + \gamma Q(s',a'))$. 수학적으로 큰 차이는 아니지만, 실제 구현 시에는 중요할 수 있다. 이 책에서는 앞의(더 흔한) 형태를 사용한다.

### 3.1 손으로 계산해 보기 — 그리드형 환경

이제 배운 것을 FrozenLake와 비슷하지만 더 단순한 환경에 적용해 보자. 초기 상태 $s_0$가 중앙에 있고, 그 주위를 네 개의 종료 상태 $s_1, s_2, s_3, s_4$가 둘러싼 구조다.

![[fig_5_5.png]]
*그림 5.5 — 단순화된 그리드형 환경. $s_0$가 초기 상태, $s_1$–$s_4$가 종료 상태다.*

FrozenLake와 똑같은 방식으로, 모든 행동은 확률적이다: 목표한 칸으로 33% 확률로 이동하고, 33% 확률로 왼쪽으로 미끄러지며, 33% 확률로 오른쪽으로 미끄러진다. 간단히 하기 위해 여기서는 할인율 $\gamma=1$을 쓴다.

![[fig_5_6.png]]
*그림 5.6 — 그리드 환경의 전이 다이어그램. 각 화살표에 확률(0.33)이 표시되어 있다.*

먼저 종료 상태들의 가치부터 계산하자. $s_1 \dots s_4$는 나가는 전이가 없으므로($Q$가 모든 행동에 대해 0), 그 가치는 그냥 도착 시 받는 즉시 보상과 같다: $V_1=1, V_2=2, V_3=3, V_4=4$.

이제 $s_0$의 행동 가치들을 계산해 보자. "up"(위) 행동부터 시작한다. 정의에 따르면, 이 값은 **즉시 보상 + 다음 스텝의 장기 가치의 기댓값**과 같다. "up" 행동에는 그 이후로 이어지는 전이가 없으므로(한 스텝이면 끝):

$$Q(s_0,\text{up}) = 0.33 \cdot V_1 + 0.33 \cdot V_2 + 0.33\cdot V_4 = 0.33\cdot 1 + 0.33\cdot 2 + 0.33 \cdot 4 = 2.31$$

같은 식으로 나머지 행동들도 계산하면:

$$Q(s_0,\text{left}) = 0.33V_1+0.33V_2+0.33V_3 = 1.98$$
$$Q(s_0,\text{right}) = 0.33V_4+0.33V_1+0.33V_3 = 2.64$$
$$Q(s_0,\text{down}) = 0.33V_3+0.33V_2+0.33V_4 = 2.97$$

$s_0$의 최종 가치는 이 행동 가치들 중 최댓값이므로 **2.97** ("down"이 최선의 행동).

> [!tip] Q값이 실전에서 더 편리한 이유
> V값보다 Q값이 훨씬 다루기 편하다. 에이전트가 행동을 결정할 땐, 현재 상태에서 가능한 모든 행동의 $Q$를 계산해서 그중 최댓값을 고르면 끝이다([[탐욕적 정책 Greedy Policy]]). 반면 $V$값만으로 같은 결정을 하려면, 가치뿐 아니라 **전이 확률까지** 알아야 한다. 실전에서는 전이 확률을 미리 알 수 없는 경우가 대부분이라, 에이전트가 직접 확률을 추정해야 한다. 이 챕터 뒤에서 FrozenLake를 양쪽 방식(V와 Q) 모두로 풀어 보며 이 차이를 직접 확인한다. 하지만 아직 하나가 빠져 있다 — $V_i$와 $Q_i$를 **일반적으로** 계산하는 방법이다.

---

## 4. 가치 반복 방법 (The Value Iteration Method)

앞의 단순한 예시에서는 환경의 구조를 이용했다 — 전이에 루프가 없어서, 종료 상태부터 값을 계산해 중심으로 진행할 수 있었다. 하지만 환경에 **루프(순환) 단 하나만 있어도** 이 접근법은 막힌다. 두 상태로 이뤄진 다음 환경을 보자.

![[fig_5_7.png]]
*그림 5.7 — 전이 다이어그램에 루프가 있는 샘플 환경*

$s_1$에서 시작해서, 유일한 행동으로 $s_2$에 가면 보상 $r=1$을 받는다. $s_2$에서 유일한 전이는 다시 $s_1$로 돌아오는 것으로, 보상은 $r=2$다. 그래서 에이전트의 삶은 $[s_1, s_2, s_1, s_2, \dots]$로 무한히 반복되는 시퀀스다. 이 무한 루프를 다루기 위해 할인율 $\gamma=0.9$를 쓴다. 두 상태의 가치는 각각 다음 무한급수로 주어진다:

$$V(s_1) = 1+\gamma(2+\gamma(1+\gamma(2+\dots))) = \sum_{i=0}^{\infty} 1\gamma^{2i}+2\gamma^{2i+1}$$
$$V(s_2) = 2+\gamma(1+\gamma(2+\gamma(1+\dots))) = \sum_{i=0}^{\infty} 2\gamma^{2i}+1\gamma^{2i+1}$$

엄밀히 말하면 정확한 값을 계산할 수는 없지만(무한합이니까), $\gamma=0.9$에서는 각 전이의 기여도가 시간이 지날수록 빠르게 줄어든다. 예를 들어 10스텝 뒤엔 $\gamma^{10}=0.9^{10}\approx0.349$지만, 100스텝 뒤엔 겨우 $0.0000266$이다. 그래서 **50번 정도만 반복해도 꽤 정확한 추정치**를 얻을 수 있다:

```python
>>> sum([0.9**(2*i) + 2*(0.9**(2*i+1)) for i in range(50)])
14.736450674121663
>>> sum([2*(0.9**(2*i)) + 0.9**(2*i+1) for i in range(50)])
15.262752483911719
```

### 4.1 알고리즘 절차

앞의 예시는 **가치 반복(value iteration)** 이라는 더 일반적인 절차의 감을 잡게 해 준다. 이는 전이 확률과 보상을 알고 있는 [[마르코프 성질과 마르코프 체인|마르코프 결정 과정(MDP)]]의 상태·행동 가치를 **수치적으로** 계산할 수 있게 해 준다. 자세한 원리와 비유는 [[가치 반복 Value Iteration]] 노트를 참고. 절차는 다음과 같다(상태의 가치 기준):

1. 모든 상태의 가치 $V_i$를 초기값(보통 0)으로 초기화한다.
2. MDP의 모든 상태 $s$에 대해, 벨만 업데이트를 수행한다:
   $$V_s \leftarrow \max_a \sum_{s'}p_{a,s\to s'}(r_{s,a,s'}+\gamma V_{s'})$$
3. 충분히 많은 횟수, 또는 변화량이 충분히 작아질 때까지 2번을 반복한다.

### 4.2 실전에서의 두 가지 한계

이론은 이렇지만, 실전에는 명백한 한계가 두 가지 있다.

**첫 번째**: 상태 공간이 **이산적이고 충분히 작아야** 모든 상태를 여러 번 순회할 수 있다. FrozenLake-4x4나 FrozenLake-8x8(Gym에 더 어려운 버전으로 존재)에는 문제가 없지만, CartPole처럼 관측값이 4개의 float(실수)로 이뤄진 경우엔 어떻게 해야 할지 명확하지 않다. 이런 경우 잠재적인 해법 하나는 관측 공간을 **구간(bin)으로 나눠 이산화**하는 것이지만, 구간을 얼마나 크게 나눠야 할지, 각 구간을 추정하는 데 데이터가 얼마나 필요할지 등 실전적인 문제가 잔뜩 생긴다. 이 문제는 이후 챕터에서 신경망을 Q-러닝에 활용하며 다룬다.

**두 번째**: 대부분의 경우 **전이 확률과 보상 행렬을 미리 알지 못한다.** Gym이 에이전트 작성자에게 제공하는 인터페이스를 떠올려 보자 — 상태를 관측하고, 행동을 결정하고, 그 후에야 다음 관측과 보상을 받는다. 상태 $s_0$에서 행동 $a_0$을 실행했을 때 상태 $s_1$로 갈 확률이 얼마인지는 (Gym 환경 코드를 직접 들여다보지 않는 한) 알 수 없다. 우리가 가진 것은 그저 에이전트가 환경과 상호작용한 **이력(history)** 뿐이다. 그래서 자연스러운 해법은, **에이전트의 경험을 두 미지수(확률·보상) 모두의 추정치로 사용**하는 것이다. 보상은 그대로 쓰면 되고, 확률을 추정하려면 모든 튜플 $(s_0, s_1, a)$에 대한 카운터를 유지하고 정규화하면 된다.

---

## 5. 가치 반복을 실전에 적용하기 — FrozenLake

이 절에서는 가치 반복 방법이 FrozenLake에서 실제로 어떻게 동작하는지 살펴본다. 전체 예제는 `Chapter05/01_frozenlake_v_iteration.py`에 있다. 이 예제의 핵심 자료구조는 다음 세 가지다.

- **보상 표(Reward table)**: "출발 상태 + 행동 + 도착 상태"를 합성 키로 갖는 딕셔너리. 값은 즉시 보상에서 얻는다.
- **전이 표(Transitions table)**: 경험한 전이의 횟수를 세는 딕셔너리. 키는 "상태 + 행동"이고, 값은 "도착 상태 → 관측 횟수"를 담은 또 다른 딕셔너리다. 예를 들어 상태 0에서 행동 1을 열 번 실행했는데 세 번은 상태 4로, 일곱 번은 상태 5로 갔다면, 키 `(0, 1)`의 값은 `{4: 3, 5: 7}`이라는 `dict`가 된다. 이 표로 우리 전이들의 확률을 추정할 수 있다.
- **가치 표(Value table)**: 상태를 그 상태의 계산된 가치로 매핑하는 딕셔너리.

전체 로직은 단순하다: 루프를 돌면서 환경에서 100번의 무작위 스텝을 플레이한다. 그 100 스텝 이후, 보상·전이 표 전체에 대해 가치 반복을 한 번 수행하며 가치 표를 업데이트한다. 그런 다음 업데이트된 가치 표를 정책 삼아 여러 번의 완전한 테스트 에피소드를 플레이해서 개선 여부를 확인한다. 그 테스트 에피소드들의 평균 보상이 0.8 경계선을 넘으면 학습을 멈춘다.

### 5.1 임포트와 상수, 타입 별칭

```python
import typing as tt
import gymnasium as gym
from collections import defaultdict, Counter
from torch.utils.tensorboard.writer import SummaryWriter

ENV_NAME = "FrozenLake-v1"
GAMMA = 0.9
TEST_EPISODES = 20
```

- `defaultdict`, `Counter` — [[defaultdict와 Counter]] 참고. 없는 키에 접근해도 자동으로 기본값을 채워주는 딕셔너리와, 개수를 세는 전용 딕셔너리다.
- `GAMMA = 0.9` — 이 챕터에서 쓸 할인율. 1보다 작게 잡아서 무한 루프가 있어도 값이 발산하지 않게 한다([[할인율 감마와 등비급수]]).
- `TEST_EPISODES = 20` — 정책 성능을 평가할 때마다 20개의 에피소드를 플레이해서 평균을 낸다.

FrozenLake 환경에서 관측 공간과 행동 공간은 모두 `Box` 클래스라서, 상태와 행동이 정수(`int`) 값으로 표현된다([[관측공간과 행동공간(Space)]] 참고). 이를 반영해 타입 별칭을 정의한다:

```python
State = int
Action = int
RewardKey = tt.Tuple[State, Action, State]
TransitKey = tt.Tuple[State, Action]
```

`RewardKey`는 (상태, 행동, 도착 상태) 세 개짜리 튜플, `TransitKey`는 (상태, 행동) 두 개짜리 튜플이다. 타입 힌트는 실제 동작에 영향을 주지 않지만, 코드를 읽는 사람(그리고 미래의 나 자신)이 각 딕셔너리의 키가 무엇을 뜻하는지 한눈에 알 수 있게 해 준다.

### 5.2 Agent 클래스 초기화

```python
class Agent:
    def __init__(self):
        self.env = gym.make(ENV_NAME)
        self.state, _ = self.env.reset()
        self.rewards: tt.Dict[RewardKey, float] = defaultdict(float)
        self.transits: tt.Dict[TransitKey, Counter] = defaultdict(Counter)
        self.values: tt.Dict[State, float] = defaultdict(float)
```

- `self.env = gym.make(ENV_NAME)` — 데이터를 수집할 환경 하나를 만든다.
- `self.state, _ = self.env.reset()` — 환경을 초기화하고 첫 상태를 저장한다.
- `self.rewards`, `self.transits`, `self.values` — 앞서 설명한 세 자료구조. 모두 `defaultdict`라서 처음 보는 키에 접근해도 알아서 `0.0`이나 빈 `Counter`가 채워진다.

### 5.3 무작위 스텝으로 경험 모으기

```python
def play_n_random_steps(self, n: int):
    for _ in range(n):
        action = self.env.action_space.sample()
        new_state, reward, is_done, is_trunc, _ = self.env.step(action)
        rw_key = (self.state, action, new_state)
        self.rewards[rw_key] = float(reward)
        tr_key = (self.state, action)
        self.transits[tr_key][new_state] += 1
        if is_done or is_trunc:
            self.state, _ = self.env.reset()
        else:
            self.state = new_state
```

- `self.env.action_space.sample()` — 행동을 **무작위로** 뽑는다. 이 단계는 순수한 **탐험(exploration)** 이다.
- `self.env.step(action)` — 그 행동을 실행하고 `(다음 상태, 보상, 종료 여부, 중단 여부, 부가정보)`를 받는다.
- `self.rewards[rw_key] = float(reward)` — (상태, 행동, 도착 상태) 조합에 대한 보상을 기록한다.
- `self.transits[tr_key][new_state] += 1` — (상태, 행동) 조합에서 이번에 도착한 상태의 카운트를 1 늘린다. 이렇게 쌓인 카운트들이 나중에 전이 확률 추정에 쓰인다.
- 에피소드가 끝났으면(`is_done`) 또는 중간에 강제 종료됐으면(`is_trunc`) 환경을 리셋하고, 아니라면 그냥 다음 상태로 넘어간다.

> [!tip] 가치 반복이 교차 엔트로피 방법과 다른 점
> 이 함수는 에피소드의 끝을 기다리지 않는다. 그냥 $n$ 스텝을 실행하고 결과만 기억하면 된다. 반면 교차 엔트로피 방법은 **완전한 에피소드**가 끝나야만 학습할 수 있었다. 이것이 가치 반복 계열 방법의 큰 장점 중 하나다.

### 5.4 행동 가치 계산하기 — calc_action_value

```python
def calc_action_value(self, state: State, action: Action) -> float:
    target_counts = self.transits[(state, action)]
    total = sum(target_counts.values())
    action_value = 0.0
    for tgt_state, count in target_counts.items():
        rw_key = (state, action, tgt_state)
        reward = self.rewards[rw_key]
        val = reward + GAMMA * self.values[tgt_state]
        action_value += (count / total) * val
    return action_value
```

이 함수는 주어진 (상태, 행동) 쌍의 가치, 즉 $Q(s,a)$를 벨만 방정식으로 계산한다. 다음 그림이 이 계산 로직을 보여준다.

![[fig_5_8.png]]
*그림 5.8 — 상태의 가치를 계산하는 과정. 전이 카운트 $c_1, c_2$의 비율로 확률을 근사하고, 이를 각 도착 상태의 (보상 + 할인된 가치)에 곱해서 더한다.*

- `target_counts = self.transits[(state, action)]` — 이 (상태, 행동)에서 각 도착 상태로 몇 번씩 갔는지를 담은 `Counter`를 가져온다. 예: `{s1: c1, s2: c2}`.
- `total = sum(target_counts.values())` — 이 (상태, 행동)을 실행한 **총 횟수**($c_1+c_2$). 나중에 개별 카운트를 나눠서 확률로 바꾸는 데 쓴다.
- 각 도착 상태 `tgt_state`마다:
  - `reward = self.rewards[rw_key]` — 그 전이에서 실제로 받았던 보상.
  - `val = reward + GAMMA * self.values[tgt_state]` — **벨만 방정식**의 핵심: "즉시 보상 + 할인된 다음 상태 가치". `self.values[tgt_state]`는 아직 계산 전이면 `defaultdict` 덕분에 자동으로 0이다.
  - `action_value += (count / total) * val` — `count / total`이 이 도착 상태로 갈 **확률의 추정치**다. 이 확률을 가중치 삼아 `val`을 더한다. 이것이 벨만 방정식의 $\sum_{s'} p_{a,s\to s'}(r_{s,a,s'}+\gamma V_{s'})$ 부분을 그대로 구현한 것이다.
- 반환값 `action_value`가 곧 $Q(s,a)$의 근사값이다.

### 5.5 최선의 행동 고르기 — select_action

```python
def select_action(self, state: State) -> Action:
    best_action, best_value = None, None
    for action in range(self.env.action_space.n):
        action_value = self.calc_action_value(state, action)
        if best_value is None or best_value < action_value:
            best_value = action_value
            best_action = action
    return best_action
```

방금 만든 함수를 이용해, 주어진 상태에서 취할 **최선의 행동**을 결정한다. 가능한 모든 행동에 대해 `calc_action_value`로 가치를 계산해 보고, 그중 가장 큰 값을 주는 행동을 고른다. 이 선택 과정은 완전히 결정론적이다(무작위성이 없다) — 탐험은 이미 `play_n_random_steps()`에서 담당하므로, 여기서는 지금까지 배운 가치 추정치에 대해 순수하게 **탐욕적으로**([[탐욕적 정책 Greedy Policy]]) 행동한다.

### 5.6 한 에피소드 플레이하기 — play_episode

```python
def play_episode(self, env: gym.Env) -> float:
    total_reward = 0.0
    state, _ = env.reset()
    while True:
        action = self.select_action(state)
        new_state, reward, is_done, is_trunc, _ = env.step(action)
        rw_key = (state, action, new_state)
        self.rewards[rw_key] = float(reward)
        tr_key = (state, action)
        self.transits[tr_key][new_state] += 1
        total_reward += reward
        if is_done or is_trunc:
            break
        state = new_state
    return total_reward
```

`select_action()`으로 최선의 행동을 찾아, 주어진 환경에서 **한 에피소드 전체**를 플레이하는 함수다. 테스트용 에피소드를 플레이할 때 쓰이는데, 학습에 쓰는 메인 환경의 현재 상태를 건드리고 싶지 않기 때문에 **별도의 두 번째 환경**을 인자로 받는다. 로직은 단순하다 — 상태를 계속 따라가며 보상을 누적할 뿐이다. 눈여겨볼 점은, 테스트 에피소드를 플레이하는 동안에도 `self.rewards`와 `self.transits`를 계속 갱신한다는 것이다. 즉 **테스트 중에 얻은 데이터도 그냥 버리지 않고 활용**한다.

### 5.7 가치 반복 자체 — value_iteration

```python
def value_iteration(self):
    for state in range(self.env.observation_space.n):
        state_values = [
            self.calc_action_value(state, action)
            for action in range(self.env.action_space.n)
        ]
        self.values[state] = max(state_values)
```

Agent 클래스의 마지막 메서드이자, 이 챕터의 핵심인 **가치 반복** 구현이다. 이미 만들어 둔 함수들 덕분에 놀랍도록 간단하다. 환경의 모든 상태를 순회하면서, 그 상태에서 가능한 모든 행동의 가치를 계산해 후보 목록을 만들고, **그 후보들 중 최댓값**으로 현재 상태의 가치를 업데이트한다. 정확히 앞서 정의한 벨만 업데이트 $V_s \leftarrow \max_a \sum_{s'}p_{a,s\to s'}(r_{s,a,s'}+\gamma V_{s'})$ 그대로다.

### 5.8 학습 루프

```python
if __name__ == "__main__":
    test_env = gym.make(ENV_NAME)
    agent = Agent()
    writer = SummaryWriter(comment="-v-iteration")

    iter_no = 0
    best_reward = 0.0
    while True:
        iter_no += 1
        agent.play_n_random_steps(100)
        agent.value_iteration()
```

- `test_env` — 테스트 에피소드 전용 별도 환경. `agent.env`(학습용 데이터 수집 환경)와는 분리되어 있다.
- `writer = SummaryWriter(...)` — TensorBoard에 학습 곡선을 기록하기 위한 도구.
- 루프의 핵심 두 줄: **먼저 100번의 무작위 스텝**으로 보상·전이 표를 새 데이터로 채우고, **그다음 모든 상태에 대해 가치 반복을 한 번 수행**한다. 이 두 단계가 계속 반복된다.

```python
        reward = 0.0
        for _ in range(TEST_EPISODES):
            reward += agent.play_episode(test_env)
        reward /= TEST_EPISODES
        writer.add_scalar("reward", reward, iter_no)
        if reward > best_reward:
            print(f"{iter_no}: Best reward updated {best_reward:.3} -> {reward:.3}")
            best_reward = reward
        if reward > 0.80:
            print("Solved in %d iterations!" % iter_no)
            break
    writer.close()
```

가치 표를 정책 삼아 테스트 에피소드를 20번 플레이하고 평균 보상을 계산한다. TensorBoard에 기록하고, 최고 기록을 갱신했으면 출력한다. 평균 보상이 **0.80**을 넘으면 "풀렸다"고 판단하고 학습을 멈춘다.

### 5.9 실행 결과

```
Chapter05$ ./01_frozenlake_v_iteration.py
3: Best reward updated 0.0 -> 0.1
4: Best reward updated 0.1 -> 0.15
7: Best reward updated 0.15 -> 0.45
9: Best reward updated 0.45 -> 0.7
11: Best reward updated 0.7 -> 0.9
Solved in 11 iterations!
```

이 결과는 확률적이라 실행할 때마다 조금씩 다르지만, 대체로 **10~100번의 반복**이면 문제를 푸는 정책을 찾았고, 모든 경우에 **1초도 안 걸렸다.** 지난 챕터에서 교차 엔트로피 방법으로 80% 성공률을 얻는 데 **약 1시간**이 걸렸던 것과 비교하면 엄청난 발전이다. 그 이유는 두 가지다.

**첫째**, 행동의 확률적인 결과와, 에피소드 길이(평균 6~10 스텝)가 겹치면서, 교차 엔트로피 방법은 "에피소드 안의 어떤 행동이 잘한 것이고 어떤 게 실수였는지" 파악하기가 어려웠다. 가치 반복은 상태(또는 행동) 각각의 값을 개별적으로 다루면서, 확률적 결과를 확률 추정과 기댓값 계산으로 자연스럽게 반영한다. 그래서 훨씬 단순하고, 환경으로부터 필요한 데이터도 훨씬 적다(RL에서는 이를 **표본 효율성(sample efficiency)** 이라 부른다).

**둘째**, 가치 반복은 학습을 시작하기 위해 **완전한 에피소드가 필요 없다.** 극단적으로는, 단 하나의 예시만으로도 값을 업데이트하기 시작할 수 있다.

다만 FrozenLake는 보상 구조상(목표 상태에 성공적으로 도달했을 때만 1을 받음) 유용한 가치 표로 학습을 시작하려면 **최소 한 번의 성공한 에피소드**가 필요하며, 이는 더 복잡한 환경에서는 어려울 수 있다. 예를 들어 `FrozenLake8x8-v1`(더 큰 8×8 버전)로 바꿔서 실행해 보면, 150에서 1,000번의 반복이 필요하고, TensorBoard 그래프를 보면 대부분의 시간을 **첫 성공 에피소드를 기다리는 데** 쓴 뒤 그다음부턴 매우 빠르게 수렴한다.

다음은 FrozenLake-4x4와 8×8 버전 각각의 학습 중 보상 변화를 보여주는 두 그래프다.

![[fig_5_9.png]]
*그림 5.9 — FrozenLake-4x4에서의 보상 변화 추이*

![[fig_5_10.png]]
*그림 5.10 — FrozenLake-8x8에서의 보상 변화 추이. 초반에 성공 에피소드를 기다리는 긴 정체 구간이 보이고, 이후 급격히 수렴한다.*

---

## 6. FrozenLake를 위한 Q-반복 (Q-iteration for FrozenLake)

전체 예제는 `Chapter05/02_frozenlake_q_iteration.py`에 있으며, 방금 본 V-값 버전과의 차이는 정말 사소하다.

- **가치 표의 키가 달라진다.** 앞서는 상태의 가치만 저장했으므로 딕셔너리의 키가 그냥 상태였다. 이제는 Q-함수의 값을 저장해야 하므로, 키가 **(상태, 행동)** 쌍의 조합이 된다.
- **`calc_action_value()` 함수가 더 이상 필요 없다.** 이제 행동 가치 자체가 이미 가치 표에 저장되어 있기 때문이다.
- 가장 중요한 변화는 에이전트의 **`value_iteration()` 메서드**다. 예전에는 `calc_action_value()` 호출을 감싸는 단순한 래퍼였는데(벨만 근사 작업을 그 함수가 대신 해 줬으므로), 이제 그 함수가 사라졌으니 `value_iteration()` 메서드 안에서 직접 이 근사를 수행해야 한다.

코드가 거의 같으므로, 가장 흥미로운 `value_iteration()` 함수로 바로 넘어가 보자.

```python
def value_iteration(self):
    for state in range(self.env.observation_space.n):
        for action in range(self.env.action_space.n):
            action_value = 0.0
            target_counts = self.transits[(state, action)]
            total = sum(target_counts.values())
            for tgt_state, count in target_counts.items():
                rw_key = (state, action, tgt_state)
                reward = self.rewards[rw_key]
                best_action = self.select_action(tgt_state)
                val = reward + GAMMA * self.values[(tgt_state, best_action)]
                action_value += (count / total) * val
            self.values[(state, action)] = action_value
```

이 코드는 이전 예제의 `calc_action_value()`와 거의 똑같은 일을 한다. 주어진 상태와 행동에 대해, 그 행동으로 도달한 목적지 상태들에 대한 통계를 이용해 이 행동의 값을 계산한다. 여전히 벨만 방정식과 카운터를 이용해 목적지 상태의 확률을 근사한다는 점은 같지만, **벨만 방정식에서 필요한 "다음 상태의 가치"를 이제는 다르게 계산해야 한다**는 점이 다르다.

예전에는 그 값이 가치 표에 (상태의 가치로) 이미 저장되어 있었으므로 그냥 꺼내 쓰면 됐다. 지금은 그렇게 할 수 없으므로, **`select_action` 메서드를 호출**해서 가장 큰 Q값을 주는 행동을 고른 뒤, 그 Q값을 목적지 상태의 가치로 사용해야 한다. 물론 이 값을 계산하는 별도의 함수를 새로 만들 수도 있지만, `select_action`이 필요한 일을 거의 다 해 주므로 그냥 재사용한다.

`select_action` 메서드 자체도 다시 짚어 보자:

```python
def select_action(self, state: State) -> Action:
    best_action, best_value = None, None
    for action in range(self.env.action_space.n):
        action_value = self.values[(state, action)]
        if best_value is None or best_value < action_value:
            best_value = action_value
            best_action = action
    return best_action
```

앞서 말했듯, 이제는 `calc_action_value` 메서드가 없으므로 행동을 고를 때 **가치 표에서 값을 바로 꺼내 비교**하기만 한다. 별것 아닌 개선처럼 보일 수 있지만, `calc_action_value`가 예전에 어떤 데이터를 썼는지 되짚어 보면 **왜 Q함수 학습이 V함수 학습보다 RL에서 훨씬 인기 있는지** 알 수 있다.

`calc_action_value`는 **보상 정보와 확률 정보를 모두** 사용한다. 가치 반복 방법 자체에는 큰 문제가 안 된다(어차피 학습 중에 이 정보를 갖고 있으므로). 하지만 다음 챕터에서 배울 **가치 반복의 확장판**은 확률 근사를 하지 않고 환경 샘플에서 값을 그냥 가져다 쓴다. 그런 방법들에게는 확률에 대한 의존성이 에이전트에게 불필요한 부담이 된다. Q-러닝의 경우, 에이전트가 결정을 내리는 데 필요한 건 그냥 **Q값**뿐이다.

> [!note] V함수가 쓸모없다는 뜻은 아니다
> V함수가 완전히 쓸모없다는 말은 아니다. **액터-크리틱(actor-critic) 방법**의 필수적인 부분이며, 이는 이 책 Part 3에서 다룬다. 하지만 가치 학습(value learning) 영역에서는 Q함수가 확실한 인기 스타다.

실행 결과는 V-반복 버전과 큰 차이가 없다(단, Q-러닝 버전은 가치 표에 **4배 더 많은 메모리**가 필요하다 — 상태 개수 대신 상태×행동 개수만큼 저장하기 때문이다).

```
Chapter05$ ./02_frozenlake_q_iteration.py
8: Best reward updated 0.0 -> 0.35
11: Best reward updated 0.35 -> 0.45
14: Best reward updated 0.45 -> 0.55
15: Best reward updated 0.55 -> 0.65
17: Best reward updated 0.65 -> 0.75
18: Best reward updated 0.75 -> 0.9
Solved in 18 iterations!
```

---

## 요약

이 챕터에서 우리는 딥 RL의 최신 방법들을 이해하기 위한 매우 중요한 개념들을 배웠다.

1. **상태의 가치 $V(s)$와 행동의 가치 $Q(s,a)$** 를 손으로 계산해 보며 복습했다.
2. **벨만 방정식**이 왜 필요한지, 결정론적/확률적인 경우 각각 어떻게 유도되는지 살펴봤다. 그리고 가치를 알면 왜 자동으로 최적 정책을 알 수 있는지 이해했다.
3. **가치 반복** 방법으로 벨만 방정식을 실제로 반복 계산해 FrozenLake를 풀었다 — 4×4 버전은 1초도 안 되어, 교차 엔트로피 방법의 1시간과 비교해 압도적으로 빨랐다.
4. 같은 아이디어를 **Q-값 버전(Q-iteration)** 으로도 구현해 보고, 왜 Q함수 기반 학습이 RL에서 더 인기 있는지 이해했다.

다음 챕터에서는 2013년 딥 RL 혁명을 촉발시킨 **딥 Q-네트워크(Deep Q-Network, DQN)** 를 배운다. 아타리(Atari) 2600 게임 여러 개에서 사람을 능가하는 성능을 보여준 바로 그 방법이다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[벨만 방정식 Bellman Equation]]
- [[가치 반복 Value Iteration]]
- [[탐욕적 정책 Greedy Policy]]
- [[defaultdict와 Counter]]
- [[할인율 감마와 등비급수]]
- [[기댓값 Expectation]]
- [[마르코프 성질과 마르코프 체인]]
- [[상태 관측 에피소드 정책]]
- [[관측공간과 행동공간(Space)]]

## 한눈에 보는 개념 지도

| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 상태의 가치 | $V(s)$ | 상태 $s$에서 시작해 얻을 기대 리턴 |
| 행동의 가치 | $Q(s,a)$ | 상태 $s$에서 행동 $a$를 했을 때의 기대 리턴 |
| 벨만 방정식 | $V(s)=\max_a\sum_{s'}p(r+\gamma V(s'))$ | 다음 상태 가치를 재활용해 현재 가치를 재귀적으로 계산 |
| 할인율 | $\gamma$ | 미래 보상을 얼마나 깎을지 (0~1) |
| 가치 반복 | — | 가치를 0으로 초기화하고 벨만 업데이트를 반복해 수렴시키는 알고리즘 |
| 탐욕적 정책 | $\arg\max_a Q(s,a)$ | 현재 가치 추정 기준으로 가장 좋은 행동을 즉시 선택 |
| 전이 확률 | $p_{a,s\to s'}$ | 상태 $s$에서 행동 $a$로 상태 $s'$에 도달할 확률 |
| 표본 효율성 | sample efficiency | 적은 환경 상호작용으로도 잘 학습하는 정도 |
