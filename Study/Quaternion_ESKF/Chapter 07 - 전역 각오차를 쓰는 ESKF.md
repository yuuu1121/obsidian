---
title: "Chapter 7 — 전역 각오차를 쓰는 ESKF (The ESKF using global angular errors)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 7
tags: [ESKF, IMU, 전역각오차, 칼만필터, 자코비안, VIO]
---

# Chapter 7 · 전역 각오차를 쓰는 ESKF

> [!abstract] 이 장을 한 문장으로
> 지금까지 각오차 $\delta\boldsymbol{\theta}$ 를 **국소(local)** 로 정의했다. 이 장은 그것을 **전역(global)** 으로 바꾸면 무엇이 달라지는지를 5·6장의 전개를 따라가며 추적하고, 바뀌는 부분만 골라 다시 유도한다. 결론은 **딱 5군데만 바뀐다.**

---

## 1. 무엇을 바꾸는가

### 1.1 합성의 위치가 바뀐다

각오차를 **전역으로 정의**한다는 것은 곧 **왼쪽에서 합성**한다는 뜻이다.

$$\mathbf{q}_t = \delta\mathbf{q}\otimes\mathbf{q} = \mathbf{q}\{\delta\boldsymbol{\theta}\}\otimes\mathbf{q}$$

[[Chapter 05 - IMU 기반 오차상태 운동학|5장]]에서 썼던 국소 정의와 비교하면

| | 국소(5·6장) | 전역(이 장) |
|---|---|---|
| 합성 | $\mathbf{q}_t = \mathbf{q}\otimes\delta\mathbf{q}$ | $\mathbf{q}_t = \delta\mathbf{q}\otimes\mathbf{q}$ |
| 오차가 사는 좌표계 | body | world |

[[Chapter 04 - 섭동 미분 적분|4장]] 4절에서 이미 두 방식을 모두 정의해 두었다. 이 장은 그중 전역 쪽을 끝까지 밀고 나가는 것이다.

### 1.2 바뀌지 않는 것 — 각속도는 여전히 국소다

> [!important] 이 구분을 놓치면 혼란스럽다
> 각**오차**는 전역으로 바꾸지만, 각**속도** $\boldsymbol{\omega}$ 의 정의는 **국소로 유지한다.** 즉 연속시간에서
> $$\dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}$$
> 이고 이산시간에서
> $$\mathbf{q} \leftarrow \mathbf{q}\otimes\mathbf{q}\{\boldsymbol{\omega}\Delta t\}$$
> 이다. **각오차를 전역으로 정의하든 말든 이것은 그대로다.**
>
> 이유는 실용적이다. **자이로가 주는 각속도 측정값이 body 좌표계, 즉 국소이기 때문**이다. 측정값을 그대로 쓰는 게 편하니 굳이 바꿀 이유가 없다.

### 1.3 왜 이런 변형을 고려하는가

