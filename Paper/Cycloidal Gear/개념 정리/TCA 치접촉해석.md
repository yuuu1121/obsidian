---
tags: [개념정리, TCA, 치접촉해석, 좌표변환, 수치해법]
난이도: 상급
선행지식: 사이클로이드 치형 방정식, 선형대수(좌표변환), 벡터 미적분
---

# TCA — 치접촉해석 (Tooth Contact Analysis)

> [!abstract] 한 줄 정의
> **무부하 상태에서 두 기어 표면이 "위치가 같고 법선이 같다"는 조건을 방정식으로 풀어, 입력각에 대한 출력각을 구하는 방법.** 그 출력각을 이론값과 비교하면 전달오차가 나온다.

---

## 1. 배경과 위치

1960년대 미국 **Gleason Works**가 처음 제안했습니다(Song 2023 3절). 원래는 스파이럴 베벨 기어의 접촉 패턴 예측용이었고, 이후 모든 기어 종류로 확장되었습니다.

> [!important] TCA가 "무부하"인 것이 핵심 제약이자 강점
> **강점**: 하중이 없으므로 **변형이 없고**, 이빨 쌍당 **접촉점이 정확히 1개**입니다. 이 단순화 덕분에 방정식이 유한한 개수로 닫히고 풀립니다.
>
> **제약**: 실제 운전은 하중이 있습니다. 하중 하에서는 변형 때문에 여러 이빨이 동시에 물리므로 TCA로 다룰 수 없습니다. 그건 **LTCA(Loaded TCA)** 또는 별도의 접촉력 반복계산으로 처리합니다.
>
> Song(2023)의 구조가 정확히 이렇습니다:
> - **3절 TCA** → 무부하 전달오차, 백래시
> - **5절 접촉력 반복계산** → 부하 상태 접촉력, 접촉 이빨 수
> - **6절 동역학 FEM** → 부하 전달오차
>
> 세 방법이 서로 다른 조건을 다룹니다. 결과를 비교할 때 조건을 혼동하면 안 됩니다.

---

## 2. 좌표계 설정

![[../assets/Song2023/fig2.png]]
*Song(2023) Fig. 2 — TCA 좌표계. $S_p$(핀 좌표계, $X_p$-$Y_p$)는 **고정**, $S_c$(사이클로이드 좌표계, $X_c$-$Y_c$)는 운동에 따라 이동·회전. $\varphi_{in}$: 크랭크축 입력각, $\varphi_{ci}$: 사이클로이드 출력각.*

| 좌표계 | 기호 | 상태 | 이유 |
|:---|:---|:---|:---|
| 핀 좌표계 | $S_p$ | **고정** | 핀은 하우징에 고정되어 움직이지 않음 |
| 사이클로이드 좌표계 | $S_c$ | 이동 + 회전 | 편심 공전 + 자전 |

### 2.1 변환 행렬

$$M_{cp} = \begin{bmatrix}
\cos\varphi_{ci} & \sin\varphi_{ci} & 0 & a\cos\varphi_{in} \\
-\sin\varphi_{ci} & \cos\varphi_{ci} & 0 & a\sin\varphi_{in} \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

> [!tip] 동차변환행렬(homogeneous transformation matrix) 읽는 법
> $4\times4$ 행렬은 **항상** 이 구조입니다:
> $$M = \begin{bmatrix} \mathbf{R}_{3\times3} & \mathbf{t}_{3\times1} \\ \mathbf{0}_{1\times3} & 1 \end{bmatrix}$$
>
> | 블록 | 내용 | 이 경우의 물리적 의미 |
> |:---|:---|:---|
> | 좌상 $3\times3$ = $\mathbf{R}$ | **회전** | $\varphi_{ci}$만큼의 2D 회전 — 사이클로이드의 **자전** |
> | 우측 열 = $\mathbf{t}$ | **평행이동** | $(a\cos\varphi_{in},\, a\sin\varphi_{in})$ — 편심량 $a$만큼, $\varphi_{in}$ 방향으로. 사이클로이드의 **편심 공전** |
> | 하단 행 $[0\,0\,0\,1]$ | 패딩 | 동차좌표 유지용 |
>
> **왜 $4\times4$인가 (3D인데 왜 4차원)**: 회전은 행렬 곱으로 표현되지만 평행이동은 덧셈입니다. 좌표에 1을 추가해 4차원으로 만들면 **평행이동도 행렬 곱으로 통일**할 수 있습니다. 그러면 여러 변환을 곱셈으로 합성할 수 있어 로보틱스·CG에서 표준으로 씁니다.
>
> 확인: $\begin{bmatrix}x\\y\\0\\1\end{bmatrix}$에 $M$을 곱하면 $\begin{bmatrix}x\cos\varphi_{ci} + y\sin\varphi_{ci} + a\cos\varphi_{in}\\ \ldots\\0\\1\end{bmatrix}$ — 회전 후 평행이동이 한 번에 됩니다.

