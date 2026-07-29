---
date: 2026-07-29
status: Concept
tags:
  - Concept
  - Optimization
  - Math
  - Control
aliases:
  - QP
  - 이차계획법
  - Quadratic Programming
  - 볼록 최적화
keywords: QP, quadratic program, convex, optimization, LP, NLP, SQP, KKT
related notes: "[[Koopman MPC]], [[Affine]], [[Pseudo-inverse]]"
dg-publish: false
---

# QP (Quadratic Program, 이차계획법)

> [!abstract] 한 문장 요약
> **목적함수가 이차식, 제약이 전부 선형인 최적화 문제.** 이 조합이 특별한 이유는 **볼록(convex)** 이라서 — 최저점이 하나뿐이고, 어디서 출발해도 같은 답이 나오며, 안정적으로 빨리 풀립니다. [[Koopman MPC]]가 실시간으로 돌아가는 근거가 정확히 이것입니다.

아래 1~7번을 순서대로 읽으면 QP가 왜 그렇게 중요한지가 쌓입니다.

---

## 1. 정의

$$
\underset{z}{\text{minimize}}\quad \underbrace{\tfrac12 z^\top P z + q^\top z}_{\text{이차식}}
\qquad\text{subject to}\qquad
\underbrace{Az \le b,\quad Cz = d}_{\text{전부 선형}}
$$

이름 그대로입니다 — **Quadratic**(목적함수가 2차) + **Program**(최적화 문제의 옛 용어, "계획법").

| 기호 | 의미 |
|:---|:---|
| $z$ | 찾으려는 값 (최적화 변수) |
| $P$ | 이차항 계수 행렬 — **여기가 볼록성을 결정** |
| $q$ | 일차항 계수 |
| $Az\le b$ | 부등식 제약 (범위 제한 등) |
| $Cz = d$ | 등식 제약 (반드시 만족해야 하는 관계) |

> [!note] $\tfrac12$ 은 왜 붙나
> 미분하면 $\tfrac12 \cdot 2 = 1$ 이 되어 그래디언트가 $Pz + q$ 로 깔끔해지기 때문입니다. 관례일 뿐 본질은 아닙니다.

---

## 2. 가장 단순한 예 — 1차원

$$
\underset{z}{\text{min}}\ \ z^2 - 4z \qquad \text{s.t.}\quad z \le 1
$$

제약이 없다면 미분해서 $2z-4=0 \Rightarrow z=2$ 가 답입니다. 그런데 $z\le1$ 이라는 제약이 있으니 **$z=1$** 이 답입니다.

```
   f(z) = z² − 4z
      │
    0 ┼──────╮
      │       ╲          ← 제약 없으면 z=2가 최저
   −3 ┤    ●   ╲___╱
      │    ↑ z=1 (제약 때문에 여기서 멈춤)
      └────┬────┬────── z
           1    2
```

> [!important] QP의 본질이 여기 다 있습니다
> **"목적함수를 최소화하되, 제약이 허용하는 범위 안에서"** — 제약이 없으면 그냥 미분해서 풀면 되고, 제약이 있으면 그 경계에서 멈추게 됩니다.
>
> 위 실험에서 본 **입력 포화**($\omega$ 가 $-5$ 에 붙는 현상)가 정확히 이 상황입니다.

---

## 3. 왜 하필 "이차식 + 선형제약"인가 — 볼록성

이 조합이 특별한 이유는 단 하나, **볼록(convex)** 이기 때문입니다.

```
     볼록 (그릇 모양)              비볼록 (울퉁불퉁)
        \        /                \    /\      /\    /
         \      /                  \  /  \    /  \  /
          \____/                    \/    \__/    \/
            ↑                        ↑              ↑
       최저점 하나                여러 개 — 어디가 진짜?
```

| | **볼록 QP** | 비볼록 |
|:---|:---|:---|
| 최저점 | **하나뿐** (국소 = 전역) | 여러 개, 갇힐 수 있음 |
| 초기 추측 | **불필요** | 좋은 값이 있어야 함 |
| 계산 | 다항시간, 안정적 | 느리고 보장 없음 |
| 재현성 | 항상 같은 답 | 출발점마다 다른 답 |