[[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 3.1절에서 언급했듯, Li와 Mourikis (2012)는 **전역으로 정의한 각오차가 더 나은 성질**을 가진다는 증거를 제시했다. 관측 가능성(observability) 관점에서 일관성이 개선된다는 것이 요지다. MSCKF 계열 VIO 구현들이 이 방향을 택하는 배경이기도 하다.

---

## 2. 연속시간 운동학

### 2.1 참 상태와 공칭 상태 — 변화 없음

> [!note] 당연한 이야기
> 참 상태와 공칭 상태의 운동학에는 **오차가 등장하지 않는다.** 따라서 방정식이 전혀 바뀌지 않는다. [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 3.2~3.4절을 그대로 쓰면 된다.

### 2.2 오차 상태 운동학

바뀌는 것은 여기부터다.

$$\boxed{\begin{aligned}
\dot{\delta\mathbf{p}} &= \delta\mathbf{v} \\
\dot{\delta\mathbf{v}} &= -\left[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)\right]_\times\delta\boldsymbol{\theta} - \mathbf{R}\,\delta\mathbf{a}_b + \delta\mathbf{g} - \mathbf{R}\,\mathbf{a}_n \\
\dot{\delta\boldsymbol{\theta}} &= -\mathbf{R}\,\delta\boldsymbol{\omega}_b - \mathbf{R}\,\boldsymbol{\omega}_n \\
\dot{\delta\mathbf{a}}_b &= \mathbf{a}_w, \qquad \dot{\delta\boldsymbol{\omega}}_b = \boldsymbol{\omega}_w, \qquad \dot{\delta\mathbf{g}} = 0
\end{aligned}}$$

국소 버전과 나란히 놓고 보자.

| | 국소 (5장) | 전역 (이 장) |
|---|---|---|
| $\dot{\delta\mathbf{v}}$ 의 $\delta\boldsymbol{\theta}$ 항 | $-\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times$ | $-[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)]_\times$ |
| $\dot{\delta\boldsymbol{\theta}}$ | $-[\boldsymbol{\omega}_m-\boldsymbol{\omega}_b]_\times\delta\boldsymbol{\theta} - \delta\boldsymbol{\omega}_b - \boldsymbol{\omega}_n$ | $-\mathbf{R}\,\delta\boldsymbol{\omega}_b - \mathbf{R}\,\boldsymbol{\omega}_n$ |

> [!important] 두 가지 흥미로운 변화
> **1. 속도 식에서 $\mathbf{R}$ 이 스큐 안으로 들어갔다.**
> $-\mathbf{R}[\mathbf{a}]_\times$ 가 $-[\mathbf{R}\mathbf{a}]_\times$ 로 바뀌었다. 이는 항등식 $\mathbf{R}[\mathbf{a}]_\times\mathbf{R}^\top = [\mathbf{R}\mathbf{a}]_\times$ 와 관련된 변화다.
>
> **2. 각오차 식에서 $\delta\boldsymbol{\theta}$ 항이 사라졌다!**
> 국소 버전에는 $-[\boldsymbol{\omega}_m-\boldsymbol{\omega}_b]_\times\delta\boldsymbol{\theta}$ 라는 **자기 자신에 대한 항**이 있었는데, 전역 버전에는 **없다.** 각오차의 동역학이 자기 자신과 무관해진 것이다.
>
> 이것이 전역 정의의 큰 장점이다. 다음 절에서 전이행렬을 보면 그 효과가 더 뚜렷하다.

#### 속도 오차 유도

$\mathbf{R}_t$ 의 작은 신호 근사가 달라진다. **전역 오차이므로 $\mathbf{R}$ 의 왼쪽에 붙는다.**

$$\mathbf{R}_t = (\mathbf{I}+[\delta\boldsymbol{\theta}]_\times)\mathbf{R} + O(\|\delta\boldsymbol{\theta}\|^2)$$

([[Chapter 05 - IMU 기반 오차상태 운동학|5장]]에서는 $\mathbf{R}(\mathbf{I}+[\delta\boldsymbol{\theta}]_\times)$ 였다.)

$\mathbf{a}_B \triangleq \mathbf{a}_m-\mathbf{a}_b$, $\delta\mathbf{a}_B \triangleq -\delta\mathbf{a}_b-\mathbf{a}_n$ 로 두고 $\dot{\mathbf{v}}_t$ 를 두 가지 방식으로 전개해 비교하면

$$\dot{\delta\mathbf{v}} = \mathbf{R}\,\delta\mathbf{a}_B + [\delta\boldsymbol{\theta}]_\times\mathbf{R}(\mathbf{a}_B+\delta\mathbf{a}_B) + \delta\mathbf{g}$$

2차 항을 버리고 $[\mathbf{a}]_\times\mathbf{b} = -[\mathbf{b}]_\times\mathbf{a}$ 로 외적을 재배치하면

$$\dot{\delta\mathbf{v}} = \mathbf{R}\,\delta\mathbf{a}_B - [\mathbf{R}\mathbf{a}_B]_\times\delta\boldsymbol{\theta} + \delta\mathbf{g}$$

정의를 되돌리면 위의 결과가 된다.

#### 각오차 유도 — 여기가 핵심

참과 공칭 쿼터니언의 미분에서 출발한다.

$$\dot{\mathbf{q}}_t = \tfrac{1}{2}\mathbf{q}_t\otimes\boldsymbol{\omega}_t, \qquad \dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}$$

전역 정의 $\mathbf{q}_t = \delta\mathbf{q}\otimes\mathbf{q}$ 를 양변 미분하여 정리하면

