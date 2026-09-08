---
title: "Chapter 9 — MPC의 고속 구현 방법 (Fast Methods for Implementing Model Predictive Control)"
book: "Model Predictive Control, 3rd Ed. (Camacho, Bordons, Maestre)"
chapter: 9
tags: [MPC, 모델예측제어, 명시적MPC, 다중파라미터계획법, 조각별아핀, 고속구현]
---

# Chapter 9 · MPC의 고속 구현 방법

> [!abstract] 이 챕터를 한 문장으로
> 제약이 있는 MPC의 해는 **활성 제약 조합이 같은 영역마다 상태의 아핀 함수**라는 사실에서 출발해, 그 영역들을 **오프라인에서 미리 다 계산해 두는 명시적 MPC(explicit MPC)** 를 다중 파라미터 계획법으로 유도하고, 영역 개수가 폭발할 때 쓸 수 있는 **근사 구현들**(조기 종료, 무브 블로킹, 룩업 테이블, MPPI, 힌징 초평면, 신경망)까지 훑는다. 목표는 단 하나 — 온라인 계산 시간을 밀리초에서 **마이크로초**로 끌어내리는 것이다.

---

## 들어가며 — 왜 이 챕터가 필요한가?

지금까지 여덟 챕터를 지나오며 우리는 MPC가 **매 샘플링 시각마다 최적화 문제를 푸는 제어기**라는 것을 배웠다. 5장에서는 제약을 넣어 QP를 풀었고, 6장에서는 불확실성을 고려한 min–max 문제를 풀었으며, 7장에서는 비선형 모델 때문에 비볼록 최적화까지 감수했다.

그런데 이 모든 챕터가 조용히 넘어간 **불편한 질문**이 하나 있다.

> **"그 최적화, 샘플링 시간 안에 끝나기는 하는가?"**

이것이 MPC의 가장 큰 단점이다. 책의 표현을 그대로 옮기면, 필요한 계산 시간이 **MPC를 적용할 수 있는 공정의 대역폭(bandwidth)을 상당히 제한한다**. 제약이 있는 MPC, 적응 MPC, 강인 MPC, 비선형 공정의 MPC가 모두 그렇다. 아무리 효율적인 알고리즘이 있어도 **빠른 공정**에 붙이면 계산 시간이 너무 길다.

> [!question] 얼마나 빠른 공정이 문제인가? (책 밖 예시)
> 정유 공장의 증류탑은 시상수가 수십 분이라 샘플링 시간이 1분이어도 충분하다. QP 푸는 데 2 ms 걸린다? 아무 문제 없다. 그런데 **전력 전자 인버터**는 스위칭 주기가 수십 마이크로초이고, **자동차 엔진 제어**는 밀리초 단위다. 여기서 "QP 푸는 데 2 ms"는 곧 **적용 불가**를 뜻한다.

이 챕터의 전략은 아주 명확한 한 문장으로 요약된다.

> **필요한 계산의 대부분을 오프라인으로 옮기고, 온라인에는 아주 조금만 남긴다.**

숙제를 미리 다 해 놓고 시험장에서는 답을 베끼기만 하는 것이다. 그런데 최적화 문제의 답을 어떻게 "미리" 계산할 수 있는가? 매번 상태 $x(t)$가 달라지는데?

바로 여기에 이 챕터의 결정적 통찰이 있다. **Bemporad 외**가 보인 것은, 작은 규모의 제약 선형 공정에 대한 MPC가 **다중 파라미터 이차계획법(multiparametric quadratic programming, mp-QP)** [1] 또는 **다중 파라미터 선형계획법(mp-LP)** [2] 문제로 명시적으로 풀리며, 그 해가 **구현하기 비교적 쉬운 조각별 아핀(piecewise affine, PWA) 제어기**로 귀결된다는 사실이다.

이 챕터가 다루는 것은 다음 다섯 가지다.

1. **왜** MPC의 해가 조각별 아핀인가 (9.1절, 2차 목적함수 / 9.1.1절, 1-노름과 $\infty$-노름)
2. 이것을 일반화하는 **다중 파라미터 계획법**의 언어 (9.2절)
3. 영역들을 실제로 **계산하고 구현**하는 방법 (9.3절)
4. **불확실성이 있을 때**(min–max)도 여전히 PWA인가 (9.4절)
5. 영역이 너무 많아 감당이 안 될 때의 **근사 구현들** (9.5절)

이 방법들 덕분에 MPC 제어기의 실행 시간을 경우에 따라 **마이크로초 단위**까지 줄일 수 있다.

---

## 9.1 MPC의 조각별 아핀성 (Piecewise Affinity of MPC)

### 아이디어는 놀랍도록 단순하다

이 절 전체의 씨앗은 [3]에서 처음 지적된 **한 문장**이다.

> **선형 제약이 있는 QP나 LP 문제의 최적해는 (있다면) 활성 제약(active constraints)의 집합에 의해 결정된다. 나아가, 활성 제약 집합이 같은 상태 공간의 모든 점에서 그 해는 상태의 아핀 함수다.**

이 문장을 이해하려면 [[활성 집합법 Active Set Method]]의 직관을 떠올리면 된다. 부등식 제약 최적화에서 진짜로 답을 결정하는 것은 **"지금 어느 벽에 닿아 있는가"** 이다. 닿지 않은 벽은 있으나 마나다.

> [!tip] 고등학생을 위한 비유 — 방 안에서 공 굴리기
> 경사진 방바닥 위에 공을 놓으면 가장 낮은 곳으로 굴러간다. 방 한가운데가 가장 낮으면 공은 **벽에 안 닿고** 거기 멈춘다. 그런데 방을 기울이면(= 상태 $x(t)$가 바뀌면) 최저점이 벽 밖으로 나가서, 공은 **벽에 붙어** 멈춘다.
>
> 핵심은 이것이다. **"어느 벽에 붙어 있느냐"가 같기만 하면**, 방을 조금씩 기울여도 공의 위치는 기울기에 따라 **매끄럽게(직선적으로)** 움직인다. 벽이 하나 더 붙거나 떨어지는 **바로 그 순간에만** 공식이 바뀐다. 그래서 전체 그림은 **직선 조각들을 이어 붙인 모양**, 즉 조각별 아핀이 된다.

MPC의 최적화 문제가 바로 이 QP·LP 계열이므로, **2차·1-노름·$\infty$-노름 목적함수를 쓰는 MPC의 해는 다중 파라미터 계획법을 통해 조각별 아핀 제어기로 압축된다**[1,2]. 이제 이것을 수식으로 확인하자.

### 출발점 — 제약이 있는 MPC의 QP

5장에서 유도했던 그 QP를 다시 쓴다. 2차 목적함수를 가진 제약 MPC는 다음 문제가 된다.

$$\min_{\mathbf{u}} \;\; \frac{1}{2}\,\mathbf{u}^\mathrm{T}\mathbf{H}\,\mathbf{u} + \mathbf{b}^\mathrm{T}\mathbf{u} + f_0 \tag{9.1}$$

$$\text{s.t.}\;\; \mathbf{R}\,\mathbf{u} \le \mathbf{c} \tag{9.2}$$

각 기호가 무엇인지 처음 나온 김에 확실히 해 두자.

| 기호 | 뜻 |
|---|---|
| $\mathbf{u}$ | 결정 변수 — 미래 제어 입력(또는 증분)들을 세로로 쌓은 $n$차원 벡터 |
| $\mathbf{H}$ | 헤시안 행렬. 양정부호(positive definite)이며 목적함수의 "그릇 모양"을 결정 |
| $\mathbf{b}$ | 1차 항 계수 벡터 |
| $f_0$ | 상수항. 최적해의 위치에는 영향이 없다 |
| $\mathbf{R}$ | 제약 행렬. $m$개의 제약이 $n$개의 결정 변수에 걸려 있으므로 $m\times n$ |
| $\mathbf{c}$ | 제약의 우변 |

여기서 **결정적으로 중요한 사실**이 하나 있다. 2~4장에서 보았듯 벡터 $\mathbf{b}$와 $\mathbf{c}$는 [[자유 응답과 강제 응답|자유 응답]]에 의존하고, 자유 응답은 공정 상태 $x(t)$에 선형으로 의존한다. 따라서 둘 다 $x(t)$의 **아핀 함수**로 쓸 수 있다.

$$\mathbf{b}(x(t)) = \mathbf{b}_0 + \mathbf{B}_x\,x(t), \qquad \mathbf{c}(x(t)) = \mathbf{c}_0 + \mathbf{C}_x\,x(t)$$

$\mathbf{b}_0$와 $\mathbf{c}_0$는 각각 알맞은 크기의 상수 벡터다. 제약 $\mathbf{R}\mathbf{u} \le \mathbf{c}(x(t))$는 결정 변수 공간에서 하나의 **폴리토프** $\Omega(x(t))$를 정의하며, 이것이 최적화 문제의 실현가능 영역이다([[폴리토프와 꼭짓점]] 참고).

> [!important] 이 절의 전체 그림
> 상태 $x(t)$가 바뀌면 **목적함수의 기울기 $\mathbf{b}$** 와 **실현가능 영역 $\Omega$의 위치** 가 함께 움직인다. 그런데 둘 다 $x(t)$에 대해 **아핀**하게 움직인다. 아핀한 입력이 들어가서 아핀한 답이 나오면 — 최적해도 $x(t)$의 아핀 함수다. 단, **활성 제약 조합이 바뀌지 않는 동안만**. 이것이 전부다.

이제 최적화 문제가 실현가능한($\Omega(x(t))$가 비어 있지 않은) 모든 상태점을 생각하고, 그 해를 $\mathbf{u}^*$라 하자. 이 점들에는 **두 가지 상황**만 존재한다.

### 상황 1 — 해가 폴리토프 내부에 있는 경우 (제약 비활성)

상태가 영역 $\mathcal{X}_0$에 속해, 최소점이 $\Omega_0 = \mathrm{int}(\Omega)$, 즉 폴리토프의 **내부**에 있는 경우다. 이때는 어떤 제약도 걸려 있지 않으므로, MPC 최적화 문제의 해 $\mathbf{u}_0^*$는 그냥 **식 (9.1)의 제약 없는 최소화**와 같다.

2차 함수 $\frac{1}{2}\mathbf{u}^\mathrm{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathrm{T}\mathbf{u} + f_0$를 $\mathbf{u}$로 미분해 0으로 놓으면

$$\mathbf{H}\mathbf{u} + \mathbf{b} = 0 \quad\Longrightarrow\quad \mathbf{u}_0^* = -\mathbf{H}^{-1}\mathbf{b}(x(t))$$

이다. 여기에 $\mathbf{b}(x(t)) = \mathbf{b}_0 + \mathbf{B}_x x(t)$를 대입해 한 줄씩 풀면

$$\mathbf{u}_0^* = -\mathbf{H}^{-1}\left(\mathbf{b}_0 + \mathbf{B}_x x(t)\right)
= \underbrace{\left(-\mathbf{H}^{-1}\mathbf{B}_x\right)}_{\mathbf{K}_0}\,x(t) + \underbrace{\left(-\mathbf{H}^{-1}\right)\mathbf{b}_0}_{\overline{\mathbf{u}}_0}$$

즉 $\mathbf{u}_0^* = \mathbf{K}_0\,x(t) + \overline{\mathbf{u}}_0$ 이다. **$\Omega_0$ 안의 모든 점에서 $\mathbf{u}_0^*$는 상태 $x(t)$의 아핀 함수다.** 게인 $\mathbf{K}_0$와 상수 $\overline{\mathbf{u}}_0$는 $x(t)$와 무관한 **상수 행렬·벡터**임에 주목하자. 오프라인에서 딱 한 번 계산해 두면 끝이다.

> [!note] 이 결과가 낯설지 않은 이유
> $\mathbf{u}_0^* = \mathbf{K}_0 x(t) + \overline{\mathbf{u}}_0$ 는 결국 **상태 피드백**이다. 제약이 없는 MPC가 [[선형 이차 조절기 LQR|LQR]]과 같은 형태의 고정 게인 제어기가 된다는 4장의 결과와 정확히 같은 이야기다. 명시적 MPC의 "0번 영역"은 언제나 이 익숙한 선형 제어기다.

### 상황 2 — 해가 폴리토프 경계에 있는 경우 (제약 활성)

상태가 영역 $\mathcal{X}_a$에 속해, 해가 **활성 제약 부분집합 $a$가 정의하는 경계** $\Omega_a(x(t))$ 위에 있는 경우다. 여기서 $a$는 활성이 될 수 있는 **여러 제약 조합 중 하나**를 가리키는 이름표다.

이 경우 $\mathbf{R}$의 행을 재배열해서 활성 제약을 위로, 비활성 제약을 아래로 모을 수 있다.

$$\mathbf{R} = \begin{bmatrix} \mathbf{R}_a \\ \mathbf{R}_{\bar a}\end{bmatrix}, \qquad \mathbf{c} = \begin{bmatrix} \mathbf{c}_a \\ \mathbf{c}_{\bar a}\end{bmatrix}, \qquad \text{단} \quad \begin{array}{l}\mathbf{R}_a \mathbf{u} = \mathbf{c}_a \\ \mathbf{R}_{\bar a}\mathbf{u} < \mathbf{c}_{\bar a}\end{array}$$

$\mathbf{R}_a$는 $m_a \times n$, $\mathbf{R}_{\bar a}$는 $m_{\bar a}\times n$ 행렬이고 $\mathbf{c}_a$는 $m_a$차원 벡터이며 $m_a + m_{\bar a} = m$이다. 부등식이 **등식으로 바뀐 것**이 핵심이다. 활성 제약은 "정확히 닿아 있다"는 뜻이므로 등호가 성립한다.

따라서 $\Omega_a(x(t))$ 안의 점들에 대한 MPC 최적화 문제는 다음과 **동치**가 된다.

$$\min_{\mathbf{u}}\;\; \frac{1}{2}\mathbf{u}^\mathrm{T}\mathbf{H}\mathbf{u} + \mathbf{b}^\mathrm{T}\mathbf{u} + f_0 \qquad \text{s.t.}\;\; \mathbf{R}_a\mathbf{u} = \mathbf{c}_a$$

**부등식 제약 문제가 등식 제약 문제로 바뀌었다.** 이것이 왜 좋은가? 등식 제약은 [[영공간과 유사역행렬|영공간 방법]]으로 **완전히 제거**할 수 있기 때문이다.

**변수 치환.** 5장에서 지적했듯 다음 치환을 도입한다.

$$\mathbf{u} = \mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}$$

여기서 $\mathbf{Y}$는 $n\times m_a$, $\mathbf{Z}$는 $n\times(n-m_a)$ 행렬이며 다음을 만족하도록 고른다.

$$\mathbf{R}_a\mathbf{Y} = \mathbf{I}, \qquad \mathbf{R}_a\mathbf{Z} = 0, \qquad [\mathbf{Y}\;\;\mathbf{Z}] \text{ 는 full rank}$$

의미를 뜯어보자. $\mathbf{Y}\mathbf{c}_a$는 등식 제약을 만족하는 **특수해 하나**($\mathbf{R}_a(\mathbf{Y}\mathbf{c}_a) = \mathbf{c}_a$)이고, $\mathbf{Z}\mathbf{v}$는 제약을 **깨지 않고 움직일 수 있는 방향**($\mathbf{R}_a \mathbf{Z}\mathbf{v}=0$)이다. 기차와 선로의 비유 그대로다. 이 치환을 하면 등식 제약은 **자동으로** 만족되고, 남은 자유도는 $n - m_a$개의 변수 $\mathbf{v}$뿐이다.

> [!note] $m_a < n$이어야 한다
> 활성 제약의 개수가 결정 변수 개수보다 적고, $\mathrm{rank}(\mathbf{R}_a) = m_a$라고 가정한다. 그렇지 않으면 $\mathbf{R}_a$를 이루는 **선형독립인 활성 제약의 최대 집합**만 남겨서 쓴다.

**목적함수 다시 쓰기.** 치환을 대입하면

$$J(\mathbf{v}) = \frac{1}{2}\left[\mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}\right]^\mathrm{T}\mathbf{H}\left[\mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}\right] + \mathbf{b}^\mathrm{T}\left[\mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}\right] + f_0$$

$$= \frac{1}{2}\mathbf{v}^\mathrm{T}\mathbf{H}_v\mathbf{v} + \mathbf{b}_v^\mathrm{T}\mathbf{v} + f_{v0}$$

여기서 각 항을 $\mathbf{v}$의 차수별로 모으면

