---
title: "Chapter 5 — IMU 기반 오차상태 운동학 (Error-state kinematics for IMU-driven systems)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 5
tags: [ESKF, IMU, 칼만필터, 오차상태, 운동학, 바이어스, 자코비안]
---

# Chapter 5 · IMU 기반 오차상태 운동학

> [!abstract] 이 장을 한 문장으로
> 드디어 **ESKF 본체**다. 상태를 **참(true)·공칭(nominal)·오차(error)** 세 가지로 나누는 발상을 소개하고, IMU 측정치로부터 각각의 운동학 방정식을 유도한 뒤, 이를 이산시간으로 옮겨 **실제 코드에 옮길 수 있는 예측(prediction) 식**과 **자코비안 행렬 $\mathbf{F}_x$, $\mathbf{F}_i$** 를 완성한다.

---

## 1. 동기 — 왜 ESKF인가

### 1.1 풀고 싶은 문제

가속도계와 자이로스코프의 측정값을 적분해서 위치와 자세를 구하고 싶다. 이것을 **추측 항법(dead-reckoning)** 이라 한다. 문제는 하나다.

> [!warning] 적분은 표류한다
> IMU 측정치에는 잡음과 바이어스가 섞여 있다. 그것을 적분하면 오차가 **시간에 따라 누적**된다. 가속도의 작은 바이어스는 속도에서 시간에 비례해, 위치에서는 시간의 제곱에 비례해 커진다. 몇 초만 지나도 위치가 수 미터씩 어긋난다.

해법은 **절대 위치를 알려 주는 다른 센서(GPS, 비전 등)와 융합**하는 것이다. 그 융합 도구가 바로 **오차상태 칼만 필터(Error-State Kalman Filter, ESKF)** 다.

### 1.2 ESKF의 네 가지 강점

논문이 Madyastha et al. (2011)을 인용하며 꼽는 장점들이다.

> [!important] ESKF가 좋은 이유
> **1. 자세 오차의 표현이 최소(minimal)다.**
> 오차상태의 매개변수 개수가 자유도와 정확히 같다(3개). 과매개변수화로 인한 **공분산 행렬의 특이성 위험이 사라진다.** ([[Chapter 04 - 섭동 미분 적분|4장]] 3.2절에서 본 $3\times4$ 자코비안 문제의 해결책이다.)
>
> **2. 오차 시스템은 항상 원점 근처에서 동작한다.**
> 따라서 매개변수 특이점이나 짐벌 락 같은 문제에서 멀리 떨어져 있고, **선형화의 타당성이 항상 보장된다.**
>
> **3. 오차가 항상 작으므로 2차 항을 전부 무시할 수 있다.**
> 자코비안 계산이 **매우 쉽고 빨라진다.** 어떤 자코비안은 상수이거나 이미 가지고 있는 상태값과 같아진다.
>
> **4. 오차의 동역학이 느리다.**
> 큰 신호의 동역학은 전부 공칭 상태가 흡수했기 때문이다. 따라서 **보정(correction)을 예측(prediction)보다 낮은 주기로** 수행해도 된다. IMU는 200Hz로 돌리고 GPS는 5Hz로 받아도 괜찮다는 뜻이다.

---

## 2. ESKF의 작동 원리

### 2.1 세 가지 상태

ESKF의 핵심 발상은 하나의 상태를 **두 조각으로 쪼개는 것**이다.

| 상태 | 기호 | 성격 | 역할 |
|---|---|---|---|
| **참 상태(true)** | $\mathbf{x}_t$ | 우리가 알고 싶은 진짜 값 | 관측 불가 |
| **공칭 상태(nominal)** | $\mathbf{x}$ | **큰 신호** | IMU로 비선형 적분 |
| **오차 상태(error)** | $\delta\mathbf{x}$ | **작은 신호** | 칼만 필터로 추정 |

이들의 관계는

$$\mathbf{x}_t = \mathbf{x}\oplus\delta\mathbf{x}$$

여기서 $\oplus$ 는 적절한 합성이다. 위치·속도 같은 벡터는 평범한 덧셈, 쿼터니언은 곱셈이다.

> [!important] 왜 쪼개는가
> **공칭 상태는 크지만 비선형이어도 괜찮다.** 그냥 수치 적분하면 되니까.
> **오차 상태는 작으므로 선형으로 다룰 수 있다.** 선형-가우시안 필터링에 딱 맞는다.
>
> 즉 **"큰 것은 비선형으로 적분하고, 작은 것만 선형 필터로 다룬다"** 는 분업이다. 이 분업 덕분에 EKF가 겪는 선형화 오차 문제가 크게 줄어든다.

### 2.2 전체 흐름

```
[고주파, 예: 200Hz]
  IMU 측정 um ──→ 공칭 상태 x 적분 (잡음 무시)
                     ↓ (오차가 쌓임)
                  오차 상태 δx 예측 (잡음 포함)
                     ↓  공분산 P 증가
[저주파, 예: 5Hz]
  GPS/비전 도착 ──→ 1. 오차 상태 관측 (칼만 보정)
                    2. 오차를 공칭 상태에 주입
                    3. 오차를 0으로 리셋, P 갱신
                     ↓
                  처음으로 (무한 반복)
```

