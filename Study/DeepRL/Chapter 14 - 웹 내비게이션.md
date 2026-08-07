---
title: "Chapter 14 — 웹 내비게이션 (Web Navigation)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 14
tags: [DeepRL, 강화학습, 웹내비게이션, MiniWoB, 브라우저자동화, A3C, 모방학습]
---

# Chapter 14 · 웹 내비게이션

> [!abstract] 이 챕터를 한 문장으로
> **웹페이지도 하나의 "환경"이고, 마우스 클릭과 키보드 입력이 "행동"이라면, 강화학습 에이전트가 브라우저를 스스로 조작해서 과제를 풀게 만들 수 있다.** 이 챕터는 **MiniWoB(++)** 라는 브라우저 자동화 벤치마크를 소개하고, 화면 픽셀만 보고 클릭하는 A3C 에이전트를 만든 뒤, 텍스트 설명 추가와 사람 시연(demonstration)으로 성능을 끌어올리는 과정을 다룬다.

---

## 들어가며 — 왜 "웹 내비게이션"이 RL 문제일까?

지금까지 이 책에서는 Atari 게임, 체스, 주식 트레이딩처럼 "게임처럼 명확한 규칙이 있는" 환경을 다뤘다. 이번 챕터는 조금 다르다. 우리가 매일 쓰는 **인터넷 브라우저** 자체를 환경으로 삼는다.

여러분이 온라인으로 티켓을 예매하거나, 이메일을 보내거나, 위키백과에서 정보를 찾는 과정을 떠올려 보자. 이 모든 것은 **링크를 클릭하고, 글자를 입력하고, 버튼을 누르는 행동의 연속**이다. 만약 이 과정을 프로그램이 스스로 배워서 대신 해줄 수 있다면? 이것이 바로 **웹 내비게이션(web navigation)** 문제이고, 이를 자동화하는 것을 **브라우저 자동화([[DOM과 브라우저 자동화|browser automation]])** 라고 부른다.

> [!note] 이 챕터의 위치
> 이 챕터는 책의 **Part 3(정책 기반 방법들)를 마무리**하는 실전 응용 사례다. 6장(DQN·POMDP)과 12~13장(A3C, 텍스트 처리)에서 배운 지식들이 여기서 한꺼번에 합쳐진다.

---

## 1. 웹의 진화 — 왜 지금에서야 이런 시도가 가능해졌나

웹은 처음엔 아주 단순했다. 팀 버너스리가 만든 최초의 웹페이지(`http://info.cern.ch`)는 그냥 **글자와 링크**뿐이었다. 할 수 있는 행동이라곤 "읽기"와 "링크 클릭"뿐이다.

1995년, HTML 2.0 규격에 **폼(form)** 요소가 추가되면서 사용자가 텍스트를 입력하고, 체크박스를 토글하고, 드롭다운을 선택하고, 버튼을 누를 수 있게 되었다. 이때부터 웹페이지는 데스크톱 앱의 GUI(그래픽 사용자 인터페이스)와 비슷한 컨트롤들을 갖추기 시작했다. 차이는, 이 UI가 **로컬에 설치된 프로그램이 아니라 서버가 그때그때 보내주는 것**이라는 점이다.

지금(29년 후)은 JavaScript, HTML5 캔버스 덕분에 브라우저 안에서 MS오피스급 앱까지 돌아간다. 데스크톱 앱과 웹 앱의 경계가 거의 사라졌다. 하지만 여전히 이 모든 걸 이해하고 서버와 통신(HTTP)하는 것은 **브라우저**다.

> [!important] 웹 내비게이션의 정의
> **사용자가 하나 이상의 웹사이트와 상호작용하는 과정** — 링크 클릭, 텍스트 입력, 그 외 어떤 행동이든 목표(이메일 보내기, 특정 정보 찾기 등)를 이루기 위해 하는 모든 행동. 질문: **이걸 프로그램이 스스로 배우게 할 수 있을까?**

---

## 2. 브라우저 자동화와 RL의 연결고리

브라우저를 자동으로 조작하는 시도는 원래 RL과 무관하게 두 분야에서 오래전부터 있었다.

- **웹 테스트(website testing)**: 로그인 페이지를 새로 디자인했을 때 "비밀번호를 틀리면 오류가 뜨는가?", "비밀번호 찾기를 누르면 제대로 동작하는가?" 같은 시나리오를 매 배포마다 자동으로 확인해야 한다. 복잡한 웹사이트는 수백~수천 개의 케이스가 있어서 손으로 다 테스트할 수 없다.
- **웹 스크레이핑(web scraping)**: 예를 들어 동네 모든 피자집의 가격을 모으는 시스템을 만들려면 수백 개의 서로 다른 웹사이트를 다뤄야 한다. 단순 HTTP 요청+HTML 파싱부터, 사람처럼 마우스를 움직이고 클릭 지연까지 흉내 내는 완전한 에뮬레이션까지 다양한 도구가 있다.

**표준적인 브라우저 자동화 방식**은 진짜 브라우저(Chrome, Firefox)를 프로그램으로 제어하는 것이다. 프로그램은 [[DOM과 브라우저 자동화|DOM(Document Object Model)]] 트리와 화면상 요소의 위치 같은 **데이터를 관측**하고, 마우스 이동·클릭, 키 입력, 뒤로가기 버튼, JavaScript 실행 같은 **행동을 실행**한다.

> [!important] RL 문제로의 자연스러운 대응
> - **관측(observation)** = 웹페이지 상태(DOM, 픽셀)
> - **행동(action)** = 마우스·키보드 조작
> - **보상(reward)** = 애매하다! 과제마다 다르게 정의해야 한다(폼을 성공적으로 채웠는가, 원하는 정보 페이지에 도달했는가 등).

### 실전에서 쓸모 있는 시나리오들

1. **대규모 웹 테스트 자동화**: "마우스를 5픽셀 왼쪽으로 옮기고 클릭"처럼 저수준 명령을 일일이 정의하는 건 지루하다. 대신 몇 개의 **시범(demonstration)** 만 보여주고, 시스템이 스스로 일반화해서 비슷한 상황(버튼 위치가 조금 바뀌거나 문구가 달라져도)에 대응하게 만들고 싶다.
2. **보안 취약점 탐색**: 문제를 미리 정확히 정의하기 어려운 경우다. RL 에이전트는 사람보다 훨씬 빠르게 이상한 행동들을 대량으로 시도해볼 수 있다. 다만 행동 공간이 워낙 넓어서 무작정 무작위 클릭만으론 부족하고, 사람 전문가의 사전 지식과 결합하는 편이 효과적이다.
3. **대규모 웹 스크레이핑**: 호텔, 렌터카 등 수십만 개 웹사이트에서 정보를 뽑아내려면 보통 폼을 채워야 하는데, 사이트마다 디자인·구조·언어가 제각각이라 매우 번거롭다. RL 에이전트가 이런 반복 작업을 자동화하면 시간을 크게 절약할 수 있다.

### 왜 어려운가 — "숲을 보지 못하고 나무만 본다"

문제는, 이런 실전 응용은 **연구와 방법 비교에 쓰기엔 너무 크다.** 완전한 웹 스크레이핑 시스템 하나를 구현하려면 팀이 몇 달을 써야 하는데, 그 노력 대부분은 RL과 무관한 것들(데이터 수집, 브라우저 엔진과의 통신, 입출력 표현 방식 등)이다. 이 모든 것을 다 해결하다 보면 정작 **RL 알고리즘 자체를 비교하고 개선하는 본질**을 놓치기 쉽다.

