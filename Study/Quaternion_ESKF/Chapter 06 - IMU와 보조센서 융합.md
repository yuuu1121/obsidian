---
title: "Chapter 6 — IMU와 보조센서 융합 (Fusing IMU with complementary sensory data)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 6
tags: [ESKF, IMU, GPS, 비전, 센서융합, 칼만보정, 리셋, VIO]
---

# Chapter 6 · IMU와 보조센서 융합

> [!abstract] 이 장을 한 문장으로
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]의 예측만으로는 공분산이 무한정 커진다. GPS나 비전 같은 **다른 종류의 정보가 도착했을 때** 필터를 보정하는 세 단계 — **오차 관측 → 공칭 상태에 주입 → 오차 리셋** — 를 유도한다. 이 장을 마치면 ESKF 한 사이클이 완성된다.

---

## 들어가며 — 왜 다른 센서가 필요한가

IMU 정보는 지금까지 **예측(prediction)** 에만 쓰였다. 예측은 공분산을 계속 키우기만 한다. 오차를 실제로 **관측 가능(observable)** 하게 만들려면 다른 정보가 필요하다.

잘 설계된 시스템에서는 이 보정이 **IMU 바이어스까지 관측 가능하게** 만들어 ESKF가 그것을 제대로 추정할 수 있게 해 준다.

### 대표적인 조합

| 조합 | 특징 |
|---|---|
| **GPS + IMU** | 가장 고전적. 실외 전용 |
| **단안 비전 + IMU** | 스케일 모호성을 IMU가 해결 |
| **스테레오 비전 + IMU** | 스케일이 직접 관측됨 |

> [!note] 비전 + IMU가 뜨거운 이유
> 최근 몇 년간 **시각 센서와 IMU의 결합**이 큰 관심을 끌며 많은 연구가 쏟아졌다. 이런 vision + IMU 구성은 **GPS가 통하지 않는 환경(GPS-denied)** 에서 특히 유용하고, 스마트폰 같은 모바일 기기는 물론 UAV나 작고 민첩한 플랫폼에도 구현할 수 있다.
>
> 이것이 **VIO(Visual-Inertial Odometry)** 와 **VI-SLAM** 분야다. 이 논문이 VIO를 공부하는 사람들의 필독서로 꼽히는 이유이기도 하다.

### 보정의 세 단계

> [!important] 이 장의 전체 구조
> 1. **필터 보정을 통한 오차 상태의 관측** (6.1절)
> 2. **관측된 오차를 공칭 상태에 주입** (6.2절)
> 3. **오차 상태의 리셋** (6.3절)
>
> 세 단계가 모두 필요하다. 특히 3번을 빠뜨리면 필터가 망가진다.

---

## 1. 필터 보정을 통한 오차 상태의 관측

### 1.1 측정 모델

상태에 의존하는 정보를 주는 센서가 있다고 하자.

$$\mathbf{y} = h(\mathbf{x}_t) + \mathbf{v}$$

여기서 $h(\cdot)$ 는 시스템의 **참 상태**에 대한 일반적인 비선형 함수이고, $\mathbf{v}$ 는 공분산 $\mathbf{V}$ 를 갖는 백색 가우시안 잡음이다.

$$\mathbf{v} \sim \mathcal{N}\{0, \mathbf{V}\}$$

> [!note] 예를 들면
> **GPS**라면 $h(\mathbf{x}_t) = \mathbf{p}_t$ (위치를 그대로 측정).
> **카메라**라면 $h(\mathbf{x}_t)$ 는 3D 점을 이미지 평면에 투영하는 함수(핀홀 모델 + 좌표 변환).

### 1.2 칼만 보정 방정식

평범한 EKF의 보정 식과 같은 모양이다.

$$\boxed{\begin{aligned}
\mathbf{K} &= \mathbf{P}\mathbf{H}^\top(\mathbf{H}\mathbf{P}\mathbf{H}^\top + \mathbf{V})^{-1} \\
\hat{\delta\mathbf{x}} &\leftarrow \mathbf{K}(\mathbf{y} - h(\hat{\mathbf{x}}_t)) \\
\mathbf{P} &\leftarrow (\mathbf{I}-\mathbf{K}\mathbf{H})\mathbf{P}
\end{aligned}}$$

