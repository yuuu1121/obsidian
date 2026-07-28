---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Algorithm
aliases:
  - Hankel View of Koopman
  - Time-delay embedding
  - 시간지연 임베딩
  - Hankel DMD
keywords: HVOK, Hankel matrix, time-delay embedding, Takens theorem, delay coordinates
related notes: "[[Koopman Operator]], [[EDMD]], [[Observable Function]]"
dg-publish: false
---

# HVOK (Hankel View of Koopman) — 시간지연 임베딩

> [!abstract] 한 문장 요약
> HVOK는 **"리프팅 함수를 설계하는 대신, 과거 $d$ 스텝의 측정값을 쌓아서 고차원 특징 공간을 만드는 것"** 이며, 이것이 정당화되는 근거는 **Takens 임베딩 정리**입니다.

아래 1→7번을 순서대로 읽으면 HVOK가 왜 그렇게 생겼는지가 쌓입니다.

---

## 1. 문제의식 — 딕셔너리 설계를 시간축으로 우회하기

[[EDMD]]에서 봤듯, EDMD는 **명시적으로 고른 리프팅 맵** $\psi$ 에 의존합니다. 그런데 [[Observable Function]] 노트와 EDMD 7번에서 확인했듯, 딕셔너리 설계는 노동집약적이고 일반화가 어려운 난제입니다. 심지어 딕셔너리를 키운다고 항상 좋아지는 것도 아니고, 시스템 모델 없이는 필요한 차원의 하한조차 추정할 수 없습니다.

**HVOK의 발상은 이렇습니다.** 상태공간에서 함수를 설계하는 대신, **시간축에서 데이터를 쌓자**는 것입니다. 즉 "어떤 비선형 함수를 관측할까"를 고민하는 대신, "과거 몇 스텝을 기억할까"라는 훨씬 다루기 쉬운 질문으로 문제를 바꿔치기합니다.

| | EDMD | HVOK |
|:---|:---|:---|
| 특징 생성 | 명시적 딕셔너리 $\psi(x)$ | **암묵적** — 시간지연 스택 |
| 데이터 사용 | 단일 스텝 쌍 $(x_i, y_i)$ | **시간지연된 스냅샷** |
| 설계 부담 | 딕셔너리 선택이 핵심 난제 | 지연 차수 $d$ 하나 |
| 이론적 근거 | 사영 근사 | **Takens 임베딩 정리** |

이 표의 마지막 줄에 주목하세요. EDMD는 "왜 이 딕셔너리가 잘 작동하는가"에 답하기 어렵지만, HVOK는 **시간지연 좌표가 왜 원래 상태공간을 대신할 수 있는지**에 대해 수학적으로 정립된 답을 가지고 있습니다. 그 답이 4번에서 등장하는 Takens 정리입니다.

---

## 2. Hankel 행렬 구성

먼저 측정 시퀀스 $x_1, x_2, \dots, x_m$ 이 주어졌다고 합시다. 지연 차수 $d$ 를 정해서 **Hankel 행렬**을 만듭니다.

$$
H_X =
\begin{bmatrix}
x_1 & x_2 & \cdots & x_{m-d} \\
x_2 & x_3 & \cdots & x_{m-d+1} \\
\vdots & \vdots & \ddots & \vdots \\
x_d & x_{d+1} & \cdots & x_{m-1}
\end{bmatrix},
\qquad
H_Y =
\begin{bmatrix}
x_2 & x_3 & \cdots & x_{m-d+1} \\
x_3 & x_4 & \cdots & x_{m-d+2} \\
\vdots & \vdots & \ddots & \vdots \\
x_{d+1} & x_{d+2} & \cdots & x_m
\end{bmatrix}
$$

> [!note] 행렬 구조 읽는 법
> - **각 열** = 연속된 $d$ 개 시점의 측정값을 세로로 쌓은 것입니다. 이것이 바로 **리프팅된 상태** $z_k = [x_k; x_{k+1}; \dots; x_{k+d-1}]$ 라고 이해하면 됩니다.
> - **반대각선(anti-diagonal)이 상수**라는 점이 Hankel 행렬의 정의입니다.
> - $H_Y$ 는 $H_X$ 를 **시간축으로 정확히 한 칸 민 것**입니다. EDMD의 $Y$가 $X$의 "한 스텝 뒤"였던 것과 같은 관계입니다.
> - 차원은 $H_X \in \mathbb{R}^{dN_x \times (m-d)}$ 입니다. 지연 $d$ 를 늘리면 리프팅 차원이 $dN_x$ 로 커집니다 — EDMD에서 딕셔너리 차원 $N_\Psi$ 를 늘리는 것과 같은 역할을 지연 차수 $d$ 가 대신합니다.

$H_X$의 각 열이 이미 "리프팅된 상태"라는 점 때문에, 이제 EDMD와 똑같은 절차를 그대로 적용할 수 있습니다. 3번에서 이어집니다.

