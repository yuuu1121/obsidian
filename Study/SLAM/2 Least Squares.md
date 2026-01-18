# 2. Least Squares

# 1. Least Squares란?

---

Least Squares은 우리가 배우는 SLAM system인 ‘Graph-based SLAM system’의 backend에서 **최적화수행**에 사용하는 도구이다.

> **<Least Squares>**
**Overdetermined System(구해야 할 parameter보다 더 많은 Observations이 존재)**에서, Observation들에 noise가 존재하는 경우에 실제값와 예측값의 **Error가 최소화되도록 하는 parameter 값을 구하는 방법**이다. 그 error는 보통 **관찰값과 예측값의 차이(residual)의 제곱**으로 표현한다.
> 

![Untitled](2%20Least%20Squares/Untitled.png)

Least Squares는 선형화를 가정하여 error의 최소화를 구하는 방법이다. 만약 **Non-linear**한 모델일 경우, Gauss-Newton Method 등의 방법을 이용할 수 있다.

## 1-1. Our Problem

---

![Untitled](2%20Least%20Squares/Untitled%201.png)

이 문제는 모델 파라미터 추정 문제가 아닌, state x 추정 문제이다.

- $x$ : state vector (unknown)
- $z_i$ : state x 의 관측값 (known, noisy)
- $\hat{z_i}=f_i(x)$ : 예측값 (known & fixed)
    
    ⇒ error vector는 오직 $x$에 대한 함수
    

관측을 한 번 할때마다 observation model  $f(x)$가 하나씩 결정되고, 이때 i번째 관측이 $f_i(x)$이다.

즉, $e_i = z_i - \hat{z_i}$ 이고 global error=$\sum_ie_i$가 최소가 되게 하는 x를 찾아라.

## 1-2. Error Function 구하기

---

error function 은 다음과 같다. 이때 error function $e_i$는 **Vector**이다.

$$
e_i = z_i - \hat{z_i}=z_i-f_i(x)
$$

squared error term으로 계산해야 하는데 $e_i$가 Vector이므로 error function(sqaure form)을 구하면 다음과 같은 형태가 된다. (강의자료가 헷갈려서 이 페이지에서는 e 대신 E 사용)

$$
E_i(x) = e_i(x)^T\Omega_ie_i(x)
$$

이때 $E_i(x)$는 **Scalar** 값으로 i번째 error function의 값이다.

$\Omega_i$는 information matrix이다. $e_i(x)^Te_i(x)$ 는 스칼라이므로 중간에 삽입한다.

<aside>
💡 **<Information Matrix $\Omega$>**

![Untitled](2%20Least%20Squares/Untitled%202.png)

우리는 uncertainty를 $\delta^2$로 나타낸다. $v_i$는 i번째 관측의 noise이고, $v$의 covariance를 나타내면 $\delta^2$이다. $\delta^2$이 클수록 low confidence, 즉 uncertainty가 높다는 뜻이 된다. 불확실한 센서의 값일수록 관측값이 평균으로부터 넓게 분포되어 있어 불확실성이 높다. 센서 관측 확률 분포가 아래와 같다면, 센서 1이 가장 정밀도 높은 센서이다.

$\delta_1 < \delta_2 < \delta_3$ 이므로 $\frac{1}{\delta_1^2} \gg \frac{1}{\delta_2^2} \gg \frac{1}{\delta_3^2}$. 즉 sensor1의 영향 가장 많이 받는다.

![Untitled](2%20Least%20Squares/Untitled%203.png)

$$
E(x) = \frac{e^2_1}{\delta^2_1}+\cdots+\frac{e^2_k}{\delta^2_k}
$$

E(x)는 스칼라값이고, uncertainty가 높을수록 해당 센서가 영향을 적게 미치도록 weight를 주어야 하기 때문에 역수를 취해 가중치를 곱한다. 즉 **Information Matrix $\Omega$는 covariance matrix의 inverse matrix이다.**

$$
E_i(x) = e_i(x)^T\Omega_ie_i(x)=
\begin{bmatrix}
e_1 & \cdots  & e_k \\
\end{bmatrix}
\begin{bmatrix}
\frac{1}{\delta_1^2} & \cdots  & \frac{1}{\delta_1\delta_k} \\
\vdots & \ddots  & \vdots \\
\frac{1}{\delta_k\delta_1} & \cdots  & \frac{1}{\delta_k^2} \\
\end{bmatrix}
\begin{bmatrix}
e_1 \\ \vdots  \\ e_k \\
\end{bmatrix}
$$