> [!success] "어디서 출발해도 같은 답" — 실시간 제어의 생명줄
> 로봇이 매 스텝(19 ms마다) 문제를 새로 풉니다. 어떤 때는 좋은 답이, 어떤 때는 이상한 답이 나오면 **쓸 수 없습니다.** 볼록성이 그 일관성을 보장합니다.

### 볼록이 되는 조건

$$
\boxed{\;P \succeq 0 \quad(\text{양의 준정부호, positive semidefinite})\;}
$$

즉 모든 $z$ 에 대해 $z^\top P z \ge 0$ 이어야 합니다. 1차원으로 보면 $P>0$ 일 때 $z^2$ 계수가 양수라 **위로 열린 포물선**(그릇 모양)이 되는 것과 같습니다.

> [!warning] $P$ 가 음수 성분을 가지면
> 아래로 열린 포물선이 섞여 **최저점이 없거나 여러 개**가 됩니다. 그러면 QP라 부르긴 해도 볼록이 아니라 어려운 문제가 됩니다.
>
> MPC에서 $P$ 는 가중치 $Q, R$ 에서 나오는데, $Q\succeq0$, $R\succ0$ 으로 잡으므로 자동으로 볼록입니다.

---

## 4. 친척들과의 비교

| 이름 | 목적함수 | 제약 | 난이도 |
|:---|:---|:---|:---|
| **LP** (Linear Program) | 1차 | 선형 | 쉬움 |
| **QP** ← 지금 이것 | **2차** | **선형** | 쉬움 (볼록이면) |
| **QCQP** | 2차 | 2차 | 중간 |
| **NLP** (Nonlinear Program) | 아무거나 | 아무거나 | 어려움 |

> [!note] 왜 QP에서 멈추는가
> 목적함수를 2차까지 올려도 **선형제약을 유지하면 볼록성이 보존**됩니다. 그런데 제약까지 비선형으로 만들면 볼록성이 깨집니다. **"제약은 선형으로, 목적함수만 2차로"** 가 계산 가능성과 표현력의 균형점입니다.

---

## 5. MPC가 왜 QP인가

[[Koopman MPC]]의 최적화 문제를 QP 정의와 대조해봅시다.

$$
\begin{aligned}
\text{min}\quad & \sum_i \underbrace{(z_i-z_i^{\text{ref}})^\top Q(z_i-z_i^{\text{ref}}) + u_i^\top R u_i}_{\text{✅ 이차식}} \\
\text{s.t.}\quad & \underbrace{z_{i+1} = Az_i + Bu_i}_{\text{✅ 선형 등식}}, \qquad \underbrace{u_{\min}\le u_i\le u_{\max}}_{\text{✅ 선형 부등식}}
\end{aligned}
$$

**정확히 QP의 정의를 만족합니다.**

| QP 요소 | MPC에서 |
|:---|:---|
| 변수 $z$ | 미래 입력열 $\{u_i\}$ 와 상태 $\{z_i\}$ |
| $P$ | 가중치 $Q, R$ 로 구성 |
| $Cz=d$ | 동역학 $z_{i+1}=Az_i+Bu_i$, 초기조건 $z_0=\psi(x_k)$ |
| $Az\le b$ | 입력 제약 $u_{\min}\le u\le u_{\max}$ |

> [!success] Koopman이 하는 일이 정확히 이것입니다
> $$\underbrace{x_{i+1}=f(x_i,u_i)}_{\text{비선형 제약 → NLP}}\quad\xrightarrow{\ \text{리프팅}\ }\quad\underbrace{z_{i+1}=Az_i+Bu_i}_{\text{선형 제약 → QP}}$$
>
> 원 시스템이 비선형이면 제약이 비선형이라 **NLP**가 되어 어렵습니다(이것이 NMPC). 리프팅으로 제약을 선형으로 만들면 **QP**가 되어 실시간에 풀립니다.
>
> 대가는 차원 증가($N_x=3 \to N_\psi=8$)인데, 볼록성 덕분에 감당됩니다.

---

## 6. 비볼록이면 어떻게 하나 — SQP

bilinear 모델처럼 제약에 $u_j z$ 같은 **곱**이 있으면 선형이 아니라 QP가 아닙니다. 이때 쓰는 것이 **SQP(Sequential Quadratic Programming)** 입니다.