그래서 연구자들은 MNIST, ImageNet, Atari 같은 **벤치마크 데이터셋**을 좋아한다. 좋은 벤치마크의 조건은 두 가지다.
- 빠르게 실험하고 여러 방법을 비교할 수 있을 만큼 **단순**해야 한다.
- 동시에 개선의 여지가 남아 있을 만큼 **충분히 도전적**이어야 한다.

(Atari가 좋은 예다 — Pong처럼 30분 만에 풀리는 쉬운 게임부터, Montezuma's Revenge처럼 최근에서야 겨우 풀린 복잡한 계획이 필요한 게임까지 폭넓게 있다.)

> [!note] 저자의 주장
> 저자가 아는 한, 브라우저 자동화 영역에서 이런 벤치마크는 **딱 하나**뿐이다 — 그리고 안타깝게도 RL 커뮤니티에서 거의 잊혀졌다. 이 챕터는 이 벤치마크를 다시 조명하려는 시도다.

---

## 3. MiniWoB 벤치마크

자세한 배경·역사는 [[MiniWoB 벤치마크와 웹 내비게이션]] 참고. 여기서는 핵심만 짚는다.

2016년 12월, OpenAI가 **MiniWoB(Mini World of Bits)**라는 데이터셋을 공개했다. **80개의 브라우저 기반 과제**로 구성되며, 픽셀 수준으로 관측하고(텍스트 설명도 함께 주어짐), 원래는 **VNC(Virtual Network Computing)** 클라이언트로 마우스·키보드 행동을 전달하도록 설계되었다.

![[fig_14_1.png]]
*그림 14.1 — MiniWoB 환경들의 예시. 버튼 클릭, 숫자 맞히기, 체크박스 선택, 날짜 선택, 검색 결과 클릭, 스크롤 목록 선택 등 다양한 과제가 있다.*

과제 난이도는 천차만별이다.
- 아주 쉬운 것: "대화상자의 닫기 버튼 클릭", "버튼 하나 누르기"
- 여러 단계가 필요한 것: "접힌 그룹을 펼치고 특정 텍스트의 링크 클릭", "매번 무작위로 생성되는 날짜를 날짜 선택기로 고르기"
- 사람에겐 쉽지만 기계엔 어려운 것: "이 텍스트가 있는 체크박스에 표시"(무작위 생성된 글자를 인식해야 함 — 문자 인식이 필요)

안타깝게도 MiniWoB는 공개 직후 OpenAI에 의해 거의 방치되었다. 몇 년 뒤 스탠퍼드 연구팀이 **MiniWoB++**라는 개선판을 내놓았다(게임 수 증가, 아키텍처 재설계).

### MiniWoB++: VNC 대신 Selenium

MiniWoB++는 VNC 대신 **[[DOM과 브라우저 자동화|Selenium]]**(브라우저 자동화의 사실상 표준 라이브러리)을 사용해 성능과 안정성을 크게 높였다. 현재는 **Farama Foundation**(`https://miniwob.farama.org/`)이 관리하고 있으며, 이 챕터는 이 최신 버전을 사용한다.

### 설치

과거에는 VNC와 OpenAI Universe 때문에 설치가 매우 복잡해서, 책의 이전 판은 전용 Docker 이미지를 제공해야 했다. 지금은 훨씬 간단하다.
- `pip install miniwob==1.0`으로 MiniWoB++ 패키지 설치
- **ChromeDriver**(Chrome/Chromium과 통신하며 "테스트 모드"로 실행해주는 작은 바이너리)를 별도로 설치. 설치된 Chrome 버전과 ChromeDriver 버전이 **반드시 일치**해야 한다(Chrome 메뉴의 "Chrome 정보"에서 버전 확인).

> [!tip] 확인 방법
> Mac/Linux에서는 `which chromedriver` 명령으로 설치된 chromedriver의 경로를 확인할 수 있다. 아무것도 안 나오면 PATH 환경변수에 등록이 안 된 것이다.

설치 확인은 `Chapter14/adhoc/01_wob_create.py`로 할 수 있다. 정상이면 2초간 브라우저 창이 떴다 사라진다.

### 행동과 관측 (Actions and observations)

Atari는 6~7개의 이산 버튼, CartPole은 단 2개의 행동만 있었다. 반면 브라우저는 훨씬 유연하다.
- **키보드 전체**(모든 키의 눌림 상태 포함) — 동시에 10개 버튼을 누르는 것도 허용된다.
- **마우스**: 임의의 좌표로 이동, 버튼 상태 제어, 더블클릭, 휠 스크롤까지 지원.

관측 공간도 훨씬 풍부하다. 전체 관측은 딕셔너리(dict) 형태이며 다음을 포함한다.
- **텍스트 설명**(utterance): 예) `Click button ONE` 또는 `You are playing as X in TicTacToe, win the game`
- **화면 픽셀** (RGB 값)
- **[[DOM과 브라우저 자동화|DOM]] 요소 목록**(위치, 색상, 글꼴 등 속성 포함)

이 외에도 브라우저에 직접 접근해서 CSS 속성이나 원본 HTML 같은 추가 정보도 얻을 수 있다. 이렇게 다양한 정보를 조합할 수 있다는 것은, 픽셀 기반 시각 처리에 집중할 수도 있고, DOM 정보로 특정 요소를 바로 클릭할 수도 있고, 텍스트 설명을 이해하는 NLP 컴포넌트를 쓸 수도 있다는 뜻이다 — 실험할 여지가 아주 많다.

### 간단한 예제 코드로 살펴보기

`Chapter14/adhoc/01_wob_create.py` 코드를 한 줄씩 뜯어보자.

```python
import time
import gymnasium as gym
import miniwob
from miniwob.action import ActionTypes

RENDER_ENV = True

if __name__ == "__main__":
    gym.register_envs(miniwob)
```
`gym.register_envs(miniwob)`는 사실 **아무 일도 하지 않는다.** `miniwob` 모듈을 import하는 순간 이미 모든 환경이 등록되기 때문이다. 하지만 최신 IDE(코드 편집기)는 "이 모듈을 import했는데 안 쓰네?"라고 경고를 띄우므로, 이 호출은 **"이 모듈을 실제로 쓰고 있다"는 걸 IDE에게 알려주는 용도**일 뿐이다.

```python
env = gym.make('miniwob/click-test-2-v1',
                render_mode='human' if RENDER_ENV else None)
print(env)
try:
    obs, info = env.reset()
    print("Obs keys:", list(obs.keys()))
    print("Info dict:", info)
    assert obs["utterance"] == "Click button ONE."
    assert obs["fields"] == (("target", "ONE"),)
    print("Screenshot shape:", obs['screenshot'].shape)
```
`click-test-2`라는, 화면에 무작위로 배치된 두 버튼 중 하나를 클릭하는 과제를 사용한다. `render_mode='human'`을 주면 실제 브라우저 창이 화면에 보인다.

![[fig_14_2.png]]
*그림 14.2 — click-test-2 환경. "ONE"과 "TWO" 두 버튼이 무작위 위치에 배치되고, 지시문에 지정된 버튼을 클릭해야 한다.*

이 코드를 실행하면 다음과 같은 출력을 얻는다.