> [!note] $L_{cp}$ — 왜 회전 부분만 쓰는가
> 논문에서 $L_{cp}$는 "$M_{cp}$의 좌상단 $3\times3$ 부분행렬"입니다. **법선벡터를 변환할 때 씁니다.**
>
> **이유**: 법선벡터는 **방향**만 의미하는 벡터이고, 위치가 아닙니다. 평행이동은 방향을 바꾸지 않습니다(화살표를 옮겨도 방향은 그대로). 따라서 회전만 적용해야 합니다.
>
> 이것은 벡터 변환의 일반 규칙입니다:
> - **점(point)** → 회전 + 평행이동 (전체 $M$)
> - **벡터(방향)** → 회전만 ($\mathbf{R}$ 부분만)
>
> 동차좌표로는 점의 마지막 성분이 1, 벡터는 0으로 구별합니다.

---

## 3. 표면 방정식과 법선벡터

### 3.1 핀 치형

$$R_p(\theta_{pi}) = \begin{bmatrix}
\underbrace{r_p\sin\left(\frac{2\pi}{z_p}i\right)}_{i\text{번 핀 중심}} + \underbrace{r_{rp}\cos\theta_{pi}}_{\text{핀 표면}} \\
r_p\cos\left(\frac{2\pi}{z_p}i\right) + r_{rp}\sin\theta_{pi} \\
0 \\ 1
\end{bmatrix}$$

- $\frac{2\pi}{z_p}i$ — $i$번째 핀이 놓인 각도. $z_p = 40$이면 핀 간격은 $360°/40 = 9°$.
- $\theta_{pi}$ — 그 핀 **표면상의 점**을 가리키는 매개변수각. 핀은 원이므로 원의 매개변수 표현입니다.

### 3.2 사이클로이드 치형

$$R_c(\theta_{ci}) = \begin{bmatrix} x \\ y \\ 0 \\ 1 \end{bmatrix}, \qquad \theta_{ci} \in (0, 2\pi)$$

$x$, $y$는 [[사이클로이드 치형 방정식]]의 식 (1)(2)입니다.

> [!warning] 수정된 치형을 해석할 때
> Song 논문의 명시적 주의사항: *"when the cycloid gear is modified, the tooth profile equation in $R_c(\theta_{ci})$ should be replaced by the corresponding tooth profile equation."*
>
> 즉 표준 치형 식을 [[치형 수정 modification|수정 치형 식]](식 4, 5 또는 6, 7)으로 **갈아 넣어야** 합니다. 이것이 TCA로 수정 효과를 평가하는 방식입니다.

### 3.3 법선벡터 구하기

$$n_p(\theta_{pi}) = \frac{\dfrac{dR_p}{d\theta_{pi}} \times \mathbf{k}}{\left\lVert \dfrac{dR_p}{d\theta_{pi}} \times \mathbf{k}\right\rVert}, \qquad \mathbf{k} = [0,0,1]$$

$n_c$도 같은 방식입니다.

> [!tip] 3단계로 나눠 보기
> **① 미분** → 접선벡터
> $\dfrac{dR}{d\theta}$는 매개변수 곡선의 **접선(tangent)** 입니다. 곡선이 뻗어가는 방향입니다.
>
> **② $\mathbf{k}$와 외적** → 90° 회전
> 2D 평면 곡선에서 법선은 접선에 수직입니다. $z$축 단위벡터 $\mathbf{k}$와 외적하면 정확히 90° 돌아갑니다:
> $$[t_x, t_y, 0] \times [0, 0, 1] = [t_y, -t_x, 0]$$
> 직접 검산: 외적 공식 $(a_2b_3-a_3b_2,\; a_3b_1-a_1b_3,\; a_1b_2-a_2b_1)$에 대입하면 $(t_y \cdot 1 - 0,\; 0 - t_x \cdot 1,\; 0)= (t_y, -t_x, 0)$ ✅
>
> **③ 정규화(unitize)** → 크기 1
> 크기로 나눠 단위벡터로 만듭니다. **이 단계가 4절에서 결정적으로 중요합니다.**

---

## 4. 접촉 조건 — TCA의 핵심

### 4.1 방정식

$$\boxed{\begin{aligned}
R_c^p(\theta_{ci}, \varphi_{in}, \varphi_{ci}) &= R_p(\theta_{pi}) &&\text{...위치 일치} \\
n_c^p(\theta_{ci}, \varphi_{in}, \varphi_{ci}) &= n_p(\theta_{pi}) &&\text{...법선 일치}
\end{aligned}}$$

여기서 $R_c^p = M_{cp}R_c$, $n_c^p = L_{cp}n_c$ (사이클로이드 표면을 핀 좌표계로 변환)

