---
title: "Chapter 20 — AlphaGo Zero와 MuZero (AlphaGo Zero and MuZero)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 20
tags: [DeepRL, 강화학습, 모델기반RL, AlphaGoZero, MuZero, MCTS, 자기대국, 보드게임]
---

# Chapter 20 · AlphaGo Zero와 MuZero

> [!abstract] 이 챕터를 한 문장으로
> **AlphaGo Zero**는 바둑·체스 같은 보드게임에서, 게임 규칙만 알려주고 사람의 기보 없이 **자기 자신과 무수히 대국(자기대국)** 시키면서 [[몬테카를로 트리 탐색 MCTS|몬테카를로 트리 탐색(MCTS)]]으로 다음 수를 고르는 **모델 기반(model-based)** 강화학습 방법이며, 후속작 **MuZero**는 여기서 한 발 더 나아가 **게임 규칙 자체도 신경망이 스스로 배우게** 해서 아타리 게임처럼 규칙을 코드로 옮기기 어려운 환경까지 정복했다.

---

## 들어가며 — 이번 챕터에서 배울 것

이 책에서 지금까지 다룬 방법들(DQN, 정책 경사, 액터-크리틱 등)은 모두 **모델-프리(model-free)** 방법이었다. 즉, 환경이 어떻게 돌아가는지 예측하거나 시뮬레이션하려는 시도 없이, 오직 "지금 이 상황에서 어떻게 행동해야 보상을 최대화하는가"만 학습했다. 이번 챕터에서는 반대편, **모델 기반(model-based)** 방법을 살펴본다. 특히 두 참가자(플레이어)가 경쟁하는 **보드게임**이라는 특수한 무대에서, 이 접근이 얼마나 강력한지 확인한다.

이번 챕터의 목표:
- **AlphaGo Zero** 방법의 구조를 이해한다
- Connect 4(사목, 커넥트4) 게임으로 이 방법을 직접 구현해본다
- **MuZero**를 구현하고 AlphaGo Zero와 비교한다

---

## 1. 모델 기반 방법과 모델-프리 방법 비교

Chapter 4에서 RL 방법을 분류하는 세 가지 기준을 배웠다.

| 분류 기준 | 두 갈래 |
|---|---|
| 무엇을 학습하는가 | 가치 기반(value-based) vs 정책 기반(policy-based) |
| 데이터를 어떻게 쓰는가 | 온-폴리시(on-policy) vs 오프-폴리시(off-policy) |
| 환경을 예측하려 하는가 | **모델-프리(model-free) vs 모델 기반(model-based)** |

이 책에서 지금까지 다룬 방법은 전부 모델-프리였다. 여기서 "모델(model)"이란 **환경의 모형** — 즉 "지금 상태에서 어떤 행동을 하면 어떤 새로운 상태와 보상을 받는지"를 예측해주는 것을 뜻한다. 모델-프리 방법은 환경을 이해하거나 시뮬레이션하려는 노력을 전혀 하지 않고, 오직 최종 보상 기준으로 "좋은 행동(정책)"이나 "좋은 가치"만 직접 학습했다.

> [!note] 모델 기반이 더 나은 것은 아니다 — 그저 다른 상황에 맞는 도구
> 모델-프리가 최근 게임 AI 연구에서 인기 있는 이유는, 게임·시뮬레이터에서는 **샘플(경험)을 얻는 비용이 거의 공짜**이기 때문이다. 반면 로봇공학처럼 실제 하드웨어로 시행착오를 겪어야 하는 분야는 샘플 하나하나가 비싸고 느리므로, 예로부터 **모델 기반** 방법을 선호해왔다.

### 1.1 모델 기반 방법을 쓰는 두 가지 이유

- **① 샘플 효율성(sample efficiency)**: 정확한(또는 어느 정도 정확한) 환경 모델이 있으면, 실제 환경을 매번 건드리지 않고 **모델 안에서** 얼마든지 시행착오를 겪을 수 있다. 신발끈을 묶거나 길을 건널 때, 우리는 완벽하게 정밀한 물리 시뮬레이션 없이도 "대충 이렇게 될 것이다"라는 **머릿속 모델**로 미리 계획하고 예측한다 — 그 정도로도 충분히 쓸모 있다.
- **② 전이 가능성(transferability)**: 로봇 팔의 좋은 동역학 모델을 한 번 만들어두면, 그 모델을 **다양한 목표**(물건 집기, 조립하기 등)에 재사용할 수 있다. 반면 모델-프리 방법은 목표가 바뀌면 처음부터 다시 학습해야 하는 경우가 많다.

MuJoCo, PyBullet 같은 물리 시뮬레이터, 그리고 우리가 익히 다뤄온 Atari, CartPole 게임 자체도 사실 **현실 세계의 모델(모형)** 이다 — 실제 로봇이나 자동차 없이도 빠르고 값싸게 실행할 수 있는 근사물이다.

## 2. 보드게임을 위한 모델 기반 방법

Atari 같은 아케이드 게임은 한 명의 플레이어가 복잡한 환경과 상호작용하며 경험을 통해 실력을 늘려간다. 반면 **보드게임**은 사정이 다르다. **규칙 자체는 단순하고 명확**하지만, 게임을 복잡하게 만드는 것은 **가능한 판의 수가 어마어마하게 많다**는 점과, **전략을 알 수 없는 상대**가 나를 이기려 든다는 점이다.

보드게임에서는 게임 상태를 완전히 관측할 수 있고 규칙이 명확하기 때문에, **현재 판을 분석**하는 것이 가능해진다. 가능한 모든 수를 평가해보고 최선의 수를 고르는 방식이다. 이를 위해선 게임의 규칙을 담은 **모델**이 필요하다.

가장 단순한 평가 방법은, 가능한 행동들을 하나하나 시도해보고 그 결과 판을 재귀적으로 평가하는 것이다. 이 과정을 게임이 끝날 때까지 반복하고, 그 결과를 거슬러 전파하면 임의의 상황에서 각 수의 기대값을 추정할 수 있다.

> [!note] 미니맥스(minimax) — "내가 이기려 하고, 상대는 나를 막으려 한다"
> 이 방법의 한 변형이 **미니맥스**다. 나는 최선의 수(최댓값)를 찾으려 하고, 상대는 나에게 최악의 수(최솟값)를 강요하려 한다고 가정하고, 게임 트리를 오가며 **번갈아 최소·최대를 계산**해나가는 방식이다.

틱택토(경우의 수가 최종 상태 기준 138개뿐)처럼 작은 게임은 트리 전체를 다 훑어도 문제없다. 하지만 체커(오목·서양 장기의 일종)만 해도 게임 트리 노드가 $5\times 10^{20}$개에 달해, 아무리 좋은 컴퓨터도 브루트포스로는 감당이 안 된다. 체스나 바둑은 훨씬 더 크다. 그래서 보통은 **일정 깊이까지만 분석**하고, 가지치기(pruning)와 미리 정해둔 위치 평가 방법을 조합해 그럭저럭 잘 두는 프로그램을 만들어왔다.

---

## 3. AlphaGo Zero 방법

2017년 말, DeepMind는 저널 *Nature*에 *Mastering the game of Go without human knowledge*(Silver et al.)라는 논문을 발표했다. **AlphaGo Zero**라 불리는 이 방법은 오직 게임 규칙만 알려주고, **사람이 만든 기보나 손수 만든 특징, 사전 학습 모델 없이도** 초인적인 수준으로 바둑·체스를 두는 데 성공했다. 이 챕터에서는 이 방법을 Connect 4(사목) 게임에 직접 구현하며 이해해본다.

### 3.1 전체 개요 — 세 가지 구성 요소

AlphaGo Zero는 크게 세 부분으로 이루어진다.

1. **[[몬테카를로 트리 탐색 MCTS|몬테카를로 트리 탐색(MCTS)]]**: 게임 트리를 계속 순회하며 유망한 경로만 반씩 무작위로(semi-randomly) 걸어가면서 수의 빈도와 결과 통계를 모으는 알고리즘. 게임 트리가 워낙 크기 때문에 전체를 다 만들지 않고, **가장 유망한 경로만 무작위로 샘플링**한다(그래서 이름에 "몬테카를로"가 들어간다).
2. **현재 최고 모델(current best player)과 [[자기대국 Self-Play|자기대국(self-play)]]**: 이 최고 모델이 자기 자신과 대국하며 학습 데이터를 만든다. 초기엔 랜덤 초기 가중치라 네 살배기 아이처럼 아무렇게나 두지만, 시간이 지나며 점점 더 나은 버전으로 교체된다.
3. **견습생(apprentice) 모델의 학습**: 최고 모델의 자기대국 데이터를 보고 학습하는 모델. 주기적으로 이 모델과 현재 최고 모델이 대결하고, 견습생이 대다수 대국에서 이기면 **새로운 최고 모델**로 등극한다.

