---
date: 2026-07-28
status: Paper Review
tags:
  - PaperReview
  - Koopman
  - Robotics
  - Seminar
aliases:
  - Koopman Operators in Robot Learning
  - 쿠프만 논문 리뷰
keywords: Koopman operator, robot learning, EDMD, MPC, lifting function, runtime learning
related notes: "[[Koopman Operator]], [[EDMD]], [[Koopman MPC]]"
reference: "IEEE Transactions on Robotics, vol. 42, pp. 1088-1105, 2026"
author: Lu Shi, Masih Haseli, Giorgos Mamakoukas, Daniel Bruder, Ian Abraham, Todd Murphey, Jorge Cortés, Konstantinos Karydis
url: https://doi.org/10.1109/TRO.2026.3654384
dg-publish: false
---

# 📄 Koopman Operators in Robot Learning

> [!info] 서지 정보
> - **저자**: Lu Shi, Masih Haseli, Giorgos Mamakoukas, Daniel Bruder, Ian Abraham, Todd Murphey, Jorge Cortés, Konstantinos Karydis
> - **소속**: UC Riverside / Tsinghua AIR, UC San Diego, Zoox, U. Michigan, Yale, Northwestern
> - **저널**: *IEEE Transactions on Robotics*, vol. 42, pp. 1088–1105, 2026
> - **DOI**: [10.1109/TRO.2026.3654384](https://doi.org/10.1109/TRO.2026.3654384)
> - **투고**: 2025-05-20 / **수정**: 2025-11-24 / **게재**: 2026-01-15
> - **유형**: **Survey / Review** (튜토리얼 코드 포함)
> - **코드**: https://github.com/sunnyshi0310/KoopmanRobo ([Colab로 바로 실행](https://colab.research.google.com/github/sunnyshi0310/KoopmanRobo/blob/main/demo.ipynb))
> - **▶ 실행 예제**: [[Koopman 예제 코드|🧪 단계별 실행 스크립트]] — 이 저장소를 개념 노트 단계에 맞춰 재구성하고 실행 검증한 것

---

## 🎯 한 눈에 보기

> [!abstract] TL;DR
> 비선형 로봇 동역학을 **고차원 함수공간의 선형 연산자**로 표현하는 [[Koopman Operator|Koopman 연산자 이론]]의 로보틱스 적용을 총정리한 리뷰. **"오프라인 빅데이터 없이, small data로 runtime learning이 가능한 도구는 무엇인가"** 라는 질문에 Koopman이 부분적 답이라고 주장하며, 이론(§II, §V) → 파이프라인(§III) → 플랫폼별 사례(§IV) → 열린 문제(§VI) 순으로 전개한다.
>
> **핵심 등식 한 줄**: $\ \psi(x_{t+1}) = K\psi(x_t) + Bu_t\ $ — 비선형 시스템이 리프팅 공간에서 **선형 상태방정식**이 된다.

### 논문 구조 지도

| 절 | 내용 | 관련 개념 노트 |
|:---|:---|:---|
| **§I** | 동기 — runtime learning, small data 문제 | — |
| **§II-A** | Koopman 기초 이론 | [[Koopman Operator]], [[Observable Function]], [[Koopman-Invariant Subspace]] |
| **§II-B** | 데이터 기반 추정 — EDMD, HVOK | [[EDMD]], [[HVOK]] |
| **§II-C** | 입력이 있는 시스템 (실용적 근사 3가지) | [[Koopman with Control Input]] |
| **§III** | 로보틱스 파이프라인 — 데이터 수집 → 리프팅 설계 → 다운스트림 | [[Observable Function]], [[Koopman MPC]] |
| **§IV** | 플랫폼별 구현 사례 (manipulator ~ multiagent) | — |
| **§V** ⭐ | **심화 이론 — 이 논문의 이론적 본체**<br>§V-A 연속시간 generator / §V-B KCF·input-state separable / §V-C 딕셔너리 품질 | [[Koopman Operator]], [[Koopman with Control Input]], [[Consistency Index]], [[Koopman-Invariant Subspace]] |
| **§VI** | 열린 문제 8가지 | — |

---

## 1. 문제의식 — 왜 지금 Koopman인가 (§I)

### 논문이 던지는 동기 질문

> *"로봇이 — 물리적 몸체와 embodied learning 제약을 가진 채로 — 오프라인 데이터에 크게 의존하지 않고 novel한 환경에서 동작해야 한다면, **'small data'만으로 runtime learning** 을 할 수 있는 도구는 무엇인가?"*

이 질문의 배경에는 현행 로봇 학습의 구조적 한계가 있다. Neural ODE [1], deep RL [2], generative AI [3] 등은 모두 **고충실도 시뮬레이터로 오프라인 수집한 대량 데이터**에 의존한다. 그런데 실제 배치 환경은 다음 세 가지 특성을 갖는다.

1. **Novel** — 사전 데이터셋이 예상하지 못한 현상
2. **Unmodelable** — 제1원리로 모델링 불가 (인간 의도, 소프트 물질, 난류, 촉각 기계수용)
3. **Unsimulable** — 시뮬레이션의 복잡도가 비현실적 (Navier–Stokes 급) 이거나 파라미터·경계조건이 **알 수 없고 알 수도 없는** 경우

> [!note] 저자들의 프레이밍
> 지난 10년간 딥러닝 강조가 로보틱스를 "big data" 의존으로 몰아갔고, 그 결과 **레이블링된 오프라인 데이터 위에서 느리게 도는 알고리즘**에 갇혔다는 진단이다. (비전이 주 센싱 모달리티가 된 것도 레이블 이미지의 대량 가용성 때문이라고 지적한다.) 이 논문은 그 흐름에 대한 **대안 축**으로 Koopman을 제시한다.

### Koopman의 세 가지 이점 (§I)

| 이점 | 내용 |
|:---|:---|
| **Interpretability** | (딥) NN이 입출력 관계를 블랙박스로 표현하는 것과 달리, **원리적 기하학·대수 성질에 뿌리 둔 동역학 모델 기술**을 제공. 데이터 기반 근사의 성능을 **설명**할 수 있다. |
| **Data-efficiency** | NN 계열 대비 **제한된 수의 측정만** 요구 → 실시간 구현에 적합 |
| **Linear representation** | 선형 시스템 도구(LQR, MPC, Kalman filter, 안정성 증명)를 **그대로** 사용 |

**Formal properties**도 강조된다: 미지 모델에 물리적으로 유의미한 성질(안정성, 불변성, 대칭성)을 부여, 연속적 능동학습을 위한 **정보 측도 직접 계산**, 비선형 시스템에 선형 제어 기법 적용, 안정성 증명 용이성(constructive control Lyapunov function [18]), 샘플 효율 보장.

> [!tip] 기존 리뷰와의 차별점
> 저자들이 밝히는 포지셔닝: 기존 리뷰들은 데이터 기반 방법론 [19], 연산자 기반 알고리즘 [20], 이론 분석 중심 [21][22][23], 제어기 설계 [24], 또는 소프트 로보틱스 전용 [25]이었다. 이 논문은 **Koopman + 로보틱스 전반**을 이론부터 플랫폼별 구현까지 잇는 종합 입문서를 지향한다.

---

## 2. 이론적 토대 (§II-A)

> 📎 상세: [[Koopman Operator]], [[Observable Function]], [[Koopman-Invariant Subspace]]

### 핵심 정식화

이산시간 비선형 시스템

$$
x_{t+1} = T(x_t), \qquad x\in\mathcal{X}\subseteq\mathbb{R}^{N_x} \tag{1}
$$

관측 함수 $g\in\mathcal{F}$ 에 대한 Koopman 연산자 $\mathcal{K}:\mathcal{F}\to\mathcal{F}$:

$$
\mathcal{K}g = g\circ T \tag{2}
$$

$$
[\mathcal{K}g](x_t) = g(T(x_t)) = g(x_{t+1}) \tag{3}
$$

**유한차원 불변 부분공간** $\mathcal{S}\subseteq\mathcal{F}$ 위에서 기저 $\psi$ 를 잡으면 행렬 표현이 존재한다.

$$
\mathcal{K}\psi = \psi\circ T = K\psi \tag{4}
$$

$$
\boxed{\ \psi(x_{t+1}) = K\,\psi(x_t)\ } \tag{5}
$$

$z_t := \psi(x_t)$ 로 두면 $z_{t+1} = Kz_t$ — **완전한 선형 상태방정식**.

> [!important] 이 논문을 읽을 때 놓치면 안 되는 것
> **선형성은 공짜가 아니다.** $\mathcal{F}$ 가 $T$와의 합성에 대해 닫혀 있으려면 (전체 상태값을 반환하는 함수를 포함시키려는 순간) **무한차원**이 되어야 한다. 우리는 비선형성을 제거한 게 아니라 **차원과 맞바꾼 것**이다.
>
> 이후 논문의 거의 모든 기술적 내용은 결국 **"어떻게 유한차원으로 잘라도 정확할 것인가"** 라는 하나의 질문으로 수렴한다.

### Fig. 2의 가환도 — 이 논문 전체를 요약하는 한 장

![[koopman-operator-theory-overview.png]]

> [!note] 그림 읽는 법 — 아래에서 위로
> **① 아래쪽 (Original Domain $x\in\mathcal{X}$)**
> 회색 박스. 우리가 실제로 가진 것은 상태 $x_t$ 와, 그것을 $x_{t+1}$ 로 보내는 **Unknown Nonlinear Map $T$** 뿐이다. 화살표가 회색인 이유는 **$T$ 를 모른다**는 뜻이다 — 소프트 로봇의 점탄성이나 공중 로봇의 지면 효과처럼 제1원리로 쓸 수 없는 동역학이 여기 있다.
>
> **② 가운데 노란 화살표 (Lifting)**
> $x \to g(x)$. **[[Observable Function|리프팅 함수]]** 가 상태를 함수공간으로 밀어 올린다. 왼쪽 그림의 **굽은 곡면(원 상태공간)이 평평한 파란 평면(Koopman 공간)으로 펴지는** 시각화가 이 연산의 기하학적 의미다. 비선형 다양체가 선형 부분공간으로 대응된다.
>
> **③ 위쪽 (Lifted Domain: Koopman Space)**
> 파란 박스. Observable $g(x_t)$ 가 **Linear Operator $\mathcal{K}$** 로 전파되어 $g(x_{t+1}) = [\mathcal{K}g](x_t)$ 가 된다. 이것이 (3)식이다. 화살표가 파란색·실선인 이유는 **$\mathcal{K}$ 가 선형이고 데이터로 추정 가능**하기 때문이다.
>
> **④ 왼쪽 상단 텍스트 — 대가와 해법**
> - *Linear Dynamics $\mathcal{K}$* : 얻은 것 (선형성)
> - *$g\in\mathcal{F}$: Infinite-dimensional vector space* : **치른 대가** (무한차원)
> - *Finite Estimation $K$ from measurements* : **타협점** — 측정으로부터 유한차원 행렬 $K$ 를 추정 → (7)식 [[EDMD]]

> [!important] 이 그림에서 놓치기 쉬운 두 가지
> **1. 오른쪽 세로 점선이 핵심이다.** 두 경로($T$ 를 따라간 뒤 관측 vs. 관측한 뒤 $\mathcal{K}$ 로 전파)가 **같은 지점에서 만난다**는 것 — 즉 $T$ 와 $\mathcal{K}$ 는 다른 공간에서 작용하지만 **동일한 동역학을 encode** 한다. 이 가환성(commutativity)이 Koopman 이론의 전부다.
>
> **2. 그림에는 "Finite Estimation $K$"만 적혀 있고 그 오차는 그려져 있지 않다.** 실제로 유한차원으로 자르는 순간 위쪽 경로와 아래쪽 경로는 **정확히 만나지 않는다.** 그 어긋남의 크기를 결정하는 것이 [[Koopman-Invariant Subspace|불변 부분공간]]에 얼마나 가까운지이며, 그것을 측정하는 지표가 [[Consistency Index]]다. **이 논문의 §V-C 전체가 이 그림에 그려지지 않은 간극에 관한 것이다.**

---

## 3. 데이터 기반 추정 (§II-B)

> 📎 상세: [[EDMD]], [[HVOK]]

### EDMD — 이 논문의 계산적 심장

> [!abstract] 한 문장 요약
> EDMD는 **"상태를 딕셔너리로 들어올린 뒤 → 그 공간에서 선형 관계를 최소자승($K = \Psi(Y)\Psi(X)^\dagger$)으로 한 번에 푸는 것"** 이며, 정확도의 열쇠는 **딕셔너리 크기가 아니라 선택한 부분공간이 Koopman-불변에 얼마나 가까운가**입니다.

아래 1~8번을 순서대로 읽으면 EDMD가 왜 그렇게 생겼는지가 쌓입니다.

#### 1. 데이터 행렬 구성

먼저 시스템 $x_{t+1} = T(x_t)$ 에서 데이터를 모읍니다.

$$
X = [\,x_1, x_2, \ldots, x_M\,], \qquad Y = [\,y_1, y_2, \ldots, y_M\,]
$$

여기서 $y_i = T(x_i)$ 입니다. 즉 **$X$ 는 "현재 상태들", $Y$ 는 그 "한 스텝 뒤 상태들"** 입니다. 실제로는 하나의 궤적을 시간축으로 밀어서 $Y = [x_2, \ldots, x_{M+1}]$ 처럼 쓸 수도 있습니다.

#### 2. 리프팅 (Lifting)

핵심 아이디어는 상태 $x$ 를 그대로 쓰지 않고, **관측함수(딕셔너리) $\Psi$ 로 더 높은 차원으로 "들어올리는"** 것입니다. 예를 들어 $\Psi(x) = [x,\ x^2,\ \sin(x), \ldots]$ 같은 형태입니다.

$$
\Psi(X) = [\,\Psi(x_1),\ \Psi(x_2),\ \ldots,\ \Psi(x_M)\,]
$$

즉 각 데이터 포인트마다 딕셔너리를 적용한 결과를 **열로 쌓은 행렬**입니다. (세로 = 리프팅 차원 $N_\Psi$, 가로 = 데이터 개수 $M$. 보통 $M \gg N_\Psi$)

#### 3. 최소자승 문제 (식 6)

우리가 원하는 것은 리프팅된 공간에서 선형 관계 $\Psi(x_{t+1}) \approx K\Psi(x_t)$ 를 만족하는 $K$ 를 찾는 것입니다. 이를 오차 최소화 문제로 표현합니다.

$$
\underset{K}{\text{minimize}}\ \ \big\|\Psi(Y) - K\Psi(X)\big\|_F \tag{6}
$$

$\|\cdot\|_F$ 는 **Frobenius 노름**(행렬 원소들의 제곱합의 제곱근)입니다. 쉽게 말해 **"$K\Psi(X)$ 가 $\Psi(Y)$ 에 최대한 가깝도록"** 하는 $K$ 를 찾는 것입니다.

#### 4. 닫힌 형태 해 (식 7)

이 선형 최소자승 문제는 **명시적인 해**를 가집니다.

$$
\boxed{\ K_{\mathrm{EDMD}} = \Psi(Y)\Psi(X)^{\dagger}\ } \tag{7}
$$

여기서 $\dagger$ 는 **의사역행렬(pseudo-inverse)** 입니다 → 📎 [[Pseudo-inverse]]

> [!success] 왜 이 한 줄이 로보틱스에서 중요한가
> **딥러닝처럼 반복 학습이 필요 없고 한 번의 행렬 연산으로 구해집니다.** SVD 한 번이면 끝.
> - 논문 [68] 보고: 학습 단계가 경쟁 데이터 기반 방법 대비 **수 자릿수(orders of magnitude) 빠름**
> - [17]의 online DMD 변형: 시변 시스템에 대해 **실시간 연산자 갱신** 가능
> - → 이것이 §I의 "runtime learning" 주장을 실제로 뒷받침하는 계산적 근거다

#### 5. 예측자(predictor) (식 8, 9)

딕셔너리 스팬 안의 함수 $f(\cdot) = v_f^\top\Psi(\cdot)$ 에 대해, $\mathcal{K}f$ 의 근사 예측은

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}f} := v_f^\top K_{\mathrm{EDMD}}\Psi \tag{8}
$$

