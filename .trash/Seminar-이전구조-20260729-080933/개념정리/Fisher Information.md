---
date: 2026-07-28
status: Concept
tags:
  - Concept
  - Statistics
  - Math
  - ActiveLearning
aliases:
  - 피셔 정보
  - Fisher 정보
  - Fisher Information Matrix
  - FIM
  - Cramér-Rao bound
keywords: Fisher information, score, Cramer-Rao bound, MLE, active learning, D-optimality
related notes: "[[Koopman MPC]], [[EDMD]], [[Pseudo-inverse]]"
dg-publish: false
---

# Fisher Information (피셔 정보)

> [!abstract] 한 문장 요약
> **"이 데이터가 파라미터에 대해 얼마나 많이 알려주는가"를 재는 척도.** 값이 클수록 추정이 정확해지며($\mathcal{I} \uparrow \Leftrightarrow \mathrm{Var} \downarrow$), 미분 가능하기 때문에 **"정보를 최대로 얻는 실험/행동을 최적화로 설계"** 할 수 있습니다 — 이것이 [[Koopman MPC|능동학습 제어]]의 수학적 토대입니다.

아래 1~8번을 순서대로 읽으면, 논문 (14)(15)(16)식이 왜 그렇게 생겼는지가 쌓입니다.

---

## 1. 문제의식 — "잘 배웠다"를 어떻게 재는가

데이터로 파라미터 $\theta$ 를 추정한다고 합시다. 자연스러운 질문이 있습니다.

> **"내 추정이 얼마나 믿을 만한가?"**
> **"어떤 데이터를 더 모아야 가장 빨리 확실해지는가?"**

두 번째 질문이 특히 중요합니다. 로봇이라면 **"어디로 움직여야 모델을 가장 잘 배우는가"** 가 됩니다. 이 질문에 답하려면 "배움의 양"을 **숫자로** 재야 하고, 그 숫자가 **행동에 대해 미분 가능**해야 최적화할 수 있습니다.

Fisher 정보가 정확히 그 숫자입니다.

---

## 2. 준비 — 우도(likelihood)와 score

### 우도

파라미터 $\theta$ 가 주어졌을 때 관측 $x$ 가 나올 확률밀도 $p(x|\theta)$ 를, **$x$ 를 고정하고 $\theta$ 의 함수로 볼 때** 우도라고 부릅니다.

$$
L(\theta) = p(x\,|\,\theta)
$$

**해석**: "이 $\theta$ 가 지금 본 데이터를 얼마나 잘 설명하는가." 우도를 최대로 만드는 $\theta$ 를 고르는 것이 **최대우도추정(MLE)** 입니다.

### Score — 우도의 민감도

로그우도를 $\theta$ 로 미분한 것을 **score** 라 합니다.

$$
s(\theta) = \frac{\partial \log p(x|\theta)}{\partial \theta}
$$

