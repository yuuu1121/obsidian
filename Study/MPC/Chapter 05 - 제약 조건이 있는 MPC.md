---
title: "Chapter 5 — 제약 조건이 있는 MPC (Constrained Model Predictive Control)"
book: "Model Predictive Control, 3rd Ed. (Camacho, Bordons, Maestre)"
chapter: 5
tags: [MPC, 모델예측제어, 제약조건, 이차계획법, KKT, 실현가능성]
---

# Chapter 5 · 제약 조건이 있는 MPC

> [!abstract] 이 챕터를 한 문장으로
> 실제 공정의 밸브는 100% 이상 열리지 않고 탱크는 넘치면 안 된다. 이 **제약(constraint)** 을 "계산한 다음 잘라내는(clipping)" 임시방편이 아니라 **최적화 문제 안에 명시적으로 집어넣는** 방법을 배우고, 그 결과 생기는 **이차계획법(QP)** 문제를 실제로 푸는 알고리즘들(활성 집합법·내점법·프라이멀-듀얼·피벗팅), 그리고 "풀 수 있는 해가 아예 없어지는" **실현불가능(infeasibility)** 상황을 관리하는 기술까지 다룬다.

---

## 들어가며 — 왜 이 챕터가 필요한가?

1장부터 4장까지 우리는 MPC의 뼈대를 세웠다. 모델로 미래를 예측하고, 비용함수를 최소화하는 미래 제어 시퀀스를 구하고, 그중 첫 항만 적용하고 다음 샘플에 다시 계산한다([[이동 구간 원리 Receding Horizon]]). 그런데 그 모든 계산에는 조용한 가정이 하나 깔려 있었다: **모든 신호가 무한한 범위를 가진다**는 가정이다.

현실은 그렇지 않다. 책의 첫 문단이 열거하는 것들을 보자.

- **액추에이터의 한계**: 제어 밸브는 완전히 닫힌 위치와 완전히 열린 위치 사이에서만 움직인다. 게다가 움직이는 **속도(slew rate)** 에도 한계가 있다. 한 샘플 사이에 0%에서 100%로 점프하는 밸브는 없다.
- **구조적·안전상의 이유**: 탱크의 수위, 배관의 유량, 용기의 압력에는 넘으면 안 되는 선이 있다.
- **센서의 측정 범위**: 센서가 읽을 수 있는 범위를 벗어나면 그 값은 의미가 없다.

여기에 더 중요한 사실이 하나 있다. **공장의 운전점(operating point)은 경제적 목표에 따라 정해지며, 그 최적 운전점은 대개 여러 제약이 교차하는 자리에 있다.** 즉 가장 돈이 되는 지점은 언제나 "아슬아슬한 곳"이다. 그래서 제어 시스템은 늘 한계 근처에서 돌아가고, 제약 위반이 일어날 가능성이 상시적으로 존재한다.

> [!important] 이 챕터의 핵심 주장
> 제어 시스템, 특히 **장구간 예측 제어(long-range predictive control)** 는 제약 위반을 **미리 내다보고(anticipate) 적절하게 교정해야 한다.** 이것이 MPC가 PID 같은 고전 제어보다 근본적으로 유리한 지점이며, 이 챕터 전체가 그 방법에 관한 이야기다.

비유를 하나 들자. **좁은 골목에서 후진으로 주차하는 상황**을 생각해 보자. 초보 운전자는 앞만 보고 핸들을 꺾다가 벽에 닿을 것 같으면 급하게 멈춘다(이것이 clipping이다). 숙련된 운전자는 **몇 수 앞을 미리 계산해서** "여기서 이만큼만 꺾어야 나중에 벽에 안 닿는다"고 판단한다. 이것이 제약을 명시적으로 고려한 MPC다. 결과는 확연히 다르다. 초보는 여러 번 앞뒤로 왔다 갔다 하지만, 숙련자는 한 번에 들어간다.

---

## 5.1 제약과 최적화 (Constraints and Optimization)

### MPC는 비싸다 — 그런데 왜 쓰는가?

책은 솔직하게 시작한다. 산업 현장에서 MPC를 구현하는 일은 **결코 사소하지 않으며**, PID 기반의 고전 제어 구조를 구축하는 것보다 확실히 더 어려운 작업이다. 구체적으로 어떤 부담이 있는가?

1. **모델을 먼저 구해야 한다.** 그러려면 상당한 수의 **플랜트 시험(plant test)** 이 필요하고, 대부분의 경우 이는 공장을 정상 운전 조건에서 벗어나게 만든다는 뜻이다. 즉 시험하는 동안 생산에 손해가 난다.
2. **장비 부담.** 경우에 따라 더 강력한 컴퓨터와 더 좋은 계측기가 필요하다.
3. **소프트웨어 비용.** 상용 MPC 패키지는 비싸다.
4. **인력 훈련.** 제어 담당자가 MPC를 시운전하고 운용할 수 있도록 적절한 교육을 받아야 한다.

이 모든 부담에도 불구하고 MPC는 **운전 비용을 줄이거나 생산량을 늘려서 경제적으로 이득이라는 것을 스스로 증명해 왔고**, 산업계에서 가장 성공한 고급 제어 기법 중 하나가 되었다. 그 이유는 응용마다 다르지만, 공통적으로 **비용함수를 최적화하는 능력**과 **제약을 다루는 능력**에서 나온다.

### MPC가 돈을 버는 네 가지 경로

책이 드는 이유는 다음 네 가지다.

| 경로 | 내용 |
|---|---|
| **운전 조건 최적화** | MPC의 비용함수는 운전 비용이나 경제적 의미가 있는 어떤 목표든 최소화하도록 설계할 수 있다 |
| **전이(transition) 최적화** | 한 운전점에서 다른 운전점으로 옮겨 가는 비용을 목적함수로 측정할 수 있어, 시동(startup)이나 시운전 시간을 단축한다 |
| **오차 분산 최소화** | 출력 오차의 **분산(variance)** 을 줄이도록 정식화할 수 있다 |
| **비상 정지 횟수 감소** | 제약을 명시적으로 고려하면 외란 때문에 비상 시스템이 작동해 공정이 멈추는 일을 줄인다 |

세 번째 항목이 가장 흥미롭고, 그림 5.1이 바로 그것을 설명한다.

![[mpc_fig_5_1.png]]
*그림 5.1 — 최적 운전점과 제약*

> [!example] 그림이 말하는 것
> 어떤 공정의 **생산량(유량 $Q$)** 은 **운전 압력**과 연결되어 있는데, 압력은 $p_{\max}$ 라는 상한을 넘을 수 없다. 압력이 높을수록 생산량이 많으므로, 이상적으로는 $p_{\max}$ 에 딱 붙여 운전하고 싶다. 하지만 제어가 흔들리면(분산이 크면) 설정점을 한계에서 멀찍이 떨어뜨려 놓아야 한다 — 그림의 운전점 $P_1$ 이 그 경우이고, 그만큼 생산량을 손해 본다. **제어 시스템이 분산을 줄일 수 있다면 설정점을 최적 운전점에 훨씬 가깝게 잡을 수 있다** — 그것이 운전점 $P_2$ 이고, 대응하는 유량이 더 크다. 분산 감소가 곧바로 생산량 증가로 환산되는 것이다. 덤으로 제품의 품질과 균일성도 좋아진다.

이 그림 하나가 "왜 제약을 제대로 다루는 것이 돈이 되는가"에 대한 산업적 대답이다. 네 번째 항목도 같은 논리다. 공정은 한계에서 운전할 수 없는데, 외란 때문에 제약을 위반하면 비상 시스템이 작동해 공정을 정지시켜 버리기 때문이다. 제약을 명시적으로 고려하면 이 문제를 완화할 수 있다.

---

## 5.2 제약 없는 MPC 정식화와 잘라내기 (Unconstrained MPC Formulations with Clipping)

### 지금까지의 계산을 복습하면

앞 장들에서 MPC의 제어 동작은 다음 이차 목적함수를 최소화하는 벡터 $\mathbf{u}$ 를 계산해서 얻었다.

