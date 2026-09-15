---
title: "Chapter 4 — 섭동·미분·적분 (Perturbations, derivatives and integrals)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 4
tags: [ESKF, 쿼터니언, 자코비안, 섭동, 리군, 매니폴드, 미분, 적분]
---

# Chapter 4 · 섭동·미분·적분

> [!abstract] 이 장을 한 문장으로
> **"곡면 위에 사는 회전을 어떻게 미분할 것인가?"** 라는 이 논문의 핵심 질문에 답한다. 회전에는 덧셈이 없으므로 $\oplus$·$\ominus$ 라는 새 연산을 정의하고, 그로부터 **네 가지 미분 정의**를 세운 뒤, 실제로 쓰이는 **자코비안**들을 유도하고, 마지막으로 각속도를 **시간적분**해 자세를 갱신하는 방법을 정리한다.

---

## 들어가며 — 왜 회전은 미분하기 어려운가

미분의 정의를 떠올려 보자.

$$\frac{\partial f(x)}{\partial x} = \lim_{\delta x\to 0}\frac{f(x+\delta x) - f(x)}{\delta x}$$

이 정의에는 **덧셈 $+$ 과 뺄셈 $-$** 이 들어 있다. 평범한 벡터 공간 $\mathbb{R}^n$ 에서는 아무 문제가 없다. 그런데 회전에서는?

> [!warning] 회전행렬 두 개를 더하면 회전행렬이 아니다
> $\mathbf{R}_1 + \mathbf{R}_2$ 를 계산해 보라. 결과는 $\mathbf{R}^\top\mathbf{R}=\mathbf{I}$ 를 만족하지 않는다. **회전이 아니다.** 쿼터니언도 마찬가지로, $\mathbf{q}_1 + \mathbf{q}_2$ 는 단위 길이가 아니다.
>
> [[Chapter 02 - 회전과 상호관계|2장]]에서 본 대로 $SO(3)$ 는 **평평한 벡터 공간이 아니라 휘어진 곡면(매니폴드)** 이다. 곡면 위의 두 점을 더한다는 것은 애초에 말이 안 된다. 지구 표면 위의 서울과 뉴욕을 "더하면" 어디가 되는가? 그런 연산은 정의되지 않는다.

그래서 이 장은 먼저 **덧셈과 뺄셈을 대신할 연산을 새로 만드는 일**부터 시작한다.

---

## 1. SO(3)의 덧셈·뺄셈 연산자 $\oplus$ 와 $\ominus$

![[fig_4_1.png]]
*그림 4.1 — $S^3$ 매니폴드는 $\mathbb{R}^4$ 의 단위 구면이고(그림에서는 파란 원), 모든 단위 쿼터니언이 여기 산다. 매니폴드에 대한 접공간은 초평면 $\mathbb{R}^3$ 이다(빨간 선). 왼쪽: $\mathrm{Exp}()$ 과 $\mathrm{Log}()$ 연산자가 $\mathbb{R}^3$ 의 원소와 $S^3$ 의 원소를 서로 옮긴다. 오른쪽: $\oplus$ 와 $\ominus$ 연산자가 매니폴드의 원소와 접공간의 원소를 연결한다. (같은 그림이 $SO(3)$ 매니폴드도 설명한다.)*

### 1.1 덧셈 연산자 $\oplus$

**"회전에 작은 회전을 더한다"** 는 뜻의 연산이다.

$$\oplus: SO(3)\times\mathbb{R}^3 \to SO(3)$$

$$\boxed{\mathbf{S} = \mathbf{R}\oplus\boldsymbol{\theta} \triangleq \mathbf{R}\circ\mathrm{Exp}(\boldsymbol{\theta})}$$

읽는 법은 이렇다. 기준이 되는 회전 $\mathbf{R}$ 이 있고, 거기에 **접공간의 벡터** $\boldsymbol{\theta}\in\mathbb{R}^3$ 로 지정된 (보통 작은) 회전을 합성한다.

각 표현으로 쓰면

$$\mathbf{q}_S = \mathbf{q}_R\oplus\boldsymbol{\theta} = \mathbf{q}_R\otimes\mathrm{Exp}(\boldsymbol{\theta}), \qquad \mathbf{R}_S = \mathbf{R}_R\oplus\boldsymbol{\theta} = \mathbf{R}_R\,\mathrm{Exp}(\boldsymbol{\theta})$$

> [!important] 이 연산의 핵심 아이디어
> **더하는 쪽($\boldsymbol{\theta}$)은 평평한 3차원 벡터**다. 곡면 위의 점끼리 더하는 게 아니라, **곡면 위의 점 + 접평면의 벡터 = 곡면 위의 점**이다. 지구 위의 서울에서 "북쪽으로 10km"라는 평면 벡터를 더하면 다시 지구 위의 한 점이 나오는 것과 같다.
>
> 그리고 $\boldsymbol{\theta}$ 는 자유로운 3개의 숫자다. 제약 조건이 없다. **그래서 여기에 대해서는 평범하게 미분하고 평범하게 공분산을 정의할 수 있다.** 이것이 ESKF의 근본 전략이다.

### 1.2 뺄셈 연산자 $\ominus$

위의 역연산이다. 두 회전 사이의 **벡터로 표현된 각도 차이**를 돌려준다.

$$\ominus: SO(3)\times SO(3) \to \mathbb{R}^3$$

$$\boxed{\boldsymbol{\theta} = \mathbf{S}\ominus\mathbf{R} \triangleq \mathrm{Log}(\mathbf{R}^{-1}\circ\mathbf{S})}$$

각 표현으로는

$$\boldsymbol{\theta} = \mathbf{q}_S\ominus\mathbf{q}_R = \mathrm{Log}(\mathbf{q}_R^*\otimes\mathbf{q}_S), \qquad \boldsymbol{\theta} = \mathbf{R}_S\ominus\mathbf{R}_R = \mathrm{Log}(\mathbf{R}_R^\top\mathbf{R}_S)$$

이 차이 $\boldsymbol{\theta}$ 는 **기준 원소 $\mathbf{R}$ 에서의 접공간**에 표현된 값이다.

