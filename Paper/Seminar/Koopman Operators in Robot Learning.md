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
> - **코드**: https://github.com/sunnyshi0310/KoopmanRobo

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
| **§V** | 심화 이론 — 연속시간, KCF, 딕셔너리 구성 | [[Koopman with Control Input]], [[Consistency Index]] |
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

$$
\underset{K}{\text{minimize}}\ \ \big\|\Psi(Y) - K\Psi(X)\big\|_F \tag{6}
$$

$$
\boxed{\ K_{\mathrm{EDMD}} = \Psi(Y)\Psi(X)^{\dagger}\ } \tag{7}
$$

> [!success] 왜 이 한 줄이 로보틱스에서 중요한가
> **닫힌 형태 해(closed-form)** 다. 반복 최적화가 없다. SVD 한 번이면 끝.
> - 논문 [68] 보고: 학습 단계가 경쟁 데이터 기반 방법 대비 **수 자릿수(orders of magnitude) 빠름**
> - [17]의 online DMD 변형: 시변 시스템에 대해 **실시간 연산자 갱신** 가능
> - → 이것이 §I의 "runtime learning" 주장을 실제로 뒷받침하는 계산적 근거다

### 예측자와 고유함수

$f = v_f^\top\psi \in \mathrm{span}(\psi)$ 에 대해

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}f} := v_f^\top K_{\mathrm{EDMD}}\psi \tag{8}
$$

$v$ 가 **좌고유벡터** ($v^\top K_{\mathrm{EDMD}} = \lambda v^\top$) 이면 근사 [[Koopman Eigenfunction|Koopman 고유함수]]가 나온다.

$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}\phi} = v^\top K_{\mathrm{EDMD}}\psi = \lambda v^\top\psi = \lambda\phi \tag{9}
$$

### ⚠️ EDMD가 실제로 근사하는 것

> [!warning] $K_{\mathrm{EDMD}} \ne \mathcal{K}$
> EDMD 행렬은 Koopman 연산자 자체가 아니라 **$\mathrm{span}(\psi)$ 위로의 사영된 작용**을 encode 한다.
> $$\mathcal{P}_{\mathrm{span}(\psi)}\mathcal{K} : \mathcal{F}\to\mathcal{F} \tag{10}$$
> 내적은 데이터가 만드는 **경험적 측도** 기준이다.
> $$\mu_{\mathcal{X}} = \frac{1}{M}\sum_{i=1}^{M}\delta_{x_i} \tag{11}$$

**수렴성** [30]: 딕셔너리·데이터가 커지면 연산자 위상에서 수렴, 고유값 포착, 고유함수 약수렴.

> [!danger] 논문이 반복 강조하는 반직관적 사실
> **"큰 부분공간이 반드시 좋은 예측을 주지 않는다."**
>
> 반례: $x^+ = 0.5x$, $\psi_1(x)=x$, $\psi_2(x)=[x,\sin(x)]$
> - $\mathrm{span}(\psi_1)\subset\mathrm{span}(\psi_2)$ 임에도
> - $\psi_1$: 불변 → 예측 **정확(exact)** ✅
> - $\psi_2$: 불변 아님 → 일부 함수에서 **큰 오차** ❌
>
> 게다가 **시스템 모델 없이는 목표 정확도를 위한 딕셔너리 차원의 하한을 추정할 방법조차 없다.** → 딕셔너리는 반드시 **시스템/데이터 정보에 기반해 설계·학습**되어야 한다.

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

## 4. 입력이 있는 시스템 (§II-C, §V-B)

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
| **② Input-affine** ⭐ | $g(x_{t+1})\approx Kg(x_t)+Bu_t$ | **선형 구조 보존** → LQR/MPC 직결 | 아핀성은 근사일 뿐 |
| **③ Control-coherent** [37] | 입력 변화에도 일관된 임베딩 | 새 제어 시퀀스로 **일반화 우수** | 최신 기법, 비용 |

**②가 지배적**이다. 결과가 완전한 선형 상태공간 모델이므로 고전 제어 도구를 문자 그대로 쓸 수 있기 때문이다. 논문은 이것이 [36]의 **input-state separable model의 특수 사례**임을 짚어, 임시방편이 아니라 이론적 배경이 있음을 명확히 한다.

### 이론적으로 엄밀한 두 프레임 (§V-B)

**(A) 무한 입력 시퀀스** [105] — 입력 시퀀스를 상태에 포함시키고 **좌시프트 연산자** $S$ 를 그 동역학으로 삼아 **제어 시스템을 자율 시스템으로 변환**한다.

$$
\chi^+ = (T_u(x,u_s(0)),\ Su_s) =: L(\chi) \tag{22}
$$
$$
\mathcal{K}_Lf = f\circ L \tag{23}
$$

무한차원 의존 때문에 실용적으론 **linear predictor** 근사를 쓴다.