> [!warning] 공분산 갱신 식의 수치 안정성
> 논문은 가장 단순한 형태 $\mathbf{P}\leftarrow(\mathbf{I}-\mathbf{K}\mathbf{H})\mathbf{P}$ 를 제시하면서, **이 형태가 수치적으로 불안정하다**고 명시적으로 경고한다. 결과가 대칭이라는 보장도, 양정치(positive definite)라는 보장도 없다.
>
> 더 안정적인 형태를 쓰는 것이 좋다.
> - **대칭 형태**: $\mathbf{P}\leftarrow\mathbf{P}-\mathbf{K}(\mathbf{H}\mathbf{P}\mathbf{H}^\top+\mathbf{V})\mathbf{K}^\top$
> - **Joseph 형태** (대칭 + 양정치): $\mathbf{P}\leftarrow(\mathbf{I}-\mathbf{K}\mathbf{H})\mathbf{P}(\mathbf{I}-\mathbf{K}\mathbf{H})^\top + \mathbf{K}\mathbf{V}\mathbf{K}^\top$
>
> 장시간 돌리는 시스템에서는 Joseph 형태를 쓰는 것을 권한다. 계산량은 조금 늘지만 필터가 발산하는 사고를 막아 준다.

### 1.3 여기서 $\mathbf{H}$ 가 문제다

위 식들이 요구하는 자코비안 $\mathbf{H}$ 는 **오차 상태 $\delta\mathbf{x}$ 에 대해** 정의되어야 하고, 최선의 참 상태 추정치 $\hat{\mathbf{x}}_t = \mathbf{x}\oplus\hat{\delta\mathbf{x}}$ 에서 평가되어야 한다.

그런데 이 단계에서 **오차 상태의 평균은 아직 0**이다(아직 관측하지 않았으므로). 따라서 $\hat{\mathbf{x}}_t = \mathbf{x}$ 이고, 공칭 상태를 평가점으로 쓸 수 있다.

$$\mathbf{H} \triangleq \left.\frac{\partial h}{\partial\delta\mathbf{x}}\right|_{\mathbf{x}}$$

### 1.4 연쇄법칙으로 $\mathbf{H}$ 계산하기

가장 이해하기 쉬운 방법은 **연쇄법칙(chain rule)** 이다.

$$\mathbf{H} \triangleq \left.\frac{\partial h}{\partial\delta\mathbf{x}}\right|_{\mathbf{x}} = \left.\frac{\partial h}{\partial\mathbf{x}_t}\right|_{\mathbf{x}}\left.\frac{\partial\mathbf{x}_t}{\partial\delta\mathbf{x}}\right|_{\mathbf{x}} = \mathbf{H}_x\,\mathbf{X}_{\delta\mathbf{x}}$$

> [!important] 두 조각으로 나누는 것이 요령이다
> **$\mathbf{H}_x = \partial h/\partial\mathbf{x}_t$** — 센서 측정 함수를 **자기 인자로** 미분한 것. 평범한 EKF에서 쓰는 바로 그 자코비안이다. **사용하는 센서마다 다르므로** 논문은 이 부분을 다루지 않는다. 여러분의 센서에 맞게 구하면 된다.
>
> **$\mathbf{X}_{\delta\mathbf{x}} = \partial\mathbf{x}_t/\partial\delta\mathbf{x}$** — 참 상태를 오차 상태로 미분한 것. **오직 ESKF의 상태 합성 방식에만 의존**하므로 여기서 한 번 구해 두면 모든 센서에 재사용할 수 있다.
>
> 이 분리가 ESKF 구현을 깔끔하게 만든다. 센서를 추가할 때 $\mathbf{H}_x$ 만 새로 쓰면 된다.

### 1.5 $\mathbf{X}_{\delta\mathbf{x}}$ 구하기

각 상태에 대해 미분해 보면, **쿼터니언을 뺀 나머지는 전부 $3\times3$ 단위행렬**이다. 예를 들어 위치는 $\partial(\mathbf{p}+\delta\mathbf{p})/\partial\delta\mathbf{p} = \mathbf{I}_3$ 이다.

유일한 예외가 **쿼터니언 항**이다. $4\times3$ 크기이며

$$\mathbf{Q}_{\delta\boldsymbol{\theta}} = \frac{\partial(\mathbf{q}\otimes\delta\mathbf{q})}{\partial\delta\boldsymbol{\theta}}$$

따라서 전체 형태는

$$\mathbf{X}_{\delta\mathbf{x}} = \left.\frac{\partial\mathbf{x}_t}{\partial\delta\mathbf{x}}\right|_{\mathbf{x}} = \begin{bmatrix}\mathbf{I}_6 & 0 & 0 \\ 0 & \mathbf{Q}_{\delta\boldsymbol{\theta}} & 0 \\ 0 & 0 & \mathbf{I}_9\end{bmatrix} \in \mathbb{R}^{19\times18}$$