> [!note] $\boldsymbol{\theta}$ 가 작아야만 성립하는 건 아니다
> 보통 이 차이는 작은 값을 다룰 때 쓰지만, 위 정의는 **$\boldsymbol{\theta}$ 가 어떤 값이든 성립한다.** 단, $SO(3)$ 매니폴드의 첫 번째 덮개 범위 안, 즉 각도 $\theta < \pi$ 인 범위에서만 유일하게 정의된다. ([[Chapter 02 - 회전과 상호관계|2장]] 4.5절의 이중 덮개 문제와 연결된다.)

### 1.3 왜 이 두 연산이 중요한가

| 벡터 공간 $\mathbb{R}^n$ | 매니폴드 $SO(3)$ |
|---|---|
| $x + \delta x$ | $\mathbf{R}\oplus\boldsymbol{\theta}$ |
| $x_2 - x_1$ | $\mathbf{R}_2\ominus\mathbf{R}_1$ |
| 미분: $\frac{f(x+\delta x)-f(x)}{\delta x}$ | 미분: $\frac{f(\mathbf{R}\oplus\boldsymbol{\theta})\ominus f(\mathbf{R})}{\boldsymbol{\theta}}$ |

**$\{+,-\}$ 를 $\{\oplus,\ominus\}$ 로 바꾸면 미분의 정의를 그대로 옮겨 쓸 수 있다.** 이것이 다음 절의 내용이다.

---

## 2. 네 가지 미분 정의

함수의 **입력과 출력이 각각 벡터 공간이냐 $SO(3)$ 냐**에 따라 네 가지 조합이 나온다. 각 경우에 맞는 연산자를 골라 쓰면 된다.

| | 출력: 벡터 공간 | 출력: $SO(3)$ |
|---|---|---|
| **입력: 벡터 공간** | $\{+,-\}$ (고전적) | $\{+,\ominus\}$ |
| **입력: $SO(3)$** | $\{\oplus,-\}$ | $\{\oplus,\ominus\}$ |

### 2.1 벡터 공간 → 벡터 공간

평범한 미분이다. $f:\mathbb{R}^m\to\mathbb{R}^n$ 에 대해

$$\frac{\partial f(\mathbf{x})}{\partial\mathbf{x}} \triangleq \lim_{\delta\mathbf{x}\to 0}\frac{f(\mathbf{x}+\delta\mathbf{x}) - f(\mathbf{x})}{\delta\mathbf{x}} \in \mathbb{R}^{n\times m}$$

오일러 적분은 익숙한 선형 근사를 준다.

$$f(\mathbf{x}+\Delta\mathbf{x}) \approx f(\mathbf{x}) + \frac{\partial f}{\partial\mathbf{x}}\Delta\mathbf{x}$$

### 2.2 SO(3) → SO(3)

$f: SO(3)\to SO(3)$ 에 대해 $\{\oplus,\ominus\}$ 를 쓴다.

$$\frac{\partial f(\mathbf{R})}{\partial\boldsymbol{\theta}} \triangleq \lim_{\delta\boldsymbol{\theta}\to 0}\frac{f(\mathbf{R}\oplus\delta\boldsymbol{\theta})\ominus f(\mathbf{R})}{\delta\boldsymbol{\theta}} = \lim_{\delta\boldsymbol{\theta}\to 0}\frac{\mathrm{Log}\left(f^{-1}(\mathbf{R})\,f(\mathbf{R}\,\mathrm{Exp}(\delta\boldsymbol{\theta}))\right)}{\delta\boldsymbol{\theta}} \in \mathbb{R}^{3\times3}$$

오일러 적분은

$$f(\mathbf{R}\oplus\Delta\boldsymbol{\theta}) \approx f(\mathbf{R})\oplus\frac{\partial f}{\partial\boldsymbol{\theta}}\Delta\boldsymbol{\theta} = f(\mathbf{R})\,\mathrm{Exp}\!\left(\frac{\partial f}{\partial\boldsymbol{\theta}}\Delta\boldsymbol{\theta}\right)$$

### 2.3 벡터 공간 → SO(3)

$f:\mathbb{R}^m\to SO(3)$ 에 대해 입력에는 $+$, 출력에는 $\ominus$ 를 쓴다.

$$\frac{\partial f(\mathbf{x})}{\partial\mathbf{x}} \triangleq \lim_{\delta\mathbf{x}\to 0}\frac{f(\mathbf{x}+\delta\mathbf{x})\ominus f(\mathbf{x})}{\delta\mathbf{x}} = \lim_{\delta\mathbf{x}\to 0}\frac{\mathrm{Log}(f^{-1}(\mathbf{x})f(\mathbf{x}+\delta\mathbf{x}))}{\delta\mathbf{x}} \in \mathbb{R}^{3\times m}$$

### 2.4 SO(3) → 벡터 공간

$f: SO(3)\to\mathbb{R}^n$ 에 대해 입력에는 $\oplus$, 출력에는 $-$ 를 쓴다.

$$\frac{\partial f(\mathbf{R})}{\partial\boldsymbol{\theta}} \triangleq \lim_{\delta\boldsymbol{\theta}\to 0}\frac{f(\mathbf{R}\oplus\delta\boldsymbol{\theta}) - f(\mathbf{R})}{\delta\boldsymbol{\theta}} = \lim_{\delta\boldsymbol{\theta}\to 0}\frac{f(\mathbf{R}\,\mathrm{Exp}(\delta\boldsymbol{\theta})) - f(\mathbf{R})}{\delta\boldsymbol{\theta}} \in \mathbb{R}^{n\times 3}$$

> [!tip] 규칙은 하나다
> **회전이 있는 쪽에는 $\oplus$/$\ominus$ 를, 벡터가 있는 쪽에는 $+$/$-$ 를 쓴다.** 네 가지를 외울 필요 없이 이 원칙만 기억하면 된다.
>
> 그리고 결과인 자코비안은 **어느 경우든 평범한 행렬**이다. 크기만 잘 세면 된다. 회전이 개입한 차원은 3이 된다($SO(3)$ 의 자유도가 3이므로).

---

## 3. 유용한, 그리고 매우 유용한 회전의 자코비안