논문의 설명을 그대로 옮기면 이렇다. 고주파 IMU 데이터 $\mathbf{u}_m$ 은 공칭 상태 $\mathbf{x}$ 로 적분된다. 이 공칭 상태는 **잡음 항 $\mathbf{w}$ 와 모델의 불완전성을 고려하지 않으므로 오차가 누적**된다. 그 오차들이 오차 상태 $\delta\mathbf{x}$ 에 모이고, ESKF가 이번에는 **모든 잡음과 섭동을 포함해서** 이를 추정한다.

오차 상태는 작은 신호이므로 그 전개 함수는 **(시변) 선형 동역학 시스템**으로 정확히 기술되며, 그 동역학·제어·측정 행렬은 공칭 상태의 값들로부터 계산된다.

공칭 상태 적분과 병행하여 ESKF는 오차 상태의 가우시안 추정치를 **예측만** 한다. 지금은 오차를 보정할 다른 측정이 없기 때문이다. 필터 보정은 **IMU가 아닌 정보(GPS, 비전 등)가 도착할 때** 수행되며, 이것이 오차를 관측 가능하게 만든다. 보정 후 오차 상태의 평균은 공칭 상태에 **주입(inject)** 되고, 그다음 **0으로 리셋**된다. 오차 상태의 공분산 행렬은 이 리셋을 반영하도록 갱신된다.

---

## 3. 연속시간 시스템 운동학

### 3.1 변수 정의표

논문의 Table 3이다. ESKF에 등장하는 모든 변수를 한눈에 볼 수 있다.

| 물리량 | 참 | 공칭 | 오차 | 합성 | 측정 | 잡음 |
|---|---|---|---|---|---|---|
| 전체 상태 | $\mathbf{x}_t$ | $\mathbf{x}$ | $\delta\mathbf{x}$ | $\mathbf{x}_t = \mathbf{x}\oplus\delta\mathbf{x}$ | | |
| 위치 | $\mathbf{p}_t$ | $\mathbf{p}$ | $\delta\mathbf{p}$ | $\mathbf{p}_t = \mathbf{p}+\delta\mathbf{p}$ | | |
| 속도 | $\mathbf{v}_t$ | $\mathbf{v}$ | $\delta\mathbf{v}$ | $\mathbf{v}_t = \mathbf{v}+\delta\mathbf{v}$ | | |
| 쿼터니언 | $\mathbf{q}_t$ | $\mathbf{q}$ | $\delta\mathbf{q}$ | $\mathbf{q}_t = \mathbf{q}\otimes\delta\mathbf{q}$ | | |
| 회전행렬 | $\mathbf{R}_t$ | $\mathbf{R}$ | $\delta\mathbf{R}$ | $\mathbf{R}_t = \mathbf{R}\,\delta\mathbf{R}$ | | |
| 각도 벡터 | | | $\delta\boldsymbol{\theta}$ | $\delta\mathbf{q}=e^{\delta\boldsymbol{\theta}/2}$, $\delta\mathbf{R}=e^{[\delta\boldsymbol{\theta}]_\times}$ | | |
| 가속도계 바이어스 | $\mathbf{a}_{bt}$ | $\mathbf{a}_b$ | $\delta\mathbf{a}_b$ | $\mathbf{a}_{bt}=\mathbf{a}_b+\delta\mathbf{a}_b$ | | $\mathbf{a}_w$ |
| 자이로 바이어스 | $\boldsymbol{\omega}_{bt}$ | $\boldsymbol{\omega}_b$ | $\delta\boldsymbol{\omega}_b$ | $\boldsymbol{\omega}_{bt}=\boldsymbol{\omega}_b+\delta\boldsymbol{\omega}_b$ | | $\boldsymbol{\omega}_w$ |
| 중력 벡터 | $\mathbf{g}_t$ | $\mathbf{g}$ | $\delta\mathbf{g}$ | $\mathbf{g}_t=\mathbf{g}+\delta\mathbf{g}$ | | |
| 가속도 | $\mathbf{a}_t$ | | | | $\mathbf{a}_m$ | $\mathbf{a}_n$ |
| 각속도 | $\boldsymbol{\omega}_t$ | | | | $\boldsymbol{\omega}_m$ | $\boldsymbol{\omega}_n$ |

> [!note] 두 가지 중요한 규약 결정
> **1. 각속도 $\boldsymbol{\omega}$ 는 공칭 쿼터니언에 대해 국소적으로 정의한다.**
> 자이로가 **body 기준 각속도**를 주므로, 측정값 $\boldsymbol{\omega}_m$ 을 그대로 쓸 수 있다.
>
> **2. 각오차 $\delta\boldsymbol{\theta}$ 도 공칭 자세에 대해 국소적으로 정의한다.**
> 이것이 반드시 최적은 아니지만 **대부분의 IMU 적분 연구가 택하는 고전적 방식**이다. Li와 Mourikis (2012)는 **전역으로 정의한 각오차가 더 나은 성질**을 가진다는 증거를 제시했고, 그 방식은 [[Chapter 07 - 전역 각오차를 쓰는 ESKF|7장]]에서 다룬다. 하지만 이 문서의 전개·예제·알고리즘 대부분은 **국소 각오차** 기준이다.

### 3.2 참 상태 운동학

참 상태의 운동학 방정식은 물리 그 자체다.

$$\dot{\mathbf{p}}_t = \mathbf{v}_t$$
$$\dot{\mathbf{v}}_t = \mathbf{a}_t$$
$$\dot{\mathbf{q}}_t = \tfrac{1}{2}\mathbf{q}_t\otimes\boldsymbol{\omega}_t$$
$$\dot{\mathbf{a}}_{bt} = \mathbf{a}_w$$
$$\dot{\boldsymbol{\omega}}_{bt} = \boldsymbol{\omega}_w$$
$$\dot{\mathbf{g}}_t = 0$$

