---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Theory
aliases:
  - 일관성 지표
  - Forward-backward consistency
  - SSD
  - T-SSD
keywords: consistency index, forward-backward, SSD, T-SSD, subspace quality
related notes: "[[Koopman-Invariant Subspace]], [[EDMD]], [[Observable Function]]"
dg-publish: false
---

# Consistency Index (시간 순방향-역방향 일관성 지표)

> [!abstract] 한 문장 요약
> [[EDMD]] residual은 **기저 선택에 따라 요동치는 가짜 지표**이며, 이를 대신할 **기저에 무관한(basis-independent)** 척도가 바로 **순방향·역방향 EDMD 행렬이 서로 역행렬인지를 재는 consistency index**입니다.

아래 1→8번을 순서대로 읽으면 왜 residual을 버리고 이 지표를 써야 하는지가 쌓입니다.

---

## 1. 문제 제기 — EDMD residual로는 왜 부족한가

[[EDMD]]에서 딕셔너리를 고를 때 흔히 쓰는 기준은 최소자승 residual, 즉 (27)식의 비용함수를 얼마나 낮췄는가입니다. 그런데 논문 Fig. 3은 이 기준이 **속아 넘어가기 쉽다**는 것을 보여줍니다.

선형 시스템 $x^+ = 0.6x$ 와, 딕셔너리 족

$$
\psi_\alpha(x) = \big[\,x,\ \ x + \alpha\sin(x)\,\big], \qquad \alpha\in[0.01, 100]
$$

를 생각해 봅시다.

> [!warning] 무엇이 문제인가
> - **모든 $\alpha \ne 0$ 에 대해 $\mathrm{span}(\psi_\alpha) = \mathrm{span}\{x, \sin(x)\} =: \mathcal{S}$ — 부분공간은 완전히 동일합니다.** $\alpha$ 는 그 안의 기저(basis)만 바꿀 뿐입니다.
> - 그런데 **EDMD residual은 $\alpha$ 에 따라 크게 요동치고, 심지어 임의로 0에 가깝게 만들 수도 있습니다.**
> - 하지만 $\mathcal{S}$ 자체는 **Koopman 불변이 아닙니다.**

즉 같은 부분공간을 놓고도 residual은 기저를 어떻게 잡느냐에 따라 좋아 보였다 나빠 보였다 합니다. **결론**: residual을 최소화하는 최적화 (논문 (27))는 **부분공간의 진짜 품질이 아니라 기저 선택의 우연**을 좇을 수 있습니다. 그렇게 얻은 모델은 **장기 예측에서 무너집니다.**

여기서 자연스러운 질문이 나옵니다. **residual이 기저에 따라 흔들린다면, 애초에 기저에 무관한 지표를 만들면 되지 않을까?** 이것이 이 노트가 소개하는 consistency index의 출발점입니다. 이 반례가 어떻게 풀리는지는 ↓ 3번의 "기저 독립성"에서 다시 확인합니다.

---

## 2. 정의 — $K_F$, $K_B$, 그리고 $I_C$

기저 독립적인 지표를 만들기 위해, 먼저 순방향·역방향 EDMD 행렬을 각각 계산합니다.

$$
K_F = \Psi(Y)\,\Psi(X)^{\dagger} \qquad(\text{시간 순방향})
$$
$$
K_B = \Psi(X)\,\Psi(Y)^{\dagger} \qquad(\text{시간 역방향}) \tag{논문 (29)}
$$

$K_F$ 는 "현재 → 다음"을 예측하는 익숙한 EDMD 행렬이고, $K_B$ 는 그 반대로 "다음 → 현재"를 예측하도록 $X$ 와 $Y$ 의 역할을 뒤바꿔 만든 행렬입니다.

이 둘을 이용해 **consistency index**를 정의합니다.

$$
\boxed{\;I_C(\psi, X, Y) := \lambda_{\max}\big(I - K_F K_B\big)\;} \tag{논문 (28)}
$$

