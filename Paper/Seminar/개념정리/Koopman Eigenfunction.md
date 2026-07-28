---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Theory
aliases:
  - Koopman 고유함수
  - Eigenfunction
  - Koopman Mode
keywords: eigenfunction, eigenvalue, spectrum, Koopman mode decomposition
related notes: "[[Koopman Operator]], [[EDMD]], [[Koopman-Invariant Subspace]]"
dg-publish: false
---

# Koopman Eigenfunction (쿠프만 고유함수)

> [!abstract] 한 줄 요약
> Koopman 연산자의 고유함수를 따라가면 **비선형 동역학이 단 하나의 스칼라 곱셈 $\lambda$ 로 축소된다.** 이것이 비선형 시스템의 안정성·불변량·좌표변환을 선형대수의 언어로 다룰 수 있게 하는 통로다.

---

## 1. 정의

함수 $\phi \in \mathcal{F}$ 와 스칼라 $\lambda \in \mathbb{C}$ 가

$$
\boxed{\;\mathcal{K}\phi = \lambda\phi\;}
$$

를 만족하면, $\phi$ 를 **Koopman 고유함수**, $\lambda$ 를 **Koopman 고유값**이라 한다.

$\mathcal{K}\phi = \phi \circ T$ 이므로 이것을 풀어쓰면

$$
\phi\big(T(x)\big) = \lambda\,\phi(x), \qquad \forall x \in \mathcal{X}
$$

**즉, 상태를 한 스텝 전파한 뒤 $\phi$ 로 재면, 원래 값에 $\lambda$ 를 곱한 것과 같다.**

---

## 2. 왜 강력한가 — 동역학의 완전한 대각화

고유함수를 따라 시간을 전개하면:

$$
\phi(x_t) = \lambda\,\phi(x_{t-1}) = \lambda^2\phi(x_{t-2}) = \cdots = \boxed{\lambda^t\,\phi(x_0)}
$$

**비선형 시스템의 궤적을 한 줄의 지수 함수로 예측한다.** 시뮬레이션 없이, 초기값 하나만 알면 임의 시점의 값이 나온다.

### 고유값의 물리적 의미

이산시간에서 $\lambda \in \mathbb{C}$ 를 극형식으로 $\lambda = |\lambda|e^{i\theta}$ 라 쓰면:

| 조건 | 거동 | 해석 |
|:---|:---|:---|
| $\|\lambda\| < 1$ | $\phi(x_t) \to 0$ | **감쇠 모드** — 이 방향으로 수축 |
| $\|\lambda\| = 1$ | 크기 유지, 각속도 $\theta$ 로 회전 | **지속 진동 / 보존량** |
| $\|\lambda\| > 1$ | 발산 | **불안정 모드** |
| $\lambda = 1$ | $\phi(x_t) = \phi(x_0)$ 상수 | **불변량(invariant)** — 보존되는 물리량 |

> [!success] 실용적 함의
> $\lambda = 1$ 인 고유함수는 **에너지, 운동량 같은 보존량**에 대응한다. $|\lambda| = 1$ 인 것들은 **끌개(attractor)의 위상 좌표**를 준다. 즉 고유함수를 찾는 것은 곧 **비선형 시스템의 자연 좌표계를 찾는 것**이다.

연속시간에서는 [[Koopman Operator|Koopman generator]] $\mathcal{L}_G\phi = \sigma\phi$ 이고, $\lambda = e^{\sigma \Delta t}$ 관계가 성립한다. $\mathrm{Re}(\sigma) < 0$ 이 감쇠, $\mathrm{Im}(\sigma)$ 가 진동 주파수다.

---

## 3. 고유함수는 1차원 불변 부분공간이다

$\mathcal{S} = \mathrm{span}\{\phi\}$ 를 생각하면, $\mathcal{K}(c\phi) = c\lambda\phi \in \mathcal{S}$ 이므로 **$\mathcal{S}$ 는 자동으로 [[Koopman-Invariant Subspace|Koopman 불변]]** 이다.

> [!important] 관점의 전환
> **좋은 딕셔너리를 찾는 문제 = 고유함수들을 찾는 문제**다. 고유함수 $\phi_1, \dots, \phi_r$ 을 딕셔너리로 쓰면
> $$
> K = \mathrm{diag}(\lambda_1, \dots, \lambda_r)
> $$
> 즉 **완전 대각 행렬**이 되어 모드들이 서로 완전히 분리된다. 이것이 이론적으로 가장 이상적인 리프팅이다.

### 고유함수의 곱셈 성질

$\phi_1, \phi_2$ 가 각각 $\lambda_1, \lambda_2$ 에 대응하는 고유함수라면, 그 곱도 고유함수다.