이제 실제로 쓸 자코비안들을 구한다. 벡터 $\mathbf{a}$ 를 단위축 $\mathbf{u}$ 를 중심으로 $\theta$ 만큼 회전시키는 상황을 생각하자. 회전을 세 가지 동등한 형태로 쓸 수 있다.

$$\boldsymbol{\theta} = \mathbf{u}\theta, \qquad \mathbf{q} = \mathbf{q}\{\boldsymbol{\theta}\}, \qquad \mathbf{R} = \mathbf{R}\{\boldsymbol{\theta}\}$$

### 3.1 벡터에 대한 자코비안 — 가장 쉬운 것

회전된 결과를 **회전 대상 벡터**로 미분하면

$$\frac{\partial(\mathbf{q}\otimes\mathbf{a}\otimes\mathbf{q}^*)}{\partial\mathbf{a}} = \frac{\partial(\mathbf{R}\mathbf{a})}{\partial\mathbf{a}} = \mathbf{R}$$

당연하다. $\mathbf{R}\mathbf{a}$ 는 $\mathbf{a}$ 에 대해 선형이므로 미분은 그냥 $\mathbf{R}$ 이다.

### 3.2 쿼터니언에 대한 자코비안 — 까다로운 것

반대로 **쿼터니언으로** 미분하는 것은 까다롭다. 표기를 가볍게 해서 $\mathbf{q} = [w\ \ \mathbf{v}]$ 라 쓰고 회전 작용을 전개하면

$$\mathbf{a}' = \mathbf{q}\otimes\mathbf{a}\otimes\mathbf{q}^* = w^2\mathbf{a} + 2w(\mathbf{v}\times\mathbf{a}) + 2(\mathbf{v}^\top\mathbf{a})\mathbf{v} - (\mathbf{v}^\top\mathbf{v})\mathbf{a}$$

여기서 각 성분으로 미분하면