특히 $v_\phi$ 가 $K_{\mathrm{EDMD}}$ 의 **좌고유벡터**($v_\phi^\top K_{\mathrm{EDMD}} = \lambda_\phi v_\phi^\top$)이면, 근사 [[Koopman Eigenfunction|Koopman 고유함수]]를 얻습니다.

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}\phi} = v_\phi^\top K_{\mathrm{EDMD}}\Psi = \lambda_\phi v_\phi^\top\Psi = \lambda_\phi\phi \tag{9}
$$

즉 **고유함수 $\phi$ 는 시간에 따라 단순히 고유값 $\lambda_\phi$ 로 스케일되며 진화한다**는 뜻입니다 ($\phi(x_t) = \lambda_\phi^t\phi(x_0)$) — 이것이 Koopman의 "선형성" 매력의 핵심입니다.

#### 6. 개념적으로 가장 중요한 포인트

> [!danger] $K_{\mathrm{EDMD}} \ne \mathcal{K}$
> $K_{\mathrm{EDMD}}$ 는 **진짜 Koopman 연산자 $\mathcal{K}$ 자체가 아닙니다.** 이것은 $\mathcal{K}$ 의 작용을 $\mathrm{span}(\Psi)$ 위로 **직교 투영(projection)** 한 것을 인코딩합니다.
> $$\mathcal{P}_{\mathrm{span}(\Psi)}\mathcal{K} : \mathcal{F}\to\mathcal{F} \tag{10}$$
> 투영은 **경험적 측도** 기반 $L_2$ 내적으로 정의됩니다.
> $$\mu_{\mathcal{X}} = \frac{1}{M}\sum_{i=1}^{M}\delta_{x_i} \tag{11}$$
> 데이터 포인트마다 디랙 측도를 놓은 것이니, **"가진 데이터 위에서만 오차를 재는 투영"** 이라고 이해하면 됩니다.

**수렴성** [30]: 딕셔너리·데이터가 커지면 연산자 위상에서 수렴, 고유값 포착, 고유함수 약수렴. **다만 이 수렴성이 실용적 성능을 보장하지는 않습니다** — 바로 다음 항목입니다.

#### 7. 딕셔너리 선택의 미묘함

> [!danger] 논문이 반복 강조하는 반직관적 사실
> **"딕셔너리를 크게 만든다고 항상 좋은 것은 아닙니다."**
>
> 예시로 선형 시스템 $x^+ = 0.5x$ 를 봅시다.
>
> | 딕셔너리 | 부분공간 | 결과 |
> |:---|:---|:---|
> | $\Psi_1(x)=x$ | 작음 | **Koopman-불변** → 예측 **정확(exact)** ✅ |
> | $\Psi_2(x)=[x,\sin(x)]$ | **더 큼** | 불변 아님 → 일부 함수에서 **큰 오차** ❌ |
>
> $\mathrm{span}(\Psi_1)\subset\mathrm{span}(\Psi_2)$ 인데도 **작은 쪽이 이깁니다.** 즉 오차는 **부분공간의 크기가 아니라 $\mathrm{span}(\Psi)$ 가 얼마나 [[Koopman-Invariant Subspace|Koopman-불변]]에 가까운가**에 달려 있습니다.
>
> 게다가 **시스템 모델 없이는 목표 정확도를 위한 딕셔너리 차원의 하한을 추정할 방법조차 없습니다.** → 딕셔너리는 반드시 **시스템/데이터 정보에 기반해 설계·학습**되어야 합니다.