이렇게 단순하고(심지어 소박해 보이기까지 하는) 방법으로 AlphaGo Zero는 이전 모든 AlphaGo 버전을 꺾고 세계 최강 바둑 기사가 되었다. 이후 DeepMind는 이 방법을 체스·쇼기(일본 장기)에도 적용한 논문(*Mastering chess and shogi by self-play with a general reinforcement learning algorithm*)을 발표했는데, 여기서 학습된 모델은 당시 최강 체스 프로그램이었던 **Stockfish**(수십 년의 사람 전문가 노력으로 개발됨)를 이겼다.

### 3.2 MCTS 자세히 보기

틱택토의 부분 트리로 MCTS를 이해해보자.

![[fig_20_1.png]]
*그림 20.1 — 틱택토의 게임 트리. 첫 수는 9가지 선택지가 있고, 각 선택지가 다음 갈림길로 이어진다.*

게임이 처음 시작될 때 놓을 수 있는 칸은 9개이므로 루트 노드에서 9개의 가지가 뻗어 나간다. 어떤 상태에서 가능한 행동의 개수를 **분기 계수(branching factor)** 라 부르며, 이는 게임 트리가 얼마나 "무성한지"를 나타낸다. 틱택토는 첫 수에서 9, 다음 수에서 8, 이런 식으로 줄어들어 최대 $9! = 362880$개의 노드를 가진다.

체스는 첫 수부터 20가지, 바둑(19×19판)은 361가지나 되므로, 트리는 급격히 커진다. 이런 **조합 폭발(combinatorial explosion)** 을 감당하려면 무작위 샘플링이 필요하다. 일반적인 MCTS에서는 루트에서 시작해 게임이 끝날 때까지 무작위(또는 어떤 전략)로 여러 번 깊이 우선 탐색을 수행하고, 게임 결과에 따라 방문한 가지들의 가중치를 갱신한다.

AlphaGo Zero는 여기에 신경망을 결합한 변형 MCTS를 쓴다. 각 간선(어떤 상태 $s$에서 행동 $a$를 하는 것)마다 세 값을 저장한다: 사전 확률 $P(s,a)$, 방문 횟수 $N(s,a)$, 행동 가치 $Q(s,a)$. 다음 수는 효용값 $U(s,a) \propto Q(s,a) + \dfrac{P(s,a)}{1+N(s,a)}$ 이 가장 큰 쪽을 고른다. 이 공식이 어떻게 탐험과 활용을 동시에 노리는지는 [[UCB와 탐험 계수]]에 자세히 정리했다.

탐색이 게임 종료 상태에 닿거나, 아직 안 가본 리프 노드를 만나면 신경망을 호출해 $N=0, P=p_{net}, Q=0$으로 새 노드를 만든다. 이 신경망은 사전 확률뿐 아니라 **그 상황이 현재 플레이어 관점에서 얼마나 유리한지(가치)** 도 함께 반환한다. 값을 얻으면 지나온 경로를 거슬러 올라가며 통계를 갱신하는 **역전파(backup)** 를 수행하는데, 두 플레이어가 번갈아 두므로 **한 단계 올라갈 때마다 부호가 뒤집힌다.**

AlphaGo Zero는 이 탐색을 한 수를 두기 전에 **1,000~2,000회** 반복한 뒤, 방문 횟수 $N(s,a)$를 확률로 변환해 실제 둘 수를 정한다.

### 3.3 자기대국(Self-Play)

MCTS로 얻은 확률과 가치를 계산하는 신경망은 정책과 가치 두 개를 출력하는 구조([[액터-크리틱과 어드밴티지|액터-크리틱(A2C)]]의 두 헤드 구조와 유사)로, 입력으로는 (이전 몇 수를 포함한) 현재 게임 판을, 출력으로는 다음 두 값을 낸다.

- **정책 헤드(policy head)**: 각 행동에 대한 확률 분포.
- **가치 헤드(value head)**: 현재 플레이어 관점에서 이 게임의 결과를 예측한 값. 바둑은 수가 결정적(deterministic)이라 이 값에 할인율을 적용하지 않지만, 주사위를 굴리는 백개먼처럼 확률적 요소가 있는 게임이라면 할인을 적용해야 한다.

[[자기대국 Self-Play]]에서 자세히 다루듯, 매 수마다 MCTS를 여러 번 수행해 통계를 모은 뒤 행동을 고른다. 초반 수는 다양한 학습 데이터 확보를 위해 확률적으로, 일정 단계 이후엔 방문 횟수가 가장 큰 수를 그대로 고르는 결정적 방식으로 전환한다. 평가 대국(견습생 vs 최고 모델)에서는 처음부터 항상 결정적으로 둔다.

대국이 끝나면 매 스텝이 $(s_t, \pi_t, r_t)$ — 게임 상태, MCTS가 계산한 행동 확률, 그 판의 최종 결과 — 형태로 학습 데이터셋에 쌓인다.

### 3.4 학습과 평가

자기대국으로 쌓인 데이터(상태, 행동 확률, 결과값)에서 미니배치를 뽑아, **가치 헤드의 예측과 실제 결과 사이의 평균 제곱 오차(MSE)**, 그리고 **예측 확률과 MCTS 샘플링 확률 사이의 교차 엔트로피 손실**을 최소화하도록 학습한다. 일정 학습 스텝마다 현재 최고 모델과 학습 중인 모델이 여러 판을 겨루고, 학습 모델이 확연히 더 강해지면 최고 모델 자리를 넘겨받는 과정이 무한히 반복된다.

---

## 4. Connect 4로 AlphaGo Zero 구현하기

이제 실제로 Connect 4(사목, 6×7 격자에 디스크를 떨어뜨려 가로·세로·대각선 4개를 먼저 만드는 게임)로 이 방법을 구현해본다.

![[fig_20_2.png]]
*그림 20.2 — Connect 4의 두 판 예시. 왼쪽은 첫 번째 플레이어(빨강)가 방금 승리한 상황, 오른쪽은 두 번째 플레이어(파랑)가 그룹을 만들려는 상황.*

Connect 4는 규칙이 단순해 보여도 약 $4.5 \times 10^{12}$개의 서로 다른 게임 상태가 있어, 브루트포스로 풀기엔 여전히 벅차다. 예제는 다음 파일들로 구성된다.

- `Chapter20/lib/game.py`: 게임의 저수준 표현 — 수를 두고, 상태를 인코딩·디코딩하는 등의 유틸리티.
- `Chapter20/lib/mcts.py`: GPU 가속 리프 확장과 노드 백업을 지원하는 MCTS 구현.
- `Chapter20/lib/model.py`: 신경망과, 게임 상태 ↔ 모델 입력 변환, 한 게임 플레이 등 모델 관련 함수.
- `Chapter20/train.py`: 모든 요소를 엮어 새 최고 모델 체크포인트를 만들어내는 메인 학습 스크립트.
- `Chapter20/play.py`: 모델 체크포인트끼리 자동 토너먼트를 벌이는 도구.
- `Chapter20/telegram-bot.py`: 사람이 텔레그램에서 모델과 직접 대국할 수 있게 해주는 봇(사람에 의한 검증용).

### 4.1 게임 모델 (`lib/game.py`)

이 방법 전체의 전제는 **행동의 결과를 예측할 수 있어야 한다**는 것이다. 즉 "이 상태에서 이 행동을 하면 어떤 새 상태가 되는가"를 정확히 알아야 한다. 이는 Atari나 Gym 환경보다 훨씬 강한 요구사항이다 — Gym에서는 임의의 상태에서부터 다시 시작하도록 지정할 수 없기 때문이다.

Connect 4의 완전한 상태는 6×7 칸의 상태와 "누구 차례인가"로 표현된다. MCTS 도중 게임 상태를 **수백만~수십억 개** 저장해야 할 수 있으므로, **메모리 효율**이 매우 중요하다. 그래서 두 가지 표현을 함께 쓴다.

- **인코딩된 형태**: 전체 판을 단 63비트로 표현. 64비트 아키텍처의 워드 하나에 들어가 빠르고 가볍다.
- **디코딩된 형태**: 길이 7짜리 리스트(각 원소가 그 열의 디스크들을 담은 리스트). 메모리는 더 쓰지만 다루기 편하다.

```python
GAME_ROWS = 6
GAME_COLS = 7
BITS_IN_LEN = 3
PLAYER_BLACK = 1
PLAYER_WHITE = 0
COUNT_TO_WIN = 4
INITIAL_STATE = encode_lists([[]] * GAME_COLS)
```