$$\mathbf{H}_v = \mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}, \qquad \mathbf{b}_v = \mathbf{Z}^\mathrm{T}\left(\mathbf{b} + \mathbf{H}\mathbf{Y}\mathbf{c}_a\right)$$

$$f_{v0} = \left(\frac{1}{2}\mathbf{c}_a^\mathrm{T}\mathbf{Y}^\mathrm{T}\mathbf{H} + \mathbf{b}^\mathrm{T}\right)\mathbf{Y}\mathbf{c}_a + f_0$$

이다. 즉 **$n - m_a$개 변수의 제약 없는 QP 문제**가 되었다. $\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}$가 양정부호이므로 전역 최적점이 **유일**하고, 그것은 다음 선형 연립방정식의 해다.

$$\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}\,\mathbf{v} = -\mathbf{Z}^\mathrm{T}\left(\mathbf{b} + \mathbf{H}\mathbf{Y}\mathbf{c}_a\right)$$

풀면

$$\mathbf{v}^* = -\left(\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}\right)^{-1}\mathbf{Z}^\mathrm{T}\left(\mathbf{b} + \mathbf{H}\mathbf{Y}\mathbf{c}_a\right)$$

이 식이 말해 주는 것은, $\mathbf{v}^*$가 $\mathbf{b}$와 $\mathbf{c}_a$의 **아핀 함수**이고, 그 둘이 다시 $x(t)$의 아핀 함수라는 것이다. **아핀의 아핀은 아핀이다.**

**최종 제어법칙.** $\mathbf{u} = \mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}$에 되돌려 넣고 한 줄씩 전개한다.

$$\mathbf{u}_a^* = \mathbf{Y}\mathbf{c}_a + \mathbf{Z}\mathbf{v}^*$$

$$= \mathbf{Y}\mathbf{c}_a - \mathbf{Z}\left(\left(\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}\right)^{-1}\mathbf{Z}^\mathrm{T}\left(\mathbf{b} + \mathbf{H}\mathbf{Y}\mathbf{c}_a\right)\right)$$

$$= \underbrace{-\mathbf{Z}\left(\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}\right)^{-1}\mathbf{Z}^\mathrm{T}\mathbf{B}_x}_{\mathbf{K}_a}\,x(t) \;+\; \underbrace{\mathbf{Y}\mathbf{c}_a - \mathbf{Z}\left(\mathbf{Z}^\mathrm{T}\mathbf{H}\mathbf{Z}\right)^{-1}\mathbf{Z}^\mathrm{T}\left(\mathbf{b}_0 + \mathbf{H}\mathbf{Y}\mathbf{c}_a\right)}_{\overline{\mathbf{u}}_a}$$

마지막 줄에서 $\mathbf{b} = \mathbf{b}_0 + \mathbf{B}_x x(t)$를 풀어 $x(t)$가 곱해진 항과 아닌 항으로 갈랐다는 점에 주목하자.

> [!important] 9.1절의 결론
> **2차 목적함수와 선형 제약을 가진 MPC는 공정 상태의 조각별 아핀(PWA) 함수인 제어기가 된다.** 각 조각의 상수 행렬 $\mathbf{K}_a, \overline{\mathbf{u}}_a$는 **활성 제약 집합만 알면** 쉽게 계산된다. 남은 문제는 딱 하나 — **가능한 모든 활성 제약 조합에 대해, 상태 공간에서 영역 $\mathcal{X}_0$와 $\mathcal{X}_a$를 어떻게 특징지을 것인가?** 이 문제의 답이 다음 절의 다중 파라미터 계획법이다.

영역을 오프라인에서 다 구해 놓으면, 온라인 제어기는 **딱 세 단계**로 끝난다.

1. 공정 상태 $x(t)$를 읽거나 추정한다.
2. 현재 상태가 **어느 영역에 있는지** 판정한다.
3. 그 영역에 해당하는 **아핀 제어기를 적용**한다.

> [!note] 제어기는 상태만의 함수가 아니어도 된다
> 각주가 짚듯, 제어법칙은 **미래 기준값(reference)과 측정 가능한 외란**의 아핀 함수일 수도 있다. 이 확장이 바로 9.2절에서 파라미터 벡터 $\mathbf{p}$를 도입하는 이유다.

> [!warning] 영역 개수는 어마어마할 수 있다
> 제약 조합의 최대 개수 — 따라서 가능한 영역의 최대 개수 — 는 **매우 클 수 있다**. $m$개의 제약이 있으면 조합은 $2^m$개다. 다행히 **비어 있지 않은 영역의 수는 보통 그중 아주 작은 일부**다. 하지만 이 폭발 가능성이 9.5절 전체의 존재 이유다.

### 9.1.1 1-노름과 $\infty$-노름의 경우 (The 1-Norm and $\infty$-Norm Cases)

목적함수를 제곱이 아니라 **절댓값**(1-노름)이나 **최댓값**($\infty$-노름)으로 잡아도 결과는 같다. [4]에서 보인 대로 이 경우에도 MPC는 상태의 조각별 아핀 함수가 된다. 다만 **QP 대신 LP**를 풀게 되고, 그래서 논리가 살짝 달라진다.

먼저 1-노름의 경우를 보자. 가중된 기준값 오차의 절댓값 합에 제어 신호 절댓값의 합을 더한 목적함수다.

$$\min_{\mathbf{u}}\;\; \left|\mathbf{r} - \underbrace{\left(\mathbf{G}\mathbf{u} + \mathbf{F}_x x(t)\right)}_{\mathbf{y}}\right|^\mathrm{T}\mathbf{q} + \left|\mathbf{u}\right|^\mathrm{T}\mathbf{c} \tag{9.3}$$

$$\text{s.t.}\;\; \mathbf{R}\mathbf{u} \le \mathbf{C}_x x(t) + \mathbf{c}_0$$

$\mathbf{r}$은 기준값 벡터, $\mathbf{q}$는 출력 오차의 절댓값에 매기는 벌점 벡터, $\mathbf{y} = \mathbf{G}\mathbf{u}+\mathbf{F}_x x(t)$는 예측 출력이다([[자유 응답과 강제 응답]], [[하삼각 토플리츠 행렬]] 참고).

> [!note] 책 원문의 조판 누락을 복원했다
> 식 (9.3)의 두 번째 항은 **책 인쇄본 자체에서 $|\mathbf{u}|^\mathrm{T}$ 뒤의 가중 벡터가 누락**되어 있다(추출 오류가 아니다). 이어지는 식 (9.6)의 행렬 $\mathbf{S}$에서 그 자리에 $\mathbf{c}^\mathrm{T}$가 등장하므로, 여기서는 $|\mathbf{u}|^\mathrm{T}\mathbf{c}$로 복원했다.

**절댓값을 어떻게 선형으로 만드는가.** [[선형계획법과 1-노름 목적함수]]에서 다룬 그 트릭이다. 절댓값을 직접 계산하는 대신 **"그것보다 큰 보조 변수를 두고, 그 보조 변수를 최소화"** 한다. 문제 (9.3)은 다음 mp-LP 문제로 표현된다.

$$\min_{\mathbf{u},\alpha,\beta,\mu}\;\; \mu \tag{9.4}$$

$$\text{s.t.}\;\;\begin{aligned}
&\mathbf{R}\mathbf{u} \le \mathbf{C}_x x(t) + \mathbf{c}_0 \\
&-\alpha \le \mathbf{r} - \mathbf{G}\mathbf{u} - \mathbf{F}_x x(t) \le \alpha \\
&-\beta \le \mathbf{u} \le \beta \\
&-\mu \le \alpha^\mathrm{T}\mathbf{q} + \beta^\mathrm{T}\mathbf{c} \le \mu
\end{aligned}$$

여기서 $\alpha$와 $\beta$는 알맞은 차원의 **음이 아닌 성분**을 가진 벡터이고 $\mu$는 음이 아닌 스칼라다.

각 줄이 하는 일을 뜯어 보자.

- $-\alpha \le \mathbf{r}-\mathbf{y} \le \alpha$ 는 $\alpha \ge |\mathbf{r}-\mathbf{y}|$ 와 같은 말이다. $\alpha$가 오차의 절댓값을 **위에서 덮는 상자**다.
- $-\beta \le \mathbf{u} \le \beta$ 도 같은 방식으로 $\beta \ge |\mathbf{u}|$.
- 마지막 줄은 $\mu \ge \alpha^\mathrm{T}\mathbf{q} + \beta^\mathrm{T}\mathbf{c}$, 즉 $\mu$가 **전체 비용을 덮는 상자**다.
- 그리고 목적은 $\mu$를 최소화하는 것 — 상자를 최대한 작게 조이면, 결국 $\alpha=|\mathbf{r}-\mathbf{y}|$, $\beta=|\mathbf{u}|$, $\mu=$ 원래 비용이 된다.

**표준형으로 정리.** 결정 변수를 전부 음이 아니게 만들기 위해 제어 신호를 양의 부분과 음의 부분으로 쪼갠다.

$$\mathbf{u} = \mathbf{u}_+ - \mathbf{u}_-$$

그리고 전부 하나의 벡터로 묶는다.

$$\mathbf{z}^\mathrm{T} = \left[\mathbf{u}_+^\mathrm{T},\; \mathbf{u}_-^\mathrm{T},\; \alpha^\mathrm{T},\; \beta^\mathrm{T},\; \mu\right]$$

그러면 문제는 **표준 LP** 모양이 된다.

$$\min_{\mathbf{z}}\;\; [0\;\cdots\;0\;\;1]\,\mathbf{z} \tag{9.5}$$

목적함수 벡터가 마지막 성분만 1인 것에 주목하자. **오직 $\mu$만 최소화**한다는 뜻이다. 제약은 다음과 같다.

$$\underbrace{\begin{bmatrix}
\mathbf{R} & -\mathbf{R} & \mathbf{0} & \mathbf{0} & 0\\
-\mathbf{G} & \mathbf{G} & -\mathbf{I} & \mathbf{0} & 0\\
\mathbf{G} & -\mathbf{G} & -\mathbf{I} & \mathbf{0} & 0\\
\mathbf{I} & -\mathbf{I} & \mathbf{0} & -\mathbf{I} & 0\\
-\mathbf{I} & \mathbf{I} & \mathbf{0} & -\mathbf{I} & 0\\
\mathbf{0} & \mathbf{0} & \mathbf{q}^\mathrm{T} & \mathbf{c}^\mathrm{T} & -1\\
\mathbf{0} & \mathbf{0} & -\mathbf{q}^\mathrm{T} & -\mathbf{c}^\mathrm{T} & -1
\end{bmatrix}}_{\mathbf{S}}\mathbf{z}
\;\le\;
\underbrace{\begin{bmatrix}\mathbf{C}_x\\ \mathbf{F}_x\\ -\mathbf{F}_x\\ \mathbf{0}\\ \mathbf{0}\\ \mathbf{0}\\ \mathbf{0}\end{bmatrix}}_{\mathbf{D}_x} x(t)
\;+\;
\underbrace{\begin{bmatrix}\mathbf{c}_0\\ -\mathbf{r}\\ \mathbf{r}\\ \mathbf{0}\\ \mathbf{0}\\ 0\\ 0\end{bmatrix}}_{\mathbf{d}_0} \tag{9.6}$$

행별로 읽으면 각각 원래 제약, 오차 상한/하한, 입력 상한/하한, 비용 상한/하한이다. $\mathbf{u}=\mathbf{u}_+-\mathbf{u}_-$ 치환 때문에 $\mathbf{R}$이 $[\mathbf{R}\;\;-\mathbf{R}]$처럼 짝을 이뤄 나타난다.

**LP의 답은 꼭짓점에 있다.** 여기서 QP와 결정적으로 다른 점이 나온다. LP 문제의 최적해는 실현가능 영역 $\mathbf{S}\mathbf{z} \le \mathbf{D}_x x(t)+\mathbf{d}_0$, 즉 $\Omega(x(t))$의 **꼭짓점 중 하나**에서 달성된다([[폴리토프와 꼭짓점]]). 따라서 꼭짓점은 다음 **등식** 방정식의 해로 주어진다.

$$\mathbf{S}\mathbf{z} = \mathbf{D}_x x(t) + \mathbf{d}_0$$

> [!tip] 왜 LP의 답은 항상 구석에 있을까
> 목적함수가 **평면**이기 때문이다. 평평한 지붕을 기울이면 물은 반드시 **가장 낮은 모서리**로 흐른다. 지붕 한가운데에 물이 고이려면 지붕이 오목해야(= 목적함수가 2차여야) 한다. LP에서는 그럴 일이 없으므로 답은 언제나 다면체의 구석이다.

이 경우 임계 영역(critical region) $\mathcal{X}_a$는 **파라미터 공간에서 같은 선형독립 제약 부분집합이 활성인 점들의 집합**으로만 정의된다. 즉 해는 언제나 다면체의 꼭짓점이다. 임의의 $x(t)\in\mathcal{X}_a$에 대해 최적화 문제의 정의역은 $\Omega_a(x(t))$이고 해는 꼭짓점 $\mathbf{z}_a$이며, 다음처럼 계산된다.

$$\mathbf{z}_a = (\mathbf{S}_a)^{-1}\left(\mathbf{D}_{x,a}\,x(t) + \mathbf{d}_{0,a}\right) = \underbrace{(\mathbf{S}_a)^{-1}\mathbf{D}_{x,a}}_{\mathbf{K}_a}\,x(t) + \underbrace{(\mathbf{S}_a)^{-1}\mathbf{d}_{0,a}}_{\overline{\mathbf{z}}_a} \tag{9.7}$$

아래첨자 $a$는 해 $\mathbf{z}_a$를 만들어 내는 행렬·벡터의 **해당 행/성분**을 가리키며, $\mathbf{S}_a$가 full rank라고 가정했다(퇴화(degeneracy)가 없다면 $\dim(\mathbf{z})$개의 선형독립 행을 항상 찾을 수 있다[2]).

> [!important] 9.1.1절의 결론
> 임계 영역 $\mathcal{X}_a$ 안에서 LP 문제의 해도 **상태의 아핀 함수**이고, 따라서 전체 해는 다시 **상태 변수의 조각별 아핀 함수**다. 목적함수가 2차든 1-노름이든 $\infty$-노름이든, 결론은 하나다. 임계 영역 $\mathcal{X}_a$를 실제로 계산하는 방법은 9.3절에서 다중 파라미터 계획법을 제대로 도입한 뒤에 보인다.

### 예제 9.1 — 한 스텝 지평의 명시적 MPC (Explicit MPC for a Single-Step Horizon)

말로만 하면 와닿지 않으니, 손으로 끝까지 풀 수 있는 가장 작은 예제를 보자.

다음 이산시간 선형 시스템을 생각한다.

$$x(t+1) = a\,x(t) + b\,u(t)$$

$a$와 $b$는 양의 스칼라, $x(t)\in\mathbb{R}$은 상태, $u(t)\in\mathbb{R}$은 제어 입력이다.

**목적함수.** 간단히 하기 위해 제어기의 목표를 다음 2차 비용의 최소화로 잡는다.

$$J = x(t+1)^2 + u(t)^2$$

이는 예측 지평 $N_\mathrm{p}=1$에 해당한다. 시스템 모델 $x(t+1)=ax(t)+bu(t)$를 대입하고 2로 나누면

$$\frac{J}{2} = \frac{1}{2}\left(a^2x(t)^2 + 2ab\,x(t)u(t) + b^2u(t)^2\right) + \frac{1}{2}u(t)^2$$

$u(t)$의 차수별로 항을 모으면(등가 목적함수)

$$J = \frac{1}{2}\underbrace{(b^2+1)}_{\mathbf{H}}\,u(t)^2 + \underbrace{a\,b\,x(t)}_{\mathbf{b}^\mathrm{T}}\,u(t) + \frac{a^2 x(t)^2}{2}$$

이다. 즉 이 문제의 헤시안은 스칼라 $\mathbf{H}=b^2+1$, 1차 항 계수는 $\mathbf{b}=ab\,x(t)$이다. **$\mathbf{b}$가 $x(t)$에 선형으로 의존**하는 것을 눈으로 확인할 수 있다($\mathbf{b}_0=0$, $\mathbf{B}_x = ab$).

**제약.** 입력의 크기를 $\gamma$(양의 스칼라)로 제한한다.

$$\underbrace{\begin{bmatrix}-1\\ 1\end{bmatrix}}_{\mathbf{R}}u(t) \le \underbrace{\begin{bmatrix}\gamma\\ \gamma\end{bmatrix}}_{\mathbf{c}}$$