```
Obs keys: ['utterance', 'dom_elements', 'screenshot', 'fields']
Info dict: {'done': False, 'env_reward': 0, 'raw_reward': 0, 'reason': None, 'root_dom':
[1] body @ (0, 0) classes=[] children=1}
Screenshot shape: (210, 160, 3)
```
관측에는 `utterance`(과제 설명), `dom_elements`, `screenshot`, `fields`(과제에 중요한 DOM 요소들)가 들어있다. 흥미로운 점은 **스크린샷 크기가 Atari 게임과 똑같은 (210, 160, 3)** 이라는 것 — 저자는 이게 우연이 아닐 거라고 말한다(같은 크기를 표준으로 삼았다는 뜻).

```python
    if RENDER_ENV:
        time.sleep(2)
    target_elems = [e for e in obs['dom_elements'] if e['text'] == "ONE"]
    assert target_elems
    print("Target elem:", target_elems[0])
```
`dom_elements` 목록에서 텍스트가 `"ONE"`인 요소를 찾는다. 이렇게 찾은 요소는 위치·크기·태그·색 등 풍부한 속성을 갖고 있다(`ref`, `left`, `top`, `width`, `height`, `tag`, `text`, `bg_color` 등).

```python
    action = env.unwrapped.create_action(
        ActionTypes.CLICK_ELEMENT, ref=target_elems[0]["ref"])
    obs, reward, terminated, truncated, info = env.step(action)
    print(reward, terminated, info)
finally:
    env.close()
```
찾은 요소의 `ref`(정수 식별자)를 이용해 **CLICK_ELEMENT** 행동을 만들고 실행한다. 이는 특정 DOM 요소를 마우스로 클릭하는 것을 흉내 낸다. 결과로 다음과 같은 보상이 나온다.

```
0.7936 True {'done': True, 'env_reward': 0.7936, 'raw_reward': 1, 'reason': None,
'elapsed': 2.066638231277466}
```

> [!tip] 보상은 시간이 지날수록 깎인다
> `RENDER_ENV = False`(화면 렌더링을 끄고 headless 모드)로 하면 렌더링에 걸리는 시간이 없어지므로, 같은 정답 행동이라도 **보상이 더 높게(0.9918)** 나온다 — MiniWoB의 보상 설계 자체가 "빨리 해결할수록 좋은 점수"이기 때문이다.

---

## 4. 단순 클릭 접근법 (The simple clicking approach)

이제 실제로 A3C 에이전트를 만들어본다. 목표: **이미지(픽셀) 관측만 보고 어디를 클릭할지 결정**하는 것. 이 방식은 MiniWoB 전체 과제 중 일부만 풀 수 있지만, 문제를 이해하는 좋은 출발점이 된다.

### 격자 행동 (Grid actions)

앞서 봤듯 마우스 행동 공간은 사실상 무한하다 — 좌표를 어디든 정할 수 있고, 누른 채 드래그도 할 수 있다. 이 챕터에서는 문제를 크게 단순화해서, **활성 웹페이지 영역(210×160픽셀) 안의 고정된 격자점에서만 클릭**하도록 제한한다.

![[fig_14_3.png]]
*그림 14.3 — 격자 행동 공간. 위쪽 50픽셀은 "지시문 영역"(클릭 가능한 요소 없음)이고, 그 아래 160픽셀 영역을 10픽셀 간격 격자로 나눠 각 칸을 하나의 행동으로 취급한다.*

원조 MiniWoB에서는 OpenAI Universe가 이런 래퍼(wrapper)를 이미 제공했지만, MiniWoB++에는 없어서 저자가 `lib/wob.py`에 직접 구현했다. 핵심 코드를 뜯어보자.

```python
WIDTH = 160
HEIGHT = 210
X_OFS = 0
Y_OFS = 50
BIN_SIZE = 10
WOB_SHAPE = (3, HEIGHT, WIDTH)

class MiniWoBClickWrapper(gym.ObservationWrapper):
    FULL_OBS_KEY = "full_obs"

    def __init__(self, env: gym.Env, keep_text: bool = False,
                 keep_obs: bool = False, bin_size: int = BIN_SIZE):
        super(MiniWoBClickWrapper, self).__init__(env)
        self.bin_size = bin_size
        self.keep_text = keep_text
        self.keep_obs = keep_obs
        img_space = spaces.Box(low=0, high=255, shape=WOB_SHAPE, dtype=np.uint8)
        if keep_text:
            self.observation_space = spaces.Tuple(
                (img_space, spaces.Text(max_length=1024)))
        else:
            self.observation_space = img_space
        self.x_bins = WIDTH // bin_size
        count = self.x_bins * ((HEIGHT - Y_OFS) // bin_size)
        self.action_space = spaces.Discrete(count)
```
- `WOB_SHAPE = (3, 210, 160)`: 채널(RGB) × 높이 × 너비 텐서로 관측 공간을 정의한다.
- `Y_OFS = 50`: 위쪽 50픽셀(지시문 영역)은 클릭해봤자 의미가 없으니 격자에서 제외한다.
- `bin_size=10`이면 가로 16칸 × 세로 16칸 = **256개의 이산(discrete) 행동**이 생긴다(`spaces.Discrete(count)`).
- `keep_text=True`로 설정하면, 관측이 (이미지, 텍스트) **튜플**로 바뀐다. 이 기능은 뒤에서 텍스트를 함께 쓰는 모델을 만들 때 사용한다.

```python
    @classmethod
    def create(cls, env_name: str, bin_size: int = BIN_SIZE, keep_text: bool = False,
               keep_obs: bool = False, **kwargs) -> "MiniWoBClickWrapper":
        gym.register_envs(miniwob)
        x_bins = WIDTH // bin_size
        y_bins = (HEIGHT - Y_OFS) // bin_size
        act_cfg = ActionSpaceConfig(
            action_types=(ActionTypes.CLICK_COORDS, ), coord_bins=(x_bins, y_bins))
        env = gym.make(env_name, action_space_config=act_cfg, **kwargs)
        return MiniWoBClickWrapper(
            env, keep_text=keep_text, keep_obs=keep_obs, bin_size=bin_size)
```
`create()`는 환경을 만들 때 `ActionSpaceConfig`를 이용해 "클릭 좌표 행동만 쓰겠다, 그리고 좌표는 이 격자 크기로 나누겠다"고 MiniWoB 자체에 알려준다.

```python
    def _observation(self, observation: dict) -> np.ndarray | tt.Tuple[np.ndarray, str]:
        text = observation['utterance']
        scr = observation['screenshot']
        scr = np.transpose(scr, (2, 0, 1))
        if self.keep_text:
            return scr, text
        return scr
```
MiniWoB의 원본 스크린샷은 (높이, 너비, 채널) 순서인데, PyTorch 컨볼루션 레이어는 (채널, 높이, 너비) 순서를 기대한다. `np.transpose(scr, (2, 0, 1))`로 축 순서를 바꿔준다.