- `GAME_ROWS`, `GAME_COLS`: 판의 크기. 코드 전체에서 이 값을 참조하므로, 값만 바꾸면 다른 크기의 게임도 실험해볼 수 있다.
- `BITS_IN_LEN`: 한 열에 쌓인 디스크 높이를 인코딩하는 데 쓰는 비트 수. 6×7 게임에선 열마다 최대 6개까지 쌓이므로, 0~7까지 표현 가능한 3비트면 충분하다.
- `PLAYER_BLACK`, `PLAYER_WHITE`: 디코딩된 표현에서 쓰는 플레이어 값.
- `COUNT_TO_WIN`: 이기기 위해 만들어야 할 연속 개수(사목이므로 4).
- `INITIAL_STATE`: 7개 열이 모두 빈 리스트인 초기 상태의 인코딩값.

주요 함수 목록:
- `encode_lists(state_lists)`: 디코딩 형태 → 인코딩(63비트 정수) 형태로 변환.
- `decode_binary(state_int)`: 정수 표현 → 리스트 형태로 되돌림.
- `possible_moves(state_int)`: 현재 상태에서 둘 수 있는 열의 인덱스 목록(0~6, 왼쪽부터).
- `move(state_int, col, player)`: 핵심 함수. 인코딩된 상태, 열 인덱스, 플레이어를 받아 (새 상태, 승리 여부)를 반환. 열 인덱스가 유효하지 않으면(가득 찬 열이면) 예외가 발생한다. 무승부는 `move()` 이후 `possible_moves()`가 빈 리스트인지 별도로 확인해야 한다.
- `render(state_int)`: 판 상태를 문자열 리스트로 반환(텔레그램 봇에서 사용).

### 4.2 MCTS 구현 (`lib/mcts.py`)

`MCTS` 클래스는 한 번에 여러 MCTS 배치를 수행하고 통계를 관리한다. 생성자는 노드 선택 시 쓰이는 상수 `c_puct` 하나만 받는다.

```python
class MCTS:
    def __init__(self, c_puct: float = 1.0):
        self.c_puct = c_puct
        # count of visits, state_int -> [N(s, a)]
        self.visit_count: tt.Dict[int, tt.List[int]] = {}
        # total value of the state's act, state_int -> [W(s, a)]
        self.value: tt.Dict[int, tt.List[float]] = {}
        # average value of actions, state_int -> [Q(s, a)]
        self.value_avg: tt.Dict[int, tt.List[float]] = {}
        # prior probability of actions, state_int -> [P(s,a)]
        self.probs: tt.Dict[int, tt.List[float]] = {}
```

네 개의 딕셔너리 모두 **키는 인코딩된 게임 상태(정수)**이고, 값은 각 열(행동)에 대한 통계 리스트다. 각 딕셔너리 위 주석은 논문의 기호($N,W,Q,P$)와 일치시켜 놨다.

`clear()`는 현재 최고 모델이 새 모델로 교체될 때, 이전에 쌓인 통계가 더는 유효하지 않으므로 초기화하는 메서드다.

```python
def clear(self):
    self.visit_count.clear()
    self.value.clear()
    self.value_avg.clear()
    self.probs.clear()
```

`find_leaf()`는 루트 상태에서 시작해 **아직 안 가본 리프 노드**를 만나거나 **게임이 끝날 때까지** 트리를 한 번 내려가는 메서드다. 지나온 상태와 취한 행동을 기록해두어야 나중에 통계를 갱신할 수 있다.

```python
def find_leaf(self, state_int: int, player: int):
    states = []
    actions = []
    cur_state = state_int
    cur_player = player
    value = None
```

리스트를 준비하는 부분이다. `states`, `actions`는 이번 탐색에서 지나온 상태·행동을 기록한다.

```python
    while not self.is_leaf(cur_state):
        states.append(cur_state)
        counts = self.visit_count[cur_state]
        total_sqrt = m.sqrt(sum(counts))
        probs = self.probs[cur_state]
        values_avg = self.value_avg[cur_state]
```

리프가 아닌 동안(이미 확장된 노드인 동안) 반복하며, 그 상태의 방문 횟수·확률·평균 가치 통계를 꺼낸다.

```python
        if cur_state == state_int:
            noises = np.random.dirichlet([0.03] * game.GAME_COLS)
            probs = [0.75 * prob + 0.25 * noise for prob, noise in zip(probs, noises)]
        score = [
            value + self.c_puct*prob*total_sqrt/(1+count)
            for value, prob, count in zip(values_avg, probs, counts)
        ]
```

**루트 노드일 때만** 디리클레 노이즈를 확률에 섞어 탐험을 늘린다([[UCB와 탐험 계수]] 참고). 그다음 각 행동의 점수(효용값)를 계산한다.

```python
        invalid_actions = set(range(game.GAME_COLS)) - \
            set(game.possible_moves(cur_state))
        for invalid in invalid_actions:
            score[invalid] = -np.inf
        action = int(np.argmax(score))
        actions.append(action)
```

이미 가득 찬 열처럼 **불가능한 행동은 점수를 $-\infty$로 만들어** 절대 선택되지 않게 막는다. 그런 다음 점수가 가장 큰 행동을 고른다.

```python
        cur_state, won = game.move(cur_state, action, cur_player)
        if won:
            value = -1.0
        cur_player = 1-cur_player
        # check for the draw
        moves_count = len(game.possible_moves(cur_state))
        if value is None and moves_count == 0:
            value = 0.0
    return value, cur_state, cur_player, states, actions
```

게임 엔진에 실제로 수를 두게 하고, 이겼다면 결과값을 -1(다음 플레이어 관점에서는 진 것이므로), 무승부면 0으로 설정한다. 최종 상태(승/패/무)는 절대 MCTS 통계에 추가되지 않으므로 항상 리프로 남는다.

`search_batch()`는 `search_minibatch()`를 여러 번 호출하는 진입점이다. 신경망 확장 연산이 병목이므로, **여러 리프를 한꺼번에 모아 신경망을 한 번에 실행**해 효율을 높인다. 대신 배치로 묶으면 순차 실행과 똑같은 결과가 나오지는 않는다는 단점이 있다 — 배치 안의 첫 탐색만 루트를 확장하고, 나머지는 그 확장 전의 트리 상태를 보게 되기 때문이다. 이를 보완하려면 미니배치를 **여러 번** 반복해서 수행한다.

```python
def is_leaf(self, state_int):
    return state_int not in self.probs

def search_batch(self, count, batch_size, state_int, player, net, device="cpu"):
    for _ in range(count):
        self.search_minibatch(batch_size, state_int, player, net, device)
```

`search_minibatch()`에서는 먼저 `find_leaf()`로 리프를 찾고, 게임이 끝난 경우(값이 `None`이 아님)엔 바로 백업 큐에 담고, 아니면 나중에 확장할 큐에 담는다.

```python
def search_minibatch(self, count, state_int, player, net, device="cpu"):
    backup_queue = []
    expand_states = []
    expand_players = []
    expand_queue = []
    planned = set()
    for _ in range(count):
        value, leaf_state, leaf_player, states, actions = \
            self.find_leaf(state_int, player)
        if value is not None:
            backup_queue.append((value, states, actions))
        else:
            if leaf_state not in planned:
                planned.add(leaf_state)
                leaf_state_lists = game.decode_binary(leaf_state)
                expand_states.append(leaf_state_lists)
                expand_players.append(leaf_player)
                expand_queue.append((leaf_state, states, actions))
```

`planned` 집합으로 **같은 리프를 중복해서 확장하지 않도록** 막는다. 확장이 필요한 상태들을 모아 신경망을 한 번에 호출한다.

```python
    if expand_queue:
        batch_v = model.state_lists_to_batch(expand_states, expand_players, device)
        logits_v, values_v = net(batch_v)
        probs_v = F.softmax(logits_v, dim=1)
        values = values_v.data.cpu().numpy()[:, 0]
        probs = probs_v.data.cpu().numpy()
```

네트워크가 반환한 로짓을 소프트맥스로 확률로 바꾸고, 값들을 NumPy 배열로 꺼낸다.

```python
    for (leaf_state, states, actions), value, prob in \
            zip(expand_queue, values, probs):
        self.visit_count[leaf_state] = [0]*game.GAME_COLS
        self.value[leaf_state] = [0.0]*game.GAME_COLS
        self.value_avg[leaf_state] = [0.0]*game.GAME_COLS
        self.probs[leaf_state] = prob
        backup_queue.append((value, states, actions))
```

새 노드를 만들 때는 방문 횟수·가치를 전부 0으로, 사전 확률은 신경망이 준 값으로 채운다.

```python
    for value, states, actions in backup_queue:
        cur_value = -value
        for state_int, action in zip(states[::-1], actions[::-1]):
            self.visit_count[state_int][action] += 1
            self.value[state_int][action] += cur_value
            self.value_avg[state_int][action] = self.value[state_int][action] / \
                self.visit_count[state_int][action]
            cur_value = -cur_value
```