> [!note] 19×18 행렬
> 왼쪽 위 $\mathbf{I}_6$ 는 위치·속도(3+3), 오른쪽 아래 $\mathbf{I}_9$ 는 두 바이어스와 중력(3+3+3)이다. 가운데만 $4\times3$ 이라서 전체가 $19\times18$ 이 된다. [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]에서 말한 "19차원 상태, 18차원 오차 상태"가 여기 그대로 나타난다.

#### 쿼터니언 블록 유도

[[Chapter 01 - 쿼터니언의 정의와 성질|1장]]의 곱 행렬과 $\delta\mathbf{q}\to[1,\ \tfrac{1}{2}\delta\boldsymbol{\theta}]$ 극한을 쓰면

$$\mathbf{Q}_{\delta\boldsymbol{\theta}} = \frac{\partial(\mathbf{q}\otimes\delta\mathbf{q})}{\partial\delta\mathbf{q}}\left.\frac{\partial\delta\mathbf{q}}{\partial\delta\boldsymbol{\theta}}\right|_{\hat{\delta\boldsymbol{\theta}}=0} = [\mathbf{q}]_L\,\frac{1}{2}\begin{bmatrix}0&0&0\\1&0&0\\0&1&0\\0&0&1\end{bmatrix}$$

계산하면

$$\boxed{\mathbf{Q}_{\delta\boldsymbol{\theta}} = \frac{1}{2}\begin{bmatrix}
-q_x & -q_y & -q_z \\
q_w & -q_z & q_y \\
q_z & q_w & -q_x \\
-q_y & q_x & q_w
\end{bmatrix}}$$

---

## 2. 관측된 오차를 공칭 상태에 주입

ESKF 갱신이 끝나면, 공칭 상태를 관측된 오차 상태로 갱신한다. **적절한 합성**(덧셈 또는 쿼터니언 곱)을 쓴다.

$$\mathbf{x} \leftarrow \mathbf{x}\oplus\hat{\delta\mathbf{x}}$$

구체적으로는

$$\boxed{\begin{aligned}
\mathbf{p} &\leftarrow \mathbf{p} + \hat{\delta\mathbf{p}} \\
\mathbf{v} &\leftarrow \mathbf{v} + \hat{\delta\mathbf{v}} \\
\mathbf{q} &\leftarrow \mathbf{q}\otimes\mathbf{q}\{\hat{\delta\boldsymbol{\theta}}\} \\
\mathbf{a}_b &\leftarrow \mathbf{a}_b + \hat{\delta\mathbf{a}_b} \\
\boldsymbol{\omega}_b &\leftarrow \boldsymbol{\omega}_b + \hat{\delta\boldsymbol{\omega}_b} \\
\mathbf{g} &\leftarrow \mathbf{g} + \hat{\delta\mathbf{g}}
\end{aligned}}$$

> [!important] 자세만 곱셈이다
> 다섯 개는 평범한 덧셈인데 **쿼터니언만 곱셈**이다. [[Chapter 04 - 섭동 미분 적분|4장]]에서 본 $\oplus$ 연산이 여기서 실제로 쓰인다. $\mathbf{q}\{\hat{\delta\boldsymbol{\theta}}\} = \mathrm{Exp}(\hat{\delta\boldsymbol{\theta}})$ 이고, $\hat{\delta\boldsymbol{\theta}}$ 가 작으므로 $[1,\ \hat{\delta\boldsymbol{\theta}}/2]$ 로 근사한 뒤 정규화해도 된다.
>
> 이 한 줄이 **"매니폴드 위에서 갱신한다"** 는 ESKF의 정신을 그대로 보여 준다. 오차는 평평한 공간에서 계산하고, 적용할 때만 곡면 위로 올려보낸다.

---

## 3. ESKF 리셋

### 3.1 왜 리셋이 필요한가

오차를 공칭 상태에 주입했으면, 오차 상태의 평균 $\hat{\delta\mathbf{x}}$ 를 **0으로 리셋**해야 한다. 같은 오차를 두 번 적용하면 안 되기 때문이다.

> [!important] 자세 부분이 특히 중요하다
> 논문이 강조하는 지점이다. **새로운 자세 오차는 새 공칭 상태의 자세 좌표계에 대해 국소적으로 표현**되기 때문이다.
>
> 공칭 자세가 $\mathbf{q}$ 에서 $\mathbf{q}^+ = \mathbf{q}\otimes\hat{\delta\mathbf{q}}$ 로 바뀌었으므로, **오차를 재는 기준 좌표계 자체가 회전했다.** 남아 있는 불확실성(공분산)도 그 새 좌표계에 맞춰 다시 표현해야 한다.
>
> 이것은 매니폴드 위에서 작업할 때만 생기는 문제다. 평평한 공간이라면 기준점을 옮겨도 방향이 그대로이므로 공분산이 변하지 않는다.