여기서 $\lambda_{\max}(\cdot)$ 는 최대 고유값입니다.

---

## 3. 직관 — 왜 이 식이 말이 되는가

> [!success] 아이디어가 아름다운 이유
> 부분공간이 **Koopman 불변**이면, 시간을 앞으로 밀었다가 뒤로 밀면 **정확히 제자리로 돌아와야 합니다.** 쉽게 말해 "앞으로 한 스텝 갔다가 다시 뒤로 한 스텝 오면 원래 있던 곳"이라는 당연한 요구입니다. 이것이 수식으로는
> $$K_F K_B = I \quad\Longrightarrow\quad I_C = 0$$
> 로 표현됩니다. 불변이 아니면 순방향·역방향 행렬이 서로 역행렬이 되지 못하고, **그 어긋난 정도가 곧 $I_C$** 입니다. $I_C$ 가 클수록 불변성에서 멀리 떨어져 있다고 이해하면 됩니다.

이제 ↑ 1번의 반례로 돌아가 봅시다. 왜 $I_C$ 는 residual과 달리 $\alpha$ 에 흔들리지 않을까요? 기저를 $\psi \to C^\top\psi$ 로 바꾸면 $K_F \to C^{-1}K_F C$, $K_B \to C^{-1}K_B C$ 가 되므로

$$
K_FK_B \to C^{-1}(K_FK_B)C
$$

즉 **닮음 변환(similarity transform)** 이 걸릴 뿐입니다. 고유값은 닮음 변환에 불변이므로, $I_C = \lambda_{\max}(I-K_FK_B)$ 역시 기저를 아무리 바꿔도 값이 변하지 않습니다. **1번에서 residual이 흔들렸던 이유는 정확히 이 닮음 변환 불변성이 residual에는 없기 때문**이었고, $I_C$ 는 애초에 그 불변성을 갖도록 설계된 지표입니다.

---

## 4. 네 가지 핵심 성질 (논문 V-C절)

3번의 직관을 논문은 네 가지 성질로 정리합니다.

1. **범위**: $I_C \in [0,1]$
2. **기저 독립성**: (27)의 비용함수와 달리, $I_C$ 는 **$\mathrm{span}(\psi)$ 에만 의존**하고 특정 기저에는 의존하지 않습니다. (Fig. 3이 이것을 시각적으로 보여줍니다 — residual은 $\alpha$ 에 따라 요동치지만 $\sqrt{I_C}$ 는 평평합니다.)
3. **계산 가능성**: 적절한 기저 변환 하에서 $I_C$ 는 **양반정부호 행렬의 최대 고유값**으로 볼 수 있어 표준 최적화 솔버를 쓸 수 있습니다. ($I - K_FK_B$ 자체는 일반적으로 대칭이 아닙니다.)
4. **⭐ 부분공간 전체에 대한 tight upper bound**: 이것이 진짜 결정적입니다.

$$
I_C(\psi, X, Y) = \max_{\substack{f\in\mathrm{span}(\psi) \\ \|\mathcal{K}f\|_{L^2(\mu_\mathcal{X})}\ne 0}}
\frac{\big\|\mathcal{K}f - \mathcal{P}_{\mathcal{K}f}\big\|_{L^2(\mu_\mathcal{X})}}{\big\|\mathcal{K}f\big\|_{L^2(\mu_\mathcal{X})}}
$$

여기서 $\mathcal{P}_{\mathcal{K}f}$ 는 (8)식의 EDMD 예측자, $L^2$ 노름은 경험적 측도 (11) 기준입니다.

> [!important] 이 식이 말하는 것
> $I_C$ 는 **부분공간 안의 모든 함수에 대한 상대 예측 오차의 최댓값**입니다. 즉 $I_C = 0.02$ 라면 *"$\mathrm{span}(\psi)$ 안의 어떤 함수를 예측하더라도 상대 오차가 2%를 넘지 않는다"* 는 **보장**이 됩니다. 이 4번째 성질이 결정적인 이유는, residual은 **딕셔너리 원소 몇 개에 대한 오차**만 알려줄 뿐 부분공간 전체에 대해서는 아무 보장도 주지 못하기 때문입니다. $I_C$ 는 그 공백을 정확히 메웁니다.