> [!note] 왜 로그를 씌우는가
> ① 곱이 합이 되어 독립 관측을 다루기 쉽고, ② 지수족(가우시안 등)에서 지수가 풀려 식이 간단해지며, ③ 미분이 $\frac{p'}{p}$ 형태가 되어 스케일에 둔감해집니다. 실용적 편의이지 본질적 제약은 아닙니다.

**score의 성질**: 참 $\theta$ 에서 기댓값이 0입니다.

$$
\mathbb{E}[s(\theta)] = 0
$$

즉 score는 "평균적으로는 0이지만 **얼마나 흔들리는가**"가 정보의 실체입니다. 그래서 다음 단계에서 분산을 잽니다.

---

## 3. 정의 — score의 분산

$$
\boxed{\ \mathcal{I}(\theta) = \mathbb{E}\big[\,s(\theta)\,s(\theta)^\top\,\big] = \mathbb{E}\left[\frac{\partial \log p}{\partial\theta}\ \frac{\partial \log p}{\partial\theta}^\top\right]\ }
$$

2번에서 $\mathbb{E}[s]=0$ 이었으므로, 이것은 곧 **score의 분산(공분산 행렬)** 입니다.

> [!important] 왜 "분산"이 "정보"인가 — 이 노트에서 가장 중요한 직관
> score는 **"$\theta$ 를 조금 바꾸면 우도가 얼마나 변하는가"** 입니다.
>
> | score가 크게 흔들림 | score가 거의 안 변함 |
> |:---|:---|
> | $\theta$ 를 조금만 바꿔도 우도가 **확 달라짐** | $\theta$ 를 어떻게 바꿔도 우도가 **비슷** |
> | 데이터가 $\theta$ 를 **날카롭게 특정** | 데이터로 $\theta$ 를 **구별 못 함** |
> | 정보 **많음** ✅ | 정보 **없음** ❌ |
>
> 즉 **"민감할수록 많이 배운다"** 는 것이 Fisher 정보의 전부입니다.

### 동등한 표현 (자주 쓰는 형태)

정칙 조건 하에서 다음도 성립합니다.

$$
\mathcal{I}(\theta) = -\,\mathbb{E}\left[\frac{\partial^2 \log p}{\partial\theta^2}\right]
$$

**기하학적 해석**: 로그우도의 **곡률(curvature)** 입니다. 최댓값 근처에서

- **뾰족한 봉우리** → 곡률 큼 → $\mathcal{I}$ 큼 → 최적 $\theta$ 가 명확
- **평평한 봉우리** → 곡률 작음 → $\mathcal{I}$ 작음 → 어디가 최적인지 흐릿

```
  log L(θ)                      log L(θ)
     │      ╱╲                     │    ╭─────╮
     │     ╱  ╲                    │   ╱       ╲
     │    ╱    ╲                   │  ╱         ╲
     └───────────── θ              └───────────────── θ
       뾰족 = 정보 많음              평평 = 정보 적음
       (θ̂ 를 확신)                  (θ̂ 가 어디든 비슷)
```

---

## 4. 손으로 계산해보기 — 가우시안 평균

가장 단순한 예로 감을 잡읍시다. $x_1,\dots,x_n \sim \mathcal{N}(\mu, \sigma^2)$ 에서 $\mu$ 를 추정합니다 ($\sigma$ 는 알려짐).

<details>
<summary><b>계산 과정</b></summary>

로그우도:
$$
\log p = -\frac{1}{2\sigma^2}\sum_{i=1}^n (x_i-\mu)^2 + \text{const}
$$

score:
$$
s(\mu) = \frac{\partial \log p}{\partial \mu} = \frac{1}{\sigma^2}\sum_{i=1}^n (x_i - \mu)
$$

2차 미분:
$$
\frac{\partial^2 \log p}{\partial\mu^2} = -\frac{n}{\sigma^2}
$$

따라서
$$
\mathcal{I}(\mu) = -\mathbb{E}\left[\frac{\partial^2\log p}{\partial\mu^2}\right] = \frac{n}{\sigma^2}
$$
</details>

$$
\boxed{\ \mathcal{I}(\mu) = \frac{n}{\sigma^2}\ }
$$

> [!success] 이 결과가 말하는 세 가지
> - **$n$ 에 비례** — 데이터가 많을수록 정보가 많다 (당연하지만 수식이 확인해줍니다)
> - **$\sigma^2$ 에 반비례** — 노이즈가 클수록 정보가 적다
> - **표본평균의 분산이 정확히 $\sigma^2/n = \mathcal{I}^{-1}$** — 정보의 역수가 곧 추정 분산입니다. 다음 5번의 주제입니다.

---

## 5. Cramér–Rao bound — 정보의 역수가 정확도의 한계

$$
\boxed{\ \mathrm{Var}[\hat\theta] \ \ge\ \mathcal{I}(\theta)^{-1}\ }
$$

**어떤 불편추정량(unbiased estimator)도 분산이 $\mathcal{I}^{-1}$ 보다 작을 수 없습니다.**

> [!important] 읽는 법 — 이것은 알고리즘 한계가 아니라 정보의 한계입니다
> 추정 방법을 아무리 잘 만들어도, **데이터에 담긴 정보량 자체가 정확도의 천장**을 정합니다. 더 정확해지고 싶으면 알고리즘을 바꿀 게 아니라 **더 정보량이 큰 데이터를 모아야** 합니다.
>
> 그리고 이것이 능동학습의 존재 이유입니다 — **"데이터를 어떻게 모을지"를 최적화 대상으로 삼는 것**.

$$
\mathcal{I} \uparrow \quad\Longleftrightarrow\quad \mathrm{Var}[\hat\theta] \downarrow \quad\Longleftrightarrow\quad \text{더 확실히 안다}
$$

Cramér–Rao bound를 등호로 달성하는 추정량을 **효율적(efficient)** 이라 하며, MLE는 점근적으로 효율적입니다.

---

## 6. 행렬로 확장 — Fisher Information Matrix

$\theta$ 가 벡터(또는 행렬)면 $\mathcal{I}$ 는 **행렬**이 됩니다.

$$
[\mathcal{I}]_{ij} = \mathbb{E}\left[\frac{\partial\log p}{\partial\theta_i}\frac{\partial\log p}{\partial\theta_j}\right]
$$

> [!note] 기하학적 그림 — 불확실성 타원체
> $\mathcal{I}^{-1}$ 은 추정 오차의 공분산이므로, 그것이 그리는 **타원체**가 불확실성의 모양입니다.
> - $\mathcal{I}$ 의 **큰 고유값** 방향 → 잘 아는 방향 (타원체가 얇음)
> - $\mathcal{I}$ 의 **작은 고유값** 방향 → 잘 모르는 방향 (타원체가 길쭉함)
>
> **능동학습이 하는 일**: 타원체가 길쭉한 방향, 즉 **아직 모르는 방향으로 데이터를 모으러 가는 것**입니다.

### 행렬을 스칼라로 줄이기 — 최적 실험 설계

최적화 비용함수에 넣으려면 행렬을 하나의 수로 요약해야 합니다. 이 선택을 **optimality criterion** 이라 합니다.

| 기준 | 정의 | 기하학적 의미 | 성격 |
|:---|:---|:---|:---|
| **D-optimality** | $\det\mathcal{I}$ 최대화 | 불확실성 타원체의 **부피** 최소화 | 가장 널리 쓰임. 좌표 변환에 불변 |
| **T-optimality (A)** | $\mathrm{tr}\,\mathcal{I}$ 최대화 | 축 길이의 **합** | 계산이 가장 쉬움 |
| **E-optimality** | $\lambda_{\min}(\mathcal{I})$ 최대화 | **가장 긴 축** 최소화 | 최악 방향을 보수적으로 개선 |

논문 (16)식의 $\mathcal{I}(z_i, {}^tK)$ 가 바로 이 스칼라화를 가리키며, D- 또는 T-optimality를 쓴다고 명시합니다.

---

## 7. Koopman 논문에서의 쓰임 — (14)(15)식

> 📎 전체 맥락: [[Koopman MPC]] 5~6번

### 왜 Koopman에서 유독 쉬운가

[[EDMD]] 4번의 닫힌 형태 해 $K=\Psi(Y)\Psi(X)^\dagger$ 는 **선형 최소제곱**입니다. 여기에 오차를 가우시안으로 모델링하면

$$
z_{t+1} = Kz_t + Bu_t + \varepsilon,\qquad \varepsilon\sim\mathcal{N}(0,\Sigma)
$$

이고, **최소제곱 = 가우시안 가정 하의 MLE** 이므로 2~5번의 도구가 **그대로** 적용됩니다.

> [!success] 이것이 결정적 차이입니다
> 신경망이라면 "이 가중치가 얼마나 확실한가"를 묻는 순간 베이지안 근사·앙상블 같은 무거운 장치가 필요합니다. **Koopman은 공식이 있습니다.** 이 차이가 능동학습을 실용적으로 만듭니다.

### 논문 (14) — 정의 그대로

$$
\mathcal{I} = \mathbb{E}\Big[\tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}\ \tfrac{\partial\log p(z_{t+1}|K,z_k)}{\partial K}^\top\Big] \tag{14}
$$