첫 행은 $-u(t)\le\gamma$ 즉 $u(t)\ge-\gamma$, 둘째 행은 $u(t)\le\gamma$다.

**세 가지 경우를 손으로 푼다.**

- **제약이 하나도 활성이 아닐 때** — 9.1절 상황 1이다.
$$u(t)^* = -\mathbf{H}^{-1}\mathbf{b} = -\frac{ab}{b^2+1}\,x(t)$$

- **하한 제약 $u(t)\ge-\gamma$가 활성일 때** — 제약 없는 해가 하한 아래로 내려가려 할 때다.
$$u(t)^* = -\gamma \qquad \text{if } -\frac{ab}{b^2+1}x(t) < -\gamma$$

- **상한 제약 $u(t)\le\gamma$가 활성일 때**
$$u(t)^* = \gamma \qquad \text{if } -\frac{ab}{b^2+1}x(t) > \gamma$$

**조건을 $x(t)$에 대해 풀어 정리하자.** $-\frac{ab}{b^2+1}x(t) < -\gamma$ 의 양변에 $-\frac{b^2+1}{ab}$($a,b>0$이므로 음수)를 곱하면 부등호가 뒤집혀 $x(t) > \frac{\gamma(b^2+1)}{ab}$가 된다. 같은 식으로 반대쪽도 정리하면, 기대한 대로 **조각별 선형 제어법칙**이 나온다.

$$u(t)^* = \begin{cases}
-\gamma, & \text{if } x(t) > \dfrac{\gamma(b^2+1)}{ab} \\[8pt]
-\dfrac{ab}{b^2+1}\,x(t), & \text{if } -\dfrac{\gamma(b^2+1)}{ab} \le x(t) \le \dfrac{\gamma(b^2+1)}{ab} \\[8pt]
\gamma, & \text{if } x(t) < -\dfrac{\gamma(b^2+1)}{ab}
\end{cases}$$

즉 이 제어법칙은 상태 공간을 **서로 다른 활성 제약 시나리오에 대응하는 세 영역**으로 분할한다.

![[mpc_fig_9_1.png]]

> [!example] 그림 9.1이 말하는 것
> $a=b=\gamma=1$로 두었을 때의 명시적 MPC 제어법칙 $u(t)$를 상태 $x(t)$의 함수로 그린 것이다. 가운데 구간에서는 원점을 지나는 **기울기 $-ab/(b^2+1) = -0.5$인 직선**이고, 양 끝에서는 $\pm\gamma=\pm 1$로 **평평하게 눌린다**. 세 조각의 경계는 $x = \pm\gamma(b^2+1)/(ab) = \pm 2$다. 왼쪽 평평한 부분이 상한 제약 영역, 오른쪽 평평한 부분이 하한 제약 영역, 가운데 비스듬한 부분이 제약 비활성 영역이다. **꺾인 직선 세 개** — 이것이 조각별 아핀 제어기의 가장 순수한 모습이다.

> [!note] 계산 시간 비교 (Core i7 2.7 GHz, 16 GB RAM, MATLAB®)
> 100개의 무작위 상태에 대해 측정한 결과다.
>
> | 방식 | 평균 계산 시간 | 표준편차 |
> |---|---|---|
> | 온라인 QP | $1.94\cdot10^{-3}$ s | $9.4\cdot10^{-4}$ s |
> | 명시적 제어기 | $4.98\cdot10^{-6}$ s | $1.18\cdot10^{-5}$ s |
>
> 약 **390배** 빠르다. 명시적 MPC 정식화의 계산상 이점을 보여 주는 수치다.

---

## 9.2 MPC와 다중 파라미터 계획법 (MPC and Multiparametric Programming)

앞 절의 결과는 일반화할 수 있다. **선형 제약이 있는 MPC 문제는 다중 파라미터 계획법(multiparametric programming) 문제로 정식화된다.** 여기서 해는 상태·기준값·예측된 외란처럼 **변하는 파라미터들을 담은 벡터 $\mathbf{p}$**로 표현된다.

이 기법의 이점은 명확하다. **파라미터가 바뀌어도 최적화 문제를 다시 풀 필요가 없다.** 해가 이미 그 불확실 파라미터의 함수로 구해져 있기 때문이다.

> [!tip] 비유 — 공식 대 계산
> 이차방정식 $ax^2+bx+c=0$을 풀 때마다 수치해석으로 근을 찾아 헤맬 필요가 없다. 근의 공식 $x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}$가 이미 **계수의 함수로** 답을 준다. 다중 파라미터 계획법이 하려는 일이 정확히 이것이다. 최적화 문제의 답을 **파라미터의 함수(공식)로** 미리 구해 두는 것. 차이가 있다면, 이 "공식"은 조각마다 다르고 조각의 경계도 함께 계산해 줘야 한다는 점이다. 자세한 배경은 [[다중 파라미터 계획법 Multiparametric Programming]] 참고.

> [!note] 민감도 분석과의 관계
> 각주가 짚듯, 다중 파라미터 계획법은 최적화 해의 **민감도 분석(sensitivity analysis)** 과 밀접하다. 민감도 분석이 답하는 질문은 두 가지다. (1) 목적함수의 계수가 바뀌면 최적해가 어떻게 변하는가? (2) 제약의 우변이 바뀌면 최적해가 어떻게 변하는가? MPC에서는 상태 $x(t)$가 바뀌면 **둘 다** 바뀌므로, 두 질문을 동시에 푸는 셈이다.

### 파라미터를 명시적으로 드러낸 문제

최적화 문제를 다음처럼 쓴다.

$$\min_{\mathbf{u}}\;\; \frac{1}{2}\mathbf{u}^\mathrm{T}\mathbf{H}\mathbf{u} + \mathbf{b}(\mathbf{p})^\mathrm{T}\mathbf{u} + f_0 \tag{9.8}$$

$$\text{s.t.}\;\; \mathbf{R}\mathbf{u} \le \mathbf{r}(\mathbf{p})$$

벡터 $\mathbf{b}(\mathbf{p})$와 $\mathbf{r}(\mathbf{p})$는 $\mathbf{p}$에 **아핀하게 의존**한다. $\mathbf{p}$는 최적화 문제의 해에서 명시적으로 다룰 파라미터들(예: 상태)을 담은 벡터다. 따라서 다음처럼 펼쳐 쓸 수 있다.

$$\mathbf{b}(\mathbf{p}) = \mathbf{b}_0 + \mathbf{B}_p\,\mathbf{p}, \qquad \mathbf{c}(\mathbf{p}) = \mathbf{c}_0 + \mathbf{R}_p\,\mathbf{p}$$

9.1절과 형태가 완전히 같다. 달라진 것은 $x(t)$ 자리에 더 일반적인 $\mathbf{p}$가 들어갔다는 것뿐이다.

### KKT 조건으로 해를 특징짓기

이제 9.1절에서처럼 경우를 나누는 대신, **한 번에** 다룰 수 있는 도구를 쓴다. 문제 (9.8)의 1차 **카루쉬–쿤–터커(Karush–Kuhn–Tucker, KKT)** 최적성 조건이다([[KKT 조건]] 참고).

$$\mathbf{H}\mathbf{u}^* + \mathbf{b}(\mathbf{p}) + \mathbf{R}^\mathrm{T}\boldsymbol{\lambda}^* = 0 \tag{9.9}$$

$$\mathbf{R}\mathbf{u}^* \le \mathbf{r}(\mathbf{p}) \tag{9.10}$$

$$\boldsymbol{\lambda}^* \ge 0 \tag{9.11}$$

$$\lambda_i^* \cdot \left(\mathbf{R}_i\mathbf{u}^* - \mathbf{c}_i(\mathbf{p})\right) = 0, \qquad i = 1..n_\mathrm{r} \tag{9.12}$$

$\boldsymbol{\lambda}^*$는 **라그랑주 승수(Lagrange multipliers)** 이고, 아래첨자 $i$는 해당 행렬·벡터의 $i$번째 행 또는 성분을 가리킨다. 네 조건의 의미를 하나씩 짚으면

- **(9.9) 정상성(stationarity)** — 목적함수를 내리려는 힘 $\mathbf{H}\mathbf{u}+\mathbf{b}$와 제약이 되미는 힘 $\mathbf{R}^\mathrm{T}\boldsymbol{\lambda}$가 **정확히 균형**을 이룬다.
- **(9.10) 원시 실현가능성** — 해가 제약을 어기지 않는다.
- **(9.11) 듀얼 실현가능성** — 벽은 **밀 수만 있고 당길 수는 없다**. 그래서 승수가 음이 아니다.
- **(9.12) 상보 여유(complementary slackness)** — 각 제약에 대해 **"닿아 있거나($\mathbf{R}_i\mathbf{u}^*=\mathbf{c}_i$) 아니면 승수가 0이거나"** 둘 중 하나다. 닿지 않은 벽은 힘을 주지 않는다.

**활성/비활성으로 나누기.** $\boldsymbol{\lambda}_a$와 $\boldsymbol{\lambda}_{\bar a}$를 각각 활성·비활성 제약에 대응하는 승수 집합이라 하자. 조건 (9.12)에 의해 비활성 제약에서는 $\boldsymbol{\lambda}_{\bar a}=0$이고, 활성 제약에서는 $\boldsymbol{\lambda}_a > 0$이므로

$$\mathbf{R}_a\mathbf{u}^* = \mathbf{c}_a(\mathbf{p})$$

가 활성 집합에 속한 제약들에 대해 성립한다.

**유도 1단계 — 최적 입력을 승수로 표현.** 활성 집합이 최적 입력 수열에 직접 영향을 준다는 점에 주목하며, 식 (9.9)를 $\mathbf{u}^*$에 대해 푼다. $\boldsymbol{\lambda}_{\bar a}=0$이므로 $\mathbf{R}^\mathrm{T}\boldsymbol{\lambda}^* = \mathbf{R}_a^\mathrm{T}\boldsymbol{\lambda}_a^*$이고,

$$\mathbf{H}\mathbf{u}^* = -\mathbf{b}(\mathbf{p}) - \mathbf{R}_a^\mathrm{T}\boldsymbol{\lambda}_a^*$$

$$\mathbf{u}_a^*(\mathbf{p}) = -\mathbf{H}^{-1}\left(\mathbf{b}(\mathbf{p}) + \mathbf{R}_a^\mathrm{T}\boldsymbol{\lambda}_a^*\right) \tag{9.13}$$

아래첨자 $a$는 활성 제약 집합에 대한 의존성을 강조하기 위해 붙였다. 아직 $\boldsymbol{\lambda}_a^*$를 모르므로 이걸로 끝이 아니다.

**유도 2단계 — 승수를 파라미터로 표현.** 식 (9.13)을 활성 제약 등식 $\mathbf{R}_a\mathbf{u}^* = \mathbf{c}_a(\mathbf{p})$에 대입한다.

$$\mathbf{R}_a\mathbf{H}^{-1}\left(\mathbf{b}(\mathbf{p}) + \mathbf{R}_a^\mathrm{T}\boldsymbol{\lambda}_a^*\right) + \mathbf{c}_a(\mathbf{p}) = 0$$

$\boldsymbol{\lambda}_a^*$에 대해 정리하면

$$\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\boldsymbol{\lambda}_a^* = -\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{b}(\mathbf{p}) + \mathbf{c}_a(\mathbf{p})\right)$$

$$\boxed{\;\boldsymbol{\lambda}_a^* = -\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\right)^{-1}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{b}(\mathbf{p}) + \mathbf{c}_a(\mathbf{p})\right)\;}$$

$\mathbf{H}$가 양정부호이고 $\mathbf{R}_a$가 full row rank이면 $\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}$는 가역이다.

**유도 3단계 — 제어법칙 완성.** 이 $\boldsymbol{\lambda}_a^*$를 식 (9.13)에 되돌려 넣는다.

$$\mathbf{u}^*(\mathbf{p}) = -\mathbf{H}^{-1}\left(\mathbf{b}(\mathbf{p}) - \mathbf{R}_a^\mathrm{T}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\right)^{-1}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{b}(\mathbf{p}) + \mathbf{c}_a(\mathbf{p})\right)\right) \tag{9.14}$$

여기서 $\mathbf{b}(\mathbf{p}) = \mathbf{b}_0+\mathbf{B}_p\mathbf{p}$와 $\mathbf{c}_a(\mathbf{p}) = \mathbf{c}_{0,a}+\mathbf{R}_p\mathbf{p}$를 펼쳐, $\mathbf{p}$가 곱해진 항과 상수항으로 가르면 다음 **아핀 표현**을 얻는다.

$$\mathbf{u}_a^*(\mathbf{p}) = \mathbf{K}_a\,\mathbf{p} + \overline{\mathbf{u}}_a \tag{9.15}$$

여기서 $\mathbf{K}_a$와 $\overline{\mathbf{u}}_a$는 다음과 같이 계산된다.

$$\mathbf{K}_a = -\mathbf{H}^{-1}\left(\mathbf{B}_p - \mathbf{R}_a^\mathrm{T}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\right)^{-1}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{B}_p + \mathbf{R}_p\right)\right)$$

$$\overline{\mathbf{u}}_a = -\mathbf{H}^{-1}\left(\mathbf{b}_0 - \mathbf{R}_a^\mathrm{T}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\right)^{-1}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{b}_0 + \mathbf{c}_{0,a}\right)\right)$$

보다시피 결과 제어기는 **고려한 파라미터의 아핀 함수**이며, 게인은 **최적점에서의 활성 제약 집합에 의존**한다.

> [!note] 책 인쇄본의 부호 오식을 바로잡았다
> **책 인쇄본의 $\mathbf{K}_a$는 $+\mathbf{R}_a^\mathrm{T}(\cdots)$ 로 되어 있으나, 식 (9.14)·$\overline{\mathbf{u}}_a$ 와 유도상 $-$ 가 맞다(책 오식).** 확인은 간단하다. 식 (9.14)에 $\mathbf{b}(\mathbf{p}) = \mathbf{b}_0 + \mathbf{B}_p\mathbf{p}$ 와 $\mathbf{c}_a(\mathbf{p}) = \mathbf{c}_{0,a} + \mathbf{R}_p\mathbf{p}$ 를 대입해 $\mathbf{p}$ 가 곱해진 항만 모으면, 괄호 안의 부호가 (9.14)에서 그대로 따라 내려와 $\mathbf{B}_p - \mathbf{R}_a^\mathrm{T}(\cdots)(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{B}_p + \mathbf{R}_p)$ 가 된다. 상수항만 모으면 $\overline{\mathbf{u}}_a$ 식이 되는데, 그쪽은 책도 $-$ 로 인쇄되어 있어 서로 앞뒤가 맞지 않았다. 위 본문은 바로잡은 $-$ 로 적었다.

### 영역은 어디까지인가 — 임계 영역의 정의

제어기를 구현하려면 **파라미터 공간에서 특정 제약 집합이 활성인 영역**을 알아내야 한다. 두 가지 조건이 그 영역을 정의한다.

**조건 1 — 비활성 제약은 계속 비활성이어야 한다.** KKT 조건 (9.10)을 떠올리자. 아핀 제어법칙 $\mathbf{u}_a^*(\mathbf{p})$는 **비활성 제약 집합이 그대로인 곳에서만** 최적으로 남는다. 즉 다음이 성립하는 동안이다.

$$\mathbf{R}_{\bar a}\left(\mathbf{K}_a\mathbf{x} + \overline{\mathbf{u}}_a\right) < \mathbf{c}_{\bar a}(\mathbf{p}) \tag{9.16}$$

말로 옮기면 "이 조각의 공식으로 계산한 입력을 **아직 안 걸린 제약들에 넣어 봤을 때 여전히 안 걸리는가**"를 확인하는 것이다.

**조건 2 — 활성 제약의 승수는 양수여야 한다.** KKT 조건 (9.11)이다.

$$\boldsymbol{\lambda}_a^* = -\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}\right)^{-1}\left(\mathbf{R}_a\mathbf{H}^{-1}\mathbf{b}(\mathbf{p}) + \mathbf{c}_a(\mathbf{p})\right) > 0 \tag{9.17}$$

말로 옮기면 "**닿아 있다고 가정한 벽이 정말로 밀고 있는가**"를 확인하는 것이다. 승수가 음이 되면 그 벽은 사실 당기고 있다는 뜻이고, 이는 불가능하므로 그 제약은 활성이 아니어야 한다.