<details>
<summary><b>왜 "부분공간 전체"가 중요한가 — residual이 놓치는 것</b></summary>

딕셔너리 $\psi$ 가 유한 개의 함수 $\psi_1, \ldots, \psi_N$ 로 구성되어 있어도, $\mathrm{span}(\psi)$ 자체는 그 선형결합으로 만들 수 있는 **비가산 무한 개의 함수**를 담고 있습니다. residual은 딕셔너리 원소들 자체에 대한 예측 오차만 보므로, 그 선형결합 중 특정 방향으로 오차가 크게 튀는 함수가 있어도 residual만 봐서는 알 수 없습니다. $I_C$ 는 이 최악의 방향까지 포함한 최댓값이므로, 부분공간 전체에 대해 안전한 보장을 제공합니다.
</details>

---

## 5. Robust minimax 해석

4번째 성질(tight upper bound)을 최적화 문제로 다시 쓰면, consistency index를 최소화하는 것은 다음 **robust minimax 문제**와 동등합니다.

$$
\min_{\psi\in\mathcal{P}_\mathcal{F}}\ \ \max_{\substack{f\in\mathrm{span}(\psi)\\ \|\mathcal{K}f\|\ne0}}\ \
\frac{\|\mathcal{K}f - \mathcal{P}_{\mathcal{K}f}\|_{L^2(\mu_\mathcal{X})}}{\|\mathcal{K}f\|_{L^2(\mu_\mathcal{X})}} \tag{논문 (30)}
$$

($\max$ 부분에 닫힌 형태 표현이 있으므로 실제로 풀 수 있습니다.)

1번의 반례와 대조해 보면, residual 최소화와 consistency index 최소화의 차이가 분명해집니다.

> [!note] residual 최소화와의 결정적 차이
>
> | | EDMD residual (27) | Consistency index (30) |
> |:---|:---|:---|
> | 고려하는 함수 | **유한 개** (딕셔너리 원소들) | **비가산 무한 개** (부분공간 전체) |
> | 기저 의존성 | **있음** (artifact) | **없음** |
> | 보장 | 없음 | 상대 예측 오차의 tight bound |
> | 장기 예측 | 취약 | **우수** |

---

## 6. 실험적 증거 — 논문 Fig. 4의 진자 예제

이론이 실제로 성립하는지, 논문은 감쇠 진자로 검증합니다.

**시스템**: 감쇠 진자
$$
[\dot{\theta}, \ddot{\theta}] = \big[\,\dot\theta,\ -9.81\sin(\theta) - 0.1\dot\theta\,\big]
$$

**딕셔너리**: 5개 함수의 파라메트릭 족
$$
\psi(\theta,\dot\theta) = \big[\,\theta,\ \dot\theta,\ \mathrm{NN}_1,\ \mathrm{NN}_2,\ \mathrm{NN}_3\,\big]
$$
(각 NN은 feedforward 신경망)

**결과**: 진자 각도 진화 예측에서

- **Consistency index 최소화**로 학습한 부분공간 → **장기 예측 우수** ✅
- **EDMD residual 최소화** (27)로 학습한 부분공간 → 장기 예측 열화 ❌

**논문의 설명**: consistency index는 함수공간의 **(비가산적으로) 모든 원소**를 고려하는 반면, EDMD residual은 **유한 개 함수만** 고려하기 때문입니다. 5번의 표에서 정리한 차이가 실측으로도 그대로 재현되는 셈입니다.

---

## 7. 대수적 대안 — SSD와 T-SSD

지금까지는 $I_C$ 를 최적화로 최소화하는 접근이었지만, 이런 최적화 기반 방법은 비볼록성 때문에 전역 최적해를 못 찾을 수 있습니다. 그래서 **대수적 탐색**이 대안이 됩니다. 자세한 내용은 [[Koopman-Invariant Subspace]] §4 참고.

