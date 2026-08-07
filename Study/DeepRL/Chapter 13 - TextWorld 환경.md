---
title: "Chapter 13 — TextWorld 환경 (The TextWorld Environment)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 13
tags: [DeepRL, 강화학습, NLP, TextWorld, DQN, RNN, LSTM, Transformer, LLM]
---

# Chapter 13 · TextWorld 환경

> [!abstract] 이 챕터를 한 문장으로
> **텍스트로만 이루어진 어드벤처 게임**(인터랙티브 픽션)을 강화학습으로 풀어보면서, 이미지가 아니라 **글**을 관측(observation)으로 다뤄야 하는 문제 — 즉 딥러닝 자연어 처리(NLP)의 기본기(RNN, LSTM, 임베딩, 트랜스포머)를 배우고, 마지막엔 ChatGPT 같은 LLM으로 같은 문제를 풀어본다.

---

## 들어가며 — 왜 텍스트 게임인가?

지금까지 이 책에서 다룬 게임은 대부분 Atari처럼 **이미지(픽셀)** 를 관측으로 받는 게임이었다. 하지만 게임 장르는 그 외에도 무수히 많다. 이 챕터는 "얼마나 어려운 게임을 골라야 RL 연구에 적당할까?"라는 질문에서 출발한다.

> [!note] 게임 난이도의 딜레마
> - Atari 2600 게임들은 이제 대부분의 연구자가 손쉽게 학습시킬 수 있을 만큼 다뤄졌다.
> - 반대로 StarCraft II나 Dota 같은 게임은 너무 복잡해서, DeepMind조차 수 주간 GPU 클러스터를 돌려야 했다. 보통 연구자에게는 너무 비싸다.
> - 그래서 "중간 난이도"를 찾는 몇 가지 전략이 있다: ① Z80·NES·Sega·C64 같은 옛날 콘솔의 수천 개 게임을 쓰거나, ② Doom처럼 복잡한 게임 엔진은 그대로 두되 목표만 단순화(복도 이동, 무기 줍기 등 microgame)하거나, ③ **그림은 단순하지만 장기 계획과 복잡한 탐색이 필요한 게임**을 고른다.

세 번째 방식의 대표 예가 Atari의 악명 높은 **Montezuma's Revenge**다. 그리고 이와 같은 계열에 있는 것이 이번 챕터의 주인공, **텍스트 기반 게임(인터랙티브 픽션)** 이다. 그래픽 대신 오직 **텍스트**로 게임 상태를 전달하고, 플레이어도 텍스트 명령으로만 반응한다.

---

## 1. 인터랙티브 픽션(Interactive Fiction) — 역사

가장 오래된 예시는 1976년작 **Adventure**(어드벤처) 게임이다. 화면에는 다음과 같은 글이 뜬다:

> *"You are standing at the end of a road before a small brick building. Around you is a forest. A small stream flows out of the building and down a gully."* (당신은 작은 벽돌 건물 앞, 길의 끝에 서 있다. 주위는 숲이고, 건물에서 작은 개울이 흘러나와 협곡으로 내려간다.)

플레이어는 "verb + noun"(동사 + 명사) 형태의 짧은 명령, 예를 들어 `go down`(아래로 가라) 같은 텍스트를 입력해 게임을 진행한다.

![[fig_13_1.png]]
*그림 13.1 — 인터랙티브 픽션 게임 진행 예시. 화면에 글로 상황이 설명되고, 플레이어가 `>` 프롬프트에 명령을 입력한다*

> [!tip] 비유 — 그림 없는 방탈출
> 인터랙티브 픽션은 "방탈출 게임을 오직 글로만 진행하는 것"과 비슷하다. 눈으로 방을 볼 수 없으니, 안내문("문이 하나 있고 잠겨 있다")을 읽고 머릿속으로 상상하며 "열쇠로 문을 연다" 같은 문장으로 행동을 지시해야 한다. 그래픽 카드가 변변찮던 1970~80년대에는 이 방식이 최선이었다.

80~90년대에는 개인 개발자와 상업 스튜디오가 만든 수백 개의 크고 작은 게임이 나왔다. 그중 일부는 수 시간의 플레이타임, 수천 개의 장소, 수많은 상호작용 대상 물건을 담고 있었다. 대표적으로 **Zork I**(1980년, Infocom)의 지도를 보면 그 규모를 짐작할 수 있다.

![[fig_13_2.png]]
*그림 13.2 — Zork I의 지하 세계 지도 일부. 수십 개의 방과 통로로 이루어진 큰 세계다*