핵심 백업(backup) 로직이다. 지나온 경로를 **거꾸로(`[::-1]`)** 순회하며 방문 횟수를 늘리고 누적 가치를 더한 뒤 평균을 갱신한다. 매 단계마다 `cur_value = -cur_value`로 **부호를 뒤집는데**, 두 플레이어가 번갈아 두므로 나에게 좋은 결과는 상대에겐 나쁜 결과이기 때문이다.

```python
def get_policy_value(self, state_int, tau=1):
    counts = self.visit_count[state_int]
    if tau == 0:
        probs = [0.0] * game.GAME_COLS
        probs[np.argmax(counts)] = 1.0
    else:
        counts = [count ** (1.0 / tau) for count in counts]
        total = sum(counts)
        probs = [count / total for count in counts]
    values = self.value_avg[state_int]
    return probs, values
```

방문 횟수를 실제 행동 확률로 바꾸는 마지막 함수다. $\tau$(온도)가 0이면 방문 횟수가 가장 큰 행동에 확률 1을 몰아주고(결정적), 그렇지 않으면 $N(s,a)^{1/\tau} / \sum_k N(s,k)^{1/\tau}$ 공식을 쓴다(자세한 설명은 [[UCB와 탐험 계수]] 참고).

### 4.3 모델 (`lib/model.py`)

신경망은 원래 AlphaGo Zero 논문보다 단순화한, **6개 층짜리 잔차(residual) 합성곱 네트워크**다. 입력은 6×7 크기의 채널 2개 — 첫 채널은 현재 플레이어의 디스크 위치, 둘째 채널은 상대의 디스크 위치를 담는다. 이렇게 **"내 디스크 vs 상대 디스크"** 로만 표현하면, 누가 선공이든 관계없이 항상 **현재 플레이어 관점**에서 판을 분석할 수 있다.

네트워크 몸통은 공통 잔차 합성곱 필터들로 이루어지고, 그 출력이 정책 헤드·가치 헤드(합성곱 층 + 완전연결 층 조합)로 전달된다. 정책 헤드는 각 열(디스크를 떨어뜨릴 위치)에 대한 로짓을, 가치 헤드는 스칼라 값 하나를 반환한다.

`state_lists_to_batch()`는 리스트 형태의 게임 상태 배치를 모델 입력 형태로 바꾸는 함수이고, 내부적으로 `_encode_list_state()`를 사용한다.

```python
def _encode_list_state(dest_np, state_list, who_move):
    assert dest_np.shape == OBS_SHAPE
    for col_idx, col in enumerate(state_list):
        for rev_row_idx, cell in enumerate(col):
            row_idx = game.GAME_ROWS - rev_row_idx - 1
            if cell == who_move:
                dest_np[0, row_idx, col_idx] = 1.0
            else:
                dest_np[1, row_idx, col_idx] = 1.0

def state_lists_to_batch(state_lists, who_moves_lists, device="cpu"):
    assert isinstance(state_lists, list)
    batch_size = len(state_lists)
    batch = np.zeros((batch_size,) + OBS_SHAPE, dtype=np.float32)
    for idx, (state, who_move) in enumerate(zip(state_lists, who_moves_lists)):
        _encode_list_state(batch[idx], state, who_move)
    return torch.tensor(batch).to(device)
```

각 열을 순회하며, 그 칸의 디스크가 `who_move`(현재 차례인 플레이어)의 것이면 채널 0에, 상대 것이면 채널 1에 1.0을 표시한다. 이렇게 만든 NumPy 배열을 텐서로 바꿔 반환한다.

`play_game()`은 두 신경망 사이의 대국을 시뮬레이션하고, 필요하면 리플레이 버퍼에 수를 저장하는 함수다.

```python
def play_game(mcts_stores: tt.Optional[mcts.MCTS | tt.List[mcts.MCTS]],
              replay_buffer: tt.Optional[collections.deque], net1: Net, net2: Net,
              steps_before_tau_0: int, mcts_searches: int, mcts_batch_size: int,
              net1_plays_first: tt.Optional[bool] = None,
              device: torch.device = torch.device("cpu")):
    if mcts_stores is None:
        mcts_stores = [mcts.MCTS(), mcts.MCTS()]
    elif isinstance(mcts_stores, mcts.MCTS):
        mcts_stores = [mcts_stores, mcts_stores]
```

`mcts_stores`는 단일 인스턴스, 두 개짜리 리스트, 또는 `None`일 수 있어 다양한 쓰임새에 유연하게 대응한다. 그 외 인자로는 리플레이 버퍼, 사용할 두 신경망, $\tau$가 0으로 바뀌기까지 걸리는 스텝 수, MCTS 탐색 횟수·배치 크기, 누가 선공인지 등을 받는다.

```python
    state = game.INITIAL_STATE
    nets = [net1, net2]
    if net1_plays_first is None:
        cur_player = np.random.choice(2)
    else:
        cur_player = 0 if net1_plays_first else 1
    step = 0
    tau = 1 if steps_before_tau_0 > 0 else 0
    game_history = []
```

선공 정보가 없으면 무작위로 정한다.

```python
    result = None
    net1_result = None
    while result is None:
        mcts_stores[cur_player].search_batch(
            mcts_searches, mcts_batch_size, state,
            cur_player, nets[cur_player], device=device)
        probs, _ = mcts_stores[cur_player].get_policy_value(state, tau=tau)
        game_history.append((state, cur_player, probs))
        action = np.random.choice(game.GAME_COLS, p=probs)
```

매 턴 MCTS로 통계를 모으고, 얻은 확률에서 행동을 샘플링한다.

```python
        if action not in game.possible_moves(state):
            print("Impossible action selected")
        state, won = game.move(state, action, cur_player)
        if won:
            result = 1
            net1_result = 1 if cur_player == 0 else -1
            break
        cur_player = 1-cur_player
        # check the draw case
        if len(game.possible_moves(state)) == 0:
            result = 0
            net1_result = 0
            break
        step += 1
        if step >= steps_before_tau_0:
            tau = 0
```

일정 스텝 수가 지나면 $\tau$를 0으로 낮춰 이후엔 결정적으로 최선의 수만 두게 한다.

```python
    if replay_buffer is not None:
        for state, cur_player, probs in reversed(game_history):
            replay_buffer.append((state, cur_player, probs, result))
            result = -result
    return net1_result, step
```

게임 기록을 **거꾸로** 순회하며 리플레이 버퍼에 저장하고, 매 스텝마다 결과의 부호를 뒤집는다 — 각 스텝은 "그 시점 플레이어" 관점에서의 결과여야 하기 때문이다.

### 4.4 학습 (Training)

`train.py`의 학습 루프는 지금까지 설명한 함수들을 순서대로 엮은 것이다. 현재 최고 모델이 계속 자기대국을 하며 리플레이 버퍼를 채우고, 다른 네트워크는 이 데이터로 학습한다 — MCTS 샘플링 확률과 정책 헤드 출력 사이의 교차 엔트로피, 그리고 가치 헤드 예측과 실제 게임 결과 사이의 MSE를 합쳐 손실로 삼는다. 일정 스텝마다 학습 중인 네트워크와 현재 최고 네트워크가 100판을 겨루고, 학습 네트워크가 60% 넘게 이기면 가중치를 동기화(즉 최고 모델 교체)한다. 이 과정이 무한히 반복되며, 점점 더 실력 있는 모델을 찾아나간다.

### 4.5 테스트와 비교

학습 도중 최고 모델이 교체될 때마다 가중치가 저장되므로, 다양한 강도의 여러 에이전트가 만들어진다. `play.py` 도구로 여러 모델 파일을 받아 모델들끼리 **모두-대-모두 토너먼트**를 벌여, 승수 기준 순위표를 만들 수 있다.

### 4.6 결과

저자는 학습을 빠르게 하기 위해 하이퍼파라미터를 일부러 작게 설정했다(자기대국 한 스텝당 MCTS 10회, 미니배치 크기 8). 덕분에 **1시간 학습, 2,500게임의 자기대국만으로도** 즐길 만한 수준의 모델이 나왔다(물론 아이 수준보다도 한참 아래였지만, 두 수에 한 번꼴로만 실수하는 수준의 진전은 보였다).

학습률 0.1과 0.001, 두 값으로 각각 10시간·40,000게임씩 실험했다.

![[fig_20_3.png]]
*그림 20.3 — 두 학습률(왼쪽 0.1, 오른쪽 0.001)에 대한 학습 중 승률. 두 경우 모두 0.5 부근을 오가며, 때로는 0.8~0.9까지 튀기도 한다.*

승률이 0.5 부근을 맴도는 이유는, 학습 중인 모델과 최고 모델을 계속 비교하면서 최고 모델 자체가 계속 바뀌기 때문에 나타나는 자연스러운 현상이다.

![[fig_20_4.png]]
*그림 20.4 — 두 학습률(왼쪽 0.1, 오른쪽 0.001)에 대한 전체 손실. 뚜렷한 추세가 보이지 않는다.*