```python
    def step(self, action: int) -> tt.Tuple[...]:
        b_x, b_y = action_to_bins(action, self.bin_size)
        new_act = {
            "action_type": 0,
            "coords": np.array((b_x, b_y), dtype=np.int8),
        }
        obs, reward, is_done, is_tr, info = self.env.step(new_act)
        ...

def action_to_bins(action: int, bin_size: int = BIN_SIZE) -> tt.Tuple[int, int]:
    row_bins = WIDTH // bin_size
    b_y = action // row_bins
    b_x = action % row_bins
    return b_x, b_y
```
에이전트가 선택한 행동은 그냥 0~255 사이의 정수(격자 칸 번호)다. `action_to_bins()`는 이 번호를 (x칸, y칸) 좌표로 변환한다(정수 나눗셈 `//`으로 행, 나머지 `%`으로 열을 구하는 방식 — 마치 시계를 읽듯 전체 번호를 "몇 번째 줄, 몇 번째 칸"으로 풀어내는 것과 같다). 그다음 이를 MiniWoB의 `action_type=0`(설정한 `CLICK_COORDS` 행동)과 함께 딕셔너리로 감싸 환경에 전달한다.

> [!tip] 브루트포스로 래퍼 확인하기
> GitHub의 `adhoc/03_clicker.py`는 `click-dialog-v1` 과제에서 256개 격자 칸을 순서대로 전부 클릭해보는 무식한(brute force) 방법으로 래퍼가 잘 동작하는지 보여준다.

### RL 파트

관측·행동을 변환하고 나면 RL 부분은 오히려 단순하다. **A3C** 방법을 그대로 사용하며, 에이전트는 160×210 이미지를 보고 **256개 격자 칸 중 어디를 클릭할지에 대한 확률 분포(정책)** 를 출력하고, 동시에 정책 경사 추정의 기준선(baseline)으로 쓸 **상태 가치**도 함께 추정한다.

관련 모듈 구성:
- `lib/common.py`: `RewardTracker`, `unpack_batch` 등 챕터 전반에서 재사용되는 함수
- `lib/model.py`: 모델 정의
- `lib/wob.py`: MiniWoB 전용 코드(환경 래퍼 등)
- `wob_click_train.py`: 학습 스크립트
- `wob_click_play.py`: 학습된 모델을 불러와 실행하고 보상 통계를 기록하는 스크립트

### 모델과 학습 코드

```python
class Model(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int):
        super(Model, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 64, 5, stride=5),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=2),
            nn.ReLU(),
            nn.Flatten(),
        )
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.policy = nn.Linear(size, n_actions)
        self.value = nn.Linear(size, 1)

    def forward(self, x: torch.ByteTensor) -> tt.Tuple[torch.Tensor, torch.Tensor]:
        xx = x / 255.0
        conv_out = self.conv(xx)
        return self.policy(conv_out), self.value(conv_out)
```
- 합성곱(convolution) 레이어 2개로 이미지 특징을 뽑는다. 첫 레이어는 `stride=5`로 크게 건너뛰며 훑고, 두 번째는 `stride=2`로 더 세밀하게 훑는다.
- `x / 255.0`: 픽셀값(0~255)을 신경망이 다루기 좋은 0~1 범위로 정규화한다.
- `self.policy`, `self.value`: 같은 합성곱 특징을 공유하면서, 하나는 행동 확률(정책), 하나는 상태 가치를 각각 출력하는 **두 개의 선형(Linear) 헤드**다.

이 모델은 크게 정교하게 튜닝되지 않았다고 저자는 밝힌다 — 즉 여러분이 더 개선할 여지가 충분히 있는 부분이다.

학습 스크립트 `wob_click_train.py`는 12장의 A3C 학습 코드와 사실상 동일하다. `AsyncVectorEnv`로 **8개의 병렬 환경**(=8개의 Chrome 인스턴스를 백그라운드에서 실행)을 굴린다. 메모리가 넉넉하면 이 병렬 개수를 늘려 실험해볼 수 있다.

### 학습 결과

기본값으로는 `click-dialog-v1`(무작위 위치에 뜨는 대화상자를, 모서리의 × 버튼을 클릭해 닫는 과제)을 사용하며, **약 8분** 학습으로 평균 보상 0.9에 도달한다.

![[fig_14_4.png]]
*그림 14.4 — click-dialog 학습 시 평균 보상(왼쪽)과 에피소드당 스텝 수(오른쪽)의 변화*

이상적으로는 딱 1번 클릭(닫기 버튼)이면 끝나야 하지만, 실제로는 에이전트가 종료 전까지 **7~9프레임**을 본다. 이유는 두 가지다: 대화상자의 × 표시가 뜨는 데 약간의 지연이 있고, 컨테이너 안의 브라우저 자체가 클릭과 보상 사이에 시간 간격을 만든다.

학습된 정책은 `wob_click_play.py`로 확인할 수 있다.
```
$ ./wob_click_play.py -m saves/best_0.923_45400.dat --verbose
0 0.0 False {...}
1 0.9788 True {'done': True, 'env_reward': 0.9788, ...}
Round 0 done
Done 1 rounds, mean steps 2.00, mean reward 0.979
```
`--render` 옵션을 주면 에이전트가 실제로 행동하는 브라우저 창을 볼 수 있다.

---

## 5. 단순 클릭 방식의 한계 (Simple clicking limitations)

이 방식은 `click-dialog`처럼 상대적으로 단순한 과제만 풀 수 있다. 더 복잡한 과제는 대개 수렴하지 않는다. 이유를 하나씩 살펴보자.

### (1) 에이전트가 상태가 없다(stateless) → 마르코프 성질 위반, POMDP

우리 에이전트는 **이전에 무슨 행동을 했는지 전혀 기억하지 않고**, 지금 눈에 보이는 화면(관측)만으로 다음 행동을 결정한다. [[마르코프 성질과 마르코프 체인|마르코프 성질]]이 성립한다면 "현재 관측만 봐도 충분"하지만, MiniWoB의 일부 과제에서는 이 가정이 깨진다.

예를 들어 `click-button-sequence` 과제는 **먼저 버튼 ONE을, 그다음 버튼 TWO를** 클릭해야 한다.

![[fig_14_5.png]]
*그림 14.5 — 상태 없는 에이전트가 풀기 어려운 환경의 예. 두 버튼을 정해진 순서(ONE → TWO)로 클릭해야 하는데, 화면 이미지 한 장만 봐서는 "지금 몇 번째 클릭인지" 알 수 없다.*

설령 운 좋게 순서대로 클릭했더라도, 에이전트는 **화면 한 장만으로는 "다음에 어느 버튼을 눌러야 하는지" 구분할 수 없다** — 두 버튼을 누르기 전과 하나만 누른 후의 화면이 겉보기엔 거의 같기 때문이다. 이런 문제를 **부분 관측 마르코프 결정 과정(POMDP, Partially Observable MDP)** 이라 부른다(6장에서 짧게 다룬 개념). 일반적인 해법은 에이전트가 **어떤 형태로든 상태(과거 정보)를 기억**하게 만드는 것이다. 어려운 점은, 관련 있는 정보만 최소한으로 남기고 불필요한 정보로 에이전트를 과부하시키지 않는 **균형**을 찾는 것이다.

### (2) 필요한 정보가 이미지에 없거나 다루기 불편한 형태다

`click-tab`과 `click-checkboxes` 과제를 보자.

![[fig_14_6.png]]
*그림 14.6 — 텍스트 설명이 중요한 환경의 예. 왼쪽(click-tab)은 매번 무작위로 선택된 탭을 클릭해야 하고, 오른쪽(click-checkboxes)은 무작위 텍스트가 적힌 체크박스들을 선택해야 한다.*

