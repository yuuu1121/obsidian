---
title: "부록 A~E — 수치적분과 전이행렬 (Appendices)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 99
tags: [ESKF, 수치적분, RungeKutta, 전이행렬, 공분산, 노이즈, 부록]
---

# 부록 A~E · 수치적분과 전이행렬

> [!abstract] 이 부록을 한 문장으로
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]에서 "가장 단순한 오일러 형태"라고 하고 넘어간 **전이행렬 $\mathbf{F}_x$ 를 더 정밀하게 구하는 방법들**을 모았다. Runge-Kutta 수치적분(A), 폐형식 해(B), 절단급수 근사(C), RK로 전이행렬 구하기(D), 그리고 **랜덤 노이즈의 적분**(E)이다.

> [!tip] 언제 읽어야 하나
> 처음 ESKF를 구현할 때는 **부록 E만 읽으면 된다.** 노이즈 공분산 $\mathbf{Q}_i$ 를 왜 그렇게 쓰는지가 거기 있다. A~D는 "오일러 근사로는 정밀도가 부족하다"는 문제를 실제로 겪었을 때 돌아와서 읽으면 된다.

---

# 부록 A · Runge-Kutta 수치적분

## A.0 문제 설정

다음 형태의 비선형 미분방정식을 풀고 싶다.

$$\dot{\mathbf{x}} = f(t,\mathbf{x})$$

제한된 시간 구간 $\Delta t$ 에 대해 적분해서 **차분방정식**으로 바꾸는 것이 목표다.

$$\mathbf{x}(t+\Delta t) = \mathbf{x}(t) + \int_t^{t+\Delta t}f(\tau,\mathbf{x}(\tau))\,d\tau$$

$t_n = n\Delta t$, $\mathbf{x}_n \triangleq \mathbf{x}(t_n)$ 로 쓰면

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \int_{n\Delta t}^{(n+1)\Delta t}f(\tau,\mathbf{x}(\tau))\,d\tau$$

가장 널리 쓰이는 방법이 **Runge-Kutta(RK)** 계열이다. 이 방법들은 **여러 번의 반복으로 구간 내 미분값을 추정**한 뒤, 그 미분값으로 $\Delta t$ 만큼 적분한다.

> [!note] 논문의 출처 명시
> 논문은 이 부록의 내용이 전부 영문 위키백과의 Runge-Kutta method 항목에서 가져온 것이라고 밝히고 있다. 표준적인 수치해석 내용이다.

## A.1 오일러 방법 (Euler method)

**미분값이 구간 내내 일정하다**고 가정한다.

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\,f(t_n,\mathbf{x}_n)$$

일반 RK 형식으로 보면 **1단계(single-stage)** 방법이다. 시작점에서 미분을 계산하고

$$\mathbf{k}_1 = f(t_n,\mathbf{x}_n)$$

그것으로 끝점 값을 구한다.

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\,\mathbf{k}_1$$

## A.2 중점 방법 (Midpoint method)

**구간 중점에서의 미분값**을 쓴다고 가정한다.

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\,f\!\left(t_n+\tfrac{1}{2}\Delta t,\ \mathbf{x}_n + \tfrac{1}{2}\Delta t\,f(t_n,\mathbf{x}_n)\right)$$

2단계로 나눠 설명하면 이렇다. 먼저 오일러 방법으로 중점까지 적분하고

$$\mathbf{k}_1 = f(t_n,\mathbf{x}_n), \qquad \mathbf{x}(t_n+\tfrac{1}{2}\Delta t) = \mathbf{x}_n + \tfrac{1}{2}\Delta t\,\mathbf{k}_1$$

그 값으로 중점에서의 미분 $\mathbf{k}_2$ 를 구해 적분한다.

$$\mathbf{k}_2 = f\!\left(t_n+\tfrac{1}{2}\Delta t,\ \mathbf{x}(t_n+\tfrac{1}{2}\Delta t)\right), \qquad \mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\,\mathbf{k}_2$$

> [!tip] [[Chapter 04 - 섭동 미분 적분|4장]] 6.1절과 연결된다
> 4장에서 각속도 적분할 때 **중간값(midward)** 이 오차가 가장 작다고 했던 것이 바로 이 방법이다.

## A.3 RK4 방법

그냥 "Runge-Kutta 방법"이라고 하면 보통 이것을 가리킨다. 구간의 **시작·중점·끝**에서 $f()$ 를 평가하며, **4개의 미분값 $\mathbf{k}_1 \dots \mathbf{k}_4$** 를 순차적으로 구한 뒤 **가중평균**하여 4차 정밀도의 미분 추정값을 얻는다.

$$\boxed{\mathbf{x}_{n+1} = \mathbf{x}_n + \frac{\Delta t}{6}\left(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4\right)}$$

각 기울기는

$$\begin{aligned}
\mathbf{k}_1 &= f(t_n,\ \mathbf{x}_n) \\
\mathbf{k}_2 &= f\!\left(t_n+\tfrac{\Delta t}{2},\ \mathbf{x}_n + \tfrac{\Delta t}{2}\mathbf{k}_1\right) \\
\mathbf{k}_3 &= f\!\left(t_n+\tfrac{\Delta t}{2},\ \mathbf{x}_n + \tfrac{\Delta t}{2}\mathbf{k}_2\right) \\
\mathbf{k}_4 &= f\!\left(t_n+\Delta t,\ \mathbf{x}_n + \Delta t\,\mathbf{k}_3\right)
\end{aligned}$$