손실 그래프도 뚜렷한 추세 없이 오르내리는데, 이 역시 최고 정책이 계속 바뀌면서 학습 대상 모델이 계속 재학습되기 때문이다.

토너먼트 검증에서는 모든 모델 쌍마다 대국을 벌여야 하므로 시간이 오래 걸린다(예: `./play.py --cuda -r 10 saves/v2/best_* > semi-v2.txt`). 모델의 실력이 실제로 향상되는지 확인하기 위해 승률을 모델 인덱스에 따라 그렸다.

![[fig_20_5.png]]
*그림 20.5 — 학습이 진행됨(모델 인덱스 증가)에 따른 최고 모델들의 승률(왼쪽 0.1, 오른쪽 0.001). 두 경우 모두 실력이 향상되는 추세를 보이지만, 학습률이 작은 쪽(0.001)이 더 일관된 경향을 보인다.*

두 실험을 서로 겨루게 한 결과, **학습률 0.001로 학습한 모델들이 상당한 차이로 이겼다** — 학습률을 낮추는 것이 더 안정적인 학습으로 이어짐을 보여준다.

---

## 5. MuZero

AlphaGo Zero(2017년 발표)의 후속작인 **MuZero**는 DeepMind의 Schrittwieser 등이 2020년 논문 *Mastering Atari, Go, chess and shogi by planning with a learned model*에서 소개했다. 이 방법은 **정확한 게임 모델(규칙)이 있어야 한다는 요구사항을 없애면서도** 여전히 모델 기반 방법군에 속한다.

AlphaGo Zero에서는 MCTS 도중 게임 모델을 계속 사용했다 — 어떤 행동이 가능한지, 행동 후 새 상태가 무엇인지, 최종 승패가 무엇인지 전부 게임 엔진에 물어봤다. 언뜻 보면 이 모델 없이 학습 과정을 진행하는 게 불가능해 보이지만, MuZero는 그것을 실제로 해냈을 뿐 아니라 바둑·체스·쇼기에서 AlphaGo Zero의 기록을 넘어섰고, **57개 아타리 게임**에서도 최고 수준의 성능을 달성했다.

### 5.1 고수준 모델

MuZero의 핵심도 AlphaGo Zero와 마찬가지로 MCTS다 — 현재 트리 루트의 게임 상태에 대해 여러 번 탐색을 수행해 미래 결과에 대한 통계를 계산한다. 다른 점은, "이 행동을 하면 어떤 상태가 되는가?"라는 질문에 **게임 모델 대신 신경망**으로 답한다는 것이다. MuZero는 이를 위해 두 개의 추가 신경망을 도입한다.

1. **표현(representation) 네트워크** $h_\theta(o) \to s$: 게임 관측을 은닉 상태로 변환.
2. **동역학(dynamics) 네트워크** $g_\theta(s,a) \to r, s'$: 은닉 상태 $s$에 행동 $a$를 적용해 다음 은닉 상태 $s'$(그리고 즉시 보상 $r$)를 얻음.

AlphaGo Zero는 정책과 가치를 예측하는 네트워크 $f_\theta(s) \to \pi, v$ 하나만 썼지만, MuZero는 **세 개의 네트워크**를 동시에 학습한다. 세 네트워크가 어떻게 협력하는지, 그리고 "학습된 모델"이 무슨 의미인지는 [[MuZero의 학습된 환경 모델]]에 정리했다.

![[fig_20_6.png]]
*그림 20.6 — MuZero의 몬테카를로 트리 탐색. 표현 네트워크 $h_\theta$로 관측을 은닉 상태 $s_0$로 바꾸고, $f_\theta$로 정책·가치를 얻은 뒤, 동역학 네트워크 $g_\theta$로 다음 은닉 상태 $s_1$과 보상을 예측한다.*

현재 게임 관측 $o$에 대해 먼저 표현 네트워크 $h_\theta$로 은닉 상태 $s_0$를 계산한다. 이 은닉 상태로 $f_\theta$를 이용해 정책 $\pi_0$과 가치 $v_0$을 계산할 수 있다 — 어떤 행동을 취해야 할지($\pi_0$), 그 행동의 예상 결과가 무엇인지($v_0$)를 알려주는 값이다. 정책·가치를 방문 횟수 통계와 결합해 [[UCB와 탐험 계수|효용값]] $U(s,a)$를 계산하고, 가장 큰 효용값을 가진 행동을 골라 트리를 내려간다.

이 상태에서 이 행동을 처음 선택하는 것(즉 아직 확장되지 않은 노드)이라면, 신경망 $g_\theta(s_0, a) \to r_1, s_1$을 써서 즉시 보상 $r_1$과 다음 은닉 상태 $s_1$을 얻는다. 이 과정이 수백 번(원 논문에서는 800회) 반복되며 방문 횟수가 쌓이고, 노드가 확장될 때마다 $f_\theta$로 얻은 값이 트리 루트까지 전달된다. AlphaGo Zero 논문에서는 이를 "백업(backup)"이라 불렀지만, MuZero 논문에서는 "역전파(backpropagation)"라 부른다 — 의미는 같다: 확장된 노드의 값을 루트까지 (부호를 뒤집으며) 더해나가는 것.

### 5.2 학습 과정

MCTS는 트리 루트에 있는 단일 게임 상태에 대해 수행된다. 모든 탐색 라운드가 끝나면, 탐색 중 각 행동이 실행된 빈도를 바탕으로 루트 상태에서 행동을 고른다. 그 행동을 환경에서 실제로 실행해 다음 상태와 보상을 얻고, 다시 그 상태를 루트로 삼아 새로운 MCTS를 수행한다.

이 과정을 반복하면 에피소드가 만들어지고, 리플레이 버퍼에 저장해 학습에 쓴다. 학습 배치를 만들 때는 리플레이 버퍼에서 에피소드 하나를 뽑고, 그 안에서 무작위 위치를 골라 **고정된 스텝 수만큼(논문에서는 5스텝) 풀어서(unroll)** 진행한다. 언롤의 매 스텝마다 다음 데이터를 모은다.

- MCTS의 행동 빈도 → **정책 목표**(교차 엔트로피 손실로 학습)
- 에피소드 끝까지의 할인된 보상 합 → **가치 목표**(MSE 손실로 학습)
- 실제로 받은 즉시 보상 → 동역학 네트워크가 예측한 보상의 **목표값**(역시 MSE 손실)

또한 각 언롤 스텝에서 취한 행동을 기억해, 동역학 네트워크 $g_\theta(s,a)\to r,s'$의 입력으로 사용한다.

배치가 준비되면, 언롤된 에피소드 구간의 첫 관측에 **표현 네트워크**를 적용한다. 그다음 현재 은닉 상태에서 정책·가치를 계산하고 손실을 구한 뒤, **동역학 네트워크** 스텝을 밟아 다음 은닉 상태를 얻는 과정을 5번(언롤 길이만큼) 반복한다. 원 논문은 언롤된 스텝의 그래디언트를 0.5배로 스케일링했는데, 이 구현에서는 손실 자체에 이 상수를 곱해 같은 효과를 냈다.

### 5.3 Connect 4로 MuZero 구현하기

구현은 다음 모듈들로 구성된다.

- `lib/muzero.py`: MCTS 자료구조·함수, 신경망, 배치 생성 로직.
- `train-mu.py`: 자기대국으로 에피소드를 생성하고 학습하며, 주기적으로 학습 모델과 최고 모델을 비교하는 학습 루프(AlphaGo Zero와 동일한 방식).
- `play-mu.py`: 모델 리스트끼리 여러 대국을 벌여 순위를 매기는 스크립트.

### 5.4 하이퍼파라미터와 MCTS 트리 노드

대부분의 MuZero 하이퍼파라미터는 하나의 데이터클래스에 모아 관리한다.

```python
@dataclass
class MuZeroParams:
    actions_count: int = game.GAME_COLS
    max_moves: int = game.GAME_COLS * game.GAME_ROWS >> 2 + 1
    dirichlet_alpha: float = 0.3
    discount: float = 1.0
    unroll_steps: int = 5
    pb_c_base: int = 19652
    pb_c_init: float = 1.25
    dev: torch.device = torch.device("cpu")
```

`dirichlet_alpha`, `pb_c_base`, `pb_c_init`은 [[UCB와 탐험 계수]]에서 다룬 탐험 관련 파라미터이고, `unroll_steps`는 학습 시 몇 스텝을 풀어서 볼지, `discount`는 할인율이다.

AlphaGo Zero의 MCTS는 게임 상태를 정수 하나로 식별할 수 있어서 딕셔너리로 트리를 관리했다. 하지만 MuZero의 노드는 **신경망이 만든 부동소수점 벡터(은닉 상태)** 로 식별되기 때문에, 두 은닉 상태가 "같은 상태"인지 비교할 방법이 없다. 그래서 트리를 딕셔너리 대신 **노드가 자식 노드를 참조하는 "진짜" 트리 구조**로 저장한다(메모리 효율은 떨어지지만 어쩔 수 없는 선택이다).

