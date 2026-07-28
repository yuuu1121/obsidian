---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - LinearAlgebra
  - Math
aliases:
  - 의사역행렬
  - 유사역행렬
  - Moore-Penrose inverse
  - Pinv
keywords: pseudo-inverse, Moore-Penrose, least squares, SVD, normal equation, minimum norm
related notes: "[[EDMD]], [[Koopman Operator]]"
dg-publish: false
---

# Pseudo-inverse (의사역행렬, $A^\dagger$)

> [!abstract] 한 문장 요약
> **역행렬이 존재하지 않는 행렬에 대해서도 "가장 그럴듯한 역행렬 역할"을 해주는 행렬.** $Ax = b$ 를 정확히 풀 수 없을 때 $x = A^\dagger b$ 는 **오차를 최소화하는 답**을 주고, 답이 무한히 많을 때는 **그중 가장 작은 답**을 줍니다.

$$
\boxed{\ x^\star = A^\dagger b\ }
$$

[[EDMD]]의 $K = \Psi(Y)\Psi(X)^\dagger$ 가 바로 이것입니다. 왜 거기에 $\dagger$ 가 붙는지가 이 노트의 최종 목적지입니다.

---

## 1. 왜 필요한가 — 역행렬의 한계

연립방정식 $Ax = b$ 를 풀 때, $A$ 가 **정사각이고 가역**이면 답은 하나입니다.

$$
x = A^{-1}b
$$

문제는 **현실의 데이터 행렬은 거의 항상 정사각이 아니라는 것**입니다. $A \in \mathbb{R}^{m\times n}$ 일 때 두 가지 상황이 생깁니다.

### 상황 ① 식이 너무 많다 ($m > n$, overdetermined)

미지수 2개인데 방정식이 100개인 경우. 측정에 노이즈가 있으면 **모든 식을 동시에 만족하는 $x$ 는 존재하지 않습니다.**

> 예: 점 100개를 지나는 직선을 찾으라 → 그런 직선은 없습니다. 하지만 "가장 잘 맞는" 직선은 있습니다.

**→ 우리가 원하는 것: 오차 $\|Ax - b\|$ 를 최소화하는 $x$**

### 상황 ② 미지수가 너무 많다 ($m < n$, underdetermined)

방정식 2개인데 미지수 100개. 이번엔 **답이 무한히 많습니다.**

> 예: $x_1 + x_2 = 1$ → $(1,0), (0,1), (0.5,0.5), \ldots$ 무한개

**→ 우리가 원하는 것: 그중 노름 $\|x\|$ 가 가장 작은 $x$** (가장 "얌전한" 해)

> [!success] 의사역행렬의 정체
> $A^\dagger$ 는 **이 두 요구를 동시에 만족하는 유일한 답**을 줍니다.
>
> $$x = A^\dagger b \;=\; \underset{x}{\arg\min}\ \|x\|_2 \quad\text{among}\quad \underset{x}{\arg\min}\ \|Ax-b\|_2$$
>
> 읽는 법: **"먼저 오차를 최소화하고, 그런 $x$ 가 여럿이면 그중 가장 작은 것".** 그래서 어떤 $A$ 에 대해서도 답이 **항상 존재하고 유일**합니다.

---

## 2. 가장 흔한 경우의 공식 (full column rank)

$A \in \mathbb{R}^{m\times n}$ 이고 $m > n$, 열이 선형독립(full column rank)이면:

$$
\boxed{\ A^\dagger = (A^\top A)^{-1}A^\top\ }
$$

이것이 **최소자승법의 정규방정식(normal equation)** 그 자체입니다.

<details>
<summary><b>유도 — 왜 이 공식인가</b></summary>

오차 제곱을 최소화합니다.

$$
J(x) = \|Ax - b\|_2^2 = (Ax-b)^\top(Ax-b) = x^\top A^\top A x - 2b^\top Ax + b^\top b
$$

$x$ 로 미분해서 0으로 두면:

$$
\frac{\partial J}{\partial x} = 2A^\top Ax - 2A^\top b = 0
$$

$$
\Rightarrow\quad \underbrace{A^\top A\,x = A^\top b}_{\text{정규방정식}}
$$

$A$ 가 full column rank면 $A^\top A$ 는 가역이므로

$$
x = (A^\top A)^{-1}A^\top b = A^\dagger b
$$
</details>