> [!note] 가중치 $1:2:2:1$ 의 의미
> 중점에서 잰 두 기울기($\mathbf{k}_2, \mathbf{k}_3$)에 두 배의 무게를 준다. 심프슨 공식(Simpson's rule)과 같은 발상이다.

## A.4 일반 Runge-Kutta 방법

$s$ 단계 일반형은

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\sum_{i=1}^{s}b_i\mathbf{k}_i$$

$$\mathbf{k}_i = f\!\left(t_n + c_i\Delta t,\ \mathbf{x}_n + \Delta t\sum_{j=1}^{s}a_{ij}\mathbf{k}_j\right)$$

계수 $\{a_{ij}\}, \{b_i\}, \{c_i\}$ 를 모아 놓은 것을 **Butcher 표(Butcher tableau)** 라 한다. 위의 오일러·중점·RK4는 전부 이 일반형의 특수한 경우다.

---

# 부록 B · 폐형식 적분

## B.0 선형 시스템이면 정확한 해가 있다

**1차 선형 미분방정식**을 생각하자.

$$\dot{\mathbf{x}}(t) = \mathbf{A}\,\mathbf{x}(t)$$

관계가 선형이고 구간 내에서 $\mathbf{A}$ 가 상수라면, 구간 $[t_n, t_n+\Delta t]$ 에 대한 적분은

$$\boxed{\mathbf{x}_{n+1} = e^{\mathbf{A}\Delta t}\,\mathbf{x}_n = \boldsymbol{\Phi}\,\mathbf{x}_n}$$

여기서 $\boldsymbol{\Phi}$ 를 **전이행렬(transition matrix)** 이라 한다. 테일러 전개하면

$$\boldsymbol{\Phi} = e^{\mathbf{A}\Delta t} = \mathbf{I} + \mathbf{A}\Delta t + \tfrac{1}{2}\mathbf{A}^2\Delta t^2 + \tfrac{1}{3!}\mathbf{A}^3\Delta t^3 + \cdots = \sum_{k=0}^{\infty}\frac{1}{k!}\mathbf{A}^k\Delta t^k$$

> [!important] 이것이 $\mathbf{F}_x$ 의 정체다
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 4.3절의 $\mathbf{F}_x$ 가 바로 이 $\boldsymbol{\Phi}$ 다. 5장에서는 급수를 **1차에서 끊은** $\mathbf{I}+\mathbf{A}\Delta t$ 를 썼다. 부록 C가 더 높은 차수까지 가는 방법을 다룬다.

알려진 $\mathbf{A}$ 에 대해 이 급수를 쓰다 보면 **익숙한 급수가 튀어나오는 경우**가 있고, 그때는 적분 결과를 폐형식으로 쓸 수 있다.

## B.1 각오차의 적분 — 로드리게스가 다시 등장한다

바이어스와 노이즈를 뺀 각오차 동역학([[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 식의 정리된 버전)을 보자.

$$\dot{\delta\boldsymbol{\theta}} = -[\boldsymbol{\omega}]_\times\,\delta\boldsymbol{\theta}$$

전이행렬을 테일러 급수로 쓰면

$$\boldsymbol{\Phi} = e^{-[\boldsymbol{\omega}]_\times\Delta t} = \mathbf{I} - [\boldsymbol{\omega}]_\times\Delta t + \tfrac{1}{2}[\boldsymbol{\omega}]_\times^2\Delta t^2 - \tfrac{1}{3!}[\boldsymbol{\omega}]_\times^3\Delta t^3 + \tfrac{1}{4!}[\boldsymbol{\omega}]_\times^4\Delta t^4 - \cdots$$

이제 $\boldsymbol{\omega}\Delta t \triangleq \mathbf{u}\theta$ 로 두고(회전축과 회전각), $[\mathbf{u}]_\times$ 의 거듭제곱이 주기적이라는 성질([[Chapter 02 - 회전과 상호관계|2장]] 3.3절)을 쓰면 항들을 묶을 수 있다.

$$\begin{aligned}
\boldsymbol{\Phi} &= \mathbf{I} - [\mathbf{u}]_\times\left(\theta - \frac{\theta^3}{3!} + \frac{\theta^5}{5!} - \cdots\right) + [\mathbf{u}]_\times^2\left(\frac{\theta^2}{2!} - \frac{\theta^4}{4!} + \frac{\theta^6}{6!} - \cdots\right) \\
&= \mathbf{I} - [\mathbf{u}]_\times\sin\theta + [\mathbf{u}]_\times^2(1-\cos\theta)
\end{aligned}$$

> [!important] 로드리게스 공식이 그대로 나왔다
> 이 결과는 **회전행렬**이다. 정확히는
> $$\boldsymbol{\Phi} = \mathbf{R}\{-\mathbf{u}\theta\} = \mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}$$
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] $\mathbf{F}_x$ 의 각오차 대각 블록에 있던 $\mathbf{R}^\top\{(\boldsymbol{\omega}_m-\boldsymbol{\omega}_b)\Delta t\}$ 가 **근사가 아니라 정확한 폐형식 해**였던 것이다. 오일러 근사 $\mathbf{I}-[\boldsymbol{\omega}]_\times\Delta t$ 를 쓰는 대신 이걸 쓰면 그 블록만큼은 오차가 없다.

## B.2 단순화된 IMU 예제 — 블록별로 폐형식 구하기

중력과 센서 바이어스를 생략한 단순한 IMU 시스템을 보자.

$$\dot{\delta\mathbf{p}} = \delta\mathbf{v}, \qquad \dot{\delta\mathbf{v}} = -\mathbf{R}[\mathbf{a}]_\times\delta\boldsymbol{\theta}, \qquad \dot{\delta\boldsymbol{\theta}} = -[\boldsymbol{\omega}]_\times\delta\boldsymbol{\theta}$$

상태 벡터와 동역학 행렬은

$$\delta\mathbf{x} = \begin{bmatrix}\delta\mathbf{p}\\ \delta\mathbf{v}\\ \delta\boldsymbol{\theta}\end{bmatrix}, \qquad
\mathbf{A} = \begin{bmatrix}0&\mathbf{P}_v&0\\ 0&0&\mathbf{V}_\theta\\ 0&0&\boldsymbol{\Theta}_\theta\end{bmatrix}$$

$$\mathbf{P}_v = \mathbf{I}, \qquad \mathbf{V}_\theta = -\mathbf{R}[\mathbf{a}]_\times, \qquad \boldsymbol{\Theta}_\theta = -[\boldsymbol{\omega}]_\times$$

### B.2.1 거듭제곱의 규칙성을 찾는다

$\mathbf{A}$ 의 거듭제곱을 몇 개 써 보면 패턴이 드러난다.

$$\mathbf{A}^2 = \begin{bmatrix}0&0&\mathbf{P}_v\mathbf{V}_\theta\\ 0&0&\mathbf{V}_\theta\boldsymbol{\Theta}_\theta\\ 0&0&\boldsymbol{\Theta}_\theta^2\end{bmatrix}, \qquad
\mathbf{A}^3 = \begin{bmatrix}0&0&\mathbf{P}_v\mathbf{V}_\theta\boldsymbol{\Theta}_\theta\\ 0&0&\mathbf{V}_\theta\boldsymbol{\Theta}_\theta^2\\ 0&0&\boldsymbol{\Theta}_\theta^3\end{bmatrix}$$

따라서 $k>1$ 에 대해

$$\mathbf{A}^{k>1} = \begin{bmatrix}0&0&\mathbf{P}_v\mathbf{V}_\theta\boldsymbol{\Theta}_\theta^{k-2}\\ 0&0&\mathbf{V}_\theta\boldsymbol{\Theta}_\theta^{k-1}\\ 0&0&\boldsymbol{\Theta}_\theta^k\end{bmatrix}$$

> [!important] 관찰이 열쇠다
> **고정된 부분과 $\boldsymbol{\Theta}_\theta$ 의 증가하는 거듭제곱**으로 이루어져 있다. 그리고 $\boldsymbol{\Theta}_\theta = -[\boldsymbol{\omega}]_\times$ 의 거듭제곱은 B.1절에서 본 대로 **주기적**이다. 그래서 급수를 닫힌 형태로 묶을 수 있다.

전이행렬을 블록으로 나눠 쓴다.

$$\boldsymbol{\Phi} = \begin{bmatrix}\mathbf{I}&\boldsymbol{\Phi}_{pv}&\boldsymbol{\Phi}_{p\theta}\\ 0&\mathbf{I}&\boldsymbol{\Phi}_{v\theta}\\ 0&0&\boldsymbol{\Phi}_{\theta\theta}\end{bmatrix}$$

### B.2.2 블록 하나씩 정복하기

**대각 블록 두 개** — 위 두 개는 보이는 대로 단위행렬이다.

**회전 대각 블록** $\boldsymbol{\Phi}_{\theta\theta}$ — B.1절의 결과 그대로다.

$$\boldsymbol{\Phi}_{\theta\theta} = \sum_{k=0}^\infty\frac{1}{k!}\boldsymbol{\Theta}_\theta^k\Delta t^k = \mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}$$

