---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Control
aliases:
  - Koopman 제어 입력
  - Koopman Control Family
  - KCF
  - Input-state separable model
keywords: control input, bilinear, KCF, input-state separable, linear predictor
related notes: "[[Koopman Operator]], [[EDMD]], [[Koopman MPC]]"
dg-publish: false
---

# Koopman with Control Input (입력이 있는 시스템으로의 확장)

> [!abstract] 한 줄 요약
> Koopman은 원래 **자율(unforced) 시스템**을 위해 만들어졌다. 제어 입력 $u$ 를 넣는 순간 이론이 훨씬 까다로워진다 — **상태는 내부 동역학을 따르지만 입력은 그렇지 않기 때문**이다. 논문은 실용적 근사 3가지(III절)와 이론적으로 엄밀한 프레임 2가지(V-B절)를 구분해서 제시한다.

---

## 1. 왜 어려운가 — 근본적 비대칭

제어 시스템:

$$
x_{t+1} = T_u(x_t, u_t), \qquad x \in \mathcal{X} \subseteq \mathbb{R}^{N_x},\ u \in \mathcal{U} \subseteq \mathbb{R}^{N_u}
$$

> [!important] 논문이 짚는 핵심 난점
> - **상태 $x$**: 시스템의 **내재적 속성**. 내부 동역학에 따라 진화한다. → Koopman 연산자가 다룰 수 있다.
> - **입력 $u$**: 특히 개루프(open-loop)에서는 **사전에 알 수 없고**, 시스템 진화에 큰 영향을 준다. **정해진 동역학 규칙을 따르지 않는다.** → Koopman 연산자의 구조로 표현할 방법이 없다.
>
> 즉 $u$ 는 "동역학을 갖지 않는 객체"이므로, "동역학의 선형 표현"인 Koopman 틀에 자연스럽게 들어가지 않는다.

---

## 2. 실용적 근사 3가지 (논문 II-C절)

### (1) 상태·입력 결합 리프팅 (Joint lifting)

입력 $u$ 를 확장 상태의 일부로 취급하고, 결합 공간 위에서 관측 함수 $g(x,u)$ 를 정의한다.

$$
\psi(x_t, u_t) \ \longrightarrow\ \psi(x_{t+1}, u_{t+1}) = K\,\psi(x_t, u_t)
$$

- **장점**: 직관적, 구현 간단
- **단점**: **미래 입력을 안다고 가정**해야 함. $u$ 가 임의로 변하면 일반화 실패 (입력이 동역학 규칙을 안 따르므로)
- **적합**: 구조화되거나 반복적인 입력 패턴(structured or repetitive input patterns)을 갖는 학습 기반 로봇 시스템

### (2) 리프팅 공간에서의 입력 아핀 형태 ⭐ 가장 널리 쓰임

관측값의 진화가 **입력에 대해 아핀(affine)** 이라고 가정한다.

$$
\boxed{\;\psi(x_{t+1}) \approx K\,\psi(x_t) + B\,u_t\;}
$$

- $K$: 자율(autonomous) 부분에 대한 유한차원 Koopman 근사
- $B$: 제어 입력의 선형 영향

**추정 방법**: [[EDMD]]를 그대로 확장한다. 리프팅 상태와 입력을 세로로 쌓아 최소제곱을 푼다.

$$
\Psi(Y) \approx \underbrace{\begin{bmatrix} K & B \end{bmatrix}}_{\text{구할 것}}
\begin{bmatrix} \Psi(X) \\ U \end{bmatrix}
\quad\Longrightarrow\quad
\begin{bmatrix} K & B \end{bmatrix} = \Psi(Y)\begin{bmatrix} \Psi(X) \\ U \end{bmatrix}^{\dagger}
$$

$U = [u_1, \dots, u_M]$ 는 입력 데이터 행렬. **여전히 닫힌 형태 해**이므로 빠르다.

> [!success] 이 형태가 지배적인 이유
> 결과가 **완전한 선형 상태공간 모델** $z_{t+1} = Kz_t + Bu_t$ 이다. 그러면 **LQR, MPC, Kalman filter를 문자 그대로 그대로** 적용할 수 있다. 논문이 말하는 *"aligns naturally with classical control design tools"* 가 이 뜻이며, [[Koopman MPC]]에서 최적화 문제가 **볼록 QP**가 되는 근거이기도 하다.

