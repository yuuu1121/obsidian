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

> [!abstract] 한 문장 요약
> Koopman은 원래 자율(unforced) 시스템을 위해 만들어졌는데, 제어 입력 $u$ 를 넣는 순간 **"상태는 내부 동역학을 따르지만 입력은 그렇지 않다"** 는 근본적 비대칭 때문에 이론이 까다로워지며, 그 어려움은 결국 **"리프팅 상태에는 선형, 입력에는 비선형일 수밖에 없다"** 는 하나의 결론으로 수렴합니다.

아래 1→9번을 순서대로 읽으면 왜 그런 결론에 도달하는지가 쌓입니다.

---

## 1. 왜 어려운가 — 상태와 입력의 근본적 비대칭

먼저 제어 시스템을 정의합니다.

$$
x_{t+1} = T_u(x_t, u_t), \qquad x \in \mathcal{X} \subseteq \mathbb{R}^{N_x},\ u \in \mathcal{U} \subseteq \mathbb{R}^{N_u}
$$

여기서 주목할 것은 $x$ 와 $u$ 가 시스템에서 완전히 다른 역할을 한다는 점입니다.

> [!important] 논문이 짚는 핵심 난점
> - **상태 $x$**: 시스템의 내재적 속성입니다. 내부 동역학에 따라 진화하므로, Koopman 연산자가 다룰 수 있습니다.
> - **입력 $u$**: 특히 개루프(open-loop)에서는 사전에 알 수 없고, 시스템 진화에 큰 영향을 줍니다. **정해진 동역학 규칙을 따르지 않습니다.** 그래서 Koopman 연산자의 구조로 표현할 방법이 없습니다.
>
> 즉 $u$ 는 "동역학을 갖지 않는 객체"이니, "동역학의 선형 표현"인 Koopman 틀에 자연스럽게 들어가지 않습니다.

이 비대칭이 이 노트 전체를 관통하는 하나의 문제입니다. 논문은 이를 다루는 방법을 두 갈래로 제시합니다. 먼저 **실용적 근사 3가지**(II-C절, 2~4번)를 보고, 이어서 **이론적으로 엄밀한 프레임 2가지**(V-B절, 5~6번)를 봅니다. 그리고 7번에서 이 둘이 결국 하나의 통합된 형태로 만난다는 것을 확인합니다.

---

## 2. 실용적 근사 ① Joint lifting

첫 번째 근사는 입력 $u$ 를 아예 확장 상태의 일부로 취급하는 것입니다. 결합 공간 위에서 관측 함수 $g(x,u)$ 를 정의합니다.

$$
\psi(x_t, u_t) \ \longrightarrow\ \psi(x_{t+1}, u_{t+1}) = K\,\psi(x_t, u_t)
$$

이 방식은 직관적이고 구현이 간단하다는 장점이 있습니다. 하지만 **미래 입력을 안다고 가정**해야 한다는 근본적인 단점을 피할 수 없습니다. 1번에서 본 것처럼 $u$ 는 동역학 규칙을 안 따르므로, $u$ 가 임의로 변하면 일반화에 실패합니다.

그래서 이 방식은 구조화되거나 반복적인 입력 패턴(structured or repetitive input patterns)을 갖는 학습 기반 로봇 시스템에 적합합니다.

---

## 3. 실용적 근사 ② Input-affine — 가장 널리 쓰이는 형태

두 번째 근사는 관측값의 진화가 **입력에 대해 아핀(affine)** 이라고 가정하는 것입니다. (아핀이 정확히 무엇이고 왜 "선형"과 구분되는지는 📎 [[Affine]] 참고)

$$
\boxed{\;\psi(x_{t+1}) \approx K\,\psi(x_t) + B\,u_t\;}
$$

여기서 $K$ 는 자율(autonomous) 부분에 대한 유한차원 Koopman 근사이고, $B$ 는 제어 입력의 선형 영향입니다.

**추정 방법**은 [[EDMD]]를 그대로 확장하면 됩니다. 리프팅 상태와 입력을 세로로 쌓아 최소제곱을 풉니다.

$$
\Psi(Y) \approx \underbrace{\begin{bmatrix} K & B \end{bmatrix}}_{\text{구할 것}}
\begin{bmatrix} \Psi(X) \\ U \end{bmatrix}
\quad\Longrightarrow\quad
\begin{bmatrix} K & B \end{bmatrix} = \Psi(Y)\begin{bmatrix} \Psi(X) \\ U \end{bmatrix}^{\dagger}
$$