`click-tab`은 세 개의 탭 중 매번 무작위로 지정된 것을 클릭해야 하는데, "어느 탭인지"는 **텍스트 설명**(관측의 `utterance` 필드, 화면 상단에도 표시됨)으로만 주어진다. 우리 에이전트는 픽셀만 보므로, 화면 위쪽의 작은 글자와 정답 클릭 사이의 관계를 연결하기 어렵다. `click-checkboxes`는 더 심하다 — 무작위로 생성된 텍스트가 적힌 여러 체크박스를 선택해야 한다.

해결책 두 가지:
1. **OCR(광학 문자 인식, optical character recognition)** 네트워크로 이미지 속 글자를 텍스트로 변환한다.
2. (다음 절에서 다룰 방법) **텍스트 설명 자체를 모델 입력에 섞어 넣는다.**

### (3) 행동 공간의 차원이 너무 크다

클릭 한 번만 필요한 단순한 문제라도 행동 가짓수가 매우 많으면(우리 예에서는 256개), 에이전트가 정답을 우연히 찾아내기까지 오래 걸린다. 해결책 중 하나는 **사람의 시연(demonstration)을 학습에 포함**시키는 것이다.

예로 `count-sides` 과제를 보자.

![[fig_14_7.png]]
*그림 14.7 — count-sides 환경의 예. 화면에 그려진 도형의 변의 수를 세어, 그에 해당하는 숫자 버튼을 클릭해야 한다.*

목표는 그려진 도형의 **변의 개수에 해당하는 버튼을 클릭**하는 것이다. 저자의 실험에서는 시연 없이 하루를 학습해도 전혀 진전이 없었지만, 사람이 정답을 클릭하는 예시 20여 개를 추가하자 **단 15분 만에 문제를 풀었다.** 하이퍼파라미터를 더 튜닝하면 개선 여지가 있겠지만, 시연 하나만으로도 효과가 인상적이라는 것을 보여준다.

---

## 6. 텍스트 설명 추가하기 (Adding text description)

클리커 에이전트를 개선하는 첫걸음으로, 문제의 텍스트 설명을 모델에 함께 넣어보자. 앞서 봤듯 어떤 과제는 클릭해야 할 탭의 번호나 체크할 항목 목록처럼 **중요한 정보가 텍스트로만** 주어진다. 같은 정보가 이미지 상단에도 표시되긴 하지만, 픽셀이 항상 좋은 텍스트 표현 방식은 아니다.

모델의 입력을 "이미지만"에서 "이미지+텍스트"로 확장해야 한다. 13장에서 텍스트를 다뤄봤으니, [[LSTM과 패킹된 시퀀스|순환 신경망(RNN)]]을 쓰는 게 자연스러운 선택이다(이런 토이 문제에 최적은 아닐 수 있지만 유연하고 확장성이 있다).

### 구현

전체 코드는 `Chapter16/wob_click_mm_train.py`에 있다(챕터 번호 표기가 책 원문 그대로다). 기존 클리커 모델 대비 추가되는 부분은 많지 않다.

먼저 `MiniWoBClickWrapper`에 `keep_text=True`를 전달해서, 관측이 (이미지, 텍스트) **튜플**로 나오게 한다.

### 전처리기(Preprocessor)

모델이 이런 튜플을 처리하려면, **에이전트가 행동을 고를 때**와 **학습 코드** 두 곳 모두를 손봐야 한다. 이때 PTAN 라이브러리의 **전처리기(preprocessor)** 기능을 활용한다. 전처리기는 "관측 목록을 모델에 넣기 좋은 형태로 바꿔주는 함수"다. 기본 전처리기는 NumPy 배열 목록을 PyTorch 텐서로 바꾸고(필요하면 GPU로 옮기고) 끝이지만, 이번처럼 이미지는 텐서로, 텍스트는 별도 방식으로 처리해야 하는 경우엔 직접 정의해야 한다.

> [!note] 왜 모델 안에 안 넣고 별도 전처리기로 뺐나
> 이론적으로는 PyTorch의 유연함 덕분에 전처리 로직을 모델 내부에 넣을 수도 있다. 하지만 관측이 단순 NumPy 배열인 흔한 경우엔 **기본 전처리기가 알아서 처리**해 주므로, 이런 구조가 전체적으로 코드를 더 간단하게 만들어준다.

```python
MM_EMBEDDINGS_DIM = 50
MM_HIDDEN_SIZE = 128
MM_MAX_DICT_SIZE = 100
TOKEN_UNK = "#unk"

class MultimodalPreprocessor:
    log = logging.getLogger("MulitmodalPreprocessor")

    def __init__(self, max_dict_size: int = MM_MAX_DICT_SIZE,
                 device: torch.device = torch.device('cpu')):
        self.max_dict_size = max_dict_size
        self.token_to_id = {TOKEN_UNK: 0}
        self.next_id = 1
        self.tokenizer = TweetTokenizer(preserve_case=True)
        self.device = device

    def __len__(self):
        return len(self.token_to_id)
```
생성자에서 **토큰(단어) → 정수 ID** 매핑(사전이 아직 다 채워지지 않았으므로 동적으로 늘어남)을 만들고, `nltk` 패키지의 `TweetTokenizer`로 문장을 토큰 단위로 쪼갤 준비를 한다. `TOKEN_UNK`는 "모르는 단어(unknown)"를 위한 특수 토큰이다.

```python
def __call__(self, batch: tt.Tuple[tt.Any, ...] | tt.List[tt.Tuple[tt.Any, ...]]):
    tokens_batch = []
    if isinstance(batch, tuple):
        batch_iter = zip(*batch)
    else:
        batch_iter = batch
    for img_obs, txt_obs in batch_iter:
        tokens = self.tokenizer.tokenize(txt_obs)
        idx_obs = self.tokens_to_idx(tokens)
        tokens_batch.append((img_obs, idx_obs))
    tokens_batch.sort(key=lambda p: len(p[1]), reverse=True)
    img_batch, seq_batch = zip(*tokens_batch)
    lens = list(map(len, seq_batch))
```
목표는 (이미지, 텍스트) 튜플의 배치를 **① 이미지 텐서**(모양: 배치 크기 × 3 × 210 × 160)와 **② 토큰들을 담은 [[LSTM과 패킹된 시퀀스|패킹된 시퀀스(packed sequence)]]** 두 가지로 변환하는 것이다.

`VectorEnv`가 `gym.Tuple` 관측 공간을 다루는 방식 차이 때문에, 배치가 "(이미지 배치, 텍스트 배치) 튜플" 형태로 올 수도 있고, "(이미지, 텍스트) 개별 샘플들의 리스트" 형태로 올 수도 있다. 코드는 `batch`의 타입을 확인해서 이 차이를 흡수한다.

먼저 텍스트를 토큰화하고 각 토큰을 정수 ID로 바꾼다. 그다음 **토큰 길이가 긴 순서로 배치를 정렬**하는데, 이는 밑단의 cuDNN 라이브러리가 RNN을 효율적으로 처리하기 위해 요구하는 조건이다.