$$\dot{\delta\mathbf{q}}\otimes\mathbf{q} = \tfrac{1}{2}\delta\mathbf{q}\otimes\mathbf{q}\otimes\delta\boldsymbol{\omega}$$

양변 오른쪽에 $\mathbf{q}^*$ 를 곱하고, $\mathbf{q}\otimes\delta\boldsymbol{\omega}\otimes\mathbf{q}^* = \mathbf{R}\,\delta\boldsymbol{\omega}$ ([[Chapter 04 - 섭동 미분 적분|4장]] 5.3절)를 쓰면

$$\dot{\delta\mathbf{q}} = \tfrac{1}{2}\delta\mathbf{q}\otimes(\mathbf{R}\,\delta\boldsymbol{\omega}) = \tfrac{1}{2}\delta\mathbf{q}\otimes\delta\boldsymbol{\omega}_G$$

여기서 $\delta\boldsymbol{\omega}_G \triangleq \mathbf{R}\,\delta\boldsymbol{\omega}$ 는 **전역 좌표계에서 표현된 작은 신호 각속도**다. 전개하여 벡터 성분만 취하고 2차 항을 버리면

$$\dot{\delta\boldsymbol{\theta}} = \delta\boldsymbol{\omega}_G = \mathbf{R}\,\delta\boldsymbol{\omega}$$

마지막으로 $\delta\boldsymbol{\omega} = -\delta\boldsymbol{\omega}_b - \boldsymbol{\omega}_n$ 을 대입하면

$$\dot{\delta\boldsymbol{\theta}} = -\mathbf{R}\,\delta\boldsymbol{\omega}_b - \mathbf{R}\,\boldsymbol{\omega}_n$$

> [!note] $\delta\boldsymbol{\theta}$ 항이 사라진 이유
> 유도 과정을 보면 $\dot{\delta\boldsymbol{\theta}} = \delta\boldsymbol{\omega}_G$ 라는 **아주 깔끔한 관계**가 나온다. 전역 각오차의 변화율은 전역 각속도 오차와 그냥 같다. 국소 정의에서 나타났던 $-[\boldsymbol{\omega}]_\times\delta\boldsymbol{\theta}$ 항은 "회전하는 좌표계에서 오차를 재기 때문에" 생기던 항인데, 전역 좌표계는 회전하지 않으므로 그 항이 없다.

---

## 3. 이산시간 운동학

### 3.1 공칭 상태 — 변화 없음

오차가 개입하지 않으므로 [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 4.1절과 동일하다.

### 3.2 오차 상태

오일러 적분을 쓰면

$$\boxed{\begin{aligned}
\delta\mathbf{p} &\leftarrow \delta\mathbf{p} + \delta\mathbf{v}\Delta t \\
\delta\mathbf{v} &\leftarrow \delta\mathbf{v} + \left(-[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)]_\times\delta\boldsymbol{\theta} - \mathbf{R}\delta\mathbf{a}_b + \delta\mathbf{g}\right)\Delta t + \mathbf{v}_i \\
\delta\boldsymbol{\theta} &\leftarrow \delta\boldsymbol{\theta} - \mathbf{R}\,\delta\boldsymbol{\omega}_b\Delta t + \boldsymbol{\theta}_i \\
\delta\mathbf{a}_b &\leftarrow \delta\mathbf{a}_b + \mathbf{a}_i \\
\delta\boldsymbol{\omega}_b &\leftarrow \delta\boldsymbol{\omega}_b + \boldsymbol{\omega}_i \\
\delta\mathbf{g} &\leftarrow \delta\mathbf{g}
\end{aligned}}$$

### 3.3 전이 행렬

$$\mathbf{F}_x = \begin{bmatrix}
\mathbf{I} & \mathbf{I}\Delta t & 0 & 0 & 0 & 0 \\
0 & \mathbf{I} & \boxed{-[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)]_\times\Delta t} & -\mathbf{R}\Delta t & 0 & \mathbf{I}\Delta t \\
0 & 0 & \boxed{\mathbf{I}} & 0 & \boxed{-\mathbf{R}\Delta t} & 0 \\
0 & 0 & 0 & \mathbf{I} & 0 & 0 \\
0 & 0 & 0 & 0 & \mathbf{I} & 0 \\
0 & 0 & 0 & 0 & 0 & \mathbf{I}
\end{bmatrix}$$

