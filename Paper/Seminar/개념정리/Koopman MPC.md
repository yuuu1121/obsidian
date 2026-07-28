---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Koopman
  - Control
  - MPC
aliases:
  - Koopman MPC
  - Koopman NMPC
  - KMPC
keywords: MPC, quadratic program, convex, receding horizon, LQR
related notes: "[[Koopman Operator]], [[Koopman with Control Input]], [[EDMD]]"
dg-publish: false
---

# Koopman MPC (쿠프만 기반 모델예측제어)

> [!abstract] 한 줄 요약
> Koopman 리프팅으로 얻은 **선형** 모델을 MPC에 넣으면, 원래 비선형이라 비볼록이었을 최적제어 문제가 **볼록 이차계획법(QP)** 이 된다. → **전역 최적해 + 초기화 불필요 + 고차원에서도 실시간 계산 가능.** 이것이 Koopman이 로보틱스 제어에서 실제로 채택되는 가장 직접적 이유다.

---

## 1. 일반 최적제어 정식화

Koopman 모델을 얻고 나면 유한 예측구간(horizon) 위의 제약 최적화 문제를 푼다.

$$
\begin{aligned}
\underset{\{z_i\}_{i=0}^{N_h},\ \{u_i\}_{i=0}^{N_h}}{\text{minimize}} \quad & J\big(\{z_i\}_{i=0}^{N_h},\ \{u_i\}_{i=0}^{N_h}\big) \\[4pt]
\text{subject to} \quad & z_{i+1} = F_K(z_i, u_i) \\
& z_0 = \psi(x_t)
\end{aligned} \tag{논문 (12)}
$$

| 기호 | 의미 |
|:---|:---|
| $N_h$ | 예측구간 스텝 수 |
| $J$ | 이차(quadratic) 비용함수 |
| $\psi$ | 리프팅 딕셔너리 → [[Observable Function]] |
| $F_K$ | Koopman 기반 시스템 모델 |
| $z_i, u_i$ | horizon $i$ 번째 스텝의 리프팅 상태 / 입력 |
| $z_0 = \psi(x_t)$ | **현재 측정 상태를 리프팅한 것이 초기조건** |

목적함수는 목표 궤적으로부터의 이탈을 벌하고, 제약은 Koopman 모델과의 일관성을 강제한다.

---

## 2. 선형 실현 → 볼록 QP

$F_K$ 가 **선형**이면 ([[Koopman with Control Input|input-affine 형태]] $z^+ = Kz + Bu$), 문제 (12)는 다음 **이차계획법(QP)** 이 된다.

$$
\begin{aligned}
\underset{\{z_i\},\{u_i\}}{\text{minimize}} \quad & \sum_{i=0}^{N_h}\Big( z_i^\top G_i z_i + u_i^\top H_i u_i + g_i^\top z_i + h_i^\top u_i \Big) \\[4pt]
\text{subject to} \quad & z_{i+1} = K z_i + B u_i \\
& z_0 = \psi(x_t)
\end{aligned} \tag{논문 (13)}
$$

- $G_i \succeq 0$: 상태 가중 (추종 오차 벌점)
- $H_i \succ 0$: 입력 가중 (에너지/제어량 벌점)
- $g_i, h_i$: 선형항 (기준 궤적 offset 등에서 유래)

> [!success] 왜 이것이 결정적인가 — 논문의 핵심 주장
> **선형 Koopman 실현은 문제를 볼록(convex)으로 만든다.** 따라서
>
> 1. **유일한 전역 최적해(unique globally optimal solution)** 가 존재한다
> 2. **초기화(initialization)가 필요 없다** — 비볼록 NMPC의 고질적 문제인 "좋은 초기 추측" 문제가 사라진다
> 3. **고차원 모델에서도 효율적으로 계산**된다 [106][107][108]
>
> → **실시간 피드백 제어에 매우 적합**하다. 리프팅으로 차원이 커졌음에도 계산이 감당되는 이유가 바로 볼록성이다.

---

