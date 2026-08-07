---
title: "Chapter 19 — 인간 피드백 강화학습 (Reinforcement Learning with Human Feedback)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 19
tags: [DeepRL, 강화학습, RLHF, 보상모델, LLM, ChatGPT]
---

# Chapter 19 · 인간 피드백 강화학습 (RLHF)

> [!abstract] 이 챕터를 한 문장으로
> 보상 함수를 사람이 직접 코딩하기 어려운 문제에서는, **"이 행동과 저 행동 중 어느 게 나은가요?"라는 사람의 선호 판단**으로부터 보상을 대신 학습시킬 수 있다 — 이것이 **RLHF(Reinforcement Learning with Human Feedback)** 이며, 놀랍게도 이 방법이 오늘날 ChatGPT를 비롯한 모든 대형 언어모델(LLM) 학습의 심장부에 자리 잡고 있다.

---

## 들어가며 — 이 챕터에서 배울 것

이 챕터는 비교적 최근에 등장한 방법을 다룬다. "원하는 행동을 명시적인 보상 함수로 정의하기 어려운 상황"을 다루는 **RLHF**다. 이는 지난 챕터(18장)에서 다룬 **탐험(exploration)** 문제와도 연결된다 — 사람의 피드백이 에이전트의 학습 방향을 새로운 곳으로 밀어줄 수 있기 때문이다.

흥미롭게도 이 방법은 원래 RL의 아주 좁은 하위 문제를 위해 개발되었는데, 오늘날 대형 언어모델(LLM) 분야에서 엄청나게 성공하며 화제의 중심이 되었다. 이 책은 LLM을 다루는 책이 아니므로, 이 챕터에서는 OpenAI와 Google의 원 논문 Christiano 등, *Deep reinforcement learning from human preferences* [Chr+17] 을 중심으로 다루되, LLM 학습에서 이 방법이 어떻게 쓰이는지도 개략적으로 설명한다.

이 챕터에서 우리는:
- 보상 목표가 불분명한 문제와 탐험 문제를 다루기 위해 RL에서 사람 피드백을 활용하는 법을 살펴본다.
- SeaQuest 아타리 게임에 새로운 행동을 가르치기 위해, RLHF 파이프라인을 처음부터 직접 구현해본다.

---

## 1. 복잡한 환경에서의 보상 함수 — "숫자 하나로는 부족하다"

### 1.1 보상은 RL의 심장이다

1장에서 이야기했듯, **보상은 RL의 핵심 개념**이다. 보상이 없으면 우리는 눈먼 것과 같다 — 이 책에서 다룬 거의 모든 방법이 환경이 주는 보상 값에 크게 의존한다.

- **가치 기반 방법**(Part 2, DQN 등)에서는 보상으로 $Q$-값을 근사해 행동을 평가하고 가장 좋은 것을 고른다.
- **정책 기반 방법**(Part 3, [[정책 경사 Policy Gradient|정책 경사]] 등)에서는 보상이 훨씬 더 직접적으로 쓰인다 — 어려운 수식을 다 걷어내고 말하면, "더 많은 누적 미래 보상을 가져오는 행동을 선호하도록" 정책을 최적화하는 것이 전부다.
- **블랙박스 방법**(17장)에서는 보상으로 "이 에이전트 변종을 살릴지 버릴지"를 결정했다.

우리가 실험해온 거의 모든 RL 환경에서는 보상 함수가 이미 정해져 있었다 — 아타리는 점수, FrozenLake는 명확한 목표 지점, 시뮬레이션 로봇은 이동 거리 등. 유일한 예외는 10장의 주식 거래 시스템이었는데, 우리가 직접 환경을 만들며 보상을 어떻게 설계할지 고민했었다. 그때조차도 무엇을 보상으로 쓸지는 비교적 명확했다.

### 1.2 그런데 현실에서는 보상을 정의하기 어렵다

문제는, 실제 삶의 문제에서는 "무엇을 보상으로 써야 하는가"를 명확히 하기가 그렇게 쉽지 않다는 점이다.

> [!example] 챗봇의 딜레마
> 챗봇에게 "내일 날씨 어때?"라고 물었는데, 정확하지만 **무례한 말투**로 답했다고 하자. 이걸 얼마나 감점해야 할까? 반대로 아주 **공손하지만 틀린 정보**를 줬다면? 만약 "정보의 정확성"이라는 단 하나의 기준만 최적화하면, "일은 하지만 아무도 쓰기 싫은" 챗봇이 나올 수 있다. 너무 어색하고 이상해서 말이다.

> [!example] 화물 운송 회사의 딜레마
> 운송 회사가 "이익 최대화" 하나만 최적화한다면? 운전 규칙, 근무 시간, 노동법 등 수많은 제약을 무시하고 "이웃집 담장을 뚫고 지나가는 게 제일 빠른 길"이라는 결론에 도달할 수도 있다.

즉 현실에서는 **딱 하나의 값만 최대화하면 되는 경우가 오히려 예외적**이다. 대부분은 여러 요소 사이에서 균형을 잡아야 한다.

### 1.3 SeaQuest로 보는 구체적인 예시