위치의 미분은 속도, 속도의 미분은 가속도. 자세의 미분은 [[Chapter 04 - 섭동 미분 적분|4장]] 5.1절에서 유도한 그 식이다. 바이어스는 **랜덤 워크(random walk)** 로 모델링하고, 중력은 상수다.

### 3.3 IMU 측정 모델

IMU는 참값을 그대로 주지 않는다. **바이어스와 잡음이 섞여** 나온다.

$$\mathbf{a}_m = \mathbf{R}_t^\top(\mathbf{a}_t - \mathbf{g}_t) + \mathbf{a}_{bt} + \mathbf{a}_n$$
$$\boldsymbol{\omega}_m = \boldsymbol{\omega}_t + \boldsymbol{\omega}_{bt} + \boldsymbol{\omega}_n$$

> [!important] 가속도계는 중력을 뺀 값을 body 좌표계로 측정한다
> 첫 식의 구조를 잘 보자. $\mathbf{R}_t^\top$ 은 **world → body 변환**이고, $(\mathbf{a}_t - \mathbf{g}_t)$ 는 **가속도에서 중력을 뺀 것**이다.
>
> 가만히 놓인 IMU를 생각해 보자. $\mathbf{a}_t = 0$ 이지만 $\mathbf{g}_t = (0,0,-9.8)$ 이므로 $\mathbf{a}_m \approx \mathbf{R}_t^\top(0,0,+9.8)$ 이 된다. **정지한 가속도계는 위쪽으로 1g를 읽는다.** 실제로 그렇다. 이것이 자유낙하 상태에서 가속도계가 0을 읽는 이유이기도 하다. [[IMU 센서 모델과 바이어스]]에 더 자세히 정리했다.

측정 방정식을 뒤집어 참값을 분리하면

$$\mathbf{a}_t = \mathbf{R}_t(\mathbf{a}_m - \mathbf{a}_{bt} - \mathbf{a}_n) + \mathbf{g}_t$$
$$\boldsymbol{\omega}_t = \boldsymbol{\omega}_m - \boldsymbol{\omega}_{bt} - \boldsymbol{\omega}_n$$

이를 대입하면 **최종 참 상태 운동학**이 나온다.

$$\boxed{\begin{aligned}
\dot{\mathbf{p}}_t &= \mathbf{v}_t \\
\dot{\mathbf{v}}_t &= \mathbf{R}_t(\mathbf{a}_m - \mathbf{a}_{bt} - \mathbf{a}_n) + \mathbf{g}_t \\
\dot{\mathbf{q}}_t &= \tfrac{1}{2}\mathbf{q}_t\otimes(\boldsymbol{\omega}_m - \boldsymbol{\omega}_{bt} - \boldsymbol{\omega}_n) \\
\dot{\mathbf{a}}_{bt} &= \mathbf{a}_w, \qquad \dot{\boldsymbol{\omega}}_{bt} = \boldsymbol{\omega}_w, \qquad \dot{\mathbf{g}}_t = 0
\end{aligned}}$$

> [!note] 중력을 상태에 넣는 이유
> 이 정식화에서 특이한 점은 **중력 벡터 $\mathbf{g}_t$ 를 필터가 추정한다**는 것이다. 보통은 $\mathbf{g}=(0,0,-9.8)$ 로 고정하는데 말이다.
>
> 이유는 **선형성을 개선하기 위해서**다. 시스템은 임의의 알려진 초기 자세 $\mathbf{q}_t(0)=\mathbf{q}_0$ 에서 시작하는데, 이것이 일반적으로 수평면에 있지 않으므로 초기 중력 벡터를 모른다. 여기서 보통 $\mathbf{q}_0=(1,0,0,0)$, 즉 $\mathbf{R}_0=\mathbf{I}$ 로 두면, **초기 자세의 불확실성이 전부 중력 방향의 불확실성으로 옮겨간다.**
>
> 그러면 속도 방정식이 $\mathbf{g}$ 에 대해 **선형**이 되고, 불확실성을 전부 $\mathbf{g}$ 가 짊어지며, $\mathbf{q}$ 는 불확실성 없이 출발한다. 중력이 추정되고 나면 수평면을 복원할 수 있고, 원한다면 전체 상태와 궤적을 수평 기준으로 재정렬할 수 있다.
>
> 물론 이는 선택 사항이다. 중력 관련 식을 전부 빼고 $\mathbf{g}=(0,0,-9.8xx)$ 로 두는 고전적 접근을 택해도 된다. 그 경우 초기 자세 $\mathbf{q}_0$ 가 불확실해진다.

### 3.4 공칭 상태 운동학

**잡음과 섭동을 전부 뺀** 모델이다. 실제로 적분하는 것이 이것이다.

$$\boxed{\begin{aligned}
\dot{\mathbf{p}} &= \mathbf{v} \\
\dot{\mathbf{v}} &= \mathbf{R}(\mathbf{a}_m - \mathbf{a}_b) + \mathbf{g} \\
\dot{\mathbf{q}} &= \tfrac{1}{2}\mathbf{q}\otimes(\boldsymbol{\omega}_m - \boldsymbol{\omega}_b) \\
\dot{\mathbf{a}}_b &= 0, \qquad \dot{\boldsymbol{\omega}}_b = 0, \qquad \dot{\mathbf{g}} = 0
\end{aligned}}$$

