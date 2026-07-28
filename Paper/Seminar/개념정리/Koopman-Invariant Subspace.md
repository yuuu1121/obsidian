---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Theory
aliases:
  - Koopman 불변 부분공간
  - Invariant Subspace
keywords: invariant subspace, SSD, T-SSD, exactness, finite-dimensional
related notes: "[[Koopman Operator]], [[EDMD]], [[Consistency Index]]"
dg-publish: false
---

# Koopman-Invariant Subspace (쿠프만 불변 부분공간)

> [!abstract] 한 줄 요약
> **유한차원 Koopman 근사가 "근사"가 아니라 "정확"해지는 유일한 조건.** 딕셔너리가 span 하는 부분공간이 Koopman 연산자에 대해 닫혀 있으면 예측 오차가 0이 된다. 실무의 거의 모든 오차는 "이 조건이 얼마나 깨져 있는가"로 환원된다.

---

## 1. 정의

$\mathcal{S} \subseteq \mathcal{F}$ 가 **Koopman 불변(invariant)** 이라는 것은:

$$
\boxed{\;\mathcal{K}g \in \mathcal{S}, \qquad \forall g \in \mathcal{S}\;}
$$

즉 **부분공간 안의 함수를 한 스텝 전파해도 여전히 그 부분공간 안에 머문다**는 뜻이다.

### 왜 이게 결정적인가

$\mathcal{S}$ 가 유한차원이고 불변이면, $\mathcal{K}$ 를 $\mathcal{S}$ 로 제한한 $\mathcal{K}|_{\mathcal{S}} : \mathcal{S} \to \mathcal{S}$ 는 **닫힌 선형 사상**이므로 행렬로 정확히 표현된다. 기저 $\psi$ 에 대해

$$
\mathcal{K}\psi = \psi \circ T = K\psi, \qquad K \in \mathbb{C}^{\dim(\mathcal{S}) \times \dim(\mathcal{S})}
$$

이것이 논문 (4)식이며, 여기에서 유한차원 선형 시스템 (5)식 $\psi(x_{t+1}) = K\psi(x_t)$ 가 **정확히(exactly)** 성립한다.

**불변이 아니면**: $\mathcal{K}g$ 가 $\mathcal{S}$ 밖으로 나가버리므로, 그 성분을 $\mathcal{S}$ 안으로 강제로 사영해야 한다. 그 사영에서 잘려나간 부분이 곧 **[[EDMD]] 오차**이며, multi-step rollout에서 누적된다.

---

## 2. 직관: "닫혀 있다"는 게 무슨 뜻인가

[[Observable Function]] 노트의 예제를 다시 보자.

$$
\dot{x}_1 = \mu x_1, \qquad \dot{x}_2 = \lambda(x_2 - x_1^2)
$$

$\mathcal{S} = \mathrm{span}\{x_1, x_2, x_1^2\}$ 를 잡으면, 각 기저원소를 전파해도

- $x_1$ 을 전파 → $\mu x_1$ ∈ $\mathcal{S}$ ✅
- $x_2$ 를 전파 → $\lambda x_2 - \lambda x_1^2$ ∈ $\mathcal{S}$ ✅
- $x_1^2$ 을 전파 → $2\mu x_1^2$ ∈ $\mathcal{S}$ ✅

**모두 $\mathcal{S}$ 안에 머문다 → 불변.** 그래서 3차원 선형 시스템이 정확했다.

반면 $\dot{x}_1 = \mu x_1 + x_2^2$ 였다면 $x_1^2$ 을 전파할 때 $x_1x_2^2$ 라는 **바깥 항**이 튀어나온다. 그걸 넣으면 또 다른 항이 나오고... **닫히지 않는다.** 이런 경우가 압도적 다수다.

> [!warning] 정확한 불변 부분공간은 희귀하다
> 논문 V-C절이 명시한다: *"Exact Koopman-invariant subspaces capturing complete information about the dynamics are rare."*
>
> 그래서 실무 전략은 **"약간의 오차를 허용하는 대신 더 많은(부정확한) 정보를 담는"** 쪽으로 간다. 문제는 그 근사 정확도를 **어떻게 특성화하고 튜닝하느냐**다. → T-SSD (아래 §4)

---

## 3. 딕셔너리 최적화의 함정 — Residual만으로는 부족하다

### 순진한 접근

딕셔너리 $\psi$ 를 NN 등 파라메트릭 함수족으로 두고 EDMD residual을 최소화한다. (6)과 (7)을 결합하면

$$
\underset{\psi}{\text{minimize}} \quad \big\| \Psi(Y) - \Psi(Y)\Psi(X)^\dagger\,\Psi(X) \big\|_F \tag{논문 (27)}
$$

**문제점 두 가지**:

1. $\psi$ 가 파라메트릭 족(NN 등)에 속하므로 **일반적으로 비볼록** → 전역 최적해 보장 없음
2. **더 심각**: residual을 작게 만드는 것이 **불변 부분공간에 가까워지는 것을 의미하지 않는다**

### 논문 Fig. 3의 반례 (매우 중요)

선형 시스템 $x^+ = 0.6x$ 와 딕셔너리 족

$$
\psi_\alpha(x) = [\,x,\ \ x + \alpha\sin(x)\,], \qquad \alpha \in [0.01, 100]
$$

를 생각하자.

