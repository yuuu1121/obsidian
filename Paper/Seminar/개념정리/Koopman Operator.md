---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - DynamicalSystems
aliases:
  - 쿠프만 연산자
  - Koopman 연산자
keywords: Koopman operator, lifting, observable, linear operator
related notes: "[[Observable Function]], [[Koopman-Invariant Subspace]], [[EDMD]]"
dg-publish: false
---

# Koopman Operator (쿠프만 연산자)

> [!abstract] 한 줄 요약
> **비선형 시스템의 "상태"를 직접 다루는 대신, 상태의 "함수(observable)"를 다루면 — 무한차원이라는 대가를 치르고 — 완전히 **선형**인 연산자로 동역학을 표현할 수 있다.

---

## 1. 핵심 아이디어: 왜 선형이 되는가

### 문제 설정

이산시간 비선형 시스템을 생각하자.

$$
x_{t+1} = T(x_t), \qquad x \in \mathcal{X} \subseteq \mathbb{R}^{N_x}
$$

여기서 $T$는 **비선형** 전이 함수다. 상태 $x$를 직접 다루면 비선형이라 선형 제어 이론(LQR, Kalman filter 등)을 쓸 수 없다.

### 관점의 전환

Koopman(1931)의 발상은 이것이다.

> **"상태 $x$를 추적하지 말고, 상태를 측정한 값 $g(x)$를 추적하자."**

$g : \mathcal{X} \to \mathbb{C}$ 를 **[[Observable Function|관측 함수(observable)]]** 라 하고, 이런 함수들이 모인 벡터공간을 $\mathcal{F}$ 라 하자. 그러면 Koopman 연산자 $\mathcal{K} : \mathcal{F} \to \mathcal{F}$ 는 **함수 합성(composition)** 으로 정의된다.

$$
\boxed{\;\mathcal{K}g = g \circ T, \qquad \forall g \in \mathcal{F}\;}
$$

$\circ$ 는 함수 합성이다. 이걸 특정 시점 $x_t$ 에서 평가하면 의미가 명확해진다.

$$
[\mathcal{K}g](x_t) = (g \circ T)(x_t) = g\big(T(x_t)\big) = g(x_{t+1})
$$

**즉, $\mathcal{K}$ 는 "관측값을 한 스텝 앞으로 밀어주는" 연산자다.**

### 왜 선형인가 (증명)

$\mathcal{K}$ 가 선형이라는 것은 다음을 보이면 된다. $g_1, g_2 \in \mathcal{F}$, $\alpha, \beta \in \mathbb{C}$ 에 대해

$$
\begin{aligned}
[\mathcal{K}(\alpha g_1 + \beta g_2)](x)
&= (\alpha g_1 + \beta g_2)\big(T(x)\big) \\
&= \alpha\, g_1\big(T(x)\big) + \beta\, g_2\big(T(x)\big) \\
&= \alpha\,[\mathcal{K}g_1](x) + \beta\,[\mathcal{K}g_2](x)
\end{aligned}
$$

> [!important] 선형성의 출처
> $T$ 자체는 여전히 비선형이다. 선형성은 **$T$의 성질이 아니라, "함수 합성"이라는 연산이 함수공간 위에서 선형이라는 성질**에서 나온다. 즉 우리는 비선형성을 없앤 게 아니라, **비선형성을 "무한차원"이라는 비용으로 교환**한 것이다.

---

## 2. 그림으로 보는 두 경로 (논문 Fig. 2)

![[koopman-operator-theory-overview.png]]

그림의 층위를 아래에서 위로 읽으면 이론의 논리 순서가 그대로 나온다.

| 층위 | 그림의 요소 | 의미 |
|:---|:---|:---|
| **아래** | `Original Domain x∈X`, 회색 박스, 굽은 곡면 | 우리가 실제로 가진 것: 상태 $x_t$ 와 **Unknown Nonlinear Map $T$**. 회색 = 모른다 |
| **가운데** | 노란 화살표 `x → g(x)` | **리프팅** — 굽은 곡면을 평평한 평면으로 편다 |
| **위** | `Lifted Domain: Koopman Space`, 파란 박스 | Observable $g(x_t)$ 가 **Linear Operator $\mathcal{K}$** 로 전파 → $g(x_{t+1})=[\mathcal{K}g](x_t)$ |
| **좌상단** | `Infinite-dimensional vector space` | **치른 대가** |
| **좌상단** | `Finite Estimation K from measurements` | **타협점** — 측정에서 유한차원 $K$ 추정 → [[EDMD]] |

> [!important] 그림의 기하학적 핵심
> 왼쪽의 **굽은 곡면 → 평평한 파란 평면** 시각화가 리프팅의 본질이다. 원 상태공간에서 비선형 다양체 위를 기어가던 궤적이, 리프팅 공간에서는 **평면 위의 직선적 진화**가 된다. 좌표계를 바꿨을 뿐 궤적 자체는 같다.