**위치-속도 블록** — 가장 쉽다.

$$\boldsymbol{\Phi}_{pv} = \mathbf{P}_v\Delta t = \mathbf{I}\Delta t$$

**속도-각도 블록** $\boldsymbol{\Phi}_{v\theta}$ — 여기서부터 기교가 필요하다. 급수를 쓰면

$$\boldsymbol{\Phi}_{v\theta} = \mathbf{V}_\theta\Delta t + \tfrac{1}{2}\mathbf{V}_\theta\boldsymbol{\Theta}_\theta\Delta t^2 + \tfrac{1}{3!}\mathbf{V}_\theta\boldsymbol{\Theta}_\theta^2\Delta t^3 + \cdots = \mathbf{V}_\theta\,\boldsymbol{\Sigma}_1$$

$$\boldsymbol{\Sigma}_1 = \mathbf{I}\Delta t + \tfrac{1}{2}\boldsymbol{\Theta}_\theta\Delta t^2 + \tfrac{1}{3!}\boldsymbol{\Theta}_\theta^2\Delta t^3 + \cdots$$

> [!note] $\boldsymbol{\Sigma}_1$ 의 아래첨자 "1"이 뜻하는 것
> 이 급수는 $\boldsymbol{\Phi}_{\theta\theta}$ 의 급수와 닮았지만 **두 가지가 어긋난다.**
> 1. **각 항에서 $\boldsymbol{\Theta}_\theta$ 의 거듭제곱이 하나씩 모자란다.**
> 2. **급수 앞쪽의 항 하나가 빠져 있다.**
>
> 아래첨자 "1"이 바로 "하나씩 모자라다"는 뜻이다.