참 상태 식에서 $\mathbf{a}_n, \boldsymbol{\omega}_n, \mathbf{a}_w, \boldsymbol{\omega}_w$ 를 전부 0으로 놓은 것이다. 단순하다.

### 3.5 오차 상태 운동학 — 이 장의 핵심 결과

목표는 **오차 상태의 선형화된 동역학**을 구하는 것이다. 각 상태 방정식에 대해 합성 관계를 대입하고 오차에 대해 풀면서 **2차 이상의 무한소를 전부 버린다.**

결과는 이렇다.

$$\boxed{\begin{aligned}
\dot{\delta\mathbf{p}} &= \delta\mathbf{v} \\
\dot{\delta\mathbf{v}} &= -\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\,\delta\boldsymbol{\theta} - \mathbf{R}\,\delta\mathbf{a}_b + \delta\mathbf{g} - \mathbf{R}\,\mathbf{a}_n \\
\dot{\delta\boldsymbol{\theta}} &= -[\boldsymbol{\omega}_m - \boldsymbol{\omega}_b]_\times\,\delta\boldsymbol{\theta} - \delta\boldsymbol{\omega}_b - \boldsymbol{\omega}_n \\
\dot{\delta\mathbf{a}}_b &= \mathbf{a}_w, \qquad \dot{\delta\boldsymbol{\omega}}_b = \boldsymbol{\omega}_w, \qquad \dot{\delta\mathbf{g}} = 0
\end{aligned}}$$

> [!important] 이 식이 왜 대단한가
> **모든 항이 오차에 대해 1차(선형)다.** $\delta\mathbf{v}, \delta\boldsymbol{\theta}, \delta\mathbf{a}_b, \delta\mathbf{g}$ 가 전부 곱해지지 않고 따로 더해져 있다. 계수는 전부 공칭 상태($\mathbf{R}$, $\mathbf{a}_m-\mathbf{a}_b$ 등)로 이루어져 있는데, 이 값들은 우리가 이미 알고 있다.
>
> 즉 이것은 **시변 선형 시스템**이다. 칼만 필터가 다룰 수 있는 정확히 그 형태다.

#### 쉬운 네 개와 어려운 두 개

위치·두 바이어스·중력의 오차 방정식(1, 4, 5, 6번째)은 **선형 방정식에서 유도되므로 자명하다.** 예를 들어 위치를 보자. 참·공칭 위치 방정식 $\dot{\mathbf{p}}_t = \mathbf{v}_t$, $\dot{\mathbf{p}} = \mathbf{v}$ 와 합성 $\mathbf{p}_t = \mathbf{p}+\delta\mathbf{p}$ 를 쓰면

$$\dot{\delta\mathbf{p}} = \dot{\mathbf{p}}_t - \dot{\mathbf{p}} = \mathbf{v}_t - \mathbf{v} = \delta\mathbf{v}$$

끝이다. 반면 **속도와 자세**의 오차 방정식은 비선형 방정식을 다뤄야 해서 손이 많이 간다.

#### 속도 오차 유도의 핵심

두 가지 재료를 쓴다. 하나는 $\mathbf{R}_t$ 의 작은 신호 근사([[Chapter 04 - 섭동 미분 적분|4장]] 4.1절)

$$\mathbf{R}_t = \mathbf{R}(\mathbf{I} + [\delta\boldsymbol{\theta}]_\times) + O(\|\delta\boldsymbol{\theta}\|^2)$$

다른 하나는 body 좌표계 가속도를 큰 신호와 작은 신호로 나눈 것이다.

$$\mathbf{a}_B \triangleq \mathbf{a}_m - \mathbf{a}_b, \qquad \delta\mathbf{a}_B \triangleq -\delta\mathbf{a}_b - \mathbf{a}_n$$

이제 참 가속도를 큰 신호와 작은 신호의 합성으로 쓸 수 있다.

$$\mathbf{a}_t = \mathbf{R}_t(\mathbf{a}_B+\delta\mathbf{a}_B) + \mathbf{g} + \delta\mathbf{g}$$

핵심 요령은 $\dot{\mathbf{v}}_t$ 를 **두 가지 방식으로 전개해 비교**하는 것이다. 왼쪽은 오차 합성 정의로, 오른쪽은 참 운동학으로 계산한다. ($O(\|\delta\boldsymbol{\theta}\|^2)$ 항은 무시한다.)

$$\underbrace{\mathbf{R}\mathbf{a}_B+\mathbf{g}+\dot{\delta\mathbf{v}}}_{\text{좌: }\dot{\mathbf{v}}+\dot{\delta\mathbf{v}}} = \underbrace{\mathbf{R}\mathbf{a}_B + \mathbf{R}\delta\mathbf{a}_B + \mathbf{R}[\delta\boldsymbol{\theta}]_\times\mathbf{a}_B + \mathbf{R}[\delta\boldsymbol{\theta}]_\times\delta\mathbf{a}_B + \mathbf{g}+\delta\mathbf{g}}_{\text{우: }\mathbf{R}(\mathbf{I}+[\delta\boldsymbol{\theta}]_\times)(\mathbf{a}_B+\delta\mathbf{a}_B)+\mathbf{g}+\delta\mathbf{g}}$$

양변에서 공통항 $\mathbf{R}\mathbf{a}_B+\mathbf{g}$ 를 지우면

