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

> [!abstract] 한 문장 요약
> 이 노트는 **"유한차원 Koopman 근사가 근사가 아니라 정확해지는 유일한 조건"**을 다루며, 그 조건을 재는 가장 그럴듯한 방법(residual 최소화)이 왜 함정인지, 그래서 대신 무엇을 써야 하는지까지 이어집니다.

아래 1→8번을 순서대로 읽으면 "불변 부분공간"이라는 조건이 왜 필요하고, 왜 다루기 까다로운지가 쌓입니다.

---

## 1. 정의 — 왜 이 조건이 결정적인가

$\mathcal{S} \subseteq \mathcal{F}$ 가 **Koopman 불변(invariant)** 이라는 것은 다음을 만족한다는 뜻입니다.

$$
\boxed{\;\mathcal{K}g \in \mathcal{S}, \qquad \forall g \in \mathcal{S}\;}
$$

쉽게 말해 **부분공간 안의 함수를 한 스텝 전파해도 결과가 여전히 그 부분공간 안에 머문다**는 것입니다.

이게 왜 결정적인지는 선형대수로 바로 설명됩니다. $\mathcal{S}$ 가 유한차원이고 불변이면, $\mathcal{K}$ 를 $\mathcal{S}$ 로 제한한 사상 $\mathcal{K}|_{\mathcal{S}} : \mathcal{S} \to \mathcal{S}$ 는 **닫힌 선형 사상**이 됩니다. "닫혀 있다"는 것은 곧 "행렬로 정확히 표현 가능하다"는 뜻입니다. 기저 $\psi$ 에 대해

$$
\mathcal{K}\psi = \psi \circ T = K\psi, \qquad K \in \mathbb{C}^{\dim(\mathcal{S}) \times \dim(\mathcal{S})}
$$

이것이 논문 (4)식이며, 여기에서 유한차원 선형 시스템 (5)식 $\psi(x_{t+1}) = K\psi(x_t)$ 가 **정확히(exactly)** 성립합니다. 근사가 아니라 등식입니다.

---

## 2. 직관 — "닫혀 있다"는 걸 어떻게 검증하는가

가장 확실한 검증법은 **기저원소를 하나씩 전파해보고, 결과가 여전히 부분공간 안에 있는지 확인**하는 것입니다. [[Observable Function]] 노트의 예제로 봅시다.

$$
\dot{x}_1 = \mu x_1, \qquad \dot{x}_2 = \lambda(x_2 - x_1^2)
$$

$\mathcal{S} = \mathrm{span}\{x_1, x_2, x_1^2\}$ 를 잡으면, 각 기저원소를 전파했을 때

- $x_1$ 을 전파 → $\mu x_1$ ∈ $\mathcal{S}$ ✅
- $x_2$ 를 전파 → $\lambda x_2 - \lambda x_1^2$ ∈ $\mathcal{S}$ ✅
- $x_1^2$ 을 전파 → $2\mu x_1^2$ ∈ $\mathcal{S}$ ✅

**셋 다 $\mathcal{S}$ 밖으로 나가지 않습니다 → 불변.** 그래서 이 시스템은 3차원 선형 시스템으로 정확히 표현됩니다.

반면 $\dot{x}_1 = \mu x_1 + x_2^2$ 였다면 어떻게 될까요? $x_1^2$ 을 전파할 때 $x_1x_2^2$ 라는 **$\mathcal{S}$ 에 없는 새 항**이 튀어나옵니다. 그 항을 넣어서 기저를 늘리면 또 다른 새 항이 나오고 — **닫히지 않습니다.** 실무에서는 이런 경우가 압도적으로 많습니다.

---

## 3. 닫히지 않으면 무슨 일이 생기는가 — 사영과 오차 누적

1번의 정의를 뒤집어 보면, **닫혀 있지 않다는 것은 $\mathcal{K}g$ 가 $\mathcal{S}$ 밖으로 나간다**는 뜻입니다. 그런데 우리는 유한차원 행렬 $K$ 로만 계산하고 싶으므로, 밖으로 나간 성분을 억지로 $\mathcal{S}$ 안으로 **사영(projection)** 해야 합니다.