첫 번째 문제는 $[\mathbf{u}]_\times^3 = -[\mathbf{u}]_\times$ 성질([[Chapter 02 - 회전과 상호관계|2장]] 3.3절)에서 나오는 항등식으로 해결한다.

$$\boldsymbol{\Theta}_\theta = \frac{\boldsymbol{\Theta}_\theta^3}{\|\boldsymbol{\omega}\|^2} = \frac{-\boldsymbol{\Theta}_\theta^3}{\|\boldsymbol{\omega}\|^2}$$

**이 식으로 $\boldsymbol{\Theta}_\theta$ 의 지수를 2씩 올릴 수 있다.** 두 번째 문제는 **빠진 항을 더했다 빼서** 완전한 급수로 만든 뒤 닫힌 형태로 치환하면 된다. 결과는

$$\boldsymbol{\Sigma}_1 = \mathbf{I}\Delta t - \frac{\boldsymbol{\Theta}_\theta}{\|\boldsymbol{\omega}\|^2}\left(\mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\} - \mathbf{I} - \boldsymbol{\Theta}_\theta\Delta t\right)$$

따라서 최종적으로

$$\boldsymbol{\Phi}_{v\theta} = \begin{cases}
-\mathbf{R}[\mathbf{a}]_\times\Delta t & \boldsymbol{\omega}=0 \\[6pt]
-\mathbf{R}[\mathbf{a}]_\times\left(\mathbf{I}\Delta t + \dfrac{[\boldsymbol{\omega}]_\times}{\|\boldsymbol{\omega}\|^2}\left(\mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}-\mathbf{I}+[\boldsymbol{\omega}]_\times\Delta t\right)\right) & \boldsymbol{\omega}\neq0
\end{cases}$$

**위치-각도 블록** $\boldsymbol{\Phi}_{p\theta}$ — 같은 요령을 한 번 더 쓴다. 이번에는 $\boldsymbol{\Theta}_\theta$ 가 **두 개씩** 모자라므로 $\boldsymbol{\Sigma}_2$ 를 쓴다.

$$\boldsymbol{\Phi}_{p\theta} = \mathbf{P}_v\mathbf{V}_\theta\,\boldsymbol{\Sigma}_2, \qquad \boldsymbol{\Sigma}_2 = \tfrac{1}{2}\mathbf{I}\Delta t^2 + \tfrac{1}{3!}\boldsymbol{\Theta}_\theta\Delta t^3 + \tfrac{1}{4!}\boldsymbol{\Theta}_\theta^2\Delta t^4 + \cdots$$

닫힌 형태로 바꾸면

$$\boldsymbol{\Sigma}_2 = \tfrac{1}{2}\mathbf{I}\Delta t^2 - \frac{1}{\|\boldsymbol{\omega}\|^2}\left(\mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\} - \mathbf{I} - \boldsymbol{\Theta}_\theta\Delta t - \tfrac{1}{2}\boldsymbol{\Theta}_\theta^2\Delta t^2\right)$$

$$\boldsymbol{\Phi}_{p\theta} = \begin{cases}
-\mathbf{R}[\mathbf{a}]_\times\dfrac{\Delta t^2}{2} & \boldsymbol{\omega}=0 \\[6pt]
-\mathbf{R}[\mathbf{a}]_\times\,\boldsymbol{\Sigma}_2 & \boldsymbol{\omega}\neq0
\end{cases}$$

> [!tip] 이 절에서 배울 기법
> 개별 공식을 외울 필요는 없다. **요령 세 가지**가 핵심이다.
> 1. $\mathbf{A}^k$ 의 **패턴을 찾아** 블록별로 분리한다.
> 2. 지수가 모자란 급수는 $[\mathbf{u}]_\times^3=-[\mathbf{u}]_\times$ **항등식으로 지수를 보충**한다.
> 3. 앞쪽 항이 빠진 급수는 **더했다 빼서** 완전한 급수로 만든 뒤 닫힌 형태로 치환한다.
>
> 그리고 실무적 결론은 명확하다. **$\boldsymbol{\omega}=0$ 분기가 반드시 필요하다.** $\|\boldsymbol{\omega}\|^2$ 로 나누기 때문이다. 정지 상태에서 NaN이 나는 버그의 전형적 원인이다.

## B.3 완전한 IMU 예제

논문은 이어서 **바이어스와 중력까지 포함한 완전한 IMU 시스템**(B.3)에 대해 같은 방식으로 폐형식 전이행렬을 유도한다. 상태가 $18$ 차원이라 블록이 훨씬 많아지지만, **위에서 본 세 가지 요령을 그대로 반복 적용**하는 것이 전부다.

---

# 부록 C · 절단급수를 이용한 근사

## C.0 어디까지 정밀해야 하는가

> [!note] 논문의 현실적인 문제 제기
> 앞 절에서 폐형식 표현을 얻었다. 폐형식은 언제나 흥미롭지만, **고차 오차가 실제 알고리즘 성능에 어느 정도나 영향을 주는지는 불분명하다.**
>
> 특히 **시각-관성 융합이나 GPS-관성 융합처럼 IMU 적분 오차가 비교적 높은 주기로 관측되고 보상되는 시스템**에서는 더욱 그렇다. 어차피 곧 보정될 오차를 정밀하게 계산하는 데 계산량을 쓸 이유가 없다는 것이다.