### 3.2 리셋 함수와 자코비안

리셋 함수를 $g()$ 라 하면

$$\delta\mathbf{x} \leftarrow g(\delta\mathbf{x}) = \delta\mathbf{x}\ominus\hat{\delta\mathbf{x}}$$

여기서 $\ominus$ 는 $\oplus$ 의 역연산이다. ESKF 리셋 연산은 결국

$$\boxed{\begin{aligned}
\hat{\delta\mathbf{x}} &\leftarrow 0 \\
\mathbf{P} &\leftarrow \mathbf{G}\,\mathbf{P}\,\mathbf{G}^\top
\end{aligned}}$$

자코비안 $\mathbf{G}$ 는

$$\mathbf{G} \triangleq \left.\frac{\partial g}{\partial\delta\mathbf{x}}\right|_{\hat{\delta\mathbf{x}}}$$

앞의 갱신 자코비안과 마찬가지로, **자세 오차를 뺀 모든 대각 블록에서 단위행렬**이다.

$$\mathbf{G} = \begin{bmatrix}\mathbf{I}_6 & 0 & 0 \\ 0 & \mathbf{I}-\left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times & 0 \\ 0 & 0 & \mathbf{I}_9\end{bmatrix}$$

### 3.3 실무에서는 대개 무시한다

> [!tip] 대부분의 구현이 $\mathbf{G}=\mathbf{I}_{18}$ 로 둔다
> 논문이 직접 밝히는 바다. 대부분의 경우 오차 항 $\hat{\delta\boldsymbol{\theta}}$ 는 **무시할 수 있을 만큼 작아서**, 자코비안이 그냥 $\mathbf{G}=\mathbf{I}_{18}$ 이 되고 리셋이 자명해진다. **실제 ESKF 구현 대부분이 이렇게 한다.**
>
> 다만 여기 제시된 정확한 식을 쓰면 **더 정밀한 결과**를 얻을 수 있고, 이는 **오도메트리 시스템의 장기 오차 표류를 줄이는 데** 유용할 수 있다. 몇 시간씩 돌리는 시스템이라면 고려할 가치가 있다.

### 3.4 자세 오차 블록의 유도

새 각오차 $\delta\boldsymbol{\theta}^+$ 를 이전 오차 $\delta\boldsymbol{\theta}$ 와 관측된 오차 $\hat{\delta\boldsymbol{\theta}}$ 로 표현하고 싶다. 두 가지 사실에서 출발한다.

**사실 1. 리셋해도 참 자세는 변하지 않는다.** $\mathbf{q}_t^+ = \mathbf{q}_t$ 이므로

$$\mathbf{q}^+\otimes\delta\mathbf{q}^+ = \mathbf{q}\otimes\delta\mathbf{q}$$

**사실 2. 관측된 오차 평균은 이미 공칭 상태에 주입되었다.**

$$\mathbf{q}^+ = \mathbf{q}\otimes\hat{\delta\mathbf{q}}$$

둘을 합치면

$$\delta\mathbf{q}^+ = (\mathbf{q}^+)^*\otimes\mathbf{q}\otimes\delta\mathbf{q} = (\mathbf{q}\otimes\hat{\delta\mathbf{q}})^*\otimes\mathbf{q}\otimes\delta\mathbf{q} = \hat{\delta\mathbf{q}}^*\otimes\delta\mathbf{q} = [\hat{\delta\mathbf{q}}^*]_L\,\delta\mathbf{q}$$

$\hat{\delta\mathbf{q}}^* \approx [1,\ -\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]$ 를 대입해 전개하면 스칼라 식 하나와 벡터 식 하나가 나오는데, 스칼라 쪽은 무한소끼리의 관계라 정보가 없고, 벡터 쪽이 답을 준다.

$$\delta\boldsymbol{\theta}^+ = -\hat{\delta\boldsymbol{\theta}} + \left(\mathbf{I}-\left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times\right)\delta\boldsymbol{\theta} + O(\|\delta\boldsymbol{\theta}\|^2)$$

여기서 $\hat{\delta\boldsymbol{\theta}}^+ = 0$ 임을 보일 수 있는데, 이는 리셋 연산에서 우리가 기대하는 바로 그 결과다. 자코비안은 그냥 읽어내면 된다.