$$\frac{\partial\mathbf{a}'}{\partial w} = 2(w\mathbf{a} + \mathbf{v}\times\mathbf{a})$$

$$\frac{\partial\mathbf{a}'}{\partial\mathbf{v}} = 2(\mathbf{v}^\top\mathbf{a}\,\mathbf{I}_3 + \mathbf{v}\mathbf{a}^\top - \mathbf{a}\mathbf{v}^\top - w[\mathbf{a}]_\times)$$

합쳐서 $3\times4$ 행렬로

$$\frac{\partial(\mathbf{q}\otimes\mathbf{a}\otimes\mathbf{q}^*)}{\partial\mathbf{q}} = 2\begin{bmatrix} w\mathbf{a}+\mathbf{v}\times\mathbf{a} & \big|\ \ \mathbf{v}^\top\mathbf{a}\,\mathbf{I}_3 + \mathbf{v}\mathbf{a}^\top - \mathbf{a}\mathbf{v}^\top - w[\mathbf{a}]_\times\end{bmatrix} \in \mathbb{R}^{3\times4}$$

> [!warning] 이것이 바로 ESKF를 쓰는 이유다
> 자코비안이 $3\times4$ 다. **입력이 4개인데 자유도는 3개**다. 즉 **과매개변수화(over-parametrized)** 되어 있다. 이런 자코비안으로 공분산을 계산하면 $4\times4$ 공분산 행렬이 나오는데, 이 행렬은 **반드시 특이(singular)** 하다. 랭크가 3인데 크기는 4이기 때문이다.
>
> 칼만 필터에서 특이 공분산은 재앙이다. 역행렬을 구해야 하는데 구할 수 없다. 이것이 **오차상태(error-state)를 도입해서 3차원으로 다루는 근본 이유**다. [[왜 오차상태를 쓰는가]]에 더 자세히 정리했다.

### 3.3 SO(3)의 우자코비안 — 이 장의 핵심

![[fig_4_2.png]]
*그림 4.2 — 우자코비안 $\mathbf{J}_r = \partial\boldsymbol{\theta}/\partial\delta\boldsymbol{\phi}$ 는 매개변수 $\boldsymbol{\theta}$ 주변의 변화 $\delta\boldsymbol{\theta}$ 를, 점 $\mathrm{Exp}(\boldsymbol{\theta})$ 에서 매니폴드에 접하는 벡터 공간 위의 변화 $\delta\boldsymbol{\phi}$ 로 옮긴다.*

#### 문제 설정

$\mathbf{R} = \mathrm{Exp}(\boldsymbol{\theta})$ 인 상황에서, **$\boldsymbol{\theta}$ 를 $\delta\boldsymbol{\theta}$ 만큼 흔들면 $\mathbf{R}$ 은 얼마나 변하는가?**

여기서 함정이 있다. $\mathbf{R}$ 의 변화를 **매니폴드 위의 접공간에서** 측정해야 한다는 것이다. 그 변화량을 $\delta\boldsymbol{\phi}$ 라 하면 그림 4.2가 보여주는 관계는

$$\mathrm{Exp}(\boldsymbol{\theta})\oplus\delta\boldsymbol{\phi} = \mathrm{Exp}(\boldsymbol{\theta}+\delta\boldsymbol{\theta})$$

즉

$$\mathrm{Exp}(\boldsymbol{\theta})\,\mathrm{Exp}(\delta\boldsymbol{\phi}) = \mathrm{Exp}(\boldsymbol{\theta}+\delta\boldsymbol{\theta})$$

> [!important] 왜 $\delta\boldsymbol{\theta} \neq \delta\boldsymbol{\phi}$ 인가
> **매개변수 공간에서 $\delta\boldsymbol{\theta}$ 만큼 움직인 것이, 매니폴드 위에서는 $\delta\boldsymbol{\phi}$ 만큼의 회전으로 나타난다.** 이 둘은 일반적으로 같지 않다.
>
> 지구본 비유가 도움이 된다. 위도·경도라는 **매개변수**를 똑같이 1도씩 바꿔도, **실제 지표면에서 움직인 거리**는 적도냐 극지방이냐에 따라 완전히 다르다. 곡면이 휘어 있기 때문이다. 우자코비안은 그 "환산율"이다.

#### 정의

$$\boxed{\mathbf{J}_r(\boldsymbol{\theta}) \triangleq \frac{\partial\,\mathrm{Exp}(\boldsymbol{\theta})}{\partial\boldsymbol{\theta}} = \lim_{\delta\boldsymbol{\theta}\to 0}\frac{\mathrm{Exp}(\boldsymbol{\theta}+\delta\boldsymbol{\theta})\ominus\mathrm{Exp}(\boldsymbol{\theta})}{\delta\boldsymbol{\theta}}}$$

이것을 **$SO(3)$ 의 우자코비안(right Jacobian)** 이라 한다. "우(right)"인 이유는 섭동이 **오른쪽에** 곱해지기 때문이다.

#### 폐형식 공식

Chirikjian (2012)에 따르면 닫힌 형태로 계산할 수 있다.

$$\mathbf{J}_r(\boldsymbol{\theta}) = \mathbf{I} - \frac{1-\cos\|\boldsymbol{\theta}\|}{\|\boldsymbol{\theta}\|^2}[\boldsymbol{\theta}]_\times + \frac{\|\boldsymbol{\theta}\|-\sin\|\boldsymbol{\theta}\|}{\|\boldsymbol{\theta}\|^3}[\boldsymbol{\theta}]_\times^2$$

$$\mathbf{J}_r^{-1}(\boldsymbol{\theta}) = \mathbf{I} + \frac{1}{2}[\boldsymbol{\theta}]_\times + \left(\frac{1}{\|\boldsymbol{\theta}\|^2} - \frac{1+\cos\|\boldsymbol{\theta}\|}{2\|\boldsymbol{\theta}\|\sin\|\boldsymbol{\theta}\|}\right)[\boldsymbol{\theta}]_\times^2$$

#### 실전에서 쓰는 세 가지 성질

$$\mathrm{Exp}(\boldsymbol{\theta}+\delta\boldsymbol{\theta}) \approx \mathrm{Exp}(\boldsymbol{\theta})\,\mathrm{Exp}(\mathbf{J}_r(\boldsymbol{\theta})\,\delta\boldsymbol{\theta})$$

$$\mathrm{Exp}(\boldsymbol{\theta})\,\mathrm{Exp}(\delta\boldsymbol{\theta}) \approx \mathrm{Exp}(\boldsymbol{\theta}+\mathbf{J}_r^{-1}(\boldsymbol{\theta})\,\delta\boldsymbol{\theta})$$

$$\mathrm{Log}(\mathrm{Exp}(\boldsymbol{\theta})\,\mathrm{Exp}(\delta\boldsymbol{\theta})) \approx \boldsymbol{\theta} + \mathbf{J}_r^{-1}(\boldsymbol{\theta})\,\delta\boldsymbol{\theta}$$

> [!tip] 이 세 줄이 하는 일
> 이 공식들은 **지수 안쪽의 덧셈과 바깥쪽의 곱셈을 서로 바꿔 주는 번역기**다. $\mathrm{Exp}(\mathbf{a}+\mathbf{b}) \neq \mathrm{Exp}(\mathbf{a})\mathrm{Exp}(\mathbf{b})$ 라는 골치 아픈 사실(행렬 지수는 교환법칙이 없으므로)을, 우자코비안이라는 보정 항을 하나 끼워서 해결한다.
>
> **다행히 ESKF에서는 $\boldsymbol{\theta}$ 가 항상 작다.** $\|\boldsymbol{\theta}\|\to0$ 이면 $\mathbf{J}_r \to \mathbf{I}$ 가 되어 보정이 필요 없어진다. 이것이 오차상태를 쓰면 계산이 간단해지는 또 하나의 이유다.

### 3.4 회전 벡터에 대한 자코비안

회전된 벡터 $\mathbf{a}' = \mathbf{R}\{\boldsymbol{\theta}\}\mathbf{a}$ 를 **회전 벡터 $\boldsymbol{\theta}$** 로 미분한다. 위의 첫 번째 성질을 쓰면

$$\frac{\partial(\mathbf{R}\{\boldsymbol{\theta}\}\mathbf{a})}{\partial\boldsymbol{\theta}} = \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathbf{R}\{\boldsymbol{\theta}\}\mathrm{Exp}(\mathbf{J}_r\delta\boldsymbol{\theta})\mathbf{a} - \mathbf{R}\{\boldsymbol{\theta}\}\mathbf{a}}{\delta\boldsymbol{\theta}}$$

$\mathrm{Exp}(\boldsymbol{\epsilon})\approx\mathbf{I}+[\boldsymbol{\epsilon}]_\times$ 로 근사하고, $[\mathbf{b}]_\times\mathbf{a} = -[\mathbf{a}]_\times\mathbf{b}$ 를 쓰면

$$\boxed{\frac{\partial(\mathbf{q}\otimes\mathbf{a}\otimes\mathbf{q}^*)}{\partial\boldsymbol{\theta}} = \frac{\partial(\mathbf{R}\mathbf{a})}{\partial\boldsymbol{\theta}} = -\mathbf{R}\{\boldsymbol{\theta}\}[\mathbf{a}]_\times\mathbf{J}_r(\boldsymbol{\theta})}$$

> [!note] 크기를 보라
> 이번에는 자코비안이 $3\times3$ 이다. 3.2절의 $3\times4$ 와 비교해 보라. **회전 벡터로 미분하니 정사각 행렬이 나왔다.** 특이하지 않고, 역행렬도 구할 수 있다. ESKF가 오차를 회전 벡터(3개)로 다루는 이유가 여기 또 한 번 드러난다.

### 3.5 회전 합성의 자코비안

$SO(3)$ 의 합성 $\mathbf{P} = \mathbf{Q}\circ\mathbf{R}$ 을 생각하자. 쿼터니언으로도 행렬로도 쓸 수 있다.

$$\mathbf{p} = \mathbf{q}\otimes\mathbf{r}, \qquad \mathbf{P} = \mathbf{Q}\,\mathbf{R}$$

이것은 $SO(3)\to SO(3)$ 함수이므로 2.2절의 정의를 쓴다. 각 인자에 대한 미분을 구해 보자.

**왼쪽 인자에 대해** — 섭동 $\delta\boldsymbol{\theta}_Q$ 를 $\mathbf{Q}$ 에 가한다.

$$\begin{aligned}
\frac{\partial(\mathbf{Q}\circ\mathbf{R})}{\partial\delta\boldsymbol{\theta}_Q}
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\big((\mathbf{Q}\oplus\delta\boldsymbol{\theta})\mathbf{R}\big)\ominus(\mathbf{Q}\mathbf{R})}{\delta\boldsymbol{\theta}} \\
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathrm{Log}\big[(\mathbf{Q}\mathbf{R})^\top\,\mathbf{Q}\,\mathrm{Exp}(\delta\boldsymbol{\theta})\,\mathbf{R}\big]}{\delta\boldsymbol{\theta}} \\
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathrm{Log}\big[\mathbf{R}^\top\,\mathrm{Exp}(\delta\boldsymbol{\theta})\,\mathbf{R}\big]}{\delta\boldsymbol{\theta}} \\
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathrm{Log}\big[\mathrm{Exp}(\mathbf{R}^\top\delta\boldsymbol{\theta})\big]}{\delta\boldsymbol{\theta}} = \mathbf{R}^\top
\end{aligned}$$