$$\dot{\delta\mathbf{v}} = \mathbf{R}\left(\delta\mathbf{a}_B + [\delta\boldsymbol{\theta}]_\times\mathbf{a}_B\right) + \mathbf{R}[\delta\boldsymbol{\theta}]_\times\delta\mathbf{a}_B + \delta\mathbf{g}$$

**2차 항** $\mathbf{R}[\delta\boldsymbol{\theta}]_\times\delta\mathbf{a}_B$ 를 버리고, $[\mathbf{a}]_\times\mathbf{b} = -[\mathbf{b}]_\times\mathbf{a}$ 로 외적을 재배치하면

$$\dot{\delta\mathbf{v}} = \mathbf{R}\left(\delta\mathbf{a}_B - [\mathbf{a}_B]_\times\delta\boldsymbol{\theta}\right) + \delta\mathbf{g}$$

정의를 되돌리면 최종 결과가 나온다.

$$\dot{\delta\mathbf{v}} = -\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\delta\boldsymbol{\theta} - \mathbf{R}\delta\mathbf{a}_b + \delta\mathbf{g} - \mathbf{R}\mathbf{a}_n$$

> [!note] $-\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times$ 항의 물리적 의미
> **자세가 조금 틀어져 있으면 중력 보상이 어긋나고, 그것이 속도 오차로 이어진다**는 뜻이다. 자세 오차 $\delta\boldsymbol{\theta}$ 가 속도 오차 $\delta\mathbf{v}$ 로 흘러 들어가는 통로다.
>
> 이 결합이 있기 때문에 **GPS로 위치만 관측해도 자세와 바이어스가 관측 가능해진다.** 위치 오차 → 속도 오차 → 자세 오차로 정보가 거슬러 올라가기 때문이다. ESKF가 작동하는 근본 원리다.

#### 등방성 잡음 가정 — $\mathbf{R}\mathbf{a}_n$ 에서 $\mathbf{R}$ 을 지우기

식을 더 깔끔하게 만들 수 있다. 가속도계 잡음이 **백색이고, 상관이 없고, 등방적(isotropic)** 이라고 가정하는 경우가 많다.

$$\mathbb{E}[\mathbf{a}_n] = 0, \qquad \mathbb{E}[\mathbf{a}_n\mathbf{a}_n^\top] = \sigma_a^2\mathbf{I}$$

즉 **공분산 타원체가 원점 중심의 완전한 구**라는 뜻이고, 따라서 그 평균과 공분산이 **회전에 대해 불변**이다. 증명은 한 줄이다.

$$\mathbb{E}[\mathbf{R}\mathbf{a}_n] = \mathbf{R}\,\mathbb{E}[\mathbf{a}_n] = 0$$
$$\mathbb{E}[(\mathbf{R}\mathbf{a}_n)(\mathbf{R}\mathbf{a}_n)^\top] = \mathbf{R}\,\mathbb{E}[\mathbf{a}_n\mathbf{a}_n^\top]\,\mathbf{R}^\top = \mathbf{R}(\sigma_a^2\mathbf{I})\mathbf{R}^\top = \sigma_a^2\mathbf{I}$$

**회전시켜도 통계적으로 완전히 같은 확률변수다.** 그러므로 아무 손해 없이 잡음 벡터를 다시 정의할 수 있다.

$$\mathbf{a}_n \leftarrow \mathbf{R}\,\mathbf{a}_n$$

그 결과

$$\boxed{\dot{\delta\mathbf{v}} = -\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\delta\boldsymbol{\theta} - \mathbf{R}\,\delta\mathbf{a}_b + \delta\mathbf{g} - \mathbf{a}_n}$$

> [!important] 이것이 $\mathbf{Q}_i$ 에 $\mathbf{R}$ 이 없는 이유다
> 4.3절의 섭동 행렬 $\mathbf{F}_i$ 와 잡음 공분산 $\mathbf{Q}_i$ 를 보면 **회전행렬이 전혀 등장하지 않는다.** 등방성 가정 덕분에 $\mathbf{R}$ 을 흡수해 버렸기 때문이다.
>
> [[Chapter 07 - 전역 각오차를 쓰는 ESKF|7장]]에서 각오차 정의를 바꿔도 $\mathbf{F}_i$, $\mathbf{Q}_i$ 가 그대로인 것도 같은 이유다.

> [!warning] 이 가정이 깨지는 경우
> 논문은 각주로 경고한다. **세 축의 가속도계가 서로 동일하지 않은 경우에는 이 가정을 쓸 수 없다.** 축마다 잡음 특성이 다르면 공분산이 $\sigma^2\mathbf{I}$ 형태가 아니라 대각 성분이 다른 행렬이 되고, 그러면 $\mathbf{R}\boldsymbol{\Sigma}\mathbf{R}^\top \neq \boldsymbol{\Sigma}$ 가 된다. 이때는 $\mathbf{R}$ 을 명시적으로 끌고 다녀야 한다.

#### 자세 오차 유도의 핵심

같은 "두 가지 방식으로 전개하기" 요령을 쓴다. 각속도도 큰 신호와 작은 신호로 나눈다.

$$\boldsymbol{\omega} \triangleq \boldsymbol{\omega}_m-\boldsymbol{\omega}_b, \qquad \delta\boldsymbol{\omega} \triangleq -\delta\boldsymbol{\omega}_b-\boldsymbol{\omega}_n, \qquad \boldsymbol{\omega}_t = \boldsymbol{\omega}+\delta\boldsymbol{\omega}$$