> [!note] 왜 두 조건이 필요한가 — 접촉의 기하학적 정의
> **위치만 같으면** 두 곡선이 **교차(cross)** 할 수도 있습니다. 교차는 접촉이 아니라 간섭(파고듦)입니다.
>
> **법선까지 같아야** 두 곡선이 **접(tangent)** 합니다 — 이것이 접촉입니다.
>
> 직관: 두 원이 만나는 방식은 (1) 두 점에서 교차, (2) 한 점에서 접함 두 가지입니다. 접할 때만 두 원의 법선(중심을 잇는 선)이 일치합니다.

### 4.2 방정식 3개, 미지수 4개 — 그래서 풀린다

> [!important] 이 계수 세기가 TCA 이해의 핵심이다
> **방정식 개수**:
>
> | 조건 | 스칼라 방정식 수 | 이유 |
> |:---|:---:|:---|
> | 위치 일치 | **2** | $x$축, $y$축에 투영 (평면 문제이므로 $z$는 자동) |
> | 법선 일치 | **1** | $x$성분만 |
> | **합계** | **3** | |
>
> **왜 법선 조건이 2개가 아니라 1개인가**: $n_c^p$와 $n_p$가 **둘 다 단위벡터**입니다. 크기가 1로 고정되어 있으므로 $x$성분이 같으면 $y$성분은 자동으로 같습니다($n_x^2 + n_y^2 = 1$이므로 $n_y = \pm\sqrt{1-n_x^2}$, 부호는 방향으로 결정).
>
> **즉 3.3절 ③단계의 정규화가 여기서 결실을 맺습니다.** 정규화하지 않았다면 방정식이 4개가 되어 시스템이 **과결정(overdetermined)** 되고 일반적으로 해가 없어집니다.
>
> **미지수 4개**: $\theta_{ci}$(사이클로이드 표면 매개변수), $\theta_{pi}$(핀 표면 매개변수), $\varphi_{in}$(입력각), $\varphi_{ci}$(출력각)
>
> **결과**: 방정식 3개 + 미지수 4개 → **하나를 주면 나머지 3개가 결정**됩니다. 실제로는 $\varphi_{in}$을 일정 스텝으로 주고 $\varphi_{ci}$를 구합니다.

### 4.3 전달오차로 이어지는 흐름

```
φ_in 을 스텝별로 준다 (예: 0.1°씩)
    ↓
식 (15) 비선형 연립방정식을 푼다  →  θ_ci, θ_pi, φ_ci 획득
    ↓
TE = φ_ci − φ_in / z_c            →  그 순간의 전달오차
    ↓
모든 스텝에 반복  →  전달오차 곡선 (Fig. 8)
```

---

## 5. 수치해법의 실무적 함정

> [!danger] 논문이 명시적으로 경고하는 문제
> Song(2023) 3.4절:
>
> > *"there are cases where the solution results in interference between the cycloid and the pin teeth, which can be avoided by adjusting the initial value of the solution to the system of equations several times."*
>
> **식 (15)는 비선형 연립방정식**이므로 해석해가 없고 Newton법 등 반복 수치해법으로 풀어야 합니다. 그런데:
>
> 1. **초기값에 민감** — 초기값이 나쁘면 수렴하지 않거나 엉뚱한 해로 갑니다.
> 2. **물리적으로 불가능한 해가 존재** — 두 기어가 서로 파고든(interference) 상태도 방정식을 만족할 수 있습니다.
> 3. **여러 개의 해** — 여러 핀 중 어느 것과 접촉하는지에 따라 해가 여러 개입니다.
>
> **대응**: 여러 초기값을 시도하고, 얻은 해가 물리적으로 타당한지(간섭 없는지) 검사하는 로직이 필요합니다.

> [!tip] 실제 구현 시 권장 전략
> ```python
> from scipy.optimize import fsolve
>
> def contact_eqs(unknowns, phi_in, i_pin, params):
>     theta_c, theta_p, phi_ci = unknowns
>     # 위치 2개 + 법선 1개 = 3개 residual 반환
>     ...
>     return [res_x, res_y, res_n]
>
> def solve_contact(phi_in, i_pin, params, prev_solution=None):
>     # 전략 1: 이전 스텝의 해를 초기값으로 (연속성 활용) ← 가장 효과적
>     candidates = [prev_solution] if prev_solution is not None else []
>     # 전략 2: 기하학적 추정값
>     candidates.append(geometric_guess(phi_in, i_pin, params))
>     # 전략 3: 여러 무작위 초기값
>     candidates += [random_guess() for _ in range(10)]
>
>     for x0 in candidates:
>         sol, info, ier, msg = fsolve(contact_eqs, x0,
>                                      args=(phi_in, i_pin, params),
>                                      full_output=True)
>         if ier == 1 and is_physically_valid(sol, params):  # 간섭 검사 필수
>             return sol
>     raise RuntimeError(f"수렴 실패: phi_in={phi_in}, pin={i_pin}")
> ```
>
> **전략 1(이전 해를 초기값으로)이 가장 중요합니다.** $\varphi_{in}$을 작은 스텝으로 증가시키면 해도 연속적으로 변하므로, 직전 해가 훌륭한 초기값이 됩니다. 이 기법을 **연속법(continuation method)** 이라 부릅니다.
>
> `is_physically_valid()`는 최소한 (1) $\theta$가 유효 범위인지, (2) 접촉점이 이빨 면 안에 있는지, (3) 다른 핀과 간섭하지 않는지를 확인해야 합니다.

