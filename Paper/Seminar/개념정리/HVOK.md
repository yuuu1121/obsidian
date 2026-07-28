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

> [!abstract] 한 줄 요약
> 리프팅 함수를 **설계하지 않고**, 대신 **과거 $d$ 스텝의 측정값을 쌓아서** 고차원 특징 공간을 만드는 방법. Takens 정리에 기반하며, 소프트 로봇·공중 로봇처럼 **딕셔너리 설계가 어렵고 시간 구조가 풍부한** 시스템에서 특히 강력하다.

---

## 1. 문제의식 — 딕셔너리 설계를 피하고 싶다

[[EDMD]]는 **명시적으로 고른 리프팅 맵** $\psi$ 에 의존한다. 그런데 [[Observable Function]] 노트에서 봤듯 딕셔너리 설계는 노동집약적이고 일반화가 어렵다.

**HVOK의 발상**: 상태공간에서 함수를 설계하는 대신, **시간축에서 데이터를 쌓자.**

| | EDMD | HVOK |
|:---|:---|:---|
| 특징 생성 | 명시적 딕셔너리 $\psi(x)$ | **암묵적** — 시간지연 스택 |
| 데이터 사용 | 단일 스텝 쌍 $(x_i, y_i)$ | **시간지연된 스냅샷** |
| 설계 부담 | 딕셔너리 선택이 핵심 난제 | 지연 차수 $d$ 하나 |
| 이론적 근거 | 사영 근사 | **Takens 임베딩 정리** |

---

## 2. Hankel 행렬 구성

측정 시퀀스 $x_1, x_2, \dots, x_m$ 이 주어졌을 때, 지연 차수 $d$ 로 **Hankel 행렬**을 만든다.

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

> [!note] 구조 읽는 법
> - **각 열** = 연속된 $d$ 개 시점의 측정값을 세로로 쌓은 것 → 이것이 **리프팅된 상태** $z_k = [x_k; x_{k+1}; \dots; x_{k+d-1}]$
> - **반대각선(anti-diagonal)이 상수** → Hankel 행렬의 정의
> - $H_Y$ 는 $H_X$ 를 **시간축으로 정확히 한 칸 민 것**
> - 차원: $H_X \in \mathbb{R}^{dN_x \times (m-d)}$ — 지연 $d$ 를 늘리면 리프팅 차원이 $dN_x$ 로 커진다

---

## 3. 연산자 추정

EDMD와 **완전히 같은 최소제곱**을 Hankel 행렬에 적용한다.

$$
H_Y \approx K_{\mathrm{HVOK}}\,H_X
\qquad\Longrightarrow\qquad
\boxed{\;K_{\mathrm{HVOK}} = H_Y\,H_X^{\dagger}\;}
$$

즉 **알고리즘 자체는 EDMD와 동일하고, 리프팅을 딕셔너리가 아니라 시간지연으로 대체**한 것뿐이다. 이 관점에서 HVOK는 "딕셔너리 $\psi(x_k) = [x_k; x_{k+1}; \dots; x_{k+d-1}]$ 를 쓰는 EDMD"라고 볼 수도 있다.

---

## 4. 왜 작동하는가 — Takens 임베딩 정리

논문은 이를 *"Takens-type observability arguments"* 로 표현한다.

> [!important] Takens 정리 (직관적 서술)
> 매끄러운 동역학계의 끌개(attractor) 차원이 $D$ 일 때, **단 하나의 스칼라 측정값**이라도 충분히 많은 시간지연 좌표 $[y_t, y_{t-\tau}, \dots, y_{t-(d-1)\tau}]$ 를 쌓으면 ($d > 2D$), 그 지연 좌표계는 원래 끌개와 **위상적으로 동등(diffeomorphic)** 한 임베딩을 만든다.

**로보틱스적 의미**:

1. **부분 관측(partial observability) 문제를 자동으로 완화한다.** 소프트 로봇에서 전체 변형 상태를 측정할 수 없더라도, 끝단 위치의 시계열만으로 숨은 동역학을 복원할 수 있다.
2. **시간지연 좌표는 미분 정보를 암묵적으로 포함한다.** $x_{k+1} - x_k \approx \dot{x}\Delta t$ 이므로 속도·가속도 정보가 자연히 들어온다.
3. **느린 응답·이력현상(hysteresis)을 포착한다.** 소프트 로봇의 점탄성처럼 현재 상태만으로 결정되지 않는 거동을 과거 이력이 대신 설명한다.

---

## 5. 논문에서 HVOK가 선호되는 플랫폼

논문 Table I 및 III-B 논의 기준:

| 플랫폼 | HVOK가 유리한 이유 |
|:---|:---|
| **Soft / Continuum robot** | 느린 응답 특성(slow response), 점탄성, 무한 자유도 → 딕셔너리 설계가 사실상 불가능. 시간 구조가 정보를 대신 담아준다. [72][74] |
| **Aerial robot** | 강한 환경 외란(gust, ground effect) → 외란의 시간적 상관을 지연 좌표가 포착 |
| **Bio-inspired robot** | 주기적·리듬 동역학 → 시간 구조가 풍부 |

논문 원문 표현: *"particularly favored due to its ability to capture strong environmental disturbances (as seen in aerial systems) or slow response characteristics (as in soft robotics)"*

---

## 6. 장단점

> [!success] 장점
> - **딕셔너리 설계 불필요** — 튜닝할 것은 지연 차수 $d$ 하나
> - **부분 관측 시스템에 강함** — 측정 못 하는 상태를 시간이 대신함
> - **부분 관측·강한 비선형 상황에서 더 안정적인 Koopman 추정** (논문 표현: *"often yielding more stable Koopman estimates"*)
> - EDMD와 동일한 닫힌 형태 해 → 여전히 빠름

> [!warning] 단점 / 주의
> - **$d$ 선택이 여전히 하이퍼파라미터.** 너무 작으면 임베딩 부족, 너무 크면 차원 폭발 + 데이터 부족
> - **차원이 $dN_x$ 로 선형 증가** — 다자유도 로봇에서 금방 커진다. SVD 절단으로 축소하는 게 관례
> - **샘플링 레이트에 민감.** 논문 VI절이 별도 open problem으로 지적한다 ([166]): 샘플링이 부족하면 외란 추정·제어 정확도가 저하된다
> - **Hankel 행렬은 구조적으로 ill-conditioned 되기 쉽다** — 열들이 강하게 상관됨. 정규화/절단 필수
> - **비정상(non-stationary) 시스템에서 지연 좌표의 의미가 흔들린다**

---

## 7. 의사코드

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

---

## Related Notes
> [!tip] 관련 노트
> - [[EDMD]] — 동일한 최소제곱, 다른 리프팅
> - [[Observable Function]] — HVOK가 우회하려는 설계 문제
> - [[Koopman Operator]] — 상위 개념
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