이런 게임의 난이도는 사실상 무한히 키울 수 있다 — 물건 사이의 복잡한 상호작용, 게임 상태 탐색, 다른 캐릭터와의 대화 등 현실적인 요소를 얼마든지 추가할 수 있기 때문이다. 이런 고전 게임들은 지금도 [Interactive Fiction Archive](http://ifarchive.org)에서 만나볼 수 있다.

---

## 2. TextWorld 환경 소개

2018년 6월, Microsoft Research는 RL 연구자와 애호가들이 텍스트 게임을 손쉽게 실험할 수 있도록 **TextWorld**라는 오픈소스 프로젝트를 공개했다([GitHub](https://github.com/microsoft/TextWorld)). 주요 기능은 다음과 같다.

- **텍스트 게임용 Gym 환경**: Z-machine 바이트코드(버전 1~8)와 Glulx 게임 두 형식을 지원한다.
- **게임 생성기**: 물건 개수, 설명, 퀘스트 길이 같은 조건을 지정해 **무작위 생성 퀘스트**를 만들 수 있다.
- **난이도 조절 기능**: 생성된 게임의 내부 상태를 살짝 엿볼 수 있게 해서 복잡도를 조절할 수 있다. 예를 들어 에이전트가 올바른 방향으로 한 걸음 나아갈 때마다 **중간 보상(intermediate reward)** 을 줄 수 있다.

> [!example] 실습 준비
> 이 챕터에서는 여러 게임으로 실습하며 여러 버전의 학습 코드를 실행해 본다. `Chapter13/game/make_games.sh` 스크립트로 게임을 미리 생성해야 하며, 이 스크립트는 서로 다른 시드값으로 **길이 5짜리 게임 21개**를 만든다. 복잡도가 아주 높진 않지만, 실험과 아이디어 검증의 기반으로 쓰기에는 충분하다.

### 2.1 환경 설치

TextWorld는 (이 책 집필 시점 기준) Linux와 macOS만 공식 지원한다(윈도우는 Docker 컨테이너로 우회 가능). 내부적으로는 [Inform 7](https://inform7.com) 시스템에 의존한다.

설치는 간단하다.

```bash
pip install textworld==1.6.1
```

설치하면 파이썬 코드에서 바로 임포트해 쓸 수 있고, 커맨드라인 도구 두 개(`tw-make`, `tw-play`)도 함께 제공된다. 이 둘은 [ifarchive.org](http://ifarchive.org)에 있는 완성형 게임을 직접 풀 게 아니라면 꼭 필요하진 않지만, 이 챕터에서는 간단함을 위해 **인위적으로 생성한 퀘스트**로 시작한다.

### 2.2 게임 생성 — `tw-make`

`tw-make` 유틸리티로 다음과 같은 특성을 지정해 게임을 생성할 수 있다.

- **게임 시나리오**: 물건을 찾고 순서대로 행동하는 고전적인 퀘스트, 또는 동전을 모으며 장면을 이동하는 "coin collection" 시나리오
- **게임 테마**: 현재는 "house"(집)와 "basic"(기본) 두 가지만 존재
- **물건 속성**: "key"(열쇠)가 아니라 "green key"(초록 열쇠)처럼 형용사를 붙일 수 있음
- **병렬 퀘스트 개수**: 기본은 하나의 행동 순서만 존재하지만, 여러 개의 하위 목표·대체 경로를 허용하도록 바꿀 수 있음
- **퀘스트 길이**: 목표에 도달하기까지 필요한 스텝 수
- **랜덤 시드**: 재현 가능한 게임을 만들 때 사용

생성된 게임은 Glulx나 Z-machine 포맷으로 나오는데, 둘 다 표준 가상 머신 명령어라서 여러 인터랙티브 픽션 인터프리터에서 일반 게임처럼 플레이할 수 있다.

```bash
$ tw-make tw-coin_collector --output t1 --seed 10 --level 5 --format ulx
Global seed: 10
Game generated: t1.ulx
```

이 명령은 `t1.ulx`, `t1.ni`, `t1.json` 세 파일을 만든다. `.ulx`는 인터프리터에 로드할 바이트코드, 나머지 둘은 게임 진행 중 부가 정보를 제공하는 확장 데이터다.

`tw-play` 유틸리티로 직접 플레이해볼 수도 있다(가장 편한 방법은 아니지만 결과를 확인하기엔 충분하다).

```bash
$ tw-play t1.ulx
Using TWInform7.
...

Hey, thanks for coming over to the TextWorld today, there
is something I need you to do for me. First thing I need you
to do is to try to venture east. Then, venture south. After
that, try to go to the south. Once you succeed at that, try
to go west. If you can finish that, pick-up the coin from
the floor of the chamber. Once that's all handled, you can stop!

-= Spare Room =-
You are in a spare room. An usual one.

You don't like doors? Why not try going east, that entranceway
is unblocked.

> _
```

### 2.3 관측·행동 공간 살펴보기

게임을 만들고 노는 건 재밌지만, TextWorld의 진짜 가치는 **RL 인터페이스**를 제공한다는 데 있다. 방금 만든 게임으로 무엇을 할 수 있는지 확인해보자.

```python
>>> from textworld import gym
>>> from textworld.gym import register_game
>>> env_id = register_game("t1.ulx")
>>> env_id
'tw-v0'
>>> env = gym.make(env_id)
>>> env
<textworld.gym.envs.textworld.TextworldGymEnv object at 0x102f77350>
>>> r = env.reset()
>>> print(r[1])
{}
>>> print(r[0][1205:])
$$
```

> [!warning] `gym.make()`가 아니라 `textworld.gym.make()`
> 여기서 쓰인 `make()`는 Gymnasium의 `make()`가 아니라 `textworld` 모듈 자체의 함수다. 실수가 아니라 의도된 것이다. 최근 TextWorld 릴리스는 Gym API 패키지에 대한 의존을 제거하고, `Env` 클래스와 겉보기엔 비슷하지만 완전히 같지는 않은 **자체 환경 클래스**를 제공한다. 이는 OpenAI Gym에서 Farama Gymnasium으로 넘어가는 과도기의 임시 조치로 보인다.

이 전환기 때문에 몇 가지를 새로 알아둬야 한다.

- 게임을 만들 때는 `gym.make()`가 아니라 `textworld.gym.make()`를 써야 한다.
- 생성된 환경은 별도의 관측·행동 공간 명세가 없다. 기본적으로 관측과 행동 모두 **그냥 문자열(str)**이다.
- `step()` 함수가 `is_truncated` 플래그를 돌려주지 않는다. 대신 관측, 보상, `is_done` 플래그, 부가 정보 딕셔너리만 반환한다. 이 때문에 Gymnasium용 래퍼(wrapper)를 그대로 적용할 수 없고, 작은 "어댑터" 래퍼를 직접 만들어야 한다.

과거 버전의 TextWorld는 토큰화(tokenization) 기능도 제공했지만, 지금은 제거되어서 텍스트 전처리를 **직접** 구현해야 한다.

---

## 3. 부가 게임 정보 (Extra Game Information)

본격적으로 학습 코드를 설계하기 전에, 이 문제가 얼마나 어려운지부터 짚고 넘어가자.

- 관측은 어휘 크기 1,250개짜리 사전에서 뽑은, 최대 200 토큰짜리 텍스트 시퀀스다. 행동은 최대 8 토큰까지 갈 수 있다. 생성된 게임은 **정확한 순서로 실행해야 하는 5개의 행동**을 요구한다. 무작위 탐색만으로 8×5=40 토큰짜리 정답 시퀀스를 맞힐 확률은 대략 $\frac{1}{1250^{40}} \approx \frac{1}{10^{123}}$ 수준이다.

> [!warning] 사실상 0에 가까운 확률
> 아무리 빠른 GPU를 써도 이 확률은 희망이 없다. 물론 문장 시작·끝을 알리는 특수 토큰이 있어서 실제 확률은 이보다 조금 낫지만, 순수 무작위 탐색으로 정답 행동열을 찾을 가능성은 극도로 희박하다.

- 또 하나의 난관은 [[POMDP 부분관측 마르코프결정과정]] 문제다. 게임 속 인벤토리(내가 들고 있는 물건 목록)는 `inventory` 같은 명시적 명령을 내려야만 표시된다. 그래서 `take apple`을 실행한 직후에도 에이전트가 받는 화면 관측은 **직전과 거의 똑같다**(다만 장면 설명에서 사과가 더 이상 언급되지 않는다는 점만 다르다). 에이전트 입장에서는 방금 사과를 집었는지 아닌지 확신할 수 없다. Atari 게임에서 여러 프레임을 쌓아 처리했던 것처럼, 상태를 명시적으로 누적해야 하지만, 이번엔 그 방식이 에이전트가 처리할 정보량을 크게 늘린다.

다행히 TextWorld는 이런 문제를 완화할 편리한 방법을 제공한다. 게임을 등록할 때 다음과 같은 추가 정보를 요청할 수 있다.

- `look` 명령을 실행했을 때와 같은 **현재 방의 별도 설명**
- **현재 인벤토리**
- **현재 위치의 이름**
- **현재 게임 세계 상태의 사실(fact)들**
- **마지막 행동과 마지막으로 실행한 명령**
- **현재 상태에서 실행 가능한(admissible) 명령 목록**
- **게임을 깨기 위해 실행해야 할 행동 순서(정답)**

여기에 더해, 매 스텝마다 **중간 보상**(올바른 방향으로 한 걸음 나아갈 때마다 주어지는 보상)도 요청할 수 있다. 특히 유용한 두 가지는 **실행 가능 명령 목록**(행동 공간을 $1250^{40}$에서 겨우 십여 개 수준으로 극적으로 줄여준다)과 **중간 보상**(학습이 올바른 방향으로 가도록 유도한다)이다.

이 부가 정보를 켜려면 `register_game()`에 `EnvInfos` 객체를 전달한다.

```python
>>> from textworld import gym, EnvInfos
>>> from textworld.gym import register_game
>>> env_id = register_game("t1.ulx", request_infos=EnvInfos(inventory=True,
intermediate_reward=True, admissible_commands=True, description=True))
>>> env = gym.make(env_id)
>>> r = env.reset()
>>> r[1]
{'description': "-= Spare Room =-\nYou are in a spare room. An usual one.\n\n\nYou
don't like doors? Why not try going east, that entranceway is unblocked.", 'admissible_commands':
['go east', 'inventory', 'look'], 'inventory': 'You are carrying nothing.', 'intermediate_reward': 0}
```

전에는 텅 비었던 딕셔너리가 이제 유용한 정보로 채워졌다. 이 상태에서는 딱 세 개의 명령(`go east`, `inventory`, `look`)만 의미가 있다. 첫 번째 것을 실행해보자.

```python
>>> r = env.step('go east')
>>> r[1:]
(0, False, {'description': "-= Attic =-\nYou make a grand eccentric entrance into an
attic.\n\n\nYou need an unblocked exit? You should try going south. You don't like
doors? Why not try going west, that entranceway is unblocked.", 'admissible_commands':
['go south', 'go west', 'inventory', 'look'], 'inventory': 'You are carrying nothing.',
'intermediate_reward': 1})
```

명령이 받아들여졌고, 중간 보상 1을 받았다. 이제 베이스라인 DQN 에이전트를 구현할 준비가 됐지만, 그 전에 **자연어 처리(NLP)** 의 기초를 잠깐 짚고 넘어가야 한다.

---

## 4. 딥 NLP 기초

이 절은 딥러닝 기반 NLP의 표준 구성 요소를 훑어보는 짧은 소개다. 이 분야는 지금도 매우 빠르게 발전하고 있고, 특히 ChatGPT와 LLM이 챗봇·텍스트 처리 분야의 새 기준을 세웠다. RNN이나 LSTM 같은 옛날 기법이 지금은 유행이 지난 것처럼 보일 수 있지만, 역사적 맥락을 아는 것은 여전히 중요하다. 간단한 작업이라면 화려하지 않아도 적합한 도구를 고르는 게 더 나을 때도 많다.

### 4.1 순환 신경망 (RNN)

NLP에는 다른 분야와 구별되는 고유한 특징이 있다. **가변 길이 데이터를 다뤄야 한다**는 점이다. 단어는 여러 글자로 이뤄지고, 문장은 가변 길이의 단어열로 이뤄지며, 문단·문서는 문장 개수가 제각각이다. 이런 가변성은 NLP만의 문제는 아니고 신호 처리, 영상 처리 등에서도 나타난다. 심지어 이미지 캡션 문제처럼, 신경망이 이미지의 여러 영역에 순서대로 주목해야 하는 컴퓨터 비전 문제도 일종의 시퀀스 문제로 볼 수 있다.

[[RNN 순환신경망]]은 이런 가변성을 다루는 표준 구성 요소다. RNN은 고정 크기 입력과 출력을 갖는 네트워크를 **시퀀스**에 반복 적용하면서, 시퀀스를 따라 정보를 전달할 수 있다. 이 정보를 **hidden state**(은닉 상태)라고 부르며, 보통은 그냥 어떤 크기의 숫자 벡터다.

RNN 하나는 고정 크기 숫자 벡터 하나를 입력받아 다른 벡터를 출력한다. 일반적인 순전파·합성곱 신경망과 다른 점은, **두 개의 추가 게이트**(하나는 입력용, 하나는 출력용)를 갖는다는 것이다. 추가 입력은 시퀀스의 이전 항목에서 넘어온 hidden state를 받고, 추가 출력은 변환된 hidden state를 다음 항목에 넘긴다.

![[fig_13_3.png]]
*그림 13.3 — RNN 블록의 구조*

RNN은 두 개의 입력을 가지므로, **어떤 길이의 시퀀스에도 적용**할 수 있다. 이전 항목이 만든 hidden state를 다음 항목에 계속 넘기기만 하면 된다. 다음 그림은 "this is a cat"이라는 문장에 RNN을 적용해, 시퀀스의 매 단어마다 출력을 만드는 과정을 보여준다.

![[fig_13_4.png]]
*그림 13.4 — RNN이 문장에 적용되는 방식*

적용 과정에서는 매 입력 항목에 **같은 RNN**이 적용되지만, hidden state를 갖고 있으므로 시퀀스를 따라 정보를 전달할 수 있다. 합성곱 신경망도 여러 위치에 같은 필터 집합을 적용한다는 점에서 비슷하지만, 결정적 차이는 **합성곱 신경망은 hidden state를 넘기지 못한다**는 것이다.

이 모델은 단순해 보이지만, 표준 순전파 신경망 모델에 **추가적인 자유도**를 부여한다. 순전파 신경망은 입력이 정해지면(추론 시에는) 항상 같은 출력을 낸다. 반면 RNN의 출력은 입력뿐 아니라 **hidden state**(신경망 스스로 바꿀 수 있는)에도 의존한다. 그래서 신경망은 시퀀스의 시작부터 끝까지 정보를 전달하며, 같은 입력이라도 문맥에 따라 다른 출력을 만들 수 있다. 이런 문맥 의존성은 자연어 처리에서 매우 중요하다 — 자연어에서는 단어 하나가 문맥에 따라 완전히 다른 뜻을 가질 수 있고, 문장 전체의 의미도 단어 하나로 바뀔 수 있기 때문이다.

물론 이런 유연함에는 대가가 따른다. RNN은 보통 학습에 시간이 더 걸리고, 손실이 요동치거나 학습 도중 갑자기 이상해지는 등의 특이한 현상을 보이기도 한다. 하지만 연구 커뮤니티가 RNN을 더 실용적이고 안정적으로 만들기 위해 많은 노력을 기울여왔기 때문에, RNN과 트랜스포머 같은 그 현대적 대안들은 가변 길이 입력을 처리해야 하는 시스템의 표준 구성 요소로 자리잡았다.

이 챕터의 예제에서는 RNN의 진화형인 [[LSTM 장단기메모리]] 모델을 쓴다. LSTM은 1995년 Sepp Hochreiter와 Jürgen Schmidhuber가 논문 *"LSTM can solve hard long time lag problems"* 에서 처음 제안했고, 1996년 NIPS(Neural Information Processing Systems) 학회에서 발표되었다[HS96]. 우리가 방금 살펴본 RNN과 매우 비슷하지만, 기존 RNN의 여러 문제를 해결하기 위해 내부 구조가 좀 더 복잡하다.

### 4.2 워드 임베딩 (Word Embedding)

현대 딥러닝 기반 NLP의 또 다른 표준 구성 요소는 [[워드 임베딩 Word Embedding]]이며, 대표적인 훈련 기법의 이름을 따 **word2vec**이라고도 불린다. 이 아이디어는 "언어 시퀀스를 신경망 안에서 어떻게 표현할까"라는 문제에서 나왔다. 신경망은 보통 고정 크기 숫자 벡터로 작업하지만, NLP에서는 보통 단어나 글자가 입력으로 들어온다.

> [!tip] 다른 방법도 있다
> word2vec 같은 예전 방법이 단순한 작업에는 여전히 흔히 쓰이고 관련성도 여전히 크지만, BERT나 트랜스포머 같은 방법이 더 복잡한 작업에 널리 쓰인다. 트랜스포머는 이 챕터 뒤에서 짧게 다룬다.

가능한 해법 하나는 사전을 **원-핫 인코딩**하는 것이다. 즉 모든 단어가 입력 벡터에서 자기만의 자리를 갖고, 입력 시퀀스에서 그 단어를 만나면 그 위치를 1로 설정한다. 이는 상대적으로 작은 이산 항목 집합을 NN 친화적으로 표현해야 할 때 흔히 쓰는 표준적 접근이다. 하지만 원-핫 인코딩은 단어에는 잘 맞지 않는데, 이유는 다음과 같다.

- 입력 집합이 보통 작지 않다. 자주 쓰이는 영어 단어만 인코딩하려 해도 최소 수천 단어가 필요하다. 옥스포드 영어 사전에는 상용어 17만 개와 폐어·희귀어 5만 개가 있다. 이건 표준 어휘일 뿐이고, 은어·신조어·과학 용어·오타·농담·트위터(X) 밈 등은 포함되지도 않았다. 그리고 이건 영어 한 언어에 대해서만 그렇다!
- 원-핫 표현과 관련된 두 번째 문제는 어휘의 빈도가 매우 불균등하다는 점이다. "a"나 "cat"처럼 매우 흔한 단어의 집합은 비교적 작지만, "covfefe"나 "bibliopole"처럼 훨씬 드물게 쓰이는 단어의 집합은 아주 크다. 그래서 원-핫 표현은 공간 측면에서 매우 비효율적이다.
- 단순 원-핫 표현의 또 다른 문제는 단어 사이의 관계를 담지 못한다는 점이다. 예를 들어 어떤 단어들은 동의어라서 같은 뜻이지만 서로 다른 벡터로 표현된다. 어떤 단어들은 "United Nations"나 "fair trade"처럼 매우 자주 함께 쓰이는데, 이 사실도 원-핫 표현에서는 담기지 않는다.

이 모든 문제를 극복하기 위해 워드 임베딩을 쓸 수 있다. 이는 어휘 속 모든 단어를 조밀하고(dense) 고정 길이인 숫자 벡터로 매핑하는 방법이다. 이 숫자들은 무작위가 아니라, 대량의 텍스트 말뭉치로부터 **단어의 문맥을 포착하도록 학습**된다. 워드 임베딩에 대한 상세한 설명은 이 책의 범위를 벗어나지만, 이는 단어·글자 등을 시퀀스 안에서 표현하는 매우 강력하고 널리 쓰이는 NLP 기법이다. 지금은 그냥 단어를 숫자 벡터로 매핑해주는 것이라 생각하면 되고, 이 매핑 덕분에 신경망이 단어들을 서로 구분할 수 있게 된다.

이 매핑을 얻는 방법은 두 가지다. 첫째, 필요한 언어에 대해 **미리 학습된(pretrained) 벡터**를 다운로드할 수 있다. "GloVe pretrained vectors"나 "word2vec pretrained"를 구글에서 검색하면 여러 출처를 찾을 수 있다(GloVe와 word2vec은 이런 벡터를 학습하는 서로 다른 방법이며, 비슷한 결과를 낸다). 다른 방법은 **자신의 데이터셋으로 직접 학습**하는 것이다. 이를 위해 fastText([https://fasttext.cc/](https://fasttext.cc/), Facebook의 오픈소스 도구) 같은 전용 도구를 쓰거나, 그냥 임베딩을 무작위로 초기화한 뒤 일반적인 학습 과정에서 모델이 스스로 조정하도록 둘 수도 있다.

추가로, LLM(그리고 일반적으로 모든 시퀀스-투-시퀀스 아키텍처)은 매우 고품질의 텍스트 임베딩을 만들어낼 수 있다. OpenAI ChatGPT API는 어떤 텍스트든 임베딩 벡터로 바꿔주는 전용 요청 기능을 제공한다.

### 4.3 Encoder-Decoder 아키텍처

NLP에서 널리 쓰이는 또 다른 모델은 **Encoder-Decoder**, 또는 **seq2seq**라 불리는 구조다. 원래는 기계 번역에서 나왔는데, 시스템이 원본 언어의 단어 시퀀스를 입력받아 목표 언어의 또 다른 시퀀스를 만들어야 하는 상황이었다. [[Encoder-Decoder와 seq2seq]]의 핵심 아이디어는 RNN을 써서 입력 시퀀스를 **인코더(encoder)**가 어떤 고정 길이 표현으로 **인코딩**하는 것이다. 그다음 이 인코딩된 벡터를 **디코더(decoder)**라 불리는 또 다른 RNN에 먹여서, 목표 언어의 결과 시퀀스를 생성하게 한다. 다음은 영어 문장을 러시아어로 번역하는 예시다.

![[fig_13_5.png]]
*그림 13.5 — 기계 번역에서의 Encoder-Decoder 아키텍처*

(현대적인 수많은 변형과 확장이 붙은) 이 모델은 여전히 기계 번역의 주요 작업 방식이지만, 오디오 처리, 이미지 캡션, 비디오 캡션 등 훨씬 넓은 도메인에 적용할 수 있을 만큼 일반적이다. 이번 TextWorld 예제에서는 환경에서 온 가변 크기 관측의 **임베딩을 생성하는 데** 이 아이디어를 쓴다(디코더까지 쓰는 게 아니라 인코더 부분만 활용).

RNN은 특정 맥락에서는 여전히 매우 효과적이지만, 최근 몇 년 사이 NLP는 더 복잡한 **트랜스포머(Transformer)** 모델의 등장으로 크게 발전했다.

### 4.4 트랜스포머 (Transformers)

[[Transformer 트랜스포머]]는 2017년 구글의 Vaswani 등이 발표한 논문 *Attention is all you need*에서 제안된 아키텍처다[Vas17]. 고수준에서 보면 방금 다룬 것과 같은 Encoder-Decoder 아키텍처를 쓰지만, 기존 RNN이 갖고 있던 문제들을 해결하기 위해 밑바탕 구성 요소에 여러 개선을 더했다.

- **위치 인코딩(Positional encoding)**: 입력·출력 시퀀스의 위치 정보를 임베딩에 주입한다.
- **어텐션 메커니즘(Attention mechanism)**: 2015년에 처음 제안된 개념으로, 시스템이 입력 시퀀스의 특정 부분에 집중하는 방법을 **학습 가능한 방식**으로 구현한 것이다. 트랜스포머에서는 어텐션이 매우 적극적으로 쓰이는데, 이는 논문 제목에서도 짐작할 수 있다.

오늘날 트랜스포머는 LLM을 포함해 거의 모든 NLP·딥러닝 시스템의 핵심에 자리한다. 이 아키텍처를 깊이 다루지는 않지만, 궁금하다면 다음 글을 참고하라: [https://jalammar.github.io/illustrated-transformer/](https://jalammar.github.io/illustrated-transformer/).

이제 우리의 첫 번째 베이스라인 DQN 에이전트를 구현해 TextWorld 문제를 풀 준비가 모두 끝났다.

---

## 5. 베이스라인 DQN

TextWorld 환경에서는 다음과 같은 주요 난관이 있다.

- **텍스트 시퀀스 자체의 문제**: 앞서 논의했듯, 시퀀스 길이의 가변성은 RNN에서 기울기 소실·폭발이나 느린 학습, 수렴 문제를 일으킬 수 있다. 게다가 TextWorld 환경은 이런 시퀀스를 여러 개 따로 제공하는데, 예를 들어 장면 설명(scene description) 문자열은 인벤토리 문자열과는 에이전트에게 완전히 다른 의미를 가질 수 있으므로 별도로 다뤄야 한다.
- **행동 공간의 문제**: 앞서 봤듯, TextWorld는 매 상태에서 실행 가능한 명령 목록을 제공해줄 수 있고, 이는 선택해야 할 행동 공간을 크게 줄여준다. 하지만 여기에도 여러 복잡함이 있다. 실행 가능 명령 목록이 상태마다 달라진다(위치가 다르면 허용되는 명령도 다르다). 또, 실행 가능 명령 목록의 각 항목 자체가 단어들의 시퀀스라는 문제도 있다.

이 두 가변성을 모두 제거하는 잠재적 방법은, 가능한 모든 명령의 사전을 만들어 그것을 이산적이고 고정된 크기의 행동 공간으로 쓰는 것이다.

> [!note] 이 챕터에서 택하지 않은 길
> 간단한 게임이라면 위치·물건 개수가 그리 많지 않아 이 방법이 통할 수도 있다. 연습 삼아 시도해봐도 좋지만, 이 책은 다른 길을 택한다.

지금까지는 항상 **소수의 미리 정의된 이산 행동**만 있는 환경을 다뤄왔고, 이는 DQN 아키텍처에도 영향을 미쳤다 — 신경망이 한 번의 순전파로 모든 행동에 대한 Q값을 예측하는 방식이었다(어차피 argmax를 구하려면 모든 행동의 Q값이 다 필요하니 편리했다). 하지만 이런 DQN 아키텍처는 방법론 자체가 강제하는 게 아니므로, 필요하면 바꿀 수 있다. 그리고 가변 개수의 행동이라는 이슈도 이런 식으로 해결할 수 있다. 우리 베이스라인 DQN의 아키텍처를 그림으로 보자.

![[fig_13_6.png]]
*그림 13.6 — TextWorld 베이스라인 DQN의 아키텍처*

다이어그램의 대부분을 차지하는 것은 전처리 블록들(왼쪽)이다. 입력으로는 관측의 개별 부분("Raw text", "Description", "Inventory")의 가변 시퀀스와, 평가할 명령(action) 시퀀스 하나가 들어온다. 이 명령은 실행 가능 명령 목록에서 가져온다. 신경망의 목표는 **현재 게임 상태와 이 특정 명령 하나**에 대한 Q값을 하나 예측하는 것이다. 이는 지금까지 써온 DQN과는 접근이 다른데, 어떤 명령들이 매 상태에서 평가될지 미리 알 수 없기 때문에 **명령 하나하나를 개별적으로 평가**한다.

이 네 개의 입력 시퀀스(우리 어휘의 토큰 ID 리스트)는 임베딩 레이어를 거친 뒤, 별도의 LSTM RNN으로 들어간다. 그림에서 "Encoders"라 표시된 LSTM 네트워크들의 목표는 가변 길이 시퀀스를 고정 크기 벡터로 바꾸는 것이다(LSTM은 인코더의 구체적인 구현체이므로 이렇게 표시했다).

입력 조각마다 **분리된 가중치**를 가진 자신만의 LSTM이 적용되는데, 이는 서로 다른 입력 시퀀스로부터 서로 다른 데이터를 포착하도록 한다. 이 챕터 후반에는 LSTM을 Hugging Face Hub의 사전 학습된 트랜스포머로 교체해, 훨씬 더 스마트하고 큰 모델을 같은 문제에 썼을 때의 효과를 확인해본다.

인코더들의 출력은 하나의 벡터로 이어붙여진(concatenate) 뒤 메인 DQN 네트워크로 들어간다. 가변 길이 시퀀스가 고정 크기 벡터로 이미 변환됐으므로, DQN 네트워크 자체는 단순하다 — 그냥 여러 개의 순전파 레이어를 거쳐 단일 Q값 하나를 만들어낸다. 계산 효율은 좋지 않지만, 베이스라인으로는 충분하다.

전체 소스 코드는 `Chapter13` 디렉터리에 있으며 다음 모듈로 구성된다.

- `train_basic.py`: 베이스라인 학습 프로그램
- `lib/common.py`: Ignite 엔진과 하이퍼파라미터를 설정하는 공용 유틸리티
- `lib/preproc.py`: 임베딩과 인코더 클래스를 포함한 전처리 파이프라인
- `lib/model.py`: DQN 모델과 DQN 에이전트, 헬퍼 함수

전체 소스 코드를 다 싣지는 않고, 이어지는 절에서 가장 중요하거나 까다로운 부분만 설명한다.

### 5.1 관측 전처리

파이프라인의 가장 왼쪽 부분(그림 13.6)부터 시작하자. 입력에서는 개별 상태 관측용 토큰 리스트 여러 개와, 평가할 명령 하나를 받는다. 하지만 앞서 봤듯 TextWorld 환경은 문자열과 부가 정보를 담은 딕셔너리를 내놓으므로, 문자열을 토큰화하고 불필요한 정보를 제거해야 한다. 이것이 `lib/preproc.py` 모듈에 정의된 `TextWorldPreproc` 클래스의 역할이다.

```python
class TextWorldPreproc(gym.Wrapper):
    log = logging.getLogger("TextWorldPreproc")

    OBS_FIELD = "obs"

    def __init__(
            self, env: gym.Env, vocab_rev: tt.Optional[tt.Dict[str, int]],
            encode_raw_text: bool = False,
            encode_extra_fields: tt.Iterable[str] = ('description', 'inventory'),
            copy_extra_fields: tt.Iterable[str] = (),
            use_admissible_commands: bool = True, keep_admissible_commands: bool = False,
            use_intermediate_reward: bool = True, tokens_limit: tt.Optional[int] = None,
            reward_wrong_last_command: tt.Optional[float] = None
    ):
```

이 클래스는 `gym.Wrapper` 인터페이스를 구현해, TextWorld 환경의 관측과 행동을 우리가 원하는 형태로 변환한다. 생성자는 여러 플래그를 받는데, 이후 실험을 단순하게 만들어준다. 예를 들어 실행 가능 명령이나 중간 보상 사용 여부를 끄거나, 토큰 개수의 한계를 설정하거나, 처리할 관측 필드 집합을 바꿀 수 있다.

```python
        super(TextWorldPreproc, self).__init__(env)
        self._vocab_rev = vocab_rev
        self._encode_raw_text = encode_raw_text
        self._encode_extra_field = tuple(encode_extra_fields)
        self._copy_extra_fields = tuple(copy_extra_fields)
        self._use_admissible_commands = use_admissible_commands
        self._keep_admissible_commands = keep_admissible_commands
        self._use_intermediate_reward = use_intermediate_reward
        self._num_fields = len(self._encode_extra_field) + int(self._encode_raw_text)
        self._last_admissible_commands = None
        self._last_extra_info = None
        self._tokens_limit = tokens_limit
        self._reward_wrong_last_command = reward_wrong_last_command
        self._cmd_hist = []
```

다음으로 `num_fields` 프로퍼티는 인코딩할 관측 시퀀스의 개수를 반환해, 인코딩된 관측의 형태(shape)를 파악하는 데 쓰인다.

```python
    @property
    def num_fields(self):
        return self._num_fields

    def _maybe_tokenize(self, s: str) -> str | tt.List[int]:
        if self._vocab_rev is None:
            return s
        tokens = common.tokenize(s, self._vocab_rev)
        if self._tokens_limit is not None:
            tokens = tokens[:self._tokens_limit]
        return tokens
```

`_maybe_tokenize()` 메서드는 입력 문자열을 토큰화한다. 사전이 주어지지 않으면 문자열을 그대로 돌려준다. 이 기능은 트랜스포머 버전에서 쓰이는데, Hugging Face 라이브러리가 자체 토큰화를 수행하기 때문이다.

`_encode()` 메서드는 관측 변환의 핵심이다.

```python
    def _encode(self, obs: str, extra_info: dict) -> dict:
        obs_result = []
        if self._encode_raw_text:
            obs_result.append(self._maybe_tokenize(obs))
        for field in self._encode_extra_field:
            extra = extra_info[field]
            obs_result.append(self._maybe_tokenize(extra))
        result = {self.OBS_FIELD: obs_result}
        if self._use_admissible_commands:
            result[KEY_ADM_COMMANDS] = [
                self._maybe_tokenize(cmd) for cmd in extra_info[KEY_ADM_COMMANDS]
            ]
            self._last_admissible_commands = extra_info[KEY_ADM_COMMANDS]
        if self._keep_admissible_commands:
            result[KEY_ADM_COMMANDS] = extra_info[KEY_ADM_COMMANDS]
            if 'policy_commands' in extra_info:
                result['policy_commands'] = extra_info['policy_commands']
        self._last_extra_info = extra_info
        for field in self._copy_extra_fields:
            if field in extra_info:
                result[field] = extra_info[field]
        return result
```

이 메서드는 관측 문자열과 부가 정보 딕셔너리를 받아, 다음 키를 가진 딕셔너리 하나를 반환한다.

- `obs`: 입력 시퀀스들의 토큰 ID 리스트들의 리스트
- `admissible_commands`: 현재 상태에서 가능한 명령 목록. 각 명령은 토큰화되어 토큰 ID 리스트로 변환된다.

추가로, 이 메서드는 부가 정보 딕셔너리와 원본 실행 가능 명령 목록을 기억해둔다. 학습에는 필요 없지만, 모델을 실제로 적용할 때 명령의 인덱스로부터 명령 텍스트를 다시 얻는 데 유용하다.

`_encode()` 메서드가 정의됐으니, `reset()`과 `step()` 구현은 간단하다 — 관측을 인코딩하고 (활성화된 경우) 중간 보상을 처리하기만 하면 된다.

```python
    def reset(self, seed: tt.Optional[int] = None):
        res, extra = self.env.reset()
        self._cmd_hist = []
        return self._encode(res, extra), extra

    def step(self, action):
        if self._use_admissible_commands:
            action = self._last_admissible_commands[action]
        self._cmd_hist.append(action)
        obs, r, is_done, extra = self.env.step(action)
        if self._use_intermediate_reward:
            r += extra.get('intermediate_reward', 0)
        if self._reward_wrong_last_command is not None:
            if action not in self._last_extra_info[KEY_ADM_COMMANDS]:
                r += self._reward_wrong_last_command
        return self._encode(obs, extra), r, is_done, extra
```

`step()` 메서드가 래핑된 환경으로부터 4개의 항목을 기대하지만 실제로는 5개를 받는다는 점이 눈에 띈다. 이는 앞서 이야기했던 TextWorld 환경과 최신 Gym 인터페이스 사이의 비호환성을 감춰준다.

마지막으로, 기억해둔 상태에 접근할 수 있는 프로퍼티가 두 개 있다.

```python
    @property
    def last_admissible_commands(self):
        if self._last_admissible_commands:
            return tuple(self._last_admissible_commands)
        return None

    @property
    def last_extra_info(self):
        return self._last_extra_info
```

앞의 클래스가 어떻게 적용되고 관측에 어떤 일을 하는지 확인하기 위해, 짧은 대화형 세션을 살펴보자. 여기서는 게임을 등록하며 인벤토리, 중간 보상, 실행 가능 명령, 장면 설명을 요청한다.

```python
>>> from textworld import gym, EnvInfos
>>> from lib import preproc, common
>>> env_id = gym.register_game("games/simple1.ulx", request_infos=EnvInfos(inventory=True,
intermediate_reward=True, admissible_commands=True, description=True))
>>> env = gym.make(env_id)
>>> env.reset()[1]
```

```python
{'intermediate_reward': 0, 'inventory': 'You are carrying: a type D latchkey, a teacup
and a sponge.', 'description': "-= Spare Room =-\nThis might come as a shock to you, but
you've just walked into a spare room. You can barely contain your excitement.\n\nYou can
make out a closed usual looking crate close by. You can make out a rack. However, the
rack, like an empty rack, has nothing on it.\n\nThere is an exit to the east. Don't worry,
it is unblocked. You don't like doors? Why not try going south, that entranceway is
unguarded.", 'admissible_commands': ['drop sponge', 'drop teacup', 'drop type D latchkey',
'examine crate', 'examine rack', 'examine sponge', 'examine teacup', 'examine type D
latchkey', 'go east', 'go south', 'inventory', 'look', 'open crate', 'put sponge on rack',
'put teacup on rack', 'put type D latchkey on rack']}
```

이것이 TextWorld 환경에서 얻은 원본(raw) 관측이다. 이제 게임 어휘를 추출해 우리 전처리기를 적용해보자.

```python
>>> vocab, action_space, obs_space = common.get_games_spaces(["games/simple1.ulx"])
>>> vocab
{0: 'a', 1: 'about', 2: 'accomplished', 3: 'an', 4: 'and', 5: 'appears', 6: 'are', 7: 'as',
8: 'barely', 9: 'be', 10: 'because', 11: 'begin', 12: 'being', 13: 'believe'
....
>>> len(vocab)
192
>>> vocab_rev = common.build_rev_vocab(vocab)
>>> vocab_rev
{'a': 0, 'about': 1, 'accomplished': 2, 'an': 3, 'and': 4, 'appears': 5, 'are': 6,
'arrive': 7
...
>>> pr_env = preproc.TextWorldPreproc(env, vocab_rev)
>>> r = pr_env.reset()
>>> r[0]
{'obs': [[142, 132, 166, 106, 26, 8, 136, 167, 188, 17, 188, 86, 180, 82, 0, 142, 132,
188, 20, 9, 27, 191, 57, 188, 20, 103, 121, 0, 24, 178, 101, 35, 23, 18, 188, 20, 103,
121, 0, 129, 77, 161, 129, 94, 3, 50, 129, 73, 111, 115, 85, 163, 84, 3, 58, 167, 161, 44,
152, 186, 85, 84, 172, 188, 152, 94, 41, 184, 110, 169, 72, 141, 159, 53, 84, 173], [188,
6, 0, 170, 36, 92, 0, 157, 4, 0, 143]], 'admissible_commands': [[42, 143], [42, 157], [42,
170, 36, 92], [55, 35], [55, 129], [55, 143], [55, 157], [55, 170, 36, 92], [71, 44],
[71, 141], [83], [100], [117, 35], [127, 143, 115, 129], [127, 157, 115, 129], [127, 170,
36, 92, 115, 129]]}
>>> r[1]
```

```python
{'intermediate_reward': 0, 'inventory': 'You are carrying: a type D latchkey, a teacup
and a sponge.', 'description': "-= Spare Room =-\nThis might come as a shock to you, but
you've just walked into a spare room. You can barely contain your excitement.\n\nYou can
make out a closed usual looking crate close by. You can make out a rack. However, the
rack, like an empty rack, has nothing on it.\n\nThere is an exit to the east. Don't worry,
it is unblocked. You don't like doors? Why not try going south, that entranceway is
unguarded.", 'admissible_commands': ['drop sponge', 'drop teacup', 'drop type D latchkey',
'examine crate', 'examine rack', 'examine sponge', 'examine teacup', 'examine type D
latchkey', 'go east', 'go south', 'inventory', 'look', 'open crate', 'put sponge on rack',
'put teacup on rack', 'put type D latchkey on rack']}
```

행동 하나를 실행해보자. 0번 행동은 실행 가능 명령 목록의 첫 항목인 "drop sponge"(스펀지를 내려놓는다)에 대응한다.

```python
>>> r[1]['inventory']
'You are carrying: a type D latchkey, a teacup and a sponge.'
>>> obs, reward, is_done, _, info = pr_env.step(0)
>>> info['inventory']
'You are carrying: a type D latchkey and a teacup.'
>>> reward
0
```

보다시피, 이제 스펀지가 사라졌다. 다만 이건 정답 행동이 아니었으므로 중간 보상은 주어지지 않았다.

이 표현은 아직 신경망에 바로 넣을 수는 없지만, 우리가 원하는 형태에 훨씬 가까워졌다.

### 5.2 임베딩과 인코더

전처리 파이프라인의 다음 단계는 두 개의 클래스로 구현된다.

- `Encoder`: 임베딩이 적용된 뒤의 시퀀스 하나를 고정 크기 벡터로 바꾸는, LSTM 유닛을 감싼 래퍼
- `Preprocessor`: 임베딩 적용과, 대응하는 인코더 클래스로 개별 시퀀스를 변환하는 역할을 담당하는 클래스

`Encoder` 클래스가 더 단순하니 먼저 살펴보자.

```python
class Encoder(nn.Module):
    def __init__(self, emb_size: int, out_size: int):
        super(Encoder, self).__init__()
        self.net = nn.LSTM(input_size=emb_size, hidden_size=out_size, batch_first=True)

    def forward(self, x):
        self.net.flatten_parameters()
        _, hid_cell = self.net(x)
        return hid_cell[0].squeeze(0)
```

로직은 이렇다. LSTM 레이어를 적용하고, 시퀀스를 다 처리한 뒤의 hidden state를 반환한다.

`Preprocessor` 클래스는 조금 더 복잡한데, 여러 `Encoder` 인스턴스를 결합하면서 임베딩까지 함께 담당하기 때문이다.

```python
class Preprocessor(nn.Module):
    def __init__(self, dict_size: int, emb_size: int, num_sequences: int,
                 enc_output_size: int, extra_flags: tt.Sequence[str] = ()):
        super(Preprocessor, self).__init__()
        self._extra_flags = extra_flags
        self._enc_output_size = enc_output_size
        self.emb = nn.Embedding(num_embeddings=dict_size, embedding_dim=emb_size)
        self.encoders = []
        for idx in range(num_sequences):
            enc = Encoder(emb_size, enc_output_size)
            self.encoders.append(enc)
            self.add_module(f"enc_{idx}", enc)
        self.enc_commands = Encoder(emb_size, enc_output_size)
```

생성자에서는 사전의 모든 토큰을 고정 크기의 조밀한 벡터로 매핑하는 임베딩 레이어를 만든다. 그다음 입력 시퀀스마다 `Encoder` 인스턴스를 `num_sequences`개 만들고, 명령 토큰을 인코딩할 인스턴스를 하나 더 만든다.

내부 메서드 `_apply_encoder()`는 시퀀스들의 배치(각 시퀀스는 토큰 ID 리스트)를 받아 인코더로 변환한다.

```python
    def _apply_encoder(self, batch: tt.List[tt.List[int]], encoder: Encoder):
        dev = self.emb.weight.device
        batch_t = [self.emb(torch.tensor(sample).to(dev)) for sample in batch]
        batch_seq = rnn_utils.pack_sequence(batch_t, enforce_sorted=False)
        return encoder(batch_seq)
```

> [!note] `pack_sequence`와 `enforce_sorted=False`
> 예전 버전의 PyTorch에서는 RNN에 넣기 전 가변 길이 시퀀스의 배치를 길이순으로 정렬해줘야 했다. PyTorch 1.0부터는 이 정렬과 변환을 `PackedSequence` 클래스가 내부적으로 처리해준다. 이 기능을 쓰려면 `enforce_sorted=False` 파라미터를 넘겨주기만 하면 된다.

`encode_observations()` 메서드는 (`TextWorldPreproc`에서 만든) 관측들의 배치를 받아 하나의 텐서로 인코딩한다.

```python
    def encode_observations(self, observations: tt.List[dict]) -> torch.Tensor:
        sequences = [obs[TextWorldPreproc.OBS_FIELD] for obs in observations ]
        res_t = self.encode_sequences(sequences)
        if not self._extra_flags:
            return res_t
        extra = [[obs[field] for field in self._extra_flags] for obs in observations]
        extra_t = torch.Tensor(extra).to(res_t.device)
        res_t = torch.cat([res_t, extra_t], dim=1)
        return res_t
```

가변 시퀀스 외에도, 추가 "플래그" 필드를 인코딩된 텐서에 직접 이어붙일 수 있다. 이 기능은 이후 실험과 확장에서 쓰인다(예: "방문한 방 추적" 확장).

마지막으로, `encode_sequences()`와 `encode_commands()` 두 메서드는 가변 길이 시퀀스 배치에 서로 다른 인코더를 적용하는 데 쓰인다.

```python
    def encode_sequences(self, batches):
        data = []
        for enc, enc_batch in zip(self.encoders, zip(*batches)):
            data.append(self._apply_encoder(enc_batch, enc))
        res_t = torch.cat(data, dim=1)
        return res_t

    def encode_commands(self, batch):
        return self._apply_encoder(batch, self.enc_commands)
```

### 5.3 DQN 모델과 에이전트

여기까지 준비가 끝났으니, 이제 우리 에이전트의 두뇌인 DQN 모델을 살펴보자. 이 모델은 `num_sequences × encoder_size` 크기의 벡터를 입력받아 스칼라 값 하나를 출력해야 한다. 하지만 지금까지 다룬 다른 DQN 모델들과 모델을 **적용하는 방식**에 차이가 있다.

```python
class DQNModel(nn.Module):
    def __init__(self, obs_size: int, cmd_size: int, hid_size: int = 256):
        super(DQNModel, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(obs_size + cmd_size, hid_size),
            nn.ReLU(),
            nn.Linear(hid_size, 1)
        )

    def forward(self, obs, cmd):
        x = torch.cat((obs, cmd), dim=1)
        return self.net(x)

    @torch.no_grad()
    def q_values(self, obs_t, commands_t):
        result = []
        for cmd_t in commands_t:
            qval = self(obs_t, cmd_t.unsqueeze(0))[0].cpu().item()
            result.append(qval)
        return result
```

앞의 코드에서 `forward()` 메서드는 관측과 명령, 두 배치를 받아 각 쌍에 대한 Q값들의 배치를 만든다. 또 다른 메서드 `q_values()`는 `Preprocessor` 클래스가 만든 관측 하나와, 인코딩된 명령들의 텐서를 받아, **모든 명령 각각에 대한** Q값 목록을 반환한다.

`model.py` 모듈에는 `DQNAgent` 클래스도 있는데, 이는 전처리기를 받아 의사결정 시 관측 전처리의 세부사항을 감춰주는 PTAN Agent 인터페이스를 구현한다.

### 5.4 학습 코드

전처리와 준비가 다 끝났으니, 나머지 코드는 이전 챕터들에서 이미 구현한 것과 거의 같다. 그래서 학습 코드를 다시 싣지 않고, 학습 로직만 설명한다.

모델을 학습하려면 `Chapter13/train_basic.py` 유틸리티를 쓴다. 다음과 같은 커맨드라인 인자로 학습 동작을 바꿀 수 있다.

- `-g` 또는 `--game`: `games` 디렉터리에 있는 게임 파일들의 접두사. 제공된 스크립트는 `simpleNN.ulx`(NN은 게임 시드)라는 이름의 게임 여러 개를 생성한다.
- `-s` 또는 `--suffices`: 학습에 사용할 게임 개수. 기본값은 1이며, 이 경우 `simple1.ulx` 파일만 학습에 쓰인다. `-s 10`을 주면 인덱스 1~10인 게임 10개가 등록되어 학습에 쓰인다. 이 옵션은 학습 게임의 다양성을 높이기 위한 것으로, 목표는 구체적인 게임 하나만 잘 푸는 게 아니라 (바라건대) 비슷한 다른 게임에서도 잘 행동하도록 배우는 것이다.
- `-v` 또는 `--validation`: 검증에 쓸 게임의 접미사. 기본값은 `-val`이며, 학습된 에이전트의 일반화 능력을 확인하는 데 쓸 게임 파일을 지정한다.
- `--params`: 사용할 하이퍼파라미터. `lib/common.py`에 `small`과 `medium` 두 세트가 정의되어 있다. 첫 번째는 임베딩과 인코더 벡터 개수가 적어서, 게임 몇 개를 빠르게 푸는 데는 훌륭하지만 많은 게임으로 학습할 때는 수렴에 어려움을 겪는다.
- `--dev`: 계산에 쓸 디바이스 이름을 지정한다.
- `-r` 또는 `--run`: 실행 이름. 저장 디렉터리와 TensorBoard의 이름에 쓰인다.

학습 중에는 100번의 학습 반복마다 검증이 수행되며, 현재 네트워크로 검증 게임을 실행한다. 보상과 스텝 수는 TensorBoard에 기록되어, 우리 에이전트의 일반화 능력을 파악하는 데 도움을 준다. RL에서 일반화는 큰 이슈로 알려져 있다. 제한된 궤적 집합으로 학습하다 보니, 학습 과정이 특정 상태들에 과적합되기 쉽고, 보지 못한 게임에서 좋은 행동을 한다는 보장이 없기 때문이다. Atari 게임에서는 게임플레이가 보통 크게 바뀌지 않는 것과 비교하면, 인터랙티브 픽션 게임은 서로 다른 퀘스트·물건·소통 방식 때문에 변동성이 훨씬 클 수 있다. 그래서 우리 에이전트가 게임들 사이에서 얼마나 잘 일반화하는지 확인하는 것은 흥미로운 실험이다.

### 5.5 학습 결과

기본적으로 `games/make_games.sh` 스크립트는 `simple1.ulx`부터 `simple20.ulx`까지 이름 붙은 게임 20개와, 검증용 게임 `simple-val.ulx`를 생성한다.

먼저 게임 하나로, `small` 하이퍼파라미터 세트를 써서 에이전트를 학습해보자.

```bash
$ ./train_basic.py -s 1 --dev cuda -r t1
Registered env tw-simple-v0 for game files ['games/simple1.ulx']
Game tw-simple-v1, with file games/simple-val.ulx will be used for validation
Episode 1: reward=0 (avg 0.00), steps=50 (avg 50.00), speed=0.0 f/s, elapsed=0:00:04
Episode 2: reward=1 (avg 0.02), steps=50 (avg 50.00), speed=0.0 f/s, elapsed=0:00:04
1: best avg training reward: 0.020, saved
Episode 3: reward=-2 (avg -0.02), steps=50 (avg 49.60), speed=0.0 f/s, elapsed=0:00:04
Episode 4: reward=6 (avg 0.10), steps=30 (avg 49.60), speed=0.0 f/s, elapsed=0:00:04
...
```

`-s` 옵션은 학습에 쓸 게임 인덱스 개수를 지정한다. 이 경우 게임 하나만 쓴다. 에피소드당 평균 스텝 수가 15 아래로 떨어지면 학습이 멈추는데, 이는 에이전트가 올바른 행동 순서를 찾아내 게임을 효율적으로 끝까지 갈 수 있게 됐다는 뜻이다.

게임 하나만 쓸 경우 약 3분, 약 120에피소드 만에 게임을 풀어낸다. 다음 그림은 학습 중 보상과 스텝 수의 변화다.

![[fig_13_7.png]]
*그림 13.7 — 게임 1개로 학습했을 때의 학습 보상(왼쪽)과 에피소드당 스텝 수(오른쪽)*

하지만 검증 보상(게임 `simple-val.ulx`에서 얻은 보상)을 확인해보면, 시간이 지나도 전혀 개선되지 않는다. 필자의 경우 검증 보상은 계속 0이었고, 검증 에피소드의 스텝 수는 기본 시간 제한인 50에 머물렀다. 즉 학습된 에이전트가 **일반화하지 못했다**는 뜻이다.

학습에 쓰는 게임 수를 늘리면, 신경망이 여러 상태에서 더 많은 행동 순서를 찾아내야 하므로 수렴에 더 많은 시간이 걸린다. 다음은 게임 20개로 학습했을 때(`-s 20` 옵션)의 같은 보상·스텝 차트다.

![[fig_13_8.png]]
*그림 13.8 — 게임 20개로 학습했을 때의 학습 보상(왼쪽)과 에피소드당 스텝 수(오른쪽)*

수렴까지 거의 2시간이 걸리지만, 그래도 우리의 작은 하이퍼파라미터 세트로 20개 게임에서의 성능을 개선할 수 있었다.

검증 지표는 다음 그림에서 볼 수 있듯 조금 더 흥미로워졌다. 학습이 끝날 무렵 에이전트는 최대 점수 6점 중 2점을 얻었고, 학습 중간쯤에는 4점을 얻기도 했다. 하지만 검증 게임의 스텝 수는 여전히 50으로, 에이전트가 그냥 어느 정도 무작위로 돌아다니며 행동을 실행하고 있다는 뜻이다. 그다지 인상적이지는 않다.

![[fig_13_9.png]]
*그림 13.9 — 게임 20개 학습 중 검증 보상*

이 에이전트에 대해 다른 하이퍼파라미터(`-s medium`으로 시도 가능)는 따로 시도해보지 않았다.

---

## 6. 관측 튜닝하기 (Tweaking Observations)

첫 번째 개선 시도는 에이전트에게 **더 많은 정보를 제공**하는 것이다. 여기서는 각 수정이 학습 결과에 미친 효과를 간단히 소개한다. 전체 예제 코드는 `Chapter13/train_preproc.py`에 있다.

### 6.1 방문한 방 추적하기

먼저 알 수 있는 사실: 우리 에이전트는 지금 있는 방을 **이미 가본 적 있는지 없는지** 전혀 모른다. 정책이 이미 최적 경로를 알고 있는 상황이라면 이 정보가 필요 없을 수도 있다(생성된 게임은 항상 방이 다르니까). 하지만 정책이 완벽하지 않다면, 같은 방을 반복해서 돌고 있다는 것을 명확히 알려주는 게 유용할 수 있다.

이 지식을 관측에 반영하기 위해, `preproc.LocationWrapper` 클래스에 간단한 방 추적 기능을 구현했다. 이 클래스는 에피소드 동안 방문한 방들을 추적한다. 그러면 이 플래그가 에이전트의 관측에 **단일 숫자 1(이전에 방문한 방이면) 또는 0(새 위치면)** 으로 이어붙여진다.

에이전트를 이 확장 기능으로 학습시키려면, `train_preproc.py`를 추가 커맨드라인 옵션 `--seen-rooms`와 함께 실행하면 된다.

다음은 20개 게임에서 베이스라인 버전과 이 추가 관측을 비교한 차트다. 보다시피, 학습 게임에서의 보상은 거의 같지만 **검증 보상이 개선**되었다 — 학습 내내 거의 계속 0이 아닌 검증 보상을 얻을 수 있었다. 다만 검증 게임에서의 스텝 수는 여전히 50이다.

![[fig_13_10.png]]
*그림 13.10 — 게임 20개에서의 학습 보상(왼쪽)과 검증 보상(오른쪽)*

하지만 이 확장 기능을 게임 200개로 시도해본 결과(생성 스크립트를 수정해야 함), 흥미로운 결과를 얻었다. 14시간의 학습과 8,000 에피소드 뒤, 에이전트는 검증 게임에서 최대 점수를 받았을 뿐 아니라 이를 **효율적으로**(10 스텝 미만으로) 해낼 수 있었다. 이는 그림 13.11과 그림 13.12에 나타나 있다.

![[fig_13_11.png]]
*그림 13.11 — 게임 200개에서의 학습 보상(왼쪽)과 에피소드 스텝 수(오른쪽)*

![[fig_13_12.png]]
*그림 13.12 — 검증 보상(왼쪽)과 에피소드 스텝 수(오른쪽)*

> [!success] 핵심 관찰
> 방 하나짜리 신호(방문했는지 여부) 하나만 더해줘도, **학습 게임의 다양성이 충분히 클 때**(200개) 일반화 성능이 극적으로 좋아졌다. 게임 20개로는 이 효과가 뚜렷하지 않았다. 즉, 좋은 관측 설계와 충분한 데이터 다양성이 함께 갖춰져야 일반화가 이루어진다는 것을 보여준다.

### 6.2 상대적 행동 (Relative Actions)

에이전트 학습을 개선하기 위한 두 번째 시도는 **행동 공간**에 관한 것이다. 원칙적으로 우리 에이전트의 임무는 방을 이동하고, 주변 물건에 특정 행동(예: 사물함을 열고 안에서 무언가를 꺼내는 것)을 하는 것이다. 그래서 내비게이션(이동)은 학습 과정에서 매우 중요한 요소다.

현재 우리는 "go north"(북쪽으로 가라)나 "go east"(동쪽으로 가라) 같은 **절대 좌표 방식**의 명령으로 이동한다. 이는 방마다 다르다 — 방마다 이용 가능한 출구가 다를 수 있기 때문이다. 게다가 어떤 행동을 실행한 뒤, 원래 방으로 돌아가려는 역방향 행동은 **처음 실행했던 행동에 따라 달라진다.** 예를 들어 북쪽으로 나가는 출구가 있는 방에 있다면, 그 출구로 나간 뒤 돌아가려면 "go south"를 실행해야 한다. 하지만 우리 에이전트는 행동의 이력을 기억하지 못하므로, 북쪽으로 간 뒤 어떻게 돌아가야 할지 전혀 알 수 없다.

앞 절에서는 방이 방문됐는지 여부에 대한 정보를 추가했다. 이번에는 절대 행동을 **상대 행동**으로 바꿔보자. 이를 위해 `preproc.RelativeDirectionsWrapper` 래퍼를 만들었는데, 이 래퍼는 **바라보는 방향(heading direction)** 을 추적하며 "go north"나 "go east" 같은 명령을 헤딩 방향에 따라 "go left"(왼쪽), "go right"(오른쪽), "go forward"(앞으로), "go back"(뒤로)으로 바꿔준다. 예를 들어 북쪽으로 나가는 출구가 있는 방에 있고 현재 북쪽을 바라보고 있다면, 그 출구를 쓰려면 "go forward" 명령을 실행해야 한다. 그 뒤에는 "go back" 명령으로 원래 방으로 돌아갈 수 있다. 이런 변환을 통해 우리 모델이 TextWorld 게임을 좀 더 쉽게 탐색할 수 있기를 기대한다.

이 확장 기능을 켜려면 `train_preproc.py`를 `--relative-actions` 커맨드라인 옵션과 함께 실행하면 된다. 이 확장은 "방문한 방" 기능이 함께 켜져 있어야 하므로, 여기서는 두 수정을 함께 적용한 효과를 테스트하는 셈이다.

게임 20개에서는 학습 동역학과 검증 결과가 베이스라인 버전과 매우 비슷하다(그림 13.13).

![[fig_13_13.png]]
*그림 13.13 — 게임 20개에서의 학습 보상(왼쪽)과 검증 보상(오른쪽)*

하지만 게임 200개에서는, 에이전트가 겨우 2.5시간 만에 검증 게임에서 최대 점수를 얻을 수 있었다("방문한 방" 확장에서는 13시간이 걸렸던 것과 비교된다). 검증에서의 스텝 수도 10 아래로 줄었다. 다만 아쉽게도, 학습을 더 진행하자 검증 지표가 다시 낮은 점수로 되돌아갔다 — 에이전트가 게임에 **과적합**되어 이전에 배웠던 기술을 잊어버린 것이다.

![[fig_13_14.png]]
*그림 13.14 — 게임 200개에서의 검증 보상(왼쪽)과 에피소드 스텝 수(오른쪽)*

> [!warning] 빠른 학습과 과적합은 한 세트로 온다
> 상대 행동 덕분에 훨씬 빠르게 최고 성능에 도달했지만, 그만큼 그 지점을 지나 계속 학습하면 오히려 성능이 붕괴할 위험도 커졌다. 검증 곡선이 정점을 찍었을 때 학습을 멈추는 것(조기 종료, early stopping)이 실전에서는 중요한 이유다.

### 6.3 관측에 목표 포함하기 (Objective in Observation)

또 다른 아이디어는 **게임의 목표(objective)** 를 에이전트의 관측에 함께 넣어주는 것이다. 목표는 게임 시작 시점에 텍스트로 주어진다. 예를 들면 다음과 같다.

> *"First thing I need you to do is to try to venture east. Then, venture south. After that, try to go to the south. Once you succeed at that, try to go west. If you can finish that, pick up the coin from the floor of the chamber. Once that's all handled, you can stop!"*
> (먼저 동쪽으로 가라. 그다음 남쪽으로 가라. 그다음 다시 남쪽으로 가라. 그게 끝나면 서쪽으로 가라. 그걸 마치면 방바닥에서 동전을 주워라. 그러면 끝이다!)

이 정보는 에이전트가 자신의 행동을 **계획**하는 데 도움이 될 수 있으므로, 이를 인코딩된 벡터에 추가해보자. 우리 래퍼들이 이미 충분히 유연하므로 새 래퍼를 따로 구현할 필요는 없다. 그저 몇 가지 추가 인자만 넘겨주면 된다. 목표를 켜려면 `train_preproc.py`를 `-objective` 커맨드라인 인자와 함께 실행한다.

게임 20개에서의 결과는 베이스라인과 거의 동일하며, 그림 13.15에 나타나 있다.

![[fig_13_15.png]]
*그림 13.15 — 게임 20개에서의 학습 보상(왼쪽)과 검증 보상(오른쪽)*

게임 200개에서의 학습은 앞의 개선들보다 덜 성공적이었다. 검증 중 점수는 2~4 사이를 오갔고 한 번도 6점(최대 점수)에 도달하지 못했다. 보상과 검증 보상 차트는 그림 13.16과 같다.

![[fig_13_16.png]]
*그림 13.16 — 게임 200개에서의 학습 보상(왼쪽)과 검증 보상(오른쪽)*

> [!note] 왜 목표 추가가 기대만큼 효과가 없었을까
> 목표 텍스트는 정보량이 많지만, 그 자체로 "지금 무엇을 해야 하는가"를 곧바로 알려주지는 않는다. 에이전트가 이 긴 지시문을 현재 상태와 연결지어 "다음 행동"으로 변환하는 것 자체가 또 다른 어려운 학습 과제이기 때문에, 단순히 정보를 더 준다고 해서 항상 성능이 좋아지는 것은 아니라는 점을 보여준다.

---

## 7. 트랜스포머 (Transformers)

다음으로 시도해볼 접근은 **사전 학습된 언어 모델**이며, 이는 현대 NLP의 사실상 표준이다. Hugging Face Hub 같은 공개 모델 저장소 덕분에, 처음부터 모델을 학습할 필요가 없다(비용이 매우 클 수 있다). 사전 학습된 모델을 우리 아키텍처에 그대로 꽂아 넣고, 신경망의 일부만 우리 데이터셋에 맞춰 미세 조정(fine-tune)하면 된다.

모델은 크기, 학습에 쓰인 데이터셋, 학습 기법 등이 서로 다른 매우 다양한 종류가 있다. 하지만 모두 단순한 API를 쓰므로, 우리 코드에 꽂아 넣는 일은 간단하고 직관적이다.

먼저 라이브러리를 설치해야 한다. 이 작업에는 `sentence-transformers==2.6.1` 패키지를 수동으로 설치해서 쓴다. 설치가 끝나면, 문자열로 주어진 어떤 문장이든 임베딩을 계산하는 데 쓸 수 있다.

```python
>>> from sentence_transformers import SentenceTransformer
>>> tr = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
>>> tr.get_sentence_embedding_dimension()
384
>>> r = tr.encode("You're standing in an ordinary boring room")
>>> type(r)
<class 'numpy.ndarray'>
>>> r.shape
(384,)
>>> r2 = tr.encode(["sentence 1", "sentence 2"], convert_to_tensor=True)
>>> type(r2)
<class 'torch.Tensor'>
>>> r2.shape
torch.Size([2, 384])
```

여기서는 `all-MiniLM-L6-v2` 모델을 썼는데, 상대적으로 작은 모델로 파라미터 2,200만 개, 학습 토큰 12억 개 규모다. 더 자세한 정보는 Hugging Face 웹사이트([https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2))에서 볼 수 있다.

이 예제에서는 고수준 인터페이스를 쓴다 — 문장이 담긴 문자열을 넣어주면 라이브러리와 모델이 알아서 변환해준다. 필요하다면 훨씬 세부적인 제어도 가능하다.

`preproc.TransformerPreprocessor` 클래스는 (LSTM으로 임베딩을 만들던) 예전 `Preprocessor` 클래스와 **동일한 인터페이스**를 구현하므로, 코드는 매우 직관적이라 따로 싣지 않는다.

트랜스포머로 에이전트를 학습하려면 `Chapter13/train_tr.py` 모듈을 실행하면 된다. 학습 도중, 트랜스포머는 (필자의 컴퓨터 기준) LSTM 모델보다 느렸다(2 FPS 대 6 FPS). 모델이 훨씬 복잡하니 놀랍지 않은 결과다. 하지만 학습 동역학은 게임 20개와 200개 모두에서 더 좋았다. 그림 13.17에서 트랜스포머와 베이스라인의 학습 보상, 에피소드 스텝 수를 볼 수 있다. 베이스라인 버전은 15 스텝에 도달하는 데 1,000 에피소드가 필요했지만, 트랜스포머는 겨우 400 에피소드만 필요했다. 다만 게임 20개에서의 검증 성능은 베이스라인보다 나빴다(최대 점수는 2였다).

![[fig_13_17.png]]
*그림 13.17 — 게임 20개에서의 학습 보상(왼쪽)과 학습 에피소드 길이(오른쪽)*

게임 200개에서도 비슷한 상황이었다 — 에이전트는 (게임 수 대비) 더 효율적으로 배웠지만, 검증 성능은 그다지 좋지 않았다. 이는 트랜스포머의 훨씬 큰 표현 능력으로 설명할 수 있다 — 트랜스포머가 만드는 임베딩은 우리 베이스라인 모델보다 거의 20배 크다(384 대 20). 그래서 에이전트가 고수준의 일반적인 관측-행동 매핑을 찾으려 애쓰는 대신, 그냥 정답 스텝 순서를 통째로 **암기**해버리기가 더 쉬워진 것이다.

> [!important] 큰 모델 = 항상 좋은 모델이 아니다
> 트랜스포머 임베딩은 훨씬 풍부한 정보를 담고 있지만, 그만큼 학습 데이터의 세부사항을 통째로 암기하기도 쉬워진다. RL에서 일반화가 목표라면, 모델의 표현력을 늘리는 것이 항상 도움이 되는 것은 아니며 오히려 과적합을 부추길 수 있다.

---

## 8. ChatGPT

TextWorld 논의를 마무리하기 위해, 마지막으로 다른 접근 — **LLM 사용** — 을 시도해보자. 2022년 말 공개 직후, OpenAI ChatGPT는 매우 인기를 끌었다. 출시 1년 만에 수백 개의 새로운 사용 사례가 등장했고, LLM을 내부에 탑재한 애플리케이션이 수천 개 개발되었다. 이 기술을 우리의 TextWorld 게임 풀이 문제에 적용해보자.

### 8.1 설정

먼저 [https://openai.com](https://openai.com)에 계정이 필요하다. 처음에는 웹 기반 대화형 채팅으로 실험을 시작하는데, 이 책 집필 시점 기준 무료로 가입 없이 사용해볼 수 있다. 다음 예제에서는 ChatGPT API를 쓰는데, 이를 위해서는 [https://platform.openai.com](https://platform.openai.com)에서 API 키를 생성해야 한다. 키를 만들었으면, 사용 중인 셸에서 환경 변수 `OPENAI_API_KEY`에 설정해야 한다.

파이썬에서 ChatGPT와 통신하기 위해 `langchain` 라이브러리([https://python.langchain.com/](https://python.langchain.com/))도 쓴다. 다음 명령으로 설치한다.

```bash
$ pip install langchain==0.1.15 langchain-openai==0.1.2
```

> [!warning] 버전 호환성 주의
> 이 패키지들은 변화가 상당히 빠른 편이라, 새 버전이 호환성을 깨뜨릴 수 있다.

### 8.2 대화형 모드 (Interactive Mode)

첫 예제에서는 웹 기반 ChatGPT 인터페이스를 써서, 방 설명과 게임 목표로부터 게임 명령을 생성하도록 요청한다. 코드는 `Chapter13/chatgpt_interactive.py`에 있으며 다음 순서로 동작한다.

1. 커맨드라인에서 지정한 게임 ID로 TextWorld 환경을 시작한다.
2. 지시문, 게임 목표, 방 설명을 담은 ChatGPT용 프롬프트를 만든다.
3. 이 프롬프트를 콘솔에 출력한다.
4. 콘솔에서 실행할 명령을 입력받는다.
5. 그 명령을 환경에서 실행한다.
6. 스텝 한도에 도달하거나 게임을 풀 때까지 2번부터 반복한다.

즉, 사용자가 할 일은 생성된 프롬프트를 복사해 [https://chat.openai.com](https://chat.openai.com) 웹 인터페이스에 붙여넣는 것이다. 그러면 ChatGPT가 콘솔에 입력해야 할 명령을 생성해준다.

전체 코드는 매우 단순하고 짧다. 게임 루프를 실행하는 `play_game` 함수 하나만 있다.

```python
env_id = register_game(
    gamefile=f"games/{args.game}{index}.ulx",
    request_infos=EnvInfos(description=True, objective=True),
)
env = gym.make(env_id)
```

환경을 만들 때, 부가 정보 두 가지만 요청한다 — 방 설명과 게임 목표다. 원칙적으로는 이 둘 다 자유 텍스트 관측에 이미 포함되어 있어서 파싱할 수도 있지만, 편의를 위해 TextWorld가 명시적으로 제공하도록 요청한다.

`play_game` 함수 시작 부분에서는 환경을 리셋하고 초기 프롬프트를 생성한다.

```python
def play_game(env, max_steps: int = 20) -> bool:
    commands = []

    obs, info = env.reset()

    print(textwrap.dedent("""\
    You're playing the interactive fiction game.
    Here is the game objective: %s

    Here is the room description: %s

    What command do you want to execute next? Reply with
    just a command in lowercase and nothing else.
    """)  % (info['objective'], info['description']))

    print("=== Send this to chat.openai.com and type the reply...")
```

마지막 문장 *"Reply with just a command in lowercase and nothing else."*(그냥 소문자로 명령만 답하고 다른 건 아무것도 쓰지 마)는 챗봇이 너무 장황해지는 걸 막아주고, 출력을 파싱하는 수고를 덜어준다.

그다음 게임이 풀리거나 스텝 한도에 도달할 때까지 루프를 실행한다.

```python
    while len(commands) < max_steps:
        cmd = input(">>> ")
        commands.append(cmd)
        obs, r, is_done, info = env.step(cmd)
        if is_done:
            print(f"You won in {len(commands)} steps! "
                  f"Don't forget to congratulate ChatGPT!")
            return True

        print(textwrap.dedent("""\
        Last command result: %s
        Room description: %s

        What's the next command?
        """) % (obs, info['description']))
        print("=== Send this to chat.openai.com and type the reply...")

    print(f"Wasn't able to solve after {max_steps} steps, commands: {commands}")
    return False
```

이어지는 프롬프트는 훨씬 단순하다 — 실행된 명령의 결과(관측)와 새로운 방 설명만 넘겨준다. 목표를 다시 넘길 필요는 없는데, 웹 인터페이스가 대화의 맥락을 계속 유지해주므로 챗봇이 이전 지시를 계속 기억하기 때문이다.

시드 1을 쓴 게임 테스트 결과를 살펴보자. 필자는 방 설명을 지면 관계상 생략했지만, 실제로는 생성된 텍스트를 전부 복사해야 한다.

```
$ ./chatgpt_interactive.py 1
Starting game 1

You're playing the interactive fiction game.
Here is the game objective: Get ready to pick stuff up and put it in places, because
you've just entered TextWorld! Here is your task for today. First stop, go to the south.
And then, head east. With that over with, make an effort to go north. With that
accomplished, ensure that the type D locker is open. Then, take the keyboard from the
type D locker. That's it!

Here is the room description: -= Spare Room =-
What command do you want to execute next? Reply with
just a command in lowercase and nothing else.

=== Send this to chat.openai.com and type the reply...
>>> go south
```

```
Last command result: -= Dish-Pit =-
Room description: -= Dish-Pit =-
What's the next command?

=== Send this to chat.openai.com and type the reply...
>>> go east
Last command result: -= Cookhouse =-
Room description: -= Cookhouse =-
What's the next command?

=== Send this to chat.openai.com and type the reply...
>>> go north
Last command result: -= Studio =-
Room description: -= Studio =-
What's the next command?

=== Send this to chat.openai.com and type the reply...
>>> open type d locker
Last command result: You open the type D locker, revealing a keyboard.
Room description: -= Studio =-
What's the next command?

=== Send this to chat.openai.com and type the reply...
>>> take keyboard
You won in 5 steps! Don't forget to congratulate ChatGPT!
```

LLM이 과제를 완벽하게 풀어냈다. 더욱 놀라운 것은, 이번 과제는 앞서 챕터에서 다룬 것보다 더 어려운 형태였다는 점이다 — "실행 가능 명령 목록" 중 하나를 고르는 게 아니라, **명령 자체를 처음부터 생성**하도록 요청했기 때문이다.

### 8.3 ChatGPT API

복사-붙여넣기는 번거롭고 지루하므로, ChatGPT API를 이용해 에이전트를 자동화해보자. `langchain` 라이브러리([https://python.langchain.com/](https://python.langchain.com/))는 LLM 기능을 활용할 수 있는 충분한 유연성과 제어력을 제공한다.

전체 코드 예제는 `Chapter13/chatgpt_auto.py`에 있다. 여기서는 핵심 함수인 `play_game()`만 살펴본다.

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def play_game(env, max_steps: int = 20) -> bool:
    prompt_init = ChatPromptTemplate.from_messages([
        ("system", "You're playing the interactive fiction game. "
                   "Reply with just a command in lowercase and nothing else"),
        ("system", "Game objective: {objective}"),
        ("user", "Room description: {description}"),
        ("user", "What command you want to execute next?"),
    ])
    llm = ChatOpenAI()
    output_parser = StrOutputParser()
```

초기 프롬프트는 이전과 같다 — 챗봇에게 어떤 종류의 게임을 하는지 알려주고, 게임에 넣을 명령만 답하도록 요청한다.

그다음 환경을 리셋하고 첫 메시지를 생성하는데, 이때 TextWorld에서 얻은 정보를 넘긴다.

```python
    commands = []

    obs, info = env.reset()
    init_msg = prompt_init.invoke({
        "objective": info['objective'],
        "description": info['description'],
    })

    context = init_msg.to_messages()
    ai_msg = llm.invoke(init_msg)
    context.append(ai_msg)
    cmd = output_parser.invoke(ai_msg)
```

`context` 변수는 매우 중요하다 — 지금까지 챗봇과 나눈 (사람 쪽·챗봇 쪽 모두의) 메시지 목록 전체를 담고 있다. 이 메시지들을 챗봇에 넘겨서 게임 진행 과정을 계속 기억하게 한다. 게임 목표는 딱 한 번만 보여주고 반복하지 않기 때문에 이 이력이 꼭 필요하다. 반면 챗봇에 너무 많은 텍스트를 계속 넘기면 비용이 커질 수 있다(ChatGPT API는 처리한 토큰 수에 따라 과금되기 때문이다). 우리 게임은 그리 길지 않아서(5~7 스텝이면 충분) 큰 걱정거리는 아니지만, 더 복잡한 게임이라면 이력 관리를 최적화해야 할 수도 있다.

그다음 게임 루프가 이어지는데, 콘솔과의 소통이 없다는 점만 빼면 대화형 버전과 매우 비슷하다.

```python
    prompt_next = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Last command result: {result}"),
        ("user", "Room description: {description}"),
        ("user", "What command you want to execute next?"),
    ])

    for _ in range(max_steps):
        commands.append(cmd)
        print(">>>", cmd)
        obs, r, is_done, info = env.step(cmd)
        if is_done:
            print(f"I won in {len(commands)} steps!")
            return True

        user_msgs = prompt_next.invoke({
            "chat_history": context,
            "result": obs.strip(),
            "description": info['description'],
        })
        context = user_msgs.to_messages()
        ai_msg = llm.invoke(user_msgs)
        context.append(ai_msg)
        cmd = output_parser.invoke(ai_msg)
```

이어지는 프롬프트에서는 대화 이력, 마지막 명령의 결과, 현재 방 설명을 넘기고 다음 명령을 요청한다.

또한 에이전트가 무한 루프에 빠지는 것을 막기 위해 스텝 수도 제한한다(가끔 실제로 그런 일이 벌어진다). 스텝 한도 안에 게임이 풀리지 않으면 루프를 종료한다.

```python
    print(f"Wasn't able to solve after {max_steps} steps, commands: {commands}")
    return False
```

앞의 코드를 TextWorld 게임 20개(시드 1~20)로 테스트해본 결과, 20개 중 **9개**를 풀 수 있었다. 실패한 상황 대부분은 에이전트가 루프에 빠졌기 때문이었다 — TextWorld가 제대로 해석하지 못하는 잘못된 명령을 계속 내는 경우("take the key from the box" 대신 "take the key"라고 하는 식)나, 내비게이션에서 막히는 경우가 있었다.

두 게임에서는 ChatGPT가 "exit"(종료) 명령을 생성해버려서 실패했는데, 이 명령은 TextWorld를 즉시 멈추게 만든다. 이런 명령의 생성을 감지하거나 프롬프트에서 아예 금지하면 풀 수 있는 게임 수를 더 늘릴 수 있을 것이다.

> [!success] 사전 학습 없이도 9/20
> 어떤 사전 학습도 없이 에이전트가 20개 중 9개 게임을 풀었다는 것은 그 자체로 인상적인 결과다. ChatGPT 비용 측면에서는, 이 실험을 돌리는 데 45만 토큰이 처리되었고 비용은 0.20달러였다. 재미로 하기에는 크지 않은 가격이다!

---

## 요약

이 챕터에서는 DQN이 인터랙티브 픽션 게임(TextWorld)에 어떻게 적용될 수 있는지 살펴봤다. 이는 RL과 NLP가 교차하는 흥미롭고 도전적인 영역이다. 복잡한 텍스트 데이터를 NLP 도구로 다루는 법을 배웠고, 재미있으면서도 도전적인 인터랙티브 픽션 환경으로 실험했다. 구체적으로는 다음을 다뤘다.

1. **인터랙티브 픽션의 역사와 TextWorld 환경**: 텍스트로만 진행되는 게임의 배경, 그리고 이를 Gym 스타일 인터페이스로 감싼 Microsoft Research의 TextWorld를 설치·생성·실행하는 법을 배웠다.
2. **관측·행동 공간의 특수성**: 텍스트 게임의 관측은 가변 길이 시퀀스이고, 행동 공간은 실행 가능 명령이라는 형태로 극적으로 줄일 수 있지만 여전히 가변적이라는 점, 그리고 인벤토리처럼 부분 관측(POMDP)이 되는 부분을 확인했다.
3. **딥 NLP 기초**: 가변 길이 시퀀스를 다루는 RNN·LSTM, 단어를 벡터로 바꾸는 워드 임베딩, 입력을 압축했다가 새로 생성하는 Encoder-Decoder(seq2seq), 그리고 어텐션을 중심으로 한 트랜스포머까지 훑었다.
4. **베이스라인 DQN 구현**: LSTM 인코더로 여러 텍스트 필드를 각각 고정 크기 벡터로 압축하고, 이를 이어붙여 하나의 (관측, 명령) 쌍마다 Q값을 예측하는 아키텍처를 구현했다.
5. **관측 튜닝 실험**: 방문한 방 추적, 상대적 행동, 목표 포함이라는 세 가지 확장을 시도하며, 각각이 학습 속도와 일반화 성능에 미치는 다양한(때로는 예상 밖의) 효과를 관찰했다.
6. **사전 학습된 트랜스포머 적용**: Hugging Face의 `sentence-transformers`로 LSTM 인코더를 대체해, 더 크고 스마트한 임베딩이 학습 속도는 높이지만 반드시 일반화까지 개선하지는 않는다는 점을 확인했다.
7. **ChatGPT로 같은 문제 풀기**: 웹 인터페이스와 API 양쪽으로 LLM을 활용해, 사전 학습이나 강화학습 없이도 상당수의 게임을 풀어낼 수 있음을 보였다.

다음 챕터에서는 "실전 속의 RL" 탐구를 계속하며, 웹 자동화(web automation) 분야에서 RL 방법이 얼마나 적용 가능한지 살펴본다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[RNN 순환신경망]]
- [[LSTM 장단기메모리]]
- [[워드 임베딩 Word Embedding]]
- [[Encoder-Decoder와 seq2seq]]
- [[Transformer 트랜스포머]]
- [[POMDP 부분관측 마르코프결정과정]]
- [[원-핫 인코딩]]
- [[상태 관측 에피소드 정책]]
- [[타깃 네트워크와 부트스트래핑]]

## 한눈에 보는 개념 지도
| 개념 | 기호/용어 | 한 줄 뜻 |
|---|---|---|
| 인터랙티브 픽션 | Interactive Fiction | 텍스트로만 진행되는 어드벤처 게임 장르 |
| TextWorld | `textworld` | Microsoft Research가 만든 텍스트 게임용 RL 환경 |
| 실행 가능 명령 | admissible_commands | 현재 상태에서 실제로 의미 있는 명령 목록 (행동 공간 축소) |
| 중간 보상 | intermediate_reward | 올바른 방향으로 한 걸음마다 주어지는 보조 보상 |
| POMDP | Partially Observable MDP | 상태 전체가 아니라 일부(관측)만 보이는 MDP |
| RNN | Recurrent NN | hidden state를 넘기며 가변 길이 시퀀스를 처리하는 신경망 |
| LSTM | Long Short-Term Memory | 게이트로 기억·망각을 조절하는 RNN의 개선판 |
| 워드 임베딩 | Word Embedding | 단어를 조밀한 고정 길이 벡터로 매핑 |
| 인코더 | Encoder | 가변 길이 시퀀스 → 고정 크기 벡터 |
| Encoder-Decoder | seq2seq | 인코딩 후 새 시퀀스를 생성하는 구조 |
| 트랜스포머 | Transformer | 어텐션 기반의 현대 NLP 표준 아키텍처 |
| 문장 임베딩 | Sentence Transformer | 사전 학습된 트랜스포머로 문장 전체를 벡터화 |
| LLM 활용 | ChatGPT API | 학습 없이 자연어 이해·생성 능력으로 게임을 직접 풀기 |