같은 결과에 도달하는 **두 개의 경로**가 있다.

| 경로 | 방식 | 특성 |
|:---|:---|:---|
| 아래 경로 (bottom route) | $x$ 를 $T$ 로 전파한 뒤 $g$ 로 관측 | 원 상태공간, **저차원 + 비선형** |
| 위 경로 (top route) | $g$ 로 리프팅한 뒤 $\mathcal{K}$ 로 전파 | Koopman 공간, **고차원(무한) + 선형** |

$T$ 와 $\mathcal{K}$ 는 **서로 다른 공간에서 작용하지만 동일한 동역학을 encode** 한다. 이것이 논문에서 말하는 "equivalence / substitution"이다.

---

## 3. 무한차원 문제와 유한차원 근사

### $\mathcal{F}$ 는 왜 무한차원이 되는가

$\mathcal{K}$ 가 well-defined 되려면 $\mathcal{F}$ 가 **$T$와의 합성에 대해 닫혀(closed) 있어야** 한다. 즉 $g \in \mathcal{F} \Rightarrow g \circ T \in \mathcal{F}$.

문제는 여기서 우리가 "전체 상태값을 반환하는 함수 $g_i(x) = x_i$ 는 반드시 포함하고 싶다"고 요구하면, $T$가 비선형인 이상 $x_i \circ T$, $x_i \circ T \circ T$, ... 가 계속 새로운 함수를 만들어내며 $\mathcal{F}$ 를 무한차원으로 밀어붙인다는 점이다.

### 해법: [[Koopman-Invariant Subspace|불변 부분공간]]

무한차원을 피하려면 **유한차원이면서 $\mathcal{K}$ 에 대해 불변인 부분공간** $\mathcal{S} \subseteq \mathcal{F}$ 를 찾으면 된다.

$$
\mathcal{S} \text{ is Koopman-invariant} \iff \mathcal{K}g \in \mathcal{S},\ \ \forall g \in \mathcal{S}
$$

$\mathcal{S}$ 가 유한차원이면, 그 위에 제한된 연산자 $\mathcal{K}|_{\mathcal{S}} : \mathcal{S} \to \mathcal{S}$ 는 **행렬로 표현 가능**하다. $\psi$ 를 $\mathcal{S}$ 의 기저를 원소로 갖는 벡터값 함수라 하면, 어떤 행렬 $K \in \mathbb{C}^{\dim(\mathcal{S}) \times \dim(\mathcal{S})}$ 가 존재해서

$$
\mathcal{K}\psi = \psi \circ T = K\psi \tag{논문 (4)}
$$

여기에 $\mathcal{K}\psi(x_t) = \psi(x_{t+1})$ 을 결합하면 **드디어 유한차원 선형 시스템**이 나온다.

$$
\boxed{\;\psi(x_{t+1}) = K\,\psi(x_t)\;} \tag{논문 (5)}
$$

$z_t := \psi(x_t)$ 로 두면 그냥 익숙한 선형 상태방정식이다.

$$
z_{t+1} = K z_t
$$

> [!tip] full-state observability
> 만약 $\mathcal{S}$ 가 상태 observable $g_i(x) = x_i$ 를 모두 포함한다면, 기저 $\psi$ 를 $\psi = [x_1, \dots, x_{N_x}, \text{(추가 함수들)}]^\top$ 형태로 잡을 수 있다. 이 경우 리프팅된 선형 시스템 (5)는 원 비선형 시스템 (1)의 **정보를 완전히 보존**한다. 논문 각주 4의 "full-state observability assumption"이 이것이다. 실무적으로 이게 중요한 이유는, 리프팅 공간에서 제어를 설계한 뒤 **$z$ 의 앞부분만 읽으면 바로 원 상태 $x$ 를 복원**할 수 있기 때문이다 (디코더가 필요 없음).

---

## 4. 스펙트럼 분해 — 고유함수/고유값

행렬 $K$ 의 고유분해는 곧 Koopman 연산자의 스펙트럼 정보를 준다.

**Koopman 고유함수(eigenfunction)** $\phi$ 와 고유값 $\lambda$ 는 다음을 만족한다.

$$
\mathcal{K}\phi = \lambda \phi \quad\Longleftrightarrow\quad \phi(T(x)) = \lambda\,\phi(x)
$$

이게 강력한 이유: 고유함수를 따라가면 **동역학이 스칼라 곱셈으로 축소**된다.

$$
\phi(x_t) = \lambda^t \phi(x_0)
$$

즉 $|\lambda| < 1$ 이면 그 성분은 감쇠, $|\lambda| = 1$ 이면 지속 진동, $|\lambda| > 1$ 이면 발산이다. **비선형 시스템의 안정성/불변량 분석을 선형대수의 언어로 할 수 있게 된다.** 자세한 내용은 [[Koopman Eigenfunction]] 참고.

