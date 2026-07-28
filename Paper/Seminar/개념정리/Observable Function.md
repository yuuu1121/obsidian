---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
aliases:
  - 관측 함수
  - Lifting Function
  - 리프팅 함수
  - Dictionary
keywords: observable, lifting function, dictionary, basis function, RBF
related notes: "[[Koopman Operator]], [[Koopman-Invariant Subspace]], [[EDMD]]"
dg-publish: false
---

# Observable Function / Lifting Function (관측 함수 · 리프팅 함수)

> [!abstract] 한 줄 요약
> 상태 $x$ 를 고차원 공간으로 올려보내는 함수 $\psi(x)$. **Koopman 방법론의 성패를 사실상 결정하는 유일한 설계 변수**이며, 잘 고르면 선형 예측이 정확해지고 잘못 고르면 아무리 데이터가 많아도 예측이 무너진다.

---

## 1. 정의와 용어 정리

| 용어 | 의미 |
|:---|:---|
| **Observable** $g$ | 상태공간을 정의역으로 갖는 복소수값 함수 $g : \mathcal{X} \to \mathbb{C}$. "상태를 측정한 값". |
| **Lifting function** | observable 중에서 실제로 리프팅에 쓰려고 우리가 고른 것. 같은 말로 쓰인다. |
| **Dictionary** $\psi$ | 리프팅 함수들을 모아놓은 벡터값 함수 $\psi = [\psi_1, \psi_2, \dots, \psi_{N_\psi}]^\top$. |
| **Lifted state** $z$ | $z = \psi(x) \in \mathbb{R}^{N_\psi}$. Koopman 공간에서의 상태. |

$$
\underbrace{x \in \mathbb{R}^{N_x}}_{\text{원 상태, 저차원, 비선형}} \quad\xrightarrow{\ \psi\ }\quad \underbrace{z = \psi(x) \in \mathbb{R}^{N_\psi}}_{\text{리프팅 상태, 고차원}\ (N_\psi \gg N_x),\ \text{선형}}
$$

---

## 2. 왜 "리프팅"이 선형화를 만드는가 — 손으로 푸는 예제

가장 유명한 예제 (Brunton et al.의 표준 예제). 다음 비선형 시스템을 보자.

$$
\begin{aligned}
\dot{x}_1 &= \mu x_1 \\
\dot{x}_2 &= \lambda (x_2 - x_1^2)
\end{aligned}
$$

$x_1^2$ 항 때문에 **비선형**이다. 여기서 딕셔너리를 다음처럼 잡아보자.

$$
\psi(x) = \begin{bmatrix} x_1 \\ x_2 \\ x_1^2 \end{bmatrix} =: \begin{bmatrix} z_1 \\ z_2 \\ z_3 \end{bmatrix}
$$

$z_3 = x_1^2$ 의 시간 미분을 계산하면

$$
\dot{z}_3 = \frac{d}{dt}(x_1^2) = 2x_1\dot{x}_1 = 2x_1(\mu x_1) = 2\mu x_1^2 = 2\mu z_3
$$

이제 세 식을 모아 쓰면

$$
\frac{d}{dt}\begin{bmatrix} z_1 \\ z_2 \\ z_3 \end{bmatrix}
= \begin{bmatrix} \mu & 0 & 0 \\ 0 & \lambda & -\lambda \\ 0 & 0 & 2\mu \end{bmatrix}
\begin{bmatrix} z_1 \\ z_2 \\ z_3 \end{bmatrix}
$$

> [!success] 핵심
> **완전히 선형이다.** 근사가 아니라 **정확(exact)** 하다. 비선형항 $x_1^2$ 을 "없앤" 게 아니라 **새로운 좌표축 $z_3$ 으로 승격**시켰더니, 그 축의 동역학마저 자기 자신에 대해 닫혀버린 것이다.
>
> 이 예제에서 $\mathrm{span}\{x_1, x_2, x_1^2\}$ 는 [[Koopman-Invariant Subspace|Koopman 불변 부분공간]]이다. 3차원만으로 무한차원 문제가 정확히 닫힌 **운 좋은** 경우다.

**왜 운이 좋은가**: 만약 동역학이 $\dot{x}_1 = \mu x_1 + x_2^2$ 였다면 $\dot{z}_3 = 2x_1(\mu x_1 + x_2^2) = 2\mu z_3 + 2x_1x_2^2$ 이 되어 $x_1x_2^2$ 라는 **새 항이 튀어나오고**, 그걸 $z_4$ 로 넣으면 또 새 항이 나오고... 이렇게 닫히지 않는 경우가 일반적이다. 그래서 대부분의 실제 시스템에서는 유한 딕셔너리로 **근사**할 수밖에 없다.

---

## 3. 딕셔너리 설계 3가지 전략 (논문 III-B절)

### (1) 수동 선택 기저 함수 (Manually selected)

도메인 지식이나 시행착오로 고르는 방식.

| 종류 | 형태 | 적합한 상황 |
|:---|:---|:---|
| **다항식(Polynomial)** | $1, x_i, x_ix_j, x_i^2, \dots$ | 동역학이 다항식/약한 비선형. 저차원. |
| **Hermite 다항식** | $H_n(x)$ | 데이터가 **정규분포**를 따를 때 (직교성이 유리) |
| **RBF (Radial Basis Function)** | $\psi_i(x) = \exp(-\|x - c_i\|^2 / 2\sigma^2)$ 또는 thin-plate spline | 공간적으로 복잡한 구조. 중심 $c_i$ 를 데이터에서 샘플링. |
| **삼각함수 / 스펙트럼 요소** | $\sin(kx), \cos(kx)$ | 주기적 동역학. 블록 대각 관측 행렬로 이어짐 [27]. |

