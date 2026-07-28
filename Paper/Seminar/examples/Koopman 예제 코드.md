---
date: 2026-07-28
status: Code
tags:
  - Code
  - Koopman
  - Tutorial
aliases:
  - Koopman 예제 코드
  - KoopmanRobo
keywords: KoopmanRobo, tutorial, EDMD, MPC, differential drive, example code
related notes: "[[EDMD]], [[Koopman MPC]], [[Observable Function]]"
dg-publish: false
---

# 🧪 Koopman 실행 예제

> [!abstract] 무엇인가
> 논문 저자들이 공개한 공식 튜토리얼 [KoopmanRobo](https://github.com/sunnyshi0310/KoopmanRobo)를 **단계별로 실행 가능한 스크립트**로 재구성한 것입니다. 개념 노트의 각 단계와 1:1로 대응되며, 모든 스크립트는 **실제로 실행 검증했습니다**.

---

## 🔗 원본 저장소

| 항목 | 링크 |
|:---|:---|
| **공식 튜토리얼** | https://github.com/sunnyshi0310/KoopmanRobo |
| Colab에서 바로 실행 | [demo.ipynb 열기](https://colab.research.google.com/github/sunnyshi0310/KoopmanRobo/blob/main/demo.ipynb) |
| 논문 preprint | https://arxiv.org/pdf/2408.04200 |

**저자들이 함께 안내하는 추가 구현**

| 구현 | 링크 | 내용 |
|:---|:---|:---|
| C++ | [koopmanOperatorsInRobotLearning](https://github.com/giorgosmamakoukas/koopmanOperatorsInRobotLearning) | 도립진자 예제 |
| Quadrotor | [active-learning-koopman](https://github.com/i-abr/active-learning-koopman) | 능동학습 Koopman ([[Koopman MPC]] 5–6번) |
| MATLAB | [ACD-EDMD](https://github.com/sunnyshi0310/ACD-EDMD) | 2-DOF 로봇팔, 차동구동 로봇 |
| **PyKoopman** | [dynamicslab/pykoopman](https://github.com/dynamicslab/pykoopman) | 여러 딕셔너리·추정법 비교 (가장 추천) |

---

## 📁 구성

```
examples/
└── koopman_diffdrive/
    ├── koopman_lib.py            공용 모듈 (시스템·데이터·딕셔너리·EDMD)
    ├── 01_collect_data.py        데이터 수집        → [[EDMD]] 1번
    ├── 02_edmd_fit.py            리프팅 + EDMD      → [[EDMD]] 2~5번
    ├── 03_mpc_control.py         Koopman MPC        → [[Koopman MPC]]
    ├── 04_dictionary_study.py    딕셔너리·구조 비교  → [[Observable Function]]
    └── demo_official.ipynb       원본 노트북 (참고용, 수정 없음)
```

---

## 🚀 실행 방법

```bash
cd examples/koopman_diffdrive

pip install numpy scipy matplotlib cvxpy

python 01_collect_data.py      # 데이터 생성 → data_diffdrive.npz
python 02_edmd_fit.py          # 모델 학습   → model_diffdrive.npz
python 04_dictionary_study.py  # 딕셔너리 비교 (03보다 먼저 봐도 좋습니다)
python 03_mpc_control.py       # MPC 제어 (가장 오래 걸림, 약 1분)
```

01 → 02 순서는 지켜야 합니다(파일 의존). 03과 04는 순서 무관합니다.

> [!tip] 검증된 환경
> Python 3.14 / numpy 2.4.4 / scipy 1.17.1 / matplotlib 3.10.9 / cvxpy 1.9.2 에서 전 스크립트 실행 확인했습니다. 원본 README가 명시한 테스트 버전은 numpy 1.26 / matplotlib 3.9.2 / cvxpy 1.6.4 / scipy 1.12 입니다.

---

## 🤖 대상 시스템

차동구동 로봇(differential-drive robot)의 운동학입니다.

$$
\dot{x} = v\cos\theta, \qquad \dot{y} = v\sin\theta, \qquad \dot{\theta} = \omega
$$

- 상태 $x = [x, y, \theta]$ — 평면상 위치와 자세
- 입력 $u = [v, \omega]$ — 선속도, 각속도

> [!important] 이 시스템을 고른 것이 왜 좋은 교보재인가
> 비선형항이 $v\cos\theta$, $v\sin\theta$ — **입력과 상태함수의 곱**입니다. 이 구조 때문에 [[Koopman with Control Input|input-affine]] 모델로는 원리적으로 표현할 수 없고, bilinear가 필요합니다. 04번이 이것을 수치로 보여줍니다.

---

## 📊 실제 실행 결과

아래는 이 저장소에서 직접 돌린 값입니다.

### 02번 — EDMD의 속도

```
딕셔너리 차원 N_psi = 11
EDMD 완료 — 소요시간 0.0861 초
재구성 RMS 오차: 6.437e-15
```

10,000개 데이터로 학습하는 데 **0.09초**입니다. 반복 최적화가 없기 때문이며([[Pseudo-inverse]] 한 번), 이것이 논문의 runtime learning 주장을 떠받치는 계산적 근거입니다.

### 04번 — 딕셔너리 × 모델 구조

| 딕셔너리 | 차원 | input-affine | bilinear |
|:---|---:|---:|---:|
| poly1 | 6 | 1.855e-02 | 1.600e-02 |
| poly2 | 15 | 1.854e-02 | 9.819e-03 |
| poly3 | 25 | 1.854e-02 | 4.583e-03 |
| **poly1 + trig** | **8** | 1.854e-02 | **3.525e-15** |
| poly2 + trig | 17 | 1.854e-02 | 8.528e-15 |

> [!success] 이 표가 논문의 핵심 주장 두 가지를 동시에 보여줍니다
> **① 차원을 키우는 것은 답이 아니다** — affine 열은 차원을 6→25로 4배 키워도 오차가 그대로입니다.
>
> **② 딕셔너리와 모델 구조가 함께 맞아야 한다** — `poly1+trig`(8차원) + bilinear 조합에서 오차가 **3.5e-15**, 즉 기계 정밀도입니다. 25차원 poly3보다 훨씬 정확합니다. 8차원으로 비선형 시스템이 **정확히** 선형화된 것이며, 이것이 [[Koopman-Invariant Subspace|불변 부분공간]]을 실제로 찾은 사례입니다.

### 03번 — 볼록성 vs 정확도

| 모델 | 1-step 오차 | 추종 오차 | QP 1회 |
|:---|---:|---:|---:|
| (A) input-affine, **볼록 QP** | 1.85e-02 | 17.16 m | 18.9 ms |
| (B) bilinear, **비볼록 SQP** | 3.52e-15 | 6.30 m | 108.9 ms |

> [!warning] 정직하게 밝혀둘 점
> (B)의 6.3 m도 "추종 성공"이라 부를 수준은 아닙니다. 모델이 1-step으로 정확해도 MPC 성능은 예측구간·가중치·입력 제약·SQP 반복 횟수에 함께 좌우되며, 여기서는 **모델 구조의 영향을 분리해 보여주는 것이 목적**이라 나머지를 튜닝하지 않았습니다. 각 스크립트 하단 "직접 해보기"로 개선해볼 수 있습니다.
>
> 그럼에도 (A) 17.16 m → (B) 6.30 m 라는 차이는 **모델 구조 하나만 바꿔서** 얻은 것이며, [[Koopman MPC]] 3번이 말하는 "때때로 비선형 실현이 더 정확해서 트레이드오프가 정당화된다"의 구체적 사례입니다.

---

## ⚠️ 원본 노트북에서 발견한 점

원본 `demo.ipynb`를 그대로 돌릴 때 알아두면 좋은 두 가지입니다. 교육용 코드라 의도적으로 단순화한 부분일 수 있습니다.

> [!note] ① `dt` 불일치
> 셀 4에서 `dt = 0.05`로 데이터를 수집하는데, MPC 셀(14)에서 `dt = 0.1`로 **덮어씁니다**. 학습된 모델의 시간 스케일과 시뮬레이션 시간 스케일이 2배 어긋난 채 제어가 돌아갑니다. 이 저장소의 스크립트는 학습에 쓴 `dt`를 일관되게 사용합니다.
>
> 논문 VI절이 **sampling rate selection**을 열린 문제로 꼽는 이유를 체감할 수 있는 지점이기도 합니다 (논문 [166]).

> [!note] ② input-affine의 구조적 한계
> 원본은 input-affine 모델만 사용합니다. 그런데 위 04번 결과처럼 이 시스템에서는 그 구조로 $v\cos\theta$ 를 표현할 수 없어, 딕셔너리를 어떻게 손봐도 예측 정확도가 1.85e-02 근처에서 정체됩니다. 이 저장소의 03·04번은 bilinear를 함께 제공해 그 차이를 드러냅니다.

---

## 🗺️ 개념 노트와의 대응

| 스크립트 | 대응 개념 노트 |
|:---|:---|
| 01_collect_data | [[EDMD]] 1번 (데이터 행렬), persistent excitation |
| 02_edmd_fit | [[Observable Function]], [[EDMD]] 2~5번, [[Pseudo-inverse]] |
| 03_mpc_control | [[Koopman MPC]] 1~3번, [[Koopman with Control Input]], [[Affine]] |
| 04_dictionary_study | [[Observable Function]], [[Koopman-Invariant Subspace]], [[EDMD]] 7번 |

---

## Related Notes
> [!tip] 관련 노트
> - [[Koopman Operators in Robot Learning|📄 논문 리뷰 본문]]
> - [[EDMD]] — 02번 스크립트의 이론
> - [[Observable Function]] — 04번 실험의 이론
> - [[Koopman MPC]] — 03번 스크립트의 이론
> - [[Koopman with Control Input]] — affine vs bilinear