> **"어려운 문제를 한 번에 못 푸니, 쉬운 QP를 여러 번 푼다."**

$$
u^{(0)} \xrightarrow[\text{QP 풀기}]{\text{현재 해 주변에서 선형화}} u^{(1)} \xrightarrow[\text{QP 풀기}]{\text{재선형화}} u^{(2)} \to \cdots
$$

각 반복에서 **1차 테일러 전개**로 비선형 제약을 펴서 QP로 만들고, 그 해를 기준으로 다시 폅니다.

> [!warning] SQP는 볼록성을 되찾아주지 않습니다
> 각 **반복**은 볼록 QP이지만, 전체 문제는 여전히 비볼록입니다. 따라서
> - **국소 최적해**만 보장 (출발점에 따라 다른 답)
> - 계산량이 반복 횟수만큼 증가
>
> 03번 실험에서 bilinear MPC가 affine 대비 **6배 느렸던**(19 ms → 109 ms) 이유입니다.

📎 실제 적용 사례와 수렴 거동: [[실험 기록 - MPC 제어]] ②번

---

## 7. 실무 감각

### 문제 크기 — 변수가 몇 개인가

MPC에서 변수 개수는

$$
N_{\text{var}} = H \times (N_\psi + N_u)
$$

03번 기준: $15\times(8+2) = 150$ 개.

> [!tip] condensed form으로 줄일 수 있습니다
> 동역학 제약을 반복 대입해 $z_i$ 를 소거하면 변수가 $H\times N_u = 30$ 개로 줄어듭니다. **리프팅 차원과 무관**해지는 것이 핵심입니다. → [[Koopman MPC]] 2번의 접힌 섹션

### 솔버

| 솔버 | 특징 |
|:---|:---|
| **OSQP** | 1차 방법, 큰 문제·warm start에 강함. cvxpy 기본 QP 솔버 중 하나 |
| **qpOASES** | active-set 방식, MPC에 특화 |
| **Clarabel / ECOS** | 내점법(interior-point), 범용 |

예제 코드는 `cvxpy`로 **문제를 기술만** 하고 솔버 선택은 맡깁니다.

```python
prob = cp.Problem(cp.Minimize(cost), cons)
prob.solve(warm_start=True)      # warm_start: 이전 해를 재사용해 가속
```

> [!note] warm start가 MPC에서 특히 유효한 이유
> receding horizon이라 **매 스텝 문제가 조금씩만 바뀝니다.** 이전 해가 좋은 출발점이 되므로 반복 횟수가 크게 줄어듭니다.

---

## 📌 전체 흐름 한 눈에

```
 ①  정의        min ½zᵀPz + qᵀz   s.t.  Az ≤ b,  Cz = d        (1번)
        │        이차 목적함수 + 선형 제약
        │
 ②  왜 특별한가   P ⪰ 0 이면 볼록                                (3번)
        │        → 최저점 하나 / 초기값 불필요 / 안정적
        │        → "어디서 출발해도 같은 답" = 실시간 제어의 생명줄
        │
 ③  MPC가 QP    이차비용 + 선형동역학 + 박스제약 = 정확히 QP       (5번)
        │
 ④  Koopman의 역할   비선형 제약(NLP) → 리프팅 → 선형 제약(QP)     (5번)
        │
 ⑤  비볼록이면   SQP: 선형화 → QP → 재선형화 반복                  (6번)
                 단, 국소해만 보장 + 계산량 증가
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| MPC 전체 정식화와 각 항의 의미 | [[Koopman MPC]] 0~2번 |
| condensed form 유도 | [[Koopman MPC]] 2번의 접힌 섹션 |
| 선형 vs 아핀의 정확한 구분 | [[Affine]] |
| SQP 선형화를 코드로 | [[Koopman 예제 코드]] ⑦ |
| 반복 횟수가 성능에 미치는 영향 (실측) | [[실험 기록 - MPC 제어]] ② |
| 제약 없는 최소자승(QP의 특수 사례) | [[Pseudo-inverse]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman MPC]] — QP가 실제로 쓰이는 곳
> - [[Affine]] — "선형 제약"의 정확한 의미
> - [[Pseudo-inverse]] — 제약 없는 QP = 최소자승
> - [[실험 기록 - MPC 제어]] — 제약 포화·SQP 반복의 실측
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