그래서 이 절은 전이행렬을 **테일러 급수에서 유의미한 항까지만 자르는** 방법을 다룬다. 자르는 방식은 **시스템 단위**와 **블록 단위** 두 가지가 있다.

## C.1 시스템 단위 절단

### C.1.1 1차 절단 = 유한차분법 = 오일러 방법

$\dot{\mathbf{x}} = f(t,\mathbf{x})$ 형태의 시스템에 대해 미분의 유한차분 정의를 쓰면

$$\dot{\mathbf{x}} = \lim_{\Delta t\to0}\frac{\mathbf{x}(t+\Delta t)-\mathbf{x}(t)}{\Delta t} \approx \frac{\mathbf{x}_{n+1}-\mathbf{x}_n}{\Delta t}$$

즉시 다음을 얻는다.

$$\mathbf{x}_{n+1} \approx \mathbf{x}_n + \Delta t\,f(t_n,\mathbf{x}_n)$$

이것이 정확히 **오일러 방법**이다. $f()$ 를 구간 시작점에서 선형화하면

$$\mathbf{x}_{n+1} \approx \mathbf{x}_n + \Delta t\,\mathbf{A}\,\mathbf{x}_n$$

이는 지수 해를 1차 항에서 자른 것과 **완전히 동일하다.**

$$\mathbf{x}_{n+1} = e^{\mathbf{A}\Delta t}\mathbf{x}_n \approx (\mathbf{I}+\Delta t\,\mathbf{A})\mathbf{x}_n$$

> [!important] 세 가지가 전부 같은 것이다
> **오일러 방법(부록 A.1) = 유한차분법 = 1차 시스템 단위 테일러 절단.**
> 따라서 근사 전이행렬은
> $$\boldsymbol{\Phi} \approx \mathbf{I} + \Delta t\,\mathbf{A}$$

[[Chapter 05 - IMU 기반 오차상태 운동학|5장]] B.2절의 단순화된 IMU 예제에 적용하면

$$\boldsymbol{\Phi} \approx \begin{bmatrix}\mathbf{I} & \mathbf{I}\Delta t & 0 \\ 0 & \mathbf{I} & -\mathbf{R}[\mathbf{a}]_\times\Delta t \\ 0 & 0 & \mathbf{I}-[\boldsymbol{\omega}]_\times\Delta t\end{bmatrix}$$

그런데 우리는 부록 B.1에서 **회전 항에는 간결한 폐형식 해 $\boldsymbol{\Phi}_\theta = \mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}$ 가 있다**는 것을 이미 안다. 그러니 그 부분만 정확한 값으로 바꿔 쓰는 편이 낫다.

$$\boldsymbol{\Phi} \approx \begin{bmatrix}\mathbf{I} & \mathbf{I}\Delta t & 0 \\ 0 & \mathbf{I} & -\mathbf{R}[\mathbf{a}]_\times\Delta t \\ 0 & 0 & \mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}\end{bmatrix}$$

> [!tip] 이것이 5장에서 쓴 바로 그 행렬이다
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 4.3절의 $\mathbf{F}_x$ 가 정확히 이 구조다. **대부분 1차 근사이되, 회전 블록만 폐형식**이다. 가성비가 가장 좋은 조합이라서 논문이 그것을 기본으로 삼았다.

### C.1.2 N차 절단

더 높은 차수로 자르면 정밀도가 올라간다. 특히 흥미로운 절단 차수는 **결과의 희소성(sparsity)을 최대한 활용하는 차수**, 즉 **그 이상 가도 새로운 0이 아닌 항이 생기지 않는 차수**다.

단순화된 IMU 예제에서 그 차수는 **2**이며, 결과는

$$\boldsymbol{\Phi} \approx \mathbf{I} + \mathbf{A}\Delta t + \tfrac{1}{2}\mathbf{A}^2\Delta t^2 = \begin{bmatrix}
\mathbf{I} & \mathbf{I}\Delta t & -\tfrac{1}{2}\mathbf{R}[\mathbf{a}]_\times\Delta t^2 \\
0 & \mathbf{I} & -\mathbf{R}[\mathbf{a}]_\times(\mathbf{I}-\tfrac{1}{2}[\boldsymbol{\omega}]_\times\Delta t)\Delta t \\
0 & 0 & \mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}
\end{bmatrix}$$

> [!note] 2차로 가면 무엇이 좋아지나
> 1차 근사에서 **0이던 자리**(위치 행의 자세 열)에 $-\tfrac{1}{2}\mathbf{R}[\mathbf{a}]_\times\Delta t^2$ 가 생겼다. 자세 오차가 위치 오차로 **직접** 전파되는 경로가 추가된 것이다. 물리적으로는 "자세가 틀어진 상태로 가속도를 두 번 적분하면 위치가 어긋난다"는 효과다. $\Delta t$ 가 크거나 가속도가 클 때 의미가 있다.

## C.2 블록 단위 절단