3번의 정의에서 $\theta \to K$ 로 바꾼 것뿐입니다.

### 논문 (15) — 가우시안이라 닫힌 형태

$$
\mathcal{I} = \tfrac{\partial z_{t+1}}{\partial K}^\top\Sigma^{-1}\tfrac{\partial z_{t+1}}{\partial K} \ \propto\ \mathrm{Var}[K]^{-1} \tag{15}
$$

- $\Sigma^{-1}$ 이 곱해진 것 → 4번에서 본 "노이즈가 클수록 정보가 적다"의 다변량 버전
- $\propto \mathrm{Var}[K]^{-1}$ → 5번의 Cramér–Rao 관계 그 자체

### 논문 (16) — 정보를 최대화하는 제어

$$
\underset{\{u_i\}}{\min}\ \sum_{i=0}^{N_h-1}\big(\underbrace{-\mathcal{I}(z_i,{}^tK)}_{\text{정보 최대화}} + \underbrace{u_i^\top Ru_i}_{\text{제어량 절약}}\big) \tag{16}
$$

**음수 부호**에 주목하세요. $-\mathcal{I}$ 를 최소화 = $\mathcal{I}$ 를 최대화입니다.

> [!important] 왜 이게 가능한가 — "행동 가능(actionable)"의 의미
> (15)를 보면 $\mathcal{I}$ 가 $z_i$ 에 의존하고, $z_i$ 는 $z_{i+1}=Kz_i+Bu_i$ 를 통해 **입력 $u$ 가 결정**합니다.
>
> $$u \ \longrightarrow\ z \ \longrightarrow\ \mathcal{I} \qquad\text{그리고 이 사슬이 미분 가능}$$
>
> 즉 **"어디로 갈지 고르면 얼마나 배울지가 정해진다"** 는 것이고, 그래서 최적화 대상이 됩니다. 만약 $\mathcal{I}$ 가 사후에 관찰만 되는 지표였다면 제어기가 손쓸 방법이 없었을 것입니다.