↑ [[EDMD]] 노트 6번에서 이미 이 메커니즘을 봤습니다: $K_{\text{EDMD}}$ 가 인코딩하는 것은 진짜 $\mathcal{K}$ 가 아니라 $\mathcal{P}_{\mathrm{span}(\Psi)}\mathcal{K}$, 즉 **span(Ψ) 평면 위로 내린 그림자**입니다. 1스텝이라면 이 사영 오차가 작을 수 있지만, **multi-step rollout에서는 매 스텝 사영이 반복되면서 오차가 누적**됩니다.

반대로 말하면, **$\mathcal{S}$ 가 불변이면 사영할 것이 아예 없습니다** — 그림자가 원본과 같으므로 오차가 정확히 0입니다. 그래서 "불변인가 아닌가"가 EDMD 예측 정확도를 가르는 유일한 조건이 됩니다.

---

## 4. 그런데 정확한 불변 부분공간은 희귀하다

3번의 논리를 따라가면 자연스러운 결론은 "그럼 불변 부분공간을 찾으면 되지 않나"입니다. 문제는 그게 쉽지 않다는 것입니다.

> [!warning] 정확한 불변 부분공간은 희귀하다
> 논문 V-C절이 명시합니다: *"Exact Koopman-invariant subspaces capturing complete information about the dynamics are rare."*
>
> 그래서 실무 전략은 **"약간의 오차를 허용하는 대신 더 많은(부정확한) 정보를 담는"** 쪽으로 갑니다. 문제는 이제 그 근사 정확도를 **어떻게 특성화하고 튜닝하느냐**입니다. 이 질문에 대한 답이 8번의 T-SSD입니다.

일단 "오차를 허용한다"고 정했다면, 다음 질문은 당연히 "그 오차를 어떻게 재고 최소화할 것인가"입니다. 여기서 가장 그럴듯해 보이는 접근이 사실은 함정입니다 — 다음 단계가 이 노트의 핵심입니다.

---

## 5. 함정 — Residual 최소화로는 부족하다

### 순진한 접근

딕셔너리 $\psi$ 를 NN 등 파라메트릭 함수족으로 두고, EDMD의 예측 오차(residual)를 직접 최소화하려는 시도를 생각해볼 수 있습니다. [[EDMD]] 노트의 (6)식과 (7)식을 결합하면 이런 목적함수가 나옵니다.

$$
\underset{\psi}{\text{minimize}} \quad \big\| \Psi(Y) - \Psi(Y)\Psi(X)^\dagger\,\Psi(X) \big\|_F \tag{논문 (27)}
$$

**여기에는 문제가 두 가지 있습니다.**

1. $\psi$ 가 파라메트릭 족(NN 등)에 속하므로 최적화가 **일반적으로 비볼록(non-convex)** 입니다 → 전역 최적해를 보장할 수 없습니다.
2. **더 심각한 문제**: residual을 작게 만드는 것이 **불변 부분공간에 가까워지는 것을 의미하지 않습니다.**

두 번째 문제는 직관에 어긋나기 때문에 실제 반례로 확인해볼 필요가 있습니다.

### 논문 Fig. 3의 반례 (이 노트의 클라이맥스)

선형 시스템 $x^+ = 0.6x$ 와, 파라미터 $\alpha$ 로 조절되는 딕셔너리 족을 생각해봅시다.

$$
\psi_\alpha(x) = [\,x,\ \ x + \alpha\sin(x)\,], \qquad \alpha \in [0.01, 100]
$$

이 예제를 자세히 뜯어보면 다음을 알 수 있습니다.

> [!important] 핵심 관찰
> - **모든 $\alpha \in \mathbb{R}\setminus\{0\}$ 에 대해 $\mathrm{span}(\psi_\alpha) = \mathrm{span}\{x, \sin(x)\} =: \mathcal{S}$ 로 완전히 동일합니다.** ($\alpha$ 는 같은 부분공간 안에서 기저만 바꿀 뿐입니다)
> - 그런데 **EDMD residual은 $\alpha$ 에 따라 달라집니다** — 심지어 $\alpha$ 를 조절해서 residual을 임의로 0에 가깝게 만들 수 있습니다.
> - 하지만 $\mathcal{S} = \mathrm{span}\{x, \sin(x)\}$ 자체는 **애초에 불변이 아닙니다.**
>
> **결론**: 같은 부분공간인데 residual만 기저 선택에 따라 바뀝니다. 즉 residual이 작다는 것은 좋은 부분공간을 골랐다는 신호가 아니라, **기저 선택의 인공물(artifact)** 일 뿐입니다. 따라서 (27)을 최소화해서 얻은 모델은 **장기 예측(long-term prediction)에 부적합**할 수 있습니다.