Information matrix는 실제 전달하는 정보의 양이라고 표현 할 수도 있고, 센서 노이즈가 평균이 0이고 정규분포를 따르는 가우시안 확률로 error가 있다는 가정을 표현하기 위해 넣었다고도 할 수 있다.

---

Information mtx는 Heteroskedasticity (이분산성)이다. 즉, SLAM system에서 여러 개의 sensor를 사용하는데, sensor간에 영향을 안준다고 가정하고 각각 센서마다 서로 다른 독립적인 분산을 따른다는 의미이다.

Off-diagonal term은 센서와 센서 사이의 관계를 나타내준다. 센서끼리의 영향이 없다고 가정하면 모두 0으로 나타낼 수 있다.

![Untitled](2%20Least%20Squares/Untitled%204.png)

off-diagonal term 이 모두 0이면 서로 다른 센서끼리는 영향을 받지 않는 것을 볼 수 있다. $e_1, e_2, e_3$는 3개 센서의 각 error이다.

![Untitled](2%20Least%20Squares/Untitled%205.png)

</aside>

## 1-3.  **x*(error를 최소화 시키는 x 값) 찾기**

---

Error function을 이용해 우리가 구해야 할 것은 **$x^*$(error function를 최소화 시키는 $x$ 값)**이다.

![Untitled](2%20Least%20Squares/Untitled%206.png)

argmin을 구할 때는 수식적인 방법으로 Iterative하게 접근을 하여 구한다.

단, 이 과정으로 최적의 해를 찾을 때는 **중요한 가정 (Assumption)**이 존재한다.

- 초기에 setting한 값이 좋은 값이라는 가정
- Error function을 이용하여 반드시 최적의 해를 찾는 것은 아니므로, 이를 이용하면 Global minima를 구할 수 있다는 믿음
- (hopefully global) minima 주변에서 error function이 smooth 하다.

# 2. Gauss-Newton Method

---

Gauss-Newton Method는 Non-linear한 모델에서 최적의 Parameter를 구하는 방법 중 하나이다.

위 예제에서 Gauss-Newton Method의 전체적인 과정은 다음과 같다.

1. Taylor 급수와 전개를 활용하여 Non-linear한 식(current sol/initial guess 주변의 error term)을 Linear하게 만든다.
2. Squared Error이기 때문에 식을 정리하면 이차 식(Qudaratic Form)이 나오는데,
최솟값을 찾기 위해 편미분을 한다.
3. 편미분을 0으로 두고 linear system을 풀어 새로운 x값을 구한다.
4. 새로운 x값을 이용하여 초기값을 다시 구한다.
5. 최적의 해를 구할 때까지 반복한다.

## 2-1.  **Error Function 선형화**

---

테일러 전개로 선형화를 하기 위해, $e_i(x)=e_i(x+\Delta x)$로 두고 식을 쓴다. 이때 $x$는 상수로 취급하고 변화량($\Delta x$)만 변수로 취급한다.

![Untitled](2%20Least%20Squares/Untitled%207.png)

<aside>
💡 **<Taylor expansion>**

![Untitled](2%20Least%20Squares/Untitled%208.png)

</aside>

이를 풀어쓰면

![Untitled](2%20Least%20Squares/Untitled%209.png)

모든 i에 대해 Error를 구하고 그 합을 통해 Global Error $F(x)=\sum_ie_i(x)$를 구한다.

![Untitled](2%20Least%20Squares/Untitled%2010.png)

## 2-2.  **2차식 편미분**

---

global error term을 $\Delta x$에 대한 quadratic form(2차식)으로 쓰면

![Untitled](2%20Least%20Squares/Untitled%2011.png)

$F(x+\Delta x)$ 편미분하면

![Untitled](2%20Least%20Squares/Untitled%2012.png)

<aside>
💡 **<행렬의 편미분>**

![Untitled](2%20Least%20Squares/Untitled%2013.png)

</aside>

## 2-3.  **편미분 식을 활용한 새로운 x 찾기**

---

미분 값이 0이 되는 x 값을 찾으면 된다.