> [!note] 이론적 위치
> 이 형태는 [36]의 **input-state separable model의 특수한 경우**다. 즉 임시방편이 아니라 확실한 이론적 배경이 있으며, 그 프레임이 근사 오차 분석까지 제공한다.

### (3) Control-coherent Koopman [37]

서로 다른 제어 입력 하에서 Koopman 임베딩의 **일관성(consistency)을 보존**하는 데 초점.

- 제어 입력이 변해도 진화 연산자가 **coherent하게 유지되는 임베딩 공간**을 찾는다
- **새로운 제어 시퀀스로의 일반화**가 개선되고, 입력 변동에 robust한 연산자 학습을 지원
- **적합**: manipulation, underactuated system — 입력 변화가 태스크 성패를 좌우하는 경우

### 3가지 비교

| 방식 | 리프팅 대상 | 모델 형태 | 볼록성 | 주 단점 |
|:---|:---|:---|:---:|:---|
| Joint lifting | $g(x,u)$ | 선형 (확장 상태) | ✅ | 미래 입력 가정, 일반화 취약 |
| **Input-affine** | $\psi(x)$ | $Kz + Bu$ | ✅ | 입력 아핀성이 근사일 뿐 |
| Control-coherent | 학습된 임베딩 | 일관성 제약 | 상황 의존 | 최신 기법, 계산 비용 |

---

## 3. 이론적으로 엄밀한 프레임 2가지 (논문 V-B절)

### (A) 무한 입력 시퀀스 전체를 고려 [105] (Korda & Mezić)

**발상**: 가능한 **모든 입력 시퀀스**를 상태의 일부로 넣어버린다.

$\ell(\mathcal{U})$ 를 모든 무한 입력 시퀀스 $\{u_s(i)\}_{i=0}^{\infty}$ 의 공간이라 하고, $S : \ell(\mathcal{U}) \to \ell(\mathcal{U})$ 를 **좌시프트 연산자(left-shift)** 라 하자 ($\{u_s(i)\}_{i=0}^\infty \mapsto \{u_s(i)\}_{i=1}^\infty$).

확장 상태 $\chi := (x, u_s) \in \mathcal{X}\times\ell(\mathcal{U})$ 에 대해 **자율 시스템**을 정의한다.

$$
\chi^+ = \big(T_u(x, u_s(0)),\ S u_s\big) =: L(\chi) \tag{논문 (22)}
$$

> [!important] 트릭의 핵심
> 입력 시퀀스를 상태에 포함시키고 "시프트"를 그 동역학으로 삼으면, **제어 시스템이 자율 시스템으로 바뀐다.** 그러면 (2)식의 표준 Koopman 정의를 그대로 쓸 수 있다.
> $$\mathcal{K}_L f = f\circ L, \qquad \forall f \in \mathcal{H} \tag{논문 (23)}$$

**한계**: 무한 입력 시퀀스에 의존하므로 유한차원 모델을 직접 찾을 방법이 없다. 그래서 [105]는 MPC(짧은 구간 예측만 정확하면 됨)를 목표로, **linear predictor** 근사를 가정한다.

$$
z^+ \approx Az + Bu, \qquad z_0 = \psi(x_0) \tag{논문 (24)}
$$

$A, B$ 는 EDMD류 방법으로 추정. **주의**: 이 모델은 무한 입력 시퀀스를 고려하지 않으므로 $\mathcal{K}_L$ 의 정보를 일반적으로 다 담지 못한다. **리프팅 차원을 무한대로 보내도 궤적 수렴을 일반적으로 결론지을 수 없다** (논문 명시).

### (B) Koopman Control Family (KCF) [36] (Haseli & Cortés)

**발상**: 무한 시퀀스를 쓰지 말고, **입력을 상수로 고정한 시스템들의 족(family)** 으로 표현하자.

$$
x^+ = T_{\hat{u}}(x) := T_u(x, u \equiv \hat{u}), \qquad \hat{u}\in\mathcal{U} \tag{논문 (25)}
$$

임의의 입력 시퀀스 $\{u_i\}$ 로 생성된 궤적은 이 상수입력 시스템들의 **합성**으로 정확히 표현된다.