```python
class MCTSNode:
    def __init__(self, prior: float, first_plays: bool):
        self.first_plays: bool = first_plays
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior
        self.children: tt.Dict[Action, MCTSNode] = {}
        # node is not expanded, so has no hidden state
        self.h = None
        # predicted reward
        self.r = 0.0
```

새 노드는 자식이 없고 은닉 상태(`h`)도 아직 계산되지 않은 상태로 생성된다.

```python
@property
def is_expanded(self) -> bool:
    return bool(self.children)

@property
def value(self) -> float:
    return 0 if not self.visit_count else self.value_sum / self.visit_count
```

자식이 하나라도 있으면 확장된 노드로 취급하고, 노드의 가치는 누적 가치 합을 방문 횟수로 나눈 평균이다.

```python
def select_child(self, params: MuZeroParams, min_max: MinMaxStats) -> \
        tt.Tuple[Action, "MCTSNode"]:
    max_ucb, best_action, best_node = None, None, None
    for action, node in self.children.items():
        ucb = ucb_value(params, self, node, min_max)
        if max_ucb is None or max_ucb < ucb:
            max_ucb = ucb
            best_action = action
            best_node = node
    return best_action, best_node
```

`select_child()`는 모든 자식 노드에 대해 UCB 값을 계산해 가장 큰 것을 고른다.

```python
def ucb_value(params: MuZeroParams, parent: MCTSNode, child: MCTSNode,
              min_max: MinMaxStats) -> float:
    pb_c = m.log((parent.visit_count + params.pb_c_base + 1) /
                 params.pb_c_base) + params.pb_c_init
    pb_c *= m.sqrt(parent.visit_count) / (child.visit_count + 1)
    prior_score = pb_c * child.prior
    value_score = 0.0
    if child.visit_count > 0:
        value_score = min_max.normalize(child.value + child.r)
    return prior_score + value_score
```

AlphaGo Zero의 UCB 공식과 비슷하지만, `pb_c`라는 계수가 부모 노드의 방문 횟수에 따라 서서히 커지도록 설계되어 있다(자세한 설명은 [[UCB와 탐험 계수]] 참고).

```python
def get_act_probs(self, t: float = 1) -> tt.List[float]:
    child_visits = sum(map(lambda n: n.visit_count, self.children.values()))
    p = np.array([(child.visit_count / child_visits) ** (1 / t)
                  for _, child in sorted(self.children.items())])
    p /= sum(p)
    return list(p)
```

`get_act_probs()`는 방문 횟수를 온도 계수 $t$에 따라 확률로 바꾼다. $t$가 0에 가까울수록 방문 횟수가 가장 큰 행동에 확률이 몰리고, $t$가 클수록 분포가 평평해진다.

```python
def select_action(self, t: float, params: MuZeroParams) -> Action:
    act_vals = list(sorted(self.children.keys()))
    if not act_vals:
        res = np.random.choice(params.actions_count)
    elif t < 0.0001:
        res, _ = max(self.children.items(), key=lambda p: p[1].visit_count)
    else:
        p = self.get_act_probs(t)
        res = int(np.random.choice(act_vals, p=p))
    return res
```

`select_action()`은 세 가지 경우를 처리한다: 자식이 아예 없으면 완전 무작위, 온도가 거의 0이면 방문 횟수가 가장 큰 행동을 그대로, 그 외에는 `get_act_probs()`로 얻은 확률에 따라 샘플링한다.

### 5.5 모델

세 신경망 각각의 구조를 살펴본다. 자세한 역할 설명은 [[MuZero의 학습된 환경 모델]]에 정리했다.

**표현 모델**은 입력(2×6×7, AlphaGo Zero와 같은 관측 형식)을 은닉 상태(`HIDDEN_STATE_SIZE=64` 차원 벡터)로 변환한다.

```python
class ReprModel(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...]):
        super(ReprModel, self).__init__()
        self.conv_in = nn.Sequential(
            nn.Conv2d(input_shape[0], NUM_FILTERS, kernel_size=3, padding=1),
            nn.BatchNorm2d(NUM_FILTERS),
            nn.LeakyReLU()
        )
        # layers with residual
        self.conv_1 = nn.Sequential(
            nn.Conv2d(NUM_FILTERS, NUM_FILTERS, kernel_size=3, padding=1),
            nn.BatchNorm2d(NUM_FILTERS),
            nn.LeakyReLU()
        )
        # ... conv_2 ~ conv_5, 구조 동일 ...
        self.conv_out = nn.Sequential(
            nn.Conv2d(NUM_FILTERS, 16, kernel_size=1),
            nn.BatchNorm2d(16),
            nn.LeakyReLU(),
            nn.Flatten()
        )
        body_shape = (NUM_FILTERS,) + input_shape[1:]
        size = self.conv_out(torch.zeros(1, *body_shape)).size()[-1]
        self.out = nn.Sequential(
            nn.Linear(size, 128),
            nn.ReLU(),
            nn.Linear(128, HIDDEN_STATE_SIZE),
        )
```

구조는 AlphaGo Zero 예제와 거의 같지만, 마지막에 정책·가치 대신 **은닉 상태 벡터**를 반환한다.

```python
def forward(self, x):
    v = self.conv_in(x)
    v = v + self.conv_1(v)
    v = v + self.conv_2(v)
    v = v + self.conv_3(v)
    v = v + self.conv_4(v)
    v = v + self.conv_5(v)
    c_out = self.conv_out(v)
    out = self.out(c_out)
    return out
```

**잔차 연결**(`v = v + self.conv_N(v)`)이 있어서, 층을 통과한 결과에 원래 입력을 그대로 더해준다 — 층이 깊어져도 학습이 잘 되도록 돕는 구조다.

**예측(prediction) 모델**은 은닉 상태를 받아 정책과 가치를 반환한다.

```python
class PredModel(nn.Module):
    def __init__(self, actions: int):
        super(PredModel, self).__init__()
        self.policy = nn.Sequential(
            nn.Linear(HIDDEN_STATE_SIZE, 128),
            nn.ReLU(),
            nn.Linear(128, actions),
        )
        self.value = nn.Sequential(
            nn.Linear(HIDDEN_STATE_SIZE, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x) -> tt.Tuple[torch.Tensor, torch.Tensor]:
        return self.policy(x), self.value(x).squeeze(1)
```

정책·가치 각각 2층짜리 완전연결 헤드로 이루어져 있다.

**동역학(dynamics) 모델**은 은닉 상태와 원-핫 인코딩된 행동을 받아 즉시 보상과 다음 은닉 상태를 반환한다.

```python
class DynamicsModel(nn.Module):
    def __init__(self, actions: int):
        super(DynamicsModel, self).__init__()
        self.reward = nn.Sequential(
            nn.Linear(HIDDEN_STATE_SIZE + actions, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )
        self.hidden = nn.Sequential(
            nn.Linear(HIDDEN_STATE_SIZE + actions, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, HIDDEN_STATE_SIZE),
        )

    def forward(self, h: torch.Tensor, a: torch.Tensor) -> \
            tt.Tuple[torch.Tensor, torch.Tensor]:
        x = torch.hstack((h, a))
        return self.reward(x).squeeze(1), self.hidden(x)
```

`torch.hstack((h, a))`로 은닉 상태와 행동(원-핫 벡터)을 이어붙인 뒤, 각각 보상 예측용·다음 은닉 상태 예측용 완전연결 층에 통과시킨다.

세 네트워크는 `MuZeroModels` 클래스로 함께 관리된다.

```python
class MuZeroModels:
    def __init__(self, input_shape: tt.Tuple[int, ...], actions: int):
        self.repr = ReprModel(input_shape)
        self.pred = PredModel(actions)
        self.dynamics = DynamicsModel(actions)

    def to(self, dev: torch.device):
        self.repr.to(dev)
        self.pred.to(dev)
        self.dynamics.to(dev)
```

`sync()`, `get_state_dict()`, `set_state_dict()` 메서드는 (AlphaGo Zero와 마찬가지로) 최고 모델을 복사하거나 저장·불러오는 데 쓰인다.

```python
def sync(self, src: "MuZeroModels"):
    self.repr.load_state_dict(src.repr.state_dict())
    self.pred.load_state_dict(src.pred.state_dict())
    self.dynamics.load_state_dict(src.dynamics.state_dict())

def get_state_dict(self) -> tt.Dict[str, dict]:
    return {
        "repr": self.repr.state_dict(),
        "pred": self.pred.state_dict(),
        "dynamics": self.dynamics.state_dict(),
    }

def set_state_dict(self, d: dict):
    self.repr.load_state_dict(d['repr'])
    self.pred.load_state_dict(d['pred'])
    self.dynamics.load_state_dict(d['dynamics'])
```