---

## 3. 연산자 추정 — EDMD와 완전히 동일한 최소자승

$H_X$, $H_Y$ 를 EDMD의 $\Psi(X)$, $\Psi(Y)$ 자리에 그대로 대입하면 됩니다.

$$
H_Y \approx K_{\mathrm{HVOK}}\,H_X
\qquad\Longrightarrow\qquad
\boxed{\;K_{\mathrm{HVOK}} = H_Y\,H_X^{\dagger}\;}
$$

즉 **알고리즘 자체는 EDMD와 완전히 동일하고, 리프팅을 "딕셔너리"가 아니라 "시간지연"으로 대체**한 것뿐입니다. 딕셔너리 설계, 최소자승 정식화, 의사역행렬을 이용한 닫힌 형태 해 — 이 모든 절차가 EDMD와 한 글자도 다르지 않습니다. 바뀐 것은 리프팅 함수의 **정체**뿐입니다.

이 관점에서 HVOK는 "딕셔너리 $\psi(x_k) = [x_k; x_{k+1}; \dots; x_{k+d-1}]$ 를 쓰는 EDMD"라고 볼 수도 있습니다. 그런데 여기서 자연스러운 의문이 생깁니다 — 왜 하필 "과거 값을 그대로 쌓는" 이 특정한 리프팅이 좋은 선택일까요? EDMD였다면 이 리프팅이 Koopman-불변에 가까운지 보장할 방법이 없었을 것입니다. HVOK가 특별한 이유는 4번에서 나옵니다.

---

## 4. 왜 작동하는가 — Takens 임베딩 정리

논문은 이를 *"Takens-type observability arguments"* 로 표현합니다.

> [!important] Takens 정리 (직관적 서술)
> 매끄러운 동역학계의 끌개(attractor) 차원이 $D$ 일 때, **단 하나의 스칼라 측정값**이라도 충분히 많은 시간지연 좌표 $[y_t, y_{t-\tau}, \dots, y_{t-(d-1)\tau}]$ 를 쌓으면 ($d > 2D$), 그 지연 좌표계는 원래 끌개와 **위상적으로 동등(diffeomorphic)** 한 임베딩을 만듭니다.

즉 1번에서 "왜 시간축으로 우회해도 되는가"라는 질문에 대한 답이 여기 있습니다. 시간지연 좌표만 충분히 쌓으면, 원래 상태 전체를 관측하지 못했더라도 그 상태공간의 기하학적 구조를 그대로 복원할 수 있다는 것이 Takens 정리가 보장하는 내용입니다.

이 정리로부터 **로보틱스적 의미** 세 가지가 따라옵니다.

1. **부분 관측(partial observability) 문제를 자동으로 완화합니다.** 소프트 로봇에서 전체 변형 상태를 측정할 수 없더라도, 끝단 위치의 시계열만으로 숨은 동역학을 복원할 수 있습니다.
2. **시간지연 좌표는 미분 정보를 암묵적으로 포함합니다.** $x_{k+1} - x_k \approx \dot{x}\Delta t$ 이므로 속도·가속도 정보가 자연히 들어옵니다.
3. **느린 응답·이력현상(hysteresis)을 포착합니다.** 소프트 로봇의 점탄성처럼 현재 상태만으로 결정되지 않는 거동을, 과거 이력이 대신 설명해 줍니다.

이 세 가지 성질 덕분에 HVOK가 특히 강력해지는 플랫폼들이 있습니다. 5번에서 살펴봅니다.

---

## 5. 어느 플랫폼에서 쓰나

논문 Table I 및 III-B 논의를 기준으로 정리하면 다음과 같습니다.

| 플랫폼 | HVOK가 유리한 이유 |
|:---|:---|
| **Soft / Continuum robot** | 느린 응답 특성(slow response), 점탄성, 무한 자유도 → 딕셔너리 설계가 사실상 불가능합니다. 시간 구조가 정보를 대신 담아줍니다. [72][74] |
| **Aerial robot** | 강한 환경 외란(gust, ground effect) → 외란의 시간적 상관을 지연 좌표가 포착합니다 |
| **Bio-inspired robot** | 주기적·리듬 동역학 → 시간 구조가 풍부합니다 |

논문 원문 표현은 다음과 같습니다: *"particularly favored due to its ability to capture strong environmental disturbances (as seen in aerial systems) or slow response characteristics (as in soft robotics)"*.

세 플랫폼 모두 공통적으로 **"딕셔너리를 손으로 설계하기 어렵거나, 시간 구조 자체가 물리적으로 의미 있는 정보를 담고 있는" 시스템**이라는 점에 주목하세요. 정확히 4번의 세 가지 의미가 실제로 힘을 발휘하는 상황입니다.

---