18장에서 실험한 아타리 SeaQuest 게임이 아주 좋은 사례다. (직접 플레이해보고 싶다면 브라우저에서: https://www.retrogames.cz/play_221-Atari2600.php ) 이 게임에서 점수는 다음 활동들의 합이다.

- 악당 물고기와 적 잠수함을 쏘아 맞추기
- 잠수부를 구조해 수면으로 데려오기
- 적의 공격과 수면의 배들을 피하기 (게임 후반 등장)

산소가 한정되어 있으므로, 잠수함은 주기적으로 수면 위로 올라가 산소를 채워야 한다.

최신 RL 방법들은 "물고기·잠수함을 쏴서 점수 얻기"는 몇 시간 학습이면 큰 문제 없이 발견해낸다. 그런데 **잠수부를 구조해 얻는 점수는 훨씬 발견하기 어렵다** — 잠수부 6명을 모아 수면까지 도달해야만 보상이 나오기 때문이다. 산소 재충전도 마찬가지로 발견하기 어렵다. 신경망은 애초에 "산소"가 무엇인지, 화면 아래 게이지와 잠수함의 갑작스러운 죽음이 무슨 관계인지 전혀 모른다. $\epsilon$-greedy 탐험을 쓰는 우리 RL 방법은, 마치 갓난아기가 버튼을 무작위로 눌러보며 우연히 맞는 긴 행동 순서를 찾아내길 기다리는 것과 비슷하다 — 그 긴 순서가 실행되기까지 아주 오랜 시간이 걸릴 수 있다.

그 결과, SeaQuest 학습 에피소드 대부분은 **평균 점수 300~500점, 500스텝** 정도에서 멈춘다. 잠수함이 산소 부족으로 죽어버리고, 무작위로 수면에 올라가는 일이 너무 드물어서 "사실 게임을 훨씬 오래 할 수 있다"는 걸 발견하지 못하는 것이다. 반면 이 게임을 처음 보는 사람도 몇 분만 해보면 산소를 채우고 잠수부를 구하는 법을 스스로 알아낸다.

> [!important] 여기서 RLHF가 등장하는 이유
> 산소가 중요하다는 걸 "산소 재충전 시 추가 보상"처럼 보상 함수에 직접 끼워 넣어 도와줄 수도 있다. 하지만 그러면 여기저기 보상을 미세 조정하는 악순환에 빠지기 쉽다 — 이건 애초에 RL을 쓰면서 피하려던 바로 그 노력이다. **RLHF는 이런 저수준 보상 함수 손질을 피하면서, 사람이 에이전트의 행동에 직접 피드백을 줄 수 있게 해주는 접근법**이다.

---

## 2. 이론적 배경

2017년 OpenAI와 Google 연구자들이 발표한 원조 RLHF 논문 [Chr+17]을 살펴보자. 이 논문 발표 이후(특히 ChatGPT 출시 이후) 이 방법은 매우 활발한 연구 분야가 되었다. 최신 동향은 https://github.com/opendilab/awesome-RLHF 에서 확인할 수 있다.

### 2.1 방법 개요

논문 저자들은 두 부류의 문제로 실험했다 — MuJoCo 시뮬레이션 로봇(15·16장에서 다룬 연속 제어 문제와 유사)과 여러 아타리 게임.

핵심 아이디어는 이렇다. **원래의 RL 모델 구조는 그대로 두되, 환경이 주는 보상을 "보상 예측기(reward predictor)"라는 신경망으로 갈아 끼운다.** 이 신경망은 사람이 모은 데이터로 학습되며, 논문에서는 $\hat{r}(o,a)$ 로 표기한다. 관측과 행동을 받아 즉시 보상의 실수(float) 값을 반환한다.

이 보상 예측기를 학습시킬 데이터는 사람이 직접 숫자를 매겨서 주는 게 아니라, **사람의 선호로부터 유도**된다. 사람들에게 에이전트 행동을 담은 짧은 영상 두 개를 보여주고 "어느 쪽이 더 낫나요?"라고 묻는다. 다시 말해, 보상 예측기의 학습 데이터는 **두 개의 에피소드 조각(segment) $\sigma_1, \sigma_2$**(관측·행동 $(o_t, a_t)$ 의 고정 길이 나열)와, 사람이 준 라벨 $\mu$(어느 쪽을 선호하는지)로 구성된다. 답변 선택지는 "첫 번째", "두 번째", "둘 다 좋다", "판단 불가"의 4가지다.

이 개념 전체(RLHF의 큰 그림)는 [[RLHF 인간 피드백 강화학습]] 에서 더 자세히 다룬다.

### 2.2 선호를 확률로, 확률을 손실로

신경망 $\hat{r}(o,a)$ 은 다음 데이터로 [[교차 엔트로피 Cross-Entropy|교차 엔트로피]] 손실을 이용해 학습된다. 먼저, "사람이 $\sigma_1$ 을 $\sigma_2$ 보다 선호할 확률"을 추정하는 함수 $\hat{P}[\sigma_1 \succ \sigma_2]$ 를 다음처럼 정의한다.

$$\hat{P}[\sigma_1 \succ \sigma_2] = \frac{e^{\sum \hat{r}(o^1_t,a^1_t)}}{e^{\sum \hat{r}(o^1_t,a^1_t)} + e^{\sum \hat{r}(o^2_t,a^2_t)}}$$

말로 풀면: **세그먼트마다 모든 스텝의 예측 보상을 합산하고, 그 값을 지수화(exponentiate)한 뒤, 정규화(비율을 취함)한다.** 이 손실 함수와 확률식의 자세한 유도, 그리고 왜 이것이 [[소프트맥스 Softmax]] 와 같은 구조인지는 [[선호 기반 보상 모델과 브래들리-테리 모델]] 에서 깊이 다룬다.

교차 엔트로피 손실은 이진 분류의 표준 공식으로 계산한다.

$$\text{loss}(\hat{r}) = -\sum_{(\sigma_1,\sigma_2,\mu)} \mu_1 \log \hat{P}[\sigma_1 \succ \sigma_2] + \mu_2 \log \hat{P}[\sigma_2 \succ \sigma_1]$$

$\mu_1, \mu_2$ 값은 사람의 판단에 따라 정해진다. 첫 번째 세그먼트가 더 좋다면 $\mu_1=1, \mu_2=0$, 두 번째가 더 좋다면 $\mu_2=1, \mu_1=0$, 둘 다 좋다고 판단하면 두 값 모두 $0.5$ 로 둔다.

### 2.3 이 보상 모델의 3가지 장점

이런 방식의 보상 모델은 다른 대안들과 비교했을 때 다음과 같은 이점이 있다.

1. **필요한 라벨 수를 크게 줄인다.** 신경망으로 보상을 예측하면, 정책의 모든 행동 하나하나에 라벨을 다는 극단적인 경우를 피할 수 있다. RL에서는 수백만 번의 환경 상호작용이 일어나므로, 이를 전부 라벨링하는 건 엄청나게 비싸다. 고수준 목표를 다루는 경우엔 거의 불가능한 일이기도 하다.
2. **좋은 행동뿐 아니라 싫어하는 행동에 대한 피드백도 줄 수 있다.** 14장에서 웹 자동화 에이전트를 학습시킬 때 사람의 시연 기록을 사용했던 것을 기억하는가? 그런데 사람의 시연은 오직 긍정적인 예("이렇게 해라")만 보여줄 뿐, 부정적인 예("이렇게 하지 마라")를 포함할 방법이 없다. 게다가 사람의 시연은 수집하기 더 어렵고 오류도 더 많이 포함하기 쉽다.
3. **사람이 원하는 행동을 알아볼 수는 있지만, 그것을 직접 재현하지는 못하는 문제에도 대응할 수 있다.** 예를 들어 16장의 네 발 달린 Ant 로봇을 직접 조종하는 건 사람에게 매우 어려운 일이다. 그럼에도 우리는 그 로봇이 정상적으로 걷는지 아니면 정책이 잘못됐는지를 알아보는 데는 아무 문제가 없다.

### 2.4 실제 학습 파이프라인의 구조

RLHF 논문에서 저자들은 보상 모델 학습과 활용에 여러 접근법을 시도했다. 그들의 설정에서는 세 프로세스가 병렬로 동시에 돌아갔다.

1. RL 학습 방법(A2C)이 현재의 $\hat{r}(o,a)$ 네트워크를 보상 예측에 사용한다. 무작위로 뽑힌 궤적 조각 $\sigma = (o_i, a_i)$ 는 라벨링용 데이터베이스에 저장된다.
2. 사람 라벨러들이 세그먼트 쌍 $(\sigma_1, \sigma_2)$ 을 표본으로 뽑아 라벨 $\mu$ 를 매기고, 데이터베이스에 저장한다.
3. 보상 모델 $\hat{r}(o,a)$ 는 데이터베이스에 쌓인 라벨링된 쌍들로 주기적으로 학습되고, 그 결과가 다시 RL 학습 프로세스로 전달된다.

이 과정을 나타낸 것이 Figure 19.1이다.

![[fig_19_1.png]]
*그림 19.1 — RLHF 구조: "RL 학습"이 세그먼트 $\sigma$ 를 DB에 쌓고, 사람이 세그먼트 쌍 $\sigma^1,\sigma^2$ 를 보고 라벨 $\mu$ 를 매겨 DB에 저장하며, "보상 학습"이 그 라벨 $(\sigma^1,\sigma^2,\mu)$ 로 새 보상 모델 $\hat{r}(o,a)$ 를 만들어 다시 RL 학습에 공급하는 순환 구조*

앞서 이야기했듯, 이 논문은 아타리 게임과 연속 제어라는 두 부류의 문제를 다뤘다. 두 분야 모두에서 결과는 그리 극적이지 않았다 — 어떤 경우엔 기존 RL이 더 나았고, 어떤 경우엔 RLHF가 더 나았다. 하지만 RLHF가 정말 두각을 나타낸 곳은 바로 **LLM 학습 파이프라인**이었다. RLHF 실습에 들어가기 전에, 왜 그렇게 됐는지 잠깐 살펴보자.

### 2.5 RLHF와 LLM

2022년 말 출시된 ChatGPT는 순식간에 엄청난 화제가 되었다. 일반 대중에게는 2012년의 AlexNet보다도 더 큰 영향을 미쳤다고 할 수 있는데, AlexNet은 "기술적인 이야기"라서 무엇이 그렇게 특별한지 설명하기가 더 어려웠던 반면, ChatGPT는 달랐다. 출시 한 달 만에 사용자 1억 명을 돌파했고, 거의 모든 사람이 이 이야기를 할 정도였다.

ChatGPT(그리고 모든 현대 LLM)의 학습 파이프라인 중심에는 RLHF가 자리 잡고 있다. 그 덕분에 이 대형 모델 미세조정 방법은 순식간에 인기를 얻었고 연구 관심도 폭발적으로 늘었다. 이 책이 LLM을 다루는 책은 아니기에, 여기서는 파이프라인과 그 안에서 RLHF가 어떻게 쓰이는지만 간단히 설명한다. 흥미로운 응용 사례이기 때문이다.

큰 틀에서 LLM 학습은 3단계로 이뤄진다.

1. **사전학습(Pretraining)**: 언어 모델을 방대한 텍스트 말뭉치로 초기 학습시키는 단계. 구할 수 있는 모든 정보를 모아 비지도 방식으로 학습시킨다. 그 규모(와 비용)는 어마어마하다 — LLaMA 학습에 쓰인 RedPajama 데이터셋은 1.2조 개의 토큰(대략 1,500만 권의 책 분량)을 담고 있다. 이 단계에서 무작위로 초기화된 모델은 언어의 규칙성과 깊은 연관 관계를 배운다. 다만 데이터 양이 워낙 방대해서, 가짜 뉴스나 혐오 발언 같은 인터넷의 온갖 지저분한 것들까지 걸러내지 못한 채 그대로 학습에 들어간다.
2. **지도 미세조정(Supervised fine-tuning)**: 사전에 정의된, 사람이 직접 선별한 대화 예시들로 모델을 미세조정하는 단계. 여기서 쓰이는 데이터셋은 사람이 직접 만든 것이고 분량도 훨씬 적다 — 대략 1만~10만 개의 대화 예시 수준이다. 이 데이터는 보통 해당 분야 전문가들이 만들고 검증하기 때문에 많은 노력이 든다.
3. **RLHF 미세조정** (**"모델 정렬(alignment)"** 이라고도 부른다): 이 단계는 우리가 이미 설명한 과정과 같다. 생성된 대화 쌍을 사람에게 보여주고 라벨링을 시키고, 그 라벨로 보상 모델을 학습시키고, 이 보상 모델을 RL 알고리즘에 사용해 LLM 모델이 사람의 선호를 따르도록 미세조정한다. 라벨링된 샘플 수는 지도 미세조정 단계보다 더 많다(대략 100만 쌍 수준). 하지만 두 대화 중 어느 게 나은지 비교하는 일이 대화를 처음부터 완성해서 만들어내는 일보다 훨씬 쉬운 작업이라, 이는 별로 문제가 되지 않는다.

짐작하듯, 첫 단계가 가장 비용이 많이 들고 시간도 오래 걸린다 — 테라바이트 단위의 텍스트를 트랜스포머에 밀어 넣어야 한다. 하지만 각 단계의 중요도는 전혀 다르다. 마지막 단계에서 시스템은 주어진 문제에 대한 최선의 해답이 무엇인지 배울 뿐 아니라, 그것을 **사회적으로 받아들여지는 방식으로 생성하는 것**에 대한 피드백까지 얻는다.

RLHF는 바로 이런 작업에 매우 잘 맞는다 — 단지 대화 쌍만으로, 챗봇처럼 복잡한 대상에 대한 라벨러들의 암묵적인 "선호 모델"을 나타내는 보상 모델을 배울 수 있기 때문이다. 이걸 (예를 들어 보상 함수를 통해) 명시적으로 하려고 하면 굉장히 어렵고 불확실성이 큰 문제가 될 수 있다.

정책 미세조정 자체가 어떤 원리로 "기존 지식을 지키면서 새 지식만 얹는지"는 [[정책 미세조정 Fine-tuning]] 에서 자세히 다룬다.

---

## 3. RLHF 실습 — SeaQuest에 새로운 행동 가르치기

방금 살펴본 파이프라인을 더 잘 이해하기 위해, "직접 해보는 것이 가장 좋은 학습법"이라는 말대로 이제 우리 손으로 직접 구현해본다. 지난 챕터에서 SeaQuest 아타리 환경을 다뤘는데, 이 게임은 탐험 관점에서 까다로운 문제였으므로, 사람 피드백으로 무엇을 이룰 수 있는지 확인하기에 딱 좋은 환경이다.

챕터의 범위를 한정하고 예제를 더 재현하기 쉽게 만들기 위해, 원 RLHF 논문 [Chr+17]의 실험 설정에서 다음과 같은 변경을 가했다.

- 단일 SeaQuest 환경에만 집중했다. 목표는 18장에서 얻은 A2C 결과(평균 점수 400, 산소 부족으로 인한 500스텝 에피소드)를 개선하는 것이었다.
- 비동기적 라벨링과 보상 모델 학습 대신, 이 과정을 별도의 단계로 분리했다.
  1. A2C 학습을 수행하며 궤적 조각을 로컬 파일에 저장한다. 이 학습은 선택적으로 보상 모델 네트워크를 불러와 사용할 수 있어서, 학습 후에 더 많은 샘플을 라벨링하며 보상 모델을 반복 개선할 수 있다.
  2. 웹 UI로 무작위 궤적 조각 쌍을 라벨링하고, 그 라벨을 JSON 파일에 저장한다.
  3. 그 조각과 라벨로 보상 모델을 학습시키고, 결과를 디스크에 저장한다.
- 보상 모델 학습의 여러 변형(L2 정규화, 앙상블 등)은 모두 생략했다.
- 라벨 수를 훨씬 적게 잡았다 — 매 실험마다 에피소드 조각 100쌍씩만 추가로 라벨링하고 모델을 재학습했다.
- 보상 모델에 행동(action)을 명시적으로 추가했다. 자세한 내용은 아래 "보상 모델 학습" 절 참고.
- 보상 모델은 저장된 최고 성능 모델을 미세조정하는 데 사용했다. 참고로 원 논문에서는 모델을 처음부터 학습시키면서 병렬 RLHF 라벨링과 보상 모델 재학습으로 개선해나갔다.

### 3.1 A2C를 이용한 초기 학습

첫 모델("버전 0" 또는 v0)을 얻기 위해, 이 책에서 이미 여러 번 다룬 것과 같은 아타리 래퍼(wrapper)를 적용한 표준 A2C 코드를 사용했다.

학습을 시작하려면 `Chapter19/01_a2c.py` 모듈을 실행하면 된다. 기본적인 A2C 학습 외에도, 보상 모델을 사용하도록 켜는 커맨드라인 옵션이 있지만(앞서 다룬 내용) 이 단계에서는 필요 없다.

기본 모델의 학습을 시작하려면 다음 명령을 사용한다.

```
Chapter19$ ./01_a2c.py --dev cuda -n v0 --save save/v0 --db-path db-v0
```

실행하면 다음과 같은 신경망 구조가 출력된다.

```python
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
    (2): Linear(in_features=512, out_features=18, bias=True)
  )
  (value): Sequential(
    (0): Linear(in_features=3136, out_features=512, bias=True)
    (1): ReLU()
    (2): Linear(in_features=512, out_features=1, bias=True)
  )
)
```

이 구조는 이전 챕터들에서 본 A2C 에이전트와 동일하다 — 화면 이미지를 처리하는 합성곱(conv) 부분, 그리고 정책(policy, 18개 행동에 대한 확률)과 가치(value, 상태 하나의 값)를 각각 출력하는 두 개의 머리(head)로 나뉜다.

커맨드라인 옵션 설명:
- `--dev`: 연산에 쓸 장치 이름.
- `-n`: 실행 이름. TensorBoard에서 사용된다.
- `--save`: 테스트 후 최고 성능 모델을 저장할 디렉터리 이름. 100배치마다 현재 모델로 SeaQuest에서 10번의 테스트 에피소드를 (보상 클리핑을 끈 채, 즉 원래 점수 범위 그대로) 수행하고, 이 10회 중 최고 보상이나 스텝 수가 기존 기록보다 좋으면 모델을 파일로 저장한다. 이 파일들이 나중에 미세조정에 쓰인다.
- `--db-path`: 학습 중 무작위 에피소드 조각을 저장할 디렉터리 이름. 이 데이터는 나중에 라벨링과 보상 모델 학습에 쓰인다.

**에피소드 조각 데이터베이스(DB)의 구조**를 살펴보자. 아주 단순하다. 학습에 사용되는 각 환경(총 16개)마다 0~15의 식별자가 부여되고, `--db-path`로 준 디렉터리 아래 서브디렉터리로 쓰인다. 즉 각 환경은 자신만의 디렉터리에 독립적으로 무작위 조각을 저장한다. 이 저장 로직은 `lib/rlhf.py` 모듈에 있는 `EpisodeRecorderWrapper` 라는 Gym API `Wrapper` 서브클래스로 구현되어 있다. ([[Wrapper 래퍼 패턴]] 참고)

이 래퍼의 소스 코드를 살펴보자. 먼저 두 하이퍼파라미터를 선언한다 — 조각의 길이를 정하는 `EPISODE_STEPS`, 그리고 에피소드 기록을 시작할 확률인 `START_PROB`이다.

```python
# how many transitions to store in episode
EPISODE_STEPS = 50
# probability to start episode recording
START_PROB = 0.00005

@dataclass(frozen=True)
class EpisodeStep:
    obs: np.ndarray
    act: int

class EpisodeRecorderWrapper(gym.Wrapper):
    def __init__(self, env: gym.Env, db_path: pathlib.Path, env_idx: int,
                 start_prob: float = START_PROB, steps_count: int = EPISODE_STEPS):
        super().__init__(env)
        self._store_path = db_path / f"{env_idx:02d}"
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._start_prob = start_prob
        self._steps_count = steps_count
        self._is_storing = False
        self._steps: tt.List[EpisodeStep] = []
        self._prev_obs = None
        self._step_idx = 0
```

- `EPISODE_STEPS = 50`: 에피소드 조각 하나가 몇 스텝 길이인지. ([[데이터클래스 dataclass]] 로 정의된 `EpisodeStep`이 그 한 스텝, 관측(`obs`)과 행동(`act`) 하나를 담는다.)
- `START_PROB = 0.00005`: 매 스텝마다 "지금부터 조각 기록을 시작할지" 결정하는 아주 낮은 확률.
- `self._store_path`: 이 환경 전용 저장 디렉터리 (`env_idx`로 구분).
- `self._is_storing`: 지금 조각을 기록하는 중인지 나타내는 플래그.
- `self._steps`: 지금까지 기록된 `EpisodeStep` 리스트.

에피소드 조각은 `EpisodeStep` 객체(관측과, 그 관측에서 취한 행동)의 리스트로 저장된다.

**환경을 리셋하는 메서드**는 매우 단순하다 — 스텝 카운터(`_step_idx`)를 갱신하고, 기록 중이라면(`_is_storing`이 True) 관측을 `_prev_obs`에 저장한다. 우리 조각은 고정된 스텝 수(기본 50)를 가지며, **에피소드 경계와 무관하게** 기록된다(즉, 잠수함이 죽기 직전에 기록을 시작했다면, `reset()` 이후 다음 에피소드의 시작 부분까지 이어서 기록한다).

```python
def reset(self, *, seed: int | None = None, options: dict[str, tt.Any] | None = None) \
        -> tuple[WrapperObsType, dict[str, tt.Any]]:
    self._step_idx += 1
    res = super().reset(seed=seed, options=options)
    if self._is_storing:
        self._prev_obs = deepcopy(res[0])
    return res
```

원한다면 이 로직을 실험해볼 수도 있다. 원칙적으로 에피소드가 끝난 이후의 관측은 그 전 관측·행동과는 독립적이니까. 하지만 그러면 조각 데이터의 길이가 가변적이 되어 처리가 복잡해진다.

**래퍼의 핵심 로직은 `step()` 메서드**에 있고, 이것도 그리 복잡하지 않다. 매 행동마다, 기록 중이면 그 스텝을 저장하고, 아니라면 무작위 수를 뽑아 기록을 시작할지 결정한다.

```python
def step(self, action: WrapperActType) -> tuple[
        WrapperObsType, SupportsFloat, bool, bool, dict[str, tt.Any]
]:
    self._step_idx += 1
    obs, r, is_done, is_tr, extra = super().step(action)
    if self._is_storing:
        self._steps.append(EpisodeStep(self._prev_obs, int(action)))
        self._prev_obs = deepcopy(obs)
        if len(self._steps) >= self._steps_count:
            store_segment(self._store_path, self._step_idx, self._steps)
            self._is_storing = False
            self._steps.clear()
    elif random.random() <= self._start_prob:
        # start recording
        self._is_storing = True
        self._prev_obs = deepcopy(obs)
    return obs, r, is_done, is_tr, extra
```

한 줄씩 보면: 원래 환경의 `step()`을 호출해 결과를 얻은 뒤, **기록 중이라면** 방금 스텝(이전 관측 + 이번 행동)을 리스트에 쌓는다. 리스트가 목표 길이(50)에 도달하면 `store_segment()`로 저장하고 기록 상태를 초기화한다. **기록 중이 아니라면** 아주 낮은 확률로 새 기록을 시작한다.

기본적으로 기록 시작 확률은 매우 낮다(`START_PROB = 0.00005`, 즉 0.005% 확률). 하지만 학습 중 워낙 많은 스텝을 진행하기 때문에 라벨링할 조각은 충분히 쌓인다. 예를 들어 1,200만 환경 스텝(약 5시간 학습) 후에는 데이터베이스에 2,500개의 조각이 쌓이며, 디스크 용량으로는 12GB에 달한다.

`step()` 메서드는 `store_segment()` 함수를 이용해 `EpisodeStep` 리스트를 저장하는데, 이건 그냥 리스트를 `pickle.dumps()`로 직렬화하는 것뿐이다.

```python
def store_segment(root_path: pathlib.Path, step_idx: int, steps: tt.List[EpisodeStep]):
    out_path = root_path / f"{step_idx:08d}.dat"
    dat = pickle.dumps(steps)
    out_path.write_bytes(dat)
    print(f"Stored {out_path}")
```

라벨링을 쉽게 하기 위해 짚고 넘어갈 중요한 세부사항이 있다. **DB에 저장하는 관측은 표준 아타리 래퍼를 거치기 전의 원본**이다. 이러면 저장해야 할 데이터 크기는 커지지만, 사람 라벨러는 흑백으로 축소된 이미지 대신 **원래의 컬러 아타리 화면(160×192 해상도)**을 그대로 보게 된다.

이를 위해, 이 래퍼는 원래 Gymnasium 환경 바로 다음, 아타리 래퍼들보다 앞서 적용된다. `01_a2c.py` 모듈의 관련 코드는 다음과 같다.

```python
def make_env() -> gym.Env:
    e = gym.make("SeaquestNoFrameskip-v4")
    if reward_path is not None:
        p = pathlib.Path(reward_path)
        e = rlhf.RewardModelWrapper(e, p, dev=dev, metrics_queue=metrics_queue)
    if db_path is not None:
        p = pathlib.Path(db_path)
        p.mkdir(parents=True, exist_ok=True)
        e = rlhf.EpisodeRecorderWrapper(e, p, env_idx=env_idx)
    e = ptan.common.wrappers.wrap_dqn(e)
    # add time limit after all wrappers
    e = gym.wrappers.TimeLimit(e, TIME_LIMIT)
    return e
```

래퍼가 씌워지는 순서를 보자. 원본 환경 → (있다면) 보상 모델 래퍼 → 에피소드 기록 래퍼 → **그다음에야** 표준 아타리 전처리(`wrap_dqn`, 흑백·다운스케일·프레임 스태킹 등)가 적용된다. 그래서 기록되는 관측은 항상 전처리 전의 원본 컬러 화면이다.

학습 프로세스의 하이퍼파라미터(학습률 감소 스케줄, 신경망 구조, 환경 개수 등)는 논문 그대로 가져왔다. 5시간, 1,200만 관측 동안 학습시켰다. 테스트 결과 그래프는 Figure 19.2에서 볼 수 있다.

![[fig_19_2.png]]
*그림 19.2 — A2C 학습 중 테스트 보상(왼쪽)과 스텝 수(오른쪽) 변화*

최고 성능 모델은 (환경의 보상 클리핑을 끈 상태에서) 460점의 보상 수준까지 도달했다. 나쁘지 않지만, 산소를 주기적으로 채워줬다면 얻을 수 있었을 결과보다는 훨씬 낮다. 이 모델의 플레이 영상은 https://youtu.be/R_H3pXu-7cw 에서 볼 수 있다. 영상을 보면 알 수 있듯, 에이전트는 물고기 쏘는 것은 거의 완벽하게 마스터했지만, "바닥에 가만히 떠 있는" 국소 최적점(local optima)에 갇혀 버렸다(아마도 그곳에 적 잠수함이 나타나지 않아 더 안전하기 때문일 것이다). 산소를 채워야 한다는 개념 자체를 전혀 모르는 것이다.

모델 파일로 직접 영상을 녹화하고 싶다면, 모델 파일명을 받는 `01_play.py` 도구를 사용하면 된다.

### 3.2 라벨링 과정

A2C 학습을 통해 12GB, 2,500개의 무작위 에피소드 조각을 얻었다. 각 조각은 50스텝 분량의 화면 관측과 그때 취한 행동을 담고 있다. 이제 RLHF 파이프라인의 라벨링 과정으로 넘어갈 차례다.

라벨링 과정에서는 에피소드 조각 쌍을 무작위로 뽑아 사람에게 보여주고 "어느 쪽이 더 나은가요?"를 물어야 한다. 그 답은 보상 모델 학습을 위해 저장되어야 한다. 이 로직은 정확히 `02_label_ui.py`에 구현되어 있다.

라벨링 UI는 [NiceGUI](https://nicegui.io/) 라이브러리를 이용한 웹 애플리케이션으로 구현됐다. NiceGUI는 파이썬만으로 현대적인 웹 UI를 만들 수 있게 해주고, 버튼·리스트·팝업 다이얼로그 같은 다양한 상호작용 위젯을 제공한다. 원칙적으로는 자바스크립트나 CSS를 몰라도 되지만(알면 도움이 되긴 한다), NiceGUI를 처음 써봐도 문제없다. 다음 명령으로 설치하면 된다.

```
pip install nicegui==1.4.26
```

라벨링 UI를 시작하려면(NiceGUI 설치 후), 저장된 에피소드 조각이 있는 DB 경로를 지정하면 된다.

```
Chapter19$ ./02_label_ui.py -d db-v0
NiceGUI ready to go on http://localhost:8080, http://172.17.0.1:8080,
http://172.18.0.1:8080, and http://192.168.10.8:8080
```

이 인터페이스는 HTTP로 제공되므로(브라우저에서 열면 된다) 모든 머신 인터페이스의 8080 포트에서 대기한다. 원격 서버에서 시작할 때 편리하지만, 라벨링 UI에는 **인증(authentication)과 인가(authorization)가 전혀 없다**는 위험을 알아둬야 한다. 포트를 바꾸거나 특정 네트워크 인터페이스로 범위를 제한하고 싶다면 `02_label_ui.py`를 손보면 된다.

라벨링 인터페이스를 스크린샷으로 살펴보자.

![[fig_19_3_b.png]]
*그림 19.3 — DB 정보를 보여주는 라벨링 UI 화면 (DB 경로, 전체 조각 수, 라벨 수)*

이 인터페이스는 매우 단순하다. 왼쪽에는 UI의 서로 다른 기능으로 이동하는 세 개의 링크가 있다.
- **Overview**: 데이터베이스 경로, 담긴 조각의 전체 개수, 이미 만들어진 라벨 수를 보여준다.
- **Label new data**: 무작위로 조각 쌍을 표본으로 뽑아 라벨링할 수 있게 해준다.
- **Existing labels**: 이미 매겨진 모든 라벨을 보여주고, 필요하면 수정할 수 있게 해준다.

필요하면 왼쪽 위 버튼(가로줄 3개)을 눌러 링크 목록을 숨기거나 보이게 할 수 있다. 가장 많은 시간을 쓰게 되는 곳은 **Label new data** 화면인데, Figure 19.4에서 볼 수 있다.

![[fig_19_4.png]]
*그림 19.4 — 새 라벨을 매기는 화면. 왼쪽에는 무작위로 뽑힌 20개의 조각 쌍 목록, 오른쪽에는 선택된 쌍의 두 영상(움직이는 GIF)과 세 개의 판단 버튼이 보인다.*

여기에는 라벨링할 수 있는 20개의 무작위 조각 쌍 목록이 있다. 목록에서 항목을 선택하면 인터페이스가 두 조각을 (즉석에서 생성되는 움직이는 GIF로) 보여준다. 사용자는 세 버튼 중 하나를 눌러 라벨을 매길 수 있다.

- **#1 IS BETTER (1)**: 첫 번째 조각을 선호로 표시. 학습 시 $\mu_1 = 1.0, \mu_2 = 0.0$ 이 된다.
- **BOTH ARE GOOD (0)**: 둘 다 똑같이 좋다(혹은 나쁘다)로 표시. $\mu_1 = 0.5, \mu_2 = 0.5$.
- **#2 IS BETTER (2)**: 두 번째 조각을 선호로 표시. $\mu_1 = 0.0, \mu_2 = 1.0$.

버튼을 클릭하는 대신 키보드의 `0`("둘 다 좋음"), `1`("첫 번째가 나음"), `2`("두 번째가 나음") 키로도 라벨을 매길 수 있다. 라벨이 매겨지면 UI는 자동으로 목록의 다음 미라벨 항목을 선택하므로, 키보드만으로 라벨링 작업을 계속 진행할 수 있다. 목록의 모든 항목을 다 라벨링했다면 **RESAMPLE LIST** 버튼을 눌러 새로운 20개 표본을 불러올 수 있다.

버튼 클릭이나 키 입력으로 매겨진 라벨은 DB 디렉터리 루트의 `labels.json` 파일에 저장된다. 이 파일은 매 줄이 하나의 항목(두 조각의 경로와 매겨진 라벨)인 트리비얼한 JSON-line 형식이다.

```
Chapter19$ head db-v0/labels.json
{"sample1":"14/00023925.dat","sample2":"10/00606788.dat","label":0}
{"sample1":"02/01966114.dat","sample2":"10/01667833.dat","label":2}
{"sample1":"00/02432057.dat","sample2":"06/01410909.dat","label":1}
...
```

필요하다면 **Existing labels** 링크로 기존 라벨을 검토할 수 있다(Figure 19.5). Label new data와 거의 같은 인터페이스지만, 새 20개 쌍을 뽑는 대신 이미 라벨된 쌍들을 보여준다.

![[fig_19_5.png]]
*그림 19.5 — 기존 라벨을 검토·수정하는 화면. 목록 왼쪽 열에 현재 매겨진 라벨 값(0/1/2)이 표시된다.*

앞서 설명한 버튼이나 키보드 단축키로 이 쌍들의 라벨도 바꿀 수 있다.

실험 중 저자는 첫 라운드로 100쌍을 라벨링했는데, 잠수함이 수면 위에 있는 (드물게 발생하는) 상황에는 특히 신경 써서 "좋음"으로 표시했고, 산소가 낮은 (자주 발생하는) 상황은 "나쁨"으로 표시했다. 그 외 상황에서는 물고기를 제대로 맞춘 조각을 선호했다. 이렇게 손에 몇 개의 라벨이 생겼으니, 다음 단계인 보상 모델 학습으로 넘어갈 준비가 되었다.

### 3.3 보상 모델 학습

보상 모델 신경망의 구조는 대부분 논문에서 그대로 가져왔지만, **행동을 다루는 방식**이 다르다. 논문에서는 저자들이 행동을 어떻게 반영하는지 구체적으로 밝히지 않고 그저 "보상 예측기에는 정책의 입력과 같은 84×84 이미지를 쓰고, 4프레임을 쌓아 84×84×4 텐서를 입력으로 사용한다"고만 언급했다. 이로부터 저자는 보상 모델이 프레임 간의 "역학(dynamics)"으로부터 행동을 **암묵적으로** 유추한다는 가정을 세웠다. 하지만 이 방식은 직접 시도해보지 않았고, 대신 합성곱 계층에서 얻은 벡터에 행동의 [[원-핫 인코딩]]을 이어 붙여(concatenate) **명시적으로** 신경망에 행동을 보여주기로 했다. 연습 삼아, 논문의 방식대로 코드를 바꿔서 결과를 비교해보는 것도 좋다.

나머지 구조와 학습 파라미터는 논문과 동일하다. 보상 모델 신경망 코드를 살펴보자.

```python
class RewardModel(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 16, kernel_size=7, stride=3),
            nn.BatchNorm2d(16),
            nn.Dropout(p=0.5),
            nn.LeakyReLU(),
            nn.Conv2d(16, 16, kernel_size=5, stride=2),
            nn.BatchNorm2d(16),
            nn.Dropout(p=0.5),
            nn.LeakyReLU(),
            nn.Conv2d(16, 16, kernel_size=3, stride=1),
            nn.BatchNorm2d(16),
            nn.Dropout(p=0.5),
            nn.LeakyReLU(),
            nn.Conv2d(16, 16, kernel_size=3, stride=1),
            nn.BatchNorm2d(16),
            nn.Dropout(p=0.5),
            nn.LeakyReLU(),
            nn.Flatten(),
        )
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.out = nn.Sequential(
            nn.Linear(size + n_actions, 64),
            nn.LeakyReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, obs: torch.ByteTensor, acts: torch.Tensor) -> torch.Tensor:
        conv_out = self.conv(obs / 255)
        comb = torch.hstack((conv_out, acts))
        out = self.out(comb)
        return out
```

한 줄씩 짚어보자.
- `self.conv`: 네 개의 합성곱 층이 쌓여 있는데, 매 합성곱 뒤에 [[배치 정규화와 드롭아웃|BatchNorm2d와 Dropout(p=0.5)]]이 따라오고, 활성화 함수로는 (음수 구간에도 작은 기울기를 남겨두는) `LeakyReLU`를 쓴다. 데이터가 적은 만큼(라벨이 겨우 몇백 개) 과적합을 막는 장치들이 층마다 촘촘히 들어간 셈이다.
- `size = self.conv(torch.zeros(1, *input_shape)).size()[-1]`: 더미 입력을 한 번 흘려서 합성곱 출력의 크기를 자동으로 계산한다. 매번 손으로 크기를 계산하지 않아도 되는 실용적인 트릭이다.
- `self.out`: 합성곱에서 나온 특징 벡터(`size` 차원)에 행동의 원-핫 벡터(`n_actions` 차원)를 **이어붙인 뒤**, 두 개의 선형 층을 거쳐 실수 값 하나를 뽑아낸다.
- `forward()`: `obs / 255`로 픽셀 값을 0~1 범위로 정규화하고, 합성곱 결과(`conv_out`)와 행동(`acts`)을 `torch.hstack`으로 가로 방향(같은 행, 다른 열)으로 이어붙인 다음(`comb`), 최종 출력을 계산한다.

보상 모델의 학습은 `03_reward_train.py`에 구현되어 있고 복잡한 내용은 없다. JSON 파일에서 라벨링된 데이터를 읽어들이고(커맨드라인에 여러 DB를 넘겨 학습에 함께 쓸 수 있다), 데이터의 20%를 테스트용으로 떼어두고, `calc_loss()` 함수에서 이진 교차 엔트로피 목적함수를 계산한다.

```python
def calc_loss(model: rlhf.RewardModel, s1_obs: torch.ByteTensor,
              s1_acts: torch.Tensor, s2_obs: torch.ByteTensor,
              s2_acts: torch.Tensor, mu: torch.Tensor) -> torch.Tensor:
    batch_size, steps = s1_obs.size()[:2]
    s1_obs_flat = s1_obs.flatten(0, 1)
    s1_acts_flat = s1_acts.flatten(0, 1)
    r1_flat = model(s1_obs_flat, s1_acts_flat)
    r1 = r1_flat.view((batch_size, steps))
    R1 = torch.sum(r1, 1)

    s2_obs_flat = s2_obs.flatten(0, 1)
    s2_acts_flat = s2_acts.flatten(0, 1)
    r2_flat = model(s2_obs_flat, s2_acts_flat)
    r2 = r2_flat.view((batch_size, steps))
    R2 = torch.sum(r2, 1)

    R = torch.hstack((R1.unsqueeze(-1), R2.unsqueeze(-1)))
    loss_t = F.binary_cross_entropy_with_logits(R, mu)
    return loss_t
```

이 함수를 한 단계씩 이해해보자.

- 처음에 관측·행동 텐서는 `(batch, time, colors, height, width)`(관측)와 `(batch, time, actions)`(행동) 형태를 갖는다. 여기서 `time`은 조각 안의 스텝 순서를 나타내는 차원이다. 구체적으로 관측 텐서는 $64 \times 50 \times 3 \times 210 \times 160$, 행동 텐서는 $64 \times 50 \times 18$ 크기다. (배치 64개, 조각 길이 50스텝, 컬러 3채널, $210\times160$ 화면, 행동 18가지)
- `s1_obs.flatten(0, 1)`: 손실 계산의 첫 단계로, 배치와 시간 두 차원을 하나로 합쳐(flatten) **시간 차원을 없앤다**. 그래야 신경망에 한 번에 넣어 보상 값 $\hat{r}(o,a)$ 을 계산할 수 있다.
- `r1 = r1_flat.view((batch_size, steps))` 그리고 `R1 = torch.sum(r1, 1)`: 시간 차원을 다시 복원한 뒤, 논문 공식대로 그 차원을 따라 **합산**한다. 이것이 세그먼트 전체의 총점 $\sum \hat{r}(o_t,a_t)$ 이다.
- `R = torch.hstack((R1.unsqueeze(-1), R2.unsqueeze(-1)))`: 두 세그먼트의 총점을 나란히 붙여 하나의 텐서로 만든다.
- `F.binary_cross_entropy_with_logits(R, mu)`: 이 텐서에 파이토치의 이진 교차 엔트로피 함수를 적용해 손실을 계산한다. `_with_logits`가 붙은 버전을 쓰는 이유는, 앞서 본 소프트맥스-비율 식(지수화 후 정규화)을 시그모이드/소프트맥스와 수학적으로 동치인 형태로 이 함수가 내부에서 안정적으로 계산해주기 때문이다.

매 에포크마다 테스트 손실(데이터의 20%로 계산)을 구하고, 새 손실이 이전 최솟값보다 낮으면 보상 모델을 저장한다. 훈련 손실이 4에포크 연속으로 (테스트 손실 최소치보다) 나아지지 않으면 학습을 멈춘다.

앞서 정한 라벨 수(몇백 개)라면 학습은 매우 빠르다 — 십여 에포크, 몇 분 정도면 끝난다. 다음은 학습 과정의 예시다. `-o` 옵션은 최고 모델이 저장될 디렉터리 이름을 지정한다.

```
Chapter19$ ./03_reward_train.py --dev cuda -n v0-rw -o rw db-v0
Namespace(dev='cuda', name=v0-rw', out='rw', dbs=['db-v0'])
Loaded DB from db-v0 with 149 labels and 2534 paths
...
Epoch 0 done, train loss 0.131852, test loss 0.132976
Save model for 0.13298 test loss
Epoch 1 done, train loss 0.104426, test loss 0.354560
Epoch 2 done, train loss 0.159513, test loss 0.170160
Epoch 3 done, train loss 0.054362, test loss 0.066557
Save model for 0.06656 test loss
Epoch 4 done, train loss 0.046695, test loss 0.121662
Epoch 5 done, train loss 0.055446, test loss 0.064895
Save model for 0.06490 test loss
Epoch 6 done, train loss 0.024505, test loss 0.025308
Save model for 0.02531 test loss
Epoch 7 done, train loss 0.015864, test loss 0.045814
Epoch 8 done, train loss 0.024745, test loss 0.054631
Epoch 9 done, train loss 0.027670, test loss 0.054107
Epoch 10 done, train loss 0.025979, test loss 0.048673
Best test loss was less than current for 4 epoches, stop
```

149개 라벨, 2,534개 조각 경로를 불러왔고, 6번째 에포크에서 테스트 손실 0.02531로 최저를 찍은 뒤, 4에포크 연속으로 개선이 없어 학습이 멈춘 걸 볼 수 있다.

### 3.4 A2C와 보상 모델 결합하기

보상 모델을 학습시켰으니, 이제 드디어 RL 학습에 이걸 써볼 차례다. 같은 도구 `01_a2c.py`를 쓰지만, 몇 가지 추가 인자를 준다.

- `-r` 또는 `--reward`: 사용할 보상 모델의 경로. 이 옵션을 주면 환경의 보상 대신, **관측과 우리가 취한 행동으로부터 이 모델이 계산한 보상**을 쓴다. 추가 환경 래퍼로 구현되어 있으며, 곧 살펴본다.
- `-m` 또는 `--model`: 불러올 액터 모델(이전 A2C 학습 라운드에서 저장된)의 경로. 처음부터 새로 학습하는 대신 RLHF로 미세조정을 하는 것이므로 액터 모델이 필요하다. 원칙적으로는 보상 모델로 처음부터 학습을 시도해볼 수도 있지만, 저자의 실험에서는 그리 성공적이지 않았다.
- `--finetune`: 미세조정 모드를 켠다. 합성곱 층이 얼려지고(freeze) 학습률이 10배 낮아진다. 이런 조정이 없으면 액터가 매우 빠르게 기존에 배운 모든 것을 잊어버리고 보상이 거의 0으로 떨어진다. (자세한 원리는 [[정책 미세조정 Fine-tuning]] 참고)

방금 학습시킨 보상 모델을 쓰려면 명령줄은 다음과 같은 모습이다.

```
./01_a2c.py --dev cuda -n v1 -r rw/reward-v0.dat --save save/v1 -m save/v0/model_rw=460-steps=580.dat --finetune
```

결과를 확인하기 전에, 보상 모델이 RL 학습 과정에서 어떻게 쓰이는지 먼저 살펴보자. 변경을 최소화하기 위해, 저자는 **환경 래퍼**로 구현했다. 이 래퍼는 원본 환경과 아타리 래퍼 사이에 끼워지는데, 보상 모델은 스케일이 조정되지 않은(unscaled) 원본 컬러 화면 이미지를 필요로 하기 때문이다.

이 래퍼의 코드는 `lib/rlhf.py`에 있고 `RewardModelWrapper`라 불린다. 래퍼의 생성자는 데이터 파일에서 모델을 불러오고 몇 가지 필드를 설정한다. 논문에 따르면 보상 모델이 예측한 보상은 **평균 0, 분산 1이 되도록 정규화**되므로, 래퍼는 정규화를 위해 최근 100개의 보상을 `collections.deque`에 저장해둔다. 정규화 외에도, 래퍼는 지표(metric)를 보낼 큐(queue)를 가질 수 있다. 이 지표에는 정규화 값들과, 실제 원본 환경의 보상 합계 정보가 담긴다.

```python
class RewardModelWrapper(gym.Wrapper):
    KEY_REAL_REWARD_SUM = "real_reward_sum"
    KEY_REWARD_MU = "reward_mu"
    KEY_REWARD_STD = "reward_std"

    def __init__(self, env: gym.Env, model_path: pathlib.Path, dev: torch.device,
                 reward_window: int = 100, metrics_queue: tt.Optional[queue.Queue] = None):
        super().__init__(env)
        self.device = dev
        assert isinstance(env.action_space, gym.spaces.Discrete)
        s = env.observation_space.shape
        self.total_actions = env.action_space.n
        self.model = RewardModel(
            input_shape=(s[2], s[0], s[1]), n_actions=self.total_actions)
        self.model.load_state_dict(torch.load(model_path,
            map_location=torch.device('cpu'), weights_only=True))
        self.model.eval()
        self.model.to(dev)
        self._prev_obs = None
        self._reward_window = collections.deque(maxlen=reward_window)
        self._real_reward_sum = 0.0
        self._metrics_queue = metrics_queue
```

`self.model.eval()`을 호출하는 이유를 눈여겨보자. 앞서 배운 [[배치 정규화와 드롭아웃]] 을 여기서 끄는 것이다 — 학습이 아니라 **추론(inference)**용이니, 무작위로 뉴런을 꺼버리는 드롭아웃도, 배치마다 통계를 다시 계산하는 배치정규화도 켜져 있으면 안 된다.

`reset()` 메서드에서는 관측을 기억해두고 보상 카운터를 리셋한다.

```python
def reset(self, *, seed: int | None = None, options: dict[str, tt.Any] | None = None) \
        -> tuple[WrapperObsType, dict[str, tt.Any]]:
    res = super().reset(seed=seed, options=options)
    self._prev_obs = deepcopy(res[0])
    self._real_reward_sum = 0.0
    return res
```

래퍼의 핵심 로직은 `step()` 함수에 있는데, 이것도 그렇게 복잡하지 않다 — 모델을 관측과 행동에 적용하고, 보상을 정규화한 뒤, 원래 보상 대신 이 값을 반환한다. 모델 적용은 성능 측면에서 그리 효율적이지 않고(여러 환경이 병렬로 돌아가는 상황이라) 최적화할 여지가 있지만, 저자는 우선 단순한 버전을 구현하고 최적화는 독자를 위한 연습 문제로 남겨두었다.

```python
def step(self, action: WrapperActType) -> tuple[
        WrapperObsType, SupportsFloat, bool, bool, dict[str, tt.Any]
]:
    obs, r, is_done, is_tr, extra = super().step(action)
    self._real_reward_sum += r
    p_obs = np.moveaxis(self._prev_obs, (2, ), (0, ))
    p_obs_t = torch.as_tensor(p_obs).to(self.device)
    p_obs_t.unsqueeze_(0)

    act = np.eye(self.total_actions)[[action]]
    act_t = torch.as_tensor(act, dtype=torch.float32).to(self.device)
    new_r_t = self.model(p_obs_t, act_t)
    new_r = float(new_r_t.item())

    # track reward for normalization
    self._reward_window.append(new_r)
    if len(self._reward_window) == self._reward_window.maxlen:
        mu = np.mean(self._reward_window)
        std = np.std(self._reward_window)
        new_r -= mu
        new_r /= std
        self._metrics_queue.put((self.KEY_REWARD_MU, mu))
        self._metrics_queue.put((self.KEY_REWARD_STD, std))
    if is_done or is_tr:
        self._metrics_queue.put((self.KEY_REAL_REWARD_SUM, self._real_reward_sum))
    self._prev_obs = deepcopy(obs)
    return obs, new_r, is_done, is_tr, extra
```

한 줄씩 짚어보자.
- `obs, r, is_done, is_tr, extra = super().step(action)`: 원본 환경의 진짜 보상 `r`을 얻는다(이건 오직 지표 추적용으로만 쓰이고, 실제 학습에는 쓰이지 않는다).
- `p_obs = np.moveaxis(self._prev_obs, (2,), (0,))`: 이미지의 채널 축 순서를 파이토치가 기대하는 형태(채널이 맨 앞)로 바꾼다.
- `act = np.eye(self.total_actions)[[action]]`: `np.eye`로 단위 행렬을 만들고 행동 인덱스로 그 행을 뽑아, 행동의 [[원-핫 인코딩]] 벡터를 만든다.
- `new_r_t = self.model(p_obs_t, act_t)`: 이전 관측과 지금 행동을 보상 모델에 넣어 예측 보상을 얻는다.
- `self._reward_window`에 최근 100개 보상을 쌓아두고, 창이 다 차면 평균 `mu`와 표준편차 `std`로 **정규화**(`new_r -= mu; new_r /= std`)한다. 논문에서 요구한 "평균 0, 분산 1" 정규화가 바로 이것이다.
- 에피소드가 끝나면(`is_done or is_tr`) 진짗값 보상 합계를 지표 큐에 실어 보낸다 — 사람이 볼 수 있게 TensorBoard 등에 기록하기 위해서다.
- 마지막으로 원래 보상 `r` 대신 정규화된 예측 보상 `new_r`을 반환한다. **이 반환값이 이제부터 A2C 학습이 실제로 사용하는 보상**이다.

나머지 학습 과정은 동일하다. 커맨드라인에 보상 모델 파일이 주어지면, 환경 생성 함수에 이 새 래퍼를 끼워 넣기만 하면 된다.

```python
def make_env() -> gym.Env:
    e = gym.make("SeaquestNoFrameskip-v4")
    if reward_path is not None:
        p = pathlib.Path(reward_path)
        e = rlhf.RewardModelWrapper(e, p, dev=dev, metrics_queue=metrics_queue)
    if db_path is not None:
        p = pathlib.Path(db_path)
        p.mkdir(parents=True, exist_ok=True)
        e = rlhf.EpisodeRecorderWrapper(e, p, env_idx=env_idx)
    e = ptan.common.wrappers.wrap_dqn(e)
    # add time limit after all wrappers
    e = gym.wrappers.TimeLimit(e, TIME_LIMIT)
    return e
```

이 코드로, 이제 앞서 만든 라벨들과 이전 모델을 결합할 수 있다.

---

## 4. 라벨 100개로 미세조정하기

기본 A2C 학습에서 얻은 최고 모델(테스트에서 580스텝에 460점을 낸 모델)로 학습을 진행했다. 추가로 새 DB 디렉터리(`v1`)에 에피소드 조각을 샘플링하도록 켰다. 전체 명령줄은 다음과 같다.

```
./01_a2c.py --dev cuda -n v1 -r rw/reward-v0.dat --save save/v1 -m save/v0/model_rw=460-steps=580.dat --finetune --db-path v1
```

이 모델은 꽤 빨리 과적합되기 시작해서, 200만 스텝(3시간) 후 학습을 멈췄다. Figure 19.6은 테스트 결과(보상과 스텝 수)를 보여준다.

![[fig_19_6.png]]
*그림 19.6 — 미세조정 중 테스트 보상(왼쪽)과 스텝 수(오른쪽)*

Figure 19.7은 훈련 보상(모델이 예측한 값)과 전체 손실을 보여준다.

![[fig_19_7.png]]
*그림 19.7 — 미세조정 중 훈련 보상(왼쪽, 모델이 예측한 값)과 전체 손실(오른쪽)*

최고 모델은 50만 학습 스텝에서 저장되었고, 1,120스텝 동안 900점의 보상을 냈다. 원래 모델과 비교하면 꽤 큰 개선이다.

이 모델의 영상 녹화는 https://youtu.be/LnPwuyVrj9g 에서 볼 수 있다. 플레이를 보면, 에이전트가 산소를 채우는 법을 배웠고, 이제 화면 중간에서 시간을 보내고 있다는 걸 알 수 있다. 저자는 또한 잠수부를 좀 더 의도적으로 줍는 것 같다는 인상을 받았다(다만 이 행동을 위한 라벨링을 특별히 하지는 않았다). 전반적으로 이 방법은 잘 작동하며, 단 100개의 라벨만으로 에이전트에게 새로운 것을 가르칠 수 있다는 게 꽤 인상적이다.

더 많은 라벨링으로 모델을 개선해보자.

### 4.1 실험 2라운드

두 번째 라운드에서는 더 많은 라벨링을 했다 — v0 DB에서 50쌍, 미세조정 중 저장된 조각(v1 DB)에서 50쌍. 미세조정 중 생성된 데이터베이스(v1)에는 잠수함이 수면에 떠 있는 조각이 훨씬 많이 담겨 있었는데, 이는 우리 파이프라인이 기대한 대로 작동하고 있다는 확인이 된다. 라벨링 중에는 산소 재충전 조각에 더 무게를 실었다.

라벨링 후 보상 모델을 재학습했는데, 몇 분밖에 걸리지 않았다. 그다음 최고 v1 모델(보상 900, 1,120스텝)을 이 보상 모델로 다시 미세조정했다.

Figure 19.8과 Figure 19.9는 테스트 결과, 훈련 보상, 손실을 담은 그래프다.

![[fig_19_8.png]]
*그림 19.8 — 2라운드 미세조정 중 테스트 보상(왼쪽)과 스텝 수(오른쪽)*

![[fig_19_9.png]]
*그림 19.9 — 2라운드 미세조정 중 훈련 보상(왼쪽)과 전체 손실(오른쪽)*

150만 스텝(2시간) 후 학습이 정체됐는데, 최고 모델은 v1의 최고 모델보다 나아지지 않았다 — 최고 모델은 1,084스텝 동안 860점을 기록했다.

### 4.2 실험 3라운드

여기서는 라벨링 중 산소 재충전뿐 아니라 물고기 사격과 잠수부 수거에도 더 신경을 썼다. 아쉽게도 100쌍 중 잠수부가 등장하는 예시는 몇 개뿐이라, 이 행동을 제대로 가르치려면 더 많은 라벨링이 필요해 보인다.

> [!note] 잠수부가 잘 안 보이는 이유
> 잠수부를 잘 줍지 못하는 것은, 배경과 잘 구분되지 않아서일 수도 있다 — 흑백(grayscale) 이미지에서는 거의 보이지 않기 때문이다. 이를 고치려면 아타리 래퍼의 대비(contrast)를 조정해볼 수 있다.

보상 모델 재학습 후 A2C 미세조정을 시작했다. 이번에도 약 200만 스텝, 3시간 동안 돌렸는데 결과가 흥미로웠다. 학습 마지막에는(Figure 19.10과 19.11 참고) 테스트 중 보트가 (환경에 설정한 한계인) 5,000스텝에 도달했지만, 점수는 꽤 낮았다. 아마도 잠수함이 그냥 수면에만 계속 머물러 있었을 것이다 — 매우 안전하지만 우리가 원하는 행동은 아니다. 라벨링된 샘플 때문일 수 있다. 이상하게도, 이후 모델들의 영상을 녹화해보니 행동이 달라져 있었고 스텝 수도 훨씬 낮았는데, 이는 테스트 과정에 어떤 버그가 있었다는 걸 암시할 수도 있다.

![[fig_19_10.png]]
*그림 19.10 — 3라운드 미세조정 중 테스트 보상(왼쪽)과 스텝 수(오른쪽)*

![[fig_19_11.png]]
*그림 19.11 — 3라운드 미세조정 중 훈련 보상(왼쪽)과 전체 손실(오른쪽)*

과적합이 일어나기 전, 학습 과정은 v2 모델들보다 더 나은 여러 정책을 만들어냈다. 예를 들어 다음 녹화에서는, 에이전트가 산소를 두 번 채우고 1,613스텝 동안 1,820점을 기록했다: https://youtu.be/DVe_9b3gdxU

### 4.3 전체 결과 정리

다음 표는 실험 라운드별 정보와 결과를 정리한 것이다.

| 단계 | 라벨 수 | 보상 | 스텝 | 영상 |
|---|---|---|---|---|
| Initial (v0) | 없음 | 460 | 580 | https://youtu.be/R_H3pXu-7cw |
| v1 | 100 | 900 | 1,120 | https://youtu.be/LnPwuyVrj9g |
| v2 | 200 | 860 | 1,083 | — |
| v3 | 300 | 1,820 | 1,613 | https://youtu.be/DVe_9b3gdxU |

*표 19.1 — 실험 라운드 요약*

보다시피, **단 300개의 라벨만으로 점수를 거의 4배 가까이 끌어올릴 수 있었다.** 연습 문제로, 잠수부를 줍도록 에이전트를 가르쳐보길 권한다 — 제대로 해낸다면 훨씬 좋은 점수를 얻을 수도 있을 것이다. 또 하나 해볼 만한 실험은, 이전 단계의 최고 모델이 아니라 **원래의 v0 모델을 기준으로 미세조정**하는 것이다. 과적합이 일어나기 전까지 학습 시간을 더 확보할 수 있으므로 더 나은 결과로 이어질 수도 있다.

---

## 5. 요약

이 챕터에서는 RL 도구 상자의 최근 추가 항목인 RLHF를 살펴봤다. 이 방법은 LLM 학습 파이프라인의 핵심에 있으며, 모델의 품질을 끌어올릴 수 있게 해준다. 챕터에서는 RLHF를 직접 구현해 SeaQuest 아타리 게임에 적용해봤는데, 이를 통해 이 방법이 RL 파이프라인에서 모델 개선에 어떻게 쓰일 수 있는지 확인할 수 있었다.

정리하면:
1. **보상 함수를 명시적으로 정의하기 어려운 문제**가 실제로 매우 흔하다는 것을 확인했다(챗봇 말투, 운송 규칙, SeaQuest의 산소·잠수부 문제 등).
2. **RLHF의 핵심 구조** — RL 학습, 사람 라벨링, 보상 모델 학습이 맞물려 돌아가는 순환 구조 — 를 배웠다.
3. 두 세그먼트의 선호를 확률로 바꾸는 수식(소프트맥스와 동일 구조인 브래들리-테리 모델)과, 이를 교차 엔트로피 손실로 학습시키는 과정을 유도했다.
4. **LLM 학습의 3단계**(사전학습 → 지도 미세조정 → RLHF 미세조정=정렬) 중 RLHF가 차지하는 역할을 이해했다.
5. SeaQuest 환경에서 **에피소드 조각 기록 → 웹 UI 라벨링 → 보상 모델 학습 → 미세조정**의 전체 파이프라인을 직접 구현하고, 겨우 300개의 라벨로 점수를 4배 가까이 끌어올리는 것을 확인했다.

다음 챕터에서는 완전히 다른 계열의 RL 방법 — AlphaGo, AlphaZero, MuZero를 다룬다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[RLHF 인간 피드백 강화학습]]
- [[선호 기반 보상 모델과 브래들리-테리 모델]]
- [[정책 미세조정 Fine-tuning]]
- [[배치 정규화와 드롭아웃]]
- [[교차 엔트로피 Cross-Entropy]]
- [[소프트맥스 Softmax]]
- [[원-핫 인코딩]]
- [[데이터클래스 dataclass]]
- [[Wrapper 래퍼 패턴]]
- [[과적합과 검증데이터]]

## 한눈에 보는 개념 지도
| 개념 | 기호/코드 | 한 줄 뜻 |
|---|---|---|
| 보상 예측기 | $\hat{r}(o,a)$ | 관측·행동을 받아 예측 보상을 내는 신경망 |
| 에피소드 조각 | $\sigma$ | 고정 길이(50스텝)의 (관측, 행동) 나열 |
| 선호 라벨 | $\mu_1, \mu_2$ | 사람이 어느 조각을 선호했는지 나타내는 값(0/0.5/1) |
| 선호 확률 | $\hat{P}[\sigma_1 \succ \sigma_2]$ | 두 조각 점수의 소프트맥스 비율 |
| 손실 함수 | $\text{loss}(\hat{r})$ | 라벨과 예측 확률 사이의 교차 엔트로피 |
| 에피소드 기록 래퍼 | `EpisodeRecorderWrapper` | 무작위로 조각을 뽑아 DB에 저장하는 Gym 래퍼 |
| 보상 모델 래퍼 | `RewardModelWrapper` | 환경 보상을 학습된 $\hat{r}$ 값으로 바꿔치기하는 Gym 래퍼 |
| 미세조정 | `--finetune` | 합성곱 층 동결 + 학습률 10배 감소로 기존 지식 보존 |
| LLM 정렬 단계 | RLHF fine-tuning | 사전학습·지도미세조정 다음의 3번째 LLM 학습 단계 |