$U = [u_1, \dots, u_M]$ 는 입력 데이터 행렬입니다. 이 역시 **여전히 닫힌 형태 해**이므로 빠릅니다.

이 형태가 왜 지배적인지는 다음 콜아웃에 주목하세요.

> [!success] 이 형태가 지배적인 이유
> 결과가 **완전한 선형 상태공간 모델** $z_{t+1} = Kz_t + Bu_t$ 입니다. 그러면 LQR, MPC, Kalman filter를 문자 그대로 적용할 수 있습니다. 논문이 말하는 *"aligns naturally with classical control design tools"* 가 이 뜻이며, [[Koopman MPC]]에서 최적화 문제가 **볼록 QP**가 되는 근거이기도 합니다.

> [!note] 이론적 위치
> 이 형태는 [36]의 **input-state separable model의 특수한 경우**입니다. 즉 임시방편이 아니라 확실한 이론적 배경이 있으며, 그 프레임이 근사 오차 분석까지 제공합니다. 이 관계는 7번에서 다시 등장합니다.

---

## 4. 실용적 근사 ③ Control-coherent, 그리고 3가지 비교

세 번째 근사인 **Control-coherent Koopman** [37]은 서로 다른 제어 입력 하에서 Koopman 임베딩의 **일관성(consistency)을 보존**하는 데 초점을 둡니다.

제어 입력이 변해도 진화 연산자가 coherent하게 유지되는 임베딩 공간을 찾는 것이 핵심입니다. 그 결과 새로운 제어 시퀀스로의 일반화가 개선되고, 입력 변동에 robust한 연산자 학습을 지원합니다. 이 방식은 manipulation, underactuated system처럼 입력 변화가 태스크 성패를 좌우하는 경우에 적합합니다.

세 가지 근사를 정리하면 다음과 같습니다.

| 방식 | 리프팅 대상 | 모델 형태 | 볼록성 | 주 단점 |
|:---|:---|:---|:---:|:---|
| Joint lifting | $g(x,u)$ | 선형 (확장 상태) | ✅ | 미래 입력 가정, 일반화 취약 |
| **Input-affine** | $\psi(x)$ | $Kz + Bu$ | ✅ | 입력 아핀성이 근사일 뿐 |
| Control-coherent | 학습된 임베딩 | 일관성 제약 | 상황 의존 | 최신 기법, 계산 비용 |

여기까지가 논문 II-C절의 실용적 근사입니다. 이제 왜 이런 근사가 필요했는지를 **이론적으로 엄밀하게** 다루는 V-B절의 두 프레임으로 넘어갑니다.

---

## 5. 이론 프레임 (A) 무한 입력 시퀀스 [105] (Korda & Mezić)

첫 번째 이론 프레임의 발상은, 가능한 **모든 입력 시퀀스**를 상태의 일부로 넣어버리는 것입니다. 이렇게 하면 1번의 비대칭 문제 — 입력은 동역학을 따르지 않는다는 문제 — 를 정면으로 우회할 수 있습니다.

$\ell(\mathcal{U})$ 를 모든 무한 입력 시퀀스 $\{u_s(i)\}_{i=0}^{\infty}$ 의 공간이라 하고, $S : \ell(\mathcal{U}) \to \ell(\mathcal{U})$ 를 **좌시프트 연산자(left-shift)** 라 합시다 ($\{u_s(i)\}_{i=0}^\infty \mapsto \{u_s(i)\}_{i=1}^\infty$).

확장 상태 $\chi := (x, u_s) \in \mathcal{X}\times\ell(\mathcal{U})$ 에 대해 **자율 시스템**을 정의합니다.

$$
\chi^+ = \big(T_u(x, u_s(0)),\ S u_s\big) =: L(\chi) \tag{논문 (22)}
$$

> [!important] 트릭의 핵심
> 입력 시퀀스를 상태에 포함시키고 "시프트"를 그 동역학으로 삼으면, **제어 시스템이 자율 시스템으로 바뀝니다.** 그러면 (2)식의 표준 Koopman 정의를 그대로 쓸 수 있습니다.
> $$\mathcal{K}_L f = f\circ L, \qquad \forall f \in \mathcal{H} \tag{논문 (23)}$$