$$
x_{m+1} = T_{u_m}\circ T_{u_{m-1}}\circ\cdots\circ T_{u_0}(x_0) \tag{논문 (26)}
$$

각 부분시스템마다 Koopman 연산자를 정의하면 — 이것이 **Koopman Control Family** $\{\mathcal{K}_{\hat u}\}_{\hat u \in \mathcal{U}}$ —

$$
\mathcal{K}_{\hat u}\,g = g\circ T_{\hat u}, \qquad \forall g\in\mathcal{F}
$$

그러면 궤적을 따른 관측값 진화가 **연산자들의 곱**으로 표현된다.

$$
g(x_{m+1}) = \big[\mathcal{K}_{u_0}\mathcal{K}_{u_1}\cdots\mathcal{K}_{u_m}g\big](x_0)
$$

### Input-State Separable Model ⭐

KCF의 **공통 불변 부분공간(common invariant subspace)** 위에서 모델은 반드시 다음 형태를 갖는다 ([36, Th. 4.3]).

$$
\boxed{\;\psi(x^+) = \psi\circ T(x,u) = A(u)\,\psi(x)\;}
$$

여기서 $\psi : \mathcal{X}\to\mathbb{C}^{N_\psi}$ 는 리프팅 함수, $A : \mathcal{U}\to\mathbb{C}^{N_\psi\times N_\psi}$ 는 **행렬값 함수**다.

> [!important] 이 형태를 읽는 법
> **리프팅 상태에 대해서는 선형, 입력에 대해서는 비선형.**
>
> 왜 입력에 비선형이어야 하는가? 개루프에서 입력은 정해진 동역학을 따르지 않으므로, **Koopman 연산자의 구조로 입력의 비선형성을 선형 연산자로 표현할 수 없기 때문**이다.

**통합적 관점**: 널리 쓰이는 모델들이 전부 이 형태의 특수 사례다 ([36, Lemmas 4.4–4.5]).

| 모델 | $A(u)$ 형태 |
|:---|:---|
| **Linear (lifted)** | $A(u)\psi = K\psi + Bu$ → 상수 + 아핀 항 |
| **Bilinear** | $A(u) = K + \sum_{j=1}^{N_u} u_j B_j$ |
| **Linear switched** [161] | $A(u) = A_{\sigma(u)}$, 유한 개 모드 |

즉 **리프팅 선형/쌍선형/스위칭 모델은 모두 KCF 연산자들의 서로 다른 유한차원 근사**로 이해된다.

### 두 프레임의 관계

> [!note] 동등하지만 용도가 다르다
> 적절한 함수공간 조건 하에서 두 확장은 **동등함이 증명되어 있다** [162]. 다만 정보를 다루는 방식이 근본적으로 다르므로 용도가 갈린다.
>
> | 상황 | 적합한 프레임 |
> |:---|:---|
> | 모든 가능한 입력 하의 일반 이론 분석, 불변량, 도달불가능 집합, 스펙트럼 성질 | **무한 입력 시퀀스** [105] (단일 연산자라서 유리) |
> | 유한차원 표현, 유한시간 궤적, MPC 유한구간 예측, 궤적 데이터 기반 학습 | **KCF** [36] (무한 시퀀스 불필요 + input-state separable form) |

---

## 4. Bilinear 모델 — 실무의 절충안

$$
z_{t+1} = K z_t + \sum_{j=1}^{N_u} u_{t,j}\,B_j z_t + B u_t
$$

- **선형 모델보다 표현력이 높다** (입력과 상태의 상호작용을 포착)
- **비선형 모델보다 구조가 단순하다**
- **대가**: [[Koopman MPC|MPC]] 문제가 **비볼록**이 되어 국소 최적해만 얻을 수 있고 계산이 느려진다
- 논문 [43][97]: 최근 활발히 탐구되는 방향. 예측 정확도가 충분히 개선되면 이 트레이드오프가 정당화된다

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 자율 시스템의 원형
> - [[EDMD]] — $[K\ B]$ 추정의 기반
> - [[Koopman MPC]] — 입력 아핀 모델의 직접적 응용
> - [[Koopman-Invariant Subspace]] — KCF의 공통 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