```python
img_v = torch.FloatTensor(np.asarray(img_batch)).to(self.device)
seq_arr = np.zeros(
    shape=(len(seq_batch), max(len(seq_batch[0]), 1)), dtype=np.int64)
for idx, seq in enumerate(seq_batch):
    seq_arr[idx, :len(seq)] = seq
    if len(seq) == 0:
        lens[idx] = 1
seq_v = torch.LongTensor(seq_arr).to(self.device)
seq_p = rnn_utils.pack_padded_sequence(seq_v, lens, batch_first=True)
return img_v, seq_p
```
이미지는 텐서로 바로 변환한다. 텍스트는 (배치 크기 × 최장 문장 길이) 크기의 0으로 채워진 행렬을 만들고, 각 문장의 실제 토큰들을 앞부터 채워 넣는다(뒤쪽 남는 자리가 자연스럽게 "패딩"이 된다). 빈 문장(길이 0)이면 최소 길이 1로 보정해준다. 마지막으로 `pack_padded_sequence`로 패킹해서 RNN에 효율적으로 넣을 수 있는 형태로 만든다.

```python
def tokens_to_idx(self, tokens):
    res = []
    for token in tokens:
        idx = self.token_to_id.get(token)
        if idx is None:
            if self.next_id == self.max_dict_size:
                self.log.warning("...")
                idx = 0
            else:
                idx = self.next_id
                self.next_id += 1
            self.token_to_id[token] = idx
        res.append(idx)
    return res
```
문제는 텍스트 설명에 어떤 단어가 나올지 **미리 알 수 없다**는 점이다. 한 글자씩(character-level) 처리하는 방법도 있지만, 그러면 시퀀스가 너무 길어진다. 여기서는 사전 크기를 100개로 고정해두고, 처음 보는 단어에는 새 ID를 동적으로 부여하는 방식을 쓴다. 사전이 꽉 차면 새 단어는 전부 `#unk`(0번)로 처리한다. 다만 이 방식은 무작위로 생성되는 문자열(예: `click-checkboxes`의 무작위 텍스트)이 섞인 문제에는 잘 안 맞을 수 있다 — 이런 경우엔 글자 단위 토큰화나 미리 정해둔 사전을 쓰는 대안이 있다.

### 모델

```python
class ModelMultimodal(nn.Module):
    def __init__(self, input_shape: tt.Tuple[int, ...], n_actions: int,
                 max_dict_size: int = MM_MAX_DICT_SIZE):
        super(ModelMultimodal, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_shape[0], 64, 5, stride=5),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=2),
            nn.ReLU(),
            nn.Flatten(),
        )
        size = self.conv(torch.zeros(1, *input_shape)).size()[-1]
        self.emb = nn.Embedding(max_dict_size, MM_EMBEDDINGS_DIM)
        self.rnn = nn.LSTM(MM_EMBEDDINGS_DIM, MM_HIDDEN_SIZE, batch_first=True)
        self.policy = nn.Linear(size + MM_HIDDEN_SIZE*2, n_actions)
        self.value = nn.Linear(size + MM_HIDDEN_SIZE*2, 1)
```
기존 클리커 모델과 다른 점은 **임베딩 레이어**(정수 토큰 ID → 밀집 벡터로 변환)와 **[[LSTM과 패킹된 시퀀스|LSTM]]** 이 추가된 것. `self.policy`, `self.value`의 입력 크기가 `size + MM_HIDDEN_SIZE*2`로 커진 것에 주목하자 — 이미지 특징(`size`)과 텍스트 특징(LSTM의 은닉 상태, `*2`인 이유는 LSTM의 은닉 상태가 hidden state와 cell state 두 가지로 구성되기 때문)을 이어붙이기(concatenate) 때문이다.

```python
def _concat_features(self, img_out, rnn_hidden):
    batch_size = img_out.size()[0]
    if isinstance(rnn_hidden, tuple):
        flat_h = list(map(lambda t: t.view(batch_size, -1), rnn_hidden))
        rnn_h = torch.cat(flat_h, dim=1)
    else:
        rnn_h = rnn_hidden.view(batch_size, -1)
    return torch.cat((img_out, rnn_h), dim=1)

def forward(self, x: tt.Tuple[torch.Tensor, rnn_utils.PackedSequence]):
    x_img, x_text = x
    emb_out = self.emb(x_text.data)
    emb_out_seq = rnn_utils.PackedSequence(emb_out, x_text.batch_sizes)
    rnn_out, rnn_h = self.rnn(emb_out_seq)
    xx = x_img / 255.0
    conv_out = self.conv(xx)
    feats = self._concat_features(conv_out, rnn_h)
    return self.policy(feats), self.value(feats)
```
이미지는 지금까지처럼 합성곱을 거치고, 텍스트는 임베딩 → LSTM을 거쳐 문맥이 압축된 은닉 상태가 된다. `_concat_features()`가 이 둘을 하나의 특징 벡터로 이어붙이면, 이 결합된 특징이 정책·가치 헤드로 들어간다. 즉 에이전트는 **"화면이 이렇게 생겼고, 지시문은 이런 내용이다"** 두 가지를 함께 고려해서 클릭 위치를 결정하게 된다.

학습 스크립트 `wob_click_mm_train.py`는 기존 `wob_click_train.py`를 거의 그대로 복사하되, 래퍼 생성 방식, 모델, 전처리기만 바꾼 것이다.

### 결과

`click-button` 환경(무작위로 놓인 여러 버튼 중 선택)에서 실험했다.

![[fig_14_8.png]]
*그림 14.8 — click-button 환경의 여러 상황. 똑같이 생긴 Submit 버튼이 여러 개 있는 경우도 있다(왼쪽 첫 번째).*

![[fig_14_9.png]]
*그림 14.9 — click-button 학습 시 평균 보상(왼쪽)과 에피소드당 스텝 수(오른쪽)*

3시간 학습 후 에이전트는 클릭하는 법을 배웠다(에피소드당 스텝 수가 5~7로 줄었다)는 것을 확인했지만, 평균 보상은 0.2에서 정체되었고 이후엔 개선이 없었다. 저자는 이것이 **하이퍼파라미터 튜닝이 더 필요하다는 신호**이거나, **환경 자체의 모호함** 때문일 수 있다고 본다 — 실제로 이 환경은 종종 같은 문구의 버튼(예: 그림 14.8 첫 상황의 두 개의 "Submit" 버튼)이 여러 개 있는데, 그중 하나만 정답이라 에이전트 입장에서 정답을 구별할 근거가 부족하다.

`click-tab` 환경(텍스트 설명이 중요한, 무작위로 지정된 탭을 클릭)에서도 실험했다.

![[fig_14_10.png]]
*그림 14.10 — click-tab 환경의 여러 상황*

이 환경에서는 학습이 성공적이지 못했다. 클릭 위치가 고정되어 있어 `click-button`보다 오히려 쉬워 보이는데도 실패한 것이 이상하다고 저자는 지적하며, 아마 하이퍼파라미터 튜닝이 필요할 것이라고 본다 — 여러분이 직접 도전해볼 만한 실험 과제로 남겨둔다.

---

## 7. 사람 시연 활용하기 (Human demonstrations)

자세한 이론적 배경은 [[모방학습과 행동 복제]] 참고. 여기서는 이 챕터의 구체적 구현을 다룬다.

학습 과정을 개선하기 위해 **사람의 시연(demonstration)** 을 활용해보자. 아이디어는 단순하다 — 에이전트가 스스로 최선의 방법을 찾도록 돕기 위해, "이렇게 하면 될 것 같다"는 예시 몇 개를 미리 보여주는 것이다. 완벽하거나 최적이 아니어도 괜찮다. 유망한 방향만 알려주면 된다.