> [!important] 세 곳이 바뀌었다 (상자 표시)
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]의 $\mathbf{F}_x$ 와 비교해 보자.
>
> | 위치 | 국소 | 전역 |
> |---|---|---|
> | $\partial\delta\mathbf{v}/\partial\delta\boldsymbol{\theta}$ | $-\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\Delta t$ | $-[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)]_\times\Delta t$ |
> | $\partial\delta\boldsymbol{\theta}/\partial\delta\boldsymbol{\theta}$ | $\mathbf{R}^\top\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\}$ | $\mathbf{I}$ |
> | $\partial\delta\boldsymbol{\theta}/\partial\delta\boldsymbol{\omega}_b$ | $-\mathbf{I}\Delta t$ | $-\mathbf{R}\Delta t$ |
>
> 가운데 줄이 특히 눈에 띈다. **각오차의 자기 전이가 회전행렬에서 단위행렬로 바뀌었다.** 구현이 그만큼 단순해진다.

### 3.4 섭동 행렬 — 변화 없음

등방성(isotropic) 잡음을 가정하면 $\mathbf{F}_i$ 와 $\mathbf{Q}_i$ 는 [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]과 **동일하다.**

$$\mathbf{F}_i = \begin{bmatrix}0&0&0&0\\ \mathbf{I}&0&0&0\\ 0&\mathbf{I}&0&0\\ 0&0&\mathbf{I}&0\\ 0&0&0&\mathbf{I}\\ 0&0&0&0\end{bmatrix}, \qquad
\mathbf{Q}_i = \begin{bmatrix}\mathbf{V}_i&0&0&0\\ 0&\boldsymbol{\Theta}_i&0&0\\ 0&0&\mathbf{A}_i&0\\ 0&0&0&\boldsymbol{\Omega}_i\end{bmatrix}$$

> [!note] 왜 잡음 부분은 안 바뀌나
> $\dot{\delta\boldsymbol{\theta}}$ 에 $-\mathbf{R}\boldsymbol{\omega}_n$ 이 들어 있으므로 원칙적으로는 $\mathbf{R}$ 이 나타나야 할 것 같다. 하지만 **잡음이 등방성**이면 $\mathbf{R}\boldsymbol{\Sigma}\mathbf{R}^\top = \mathbf{R}(\sigma^2\mathbf{I})\mathbf{R}^\top = \sigma^2\mathbf{I} = \boldsymbol{\Sigma}$ 이므로 회전이 공분산을 바꾸지 않는다. 그래서 그대로다. 자세한 내용은 [[부록 A-E - 수치적분과 전이행렬|부록 E]]에 있다.

---

## 4. 보조센서와의 융합

ESKF 기계장치와 관련된 융합 방정식은 전역 각오차를 고려해도 **아주 조금만 달라진다.**

### 4.1 오차 상태 관측

국소 정의와 **유일하게 다른 점**은 자세를 각오차와 연결하는 관측 함수의 자코비안 블록이다.

$$\mathbf{Q}_{\delta\boldsymbol{\theta}} \triangleq \frac{\partial(\delta\mathbf{q}\otimes\mathbf{q})}{\partial\delta\boldsymbol{\theta}} = [\mathbf{q}]_R\,\frac{1}{2}\begin{bmatrix}0&0&0\\1&0&0\\0&1&0\\0&0&1\end{bmatrix}$$

계산하면

$$\boxed{\mathbf{Q}_{\delta\boldsymbol{\theta}} = \frac{1}{2}\begin{bmatrix}
-q_x & -q_y & -q_z \\
q_w & q_z & -q_y \\
-q_z & q_w & q_x \\
q_y & -q_x & q_w
\end{bmatrix}}$$

> [!tip] 국소 버전과 부호만 다르다
> [[Chapter 06 - IMU와 보조센서 융합|6장]]의 국소 버전과 비교하면 **오프대각 성분의 부호 패턴만 다르다.** 국소는 $[\mathbf{q}]_L$ 을, 전역은 $[\mathbf{q}]_R$ 을 쓰기 때문이다. [[Chapter 01 - 쿼터니언의 정의와 성질|1장]] 3.3절에서 두 곱 행렬의 차이가 부호 하나였던 것이 여기서 그대로 드러난다.

