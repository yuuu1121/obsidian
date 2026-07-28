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

> [!abstract] 한 줄 요약
> [[EDMD]] residual은 **기저 선택에 따라 요동치는 가짜 지표**다. Consistency index는 **부분공간 자체에만 의존하는(basis-independent)** 품질 척도로, 순방향·역방향 EDMD 행렬이 서로 역행렬인지를 측정한다. 장기 예측 성능을 원한다면 residual이 아니라 이것을 최소화해야 한다.

---

## 1. 왜 EDMD residual로는 부족한가

### 논문 Fig. 3의 반례 (다시 강조)

선형 시스템 $x^+ = 0.6x$, 딕셔너리 족

$$
\psi_\alpha(x) = \big[\,x,\ \ x + \alpha\sin(x)\,\big], \qquad \alpha\in[0.01, 100]
$$

> [!warning] 무엇이 문제인가
> - **모든 $\alpha \ne 0$ 에 대해 $\mathrm{span}(\psi_\alpha) = \mathrm{span}\{x, \sin(x)\} =: \mathcal{S}$ — 부분공간은 완전히 동일하다.** $\alpha$ 는 기저(basis)만 바꾼다.
> - 그런데 **EDMD residual은 $\alpha$ 에 따라 크게 달라지고, 임의로 0에 가깝게 만들 수 있다.**
> - 하지만 $\mathcal{S}$ 는 **Koopman 불변이 아니다.**
>
> **결론**: residual을 최소화하는 최적화 (논문 (27))는 **부분공간의 품질이 아니라 기저 선택의 우연**을 좇을 수 있다. 그렇게 얻은 모델은 **장기 예측에서 무너진다.**

---

## 2. 정의

순방향·역방향 EDMD 행렬을 각각 계산한다.

$$
K_F = \Psi(Y)\,\Psi(X)^{\dagger} \qquad(\text{시간 순방향})
$$
$$
K_B = \Psi(X)\,\Psi(Y)^{\dagger} \qquad(\text{시간 역방향}) \tag{논문 (29)}
$$

**Consistency index**는 다음으로 정의된다.

$$
\boxed{\;I_C(\psi, X, Y) := \lambda_{\max}\big(I - K_F K_B\big)\;} \tag{논문 (28)}
$$

$\lambda_{\max}(\cdot)$ 는 최대 고유값.

### 직관

> [!success] 아이디어가 아름다운 이유
> 부분공간이 **Koopman 불변**이면, 시간을 앞으로 밀었다가 뒤로 밀면 **정확히 제자리로 돌아와야 한다**. 즉
> $$K_F K_B = I \quad\Longrightarrow\quad I_C = 0$$
> 불변이 아니면 순방향·역방향 행렬이 서로 역행렬이 되지 못하고, **그 어긋난 정도가 곧 $I_C$** 다. $I_C$ 가 클수록 불변성에서 멀다.
>
> 왜 이게 기저에 무관한가: $\psi \to C^\top\psi$ 로 기저를 바꾸면 $K_F \to C^{-1}K_F C$, $K_B \to C^{-1}K_B C$ 이므로 $K_FK_B \to C^{-1}(K_FK_B)C$ — **닮음 변환(similarity)** 이다. 고유값은 닮음 변환에 불변이므로 $I_C$ 도 불변이다.

---

## 3. 네 가지 핵심 성질 (논문 V-C절)

1. **범위**: $I_C \in [0,1]$
2. **기저 독립성**: (27)의 비용함수와 달리, $I_C$ 는 **$\mathrm{span}(\psi)$ 에만 의존**하고 특정 기저에는 의존하지 않는다. (Fig. 3이 이것을 시각적으로 보여준다 — residual은 $\alpha$ 에 따라 요동치지만 $\sqrt{I_C}$ 는 평평하다.)
3. **계산 가능성**: 적절한 기저 변환 하에서 $I_C$ 는 **양반정부호 행렬의 최대 고유값**으로 볼 수 있어 표준 최적화 솔버를 쓸 수 있다. ($I - K_FK_B$ 자체는 일반적으로 대칭이 아니다.)
4. **⭐ 부분공간 전체에 대한 tight upper bound**: 이것이 진짜 결정적이다.

$$
I_C(\psi, X, Y) = \max_{\substack{f\in\mathrm{span}(\psi) \\ \|\mathcal{K}f\|_{L^2(\mu_\mathcal{X})}\ne 0}}
\frac{\big\|\mathcal{K}f - \mathcal{P}_{\mathcal{K}f}\big\|_{L^2(\mu_\mathcal{X})}}{\big\|\mathcal{K}f\big\|_{L^2(\mu_\mathcal{X})}}
$$