#### 8. DMD와의 관계 (Remark 1)

DMD는 원래 **유체 흐름의 특징(coherent feature)을 뽑기 위해** 나온 방법입니다 [34]. EDMD보다 **먼저** 개발되었지만, exact DMD는 **리프팅이 없는 EDMD의 특수한 경우**로 볼 수 있습니다. 즉 딕셔너리를 항등함수 $\Psi(x)=x$ 로 두면 DMD가 됩니다.

$$
K_{\mathrm{DMD}} = YX^{\dagger}
$$

DMD는 "데이터에 가장 잘 맞는 선형 시스템 행렬"을 구하는 것이고, EDMD는 **그것을 리프팅된 공간에서** 하는 것입니다.

### HVOK — 딕셔너리 설계를 우회하는 길

$$
H_X = \begin{bmatrix} x_1&\cdots&x_{m-d}\\ x_2&\cdots&x_{m-d+1}\\ \vdots&\ddots&\vdots\\ x_d&\cdots&x_{m-1}\end{bmatrix},\quad
H_Y = \begin{bmatrix} x_2&\cdots&x_{m-d+1}\\ x_3&\cdots&x_{m-d+2}\\ \vdots&\ddots&\vdots\\ x_{d+1}&\cdots&x_{m}\end{bmatrix}
$$

$$
H_Y \approx K_{\mathrm{HVOK}} H_X
$$

**Takens형 관측가능성 논변**에 기반. 명시적 기저 설계 대신 **시간적 리프팅**으로 암묵적 특징공간을 구성한다. 부분 관측되거나 강한 비선형 시스템에서 **더 안정적인 Koopman 추정**을 낳는 경우가 많다. → 소프트/공중 로봇에서 선호. 📎 [[HVOK]]

---

## 4. 입력이 있는 시스템 — 실용적 근사 (§II-C)

> 📎 상세: [[Koopman with Control Input]]

### 근본적 난점

> [!important] 상태와 입력의 비대칭
> - **상태**: 시스템의 내재적 속성, 내부 동역학에 따라 진화 → Koopman이 다룰 수 있음
> - **입력**: 개루프에서는 사전에 알 수 없고, **정해진 동역학 규칙을 따르지 않음** → Koopman 구조로 표현 불가
>
> Koopman은 원래 **unforced 시스템**을 위해 만들어졌다. 이것이 모든 어려움의 근원이다.

### 실용적 근사 3가지 (§II-C)

| 방식 | 형태 | 장점 | 단점 |
|:---|:---|:---|:---|
| **① Joint lifting** | $g(x,u)$ 결합 공간 | 직관적·간단 | **미래 입력 가정**, 임의 입력에 일반화 실패 |
| **② Input-affine** ⭐ | $g(x_{t+1})\approx Kg(x_t)+Bu_t$ | **선형 구조 보존** → LQR/MPC 직결 ([[Affine]]) | 아핀성은 근사일 뿐 |
| **③ Control-coherent** [37] | 입력 변화에도 일관된 임베딩 | 새 제어 시퀀스로 **일반화 우수** | 최신 기법, 비용 |

**②가 지배적**이다. 결과가 완전한 선형 상태공간 모델이므로 고전 제어 도구를 문자 그대로 쓸 수 있기 때문이다. 논문은 이것이 [36]의 **input-state separable model의 특수 사례**임을 짚어, 임시방편이 아니라 이론적 배경이 있음을 명확히 한다.

### 이 근사들의 이론적 근거는?

위 3종은 **왜 그렇게 해도 되는지**에 대한 근거가 여기까지는 없다. 논문은 그것을 §V-B로 미루며, 거기서 두 가지 엄밀한 프레임(**무한 입력 시퀀스** [105], **Koopman Control Family** [36])을 제시한다.

특히 KCF의 **input-state separable form** $\psi(x^+)=A(u)\psi(x)$ 이 위 ②를 포함한 실무 모델 전부를 특수 사례로 포섭한다는 것이 이 논문의 이론적 하이라이트다.

> 📎 **→ 아래 [7-B. 제어 입력의 엄밀한 처리](#7-b-제어-입력의-엄밀한-처리-v-b)에서 (21)~(26)식과 함께 상세히 다룬다.** 상세 노트: [[Koopman with Control Input]]

---

## 5. 로보틱스 파이프라인 (§III)

논문이 제시하는 3단계 파이프라인:

```
① 데이터 수집  →  ② 리프팅 함수 설계/선택  →  ③ 다운스트림 태스크
   (§III-A)          (§III-B)                    (제어 §III-C / 추정 §III-D / 계획 §III-E)
```

### ① 데이터 수집 (§III-A)

| 방법 | 내용 | 적용 |
|:---|:---|:---|
| **무작위 선택** [61] | 랜덤 초기조건·입력으로 전파. **persistent excitation** 확보를 위해 로봇의 전체 동작 범위에서 샘플링 [95][97] | 소프트 로봇 [62][70][99] — 공격적 명령이 나와도 주변에 해가 적음. 안전을 위해 밀폐 공간 필요할 수 있음 [98] |
| **반복 정제** | 베이스라인 제어기(개루프·naive 가능)에서 시작해 점진 개선. Folkestad et al. [78]은 **이전 에피소드 제어기로 현재 데이터 생성** | 안전한 수집 + 관측 정보량 개선 |
| **정보 가치 기반** | 최적화에 **정보 풍부성 제약**을 명시적으로 도입 → 능동학습 [100] | §III-C2와 연결 |

### ② 리프팅 함수 설계 (§III-B)

> 📎 상세: [[Observable Function]]

| 전략 | 예시 | 특성 |
|:---|:---|:---|
| **수동 선택** | 스펙트럴 요소(블록 대각 관측행렬 [27]), **Hermite 다항식**(정규분포 데이터), **RBF**(공간적으로 복잡한 동역학) | 효과적이나 **노동집약적**, 일반화 취약 |
| **물리 정보 기반** | Shi et al. [69] — configuration symmetry, workspace constraint 반영 / [90] — **고차 시간 상태 미분** | 해석 가능성 + robustness 향상. 전체 동역학 모델 없이도 가능 |
| **NN 기반** | **Deep Koopman** [102], **Autoencoder-Koopman** [16] | 높은 유연성. 단 **해석 가능성 상실, OOD 일반화 취약, overfitting** |

**플랫폼별 경향 (Table I)**:

| 플랫폼 | 선호 방식 | 이유 |
|:---|:---|:---|
| Manipulation, Legged | **NN 기반** | 동역학의 높은 복잡성·비선형성 |
| Wheeled | **수동 설계** | 동역학이 비교적 단순·잘 이해됨 |
| Aerial, Soft | 전부 (특히 **HVOK**) | 강한 환경 외란 / 느린 응답 특성 포착 |

> [!warning] 논문의 자기비판 — 이 절의 결론
> *"대부분의 방법은 엄밀한 수렴 분석이 없다 — 즉 구성된 observable들이 **Koopman 불변 부분공간을 span 하는지**, 참 연산자의 정확한 근사인지 검토하지 않는다."*
>
> 이 gap을 메우기 위해 §V-C에서 별도의 이론적 논의를 전개한다. → §7 참고

### ③-a 제어기 설계 (§III-C)

> 📎 상세: [[Koopman MPC]]

$$
\begin{aligned}
\underset{\{z_i\},\{u_i\}}{\text{min}}\ & J(\{z_i\}_{i=0}^{N_h},\{u_i\}_{i=0}^{N_h})\\
\text{s.t.}\ & z_{i+1}=F_K(z_i,u_i),\quad z_0=\psi(x_t)
\end{aligned} \tag{12}
$$

선형 실현이면 **볼록 QP**가 된다.

$$
\begin{aligned}
\underset{\{z_i\},\{u_i\}}{\text{min}}\ & \sum_{i=0}^{N_h}\big(z_i^\top G_iz_i + u_i^\top H_iu_i + g_i^\top z_i + h_i^\top u_i\big)\\
\text{s.t.}\ & z_{i+1}=Kz_i+Bu_i,\quad z_0=\psi(x_t)
\end{aligned} \tag{13}
$$

> [!success] 논문의 핵심 실용적 주장
> **볼록성 → 유일한 전역 최적해 + 초기화 불필요 + 고차원에서도 효율적 계산** [106][107][108] → **실시간 피드백 제어에 적합**.
>
> 비선형/쌍선형 실현은 (12)를 **비볼록**으로 만들어 국소 최적해만 얻고 효율이 떨어진다 [109]. 다만 예측이 더 정확해지면 그 트레이드오프가 정당화되며, 최근 쌍선형 실현 [43]이 절충안으로 탐구된다 [97].

**계보**: [104] 최초 도입 → [105] Koopman MPC → [79] Koopman NMPC → [43][97] Bilinear

### ③-b 능동학습(Active Learning) (§III-C2)

> [!abstract] 이 절이 말하는 것
> 보통의 제어기는 **"목표까지 잘 가라"** 만 시킵니다. 능동학습 제어기는 여기에 **"가는 김에 모델도 잘 배워라"** 를 더합니다. 놀라운 점은, Koopman이 선형이라서 **"얼마나 잘 배우는가"를 수식으로 쓸 수 있고, 그걸 비용함수에 그냥 넣을 수 있다**는 것입니다.

#### 왜 이게 Koopman에서만 쉬운가

[[EDMD]] 4번의 닫힌 형태 해 $K = \Psi(Y)\Psi(X)^\dagger$ 를 떠올려봅시다. 이것은 **선형 최소제곱**입니다. 선형 최소제곱은 통계학에서 가장 잘 이해된 문제이고, 특히 **추정치 $K$ 의 불확실성을 해석적으로 계산**할 수 있습니다.

신경망이라면 "이 가중치가 얼마나 확실한가"를 묻는 순간 베이지안 근사나 앙상블 같은 무거운 장치가 필요합니다. Koopman은 그냥 공식이 있습니다. **이 차이가 능동학습을 실용적으로 만듭니다.**

#### 1단계 — 결정론적 최소제곱에 확률을 도입한다

여기서 첫 번째 개념 도약이 일어납니다. EDMD는 결정론적인데 왜 갑자기 확률분포 $p(z_{t+1}|K, z_k)$ 가 나올까요?

> [!note] 최소제곱 = 가우시안 가정 하의 최대우도 추정
> 모델이 완벽하지 않으니 예측에 오차가 있습니다. 그 오차를 **평균 0, 공분산 $\Sigma$ 인 가우시안 노이즈**로 모델링하면
> $$z_{t+1} = Kz_t + Bu_t + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \Sigma)$$
> 즉 $z_{t+1}$ 은 **평균이 $Kz_t + Bu_t$ 인 정규분포**를 따릅니다.
> $$p(z_{t+1}\,|\,K, z_t) = \mathcal{N}\big(Kz_t + Bu_t,\ \Sigma\big)$$
> 이 가정 하에서 **최대우도 추정 = 최소제곱**이라는 것이 표준 결과입니다. 즉 우리가 (7)식에서 이미 하고 있던 일에 확률적 해석을 입힌 것뿐이며, 새로운 가정을 얹은 게 아닙니다.