부등식 (9.16)과 (9.17)이 함께 공간 안에 **(비어 있을 수도 있는) 영역 $\mathcal{P}_a$** 를 정의한다. 두 조건 모두 $\mathbf{p}$에 대해 선형이므로, $\mathcal{P}_a$는 **다면체**다.

> [!important] 왜 $\mathbf{p}$로 일반화하는 것이 중요한가
> 다중 파라미터 문제의 해가 다시 조각별 아핀이라는 것도 중요하지만, 더 중요한 것은 **제어 영역이 정의되는 공간의 차원이 파라미터 벡터 $\mathbf{p}$의 차원**이라는 점이다. $\mathbf{p}$에는 상태뿐 아니라 **예측 구간에 걸쳐 정의된 기준값과 측정 가능한 외란**도 포함될 수 있다. 즉 "미래 기준값이 이렇게 바뀔 것"까지 미리 반영한 명시적 제어기를 만들 수 있다. 대신 차원이 늘어나면 영역 개수도 함께 늘어난다는 대가가 따른다.

이 영역 안의 모든 점에서 최적화 문제의 해는 활성 제약 집합 $a$의 교집합 위에 있고, 제어기는 식 (9.15)로 주어진다.

### 예제 9.2 — 기준값 변화를 다루는 다중 파라미터 QP (Multiparametric QP with Reference Changes)

파라미터 $\mathbf{p}$에 **기준값**을 넣으면 어떻게 되는지 보여 주는 예제다.

다음 1차 시스템을 생각한다.

$$x(t+1) = 0.9\,x(t) + u(t)$$

조작 변수는 $-1 \le u(t) \le 1$로 제한되고, 목적함수는 $N_\mathrm{p}=5$ 시점 동안 **상수 기준값 $\bar r$** 을 추종하는 것이다.

$$J = \sum_{j=1}^{N_\mathrm{p}}\left(\left(x(t+j)-\bar r\right)^2 + u(t+j-1)^2\right)$$

**예측식 세우기.** 예측 구간에 대한 상태 벡터의 예측은 $\mathbf{x} = \mathbf{G}\mathbf{u} + \mathbf{F}_x x(t)$로 계산되며,

$$\mathbf{G} = \begin{bmatrix}
1 & 0 & 0 & 0 & 0\\
0.9 & 1 & 0 & 0 & 0\\
0.81 & 0.9 & 1 & 0 & 0\\
0.729 & 0.81 & 0.9 & 1 & 0\\
0.6561 & 0.729 & 0.81 & 0.9 & 1
\end{bmatrix},
\qquad
\mathbf{F}_x = \begin{bmatrix}0.9\\ 0.81\\ 0.729\\ 0.6561\\ 0.5905\end{bmatrix}$$

이다. 숫자의 출처를 확인해 보자. $x(t+1)=0.9x(t)+u(t)$를 반복 대입하면 $x(t+2)=0.9^2x(t)+0.9u(t)+u(t+1)$, $x(t+3)=0.9^3x(t)+0.81u(t)+\cdots$ 이다. 그래서 $\mathbf{F}_x$의 성분은 $0.9^j$($0.9,\,0.81,\,0.729,\,0.6561,\,0.59049$)이고, $\mathbf{G}$는 같은 숫자들이 아래로 밀리며 채워지는 **하삼각 토플리츠 행렬**이다([[하삼각 토플리츠 행렬]], [[임펄스 응답과 컨볼루션]] 참고).

**목적함수를 QP 표준형으로.** 목적함수는 다음처럼 쓸 수 있다.

$$J = \left(\mathbf{G}\mathbf{u} + \mathbf{F}_x x(t) - \mathbf{1}_5\bar r\right)^\mathrm{T}\left(\mathbf{G}\mathbf{u} + \mathbf{F}_x x(t) - \mathbf{1}_5\bar r\right) + \mathbf{u}^\mathrm{T}\mathbf{u}$$

$$= \left(\mathbf{G}\mathbf{u} + \mathbf{F}_p\,p(t)\right)^\mathrm{T}\left(\mathbf{G}\mathbf{u} + \mathbf{F}_p\,p(t)\right) + \mathbf{u}^\mathrm{T}\mathbf{u}$$

여기가 이 예제의 **핵심 트릭**이다. $\mathbf{1}_5 = [1\,1\,1\,1\,1]^\mathrm{T}$로 두고

$$p(t) = \begin{bmatrix}x(t)\\ \bar r\end{bmatrix}, \qquad \mathbf{F}_p = \left[\mathbf{F}_x \;\; -\mathbf{1}_5\right]$$

로 묶으면, **상태와 기준값이 하나의 파라미터 벡터**가 된다. 그러면 $\mathbf{F}_x x(t) - \mathbf{1}_5 \bar r = \mathbf{F}_p\,p(t)$가 되어 표기가 깔끔해진다.

$J$를 2로 나누고 상수항을 제거하면 표준형 QP를 얻는다.

$$J' = \frac{1}{2}\mathbf{u}^\mathrm{T}\underbrace{\left(\mathbf{G}^\mathrm{T}\mathbf{G} + \mathbf{I}\right)}_{\mathbf{H}}\mathbf{u} + \underbrace{\left(\mathbf{F}_p\mathbf{p}\right)^\mathrm{T}\mathbf{G}}_{\mathbf{b}(\mathbf{p})^\mathrm{T}}\mathbf{u}$$

$\mathbf{b}(\mathbf{p})$가 $\mathbf{p}$에 **선형**임을 확인하자. 다중 파라미터 정식화의 전제가 정확히 성립한다.

**제약 행렬.**

$$\underbrace{\begin{bmatrix}\mathbf{I}_5\\ -\mathbf{I}_5\end{bmatrix}}_{\mathbf{R}}\mathbf{u} \le \underbrace{\mathbf{1}_{10}}_{\mathbf{c}}$$

위 다섯 행이 $u(t+j)\le 1$, 아래 다섯 행이 $-u(t+j)\le 1$ 즉 $u(t+j)\ge-1$이다.

![[mpc_fig_9_2.png]]

> [!example] 그림 9.2가 말하는 것
> (a)는 mp-QP를 풀어 얻은 1차 시스템의 **제어기 영역들**이고, (b)는 기준값이 그림에 표시된 패턴대로 바뀔 때 **증강 상태 공간(상태 + 기준값)** 에서 시스템이 따라간 궤적이다. 여기서 결정적으로 눈여겨볼 점은 **세로축이 기준값**이라는 것이다. 즉 영역 분할이 상태 축 하나가 아니라 **(상태, 기준값)의 2차원 평면** 위에 그려져 있다. 기준값이 바뀌면 궤적은 세로로 점프하고, 그 새로운 높이에서 다시 가로로 움직이며 상태가 기준값을 따라간다. 그림이 보여 주듯 제어기는 기준값을 정확하게 추종한다.

> [!note] 계산 시간 비교 (Core i7 2.7 GHz, 16 GB RAM, MATLAB®)
> 100개의 무작위 상태에 대한 결과다.
>
> | 방식 | 평균 계산 시간 | 표준편차 |
> |---|---|---|
> | 온라인 QP | $1.3\cdot10^{-3}$ s | $4.94\cdot10^{-4}$ s |
> | 명시적 제어기 | $3.14\cdot10^{-5}$ s | $1.2\cdot10^{-5}$ s |
>
> 약 **41배** 빠르다. 예제 9.1보다 배율이 줄어든 것은 결정 변수가 1개에서 5개로 늘어 영역 판정 비용이 커졌기 때문으로 보인다(책의 설명은 아니다).

---

## 9.3 MPC의 조각별 구현 (Piecewise Implementation of MPC)

앞 절이 "영역이 어떤 부등식으로 정의되는가"를 말했다면, 이 절은 **"그 영역들을 실제로 어떻게 다 찾아내는가"** 를 다룬다.

보통 명시적 MPC 제어기는 $\mathbf{p} = x$인 경우, 즉 **상태 공간의 영역들에 대해 단순한 아핀 제어법칙**을 정의하는 경우에 집중한다.

### 무식한 방법과 재귀적 방법

**무식한 방법(brute force).** 가능한 모든 활성 제약 집합을 열거하는 알고리즘을 돌린 뒤, 식 (9.16)과 (9.17)로 각 영역을 정의하면 된다. 원리적으로는 맞지만 조합이 $2^m$개라 감당이 안 된다.

**재귀적 방법.** [1]에서 제안한 더 효율적인 방법은 다음과 같다.

1. **시작점 잡기.** 상태 공간 $\mathcal{X}$ 안의 실현가능한 점 $x_0 \in \mathcal{X}$를 하나 고르고, 그에 딸린 QP 문제를 푼다.
2. **첫 영역 확정.** 그 해로부터 활성 제약을 얻고, (9.16)과 (9.17)에서 **군더더기 제약(superfluous constraints)** 을 제거해 영역 $\mathcal{X}_0$를 결정한다.
3. **나머지 공간을 쪼개기.** $\mathcal{X}_0$를 정의하는 $m$개의 부등식을 하나씩 차례로 고려해 다음 집합들을 만든다.

$$\mathcal{X}_i = \left\{\begin{array}{l} x \in \mathcal{X}\\ \mathbf{R}_i x > c_i\\ \mathbf{R}_j x \le c_j,\;\forall j<i\end{array}\right\}, \qquad i = 1,\cdots,m$$

여기서 $\mathbf{R}_i$와 $c_i$는 각각 행렬 $\mathbf{R}$의 $i$번째 행과 벡터 $\mathbf{c}$의 $i$번째 성분이다. 이렇게 하면 $\mathcal{X}$가 영역 $\mathcal{X}_0, \mathcal{X}_1, \ldots, \mathcal{X}_m$으로 **분할**된다.

그리고 이 절차를 $\mathcal{X}_1,\ldots,\mathcal{X}_m$ 각각에 **재귀적으로** 적용한다. 즉 $\mathcal{X}_1$ 안에서 실현가능한 점을 찾아 대응하는 QP를 풀면 임계 영역 $\mathcal{X}_{1_0}$가 나오고, 이 $\mathcal{X}_{1_0}$를 $\mathcal{X}$ 자리에 놓고 1~3단계를 다시 반복한다.

> [!tip] 비유 — 지도를 색칠하며 넓혀 가기
> 미지의 땅에 서서 "내가 서 있는 이 구역의 규칙"을 알아냈다고 하자. 그 구역의 **경계선 하나하나를 넘어간 바깥쪽**이 아직 모르는 땅이다. 경계선을 하나씩 넘어가 그 너머에서 다시 같은 조사를 반복한다. 이미 칠한 구역은 다시 안 밟도록($\mathbf{R}_j x \le c_j,\;\forall j<i$ 조건이 이 역할을 한다) 조심하면, 언젠가 지도 전체가 칠해진다.

> [!note] 시작점은 어디로 잡는가
> [1]은 $\mathcal{X}$의 **체비쇼프 중심(Chebyshev centre)** 을 $x_0$로 제안한다. 폴리토프의 체비쇼프 중심은 LP 문제를 풀어 찾을 수 있다(그 폴리토프 안에 들어가는 가장 큰 공의 중심이다). 또한 행렬 $\mathbf{R}_a\mathbf{H}^{-1}\mathbf{R}_a^\mathrm{T}$가 **비특이(nonsingular)** 하도록 주의해야 한다[1].

### 명시적 MPC의 한계 — 영역 폭발과 그 완화

여기서 유추할 수 있듯, 명시적 MPC의 **주된 한계는 생성될 수 있는 영역의 개수가 매우 많다**는 것이고, 그 수는 **예측 구간이 길어질수록 커진다**. 이를 줄이기 위한 영역 단순화 방법이 여럿 있다[18].

- **최적 방법(Optimal Methods).** 제어 동작의 **최적성을 그대로 보존**하면서 제어기 구조만 단순화한다.
  1. **같은 제어법칙을 공유하는 영역들을 병합**해 볼록 합집합(convex union)으로 만든다.
  2. **제어 동작이 포화된 영역을 제거**하고, 이웃한 비포화 영역을 확장해서 덮는다. 이후 포화 한계를 지키기 위해 **클리핑(clipping)** 을 적용한다.
- **준최적 방법(Suboptimal Methods).** 더 단순한 조각별 함수 $f_{\text{approx}}(x)$를 최적 제어법칙 $f_{\text{opt}}(x)$와의 차이를 최소화하도록 계산한다. 예컨대 **더 짧은 예측 구간으로 MPC 문제를 먼저 풀어** 영역 수를 줄인 뒤, 원래 제어기와 근사 제어기 사이의 **제곱 오차 적분**을 최소화하는 식이다.

> [!tip] 비유 — 세금표 압축하기
> **최적 방법**은 "세율이 똑같은 인접 구간 두 개를 한 줄로 합치기"다. 표는 짧아졌지만 내는 세금은 **1원도 안 달라진다**. **준최적 방법**은 "구간을 확 줄여 대충 비슷하게 만들기"다. 표가 훨씬 짧아진 대신 세금이 조금 달라진다. 어느 쪽을 택할지는 표의 크기와 오차 허용치 사이의 거래다.

### 예제 9.3 — 이중 적분기 (The Double Integrator)

명시적 MPC의 교과서적 예제다. 영역이 실제 숫자로 어떻게 나오는지 끝까지 따라가 보자.

다음 연속시간 전달함수로 기술되는 이중 적분기(double integrator) 공정을 생각한다.

$$Y(s) = \frac{1}{s^2}U(s)$$

샘플링 시간 1 단위로 샘플링하고 두 적분기 입력 모두에 샘플 앤 홀드를 가정하면, 이산 상태공간 표현은 다음과 같다([[상태공간 모델]] 참고).

$$A = \begin{bmatrix}1 & 1\\ 0 & 1\end{bmatrix}, \qquad B = \begin{bmatrix}0\\ 1\end{bmatrix}, \qquad C = \begin{bmatrix}1 & 0\end{bmatrix}$$

> [!note] 책 본문의 $B$는 오식이다
> **책 본문은 $B = [1\;\;1]^\mathrm{T}$ 로 인쇄되어 있으나, 표 9.1의 $K$·$Q_N$ 과 Code 9.1은 $[0;1]$ 에서만 재현된다.** 이산 리카티 방정식을 직접 풀어 보면 확인된다. $B=[0;1]$ 일 때 종단 벌점이 정확히 $Q_N = \begin{bmatrix}2.1429 & 1.2246\\ 1.2246 & 1.3996\end{bmatrix}$ 이고 LQR 게인이 $K = [-0.8166\;\;-1.7499]$ 로, 표 9.1의 1번 영역 제어법칙과 일치한다. 반면 $B=[1;1]$ 이면 $K = [-0.8166\;\;-0.9333]$ 이 나와 표와 어긋난다. 그러므로 **Code 9.1의 `B = [0; 1]` 이 맞고 본문 쪽이 오식**이며, 위 본문은 바로잡아 적었다. 예제 9.4도 같은 $A$ 와 $B=[0;1]$ 을 쓴다.

**목적함수.** 다음을 최소화한다.

$$J = \sum_{j=1}^{N}\left(x(t+j)^\mathrm{T}Q_j\,x(t+j) + u(t+j-1)^\mathrm{T}R\,u(t+j-1)\right) \tag{9.18}$$

파라미터는 $N=2$, $R=0.1$이고

$$Q_j = \begin{bmatrix}1 & 0\\ 0 & 0\end{bmatrix}\;(j<N), \qquad Q_N = \begin{bmatrix}2.1429 & 1.2246\\ 1.2246 & 1.3996\end{bmatrix}$$

이다. 즉 제어기는 2차 함수 (9.18)을 최소화하는데, 이 함수는 **예측 구간 끝의 상태에도 벌점을 매긴다**(이 예제에서 $N=2$). 이 종단 벌점 $Q_N$이 어디서 왔는지가 중요하다.

> [!note] $Q_N$의 정체 — 리카티 방정식
> 각주가 밝히듯, **구간 이후에 적용되는 제어법칙**은 리카티 방정식(부록 B 참고)을 풀어 얻은 $u(t) = K\,x(t)$이며 $K = [-0.8166 \;\; -1.7499]$다. 즉 $Q_N$은 "$N$스텝 이후로는 이 LQR 게인으로 무한히 제어한다고 할 때의 비용"을 나타내는 행렬이다. 이렇게 종단 벌점을 리카티 해로 잡는 것은 5장에서 본 안정성 확보의 표준 처방이다([[리카티 방정식]], [[선형 이차 조절기 LQR]] 참고). 표 9.1의 1번 영역 제어법칙이 정확히 이 $K$와 같다는 점이 이를 확인해 준다.