$\dot{\mathbf{q}}_t$ 를 두 방식으로 계산한다. 왼쪽은 합성 $\mathbf{q}_t=\mathbf{q}\otimes\delta\mathbf{q}$ 를 미분한 것, 오른쪽은 참 운동학이다.

$$\underbrace{\dot{\mathbf{q}}\otimes\delta\mathbf{q} + \mathbf{q}\otimes\dot{\delta\mathbf{q}}}_{\text{좌}} = \underbrace{\tfrac{1}{2}\mathbf{q}\otimes\delta\mathbf{q}\otimes\boldsymbol{\omega}_t}_{\text{우}}$$

좌변의 $\dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}$ 를 대입하고 공통의 $\mathbf{q}$ 를 소거한 뒤 $\dot{\delta\mathbf{q}}$ 에 대해 정리하면

$$2\,\dot{\delta\mathbf{q}} = \delta\mathbf{q}\otimes\boldsymbol{\omega}_t - \boldsymbol{\omega}\otimes\delta\mathbf{q} = \left([\boldsymbol{\omega}_t]_R - [\boldsymbol{\omega}]_L\right)\delta\mathbf{q}$$

[[Chapter 01 - 쿼터니언의 정의와 성질|1장]] 3.3절의 좌·우 곱 행렬을 대입하면 그 차이가 아주 단순해진다.

$$[\boldsymbol{\omega}_t]_R-[\boldsymbol{\omega}]_L = \begin{bmatrix}0 & -\delta\boldsymbol{\omega}^\top \\ \delta\boldsymbol{\omega} & -[\boldsymbol{\omega}_t+\boldsymbol{\omega}]_\times\end{bmatrix} \approx \begin{bmatrix}0 & -\delta\boldsymbol{\omega}^\top \\ \delta\boldsymbol{\omega} & -[2\boldsymbol{\omega}+\delta\boldsymbol{\omega}]_\times\end{bmatrix}$$

$\delta\mathbf{q}\approx[1,\ \tfrac{1}{2}\delta\boldsymbol{\theta}]$ 를 넣고 전개하면 스칼라 식 하나와 벡터 식 하나가 나온다.

$$0 = \delta\boldsymbol{\omega}^\top\delta\boldsymbol{\theta} + O(\|\delta\|^2) \qquad \text{(무한소끼리의 관계, 정보 없음)}$$

$$\dot{\delta\boldsymbol{\theta}} = \delta\boldsymbol{\omega} - [\boldsymbol{\omega}]_\times\delta\boldsymbol{\theta} + O(\|\delta\|^2)$$

2차 항을 버리고 정의를 되돌리면

$$\boxed{\dot{\delta\boldsymbol{\theta}} = -[\boldsymbol{\omega}_m-\boldsymbol{\omega}_b]_\times\delta\boldsymbol{\theta} - \delta\boldsymbol{\omega}_b - \boldsymbol{\omega}_n}$$

> [!note] $-[\boldsymbol{\omega}]_\times\delta\boldsymbol{\theta}$ 항은 어디서 왔나
> **오차를 회전하는 좌표계(body)에서 재기 때문에** 생기는 항이다. 기준 자체가 돌아가고 있으므로 그만큼 보정이 필요하다. 원심력·코리올리 항이 회전 좌표계에서 나타나는 것과 같은 성격이다.
>
> [[Chapter 07 - 전역 각오차를 쓰는 ESKF|7장]]에서 오차를 전역 좌표계에 정의하면 **이 항이 사라진다.** 전역 좌표계는 회전하지 않기 때문이다.

---

## 4. 이산시간 시스템 운동학

실제 코드는 연속시간 미분방정식이 아니라 **한 스텝씩 갱신하는 이산 식**으로 짠다.

### 4.1 공칭 상태의 이산 갱신

$$\boxed{\begin{aligned}
\mathbf{p} &\leftarrow \mathbf{p} + \mathbf{v}\Delta t + \tfrac{1}{2}\left(\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)+\mathbf{g}\right)\Delta t^2 \\
\mathbf{v} &\leftarrow \mathbf{v} + \left(\mathbf{R}(\mathbf{a}_m-\mathbf{a}_b)+\mathbf{g}\right)\Delta t \\
\mathbf{q} &\leftarrow \mathbf{q}\otimes\mathbf{q}\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\} \\
\mathbf{a}_b &\leftarrow \mathbf{a}_b, \qquad \boldsymbol{\omega}_b \leftarrow \boldsymbol{\omega}_b, \qquad \mathbf{g} \leftarrow \mathbf{g}
\end{aligned}}$$

여기서 $\mathbf{q}\{\mathbf{v}\}$ 는 회전 벡터 $\mathbf{v}$ 에 대응하는 쿼터니언, 즉 $\mathrm{Exp}(\mathbf{v})$ 다.

> [!tip] 더 정밀한 적분이 필요하면
> 위 식은 가장 단순한 형태다. [[부록 A-E - 수치적분과 전이행렬|부록]]에 Runge-Kutta를 비롯한 더 정밀한 적분법이 정리되어 있다.

### 4.2 오차 상태의 이산 갱신

결정론적 부분은 평범하게 적분하고, 확률적 부분은 **랜덤 임펄스**로 나타난다.

