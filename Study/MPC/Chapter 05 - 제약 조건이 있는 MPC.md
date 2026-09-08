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

## 5.6 이차계획 문제를 어떻게 푸는가? (How to Solve Quadratic Programs?)

### 공통 뼈대 — 반복법과 출발점 찾기

QP의 해는 **초기 실현가능점 $\mathbf{u}^0$ 에서 시작해 반복적으로** 찾는다. 반복열 $\{\mathbf{u}^l\}_{l=0,1,2,\ldots}$ 이 $J(\mathbf{u})$ 의 최소점, 즉 제약을 만족하는 모든 $\mathbf{u}$ 에 대해 $J(\mathbf{u}^*)\le J(\mathbf{u})$ 인 $\mathbf{u}^*$ 로 수렴하도록 만드는 것이다.

**그런데 출발점은 어떻게 구하는가?** 실현가능한 점은 $\mathbf{r} = \mathbf{R}\mathbf{u}^0 - \mathbf{c} < 0$ 을 만족해야 한다. 책은 먼저 간단한 후보 세 가지를 시험해 보라고 한다.

1. **제어 신호를 그대로 유지한다.** 즉 $u(k+j) = u(k-1)$. 아무것도 바꾸지 않는 시나리오다.
2. **직전의 최적 시퀀스를 한 칸 밀고 마지막에 0을 붙인다.** 만약 직전 시퀀스가
   $$\mathbf{u}^{k-1} = [\Delta u(k-1),\ \Delta u(k),\ \ldots,\ \Delta u(k+n-2),\ \Delta u(k+n-1)]$$
   였다면, 이번 출발점은
   $$\mathbf{u}^{0} = [\Delta u(k),\ \Delta u(k+1),\ \ldots,\ \Delta u(k+n-1),\ 0]$$
   이다. 이 아이디어는 5.8절의 **재귀적 실현가능성** 증명에서 그대로 다시 등장한다 — "꼬리(tail)를 이어 붙이기"가 MPC 이론의 핵심 트릭이기 때문이다.
3. **제약 없는 해를 계산한 뒤 입력 제약에 맞게 잘라낸다.** 즉 5.2절의 clipping을 출발점 생성기로만 쓰는 것이다.

> [!warning] 이 출발점들이 나쁠 수 있는 경우
> 책이 명시적으로 경고한다. 시각 $k$ 에서 **기준값이 바뀌었거나**, **출력 제약처럼 더 복잡한 제약이 있는 경우**에는 위 출발점들이 좋지 않을 수 있다. 그럴 때는 아래의 일반적인 절차가 필요하다.

**일반적인 초기해 탐색 — LP로 실현가능성 자체를 푼다.** 다음 선형계획 문제를 푼다.

$$\min_{\mathbf{u}'} J'(\mathbf{u}') = \min_{\mathbf{u}'}[0\ \ 0\ \cdots\ 0\ \ 1]\,\mathbf{u}'$$

제약은 $\mathbf{R}'\mathbf{u}' \le \mathbf{c}$ 이며, 다음과 같이 정의한다.

$$\mathbf{u}' = \begin{bmatrix}\mathbf{u} \\ z\end{bmatrix}, \qquad \mathbf{R}' = [\mathbf{R}\ \ -\mathbf{1}], \qquad \text{출발점 } \mathbf{u}' = \begin{bmatrix}\mathbf{u}^0 \\ r_{\max}\end{bmatrix}$$

**이 트릭의 아름다움을 보자.** 변수 $z$ 를 하나 추가하고 모든 제약을 $\mathbf{R}\mathbf{u} - \mathbf{1}z \le \mathbf{c}$ 로 느슨하게 만들었다. $z$ 를 충분히 크게 잡으면 **어떤 $\mathbf{u}$ 든 이 제약을 만족한다.** 그래서 **이 확대된 문제는 여유 변수(slack variable) $z$ 덕분에 항상 실현가능하다.** 그리고 목적함수는 오직 $z$ 하나만 최소화한다 — "제약 위반량을 최대한 줄여라"는 뜻이다.

판정도 간단하다.

- $J'(\mathbf{u}') \le 0$, 즉 $z \le 0$ 이면 **원래 문제의 실현가능해를 찾은 것**이다(제약을 느슨하게 할 필요가 없었다는 뜻이므로).
- 그렇지 않으면 **원래 문제는 실현불가능(unfeasible)** 하다.

> [!tip] 비유 — 옷이 맞는지 확인하는 법
> 옷이 몸에 맞는지 알고 싶다. 억지로 입어 보는 대신, **"몇 센티미터를 늘려야 입을 수 있는가"** 를 최소화한다. 답이 0 이하면 옷은 이미 맞는다. 답이 양수면 그만큼 부족하다는 뜻이다. $z$ 가 바로 그 "늘려야 하는 양"이다.

이 지점부터 알고리즘들이 갈라진다. 최적화 솔버에서 흔히 쓰이는 방법들을 차례로 보자.

### 5.6.1 실현가능 방향법 (Feasible Direction Methods)

**핵심 아이디어**: 실현가능한 점에서 출발해 **더 나은 실현가능한 점으로 옮겨 가기를 반복**하여 최적점에 도달한다. 즉 항상 울타리 안에 머물면서 아래로 내려간다.

실현가능점 $\mathbf{u}^k$ 가 주어지면, 개선 방향 $\mathbf{d}_k$ 를 찾아 충분히 작은 걸음을 내딛는다.

$$\mathbf{u}^{k+1} = \mathbf{u}^k + \lambda_k\mathbf{d}$$

이 새로운 점은 실현가능하면서 목적함수 $J(\mathbf{u})$ 의 값이 더 작아야 한다.

**방향 $\mathbf{d}$ 가 만족해야 할 두 조건.** 활성·비활성 부등식 제약 집합을 각각 $\mathbf{A}_1\mathbf{u}^k = \mathbf{a}_1$, $\mathbf{A}_2\mathbf{u}^k < \mathbf{a}_2$ 라 하자.

| 조건 | 수식 | 의미 |
|---|---|---|
| 실현가능성 유지 | $\mathbf{A}_1\mathbf{d} \le 0$ | 이미 벽에 닿아 있으니 벽 쪽으로 더 가면 안 된다 |
| 최적성 개선 | $\nabla J(\mathbf{u})^\mathsf{T}\mathbf{d} < 0$ | 그래디언트와 예각이 아니어야, 즉 내려가는 방향이어야 한다 |

이를 위해 **$-\nabla J(\mathbf{u}^k) = -(\mathbf{H}\mathbf{u}^k + \mathbf{b})$ 에 가장 가까운 실현가능 방향 $\mathbf{d}$** 를 찾는다. $-\nabla J$ 는 $J(\mathbf{u})$ 의 **최급강하 방향(steepest descent)** 이다(각주가 상기시키듯 $J(\mathbf{u})$ 는 구성상 미분가능하고 볼록하다). 그런 방향은 다음 최적화 문제를 풀어 얻는다.

$$\min_{\mathbf{d}}\ (\mathbf{d} + \nabla J(\mathbf{u}))^\mathsf{T}(\mathbf{d} + \nabla J(\mathbf{u}))$$

제약은 활성 제약 $\mathbf{A}_1\mathbf{u}^k = \mathbf{a}_1$ 이다. 목적함수를 보면 **"$\mathbf{d}$ 를 $-\nabla J$ 에 최대한 가깝게"** 라는 뜻임이 분명하다(두 벡터 차이의 제곱 노름을 최소화하니까). 그리고 이런 종류의 이차 계획은 **앞서 배운 등식 제약 소거법으로 무제약 최적화로 바꿔 풀 수 있다.** 5.4.1절이 여기서 쓰인다.

**걸음 크기 $\lambda^*$ 는 정확히 계산할 수 있다.** $J(\mathbf{u}^k + \lambda\mathbf{d})$ 가 $\lambda$ 에 대한 이차 함수이기 때문이다. 전개하면:

$$\begin{aligned} J(\mathbf{u}^k+\lambda\mathbf{d}) &= \tfrac{1}{2}(\mathbf{u}^k+\lambda\mathbf{d})^\mathsf{T}\mathbf{H}(\mathbf{u}^k+\lambda\mathbf{d}) + \mathbf{b}^\mathsf{T}(\mathbf{u}^k+\lambda\mathbf{d}) + \mathbf{f}_0 \\ &= \tfrac{1}{2}\mathbf{d}^\mathsf{T}\mathbf{H}\mathbf{d}\,\lambda^2 + (\mathbf{d}^\mathsf{T}\mathbf{H}\mathbf{u}^k + \mathbf{b}^\mathsf{T}\mathbf{d})\lambda + J(\mathbf{u}^k)\end{aligned}$$

$\lambda$ 에 대한 위로 볼록한 포물선이므로, $\lambda$ 로 미분해 0으로 놓으면 최적 걸음이 나온다.

$$\lambda^* = -\frac{\mathbf{d}^\mathsf{T}\mathbf{H}\mathbf{u}^k + \mathbf{b}^\mathsf{T}\mathbf{d}}{\mathbf{d}^\mathsf{T}\mathbf{H}\mathbf{d}} \tag{5.13}$$

**그런데 이대로 가면 안 된다.** 비활성 제약들이 $\lambda$ 의 최댓값에 한계를 두기 때문이다. $\mathbf{A}_2(\mathbf{u}^k+\lambda\mathbf{d}) \le \mathbf{a}_2$ 를 보장해야 하므로 실제 걸음 크기는 다음과 같이 계산한다.

$$\lambda_k = \min\!\left(\lambda^*,\ \frac{c_1 - \mathbf{a}_1^\mathsf{T}\mathbf{u}^k}{\mathbf{a}_1^\mathsf{T}\mathbf{d}},\ \frac{c_2 - \mathbf{a}_2^\mathsf{T}\mathbf{u}^k}{\mathbf{a}_2^\mathsf{T}\mathbf{d}},\ \ldots\right)$$

여기서 $\mathbf{a}_j^\mathsf{T}$ 와 $c_j$ 는 비활성 제약 집합의 행과 그 한계값이며, $\mathbf{a}_j^\mathsf{T}\mathbf{d} > 0$ 인 것들만 고려한다.

> [!question] 왜 $\mathbf{a}_j^\mathsf{T}\mathbf{d} > 0$ 인 것만 보는가?
> $\mathbf{a}_j^\mathsf{T}\mathbf{d} > 0$ 이라는 것은 **그 방향으로 가면 $j$ 번째 제약에 가까워진다**는 뜻이다. 반대로 $\mathbf{a}_j^\mathsf{T}\mathbf{d} \le 0$ 이면 그 제약에서 멀어지므로 아무리 멀리 가도 위반할 일이 없다. 즉 **부딪힐 가능성이 있는 벽까지의 거리만 재면 된다.**

> [!tip] 비유 — 방 안에서 걷기
> 방 안에서 목표 지점을 향해 걷는다. 이상적인 걸음은 목표까지의 거리($\lambda^*$)지만, 도중에 **가구에 부딪히면 거기서 멈춰야 한다.** 그래서 실제 걸음은 "목표까지의 거리"와 "가장 먼저 만나는 가구까지의 거리" 중 **더 짧은 쪽**이다. 그것이 $\min$ 의 의미다.

**종료 조건.** 걸음 크기 $\lambda_k$ 가 0에 가까워지면 알고리즘이 종료된다. 목적함수를 개선할 실현가능한 걸음이 더 이상 없다는 뜻이기 때문이다. 이 시점에서 모든 활성·비활성 제약이 만족되고 그래디언트 방향이 더 이상 실현가능한 개선을 제공하지 않는다면, 현재 해를 최적으로 간주한다.