사실 이는 사람이 배우는 방식과 똑같다 — 요리책의 레시피, 무용 수업의 시범처럼, 우리는 늘 다른 사람의 예시로부터 배운다. 이런 학습 방식은 순수한 무작위 탐색보다 훨씬 효율적이다(양치질을 순수 시행착오로 배운다고 생각해보라!). 물론 시범이 틀렸거나 최선이 아닐 위험은 있지만, 전체적으로는 무작위 탐색보다 훨씬 낫다.

### 왜 사람 데이터를 그냥 못 쓸까

지금까지의 학습 흐름은 이랬다.
1. 무작위 가중치로 시작 → 처음엔 무작위 행동.
2. 반복하다 보면 (Q값이나 정책의 advantage를 통해) 어떤 행동이 더 나은 결과를 주는지 발견 → 그 행동을 선호하기 시작.
3. 결국 거의 최적인 정책에 도달.

행동 공간이 작고 환경이 단순할 때는 이 방식이 잘 작동하지만, 행동 개수를 두 배로 늘리기만 해도 필요한 관측 수가 최소 두 배 이상 늘어난다. 우리의 클리커 에이전트는 행동이 256개(10×10 격자)로, CartPole(2개 행동)보다 **128배** 많다. 학습이 오래 걸리거나 아예 수렴하지 않는 것도 당연하다.

[[오프폴리시와 온폴리시|온폴리시(on-policy)]] 방법인 A3C는 "**현재 정책**에서 얻은 샘플"로만 정책 경사를 정확히 추정할 수 있다. 사람이 만든 (관측, 행동) 쌍은 사람의 정책에서 나온 것이지, 지금 학습 중인 신경망의 정책에서 나온 게 아니다. 따라서 사람 데이터를 그대로 정책 경사 계산에 밀어 넣으면, 추정된 경사가 엉뚱한 방향(사람 정책에 대한 경사)을 가리키게 된다.

해법은 지도학습 관점에서 문제를 다시 보는 것이다 — 사람 시연에 대해서는 [[모방학습과 행동 복제|로그우도(log-likelihood) 목적함수]]를 써서, 신경망이 시연 속 행동을 따라 하도록 밀어붙인다.

> [!important] 이건 지도학습으로의 대체가 아니다
> 우리는 RL을 지도학습으로 바꾸는 게 아니라, **지도학습 기법을 빌려와 RL 학습을 돕는 것**이다. 사실 이런 일은 이번이 처음도 아니다 — Q-러닝에서 가치 함수를 학습시키는 것 자체가 본질적으로 지도학습이다.

### 시연 녹화하기 (Recording the demonstrations)

MiniWoB++로 넘어오고 Selenium을 쓰기 전에는 시연을 녹화하는 것 자체가 기술적으로 까다로웠다 — VNC 프로토콜을 캡처하고 디코딩해서 브라우저 스크린샷과 사용자 행동을 뽑아내야 했기 때문이다.

지금은 VNC가 없고 브라우저가 로컬 프로세스로 직접 실행되므로(예전엔 Docker 컨테이너 안이었음) 훨씬 직접적으로 통신할 수 있다. Farama MiniWoB++는 `python -m miniwob.scripts.record` 명령으로 시연을 JSON 파일로 캡처하는 스크립트를 기본 제공한다(`https://miniwob.farama.org/content/demonstrations/`에 문서화되어 있다).

> [!warning] 공식 녹화 스크립트의 한계
> 공식 스크립트는 관측에서 **DOM 구조만** 기록하고 **픽셀 정보는 담지 않는다.** 이 챕터의 예제들은 픽셀을 많이 사용하므로, 이 스크립트로 녹화한 시연은 우리 목적에 쓸모가 없다. 그래서 저자는 픽셀까지 포함하는 자체 녹화 도구 `Chapter14/record_demo.py`를 만들었다.

```
$ ./record_demo.py -o demos/test -g tic-tac-toe-v1 -d 1
Bottle v0.12.25 server starting up (using WSGIRefServer())...
Listening on http://localhost:8032/
Hit Ctrl-C to quit.
...
Saved in demos/test/tic-tac-toe_0426101949.json
New episode starts in 1 seconds...
```
이 명령은 `render_mode='human'`으로 환경을 시작해 브라우저 창을 띄우고, 사람이 페이지와 상호작용하는 동안 백그라운드에서 관측(스크린샷 포함)을 기록한다. 에피소드가 끝나면 스크린샷과 행동을 짝지어 `-o` 옵션으로 지정한 디렉터리에 JSON 파일로 저장한다. `-g`로 환경을 바꿀 수 있고, `-d`는 에피소드 사이 대기 시간(초)이다(생략하면 Enter를 눌러 다음 에피소드를 시작해야 한다).

![[fig_14_11.png]]
*그림 14.11 — tic-tac-toe 과제에 대한 사람 시연을 녹화하는 과정*

저자는 `Chapter14/demos` 디렉터리에 실험에 사용한 시연들을 저장해두었지만, 직접 이 스크립트로 자신만의 시연을 녹화할 수도 있다.

### 시연으로 학습하기 (Training with demonstrations)

시연 데이터를 어떻게 얻는지 알았으니, 이제 **학습 과정을 어떻게 바꿔야 하는지**만 남았다. 가장 단순하면서도 의외로 잘 작동하는 방법은, 4장(교차 엔트로피 방법)에서 썼던 **로그우도 목적함수**를 쓰는 것이다. A3C 모델을 정책 헤드가 입력을 분류(classification)하는 문제로 바라본다. 가장 단순한 형태에서는 가치(value) 헤드는 그대로 두지만, 사실 이것도 어렵지 않게 학습시킬 수 있다 — 시연 중 얻은 보상을 알고 있으므로, 각 관측 시점부터 에피소드 끝까지의 할인된 보상을 계산하면 되기 때문이다.

관련 코드는 `Chapter16/wob_click_train.py`에 있다(원문 그대로). 명령줄에서 `--demo <DIR>` 옵션을 주면 시연 데이터를 불러오는 분기가 활성화된다.

```python
demo_samples = None
if args.demo:
    demo_samples = demos.load_demo_dir(args.demo, gamma=GAMMA, steps=REWARD_STEPS)
    print(f"Loaded {len(demo_samples)} demo samples")
```
`demos.load_demo_dir()`는 지정된 디렉터리의 JSON 파일들에서 시연 샘플을 자동으로 불러와 `ExperienceFirstLast` 인스턴스(PTAN 라이브러리가 쓰는 경험 표현 형태)로 변환한다.

학습 루프 안에서는, 일반 배치를 학습하기 전에 **확률 `DEMO_PROB`(기본 0.5)** 로 시연 배치 학습을 끼워 넣는다.

```python
if demo_samples and step_idx < DEMO_FRAMES:
    if random.random() < DEMO_PROB:
        random.shuffle(demo_samples)
        demo_batch = demo_samples[:BATCH_SIZE]
        model.train_demo(net, optimizer, demo_batch, writer,
                          step_idx, device=device)
```
로직은 단순하다 — `DEMO_PROB` 확률로 시연 데이터에서 `BATCH_SIZE`개를 뽑아 한 번 학습시킨다(단, 전체 스텝이 `DEMO_FRAMES`를 넘어가면 더는 시연 학습을 하지 않는다 — 초반에만 도움을 주고 이후엔 순수 A3C로 넘어가는 구조).

실제 학습은 `model.train_demo()` 함수가 담당한다.