**오른쪽 인자에 대해** — 섭동을 $\mathbf{R}$ 에 가한다.

$$\begin{aligned}
\frac{\partial(\mathbf{Q}\circ\mathbf{R})}{\partial\delta\boldsymbol{\theta}_R}
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathrm{Log}\big[(\mathbf{Q}\mathbf{R})^\top\,\mathbf{Q}\mathbf{R}\,\mathrm{Exp}(\delta\boldsymbol{\theta})\big]}{\delta\boldsymbol{\theta}} \\
&= \lim_{\delta\boldsymbol{\theta}\to0}\frac{\mathrm{Log}\big[\mathrm{Exp}(\delta\boldsymbol{\theta})\big]}{\delta\boldsymbol{\theta}} = \mathbf{I}
\end{aligned}$$

정리하면

$$\boxed{\frac{\partial(\mathbf{Q}\circ\mathbf{R})}{\partial\delta\boldsymbol{\theta}_Q} = \mathbf{R}^\top, \qquad \frac{\partial(\mathbf{Q}\circ\mathbf{R})}{\partial\delta\boldsymbol{\theta}_R} = \mathbf{I}}$$

> [!important] 놀랍도록 단순한 결과
> 유도 과정에서 쓴 핵심 항등식은 $\mathbf{R}^\top\mathrm{Exp}(\boldsymbol{\theta})\mathbf{R} = \mathrm{Exp}(\mathbf{R}^\top\boldsymbol{\theta})$ 다. 이를 **수반 작용(adjoint)** 이라 부르며, 리 군 이론의 기본 도구다.
>
> **오른쪽 인자의 자코비안이 그냥 $\mathbf{I}$** 라는 점이 특히 유용하다. 섭동을 오른쪽(국소)에 정의하면 합성의 자코비안이 공짜가 된다는 뜻이다. [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]에서 자세 갱신 $\mathbf{q}\leftarrow\mathbf{q}\otimes\mathbf{q}\{\boldsymbol{\omega}\Delta t\}$ 의 자코비안을 쉽게 구할 수 있는 이유다.

---

## 4. 섭동, 불확실성, 잡음

이제 **회전에 붙은 작은 오차**를 어떻게 표현할지 정한다. 이것이 ESKF 설계의 근본 선택이다.

### 4.1 국소 섭동 (Local perturbations)

섭동을 **오른쪽에** 곱한다.

$$\tilde{\mathbf{q}}_L = \mathbf{q}_L\otimes\mathrm{Exp}(\delta\boldsymbol{\theta}_L), \qquad \tilde{\mathbf{R}}_L = \mathbf{R}_L\,\mathrm{Exp}(\delta\boldsymbol{\theta}_L)$$

섭동을 꺼내려면

$$\delta\boldsymbol{\theta}_L = \mathrm{Log}(\mathbf{q}_L^*\otimes\tilde{\mathbf{q}}_L) = \mathrm{Log}(\mathbf{R}_L^\top\tilde{\mathbf{R}}_L)$$

섭동각이 작으면 테일러 전개의 1차 항까지만 취해 아주 간단해진다.

$$\mathbf{q}\{\delta\boldsymbol{\theta}_L\} \approx \begin{bmatrix} 1 \\ \tfrac{1}{2}\delta\boldsymbol{\theta}_L\end{bmatrix}, \qquad \mathbf{R}\{\delta\boldsymbol{\theta}_L\} \approx \mathbf{I} + [\delta\boldsymbol{\theta}_L]_\times$$

> [!important] 이 근사가 ESKF 계산을 전부 쉽게 만든다
> 삼각함수가 사라지고 **1차식만 남는다.** $\cos(\theta/2)\approx1$, $\sin(\theta/2)\approx\theta/2$ 를 쓴 결과다. 오차가 항상 작다는 것이 보장되기 때문에 이 근사를 마음 놓고 쓸 수 있고, 그래서 자코비안이 단순해진다.

이렇게 하면 섭동을 **현재 자세에서의 접공간 $\delta\boldsymbol{\theta}_L$** 에 표현하게 되고, 그 공분산을 평범한 $3\times3$ 행렬로 쓸 수 있다.

### 4.2 전역 섭동 (Global perturbations)

섭동을 **왼쪽에** 곱하는 방법도 있다.

$$\tilde{\mathbf{q}}_G = \mathrm{Exp}(\delta\boldsymbol{\theta}_G)\otimes\mathbf{q}_G, \qquad \tilde{\mathbf{R}}_G = \mathrm{Exp}(\delta\boldsymbol{\theta}_G)\,\mathbf{R}_G$$

$$\delta\boldsymbol{\theta}_G = \mathrm{Log}(\tilde{\mathbf{q}}_G\otimes\mathbf{q}_G^*) = \mathrm{Log}(\tilde{\mathbf{R}}_G\,\mathbf{R}_G^\top)$$

이 경우 섭동은 **원점에서의 접공간**, 즉 전역 좌표계에 표현된다.