$$
\mathcal{K}(\phi_1\phi_2)(x) = \phi_1(T(x))\phi_2(T(x)) = \lambda_1\lambda_2\,\phi_1(x)\phi_2(x)
$$

$$
\Rightarrow\ \mathcal{K}(\phi_1\phi_2) = (\lambda_1\lambda_2)(\phi_1\phi_2)
$$

일반화하면 $\phi_1^{m_1}\phi_2^{m_2}\cdots$ 가 고유값 $\lambda_1^{m_1}\lambda_2^{m_2}\cdots$ 의 고유함수다. **소수의 고유함수만 찾아도 무한히 많은 고유함수를 생성할 수 있다** — 이것이 Koopman 스펙트럼이 조밀해지는 이유이기도 하다.

---

## 4. 데이터로 고유함수 구하기 — EDMD 좌고유벡터

[[EDMD]] 노트의 (9)식이 정확히 이 절차다.

**Step 1.** EDMD로 $K_{\mathrm{EDMD}} = \Psi(Y)\Psi(X)^\dagger$ 를 구한다.

**Step 2.** $K_{\mathrm{EDMD}}$ 의 **좌고유벡터(left eigenvector)** $v$ 를 구한다.

$$
v^\top K_{\mathrm{EDMD}} = \lambda\,v^\top
$$

**Step 3.** 근사 고유함수를 조합한다.

$$
\phi_{\mathrm{EDMD}}(\cdot) = v^\top\psi(\cdot) = \sum_{i=1}^{N_\psi} v_i\,\psi_i(\cdot)
$$

**검증**: 이 $\phi$ 에 대해 EDMD 예측자는
$$
\mathcal{P}^{\mathrm{EDMD}}_{\mathcal{K}\phi} = v^\top K_{\mathrm{EDMD}}\psi = \lambda v^\top \psi = \lambda\phi \tag{논문 (9)}
$$
정확히 고유함수 관계를 재현한다.

> [!warning] "좌"고유벡터인 이유
> $K$ 는 딕셔너리 계수 벡터에 작용한다. 함수 $f = v^\top\psi$ 의 계수는 행벡터 $v^\top$ 이므로, $\mathcal{K}f$ 의 계수는 $v^\top K$ 다. 따라서 $f$ 가 고유함수이려면 $v^\top K = \lambda v^\top$ 즉 **좌고유벡터** 조건이 된다. 우고유벡터를 쓰면 틀린다 (규약에 따라 $K$ 의 전치를 쓰면 뒤바뀌므로 **본인 코드의 규약을 반드시 확인**할 것).

---

## 5. 로보틱스 응용 사례

### Koopman 기반 Lyapunov 함수 [18]

$|\lambda| < 1$ 인 고유함수들로부터 **constructive control Lyapunov function**을 만들 수 있다. 예컨대 $V(x) = \sum_i |\phi_i(x)|^2$ 형태로 두면 $V(x_{t+1}) = \sum_i |\lambda_i|^2|\phi_i(x_t)|^2 < V(x_t)$ 가 자동으로 성립한다. **데이터로 학습한 모델에 안정성 증명서를 붙일 수 있다**는 뜻이며, 논문 서론이 강조하는 "formal properties"의 대표 사례다.

### 에피소딕 고유함수 학습 — 멀티로터 지면 효과 [78]

Folkestad et al.은 멀티로터가 착륙할 때 발생하는 **ground effect**(모델링이 어려운 공력)를 다루기 위해, 에피소드마다 **Koopman 고유함수 쌍을 반복 학습**하고 그로부터 실시간 제어 입력을 얻었다. 명목 제어 법칙에 비선형 보정을 점진적으로 더해가는 구조다.

---

## 6. 주의사항

> [!warning] 스펙트럼의 미묘함
> - **연속 스펙트럼**: 카오스적 시스템에서는 Koopman 연산자가 이산 고유값뿐 아니라 **연속 스펙트럼**을 가진다. 유한 EDMD로는 원리적으로 포착할 수 없다.
> - **spurious eigenvalue**: 딕셔너리가 불변이 아니면 $K_{\mathrm{EDMD}}$ 의 고유값 중 상당수가 시스템과 무관한 **허위 고유값**이다. residual 기반 필터링이 필요하다.
> - **약수렴만 보장**: Korda & Mezić [30]의 수렴 결과는 고유함수에 대해 **약수렴(weak convergence)** 만 준다. 점별(pointwise) 수렴이 아니다.

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 상위 개념, 연속시간 generator
> - [[EDMD]] — 좌고유벡터로 고유함수 추출
> - [[Koopman-Invariant Subspace]] — 고유함수 = 1차원 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