---

## 5. 로보틱스에서 왜 매력적인가 (논문 I절)

| 장점 | 내용 |
|:---|:---|
| **Interpretability** | (deep) NN의 블랙박스 입출력 매핑과 달리, 기하학적·대수적 성질에 뿌리를 둔 **동역학 모델 기술**을 준다. 근사 성능을 설명할 수 있다. |
| **Data-efficiency** | NN 계열 대비 **적은 수의 측정만** 요구 → 실시간 구현에 적합. |
| **Linear representation** | 선형 시스템 도구(LQR, MPC, Kalman filter, 안정성 증명)를 **그대로** 쓸 수 있다. |

논문이 던지는 동기 질문은 이것이다.

> "로봇이 오프라인 데이터에 크게 의존하지 않고 새로운 환경에서 동작해야 한다면, **'small data'만으로 runtime learning** 을 할 수 있는 도구는 무엇인가?"

Koopman은 이 질문에 대한 부분적 답이다. (7)식의 **닫힌 형태 해(closed-form)** 덕분에 모델 학습이 NN 대비 수 자릿수 빠르며, 온라인 증분 업데이트가 가능하기 때문이다.

---

## 6. 연속시간 버전 (논문 V-A절)

연속시간 시스템 $\dot{x} = G(x)$ 의 경우, 시간 $t$ 에 대한 flow map $G^t$ 를 통해 연산자 족(family) $\{\mathcal{K}^t\}_{t \ge 0}$ 을 정의한다.

$$
\mathcal{K}^t f = f \circ G^t
$$

이 족이 **강연속 반군(strongly continuous semigroup)** 조건

1. $\mathcal{K}^0 = \mathrm{id}$
2. $\mathcal{K}^{t_1 + t_2} = \mathcal{K}^{t_1}\mathcal{K}^{t_2}$
3. $\lim_{t \to 0}\|\mathcal{K}^t f - f\| = 0$

을 만족하면, **무한소 생성자(infinitesimal generator)** = **Koopman generator** $\mathcal{L}_G$ 를 정의할 수 있다.

$$
\mathcal{L}_G f := \lim_{t \to 0}\frac{\mathcal{K}^t f - f}{t} = G \cdot \nabla f \tag{논문 (20)}
$$

> [!note] 직관
> $\frac{d}{dt}f(x(t)) = \nabla f \cdot \dot{x} = \nabla f \cdot G(x)$ — 즉 **연쇄법칙(chain rule) 그 자체**다. 이산시간의 $\mathcal{K}$ 가 "한 스텝 밀기"라면, 연속시간의 $\mathcal{L}_G$ 는 "궤적을 따른 방향 미분(Lie derivative)"이다.

---

## 7. 자주 하는 오해

> [!warning] 오해 1: "Koopman은 비선형성을 없앤다"
> 아니다. **무한차원과 맞바꾼 것**이다. 유한차원으로 자르는 순간 근사 오차가 생기고, 그 오차의 크기는 고른 딕셔너리가 **얼마나 불변 부분공간에 가까운지**에 달려 있다. → [[Koopman-Invariant Subspace]]

> [!warning] 오해 2: "딕셔너리를 크게 할수록 좋다"
> 논문이 명시적으로 반박한다. 예: 선형 시스템 $x^+ = 0.5x$ 에 대해 $\psi_1(x) = x$, $\psi_2(x) = [x, \sin(x)]$ 를 비교하면, $\mathrm{span}(\psi_1) \subset \mathrm{span}(\psi_2)$ 임에도 **$\psi_1$ 의 예측은 정확**($\mathrm{span}(\psi_1)$이 불변이므로)하고 **$\psi_2$ 는 일부 함수에 대해 큰 오차**를 낸다. 부분공간을 키우는 것과 불변성에 가까워지는 것은 별개다.

> [!warning] 오해 3: "EDMD 행렬 = Koopman 연산자"
> 아니다. $K_{\mathrm{EDMD}}$ 는 Koopman 연산자 자체가 아니라, **$\mathrm{span}(\psi)$ 위로 사영된 연산자의 작용**을 encode 한다. → [[EDMD]]

---

## Related Notes
> [!tip] 관련 노트
> - [[Observable Function]] — 리프팅 함수, 딕셔너리
> - [[Koopman-Invariant Subspace]] — 유한차원 정확성의 조건
> - [[Koopman Eigenfunction]] — 스펙트럼 관점
> - [[EDMD]] — 데이터로 $K$ 추정하기
> - [[HVOK]] — 시간지연 임베딩 대안
> - [[Koopman with Control Input]] — 입력이 있는 시스템 확장
> - [[Koopman MPC]] — 제어 응용
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