## 3. 비선형/쌍선형 실현의 트레이드오프

> [!warning] 볼록성을 잃는 경우
> 비선형 또는 쌍선형(bilinear) Koopman 실현은 (12)를 **비볼록**으로 만든다.
> - 풀기 **덜 효율적**
> - **국소 최적해(locally optimal)** 만 얻을 수 있음 [109]
>
> **그럼에도 쓰는 이유**: 때때로 비선형 실현이 **더 정확한 예측**을 준다. 그러면 이 트레이드오프가 정당화된다. 최근 쌍선형 실현 [43] 이 선형/비선형의 장점을 절충하는 방향으로 탐구되고 있다 [97].

| 실현 | 볼록성 | 최적해 | 표현력 | 계산 |
|:---|:---:|:---|:---|:---|
| **Linear** $Kz+Bu$ | ✅ | 전역 | 보통 | 빠름 (QP) |
| **Bilinear** $Kz+\sum u_jB_jz$ | ❌ | 국소 | 높음 | 중간 |
| **Nonlinear** | ❌ | 국소 | 최고 | 느림 |

---

## 4. 계보 (논문 III-C절)

| 단계 | 기여 |
|:---|:---|
| [104] | Koopman을 모델 기반 제어에 처음 도입 — 데이터 기반 제어기의 새 부류를 열었다 |
| [105] Korda & Mezić | **Koopman MPC** 정식화. linear predictor 개념. |
| [79] | **Koopman NMPC** — 비선형 확장 |
| [43][97] | **Bilinear** Koopman 실현 |

논문은 그 외 방향(공간 제약상 미전개)으로 adaptive control [84], robust control [46], RL(환경 동역학 근사 [67] / critic network [103])을 언급한다.

---

## 5. Active Learning — 제어가 데이터도 수집한다

Koopman의 **닫힌 형태 최소제곱 해**((6),(7))는 능동학습 제어기 설계로 직접 이어진다 [100].

### Fisher 정보 행렬

리프팅 공간에서의 상태가 정규분포를 따른다고 가정하고 ($z_{t+1} = Kz_t + Bu_t$ 가 평균), **Fisher 정보 행렬**을 근사한다.

$$
\mathcal{I} = \mathbb{E}\left[\frac{\partial \log p(z_{t+1}|K,z_k)}{\partial K}\ \frac{\partial \log p(z_{t+1}|K,z_k)}{\partial K}^\top\right] \tag{논문 (14)}
$$

평균 0, 분산 $\Sigma$ 인 정규분포에서 닫힌 형태가 나온다.

$$
\mathcal{I} = \frac{\partial z_{t+1}}{\partial K}^\top \Sigma^{-1} \frac{\partial z_{t+1}}{\partial K} \ \propto\ \mathrm{Var}[K]^{-1} \tag{논문 (15)}
$$

$\mathrm{Var}[K]^{-1}$ 는 근사 Koopman 연산자의 **사후 분산의 역**이다. Fisher 정보는 추정의 사후 불확실성에 대한 하한(**Cramér–Rao bound** [110][111])을 준다.

> [!important] 왜 유용한가
> Fisher 정보는 **미분 가능(differentiable)** 하고 **행동 가능(actionable)** 하다. 즉 **Fisher 정보를 직접 최대화하는 제어기를 최적화**할 수 있으며, 이는 곧 Koopman 연산자에 대한 최선의 사후 분산을 개선한다는 뜻이다.

### 능동학습 제어기

$$
\begin{aligned}
\underset{\{u_i\}_{i=0}^{N_h}}{\text{minimize}} \quad & \sum_{i=0}^{N_h-1}\Big(-\,\mathcal{I}(z_i, {}^tK) + u_i^\top R u_i\Big) \\[4pt]
\text{subject to} \quad & z_{i+1} = {}^tK z_i + {}^tB u_i \\
& z_0 = \psi(x_t)
\end{aligned} \tag{논문 (16)}
$$