다만 이 방식에는 한계가 있습니다. 무한 입력 시퀀스에 의존하므로 유한차원 모델을 직접 찾을 방법이 없습니다. 그래서 [105]는 MPC(짧은 구간 예측만 정확하면 됨)를 목표로, **linear predictor** 근사를 가정합니다.

$$
z^+ \approx Az + Bu, \qquad z_0 = \psi(x_0) \tag{논문 (24)}
$$

$A, B$ 는 EDMD류 방법으로 추정합니다. **주의할 점**은 이 모델이 무한 입력 시퀀스를 고려하지 않으므로 $\mathcal{K}_L$ 의 정보를 일반적으로 다 담지 못한다는 것입니다. **리프팅 차원을 무한대로 보내도 궤적 수렴을 일반적으로 결론지을 수 없습니다** (논문 명시).

---

## 6. 이론 프레임 (B) Koopman Control Family (KCF) [36] (Haseli & Cortés)

두 번째 이론 프레임의 발상은, 무한 시퀀스를 쓰지 않고 **입력을 상수로 고정한 시스템들의 족(family)** 으로 표현하는 것입니다.

$$
x^+ = T_{\hat{u}}(x) := T_u(x, u \equiv \hat{u}), \qquad \hat{u}\in\mathcal{U} \tag{논문 (25)}
$$

임의의 입력 시퀀스 $\{u_i\}$ 로 생성된 궤적은 이 상수입력 시스템들의 **합성**으로 정확히 표현됩니다.

$$
x_{m+1} = T_{u_m}\circ T_{u_{m-1}}\circ\cdots\circ T_{u_0}(x_0) \tag{논문 (26)}
$$

각 부분시스템마다 Koopman 연산자를 정의하면 — 이것이 **Koopman Control Family** $\{\mathcal{K}_{\hat u}\}_{\hat u \in \mathcal{U}}$ 입니다.

$$
\mathcal{K}_{\hat u}\,g = g\circ T_{\hat u}, \qquad \forall g\in\mathcal{F}
$$

그러면 궤적을 따른 관측값 진화가 **연산자들의 곱**으로 표현됩니다.

$$
g(x_{m+1}) = \big[\mathcal{K}_{u_0}\mathcal{K}_{u_1}\cdots\mathcal{K}_{u_m}g\big](x_0)
$$

---

## 7. Input-State Separable Form — 통합 관점 (이 노트의 클라이맥스)

KCF의 **공통 불변 부분공간(common invariant subspace)** 위에서 모델은 반드시 다음 형태를 갖습니다 ([36, Th. 4.3]).

$$
\boxed{\;\psi(x^+) = \psi\circ T(x,u) = A(u)\,\psi(x)\;}
$$

여기서 $\psi : \mathcal{X}\to\mathbb{C}^{N_\psi}$ 는 리프팅 함수, $A : \mathcal{U}\to\mathbb{C}^{N_\psi\times N_\psi}$ 는 **행렬값 함수**입니다.

이제 1번의 비대칭이 여기서 정확히 회수됩니다.

> [!important] 이 형태를 읽는 법
> **리프팅 상태에 대해서는 선형, 입력에 대해서는 비선형입니다.**
>
> 왜 입력에는 비선형이어야 할까요? 1번에서 본 것처럼 개루프에서 입력은 정해진 동역학을 따르지 않습니다. 그러니 **Koopman 연산자의 구조로 입력의 비선형성을 선형 연산자로 표현할 수 없기 때문**입니다. 상태의 "내재적 동역학"과 입력의 "동역학 없음"이라는 1번의 구분이, 결국 "상태엔 선형·입력엔 비선형"이라는 하나의 수식으로 응축된 셈입니다.

이 통합 관점의 힘은 여기서 드러납니다. **널리 쓰이는 모델들이 전부 이 형태의 특수 사례**입니다 ([36, Lemmas 4.4–4.5]).

| 모델 | $A(u)$ 형태 |
|:---|:---|
| **Linear (lifted)** | $A(u)\psi = K\psi + Bu$ → 상수 + 아핀 항 |
| **Bilinear** | $A(u) = K + \sum_{j=1}^{N_u} u_j B_j$ |
| **Linear switched** [161] | $A(u) = A_{\sigma(u)}$, 유한 개 모드 |

즉 3번의 input-affine 근사, 9번의 bilinear 모델, 그리고 스위칭 모델까지 **전부 KCF 연산자들의 서로 다른 유한차원 근사**로 이해됩니다.

<details>
<summary><b>왜 3번(input-affine)이 이 통합 형태의 특수 사례인가</b></summary>