**제약과 결과.** 제어 동작이 $-1\le u(t)\le 1$과 $-1\le u(t+1)\le1$로 제한될 때 **아홉 개의 영역**이 나오며, 표 9.1과 그림 9.3에 정리되어 있다(간단히 하기 위해 이 예제에서는 지평 2 이후의 제어법칙은 제약 없이 둔다).

**표 9.1 — 영역과 대응하는 제어기**

| 영역 | 정의역 $\{x : \mathbf{R}_i x \le c_i\}$ | 아핀 제어법칙 |
|---|---|---|
| 1 | $\begin{bmatrix}-0.8166 & -1.7499\\ 0.6124 & 0.4957\\ 0.8166 & 1.7499\\ -0.6124 & -0.4957\end{bmatrix}x(t) \le \begin{bmatrix}1\\1\\1\\1\end{bmatrix}$ | $u(t) = [-0.8166\;\;-1.7499]\,x(t)$ |
| 2 | $\begin{bmatrix}2.4491 & 5.2482\\ -0.8166 & -2.5665\\ 0.8166 & 2.5665\end{bmatrix}x(t) \le \begin{bmatrix}-2.9991\\ 2.7499\\ -0.7499\end{bmatrix}$ | $u(t) = 1$ |
| 3 | $\begin{bmatrix}-0.4521 & -0.3660\\ -0.5528 & -1.5364\\ 0.5528 & 1.5364\end{bmatrix}x(t) \le \begin{bmatrix}-0.7383\\ 1.4308\\ 0.5692\end{bmatrix}$ | $u(t) = [-0.5528\;\;-1.5364]\,x(t) - 0.4308$ |
| 4 | $\begin{bmatrix}-2.4491 & -5.2482\\ -0.8166 & -2.5665\\ 0.8166 & 2.5665\end{bmatrix}x(t) \le \begin{bmatrix}-2.9991\\ -0.7499\\ 2.7499\end{bmatrix}$ | $u(t) = -1$ |
| 5 | $\begin{bmatrix}0.4521 & 0.3660\\ -0.5528 & -1.5364\\ 0.5528 & 1.5364\end{bmatrix}x(t) \le \begin{bmatrix}-0.7383\\ 0.5692\\ 1.4308\end{bmatrix}$ | $u(t) = [-0.5528\;\;-1.5364]\,x(t) + 0.4308$ |
| 6 | $\begin{bmatrix}6.7349 & 18.7181\\ 2.4491 & 7.6974\end{bmatrix}x(t) \le \begin{bmatrix}-17.4314\\ -8.2474\end{bmatrix}$ | $u(t) = 1$ |
| 7 | $\begin{bmatrix}6.7349 & 18.7181\\ -2.4491 & -7.6974\end{bmatrix}x(t) \le \begin{bmatrix}-6.9349\\ 2.2491\end{bmatrix}$ | $u(t) = 1$ |
| 8 | $\begin{bmatrix}2.4491 & 7.6974\\ -6.7349 & -18.7181\end{bmatrix}x(t) \le \begin{bmatrix}2.2491\\ -6.9349\end{bmatrix}$ | $u(t) = -1$ |
| 9 | $\begin{bmatrix}-6.7349 & -18.7181\\ -2.4491 & -7.6974\end{bmatrix}x(t) \le \begin{bmatrix}-17.4314\\ -8.2474\end{bmatrix}$ | $u(t) = -1$ |

표를 읽는 법을 짚어 두자.

- **1번 영역**이 제약이 하나도 활성이 아닌 중앙 영역이다. 제어법칙이 순수한 선형 $u=Kx$이며, 상수항이 없다. 정의역 부등식 네 개는 각각 $|u|\le1$과 $|u(t+1)|\le1$이 걸리지 않을 조건이다.
- **2, 4, 6, 7, 8, 9번 영역**은 제어 입력이 **완전히 포화**된 영역이다. $u=\pm1$ 상수이므로 $K=0$, $g=\pm1$인 아핀 함수다.
- **3, 5번 영역**은 **일부만 활성**인 중간 영역이다. 게인도 있고 상수항($\mp0.4308$)도 있는 진짜 "아핀" 조각이다. 두 영역은 원점에 대해 **정확히 대칭**임을 부호로 확인할 수 있다.
- 전체적으로 표는 원점 대칭이다. 시스템과 제약이 대칭이므로 당연한 결과다.

![[mpc_fig_9_3.png]]

> [!example] 그림 9.3이 말하는 것
> 이중 적분기에 대한 **아핀 제어기 영역들**과, 초기 상태가 $x(t)^\mathrm{T} = [-5\;\;5]$일 때 시스템이 따라간 궤적을 함께 그린 것이다. 평면이 아홉 조각으로 쪼개져 있고, 각 조각이 표 9.1의 한 행에 대응한다. 가운데 있는 것이 무제약 영역(1번)이고, 바깥으로 갈수록 포화 영역이다. 궤적은 멀리 떨어진 초기 상태에서 출발해 **포화 영역들을 가로지르며** 안으로 들어오다가, 결국 가운데 무제약 영역에 진입해 원점으로 수렴한다. 최적 제어법칙(조각별 아핀 함수)을 그대로 적용했을 때의 결과다.

**구현 관점의 연산 수.** 온라인 제어기가 하는 일은 상태를 읽거나 추정하고, 그 상태가 **어느 영역에 있는지 판정**한 뒤, 대응하는 제어법칙을 적용하는 것이다. 이 예제에서 영역 판정에 드는 연산은 최악의 경우 **곱셈 48회, 덧셈 24회, 비교 24회**다.

숫자를 검산해 보자. 표 9.1의 부등식 행 개수를 다 더하면 $4+3+3+3+3+2+2+2+2 = 24$개다. 각 행은 $2$차원 상태와의 내적이므로 곱셈 2회, 덧셈 1회, 그리고 우변과의 비교 1회가 든다. 따라서 $24\times2 = 48$회 곱셈, $24$회 덧셈, $24$회 비교다. 정확히 맞는다. 제어기 자체를 계산하는 것은 **곱셈 2회와 덧셈 1회**면 끝난다($u = k_1x_1+k_2x_2 + g$).

> [!note] 계산 시간 비교 (Core i7 2.7 GHz, 16 GB RAM, MATLAB®)
> 1000개의 무작위 상태에 대한 결과다.
>
> | 방식 | 평균 계산 시간 | 표준편차 |
> |---|---|---|
> | 온라인 QP | $1.52\cdot10^{-3}$ s | $5.9\cdot10^{-4}$ s |
> | 명시적 제어기 | $2\cdot10^{-5}$ s | $7\cdot10^{-5}$ s |
>
> 약 **76배** 빠르다.

**영역 탐색을 더 빠르게 — 반공간 트리.** 가장 시간이 많이 드는 연산은 **적절한 영역을 찾는 일**이고, 계산 부담은 **영역의 개수와 각 영역을 정의하는 제약의 개수**에 달려 있다. 영역이 아주 많으면 적용할 아핀 제어법칙을 찾는 시간 자체가 병목이 된다.

이를 극복하는 아이디어는 다음 사실에 기반한다. 임계 영역을 정의하는 **각 부등식 $\mathbf{R}_i x \le r_i$는 상태 공간을 두 개의 반공간(half space)으로 나눈다.**

$$\mathcal{X}_i = \{x\in\mathcal{X} : \mathbf{R}_i x \le c_i\}, \qquad \overline{\mathcal{X}}_i = \{x\in\mathcal{X} : \mathbf{R}_i x > r_i\}$$

어떤 영역들은 $\mathcal{X}_i$에 포함되고, 어떤 영역들은 $\overline{\mathcal{X}}_i$에 포함되며, 나머지는 양쪽에 걸친다. 이제 $\mathbf{R}_i x \le r_i$를 **한 번 검사**해서 $x$가 $\mathcal{X}_i$ 안에 있다고 판정되면, $\overline{\mathcal{X}}_i$에 포함된 **모든 영역을 이후 검사에서 통째로 버릴 수 있다.**

실제로 [5]에서는 검사 횟수를 최소화하도록 부등식을 **정렬하는 알고리즘**이 제안되었다. 핵심 아이디어는 **판별력이 큰 부등식을 먼저** 고르는 것이다. 이상적인 상황은 영역의 절반이 $\mathcal{X}_i$에, 나머지 절반이 $\overline{\mathcal{X}}_i$에 들어가는 경우다.

> [!tip] 비유 — 스무고개 (책 밖 예시)
> "동물인가요?"로 후보의 절반을 날리는 질문이 좋은 질문이다. "혹시 코끼리인가요?"처럼 후보 하나만 걸러 내는 질문은 나쁜 질문이다. 좋은 질문만 고르면 $N$개 후보를 $\log_2 N$번 만에 찾아낸다. 영역 판정을 **선형 탐색에서 이진 탐색으로** 바꾸는 셈이다(복잡도 표기는 책의 서술이 아니라 이 비유를 정리한 것이다).

**오픈소스 도구.** 이런 유형의 제어기를 생성하는 오픈소스 도구들이 있다. 특히 **MPT3 툴박스**[18]로 이 예제의 명시적 MPC 제어기를 만드는 방법이 Code 9.1에 나와 있다.

```matlab
% System parameters
A = [1, 1; 0, 1];
B = [0; 1];
Q1 = [1, 0; 0, 0];
QN = [2.1429, 1.2246; 1.2246, 1.3996];
R = 0.1;
N = 2;                          % Prediction horizon

% MPT
sys = LTISystem('A', A, 'B', B);
sys.u.min = -1, sys.u.max = 1;
sys.x.penalty = QuadFunction(Q1);
sys.u.penalty = QuadFunction(R);
sys.x.with('terminalPenalty');
sys.x.terminalPenalty = QuadFunction(QN);
expc = MPCController(sys, N).toExplicit();
expc.partition.plot()
```

코드를 읽는 법은 이렇다. `toExplicit()` 메서드가 제어기를 생성하며, 상태 공간을 영역들로 분할한다. 그 분할은 `plot` 메서드로 시각화할 수 있다(그림 9.3이 바로 이 출력이다). 나아가 임의의 상태 $x$에 대한 제어 동작은 `expc.evaluate(x)` 함수로 바로 평가할 수 있는데, 이 함수가 **영역을 자동으로 판정하고 대응하는 제어법칙을 적용**한다.

---

## 9.4 명시적 MPC와 불확실 시스템 (Explicit MPC and Uncertain Systems)

파라미터 벡터에 **외란**을 포함할 수 있으므로, **min–max MPC 제어기**도 다중 파라미터 계획법의 혜택을 볼 수 있다. 이것이 흥미로운 이유는, 불확실성을 고려할 때 **가능한 모든 불확실성 실현에 대해 제약을 만족시키려면 계산 시간이 아주 길어질 수 있기** 때문이다(6장 참고).

> [!note] 이미 알고 있는 것으로 절반은 끝났다
> $\infty$-노름(또는 1-노름)을 쓰는 min–max MPC는 **LP 문제로 표현**되고, 우리는 이미 9.1.1절에서 LP의 해가 파라미터의 조각별 아핀 함수임을 보았다. 그러므로 이 경우는 자동으로 PWA다. 남은 것은 **2차 목적함수**의 경우인데, [6]에서 이 경우의 min–max MPC 제어법칙도 조각별 아핀임이 증명되었다. 이 절은 그 증명의 논리를 따라간다.

### 유계 가산 불확실성이 있는 min–max 문제

다음 문제를 생각한다([[min-max 최적화와 게임]], [[강인 제어와 불확실성 모델]] 참고).

$$\min_{\mathbf{u}}\;\max_{\theta\in\Theta}\;J(\theta,\mathbf{u},x(t))$$

$\theta\in\Theta$는 **미래의 유계 불확실성 수열**이고 $x(t)$는 공정 상태다. 선형 예측 모델을 쓰면, $j=1,\dots,N_\mathrm{p}$에 대한 $j$스텝 앞 최적 예측 집합은 다음처럼 쓸 수 있다.

$$\mathbf{y} = \mathbf{G}_u\mathbf{u} + \mathbf{G}_\theta\theta + \mathbf{F}_x x(t) \tag{9.19}$$

여기서

$$\mathbf{y} = [y(t+1)\cdots y(t+N_\mathrm{p})]^\mathrm{T}, \quad \mathbf{u} = [\Delta u(t)\cdots\Delta u(t+N_u-1)]^\mathrm{T}, \quad \theta = [\theta(t+1)\ldots\theta(t+N_\mathrm{p})]^\mathrm{T}$$

이고 $\mathbf{F}_x x(t)$는 **자유 응답**으로, 공정 상태에 선형으로 의존한다. 예측이 세 조각 — 제어 입력의 기여, 불확실성의 기여, 자유 응답 — 의 **합**으로 깔끔히 갈라진다는 것이 [[중첩의 원리|중첩 원리]] 덕분임에 주목하자.

**목적함수의 전개.** 일반성을 잃지 않고 설정값을 상수 0으로 두면, 목적함수는 다음처럼 정의된다.

$$J(\theta,\mathbf{u},x(t)) = \mathbf{u}^\mathrm{T}\mathbf{M}_{uu}\mathbf{u} + \theta^\mathrm{T}\mathbf{M}_{\theta\theta}\theta + 2\theta^\mathrm{T}\mathbf{M}_{\theta u}\mathbf{u} + 2x(t)^\mathrm{T}\mathbf{M}_{uf}^\mathrm{T}\mathbf{u} + 2x(t)^\mathrm{T}\mathbf{M}_{\theta f}^\mathrm{T}\theta + x(t)^\mathrm{T}\mathbf{F}_x^\mathrm{T}\mathbf{F}_x x(t) \tag{9.20}$$

이는 식 (9.19)를 2차 비용에 대입해 전개한 결과이며, **$\mathbf{u}$에 대한 2차항, $\theta$에 대한 2차항, 그리고 셋 사이의 교차항**들로 이루어져 있다. $\mathbf{M}_{uu}$와 $\mathbf{M}_{\theta\theta}$는 모두 **양정부호 행렬**이다.

**핵심 관찰 — 최악의 경우는 꼭짓점에서 나온다.** $\mathbf{M}_{uu}, \mathbf{M}_{\theta\theta}$가 양정부호라는 것은 $\theta$나 $\mathbf{u}$ 중 하나를 고정하면 함수 $J$가 **강볼록(strictly convex)** 임을 뜻한다([7] Theorem 3.3.8). 따라서 $\mathbf{u}$와 $x(t)$가 주어지면, $J$의 **최댓값은 폴리토프 $\Theta$의 꼭짓점 중 하나**에서 달성된다([7] Theorem 3.4.6). 그 꼭짓점을 $\theta_p$라 하자.

> [!important] 왜 이것이 결정적인가
> 6장에서 배운 그 사실이다. **볼록 함수의 최댓값은 언제나 꼭짓점에서 나온다.** 그래서 "$\Theta$ 안의 무한히 많은 $\theta$에 대해 최댓값"이라는 계산 불가능한 문제가 **"유한 개의 꼭짓점 중 최댓값"** 이라는 계산 가능한 문제로 바뀐다([[폴리토프와 꼭짓점]]).

이제 최댓값을 쓰면

$$J^*(\mathbf{u},x(t)) = \max_{\theta\in\Theta}\left\{\theta^\mathrm{T}\mathbf{M}_{\theta\theta}\theta + \mathbf{M}_\theta'(\mathbf{u})\theta + \mathbf{M}'(\mathbf{u})\right\} = \theta_p^\mathrm{T}\mathbf{M}_{\theta\theta}\theta_p + \mathbf{M}_\theta'(\mathbf{u})\theta_p + \mathbf{M}'(\mathbf{u})$$

이고, 여기서 $\theta$가 들어간 항과 안 들어간 항을 모으면

$$\mathbf{M}_\theta'(\mathbf{u}) = 2\left(x(t)^\mathrm{T}\mathbf{M}_{\theta f}^\mathrm{T} + \mathbf{u}^\mathrm{T}\mathbf{M}_{\theta u}^\mathrm{T}\right)$$

$$\mathbf{M}'(\mathbf{u}) = \mathbf{u}^\mathrm{T}\mathbf{M}_{uu}\mathbf{u} + 2x(t)^\mathrm{T}\mathbf{M}_{uf}^\mathrm{T}\mathbf{u} + x(t)^\mathrm{T}\mathbf{F}_x^\mathrm{T}\mathbf{F}_x x(t)$$