이 반례가 보여주는 것은 4번에서 이어진 질문 — "근사 품질을 어떻게 잴 것인가" — 에 residual은 답이 될 수 없다는 것입니다. 그래서 논문은 **basis-independent 지표**인 [[Consistency Index]]를 대안으로 제시합니다.

---

## 6. 대수적 해법 — 불변성을 데이터에서 직접 찾기

Residual 최적화가 신뢰할 수 없다면(5번), 남은 길은 최적화가 아니라 **대수적 탐색(algebraic search)** 입니다. 목표는 "어떤 부분공간이 불변인지"를 데이터로부터 직접, 증명 가능하게 판별하는 것입니다.

### 데이터 관점의 불변성 조건

탐색 공간(search space)을 딕셔너리 $\psi_s$ 가 span 하는 유한차원 함수공간이라고 합시다. $\mathrm{span}(\psi_s)$ 안의 임의의 기저 $\psi$ 는 full column rank 행렬 $C$ 로 표현됩니다.

$$
\psi^\top(\cdot) = \psi_s^\top(\cdot)\,C
$$

$\mathrm{span}(\psi)$ 가 Koopman 불변이라면, 그 사실은 **데이터에 그대로 반영됩니다.**

$$
\boxed{\;\mathcal{R}\big(\psi_s(X)^\top C\big) = \mathcal{R}\big(\psi_s(Y)^\top C\big)\;} \tag{논문 (31)}
$$

여기서 $\mathcal{R}(\cdot)$ 는 **range space (열공간)** 입니다. 직관적으로 읽으면 *"$C$ 로 조합한 관측값들이 만드는 공간이, 한 스텝 전파 후에도 같은 공간이다"* 라는 뜻입니다. 이 조건은 5번의 residual과 달리 **기저 선택 $C$ 에 의존하지 않고 부분공간 자체의 성질**을 잡아냅니다.

### SSD (Symmetric Subspace Decomposition) [31][32]

**목표**: (31)을 만족하는 **열 개수가 최대인 $C$** 를 찾는 것 = 탐색 공간 안에서 **최대 Koopman-불변 부분공간**을 찾는 것입니다.

- Haseli & Cortés [31]: 임의의 유한차원 함수공간에서 **모든 Koopman 고유함수를 식별**하는 데이터 기반 필요조건과, almost surely 충분조건을 제시합니다. 순방향/역방향 EDMD 행렬의 고유분해에 기반합니다.
- [32]: 고차원 공간 탐색을 위한 **병렬(parallel) SSD**입니다.
- 핵심은 이것이 **효율적이고 증명 가능하게 올바른(provably correct)** 대수 알고리즘이라는 점입니다 — 5번의 비볼록 최적화와 대조됩니다.

---

## 7. T-SSD — 정확도와 표현력을 잇는 손잡이

SSD는 "정확한" 불변 부분공간을 찾지만, 4번에서 봤듯 그런 부분공간은 희귀합니다. **T-SSD (Tunable SSD) [33]**는 SSD를 일반화해서, 오차를 허용하되 그 크기를 튜닝할 수 있게 합니다.

(31)의 **등식을 요구하는 대신**, 두 부분공간 $\mathcal{R}(\psi_s(X)^\top C)$ 와 $\mathcal{R}(\psi_s(Y)^\top C)$ 가 **가깝기만 하면** 된다고 완화합니다. 그 근접도를 정확도 파라미터 $\epsilon \in [0,1]$ 로 지정합니다.