#### 2단계 — Fisher 정보: "데이터가 $K$ 를 얼마나 알려주는가"

> 📎 Fisher 정보 자체의 정의·직관·Cramér–Rao bound는 [[Fisher Information]] 참고

$$
\mathcal{I} = \mathbb{E}\Big[\tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}\ \tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}^\top\Big] \tag{14}
$$

기호가 복잡해 보이지만 읽는 법은 단순합니다.

| 부분 | 의미 |
|:---|:---|
| $\log p(z_{t+1}\vert K, z_k)$ | **로그우도** — 현재 $K$ 로 이 관측을 얼마나 잘 설명하는가 |
| $\partial(\cdot)/\partial K$ | **score** — $K$ 를 조금 바꾸면 우도가 얼마나 민감하게 변하는가 |
| 제곱해서 기댓값 | 그 민감도의 **크기(분산)** |

> [!important] 직관: 민감할수록 많이 배운다
> $K$ 를 조금만 바꿔도 우도가 **확 달라진다**면, 그 데이터는 $K$ 를 **날카롭게 특정**합니다 → 정보가 많음.
> 반대로 $K$ 를 어떻게 바꿔도 우도가 비슷하다면, 그 데이터로는 $K$ 를 구별할 수 없습니다 → 정보가 없음.
>
> **비유**: 로봇을 직선으로만 굴리면 회전 동역학에 대해서는 아무것도 배우지 못합니다. 그 데이터의 Fisher 정보는 회전 방향으로 0입니다. 01번 예제의 **persistent excitation** 이야기와 정확히 같은 것을, 수치로 잴 수 있게 만든 것입니다.

#### 3단계 — 가우시안이면 닫힌 형태가 나온다

일반적으로 (14)의 기댓값은 계산이 어렵습니다. 그런데 1단계의 가우시안 가정 덕분에 적분이 풀립니다.

$$
\mathcal{I} = \tfrac{\partial z_{t+1}}{\partial K}^\top\Sigma^{-1}\tfrac{\partial z_{t+1}}{\partial K} \ \propto\ \mathrm{Var}[K]^{-1} \tag{15}
$$

> [!success] (15)식에서 실제로 봐야 할 것 — $\mathrm{Var}[K]^{-1}$
> **Fisher 정보 = 추정 분산의 역수.**
>
> $$\mathcal{I} \uparrow \quad\Longleftrightarrow\quad \mathrm{Var}[K] \downarrow \quad\Longleftrightarrow\quad \text{모델을 더 확실히 안다}$$
>
> 이것이 **Cramér–Rao bound** [110][111]입니다: 어떤 불편추정량도 분산이 $\mathcal{I}^{-1}$ 보다 작을 수 없습니다. 즉 Fisher 정보는 **"이 데이터로 도달 가능한 최선의 정확도"** 를 알려주는 이론적 한계선입니다.
>
> 그러니 **$\mathcal{I}$ 를 키우는 것 = 모델 불확실성의 하한을 낮추는 것**입니다.

#### 4단계 — 왜 "행동 가능(actionable)"한가

논문이 강조하는 표현입니다. 두 성질이 결합해야 제어에 쓸 수 있습니다.

| 성질 | 없으면 어떻게 되나 |
|:---|:---|
| **미분 가능** | 비용함수에 넣어도 최적화가 안 됨 (그래디언트가 없음) |
| **행동 가능** | 입력 $u$ 를 통해 $\mathcal{I}$ 를 실제로 바꿀 수 있어야 함 |

(15)를 보면 $\mathcal{I}$ 가 $z_i$ 에 의존하고, $z_i$ 는 $z_{i+1} = Kz_i + Bu_i$ 를 통해 **입력 $u$ 가 결정**합니다. 즉 **"어디로 갈지 고르면 얼마나 배울지가 정해진다"** — 그래서 최적화 대상이 됩니다. 만약 $\mathcal{I}$ 가 사후에 관찰만 되는 지표였다면 제어기가 손쓸 방법이 없었을 것입니다.

#### 5단계 — 제어기 정식화

$$
\begin{aligned}
\underset{\{u_i\}}{\text{min}}\ & \sum_{i=0}^{N_h-1}\big(\underbrace{-\mathcal{I}(z_i,{}^tK)}_{\text{① 정보를 최대화}} + \underbrace{u_i^\top Ru_i}_{\text{② 제어량은 아끼고}}\big)\\
\text{s.t.}\ & z_{i+1}={}^tKz_i+{}^tBu_i,\quad z_0=\psi(x_t)
\end{aligned} \tag{16}
$$

**읽는 법**

- **음수 부호가 핵심**입니다. $-\mathcal{I}$ 를 **최소화**한다 = $\mathcal{I}$ 를 **최대화**한다 = 정보를 최대로 얻는다
- $\mathcal{I}$ 는 행렬이므로 스칼라로 줄여야 합니다. **D-optimality**($\det\mathcal{I}$ — 불확실성 타원체의 부피), **T-optimality**($\mathrm{tr}\,\mathcal{I}$ — 축들의 합) 등을 씁니다
- 좌상첨자 ${}^tK$ 는 **지금까지 데이터로 얻은 현재 추정치**입니다. 매 스텝 갱신되므로 receding-horizon으로 반복합니다 — **모델이 좋아지면 어디서 배울지도 달라진다**는 뜻입니다

> [!important] 그래서 무슨 일이 일어나는가
> 제어기가 목표를 향해 가면서도, **모델이 아직 잘 모르는 영역 쪽으로 일부러 궤적을 틀어** 정보를 수집합니다. "탐험(exploration)과 활용(exploitation)"의 균형을 $R$ 이 조절합니다 — $R$ 이 크면 얌전히 가고, 작으면 적극적으로 탐험합니다.

**실제 사례** [100]: 공중 로봇이 **불안정한 텀블에서 빠르게 회복**하는 모델을 학습, 다리 로봇이 **granular media(모래·자갈 등) 상호작용** 모델을 학습. 둘 다 사전 모델을 세우기 어렵고 데이터 수집 기회가 제한적인 상황이라, "적은 데이터로 잘 배우는" 능력이 결정적입니다.

> [!note] 딥 관측함수와의 긴장 — 왜 딥러닝을 섞으면 오히려 손해인가
> 딥 모델로 관측함수를 근사하면 [100][112][113] 표현력은 커집니다. 그런데 **능동학습 효과는 오히려 감소**합니다.
>
> 이유는 위 3단계로 되돌아가면 명확합니다. (15)의 닫힌 형태는 **모델이 $K$ 에 대해 선형**이기에 성립했습니다. 관측함수 자체를 신경망으로 학습하면 그 선형성이 깨지고, 비선형 관측함수를 학습하는 데 더 많은 데이터가 필요해집니다 — **적은 데이터로 잘 배우자는 능동학습의 목적과 정면으로 상충**합니다.
>
> 그럼에도 순수 딥 NN 모델과 비교하면 Koopman 선형 모델은 **데이터 효율성과 능동학습 제어에서 여전히 큰 우위**를 갖습니다.

### ③-c 상태 추정 (§III-D)

세 갈래로 정리된다.

| 방향 | 대표 연구 | 내용 |
|:---|:---|:---|
| **시스템 변동성에 robust한 추정** | Dahdah & Forbes [114] | 시스템 **집단(population)** 에 대한 robust 비선형 관측기 합성. 리프팅 공간의 선형 표현 덕에 제조 편차를 **주파수 영역**에서 정량화 → **mixed $H_2/H_\infty$** 로 수십 개 모터 드라이브에 안정적 관측기 설계 |
| **외란 추정·제거** | EVOLVER [80] | 생물 시스템에서 영감. Koopman 잠재 구조 모델링을 **진화적 외란 관측기**에 결합 → 빠른 과도응답 + 고정밀 정상상태, 수렴 보장 |
| **효율적 상태 추론** | Jiang et al. [115] / **KoopSE** [98] / Huang et al. [85] | 희소 커널 Koopman 기반 **데이터 기반 Kalman filter** / control-affine 시스템의 **배치 상태 추정**(RKHS 리프팅 → 쌍선형화, Random Fourier features) / **K-ESKF** — 딥 NN으로 관측함수 학습해 쿼드로터 자세 추정 개선 |

### ③-d 계획·위치추정 (§III-E)