이다.

### 입력 공간의 분할 — 또 하나의 PWA 구조

따라서 $\mathbf{u}$의 정의역 $\mathcal{U}$는, **어떤 꼭짓점 $\theta_p$가 최대화자(maximizer)인가**에 따라 서로 다른 영역 $\mathcal{U}_p$로 나뉜다.

> [!tip] 비유 — 어느 적수가 나를 가장 아프게 하는가
> 내가 어떤 수($\mathbf{u}$)를 두느냐에 따라, 나를 가장 아프게 할 수 있는 **상대의 최선의 수가 달라진다.** 왼쪽으로 가면 왼쪽 함정이 제일 위험하고, 오른쪽으로 가면 오른쪽 함정이 제일 위험하다. $\mathcal{U}_p$는 **"내가 여기쯤 두면, 나를 잡는 건 $p$번 함정"** 인 영역이다. 그 영역 안에서는 상대의 수가 이미 정해진 것이나 마찬가지이므로, 문제가 갑자기 쉬워진다.

각 영역 안에서 $\theta_p$는 **상수 파라미터**로 볼 수 있으므로, $J^*(\mathbf{u},x(t))$를 다시 쓸 수 있다.

$$J^*(\mathbf{u},x(t)) = \mathbf{u}^\mathrm{T}\mathbf{M}_{uu}\mathbf{u} + \mathbf{M}_u^*(\theta_p)\mathbf{u} + \mathbf{M}^*(\theta_p) \tag{9.21}$$

여기서

$$\mathbf{M}_u^*(\theta_p) = 2\left(\theta_p^\mathrm{T}\mathbf{M}_{\theta u} + x(t)^\mathrm{T}\mathbf{M}_{uf}^\mathrm{T}\right)$$

$$\mathbf{M}^*(\theta_p) = \theta_p^\mathrm{T}\mathbf{M}_{\theta\theta}\theta_p + 2\theta_p^\mathrm{T}\mathbf{M}_{\theta f}x(t) + x(t)^\mathrm{T}\mathbf{F}_x^\mathrm{T}\mathbf{F}_x x(t)$$

이다. **$\mathbf{u}$에 대한 평범한 2차 함수**가 되었다는 점이 요점이다.

$x(t)$를 또 하나의 파라미터로 보고 헤시안 $\mathbf{M}_{uu}$가 양정부호임을 감안하면 **볼록성이 따라오고, 최소화자가 유일함이 보장**된다([7] Theorem 3.3.8). 따라서 **국소 최소점 문제가 발생하지 않는다**([7] Theorem 3.4.2). 이 **조각별 2차 함수의 최소점**이 min–max 문제의 해다.

![[mpc_fig_9_4.png]]

> [!example] 그림 9.4가 말하는 것
> $N_u = N_\mathrm{p} = 1$일 때 min–max 문제의 해가 있을 수 있는 **두 가지 위치**를 보여 준다. 이 경우 2차 함수는 딱 두 개만 나타나는데, 하나($J_1$)는 불확실성이 최댓값 $\overline{\theta}$일 때, 다른 하나($J_2$)는 최솟값 $\underline{\theta}$일 때의 비용이다. min–max 문제는 이 둘의 **위쪽 포락선**, 즉 조각별 2차 곡선 $J^*$의 최소점을 찾는 일이다.
> - **(a) 곡선의 최소점** — 두 포물선 중 하나의 꼭짓점이 위쪽 포락선 위에 있으면, 거기가 답이다.
> - **(b) 곡선들의 교점** — 두 포물선의 꼭짓점이 모두 상대편에 가려져 있으면, 답은 두 곡선이 **만나는 지점**이다. 뾰족한 V자 골짜기의 바닥이다.
>
> 즉 **2차 함수들 위의 min–max 문제의 해는 그중 하나의 최소화자이거나, 둘 이상의 교점**이다.

### 두 경우 각각에서 제어법칙은 아핀이다

**경우 (a) — 어느 한 곡선의 최소점.** 이 문제를 다르게 볼 수도 있다. 각 영역 $\mathcal{U}_p$를 **최악의 경우를 계산할 때 서로 다른 플랜트 모델을 쓰는 영역**으로 보는 것이다. 이 관점에서 min–max 해는, **공칭 모델에 극단 불확실성 실현(꼭짓점 $\theta_p$)의 기여를 더한 선형 플랜트**를 생각해 얻은 해와 같다. 결과 모델도 선형이고, 이 경우 제어법칙은 $x(t)$에 대해 아핀이다.

식 (9.21)을 $\mathbf{u}$로 미분해 0으로 놓으면 $2\mathbf{M}_{uu}\mathbf{u} + \mathbf{M}_u^*(\theta_p)^\mathrm{T} = 0$이므로

$$\mathbf{u}^* = \underbrace{-\mathbf{M}_{uu}^{-1}\mathbf{M}_{uf}}_{\mathbf{K}}\,x(t) + \underbrace{\left(-\mathbf{M}_{uu}^{-1}\mathbf{M}_{\theta u}^\mathrm{T}\right)\theta_p}_{\overline{\mathbf{u}}^*} \tag{9.22}$$

**$x(t)$에 곱해지는 게인 $\mathbf{K}$는 어느 영역에서나 같고, 상수항만 꼭짓점 $\theta_p$에 따라 달라진다**는 점이 흥미롭다. 즉 이 경우의 강인 제어기는 "공칭 LQ 제어기 + 최악 외란에 대한 오프셋 보정"의 모습이다.

**경우 (b) — 교점.** 해가 교점에서 달성되는 경우($J_i = J_j$), 문제는 다음이 된다.

$$\min_{\mathbf{u}} J_i \quad\text{s.t.}\quad J_i = J_j$$

여기서 결정적인 관찰은, **등식 $J_i = J_j$가 $\mathbf{u}$에 대한 선형 방정식**이 된다는 것이다. 왜 그런가? $J_i$와 $J_j$는 식 (9.21) 형태의 2차 함수인데, **2차항 $\mathbf{u}^\mathrm{T}\mathbf{M}_{uu}\mathbf{u}$가 둘에서 완전히 동일**하다($\theta_p$에 의존하지 않는다). 그래서 $J_i - J_j = 0$을 쓰면 2차항이 **소거되고 1차항만 남는다**. 따라서 해는 다시 상태의 **아핀 함수**다.

> [!important] 9.4절의 결론
> min–max MPC 제어법칙은 문제가 실현가능한 **모든 공정 상태 공간에서 조각별 아핀이고 연속**임이 증명되었다 — 무제약의 경우는 [8], 제약이 있는 경우는 [9]. 나아가 min–max MPC 제어기를 명시적으로 결정하는(즉 영역과 각 영역의 아핀 제어기를 결정하는) 알고리즘이 [10]에서 개발되었다. 또한 [11]에서는 시스템이 선형이면 **폐루프 min–max MPC에 대한 동적 계획법 접근**의 해 역시 상태의 조각별 아핀 함수임이 증명되었다([[동적 계획법과 최적성 원리]] 참고).

> [!warning] 대가는 여전히 크다
> 상태 공간을 나눠야 하는 **영역의 개수는 예측 구간이 길어짐에 따라 매우 빠르게 증가**한다. **활성 꼭짓점**(불확실성 폴리토프의 꼭짓점 중 min–max 해의 일부가 될 수 있는 것들)만 고려하면 이 문제를 완화할 수 있지만[12], 실용적인 예측·제어 구간 값에서는 **저장 요구량과 영역 탐색 시간이 매우 커질 수 있다.** 게다가 **공정 모델이 바뀌면 영역 계산을 처음부터 다시** 해야 한다.

### 예제 9.4 — 불확실 시스템의 명시적 min–max MPC (Explicit Min–Max MPC for an Uncertain System)

다음 시스템을 생각한다.

$$x(t+1) = A\,x(t) + B\,u(t) + D\,\theta(t)$$

$$A = \begin{bmatrix}1 & 1\\ 0 & 1\end{bmatrix}, \quad B = \begin{bmatrix}0\\ 1\end{bmatrix}, \quad D = \begin{bmatrix}1 & 0\end{bmatrix}, \quad -0.1\le\theta(t)\le0.1, \quad -1\le u(t)\le1$$

역시 이중 적분기이며, 이번에는 **가산 외란 $\theta(t)$** 가 붙어 있다. 외란 크기는 입력 크기의 1/10 수준이다.

> [!note] $D$는 열벡터로 읽어야 한다
> **책 인쇄본은 $D = [1\;\;0]$ 을 행벡터로 적고 있으나, $\theta(t)$ 가 스칼라이므로 $D\theta(t)$ 가 2차원 상태에 더해지려면 열벡터 $[1\;\;0]^\mathrm{T}$ 가 맞는다.** 전치 표기가 누락된 것이다. 의미는 **외란이 첫 번째 상태(위치)에만 직접 들어온다**는 것이다.

**제어 목표**는 상태 벡터를 최대한 0에 가깝게 만들고 유지하는 것이며, 다음 min–max 문제를 푼다.

$$\min_{\mathbf{u}\in[-1,1]^5}\;\max_{\boldsymbol{\theta}\in[-0.1,0.1]^5}\;\sum_{j=1}^{5}\left(x(t+j)^\mathrm{T}x(t+j) + 10\,u(t+j-1)^2\right)$$

지평은 5이고, 제어 가중치가 10으로 꽤 크게 잡혀 있다([[제어 가중치 람다]] 참고). 즉 **입력을 아끼는 쪽으로 튜닝된** 제어기다. 최악의 경우를 따지는 $\theta$는 $[-0.1,0.1]^5$의 **32개 꼭짓점** 중 하나가 된다($2^5=32$).

![[mpc_fig_9_5.png]]

> [!example] 그림 9.5가 말하는 것
> (a)는 가산 불확실성을 가진 시스템에 대한 **조각별 제어기 영역들**이고, (b)는 $x(0) = [-6.5668\;\;0.5789]^\mathrm{T}$에서 출발한 시뮬레이션에서의 **상태와 조작 변수의 시간 변화**다. 그림 9.3의 무외란 분할과 비교하면 영역이 더 잘게 쪼개져 있는데, 이는 서로 다른 최악 꼭짓점 $\theta_p$가 각각 자기 영역을 만들기 때문이다. 그림이 보여 주듯 조각별 제어기는 상태를 **원점의 근방까지** 데려간다. 다만 **외란 때문에 상태를 원점에 정확히 유지할 수는 없다** — 궤적이 원점 주변에서 계속 미세하게 흔들린다. 이는 6장에서 본 강인 MPC의 본질적 한계 그대로다([[튜브 기반 MPC]] 참고).

---

## 9.5 MPC의 고속 근사 구현 (Fast Approximated Implementations for MPC)

이 챕터가 보여 준 대로 MPC는 명시적 제어기로 바뀔 수 있고, 원칙적으로 **작은 문제에서는** 구현이 꽤 쉽다. 그러나 여기까지 반복해서 확인한 문제가 있다.

> **상태 공간을 나눠야 하는 영역의 개수가 예측 구간에 따라 매우 빠르게 증가한다.** 그래서 실용적인 예측·제어 구간 값에서는 저장 요구량과 영역 탐색 시간이 아주 커질 수 있다.

이런 경우 MPC를 구현하는 한 가지 방법은 **근사 제어기**를 쓰는 것이다. MPC 제어기가 $u(t) = f_\mathrm{MPC}(p(t))$로 정의되고 $p(t)$가 최소한 시스템 상태를 포함하는 파라미터라 할 때, 아이디어는 다음 **근사 오차**가 동작 영역($p(t)\in\mathcal{P}$)에서 작아지도록 함수 $\hat f_\mathrm{MPC}(p(t))$를 고르는 것이다.

$$e(p(t)) = f_\mathrm{MPC}(p(t)) - \hat f_\mathrm{MPC}(p(t))$$

> [!important] 관점의 전환
> 지금까지는 **"정확한 답을 빨리 찾자"** 였다면, 여기서부터는 **"틀려도 되니까 충분히 비슷한 답을 아주 빨리 찾자"** 로 목표가 바뀐다. MPC를 **최적화 문제**가 아니라 **근사해야 할 함수**로 보기 시작하는 것이다. 이 관점의 전환이 신경망까지 이어진다.

문헌에서 제안된 접근법들을 하나씩 보자.

### 조기 종료를 이용한 준최적 NMPC 해 (Suboptimal NMPC Solutions with Early Termination)

비선형 MPC 제어기의 실행 시간을 줄이기 위해, **솔버를 제한된 반복 횟수 후에 중단**해서 준최적 해를 얻고, 이를 **이후의 샘플링 시각에서 보정**해 나가는 방법이다[19].

> [!tip] 비유 — 시험 시간이 부족할 때
> 한 문제를 완벽하게 푸느라 시간을 다 쓰는 대신, **일단 그럴듯한 답을 적고 다음 문제로 넘어간다.** 그리고 시간이 남으면 돌아와서 고친다. MPC는 어차피 **매 샘플마다 다시 푸는** [[이동 구간 원리 Receding Horizon|이동 구간]] 방식이므로, 이번에 덜 푼 것을 다음번에 이어서 개선할 기회가 있다.

전형적으로 이 방식은 **만족스러운 준최적 성능**을 주면서 계산 부담을 크게 줄인다. 예를 들어 SQP 솔버는 매 시간 스텝에서 **뉴턴 스텝 한 번**만 수행할 수 있다. 이때 이전에 시프트한 궤적에 기반해 선형화한 모델을 쓰고(**웜 스타트를 동반한 준비 단계, preparation phase**), 가장 최근의 상태 정보를 반영하는(**피드백 단계, feedback phase**) 식으로 나누면, 계산 부담이 **선형 MPC와 비슷한 수준**이 된다[19]. 7장에서 소개한 **continuation/GMRES NMPC** 방법[20]도 유사한 접근을 따른다.

### 무브 블로킹 (Move Blocking)

또 하나의 인기 있는 근사 기법으로, **연속된 여러 개의 미래 제어 동작을 하나의 결정 변수로 묶어** 결정 변수의 개수를 줄인다[21,22].

예컨대 제어 입력 $u(t+k)$가 매 샘플링 시각 $k = 0,1,\ldots,N_\mathrm{p}-1$마다 다를 수 있게 두는 대신, $k=0,2,\ldots$에 대해 $u(t+k) = u(t+k+1)$을 강제하는 식이다. 제어 수열을 만드는 최적화 변수가 줄어들므로 **최적화 문제의 차원이 작아지지만, 최적성은 어느 정도 손해**를 본다.

> [!tip] 비유 — 운전대를 몇 초마다 잡을 것인가
> 고속도로에서 1초마다 핸들을 미세 조정하는 대신 **"앞으로 5초 동안은 이 각도 유지"** 라고 정하면, 결정할 것이 5분의 1로 줄어든다. 대신 그 5초 안에 딱 맞는 조정을 놓칠 수 있다.

전형적으로 블로킹은 **근시안적(myopic) 방식**을 따른다. **가까운 미래에는 짧은 블록**을, **먼 미래로 갈수록 긴 블록**을 쓰는 것이다. 이는 자연스러운 선택인데, 어차피 이동 구간 원리 때문에 **실제로 적용되는 것은 첫 번째 제어 동작뿐**이므로 먼 미래는 대충 잡아도 손해가 적기 때문이다. 수자원 시스템 제어를 위한 **적응형 제어 해상도(adaptive control resolution)** 기법[23]이 이 아이디어를 사용한다.

> [!warning] 안정성에 영향을 준다
> 결정 변수를 이렇게 묶는 과정은 **안정성에도 영향을 미친다**. 어떤 기준에 따라 최적의 블로킹을 찾는 방법들이 제안되어 있다[22].

### 룩업 테이블 (Look-Up Tables)

MPC의 빠른 근사를 달성하는 가장 단순하면서도 효과적인 전략에 속하며[24], **전력 전자** 같은 응용에서 볼 수 있다[25].

이 방법은 두 단계로 이루어진다.

1. **오프라인 단계** — 상태-입력 공간의 **대표점들**에 대해 최적 제어 동작을 미리 계산해 테이블에 저장한다.
2. **온라인 단계** — 제어기가 룩업 테이블을 **조회**해 적절한 제어 동작을 계산한다. 필요하면 테이블에서 **가장 가까운 원소들의 해를 보간(interpolation)** 한다.

상태-입력 공간을 **균일하게 이산화**하고 테이블을 **격자 형태**로 구성하면, 알맞은 테이블 항목을 **단순한 인덱스 산술**로 빠르게 찾을 수 있다.