$$
z^+ \approx Az + Bu \tag{24}
$$

> [!warning] 논문의 명시적 경고
> 이 모델은 무한 입력 시퀀스를 고려하지 않으므로 $\mathcal{K}_L$ 의 정보를 다 담지 못한다. **리프팅 차원을 무한대로 보내도 궤적 수렴을 일반적으로 결론지을 수 없다.**

**(B) Koopman Control Family (KCF)** [36] — 입력을 상수로 고정한 시스템 족으로 표현한다.

$$
x^+ = T_{\hat u}(x) := T_u(x, u\equiv\hat u) \tag{25}
$$
$$
x_{m+1} = T_{u_m}\circ T_{u_{m-1}}\circ\cdots\circ T_{u_0}(x_0) \tag{26}
$$

공통 불변 부분공간 위에서 모델은 반드시 **input-state separable form**을 갖는다 ([36, Th. 4.3]).

$$
\boxed{\ \psi(x^+) = A(u)\,\psi(x)\ }
$$

> [!success] 통합적 관점 — 이 논문의 이론적 하이라이트
> **리프팅 선형·쌍선형·선형 스위칭 모델이 전부 이 형태의 특수 사례**다 ([36, Lemmas 4.4–4.5]). 즉 실무에서 쓰이는 모델들이 서로 무관한 heuristic이 아니라, **KCF 연산자들의 서로 다른 유한차원 근사**로 통합 이해된다.
>
> **리프팅 상태에 선형, 입력에 비선형** — 개루프 입력이 동역학을 따르지 않기에 입력의 비선형성만은 선형 연산자로 흡수할 수 없다.

두 프레임은 적절한 조건에서 **동등함이 증명되어 있다** [162]. 용도만 갈린다 — 일반 이론 분석은 (A), 유한차원·MPC·궤적 학습은 (B).

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

### ③-b 능동학습 (§III-C2)

닫힌 형태 해 (6),(7)이 **능동학습 제어기**로 직결된다 [100].

$$
\mathcal{I} = \mathbb{E}\Big[\tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}\ \tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}^\top\Big] \tag{14}
$$

$$
\mathcal{I} = \tfrac{\partial z_{t+1}}{\partial K}^\top\Sigma^{-1}\tfrac{\partial z_{t+1}}{\partial K} \propto \mathrm{Var}[K]^{-1} \tag{15}
$$

Fisher 정보는 사후 불확실성의 하한(**Cramér–Rao bound** [110][111])을 주며, **미분 가능하고 행동 가능**하다.

$$
\begin{aligned}
\underset{\{u_i\}}{\text{min}}\ & \sum_{i=0}^{N_h-1}\big(-\mathcal{I}(z_i,{}^tK) + u_i^\top Ru_i\big)\\
\text{s.t.}\ & z_{i+1}={}^tKz_i+{}^tBu_i,\quad z_0=\psi(x_t)
\end{aligned} \tag{16}
$$

**$-\mathcal{I}$ 최소화 = 정보 최대화**. 제어기가 목표 달성과 동시에 **모델을 가장 잘 배울 방향으로 로봇을 움직인다.** Receding-horizon으로 반복해 연산자 변화를 반영. 사례: 공중 로봇의 불안정 텀블 회복, 다리 로봇의 granular media 상호작용 학습 [100].

> [!note] 딥 관측함수와의 긴장
> 딥 모델로 관측함수를 근사하면 [100][112][113] 표현력은 커지지만 **능동학습 효과는 감소**한다 (비선형 관측함수 학습에 더 많은 데이터가 필요하므로). 그럼에도 순수 딥 NN 대비 Koopman 선형 모델은 **데이터 효율성과 능동학습 제어에서 여전히 큰 우위**다.

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

## 7. 심화 이론 — 딕셔너리 구성 (§V-C)

> 📎 상세: [[Consistency Index]], [[Koopman-Invariant Subspace]]

이 절이 §III-B의 자기비판("수렴 보장이 없다")에 대한 논문의 답이다.

### 최적화 기반 방법의 함정

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

### Consistency Index — basis-independent 해법 [163]

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

### 대수적 탐색 — SSD / T-SSD

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

### 연속시간 확장 (§V-A)

$\dot x = G(x)$, flow map $G^t$, 연산자족 $\mathcal{K}^tf = f\circ G^t$ (19). 강연속 반군 조건 하에 **Koopman generator**:

$$
\mathcal{L}_Gf := \lim_{t\to0}\frac{\mathcal{K}^tf-f}{t} = G\cdot\nabla f \tag{20}
$$

본질은 **연쇄법칙**이다 — 궤적을 따른 방향 미분(Lie derivative). 📎 [[Koopman Operator]] §6

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
4. **재현 가능성**: 실행 가능한 튜토리얼 코드 + 단계별 런타임 측정 제공.

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