- **배치 SLAM 재정식화** [118]: 동역학을 리프팅해 프로세스·측정 모델을 **모두 쌍선형**으로 만듦 → 궤적과 랜드마크의 동시 추정을 제약 최적화로. 추론 중 **학습된 Koopman manifold 위의 일관성 유지**
- **지형 주행성(traversability) 모델링** [119]: 고도·경사·거칠기 특징 반영. Koopman의 **선형 쌍대(dual)** 로 문제를 **밀도 공간(density space)** 으로 올리면 **볼록**해져 최적화가 tractable
- **불확실성 인지 모션 플래너** [120]: 기댓값과 **chance constraint**를 Koopman으로 계산 → 확률적 충돌 회피. 모션 프리미티브와 결합해 위험-성능 균형

### ③-e 강건성·안정성 (§III-F)

> [!warning] 실무의 벽
> 노이즈, 제한된 관측성, 데이터 부족, 유한차원 근사의 한계 [121] 때문에 학습 모델의 부정확성이 성능을 크게 훼손한다.

**(A) 불확실성 정량화·추적**: Shi et al. [84][122] — DMD/EDMD 예측 오차의 **loose/tight bound** 유도 후 제어 설계에 통합 / [61] — Kalman filter로 불확실성 모델 증강 / Han et al. [65] — NN으로 관측값 위 분포 모델링 / Chen & Lv [123] — extended state observer를 딥 Koopman에 통합

**(B) 제약 기반 설계**: Mamakoukas et al. [124] — **가장 가까운 안정 Koopman 행렬** 계산 / [125] — 예측 성능 bound로 실행 중 적응하는 robust MPC / Wang et al. [126] — **constraint-tightening**으로 **recursive feasibility + ISS** 보장

---

## 6. 플랫폼별 구현 (§IV)

> [!info] 이 절의 성격
> 논문의 서베이 본령. Table I이 시스템 유형·학습 목표·Koopman 정식화·제어 전략을 정리한 마스터 테이블이다. 아래는 각 도메인의 **대표적 문제의식**만 압축했다.

### A. Manipulation

| 범주 | 대표 연구 | 핵심 |
|:---|:---|:---|
| 모델링·예측제어 | Hagane et al. [38] | Koopman 선형화 매니퓰레이터 + **GPC**(generalized predictive control) |
| | [39] | **Lipschitz 제약** 딥 Koopman — 정확도·해석성↑, 차원↓ |
| | [127] | **Koopman-Zeroing NN** — 오토인코더 Koopman + Cartesian 피드포워드 → 입력 제약 하 잉여 매니퓰레이터 실시간 제어 |
| RL·모방학습 | [128] | 인간 시연 궤적을 Koopman 리프팅으로 **의도 모델**화 → RL 보상 성형 (안전한 HRI) |
| | [40] | **observation-only 데이터**로 잠재 표현 학습, 선형 디코더가 실제 행동으로 매핑 → action-label 데이터 대폭 절감 |
| 객체 중심·정교조작 | **KOROL** [42] | 시각 객체 특징 추출 + **특징 공간에서 Koopman rollout** → inverse dynamics 제어기 |
| | Han et al. [41] | **손과 물체의 동역학을 결합(joint) 리프팅** → 얽힌 상호작용 포착, dexterous hand manipulation |

### B. Ground Robots

- **Wheeled**: 변형·불균일 지형에서 모델링 불확실성이 두드러짐 [129]. Koopman MPC로 복잡 지형 주행 [126], **virtual control input** [46]으로 회전·좌표변환 동역학 처리
- **Legged**: 하이브리드 동역학(이산 접촉 전환), 저구동, 고자유도 [130]. 변형 지형 위 4족 다리 동역학을 **스위칭 시스템**으로 [53]. 전신/국소 동역학 Koopman 임베딩 [50][131] — Li et al. [50]은 MPC 통합 + **증분 학습(incremental learning)** 으로 domain shift 대응. [52][51]은 **더 높은 추상 수준**에서 Koopman 활용 (아직 대부분 시뮬레이션 단계)
- **Autonomous driving** [132]: 전역 차량 동역학 모델 식별 [133] → MPC 통합 [134][135][136]. 변형 지형·범프에서 **차량+지형 상호작용 동역학의 선형 표현** 가능 [137]. 쌍선형 [138], 딥 NN 결합 [113], driver-in-the-loop [139], **확률적 Koopman + 어텐션**으로 이상행동 탐지 [140]. 전용 서베이 [141] 존재

### C. Soft & Continuum Robots ⭐ 가장 유망

> [!success] 왜 소프트 로봇이 Koopman의 킬러 앱인가
> 1. 고순응성·적응성·안전성이 장점이지만 **극도로 비선형**이라 전통 모델링이 무력
> 2. **손상 위험 없이 다양한 제어 입력으로 풍부한 데이터 수집 가능** — 강체 로봇에서 얻기 어려운 이점
> 3. → 데이터 기반 전역 선형 표현이 특히 잘 맞는다. 최근 2년간 연구가 급증했다.

리프팅: 다항식 기저 [142], **시간지연 임베딩** [72][74], NN 기반 [64][65]. 제어: **MPC** [68], **LQR** [71]이 주류. 특기할 응용 — Koopman 모델을 **RL 정책 학습용 대리 환경(surrogate environment)** 으로 사용 [67] (구축이 어려운 물리/시뮬 환경을 우회).

### D. Aerial Robots

핵심 난제는 **모델링이 어려운 공력 효과** [143] — 변동 돌풍, 착륙 시 지면 효과 [144], 저고도 비행 [145][146].

- Folkestad et al. [78]: **에피소딕 학습**으로 Koopman 고유함수 쌍 추정 → 실시간 제어 입력 생성 (멀티로터 착륙 지면 효과)
- [86]: 함수 딕셔너리와 **리프팅 Koopman 쌍선형 모델을 동시 학습** → 저고도 쿼드로터 궤적 추종. NN이 온라인 측정으로 리프팅 상태·입력 갱신
- [84]: **계층 구조** — 사전 튜닝된 고속 저수준 제어기로 가는 기준 신호를 외루프가 정제. 기준과 실제 출력의 차이를 Koopman으로 학습해 실시간 외란 저감

### E. 기타 플랫폼

굴착 로봇의 버킷-토양 상호작용 [147][148], 수중 로봇의 비정상 유동 [90][89][150] (유체 유동 Koopman [149]의 계보), 재활·보조 로봇의 하이브리드(접촉/비접촉 전환) 동역학 [91][92][151] — [16]이 이종 시스템의 **통합 전역 선형 모델**을 제시, 뱀형 로봇 [152], smarticle 앙상블 [153], 수술 로봇 [93]

### F. Multiagent Systems

튜토리얼 [154][155]. **편대 제어(formation control)** 가 핵심 — 외란 하에서 대형 유지를 위해 Koopman으로 교란된 에이전트 모델을 추정 (온라인 적응 [156] / 오프라인 학습 [157]). **연결 끊김·신호 복구** [158] — 선형 운동 진화로 리더의 결측 신호 복원. 고차원 생물/공학 **군집(swarm)** 모델링 [159] — 동질 군집의 국소 상호작용 학습.

---

## 7. 심화 이론 (§V) — 이 논문의 이론적 본체

> [!abstract] §V가 존재하는 이유
> §II는 "실무에서 이렇게들 한다"를 소개했고, §III는 그것을 로봇에 적용했다. 그런데 §III-B 말미에서 저자들은 **자기비판**을 한다 — *"대부분의 방법은 엄밀한 수렴 분석이 없다. 구성된 observable들이 실제로 Koopman-불변 부분공간을 span 하는지 검토하지 않는다."*
>
> **§V는 그 빚을 갚는 절이다.** 앞에서 실용적 편의로 넘어간 세 지점을 각각 정면으로 다룬다.
>
> | 절 | 앞에서 넘어간 것 | §V의 답 |
> |:---|:---|:---|
> | **§V-A** | 이산시간만 다뤘다 | 연속시간 정식화, **Koopman generator** |
> | **§V-B** | 입력 처리를 heuristic 3종으로 소개 | 엄밀한 두 프레임 — **무한 입력 시퀀스**와 **KCF** |
> | **§V-C** | "딕셔너리는 잘 고르세요" | 품질을 재는 **basis-independent 지표**와 대수적 탐색 |

---

### 7-A. 연속시간 정식화 (§V-A)

> 📎 상세: [[Koopman Operator]] 8번

실제 로봇 동역학은 미분방정식으로 주어지는 경우가 많다. 데이터는 샘플링되므로 실무에선 이산시간을 쓰지만, **이론적 토대는 연속시간에서 세워야** 안정성·불변량 같은 성질을 논할 수 있다.

**시스템과 flow map**

$$
\dot{x} = G(x), \qquad x\in\mathcal{X}\subseteq\mathbb{R}^{N_x} \tag{17}
$$

$G$ 는 연속미분가능하다고 가정한다. 시간 $t\ge0$ 에 대한 **flow map** $G^t : \mathcal{X}\to\mathcal{X}$ 는

$$
G^t(x(0)) := x(0) + \int_{\tau=0}^{t} G(x(\tau))\,d\tau \tag{18}
$$

즉 **"$t$ 시간 동안 흘려보내는 연산"** 이다. 모든 $t\ge0$ 에서 잘 정의된다고 가정한다(complete flow).

> [!note] 왜 flow map을 먼저 정의하는가
> 이산시간의 $T$ 에 해당하는 것이 연속시간에는 **하나가 아니라 $t$ 마다 하나씩** 있다. $G^{0.1}$, $G^{0.2}$, … 각각이 별개의 사상이다. 그래서 Koopman 연산자도 **하나가 아니라 족(family)** 이 된다.

**연산자 족**

각 $t\ge0$ 마다 (2)식과 같은 방식으로 정의한다.