3번에서 본 $\psi(x_{t+1}) \approx K\psi(x_t) + Bu_t$ 는 $A(u) = K + Bu$ (선형 항만 있는 아핀 함수)로 두면 그대로 얻어집니다. 즉 "가장 널리 쓰이는 실용적 근사"는 사실 $A(u)$ 를 $u$ 에 대한 **1차 다항식**으로 제한한 것이고, bilinear 모델은 이를 조금 더 일반화해 $u_j$ 별 계수 행렬 $B_j$ 를 따로 두는 것뿐입니다. 결국 근사들 사이의 차이는 $A(u)$ 를 얼마나 풍부하게 표현하느냐의 문제로 환원됩니다.
</details>

### 두 프레임의 관계와 용도 구분

> [!note] 동등하지만 용도가 다르다
> 적절한 함수공간 조건 하에서 5번과 6번의 두 확장은 **동등함이 증명되어 있습니다** [162]. 다만 정보를 다루는 방식이 근본적으로 다르므로 용도가 갈립니다.
>
> | 상황 | 적합한 프레임 |
> |:---|:---|
> | 모든 가능한 입력 하의 일반 이론 분석, 불변량, 도달불가능 집합, 스펙트럼 성질 | **무한 입력 시퀀스** [105] (단일 연산자라서 유리) |
> | 유한차원 표현, 유한시간 궤적, MPC 유한구간 예측, 궤적 데이터 기반 학습 | **KCF** [36] (무한 시퀀스 불필요 + input-state separable form) |

---

## 8. Bilinear 모델 — 실무의 절충안

7번의 표에서 본 bilinear 모델을 조금 더 자세히 봅니다.

$$
z_{t+1} = K z_t + \sum_{j=1}^{N_u} u_{t,j}\,B_j z_t + B u_t
$$

이 모델은 선형 모델보다 표현력이 높습니다 (입력과 상태의 상호작용을 포착합니다). 동시에 비선형 모델보다는 구조가 단순합니다.

다만 대가가 있습니다. [[Koopman MPC|MPC]] 문제가 **비볼록**이 되어 국소 최적해만 얻을 수 있고 계산이 느려집니다. 논문 [43][97]에 따르면 이는 최근 활발히 탐구되는 방향이며, 예측 정확도가 충분히 개선되면 이 트레이드오프가 정당화됩니다.

---

## 📌 전체 흐름 한 눈에

```
①  근본 문제        상태 x: 내재적 동역학 (Koopman 가능) vs 입력 u: 동역학 없음 (Koopman 불가)
        │
        ├─ 실용적 근사 (II-C절) ──────────────────────────────
        │   ②  Joint lifting        ψ(x,u) 결합 리프팅 — 미래 입력 가정 필요
        │   ③  Input-affine ⭐      ψ(x⁺) ≈ Kψ(x) + Bu  — [K B] = Ψ(Y)[Ψ(X);U]†
        │   ④  Control-coherent     임베딩 일관성 보존
        │
        └─ 이론적 프레임 (V-B절) ──────────────────────────────
            ⑤  무한 입력 시퀀스 [105]   좌시프트로 자율계 전환 → 식(22)(23) → linear predictor (24)
            ⑥  KCF [36]                상수입력 족 → 식(25)(26)
                    │
            ⑦  Input-state separable form   ψ(x⁺) = A(u)ψ(x)
                    │  ← 상태엔 선형, 입력엔 비선형 (①의 비대칭이 여기로 회수됨)
                    │  ← linear/bilinear/switched 모두 이것의 특수 사례
                    │
            ⑧  Bilinear 모델   실무 절충안 (표현력 ↑, 볼록성 상실)
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| $[K\ B]$ 추정의 기반이 되는 최소자승/닫힌형 해 | [[EDMD]] |
| Input-affine 모델의 직접적 응용 (볼록 QP) | [[Koopman MPC]] |
| KCF의 공통 불변 부분공간이 무엇인가 | [[Koopman-Invariant Subspace]] |
| 왜 input-affine이 이 통합 형태의 특수 사례인가 | ↑ 7번의 접힌 섹션 |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 자율 시스템의 원형
> - [[EDMD]] — $[K\ B]$ 추정의 기반
> - [[Koopman MPC]] — 입력 아핀 모델의 직접적 응용
> - [[Koopman-Invariant Subspace]] — KCF의 공통 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