---

## 6. 계산량을 줄이는 트릭

Song(2023) 3.4절의 두 처리입니다.

### 6.1 주기성 활용

전달오차의 주기는 $2\pi/z_p$입니다[12,14]. 사이클로이드 방정식은 이빨 하나만 표현하므로:

1. 한 주기만 계산
2. $2\pi/z_c$씩 평행이동해 복제[27]
3. 전체 곡선 완성

Fig. 8(a)가 Fig. 8(b)를 평행이동해 만든 것이라고 논문이 명시합니다.

### 6.2 좌표 이동

계산 편의를 위해 핀 방정식의 $x$좌표를 $-x$ 방향으로 편심량 $a$만큼 평행이동합니다.

> [!warning] 이때 반드시 함께 해야 하는 것
> 논문: *"the displacement transformation of the coordinate transformation matrix $M_{cp}$ in the direction of the x-axis also requires translation by a displacement of one eccentric distance $a$ in the negative direction."*
>
> **$M_{cp}$의 $x$방향 변위도 똑같이 $-a$ 이동**시켜야 합니다. 즉 $a\cos\varphi_{in} \to a\cos\varphi_{in} - a$.
>
> 한쪽만 옮기면 두 좌표계가 어긋나 완전히 틀린 결과가 나옵니다. 재현 시 놓치기 쉬운 부분입니다.

---

## 7. TCA로 얻는 것들

| 결과 | 계산 방법 | Song 논문 위치 |
|:---|:---|:---|
| **전달오차 곡선** | $\varphi_{in}$ 스윕 → $TE = \varphi_{ci} - \varphi_{in}/z_c$ | Fig. 8 |
| **백래시** | 맞물림 진입각 $\beta$ → $2\beta$ | Fig. 3, 3.5절 |
| **맞물림 순간 접촉점 위치** | 해의 $\theta_{ci}$, $\theta_{pi}$ | (직접 보고 없음) |
| **맞물림 영역** | 해가 존재하는 $\varphi_{in}$ 범위 | Liang et al.[20] |

> [!note] TCA가 주지 못하는 것
> - **접촉력** — 무부하이므로 힘이 0입니다. 별도의 하중 분포 모델 필요(Song 5절).
> - **접촉응력** — 힘이 없으므로 응력도 없습니다. Hertz 접촉 또는 FEM 필요.
> - **동시 접촉 이빨 수** — 무부하에서는 1개뿐입니다. 변형을 고려해야 여러 개가 나옵니다.
> - **동적 효과** — 관성, 충격, 진동은 다루지 않습니다. 동역학 해석 필요(Song 6.2절).
>
> 즉 **TCA는 기하학적 정밀도만 다룹니다.** 강도·수명·진동은 별도 해석이 필요합니다.

---

## 8. 요약

> [!check] 기억할 것
> 1. **TCA = 무부하 기하학적 접촉 해석.** 하중이 있으면 못 씁니다.
> 2. **접촉 조건 2개**: 위치 일치 + 법선 일치. 법선까지 같아야 "교차"가 아니라 "접촉"입니다.
> 3. **방정식 3개, 미지수 4개** → 하나를 주면 풀림. 법선 정규화가 방정식 수를 3개로 줄이는 핵심 장치입니다.
> 4. **$M_{cp}$는 자전(회전) + 편심 공전(평행이동)**. 법선에는 회전($L_{cp}$)만 적용합니다.
> 5. **비선형 연립방정식이므로 초기값 민감** — 이전 스텝의 해를 초기값으로 쓰는 연속법이 최선, 간섭 검사 필수.

---

## 관련 노트

- 선행: [[사이클로이드 치형 방정식]] · [[사이클로이드 감속기 구조]]
- 후속: [[전달오차와 백래시]] (TCA로 계산하는 대상)
- 관련: [[헤르츠 접촉과 접촉응력]] (TCA가 다루지 못하는 부하 상태)
- 논문: [[Song2023 - 다목적 최적화 치형수정]] (3절이 주 출처) · 원류: Gleason Works (1960s), Litvin의 기어 기하학 이론