$$
\mathcal{K}^t f = f\circ G^t, \qquad \forall f\in\mathcal{F} \tag{19}
$$

**반군 구조**

$\mathcal{F}$ 가 Banach 공간이고 $\{\mathcal{K}^t\}_{t\ge0}$ 가 **강연속 반군(strongly continuous semigroup)** 이면 — 즉

1. $\mathcal{K}^0 = \mathrm{id}$ (0초 흘리면 제자리)
2. $\mathcal{K}^{t_1+t_2} = \mathcal{K}^{t_1}\mathcal{K}^{t_2}$ (이어 흘리기 = 합쳐 흘리기)
3. $\lim_{t\to0}\|\mathcal{K}^tf - f\| = 0$ (시간이 0으로 가면 연속적으로 항등에 접근)

를 만족하면 — **무한소 생성자(infinitesimal generator)** 를 정의할 수 있다.

$$
\boxed{\ \mathcal{L}_G f := \lim_{t\to0}\frac{\mathcal{K}^tf - f}{t} = G\cdot\nabla f\ } \tag{20}
$$

$\cdot$ 은 내적, $\nabla$ 는 그래디언트다. $\mathcal{L}_G$ 를 **Koopman generator** 라 한다.

> [!important] (20)식의 정체는 연쇄법칙이다
> 겁먹을 필요 없다. 궤적을 따라 $f$ 가 어떻게 변하는지 미분해보면
> $$\frac{d}{dt}f(x(t)) = \nabla f\cdot\dot{x} = \nabla f\cdot G(x)$$
> — **연쇄법칙 그 자체**다.
>
> | | 이산시간 | 연속시간 |
> |:---|:---|:---|
> | 대상 | $\mathcal{K}$ (연산자 하나) | $\{\mathcal{K}^t\}$ (연산자 족) + $\mathcal{L}_G$ (생성자) |
> | 하는 일 | **한 스텝 밀기** | **궤적을 따른 방향 미분** (Lie derivative) |
> | 관계 | $\mathcal{K} = \mathcal{K}^{\Delta t}$ | $\mathcal{K}^t = e^{t\mathcal{L}_G}$ |
>
> 생성자 $\mathcal{L}_G$ 하나가 연산자 족 전체를 결정한다 — 행렬지수 $e^{At}$ 가 $A$ 하나로 결정되는 것과 같은 구조다.

> [!note] 논문의 각주가 짚는 엄밀성
> 강연속 반군이 되려면 $G$ 와 $\mathcal{F}$ 를 적절히 골라야 하며(각주 5, [160, Ch. 1]), generator의 정의도 $\mathcal{F}$ 의 **조밀한 부분집합**에서만 성립하도록 완화할 수 있다(각주 6). 즉 (20)식은 $\mathcal{F}$ 전체에서 무조건 성립하는 것이 아니다.

---

### 7-B. 제어 입력의 엄밀한 처리 (§V-B)

> 📎 상세: [[Koopman with Control Input]]

§II-C에서 소개한 실용적 근사 3종(joint lifting / input-affine / control-coherent)은 **왜 그렇게 해도 되는지**에 대한 근거가 없었다. §V-B는 그 근거를 두 갈래로 제시한다.

**출발점 — 근본적 난점**

$$
x_{t+1} = T_u(x_t, u_t), \qquad x\in\mathcal{X}\subseteq\mathbb{R}^{N_x},\ u\in\mathcal{U}\subseteq\mathbb{R}^{N_u} \tag{21}
$$

> [!warning] 상태와 입력의 비대칭 — §V-B 전체를 지배하는 문제
> - **상태**: 시스템의 **내재적 속성**. 내부 동역학에 따라 진화 → Koopman이 다룰 수 있다
> - **입력**: 특히 개루프에서는 **사전에 알 수 없고**, 진화에 큰 영향을 주며, **정해진 동역학 규칙을 따르지 않는다**
>
> Koopman 연산자는 "동역학의 선형 표현"인데, 입력은 애초에 동역학을 갖지 않는다. 그러니 그 틀에 자연스럽게 들어가지 않는다.

#### ① 무한 입력 시퀀스 프레임 [105]

**발상**: 입력이 동역학을 안 따른다면, **입력 시퀀스 자체를 상태에 넣어** 동역학을 부여하자.

$\ell(\mathcal{U})$ 를 모든 무한 입력 시퀀스 $\{u_s(i)\}_{i=0}^\infty$ 의 공간, $S:\ell(\mathcal{U})\to\ell(\mathcal{U})$ 를 **좌시프트 연산자**라 하자.

$$
S:\ \{u_s(0), u_s(1), u_s(2), \dots\}\ \longmapsto\ \{u_s(1), u_s(2), u_s(3), \dots\}
$$

확장 상태 $\chi := (x, u_s)\in\mathcal{X}\times\ell(\mathcal{U})$ 에 대해

$$
\chi^+ = (x, u_s)^+ = \big(T_u(x, u_s(0)),\ Su_s\big) =: L(\chi) \tag{22}
$$

> [!success] 트릭의 핵심 — 제어계가 자율계로 바뀐다
> (22)를 보면 **입력이 사라졌다.** $L$ 은 $\chi$ 만의 함수다. 매 스텝 "시퀀스의 첫 원소를 꺼내 쓰고, 시퀀스를 한 칸 민다"는 규칙이 곧 입력의 동역학이 된 것이다.
>
> 자율 시스템이 되었으니 (2)식의 표준 Koopman 정의를 **그대로** 쓸 수 있다.
> $$\mathcal{K}_L f = f\circ L, \qquad \forall f\in\mathcal{H} \tag{23}$$
> $\mathcal{H}$ 는 정의역이 $\mathcal{X}\times\ell(\mathcal{U})$, 공역이 $\mathbb{C}$ 이며 $L$ 과의 합성에 닫힌 함수공간이다.

**대가**: 무한 입력 시퀀스에 의존하므로 (23)을 직접 다루기는 (2)보다 **훨씬 어렵다**. 유한 입력 시퀀스만 가지고 일반적인 유한차원 모델을 찾는 직접적 방법이 없다.

그래서 [105]는 MPC를 목표로 삼는다 — MPC는 **단기 예측만 정확하면 되므로** 리프팅 선형 모델(**linear predictor**)로 근사한다.

$$
z^+ \approx Az + Bu, \qquad z_0 = \psi(x_0) \tag{24}
$$

$A, B$ 는 EDMD류로 추정한다.

> [!danger] 논문이 명시하는 한계 — 놓치기 쉬운 지점
> (24)는 무한 입력 시퀀스를 고려하지 않으므로 $\mathcal{K}_L$ 의 정보를 일반적으로 **다 담지 못한다**. 더 강한 진술이 이어진다.
>
> **"리프팅 상태의 차원을 무한대로 보내도, 리프팅 선형 모델의 궤적이 비선형 시스템의 궤적으로 수렴한다고 일반적으로 결론지을 수 없다."** ([105, Corollary 1 이후 논의])
>
> 즉 §II-B에서 본 자율계의 수렴 정리 [30]가 **입력이 있는 경우로 그대로 확장되지 않는다.** 흔한 오해를 저자들이 직접 차단하는 대목이다.

#### ② Koopman Control Family (KCF) [36]

**발상**: 무한 시퀀스를 피하고, **입력을 상수로 고정한 시스템들의 족**으로 표현하자.

$$
x^+ = T_{\hat u}(x) := T_u(x,\ u\equiv\hat u), \qquad \hat u\in\mathcal{U} \tag{25}
$$

각 $\hat u$ 마다 (1)식 형태의 **자율 시스템**이 하나씩 생긴다. 임의의 입력 시퀀스로 만든 궤적은 이들의 **합성**으로 정확히 표현된다.

$$
x_{m+1} = T_{u_m}\circ T_{u_{m-1}}\circ\cdots\circ T_{u_0}(x_0) \tag{26}
$$

각 부분시스템에 (2)식을 적용해 **Koopman Control Family** $\{\mathcal{K}_{\hat u}\}_{\hat u\in\mathcal{U}}$ 를 정의한다.

$$
\mathcal{K}_{\hat u}\,g = g\circ T_{\hat u}, \qquad \forall g\in\mathcal{F}
$$

그러면 궤적을 따른 관측값 진화가 **연산자들의 곱**이 된다.

$$
g(x_{m+1}) = \big[\mathcal{K}_{u_0}\mathcal{K}_{u_1}\cdots\mathcal{K}_{u_m}\,g\big](x_0), \qquad \forall g\in\mathcal{F}
$$

> [!note] 두 프레임의 차이를 한 줄로
> - **[105]**: 연산자는 **하나**($\mathcal{K}_L$), 대신 상태공간이 무한차원($\mathcal{X}\times\ell(\mathcal{U})$)
> - **[36]**: 상태공간은 그대로($\mathcal{X}$), 대신 연산자가 **여러 개**($\hat u$ 마다 하나)
>
> 무한을 어디로 밀어냈는지가 다를 뿐, 같은 어려움을 다르게 나눠 진 것이다.

**Input-State Separable Model — §V-B의 결론**

KCF의 **공통 불변 부분공간(common invariant subspace)** 위에서 모델은 반드시 다음 형태를 갖는다 ([36, Th. 4.3]).

$$
\boxed{\ \psi(x^+) = \psi\circ T(x,u) = A(u)\,\psi(x)\ }
$$

$\psi:\mathcal{X}\to\mathbb{C}^{N_\psi}$ 는 리프팅 함수, $A:\mathcal{U}\to\mathbb{C}^{N_\psi\times N_\psi}$ 는 **행렬값 함수**다.