> [!note] 반대 경우 (full **row** rank, $m<n$)
> $$A^\dagger = A^\top(AA^\top)^{-1}$$
> 이쪽은 **최소 노름 해**를 줍니다. 두 공식 모두 아래 SVD 정의의 특수한 경우입니다.

---

## 3. 기하학적 의미 — 직교 사영

의사역행렬의 본질은 **직교 사영(orthogonal projection)** 입니다.

$Ax$ 는 $x$ 를 어떻게 고르든 항상 **$A$ 의 열공간(column space) 안**에 있습니다. 그런데 $b$ 는 일반적으로 그 밖에 있습니다. 그러니 우리가 할 수 있는 최선은 **$b$ 를 열공간 위로 수직으로 내리는 것**입니다.

```
              b ●  ← 실제 측정값 (열공간 밖)
                │
                │ ← 잔차 r = b − Ax*  (최소가 되는 거리)
                │    이 잔차는 열공간에 ⊥ 직교
                ▼
   ────────────●────────────  col(A) : A의 열공간
              Ax*
         = AA†b  (b의 정사영)
```

- $AA^\dagger$ = **$b$ 를 열공간으로 사영하는 연산자**
- 잔차 $r = b - Ax^\star$ 는 열공간에 **직교** → 이것이 정규방정식 $A^\top(Ax-b)=0$ 의 기하학적 의미

> [!important] 이 관점을 기억하세요
> "의사역행렬 = 사영" 이라는 그림이 [[EDMD]] 6번의 **"$K_{\text{EDMD}}$ 는 $\mathcal{K}$ 를 $\mathrm{span}(\Psi)$ 위로 투영한 것"** 이라는 서술과 정확히 같은 이야기입니다. 두 노트가 여기서 만납니다.

---

## 4. 일반 정의 — SVD로 (실무 표준)

랭크가 부족하거나 어떤 모양이든 통하는 정의입니다. **특이값 분해(SVD)** 를 씁니다.

$$
A = U\Sigma V^\top, \qquad \Sigma = \mathrm{diag}(\sigma_1, \ldots, \sigma_r, 0, \ldots, 0)
$$

그러면

$$
\boxed{\ A^\dagger = V\Sigma^\dagger U^\top\ }, \qquad
\Sigma^\dagger = \mathrm{diag}\Big(\tfrac{1}{\sigma_1}, \ldots, \tfrac{1}{\sigma_r},\ 0, \ldots, 0\Big)
$$

> [!tip] $\Sigma^\dagger$ 만들기 — 규칙이 아주 단순합니다
> **0이 아닌 특이값은 역수를 취하고, 0은 그대로 0으로 둔다.** (그리고 전치)
>
> $1/0 = \infty$ 로 폭발하는 걸 **정의상 회피**하는 것이 핵심입니다. 이 덕분에 **랭크가 부족한 행렬에도 $A^\dagger$ 가 항상 존재**합니다.

### Moore–Penrose 조건

$A^\dagger$ 는 다음 4가지를 만족하는 **유일한** 행렬로도 정의됩니다.

$$
\text{(1)}\ AA^\dagger A = A \qquad \text{(2)}\ A^\dagger AA^\dagger = A^\dagger
$$
$$
\text{(3)}\ (AA^\dagger)^\top = AA^\dagger \qquad \text{(4)}\ (A^\dagger A)^\top = A^\dagger A
$$

(3),(4)가 "사영이 **직교** 사영이다"를 보장하는 조건입니다.

---

## 5. ⚠️ 실무에서 가장 중요한 부분 — 수치 안정성

여기가 이론과 실제가 갈리는 지점입니다.

### 문제: 아주 작은 특이값

$\sigma_i$ 가 0은 아니지만 **아주 작으면** $1/\sigma_i$ 가 **폭발**합니다. 데이터에 섞인 미세한 노이즈가 그 방향으로 증폭되어 결과를 망칩니다.

$$
\sigma_i = 10^{-12} \quad\Rightarrow\quad \frac{1}{\sigma_i} = 10^{12}
$$

이 상태를 **ill-conditioned** 라고 하고, 그 정도를 **조건수(condition number)** 로 잽니다.

$$
\kappa(A) = \frac{\sigma_{\max}}{\sigma_{\min}}
$$