$$\boxed{\frac{\partial\delta\boldsymbol{\theta}^+}{\partial\delta\boldsymbol{\theta}} = \mathbf{I} - \left[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}\right]_\times}$$

---

## 4. ESKF 전체 알고리즘 정리

지금까지의 내용을 의사코드로 모으면 이렇다.

```
초기화:
  x  ← 초기 공칭 상태 (q = [1,0,0,0], b = 0, ...)
  P  ← 초기 공분산
  δx ← 0

반복:
  ┌─ IMU 측정 도착 (고주파, 예: 200Hz) ──────────────┐
  │  [예측]                                           │
  │  1. 공칭 상태 적분   (5장 4.1절)                  │
  │       p ← p + vΔt + ½(R(a_m-a_b)+g)Δt²            │
  │       v ← v + (R(a_m-a_b)+g)Δt                    │
  │       q ← q ⊗ Exp((ω_m-ω_b)Δt)                    │
  │  2. 공분산 전파      (5장 4.3절)                  │
  │       P ← Fx P Fxᵀ + Fi Qi Fiᵀ                    │
  │     ※ δx 평균 예측은 항상 0이므로 생략 가능       │
  │     ※ 공분산 전파는 절대 생략 금지!               │
  └───────────────────────────────────────────────────┘

  ┌─ GPS/비전 측정 도착 (저주파, 예: 5Hz) ───────────┐
  │  [보정]                                           │
  │  3. 자코비안        H = Hx · X_δx    (6.1절)      │
  │  4. 칼만 이득       K = P Hᵀ (H P Hᵀ + V)⁻¹       │
  │  5. 오차 관측       δx̂ = K(y - h(x))              │
  │  6. 공분산 갱신     P ← (I-KH)P  (Joseph 권장)    │
  │  [주입]                                           │
  │  7. x ← x ⊕ δx̂       (6.2절)                      │
  │       특히 q ← q ⊗ Exp(δθ̂)                        │
  │  [리셋]                                           │
  │  8. δx̂ ← 0                                        │
  │  9. P ← G P Gᵀ       (6.3절, 보통 G=I로 생략)     │
  └───────────────────────────────────────────────────┘
```

> [!warning] 구현할 때 가장 흔한 실수 세 가지
> 1. **공분산 예측을 빼먹는다.** 예측 단계에서 $\mathbf{P}$ 가 커지지 않으면 필터가 IMU를 과신해서 보정을 무시하게 된다.
> 2. **리셋을 빼먹는다.** 같은 오차를 반복 적용해서 발산한다.
> 3. **쿼터니언 정규화를 안 한다.** 수치 오차로 $\|\mathbf{q}\|$ 가 1에서 벗어나므로, 주입 후 반드시 정규화한다.

---

## 정리

> [!abstract] 이 장의 결론
> - 보정은 **관측 → 주입 → 리셋** 세 단계다.
> - 측정 자코비안은 $\mathbf{H} = \mathbf{H}_x\,\mathbf{X}_{\delta\mathbf{x}}$ 로 분리한다. $\mathbf{H}_x$ 는 센서별, $\mathbf{X}_{\delta\mathbf{x}}$ 는 ESKF 공용이다.
> - $\mathbf{X}_{\delta\mathbf{x}}$ 의 쿼터니언 블록 $\mathbf{Q}_{\delta\boldsymbol{\theta}}$ 만 $4\times3$ 이고 나머지는 단위행렬이다.
> - 주입은 위치·속도·바이어스·중력은 덧셈, **자세만 쿼터니언 곱**이다.
> - 리셋의 자코비안 $\mathbf{G}$ 는 정확히는 $\mathbf{I}-[\tfrac{1}{2}\hat{\delta\boldsymbol{\theta}}]_\times$ 지만, **대부분의 구현은 $\mathbf{I}$ 로 근사**한다.
> - 공분산 갱신은 **Joseph 형태**를 쓰는 것이 안전하다.

---

## 관련 노트

- [[자코비안과 공분산 전파]] — 칼만 이득과 공분산의 의미
- [[왜 오차상태를 쓰는가]] — 주입·리셋이 필요한 근본 이유
- [[Chapter 05 - IMU 기반 오차상태 운동학]] — 이전 장
- [[Chapter 07 - 전역 각오차를 쓰는 ESKF]] — 다음 장
- [[확장 칼만 필터, Extended Kalman Filter, EKF]], [[Linear Kalman Filter]]