> [!important] 이 형태가 말하는 것 — 리프팅 상태에 선형, 입력에 비선형
> **왜 입력에는 비선형이어야 하는가?** 개루프에서 입력은 정해진 동역학을 따르지 않으므로, **Koopman 연산자의 구조로 입력의 비선형성을 선형 연산자로 표현할 방법이 없다.** 위 "상태와 입력의 비대칭"이 여기서 수식으로 회수된다.
>
> 즉 실무에서 쓰는 $Kz+Bu$ 는 편의가 아니라 **$A(u)$ 를 $u$ 의 1차 다항식으로 제한한 근사**이며, 그 제한이 언제 타당한지를 이 형태가 알려준다.

> [!success] 통합 관점 — 이 논문의 이론적 하이라이트
> 널리 쓰이는 모델들이 **전부 이 형태의 특수 사례**다 ([36, Lemmas 4.4–4.5]).
>
> | 모델 | $A(u)$ |
> |:---|:---|
> | **Lifted linear** | $A(u)\psi = K\psi + Bu$ — 상수 + 아핀 항 |
> | **Bilinear** | $A(u) = K + \sum_{j=1}^{N_u}u_jB_j$ |
> | **Linear switched** [161] | $A(u) = A_{\sigma(u)}$, 유한 개 모드 |
>
> 서로 무관한 heuristic처럼 보이던 것들이 **KCF 연산자들의 서로 다른 유한차원 근사**로 통합된다. 이것이 §II-C의 실용적 선택들에 사후적 정당성을 부여하는 대목이다.
>
> 적절한 공통 불변 부분공간이 없으면, KCF의 작용을 임의 부분공간 위로 **직교 사영**해 근사한다. 이론 분석·학습법·정확도 bound는 [36] 참고.

**두 프레임은 동등하다**

적절한 함수공간 조건 하에서 [105]와 [36]이 **동등함이 증명되어 있다** [162]. 다만 정보를 다루는 방식이 근본적으로 다르므로 용도가 갈린다.

| 상황 | 적합한 프레임 | 이유 |
|:---|:---|:---|
| 모든 가능한 입력 하의 일반 이론 분석, 불변량, **도달불가능 집합**, 스펙트럼 성질 | **무한 입력 시퀀스** [105] | **단일 연산자**라서 분석 도구를 쓰기 쉽다 |
| 유한차원 표현, 유한시간 궤적, **MPC 유한구간 예측**, 궤적 데이터 기반 학습 | **KCF** [36] | 무한 시퀀스 불필요 + **input-state separable form** 사용 가능 |

---

### 7-C. 딕셔너리 구성 (§V-C)

> 📎 상세: [[Consistency Index]], [[Koopman-Invariant Subspace]]

§III-B의 자기비판("수렴 보장이 없다")에 대한 논문의 직접적인 답이다.

#### 최적화 기반 방법의 함정

$$
\underset{\psi}{\text{minimize}}\ \ \big\|\Psi(Y)-\Psi(Y)\Psi(X)^\dagger\Psi(X)\big\|_F \tag{27}
$$

**두 가지 문제**: ① 파라메트릭 족(NN 등)이라 **비볼록** ② **더 심각 — residual 최소화가 불변 부분공간에 가까워짐을 의미하지 않는다**

> [!danger] Fig. 3의 반례 — 이 논문에서 가장 중요한 그림
> $x^+=0.6x$, $\psi_\alpha(x)=[x,\ x+\alpha\sin(x)]$, $\alpha\in[0.01,100]$
>
> - **모든 $\alpha\ne0$ 에 대해 $\mathrm{span}(\psi_\alpha)$ 는 동일**하다 ($=\mathrm{span}\{x,\sin(x)\}$). $\alpha$ 는 **기저만** 바꾼다.
> - 그런데 **EDMD residual은 $\alpha$ 에 따라 요동치며 임의로 0에 가까워질 수 있다.**
> - 하지만 그 부분공간은 **불변이 아니다.**
>
> **→ residual은 부분공간의 품질이 아니라 기저 선택의 artifact를 반영한다.** (27)로 학습한 모델은 **장기 예측에 부적합**할 수 있다.

#### Consistency Index — basis-independent 해법 [163]

$$
K_F = \Psi(Y)\Psi(X)^\dagger, \qquad K_B = \Psi(X)\Psi(Y)^\dagger \tag{29}
$$

$$
\boxed{\ I_C(\psi,X,Y) := \lambda_{\max}\big(I - K_FK_B\big)\ } \tag{28}
$$

**직관**: 부분공간이 불변이면 앞으로 밀었다 뒤로 밀면 제자리다 → $K_FK_B = I$ → $I_C=0$. 불변에서 멀수록 $I_C$ 가 커진다.

**네 가지 성질**:
1. $I_C\in[0,1]$
2. **기저에 무관** — $\mathrm{span}(\psi)$ 에만 의존 (Fig. 3이 시각적 증거)
3. 적절한 기저 변환 하에 **양반정부호 행렬의 최대 고유값**으로 볼 수 있어 표준 솔버 사용 가능
4. ⭐ **부분공간 전체에 대한 tight upper bound**:

$$
I_C(\psi,X,Y) = \max_{\substack{f\in\mathrm{span}(\psi)\\ \|\mathcal{K}f\|_{L^2}\ne0}}\frac{\|\mathcal{K}f-\mathcal{P}_{\mathcal{K}f}\|_{L^2(\mu_\mathcal{X})}}{\|\mathcal{K}f\|_{L^2(\mu_\mathcal{X})}}
$$

즉 $I_C=0.02$ 는 *"부분공간 안 어떤 함수든 상대 예측 오차 2% 이내"* 라는 **보장**이다.

**Robust minimax 등가 형태**:

$$
\min_{\psi\in\mathcal{P}_\mathcal{F}}\ \max_{\substack{f\in\mathrm{span}(\psi)\\ \|\mathcal{K}f\|\ne0}}\ \frac{\|\mathcal{K}f-\mathcal{P}_{\mathcal{K}f}\|_{L^2}}{\|\mathcal{K}f\|_{L^2}} \tag{30}
$$

**Fig. 4 실험**: 감쇠 진자 $[\dot\theta,\ddot\theta]=[\dot\theta,\ -9.81\sin\theta-0.1\dot\theta]$, 딕셔너리 $[\theta,\dot\theta,\mathrm{NN}_1,\mathrm{NN}_2,\mathrm{NN}_3]$.
→ **consistency index 최소화가 residual 최소화보다 장기 예측에서 명확히 우월.** 이유: 전자는 함수공간의 **비가산적으로 많은** 원소를 고려하고, 후자는 **유한 개**만 본다.

#### 대수적 탐색 — SSD / T-SSD

**불변성의 데이터 표현**: $\psi^\top = \psi_s^\top C$ 로 두면

$$
\mathcal{R}\big(\psi_s(X)^\top C\big) = \mathcal{R}\big(\psi_s(Y)^\top C\big) \tag{31}
$$

- **SSD** [31][32]: (31)을 만족하는 **열 개수 최대인 $C$** 를 찾는 대수 알고리즘 = **최대 정확 불변 부분공간**. [31]은 임의 유한차원 함수공간에서 모든 Koopman 고유함수를 식별하는 **필요조건 + almost surely 충분조건**을 제시(순/역 EDMD 고유분해 기반). [32]는 고차원 병렬판.
- **T-SSD** [33]: 등식 대신 두 range space가 **가깝기만** 하면 되도록 완화, 정확도 파라미터 $\epsilon\in[0,1]$ 도입

> [!success] T-SSD는 EDMD와 SSD를 잇는 통합 스펙트럼 (Fig. 5)
> | $\epsilon$ | 등가 | 의미 |
> |:---:|:---|:---|
> | $0$ | **SSD** | 예측 오차 0 → 최대 정확 불변 부분공간 |
> | $(0,1)$ | **T-SSD** | 정확도 ↔ 표현력(차원) 균형 |
> | $1$ | **EDMD** | 오차 100% 허용 → 탐색 공간 전체에 EDMD |

**Fig. 6 실험**: Duffing $[\dot x_1,\dot x_2]=[x_2,\ -0.5x_2+x_1(1-x_1^2)]$, $\mathcal{X}=[-2,2]^2$, 탐색공간 = 차수 10 이하 다항식. **T-SSD($\epsilon=0.02$) 가 정규화 전체 기저보다 상대 예측 오차가 훨씬 작다.**

> [!warning] 이 절의 실무적 한계 — 논문이 스스로 밝힌 것
> 최적화 기반 딕셔너리 선택은 우수하지만 **큰 데이터셋이 필요하고 일반적으로 오프라인 사전계산에만 적용 가능**하다. §I의 "runtime learning / small data"와 긴장 관계다.

---

> [!abstract] §V 총평 — 이 절이 논문에서 갖는 위치
> §V는 §II·§III가 실용적 편의로 넘어간 세 지점에 **사후적 정당성 또는 명시적 한계**를 부여한다.
>
> | | 앞에서 한 일 | §V의 판정 |
> |:---|:---|:---|
> | **연속시간** (7-A) | 다루지 않음 | generator로 정식화. 이산시간은 $\mathcal{K}=\mathcal{K}^{\Delta t}$ 인 특수 사례 |
> | **입력 처리** (7-B) | heuristic 3종 | input-state separable form이 **전부를 포섭** ✅ / 단 리프팅 차원→∞ 라도 **수렴 보장 없음** ⚠️ |
> | **딕셔너리** (7-C) | "잘 고르세요" | residual은 **틀린 지표** ⚠️ / consistency index와 T-SSD가 대안 ✅ |
>
> **읽는 순서 제안**: 실무자는 §II·§III만으로 구현할 수 있지만, **왜 그게 되는지 / 언제 깨지는지**를 알려면 §V가 필수다. 특히 7-B의 "수렴 보장 없음"과 7-C의 Fig. 3 반례는 **실제로 물리는 함정**이다.

---

## 8. 열린 문제 (§VI)

논문이 제시하는 8가지. 저자들의 집단적 연구 경험에서 도출된 것으로, **완전하진 않지만 견고한 출발점**이라고 밝힌다.