> [!success] T-SSD는 EDMD와 SSD를 잇는 스펙트럼이다 (논문 Fig. 5)
>
> | $\epsilon$ | 동등한 알고리즘 | 의미 |
> |:---:|:---|:---|
> | $\epsilon = 0$ | **SSD** | 예측 오차 0 요구 → 최대 **정확한** 불변 부분공간 |
> | $0 < \epsilon < 1$ | **T-SSD** | 정확도와 표현력(부분공간 차원)의 **균형** |
> | $\epsilon = 1$ | **EDMD** | 최대 100% 예측 오차 허용 → 탐색 공간 전체에 EDMD 적용 |
>
> 즉 T-SSD는 **정확도(accuracy) ↔ 표현력(expressiveness)** 트레이드오프를 $\epsilon$ 하나로 조절하는 통합 프레임입니다.

**논문 Fig. 6 실험**: Duffing 시스템

$$
[\dot{x}_1, \dot{x}_2] = [\,x_2,\ -0.5x_2 + x_1(1-x_1^2)\,], \qquad \mathcal{X} = [-2,2]^2
$$

탐색 공간은 차수 10 이하의 모든 다항식입니다. **T-SSD($\epsilon = 0.02$) 로 찾은 딕셔너리가 정규화된 전체 기저보다 상대 예측 오차가 훨씬 작습니다.** 즉 무작정 큰 기저를 쓰는 것보다, 불변성 기준으로 걸러낸 작은 딕셔너리가 이깁니다 — [[EDMD]] 노트 7번의 관찰과 같은 결론입니다.

---

## 8. 실무 체크리스트

1. **딕셔너리 크기를 키우기 전에 불변성을 의심하세요.** 차원 증가가 곧 성능 향상은 아닙니다.
2. **1-step residual만 보고 판단하지 마세요.** 5번의 Fig. 3 반례가 정확히 그 함정입니다. → [[Consistency Index]] 사용을 권장합니다.
3. **시스템 구조를 아는 만큼 딕셔너리에 반영하세요.** 물리 기반 항을 넣는 것이 불변성에 가까워지는 가장 값싼 방법입니다.
4. **탐색 공간이 다항식으로 표현 가능하다면 T-SSD를 고려하세요.** 대수적 보장이 있는 몇 안 되는 경로입니다.
5. **long-horizon rollout으로 검증하세요.** 불변성이 깨진 정도는 3번에서 본 대로 다단계 예측에서 지수적으로 드러납니다.

---

## 📌 전체 흐름 한 눈에

```
①  불변의 정의            Kg ∈ S  →  닫힌 선형사상  →  행렬 K로 정확히 표현 (1번)
        │
②  검증법                 기저원소 하나씩 전파해서 S 안에 머무는지 확인 (2번)
        │
③  닫히지 않으면          K g 가 S 밖으로 → 사영 필요 → EDMD 오차, multi-step 누적 (3번)
        │
④  그런데                 정확한 불변 부분공간은 희귀 → "오차 허용 + 튜닝" 전략 (4번)
        │
⑤  함정                   residual 최소화 ≠ 불변에 가까워짐 (Fig.3 반례) (5번)
        │
⑥  대수적 해법            데이터 기반 불변성 조건 (31식) → SSD: 최대 불변 부분공간 (6번)
        │
⑦  일반화                 T-SSD: ε 로 정확도↔표현력 조절, SSD─EDMD 스펙트럼 (7번)
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| 불변성이 깨졌을 때 실제로 어떤 오차가 나는가 | [[EDMD]] 6번 — 사영 연산자의 기하학적 의미 |
| 딕셔너리를 무작정 키우면 안 되는 이유 | [[EDMD]] 7번 — 딕셔너리 선택의 미묘함 |
| residual 대신 쓸 basis-independent 지표 | [[Consistency Index]] |
| 딕셔너리를 어떻게 설계/학습하는가 | [[Observable Function]] |
| 1차원 불변 부분공간(가장 단순한 사례) | [[Koopman Eigenfunction]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operator]] — 불변 부분공간이 필요한 이유 (상위 개념)
> - [[Observable Function]] — 딕셔너리 설계 실무
> - [[EDMD]] — 불변성이 깨졌을 때 무슨 일이 생기는가
> - [[Consistency Index]] — basis-independent 품질 지표
> - [[Koopman Eigenfunction]] — 1차원 불변 부분공간
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