### 로봇으로 옮긴 직관

> [!tip] persistent excitation을 수치로 잰 것
> 로봇을 **직선으로만** 굴리면 회전 동역학은 전혀 배우지 못합니다. 그 데이터의 Fisher 정보는 **회전 방향으로 0**입니다.
>
> [[Koopman 예제 코드|예제 01번]]에서 "입력을 다양하게 줘야 한다"고 했던 persistent excitation이 바로 이것이며, Fisher 정보는 그것을 **눈대중이 아니라 숫자로** 재고 나아가 **최적화**할 수 있게 만듭니다.

---

## 8. 한계와 주의

> [!warning] ① 가우시안 가정에 의존합니다
> (15)의 깔끔한 닫힌 형태는 **오차가 가우시안**이라는 가정에서 나왔습니다. 논문 VI절(열린 문제 7번)이 정확히 이 점을 지적합니다 — *"관측 공간으로 밀어넣은 분포가 여전히 가우시안인지는 불분명하다."* 리프팅이 통계적 구조를 보존하는지가 열린 문제입니다.

> [!warning] ② 국소적 지표입니다
> Fisher 정보는 **현재 추정치 $\theta$ 주변**의 곡률입니다. 참값이 멀리 있으면 이 값이 실제 학습 효율을 잘 대변하지 못할 수 있습니다. 논문 (16)식이 ${}^tK$(현재 추정치)를 쓰고 **receding-horizon으로 반복**하는 이유이기도 합니다.

> [!warning] ③ 비선형 모델에서는 계산이 어렵습니다
> 딥 관측함수를 쓰면 $K$ 에 대한 선형성이 깨져 (15)가 성립하지 않습니다. 논문이 *"딥 모델을 쓰면 능동학습 효과가 감소한다"* 고 말하는 근본 이유입니다 → [[Koopman MPC]] 6번.

> [!warning] ④ 불편추정량 전제
> Cramér–Rao bound는 **불편(unbiased)** 추정량에 대한 것입니다. 편향을 허용하면 그보다 작은 분산도 가능합니다(ridge 정규화가 대표적 — [[Pseudo-inverse]] §5).

---

## 📌 전체 흐름 한 눈에

```
 ①  질문           "이 데이터가 θ를 얼마나 알려주나?"          (1번)
         │
 ②  재료           우도 L(θ) → score s = ∂log p/∂θ            (2번)
         │          E[s] = 0 이므로 '흔들림'이 정보의 실체
         │
 ③  정의           𝓘 = E[s sᵀ] = score의 분산                 (3번)
         │          = −E[∂²log p/∂θ²] = 로그우도의 곡률
         │          뾰족 = 정보 많음 / 평평 = 정보 적음
         │
 ④  검산           가우시안 평균:  𝓘 = n/σ²                    (4번)
         │          데이터↑ 정보↑,  노이즈↑ 정보↓
         │
 ⑤  의미           Cramér-Rao:  Var[θ̂] ≥ 𝓘⁻¹                 (5번)
         │          정보의 역수 = 정확도의 이론적 천장
         │
 ⑥  다변량         𝓘는 행렬 → 불확실성 타원체                  (6번)
         │          스칼라화: D-opt(det) / T-opt(tr) / E-opt
         │
 ⑦  응용           u → z → 𝓘 사슬이 미분 가능                 (7번)
                   ⇒ "가장 잘 배우는 궤적"을 최적화로 설계
                      = 논문 (14)(15)(16)식, 능동학습 제어
```

---

## 🔍 더 깊이 들어가려면

| 주제 | 어디로 |
|:---|:---|
| 가우시안 평균의 $\mathcal{I}$ 계산 | ↑ 4번의 접힌 섹션 |
| 이 개념이 제어기가 되는 전 과정 | [[Koopman MPC]] 5~6번 |
| 왜 최소제곱에 확률 해석이 붙는가 | [[Koopman MPC]] 5(a), [[EDMD]] 4번 |
| 정보가 부족한 데이터의 실제 예 | [[Koopman 예제 코드]] 01번 (persistent excitation) |
| 편향-분산 절충 (Cramér–Rao의 전제) | [[Pseudo-inverse]] §5 (Tikhonov 정규화) |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman MPC]] — Fisher 정보가 능동학습 제어기가 되는 과정
> - [[EDMD]] — 최소제곱 = MLE 라는 연결고리
> - [[Pseudo-inverse]] — 최소제곱의 선형대수 쪽 도구
> - [[Koopman 예제 코드]] — persistent excitation을 직접 실험
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