| # | 과제 | 핵심 |
|:---|:---|:---|
| 1 | **Koopman 공간의 제약 처리** | 원 공간의 제약을 리프팅 공간으로 어떻게 올릴 것인가. **대수적·기하학적 구조** 활용이 열쇠 |
| 2 | **확률적 시뮬레이션·belief-space 계획** | 다봉(multimodal) 분포 처리, 불확실성 하 robust 계획. **확률적 Koopman** [65][164][165]의 효율적 구현·신뢰성·적응성 |
| 3 | **샘플링 레이트 선택** | 온라인/적응 학습에서 시간 해상도가 결정적. 불충분한 샘플링이 외란 추정·제어 정확도를 저하시킴 [166]. 예측 오차 bound도 좌우 |
| 4 | **정교/dexterous manipulation 확장** | 접촉 풍부, 비파지(nonprehensile), 손 조작. **접촉의 불연속성**을 전역 선형 표현으로 다룰 잠재력. 아직 초기 단계 |
| 5 | **소프트 로보틱스 심화** | 고차원 리프팅이 연속체/소프트에서 **계산 비용 과다·intractable**. 차원 축소는 편향·일반화 저하를 유발. **소프트 로봇의 올바른 기술(description) 선택**이 열린 문제 |
| 6 | **하이브리드 시스템 확장** | 이산·연속은 각각 다뤘으나 **하이브리드**는 미개척. [16]이 unforced 이종 시스템의 리프팅 가능성을 보였으나, **입력이 있는 경우와 더 넓은 하이브리드 동역학**은 미해결 |
| 7 | **리프팅 특징의 불확실성** | 선행 연구의 **zero-mean Gaussian 가정** 재검토 필요. **Gaussian 분포를 관측 공간으로 밀어넣으면 여전히 Gaussian인가?** 어떤 조건에서? 리프팅이 **통계적 구조를 보존**하는 경우를 찾는 것이 핵심 방향 |
| 8 | **기저 최적화 문제 연구** | 비용함수가 리프팅 상태에 의존 → **Koopman-NMPC의 recursive feasibility 평가**가 어려워짐. 로봇 시스템 전반에 일반화되는 비용함수 설계 |

---

## 9. 비판적 평가

### 👍 강점

1. **이론과 실무를 실제로 잇는다.** §II(실용 근사)와 §V(엄밀 이론)를 **의도적으로 분리**한 구성이 탁월하다. 실무자는 §II·§III만 읽고 바로 구현할 수 있고, 이론가는 §V에서 그 실용적 선택들이 어디서 정당화되는지(input-state separable form이 선형/쌍선형/스위칭을 모두 포섭) 확인할 수 있다.
2. **반례로 가르친다.** $x^+=0.5x$ 딕셔너리 반례, Fig. 3의 $\alpha$-족, Fig. 4의 진자 비교 — "차원을 키우면 좋다", "residual이 작으면 좋다"는 **가장 흔한 오해를 정면으로 깬다.** 서베이가 이렇게 구체적 반례를 드는 경우는 드물다.
3. **자기비판이 정직하다.** §III-B에서 자기가 소개한 실용 방법들에 "수렴 보장 없음"을 명시하고 §V-C로 넘긴다. §V-C 끝에서는 그 이론적 방법마저 "오프라인 전용"이라 §I의 runtime 주장과 긴장 관계임을 인정한다.
4. **재현 가능성**: 실행 가능한 튜토리얼 코드 + 단계별 런타임 측정 제공. 실제로 돌려본 결과는 [[Koopman 예제 코드|🧪 실행 예제]]에 정리했습니다 — EDMD 학습이 **0.09초**에 끝나는 것을 직접 확인할 수 있습니다.

### 👎 한계 / 아쉬운 점

> [!warning] 1. Runtime learning 주장과 딕셔너리 현실의 간극
> §I은 "small data runtime learning"을 전면에 내세우지만, §V-C가 인정하듯 **좋은 딕셔너리를 얻는 이론적 방법(최적화·SSD)은 큰 데이터셋 + 오프라인 사전계산을 요구**한다. 즉 **"딕셔너리는 오프라인, 연산자만 온라인"** 이 실제 그림인데, 이 이중 구조가 §I에서는 충분히 드러나지 않는다. 논문 전체를 읽어야 비로소 보인다.

> [!warning] 2. 정량적 비교의 부재
> 서베이의 본질적 한계이긴 하나, **"Koopman이 딥러닝 베이스라인 대비 실제로 얼마나 데이터 효율적인가"** 에 대한 통일된 벤치마크가 없다. [68]의 "orders of magnitude faster"는 학습 시간이지 **최종 제어 성능**이 아니다. Table I은 무엇을 썼는지 정리하지만 **누가 더 나은지**는 답하지 않는다.

> [!warning] 3. 실패 사례의 부재
> "Koopman이 잘 안 되는 시스템"에 대한 체계적 논의가 없다. 강한 카오스(연속 스펙트럼), 극심한 접촉 불연속, 매우 고차원 상태 등에서의 **명시적 실패 모드**를 정리했다면 실무자에게 훨씬 유용했을 것이다.

> [!warning] 4. §IV의 나열적 성격
> 플랫폼별 절이 "누가 무엇을 했다"의 나열에 가깝다. 각 플랫폼에서 **왜 그 리프팅/제어 조합이 선택되었는지의 인과**는 §III-B 말미의 짧은 문단에 압축되어 있을 뿐이다.

### 🔍 세미나 토론 포인트

1. **차원의 역설**: Koopman은 "차원을 올려 선형화"하는데, 소프트 로봇처럼 **원래 자유도가 무한에 가까운** 시스템에서는 이게 역효과(§VI-5)다. 리프팅이 유리한 조건과 불리한 조건의 경계는 어디인가?
2. **Fig. 3의 교훈을 우리 문제에 적용하면**: 우리가 쓰는 딥 Koopman의 loss는 (27) 형태(residual)인가, (30) 형태(consistency)인가? 전자라면 **장기 예측이 무너질 구조적 이유**가 있다.
3. **입력 비선형성의 불가피성**: input-state separable form $\psi(x^+)=A(u)\psi(x)$ 가 말하는 "입력에는 비선형일 수밖에 없다"는 결론은, 흔히 쓰는 $Kz+Bu$ 가 **원리적으로 근사일 뿐**임을 뜻한다. 우리 시스템에서 이 근사 오차는 얼마나 되는가?
4. **§VI-7의 Gaussian 질문**: 리프팅이 통계 구조를 보존하는가 — 이것이 Koopman + Kalman filter 결합([98][115][85])의 이론적 토대를 좌우한다. 현재는 사실상 **가정**에 기대고 있다.

---

## 📚 개념 정리 노트

> [!tip] 이 리뷰에서 파생된 개념 노트
> **기초 이론**
> - [[Koopman Operator]] — 왜 비선형이 선형이 되는가, 정의·선형성 증명·연속시간 generator
> - [[Observable Function]] — 리프팅 함수 설계, 손으로 푸는 정확 선형화 예제, 3가지 전략
> - [[Koopman-Invariant Subspace]] — 유한차원 정확성의 조건, SSD/T-SSD
> - [[Koopman Eigenfunction]] — 스펙트럼 관점, $\phi(x_t)=\lambda^t\phi(x_0)$
>
> **알고리즘**
> - [[EDMD]] — $K=\Psi(Y)\Psi(X)^\dagger$ 유도, 사영 해석, 구현 주의사항
> - [[HVOK]] — Hankel 시간지연 임베딩, Takens 정리
> - [[Consistency Index]] — residual의 함정과 basis-independent 대안
>
> **제어**
> - [[Koopman with Control Input]] — 실용 근사 3가지 + KCF 이론, input-state separable form
> - [[Koopman MPC]] — 볼록 QP화, Fisher 정보 능동학습, robustness
>
> **수학 기초** (Koopman 맥락과 독립적으로도 유용)
> - [[Pseudo-inverse]] — $\dagger$ 가 무엇인가, 최소자승·직교사영·수치 안정성
> - [[Affine]] — 선형과 아핀의 차이, "차원을 올려 선형화"라는 발상, input-/control-affine 구분
> - [[Fisher Information]] — "데이터가 얼마나 알려주는가", Cramér–Rao bound, 능동학습의 토대

---

## 🔗 주요 참고문헌

| 번호 | 문헌 | 왜 중요한가 |
|:---|:---|:---|
| [26] | Koopman, *PNAS* 1931 | **원전** — Hilbert 공간 위 무한차원 선형 연산자 |
| [27] | Williams, Kevrekidis & Rowley, *J. Nonlinear Sci.* 2015 | **EDMD 원논문** |
| [30] | Korda & Mezić, *J. Nonlinear Sci.* 2018 | EDMD → Koopman **수렴성** |
| [105] | Korda & Mezić | **Koopman MPC**, linear predictor |
| [36] | Haseli & Cortés, *Automatica* 2026 | **KCF**, input-state separable model — 이론적 통합 |
| [31][32][33] | Haseli & Cortés | **SSD / parallel SSD / T-SSD** |
| [163] | — | **Consistency index** |
| [28] | Kamb et al., *SIAM J. Appl. Dyn. Syst.* 2020 | **HVOK** 시간지연 |
| [23] | Brunton et al., *SIAM Rev.* 2022 | Modern Koopman theory 종합 리뷰 |
| [25] | Shi, Liu & Karydis 2023 | 소프트 로보틱스 전용 리뷰 |
| [16] | Asada, *T-Mech* 2023 | 이종/하이브리드 시스템 통합 표현 |

---

> [!quote] 논문의 마지막 문장
> *"We believe Koopman-based methods hold tremendous potential, and we are excited to see how the robotics community will build on this foundation to drive future innovation."*