$$\boxed{\begin{aligned}
\delta\mathbf{p} &\leftarrow \delta\mathbf{p} + \delta\mathbf{v}\Delta t \\
\delta\mathbf{v} &\leftarrow \delta\mathbf{v} + \left(-\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\delta\boldsymbol{\theta} - \mathbf{R}\delta\mathbf{a}_b + \delta\mathbf{g}\right)\Delta t + \mathbf{v}_i \\
\delta\boldsymbol{\theta} &\leftarrow \mathbf{R}^\top\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\}\,\delta\boldsymbol{\theta} - \delta\boldsymbol{\omega}_b\Delta t + \boldsymbol{\theta}_i \\
\delta\mathbf{a}_b &\leftarrow \delta\mathbf{a}_b + \mathbf{a}_i \\
\delta\boldsymbol{\omega}_b &\leftarrow \delta\boldsymbol{\omega}_b + \boldsymbol{\omega}_i \\
\delta\mathbf{g} &\leftarrow \delta\mathbf{g}
\end{aligned}}$$

$\mathbf{v}_i, \boldsymbol{\theta}_i, \mathbf{a}_i, \boldsymbol{\omega}_i$ 는 속도·자세·바이어스 추정치에 가해지는 **랜덤 임펄스**로, 백색 가우시안 과정으로 모델링된다. 평균은 0이고, 공분산 행렬은 연속시간 잡음의 공분산을 스텝 시간 $\Delta t$ 에 대해 적분해서 얻는다.

$$\mathbf{V}_i = \sigma_{\tilde{a}_n}^2\Delta t^2\,\mathbf{I} \quad [m^2/s^2]$$
$$\boldsymbol{\Theta}_i = \sigma_{\tilde{\omega}_n}^2\Delta t^2\,\mathbf{I} \quad [rad^2]$$
$$\mathbf{A}_i = \sigma_{a_w}^2\Delta t\,\mathbf{I} \quad [m^2/s^4]$$
$$\boldsymbol{\Omega}_i = \sigma_{\omega_w}^2\Delta t\,\mathbf{I} \quad [rad^2/s^2]$$

> [!important] 이 네 개의 $\sigma$ 가 여러분이 튜닝할 값이다
> - $\sigma_{\tilde{a}_n}\ [m/s^2]$ — 가속도계 잡음 밀도
> - $\sigma_{\tilde{\omega}_n}\ [rad/s]$ — 자이로 잡음 밀도
> - $\sigma_{a_w}\ [m/(s^2\sqrt{s})]$ — 가속도계 바이어스 랜덤 워크
> - $\sigma_{\omega_w}\ [rad/(s\sqrt{s})]$ — 자이로 바이어스 랜덤 워크
>
> 이 값들은 **IMU 데이터시트**에서 가져오거나 **실험적으로 측정**해서 정한다. 데이터시트에는 보통 "Noise Density"와 "Random Walk"라는 이름으로 적혀 있다. 실측하려면 **Allan 분산(Allan variance)** 분석을 쓴다.
>
> $\Delta t$ 의 차수에 주목하자. **측정 잡음은 $\Delta t^2$, 바이어스 랜덤 워크는 $\Delta t$** 다. 이 차이가 중요하다. 자세한 유도는 [[부록 A-E - 수치적분과 전이행렬|부록 E]]에 있다.

### 4.3 오차 상태 자코비안과 섭동 행렬

이제 앞의 식들을 **행렬 하나로** 묶는다. 벡터들을 다음과 같이 정의한다.

$$\mathbf{x} = \begin{bmatrix}\mathbf{p}\\ \mathbf{v}\\ \mathbf{q}\\ \mathbf{a}_b\\ \boldsymbol{\omega}_b\\ \mathbf{g}\end{bmatrix}, \quad
\delta\mathbf{x} = \begin{bmatrix}\delta\mathbf{p}\\ \delta\mathbf{v}\\ \delta\boldsymbol{\theta}\\ \delta\mathbf{a}_b\\ \delta\boldsymbol{\omega}_b\\ \delta\mathbf{g}\end{bmatrix}, \quad
\mathbf{u}_m = \begin{bmatrix}\mathbf{a}_m\\ \boldsymbol{\omega}_m\end{bmatrix}, \quad
\mathbf{i} = \begin{bmatrix}\mathbf{v}_i\\ \boldsymbol{\theta}_i\\ \mathbf{a}_i\\ \boldsymbol{\omega}_i\end{bmatrix}$$

> [!note] 상태는 19차원, 오차 상태는 18차원
> $\mathbf{x}$ 는 위치3 + 속도3 + **쿼터니언4** + 바이어스3 + 바이어스3 + 중력3 = **19**차원이다.
> $\delta\mathbf{x}$ 는 위치3 + 속도3 + **각오차3** + 바이어스3 + 바이어스3 + 중력3 = **18**차원이다.
>
> **차이가 정확히 1이다.** 쿼터니언의 과잉 매개변수 하나가 오차 상태에서 사라진 것이다. 이것이 ESKF의 존재 이유를 가장 명확하게 보여 주는 숫자다.

오차 상태 시스템은 이제

$$\delta\mathbf{x} \leftarrow f(\mathbf{x},\delta\mathbf{x},\mathbf{u}_m,\mathbf{i}) = \mathbf{F}_x(\mathbf{x},\mathbf{u}_m)\,\delta\mathbf{x} + \mathbf{F}_i\,\mathbf{i}$$

**ESKF 예측 방정식**은