![Untitled](2%20Least%20Squares/Untitled%2014.png)

## 2-4.  **새로운  x를 이용한 Initial State Update**

---

반복 하기 전에 새로 찾은 값인 $\Delta x$를 이용하여 새로운 Inital State 값을 업데이트 한다.

$$
x = x+\Delta x^*
$$

구한 $x$ 값을 이용하여 2-1 ~ 2-4 과정을 반복해 최적의 State를 찾는다.

## 2-5.  **Linear System 효과적으로 풀기**

---

2-3 과정에서 Linear system $H\Delta x = -b$을 풀 때, $H$의 역행렬을 구해서 $\Delta x^*$를 구할 수 있다. 하지만 $H$가 invertible하지 않다면 Pseudo-inverse를 이용한다.

![Untitled](2%20Least%20Squares/Untitled%2015.png)

하지만 계산량이 비효율적이다. Pseudo-inverse를 대신할 수 있는 역행렬을 구하는 방법은 다양하다.

- Cholesky factorization (matrix size가 작을 때)
- QR decomposition
- Iterative methods such as conjugate gradients (matrix size가 클 때)

이 중에서, **Cholesky factorization**을 이용한 방법은 다음과 같다. 행렬 $A$에 대해 $Ax=b$를 구할 때, $A=LL^T$로 분해하여 구하면 더 쉽게 답을 찾을 수 있다. 여기서 $L$은 lower triangular mtx이고 $L^T$ upper triangular mtx이다.

계산 복잡도가 ~$O(\frac{1}{2}n^3)$ 으로 계산 복잡도가 ~$O(n^3)$ 인 LU/QR decomposition보다 낮다는 장점이 있지만, Cholesky factorization을 사용하려면 사용하는 mtx가 **positive-definite($x^THx>0, x \neq 0$)**여야 한다.

![Untitled](2%20Least%20Squares/Untitled%2016.png)

<aside>
💡 **H는 positive definite이다.

<Proof>**

$$
H=J^T\Omega J=J^T\Omega^{\frac{1}{2}} \Omega^{\frac{1}{2}} J=
J^T(\Omega^{\frac{1}{2}})^T \Omega^{\frac{1}{2}} J=
(\Omega^{\frac{1}{2}}J)^T \Omega^{\frac{1}{2}} J=B^TB>0
$$

</aside>

## 2-6.  ****Gauss-Newton 요약

---

![Untitled](2%20Least%20Squares/Untitled%2017.png)

수식으로 표현하면 아래 단계들을 반복한다고 볼 수 있다.

![Untitled](2%20Least%20Squares/Untitled%2018.png)

# 3. Least Squares vs Probabilistic State Estimation

---

Least Squares를 활용하여 해를 구하는 방법과 Probabilistic State Estimation을 활용하여 해를 구하는 방법은 모두 같은 해를 구하는 방법이다.

(Independent 가우시안 분포의 Log Likelihood 최대화) = (Squared Error 최소화)이기 때문이다.

![Untitled](2%20Least%20Squares/Untitled%2019.png)

조금 더 자세하게 살펴보면 다음과 같다.

State Estimation을 할 때, Bayes Rule을 적용하고 Markov assumption을 따른다고 가정한다.
Product term은 비선호되므로 여러 term으로 나누기 위해 구한 식에 log를 취한다. 이 때 확률 값은 모두 가우시안 분포를 가정한다면, Maximum likelihood를 구하는 것과 Squared Error를 Minimize 하는 방법은 결국 같다.

![Untitled](2%20Least%20Squares/Untitled%2020.png)

# 4. Example

---

![Untitled](2%20Least%20Squares/Untitled%2021.png)

# 5. Question

---

![Untitled](2%20Least%20Squares/Untitled%2022.png)

# 참고 자료

---

Cyrill 교수님 강의

SLAM DUNK Season2 강의

[https://taeyoung96.github.io/slam/SLAM_02/](https://taeyoung96.github.io/slam/SLAM_02/)

[다크 프로그래머 :: 최소자승법 이해와 다양한 활용예 (Least Square Method) (tistory.com)](https://darkpgmr.tistory.com/56)

참고(공분산 직관) : [https://blog.naver.com/sw4r/221025662499](https://blog.naver.com/sw4r/221025662499)