$$J(\mathbf{u}) = \tfrac{1}{2}\,\mathbf{u}^\mathsf{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathsf{T}\mathbf{u} + \mathbf{f}_0 \tag{5.1}$$

각 기호의 뜻을 짚고 가자.

- $\mathbf{u}$ — **결정 변수(decision variable)** 벡터. 우리가 정해야 하는 미래의 제어 동작들을 한 줄로 쌓은 것이다. 책의 각주가 강조하듯, 정식화에 따라 이 벡터는 제어 신호의 **실제 값**일 수도 있고 **제어 증분(control increment) $\Delta u$** 일 수도 있다([[스텝 응답과 제어 증분]]).
- $\mathbf{H}$ — **헤시안(Hessian)** 행렬. 이차항의 계수 행렬이며, MPC에서는 대개 $\mathbf{G}^\mathsf{T}\mathbf{G} + \lambda I$ 꼴로 나온다. 양정치이면 문제가 볼록하다.
- $\mathbf{b}$ — 일차항의 계수 벡터. 자유 응답 $\mathbf{f}$ 와 기준 궤적 $\mathbf{r}$ 의 차이에서 나온다.
- $\mathbf{f}_0$ — $\mathbf{u}$ 와 무관한 상수항. 최소점의 **위치**에는 영향을 주지 않는다.

제약이 없으면 이 문제의 최적해는 **그래디언트를 0으로 놓아서** 얻는다. 즉 다음 선형 방정식을 풀면 끝이다.

$$\mathbf{H}\mathbf{u} = -\mathbf{b}$$

$\mathbf{H}$ 가 가역이면 $\mathbf{u}^* = -\mathbf{H}^{-1}\mathbf{b}$ 라는 **명시적 해**가 나온다. 행렬 곱 한 번이면 끝나는 아름다운 상황이고, 이것이 지금까지 우리가 살아온 세계다([[볼록 최적화와 이차계획법 QP]]).

### 현장의 임시방편 — 잘라내기(clipping)

실무에서 MPC를 쓰는 "정상적인" 방식은 이렇다.

1. 위의 방법으로 $u(t)$ 를 계산한다.
2. 계산된 $u(t)$ 가 제약을 위반하면, **제어 프로그램이나 액추에이터가 그 값을 한계로 포화(saturate)시킨다.**
3. $u(t+1), \ldots, u(t+N)$ 이 제약을 위반하는 경우는 **아예 고려조차 하지 않는다.** 대부분의 경우 그 신호들은 계산되지도 않기 때문이다.

이 방식의 문제는 무엇인가? 책은 두 가지를 지적한다.

**첫째, 최적성의 손실이 발생한다.** 조작 변수를 프로그램이나 액추에이터로 한계 안에 항상 붙들어 둘 수는 있다. 그러나 그렇게 얻은 값은 **"제약을 고려했을 때의 최적해"가 아니다.**

![[mpc_fig_5_2.png]]
*그림 5.2 — 제어 신호 $u(t)$ 와 $u(t+1)$ 에 대한 제약*

> [!example] 그림이 말하는 것
> 제어 지평이 2인 MPC 문제에서 제약 위반이 일어나는 두 경우를 등고선으로 보여준다. **(a)** 제약 없는 최적해 $u^*(t)$ 가 $u_{\max}$ 를 넘는 경우다. 통상적인 운전 방식은 $u_{\max}$ 를 공정에 적용하지만, **제약을 고려했을 때 $J$ 가 진짜 최소가 되는 지점은 $u_c$** 로 다른 곳에 있다. **(b)** 는 더 미묘하다. $u^*(t) \le u_{\max}$ 라서 $u(t)$ 자체는 제약을 위반하지 않고, 그래서 그대로 적용된다. 그러나 **뒤따르는 $u(t+1)$ 이 제약에 걸리는 상황을 미리 반영했다면** 지금 적용해야 할 값은 $u_c$ 여야 했다. 조작 변수의 제약을 **끝까지(to their full extent)** 고려하지 않으면 목적함수 값이 더 커지고 성능이 나빠진다.

**둘째, 출력 제약을 아예 다룰 수 없다.** 조작 변수를 잘라내는 것만으로는 출력(피제어 변수)의 제약 위반을 고려할 방법이 없다. 그런데 제어 변수의 한계를 위반하는 쪽이 훨씬 비싸고 위험할 수 있다.

> [!warning] 출력 제약 위반의 실제 대가
> 책이 드는 예를 그대로 보자. 대부분의 **회분식 반응기(batch reactor)** 에서는 생산 품질 때문에 어떤 변수들이 지정된 한계 안에 머물러야 한다. 이 한계를 위반하면 **불량품**이 나오고, 심하면 **한 배치 전체를 폐기**해야 한다. 안전상의 이유로 한계가 설정된 경우라면 위반의 결과는 **장비 손상, 유출, 또는 비상 시스템 작동에 따른 비상 정지**다. 정지는 생산 손실이나 지연을 낳고, 이후의 재시동 절차 역시 대개 비싸다.

게다가 이런 식으로 운전하면 **MPC의 가장 큰 장점인 예측 능력이 온전히 활용되지 못한다.** 미래를 내다보는 컨트롤러를 만들어 놓고 정작 미래의 제약은 안 보는 셈이기 때문이다.

---

## 5.3 MPC에서의 제약 (Constraints in MPC)

지금까지의 논의가 결론짓는 바는 분명하다. **제약을 컨트롤러의 정식화 안에 포함시키면** 성능이 좋아지고, 컨트롤러가 제약 위반을 미리 예상해 교정할 수 있다. 또한 컨트롤러와 시스템이 만들어 내는 신호들의 확률적 특성에도 영향을 준다.

여기서 중요한 관찰이 하나 있다. 입력·출력·상태 제약은 **의미하는 바는 서로 다르지만, 예측 컨트롤러의 정식화 안에서는 기본적으로 같은 방식으로 처리된다.** 모두 결국 $\mathbf{u}$ 에 대한 선형 부등식으로 환원되기 때문이다. 이제 하나씩 보자.

### 5.3.1 입력 제약 (Input Constraints)

공정 입력에 작용하는 제약은 두 종류에서 나온다.

- **진폭 한계(amplitude limits)**: 제어 신호 자체의 범위. $(\underline{U}, \overline{U})$ 로 쓴다.
- **변화율 한계(slew rate limits)**: 액추에이터가 한 샘플 사이에 움직일 수 있는 양. $(\underline{u}, \overline{u})$ 로 쓴다.

> [!tip] 비유 — 자동차의 속도와 가속도
> 진폭 한계는 "이 차는 시속 200km 이상 못 낸다"이고, 변화율 한계는 "이 차는 1초에 시속 20km씩밖에 못 올린다"이다. 둘은 완전히 다른 제약이고, 둘 다 지켜야 한다.

입력 제약의 좋은 점은 **컨트롤러가 제어 동작 값을 적절히 고르기만 하면 언제나 만족시킬 수 있다**는 것이다(출력 제약은 그렇지 않다 — 뒤에 나온다). $m$ 입력 $n$ 출력 공정을 증분 형태로 쓰고, 구간 $N$ 에 걸쳐 제약이 작용한다고 하면:

$$\mathbf{1}\,\underline{U} \le T\mathbf{u} + u(t-1)\,\mathbf{1} \le \mathbf{1}\,\overline{U}$$
$$\mathbf{1}\,\underline{u} \le \mathbf{u} \le \mathbf{1}\,\overline{u}$$

기호를 풀어 보자.

- $\mathbf{1}$ 은 $(N \times n) \times m$ 크기의 행렬로, $N$ 개의 $m \times m$ 단위행렬을 세로로 쌓은 것이다. "모든 시점에 같은 한계값을 적용하라"는 뜻을 행렬로 표현한 장치다.
- $T$ 는 **하삼각 블록 행렬(lower triangular block matrix)** 로, 0이 아닌 블록 성분이 전부 $m \times m$ 단위행렬이다([[하삼각 토플리츠 행렬]]).

$T$ 가 왜 하삼각인지가 핵심이다. 증분 $\Delta u$ 를 결정 변수로 쓰면 실제 제어 신호는 **과거 값에 증분을 누적**한 것이다.

$$u(t+j) = u(t-1) + \sum_{i=0}^{j}\Delta u(t+i)$$

이 누적합을 행렬로 쓰면 정확히 하삼각 행렬이 된다. 첫 줄은 $\Delta u(t)$ 하나만, 둘째 줄은 $\Delta u(t)+\Delta u(t+1)$, 이런 식이다. 그래서 위 부등식의 가운데 항 $T\mathbf{u} + u(t-1)\mathbf{1}$ 은 "각 시점의 실제 제어 신호 값"을 의미한다.

이 두 부등식을 하나로 압축하면 다음과 같은 **표준형**이 된다.

$$\mathbf{R}\,\mathbf{u} \le \mathbf{c}$$

$$\mathbf{R} = \begin{bmatrix} I_{N\times N} \\ -I_{N\times N} \\ T \\ -T \end{bmatrix}, \qquad
\mathbf{c} = \begin{bmatrix} \mathbf{1}\,\overline{u} \\ -\mathbf{1}\,\underline{u} \\ \mathbf{1}\,\overline{U} - \mathbf{1}u(t-1) \\ -\mathbf{1}\,\underline{U} + \mathbf{1}u(t-1)\end{bmatrix}$$

읽는 법: **하한 제약도 부호를 뒤집어 상한 제약처럼 만든다.** $x \ge a$ 는 $-x \le -a$ 와 같으므로, 모든 제약을 "$\le$" 방향으로 통일할 수 있다. 그래서 블록이 네 덩어리다 — 증분의 상한, 증분의 하한, 진폭의 상한, 진폭의 하한.

> [!note] 액추에이터 비선형성과 불감대
> 같은 방식으로 액추에이터의 비선형성도 다룰 수 있다. 예를 들어 **불감대(dead zone)** 는 "그 구간의 값은 쓰지 마라"는 제약을 걸어 처리한다. 변화율의 불감대를 $(\underline{u}_d, \overline{u}_d)$, 진폭의 불감대를 $(\underline{U}_d, \overline{U}_d)$ 라 하면 다음 조건을 요구한다.
> $$\mathbf{1}\,\underline{U}_d \ge T\mathbf{u} + u(t-1)\mathbf{1} \ge \mathbf{1}\,\overline{U}_d, \qquad \mathbf{1}\,\underline{u}_d \ge \mathbf{u} \ge \mathbf{1}\,\overline{u}_d$$
> **그런데 여기엔 함정이 있다.** 이런 종류의 제약이 만드는 실현가능 영역은 **비볼록(nonconvex)** 이다. "이 구간만 빼고 나머지"는 도넛 모양이라서 두 점을 이은 선분이 영역 밖으로 나갈 수 있기 때문이다. 그래서 최적화 문제를 풀기가 어려워진다.

> [!example] 예제 5.1 — 변화율과 진폭 제약
> 3장 예제 3.3의 반응기를 다시 가져온다. 이 반응기는 좌분수 행렬 기술(left fraction matrix description)로 다음과 같이 주어진다.
> $$\mathbf{A}(z^{-1}) = \begin{bmatrix} 1 - 1.8629z^{-1} + 0.8669z^{-2} & 0 \\ 0 & 1 - 1.8695z^{-1} + 0.8737z^{-2}\end{bmatrix}$$
> $$\mathbf{B}(z^{-1}) = \begin{bmatrix} 0.0420 - 0.0380z^{-1} & 0.4758 - 0.4559z^{-1} \\ 0.0582 - 0.0540z^{-1} & 0.1445 - 0.1361z^{-1}\end{bmatrix}$$
> 여기에 **조작 변수의 최대 변화율을 샘플당 0.2, 최대 절대값을 0.3** 으로 제약을 걸었다.

![[mpc_fig_5_3.png]]
*그림 5.3 — 조작 변수에 최대 변화율·최대값 제약을 도입한 뒤 예제 3.3 반응기의 응답*

> [!example] 그림이 말하는 것
> 3장에서 조작 변수에 제약이 없었을 때의 결과와 비교하면, **제약의 도입이 폐루프 응답을 더 느리게 만들었다**는 것을 관찰할 수 있다. 이것은 실패가 아니라 당연한 대가다. 액추에이터가 천천히밖에 못 움직인다면 공정도 천천히 반응할 수밖에 없다. 중요한 것은 컨트롤러가 **이 사실을 알고** 계획을 세운다는 점이다.

### 5.3.2 출력 제약 (Output Constraints)

때로는 제어 변수가 어떤 **띠(band)** $[\underline{y}, \overline{y}]$ 안에서 궤적을 따라가기를 원한다. 안전상의 이유일 수도 있고, 단순히 출력 신호 $y(k+j)$ 에 한계를 두고 싶어서일 수도 있다.

> [!tip] 비유 — 식품 산업의 온도 프로파일
> 책이 드는 예는 식품 산업이다. 어떤 공정은 **지정된 허용오차 안에서 따라가야 하는 온도 프로파일**을 요구한다. 살균이 되려면 온도가 충분히 높아야 하고, 맛이 상하지 않으려면 너무 높으면 안 된다. 즉 "위아래 두 줄 사이"를 지켜야 한다.

이 요구는 시스템의 출력을 상·하한이 만드는 띠 안에 강제로 넣어 표현한다.

$$\underline{\mathbf{y}} \le \underbrace{\mathbf{G}\mathbf{u} + \mathbf{f}}_{\mathbf{y}} \le \overline{\mathbf{y}}$$

여기서 $\mathbf{y} = \mathbf{G}\mathbf{u} + \mathbf{f}$ 는 지금까지 계속 써 온 예측식이다. $\mathbf{G}$ 는 스텝 응답 계수로 만든 동특성 행렬이고, $\mathbf{f}$ 는 **자유 응답(free response)**, 즉 "지금부터 아무것도 안 하면 출력이 어떻게 흘러갈지"이다([[자유 응답과 강제 응답]]). 앞과 같은 요령으로 "$\le$" 방향으로 통일하면:

$$\begin{bmatrix} \mathbf{G} \\ -\mathbf{G}\end{bmatrix}\mathbf{u} \le \begin{bmatrix} \overline{\mathbf{y}} - \mathbf{f} \\ \underline{\mathbf{y}} - \mathbf{f}\end{bmatrix}$$

> [!warning] 원문 수식 확인 필요
> 원문 텍스트의 우변 아래쪽 블록이 `y − f` 로 되어 있는데, $-\mathbf{G}\mathbf{u} \le -\underline{\mathbf{y}} + \mathbf{f}$ 가 되려면 부호가 $\mathbf{f} - \underline{\mathbf{y}}$ 여야 한다. 텍스트 추출 과정에서 하한 기호의 위아래 선과 마이너스 부호가 뭉개진 것으로 보인다. **의미는 "출력이 하한 아래로 내려가지 않게 한다"** 로 읽으면 된다.

> [!note] 하삼각 구조는 공짜 선물이 아니다
> 책은 여기서 한 마디를 덧붙인다. **제약 행렬의 모든 블록이 하삼각 블록**이며, 나중에(5.4.2절) 여기서 이득을 얻을 수 있다는 것이다. 하삼각이란 "$k$ 번째 제약은 $\mathbf{u}$ 의 앞쪽 $k$ 개 성분에만 의존한다"는 뜻이고, 그래서 **앞에서부터 차례로 범위를 좁혀 나가는** 재귀적 계산이 가능해진다.

같은 방식으로 공정의 피제어 변수에 다른 종류의 제약을 걸어 응답이 특정한 성질을 갖도록 강제할 수도 있다. 책은 세 가지를 든다.

#### (a) 오버슈트(Overshoot) 제약

어떤 공정에서는 오버슈트가 바람직하지 않다. **로봇 매니퓰레이터**의 경우 오버슈트는 작업대나 잡으려는 물체와의 **충돌**을 뜻할 수 있다. 설정점이 변경 후 충분히 긴 시간 동안 일정하게 유지된다면, 오버슈트 제약은 매우 쉽게 구현된다.

$$y(t+j) \le r(t) \qquad j = N_{o1}, \ldots, N_{o2}$$

$N_{o1}$ 과 $N_{o2}$ 는 오버슈트가 일어날 수 있는 구간을 정의한다. **모르겠으면 각각 1과 $N$ 으로 두면 된다** — 즉 전 구간에 걸어도 무방하다. 이를 조작 변수의 증분으로 표현하면:

$$\mathbf{G}\mathbf{u} \le \mathbf{1}\,r(t) - \mathbf{f}$$

**출력 제약의 일반형에서 상한 $\overline{\mathbf{y}}$ 자리에 설정점 $r(t)$ 를 넣은 것**과 정확히 같은 형태다. "출력이 설정점을 넘어가지 마라"가 곧 "설정점이 곧 상한이다"이기 때문이다.

#### (b) 단조 거동(Monotonic Behaviour) 제약

어떤 제어 시스템은 설정점에 도달하기 전에 **킥백(kickback)** 이라 불리는 진동을 보인다. 이런 진동은 여러 이유에서 바람직하지 않은데, 특히 **다른 공정에 외란을 일으키기** 때문이다. 이를 피하려면 설정점 변경 후 다음 제약을 추가한다.

$$\begin{aligned} y(t+j) &\le y(t+j+1) &&\text{if } y(t) < r(t) \\ y(t+j) &\ge y(t+j+1) &&\text{if } y(t) > r(t)\end{aligned}$$

말로 풀면 **"출력이 계속 같은 방향으로만 움직여라"** 이다. 목표가 위에 있으면 계속 올라가기만 하고, 아래에 있으면 계속 내려가기만 하라는 뜻이다. 조작 변수로 표현하면:

$$\mathbf{G}\mathbf{u} + \mathbf{f} \le \begin{bmatrix} \mathbf{0}^\mathsf{T} \\ \hline \mathbf{G}'\end{bmatrix}\mathbf{u} + \begin{bmatrix} y(t) \\ \hline \mathbf{f}'\end{bmatrix}$$

여기서 $\mathbf{G}'$ 와 $\mathbf{f}'$ 는 $\mathbf{G}$ 와 $\mathbf{f}$ 의 **마지막 $n$ 개 행을 잘라낸 것**이다($n$ 은 출력 변수의 개수). 왜 잘라내는가? 좌변이 $y(t+1) \ldots y(t+N)$ 이고 우변이 $y(t) \ldots y(t+N-1)$ 이 되도록 **한 칸 밀어야** 하기 때문이다. 우변의 맨 위가 $y(t)$(현재 출력, 상수)이고 맨 아래 한 칸이 잘려 나가는 이유가 이것이다.

정리하면 다음의 깔끔한 형태가 된다.

$$\begin{bmatrix} G_0 & 0 & \cdots & 0 \\ G_1 - G_0 & G_0 & \cdots & 0 \\ \vdots & \vdots & \ddots & \vdots \\ G_{N-1}-G_{N-2} & G_{N-2}-G_{N-3} & \cdots & G_0 \end{bmatrix}\mathbf{u} \le \begin{bmatrix} y(t) - \mathbf{f}_1 \\ \mathbf{f}_1 - \mathbf{f}_2 \\ \vdots \\ \mathbf{f}_{N-1} - \mathbf{f}_N\end{bmatrix}$$

**차분(difference)의 구조가 눈에 보인다.** 좌변 행렬의 성분이 $G_k - G_{k-1}$ 이고 우변이 $\mathbf{f}_{k-1} - \mathbf{f}_k$ 인 것은, 이 제약이 본질적으로 "이웃한 두 시점의 출력을 비교하라"이기 때문이다.

![[mpc_fig_5_4.png]]
*그림 5.4 — (a) 오버슈트 제약이 있을 때와 없을 때 진동 시스템의 시뮬레이션 결과, (b) 단조 거동 제약을 도입한 후의 결과*

> [!example] 그림이 말하는 것
> (a)는 오버슈트 제약의 효과를, (b)는 단조 거동 제약을 추가한 결과를 보여준다. 책의 설명대로 **진동이 사실상 제거되었다.** 주목할 것은 이것이 컨트롤러의 튜닝 파라미터($\lambda$ 등)를 손대서 얻은 결과가 아니라, **원하는 응답 모양 자체를 제약으로 직접 지정해서** 얻은 결과라는 점이다. 이것이 제약 기반 설계의 강력함이다.

> [!example] 예제 5.2 — 오버슈트와 단조 거동 제약
> 진동 시스템 $G(s) = 50/(s^2+25)$ 를 이산화한 것을 대상으로 한다. 샘플링 시간 0.1초에서 이산 전달함수는:
> $$G(z^{-1}) = \frac{0.244835(z^{-1}+z^{-2})}{1 - 1.75516z^{-1}+z^{-2}}$$
> **예측 지평과 제어 지평을 모두 11, 가중 계수를 50** 으로 둔 제약 없는 GPC를 적용하면(그림 5.4 왼쪽) 출력에 눈에 띄는 오버슈트가 나타난다. 오버슈트 제약을 고려하면 이것이 제거된다. 그러나 오버슈트가 사라진 뒤에도 설정점에 도달하기 전 **킥백 진동**이 남아 있다. 이를 없애려면 단조 거동 제약을 걸어야 한다.
>
> **왜 지평이 이렇게 긴가?** 책이 직접 설명한다. **개루프 시스템의 진동 모드를 상쇄해야 하고, 실현가능한 해를 얻으려면 많은 수의 제어 동작을 고려해야 하기 때문이다.** 이것은 제약 MPC의 중요한 실무 교훈이다 — 제약이 빡빡할수록 **자유도(제어 지평)** 를 넉넉히 줘야 실현가능해진다([[예측 지평과 제어 지평]]).

#### (c) 비최소위상(Nonminimum Phase) 거동 제약

**비최소위상 거동**이란 입력에 스텝을 넣었을 때 출력이 **최종 위치로 가기 전에 먼저 반대 방향으로 움직이는** 현상이다([[비최소위상과 역응답]]). 이것이 바람직하지 않을 수 있으므로 제약으로 막을 수 있다.

$$\begin{aligned} y(t+j) &\ge y(t) &&\text{if } y(t) < r(t) \\ y(t+j) &\le y(t) &&\text{if } y(t) > r(t)\end{aligned}$$

즉 **"출발점보다 뒤로는 가지 마라"** 이다. 조작 변수의 증분으로 쓰면:

$$\mathbf{G}\mathbf{u} \ge \mathbf{1}y(t) - \mathbf{f}$$

단조 제약과 비교해 보면 차이가 분명하다. 단조 제약은 **이웃한 시점끼리** 비교하고, 비최소위상 제약은 **모든 시점을 현재값 $y(t)$ 하나와** 비교한다. 그래서 우변이 상수 벡터 $\mathbf{1}y(t)$ 다.

![[mpc_fig_5_5.png]]
*그림 5.5 — (a) 비최소위상 공정을 제어하는 GPC의 전형적인 응답, (b) 비최소위상 제약을 도입해 역피크를 제한한 결과*

> [!example] 예제 5.3 + 그림이 말하는 것
> 비최소위상 시스템 $G(s) = \dfrac{1-s}{1+s}$ 를 0.3초로 샘플링하면
> $$G(z^{-1}) = \frac{-1 + 1.2592z^{-1}}{1 - 0.7408z^{-1}}$$
> 이다. 분자의 첫 계수가 **음수(−1)** 인 것이 역응답의 원인이다. **예측 지평 30, 제어 지평 10, 가중 계수 0.1** 인 GPC를 적용하면(왼쪽) 설정점 변화와 **반대 방향의 초기 피크**라는 전형적인 비최소위상 거동이 나타난다. **역피크를 0.05로 제한**하면(오른쪽) 피크가 제거되지만 시스템은 더 느려진다. 특히 **제어 신호가 천천히 증가**해서 역피크를 피하는 모습이 관찰된다 — 급하게 밀면 반드시 뒤로 튀므로, 컨트롤러가 스스로 조심스러워진 것이다.

### 5.3.3 종단 제약 (Terminal Constraints)

**종단 집합 제약(terminal set constraint)** 은 운전 조건 때문에 부과될 수도 있고, **안정성을 보장하는 수단**으로 부과될 수도 있다. 여기서 책은 대단히 중요한 사실을 하나 던진다.

> [!important] 안정성 = 제약 만족 문제
> **MPC의 안정성을 보장하는 대부분의 정식화는 두 가지 핵심 재료를 갖는다: 종단 상태 벌점(terminal state penalization)과 최종 상태를 강제로 넣는 종단 집합(terminal set).** 따라서 **안정성은 제약 만족 문제로 환원된다.** 이것이 5.8절에서 본격적으로 전개될 이야기의 씨앗이다.

MPC 문제의 최종 상태(예측 지평 끝에서의 상태)가 어떤 종단 집합에 속하도록 강제되면, 그것은 제어 동작 벡터에 대한 제약 집합을 만들어 낸다. 종단 영역이 다음 다면체로 정의된다고 하자.

$$\mathbf{R}_T\,x(t+N) \le \mathbf{r}_T \tag{5.2}$$

한편 예측된 상태 벡터는 다음과 같이 표현된다.

$$\mathbf{x} = \mathbf{G}_u\mathbf{u} + \mathbf{F}_x x(t) \tag{5.3}$$

이제 유도를 한 줄씩 따라가자.

1. 식 (5.3)의 **마지막 $n$ 개 행**만 취한다($n = \dim(x(t))$, 즉 상태의 차원). 이 행들이 바로 $x(t+N)$ 에 해당한다.
   $$x(t+N) = \mathbf{g}_{u_N}\mathbf{u} + \mathbf{f}_{x_N}x(t)$$
   여기서 $\mathbf{g}_{u_N}$ 과 $\mathbf{f}_{x_N}$ 은 각각 $\mathbf{G}_u$ 와 $\mathbf{F}_x$ 의 마지막 $n$ 개 행이다.
2. 이것을 식 (5.2)에 대입한다.
   $$\mathbf{R}_T(\mathbf{g}_{u_N}\mathbf{u} + \mathbf{f}_{x_N}x(t)) \le \mathbf{r}_T \tag{5.4}$$
3. 좌변을 $\mathbf{u}$ 에 대해 정리하면 $\mathbf{R}_T\mathbf{g}_{u_N}\mathbf{u} \le \mathbf{r}_T - \mathbf{R}_T\mathbf{f}_{x_N}x(t)$ 이다.

**결론: 다면체 종단 영역은 제어 동작 벡터에 대한 선형 제약 집합을 유도한다.** 상태 공간의 기하학적 조건이 $\mathbf{u}$ 에 대한 부등식 몇 줄로 번역된 것이다([[불변 집합 Invariant Set]]).

> [!note] 종단 집합이 한 점으로 줄어드는 특수한 경우
> 종단 집합이 **점 하나**가 되는 경우가 있다. **CRHPC**(constrained receding horizon predictive control)를 적용할 때가 그 예로, 여기서는 비용 지평 $N_y$ 이후 $m$ 개의 샘플링 주기 동안 공정의 예측 출력이 예측된 기준값을 **정확히** 따라가도록 강제된다. 이때 종단 상태 제약은 미래 제어 증분에 대한 **등식 제약 집합**으로 표현된다. 예측식
> $$\mathbf{y}_m = \mathbf{G}_m\mathbf{u} + \mathbf{f}_m$$
> 에서 예측 응답이 미래 기준 $\mathbf{r}_m$ 을 따르도록 하면
> $$\mathbf{G}_m\mathbf{u} = \mathbf{r}_m - \mathbf{f}_m$$
> 이라는 등식 제약이 나온다. 책은 여기서 **"이런 종류의 제약을 도입하면 문제가 단순해져 필요한 계산량이 줄어든다"** 고 예고한다. 5.4.1절이 그 이야기다 — 등식 제약은 **변수를 소거해서 없애 버릴 수 있기** 때문이다.

### 5.3.4 일반형 (General Form)

지금까지 나온 모든 부등식 제약은 다음 하나의 형태로 표현된다.

$$\mathbf{R}\mathbf{u} \le \mathbf{r} + \mathbf{V}\mathbf{z}$$

여기서 $\mathbf{z}$ 는 **현재와 과거 신호로 구성된 벡터**다. 모델 종류에 따라 그 정체가 다르다.

| 모델 표현 | $\mathbf{z}$ 의 정체 |
|---|---|
| 상태공간 표현 | $x(t)$ 그 자체 |
| 컨볼루션 / CARIMA / CARMA 모델 | 현재 출력 + 과거 입력·출력의 유한 급수 |

그런데 **과거의 입출력 신호는 상태의 한 표현으로 볼 수 있으므로**, 모든 경우를 다음 일반형으로 쓸 수 있다.

$$\mathbf{R}\mathbf{u} \le \mathbf{r} + \mathbf{V}x(t) \tag{5.5}$$

> [!tip] 실무적으로 가장 중요한 관찰
> $\mathbf{R}$, $\mathbf{r}$, $\mathbf{V}$ 는 **공정 파라미터와 신호 한계값에만 의존**한다. 이것들은 자주 바뀌지 않으므로 **바뀔 때만 다시 계산하면 된다.** 반면 부등식 (5.5)의 **우변은 공정 상태에 의존**하고 상태는 일반적으로 매 샘플마다 바뀌므로 **매번 다시 계산해야 한다.** 실시간 구현에서는 이 구분이 계산 부담을 크게 좌우한다. 무거운 행렬 계산은 오프라인으로 밀어내고, 온라인에서는 벡터 하나만 갱신하는 것이다.

등식 제약도 같은 방식으로 만들 수 있다. 제약의 종류를 구분해서 강조하기 위해 등식 제약은 $\mathbf{A}\mathbf{u} = \mathbf{a}$ 로 쓴다.

---

## 5.4 제약 제거 (Constraint Removal)

### 왜 제약을 지우려 하는가?

지금까지 본 대로, 제약을 고려한 MPC 문제는 **식 (5.1)을 선형 제약 집합 아래에서 최소화하는 것**이다. 즉 **이차 함수를 선형 제약 아래 최적화**하는 문제이고, 이것을 흔히 **QP(quadratic program) 문제**라고 부른다.

> [!note] 용어 주의
> 책의 각주가 밝히듯, 이 챕터에서 약어 "QP"는 문맥에 따라 **"이차계획(quadratic program)"** 을 뜻하기도 하고 **"이차계획법(quadratic programming)"** 을 뜻하기도 한다. 뒤에 나올 "LP"도 마찬가지다.

여기서 핵심적인 사실 하나. **QP 알고리즘의 계산 요구량은 고려하는 제약의 개수에 크게 좌우된다.** 그렇다면 **불필요한(superfluous) 제약**, 즉 실현가능 영역을 실제로 제한하지 않는 제약들을 없애면 알고리즘의 효율을 높일 수 있다.

> [!tip] 비유 — 이중으로 쳐진 울타리
> 운동장 둘레에 울타리를 쳤는데, 그 바깥으로 10m 더 나가서 울타리를 하나 더 쳤다고 하자. **바깥 울타리는 아무 일도 하지 않는다.** 안쪽 울타리가 이미 사람들을 막고 있기 때문이다. 이런 울타리를 **잉여(redundant) 제약**이라 하고, 지워도 실현가능 영역은 전혀 변하지 않는다. 다만 경비원(최적화 알고리즘)은 매번 그 울타리도 확인하느라 시간을 쓴다.

### 5.4.1 등식 제약 제거 (Removing Equality Constraints)

먼저 더 쉬운 등식 제약부터 보자. 등식 제약은 CRHPC 같은 정식화에서 자연스럽게 나타난다 — 미래 공정 출력이 미래 기준값을 **정확히** 따르도록 강제하는 경우다.

등식 제약이 붙은 QP 문제는 다음과 같다.

$$\begin{aligned}\text{minimize } \quad & \tfrac{1}{2}\mathbf{u}^\mathsf{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathsf{T}\mathbf{u} + \mathbf{f}_0 \\ \text{subject to: } \quad & \mathbf{A}\mathbf{u} = \mathbf{a}\end{aligned}$$

$\mathbf{A}$ 는 $m \times n$ 행렬, $\mathbf{a}$ 는 $m$ 차원 벡터이며, $m < n$ 이고 $\text{rank}(\mathbf{A}) = m$ 이라고 가정한다.

> [!question] 이 가정들이 왜 필요한가?
> $m < n$ 은 **"제약의 개수가 변수의 개수보다 적다"** 는 뜻이다. 만약 $m = n$ 이면 제약만으로 답이 하나로 정해져 버려 최적화할 것이 없다. $\text{rank}(\mathbf{A}) = m$ 은 **"제약들이 서로 중복되지 않는다"** 는 뜻이다. 같은 말을 두 번 하는 제약이 있으면 랭크가 떨어진다.

목표는 **제약을 정확히 만족하면서 목적함수를 최소화하는 $\mathbf{u}$ 를 찾는 것**이다. 이를 달성하는 아이디어는 **일부 제어 변수를 나머지 변수로 표현해서, 문제를 더 작은 무제약 최적화로 축소하는 것**이다. 방법은 여러 가지다.

#### (1) 직접 소거 (Direct Elimination)

가장 직접적인 방법이다. 제약을 이용해 $m$ 개의 $\mathbf{u}$ 변수를 나머지 $n-m$ 개 변수의 함수로 표현한 뒤, 목적함수에 대입한다. 그러면 문제는 **$n-m$ 개 변수에 대한 제약 없는 이차 함수 최소화**로 줄어든다.

> [!tip] 비유 — 연립방정식 대입법
> 고등학교에서 배운 연립방정식 풀이 그대로다. $x + y = 10$ 이라는 제약이 있으면 $y = 10 - x$ 로 놓고 목적함수에 넣는다. 변수가 하나 줄고 제약도 하나 사라진다. **제약을 지운 것이 아니라 변수 안에 녹여 넣은 것**이다.

#### (2) 일반화 소거 (Generalized Elimination)

더 정교한 접근이다. 문제를 **더 작을 수 있는 보조 결정 벡터 $\mathbf{v}$ 에 의존하는 새로운 이차 함수의 최소화**로 단순화하되, 제약이 **자동으로(inherently)** 만족되도록 만든다. 이를 위해 $\mathbf{u}$ 를 다음 선형 결합으로 표현한다.

$$\mathbf{u} = \mathbf{u}^p + \mathbf{Z}\mathbf{v}$$

각 조각의 역할이 명확하다.

- $\mathbf{u}^p$ — **등식 제약을 만족하는 임의의 한 점(particular solution)**. 즉 $\mathbf{A}\mathbf{u}^p = \mathbf{a}$.
- $\mathbf{Z} \in \mathbb{R}^{n \times (n-m)}$ — $\mathbf{A}^\mathsf{T}$ 의 **영공간(null space)** 을 생성하는 행렬. 즉 $\mathbf{A}\mathbf{Z} = 0$.

**왜 이렇게 하면 제약이 자동으로 지켜지는가?** 대입해 보면 즉시 보인다.

$$\mathbf{A}\mathbf{u} = \mathbf{A}\mathbf{u}^p + \mathbf{A}\mathbf{Z}\mathbf{v} = \mathbf{a} + 0\cdot\mathbf{v} = \mathbf{a}$$

$\mathbf{v}$ 를 **아무 값으로 바꿔도** 제약이 깨지지 않는다. 즉 $\mathbf{v}$ 는 **자유롭게 움직일 수 있는 방향**만 담고 있다([[영공간과 유사역행렬]]).

> [!tip] 비유 — 기차와 선로
> $\mathbf{u}^p$ 는 **선로 위의 어느 한 지점**이고, $\mathbf{Z}$ 는 **선로가 뻗은 방향**이다. 기차는 선로 위 어디로든 갈 수 있지만(자유), 선로를 벗어날 수는 없다(제약). $\mathbf{v}$ 는 "선로를 따라 얼마나 갔는가"를 나타내는 하나의 숫자(또는 벡터)일 뿐이다. 원래 $n$ 차원 공간을 헤매던 문제가 **$n-m$ 차원의 선로 위 문제**로 줄었다.

$\mathbf{u}^p$ 는 $\mathbf{u}^p = \mathbf{Y}\mathbf{a}$ 로 구할 수 있는데, 여기서 $\mathbf{Y} \in \mathbb{R}^{n \times m}$ 은 $\mathbf{A}$ 의 **일반화 역행렬** 역할을 하며 $\mathbf{A}\mathbf{Y} = \mathbf{I}$ 를 만족한다.

**$\mathbf{Y}$ 와 $\mathbf{Z}$ 를 한꺼번에 찾는 요령.** $\mathbf{A}$ 에 추가 행렬 $\mathbf{W}$ 를 붙여 확대 행렬 $\mathbf{M}$ 을 만든다.

$$\mathbf{M} = \begin{pmatrix}\mathbf{A} \\ \mathbf{W}\end{pmatrix}$$

$\mathbf{W}$ 는 $(n-m)\times n$ 행렬로, $\mathbf{M}$ 이 **정사각이면서 가역**이 되도록 고른다. 그러면 $\mathbf{M}$ 의 역행렬을 두 블록으로 쪼갠 것이 바로 우리가 찾던 두 행렬이다.

$$\mathbf{M}^{-1} = \begin{pmatrix}\mathbf{Y} & \mathbf{Z}\end{pmatrix}$$

왜 그런가? $\mathbf{M}\mathbf{M}^{-1} = \mathbf{I}$ 를 블록으로 전개하면 된다.

$$\begin{pmatrix}\mathbf{A} \\ \mathbf{W}\end{pmatrix}\begin{pmatrix}\mathbf{Y} & \mathbf{Z}\end{pmatrix} = \begin{pmatrix}\mathbf{A}\mathbf{Y} & \mathbf{A}\mathbf{Z} \\ \mathbf{W}\mathbf{Y} & \mathbf{W}\mathbf{Z}\end{pmatrix} = \begin{pmatrix}\mathbf{I} & 0 \\ 0 & \mathbf{I}\end{pmatrix}$$

좌상단 블록에서 $\mathbf{A}\mathbf{Y} = \mathbf{I}$, 우상단 블록에서 $\mathbf{A}\mathbf{Z} = 0$ 이 **동시에 나온다.** 원하던 두 성질이 공짜로 따라오는 것이다.

> [!note] 각주의 재미있는 사실
> $\mathbf{W}$ 를 $[\mathbf{0}\ \ \mathbf{I}]$ 로 고르면, 이 방법은 **직접 소거법과 정확히 일치한다.** 즉 직접 소거는 일반화 소거의 특수한 경우다.

#### (3) 무어–펜로즈 유사역행렬 (Moore–Penrose Pseudo-inverse)

일반화 소거를 구현하는 한 가지 방법은 **무어–펜로즈 유사역행렬**을 쓰는 것이다. 이것은 $\mathbf{Y}$ 를 계산하는 직관적인 방법을 제공하며, **최소제곱(least-squares) 의미에서 최적**이다.

$$\mathbf{Y} = (\mathbf{A}^\mathsf{T}\mathbf{A})^{-1}\mathbf{A}^\mathsf{T} \qquad (\mathbf{A}^\mathsf{T}\mathbf{A} \text{ 가 가역일 때})$$

유사역행렬로 **대칭이고 멱등(idempotent)인 사영 행렬(projection matrix) $\mathbf{P}$** 를 만들 수도 있다. 이 행렬은 임의의 벡터 $\mathbf{u}$ 를 $\mathbf{A}$ 의 영공간으로 사영시키며, 따라서 $\mathbf{A}\mathbf{P} = 0$ 이 성립한다.

$$\mathbf{P} = \underbrace{\mathbf{I} - \overbrace{\mathbf{A}^\mathsf{T}(\mathbf{A}\mathbf{A}^\mathsf{T})^{-1}\mathbf{A}}^{\text{Col}(\mathbf{A}^\mathsf{T})\text{ 로의 사영}}}_{\text{Nul}(\mathbf{A})\text{ 로의 사영}}$$

$\mathbf{A}$ 가 완전 랭크(full rank)라는 조건이 필요하다. 책의 각주가 이 식의 기하학적 의미를 설명한다: 사영 $\mathbf{P}\mathbf{v}$ 는 **$\mathbf{v}$ 에서 그 벡터의 $\mathbf{A}^\mathsf{T}$ 열공간 성분을 빼는 것**이다. 그 결과 $\mathbf{P}$ 는 $\text{Col}(\mathbf{A}^\mathsf{T})$ 에 수직인 벡터, 즉 $\mathbf{A}$ 의 영공간에 속하는 벡터를 만들어 낸다.

> [!tip] 비유 — 그림자
> 햇빛 아래 막대기의 **그림자**를 생각하자. 막대기(원래 벡터 $\mathbf{v}$)에서 수직 성분을 빼면 땅에 누운 그림자(사영)가 남는다. $\mathbf{P}$ 가 하는 일이 정확히 이것이다 — **금지된 방향(제약을 깨는 방향) 성분을 잘라내고, 허용된 평면 위의 성분만 남긴다.** 멱등이라는 말은 $\mathbf{P}^2 = \mathbf{P}$, 즉 **그림자의 그림자는 그대로 그림자**라는 당연한 성질이다.

이 방법이 제안하는 변수 변환은 다음과 같다.

$$\mathbf{u} = \mathbf{u}^p + \mathbf{P}\mathbf{v} = \mathbf{Y}\mathbf{a} + \mathbf{P}\mathbf{v}$$

#### (4) 결국 무엇이 남는가 — 축소된 무제약 문제

앞의 어떤 치환을 쓰든, 제약이 있던 최적화 문제가 **제약 없는 문제**로 바뀐다. $\mathbf{u} = \mathbf{Y}\mathbf{a} + \mathbf{Z}\mathbf{v}$ 를 대입하면 등식 제약은 저절로 만족되고 목적함수는 다음이 된다. **중간 단계를 생략하지 않고 전개하면:**

$$\begin{aligned} J(\mathbf{v}) &= \tfrac{1}{2}[\mathbf{Y}\mathbf{a}+\mathbf{Z}\mathbf{v}]^\mathsf{T}\mathbf{H}[\mathbf{Y}\mathbf{a}+\mathbf{Z}\mathbf{v}] + \mathbf{b}^\mathsf{T}[\mathbf{Y}\mathbf{a}+\mathbf{Z}\mathbf{v}] + \mathbf{f}_0 \\ &= \tfrac{1}{2}\mathbf{v}^\mathsf{T}\mathbf{Z}^\mathsf{T}\mathbf{H}\mathbf{Z}\mathbf{v} + [\mathbf{b}^\mathsf{T} + \mathbf{a}^\mathsf{T}\mathbf{Y}^\mathsf{T}\mathbf{H}]\mathbf{Z}\mathbf{v} + [\tfrac{1}{2}\mathbf{a}^\mathsf{T}\mathbf{Y}^\mathsf{T}\mathbf{H} + \mathbf{b}^\mathsf{T}]\mathbf{Y}\mathbf{a} + \mathbf{f}_0\end{aligned}$$

전개 결과를 항별로 읽어 보자. 첫째 항은 $\mathbf{v}$ 에 대한 이차항이고 새로운 헤시안이 $\mathbf{Z}^\mathsf{T}\mathbf{H}\mathbf{Z}$ 다. 둘째 항은 일차항이다. 셋째와 넷째 항은 $\mathbf{v}$ 와 무관한 상수이므로 최소점의 위치와 무관하다.

즉 **$n-m$ 개 변수에 대한 무제약 QP 문제**가 되었다. 만약 $\mathbf{Z}^\mathsf{T}\mathbf{H}\mathbf{Z}$ 가 **양정치(positive definite)** 이면, 유일한 전역 최적점이 존재하며 다음 선형 연립방정식을 풀어 찾을 수 있다.

$$\mathbf{Z}^\mathsf{T}\mathbf{H}\mathbf{Z}\,\mathbf{v} = -\mathbf{Z}^\mathsf{T}\nabla J(\mathbf{u}^p) = -\mathbf{Z}^\mathsf{T}(\mathbf{b} + \mathbf{H}\mathbf{Y}\mathbf{a})$$

**이 식의 해석이 아름답다.** 우변은 "출발점 $\mathbf{u}^p$ 에서의 그래디언트를 허용 방향으로 사영한 것"이다. 즉 **내려가고 싶은 방향 중에서 갈 수 있는 성분만 남긴 것**이다([[라그랑주 승수와 등식 제약]]).

### 5.4.2 부등식 제약 제거 (Removing Inequality Constraints)

이제 부등식 $\mathbf{R}\mathbf{u} \le \mathbf{c}$ 의 경우다. 여기서는 **소거**가 아니라 **잉여 제거**가 목표다. 어떤 제약이 **잉여(redundant)** 라는 것은 $\mathbf{R}$ 과 $\mathbf{c}$ 에서 대응하는 행을 지워도 다면체 $\mathbf{R}\mathbf{u}\le\mathbf{c}$ 가 정의하는 실현가능 집합이 **전혀 변하지 않는다**는 뜻이다.

최소한의 제한 제약 집합을 찾는 알고리즘은 여럿 있고, 불필요한 제약을 없애면 계산량이 줄어든다. **그런데 역설이 있다: 그 절차 자체가 상당한 계산량을 요구할 수 있다.** 다행히 제약의 구조를 활용하면 이 부담을 덜 수 있다. 책은 두 가지 대안을 제시한다.

#### (1) 행 최대화로 제약 제거 (Removing Constraints by Row Maximization)

일반적인 방법이다. 다음 선형계획(LP) 문제를 푼다.

$$\max_{\mathbf{u}}\ \mathbf{r}_i\mathbf{u}$$

단, 제약은 $\mathbf{R}\mathbf{u}\le\mathbf{c}$ 에서 **$i$ 번째 제약 $\mathbf{r}_i\mathbf{u}\le c_i$ 를 뺀 나머지 전부**로 한다. 이때 얻은 최댓값을 $z_i$ 라 하자.

**판정: 만약 $z_i \le c_i$ 이면 $i$ 번째 제약은 잉여다.** 논리가 명쾌하다 — 나머지 제약들만 지켜도 $\mathbf{r}_i\mathbf{u}$ 가 상한 $c_i$ 를 절대 넘지 못한다면, $i$ 번째 제약은 아무 일도 하지 않는 것이다.

이 과정을 모든 제약에 대해 반복하면 잉여 제약을 전부 없앨 수 있다.

> [!warning] 비용을 잊지 말 것
> 이 방법은 **제약 하나당 LP 한 개**를 풀어야 한다. 제약이 수백 개면 LP를 수백 번 푼다. 그래서 계산을 줄이려다 계산이 더 드는 상황이 벌어질 수 있고, 이것이 다음 방법이 필요한 이유다.

#### (2) 제약 구조 활용 (Exploiting the Constraints Structure)

**제약 행렬이 하삼각**이라는 사실을 이용하면 훨씬 싸게 비제한 제약을 찾을 수 있다. $\mathbf{u} = \mathbf{1}\underline{u} + \mathbf{x}$ 로 변수를 옮기면(즉 하한을 원점으로 이동시키면) 액추에이터의 변화율·진폭 제약과 공정 출력 신호 제약이 다음과 같이 표현된다.

$$\begin{aligned}0 &\le \mathbf{x} \le \mathbf{c}_1 \\ \mathbf{c}_3 &\le T\mathbf{x} \le \mathbf{c}_2 \\ \frac{\mathbf{c}_5}{g_0} &\le \frac{\mathbf{G}}{g_0}\mathbf{x} \le \frac{\mathbf{c}_4}{g_0}\end{aligned} \tag{5.6}$$

여기서 $\mathbf{c}^\mathsf{T} = [\mathbf{c}_1^\mathsf{T}\ \mathbf{c}_2^\mathsf{T}\ \mathbf{c}_3^\mathsf{T}\ \mathbf{c}_4^\mathsf{T}\ \mathbf{c}_5^\mathsf{T}]$ 이고, $g_0$ 은 행렬 $\mathbf{G}$ 의 첫 번째 원소다($\mathbf{G}$ 가 하삼각임을 기억하자 — 그래서 $g_0$ 이 대각 성분이다). 양변을 $g_0$ 으로 나눈 이유는 **모든 제약의 첫 변수 계수를 1로 맞춰서 직접 비교할 수 있게** 하기 위해서다.

이제 잉여 제약을 찾는 간단한 절차를 적용할 수 있다.

**1단계 — 단일 변수 제약 분석.** 변수 하나($x_1$)에만 영향을 주는 제약부터 시작한다. 각 제약을 비교해 최소·최대 한계를 찾는다.

$$x_1 \le \min\!\left(c_{11},\ c_{21},\ \frac{c_{41}}{g_0}\right), \qquad x_1 \ge \max\!\left(0,\ c_{31},\ \frac{c_{51}}{g_0}\right)$$

이렇게 $l_1 \le x_1 \le r_1$ 이라는 한계를 얻는다. $r_1$ 은 **가장 작은 상한**, $l_1$ 은 **가장 큰 하한**이다. **이렇게 하면 제약 네 개를 제거할 수 있다** — 여러 상한 중 이긴 하나와 여러 하한 중 이긴 하나만 남기면 되기 때문이다.

**2단계 — 이전 한계를 이용해 다변수 의존성 평가.** 이제 $x_1$ 과 $x_2$ 를 제한하는 제약, 즉 (5.6)의 각 제약 블록의 **두 번째 행**을 본다. 방금 구한 $x_1$ 의 한계를 대입하면 다음과 같이 쓸 수 있다.

$$x_2 \le \min\!\left(c_{12},\ c_{22}-r_1,\ \frac{c_{42}}{g_0}-\frac{g_1}{g_0}r_1\right), \qquad x_2 \ge \max\!\left(0,\ c_{32}-l_1,\ \frac{c_{52}}{g_0}-\frac{g_1}{g_0}l_1\right)$$

같은 방식으로 $x_2$ 에 대한 한계 $r_2$, $l_2$ 를 세울 수 있고, **이렇게 계산된 경계에 영향을 주지 않는 제약은 잉여이므로 제거**한다.

**3단계 — 재귀적 적용.** **제약 행렬이 하삼각이므로** 같은 절차를 $x_3$ 에 적용하고, 이어서 나머지 변수들에 대해 재귀적으로 반복할 수 있다.

> [!important] 하삼각 구조가 주는 것
> 이 절차 전체가 성립하는 이유는 오직 하나, **하삼각 구조** 때문이다. $k$ 번째 제약이 앞쪽 $k$ 개 변수에만 의존하므로 **$x_1$ 을 확정한 뒤 그 결과로 $x_2$ 를 확정하는** 순차 진행이 가능하다. 만약 제약 행렬이 꽉 찬 행렬이었다면 모든 변수가 얽혀 이 방법을 쓸 수 없다. MPC의 구조가 최적화의 효율로 직결되는 좋은 예다.

> [!warning] 이 절차의 한계
> 책이 정직하게 밝힌다. **위 절차가 최소 개수의 제약을 보장하지는 않는다.** 더 줄일 수도 있지만 그러려면 더 많은 계산과 더 복잡한 알고리즘이 필요하다. 즉 이것은 **싸고 빠르게 상당수를 제거하는** 실용적 타협이다.

---

## 5.5 이차계획법 (Quadratic Programming)

### QP 문제의 표준 정식화

앞 절에서 말한 대로, 신호에 한계가 있는 공정에 MPC 컨트롤러를 구현하려면 **이차계획 문제**를 풀어야 한다. 표준형은 다음과 같다.

$$\begin{aligned}\text{minimize } \quad & J(\mathbf{u}) := \tfrac{1}{2}\mathbf{u}^\mathsf{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathsf{T}\mathbf{u} + \mathbf{f}_0 \\ \text{subject to: } \quad & \mathbf{A}\mathbf{u} = \mathbf{a}, \quad \mathbf{C}\mathbf{u} \le \mathbf{c}\end{aligned}$$

$\mathbf{A}$ 는 $m\times n$, $\mathbf{C}$ 는 $p\times n$ 행렬이고, $\mathbf{a}$ 는 $m$ 벡터, $\mathbf{c}$ 는 $p$ 벡터다. $\text{rank}(\mathbf{A}) = m$ 을 가정한다.

목표는 $J(\mathbf{u})$ 를 최소화하는 **실현가능한 결정 변수 벡터 $\mathbf{u}^*$** 를 찾는 것이다. 즉 모든 실현가능한 $\mathbf{u}$ 에 대해 $J(\mathbf{u}^*) \le J(\mathbf{u})$ 이다.

### 상계와 하계 — 라그랑지안이 등장하는 이유

여기서 책은 매우 교육적인 논리를 편다. **최솟값을 위아래에서 조여 가는 이야기**다.

**상계(upper bound)는 공짜다.** 아무 실현가능한 $\mathbf{u}$ 나 하나 찾아 $J(\mathbf{u})$ 를 계산하면, $J(\mathbf{u}) \ge J(\mathbf{u}^*)$ 이므로 그 값은 최솟값의 상계다.

**하계(lower bound)는 어떻게 얻는가?** 여기서 **라그랑지안(Lagrangian)** 을 만든다.

$$\mathcal{L}(\mathbf{u}, \boldsymbol{\lambda}, \boldsymbol{\mu}) = \tfrac{1}{2}\mathbf{u}^\mathsf{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathsf{T}\mathbf{u} + \mathbf{f}_0 + \boldsymbol{\lambda}^\mathsf{T}(\mathbf{A}\mathbf{u}-\mathbf{a}) + \boldsymbol{\mu}^\mathsf{T}(\mathbf{C}\mathbf{u}-\mathbf{c}) \tag{5.7}$$

$\boldsymbol{\lambda}$ 와 $\boldsymbol{\mu} \ge 0$ 은 각각 등식 제약과 부등식 제약에 붙는 **라그랑주 승수(Lagrange multiplier)** 벡터다([[라그랑주 승수와 등식 제약]]).

**왜 이것이 하계를 주는가?** 논리를 한 걸음씩 보자.

1. 실현가능한 $\mathbf{u}$ 에 대해 $\mathbf{A}\mathbf{u}-\mathbf{a} = 0$ 이므로 셋째 항은 **정확히 0**이다.
2. 실현가능한 $\mathbf{u}$ 에 대해 $\mathbf{C}\mathbf{u}-\mathbf{c} \le 0$ 이고 $\boldsymbol{\mu}\ge 0$ 이므로, 넷째 항은 **0 이하**다(양수 곱하기 음수는 음수).
3. 따라서 $\mathcal{L}(\mathbf{u},\boldsymbol{\lambda},\boldsymbol{\mu}) \le J(\mathbf{u})$, 즉 $J(\mathbf{u}) \ge \mathcal{L}(\mathbf{u},\boldsymbol{\lambda},\boldsymbol{\mu})$ 가 임의의 $\mathbf{u}$ 에 대해 성립한다.

라그랑지안은 항상 원래 목적함수보다 작거나 같으므로 **하계 역할**을 한다. 게다가 우리 QP 문제는 **볼록**이므로 다음이 성립한다.

$$\max_{\boldsymbol{\lambda},\boldsymbol{\mu}\ge 0}\ \min_{\mathbf{u}}\ \mathcal{L}(\mathbf{u},\boldsymbol{\lambda},\boldsymbol{\mu}) \;=\; J(\mathbf{u}^*) \;=\; \min_{\mathbf{u},\ \mathbf{A}\mathbf{u}=\mathbf{a},\ \mathbf{C}\mathbf{u}\le\mathbf{c}} J(\mathbf{u}) \tag{5.8}$$

말로 풀면: **가장 좋은 하계는, 라그랑지안을 쌍대 변수 $\boldsymbol{\lambda}$, $\boldsymbol{\mu}$ 에 대해 최대화하고 결정 변수 $\mathbf{u}$ 에 대해 최소화해서 얻는다.** 그리고 QP 문제에서는 **이 하계가 딱 맞아떨어져(tight) 실제 최솟값 $J(\mathbf{u}^*)$ 와 같다.**

> [!important] 쌍대성(duality)이 주는 것
> 이 등식은 **하계를 최대한 끌어올리면 정답에 도달한다**는 뜻이다. 따라서 **라그랑지안에 기반한 쌍대 최적화 문제(dual problem)** 는 $J(\mathbf{u})$ 의 최솟값과 최소점 $\mathbf{u}^*$ 를 계산하는 **또 다른 경로**가 된다. 5.6.4절의 프라이멀-듀얼 방법이 정확히 이 길을 간다.

> [!tip] 비유 — 경매의 두 쪽
> 물건의 진짜 가치를 모를 때, 사려는 사람들이 부르는 가장 높은 값(하계)과 팔려는 사람이 받아들일 가장 낮은 값(상계)이 만나는 지점이 시장 가격이다. **볼록 문제에서는 이 둘이 반드시 만난다**는 것이 (5.8)의 내용이다.

### KKT 조건 — 최적해가 반드시 만족해야 하는 네 가지

라그랑지안을 자세히 보면 **최적성의 필요조건 집합**이 나온다. 이것이 그 유명한 **카루시–쿤–터커(Karush–Kuhn–Tucker, KKT) 조건**이다([[KKT 조건]]).

**1. 정상성(Stationarity).** 최적점에서 $\mathbf{u}$ 에 대한 라그랑지안의 그래디언트가 사라져야 한다.

$$\nabla_{\mathbf{u}}\mathcal{L}(\mathbf{u}^*,\boldsymbol{\lambda}^*,\boldsymbol{\mu}^*) = \nabla J(\mathbf{u}^*) + \mathbf{A}^\mathsf{T}\boldsymbol{\lambda}^* + \mathbf{C}^\mathsf{T}\boldsymbol{\mu}^* = 0$$

기하학적 의미가 중요하다. 이 식을 옮겨 쓰면 $-\nabla J(\mathbf{u}^*) = \mathbf{A}^\mathsf{T}\boldsymbol{\lambda}^* + \mathbf{C}^\mathsf{T}\boldsymbol{\mu}^*$ 이며, 이는 **최적점에서의 최급강하 방향이 활성 제약들의 그래디언트의 가중 결합으로 주어진다**는 뜻이다.

> [!tip] 비유 — 벽에 눌린 공
> 공이 언덕을 굴러 내려가다 **벽에 부딪혀 멈췄다**고 하자. 공은 여전히 아래로 굴러가고 싶다(그래디언트가 0이 아니다). 그런데 왜 멈춰 있는가? **벽이 정확히 그만큼 밀고 있기 때문이다.** 중력의 접선 성분과 벽의 수직항력이 균형을 이룬다. 정상성 조건은 이 힘의 균형을 수식으로 쓴 것이고, $\boldsymbol{\mu}$ 는 **각 벽이 얼마나 세게 밀고 있는가**를 나타낸다.

**2. 프라이멀 실현가능성(Primal Feasibility).** 등식·부등식 제약이 만족되어야 한다. 당연한 요구다.

$$\mathbf{A}\mathbf{u}^* = \mathbf{a}, \qquad \mathbf{C}\mathbf{u}^* \le \mathbf{c}$$

**3. 듀얼 실현가능성(Dual Feasibility).** 부등식 제약에 붙은 승수는 음수가 아니어야 한다.

$$\boldsymbol{\mu}^* \ge 0$$

앞의 비유로 말하면 **벽은 밀 수만 있고 당길 수는 없다**는 뜻이다. 만약 $\mu_i$ 가 음수라면 그 제약이 공을 잡아당기고 있다는 뜻인데, 부등식 제약은 그런 일을 하지 않는다.

**4. 상보 여유성(Complementary Slackness).** 각 부등식 제약에 대해, 승수와 제약의 곱이 0이어야 한다.

$$\mu_i^*(\mathbf{C}_i\mathbf{u}^* - c_i) = 0 \qquad \forall i$$

이것이 KKT 조건 중 가장 중요하고 가장 실용적이다. 식 (5.7)과 (5.8)을 함께 보면, 최적해에서 **각 쌍대 변수와 대응하는 제약의 곱은 0이어야 한다**는 것이 분명해진다. 등식 제약에서는 이것이 자연스럽게 일어나지만($\mathbf{A}\mathbf{u}-\mathbf{a}=0$ 이므로), 부등식 제약에서는 위 조건이 별도로 요구된다.

의미를 정리하면 다음과 같다.

| 상황 | 결과 |
|---|---|
| 제약이 **활성(active)**, 즉 $\mathbf{C}_i\mathbf{u}^* = c_i$ | 대응하는 쌍대 변수 $\mu_i^*$ 는 **0이 아닐 수 있다** |
| 제약이 **비활성(inactive)**, 즉 $\mathbf{C}_i\mathbf{u}^* < c_i$ | 대응하는 쌍대 변수 $\mu_i^*$ 는 **반드시 0** |

> [!tip] 비유 다시 — 안 닿은 벽은 밀지 않는다
> 공이 벽에 **닿아 있으면** 그 벽은 힘을 줄 수 있다($\mu_i > 0$). 공이 벽에서 **떨어져 있으면** 그 벽은 아무 힘도 주지 않는다($\mu_i = 0$). 둘 중 하나는 반드시 0이라는 것 — 그것이 상보(complementary)라는 이름의 뜻이다.

이 KKT 조건들은 최적해 $\mathbf{u}^*$ 와 대응하는 라그랑주 승수 $\boldsymbol{\lambda}^*$, $\boldsymbol{\mu}^*$ 가 만족해야 하는 방정식·부등식 집합을 제공한다. **다만 이 조건들을 푸는 것은 일반적으로 반복 알고리즘을 요구하며 계산적으로 어려울 수 있다.** 그래서 5.6절의 알고리즘들이 필요하다.

### 5.5.1 선형 부등식만 있는 경우 (The Case of Linear Inequalities)

등식 제약은 (5.4.1절에서 봤듯이) 쉽게 소거할 수 있으므로, 일반성을 잃지 않고 **부등식 제약만 있는 경우**를 다룬다. 이때 KKT 조건은 다음 네 줄이 된다.

$$\nabla_{\mathbf{u}}\mathcal{L}(\mathbf{u}^*,\boldsymbol{\lambda}^*,\boldsymbol{\mu}^*) = \nabla J(\mathbf{u}^*) + \mathbf{C}^\mathsf{T}\boldsymbol{\mu}^* = 0 \tag{5.9}$$

$$\mathbf{C}\mathbf{u}^* \le \mathbf{c} \tag{5.10}$$

$$\boldsymbol{\mu}^* \ge 0 \tag{5.11}$$

$$\mu_i^*(\mathbf{C}_i\mathbf{u}^*-c_i) = 0 \quad \forall i \tag{5.12}$$

**이 식들로 활성 제약을 탐지할 수 있다.** 방법은 이렇다. 이차 목적함수의 그래디언트가 $\nabla J(\mathbf{u}^*) = \mathbf{H}\mathbf{u}^* + \mathbf{b}$ 이므로, 이를 정상성 조건에 대입하면:

$$\mathbf{H}\mathbf{u}^* + \mathbf{b} + \mathbf{C}^\mathsf{T}\boldsymbol{\mu}^* = 0$$

$\boldsymbol{\mu}^*$ 에 대해 풀면:

$$\boldsymbol{\mu}^* = -\mathbf{C}^{\mathsf{T}\dagger}(\mathbf{H}\mathbf{u}^*+\mathbf{b})$$

여기서 $\mathbf{C}^{\mathsf{T}\dagger} = (\mathbf{C}\mathbf{C}^\mathsf{T})^{-1}\mathbf{C}$ 는 **무어–펜로즈 유사역행렬**이다. $\mathbf{C}^\mathsf{T}$ 가 정사각도 아니고 가역도 아닐 수 있으므로 유사역행렬을 쓴다.

이제 상보 여유성 조건이 판정 기준을 준다.

- $\mu_i^* > 0$ 이면 $i$ 번째 제약은 **활성**이다. 즉 $\mathbf{C}_i\mathbf{u}^* = c_i$.
- $\mu_i^*$ 가 **음수**라면? 듀얼 실현가능성 조건 $\mu_i^*\ge 0$ 이 위배되므로, **활성 제약 집합을 다시 평가해야 한다**는 신호다.

> [!important] 이것이 활성 집합법의 씨앗
> 음수 승수가 나오면 그 제약을 활성 집합에서 빼라는 규칙이 바로 5.6.2절 **활성 집합법(active set method)** 의 핵심 논리다. 여기서 미리 그 원리를 본 셈이다.

---