시스템 전체를 같은 차수로 자르는 대신, **블록마다 다른 차수**를 적용하는 방법이다. 어떤 블록은 1차로 충분하고 어떤 블록은 2차가 필요하다면, 필요한 곳에만 계산을 쓰는 것이 효율적이다. [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 4.2절의 오차 상태 이산 갱신식이 이 방식을 따랐다.

---

# 부록 D · Runge-Kutta로 전이행렬 구하기

전이행렬 $\boldsymbol{\Phi} = e^{\mathbf{A}\Delta t}$ 를 해석적으로 구하는 대신, **RK 적분기로 수치적으로 구하는** 방법이다.

핵심 아이디어는 이렇다. 전이행렬은 다음 행렬 미분방정식의 해다.

$$\dot{\boldsymbol{\Phi}}(t) = \mathbf{A}(t)\,\boldsymbol{\Phi}(t), \qquad \boldsymbol{\Phi}(t_n) = \mathbf{I}$$

따라서 부록 A의 RK 방법들을 **이 행렬 미분방정식에 그대로 적용**하면 된다. 초기값을 단위행렬로 놓고 $\Delta t$ 만큼 적분하면 $\boldsymbol{\Phi}$ 가 나온다.

> [!tip] 언제 유용한가
> $\mathbf{A}$ 가 구간 내에서 **시간에 따라 변할 때** 특히 유용하다. 폐형식 해는 $\mathbf{A}$ 가 상수라는 가정 위에 있기 때문이다. IMU 측정값이 구간 내에서 크게 변하는 고기동(high-dynamics) 상황이라면 고려할 만하다.

논문은 D.1절에서 **오차 상태 예제**에 이를 적용한 구체적 계산을 보여 준다.

---

# 부록 E · 랜덤 노이즈와 섭동의 적분

> [!important] 실무에서 가장 중요한 부록
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]] 4.2절에서 노이즈 공분산을
> $$\mathbf{V}_i = \sigma_{\tilde{a}_n}^2\Delta t^2\mathbf{I}, \qquad \mathbf{A}_i = \sigma_{a_w}^2\Delta t\,\mathbf{I}$$
> 로 썼다. **왜 하나는 $\Delta t^2$ 이고 다른 하나는 $\Delta t$ 인가?** 그 답이 여기 있다. 이 차이를 모르고 구현하면 필터 튜닝이 영원히 안 맞는다.

## E.0 문제 설정

랜덤 변수 자체는 적분할 수 없지만, **불확실성 전파를 위해 그 분산과 공분산은 적분할 수 있다.** 연속적인 성질을 가진(그리고 연속시간으로 기술된) 시스템을 이산적으로 추정할 때, 추정기의 공분산 행렬을 세우려면 이것이 필요하다.

연속시간 동역학 시스템을 생각하자.

$$\dot{\mathbf{x}} = f(\mathbf{x},\mathbf{u},\mathbf{w})$$

여기서 $\mathbf{x}$ 는 상태 벡터, $\mathbf{u}$ 는 **노이즈 $\tilde{\mathbf{u}}$ 를 포함한 제어 신호** 벡터(측정값은 $\mathbf{u}_m = \mathbf{u}+\tilde{\mathbf{u}}$), $\mathbf{w}$ 는 **랜덤 섭동** 벡터다. 둘 다 백색 가우시안 과정으로 가정한다.

$$\tilde{\mathbf{u}} \sim \mathcal{N}\{0,\mathbf{U}^c\}, \qquad \mathbf{w}^c \sim \mathcal{N}\{0,\mathbf{W}^c\}$$

윗첨자 $^c$ 는 **연속시간** 불확실성 명세를 뜻한다.

## E.1 결정적 차이 — 샘플링되느냐 아니냐

> [!important] 이 부록 전체의 핵심
> 제어 신호의 노이즈 $\tilde{\mathbf{u}}$ 와 랜덤 섭동 $\mathbf{w}$ 사이에는 **본질적인 차이**가 있다.
>
> **제어 신호는 샘플링된다.** 이산화할 때 시각 $n\Delta t$ 에서 샘플을 얻고, $\mathbf{u}_{m,n} \triangleq \mathbf{u}_m(n\Delta t)$ 이다. 측정된 부분은 적분 구간 내내 상수로 간주되므로, **샘플링 시점의 노이즈 레벨도 구간 내내 상수로 유지된다.**
> $$\tilde{\mathbf{u}}(t) = \tilde{\mathbf{u}}(n\Delta t) = \tilde{\mathbf{u}}_n, \qquad n\Delta t < t < (n+1)\Delta t$$
>
> **섭동은 절대 샘플링되지 않는다.** $\mathbf{w}$ 는 구간 내내 계속 변하는 진짜 연속 확률과정이다.
>
> 결과적으로 **두 확률과정의 $\Delta t$ 적분은 서로 다르게 이루어진다.**

## E.2 세 항의 적분

연속시간 오차상태 동역학을 선형화하면

$$\dot{\delta\mathbf{x}} = \mathbf{A}\,\delta\mathbf{x} + \mathbf{B}\,\tilde{\mathbf{u}} + \mathbf{C}\,\mathbf{w}$$

$$\mathbf{A} \triangleq \left.\frac{\partial f}{\partial\delta\mathbf{x}}\right|_{\mathbf{x},\mathbf{u}_m}, \quad \mathbf{B} \triangleq \left.\frac{\partial f}{\partial\tilde{\mathbf{u}}}\right|_{\mathbf{x},\mathbf{u}_m}, \quad \mathbf{C} \triangleq \left.\frac{\partial f}{\partial\mathbf{w}}\right|_{\mathbf{x},\mathbf{u}_m}$$