> [!note] 어느 쪽을 택할 것인가
> | | 국소(Local) | 전역(Global) |
> |---|---|---|
> | 곱하는 위치 | 오른쪽 | 왼쪽 |
> | 표현 좌표계 | 현재 자세(body) | 전역(world) |
> | 이 논문의 기본 | ✅ 5·6장 | 7장에서 따로 |
>
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]과 [[Chapter 06 - IMU와 보조센서 융합|6장]]은 **국소 섭동**으로 전개한다. 자이로가 body 좌표계에서 각속도를 주기 때문에 자연스럽다. 다만 Li와 Mourikis (2012)는 **전역 각오차가 더 좋은 성질**을 가진다는 증거를 제시했고, 그래서 [[Chapter 07 - 전역 각오차를 쓰는 ESKF|7장]]이 따로 존재한다.

---

## 5. 시간 미분

섭동을 벡터 공간에 표현했으니, 이제 시간 미분을 쉽게 유도할 수 있다.

### 5.1 쿼터니언의 시간 미분

$\mathbf{q}(t)$ 를 원래 상태, $\tilde{\mathbf{q}} = \mathbf{q}(t+\Delta t)$ 를 섭동된 상태로 보고 미분의 정의를 적용한다.

$$\boldsymbol{\omega}_L(t) \triangleq \frac{d\boldsymbol{\theta}_L(t)}{dt} = \lim_{\Delta t\to0}\frac{\delta\boldsymbol{\theta}_L}{\Delta t}$$

여기서 $\delta\boldsymbol{\theta}_L$ 이 국소 각 섭동이므로, $\boldsymbol{\omega}_L$ 은 **$\mathbf{q}$ 가 정의하는 국소 좌표계에서의 각속도 벡터**다.

전개하면

$$\dot{\mathbf{q}} = \lim_{\Delta t\to0}\frac{\mathbf{q}\otimes\mathbf{q}\{\delta\boldsymbol{\theta}_L\} - \mathbf{q}}{\Delta t} = \lim_{\Delta t\to0}\frac{\mathbf{q}\otimes\left(\begin{bmatrix}1\\ \delta\boldsymbol{\theta}_L/2\end{bmatrix} - \begin{bmatrix}1\\ \mathbf{0}\end{bmatrix}\right)}{\Delta t} = \frac{1}{2}\mathbf{q}\otimes\begin{bmatrix}0\\ \boldsymbol{\omega}_L\end{bmatrix}$$

따라서

$$\boxed{\dot{\mathbf{q}} = \frac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}_L, \qquad \dot{\mathbf{R}} = \mathbf{R}\,[\boldsymbol{\omega}_L]_\times}$$

행렬 형태로도 쓸 수 있다. $\boldsymbol{\Omega}(\boldsymbol{\omega}) \triangleq [\boldsymbol{\omega}]_R$ 로 두면

$$\boldsymbol{\Omega}(\boldsymbol{\omega}) = \begin{bmatrix} 0 & -\boldsymbol{\omega}^\top \\ \boldsymbol{\omega} & -[\boldsymbol{\omega}]_\times\end{bmatrix} = \begin{bmatrix} 0 & -\omega_x & -\omega_y & -\omega_z \\ \omega_x & 0 & \omega_z & -\omega_y \\ \omega_y & -\omega_z & 0 & \omega_x \\ \omega_z & \omega_y & -\omega_x & 0\end{bmatrix}$$

$$\dot{\mathbf{q}} = \frac{1}{2}\boldsymbol{\Omega}(\boldsymbol{\omega}_L)\,\mathbf{q}$$

> [!important] 드디어 $1/2$ 의 출처가 명확해졌다
> [[Chapter 02 - 회전과 상호관계|2장]]에서 미뤄 둔 그 $1/2$ 이다. 위 유도를 보면 출처가 분명하다. **작은 회전의 쿼터니언 근사 $\mathbf{q}\{\delta\boldsymbol{\theta}\}\approx[1,\ \delta\boldsymbol{\theta}/2]$ 에서 온 것**이고, 그 $1/2$ 은 다시 [[Chapter 02 - 회전과 상호관계|2장]] 8절의 등경사 회전에서 "각 곱이 절반씩 기여한다"는 사실에서 왔다. 모든 것이 연결된다.

### 5.2 전역 섭동일 때

똑같은 논리를 전역 섭동에 적용하면

$$\dot{\mathbf{q}} = \frac{1}{2}\boldsymbol{\omega}_G\otimes\mathbf{q}, \qquad \dot{\mathbf{R}} = [\boldsymbol{\omega}_G]_\times\,\mathbf{R}$$

**각속도가 왼쪽으로 갔다.** 국소이면 오른쪽, 전역이면 왼쪽. 섭동을 어디에 곱했느냐와 정확히 일치한다.

### 5.3 전역-국소 관계

두 식을 나란히 놓으면

$$\frac{1}{2}\boldsymbol{\omega}_G\otimes\mathbf{q} = \dot{\mathbf{q}} = \frac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}_L$$

양변 오른쪽에 $\mathbf{q}^*$ 를 곱하면

$$\boxed{\boldsymbol{\omega}_G = \mathbf{q}\otimes\boldsymbol{\omega}_L\otimes\mathbf{q}^* = \mathbf{R}\,\boldsymbol{\omega}_L}$$

작은 각 섭동에 대해서도 마찬가지다.

$$\delta\boldsymbol{\theta}_G = \mathbf{q}\otimes\delta\boldsymbol{\theta}_L\otimes\mathbf{q}^* = \mathbf{R}\,\delta\boldsymbol{\theta}_L$$

> [!tip] 각속도와 작은 각오차는 그냥 보통 벡터처럼 변환된다
> 이 결과는 실무에서 매우 유용하다. **각속도 벡터와 작은 각 섭동은 평범한 벡터처럼 회전 변환하면 된다.** 회전축 벡터 $\mathbf{u}$ 가 $\mathbf{u}_G = \mathbf{R}\mathbf{u}_L$ 로 변환되는 것과 같은 이치다.

### 5.4 쿼터니언 곱의 시간 미분

곱의 미분 법칙은 그대로 성립하지만, **순서를 엄격히 지켜야 한다.**

$$\dot{\overline{(\mathbf{q}_1\otimes\mathbf{q}_2)}} = \dot{\mathbf{q}}_1\otimes\mathbf{q}_2 + \mathbf{q}_1\otimes\dot{\mathbf{q}}_2$$