**요약**:

| 알고리즘 | 하는 일 | 위치 |
|:---|:---|:---|
| **SSD** [31][32] | 탐색 공간 내 **최대 정확 불변 부분공간**을 찾는 대수 알고리즘. 순/역 EDMD 고유분해 기반. 증명 가능하게 올바름. | $\epsilon = 0$ |
| **T-SSD** [33] | 정확도 파라미터 $\epsilon\in[0,1]$ 로 **정확도 ↔ 표현력** 균형을 조절 | $0\le\epsilon\le1$ |
| **EDMD** | 오차 100% 허용 = 탐색 공간 전체에 그냥 EDMD | $\epsilon = 1$ |

$$
\underbrace{\text{SSD}}_{\epsilon=0} \quad\longleftrightarrow\quad \underbrace{\text{T-SSD}}_{0<\epsilon<1} \quad\longleftrightarrow\quad \underbrace{\text{EDMD}}_{\epsilon=1}
$$

**Fig. 6 실험 (Duffing 시스템)**: $[\dot x_1, \dot x_2] = [x_2, -0.5x_2 + x_1(1-x_1^2)]$, $\mathcal{X}=[-2,2]^2$, 탐색 공간 = 차수 10 이하 다항식. **T-SSD($\epsilon=0.02$) 가 정규화된 전체 기저보다 상대 예측 오차가 훨씬 작습니다.**

---

## 8. 실무적 한계

6번과 7번에서 본 것처럼 consistency index 기반 방법은 이론적으로도 실험적으로도 residual보다 우월합니다. 하지만 공짜는 아닙니다.

> [!warning] 언제 쓸 수 없는가
> 논문이 명시합니다: 최적화 기반 딕셔너리 선택은 우수한 예측 정확도를 주지만
> - **큰 데이터셋 접근이 필요**하고
> - **일반적으로 오프라인 사전계산에만 적용 가능**합니다
>
> 즉 논문 서론이 강조한 "runtime learning / small data" 시나리오와는 긴장 관계에 있습니다. **오프라인에서 좋은 딕셔너리를 확정하고, 온라인에서는 그 위에서 $K$ 만 빠르게 갱신**하는 2단 구조가 현실적 타협점입니다.

---

## 📌 전체 흐름 한 눈에

```
①  문제 제기         EDMD residual은 기저 α에 따라 요동침 (Fig.3 반례) ── span(ψ)는 동일한데도
        │
②  정의             K_F = Ψ(Y)Ψ(X)†,  K_B = Ψ(X)Ψ(Y)†  (29)
        │
③  지표             I_C = λ_max(I − K_F K_B)   (28)
        │
④  직관             앞으로 밀었다 뒤로 밀면 제자리 → 닮음변환 → 고유값 불변 → 기저 무관
        │
⑤  네 성질          범위[0,1] · 기저독립 · 계산가능 · ⭐ 부분공간 전체 tight upper bound
        │
⑥  robust minimax   (30)  ── 유한 개(residual) vs 비가산 무한 개(I_C) 비교
        │
⑦  실험 검증        Fig.4 진자: I_C 최소화 → 장기예측 우수, residual 최소화 → 열화
        │
⑧  대수적 대안       SSD(ε=0) ↔ T-SSD(0<ε<1) ↔ EDMD(ε=1)
        │
⑨  한계             큰 데이터셋 필요 + 오프라인 전용 → runtime learning과 긴장
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| SSD/T-SSD의 대수적 세부 알고리즘 | [[Koopman-Invariant Subspace]] §4 |
| residual의 정의 (27)과 EDMD 자체의 구조 | [[EDMD]] |
| 딕셔너리 설계 실무 (딕셔너리를 애초에 어떻게 고르는가) | [[Observable Function]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman-Invariant Subspace]] — SSD/T-SSD 상세
> - [[EDMD]] — residual의 정의와 한계
> - [[Observable Function]] — 딕셔너리 설계 실무
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