> [!example] 예제 5.4 — 로젠의 그래디언트 사영법 (Rosen's Gradient Projection Method)
> **로젠의 그래디언트 사영법**은 5.4.1절에서 본 무어–펜로즈 사영 행렬 $\mathbf{P}$ 에 기반한 실현가능 방향법이다. 실현가능점 $\mathbf{u}^k$ 가 주어지면, 제약 없는 최대 감소 방향을 실현가능 공간으로 사영한 것이 방향이 된다.
> $$\mathbf{d} = -\mathbf{P}\nabla J(\mathbf{u}^k)$$
> $\mathbf{d}$ 가 0이 아니면, 그것은 $\mathbf{u}^k$ 에서 $J$ 를 개선하는 방향이다. 알고리즘은 다음과 같이 요약된다.
>
> 1. 활성 제약 집합이 **비어 있으면** $\mathbf{P} = \mathbf{I}$ 로 둔다. 그렇지 않으면 $\mathbf{P} = \mathbf{I} - \mathbf{A}_1^\mathsf{T}(\mathbf{A}_1\mathbf{A}_1^\mathsf{T})^{-1}\mathbf{A}_1$.
> 2. $\mathbf{d}_k = -\mathbf{P}(\mathbf{H}\mathbf{u}^k + \mathbf{b})$ 로 둔다.
> 3. 만약 $\mathbf{d}_k = 0$ 이면 **최적성 검사**를 수행한다.
>    - **3.1** 활성 제약 집합이 비어 있지 않으면, 라그랑주 승수 벡터 $\boldsymbol{\mu} = -(\mathbf{A}_1\mathbf{A}_1^\mathsf{T})^{-1}\mathbf{A}_1(\mathbf{H}\mathbf{u}^k+\mathbf{b})$ 를 계산해, **음수 성분($\mu_j < 0$)에 대응하는 제약을 활성 집합에서 차례로 제거**한다(즉 $\mathbf{A}_1$ 에서 $j$ 행을 지운다). 1단계로 간다.
>    - **3.2** 활성 제약 집합이 비어 있거나 $\boldsymbol{\mu} > 0$ 이면 **정지**한다.
> 4. $\lambda_k$ 와 $\mathbf{u}^{k+1} = \mathbf{u}^k + \lambda_k\mathbf{d}_k$ 를 계산한다. $k$ 를 $k+1$ 로 바꾸고 1단계로 간다.
>
> **3.1단계가 KKT 조건의 실제 사용법이다.** 방향이 0이라는 것은 "더 갈 곳이 없다"는 뜻인데, 그것이 정말 최적이어서인지 아니면 **불필요한 벽에 갇혀서인지** 구별해야 한다. 음수 승수는 "이 벽은 사실 나를 막을 필요가 없다"는 신호이므로 그 벽을 놓아 주는 것이다.

### 5.6.2 활성 집합법 (The Active Set Method)

**핵심 아이디어**: 부등식 제약 QP 문제를 **등식 제약 QP 문제들의 수열**로 환원한다. 등식 제약 문제는 5.4.1절에서 봤듯이 선형 방정식 한 번으로 풀리므로, 이 환원은 큰 이득이다.

절차의 뼈대는 이렇다. 임의의 실현가능점 $\mathbf{u}^k$ 는 $\mathbf{R}\mathbf{u}^k \le \mathbf{c}$ 를 만족하며, 그중 **등식으로 정확히 만족되는 부등식들**, 즉 $\mathbf{r}_i\mathbf{u} = c_i$ 인 $\mathbf{R}$ 의 행 $\mathbf{r}_i$ 들이 **활성 제약 집합**을 이룬다. 이 행들과 대응하는 한계값 $c_i$ 를 쌓으면 등식 제약 $\mathbf{A} = \mathbf{a}$ 가 만들어진다. 이제 5.4.1절의 방법으로 풀어 해 $\mathbf{u}^{k+1}$ 을 얻는다.

$\mathbf{u}^{k+1}$ 이 **비활성 제약들에 대해 실현가능한지**에 따라 두 갈래로 나뉜다.

**갈래 1 — $\mathbf{u}^{k+1}$ 이 실현가능한 경우.** 전역 최적을 찾았는지 확인하는 최적성 검사를 한다. **모든 등식 제약의 라그랑주 승수가 $\lambda_i \ge 0$ 인지** 검증하면 된다. 그렇지 않다면, **가장 음수인 라그랑주 승수를 갖는 제약을 활성 집합에서 떨어뜨리고(drop)** 과정을 반복한다.

**갈래 2 — $\mathbf{u}^{k+1}$ 이 실현불가능한 경우.** $\mathbf{u}^k$ 와 $\mathbf{u}^{k+1}$ 을 잇는 선분이 비활성 제약들과 만나는 교점 중 **$\mathbf{u}^k$ 에서 가장 가까운 것**을 계산한다. 대응하는 제약을 활성 집합에 **추가하고**, 앞의 단계들을 반복한다.

> [!tip] 비유 — 벽을 짚어 가며 걷기
> 어두운 방에서 목표 지점으로 가려 한다. 일단 **아무 벽도 없다고 가정하고** 직진한다. 벽에 부딪히면 "이 벽은 지금 나를 막고 있다"고 기록하고(활성 집합에 추가), **벽을 따라 미끄러지며** 다시 최적점을 계산한다. 가다 보니 "아, 이 벽은 이제 나를 안 막네" 싶으면 기록에서 지운다(활성 집합에서 제거). 이 추가·제거를 반복하다 **더 이상 바뀌지 않으면** 도착이다.

> [!important] 왜 이 방법이 잘 작동하는가
> **활성 집합만 알면 문제가 끝나기 때문이다.** 5.5.1절에서 봤듯 최적해에서 비활성 제약은 승수가 0이라 아무 영향이 없다. 즉 **QP를 푸는 일은 본질적으로 "어느 제약이 활성인지 알아맞히는 일"** 이다. 활성 집합법은 그 답을 시행착오로 찾아 나가는 정직한 접근이다. 이것이 [[조각별 아핀 PWA와 명시적 MPC]]에서 상태 공간이 조각으로 나뉘는 이유와 정확히 같은 사실이다 — 조각 하나가 활성 집합 하나에 대응한다.

### 5.6.3 내점법 (Interior Point Methods)

**핵심 아이디어**: 부등식 제약을 **목적함수 안으로 집어넣는다.** 실현가능 영역의 경계 밖으로 나가려는 시도에 **벌점(penalty)** 을 매기는 **장벽(barrier)** 을 만들어 제약 위반을 막는 것이다.

**로그 장벽(logarithmic barrier)** 을 쓰면 수정된 목적함수는 다음과 같다.

$$J_\mu(\mathbf{u}) = \tfrac{1}{2}\mathbf{u}^\mathsf{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathsf{T}\mathbf{u} + \sum_{i=1}^{m}-\mu\log(\mathbf{c}_i - \mathbf{C}_i\mathbf{u})$$

$\mu > 0$ 은 **장벽 파라미터**로 벌점의 세기를 조절한다.

> [!important] 로그 장벽이 왜 효과적인가
> $\mathbf{c}_i - \mathbf{C}_i\mathbf{u}$ 는 **$i$ 번째 제약까지 남은 여유**다. 이 값이 0에 가까워지면(즉 경계에 붙으면) $\log$ 의 값이 $-\infty$ 로 발산하고, 앞에 마이너스가 붙었으므로 **벌점이 $+\infty$ 로 폭발한다.** 최소화하는 입장에서는 절대 가고 싶지 않은 곳이 된다. 즉 **경계는 무한히 높은 벽**이 되어, 반복점이 영역 **내부(interior)** 에만 머물게 된다. "내점법"이라는 이름이 여기서 나왔다.

그리고 결정적으로, **$\mu$ 가 작아질수록 $J_\mu(\mathbf{u})$ 의 해는 원래 문제의 해로 수렴한다.** 장벽을 점점 얇게 만들어 진짜 답에 다가가는 것이다.

**알고리즘.** 엄격히 실현가능한 초기점 $\mathbf{u}^k$($\mathbf{C}\mathbf{u}^k < \mathbf{c}$)에서 시작해 다음을 반복한다.

**1. 뉴턴 스텝(Newton Step).** 실현가능 영역 내부에 머물면서 목적함수를 줄이는 방향과 걸음 크기를 찾는다. 선형 시스템 하나를 풀면 된다.

- **(a) 테일러 급수 전개.** 장벽이 더해진 목적함수 $J_\mu(\mathbf{u})$ 를 $\mathbf{u}^k$ 에서 **2차 테일러 급수**로 근사한다.
  $$J_\mu(\mathbf{u}) \approx J_\mu(\mathbf{u}^k) + \nabla J_\mu(\mathbf{u}^k)^\mathsf{T}(\Delta\mathbf{u}) + \tfrac{1}{2}(\Delta\mathbf{u})^\mathsf{T}\nabla^2 J_\mu(\mathbf{u}^k)(\Delta\mathbf{u})$$
  여기서 $\Delta\mathbf{u} = \mathbf{u} - \mathbf{u}^k$ 는 현재 점에서의 이동량이다.
- **(b) 1차 최적성 조건.** 목적함수를 최소화하는 $\Delta\mathbf{u}$ 를 찾으려면 이 이차 근사의 그래디언트가 $\Delta\mathbf{u}$ 에 대해 사라져야 한다. 그러면 $\Delta\mathbf{u}$ 를 미지수로 하는 **뉴턴 선형 방정식계**가 나온다.
  $$\nabla^2 J_\mu(\mathbf{u}^k)\,\Delta\mathbf{u} = -\nabla J_\mu(\mathbf{u}^k)$$
- **(c) 프라이멀 갱신.** 이 방정식을 풀면 **뉴턴 방향** $\Delta\mathbf{u}$ 가 나오고, 프라이멀 변수를 갱신한다.
  $$\mathbf{u}^{k+1} = \mathbf{u}^k + \alpha_k\Delta\mathbf{u}$$
  $\alpha_k$ 는 걸음 크기이며, 갱신된 점이 **여전히 실현가능 영역 내부에 엄격히 머물도록**($\mathbf{C}\mathbf{u}^{k+1} < \mathbf{c}$) 보장해야 한다. 이것이 내점 조건의 유지다.

**2. 장벽 파라미터 갱신.** 매 반복 후 $\mu$ 를 미리 정한 스케줄에 따라 줄인다. 예를 들어 $\mu_{k+1} = \tau\mu_k$ 이고 $\tau < 1$ 이다. 이렇게 장벽 효과를 점차 완화하면 반복점들이 최적해로 수렴하면서 실현가능 영역의 경계에 가까이 갈 수 있게 된다.

**3. 수렴 검사.** KKT 조건의 잔차(residual)가 특정 임계값 아래로 떨어지거나, 장벽 파라미터 $\mu$ 가 충분히 작아지면 최적해 $\mathbf{u}^*$ 를 찾은 것으로 보고 종료한다. 수렴하지 않았으면 $k = k+1$ 로 하고 1단계로 돌아간다.

> [!note] 내점법이 MPC에 갖는 장점
> 책이 세 가지를 든다. **다항 시간 복잡도(polynomial time complexity)** 를 가지며, **대규모 최적화 문제를 효율적으로** 풀 수 있고, 대개 다른 방법보다 **반복 횟수가 적다.** 특히 부등식을 장벽 함수로 직접 처리하므로 계산 오버헤드가 줄어든다. 활성 집합법이 "어느 벽에 닿았나"를 조합적으로 탐색하는 데 반해, 내점법은 그 조합 탐색을 아예 하지 않는다는 점이 규모가 커질수록 유리하다.

> [!example] 예제 5.5 — 내점법으로 QP 풀기
> 다음 이차계획 문제를 생각한다.
> $$\mathbf{H} = \begin{bmatrix}1 & 0 \\ 0 & 1\end{bmatrix}, \quad \mathbf{b} = \begin{bmatrix}-1 \\ -2\end{bmatrix}, \quad \mathbf{C} = \begin{bmatrix}1 & 0 \\ 0 & 1 \\ -1 & 0 \\ 0 & -1\end{bmatrix}, \quad \mathbf{c} = \begin{bmatrix}1.5 \\ 1.5 \\ 1.5 \\ 1.5\end{bmatrix}$$
> 읽어 보면 이렇다. $\mathbf{H}$ 가 단위행렬이므로 목적함수는 $\tfrac{1}{2}(u_1^2+u_2^2) - u_1 - 2u_2$ 이고, 제약 없는 최소점은 $\mathbf{H}\mathbf{u} = -\mathbf{b}$ 에서 $(1, 2)$ 다. 제약은 $-1.5 \le u_1 \le 1.5$, $-1.5 \le u_2 \le 1.5$ 인 **정사각형 상자**다. 그러므로 제약 없는 최적점 $(1,2)$ 는 **상자 밖**이고, 진짜 답은 $u_2$ 가 상한에 눌린 곳 근처가 된다.

![[mpc_fig_5_6.png]]
*그림 5.6 — 장벽 파라미터 $\mu$ 의 값에 따른 이차 목적함수의 등고선과 최적화 경로*

> [!example] 그림이 말하는 것
> 각 부분 그림에서 이차 목적함수의 **등고선은 점선**, 부등식 제약이 정의하는 실현가능 영역은 **실선**, 최적점은 **검은 사각형**으로 표시되어 있다. 관찰할 것은 이것이다. **$\mu$ 가 클 때 최적점은 실현가능 영역의 경계에서 멀리 떨어져 있다.** 장벽이 제약 근처의 해에 큰 벌점을 매기기 때문이다. **$\mu$ 가 작아지면 최적점이 경계에 점점 가까워지고**, 결국 원래 문제의 해로 수렴한다. 오른쪽 아래 부분 그림의 **점선이 이 예제에서 최적화기가 따라간 경로**다. 이 경로를 최적화 문헌에서는 **중심 경로(central path)** 라고 부른다.

### 5.6.4 프라이멀-듀얼 방법 (The Primal-Dual Method)

**핵심 아이디어**: KKT 조건을 최적성 판정용으로 쓰는 대신, **프라이멀 변수 $\mathbf{u}$ 와 듀얼 변수 $\boldsymbol{\mu}$ 를 동시에 갱신하는 규칙**으로 삼는다. 초기 실현가능점 $\mathbf{u}^k$, $\boldsymbol{\mu}^k \ge 0$ 에서 시작한다.

**1. 프라이멀 갱신.** 정상성 조건은 최적점에서 프라이멀 변수에 대한 라그랑지안의 그래디언트가 사라져야 한다고 말한다. 이를 갱신 규칙으로 쓰면 다음 선형 시스템이 된다.

$$\mathbf{H}\mathbf{u}_{k+1} = -\mathbf{b} - \mathbf{C}^\mathsf{T}\boldsymbol{\mu}_k$$

즉 **현재의 승수 추정치를 고정한 채 $\mathbf{u}$ 를 최적화**한다.

**2. 듀얼 갱신.** 듀얼 변수는 **라그랑지안이 최대로 증가하는 방향으로 그래디언트 스텝**을 밟아 갱신한다.

$$\boldsymbol{\mu}_{k+1} = \max\!\big(0,\ \boldsymbol{\mu}_k + \alpha_k(\mathbf{C}\mathbf{u}_{k+1}-\mathbf{c})\big)$$

$\alpha_k$ 는 선 탐색(line search)으로 정하거나 고정하는 걸음 크기 파라미터다.

> [!tip] 이 식을 읽는 법
> $\mathbf{C}\mathbf{u}_{k+1} - \mathbf{c}$ 는 **제약 위반량**이다. 양수면 위반이고 음수면 여유가 있다. 그러므로 이 갱신은 **"위반한 제약의 승수는 키우고, 여유 있는 제약의 승수는 줄여라"** 는 뜻이다. 바깥의 $\max(0,\cdot)$ 은 듀얼 실현가능성 $\boldsymbol{\mu}\ge 0$ 을 강제로 지키는 장치다.
>
> 비유하면 **가격 조정**이다. 물건이 모자라면(제약 위반) 값을 올려 수요를 줄이고, 남으면 값을 내린다. 다만 값은 음수가 될 수 없다. 이 시장 균형 과정이 곧 최적해로 수렴한다.

**3. 수렴 검사.** 세 가지를 확인한다.

| 검사 항목 | 조건 |
|---|---|
| 프라이멀 실현가능성 | $\mathbf{C}\mathbf{u}_{k+1}\le\mathbf{c}$ |
| 듀얼 실현가능성 | $\boldsymbol{\mu}_{k+1}\ge 0$ |
| 상보 여유성 | $\boldsymbol{\mu}_{k+1}^\mathsf{T}(\mathbf{C}\mathbf{u}_{k+1}-\mathbf{c}) \approx 0$ |

조건이 충족되지 않으면 $k = k+1$ 로 하고 1단계로 돌아간다. 프라이멀·듀얼 변수가 수렴 기준을 만족하면 최적해 $\mathbf{u}^*$ 와 $\boldsymbol{\mu}^*$ 를 찾은 것이다.

> [!note] 이 방법의 장점
> 책이 두 가지를 든다. 첫째, **듀얼 변수가 제약의 빡빡함(tightness)에 대한 피드백을 제공한다.** $\mu_i$ 가 크다는 것은 그 제약이 성능을 크게 제한하고 있다는 뜻이므로, **어느 제약을 완화하면 이득이 큰지** 알려 주는 진단 정보가 된다. 둘째, 프라이멀-듀얼 방법은 다른 알고리즘보다 **수렴 특성이 우수한 경우가 많다.**

### 5.6.5 피벗팅 방법 (Pivoting Methods)

**심플렉스(Simplex)** 같은 피벗팅 방법은 구현이 간단해서 선형계획에서 널리 쓰여 왔다. 또한 **유한한 단계 안에** 최적해를 찾거나 실현가능해가 없음을 알려 준다는 장점이 있다.

선형 제약이 있는 MPC 문제의 최소화도 피벗팅 방법으로 풀 수 있다. 방법은 QP를 **선형 상보 문제(linear complementary problem, LCP)** 로 환원하는 것이다. $\mathbf{u} = \mathbf{l}\,\underline{u} + \mathbf{x}$ 로 두면 식 (5.1)은 다음과 같이 다시 쓸 수 있다.

$$J = \tfrac{1}{2}\mathbf{x}^\mathsf{T}\mathbf{H}\mathbf{x} + \mathbf{a}\mathbf{x} + \mathbf{f}_1 \tag{5.15}$$

여기서 $\mathbf{a} = \mathbf{b} + \underline{u}\,\mathbf{l}^\mathsf{T}\mathbf{H}$, $\mathbf{f}_1 = \mathbf{f}_0 + \underline{u}^2\mathbf{l}^\mathsf{T}\mathbf{H}\mathbf{l} + \mathbf{b}\,\underline{u}$ 이다. 제약은 압축된 형태로 다음과 같다.

$$\mathbf{x} \ge 0, \qquad R\,\mathbf{x} \le \mathbf{c} \tag{5.16}$$

$$R = \begin{bmatrix}I_{N\times N} \\ T \\ -T \\ \mathbf{G} \\ -\mathbf{G}\end{bmatrix}, \qquad \mathbf{c} = \begin{bmatrix}\mathbf{l}(\overline{u}-\underline{u}) \\ \mathbf{l}\,\overline{u} - T\mathbf{l}\,\underline{u} - u(t-1)\mathbf{l} \\ -\mathbf{l}\,\underline{u} + T\mathbf{l}\,\underline{u} + u(t-1)\mathbf{l} \\ \mathbf{l}\,\overline{y} - \mathbf{f} - \mathbf{G}\mathbf{l}\,\underline{u} \\ -\mathbf{l}\,\underline{y}+\mathbf{f}+\mathbf{G}\mathbf{l}\,\underline{u}\end{bmatrix} \tag{5.17}$$

**변수 이동의 목적을 짚자.** $\mathbf{x} \ge 0$ 이라는 형태를 만들기 위해서다. 심플렉스류 알고리즘은 "모든 변수가 음이 아닌" 표준형을 요구하므로, 하한 $\underline{u}$ 만큼 원점을 옮겨 그 형태를 맞춘 것이다.

이제 $\mathbf{x}\ge 0$ 과 $R\mathbf{x}\le\mathbf{c}$ 의 라그랑주 승수 벡터를 각각 $\mathbf{v}$, $\mathbf{v}_1$ 로, 여유 변수 벡터를 $\mathbf{v}_2$ 로 표기하면 KKT 조건은 다음과 같이 쓸 수 있다.

$$\begin{aligned} R\mathbf{x} + \mathbf{v}_2 &= \mathbf{c} \\ -\mathbf{H}\mathbf{x} - R^\mathsf{T}\mathbf{v} + \mathbf{v}_1 &= \mathbf{a} \\ \mathbf{x}^\mathsf{T}\mathbf{v}_1 = 0, \quad \mathbf{v}^\mathsf{T}\mathbf{v}_2 &= 0 \\ \mathbf{x}, \mathbf{v}, \mathbf{v}_1, \mathbf{v}_2 &\ge 0\end{aligned} \tag{5.18}$$

셋째 줄이 바로 상보 여유성이다. 이 표현들은 **선형 상보 문제** $\mathbf{s} - \mathbf{M}\mathbf{z} = \mathbf{q}$, $\mathbf{s}^\mathsf{T}\mathbf{z} = 0$, $\mathbf{s},\mathbf{z}\ge 0$ 의 형태로 정리된다.

$$\mathbf{M} = \begin{bmatrix}\mathbf{0} & -R \\ R^\mathsf{T} & \mathbf{H}\end{bmatrix}, \quad \mathbf{q} = \begin{bmatrix}\mathbf{c} \\ \mathbf{a}\end{bmatrix}, \quad \mathbf{s} = \begin{bmatrix}\mathbf{v}_2 \\ \mathbf{v}_1\end{bmatrix}, \quad \mathbf{z} = \begin{bmatrix}\mathbf{v} \\ \mathbf{x}\end{bmatrix} \tag{5.19}$$

> [!note] 선형 상보 문제(LCP)란 무엇인가 — 책의 각주 8
> $\mathbf{q}$ 와 $\mathbf{M}$ 이 각각 $m$ 벡터와 $m\times m$ 행렬로 주어졌을 때, LCP는 다음을 만족하는 두 $m$ 벡터 $\mathbf{s}$, $\mathbf{z}$ 를 찾는 문제다.
> $$\mathbf{s} - \mathbf{M}\mathbf{z} = \mathbf{q}, \qquad \mathbf{s},\mathbf{z}\ge 0, \qquad \langle\mathbf{s},\mathbf{z}\rangle = 0 \tag{5.14}$$
> 이 시스템의 해 $(\mathbf{s},\mathbf{z})$ 는 각 상보 변수 쌍 $(s_i, z_i)$ 중 하나가 기저(basic) 변수일 때 **상보 기저 실현가능해**라 불린다. **$\mathbf{q}$ 가 음이 아니면** $\mathbf{s}=\mathbf{q}$, $\mathbf{z}=\mathbf{0}$ 으로 두어 상보 실현가능 기저해를 즉시 찾을 수 있다.

이 문제는 **렘키 알고리즘(Lemke's algorithm)** 으로 풀 수 있다.

> [!note] 렘키 알고리즘 — 책의 각주 9
> $\mathbf{q}$ 가 음일 때 쓴다. **인공 변수 $z_0$** 를 도입해 다음 형태로 바꾼다.
> $$\mathbf{s}-\mathbf{M}\mathbf{z}-\mathbf{l}z_0 = \mathbf{q}, \qquad \mathbf{s},\mathbf{z},z_0\ge 0, \qquad \langle\mathbf{s},\mathbf{z}\rangle=0 \tag{5.20}$$
> 시작해는 $z_0 = \max(-q_i)$, $\mathbf{z}=0$, $\mathbf{s}=\mathbf{q}+\mathbf{l}z_0$ 으로 얻는다. 시스템과 양립하는 피벗팅 수열을 거쳐 **인공 변수 $z_0$ 를 0으로 몰아넣을 수 있으면** LCP의 해를 얻은 것이다.
>
> 렘키 알고리즘의 다른 장점들도 책이 열거한다. 파라미터 $z_0$ 가 0으로 가는 과정에서 **해를 추적할 수 있고**, **퇴화(degeneracy)를 해결하는 특별한 기법이 필요 없으며**, QP에서 생성된 LCP에 적용할 때 **QP의 제약 없는 해를 시작점으로 쓸 수 있다.**

> [!warning] 계산 비용
> 행렬 $\mathbf{H}$ 가 양정치이므로 알고리즘은 **유한한 단계 안에 최적해로 수렴**한다. **그러나 상당한 계산량이 필요하다.** 효율은 더 나은 시작점을 찾아 높일 수 있는데, 다행히 대부분의 경우 **MPC 문제의 제약 없는 해에서 출발하면 위반되는 제약이 몇 개 안 되므로** 필요한 반복 횟수가 줄어든다.

---

## 5.7 1-노름 목적함수를 쓰는 선형계획법 (Linear Programming with a 1-Norm Objective)

### 왜 제곱 대신 절댓값인가?

이차계획 알고리즘은 매우 효율적이다. **그러나 목적함수를 1-노름 형태로 쓰면 훨씬 더 효율적인 선형계획법으로 MPC 문제를 풀 수 있다.**

$$J(\mathbf{u}) = \sum_{j=N_1}^{N_2}\sum_{i=1}^{n}|y_i(t+j)-r_i(t+j)| + \lambda\sum_{j=1}^{N_u}\sum_{i=1}^{m}|\Delta u_i(t+j-1)| \tag{5.21}$$

$N_1$ 과 $N_2$ 는 비용 지평을, $N_u$ 는 제어 지평을 정의한다. MPC에서 통상 쓰는 것처럼 제곱을 취하는 대신 **출력 추종 오차의 절댓값과 제어 증분의 절댓값**을 취한 것이 차이의 전부다([[가중 노름과 대각 가중행렬]]).

> [!tip] 비유 — 벌금 매기는 방식
> 제곱(2-노름)은 **"크게 틀리면 훨씬 더 크게 벌준다"** 이다. 오차 2는 오차 1보다 4배 나쁘다. 절댓값(1-노름)은 **"틀린 만큼만 벌준다"** 이다. 오차 2는 오차 1보다 2배 나쁠 뿐이다. 실무적 결과는 이렇다. 1-노름은 큰 오차 하나에 덜 예민하고, 목적함수가 **선형**이 되어 LP로 풀린다.

### 절댓값을 선형으로 바꾸는 트릭

절댓값은 그 자체로 선형이 아니다. 그런데 **보조 변수와 부등식 두 개**로 감싸면 선형이 된다. $\mu_i \ge 0$ 과 $\beta_i \ge 0$ 을 도입해 다음을 요구한다.

$$-\mu_i \le y_i(t+j)-r_i(t+j) \le \mu_i \qquad i=1,\ldots,n,\ \ j=1,\ldots,N$$
$$-\beta_i \le \Delta u_i(t+j-1) \le \beta_i \qquad i=1,\ldots,m,\ \ j=1,\ldots,N_u$$
$$0 \le \sum_{i=1}^{n\times N}\mu_i + \lambda\sum_{i=1}^{m\times N_u}\beta_i \le \gamma$$

그러면 $\gamma$ 는 $J(\mathbf{u})$ 의 **상계**가 된다. **문제는 이제 이 상계 $\gamma$ 를 최소화하는 것으로 축소된다.**

> [!important] 이 트릭의 논리
> $-\mu \le e \le \mu$ 는 정확히 $|e| \le \mu$ 와 같다. 그러므로 $\mu$ 는 오차의 절댓값보다 크거나 같다. 이제 $\mu$ 들의 합을 **최소화**하면, 최적해에서 $\mu$ 는 **가능한 한 작아져 결국 $|e|$ 와 같아진다.** 즉 "절댓값을 계산한다" 대신 "절댓값 이상인 변수를 두고 그것을 눌러 내린다"로 문제를 바꾼 것이다. 절댓값 하나가 **부등식 두 개 + 변수 하나**로 대체되었고, 모든 것이 선형이 되었다.

### LP 문제로의 완전한 정식화

출력 변수의 제약 $(\underline{\mathbf{y}}, \overline{\mathbf{y}})$, 조작 변수의 제약 $(\underline{\mathbf{U}}, \overline{\mathbf{U}})$, 조작 변수 변화율의 제약 $(\underline{\mathbf{u}}, \overline{\mathbf{u}})$ 을 모두 고려하면 문제는 다음 **LP 문제**로 해석된다.

$$\begin{aligned}\min_{\gamma,\boldsymbol{\mu},\beta,\mathbf{u}}\quad & \gamma \\ \text{subject to:}\quad & \boldsymbol{\mu} \ge G\mathbf{u}+\mathbf{f}-\mathbf{r} \\ & \boldsymbol{\mu} \ge -G\mathbf{u}-\mathbf{f}+\mathbf{r} \\ & \overline{\mathbf{y}} \ge G\mathbf{u}+\mathbf{f} \\ & -\underline{\mathbf{y}} \ge -G\mathbf{u}-\mathbf{f} \\ & \beta \ge \mathbf{u} \\ & \beta \ge -\mathbf{u} \\ & \overline{\mathbf{u}} \ge \mathbf{u} \\ & -\underline{\mathbf{u}} \ge -\mathbf{u} \\ & \overline{\mathbf{U}} \ge T\mathbf{u}+\mathbf{1}u(t-1) \\ & -\underline{\mathbf{U}} \ge -T\mathbf{u}-\mathbf{1}u(t-1) \\ & \gamma \ge \mathbf{1}^\mathsf{T}\boldsymbol{\mu} + \lambda\mathbf{1}\beta\end{aligned}$$

한 줄씩 읽으면 의미가 분명하다. 처음 두 줄은 출력 오차의 절댓값을 $\boldsymbol{\mu}$ 로 감싼 것, 3~4번째 줄은 출력 제약, 5~6번째 줄은 제어 증분의 절댓값을 $\beta$ 로 감싼 것, 7~8번째 줄은 변화율 제약, 9~10번째 줄은 진폭 제약, 마지막 줄이 상계의 정의다.

이 문제는 다음 표준 LP 형태로 변환된다.

$$\min_{\mathbf{x}}\ \mathbf{c}^\mathsf{T}\mathbf{x} \quad\text{subject to}\quad A\mathbf{x}\le\mathbf{b},\ \ \mathbf{x}\ge 0$$

$$\mathbf{x} = \begin{bmatrix}\mathbf{u}-\underline{\mathbf{u}} \\ \hline \boldsymbol{\mu} \\ \hline \beta \\ \hline \gamma\end{bmatrix}, \qquad \mathbf{c} = \begin{bmatrix}\mathbf{0} \\ \hline \mathbf{0} \\ \hline \mathbf{0} \\ \hline 1\end{bmatrix}$$

**$\mathbf{c}$ 를 보라.** 마지막 성분만 1이고 나머지는 전부 0이다. 즉 **오직 $\gamma$ 만 최소화**한다는 뜻이다. 나머지 변수들은 제약을 통해 간접적으로 결정된다.

$$A = \left[\begin{array}{r|r|r|r}\mathbf{G} & -I & \mathbf{0} & \mathbf{0} \\ -\mathbf{G} & -I & \mathbf{0} & \mathbf{0} \\ \hline \mathbf{G} & \mathbf{0} & \mathbf{0} & \mathbf{0} \\ -\mathbf{G} & \mathbf{0} & \mathbf{0} & \mathbf{0} \\ \hline I & \mathbf{0} & -I & \mathbf{0} \\ -I & \mathbf{0} & -I & \mathbf{0} \\ \hline I & \mathbf{0} & \mathbf{0} & \mathbf{0} \\ \hline T & \mathbf{0} & \mathbf{0} & \mathbf{0} \\ -T & \mathbf{0} & \mathbf{0} & \mathbf{0} \\ \hline \mathbf{0} & \mathbf{1}^\mathsf{T} & \mathbf{1}^\mathsf{T}\lambda & -1\end{array}\right], \qquad \mathbf{b} = \begin{bmatrix}-\mathbf{G}\underline{\mathbf{u}}-\mathbf{f}+\mathbf{r} \\ \mathbf{G}\underline{\mathbf{u}}+\mathbf{f}-\mathbf{r} \\ \hline \overline{\mathbf{y}}-\mathbf{G}\underline{\mathbf{u}}-\mathbf{f} \\ -\underline{\mathbf{y}}+\mathbf{G}\underline{\mathbf{u}}+\mathbf{f} \\ \hline -\underline{\mathbf{u}} \\ \underline{\mathbf{u}} \\ \hline \overline{\mathbf{u}}-\underline{\mathbf{u}} \\ \hline \overline{\mathbf{U}}-T\underline{\mathbf{u}}-\mathbf{1}u(t-1) \\ -\underline{\mathbf{U}}+T\underline{\mathbf{u}}+\mathbf{1}u(t-1) \\ \hline \mathbf{0}\end{bmatrix}$$

### 문제의 크기 — 실제로 얼마나 큰가

책은 정확한 개수를 준다.

| 항목 | 개수 |
|---|---|
| 결정 변수의 개수 | $2\times m\times N_u + n\times N + 1$ |
| 제약의 개수 | $4\times n\times N + 5\times m\times N_u + 1$ |

> [!example] 구체적인 숫자
> 입력 5개, 출력 5개인 공정에서 제어 지평 $N_u = 10$, 비용 지평 $N = 30$ 이라 하자.
> - 변수: $2\times 5\times 10 + 5\times 30 + 1 = 100 + 150 + 1 = 251$ 개
> - 제약: $4\times 5\times 30 + 5\times 5\times 10 + 1 = 600 + 250 + 1 = 851$ 개
>
> 이 정도 규모는 **어떤 LP 알고리즘으로도 풀 수 있다.** 그리고 책은 실용적인 조언을 덧붙인다. **제약의 개수가 결정 변수의 개수보다 많으므로, 쌍대(dual) LP 문제를 푸는 편이 계산적으로 덜 비쌀 것이다.** 또한 제약 행렬 $A$ 의 특수한 형태 덕분에 **5.4.2절의 제약 축소 알고리즘**을 적용해 제약 개수를 줄일 수 있다.

> [!example] 예제 5.6 — 공기 압축기
> 압축 공기는 대부분의 산업 플랜트에서 여러 용도로 쓰이며, 공장의 여러 공정에 압축 공기를 공급하는 **공기 압축기**는 산업 현장에서 흔히 볼 수 있다. 이 예제는 **플랜트에 공기를 공급하는 대형 공기 압축기**를 다룬다.
>
> **공정의 구조.** 출구 압력은 압축기의 **가이드 베인(guide vane)** 을 조작해 제어한다. **서지(surge)** 를 막기 위해 **블로우오프 밸브(blow-off valve)** 가 설치되어 있다. 여기서 흥미로운 점이 있다.
>
> | 밸브 상태 | 공정의 성격 |
> |---|---|
> | 블로우오프 밸브 **닫힘** | 단일입력 단일출력(SISO) 공정. 표준 제어 기법으로 충분히 제어 가능 |
> | 블로우오프 밸브 **열림** | 2입력 2출력 **다변수** 공정 |
>
> 조작 변수는 **가이드 베인 각도 $u_1$** 와 **밸브 위치 $u_2$** 이고, 피제어 변수는 **공기 압력 $y_1$** 과 **공기 유량 $y_2$** 다([[다변수 시스템과 상호작용]]). 공정 모델은 다음 전달함수 행렬로 주어진다.
> $$\begin{bmatrix}Y_1(s) \\ Y_2(s)\end{bmatrix} = \begin{bmatrix}\dfrac{0.1133e^{-0.715s}}{1+4.48s+1.783s^2} & \dfrac{0.9222}{1+2.071s} \\[2mm] \dfrac{0.3378e^{-0.299s}}{1+1.09s+0.361s^2} & \dfrac{-0.321e^{-0.94s}}{1+2.463s+0.104s^2}\end{bmatrix}\begin{bmatrix}U_1(s) \\ U_2(s)\end{bmatrix}$$
> 각 성분에 붙은 $e^{-\theta s}$ 가 **지연 시간(dead time)** 이고, 성분마다 값이 다르다는 점이 이 문제를 어렵게 만든다.

![[mpc_fig_5_7.png]]
*그림 5.7 — 압축기*

> [!example] 그림이 말하는 것
> 압축기 설비의 구성도다. 가이드 베인과 블로우오프 밸브라는 두 개의 조작 지점, 그리고 압력과 유량이라는 두 개의 측정 지점이 어떻게 배치되어 있는지 보여준다. 앞의 전달함수 행렬이 왜 2×2인지가 이 그림에서 물리적으로 이해된다.

압축기는 **영주파수에서 공정을 비간섭화(decoupling)** 하고 첫 번째 루프에 PI 제어기, 두 번째 루프에 비례 제어기를 써서 제어할 수 있다. 이 제어기들은 **역 나이퀴스트 배열(inverse Nyquist array, INA)** 의 도움으로 얻은 것이다.

![[mpc_fig_5_8.png]]
*그림 5.8 — 압축기의 폐루프 응답: INA 제어기*

> [!example] 그림이 말하는 것
> 두 기준값에 연속적인 스텝 변화를 주었을 때의 시뮬레이션 폐루프 응답이다. (a)를 보면 **응답이 상당히 진동적**이다. (b)는 조작 변수의 변화를 보여주는데, **압력 설정점이 바뀔 때마다 밸브 위치에 높은 피크가 나타난다.** 이 피크가 이후 제약 GPC로 잡아야 할 문제다.

**GPC 적용.** 샘플링 시간을 0.05초로 선택하면 공정은 다음 이산 전달함수 행렬로 근사된다.

$$\begin{bmatrix}\dfrac{10^{-4}(0.7619z^{-1}+0.7307z^{-2})}{1-1.8806z^{-1}+0.8819z^{-2}}z^{-14} & \dfrac{0.022z^{-1}}{1-0.9761z^{-1}} \\[2mm] \dfrac{10^{-2}(0.1112z^{-1}+0.1057z^{-2})}{1-1.8534z^{-1}+0.8598z^{-2}}z^{-6} & \dfrac{10^{-2}(-0.2692z^{-1}-0.1821z^{-2})}{1-1.2919z^{-1}+0.306z^{-2}}z^{-19}\end{bmatrix}$$

$z^{-14}$, $z^{-6}$, $z^{-19}$ 이 각 채널의 **이산 지연 시간**이다. 성분마다 지연이 다르다는 점을 눈여겨보자.

이 공정은 다음 설계 파라미터의 **다변수 GPC**로 제어할 수 있다: $N_1 = 20$, $N_2 = 23$, $N_3 = 3$, $\lambda = 0.8$. **비용 지평의 시작점은 지연 시간들의 최댓값으로 선택되었다** — 그 이전 구간의 출력은 현재 제어 동작에 반응하지 않으므로 비용에 넣어 봐야 의미가 없기 때문이다([[예측 지평과 제어 지평]]).

![[mpc_fig_5_9.png]]
*그림 5.9 — 압축기의 폐루프 응답: 제약 없는 GPC*

> [!example] 그림이 말하는 것
> (a)에서 **두 피제어 변수 모두 진동 없이 빠르게 설정점에 도달**한다. 한 변수의 기준값 변화가 다른 변수에 일으키는 외란도 매우 작다 — 비간섭화가 잘 되었다는 뜻이다. INA 제어기(그림 5.8)와 비교하면 명백한 개선이다. 그러나 (b)의 조작 변수를 보면 **밸브 위치에 여전히 높은 피크**가 관찰된다(INA 제어기 때보다는 훨씬 작지만).

**제약 GPC로 마무리.** 조작 변수의 피크를 줄이기 위해 제약 GPC를 사용한다. 조작 변수를 **구간 $[-2.75, 2.75]$ 안에** 제한했다.

![[mpc_fig_5_10.png]]
*그림 5.10 — 압축기의 폐루프 응답: 제약 GPC*

> [!example] 그림이 말하는 것
> (a)에서 **기준값 스텝 변화에 대한 압력의 응답이 제약 없는 경우보다 약간 느리다.** 그러나 (b)에서 보듯 **조작 변수가 원하는 한계 안에 유지된다.** 이것이 제약 MPC의 전형적인 거래다 — **약간의 성능을 내주고 제약 만족을 얻는다.** 그리고 이 거래는 대개 이득이다. 밸브가 물리적으로 낼 수 없는 피크를 요구하는 "빠른" 제어기는 시뮬레이션에서만 빠를 뿐, 실제 설비에서는 그 요구가 잘려 나가며 예측과 다른 거동을 낳기 때문이다.

---

## 5.8 공칭 MPC의 재귀적 실현가능성과 안정성 (Recursive Feasibility and Stability of Nominal MPC)

### 실현가능성이라는 새로운 위험

MPC의 제어 동작이 제약이 붙은 최적화 문제를 풀어 계산될 때, 예를 들어

$$x \in \mathcal{X}, \qquad u \in \mathcal{U}$$

라는 제약이 있을 때, **최적화 문제의 해 공간이 비어 버려서 해를 얻지 못할 위험**이 생긴다. 문제가 **실현불가능(unfeasible)** 해지면 **고려한 모든 제약을 만족시키는 유효한 제어 시퀀스가 존재하지 않는다**는 뜻이다.

> [!warning] 제약 MPC의 아킬레스건
> 제약 없는 MPC는 언제나 답을 준다 — $-\mathbf{H}^{-1}\mathbf{b}$ 를 계산하면 그만이다. 그러나 제약 MPC는 **"답이 없습니다"** 라고 대답할 수 있다. 그리고 그 순간 **컨트롤러는 다음 제어 동작을 계산하지 못하고 멈춘다.** 그래서 최적화 문제의 정의역이 비어 있지 않다는 **이론적 보장**이 대단히 중요해진다.

### 무한 지평이면 쉽지만 — 그리고 그것이 왜 어려운가

이런 보장은 **무한 지평(infinite horizon) 최적화 문제**를 풀 수 있다면 쉽게 얻어진다. 한 가지 방법은 $x(t+N_\mathrm{p}+1)=0$ 같은 등식 제약을 부과하는 것이다(일반성을 잃지 않고 기준값을 0으로 가정). 그러면 $k \ge N_\mathrm{p}+1$ 에 대해 $u(t+k)=0$ 이 $x(t+k+1)=0$ 을 보장하는 적절한 해가 된다. **그러나 이렇게 하려면 매우 긴 예측 지평이 필요할 수 있다.**

### 보조 제어 법칙 + 불변 집합이라는 해법

덜 부담스러운 전략은 **적절한 보조 제어 법칙(auxiliary control law)** 을 활용하는 것이다. 상태공간 MPC에서는 **선형 이차 조절기(LQR)** 같은 안정화 피드백 이득 $u(t) = K_\mathrm{LQR}x(t)$ 를 쓰는 것이 일반적이다.

**기본 아이디어는 무한 지평을 두 부분으로 쪼개는 것이다.**

1. **처음 $N_\mathrm{p}$ 시각 동안**: MPC 컨트롤러가 제어 동작을 제공한다.
2. **시각 $N_\mathrm{p}+1$ 부터 무한대까지**: $u(t)=K_\mathrm{LQR}x(t)$ 로 제어 동작을 생성한다.

> [!tip] 비유 — 등산의 마지막 구간
> 산 정상까지 가는 길을 전부 미리 계획하는 것은 불가능하다. 대신 **"대피소까지만 계획한다."** 대피소에서 정상까지는 이미 잘 닦인 길이 있어서 누구나 안전하게 갈 수 있음을 알기 때문이다. MPC는 대피소까지의 경로를 매번 새로 계산하고, LQR이 대피소에서 정상까지를 책임진다.

**그런데 문제가 있다.** 제어 법칙 $u(t)=K_\mathrm{LQR}x(t)$ 가 **실현불가능한 제어 동작을 만들어 낼 수 있다.** LQR은 제약을 모르기 때문이다. 그러므로 보조 제어기로의 전환은 **입력·상태 제약을 위반하지 않을 것이 보장될 때만** 이루어져야 한다.

이 보장은 전환이 **제어 법칙 $u(t)=K_\mathrm{LQR}x(t)$ 에 대한 불변 집합 $\mathcal{X}_f$ 안에서** 일어나면 얻어진다. $\mathcal{X}_f$ 는 다음 두 성질을 갖는 상태 공간의 영역이다([[불변 집합 Invariant Set]]).

1. $x(t)\in\mathcal{X}_f$ 이면 $u(t)=K_\mathrm{LQR}x(t)$ 아래에서 $x(t+1)\in\mathcal{X}_f$ 이다. **(한 번 들어가면 나오지 않는다)**
2. 모든 $x(t)\in\mathcal{X}_f$ 에 대해 제어 동작 $u(t)=K_\mathrm{LQR}x(t)$ 가 실현가능하다. 즉 고려된 모든 입력·상태 제약을 만족한다. **(그 안에서는 LQR이 제약을 어기지 않는다)**

따라서 **종단 제약 $x(t+N_\mathrm{p})\in\mathcal{X}_f$ 를 최적화 문제에 추가**하면, 예측 지평 끝에서 상태가 불변 집합 $\mathcal{X}_f$ 로 몰리도록 보장할 수 있다.

> [!note] 각주가 짚는 관계
> 앞서 소개한 **원점을 종단 영역으로 부과하는 전략은 불변 집합 전략의 극단적인 특수 경우**로 볼 수 있다. 점 하나도 (자명한) 불변 집합이기 때문이다.

### 재귀적 실현가능성 증명 — 꼬리 이어 붙이기

이제 핵심 논증이다. 천천히 따라가 보자.

**1단계.** 시각 $t$ 에서 상태 $x(t)$ 가 최적화 문제를 풀 수 있는 상태라 하자. 이는 시스템을 $x(t)$ 에서 불변 집합 $\mathcal{X}_f$ 안의 상태 $x(t+N_\mathrm{p})$ 로 데려가는 제어 시퀀스

$$\{u(t),\ u(t+1),\ \ldots,\ u(t+N_\mathrm{p}-1)\}$$

를 찾을 수 있다는 뜻이다. 시스템 동역학과 부과된 모든 제약을 만족하면서 말이다. 시각 $t+N_\mathrm{p}+1$ 부터는 $u(t)=K_\mathrm{LQR}x(t)$ 를 적용할 수 있고, **미래의 모든 시스템 거동이 $\mathcal{X}_f$ 안에 갇혀 있으므로 모든 제약이 만족될 것이 보장된다.**

**2단계.** 시각 $t+1$ 에서, 공칭 모델은 앞서 계산한 시퀀스의 첫 제어 동작을 적용한 결과로 상태 $x(t+1)$ 에 있다. 따라서 **$x(t+1)$ 은 $x(t+N_\mathrm{p})$ 를 $\mathcal{X}_f$ 로 데려간 시퀀스의 일부**다.

**3단계 — 결정적인 트릭.** 이전 시퀀스의 **꼬리(tail)**

$$\{u(t+1),\ \ldots,\ u(t+N_\mathrm{p}-1)\}$$

에 제어 동작 $u(t+N_\mathrm{p})=K_\mathrm{LQR}x(t+N_\mathrm{p})$ 를 **뒤에 이어 붙이면**, 시스템을 $x(t+1)$ 에서 $\mathcal{X}_f$ 안의 상태로 데려가는 **실현가능한 시퀀스**가 만들어진다.

**4단계 — 결론.** 이는 시각 $t+1$ 에서도 MPC 최적화 문제를 풀 수 있다는 뜻이다. 실현가능한 제어 시퀀스를 하나 손에 쥐고 있으니까. 같은 논리를 다시 적용하면 시각 $t+2$ 에서도 새로운 실현가능 시퀀스를 만들 수 있다. **따라서 MPC 문제의 재귀적 실현가능성(recursive feasibility)이 보장된다**([[재귀적 실현가능성]]).

> [!important] 이 증명이 아름다운 이유
> 새로운 해를 **찾아내야 하는 것이 아니라**, 이미 가진 해를 **재활용해서** 만들어 낸다. "한 칸 밀고 뒤에 하나 붙인다"는 이 조작은 5.6절의 출발점 후보 2번과 정확히 같은 것이다. **MPC 이론에서 가장 자주 등장하는 논증 패턴**이므로 반드시 기억할 것.

> [!question] 자기점검
> 이 증명은 **공칭(nominal)** 경우, 즉 모델이 정확하고 외란이 없는 경우에만 성립한다. 왜 그런가? 힌트: 2단계에서 "공칭 모델은 상태 $x(t+1)$ 에 있다"고 했다. 실제 시스템이 모델과 다르면 $x(t+1)$ 이 예상과 달라지고, 꼬리 시퀀스가 더 이상 실현가능하지 않을 수 있다. 이것이 6장(강인 MPC)의 출발점이다.

### 불변 집합은 어떻게 계산하는가

이 절차는 **보조 제어 법칙 아래에서 시스템이 양의 불변인 종단 제약 집합 $\mathcal{X}_f$ 의 신중한 설계**에 의존한다. 이 집합은 **오프라인으로 계산**할 수 있고 여러 방법이 제안되어 있다. 직관적인 방법 하나는 원점 주위의 **타원체(ellipsoid)** 로 만드는 것이다.

$$\mathcal{X}_f = \{x(t)\ \mid\ x(t)^\mathsf{T}Px(t) \le \rho\}$$

$\rho$ 는 양의 스칼라이고, $P$ 는 보조 피드백 이득을 사용할 때 **폐루프 시스템의 리아프노프 함수를 제공하는 양정치 행렬**이다([[리아프노프 안정성과 비용함수]]).

> [!warning] 타원체의 한계
> 책이 두 가지 단점을 지적한다. 첫째, 이 접근은 **결과로 나오는 불변 집합의 크기 면에서 보수적**이다(실제로는 더 넓은 영역이 안전한데 좁게 잡는다). 둘째, 최적화기가 **타원체의 다면체 근사**를 요구할 수 있다(QP는 선형 제약을 원하는데 타원체는 이차 제약이므로).
>
> **다포체(polytope)** 같은 더 복잡한 모양도 고려할 수 있지만, 계산 방법이 까다롭고 **시스템의 차원이 커질수록 확장성이 나쁘다.**

마지막으로 책은 겸손한 단서를 단다. **재귀적 실현가능성을 보장하는 방법이 이것 하나만은 아니다.** 여러 방법이 존재하고 선택은 당면한 시스템의 구체적인 성질과 요구사항에 따라 달라진다. 다만 모든 경우에서 **궁극적인 목표는 같다: 매 시각마다 최적화 문제의 실현가능한 해를 찾을 수 있도록 보장하는 것.**

### 5.8.1 종단 비용을 통한 안정성 보장 (Ensuring Stability via Terminal Cost)

종단 영역 외에도, **종단 비용(terminal cost)** 을 최적화 문제에 포함시켜 안정성을 보장할 수 있다. 즉 제어되는 공정이 유계(bounded)로 남을 것을 보장하는 것이다. 종단 비용은 보통 **안정화 제어기(예: LQR)의 최적 잔여 비용(cost-to-go)** 으로 선택된다.

$$V_f(x(t+N_\mathrm{p})) = x(t+N_\mathrm{p})^\mathsf{T}Px(t+N_\mathrm{p})$$

여기서 $P$ 는 4장에서 소개된 **LQR 문제의 대수 리카티 방정식(algebraic Riccati equation)의 해**다.

> [!tip] 비유 — 남은 거리를 값으로 매기기
> 내비게이션이 경로를 계획할 때, 계산 범위 끝에서 **"여기서부터 목적지까지 대략 얼마나 더 걸리는지"** 를 추정값으로 더한다. 그래야 "가까워 보이지만 사실 막다른 길"에 속지 않는다. $V_f$ 가 정확히 그 추정값이고, 리카티 방정식이 그 값을 정확히 계산해 준다.

종단 비용과 종단 제약을 모두 포함하면 최적화 문제는 다음과 같아진다(각주가 밝히듯 **안정성 보장을 제공하기에 더 편리하므로 상태공간 정식화**를 쓴다).

$$\begin{aligned}\underset{\mathbf{u}}{\text{minimize}}\quad J = & \sum_{k=0}^{N_\mathrm{p}-1}\left(x(t+k)^\mathsf{T}Qx(t+k) + u(t+k)^\mathsf{T}Ru(t+k)\right) \\ & \quad + x(t+N_\mathrm{p})^\mathsf{T}Px(t+N_\mathrm{p}) \\ \text{subject to}\quad & x(t+1) = Ax(t)+Bu(t), \\ & x(t+k+1) = Ax(t+k)+Bu(t+k),\quad k=1,\ldots,N_\mathrm{p}-1, \\ & x(t+k)\in\mathcal{X},\quad u(t+k)\in\mathcal{U},\quad k=0,\ldots,N_\mathrm{p}-1, \\ & x(t+N_\mathrm{p})\in\mathcal{X}_f\end{aligned}$$

이 최적화 문제를 매 시각 풀고 **첫 번째 제어 동작만 적용**하면 MPC 제어 법칙이 된다. 초기 상태의 실현가능성과 시스템을 안정화하는 제어 법칙의 존재라는 가정 아래, **얻어진 MPC 제어 법칙은 재귀적으로 실현가능할 뿐 아니라 점근 안정(asymptotically stable)** 하다.

**재귀적 실현가능성**은 앞에서 보인 대로다 — 시각 $t$ 에서 실현가능하면 최적 제어 시퀀스의 꼬리가 시각 $t+1$ 에서 실현가능하기 때문이다.

**점근 안정성**은 $J^*(x(t))$ 가 **리아프노프 함수 역할**을 하기 때문이다. 증명을 따라가 보자.

시각 $t$ 와 $t+1$ 의 비용함수를 비교한다. $J_t^*(x)$ 를 초기 조건 $x$ 에 대한 시각 $t$ 로부터의 최적 잔여 비용, $J_{t+1}^*(x)$ 를 시각 $t+1$ 로부터의 최적 잔여 비용이라 하자. 시각 $t$ 에서 얻은 제어 시퀀스를 시각 $t+1$ 에서 $x$ 로부터 적용하면, **시각 $t+1$ 의 제어 시퀀스가 최적이므로** 다음이 성립한다.

$$J_{t+1}^*(x) \le J_t^*(x) - l(x(t), u(t))$$

여기서 $l(x(t),u(t)) = x(t)^\mathsf{T}Qx(t) + u(t)^\mathsf{T}Ru(t)$ 는 시각 $t$ 의 **단계 비용(stage cost)** 이다.

> [!important] 이 부등식이 말하는 것
> 시간이 흐를수록 **잔여 비용이 감소한다.** 얼마나 감소하는가? **방금 지불한 단계 비용만큼** 감소한다. 직관적으로 당연하다 — 앞으로 가야 할 길에서 한 구간을 이미 걸었으니, 남은 길의 비용은 그만큼 줄어든다. 그리고 **실제로는 그보다 더 줄어들 수도 있다**($\le$ 이므로). 시각 $t+1$ 에서 다시 최적화하면 꼬리 시퀀스보다 나은 것을 찾을 수 있기 때문이다.

비용함수는 **음이 아니므로**, 이 감소 수열은 반드시 수렴한다. 따라서 **외란도 모델 불확실성도 없는 경우 상태 수열 $x(t)$ 는 원점으로 수렴한다.** 그리고 그런 문제들이 존재하더라도, MPC 제어 법칙 아래의 폐루프 시스템이 **유계 궤적을 생성하는 리아프노프 시스템임을 증명할 수 있다.**

> [!note] 무한 지평의 두 조각 분해, 다시
> 종단 제약을 최적화 문제에 추가하는 것은 **무한 예측 지평을 두 부분으로 쪼개는 것**이다.
>
> | 구간 | 다루는 방식 |
> |---|---|
> | 유한 지평 부분 | 비용함수와 제약이 **명시적으로** 정의됨 |
> | 무한 지평 부분 | **종단 비용과 종단 제약**이 대신 커버함 |
>
> 또한 종단 비용 $V_f(x)$ 는 제어 불변 종단 집합 $\mathcal{X}_f$ 위의 **제어 리아프노프 함수(control Lyapunov function)** 다. 즉 임의의 $x\in\mathcal{X}_f$ 에 대해, 상태를 $\mathcal{X}_f$ 안에 유지하면서 $V_f(x)$ 를 줄이는 제어 입력 $u$ 가 존재함을 보장한다.

---

## 5.9 제약 관리 (Constraint Management)

### 실현불가능은 언제 생기는가

최적화 문제가 **실현가능(feasible)** 하다는 것은 목적함수가 유계이고 모든 제약을 만족하는 결정 변수 공간의 점이 존재한다는 뜻이다. 그런데 **제약 집합이 결정 변수 공간에서 정의하는 영역이 비어 버릴 수 있다.** 예를 들어 **달성 불가능한 제어 목표**나 공정을 운전점에서 멀리 밀어내는 **외란**이 실현불가능을 낳을 수 있다. 이런 조건에서 최적화 알고리즘은 아무 해도 찾지 못하고, 최적화 문제는 **실현불가능(infeasible)** 하다고 말한다.

실현불가능은 **정상상태 영역**과 **과도 영역** 양쪽에서 나타난다.

**정상상태에서의 실현불가능.** 보통 **달성 불가능한 제어 목표** 때문에 생긴다. 예를 들어 조작 변수가 제약되어 있어서 설정점에 도달할 수 없는 경우다. 일반적으로 **조작 변수가 초입방체(hypercube) 안에 제약되어 있으면, 도달 가능한 설정점들은 피제어 변수 공간의 다포체 안에 있으며, 그 다포체의 꼭짓점은 초입방체의 꼭짓점에 공정의 DC 이득 행렬을 곱해 정의된다.** 이런 종류의 실현불가능은 **설계 단계에서 그런 목표를 제거해** 쉽게 처리할 수 있다.

> [!tip] 비유 — 도달할 수 없는 목표
> 자전거로 시속 200km를 내라는 요구는 실현불가능하다. 이건 제어의 문제가 아니라 **목표 설정의 문제**다. 그러니 설계할 때 애초에 "이 자전거로 낼 수 있는 속도 범위"를 계산해 두고 그 안에서만 목표를 잡으면 된다. **DC 이득 행렬**이 그 계산을 해 준다 — 입력 범위를 출력 범위로 번역해 주는 것이다.

**과도 상태에서의 실현불가능.** 이쪽이 훨씬 까다롭다. 부과한 제약이 **합리적으로 보이는데도** 실현불가능이 생길 수 있다. 정상 운전에서 문제를 일으키지 않는 제약이 특정 상황에서는 문제가 된다. 책이 드는 원인들은 다음과 같다.

- **외란이나 큰 기준값 변화**가 변수를 한계 밖으로 밀어내서, **제한된 에너지의 제어 신호로는 다시 허용 영역 안으로 넣는 것이 불가능**해질 수 있다. 이런 상황에서 제약들은 **일시적으로 양립 불가능**해진다.
- **운전원이 공정 가동 중에 운전 변수의 한계를 재정의**할 때도 생긴다. 변수가 이미 새 한계 밖에 있으면 문제는 곧바로 실현불가능해진다.
- 이런 실현불가능한 해는 **최적점이 제약에 가깝고 시스템이 외란을 받는 경우**에 더 흔하며, 금지 영역으로의 이탈로 이어진다.

> [!important] 왜 이것이 치명적인가
> 실현가능성은 제약 MPC에 대단히 중요하다. 두 가지 이유에서다. 첫째, **제약 MPC 전략의 안정성 증명이 실현가능성을 요구한다**(5.8절에서 본 그대로다). 둘째, 더 직접적으로 **최적화 문제가 실현가능하지 않으면 MPC는 다음 제어 동작을 계산할 수 없어 아예 작동하지 않는다.** 제약 MPC에서 실현불가능은 충분히 일어날 법한 일이므로 **반드시 대비책을 마련해야 한다.**

### 5.9.1 실현가능성 회복 (Recovering Feasibility)

**제약 관리(constraint management)** 방법들은 공정 변수에 부과된 한계의 **종류에 따라 달라지는 기준**에 맞춰 제약에 손을 대서 실현가능성을 회복하려 한다. 그래서 먼저 한계를 분류해야 한다.

| 한계의 종류 | 성격 | 위반 가능성 |
|---|---|---|
| **물리적 한계(physical limits)** | 장비 구조 자체 때문에 생기며 주로 액추에이터와 관련 | **절대 초과 불가** |
| **안전 한계(security limits)** | 위반 시 공정 안전을 위협하거나 비상 정지를 유발. 주로 피제어 변수와 관련 | 절대 위반해서는 안 됨 |
| **운전 한계(operational limits)** | 적절한 운전 조건 유지를 위해 운전원이 정한 경계 | **특정 상황에서 초과 가능** |
| **실제 한계(real limits)** | 제어 알고리즘이 매 순간 실제로 사용하는 한계. 제약 관리자가 제공 | 물리적 한계를 절대 넘지 않도록 계산되어야 함 |

> [!important] 이 분류가 핵심이다
> 실현가능성을 회복하려면 **무언가를 포기해야 한다.** 그런데 아무거나 포기해서는 안 된다. **물리적 한계와 안전 한계는 절대 건드리면 안 되고, 운전 한계는 양보 가능하다.** 즉 제약 관리란 **"양보해도 되는 것부터 순서대로 양보하기"** 다.

가능한 해법은 다음 네 그룹으로 분류된다.

**1. 컨트롤러 분리 (Disconnection of the Controller).** 가장 쉬운 방법이다. 제약 비양립성이 생기면 컨트롤러를 **백업 값이나 백업 컨트롤러로 넘기고**, 해의 허용성이 회복되면 자동 운전으로 돌아온다.

> [!warning] 이 방법의 심각한 단점
> 책이 강하게 경고한다. 제약 비양립성 문제가 생기는 때는 대개 **폐루프 시스템이 위태로운 국면**에 있을 때이고, 그런 상황에 대한 **운전원의 경험은 대개 매우 적다.** 게다가 제약이 안전이나 경제적 측면과 관련되어 있다면, 그 순간의 결정은 언제나 결정적이다 — 어떤 제어 목표는 만족될 수 없는 상황이기 때문이다. 이 방법은 **제약 비양립성 문제가 드물게 발생할 때** 주로 쓴다.

**2. 제약 제거 (Constraint Elimination).** 제약 비양립성이 생길 때마다 **허용 불가능한 제약들의 집합**을 만들어 최적화 과정에서 **일시적으로 고려하지 않는다.** 그 후 실현가능성을 주기적으로 검사해 제거된 제약을 다시 넣는다.

> [!note] 왜 반복 실행이 필요한가
> 책의 각주가 짚듯, 결정 변수 공간의 한 점이 주어지면 **위반된 제약이 무엇인지는 쉽게 계산할 수 있다.** 그러나 최적화 방법 자체는 **어느 제약이 실현불가능을 일으키는지 알려 주지 않는다.** 그래서 일부 제약을 버린 뒤 **최적화 알고리즘을 다시 돌려** 남은 제약들의 실현가능성을 확인해야 한다.

제약 제거 방법론에는 두 가지 대안이 있다.

- **무차별 제거(Indiscriminate Elimination).** 가장 단순하다. 실현불가능이 발생할 때마다 **모든 제약을 제거**한다. **안전과 직결된 제약이 있는 경우에는 절대 쓰면 안 된다.**
- **계층적 제거(Hierarchical Elimination).** 설계 단계에서 각 제약에 **우선순위**를 부여한다. 실현가능성 문제가 생길 때마다 컨트롤러는 **낮은 우선순위 제약부터 순서대로 제거**해 실현가능성이 회복될 때까지 진행한다.

**3. 제약 완화 (Constraints Relaxation).** 한계를 **일시적으로 완화**하거나(즉 값을 키우거나), **하드 제약** $\mathbf{R}\mathbf{u} < \mathbf{a}$ 를 **소프트 제약** $\mathbf{R}\mathbf{u} < \mathbf{a}+\epsilon$ 으로 바꾸는 방법이다. 이때 비용함수에 $\epsilon^\mathsf{T}\mathbf{T}\epsilon$ 항을 더해 **제약 위반에 벌점을 매긴다.** 그러면 장기적으로 목적함수의 벌점 항이 보조 변수를 0으로 데려간다([[하드 제약과 소프트 제약]]).

> [!tip] 비유 — 통금 시간과 벌점
> "밤 10시까지 귀가"가 하드 제약이면 10시 1분 도착은 곧 실패다. 소프트 제약으로 바꾸면 "늦은 만큼 벌점"이 된다. 평소에는 벌점이 싫어서 10시 전에 들어오지만, **정말 어쩔 수 없는 날에는 늦더라도 문제가 성립한다.** 이것이 소프트 제약의 가치다 — **문제가 아예 풀리지 않는 사태를 막는다.**

**4. 제약 지평 변경 (Changing the Constraint Horizons).** 대부분의 제약 실현불가능은 **비용 지평의 앞부분에서 발생한다.** 갑작스러운 외란이 공정을 실현불가능한 영역으로 데려가기 때문이다. 이 방법의 핵심 아이디어는 **지평의 첫 부분에서는 제약을 고려하지 않는 것**이다. 일부 상용 MPC는 **제약 창(constraint window)** 이라는 개념을 사용한다.

> [!question] 자기점검
> 방법 4가 왜 합리적인가? 힌트: 지금 이미 한계 밖에 있다면, **그 사실을 제약으로 걸어 봐야 문제만 깨진다.** 중요한 것은 "지금 당장 안으로 들어가라"가 아니라 **"몇 스텝 안에 안으로 들어가라"** 이다. 제약 창은 그 유예 기간을 만들어 준다.

### 5.9.2 제약과 안정성 (Constraints and Stability)

**모든 안정성 결과는 제어 법칙의 실현가능성을 요구한다.** 기본 아이디어는 이것이다. **무한 지평 비용함수는 실현가능한 해가 있으면 단조 감소함을 보일 수 있고, 따라서 안정성을 보장하는 리아프노프 함수로 해석할 수 있다.**

**그러나 무한 지평 제어 문제는 모든 공정 변수가 제약되지 않을 때만 풀 수 있다.** 예를 들어 잘 알려진 **선형 이차 가우시안(LQG) 최적 제어기**는 해석적으로 구할 수 있고 일반적인 가정 아래 선형 공정에 대해 안정한 폐루프를 보장한다.

**제약이 있는 공정에서 무한 지평을 쓰기 어려운 이유**는 무엇인가? 관련된 최적화 문제를 풀려면 **결정 변수의 개수가 반드시 유한한 수치적 방법**을 써야 하고, 그러면 **명시적인 함수 형태가 없는 비선형 제어 법칙**이 나오기 때문이다.

**해법: 목적함수를 두 부분으로 쪼갠다.**

1. **유한 지평이고 제약이 있는 부분**
2. **무한 지평이고 제약이 없는 부분**

그러면 무한·무제약 부분은 **리카티 방정식으로 풀 수 있고**, 상태에 의존하는 비용함수를 얻는다. 이 비용함수를 유한 지평 최적화 문제에 집어넣고 수치적으로 푼다. **따라서 안정성은 유한 제어 지평을 쓸 때 종단 상태 제약을 부과하는 문제로 환원된다.**

**입출력(input-output) 관점에서 보면** 이것은 다음과 동등하다: **비용 지평 이후 충분히 큰 지평 $m$ 동안 예측 출력이 기준값을 정확히 따르도록 강제하거나**, 적어도 **출력 변수의 과도 응답을 덮을 만큼 지평을 충분히 길게 잡는 것**이다.

> [!important] 5.3.3절과 5.8절이 여기서 만난다
> 5.3.3절에서 "안정성을 보장하는 정식화는 종단 벌점과 종단 집합을 갖는다"고 했고, 5.8절에서 그것을 상태공간에서 증명했다. 이 절은 같은 이야기를 **입출력 표현(GPC 계열)** 의 언어로 다시 말하고 있다. **CRHPC의 등식 제약이 왜 안정성 장치인지**가 이제 분명해진다.

**종단 제약은 실현가능성을 위협한다.** 그래서 여러 저자가 이 문제를 완화하는 수단을 제안했고, 대부분은 앞 소절의 방법들에 대응한다. 책이 소개하는 구체적인 연구들은 다음과 같다.

| 연구 | 제안 내용 |
|---|---|
| Rawlings & Muske | **무한 지평의 초기 구간에서 상태 제약을 버려서** 문제를 실현가능하게 만든다 |
| Muske 등 | 초기 단계에서 상태 제약을 강제하지 않는 **출력 피드백 무한 지평 MPC**가 개루프 안정 시스템에 대해 안정한 폐루프를 만들고, 초기 공정·관측기 상태가 실현가능 영역 안에 있으면 불안정 공정도 안정화함을 보였다 |
| Zheng & Morari | **소프트 제약과 상태 피드백**을 쓰면 제어 지평을 충분히 크게 잡을 때 임의의 안정화 가능 시스템을 점근 안정화할 수 있고, 출력 피드백(관측기로 계산한 상태 벡터)으로도 임의의 개루프 안정 시스템을 안정화함을 보였다 |

마지막으로 책은 다음 장을 예고한다. **이 실현가능성·안정성 문제들은 강인 제어(robust control) 문제에서 더 어려워지며, 이는 다음 장에서 자세히 다뤄진다.** 예를 들어 어떤 연구는 공정을 제약 영역 밖으로 밀어낼 수 있는 **유계 외란이 있는 상황에서 제약 SGPC의 실현가능성을 보장**한다. 아이디어는 **미래의 최악 외란을 제거하는 데 필요한 최소 제어 파워를 결정**하는 것이고, 이를 구현하기 위해 **물리적 한계보다 더 빡빡한 제약을 조작 변수에 부과**한다.

> [!tip] 비유 — 여유분 남기기
> 장거리 운전에서 연료를 딱 맞게 채우지 않는다. **예상치 못한 우회로를 대비해 여유를 남긴다.** "물리적 한계보다 더 빡빡한 제약"이 정확히 이것이다 — 외란이 왔을 때 대응할 여력을 미리 확보해 두는 것이다.

---

## 5.10 제약 MPC에서의 다목적 최적화 (Multi-objective Optimization in Constrained MPC)

### 목표가 여럿일 때

지금까지 분석한 모든 MPC 전략은 미래 제어 동작 시퀀스를 결정하기 위해 **하나의 목적함수**(보통 이차 함수)에 기반했다. **그러나 많은 제어 문제에는 서로 다르고 때로는 충돌하는 제어 목표들이 있다.** 책이 드는 이유는 다음과 같다.

**1. 서로 다른 운전 단계.** 예를 들어 공정의 **시동(startup) 단계**에서는 **최소 시동 시간**이 바람직할 수 있지만, 일단 운전 영역에 도달하면 **피제어 변수의 최소 분산**이 주된 제어 목표가 될 수 있다.

**2. 목표의 전환.** 특정 운전 단계에서 작동 중이라도 제어 목표가 바뀔 수 있다. 예를 들어 **갑작스러운 외란 때문에 너무 높아진 변수의 값을 가능한 한 빨리 낮추는 것**이 목표가 될 수 있다. 피제어 변수 $y(t)$ 를 $y(t)\le y_h$ 로 유지하는 것이 목표인 공정을 생각하면, 제어 목표는 다음과 같이 정식화될 수 있다.

$$J = p(y_h - y(t+j))\sum_{j=\underline{N}_\mathrm{p}}^{\bar{N}_\mathrm{p}}(y(t+j)-r(t+j))^2 + p(y(t+j)-y_h)\sum_{j=\underline{N}_\mathrm{p}}^{\bar{N}_\mathrm{p}}(y(t+j)-y_h)^2$$

여기서 함수 $p$ 는 **계단 함수**다. 즉 인수가 0 이상이면 값 1을, 음수이면 값 0을 취한다.

> [!important] 이 식을 읽는 법 — 그리고 왜 문제인가
> 두 항이 **스위치로 켜고 꺼진다.** $y$ 가 한계 $y_h$ 아래에 있으면 첫째 항(기준값 추종)이 켜지고, $y$ 가 한계를 넘으면 둘째 항(한계로 되돌리기)이 켜진다. **모드가 바뀌는 컨트롤러**인 셈이다.
>
> **그런데 대가가 있다.** 책이 명시한다: **목적함수가 더 이상 이차 함수가 아니므로 QP 알고리즘을 쓸 수 없다.** 계단 함수 때문에 목적함수가 불연속이 되어 버렸기 때문이다. 이것이 다목적 MPC의 근본적 어려움이다.

**3. 소프트 제약.** 많은 경우 제어 목표는 오차 제곱합의 최적화가 아니라 **어떤 변수들을 지정된 경계 안에 유지하는 것**이다. 여기서 용어를 정확히 하자.

| 용어 | 정의 |
|---|---|
| **하드 제약(hard constraints)** | 위반할 수 없는 제약. 물리적 한계, 플랜트 안전 등의 이유로 변수가 반드시 규정된 영역 안에 있어야 함 |
| **소프트 제약(soft constraints)** | 넘을 수 있는 한계. 실현가능 영역 밖으로의 이탈이 바람직하진 않지만 허용됨 |

소프트 제약은 **여유 결정 변수(slack decision variable)** $\epsilon_h(j)$ 와 $\epsilon_l(j)$ 를 추가해 **QP 문제로 변환**할 수 있다.

$$y(t+j) \le y_h + \epsilon_h(j)$$
$$y(t+j) \ge y_l - \epsilon_l(j)$$
$$\epsilon_l(j),\ \epsilon_h(j) \ge 0$$

그리고 조작 변수 시퀀스는 다음을 최소화해서 결정된다.

$$J = \sum_{j=\underline{N}_\mathrm{p}}^{\bar{N}_\mathrm{p}}\epsilon_h(j)^2 + \sum_{j=\underline{N}_\mathrm{p}}^{\bar{N}_\mathrm{p}}\epsilon_l(j)^2$$

문제에 작용하는 **확장된 제약 집합** 아래에서다.

> [!tip] 왜 이것은 QP를 유지하는가
> 계단 함수 방식과 비교해 보라. 여기서는 **불연속 함수가 전혀 없다.** 목적함수는 $\epsilon$ 에 대한 이차식이고 제약은 전부 선형이다. **똑같은 "한계를 지켜라"라는 요구를, 하나는 QP를 깨뜨리는 방식으로, 다른 하나는 QP를 유지하는 방식으로 표현한 것**이다. 이 대비가 이 절의 교훈이다 — **정식화를 잘 고르면 계산 가능성을 지킬 수 있다.**

### 목적들을 하나로 합치기 — 가중합

때로는 모든 제어 목표 $J_1, J_2, \ldots, J_m$ 을 하나의 목적함수로 요약할 수 있다. 어떤 목표는 일부 피제어 변수를 기준값에 최대한 가깝게 유지하는 것일 수 있고, 다른 목표는 일부 변수를 지정된 영역 안에 유지하는 것일 수 있다. **모든 목표가 이차 함수이고 결정 변수에 대한 선형 제약 집합 $\mathbf{R}_i\mathbf{u}\le\mathbf{a}_i$ 아래에 있다면**, 미래 제어 시퀀스는 다음을 최소화해 결정할 수 있다.

$$J = \sum_{i=1}^{m}\beta_i J_i \qquad \text{subject to: } \mathbf{R}_i\mathbf{u}\le\mathbf{a}_i,\quad i=1,\ldots,m$$

각 목표의 중요도는 $\beta_i$ 를 적절히 설정해 조절한다. 어떤 경우에는 **더 중요한 목표(예: 안전 관련)에 훨씬 큰 가중치를 부여해 우선순위를 매길 수 있다.** 낮은 우선순위 목표를 고려하기 전에 반드시 달성되어야 하는 목표들 말이다.

> [!warning] 가중치 방식의 한계 — 책의 솔직한 고백
> 책이 세 가지 어려움을 든다. 첫째, 이것은 **자명하지 않은 작업이며 보통 시행착오로** 이루어진다. 둘째, **제어 목표들의 상대적 중요도를 대표하는 가중치 집합을 결정하는 것이 매우 어렵다.** 셋째, 현실의 제어 목표는 때때로 **정성적(qualitative)** 이어서 가중치 결정을 더욱 어렵게 만든다.
>
> **이 문제 때문에 다음 소절이 존재한다.** 가중치로 우선순위를 흉내 내는 대신, **우선순위를 직접 표현하는 방법**이 필요한 것이다.

### 5.10.1 목표의 우선순위화 (Prioritization of Objectives)

여기서 책은 **정수 변수를 이용해 우선순위를 명시적으로 표현하는** 방법을 소개한다. $m$ 개의 우선순위가 매겨진 제어 목표 $O_i$ 를 가진 공정을 생각하자. 목표 $O_i$ 가 목표 $O_{i+1}$ 보다 **높은 우선순위**를 가지며, 목표들이 다음과 같이 표현된다고 하자.

$$\mathbf{R}_i\mathbf{u} \le \mathbf{a}_i$$

**핵심 아이디어는 정수 변수 $L_i$ 를 도입하는 것이다.** 대응하는 제어 목표가 달성되면 $L_i = 1$, 아니면 0의 값을 갖는다. 목표는 다음과 같이 표현된다.

$$\mathbf{R}_i\mathbf{u} \le \mathbf{a}_i + K_i(1-L_i) \tag{5.22}$$

여기서 $K_i$ 는 $\mathbf{R}_i\mathbf{u} - \mathbf{a}_i$ 에 대한 **보수적인 상계**다.

> [!important] 이 식의 마법 — 빅-M 트릭
> 두 경우를 따져 보자.
> - **$L_i = 1$** (목표 달성): 우변이 $\mathbf{a}_i + 0 = \mathbf{a}_i$ 가 되어 **재정식화된 목표가 원래 제어 목표와 일치**한다.
> - **$L_i = 0$** (목표 미달성): 우변이 $\mathbf{a}_i + K_i$ 가 되는데, $K_i$ 가 충분히 큰 상계이므로 **제약이 자동으로 만족된다.** 즉 그 제약은 사실상 꺼진다.
>
> 즉 $K_i$ 를 도입함으로써, **대응하는 제어 목표 $O_i$ 가 달성되지 않을 때도 재정식화된 목표(제약)는 항상 만족된다.** 문제가 실현불가능해지는 사태를 원천적으로 막은 것이다. 최적화 문헌에서는 이런 큰 상수를 **빅-M(big-M)** 이라 부른다.

**우선순위는 다음 제약으로 부과한다.**

$$L_i - L_{i+1} \ge 0 \qquad i=1,\ldots,m-1$$

읽는 법: **$L_{i+1}=1$ 이려면 반드시 $L_i=1$ 이어야 한다.** 즉 **낮은 우선순위 목표를 달성했다고 주장하려면 그보다 높은 우선순위 목표들이 모두 달성되어 있어야 한다.** 우선순위가 부등식 하나로 깔끔하게 표현되었다.

**그리고 문제는 만족된 제어 목표의 개수를 최대화하는 것이다.**

$$\max \sum_{i=1}^{m}L_i$$

공정 모델이 선형이면 이 문제는 **혼합정수 선형계획법(MILP)** 알고리즘으로 풀 수 있다([[혼합정수계획 MILP]]).

> [!note] 정수 변수의 개수 줄이기
> 책이 실용적인 요령 하나를 소개한다. **동시에 위반될 수 없는 제약들에는 같은 변수 $L_i$ 를 쓴다.** 예를 들어 같은 제어 변수나 조작 변수에 대한 **상한과 하한**이 그런 경우다. 변수가 상한과 하한을 동시에 위반할 수는 없으므로 하나의 $L_i$ 로 충분하다. 정수 변수 하나를 줄이면 탐색 공간이 절반이 되므로 이득이 크다.

### 실패한 목표를 얼마나 잘 지킬 것인가

식 (5.22)의 제약 집합은 **만족될 수 없는 목표들의 만족 정도를 개선하도록** 수정할 수 있다. 상황을 설정하자. 어느 순간 모든 목표를 만족할 수 없고, **목표 $O_f$ 가 첫 번째로 실패한 목표**라고 하자. 이 목표를 가능한 한 근접하게 만족시키기 위해 **여유 변수 $\alpha$** 를 도입하고 다음 제약 집합을 부과한다.

$$\mathbf{R}_i\mathbf{u} \le \mathbf{a}_i + \alpha + K_i\left((i-1)+(1-L_i)-\sum_{j=1}^{i-1}L_j\right) \tag{5.23}$$

그리고 최소화할 목적함수는 다음과 같다.

$$J = -K_\alpha\sum_{i=1}^{m}L_i + f(\alpha) \tag{5.24}$$

여기서 $f$ 는 여유 변수 $\alpha$ 의 **벌점 함수**(양수이고 강한 증가 함수)이고, $K_\alpha$ 는 $f$ 의 상계다.

**왜 이렇게 하면 우선순위가 지켜지는가?** 논리를 따라가 보자.

**1. 목표 개수가 먼저다.** 최적화 알고리즘은 **$f(\alpha)$ 를 줄이려 시도하기 전에 만족된 목표의 개수($L_i=1$)를 최대화하려 한다.** 왜냐하면 **0이 아닌 $L_i$ 변수의 개수를 늘리는 편이 $f(\alpha)$ 를 줄이는 것보다 전체 목적함수를 더 작게 만들 수 있기 때문**이다. $K_\alpha$ 가 $f$ 의 상계라는 조건이 이것을 보장한다 — $L_i$ 하나를 켜서 얻는 이득 $K_\alpha$ 가 $f(\alpha)$ 를 완전히 없애서 얻는 이득보다 크거나 같기 때문이다.

**2. 식 (5.23)의 큰 항이 어떻게 작동하는가.** $i < f$ 인 모든 목표 $O_i$ 는 만족되므로($L_i=1$), (5.23)의 제약도 만족된다. $O_f$ 가 첫 번째로 실패한 목표이므로 다음이 성립한다.

$$\sum_{j=1}^{i-1}L_j = f-1 \qquad i \ge f$$

즉 $i \ge f$ 에서는 앞의 $f-1$ 개만 1이고 나머지는 0이다. 이제 (5.23)에서 $K_i$ 에 곱해지는 항을 계산해 보자.

- **$i = f$ 일 때**: $(f-1) + (1-0) - (f-1) = 1$... 원문 텍스트는 이 항이 **$i=f$ 에서 0**이라고 명시한다.
- **$i > f$ 일 때**: 이 항은 1보다 크다. 따라서 **$i>f$ 인 (5.23)의 모든 제약은 만족된다**(큰 값이 더해져 사실상 꺼지므로).

> [!warning] 원문 수식 확인 필요
> 원문은 "$i=f$ 에서 $K_i$ 에 곱해지는 항이 0이고, $i>f$ 에서는 1보다 크다"고 서술한다. $L_f=0$ 을 대입하면 $(f-1)+(1-0)-(f-1) = 1$ 이 되어 서술과 어긋난다. 텍스트 추출 과정에서 지표나 부호가 뭉개졌을 가능성이 크다(합의 상한이 $\sum_{j=1}^{i-1}$ 인지 $\sum_{j=1}^{i}$ 인지 등). **논지 자체는 명확하다: 실패한 첫 목표 $O_f$ 에서만 완화 항이 사라져 제약이 진짜로 작동하고, 그보다 낮은 우선순위 목표들의 제약은 자동으로 꺼진다.**

**3. 결과.** 유일하게 활성인 제약은 다음이다.

$$\mathbf{R}_f\mathbf{u} \le \mathbf{a}_f + \alpha$$

즉 **최적화 방법은 더 높은 우선순위의 목표들이 모두 만족된 이후에만, 첫 번째로 실패한 목표의 만족 정도를 최적화하려 시도한다.** 이것이 정확히 우리가 원했던 사전편찬식(lexicographic) 우선순위다.

> [!note] 오해하기 쉬운 지점
> 책이 명시적으로 주의를 준다. **$L_i=0$ 이라고 해서 목표 $O_i$ 가 만족되지 않았다는 뜻은 아니다.** 단지 **대응하는 제약이 완화되었다**는 것을 나타낼 뿐이다. 우연히 만족될 수도 있다.

**계산 비용은 어떤가?** 공정이 선형이고 함수 $f$ 가 선형이면 (5.24)의 최적화 문제는 **MILP**로 풀 수 있다. $f$ 가 이차 함수이면 **혼합정수 이차계획법(MIQP)** 알고리즘으로 푼다.

> [!warning] 실시간 구현의 한계
> 책이 마지막으로 경고한다. 혼합정수 계획 문제를 푸는 효율적인 알고리즘들이 있긴 하지만, **요구되는 계산량이 LP나 QP 문제보다 훨씬 크다.** 따라서 **실시간으로 이 방법을 구현하려면 목표의 개수를 작게 유지해야 한다.** 정수 변수 $m$ 개는 최악의 경우 $2^m$ 개의 조합을 뜻하므로, 목표가 조금만 늘어도 계산이 폭발한다.

---

## 연습문제 (Exercises) 훑어보기

책의 5.11절 연습문제들이다. 각 문제가 무엇을 훈련시키는지와 접근 힌트를 붙였다.

**5.1** 진폭 제약만 있는 경우를 생각하고, 이 종류의 제약만 존재할 때 최적화 문제를 어떻게 단순화할 수 있는지 논하라.
- **훈련 내용**: 제약의 종류가 문제 구조에 미치는 영향. **힌트**: 진폭 제약만 있으면 제약 행렬이 $\pm I$ 뿐이라 **박스 제약(box constraint)** 이 된다. 각 변수가 독립적으로 상하한을 갖는 경우 QP는 훨씬 단순해지며, 5.4.2절의 단일 변수 분석이 곧바로 적용된다.

**5.2** 결정 변수에 대한 활성 경계(active bounds)를 이용해 최적화 문제의 결정 변수 개수를 줄이는 방법을 설명하라.
- **훈련 내용**: 활성 집합 개념의 실용적 활용. **힌트**: 어떤 변수가 상한에 붙어 있음이 확정되면 그 변수는 **상수로 고정**되므로 결정 변수에서 빠진다. 5.6.2절의 활성 집합법과 5.4.1절의 소거가 여기서 만난다.

**5.3** 로젠의 사영법에서 사용하는 방향이 비용을 감소시키며, 벡터 $\mathbf{d}$ 가 제약 행렬의 영공간으로 사영됨을 증명하라.
- **훈련 내용**: 사영 행렬의 성질 증명. **힌트**: $\mathbf{d} = -\mathbf{P}\nabla J$ 에 대해 $\nabla J^\mathsf{T}\mathbf{d} = -\nabla J^\mathsf{T}\mathbf{P}\nabla J$ 를 계산하고, $\mathbf{P}$ 가 대칭 멱등(즉 $\mathbf{P}=\mathbf{P}^\mathsf{T}=\mathbf{P}^2$)임을 이용하면 이 값이 $-\|\mathbf{P}\nabla J\|^2 \le 0$ 임을 보일 수 있다. 영공간 성질은 $\mathbf{A}_1\mathbf{P}=0$ 에서 따라온다.

**5.4** 로젠의 방법이 변화율 제약을 어떻게 단순화할 수 있는지 상술하라.
- **훈련 내용**: 특정 제약 구조와 알고리즘의 상호작용. **힌트**: 변화율 제약은 $\pm I$ 형태이므로 활성 제약 행렬 $\mathbf{A}_1$ 이 단위행렬의 부분행렬이 되고, $(\mathbf{A}_1\mathbf{A}_1^\mathsf{T})^{-1}$ 계산이 자명해진다. 즉 사영이 **해당 성분을 0으로 만드는 것**으로 축약된다.

**5.5** $y(t+1)=ay(t)+bu(t)$ 인 시스템에 대해 $-0.2\le\Delta u(t)\le 0.2$, $-1\le u(t)\le 1$, $-3\le y(t)\le 3$ 일 때: (1) $N_\mathrm{p}=3$ 이차 목적함수로 MPC 제어 문제를 정식화하라(제약 행렬을 결정). (2) 1-노름 목적함수로 반복하라. (3) 시뮬레이션해 제약이 만족되는지 확인하라.
- **훈련 내용**: 이 챕터의 종합 연습. 5.3절(제약 행렬 구성) + 5.7절(1-노름 LP 정식화) + 검증. **힌트**: (1)은 5.3.1·5.3.2절의 $\mathbf{R}$, $\mathbf{c}$ 를 $N=3$ 에 대해 직접 써 보는 일이다. (2)는 5.7절의 $\boldsymbol{\mu}$, $\beta$, $\gamma$ 도입 절차를 그대로 따르면 된다.

**5.6** $y(t+1)=1.75y(t)-y(t-1)+0.25u(t)+0.25u(t-1)$ 인 시스템에 대해: (1) $N_\mathrm{p}=2$, 이차 목적, 오버슈트 제약으로 MPC를 정식화하라. (2) $\infty$-노름으로 단조 제약을 부과해 반복하라. (3) 결과 컨트롤러를 시뮬레이션하고 논평하라. (4) 제어 지평과 제어 가중치를 $N_\mathrm{p}=11$, $\lambda=50$ 으로 늘리고 논평하라.
- **훈련 내용**: 5.3.2절의 출력 형상 제약(오버슈트·단조) 구현. **힌트**: (4)의 숫자는 예제 5.2의 설정과 같다. 진동 시스템에서 **지평이 짧으면 실현불가능해지는 현상**을 직접 확인하라는 의도다.

**5.7** $x(t+1)=Ax(t)+Bu(t)$, $A=\begin{bmatrix}0&1\\1&1\end{bmatrix}$, $B=\begin{bmatrix}1\\1\end{bmatrix}$ 에 대해 $N_\mathrm{p}=3$, 이차 목적함수의 MPC를 정식화하되 종단 영역을 각각: (1) $\|x(t+N_\mathrm{p})\|_\infty\le 0.1$, (2) $\|x(t+N_\mathrm{p})\|_1\le 0.1$, (3) $x(t+N_\mathrm{p})^\mathsf{T}x(t+N_\mathrm{p})\le 0.1$ (마주치는 최적화 문제의 종류를 논평), (4) $x(t+N_\mathrm{p})^\mathsf{T}x(t+N_\mathrm{p})\le x(t)^\mathsf{T}x(t)$ 로 하라.
- **훈련 내용**: 5.3.3절 종단 제약의 기하학과 그것이 최적화 문제 종류를 어떻게 바꾸는지. **힌트**: (1)과 (2)는 **다면체**이므로 선형 제약이 되어 QP를 유지한다. (3)은 **이차 제약**이므로 QP가 아니라 QCQP(이차 제약 이차계획)가 된다 — 이것이 5.8절에서 "타원체는 다면체 근사가 필요할 수 있다"고 한 이유다. (4)는 우변이 현재 상태에 의존하는 **수축(contractive) 제약**이다.

**5.8** 예제 4.1의 항공기 실험을 다음 운전 제약 아래 반복하라: (1) $|u_1|\le 10$, $|u_2|\le 5$. (2) $|\Delta u_1|\le 10$, $|\Delta u_2|\le 5$. (3) 두 제약 집합을 동시에.
- **훈련 내용**: 진폭 제약과 변화율 제약의 **서로 다른 효과**를 실감하기. **힌트**: (1)만 걸면 응답이 크게 안 변할 수 있지만, (2)를 걸면 초기 응답이 눈에 띄게 느려진다. (3)에서 두 제약이 어떻게 상호작용하는지가 핵심이다.

---

## 요약

1. **제약은 예외가 아니라 기본이다.** 액추에이터의 범위와 속도, 안전·구조상의 출력 한계는 모든 실제 공정에 존재하며, 경제적 최적 운전점은 대개 제약들의 교차점에 있다. 그래서 제어 시스템은 늘 한계 근처에서 돌아간다(그림 5.1).

2. **잘라내기(clipping)는 최적이 아니다.** 제약 없이 계산한 뒤 한계로 포화시키는 방식은 목적함수 값을 키우고, 무엇보다 **출력 제약을 전혀 다룰 수 없다.** 제약을 최적화 문제 안에 명시적으로 넣어야 MPC의 예측 능력이 온전히 발휘된다(그림 5.2).

3. **모든 제약은 결국 $\mathbf{R}\mathbf{u}\le\mathbf{r}+\mathbf{V}x(t)$ 하나로 통일된다.** 입력 진폭·변화율, 출력 띠, 오버슈트, 단조 거동, 비최소위상, 종단 집합 — 모두 $\mathbf{u}$ 에 대한 선형 부등식으로 번역된다. 그리고 좌변의 행렬들은 오프라인으로, 우변만 매 샘플 갱신하면 된다.

4. **제약이 붙은 MPC는 QP 문제이고, QP를 푸는 일은 본질적으로 "어느 제약이 활성인지 알아내는 일"이다.** KKT 조건 — 정상성, 프라이멀 실현가능성, 듀얼 실현가능성, 상보 여유성 — 이 그 판정 기준을 제공한다. 활성 집합법은 그 조합을 시행착오로 탐색하고, 내점법은 로그 장벽으로 조합 탐색을 회피하며, 프라이멀-듀얼 방법은 두 변수를 동시에 갱신하고, 피벗팅 방법은 LCP로 환원해 렘키 알고리즘으로 푼다.

5. **목적함수를 1-노름으로 바꾸면 LP로 풀 수 있다.** 절댓값을 "보조 변수 + 부등식 두 개"로 감싸는 트릭이 핵심이다. 입력 5개·출력 5개, $N_u=10$, $N=30$ 인 문제는 변수 251개, 제약 851개짜리 LP가 된다.

6. **안정성은 제약 만족 문제로 환원된다.** 종단 비용(리카티 방정식의 해 $P$)과 종단 집합(불변 집합 $\mathcal{X}_f$)을 넣으면, 최적 비용 $J^*$ 가 리아프노프 함수 역할을 해 점근 안정성이 따라온다. 재귀적 실현가능성은 **직전 최적 시퀀스의 꼬리에 $K_\mathrm{LQR}$ 동작을 이어 붙이는** 논증으로 증명된다.

7. **실현불가능은 반드시 대비해야 한다.** 한계를 물리적·안전·운전·실제 한계로 분류하고, 컨트롤러 분리, 제약 제거(무차별 또는 계층적), 소프트 제약으로의 완화, 제약 지평 변경 중에서 상황에 맞는 수단을 고른다. 목표가 여럿이면 가중합으로 합치거나, 정수 변수 $L_i$ 와 빅-M 트릭으로 우선순위를 명시해 MILP/MIQP로 푼다 — 다만 계산량이 커서 목표 개수를 작게 유지해야 한다.

**다음 챕터 예고.** 이 챕터의 모든 논의는 **공칭(nominal) 경우**, 즉 모델이 정확하고 외란이 없다는 가정 위에 서 있었다. 재귀적 실현가능성 증명의 2단계가 "공칭 모델은 상태 $x(t+1)$ 에 있다"에 의존했음을 기억하자. 실제 공정에서는 모델이 틀리고 외란이 들어온다. **6장은 그 불확실성을 정면으로 다루는 강인(robust) MPC**를 배운다. 5.9.2절 끝에서 언급된 "물리적 한계보다 더 빡빡한 제약을 부과해 최악의 외란에 대비한다"는 아이디어가 그 출발점이다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[볼록 최적화와 이차계획법 QP]]
- [[KKT 조건]]
- [[라그랑주 승수와 등식 제약]]
- [[영공간과 유사역행렬]]
- [[활성 집합법 Active Set Method]]
- [[내점법 Interior Point Method]]
- [[선형계획법과 1-노름 목적함수]]
- [[하드 제약과 소프트 제약]]
- [[재귀적 실현가능성]]
- [[불변 집합 Invariant Set]]
- [[리아프노프 안정성과 비용함수]]
- [[혼합정수계획 MILP]]
- [[하삼각 토플리츠 행렬]]
- [[예측 지평과 제어 지평]]
- [[스텝 응답과 제어 증분]]
- [[자유 응답과 강제 응답]]
- [[비최소위상과 역응답]]
- [[다변수 시스템과 상호작용]]
- [[가중 노름과 대각 가중행렬]]
- [[이동 구간 원리 Receding Horizon]]
- [[조각별 아핀 PWA와 명시적 MPC]]

## 한눈에 보는 개념 지도

| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 진폭 제약 | $\underline{U} \le u \le \overline{U}$ | 제어 신호가 가질 수 있는 값의 범위 |
| 변화율 제약 | $\underline{u}\le\Delta u\le\overline{u}$ | 한 샘플 사이에 제어 신호가 움직일 수 있는 양 |
| 제약 일반형 | $\mathbf{R}\mathbf{u}\le\mathbf{r}+\mathbf{V}x(t)$ | 모든 종류의 선형 제약을 하나로 묶은 표준형 (식 5.5) |
| 헤시안 | $\mathbf{H}$ | 이차 목적함수의 이차항 계수 행렬. 양정치면 볼록 |
| 라그랑지안 | $\mathcal{L}$ | 목적함수에 제약을 승수로 붙인 함수 (식 5.7) |
| 라그랑주 승수 | $\boldsymbol{\lambda}, \boldsymbol{\mu}$ | 각 제약이 최적해를 얼마나 세게 밀고 있는지 |
| 상보 여유성 | $\mu_i(\mathbf{C}_i\mathbf{u}-c_i)=0$ | 안 닿은 제약의 승수는 0, 승수가 있는 제약은 닿아 있음 |
| 활성 제약 | $\mathbf{C}_i\mathbf{u}^*=c_i$ | 최적해에서 등식으로 만족되는, 실제로 답을 결정하는 제약 |
| 잉여 제약 | — | 지워도 실현가능 영역이 변하지 않는 제약 |
| 영공간 | $\text{Nul}(\mathbf{A})$ | $\mathbf{A}\mathbf{z}=0$ 인 벡터들의 집합. 제약을 깨지 않고 움직일 수 있는 방향 |
| 사영 행렬 | $\mathbf{P}$ | 임의의 벡터에서 금지된 방향 성분을 잘라내는 행렬 |
| 로그 장벽 | $-\mu\log(c_i-\mathbf{C}_i\mathbf{u})$ | 경계에 다가가면 무한대로 발산해 내부에 머물게 하는 벌점 |
| 장벽 파라미터 | $\mu$ | 장벽의 세기. 줄여 나가면 원래 문제의 해로 수렴 |
| 여유 변수 | $z, \epsilon, \alpha$ | 제약을 느슨하게 만들어 문제를 항상 실현가능하게 하는 보조 변수 |
| 하드 / 소프트 제약 | — | 절대 위반 불가 / 벌점을 내고 넘을 수 있음 |
| 종단 집합 | $\mathcal{X}_f$ | 예측 지평 끝에서 상태가 들어가야 하는 불변 안전 영역 |
| 종단 비용 | $x^\mathsf{T}Px$ | 지평 너머 무한 미래의 비용 추정. $P$ 는 리카티 방정식의 해 |
| 재귀적 실현가능성 | — | 지금 풀리면 다음 샘플에도 반드시 풀린다는 보장 |
| 1-노름 목적함수 | $\sum \lvert e \rvert + \lambda\sum \lvert \Delta u \rvert$ | 제곱 대신 절댓값. LP로 풀 수 있게 만든다 (식 5.21) |
| 빅-M 트릭 | $\mathbf{a}_i + K_i(1-L_i)$ | 정수 변수로 제약을 켜고 끄는 장치 (식 5.22) |