샘플링 주기 $\Delta t$ 에 대해 적분하면 **성질이 완전히 다른 세 항**이 나온다.

$$\delta\mathbf{x}_{n+1} = \delta\mathbf{x}_n + \underbrace{\int \mathbf{A}\,\delta\mathbf{x}(\tau)d\tau}_{\text{1. 동역학}} + \underbrace{\int \mathbf{B}\,\tilde{\mathbf{u}}(\tau)d\tau}_{\text{2. 측정 노이즈}} + \underbrace{\int \mathbf{C}\,\mathbf{w}^c(\tau)d\tau}_{\text{3. 섭동}}$$

### 항 1 — 동역학 부분: 전이행렬

부록 B에서 본 대로 전이행렬이 된다.

$$\delta\mathbf{x}_n + \int_{n\Delta t}^{(n+1)\Delta t}\mathbf{A}\,\delta\mathbf{x}(\tau)d\tau = \boldsymbol{\Phi}\,\delta\mathbf{x}_n$$

$\boldsymbol{\Phi} = e^{\mathbf{A}\Delta t}$ 는 폐형식으로 구하거나 여러 정밀도로 근사할 수 있다.

### 항 2 — 측정 노이즈: 결정적으로 적분된다

E.1의 성질에서 $\tilde{\mathbf{u}}$ 가 구간 내 상수이므로

$$\int_{n\Delta t}^{(n+1)\Delta t}\mathbf{B}\,\tilde{\mathbf{u}}(\tau)d\tau = \mathbf{B}\,\Delta t\,\tilde{\mathbf{u}}_n$$

> [!important] $\Delta t$ 가 **1제곱**으로 붙는다
> 측정 노이즈는 일단 샘플링되고 나면 **구간 내 거동이 알려져 있으므로(상수) 결정적인 방식으로 적분된다.** 상수를 $\Delta t$ 동안 적분했으니 $\Delta t$ 배가 되는 것이다.

### 항 3 — 섭동: 확률적으로 적분된다

확률론에서 알려진 결과다. **연속 백색 가우시안 노이즈를 $\Delta t$ 동안 적분하면 이산 백색 가우시안 임펄스**가 나온다.

$$\mathbf{w}_n \triangleq \int_{n\Delta t}^{(n+1)\Delta t}\mathbf{w}(\tau)d\tau, \qquad \mathbf{w}_n\sim\mathcal{N}\{0,\mathbf{W}\}, \qquad \boxed{\mathbf{W} = \mathbf{W}^c\Delta t}$$

> [!important] $\Delta t$ 가 **1제곱**으로 붙는다 (공분산에서)
> 위의 측정 노이즈와 달리, **섭동은 적분 구간 내부에서 결정적 거동을 갖지 않으므로 확률적으로 적분해야 한다.**
>
> 직관적으로는 이렇다. 백색 잡음을 적분하면 **랜덤 워크**가 되고, 랜덤 워크의 분산은 시간에 **비례**한다. (표준편차는 $\sqrt{\Delta t}$ 에 비례한다.) 그래서 공분산에 $\Delta t$ 가 1제곱으로 붙는다.

## E.3 정리 — Table 5

논문의 Table 5다. 적분이 시스템 행렬과 공분산 행렬에 미치는 효과를 한눈에 보여 준다.

| 설명 | 연속시간 $t$ | 이산시간 $n\Delta t$ |
|---|---|---|
| 상태 | $\dot{\mathbf{x}} = f^c(\mathbf{x},\mathbf{u},\mathbf{w})$ | $\mathbf{x}_{n+1} = f(\mathbf{x}_n,\mathbf{u}_n,\mathbf{w}_n)$ |
| 오차상태 | $\dot{\delta\mathbf{x}} = \mathbf{A}\delta\mathbf{x}+\mathbf{B}\tilde{\mathbf{u}}+\mathbf{C}\mathbf{w}$ | $\delta\mathbf{x}_{n+1} = \mathbf{F}_x\delta\mathbf{x}_n+\mathbf{F}_u\tilde{\mathbf{u}}_n+\mathbf{F}_w\mathbf{w}_n$ |
| 시스템 행렬 | $\mathbf{A}$ | $\mathbf{F}_x = \boldsymbol{\Phi} = e^{\mathbf{A}\Delta t}$ |
| 제어 행렬 | $\mathbf{B}$ | $\mathbf{F}_u = \mathbf{B}\Delta t$ |
| 섭동 행렬 | $\mathbf{C}$ | $\mathbf{F}_w = \mathbf{C}$ |
| 제어 공분산 | $\mathbf{U}^c$ | $\mathbf{U} = \mathbf{U}^c$ |
| 섭동 공분산 | $\mathbf{W}^c$ | $\mathbf{W} = \mathbf{W}^c\Delta t$ |

따라서 이산시간 오차상태 동역학 시스템은

$$\boxed{\delta\mathbf{x}_{n+1} = \mathbf{F}_x\,\delta\mathbf{x}_n + \mathbf{F}_u\,\tilde{\mathbf{u}}_n + \mathbf{F}_w\,\mathbf{w}_n}$$