$\kappa$ 가 크면 입력의 작은 오차가 출력에서 $\kappa$ 배로 증폭됩니다.

### 해법 ① Truncated SVD (특이값 절단)

임계값보다 작은 특이값을 **아예 0으로 취급**해서 버립니다.

```python
K = PsiY @ np.linalg.pinv(PsiX, rcond=1e-10)   # rcond가 절단 기준
```

> [!warning] `rcond`를 기본값으로 두지 마세요
> NumPy `pinv`의 `rcond` 기본값은 데이터 스케일에 따라 부적절할 수 있습니다. [[EDMD]]처럼 딕셔너리 성분들의 크기가 제각각인 경우(예: $x$ 와 $x^5$ 를 같이 씀) 특히 위험합니다. **특이값 스펙트럼을 직접 찍어보고 결정**하는 게 안전합니다.
> ```python
> s = np.linalg.svd(PsiX, compute_uv=False)
> print(s / s[0])        # 상대 특이값 — 어디서 뚝 떨어지는지 확인
> ```

### 해법 ② Tikhonov 정규화 (Ridge)

작은 값을 더해서 역행렬을 안정화합니다.

$$
A^\dagger \ \longrightarrow\ (A^\top A + \gamma I)^{-1}A^\top
$$

특이값 관점에서 보면 $\dfrac{1}{\sigma}$ 를 $\dfrac{\sigma}{\sigma^2+\gamma}$ 로 바꾸는 것이라, $\sigma \to 0$ 일 때 폭발하지 않고 0으로 부드럽게 갑니다.

[[EDMD]] 맥락의 형태:

$$
K = \Psi(Y)\Psi(X)^\top\big(\Psi(X)\Psi(X)^\top + \gamma I\big)^{-1}
$$

### 해법 ③ 정규 방정식을 직접 풀지 말 것

$(A^\top A)^{-1}A^\top$ 를 **코드로 그대로 옮기면 안 됩니다.** $A^\top A$ 를 만드는 순간 **조건수가 제곱**됩니다($\kappa(A^\top A) = \kappa(A)^2$).

```python
x = np.linalg.inv(A.T @ A) @ A.T @ b   # ❌ 나쁨 — 조건수 제곱
x = np.linalg.lstsq(A, b, rcond=None)[0]  # ✅ 좋음 — QR/SVD 기반
x = np.linalg.pinv(A) @ b                 # ✅ 좋음 — SVD 기반
```

**공식은 이해용, 코드는 `lstsq`/`pinv`** 로 기억하세요.

---

## 6. EDMD에서 왜 등장하는가 — 최종 정리

[[EDMD]]의 (7)식을 다시 봅시다.

$$
K_{\text{EDMD}} = \Psi(Y)\,\Psi(X)^{\dagger}
$$

여기에 지금까지의 내용을 대입하면 의미가 전부 풀립니다.

| 질문 | 답 |
|:---|:---|
| **왜 역행렬이 아니라 $\dagger$?** | $\Psi(X)$ 는 $N_\Psi \times M$ 로 **정사각이 아닙니다**(보통 $M \gg N_\Psi$). 역행렬 자체가 정의되지 않습니다 |
| **무엇을 최소화하나?** | $\|\Psi(Y) - K\Psi(X)\|_F$ — 상황 ①(overdetermined). 데이터가 딕셔너리보다 많아 **정확히 만족하는 $K$ 는 없고**, 오차 최소화가 최선입니다 |
| **왜 "투영"이라 하나?** | §3의 기하학. $\mathcal{K}$ 의 진짜 작용을 $\mathrm{span}(\Psi)$ **열공간 위로 정사영**한 것이 $K_{\text{EDMD}}$ 입니다 |
| **왜 학습이 빠른가?** | 닫힌 형태 해 = **SVD 한 번**. 반복 최적화(경사하강) 불필요 → 논문의 실시간성 주장의 근거 |
| **어디가 위험한가?** | $\Psi(X)$ 가 ill-conditioned일 때. 딕셔너리 성분 스케일 차이가 크면 특이값이 붕괴합니다 → §5의 해법 필요 |

> [!success] 한 줄로 꿰면
> **"데이터가 딕셔너리보다 많아 정확한 해가 없으니(①), 오차를 최소화하는 $K$ 를 직교 사영으로 구한다(§3) — 그 도구가 $\dagger$ 이고, SVD 한 번이면 끝난다(§4)."**