$$\boxed{\begin{aligned}
\hat{\delta\mathbf{x}} &\leftarrow \mathbf{F}_x(\mathbf{x},\mathbf{u}_m)\,\hat{\delta\mathbf{x}} \\
\mathbf{P} &\leftarrow \mathbf{F}_x\,\mathbf{P}\,\mathbf{F}_x^\top + \mathbf{F}_i\,\mathbf{Q}_i\,\mathbf{F}_i^\top
\end{aligned}}$$

#### 전이 행렬 $\mathbf{F}_x$ (18×18)

$$\mathbf{F}_x = \begin{bmatrix}
\mathbf{I} & \mathbf{I}\Delta t & 0 & 0 & 0 & 0 \\
0 & \mathbf{I} & -\mathbf{R}[\mathbf{a}_m-\mathbf{a}_b]_\times\Delta t & -\mathbf{R}\Delta t & 0 & \mathbf{I}\Delta t \\
0 & 0 & \mathbf{R}^\top\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\} & 0 & -\mathbf{I}\Delta t & 0 \\
0 & 0 & 0 & \mathbf{I} & 0 & 0 \\
0 & 0 & 0 & 0 & \mathbf{I} & 0 \\
0 & 0 & 0 & 0 & 0 & \mathbf{I}
\end{bmatrix}$$

#### 섭동 행렬 $\mathbf{F}_i$ (18×12)와 잡음 공분산 $\mathbf{Q}_i$ (12×12)

$$\mathbf{F}_i = \begin{bmatrix}
0&0&0&0\\ \mathbf{I}&0&0&0\\ 0&\mathbf{I}&0&0\\ 0&0&\mathbf{I}&0\\ 0&0&0&\mathbf{I}\\ 0&0&0&0
\end{bmatrix}, \qquad
\mathbf{Q}_i = \begin{bmatrix}
\mathbf{V}_i&0&0&0\\ 0&\boldsymbol{\Theta}_i&0&0\\ 0&0&\mathbf{A}_i&0\\ 0&0&0&\boldsymbol{\Omega}_i
\end{bmatrix}$$

> [!tip] $\mathbf{F}_i$ 를 읽는 법
> $\mathbf{F}_i$ 는 그냥 **어느 잡음이 어느 상태에 들어가는지 표시하는 지도**다. 첫 행(위치)과 마지막 행(중력)이 0인 것은 **위치와 중력에는 잡음이 직접 들어가지 않는다**는 뜻이다. 위치는 속도를 통해 간접적으로만 영향을 받고, 중력은 상수이므로 아예 잡음이 없다.

### 4.4 구현할 때의 세 가지 주의사항

> [!warning] 논문이 특별히 강조하는 것들
> **1. $\mathbf{F}_x$ 는 여러 방법으로 근사할 수 있다.**
> 여기 보인 것은 **가장 단순한 오일러 형태**다. 더 정밀한 형태는 [[부록 A-E - 수치적분과 전이행렬|부록 B~D]]를 참고하라.
>
> **2. 오차 평균 예측 식은 코드에서 건너뛰어도 된다.**
> 오차의 평균이 0으로 초기화되므로, $\hat{\delta\mathbf{x}} \leftarrow \mathbf{F}_x\hat{\delta\mathbf{x}}$ 는 **항상 0을 돌려준다.** 계산할 필요가 없다. 다만 논문 저자는 **그 줄을 쓰되 주석 처리해 두라**고 권한다. 빠뜨린 게 없음을 스스로 확인하기 위해서다.
>
> **3. 공분산 예측 식은 절대로 건너뛰면 안 된다!**
> $\mathbf{F}_i\mathbf{Q}_i\mathbf{F}_i^\top$ 항은 0이 아니므로 **공분산은 계속 커진다.** 예측 단계라면 당연히 그래야 한다. 시간이 갈수록 불확실해지는 것이 추측 항법의 본질이다.

---

## 정리

> [!abstract] 이 장의 결론
> - 상태를 **공칭(큰 신호, 비선형 적분) + 오차(작은 신호, 선형 필터)** 로 분리한다.
> - 참 상태 → IMU 측정 모델 대입 → 공칭 상태(잡음 제거) → 오차 상태(선형화)의 순서로 유도한다.
> - 오차 상태 운동학은 **완전히 선형**이며, 계수는 전부 공칭 상태에서 나온다.
> - 상태는 19차원, **오차 상태는 18차원**. 차이 1이 쿼터니언의 과잉 매개변수다.
> - 예측 단계는 **공칭 상태 적분 + 공분산 전파** 두 가지다.
> - 튜닝 파라미터는 IMU의 **잡음 밀도 2개 + 바이어스 랜덤 워크 2개**.

> [!note] 다음은 보정이다
> 예측만으로는 공분산이 무한정 커진다. [[Chapter 06 - IMU와 보조센서 융합|6장]]에서 GPS·비전 데이터로 **보정**하는 방법을 다룬다.

---

## 관련 노트

- [[왜 오차상태를 쓰는가]] — ESKF의 근본 동기
- [[IMU 센서 모델과 바이어스]] — 측정 모델과 노이즈 파라미터
- [[자코비안과 공분산 전파]] — $\mathbf{F}_x\mathbf{P}\mathbf{F}_x^\top$ 의 의미
- [[Chapter 04 - 섭동 미분 적분]] — 이전 장
- [[Chapter 06 - IMU와 보조센서 융합]] — 다음 장
- [[Linear Kalman Filter]], [[확장 칼만 필터, Extended Kalman Filter, EKF]]