> [!tip] 비유 — 삼각함수표
> 계산기가 없던 시절 $\sin 37.4°$를 구하려면 삼각함수표를 펴서 $37°$와 $38°$ 값을 찾아 그 사이를 **비례로 나눴다**. 정확한 값은 아니지만 실용적으로 충분했고, 무엇보다 **즉시** 나왔다. 룩업 테이블 MPC가 정확히 이것이다.

> [!warning] 차원의 저주
> 그러나 **문제의 크기가 커질수록 메모리 요구량과 보간의 복잡도 때문에 효율이 떨어진다.** 각 축을 $N$개로 나누면 $n$차원 공간에서는 $N^n$개의 항목이 필요하다. 상태가 2개면 표 하나, 5개면 감당 불가다. (보간이 계산 오버헤드를 조금 더하지만, 온라인 최적화보다는 여전히 훨씬 빠르다.)

### 모델 예측 경로 적분 제어 (Model Predictive Path Integral Control, MPPI)

MPPI는 MPC의 **샘플링 기반 확률적 버전**이다[26,27]. 최적화 문제를 푸는 대신, **여러 궤적을 앞으로 시뮬레이션해 보고 성능에 따라 가중치를 매기는** [[몬테카를로와 시나리오 근사|몬테카를로]] 방식을 따른다.

따라서 **QP나 LP를 풀 필요도 없고, 명시적 다중 파라미터 해도 필요 없다.** 필요한 것은 **확률적 샘플링과 비용 평가**뿐이다. 각 궤적이 서로 독립이므로 **병렬화가 쉽다** — 예컨대 GPU를 쓸 수 있다. 다만 생성되는 해는 **준최적이고 폐루프 제약 만족을 보장하지 못할 수 있다.**

**알고리즘.** 각 샘플링 시각에서 MPPI가 하는 일을 단계로 정리하면 다음과 같다.

1. **공칭 입력 수열 $\mathbf{u}_0$에서 출발**한다(예: 이전 해를 시프트하거나 휴리스틱 추측).
2. **$M$개의 섭동된 수열을 생성**한다. $\mathbf{u}_i = \mathbf{u}_0 + \boldsymbol\nu_i$, $i=1..M$이며 $\boldsymbol\nu_i$는 **평균 0, 공분산 $\Sigma$의 가우시안 분포**에서 뽑은 수열이다. 공분산 $\Sigma$는 서로 다른 입력 수열을 **얼마나 공격적으로 탐색**할지 결정한다.
3. **각 수열의 궤적을 시뮬레이션**한다. 내부 모델 $x(t+1) = f(x(t),u(t)) + w(t)$를 쓰며, $w(t)$는 확률적 외란 벡터다.
4. **각 궤적에 비용을 매긴다.**
$$J(\mathbf{x}_i,\mathbf{u}_i) = \mathbb{E}\left[\sum_{k=t}^{t+N_\mathrm{p}-1}\ell\left(x_i(k),u_i(k)\right) + \ell_N\left(x(t+N_\mathrm{p})\right)\right]$$
여기서 $\ell(\cdot)$과 $\ell_N(\cdot)$은 각각 **단계 비용(stage cost)** 과 **종단 비용(terminal cost)** 함수다.
5. **비용으로 가중 평균해 제어 수열을 갱신**한다.
$$\mathbf{u} = \frac{\displaystyle\sum_{i=1}^{M}\mathbf{u}_i\,e^{-\frac{1}{\lambda}J(\mathbf{x}_i,\mathbf{u}_i)}}{\displaystyle\sum_{i=1}^{M}e^{-\frac{1}{\lambda}J(\mathbf{x}_i,\mathbf{u}_i)}}$$
$\lambda$는 얻어진 비용들에 가중치를 매기는 파라미터다.
6. 늘 그렇듯 **$\mathbf{u}$의 첫 번째 원소만 플랜트에 적용**한다.

가중치 $e^{-J/\lambda}$의 의미를 뜯어 보자. **비용이 낮을수록 지수의 값이 커지므로 가중치가 크다.** 따라서 제어 수열은 **더 낮은 비용을 주는 수열 $\mathbf{u}_i$ 쪽으로 이동**한다. $\lambda$가 작으면 최고 성능 수열 하나에 거의 모든 가중치가 쏠리고(탐욕적), $\lambda$가 크면 모든 수열을 고르게 평균한다(보수적).

> [!tip] 비유 — 학급 평균이 아니라 성적 가중 평균
> 학생 1000명에게 각자 다른 답을 내게 하고, **점수가 높은 답에 더 큰 목소리를 주어 평균**을 낸다. 아무도 정답을 모르지만, 잘한 답들 쪽으로 계속 끌려가다 보면 꽤 좋은 답에 도달한다. 미분도, 볼록성도 필요 없다 — **비용을 계산할 수만 있으면 된다.** 이것이 MPPI가 비선형·비볼록 문제에 강한 이유다.

### 힌징 초평면 (Hinging Hyperplanes, HH)

**힌징 초평면**도 조각별 선형 모델을 표현하는 데 쓰였다[13,14]. HH 기법은 **힌지 함수(hinge functions)**, 즉 **경첩처럼 이어 붙인 초평면들**을 사용하는 비선형 함수 근사 방법이다.

이 기법을 쓰면 **MPC 제어기처럼 조각별 선형인 함수들을 기저 함수 전개(basis function expansion)로 기술**할 수 있다([[기저 함수와 일치점]] 참고). HH 기법은 MPC 맥락에서 [13]에 쓰였고, [14]에서는 **열교환기용 min–max MPC 구현**에 사용되었다.

> [!tip] 비유 — 경첩 달린 판자
> 평평한 판자 두 장을 경첩으로 이어 붙이면 $\max(0, ax+b)$ 같은 **꺾인 모양**이 하나 생긴다. 이런 경첩 여러 개를 겹쳐 더하면 아무리 복잡한 꺾인 면도 만들 수 있다. 명시적 MPC 제어법칙이 정확히 이런 꺾인 면이므로, **영역 목록을 다 저장하는 대신 경첩 몇 개의 계수만 저장**하면 되는 것이다.

> [!important] 근사면 충분한가 — 그렇다, 자주
> 근사가 **충분히 좋다면**(즉 근사 오차가 **디지털-아날로그 변환의 변환 오차보다 작다면**), 근사 구현은 **실용적 관점에서 정확한 MPC와 전혀 다르지 않다**. 어차피 제어 신호는 D/A 변환기를 거쳐 나가고, 거기서 양자화 오차가 생긴다. 그보다 작은 오차는 **물리적으로 관측조차 되지 않는다.**

### 인공 신경망 (Artificial Neural Networks, ANN)

[[인공신경망 ANN]] 기반 제어기는 **비선형 함수를 학습하는 신경망의 능력**, 또는 **대규모 병렬 계산이 필요한 특정 문제를 푸는 능력**을 활용한다.

ANN의 학습 능력은 제어기가 어떤 함수를 학습하게 하는 데 쓰이며, 그 함수는 대개 고도로 비선형인 **정방향 동특성(direct dynamics), 역동특성(inverse dynamics), 또는 공정의 다른 특성**을 나타낸다. 이것은 보통 제어기를 시운전(commissioning)할 때의 **(대개 긴) 학습 기간** 동안 지도(supervised) 또는 비지도(unsupervised) 방식으로 이루어진다.

**쓰임새는 두 갈래**다.

- **플랜트를 모델링**하는 데 쓰는 경우. 예컨대 [15]에서는 신경망이 MPC 체계 안에서 **태양열 플랜트의 자유 응답**을 모델링하는 데 쓰였고, [16]에서는 ANN으로 비선형 MPC를 구현했다.
- **제어기 자체를 모델링**하는 데 쓰는 경우 — 이 절이 다루는 방식이다. 먼저 보통 긴 학습 단계에서 ANN을 **제어기를 흉내 내도록** 조정한 다음, 제어기를 시운전한다.

> [!important] 학습 = 오프라인 계산
> ANN의 **학습 단계는 이 챕터에서 다룬 명시적 제어기를 얻기 위한 오프라인 계산과 정확히 같은 역할**이다. 명시적 MPC가 "영역과 아핀 게인의 표"를 오프라인에서 만든다면, 신경망 MPC는 "가중치 행렬들"을 오프라인에서 만든다. **둘 다 온라인에서는 조회 또는 몇 번의 행렬 곱셈뿐**이다. ANN이 일단 동작하기 시작하면 필요한 계산량은 매우 적고, 고속 구현 방법들의 온라인 계산과 견줄 만하다.

### 사장 시간이 있으면 차원이 폭발한다

이 챕터에서 소개한 방법들에 대한 **마지막 고려사항**이 하나 있다. 이 방법들의 복잡도는 **벡터 차원에 크게 의존**하는데, 이 차원은 **사장 시간(dead time)이 긴 공정에서 매우 커질 수 있다.** 산업 현장에서 흔한 상황이다.

사장 시간이 $t_\mathrm{d}$ 샘플링 시각인 경우, $p(t)$는 최소한 다음 **증강 상태 벡터**를 포함해야 한다.

$$x_a(t) = \left[x(t)^\mathrm{T}\;\; u(t-1)^\mathrm{T}\;\; u(t-2)^\mathrm{T}\;\ldots\;\; u(t-t_\mathrm{d})^\mathrm{T}\right]$$

즉 온라인 함수를 **증강 상태 $x_a(t)$의 정의역 위에서 정의**해야 한다. 왜 그런가? 사장 시간이 있으면 **이미 내보냈지만 아직 출력에 나타나지 않은 과거 입력들**이 "파이프 안에 떠 있는" 상태이고, 미래를 예측하려면 그것들을 다 알아야 하기 때문이다([[스미스 예측기]] 참고).

**해결책.** 사장 시간 때문에 벡터 차원이 커지는 것은 매우 제한적일 수 있으므로, 대신 $p(t)$에 **예측 상태 $\hat x(t+t_\mathrm{d}\mid t)$** 를 포함하면 이 문제를 완화할 수 있다[17]. 이는 시각 $t$에서 이용 가능한 정보만으로 문제없이 계산할 수 있다.

> [!tip] 왜 이것이 이득인가
> 증강 상태를 쓰면 차원이 $n_x + t_\mathrm{d}\cdot n_u$로 커진다. 사장 시간이 10샘플이고 입력이 2개면 상태 차원에 20이 더 붙는다. 명시적 MPC의 영역 개수는 차원에 지수적으로 늘어나므로 **치명적**이다. 반면 **미리 $t_\mathrm{d}$ 스텝 앞을 예측한 상태 하나**를 넣으면 차원은 $n_x$ 그대로다. 과거 입력들의 정보가 이미 그 예측값 안에 **접혀 들어가 있기** 때문이다.

### 예제 9.5 — 태양열 파라볼릭 트로프 플랜트의 딥러닝 MPC (Deep Learning MPC for a Solar Parabolic-Trough Plant)

8장에서 소개한 **10 루프 집열기 필드 ACUREX**를 생각한다. [28]에서는 집열기 필드에 공급되는 **유량을 제어하는 MPC를 심층 신경망으로 근사**하는 것의 효과를 평가하는 벤치마크로 이 시스템을 사용했다. MPC는 각 루프에 **같은 유량**을 설정하며, 목적은 **온도와 유량의 한계를 지키면서 생성되는 순 열출력(net thermal power)을 최대화**하는 것이다. 사용된 방정식은 8장의 것이고, 제어기 내부 비선형 모델과 파라미터의 추가 세부사항은 [28]에서 찾을 수 있다.

**다층 퍼셉트론.** 7장에서 배웠듯 인공 신경망은 생물학적 뉴런의 입출력 응답을 모방한 노드들의 상호 연결에서 비롯한 함수 $f_{NN}(\cdot)$으로 특징지어진다. 이 예제에서는 **다층 퍼셉트론(multilayer perceptron)**, 즉 모든 뉴런이 **입력의 가중합**에 기반해 출력을 활성화하는 순방향(feedforward) 신경망을 고려한다. 그 입력은 앞 층의 출력에 해당한다.

$$z_i^{(l)} = g^{(l)}\left(\sum_{j=1}^{n^{(l-1)}} w_{ji}^{(l-1)}\,z_j^{(l-1)} + b_i^{(l-1)}\right)$$

기호를 하나씩 짚자.

| 기호 | 뜻 |
|---|---|
| $z_i^{(l)}$ | 층 $l$의 $n^{(l)}$개 뉴런 중 $i$번째 뉴런의 출력 |
| $w_{ji}^{(l-1)}$ | 층 $l-1$의 뉴런 $j$와 $i$ 사이의 커널(가중치) |
| $b_i^{(l-1)}$ | 층 $l-1$의 뉴런 $i$의 바이어스 |
| $g^{(l)}$ | 층 $l$의 활성화 함수 |

위첨자 $(l)$은 해당 층을 강조하기 위해 붙였다. 고려된 활성화 함수 $g^{(l)}$는 **출력층을 제외한 모든 층에서 쌍곡탄젠트(hyperbolic tangent)** 이고, **출력층은 선형 함수**를 쓴다.

> [!note] 왜 출력층만 선형인가
> 은닉층의 $\tanh$는 출력을 $[-1,1]$로 짓눌러 비선형성을 만든다. 그런데 제어 출력인 **유량은 물리적 단위를 가진 실수**이므로, 마지막에서 $[-1,1]$로 눌리면 곤란하다. 그래서 출력층만 선형으로 두어 **임의의 실수값**을 낼 수 있게 한다. 회귀(regression) 문제 신경망의 표준적 구성이다.

**깊은 신경망이란.** $f_{NN}(\cdot)$의 복잡도는 **은닉층(hidden layer)** — 즉 ANN의 입력층과 출력층 사이의 층 — 의 개수에 따라 증가한다. 은닉층이 **하나뿐이면 얕은(shallow)**, **둘 이상이면 깊은(deep)** 신경망이라 부른다. 이 예제에서는 학습에 쓸 **30일치 합성 데이터셋**을 제공한 비선형 MPC 제어기를 가장 정확하게 흉내 내는 것으로 **은닉층 2개짜리 ANN**이 선택되었다(그림 9.6).

![[mpc_fig_9_6.png]]

> [!example] 그림 9.6이 말하는 것
> Acurex 필드에서 NMPC 제어기의 출력을 근사하는 데 사용된 **신경망 구조**다. 이 망은 **410개의 입력**을 가지며, 이는 입력 벡터의 성분들에 해당한다.
> $$z_1^{(1)}(k) = \left[q(k-1),\,T_{\text{in}}(k),\,T_{\text{out}}(k),\,T_a(k),\,T_f^i(k),\,T_m^i(k),\,I_i(k),\ldots,I_i(k+N_p-1)\right]$$
> 여기에는 **이전 시간 스텝의 유량** $q(k-1)$, **입구 온도** $T_{\text{in}}(k)$, **출구 온도** $T_{\text{out}}(k)$, **주위 온도** $T_a(k)$, **구간별 유체·금속 온도** $T_f^i(k)$와 $T_m^i(k)$, 그리고 **예측 구간 $N_p$에 걸친 일사량 예측** $I_i(k)$가 포함된다. ANN은 각 시간 스텝에서 **최적화된 유량 $\hat q(k)$** 를 계산하며, 이것이 고려된 NMPC 제어기의 출력과 일치한다.
>
> 입력이 410개나 되는 이유를 눈여겨보자. 구간별 온도들과 **예측 구간 전체에 걸친 일사량 예보**가 전부 입력이기 때문이다. 이는 앞서 말한 파라미터 벡터 $\mathbf{p}$가 **상태 + 측정 가능한 외란(일사량) 예보**를 모두 포함하는 경우에 정확히 해당한다. 이런 차원에서 명시적 MPC의 영역 분할은 **완전히 불가능**하다 — 신경망 근사가 유일한 현실적 선택인 이유다.

![[mpc_fig_9_7.png]]

> [!example] 그림 9.7이 말하는 것
> 주어진 **직달 일사량(direct normal irradiance) 프로파일**에 대해, NMPC 제어기와 설계된 ANN 각각의 **유량, 출구 온도, 열출력**의 시간 변화를 비교한 것이다. 세 변수의 변화가 시뮬레이션에 쓰인 일사량 프로파일과 연동되어 있음에 주목하라(구름이 지나가면 일사량이 떨어지고, 유량과 온도가 따라 반응한다).
>
> 그림이 보여 주듯 **신경망은 NMPC와 상당히 비슷한 궤적을 만들어 내되, 더 매끄럽다**. 이는 **펌프의 내구성을 높이는 데 유리**하지만, 대신 **제약을 가끔, 그리고 약간 위반**할 수 있다. (다만 NMPC 제어기를 다르게 튜닝해도 그런 매끄러운 변화를 얻을 수 있다는 점은 유의해야 한다.)