---

## 7. 자주 하는 오해

> [!warning] 오해 1: "$A^\dagger A = I$ 다"
> **일반적으로 아닙니다.** $A$ 가 full column rank일 때만 $A^\dagger A = I$ 이고, full row rank일 때는 $AA^\dagger = I$ 입니다. 둘 다 성립하는 건 $A$ 가 **가역 정사각**일 때뿐이며, 그때는 $A^\dagger = A^{-1}$ 입니다.

> [!warning] 오해 2: "$(AB)^\dagger = B^\dagger A^\dagger$ 다"
> **일반적으로 성립하지 않습니다.** 역행렬과 달리 의사역행렬은 이 성질을 잃습니다. 특정 랭크 조건에서만 성립합니다.

> [!warning] 오해 3: "pinv를 쓰면 수치 문제가 알아서 해결된다"
> `pinv`는 SVD 기반이라 안전한 편이지만, **`rcond` 임계값을 어디에 두느냐는 여전히 사용자의 판단**입니다. 절단을 too little 하면 노이즈 증폭, too much 하면 정보 손실입니다.

---

## 📌 전체 흐름 한 눈에

```
 ①  왜 필요한가       역행렬은 정사각+가역일 때만 존재
                      → 현실 데이터 행렬은 거의 항상 직사각      (1번)
         │
 ②  두 가지 곤란      m>n : 해가 없음  /  m<n : 해가 무한       (1번)
         │
 ③  정의             "오차 최소화 → 그런 답이 여럿이면 최소노름"
                      어떤 A에도 답이 항상 존재하고 유일          (1번)
         │
 ④  공식             (AᵀA)⁻¹Aᵀ  = 정규방정식                   (2번)
         │
 ⑤  기하             = 열공간 위로의 직교 사영                   (3번)
         │            └─ 이 관점이 EDMD 6번의 "투영"과 같은 이야기
 ⑥  일반 정의        SVD:  A† = VΣ†Uᵀ,  Σ†는 "0 아닌 σ만 역수"  (4번)
         │
 ⑦  ⚠️ 실무          작은 σ → 1/σ 폭발.  절단·정규화 필수        (5번)
```

**상황별 요약 카드**

| 상황 | $A^\dagger b$ 가 주는 것 |
|:---|:---|
| $A$ 가역 정사각 | $A^{-1}b$ (정확해) |
| $m>n$, full column rank | **최소자승해** $(A^\top A)^{-1}A^\top b$ |
| $m<n$, full row rank | **최소노름해** $A^\top(AA^\top)^{-1}b$ |
| 랭크 부족 / 일반 | SVD로 $V\Sigma^\dagger U^\top b$ — 최소자승해 중 최소노름 |

```python
# 실무 3줄 요약
np.linalg.pinv(A)              # SVD 기반, rcond로 절단 제어
np.linalg.lstsq(A, b)          # 방정식 풀이는 이게 더 안전
np.linalg.inv(A.T@A) @ A.T     # ❌ 절대 쓰지 말 것 (조건수 제곱)
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| 정규방정식 유도 (왜 $(A^\top A)^{-1}A^\top$ 인가) | ↑ 2번의 접힌 섹션 |
| 직교 사영의 그림 | ↑ 3번 |
| 이 $\dagger$ 가 Koopman에서 하는 일 | [[EDMD]] 4번(닫힌 형태 해), 6번(투영 해석) |
| 사영 오차가 왜 문제가 되는가 | [[Koopman-Invariant Subspace]] — 오차가 0이 되는 조건 |
| 사영 품질을 재는 법 | [[Consistency Index]] |

---

## Related Notes
> [!tip] 관련 노트
> - [[EDMD]] — $K = \Psi(Y)\Psi(X)^\dagger$, 이 노트의 최종 목적지
> - [[HVOK]] — $K_{\text{HVOK}} = H_Y H_X^\dagger$, Hankel 행렬은 특히 ill-conditioned 되기 쉬움
> - [[Koopman with Control Input]] — $[K\ B] = \Psi(Y)\begin{bmatrix}\Psi(X)\\U\end{bmatrix}^\dagger$
> - [[Consistency Index]] — 순/역 EDMD 행렬 $K_F, K_B$ 모두 $\dagger$ 로 계산
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