## 6. 장단점

> [!success] 장점
> - **딕셔너리 설계 불필요** — 튜닝할 것은 지연 차수 $d$ 하나뿐입니다
> - **부분 관측 시스템에 강함** — 측정 못 하는 상태를 시간이 대신합니다
> - **부분 관측·강한 비선형 상황에서 더 안정적인 Koopman 추정** (논문 표현: *"often yielding more stable Koopman estimates"*)
> - EDMD와 동일한 닫힌 형태 해 → 여전히 빠릅니다

> [!warning] 단점 / 주의
> - **$d$ 선택이 여전히 하이퍼파라미터입니다.** 너무 작으면 임베딩이 부족하고, 너무 크면 차원 폭발 + 데이터 부족이 발생합니다
> - **차원이 $dN_x$ 로 선형 증가합니다.** 다자유도 로봇에서는 금방 커지므로, SVD 절단으로 축소하는 것이 관례입니다
> - **샘플링 레이트에 민감합니다.** 논문 VI절이 별도 open problem으로 지적합니다 ([166]): 샘플링이 부족하면 외란 추정·제어 정확도가 저하됩니다
> - **Hankel 행렬은 구조적으로 ill-conditioned 되기 쉽습니다** — 열들이 강하게 상관되어 있기 때문입니다. 정규화/절단이 필수입니다
> - **비정상(non-stationary) 시스템에서는 지연 좌표의 의미가 흔들립니다**

---

## 7. 구현

```python
def hankel(x_seq, d):
    """x_seq: (N_x, m) 시계열 → (d*N_x, m-d+1) Hankel"""
    return np.vstack([x_seq[:, i:i + x_seq.shape[1]-d+1] for i in range(d)])

H = hankel(x_seq, d)                 # (d*N_x, m-d+1)
HX, HY = H[:, :-1], H[:, 1:]         # 한 칸 밀기

# SVD 절단으로 조건수 개선 (권장)
U, S, Vt = np.linalg.svd(HX, full_matrices=False)
r = np.sum(S > tol * S[0])           # rank truncation
K = HY @ Vt[:r].T @ np.diag(1/S[:r]) @ U[:, :r].T

# 예측: 리프팅 상태 = 과거 d 스텝 스택
z = np.concatenate([x[t-d+1], ..., x[t]])
z_next = K @ z
x_pred = z_next[-N_x:]               # 가장 최근 블록이 다음 상태
```

<details>
<summary><b>SVD 절단이 왜 필요한가</b></summary>

6번에서 지적했듯 Hankel 행렬은 연속된 시점끼리 열이 강하게 겹치기 때문에(반대각선이 상수인 구조상 인접한 열들은 대부분의 원소를 공유합니다), $H_X H_X^\top$ 의 작은 특이값들이 노이즈에 매우 취약합니다. 의사역행렬을 그대로 쓰면 이 작은 특이값들의 역수가 노이즈를 증폭시킵니다. 그래서 위 의사코드처럼 특이값이 임계치(`tol * S[0]`) 이하인 성분을 버리고 랭크 $r$ 로 절단한 뒤 의사역행렬을 계산하는 것이 관례입니다. 이는 EDMD에서 $\Psi(X)$ 가 ill-conditioned일 때 쓰는 처방과 동일한 원리입니다.
</details>

---

## 📌 전체 흐름 한 눈에

```
 ①  문제의식          딕셔너리 설계 난제 → 시간축으로 우회 (1번)
         │
 ②  Hankel 구성       H_X, H_Y  ← 각 열 = 시간지연 스택, 차원 dN_x (2번)
         │
 ③  연산자 추정        K_HVOK = H_Y H_X†   ← EDMD와 알고리즘 동일 (3번)
         │
 ④  정당화            Takens 임베딩 정리 → 왜 시간지연이 상태공간을 대신하는가 (4번)
         │
 ⑤  적용 플랫폼        soft / aerial / bio-inspired robot (5번)
         │
 ⑥  트레이드오프       d 튜닝, 차원 dN_x 증가, ill-conditioned 위험 (6번)
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| Hankel 행렬의 열 상관과 SVD 절단이 필요한 이유 | ↑ 7번의 접힌 섹션 |
| 딕셔너리 설계 자체의 어려움(HVOK가 우회하는 원래 문제) | [[Observable Function]] |
| EDMD의 최소자승·의사역행렬 절차(HVOK가 그대로 물려받는 부분) | [[EDMD]] §3~4 |
| 의사역행렬 자체가 뭔지 | [[Pseudo-inverse]] |
| 제어 입력 $u$ 를 넣으려면 | [[Koopman with Control Input]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[EDMD]] — 동일한 최소제곱, 다른 리프팅
> - [[Observable Function]] — HVOK가 우회하려는 설계 문제
> - [[Koopman Operator]] — 상위 개념
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