| 기호 | 의미 |
|:---|:---|
| $R \succ 0$ | 양정부호 입력 가중 행렬 |
| $\mathcal{I}(z_i,{}^tK)$ | **최적성 조건** — D-optimality($\det$), T-optimality($\mathrm{tr}$) 등으로 행렬을 스칼라로 축약 |
| 좌상첨자 ${}^t$ | 과거 데이터로 얻은 **현재 시점의 Koopman 추정치** |

**음수 부호**에 주목: $-\mathcal{I}$ 를 최소화 = **정보를 최대화**. 즉 제어기가 목표 달성뿐 아니라 **"모델을 가장 잘 배울 수 있는 방향으로 로봇을 움직인다"**. 문제는 **receding-horizon** 방식으로 반복되어 Koopman 연산자 변화를 반영한다.

**성과**: 모델의 전체 사후 분산을 낮춰 **적은 데이터로 효과적인 Koopman 모델**을 얻는다. 논문 사례 — 공중 로봇의 불안정 텀블 회복, 다리 로봇의 granular media 상호작용 모델 학습 [100].

> [!warning] 딥 관측함수와의 긴장 관계
> 딥 모델로 관측함수를 근사하면 [100][112][113] 모델링 범위는 넓어지지만 **능동학습의 효과는 감소한다**. 비선형 관측함수를 학습하려면 더 많은 데이터가 필요하기 때문이다. 그럼에도 순수 딥 NN 모델 대비 Koopman 기반 선형 모델은 **데이터 효율성과 능동학습을 통한 제어에서 여전히 큰 우위**를 갖는다.

---

## 6. Robustness — 실무의 벽

논문 III-F절이 다루는 내용. 학습된 모델의 부정확성(측정 노이즈, 제한된 관측성, 데이터 부족, 유한차원 근사의 한계)이 제어 성능을 크게 훼손한다.

### 대응 전략 두 갈래

**(A) 불확실성을 정량화·추적**

- Shi et al. [84][122]: DMD/EDMD로 얻은 모델의 **예측 오차에 대한 loose/tight bound**를 유도하고, 그 bound를 제어 설계에 통합
- [61]: **Kalman filter** 기반으로 불확실성 모델을 리프팅 관측값과 함께 증강
- Han et al. [65]: NN으로 관측값 위의 **분포**를 모델링
- Chen & Lv [123]: **extended state observer**를 딥 Koopman에 통합 (자율주행)

**(B) 제약 기반 설계로 성능 손실 완화**

- Mamakoukas et al. [124]: **가장 가까운 안정(stable) Koopman 행렬**을 계산 — 재구성 오차를 줄이면서 내재적 안정성 확보
- [125]: 예측 성능 bound로 실행 중 적응 가능한 robust MPC
- Wang et al. [126]: **constraint-tightening** 전략 → 유계 불확실성 하에서 **recursive feasibility와 ISS(input-to-state stability) 보장**

> [!note] 총괄 통찰 (논문 원문)
> *"Koopman 모델을 제어에 유용하게 쓰려면 불확실성을 통합하고, 예측 부정확성과 불안정성의 영향을 고려하도록 제어 설계를 증강해야 한다."*

---

## 7. 열린 문제 (논문 VI절)

> [!warning] Koopman 공간의 제약 처리
> 원 상태공간의 제약(관절 한계, 충돌 회피 등)을 **Koopman 공간으로 어떻게 리프팅할 것인가**는 아직 연구가 더 필요하다. 논문은 Koopman 연산자의 **대수적·기하학적 구조**를 활용하는 것이 열쇠라고 본다.

> [!warning] 비용함수 설계
> 비용함수가 **리프팅 상태에 의존**하게 되면, Koopman-NMPC의 **recursive feasibility 평가**가 어려워진다. 로봇 시스템 전반에 일반화되는 비용함수 설계는 열린 문제다.

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman with Control Input]] — $Kz+Bu$ 모델이 어디서 오는가
> - [[EDMD]] — $K, B$ 추정
> - [[Koopman Operator]] — 상위 개념
> - [[Observable Function]] — $\psi$ 설계
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