> [!important] 핵심 관찰
> - **모든 $\alpha \in \mathbb{R}\setminus\{0\}$ 에 대해 $\mathrm{span}(\psi_\alpha) = \mathrm{span}\{x, \sin(x)\} =: \mathcal{S}$ 로 동일하다.** ($\alpha$ 는 기저의 선택만 바꿀 뿐 부분공간은 그대로)
> - 그런데 **EDMD residual은 $\alpha$ 에 따라 달라진다** — 심지어 임의로 0에 가깝게 만들 수 있다.
> - 하지만 $\mathcal{S}$ 는 **불변이 아니다**.
>
> **결론**: residual이 작다고 좋은 부분공간이 아니다. residual은 **부분공간의 성질이 아니라 기저 선택의 artifact**를 반영한다. 따라서 (27)을 최소화해 얻은 모델은 **장기 예측(long-term prediction)에 부적합**할 수 있다.

이 함정을 피하기 위해 논문은 **basis-independent 지표**인 [[Consistency Index]]를 소개한다.

---

## 4. 불변 부분공간을 대수적으로 찾기 — SSD / T-SSD

최적화 기반 방법이 보장을 못 준다면, **대수적 탐색(algebraic search)** 으로 가면 된다.

### 데이터 관점의 불변성 조건

탐색 공간(search space)을 딕셔너리 $\psi_s$ 가 span 하는 유한차원 함수공간이라 하자. $\mathrm{span}(\psi_s)$ 안의 임의의 기저 $\psi$ 는 full column rank 행렬 $C$ 로 표현된다.

$$
\psi^\top(\cdot) = \psi_s^\top(\cdot)\,C
$$

$\mathrm{span}(\psi)$ 가 Koopman 불변이면, 그 사실이 **데이터에 반영된다**.

$$
\boxed{\;\mathcal{R}\big(\psi_s(X)^\top C\big) = \mathcal{R}\big(\psi_s(Y)^\top C\big)\;} \tag{논문 (31)}
$$

$\mathcal{R}(\cdot)$ 는 **range space (열공간)**. 직관적으로: *"$C$ 로 조합한 관측값들이 만드는 공간이, 한 스텝 전파 후에도 같은 공간이다."*

### SSD (Symmetric Subspace Decomposition) [31][32]

**목표**: (31)을 만족하는 **열 개수가 최대인 $C$** 를 찾기 = 탐색 공간 안의 **최대 Koopman-불변 부분공간**을 찾기.

- Haseli & Cortés [31]: 임의의 유한차원 함수공간에서 **모든 Koopman 고유함수를 식별**하는 데이터 기반 필요조건 + almost surely 충분조건 제시. 순방향/역방향 EDMD 행렬의 고유분해에 기반.
- [32]: 고차원 공간 탐색을 위한 **병렬(parallel) SSD**.
- **효율적이고 증명 가능하게 올바른(provably correct) 대수 알고리즘**이라는 점이 핵심.

### T-SSD (Tunable SSD) [33]

정확한 불변 부분공간은 희귀하므로, **오차를 허용하되 그 크기를 튜닝**할 수 있게 일반화한 것.

(31)의 **등식을 요구하는 대신**, 두 부분공간 $\mathcal{R}(\psi_s(X)^\top C)$ 와 $\mathcal{R}(\psi_s(Y)^\top C)$ 가 **가깝기만** 하면 된다고 완화한다. 그 거리를 정확도 파라미터 $\epsilon \in [0,1]$ 로 지정한다.

> [!success] T-SSD는 EDMD와 SSD를 잇는 스펙트럼이다 (논문 Fig. 5)
>
> | $\epsilon$ | 동등한 알고리즘 | 의미 |
> |:---:|:---|:---|
> | $\epsilon = 0$ | **SSD** | 예측 오차 0 요구 → 최대 **정확한** 불변 부분공간 |
> | $0 < \epsilon < 1$ | **T-SSD** | 정확도와 표현력(부분공간 차원)의 **균형** |
> | $\epsilon = 1$ | **EDMD** | 최대 100% 예측 오차 허용 → 탐색 공간 전체에 EDMD 적용 |
>
> 즉 T-SSD는 **정확도(accuracy) ↔ 표현력(expressiveness)** 트레이드오프를 $\epsilon$ 하나로 조절하는 통합 프레임이다.

**논문 Fig. 6 실험**: Duffing 시스템
$$
[\dot{x}_1, \dot{x}_2] = [\,x_2,\ -0.5x_2 + x_1(1-x_1^2)\,], \qquad \mathcal{X} = [-2,2]^2
$$
탐색 공간 = 차수 10 이하 모든 다항식. **T-SSD($\epsilon = 0.02$) 로 찾은 딕셔너리가 정규화된 전체 기저보다 상대 예측 오차가 훨씬 작다.**

---

## 5. 실무 체크리스트

1. **딕셔너리 크기를 키우기 전에 불변성을 의심하라.** 차원 증가 ≠ 성능 향상.
2. **1-step residual만 보고 판단하지 마라.** Fig. 3의 반례가 정확히 그 함정이다. → [[Consistency Index]] 사용.
3. **시스템 구조를 아는 만큼 딕셔너리에 넣어라.** 물리 기반 항이 불변성에 가까워지는 가장 값싼 방법이다.
4. **탐색 공간이 다항식으로 표현 가능하면 T-SSD를 고려하라.** 대수적 보장이 있는 유일한 경로다.
5. **long-horizon rollout으로 검증하라.** 불변성이 깨진 정도는 다단계 예측에서 지수적으로 드러난다.

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 불변 부분공간이 필요한 이유
> - [[Observable Function]] — 딕셔너리 설계 실무
> - [[EDMD]] — 불변성이 깨졌을 때 무슨 일이 생기는가
> - [[Consistency Index]] — basis-independent 품질 지표
> - [[Koopman Eigenfunction]] — 1차원 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