### 4.2 오차 주입

$$\boxed{\begin{aligned}
\mathbf{p} &\leftarrow \mathbf{p} + \hat{\delta\mathbf{p}} \\
\mathbf{v} &\leftarrow \mathbf{v} + \hat{\delta\mathbf{v}} \\
\mathbf{q} &\leftarrow \mathbf{q}\{\hat{\delta\boldsymbol{\theta}}\}\otimes\mathbf{q} \quad\text{← 여기만 다르다} \\
\mathbf{a}_b &\leftarrow \mathbf{a}_b + \hat{\delta\mathbf{a}_b} \\
\boldsymbol{\omega}_b &\leftarrow \boldsymbol{\omega}_b + \hat{\delta\boldsymbol{\omega}_b} \\
\mathbf{g} &\leftarrow \mathbf{g} + \hat{\delta\mathbf{g}}
\end{aligned}}$$

**쿼터니언 갱신 식만 영향을 받았다.** 곱하는 순서가 뒤바뀌었다.

### 4.3 ESKF 리셋

$$\hat{\delta\mathbf{x}} \leftarrow 0, \qquad \mathbf{P} \leftarrow \mathbf{G}\,\mathbf{P}\,\mathbf{G}^\top$$

$$\mathbf{G} = \begin{bmatrix}\mathbf{I}_6&0&0\\ 0&\mathbf{I}+\left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times&0\\ 0&0&\mathbf{I}_9\end{bmatrix}$$

> [!important] 부호가 $-$ 에서 $+$ 로 바뀌었다
> [[Chapter 06 - IMU와 보조센서 융합|6장]]에서는 $\mathbf{I}-[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]_\times$ 였다. 전역에서는 $\mathbf{I}+[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]_\times$ 다.

유도는 국소 때와 같은 두 사실에서 출발한다.

**사실 1.** 리셋해도 참 자세는 불변이다. $\delta\mathbf{q}^+\otimes\mathbf{q}^+ = \delta\mathbf{q}\otimes\mathbf{q}$

**사실 2.** 관측된 오차는 이미 주입되었다. $\mathbf{q}^+ = \hat{\delta\mathbf{q}}\otimes\mathbf{q}$

둘을 합치면

$$\delta\mathbf{q}^+ = \delta\mathbf{q}\otimes\hat{\delta\mathbf{q}}^* = [\hat{\delta\mathbf{q}}^*]_R\,\delta\mathbf{q}$$

$\hat{\delta\mathbf{q}}^*\approx[1,\ -\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]$ 를 대입해 전개하면 벡터 식에서

$$\delta\boldsymbol{\theta}^+ = -\hat{\delta\boldsymbol{\theta}} + \left(\mathbf{I}+\left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times\right)\delta\boldsymbol{\theta} + O(\|\delta\boldsymbol{\theta}\|^2)$$

$$\frac{\partial\delta\boldsymbol{\theta}^+}{\partial\delta\boldsymbol{\theta}} = \mathbf{I}+\left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times$$

국소에서는 $[\hat{\delta\mathbf{q}}^*]_L$ 을 썼는데 여기서는 $[\hat{\delta\mathbf{q}}^*]_R$ 을 쓴다. 두 곱 행렬의 부호 차이가 그대로 결과의 부호 차이로 나타난다.

---

## 5. Table 4 — 변경점 총정리

논문의 Table 4를 그대로 옮긴 것이다. **이 표가 이 장의 전부**라고 해도 좋다.