> [!warning] 제곱의 미분에 2를 곱하면 안 된다
> 스칼라라면 $(q^2)' = 2q\dot{q}$ 지만, 쿼터니언은 교환이 안 되므로
> $$\dot{\overline{(\mathbf{q}^2)}} = \dot{\mathbf{q}}\otimes\mathbf{q} + \mathbf{q}\otimes\dot{\mathbf{q}} \neq 2\,\mathbf{q}\otimes\dot{\mathbf{q}}$$
> 이다. 흔한 실수다.

---

### 5.5 각속도를 거꾸로 뽑아내기

시간 미분에서 각속도를 역산하는 표현도 유용하다. 국소 각속도는

$$\boldsymbol{\omega}_L = 2\,\mathbf{q}^*\otimes\dot{\mathbf{q}}, \qquad [\boldsymbol{\omega}_L]_\times = \mathbf{R}^\top\dot{\mathbf{R}}$$

전역 각속도는

$$\boldsymbol{\omega}_G = 2\,\dot{\mathbf{q}}\otimes\mathbf{q}^*, \qquad [\boldsymbol{\omega}_G]_\times = \dot{\mathbf{R}}\,\mathbf{R}^\top$$

> [!note] $\mathbf{R}^\top\dot{\mathbf{R}}$ 이 반대칭인 이유
> $\mathbf{R}^\top\mathbf{R}=\mathbf{I}$ 를 미분하면 $\dot{\mathbf{R}}^\top\mathbf{R}+\mathbf{R}^\top\dot{\mathbf{R}}=0$, 즉 $(\mathbf{R}^\top\dot{\mathbf{R}})^\top = -(\mathbf{R}^\top\dot{\mathbf{R}})$ 이다. **반대칭행렬일 수밖에 없고**, 그래서 각속도 벡터 하나로 표현된다. 이것이 [[리 군과 리 대수|리 대수 $\mathfrak{so}(3)$]] 가 반대칭행렬들의 집합인 근본 이유다.

---

## 6. 각속도의 시간적분

마지막으로 실전 문제다. **자이로스코프가 각속도를 찍어 주면, 그것을 어떻게 적분해서 자세를 갱신할 것인가?**

우리가 관심 있는 경우에서 각속도는 **국소 센서**가 측정하므로, 이산 시각 $t_n = n\Delta t$ 에서 국소 측정값 $\boldsymbol{\omega}(t_n)$ 을 얻는다. 따라서 국소 미분방정식을 적분한다.

$$\dot{\mathbf{q}}(t) = \tfrac{1}{2}\mathbf{q}(t)\otimes\boldsymbol{\omega}(t)$$

### 6.0 테일러 급수 — 모든 적분법의 출발점

0차·1차 적분법은 전부 $\mathbf{q}(t_n+\Delta t)$ 를 $t=t_n$ 주변에서 테일러 전개한 것에서 나온다. $\mathbf{q}\triangleq\mathbf{q}(t)$, $\mathbf{q}_n\triangleq\mathbf{q}(t_n)$ 으로 쓰면

$$\mathbf{q}_{n+1} = \mathbf{q}_n + \dot{\mathbf{q}}_n\Delta t + \tfrac{1}{2!}\ddot{\mathbf{q}}_n\Delta t^2 + \tfrac{1}{3!}\dddot{\mathbf{q}}_n\Delta t^3 + \tfrac{1}{4!}\ddddot{\mathbf{q}}_n\Delta t^4 + \cdots$$

각 미분값은 $\dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}$ 를 반복 적용해서 얻는다. $\dot{\boldsymbol{\omega}}=0$ 인 경우(각속도가 일정)

$$\begin{aligned}
\dot{\mathbf{q}}_n &= \tfrac{1}{2}\mathbf{q}_n\boldsymbol{\omega}_n \\
\ddot{\mathbf{q}}_n &= \tfrac{1}{2^2}\mathbf{q}_n\boldsymbol{\omega}_n^2 + \tfrac{1}{2}\mathbf{q}_n\dot{\boldsymbol{\omega}}_n \\
\dddot{\mathbf{q}}_n &= \tfrac{1}{2^3}\mathbf{q}_n\boldsymbol{\omega}_n^3 + \tfrac{1}{4}\mathbf{q}_n\dot{\boldsymbol{\omega}}_n\boldsymbol{\omega}_n + \tfrac{1}{2}\dot{\mathbf{q}}_n\dot{\boldsymbol{\omega}}_n \\
\mathbf{q}_n^{(i\ge4)} &= \tfrac{1}{2^i}\mathbf{q}_n\boldsymbol{\omega}_n^i + \cdots
\end{aligned}$$

여기서 표기를 아끼려고 $\otimes$ 기호를 생략했다. **모든 곱과 $\boldsymbol{\omega}$ 의 거듭제곱은 쿼터니언 곱으로 해석해야 한다.**

> [!tip] 이 급수가 뒤의 모든 공식을 낳는다
> $\dot{\boldsymbol{\omega}}=0$ 으로 두고 항을 모으면 $\mathbf{q}_n\otimes\exp(\boldsymbol{\omega}\Delta t/2)$ 가 되어 **0차 적분**이 나온다. $\dot{\boldsymbol{\omega}}\neq0$ 항까지 살리면 **1차 적분**의 외적 보정 항이 나온다.

![[fig_4_3.png]]
*그림 4.3 — 적분을 위한 각속도 근사. 빨강: 실제 각속도. 파랑: 0차 근사(아래부터 위로 forward, midward, backward). 초록: 1차 근사.*

### 6.1 0차 적분 (Zeroth order)

구간 $[t_n, t_{n+1}]$ 동안 각속도가 **일정하다고 가정**한다. 그러면

$$\mathbf{q}_{n+1} = \mathbf{q}_n\otimes\mathrm{Exp}(\boldsymbol{\omega}\Delta t)$$

문제는 "어떤 $\boldsymbol{\omega}$ 를 쓸 것인가"다. 그림 4.3의 파란 선 세 개가 각각의 선택지다.

