---
title: "Chapter 2 — 회전과 상호관계 (Rotations and cross-relations)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 2
tags: [ESKF, 쿼터니언, 회전, SO3, 리군, 로드리게스, SLERP, 지수사상]
---

# Chapter 2 · 회전과 상호관계

> [!abstract] 이 장을 한 문장으로
> 1장에서 만든 쿼터니언이라는 그릇에 드디어 **회전**을 담는다. 3D 회전 공식부터 시작해 **회전군 SO(3)** 를 정의하고, 회전행렬과 쿼터니언 각각에 대해 **지수사상·로그사상·회전 작용**을 나란히 유도한 뒤, 둘 사이를 오가는 변환식과 **SLERP(구면 보간)**, 그리고 마지막으로 "왜 하필 반각인가"라는 마술의 정체를 **등경사 회전(isoclinic rotation)** 으로 밝힌다.

---

## 들어가며 — 이 장의 구조

이 장은 논문에서 가장 길고 가장 중요한 장이다. 구조를 먼저 그려 두면 길을 잃지 않는다.

```
2.1  회전 공식          — 벡터를 돌리면 어떻게 되는가 (기하)
2.2  회전군 SO(3)       — "회전들의 집합"의 정체
2.3  회전행렬 버전      — exp/log/작용
2.4  쿼터니언 버전      — exp/log/작용  ← 2.3과 완전히 평행
2.5  둘 사이의 변환
2.6  회전의 합성
2.7  SLERP
2.8  반각의 정체 (등경사 회전)
```

**2.3과 2.4는 같은 이야기를 두 언어로 반복한다.** 하나를 이해하면 다른 하나는 거의 자동이다.

---

## 1. 3D 벡터 회전 공식

가장 기본적인 질문부터. *"벡터 $\mathbf{x}$ 를 축 $\mathbf{u}$ 를 중심으로 각 $\phi$ 만큼 돌리면 어디로 가는가?"*

![[fig_2_1.png]]
*그림 2.1 — 벡터 $\mathbf{x}$ 를 축 $\mathbf{u}$ 를 중심으로 각 $\phi$ 만큼 회전시킨 모습*

### 1.1 분해가 핵심이다

그림에서 보듯, 요령은 벡터 $\mathbf{x}$ 를 **축에 평행한 성분**과 **축에 수직한 성분**으로 쪼개는 것이다.

$$\mathbf{x} = \mathbf{x}_\parallel + \mathbf{x}_\perp$$

각각은 이렇게 구한다.

$$\mathbf{x}_\parallel = \mathbf{u}\mathbf{u}^\top\mathbf{x}, \qquad \mathbf{x}_\perp = \mathbf{x} - \mathbf{u}\mathbf{u}^\top\mathbf{x}$$

> [!note] $\mathbf{u}\mathbf{u}^\top$ 가 왜 "축 방향 성분"인가
> $\mathbf{u}^\top\mathbf{x}$ 는 스칼라(내적)로, $\mathbf{x}$ 가 축 방향으로 얼마나 뻗어 있는지를 잰 값이다. 거기에 다시 $\mathbf{u}$ 를 곱하면 그 길이만큼 축 방향으로 놓인 벡터가 된다. 즉 $\mathbf{u}\mathbf{u}^\top$ 는 **축으로의 정사영 행렬**이다.

### 1.2 왜 이렇게 쪼개는가

**축에 평행한 성분은 회전해도 꿈쩍하지 않는다.** 회전축 위에 놓인 화살표는 그 축으로 돌려 봐야 제자리다.

$$\mathbf{x}'_\parallel = \mathbf{x}_\parallel$$

**축에 수직한 성분만 실제로 돈다.** 그리고 이 성분은 축에 수직한 평면 안에서만 움직이므로, 문제가 **2D 평면 회전**으로 축소된다. 2D 회전은 우리가 이미 아는 것이다.

$$\mathbf{x}'_\perp = \mathbf{x}_\perp\cos\phi + (\mathbf{u}\times\mathbf{x}_\perp)\sin\phi$$

여기서 $\mathbf{u}\times\mathbf{x}_\perp$ 는 $\mathbf{x}_\perp$ 를 같은 평면 안에서 90° 돌린 벡터다. 즉 평면 안의 직교 기저 $\{\mathbf{x}_\perp,\ \mathbf{u}\times\mathbf{x}_\perp\}$ 를 $\cos$·$\sin$ 으로 섞은 것으로, 평범한 2D 회전 그 자체다.

### 1.3 로드리게스 회전 공식

두 성분을 다시 합치고 정리하면 그 유명한 **로드리게스 회전 공식(Rodrigues rotation formula)** 이 나온다.