$$\mathbf{F}_x = \boldsymbol{\Phi} = e^{\mathbf{A}\Delta t}, \qquad \mathbf{F}_u = \mathbf{B}\Delta t, \qquad \mathbf{F}_w = \mathbf{C}$$

$$\tilde{\mathbf{u}}_n\sim\mathcal{N}\{0,\mathbf{U}\}, \qquad \mathbf{w}_n\sim\mathcal{N}\{0,\mathbf{W}\}$$

$$\mathbf{U} = \mathbf{U}^c, \qquad \mathbf{W} = \mathbf{W}^c\Delta t$$

## E.4 5장의 공분산 식이 이제 이해된다

> [!important] $\Delta t^2$ 와 $\Delta t$ 의 차이, 최종 정리
> [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]의 네 공분산을 다시 보자.
>
> | 항 | 공식 | 정체 | $\Delta t$ 차수 |
> |---|---|---|---|
> | $\mathbf{V}_i$ | $\sigma_{\tilde{a}_n}^2\Delta t^2\mathbf{I}$ | 가속도계 **측정 노이즈** | $\Delta t^2$ |
> | $\boldsymbol{\Theta}_i$ | $\sigma_{\tilde{\omega}_n}^2\Delta t^2\mathbf{I}$ | 자이로 **측정 노이즈** | $\Delta t^2$ |
> | $\mathbf{A}_i$ | $\sigma_{a_w}^2\Delta t\,\mathbf{I}$ | 가속도계 바이어스 **랜덤 워크** | $\Delta t$ |
> | $\boldsymbol{\Omega}_i$ | $\sigma_{\omega_w}^2\Delta t\,\mathbf{I}$ | 자이로 바이어스 **랜덤 워크** | $\Delta t$ |
>
> **측정 노이즈($\tilde{\mathbf{u}}$ 계열)** — 항 2에 해당한다. $\mathbf{F}_u = \mathbf{B}\Delta t$ 이므로 공분산에는 $\mathbf{F}_u\mathbf{U}\mathbf{F}_u^\top$ 로 들어가 **$\Delta t$ 가 제곱**된다.
>
> **바이어스 랜덤 워크($\mathbf{w}$ 계열)** — 항 3에 해당한다. $\mathbf{W} = \mathbf{W}^c\Delta t$ 이고 $\mathbf{F}_w = \mathbf{C}$ 이므로 **$\Delta t$ 가 1제곱**만 붙는다.
>
> 즉 **"샘플링되는 노이즈는 제곱, 샘플링되지 않는 섭동은 1제곱"** 이다.

> [!warning] 구현 시 흔한 실수
> 이 차이를 모르고 네 항 모두에 같은 차수를 적용하면, IMU 주기 $\Delta t$ 를 바꿀 때마다 필터 성능이 달라진다. 200Hz에서 튜닝한 값이 100Hz에서 안 맞는다면 이 문제를 의심해 보자.
>
> 또 하나. 데이터시트의 단위를 확인해야 한다. 잡음 밀도는 보통 $\mu g/\sqrt{Hz}$ 나 $^\circ/s/\sqrt{Hz}$ 로, 랜덤 워크는 $^\circ/\sqrt{h}$ 등으로 주어진다. 위 식의 $\sigma$ 단위($m/s^2$, $rad/s$, $m/(s^2\sqrt{s})$, $rad/(s\sqrt{s})$)로 변환해서 넣어야 한다.

---

## 전체 정리

> [!abstract] 부록 A~E 요약
> | 부록 | 내용 | 언제 필요한가 |
> |---|---|---|
> | **A** | Runge-Kutta 적분(오일러·중점·RK4) | 공칭 상태 적분 정밀도를 올릴 때 |
> | **B** | 폐형식 전이행렬. 각오차 블록은 $\mathbf{R}^\top\{\boldsymbol{\omega}\Delta t\}$ 가 **정확해** | 정밀한 $\mathbf{F}_x$ 가 필요할 때 |
> | **C** | 절단급수 근사. 1차 = 오일러, 2차면 희소성 포화 | $\Delta t$ 가 크거나 고기동일 때 |
> | **D** | RK로 전이행렬 수치 계산 | $\mathbf{A}$ 가 구간 내 변할 때 |
> | **E** | **노이즈 공분산의 $\Delta t$ 차수** | **항상. 처음 구현할 때 필독** |

> [!tip] 실전 권장 조합
> 1. 공칭 상태: **중점 방법**(부록 A.2) 또는 [[Chapter 04 - 섭동 미분 적분|4장]] 6.2절의 1차 적분
> 2. 전이행렬: **1차 절단 + 회전 블록만 폐형식**(부록 C.1.1의 마지막 식) — [[Chapter 05 - IMU 기반 오차상태 운동학|5장]]이 채택한 형태
> 3. 노이즈: **부록 E.4 표대로** 차수를 정확히 맞출 것

---

## 관련 노트

- [[Chapter 04 - 섭동 미분 적분]] — 6절의 적분법과 연결
- [[Chapter 05 - IMU 기반 오차상태 운동학]] — $\mathbf{F}_x$, $\mathbf{Q}_i$ 의 출처
- [[Chapter 07 - 전역 각오차를 쓰는 ESKF]] — 전역 버전의 $\mathbf{F}_x$
- [[자코비안과 공분산 전파]] — 공분산 전파의 의미
- [[IMU 센서 모델과 바이어스]] — 데이터시트에서 $\sigma$ 읽는 법