| 맥락 | 항목 | **국소 각오차** | **전역 각오차** |
|---|---|---|---|
| 오차 합성 | $\mathbf{q}_t$ | $\mathbf{q}\otimes\delta\mathbf{q}$ | $\delta\mathbf{q}\otimes\mathbf{q}$ |
| 오일러 적분 | $\partial\delta\mathbf{v}/\partial\delta\boldsymbol{\theta}$ | $-\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\Delta t$ | $-[\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)]_\times\Delta t$ |
| 오일러 적분 | $\partial\delta\boldsymbol{\theta}/\partial\delta\boldsymbol{\theta}$ | $\mathbf{R}^\top\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\}$ | $\mathbf{I}$ |
| 오일러 적분 | $\partial\delta\boldsymbol{\theta}/\partial\delta\boldsymbol{\omega}_b$ | $-\mathbf{I}\Delta t$ | $-\mathbf{R}\Delta t$ |
| 오차 관측 | $\mathbf{Q}_{\delta\boldsymbol{\theta}}$ | $\dfrac{1}{2}\begin{bmatrix}-q_x&-q_y&-q_z\\ q_w&-q_z&q_y\\ q_z&q_w&-q_x\\ -q_y&q_x&q_w\end{bmatrix}$ | $\dfrac{1}{2}\begin{bmatrix}-q_x&-q_y&-q_z\\ q_w&q_z&-q_y\\ -q_z&q_w&q_x\\ q_y&-q_x&q_w\end{bmatrix}$ |
| 오차 주입 | $\mathbf{q}$ | $\mathbf{q}\otimes\mathbf{q}\{\hat{\delta\boldsymbol{\theta}}\}$ | $\mathbf{q}\{\hat{\delta\boldsymbol{\theta}}\}\otimes\mathbf{q}$ |
| 리셋 | $\mathbf{G}$ 의 자세 블록 | $\mathbf{I}-[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]_\times$ | $\mathbf{I}+[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]_\times$ |

> [!tip] 구현 전환 체크리스트
> 이미 국소 버전 ESKF를 구현했다면, 전역으로 바꾸기 위해 손댈 곳은 위 표의 **7군데뿐**이다. 나머지 코드는 전부 그대로다. 두 버전을 모두 구현해 두고 성능을 비교해 보는 것도 좋은 실험이다.

---

## 6. 어느 쪽을 쓸 것인가

> [!note] 정답은 없지만 참고할 점들
> **국소 각오차**
> - 장점: 대부분의 IMU 적분 문헌이 쓰는 고전적 방식. 참고 자료가 많다.
> - 자이로 바이어스 항이 $-\mathbf{I}\Delta t$ 로 단순하다.
>
> **전역 각오차**
> - 장점: 각오차 전이가 $\mathbf{I}$ 로 단순해진다. Li와 Mourikis (2012)에 따르면 **관측 가능성 일관성 측면에서 더 나은 성질**을 가진다.
> - 속도 오차의 자코비안이 $[\mathbf{R}\mathbf{a}]_\times$ 형태라, 자세가 크게 변해도 구조가 유지된다.
>
> 논문 본문의 대부분은 **국소** 기준으로 쓰여 있으므로, 처음 구현한다면 5·6장을 따라 국소로 만들고, 이후 이 장의 표를 참고해 전역 버전을 시험해 보는 순서를 권한다.

---

## 정리

> [!abstract] 이 장의 결론
> - 전역 각오차는 $\mathbf{q}_t = \delta\mathbf{q}\otimes\mathbf{q}$, 즉 **왼쪽 합성**이다.
> - 각속도 $\boldsymbol{\omega}$ 의 국소 정의는 **그대로 유지**한다(자이로가 body 값을 주므로).
> - 참·공칭 상태 운동학, $\mathbf{F}_i$, $\mathbf{Q}_i$ 는 **변하지 않는다.**
> - 바뀌는 것은 **Table 4의 7개 항목**뿐이다.
> - 가장 두드러진 변화는 **$\partial\delta\boldsymbol{\theta}/\partial\delta\boldsymbol{\theta}$ 가 $\mathbf{R}^\top\{\cdot\}$ 에서 $\mathbf{I}$ 로** 단순해진 것이다.

---

## 관련 노트

- [[Chapter 04 - 섭동 미분 적분]] — 국소/전역 섭동의 정의
- [[Chapter 05 - IMU 기반 오차상태 운동학]] — 국소 버전 운동학
- [[Chapter 06 - IMU와 보조센서 융합]] — 국소 버전 융합
- [[부록 A-E - 수치적분과 전이행렬]] — 더 정밀한 적분법
- [[왜 오차상태를 쓰는가]]