| 방법 | 사용하는 값 | 특징 |
|---|---|---|
| **전진(forward)** | $\boldsymbol{\omega}_n$ | 구간 시작값. 가장 단순하지만 뒤처진다 |
| **후진(backward)** | $\boldsymbol{\omega}_{n+1}$ | 구간 끝값. 앞서간다 |
| **중간(midward)** | $\bar{\boldsymbol{\omega}} = \dfrac{\boldsymbol{\omega}_n+\boldsymbol{\omega}_{n+1}}{2}$ | **평균값. 오차가 가장 작다** |

> [!tip] 실무에서는 중간값을 쓴다
> 그림에서 보듯 빨간 곡선(실제)과 비교했을 때 중간값(가운데 파란 선)이 면적 오차가 가장 작다. 구현 비용은 덧셈 한 번과 나눗셈 한 번뿐이니, 특별한 이유가 없다면 중간값을 쓰는 게 좋다.

### 6.2 1차 적분 (First order)

각속도가 구간 안에서 **선형으로 변한다고 가정**한다(그림 4.3의 초록 직선). 각가속도를

$$\dot{\boldsymbol{\omega}} = \frac{\boldsymbol{\omega}_{n+1}-\boldsymbol{\omega}_n}{\Delta t}$$

라 하면, 적분 결과는 중간값 항에 보정 항이 붙은 형태가 된다.

$$\mathbf{q}_{n+1} = \mathbf{q}_n\otimes\mathrm{Exp}\!\left(\bar{\boldsymbol{\omega}}\Delta t + \frac{\Delta t^2}{24}\boldsymbol{\omega}_n\times\boldsymbol{\omega}_{n+1}\right)$$

> [!note] 외적 보정 항의 의미
> 추가된 항 $\frac{\Delta t^2}{24}\boldsymbol{\omega}_n\times\boldsymbol{\omega}_{n+1}$ 에 **외적**이 들어 있다. 이것은 **회전축 자체가 구간 동안 움직일 때** 생기는 효과를 보정한다. 축이 고정되어 있으면($\boldsymbol{\omega}_n \parallel \boldsymbol{\omega}_{n+1}$) 외적이 0이 되어 보정이 사라지고, 0차 중간값 방법과 같아진다.
>
> 이 효과를 항공우주 분야에서는 **코닝(coning)** 이라 부른다. 고성능 IMU 처리에서 중요하게 다루는 주제다.

![[fig_4_4.png]]
*그림 4.4 — 두 개의 연속된 시간 스텝(회색 화살표 묶음과 검은 화살표 묶음)에 대한 적분 방식들. 왼쪽부터 전진(forward), 중간(midward), 후진(backward) 방식.*

그림 4.4는 세 방식이 시간축에서 어떻게 다른지 보여 준다. 각 $\mathbf{q}_{n+1}$ 을 계산할 때 어떤 $\boldsymbol{\omega}$ 노드를 끌어다 쓰는지 화살표로 표시되어 있다.

---

## 정리 — 이 장에서 챙겨야 할 것

> [!abstract] 핵심 요약
> 1. **회전에는 덧셈이 없다.** 대신 $\oplus$(매니폴드 + 접공간 벡터)와 $\ominus$(두 회전의 차이 → 접공간 벡터)를 쓴다.
> 2. **미분은 네 가지 조합**이 있지만 규칙은 하나다. 회전 쪽엔 $\oplus/\ominus$, 벡터 쪽엔 $+/-$.
> 3. **쿼터니언으로 미분하면 $3\times4$**(특이), **회전 벡터로 미분하면 $3\times3$**(정상). 이것이 오차상태를 쓰는 이유다.
> 4. **우자코비안 $\mathbf{J}_r$** 은 매개변수 공간의 변화를 매니폴드 접공간의 변화로 환산한다. 작은 각에서는 $\mathbf{J}_r\to\mathbf{I}$.
> 5. **섭동은 국소(오른쪽 곱)** 또는 **전역(왼쪽 곱)** 으로 정의할 수 있고, 그에 따라 $\dot{\mathbf{q}}$ 의 각속도가 오른쪽/왼쪽으로 붙는다.
> 6. **적분은 중간값 0차**가 가성비가 좋고, 정밀도가 필요하면 **외적 보정이 붙은 1차**를 쓴다.

| 상황 | 공식 |
|---|---|
| 회전에 오차 더하기 | $\mathbf{q}\oplus\delta\boldsymbol{\theta} = \mathbf{q}\otimes\mathrm{Exp}(\delta\boldsymbol{\theta})$ |
| 두 회전의 차이 | $\mathbf{q}_2\ominus\mathbf{q}_1 = \mathrm{Log}(\mathbf{q}_1^*\otimes\mathbf{q}_2)$ |
| 작은 회전 근사 | $\mathbf{q}\{\delta\boldsymbol{\theta}\}\approx[1,\ \delta\boldsymbol{\theta}/2]$, $\mathbf{R}\approx\mathbf{I}+[\delta\boldsymbol{\theta}]_\times$ |
| 회전 벡터 자코비안 | $-\mathbf{R}[\mathbf{a}]_\times\mathbf{J}_r$ |
| 시간 미분(국소) | $\dot{\mathbf{q}} = \tfrac{1}{2}\mathbf{q}\otimes\boldsymbol{\omega}_L$ |
| 시간 미분(전역) | $\dot{\mathbf{q}} = \tfrac{1}{2}\boldsymbol{\omega}_G\otimes\mathbf{q}$ |
| 적분(중간값) | $\mathbf{q}_{n+1} = \mathbf{q}_n\otimes\mathrm{Exp}(\bar{\boldsymbol{\omega}}\Delta t)$ |

> [!note] 여기까지가 도구 준비다
> 1~4장으로 필요한 수학 도구는 전부 갖췄다. [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]부터는 이 도구를 써서 **실제 ESKF를 조립**한다.

---

## 관련 노트

- [[리 군과 리 대수]] — 매니폴드·접공간·지수사상의 개념
- [[자코비안과 공분산 전파]] — 자코비안이 왜 필요한지
- [[왜 오차상태를 쓰는가]] — $3\times4$ 자코비안 문제의 해법
- [[Chapter 03 - 쿼터니언 규약]] — 이전 장
- [[Chapter 05 - IMU 기반 오차상태 운동학]] — 다음 장