$$\boxed{\mathbf{x}' = \mathbf{x}\cos\phi + (\mathbf{u}\times\mathbf{x})\sin\phi + \mathbf{u}(\mathbf{u}^\top\mathbf{x})(1-\cos\phi)}$$

> [!important] 이 공식의 의미
> 회전을 **축 $\mathbf{u}$ 와 각 $\phi$ 만으로** 완전히 기술했다. 행렬도 쿼터니언도 없이, 순수한 벡터 연산만으로. 이 장의 나머지는 이 하나의 사실을 회전행렬의 언어와 쿼터니언의 언어로 각각 번역하는 작업이다.

---

## 2. 회전군 SO(3)

### 2.1 회전이란 무엇을 보존하는 변환인가

회전을 "각도와 길이를 유지하면서 원점을 고정하는 변환"이라고 하자. 선형변환 $\mathbf{R}$ 이 이 조건을 만족하려면 임의의 두 벡터의 내적이 보존되어야 한다.

$$(\mathbf{R}\mathbf{a})^\top(\mathbf{R}\mathbf{b}) = \mathbf{a}^\top\mathbf{R}^\top\mathbf{R}\mathbf{b} = \mathbf{a}^\top\mathbf{b}$$

모든 $\mathbf{a},\mathbf{b}$ 에 대해 성립하려면

$$\mathbf{R}^\top\mathbf{R} = \mathbf{I}$$

이어야 한다. 이런 행렬을 **직교행렬(orthogonal matrix)** 이라 한다. 여기에 조건 하나를 더 붙인다. $\det(\mathbf{R}^\top\mathbf{R}) = (\det\mathbf{R})^2 = 1$ 이므로 $\det\mathbf{R} = \pm1$ 인데, **$-1$ 인 경우는 거울 반사(reflection)** 라서 실제 물체를 돌려서는 만들 수 없다. 그래서 $+1$ 만 남긴다.

$$SO(3) = \{\mathbf{R} \in \mathbb{R}^{3\times3}\ |\ \mathbf{R}^\top\mathbf{R} = \mathbf{I},\ \det\mathbf{R} = 1\}$$

이것이 **특수직교군(Special Orthogonal group) SO(3)** 다. "Special"은 $\det=+1$ 조건을, "Orthogonal"은 직교 조건을 가리킨다.

### 2.2 왜 "군(group)"인가

회전들의 집합은 다음을 만족한다.

| 군의 조건 | 회전에서의 의미 |
|---|---|
| 닫힘 | 회전을 두 번 하면 여전히 회전이다 |
| 결합법칙 | $(\mathbf{R}_1\mathbf{R}_2)\mathbf{R}_3 = \mathbf{R}_1(\mathbf{R}_2\mathbf{R}_3)$ |
| 항등원 | 안 돌리기($\mathbf{I}$)도 회전이다 |
| 역원 | 되돌리는 회전이 항상 있다($\mathbf{R}^\top$) |

다만 **교환법칙은 성립하지 않는다.** 1장에서 본 것과 같은 이야기다.

> [!important] SO(3)는 군이면서 동시에 매끄러운 곡면이다
> $SO(3)$ 의 원소는 숫자 9개짜리 행렬이지만, 제약 조건($\mathbf{R}^\top\mathbf{R}=\mathbf{I}$)이 6개 있어서 **실제 자유도는 3개**뿐이다. 즉 9차원 공간 속에 박혀 있는 **3차원짜리 매끄러운 곡면(매니폴드, manifold)** 이다.
>
> 이렇게 "군이면서 동시에 매끄러운 매니폴드"인 대상을 **리 군(Lie group)** 이라 부른다. 이 성질이 [[Chapter 04 - 섭동 미분 적분|4장]]에서 회전을 미분할 때 결정적인 역할을 한다. 자세한 이야기는 [[리 군과 리 대수]]에 정리했다.

---

## 3. 회전군과 회전행렬

### 3.1 지수사상 — 각속도에서 회전으로

회전하는 강체 위의 점 $\mathbf{x}$ 를 생각하자. 각속도 $\boldsymbol{\omega}$ 로 돌고 있다면 점의 속도는

$$\dot{\mathbf{x}} = \boldsymbol{\omega}\times\mathbf{x} = [\boldsymbol{\omega}]_\times\mathbf{x}$$

이것은 **선형 미분방정식**이다. 미분방정식 $\dot{\mathbf{x}} = \mathbf{A}\mathbf{x}$ 의 해가 $\mathbf{x}(t) = e^{\mathbf{A}t}\mathbf{x}(0)$ 임을 안다면, 답은 바로 나온다.

$$\mathbf{x}(t) = e^{[\boldsymbol{\omega}]_\times t}\,\mathbf{x}(0)$$

즉 **회전행렬은 반대칭행렬의 지수**다.

$$\mathbf{R} = \exp([\boldsymbol{\omega}]_\times t) = \exp([\boldsymbol{\omega}t]_\times)$$

여기서 $\boldsymbol{\theta} = \boldsymbol{\omega}t = \mathbf{u}\theta$ 를 **회전 벡터(rotation vector)** 라 하면

$$\mathbf{R} = \exp([\boldsymbol{\theta}]_\times)$$

![[fig_2_2.png]]
*그림 2.2 — 회전행렬의 지수사상. 벡터 $\mathbf{v}\in\mathbb{R}^3$ 에 스큐 연산자를 씌워 $[\mathbf{v}]_\times\in\mathfrak{so}(3)$ 로 보낸 뒤 지수를 취하면 $\mathbf{R}\in SO(3)$ 가 된다. 이 두 단계를 한꺼번에 묶은 것이 대문자 $\mathrm{Exp}(\cdot)$ 다.*

> [!note] $\mathfrak{so}(3)$ 라는 새 이름
> 반대칭행렬들의 집합 $\{[\boldsymbol{\theta}]_\times\}$ 를 **$\mathfrak{so}(3)$** 라고 쓰고 "리 대수(Lie algebra)"라 부른다. 이것은 $SO(3)$ 라는 곡면의 **항등원에서의 접평면(tangent space)** 이다. 곡면 위를 직접 계산하는 대신 평평한 접평면에서 계산하고 지수사상으로 올려보내는 것, 이것이 이 논문 전체를 관통하는 전략이다.

### 3.2 대문자 지수사상 $\mathrm{Exp}(\cdot)$

매번 "스큐 씌우고 지수 취하기"를 쓰기 번거로우니 한 덩어리로 묶는다.

$$\mathrm{Exp}: \mathbb{R}^3 \to SO(3); \qquad \boldsymbol{\theta} \mapsto \mathrm{Exp}(\boldsymbol{\theta}) \triangleq \exp([\boldsymbol{\theta}]_\times)$$

즉 $\mathrm{Exp}(\boldsymbol{\theta}) = \exp([\boldsymbol{\theta}]_\times)$ 다. **대문자는 3D 벡터를 받고, 소문자는 행렬을 받는다.** 이 구분이 논문 내내 유지되니 익혀 두자.

### 3.3 로드리게스 공식 다시 보기 — 이번엔 행렬로

$\exp([\boldsymbol{\theta}]_\times)$ 를 테일러 급수로 펼쳐 보자. 핵심은 $[\mathbf{u}]_\times$ 의 거듭제곱이 주기적이라는 사실이다.

$$[\mathbf{u}]_\times^2 = \mathbf{u}\mathbf{u}^\top - \mathbf{I}, \qquad [\mathbf{u}]_\times^3 = -[\mathbf{u}]_\times, \qquad [\mathbf{u}]_\times^4 = -[\mathbf{u}]_\times^2, \ \dots$$

**$[\mathbf{u}]_\times$ 와 $[\mathbf{u}]_\times^2$ 두 개만 계속 번갈아 나온다.** 1장 4.3절에서 순허 쿼터니언의 거듭제곱이 주기적이었던 것과 완전히 같은 구조다. 급수를 정리하면

$$\boxed{\mathbf{R} = \mathrm{Exp}(\mathbf{u}\theta) = \mathbf{I} + \sin\theta\,[\mathbf{u}]_\times + (1-\cos\theta)\,[\mathbf{u}]_\times^2}$$

이것이 **로드리게스 회전 공식의 행렬 버전**이다. 1.3절에서 기하학적으로 얻은 벡터 공식과 같은 내용이며, 실제로 양변에 $\mathbf{x}$ 를 곱해 보면 서로 일치한다.

### 3.4 로그사상 — 회전에서 각도로

지수의 반대 방향이다. 회전행렬 $\mathbf{R}$ 이 주어졌을 때 축 $\mathbf{u}$ 와 각 $\theta$ 를 뽑아낸다.

$$\theta = \arccos\left(\frac{\mathrm{trace}(\mathbf{R})-1}{2}\right), \qquad \mathbf{u} = \frac{(\mathbf{R}-\mathbf{R}^\top)^\vee}{2\sin\theta}$$

여기서 $(\cdot)^\vee$ 는 스큐 연산자의 역, 즉 반대칭행렬에서 3D 벡터를 꺼내는 연산이다.

$$\log(\mathbf{R}) = [\mathbf{u}\theta]_\times, \qquad \mathrm{Log}(\mathbf{R}) = \mathbf{u}\theta$$

> [!warning] $\theta \approx 0$ 과 $\theta \approx \pi$ 에서 조심할 것
> $\theta$ 가 0에 가까우면 $\sin\theta \approx 0$ 이라 $\mathbf{u}$ 계산에서 0으로 나누게 된다. 실무에서는 테일러 전개로 갈아타야 한다. $\theta \approx \pi$ 근처도 수치적으로 불안정하다. 라이브러리들이 이 부분을 특별 처리하는 이유다.

### 3.5 회전 작용

회전행렬로 벡터를 돌리는 건 그냥 행렬 곱이다.

$$\mathbf{x}' = \mathbf{R}\,\mathbf{x}$$

이것이 정말로 1.3절의 회전 공식과 같은지 확인해 보자. 로드리게스 공식을 대입하고 $[\mathbf{u}]_\times\mathbf{x} = \mathbf{u}\times\mathbf{x}$, $[\mathbf{u}]_\times^2 = \mathbf{u}\mathbf{u}^\top-\mathbf{I}$ 를 쓰면

$$\begin{aligned}
\mathbf{x}' &= \left(\mathbf{I} + \sin\phi\,[\mathbf{u}]_\times + (1-\cos\phi)[\mathbf{u}]_\times^2\right)\mathbf{x} \\
&= \mathbf{x} + \sin\phi\,(\mathbf{u}\times\mathbf{x}) + (1-\cos\phi)(\mathbf{u}\mathbf{u}^\top-\mathbf{I})\mathbf{x} \\
&= \mathbf{x} + \sin\phi\,(\mathbf{u}\times\mathbf{x}) + (1-\cos\phi)\,\mathbf{x}_\parallel - (1-\cos\phi)\,\mathbf{x} \\
&= \mathbf{x}_\parallel + (\mathbf{u}\times\mathbf{x})\sin\phi + \mathbf{x}_\perp\cos\phi
\end{aligned}$$

정확히 **1.3절의 벡터 회전 공식**이다. 회전행렬이 진짜 회전을 한다는 것이 확인되었다.

---

## 4. 회전군과 쿼터니언

이제 3절과 **완전히 평행한 이야기**를 쿼터니언 언어로 반복한다. 비교하며 읽으면 좋다.

### 4.0 출발점 — 가설을 세우고 나중에 증명한다

논문은 여기서 교육적인 전개를 택한다. 잘 알려진 쿼터니언 회전 공식

$$r(\mathbf{v}) = \mathbf{q}\otimes\mathbf{v}\otimes\mathbf{q}^*$$

를 **일단 가설로 받아들이고** 시작한다. 그러면 회전행렬에서 했던 논의를 그대로 되짚을 수 있다. 이 가설의 정확성은 4.4절에서 증명되며, 그것이 전체 접근을 정당화한다.

#### 단위 노름 조건이 저절로 나온다

회전은 길이를 보존해야 한다. 위 가설을 길이 보존 조건에 넣어 보자.

$$\|\mathbf{q}\otimes\mathbf{v}\otimes\mathbf{q}^*\| = \|\mathbf{q}\|^2\|\mathbf{v}\| = \|\mathbf{v}\|$$

([[Chapter 01 - 쿼터니언의 정의와 성질|1장]] 3.8절의 $\|\mathbf{p}\otimes\mathbf{q}\|=\|\mathbf{p}\|\|\mathbf{q}\|$ 를 썼다.) 따라서 $\|\mathbf{q}\|^2=1$, 즉

$$\mathbf{q}^*\otimes\mathbf{q} = 1 = \mathbf{q}\otimes\mathbf{q}^*$$

> [!important] 회전행렬의 직교 조건과 판박이다
> $$\mathbf{q}^*\otimes\mathbf{q} = 1 \qquad \longleftrightarrow \qquad \mathbf{R}^\top\mathbf{R} = \mathbf{I}$$
> 논문은 독자에게 **이 유사성 앞에서 잠시 멈춰 보라**고 권한다. 단위 쿼터니언 조건은 임의로 정한 것이 아니라, **길이를 보존하라는 요구에서 필연적으로 따라 나온 것**이다.

#### 외적도 보존된다

상대적 방향 조건도 만족한다. [[Chapter 01 - 쿼터니언의 정의와 성질|1장]] 4.1절의 교환자 관계를 두 번 쓰면

$$\begin{aligned}
r(\mathbf{v})\times r(\mathbf{w}) &= \tfrac{1}{2}\left[(\mathbf{q}\mathbf{v}\mathbf{q}^*)(\mathbf{q}\mathbf{w}\mathbf{q}^*) - (\mathbf{q}\mathbf{w}\mathbf{q}^*)(\mathbf{q}\mathbf{v}\mathbf{q}^*)\right] \\
&= \tfrac{1}{2}\,\mathbf{q}\otimes(\mathbf{v}\otimes\mathbf{w} - \mathbf{w}\otimes\mathbf{v})\otimes\mathbf{q}^* \\
&= \mathbf{q}\otimes(\mathbf{v}\times\mathbf{w})\otimes\mathbf{q}^* = r(\mathbf{v}\times\mathbf{w})
\end{aligned}$$

즉 **회전시킨 두 벡터의 외적 = 외적을 회전시킨 것**이다. 오른손 좌표계가 유지된다는 뜻이며, 거울 반사가 아니라는 확인이다.

#### $S^3$ 라는 이름

단위 쿼터니언의 집합은 곱셈 연산 아래 **군(group)** 을 이룬다. 이 군은 위상적으로 **3-구면**, 즉 $\mathbb{R}^4$ 단위 구의 3차원 표면이며 보통 $S^3$ 로 쓴다.

### 4.1 지수사상

각속도 $\boldsymbol{\omega}$ 로 도는 강체의 자세를 쿼터니언 $\mathbf{q}$ 로 표현하면, 그 미분방정식은

$$\dot{\mathbf{q}} = \tfrac{1}{2}\,\mathbf{q}\otimes\boldsymbol{\omega}$$

> [!important] 여기에 그 유명한 $1/2$ 이 나타난다
> 회전행렬의 미분방정식 $\dot{\mathbf{R}} = \mathbf{R}[\boldsymbol{\omega}]_\times$ 에는 없던 $1/2$ 이 쿼터니언 쪽에는 붙는다. 이 인자가 **모든 반각의 근원**이다. 왜 생기는지는 2.8절에서 밝힌다.

이 미분방정식을 풀면

$$\mathbf{q} = \exp(\boldsymbol{\omega}t/2) = \exp(\mathbf{u}\theta/2)$$

1장 4.4절의 공식을 대입하면

$$\boxed{\mathbf{q} = \mathrm{Exp}(\mathbf{u}\theta) \triangleq \exp(\mathbf{u}\theta/2) = \begin{bmatrix}\cos(\theta/2) \\ \mathbf{u}\sin(\theta/2)\end{bmatrix}}$$

![[fig_2_3.png]]
*그림 2.3 — 쿼터니언의 지수사상. 벡터 $\mathbf{v}\in\mathbb{R}^3$ 를 2로 나눠 순허 쿼터니언 $\mathbf{V}\in\mathbb{H}_p$ 로 보낸 뒤 지수를 취하면 단위 쿼터니언 $\mathbf{q}\in S^3$ 가 된다. 두 단계를 묶은 것이 $\mathrm{Exp}(\cdot)$ 다.*

### 4.2 대문자 지수사상 — 2로 나누는 것까지 포함한다

$$\mathrm{Exp}: \mathbb{R}^3 \to S^3; \qquad \boldsymbol{\theta} \mapsto \mathrm{Exp}(\boldsymbol{\theta}) \triangleq \exp(\boldsymbol{\theta}/2)$$

> [!note] 대문자 $\mathrm{Exp}$ 를 쓰면 행렬과 쿼터니언이 똑같아진다
> 회전행렬 쪽에서도 $\mathrm{Exp}(\boldsymbol{\theta})$, 쿼터니언 쪽에서도 $\mathrm{Exp}(\boldsymbol{\theta})$ 다. **둘 다 같은 회전 벡터 $\boldsymbol{\theta}$ 를 받아서 같은 회전을 표현한다.** 반각의 $1/2$ 은 대문자 연산자 안에 숨겨 놓았기 때문에, 대문자 표기를 쓰는 한 두 세계를 헷갈릴 일이 없다. 이 논문이 대문자 표기를 고집하는 이유다.

$S^3$ 는 4차원 공간의 **단위 초구(unit 3-sphere)** 로, 단위 쿼터니언들이 사는 곳이다.

### 4.3 로그사상

$$\mathrm{Log}(\mathbf{q}) = \boldsymbol{\theta} = \mathbf{u}\theta, \qquad \mathbf{u} = \frac{\mathbf{q}_v}{\|\mathbf{q}_v\|}, \quad \theta = 2\arctan(\|\mathbf{q}_v\|, q_w)$$

**$\arctan$ 앞에 2가 붙었다.** 지수에서 반으로 나눴으니 로그에서 두 배로 돌려놓는 것이다.

### 4.4 회전 작용 — 곱을 두 번 한다

쿼터니언으로 벡터를 돌리려면 3D 벡터 $\mathbf{x}$ 를 순허 쿼터니언으로 바꾼 뒤 양쪽에서 감싼다.

$$\boxed{\mathbf{x}' = \mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*}$$

여기서 $\mathbf{q} = \mathrm{Exp}(\mathbf{u}\phi)$ 이고, 벡터 $\mathbf{x}$ 는 순허 쿼터니언 형태로 쓴다.

$$\mathbf{x} = x\,i + y\,j + z\,k = \begin{bmatrix}0\\ \mathbf{x}\end{bmatrix} \in \mathbb{H}_p$$

이 **이중 곱(샌드위치 곱, sandwich product)** 이 정말로 회전을 수행하는지 증명해 보자. 4.1절의 $\mathbf{q}=[\cos\tfrac{\phi}{2},\ \mathbf{u}\sin\tfrac{\phi}{2}]$ 와 [[Chapter 01 - 쿼터니언의 정의와 성질|1장]]의 곱 공식을 쓴다.

$$\begin{aligned}
\mathbf{x}' &= \mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^* \\
&= \left(\cos\tfrac{\phi}{2}+\mathbf{u}\sin\tfrac{\phi}{2}\right)(0+\mathbf{x})\left(\cos\tfrac{\phi}{2}-\mathbf{u}\sin\tfrac{\phi}{2}\right) \\
&= \mathbf{x}\cos^2\tfrac{\phi}{2} + (\mathbf{u}\otimes\mathbf{x}-\mathbf{x}\otimes\mathbf{u})\sin\tfrac{\phi}{2}\cos\tfrac{\phi}{2} - \mathbf{u}\otimes\mathbf{x}\otimes\mathbf{u}\sin^2\tfrac{\phi}{2} \\
&= \mathbf{x}\cos^2\tfrac{\phi}{2} + 2(\mathbf{u}\times\mathbf{x})\sin\tfrac{\phi}{2}\cos\tfrac{\phi}{2} - \left(\mathbf{x}(\mathbf{u}^\top\mathbf{u})-2\mathbf{u}(\mathbf{u}^\top\mathbf{x})\right)\sin^2\tfrac{\phi}{2} \\
&= \mathbf{x}\left(\cos^2\tfrac{\phi}{2}-\sin^2\tfrac{\phi}{2}\right) + (\mathbf{u}\times\mathbf{x})\left(2\sin\tfrac{\phi}{2}\cos\tfrac{\phi}{2}\right) + \mathbf{u}(\mathbf{u}^\top\mathbf{x})\left(2\sin^2\tfrac{\phi}{2}\right) \\
&= \mathbf{x}\cos\phi + (\mathbf{u}\times\mathbf{x})\sin\phi + \mathbf{u}(\mathbf{u}^\top\mathbf{x})(1-\cos\phi)
\end{aligned}$$

마지막 줄에서 **반각 공식** $\cos^2\tfrac{\phi}{2}-\sin^2\tfrac{\phi}{2}=\cos\phi$, $2\sin\tfrac{\phi}{2}\cos\tfrac{\phi}{2}=\sin\phi$, $2\sin^2\tfrac{\phi}{2}=1-\cos\phi$ 를 썼다.

$\mathbf{x}_\parallel = \mathbf{u}\mathbf{u}^\top\mathbf{x}$ 로 다시 묶으면

$$\mathbf{x}' = \mathbf{x}_\perp\cos\phi + (\mathbf{u}\times\mathbf{x})\sin\phi + \mathbf{x}_\parallel$$

**정확히 1.3절의 벡터 회전 공식이다.** 4.0절의 가설이 증명되었다.

> [!important] 반각이 여기서 사라진다
> 유도 과정을 보라. $\phi/2$ 로 들어간 각도가 **반각 공식을 거치면서 $\phi$ 로 복원**되었다. $\cos^2\tfrac{\phi}{2}-\sin^2\tfrac{\phi}{2}=\cos\phi$ 라는 삼각항등식이 "곱을 두 번 하면 각도가 두 배"라는 사실의 대수적 표현인 셈이다.
>
> 이것이 왜 쿼터니언에 절반의 각도를 넣어야 하는지에 대한 **계산적인 답**이다. 기하학적인 답은 8절의 등경사 회전에 있다.

> [!question] 왜 곱을 두 번 해야 하는가?
> 한 번만 곱하면($\mathbf{q}\otimes\mathbf{x}$) 결과가 순허 쿼터니언이 아니게 되어 3D 벡터로 되돌릴 수 없다. 켤레로 한 번 더 감싸야 실수부가 상쇄되어 다시 3D 벡터가 된다.
>
> 더 깊은 이유는 2.8절에서 밝힌다. 짧게 말하면 **왼쪽 곱과 오른쪽 곱이 각각 4D 공간에서 두 평면을 동시에 돌리는데, 둘을 겹치면 한 평면에서는 효과가 상쇄되고 다른 평면에서는 두 배가 되기** 때문이다. 각도가 절반인 것도 이 "두 배" 때문이다.

### 4.5 이중 덮개 — 쿼터니언의 유일한 결점

![[fig_2_4.png]]
*그림 2.4 — 회전 매니폴드의 이중 덮개. 왼쪽: 단위 3-구면 위의 쿼터니언 $\mathbf{q}$. 가운데: 축 $\mathbf{u}$ 를 중심으로 한 벡터의 회전. 오른쪽: $\mathbf{q}$ 가 각 $\theta$ 만큼 도는 동안 벡터는 $\phi=2\theta$ 만큼 돈다. 쿼터니언이 한 바퀴($2\pi$) 도는 동안 3D 공간은 두 바퀴($4\pi$) 도는 셈이다.*

$\mathbf{q}$ 와 $-\mathbf{q}$ 를 회전 작용에 넣어 보자.

$$(-\mathbf{q})\otimes\mathbf{x}\otimes(-\mathbf{q})^* = (-1)(-1)\,\mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^* = \mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*$$

**부호가 두 번 곱해져 상쇄된다.** 즉 $\mathbf{q}$ 와 $-\mathbf{q}$ 는 **완전히 같은 회전**을 나타낸다.

#### 왜 "이중" 덮개인가 — 각도를 세어 보자

이 이름의 근거를 정확히 따져 보자. 단위 쿼터니언 $\mathbf{q}$ 를 그냥 **4차원 벡터**로 보고, 방향의 원점에 해당하는 항등 쿼터니언 $\mathbf{q}_1=[1,0,0,0]$ 과의 사이각을 $\alpha$ 라 하자. 4D 내적으로 구하면

$$\cos\alpha = \mathbf{q}_1^\top\mathbf{q} = q_w$$

한편 이 쿼터니언이 3D 공간의 물체를 돌리는 각도 $\phi$ 는

$$\mathbf{q} = \begin{bmatrix}q_w\\ \mathbf{q}_v\end{bmatrix} = \begin{bmatrix}\cos(\phi/2)\\ \mathbf{u}\sin(\phi/2)\end{bmatrix}$$

두 식에서 $q_w$ 를 비교하면 $\cos\alpha = \cos(\phi/2)$, 즉

$$\boxed{\alpha = \phi/2}$$

> [!important] 4D에서의 각도는 3D 회전각의 절반이다
> **쿼터니언 벡터가 4D 공간에서 $\alpha$ 만큼 기울어져 있을 때, 3D 공간에서는 그 두 배인 $\phi=2\alpha$ 만큼 회전이 일어난다.**
>
> 그림 2.4가 이것을 보여 준다. 숫자로 따라가 보자.
>
> | 4D 쿼터니언 각 $\alpha$ | 3D 회전각 $\phi$ | 상태 |
> |---|---|---|
> | $0$ | $0$ | 시작 |
> | $\pi/2$ | $\pi$ | 3D는 이미 **반 바퀴** |
> | $\pi$ | $2\pi$ | 3D는 **한 바퀴 완주**, 쿼터니언은 반 바퀴 |
> | $2\pi$ | $4\pi$ | 3D는 **두 바퀴**, 쿼터니언은 한 바퀴 |
>
> 쿼터니언이 3-구면 위를 **한 바퀴** 도는 동안 3D 회전은 **두 바퀴**를 돈다. 즉 쿼터니언 공간이 회전 매니폴드를 **두 번 덮는다.** 이것이 "이중 덮개(double cover)"라는 이름의 뜻이다.
>
> $\alpha=\pi$ 인 지점, 즉 $\mathbf{q}$ 와 $-\mathbf{q}$ 가 3D에서 같은 회전이 되는 것도 이 표에서 자연스럽게 읽힌다.

> [!warning] 이중 덮개가 실무에서 일으키는 문제
> 하나의 회전에 두 개의 쿼터니언이 대응하므로, **두 쿼터니언을 직접 빼서 "차이"를 재면 안 된다.** $\mathbf{q}_1 - \mathbf{q}_2$ 가 크더라도 실제 회전 차이는 0일 수 있다. 회전 차이는 반드시 $\mathrm{Log}(\mathbf{q}_1^*\otimes\mathbf{q}_2)$ 로 재야 한다.
>
> 또 SLERP처럼 보간할 때는 **두 쿼터니언의 내적이 음수면 한쪽의 부호를 뒤집어** 짧은 길로 가도록 해야 한다(2.7절 참고).

---

## 5. 회전행렬과 쿼터니언 사이의 변환

### 5.1 쿼터니언 → 회전행렬

$\mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*$ 를 행렬 형태로 전개하면

$$\mathbf{R}\{\mathbf{q}\} = (q_w^2 - \mathbf{q}_v^\top\mathbf{q}_v)\mathbf{I} + 2\,\mathbf{q}_v\mathbf{q}_v^\top + 2q_w[\mathbf{q}_v]_\times$$

성분으로 풀어 쓰면

$$\mathbf{R} = \begin{bmatrix}
q_w^2+q_x^2-q_y^2-q_z^2 & 2(q_xq_y - q_wq_z) & 2(q_xq_z+q_wq_y) \\
2(q_xq_y+q_wq_z) & q_w^2-q_x^2+q_y^2-q_z^2 & 2(q_yq_z-q_wq_x) \\
2(q_xq_z-q_wq_y) & 2(q_yq_z+q_wq_x) & q_w^2-q_x^2-q_y^2+q_z^2
\end{bmatrix}$$

### 5.2 회전행렬 → 쿼터니언

대각합(trace)을 이용한다. $\mathrm{trace}(\mathbf{R}) = 3q_w^2 - \mathbf{q}_v^\top\mathbf{q}_v = 4q_w^2-1$ 이므로

$$q_w = \tfrac{1}{2}\sqrt{1+\mathrm{trace}(\mathbf{R})}, \qquad \mathbf{q}_v = \frac{1}{4q_w}\begin{bmatrix} R_{32}-R_{23} \\ R_{13}-R_{31} \\ R_{21}-R_{12}\end{bmatrix}$$

> [!warning] $q_w \approx 0$ 일 때 터진다
> 이 식은 $q_w$ 가 0에 가까울 때(즉 $\theta \approx \pi$, 반 바퀴 회전) 0으로 나누게 된다. 실무 구현(예: Eigen, ROS tf)은 **대각 성분 중 가장 큰 것을 골라 그에 맞는 4가지 공식 중 하나를 쓰는** 방식으로 이 문제를 피한다. 직접 구현할 일이 있다면 반드시 이 분기를 넣어야 한다.

---

## 6. 회전의 합성

### 6.1 인덱스 연결 규칙

![[fig_2_5.png]]
*그림 2.5 — 회전의 합성. $\mathbb{R}^2$ 라면 단순히 각도를 더하면 되지만($\theta_{AC} = \theta_{AB}+\theta_{BC}$), 3D에서는 쿼터니언 곱으로 합성한다.*

좌표계 $\mathcal{A} \to \mathcal{B} \to \mathcal{C}$ 로 이어지는 회전은 **인덱스를 사슬처럼 이어 붙이면** 된다.

$$\mathbf{q}_{\mathcal{AC}} = \mathbf{q}_{\mathcal{AB}} \otimes \mathbf{q}_{\mathcal{BC}}, \qquad \mathbf{R}_{\mathcal{AC}} = \mathbf{R}_{\mathcal{AB}}\,\mathbf{R}_{\mathcal{BC}}$$

가운데 인덱스 $\mathcal{B}$ 가 서로 맞닿아 상쇄되고 양 끝만 남는다고 외우면 쉽다.

### 6.2 역방향

반대 방향 회전은 켤레(또는 전치)다.

$$\mathbf{q}_{\mathcal{BA}} = \mathbf{q}_{\mathcal{AB}}^*, \qquad \mathbf{R}_{\mathcal{BA}} = \mathbf{R}_{\mathcal{AB}}^\top$$

이 둘을 합치면 임의의 경로를 계산할 수 있다. 예를 들어

$$\mathbf{q}_{\mathcal{ZA}} = \mathbf{q}_{\mathcal{XZ}}^* \otimes \mathbf{q}_{\mathcal{OX}}^* \otimes \mathbf{q}_{\mathcal{OA}}$$

> [!tip] 인덱스 표기를 쓰면 실수가 줄어든다
> 실무에서 좌표 변환 버그의 대부분은 "어느 쪽이 어느 쪽으로 가는 회전인지" 헷갈려서 생긴다. $\mathbf{q}_{\mathcal{AB}}$ 처럼 항상 두 인덱스를 달고 다니면, 곱했을 때 인덱스가 맞물리는지만 확인해도 대부분의 실수를 잡을 수 있다.

---

## 7. 구면 선형 보간 (SLERP)

### 7.1 문제 설정

두 자세 $\mathbf{q}_0$ 와 $\mathbf{q}_1$ 이 주어졌을 때, $t\in[0,1]$ 에 대해 $\mathbf{q}(0)=\mathbf{q}_0$ 에서 $\mathbf{q}(1)=\mathbf{q}_1$ 로 **고정된 축을 중심으로 일정한 속도로** 부드럽게 이어 주는 $\mathbf{q}(t)$ 를 찾고 싶다.

![[fig_2_6.png]]
*그림 2.6 — $\mathbb{R}^4$ 의 단위 구면 위에서의 쿼터니언 보간(왼쪽)과, 회전이 일어나는 평면 $\pi$ 를 정면에서 본 모습(오른쪽)*

### 7.2 방법 1 — 쿼터니언 대수로

논리가 아주 자연스럽다.

**1단계.** $\mathbf{q}_0$ 에서 $\mathbf{q}_1$ 로 가는 회전 증분을 구한다.

$$\Delta\mathbf{q} = \mathbf{q}_0^* \otimes \mathbf{q}_1$$

**2단계.** 로그사상으로 축과 각도를 뽑는다.

$$\mathbf{u}\,\Delta\theta = \mathrm{Log}(\Delta\mathbf{q})$$

**3단계.** 축은 그대로 두고 **각도만 $t$ 배**로 줄인 뒤, 지수사상으로 되돌려 원래 자세에 합성한다.

$$\mathbf{q}(t) = \mathbf{q}_0 \otimes \mathrm{Exp}(t\,\mathbf{u}\,\Delta\theta)$$

전체를 한 줄로 쓰면

$$\boxed{\mathbf{q}(t) = \mathbf{q}_0 \otimes (\mathbf{q}_0^*\otimes\mathbf{q}_1)^t}$$

구현할 때는 1장 4.8절의 공식을 그대로 쓴다.

$$\mathbf{q}(t) = \mathbf{q}_0 \otimes \begin{bmatrix}\cos(t\,\Delta\theta/2) \\ \mathbf{u}\sin(t\,\Delta\theta/2)\end{bmatrix}$$

> [!note] 회전행렬로도 똑같이 할 수 있다
> $$\mathbf{R}(t) = \mathbf{R}_0\,\mathrm{Exp}(t\,\mathrm{Log}(\mathbf{R}_0^\top\mathbf{R}_1)) = \mathbf{R}_0\left(\mathbf{I} + \sin(t\Delta\theta)[\mathbf{u}]_\times + (1-\cos(t\Delta\theta))[\mathbf{u}]_\times^2\right)$$
> 구조가 완전히 같다. "차이를 구하고 → 로그로 내려가서 → $t$ 배 하고 → 지수로 올라와서 → 다시 합성"이라는 패턴은 매니폴드 위에서 보간할 때 항상 쓰는 레시피다.

### 7.3 방법 2 — 4D 벡터로 보기

쿼터니언 대수를 전혀 쓰지 않고, $\mathbf{q}_0, \mathbf{q}_1$ 을 그냥 **4차원 단위벡터**로 보는 방법도 있다. 두 벡터 사이 각은 내적으로 구한다.

$$\cos\Delta\theta = \mathbf{q}_0^\top\mathbf{q}_1 \quad \Longrightarrow \quad \Delta\theta = \arccos(\mathbf{q}_0^\top\mathbf{q}_1)$$

$\mathbf{q}_1$ 을 $\mathbf{q}_0$ 에 대해 직교정규화해서 평면의 기저를 만들고

$$\mathbf{q}_\perp = \frac{\mathbf{q}_1 - (\mathbf{q}_0^\top\mathbf{q}_1)\mathbf{q}_0}{\|\mathbf{q}_1 - (\mathbf{q}_0^\top\mathbf{q}_1)\mathbf{q}_0\|}$$

그 평면 안에서 평범하게 각도를 비례 배분한다.

$$\mathbf{q}(t) = \mathbf{q}_0\cos(t\,\Delta\theta) + \mathbf{q}_\perp\sin(t\,\Delta\theta)$$

두 방법이 같은 결과를 준다는 증명은 Dam et al. (1998)에 있다.

### 7.4 짧은 길로 가기

![[fig_2_7.png]]
*그림 2.7 — $\mathbf{q}_0$ 와 $\mathbf{q}_1$ 사이에서 최단 경로로 SLERP 하기. 왼쪽: $\Delta\theta > \pi/2$ 이면 $\mathbf{q}_1$ 대신 $-\mathbf{q}_1$ 을 쓴다. 오른쪽: 그러면 실제 3D 회전은 $\Delta\phi > \pi$ 대신 $\Delta\phi' < \pi$ 인 짧은 길을 간다.*

4.5절의 이중 덮개 때문에, 그냥 보간하면 **먼 길로 돌아갈 수 있다.** 해법은 단순하다.

$$\mathbf{q}_0^\top\mathbf{q}_1 < 0 \quad \Longrightarrow \quad \mathbf{q}_1 \leftarrow -\mathbf{q}_1$$

내적이 음수이면 한쪽 부호를 뒤집는다. $-\mathbf{q}_1$ 은 $\mathbf{q}_1$ 과 같은 회전이므로 결과는 달라지지 않으면서, 경로만 짧은 쪽으로 바뀐다.

> [!tip] 이 한 줄이 없으면 애니메이션이 갑자기 휙 돈다
> 게임이나 로봇 시뮬레이션에서 캐릭터가 이상하게 먼 길로 회전하는 버그의 단골 원인이 바로 이 부호 처리 누락이다.

---

## 8. 쿼터니언과 등경사 회전 — 마술의 정체

이 절은 논문에서 가장 흥미로운 부분이다. 지금까지 남겨 둔 두 가지 의문에 답한다.

> **의문 1.** 왜 곱을 두 번 해야 하는가? ($\mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*$)
> **의문 2.** 왜 각도가 절반인가? ($\theta/2$)

### 8.1 3D의 회전 — 축 하나, 평면 하나

![[fig_2_8.png]]
*그림 2.8 — $\mathbb{R}^3$ 에서의 회전. 축 $\mathbf{u}$ 를 중심으로 한 벡터 $\mathbf{x}$ 의 회전은 축에 수직인 평면 안에서 원을 그린다. 축에 평행한 성분은 움직이지 않고 축 위의 작은 빨간 점으로 표시된다. 오른쪽 스케치는 평면 부분공간과 축 부분공간에서 점의 거동이 근본적으로 다름을 보여 준다.*

3D에서 회전은 1.1절에서 본 대로 공간을 두 부분으로 쪼갠다. **평면(2차원)에서는 회전하고, 축(1차원)에서는 가만히 있는다.**

### 8.2 4D의 회전 — 평면 둘

![[fig_2_9.png]]
*그림 2.9 — $\mathbb{R}^4$ 에서의 회전. 두 개의 직교하는 평면 $\pi_1$, $\pi_2$ 에서 두 개의 독립적인 회전이 가능하다. 평면 $\pi_1$ 에서의 회전은 그 평면에 속한 두 성분(빨간 점)을 원운동시키고, $\pi_2$ 의 나머지 두 성분은 건드리지 않는다. 반대도 마찬가지다.*

4D로 올라가면 이야기가 달라진다. 3D에서 1차원이던 "회전축"이 4D에서는 **2차원 평면**이 된다. 그리고 2차원 평면에서는 **또 하나의 회전이 가능**하다.

즉 **4D의 회전은 서로 직교하는 두 평면에서 각각 독립적으로 일어나는 두 회전**으로 이루어진다. 각 평면의 회전각을 $\alpha_1$, $\alpha_2$ 라 하자.

### 8.3 등경사 회전 — 두 각이 같은 특별한 경우

$|\alpha_1| = |\alpha_2|$ 인 회전을 **등경사 회전(isoclinic rotation)** 이라 한다. 여기서 부호에 따라 두 종류가 갈린다.

| 종류 | 조건 | 쿼터니언과의 관계 |
|---|---|---|
| **좌 등경사(left-isoclinic)** | $\alpha_1 = +\alpha_2$ | $[\mathbf{q}]_L$ (왼쪽 곱) |
| **우 등경사(right-isoclinic)** | $\alpha_1 = -\alpha_2$ | $[\mathbf{q}]_R$ (오른쪽 곱) |

> [!important] 핵심 발견
> 단위 쿼터니언을 **왼쪽에서 곱하는 것**($[\mathbf{q}]_L$)은 4D 공간의 **좌 등경사 회전**이고, **오른쪽에서 곱하는 것**($[\mathbf{q}]_R$)은 **우 등경사 회전**이다. 1장 3.3절에서 두 행렬의 차이가 오직 부호 하나였던 것을 떠올리면, 그 부호가 바로 $\alpha_2$ 의 부호였던 것이다.

### 8.4 두 회전을 겹치면 무슨 일이 일어나는가

![[fig_2_10.png]]
*그림 2.10 — $\mathbb{R}^4$ 에서의 쿼터니언 회전. 두 개의 등경사 회전을 연달아 적용한다. 먼저 좌 회전 $L$ 은 두 평면을 모두 $+\theta/2$ 만큼 돌린다. 이어서 우 회전 $R$ 은 $\pi_1$ 을 $+\theta/2$, $\pi_2$ 를 $-\theta/2$ 만큼 돌린다. 결과적으로 $\pi_1$ 에서는 $\theta$ 만큼 누적되고, $\pi_2$ 에서는 서로 상쇄되어 0이 된다.*

이제 $\mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*$ 를 그림 2.10을 따라 읽어 보자. $\mathbf{q} = \mathrm{Exp}(\mathbf{u}\theta)$ 이므로 각 곱은 $\theta/2$ 에 해당하는 회전이다.

**왼쪽 곱 $\mathbf{q}\otimes(\cdot)$** — 좌 등경사 회전. 두 평면 모두 $+\theta/2$.

| | $\pi_1$ | $\pi_2$ |
|---|---|---|
| 좌 곱 | $+\theta/2$ | $+\theta/2$ |

**오른쪽 곱 $(\cdot)\otimes\mathbf{q}^*$** — 우 등경사 회전. 켤레이므로 부호가 반대다.

| | $\pi_1$ | $\pi_2$ |
|---|---|---|
| 우 곱 | $+\theta/2$ | $-\theta/2$ |

**합치면**

| | $\pi_1$ | $\pi_2$ |
|---|---|---|
| 합계 | $+\theta/2 + \theta/2 = \boldsymbol{\theta}$ | $+\theta/2 - \theta/2 = \mathbf{0}$ |

> [!important] 두 의문이 동시에 풀렸다
> **$\pi_2$ 평면에서는 정확히 상쇄되어 아무 일도 일어나지 않고, $\pi_1$ 평면에서만 $\theta$ 만큼 회전이 누적된다.**
>
> - **왜 곱을 두 번 하는가?** — 한 번만 하면 두 평면이 모두 돌아서 4D 회전이 되어 버린다. 두 번 해야 한 평면의 회전이 상쇄되어, 결과가 "평면 하나만 도는 3D 회전"이 된다. 상쇄된 $\pi_2$ 가 바로 3D 회전의 **회전축**에 해당한다.
> - **왜 각도가 절반인가?** — 각 곱이 $\theta/2$ 씩 기여하는데 그것이 $\pi_1$ 에서 **두 번 더해져** $\theta$ 가 되기 때문이다. 원하는 결과가 $\theta$ 이니 각 곱은 절반씩 맡아야 한다.

그리고 1장 3.5절에서 본 "$[\mathbf{p}]_R[\mathbf{q}]_L = [\mathbf{q}]_L[\mathbf{p}]_R$" 도 이제 이해된다. **서로 직교하는 평면에서 일어나는 독립적인 회전은 순서를 바꿔도 결과가 같기 때문**이다.

---

## 정리 — 두 언어 대조표

| 개념 | 회전행렬 $\mathbf{R}$ | 쿼터니언 $\mathbf{q}$ |
|---|---|---|
| 사는 곳 | $SO(3)$ | $S^3$ (단위 3-구면) |
| 리 대수 | $\mathfrak{so}(3)$ (반대칭행렬) | $\mathbb{H}_p$ (순허 쿼터니언) |
| 지수 (소문자) | $\exp([\boldsymbol{\theta}]_\times)$ | $\exp(\boldsymbol{\theta}/2)$ |
| 지수 (대문자) | $\mathrm{Exp}(\boldsymbol{\theta})$ | $\mathrm{Exp}(\boldsymbol{\theta})$ |
| 구체적 형태 | $\mathbf{I}+\sin\theta[\mathbf{u}]_\times+(1-\cos\theta)[\mathbf{u}]_\times^2$ | $[\cos(\theta/2),\ \mathbf{u}\sin(\theta/2)]$ |
| 회전 작용 | $\mathbf{R}\mathbf{x}$ | $\mathbf{q}\otimes\mathbf{x}\otimes\mathbf{q}^*$ |
| 합성 | $\mathbf{R}_1\mathbf{R}_2$ | $\mathbf{q}_1\otimes\mathbf{q}_2$ |
| 역회전 | $\mathbf{R}^\top$ | $\mathbf{q}^*$ |
| 미분방정식 | $\dot{\mathbf{R}} = \mathbf{R}[\boldsymbol{\omega}]_\times$ | $\dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}$ |
| 표현의 유일성 | 1:1 | 1:2 (이중 덮개, $\pm\mathbf{q}$) |
| 저장 | 숫자 9개 | 숫자 4개 |

> [!tip] 대문자 $\mathrm{Exp}$/$\mathrm{Log}$ 표기의 힘
> 표에서 보듯 **대문자 연산자를 쓰면 두 열이 거의 같아진다.** 회전 벡터 $\boldsymbol{\theta}\in\mathbb{R}^3$ 를 공통 언어로 삼고, 구체적 표현($\mathbf{R}$ 이냐 $\mathbf{q}$ 냐)은 그때그때 편한 것을 고르면 된다는 뜻이다. [[Chapter 04 - 섭동 미분 적분|4장]] 이후의 모든 유도가 이 원칙 위에서 진행된다.

---

## 관련 노트

- [[리 군과 리 대수]] — $SO(3)$, $\mathfrak{so}(3)$, 지수사상의 정체
- [[쿼터니언이란 무엇인가]] — 기초 직관
- [[Chapter 01 - 쿼터니언의 정의와 성질]] — 이전 장
- [[Chapter 03 - 쿼터니언 규약]] — 다음 장
- [[Chapter 04 - 섭동 미분 적분]] — 이 장의 도구를 미분에 쓴다