```python
def train_demo(net: Model, optimizer: torch.optim.Optimizer,
                batch: tt.List[ptan.experience.ExperienceFirstLast], writer, step_idx: int,
                preprocessor=ptan.agent.default_states_preprocessor,
                device: torch.device = torch.device("cpu")):
    batch_obs, batch_act = [], []
    for e in batch:
        batch_obs.append(e.state)
        batch_act.append(e.action)
    batch_v = preprocessor(batch_obs)
    if torch.is_tensor(batch_v):
        batch_v = batch_v.to(device)
    optimizer.zero_grad()
    ref_actions_v = torch.LongTensor(batch_act).to(device)
    policy_v = net(batch_v)[0]
    loss_v = F.cross_entropy(policy_v, ref_actions_v)
    loss_v.backward()
    optimizer.step()
    writer.add_scalar("demo_loss", loss_v.item(), step_idx)
```
배치를 관측(`batch_obs`)과 행동(`batch_act`)으로 나누고, 관측을 전처리기로 텐서화한 뒤 GPU로 옮긴다. 그다음 신경망에서 정책(`policy_v`)만 꺼내서, 사람이 실제로 취한 행동(`ref_actions_v`, 정답 라벨 역할)과의 [[교차 엔트로피 Cross-Entropy|교차 엔트로피]] 손실을 계산하고 역전파한다. 즉, "이 화면에서는 사람이 이렇게 클릭했다"를 신경망이 흉내 내도록 밀어붙이는 것 — 값 헤드는 이 함수에서 건드리지 않는다.

### 결과

`count-sides` 문제에서 같은 하이퍼파라미터로 두 실험을 비교했다: 시연 없는 학습 vs `demos/count-sides` 디렉터리의 시연 25개를 사용한 학습.

차이는 극적이었다. 시연 없이 처음부터 학습한 경우, 12시간·400만 프레임을 학습해도 평균 보상은 -0.4에 머물렀고 유의미한 개선이 없었다. 반면 시연을 사용한 학습은 **단 3만 프레임(8분)** 만에 평균 보상 0.5에 도달했다.

![[fig_14_12.png]]
*그림 14.12 — count-sides 문제에서 시연을 사용한 학습의 평균 보상(왼쪽)과 에피소드당 스텝 수(오른쪽)*

더 어려운 과제로 **틱택토(tic-tac-toe)** 게임도 실험했다.

![[fig_14_13.png]]
*그림 14.13 — 녹화된 틱택토 시연 게임의 진행 과정. 점이 클릭 위치를 나타낸다.*

두 시간 학습 후 도달한 최고 평균 보상은 0.05였다 — 즉 에이전트가 일부 게임은 이길 수 있지만, 지거나 비기는 경우도 많다는 뜻이다.

![[fig_14_14.png]]
*그림 14.14 — tic-tac-toe 문제에서 시연을 사용한 학습의 보상 추이(왼쪽)와 에피소드당 스텝 수(오른쪽)*

---

## 8. 더 시도해볼 것들 (Things to try)

이 챕터는 전체 100여 개 이상의 MiniWoB++ 과제 중 가장 쉬운 몇 개만 다뤘을 뿐, 미개척 영역이 훨씬 많이 남아 있다. 저자가 제안하는 실험 아이디어:

- 시연이 **잡음 섞인 클릭(noisy clicks)** 에도 견고한지 테스트해보기.
- 클리커의 행동 공간을 개선하기 — 격자 칸을 고르는 대신 **클릭할 (x, y) 좌표 자체를 예측**하도록 바꿔보기.
- 화면 픽셀 대신(또는 픽셀과 함께) **DOM 데이터**를 사용해서, "트리의 어느 요소를 클릭할지"를 예측하도록 바꿔보기.
- 키보드 입력이 필요하거나 여러 단계의 행동 계획이 필요한 **다른 문제들**도 시도해보기.
- 최근 공개된 **LaVague** 프로젝트(`https://github.com/lavague-ai/LaVague`)는 LLM으로 웹 자동화를 하는데, LLM에게 특정 작업을 수행할 Selenium 파이썬 코드를 생성하도록 요청하는 방식이다. 이걸 MiniWoB++ 문제들에 대해 검증해보면 흥미로울 것이다.

---

## 요약

이 챕터에서 우리는 브라우저 자동화라는 RL의 실전 응용 사례를 살펴봤다.

1. **웹 내비게이션이 왜 RL 문제인지** — 웹페이지를 환경으로, 클릭·타이핑을 행동으로 보는 관점을 익혔다.
2. **[[MiniWoB 벤치마크와 웹 내비게이션|MiniWoB(++)]] 벤치마크**의 역사, 설치법, 관측(텍스트·픽셀·[[DOM과 브라우저 자동화|DOM]])·행동(키보드·마우스) 공간을 알아봤다.
3. **격자 클릭 A3C 에이전트**를 만들어, 행동 공간을 다루기 쉬운 이산 공간으로 단순화하는 방법을 배웠다.
4. 이 단순 접근의 세 가지 한계 — **상태 없음(POMDP)**, **텍스트 정보 부족**, **넓은 행동 공간** — 을 이해했다.
5. **[[LSTM과 패킹된 시퀀스|LSTM]] 기반 멀티모달 모델**로 텍스트 설명을 추가해 성능을 개선하려 시도했다.
6. **[[모방학습과 행동 복제|사람 시연]]** 을 로그우도(교차 엔트로피) 방식으로 학습에 섞어 넣어, 넓은 행동 공간 문제를 극적으로 개선하는 방법을 배웠다.

이 챕터는 책의 **Part 3(정책 기반 방법)를 마무리**한다. 다음 파트부터는 연속 행동 공간, 비경사(non-gradient) 방법 등 더 복잡하고 최신의 RL 방법들을 다룬다. 바로 다음 장은 이론적으로도 실전적으로도 중요한 하위분야인 **연속 제어(continuous control)** 문제를 살펴본다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[MiniWoB 벤치마크와 웹 내비게이션]]
- [[DOM과 브라우저 자동화]]
- [[LSTM과 패킹된 시퀀스]]
- [[모방학습과 행동 복제]]
- [[마르코프 성질과 마르코프 체인]] (POMDP 관련)
- [[오프폴리시와 온폴리시]]
- [[교차 엔트로피 Cross-Entropy]]
- [[PTAN 라이브러리 구조]]

## 한눈에 보는 개념 지도
| 개념 | 기호/코드 | 한 줄 뜻 |
|---|---|---|
| MiniWoB(++) | `gym.make('miniwob/...')` | 브라우저 조작을 훈련·비교하는 RL 벤치마크 |
| DOM | `obs['dom_elements']` | 웹페이지를 요소들의 트리로 표현한 구조 |
| 격자 행동 공간 | `MiniWoBClickWrapper` | 마우스 클릭을 유한한 격자 칸 선택으로 단순화 |
| POMDP | — | 현재 관측만으론 미래를 완전히 설명 못 하는 문제 |
| 멀티모달 모델 | `ModelMultimodal` | 이미지(CNN)+텍스트(LSTM) 특징을 함께 쓰는 모델 |
| 패킹된 시퀀스 | `pack_padded_sequence` | 길이가 다른 문장들을 효율적으로 배치 처리하는 형식 |
| 모방학습/행동 복제 | `train_demo()` | 사람 시연을 교차 엔트로피로 흉내 내며 학습 |
| DEMO_PROB | 기본 0.5 | 매 스텝마다 시연 학습을 끼워 넣을 확률 |