### 5.6 MCTS 탐색 구현

**루트 노드**를 만드는 `make_expanded_root()`와, **비-루트 노드**를 확장하는 `expand_node()`는 비슷한 일을 하지만 상황이 다르다: 루트는 부모가 없으므로 동역학 네트워크를 쓸 필요가 없고, 대신 표현 네트워크로 직접 은닉 상태를 얻는다.

```python
def make_expanded_root(player_idx: int, game_state_int: int, params: MuZeroParams,
                        models: MuZeroModels, min_max: MinMaxStats) -> MCTSNode:
    root = MCTSNode(1.0, player_idx == 0)
    state_list = game.decode_binary(game_state_int)
    state_t = state_lists_to_batch([state_list], [player_idx], device=params.dev)
    h_t = models.repr(state_t)
    root.h = h_t[0].cpu().numpy()
```

새 루트 노드를 만들고, 게임 상태를 리스트로 디코딩해 텐서로 바꾼 뒤 표현 네트워크로 은닉 상태를 얻는다.

```python
    p_t, v_t = models.pred(h_t)
    # logits to probs
    p_t.exp_()
    probs_t = p_t.squeeze(0) / p_t.sum()
    probs = probs_t.cpu().numpy()
    # add dirichlet noise
    noises = np.random.dirichlet([params.dirichlet_alpha] * params.actions_count)
    probs = probs * 0.75 + noises * 0.25
```

은닉 상태로 정책·가치를 얻고, 로짓을 확률로 바꾼 뒤 **루트에만** 디리클레 노이즈를 섞는다(AlphaGo Zero와 동일한 목적).

```python
    for a, prob in enumerate(probs):
        root.children[a] = MCTSNode(prob, not root.first_plays)
    v = v_t.cpu().item()
    backpropagate([root], v, root.first_plays, params, min_max)
    return root
```

각 행동마다 자식 노드를 만들고, 얻은 가치를 역전파한다. 루트만 있는 경로이므로 이 단계에서는 딱 한 스텝짜리 역전파다.

```python
def expand_node(parent: MCTSNode, node: MCTSNode, last_action: Action,
                 params: MuZeroParams, models: MuZeroModels) -> float:
    h_t = torch.as_tensor(parent.h, dtype=torch.float32, device=params.dev)
    h_t.unsqueeze_(0)
    p_t, v_t = models.pred(h_t)
    a_t = torch.zeros(params.actions_count, dtype=torch.float32, device=params.dev)
    a_t[last_action] = 1.0
    a_t.unsqueeze_(0)
    r_t, h_next_t = models.dynamics(h_t, a_t)
    node.h = h_next_t[0].cpu().numpy()
    node.r = float(r_t[0].cpu().item())
```

비-루트 노드는 부모의 은닉 상태와 취한 행동(원-핫)을 **동역학 네트워크**에 넣어 다음 은닉 상태와 예측 보상을 얻는다.

```python
    p_t.squeeze_(0)
    p_t.exp_()
    probs_t = p_t / p_t.sum()
    probs = probs_t.cpu().numpy()
    for a, prob in enumerate(probs):
        node.children[a] = MCTSNode(prob, not node.first_plays)
    return float(v_t.cpu().item())
```

나머지는 루트와 비슷하지만, **노이즈는 넣지 않는다**(탐색 초입 루트에서만 필요한 장치이기 때문).

```python
def backpropagate(search_path: tt.List[MCTSNode], value: float, first_plays: bool,
                   params: MuZeroParams, min_max: MinMaxStats):
    for node in reversed(search_path):
        node.value_sum += value if node.first_plays == first_plays else -value
        node.visit_count += 1
        value = node.r + params.discount * value
        min_max.update(value)
```

`backpropagate()`는 탐색 경로를 거슬러 올라가며 값을 더한다. 노드가 지금 역전파되는 결과를 낸 플레이어와 같은 편(`first_plays == first_plays`)이면 그대로, 다르면 부호를 뒤집어 더한다. `value = node.r + discount * value`로 **그 노드의 예측 보상까지 합산**해 다음 단계로 넘긴다. `MinMaxStats`는 트리 전체의 최솟값·최댓값을 추적해, 나중에 값을 0~1 범위로 정규화하는 데 쓰인다.

```python
@torch.no_grad()
def run_mcts(player_idx: int, root_state_int: int, params: MuZeroParams,
             models: MuZeroModels, min_max: MinMaxStats,
             search_rounds: int = 800) -> MCTSNode:
    root = make_expanded_root(player_idx, root_state_int, params, models, min_max)
    for _ in range(search_rounds):
        search_path = [root]
        parent_node = None
        last_action = 0
        node = root
        while node.is_expanded:
            action, new_node = node.select_child(params, min_max)
            last_action = action
            parent_node = node
            node = new_node
            search_path.append(new_node)
        value = expand_node(parent_node, node, last_action, params, models)
        backpropagate(search_path, value, node.first_plays, params, min_max)
    return root
```

루트를 만든 뒤, `search_rounds`(기본 800)번 반복하며 이미 확장된 노드는 `select_child()`로 계속 내려가다가, 확장되지 않은 노드를 만나면 확장하고 값을 역전파한다.

> [!warning] MuZero MCTS는 배치 처리가 어렵다
> AlphaGo Zero와 달리, 여기선 신경망을 배치로 묶어 처리할 수 없다. 왜냐하면 탐색 경로가 **노드의 값(방문할 때마다 갱신됨)에 결정적으로 의존**하기 때문에, 같은 노드를 확장하지 않은 채로 여러 번 탐색해봐야 항상 같은 경로만 나온다. 그래서 확장을 하나씩 순서대로 해야 하며, 이는 신경망 활용 측면에서 비효율적이다. 저자도 "가장 효율적인 구현이 아니라 동작하는 프로토타입을 보여주는 것이 목적"이라 밝혔고, 병렬 프로세스로 여러 MCTS를 동시에 돌리거나 배치화를 시도해보는 것을 독자 연습 문제로 남겨두었다.

### 5.7 학습 데이터와 게임 플레이

에피소드는 `EpisodeStep` 목록과 부가 정보를 가진 `Episode` 클래스로 저장한다.

```python
@dataclass
class EpisodeStep:
    state: int
    player_idx: int
    action: int
    reward: int

class Episode:
    def __init__(self):
        self.steps: tt.List[EpisodeStep] = []
        self.action_probs: tt.List[tt.List[float]] = []
        self.root_values: tt.List[float] = []

    def __len__(self):
        return len(self.steps)

    def add_step(self, step: EpisodeStep, node: MCTSNode):
        self.steps.append(step)
        self.action_probs.append(node.get_act_probs())
        self.root_values.append(node.value)
```

`play_game()`은 MCTS를 반복 호출해 한 게임 전체를 플레이한다.

```python
@torch.no_grad()
def play_game(
        player1: MuZeroModels, player2: MuZeroModels, params: MuZeroParams,
        temperature: float, init_state: tt.Optional[int] = None
) -> tt.Tuple[int, Episode]:
    episode = Episode()
    state = game.INITIAL_STATE if init_state is None else init_state
    players = [player1, player2]
    player_idx = 0
    reward = 0
    min_max = MinMaxStats()
```

게임 상태와 필요한 객체들을 초기화한다.

```python
    while True:
        possible_actions = game.possible_moves(state)
        if not possible_actions:
            break
        root_node = run_mcts(player_idx, state, params, players[player_idx], min_max)
        action = root_node.select_action(temperature, params)
        # act randomly on wrong move
        if action not in possible_actions:
            action = int(np.random.choice(possible_actions))
```

무승부(더 이상 둘 곳 없음)를 확인하고, MCTS로 통계를 모은 뒤 (UCB가 아니라) **온도 기반 확률**로 행동을 고른다.

```python
        new_state, won = game.move(state, action, player_idx)
        if won:
            if player_idx == 0:
                reward = 1
            else:
                reward = -1
        step = EpisodeStep(state, player_idx, action, reward)
        episode.add_step(step, root_node)
        if won:
            break
        player_idx = (player_idx + 1) % 2
        state = new_state
    return reward, episode
```

수를 두고 승패를 확인한 뒤, 다음 플레이어로 넘긴다.

`sample_batch()`는 리플레이 버퍼에서 학습 배치를 뽑는 함수다. 언롤 방식이라 배치가 하나의 텐서가 아니라 **언롤 스텝 수만큼의 텐서 리스트**로 이루어진다.