> [!important] 계산 시간 — 이 챕터의 결론을 상징하는 숫자
> | 방식 | 최대 계산 시간 |
> |---|---|
> | NMPC (순차 이차계획법 SQP) | 2.5 s 미만 |
> | ANN | $3.5\cdot10^{-3}$ s 미만 |
>
> ANN이 대응하는 NMPC보다 **700배 이상 빠르게** 동작했다. 이 속도 이득은 **수백 개의 루프를 가질 수 있는 상업용 플랜트에서 적용 가능성을 가르는 차이**를 만들 수 있다.

---

## 9.6 연습문제 (Exercises) 훑어보기

책의 연습문제 여섯 개를 한 줄씩 요약하고, 무엇을 연습시키려는지와 접근 힌트를 붙인다.

**9.1 명시적 MPC의 아핀성을 증명하라.**
9.1절의 유도를 스스로 재현하는 문제다. **힌트** — 두 상황(제약 비활성 / 활성)으로 나누고, 활성인 경우는 $\mathbf{u}=\mathbf{Y}\mathbf{c}_a+\mathbf{Z}\mathbf{v}$ 치환으로 등식 제약을 제거한 뒤, $\mathbf{b}$와 $\mathbf{c}_a$가 $x(t)$의 아핀 함수라는 사실을 마지막에 쓴다. **연습시키는 것** — "아핀의 아핀은 아핀"이라는 이 챕터의 논리 골격.

**9.2 $\infty$-노름 경우의 명시적 MPC 제어기를 유도하라.** 즉 최적화 문제가 다음일 때다.
$$\min_{\mathbf{u}}\;\left\|\mathbf{r}-\left(\mathbf{G}\mathbf{u}+\mathbf{F}x(t)\right)\right\|_\infty \qquad \text{s.t.}\;\;\mathbf{R}\mathbf{u}\le\mathbf{V}x(t)+\mathbf{c}^b$$
**힌트** — 9.1.1절의 1-노름 유도를 그대로 흉내 내되, $\infty$-노름은 "**최댓값**"이므로 보조 변수가 **하나면 충분**하다. $\mu \ge r_i - (\mathbf{G}\mathbf{u}+\mathbf{F}x)_i$와 $\mu \ge -(r_i - (\cdots)_i)$를 **모든 $i$에 대해** 걸고 $\mu$를 최소화하면 된다. 1-노름은 성분별 보조 변수 $\alpha$가 필요했지만 $\infty$-노름은 스칼라 하나다. **연습시키는 것** — 노름의 종류가 LP 정식화의 보조 변수 구조를 어떻게 바꾸는가.

**9.3 동적 계획법을 써서, 선형 시스템에 대한 폐루프 min–max MPC가 상태의 조각별 아핀 함수임을 증명하라.** 문제는 다음 재귀 문제를 고려하라고 안내한다.
$$J_t^*(x(t)) \triangleq \min_{u(t)} J_t(x(t),u(t))$$
$$\text{s.t.}\quad \left.\begin{array}{r}\mathbf{R}_x x(t) + \mathbf{R}_u u(t) \le r\\ f(x(t),u(t),\theta(t)) \in \mathcal{X}(t+1)\end{array}\right\}\;\forall\theta(t)\in\Theta$$
$$J_t(x(t),u(t)) \triangleq \max_{\theta(t)\in\Theta} L(x(t),u(t)) + J_{t+1}^*(x(t+1))$$
여기서 $\mathcal{X}(t+1)$은 함수 $J_{t+1}^*(x(t+1))$이 정의되는 영역이다. 시스템은
$$x(t+1) = A(\theta(t))x(t) + B(\theta(t))u(t) + E(\theta(t))$$
$$A(\theta(t)) = A_0 + \sum_{i=1}^{n_\theta} A_i\theta^i(t), \quad B(\theta(t)) = B_0 + \sum_{i=1}^{n_\theta}B_i\theta^i(t), \quad E(\theta(t)) = E_0 + \sum_{i=1}^{n_\theta}E_i\theta^i(t)$$
이고 $\theta^i(t)$는 불확실성 벡터 $\theta(t)\in\Theta$의 $i$번째 성분이다. 단계 비용과 종단 비용은
$$L(x(t+j),u(t+j)) \triangleq \|Q\,x(t+j)\|_p + \|R\,u(t+j)\|_p, \qquad J_{t+N}^*(x(t+N)) \triangleq \|P\,x(t+N)\|_p$$
이다. **힌트** — **뒤에서 앞으로(backward) 귀납법**을 쓴다. 종단 비용 $\|Px(t+N)\|_p$는 ($p=1$ 또는 $\infty$이면) 조각별 아핀이고, "조각별 아핀 함수의 최댓값도 조각별 아핀", "조각별 아핀 함수를 선형 제약 아래 최소화한 값함수도 조각별 아핀"이라는 두 보조 사실을 쓰면 $J_t^*$가 한 단계씩 조각별 아핀으로 전파된다. **연습시키는 것** — 9.4절의 결과[11]를 동적 계획법 언어로 재구성하기.

**9.4 명시적 MPC의 복잡도를 차원의 함수로 논하라.** $\dim(x(t))=n_x$, $\dim(y(t))=n_y$, $\dim(u(t))=n_u$, $\dim(p(t))=n_p$(측정 가능 외란)이고 예측·제어 지평이 $N$이며, 제약이 $\mathbf{R}\mathbf{u}\le\mathbf{V}x(t)+\mathbf{c}$($\mathbf{R}$은 $m\times(N\times n_u)$)일 때, **최대 영역 개수, 필요한 저장 공간 크기, 명시적 MPC 구현에 필요한 곱셈·덧셈·비교 횟수**를 $n_x,n_u,n_p,m,N$의 함수로 논하라. **힌트** — 최대 영역 수는 활성 제약 조합 수이므로 $2^m$이 상한이다. 저장 공간은 영역당 (부등식 행렬 + 게인 + 상수항)이고, 연산 수는 예제 9.3에서 손으로 센 방식(부등식 행 수 × 파라미터 차원)을 일반화하면 된다. **연습시키는 것** — 이 챕터가 반복해 경고한 "영역 폭발"을 숫자로 체감하기.

**9.5 주어진 이중 적분기 명시적 MPC(예제 9.3)를 다뤄 보라.**
1. 제어기를 시뮬레이션하는 프로그램을 작성하고, $\|x(t)\|_\infty \le 5$인 여러 초기 상태에 대해 응답을 시뮬레이션하라. **모든 궤적이 원점으로 수렴하는가?**
2. 제어기의 **흡인 영역(attraction region)** 을 구하라.
3. $N=3$으로 제어기를 다시 계산하고 1을 반복하라. **제어 지평을 늘리면 흡인 영역이 넓어지는가?**

**힌트** — 표 9.1을 그대로 코드로 옮기고, 매 스텝 아홉 개 영역의 부등식을 검사해 해당 제어법칙을 적용하면 된다. 3번의 답은 일반적으로 "그렇다"인데, 지평이 길수록 제약 안에서 원점으로 되돌아올 수 있는 상태가 많아지기 때문이다([[재귀적 실현가능성]], [[불변 집합 Invariant Set]] 참고). **연습시키는 것** — 명시적 제어기를 직접 구현해 보고, 지평 길이와 실현가능 영역의 관계를 체감하기.

**9.6 측정 가능한 외란이 있는 시스템의 명시적 MPC.** $x(t+1) = 0.9x(t) + u(t) + p(t)$, $-1\le u(t)\le 1$, $J = \sum_{j=1}^{N}\left(x(t+j)^2 + \lambda u(t+j-1)^2\right)$이고 $p(t)$는 **측정 가능한 외란**이다.
1. 측정 가능한 외란을 고려한 명시적 MPC를 **어떻게 얻는지 설명하라.**
2. $N=2$에 대한 명시적 제어기를 구하라. 미래 외란은 현재 측정 외란과 같다고 추정하며($p(k+j)=p(k)$, $j=1,\ldots,N$), 제어 가중치는 $\lambda=1$이다.
3. 미래 외란이 $p(k+j+1) = 2p(k+j) - p(k+j-1)$($j=1,\ldots,N$)로 계산된다면 **무엇을 해야 하는지 지적하라.**

**힌트** — 1번의 답이 9.2절 전체다. 파라미터 벡터를 $\mathbf{p} = [x(t)\;\;p(t)]^\mathrm{T}$로 잡으면 되며, 예제 9.2에서 기준값 $\bar r$을 파라미터에 넣은 것과 **완전히 같은 트릭**이다. 3번은 외란 예측이 $p(k)$와 $p(k-1)$ **두 값의 선형 결합**이 되므로 파라미터 벡터를 $[x(t)\;\;p(k)\;\;p(k-1)]^\mathrm{T}$로 **한 차원 더 늘려야** 한다는 것이 답이다. **연습시키는 것** — 파라미터 벡터의 설계가 곧 명시적 MPC 설계라는 감각.

---

## 요약

1. **모든 것의 출발점은 한 문장이다.** QP·LP의 최적해는 **활성 제약 집합**이 결정하고, 활성 집합이 같은 영역 안에서는 해가 상태의 **아핀 함수**다. 그래서 제약이 있는 MPC의 제어법칙은 **조각별 아핀(PWA)** 이 된다. 2차 목적함수든(9.1절), 1-노름·$\infty$-노름이든(9.1.1절) 결론은 같다.

2. **다중 파라미터 계획법이 이를 일반화한다**(9.2절). KKT 조건에서 출발해 $\mathbf{u}_a^*(\mathbf{p}) = \mathbf{K}_a\mathbf{p} + \overline{\mathbf{u}}_a$ (식 9.15)를 얻고, 영역 $\mathcal{P}_a$는 "비활성 제약이 계속 비활성"(9.16)과 "활성 승수가 양수"(9.17)라는 **두 부등식 집합**으로 정의된다. 파라미터 $\mathbf{p}$에 상태뿐 아니라 **기준값과 측정 가능한 외란**도 넣을 수 있다(예제 9.2).

3. **영역은 재귀적으로 찾고, 탐색은 반공간 트리로 가속한다**(9.3절). 실현가능한 점에서 QP를 풀어 영역 하나를 확정하고, 그 경계 부등식을 하나씩 넘어가며 재귀한다. 온라인 부담의 대부분은 **영역 판정**이므로, 판별력 큰 부등식부터 검사해 후보를 절반씩 쳐내는 것이 핵심이다[5]. 이중 적분기 예제(예제 9.3)에서는 9개 영역, 최악의 경우 곱셈 48회로 온라인 QP보다 **약 76배** 빨랐다.

4. **불확실성이 있어도 여전히 PWA다**(9.4절). $\infty$-노름 min–max는 LP라 자동이고, 2차 목적함수 min–max도 [6]에서 PWA임이 증명되었다. 논리는 "**최악의 경우는 폴리토프 $\Theta$의 꼭짓점에서 나온다**"이며, 최대화 꼭짓점 $\theta_p$에 따라 입력 공간이 영역 $\mathcal{U}_p$로 갈린다. 해는 각 2차 곡선의 최소점이거나 **곡선들의 교점**이고(그림 9.4), 두 경우 모두 상태의 아핀 함수다.

5. **영역 폭발이 명시적 MPC의 아킬레스건이다.** 영역 개수는 예측 구간과 파라미터 차원에 따라 매우 빠르게 늘고, 사장 시간이 있으면 증강 상태 때문에 더 심해진다. 완화책은 영역 병합·포화 영역 제거(최적 방법)와 짧은 지평 근사(준최적 방법)[18], 그리고 예측 상태 $\hat x(t+t_\mathrm{d}\mid t)$의 사용[17]이다.

6. **감당이 안 되면 근사한다**(9.5절). **조기 종료 NMPC**[19], **무브 블로킹**[21,22], **룩업 테이블**[24], **MPPI**[26,27], **힌징 초평면**[13,14], **신경망**이 그 목록이다. 관점이 "정확한 답을 빨리"에서 **"충분히 비슷한 답을 아주 빨리"** 로 옮겨간다. 근사 오차가 **D/A 변환 오차보다 작으면 실용적으로는 정확한 MPC와 구별되지 않는다.**

7. **ACUREX 태양열 플랜트 예제(예제 9.5)가 이 챕터를 상징한다.** 입력 410개짜리 은닉층 2개 신경망이 NMPC를 흉내 내어, 최대 2.5초 걸리던 계산을 **3.5 ms 미만**으로 — **700배 이상** — 줄였다. 신경망의 **학습 단계는 명시적 MPC의 오프라인 영역 계산과 정확히 같은 역할**을 한다.

**다음 챕터 예고.** 이 챕터로 우리는 "MPC를 어떻게 빠르게 실행할 것인가"라는 구현 측면의 질문에 답했고, 이로써 이론과 구현 기법이 모두 갖춰졌다. 이어지는 [[Chapter 10 - 응용 사례]]에서는 **9장까지 배운 도구들이 실제 공정에서 어떻게 쓰이는지**를 다섯 가지 사례로 확인한다. 태양열 발전소(Acurex 분산 집열기, Mojave Beta), 올리브유 공장의 써모믹서, 수소 저장과 배터리를 갖춘 파일럿 마이크로그리드, 병원 재고 관리, 그리고 구리 주조 플래시 용광로의 압력 제어다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[조각별 아핀 PWA와 명시적 MPC]]
- [[다중 파라미터 계획법 Multiparametric Programming]]
- [[임계 영역과 상태 공간 분할]]
- [[KKT 조건]]
- [[활성 집합법 Active Set Method]]
- [[볼록 최적화와 이차계획법 QP]]
- [[선형계획법과 1-노름 목적함수]]
- [[폴리토프와 꼭짓점]]
- [[영공간과 유사역행렬]]
- [[min-max 최적화와 게임]]
- [[무브 블로킹과 룩업 테이블]]
- [[모델 예측 경로 적분 제어 MPPI]]
- [[힌징 초평면과 함수 근사]]
- [[인공신경망 ANN]]
- [[사장 시간과 증강 상태]]

## 한눈에 보는 개념 지도

| 개념 | 기호 | 한 줄 뜻 |
|---|---|---|
| 활성 제약 집합 | $a$ | 최적점에서 등호로 걸려 있는 제약들의 조합. 이것이 조각을 결정한다 |
| 비활성 제약 집합 | $\bar a$ | 여유가 있어 답에 영향을 주지 않는 제약들 |
| 임계 영역 | $\mathcal{X}_a$, $\mathcal{P}_a$ | 같은 활성 집합이 유지되는 상태(파라미터) 공간의 다면체 조각 |
| 아핀 제어법칙 | $\mathbf{u}_a^*=\mathbf{K}_a\mathbf{p}+\overline{\mathbf{u}}_a$ | 각 조각에서 쓰는 "게인 × 파라미터 + 상수" 공식 (식 9.15) |
| 파라미터 벡터 | $\mathbf{p}$ | 상태·기준값·측정 외란 등 변하는 값들을 담은 벡터 |
| 라그랑주 승수 | $\boldsymbol{\lambda}$ | 각 제약이 최적점을 얼마나 세게 밀고 있는지 |
| 헤시안 | $\mathbf{H}$ | QP 목적함수의 2차항 행렬. 양정부호이면 최소점이 유일 |
| 영공간 기저 | $\mathbf{Z}$ | 등식 제약을 깨지 않고 움직일 수 있는 방향들 ($\mathbf{R}_a\mathbf{Z}=0$) |
| 최악 꼭짓점 | $\theta_p$ | min–max에서 비용을 최대로 만드는 불확실성 폴리토프의 꼭짓점 |
| 무브 블로킹 | — | 연속된 미래 입력을 하나로 묶어 결정 변수를 줄이는 근사 |
| 룩업 테이블 | — | 대표점의 최적 입력을 미리 저장하고 온라인에서 조회·보간 |
| MPPI | $\lambda$ | 궤적을 무작위로 샘플링하고 $e^{-J/\lambda}$로 가중 평균하는 무최적화 MPC |
| 증강 상태 | $x_a(t)$ | 사장 시간 때문에 과거 입력까지 붙여 늘린 상태 벡터 |