- **장점**: 해석 가능, 데이터 적게 필요, 계산 빠름
- **단점**: 노동집약적(labor-intensive), 다른 시스템으로 일반화 어려움
- **논문의 관찰**: **wheeled robot**처럼 동역학이 비교적 단순하고 잘 이해된 시스템에서 주로 쓰인다.

### (2) 물리 정보 기반 (Physics-informed)

로봇은 **kinematic constraint, DoF, geometric configuration space** 같은 구조를 갖는다. 전체 동역학 모델이 없어도 이 구조는 알 수 있다.

- Shi et al. [69]: **configuration symmetry**와 **workspace constraint**를 관측 공간 구성에 반영 → 해석 가능성 + robustness 향상
- [90]: **고차 시간 상태 미분(higher-order time state derivative)** 을 기저로 합성. 미분항이 표현력을 풍부하게 만든다.

> [!tip] 왜 미분항이 도움이 되는가
> 기계 시스템은 $\ddot{q} = f(q, \dot{q}, u)$ 꼴이다. 관측 공간에 $\dot{q}, \ddot{q}$ 를 넣으면 Koopman 연산자가 "이미 알려진 물리 구조"를 학습하는 데 데이터를 낭비하지 않아도 된다.

### (3) 신경망 기반 (NN-based) — Deep Koopman

리프팅 함수 자체를 데이터로부터 학습한다.

- **Deep Koopman** [102] / **Autoencoder-Koopman** [16]:
  - 인코더 $\psi_\theta : x \mapsto z$ (NN)
  - 잠재 공간에서 선형 전파 $z_{t+1} = Kz_t$
  - 디코더 $\psi^{-1}_\theta : z \mapsto x$
  - Loss = 재구성 오차 + 선형 예측 오차

$$
\mathcal{L} = \underbrace{\|x - \psi^{-1}_\theta(\psi_\theta(x))\|^2}_{\text{reconstruction}} + \underbrace{\|\psi_\theta(x_{t+1}) - K\psi_\theta(x_t)\|^2}_{\text{linearity}} + \underbrace{\|x_{t+1} - \psi^{-1}_\theta(K\psi_\theta(x_t))\|^2}_{\text{prediction}}
$$

- **장점**: 높은 유연성·표현력
- **단점**: 해석 가능성 상실, **OOD(out-of-distribution) 일반화 취약**, overfitting 위험, 데이터 많이 필요
- **논문의 관찰**: **manipulation**과 **legged locomotion**에서 널리 채택 — 동역학이 매우 복잡·비선형이기 때문.

---

## 4. 논문이 정리한 플랫폼별 경향 (Table I 요약)

| 로봇 플랫폼 | 선호되는 리프팅 방식 | 이유 |
|:---|:---|:---|
| Manipulator, Legged | **NN 기반** | 동역학의 복잡성·비선형성이 높음 |
| Wheeled robot | **수동 설계** | 동역학이 비교적 단순하고 잘 알려짐 |
| Aerial robot | 전부 (특히 **[[HVOK]]**) | 강한 환경 외란(gust, ground effect) 포착에 시간지연이 유리 |
| Soft robot | 전부 (특히 **[[HVOK]]**) | 느린 응답 특성(slow response) 포착에 시간지연이 유리 |

---

## 5. 논문의 결정적 경고

> [!warning] 대부분의 방법에 수렴성 보장이 없다
> 논문 III-B 말미에 명시된다: 위에 소개한 실용적 방법들은 **대부분 엄밀한 수렴 분석이 없다**. 즉 구성된 observable들이 실제로 **Koopman 불변 부분공간을 span 하는지**, 또는 참 Koopman 연산자의 **정확한 근사인지** 검증하지 않는다.
>
> 이 gap을 메우기 위해 논문은 V-C절에서 이론적 논의(consistency index, SSD, T-SSD)를 별도로 전개한다. → [[Consistency Index]]

---

## 6. 실전 체크리스트

1. **상태 자체를 딕셔너리에 포함하라** ($\psi$ 의 첫 $N_x$ 성분 $= x$). 그래야 리프팅 상태에서 원 상태를 디코더 없이 읽을 수 있다 (full-state observability).
2. **상수함수 $\psi_0 = 1$ 을 넣을지 결정하라**. 넣으면 affine 항(bias)을 표현할 수 있다.
3. **차원 $N_\psi$ 는 무작정 키우지 마라**. 불변성에 가까워지지 않으면 오히려 나빠진다 ([[Koopman Operator]] §7 오해 2 참고).
4. **정규화/스케일링**. RBF 폭 $\sigma$ 나 다항식 차수는 상태 범위에 민감하다.
5. **검증은 long-horizon 예측으로 하라**. 1-step 오차가 작아도 다단계 예측이 발산할 수 있다 ([[Consistency Index]]가 정확히 이 문제를 다룬다).

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 상위 개념
> - [[Koopman-Invariant Subspace]] — "좋은 딕셔너리"의 수학적 정의
> - [[EDMD]] — 딕셔너리가 정해진 뒤 $K$ 를 추정하는 법
> - [[Consistency Index]] — 딕셔너리 품질의 basis-independent 척도
> - [[HVOK]] — 딕셔너리 설계를 우회하는 시간지연 방식
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