```python
def sample_batch(
        episode_buffer: tt.Deque[Episode], batch_size: int, params: MuZeroParams,
) -> tt.Tuple[
    torch.Tensor, tt.Tuple[torch.Tensor, ...], tt.Tuple[torch.Tensor, ...],
    tt.Tuple[torch.Tensor, ...], tt.Tuple[torch.Tensor, ...],
]:
    states = []
    player_indices = []
    actions = [[] for _ in range(params.unroll_steps)]
    policy_targets = [[] for _ in range(params.unroll_steps)]
    rewards = [[] for _ in range(params.unroll_steps)]
    values = [[] for _ in range(params.unroll_steps)]
```

언롤 스텝마다 별도의 리스트를 준비한다.

```python
    for episode in np.random.choice(episode_buffer, batch_size):
        assert isinstance(episode, Episode)
        ofs = np.random.choice(len(episode) - params.unroll_steps)
        state = game.decode_binary(episode.steps[ofs].state)
        states.append(state)
        player_indices.append(episode.steps[ofs].player_idx)
```

무작위 에피소드와 무작위 시작 위치(`ofs`)를 고른다.

```python
        for s in range(params.unroll_steps):
            full_ofs = ofs + s
            actions[s].append(episode.steps[full_ofs].action)
            rewards[s].append(episode.steps[full_ofs].reward)
            policy_targets[s].append(episode.action_probs[full_ofs])
            value = 0.0
            for step in reversed(episode.steps[full_ofs:]):
                value *= params.discount
                value += step.reward
            values[s].append(value)
```

각 언롤 스텝에서 행동, 즉시 보상, MCTS가 계산한 정책을 기록하고, 그 지점부터 에피소드 끝까지의 **할인된 보상 합**을 가치 목표로 계산한다.

```python
    states_t = state_lists_to_batch(states, player_indices, device=params.dev)
    res_actions = tuple(
        torch.as_tensor(np.eye(params.actions_count)[a],
                         dtype=torch.float32, device=params.dev)
        for a in actions
    )
    res_policies = tuple(
        torch.as_tensor(p, dtype=torch.float32, device=params.dev)
        for p in policy_targets
    )
    res_rewards = tuple(
        torch.as_tensor(r, dtype=torch.float32, device=params.dev)
        for r in rewards
    )
    res_values = tuple(
        torch.as_tensor(v, dtype=torch.float32, device=params.dev)
        for v in values
    )
    return states_t, res_actions, res_policies, res_rewards, res_values
```

`np.eye(actions_count)[a]`는 **[[원-핫 인코딩|원-핫 인코딩]]** 을 손쉽게 만드는 NumPy 트릭이다(단위 행렬에서 인덱스로 행을 뽑으면 그 인덱스만 1인 벡터가 나온다). 나머지 값들은 텐서로 변환해 반환한다.

학습 스텝 자체는 다음과 같다.

```python
states_t, actions, policy_tgt, rewards_tgt, values_tgt = \
    mu.sample_batch(replay_buffer, BATCH_SIZE, params)
optimizer.zero_grad()
h_t = net.repr(states_t)
loss_p_full_t = None
loss_v_full_t = None
loss_r_full_t = None
for step in range(params.unroll_steps):
    policy_t, values_t = net.pred(h_t)
    loss_p_t = F.cross_entropy(policy_t, policy_tgt[step])
    loss_v_t = F.mse_loss(values_t, values_tgt[step])
    # dynamic step
    rewards_t, h_t = net.dynamics(h_t, actions[step])
    loss_r_t = F.mse_loss(rewards_t, rewards_tgt[step])
    if step == 0:
        loss_p_full_t = loss_p_t
        loss_v_full_t = loss_v_t
        loss_r_full_t = loss_r_t
    else:
        loss_p_full_t += loss_p_t * 0.5
        loss_v_full_t += loss_v_t * 0.5
        loss_r_full_t += loss_r_t * 0.5
loss_full_t = loss_v_full_t + loss_p_full_t + loss_r_full_t
loss_full_t.backward()
optimizer.step()
```

**처음 한 번만** 표현 네트워크로 실제 관측을 은닉 상태로 바꾸고(`h_t = net.repr(states_t)`), 그 뒤로는 반복문 안에서 계속 **예측 네트워크(`net.pred`)로 정책·가치 손실**을 구하고, **동역학 네트워크(`net.dynamics`)로 다음 은닉 상태와 보상 손실**을 구한다. 첫 스텝(`step == 0`)의 손실은 그대로 쓰고, 이후 스텝들은 0.5를 곱해 더한다 — 원 논문의 그래디언트 스케일링(0.5배)을 손실에 직접 곱하는 방식으로 구현한 것이다.

### 5.8 MuZero 결과

15시간 학습, 3,400개 에피소드로 실험했다(학습 속도가 그리 빠르지 않음을 알 수 있다).

![[fig_20_7.png]]
*그림 20.7 — MuZero 학습의 정책 손실(왼쪽)과 가치 손실(오른쪽). 자기대국 학습에서 흔히 그렇듯 뚜렷한 추세가 보이지 않는다.*

학습 동안 거의 200개의 "현재 최고 모델"이 저장되었고, `play-mu.py`로 토너먼트를 진행해 상위 10개 모델을 확인했다. 흥미롭게도 **가장 좋은 모델들이 학습 초반에 저장된 모델**이었는데, 이는 (하이퍼파라미터를 많이 튜닝하지 않았다는 전제하에) 수렴이 그다지 좋지 않았다는 신호일 수 있다.

![[fig_20_8.png]]
*그림 20.8 — 학습 중 저장된 최고 모델들의 승률. 정책 손실과 상관관계가 큰데, 정책 손실이 낮을수록 더 나은 플레이로 이어지는 것이 당연하기 때문이다.*

### 5.9 MuZero와 아타리

이 예제에서는 Connect 4(두 플레이어 보드게임)를 다뤘지만, MuZero의 진짜 강점은 **은닉 상태를 쓴다는 일반화** 덕분에 더 전형적인 RL 시나리오에도 적용할 수 있다는 것이다. 실제로 원 논문에서는 이 방법을 **57개의 아타리 게임**에 성공적으로 적용했다. 물론 그런 시나리오에 맞게 튜닝과 조정이 필요하지만, 핵심 아이디어는 동일하다. 이는 독자에게 남겨진 연습 문제다.

---

## 6. 요약

이 챕터에서 우리는:
1. **모델-프리 vs 모델 기반** 방법의 차이와, 모델 기반 방법이 유리한 두 가지 이유(샘플 효율성, 전이 가능성)를 배웠다.
2. 보드게임이라는 특수한 무대에서, **미니맥스**나 브루트포스 트리 탐색이 왜 큰 게임에서는 통하지 않는지 확인했다.
3. **AlphaGo Zero**의 세 축 — [[몬테카를로 트리 탐색 MCTS|MCTS]], [[자기대국 Self-Play|자기대국]], 견습생 모델 학습 — 을 이해하고, Connect 4에서 직접 구현했다.
4. **MuZero**가 게임 규칙 자체를 표현·동역학·예측이라는 [[MuZero의 학습된 환경 모델|세 신경망]]으로 대체하는 방식과, 아타리 게임까지 적용 가능한 일반성을 대가로 더 무거운 학습 과정을 치른다는 점을 배웠다.

이 방법들은 바둑·체스 같은 게임 너머로, **단백질 접힘(protein folding), 금융, 에너지 관리** 등 실제 산업 문제에도 응용되고 있다. 다음 챕터에서는 실용적 RL의 또 다른 방향인 **이산 최적화 문제**(스케줄 최적화부터 단백질 접힘까지)를 다룬다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[몬테카를로 트리 탐색 MCTS]]
- [[자기대국 Self-Play]]
- [[UCB와 탐험 계수]]
- [[MuZero의 학습된 환경 모델]]
- [[액터-크리틱과 어드밴티지]]
- [[교차 엔트로피 Cross-Entropy]]
- [[손실함수의 종류]]
- [[데이터클래스 dataclass]]
- [[원-핫 인코딩]]

## 한눈에 보는 개념 지도
| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 사전 확률 | $P(s,a)$ | 신경망이 예측한 "이 수가 좋아 보인다"는 확률 |
| 방문 횟수 | $N(s,a)$ | 이 (상태,행동)을 몇 번 탐색했는가 |
| 행동 가치 | $Q(s,a)$ | 이 수를 뒀을 때 실제로 얻은 평균 결과 |
| 효용값 | $U(s,a)$ | 다음 수를 고를 때 쓰는 점수(활용+탐험) |
| 온도 | $\tau$ | 방문 횟수를 확률로 바꿀 때 뾰족함/평평함을 조절 |
| 표현 네트워크 | $h_\theta(o)\to s$ | 관측 → 은닉 상태 |
| 동역학 네트워크 | $g_\theta(s,a)\to r,s'$ | 은닉 상태+행동 → 보상, 다음 은닉 상태 |
| 예측 네트워크 | $f_\theta(s)\to \pi,v$ | 은닉 상태 → 정책, 가치 |