여기서 $\mathcal{P}_{\mathcal{K}f}$ 는 (8)식의 EDMD 예측자, $L^2$ 노름은 경험적 측도 (11) 기준.

> [!important] 이 식이 말하는 것
> $I_C$ 는 **부분공간 안의 모든 함수에 대한 상대 예측 오차의 최댓값**이다. 즉 $I_C = 0.02$ 라면 *"$\mathrm{span}(\psi)$ 안의 어떤 함수를 예측하더라도 상대 오차가 2%를 넘지 않는다"* 는 **보장**이 된다. residual은 이런 보장을 전혀 주지 못한다.

---

## 4. Robust minimax 해석

Consistency index를 최소화하는 것은 다음 **robust minimax 문제**와 동등하다.

$$
\min_{\psi\in\mathcal{P}_\mathcal{F}}\ \ \max_{\substack{f\in\mathrm{span}(\psi)\\ \|\mathcal{K}f\|\ne0}}\ \
\frac{\|\mathcal{K}f - \mathcal{P}_{\mathcal{K}f}\|_{L^2(\mu_\mathcal{X})}}{\|\mathcal{K}f\|_{L^2(\mu_\mathcal{X})}} \tag{논문 (30)}
$$

($\max$ 부분에 닫힌 형태 표현이 있으므로 실제로 풀 수 있다.)

> [!note] residual 최소화와의 결정적 차이
>
> | | EDMD residual (27) | Consistency index (30) |
> |:---|:---|:---|
> | 고려하는 함수 | **유한 개** (딕셔너리 원소들) | **비가산 무한 개** (부분공간 전체) |
> | 기저 의존성 | **있음** (artifact) | **없음** |
> | 보장 | 없음 | 상대 예측 오차의 tight bound |
> | 장기 예측 | 취약 | **우수** |

---

## 5. 실험적 증거 — 논문 Fig. 4의 진자 예제

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

**논문의 설명**: consistency index는 함수공간의 **(비가산적으로) 모든 원소**를 고려하는 반면, EDMD residual은 **유한 개 함수만** 고려하기 때문이다.

---

## 6. 대수적 대안 — SSD와 T-SSD

최적화 기반 방법은 비볼록성 때문에 전역 최적해를 못 찾을 수 있다. 그래서 **대수적 탐색**이 대안이 된다. 자세한 내용은 [[Koopman-Invariant Subspace]] §4 참고.

**요약**:

| 알고리즘 | 하는 일 | 위치 |
|:---|:---|:---|
| **SSD** [31][32] | 탐색 공간 내 **최대 정확 불변 부분공간**을 찾는 대수 알고리즘. 순/역 EDMD 고유분해 기반. 증명 가능하게 올바름. | $\epsilon = 0$ |
| **T-SSD** [33] | 정확도 파라미터 $\epsilon\in[0,1]$ 로 **정확도 ↔ 표현력** 균형을 조절 | $0\le\epsilon\le1$ |
| **EDMD** | 오차 100% 허용 = 탐색 공간 전체에 그냥 EDMD | $\epsilon = 1$ |

$$
\underbrace{\text{SSD}}_{\epsilon=0} \quad\longleftrightarrow\quad \underbrace{\text{T-SSD}}_{0<\epsilon<1} \quad\longleftrightarrow\quad \underbrace{\text{EDMD}}_{\epsilon=1}
$$

**Fig. 6 실험 (Duffing 시스템)**: $[\dot x_1, \dot x_2] = [x_2, -0.5x_2 + x_1(1-x_1^2)]$, $\mathcal{X}=[-2,2]^2$, 탐색 공간 = 차수 10 이하 다항식. **T-SSD($\epsilon=0.02$) 가 정규화된 전체 기저보다 상대 예측 오차가 훨씬 작다.**

---

## 7. 실무적 한계

> [!warning] 언제 쓸 수 없는가
> 논문이 명시한다: 최적화 기반 딕셔너리 선택은 우수한 예측 정확도를 주지만
> - **큰 데이터셋 접근이 필요**하고
> - **일반적으로 오프라인 사전계산에만 적용 가능**하다
>
> 즉 논문 서론이 강조한 "runtime learning / small data" 시나리오와는 긴장 관계에 있다. **오프라인에서 좋은 딕셔너리를 확정하고, 온라인에서는 그 위에서 $K$ 만 빠르게 갱신**하는 2단 구조가 현실적 타협점이다.

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman-Invariant Subspace]] — SSD/T-SSD 상세
> - [[EDMD]] — residual의 정의와 한계
> - [[Observable Function]] — 딕셔너리 설계 실무
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
