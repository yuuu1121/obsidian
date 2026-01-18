# 7. Kalman Filter & EKF

# 1. Kalman Filter

---

probabilistic state estimation technique으로, Dynamic system의 state를 추정한다.

칼만 필터는 Bayes Filter의 한 종류로 아래 가정을 만족하는 경우 사용할 수 있다.

- **모든 분포가 가우시안 확률 분포이다.**

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled.png)

- **모델이 Linear system이다. (가우시안 확률 분포를 유지하기 위해)**

**Kalman Filter의 특징은 아래와 같다.**

- Bayes Filter와 같이 Recursive한 Filter이다.
    - Step1. Prediction Step : 이전 state를 이용해 현재 state 예측 (control 사용)
    - Step2. Correction Step : 센서 데이터 사용해 보정 (observation 사용)
- Kalman Filter는 optimal MMSE(Minimum Mean Square Error) filter이다.
- system eqaution은 linear 하다.
- uncertatinty(initial state error, system으로 들어가는 noise)가 Gaussian, zero-mean, white, and uncorrelated 하다.

칼만 필터는 trajectory estimation 분야에서 제안된 알고리즘이다. 이를 확장해서 현재는 Control, navigation 등등 다양한 분야에서 칼만 필터가 쓰이고 있다.

## 예제 1

예를 들어 칼만 필터를 이해해보자. 위의 그림은 position을 나타낸 것이고 원의 크기는 uncertainty를 나타낸다. 첫번째 아래 그림처럼 검은색 점에 배의 현재 위치가 있고, 다음에 어디로 가야할지 예측하는 문제가 있다고 가정하자. Prediction을 통해서 검은색 (X) 표시가 되어있는 곳으로 갈 것이라 예측했다. 

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%201.png)

등대를 Observation 하여 세번째 그림의 초록색 (X) 표시가 내가 있는 위치라고 알 수 있다.

칼만필터 알고리즘을 활용해서 초록색 (X) 표시와 검은색 (X) 표시의 Weighted sum 계산을 통해 위치를 빨간색 (X) 표시로 나타낼 수 있다.

## 예제 2

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%202.png)

Correction step에서 Prediction 보다 Measurement 값에 가깝게 업데이트 되었다. 이는 확률적으로 보았을 때 measurement 값의 정확도가 높기 때문에(분산이 낮다) measurement에 wieght를 주어서 계산한 결과이다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%203.png)

다음 time step에서도 Recursive하게 진행한다.

# 2. Kalman Filter 증명

---

<aside>
💡

**<Marginalization & Conditioning>**
Marginalization을 했을 때도, Contditional probability를 따졌을 때도 모두 가우시안 확률 분포를 따르고 있다는 것을 명심하자.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%204.png)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%205.png)

- **Marginal probability** : 두 개 이상의 확률로 결합된 결합확률에서 하나의 확률만 선택하여 나타낸 확률
    
    ![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%206.png)
    
- **Conditional probability** : 특정 선행사건이 일어난 전제 하에서 어떤 사건이 일어날 확률
    
    ![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%207.png)
    
    - 증명
    
    [2-4. Conditional Gaussian distribution](https://jgshin.tistory.com/16)
    
</aside>

Linear model이란 Linear한 함수를 활용해서 표현이 가능한 모델이다. **Input이 가우시안 분포를 가진다면, Linear model의 Output도 가우시안 분포를 가지게 된다.** Non-Linear model에서는 input이 가우시안이어도 output이 가우시안이 아닐 수 있다. 칼만필터는 가우시안이라는 조건 아래에서 진행되기 때문에 가우시안이 아니면 칼만 필터의 적용이 불가능하다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%208.png)

칼만 필터를 방정식으로 풀어 쓰면 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%209.png)

각 mtx가 무엇을 나타내는지는 아래와 같다.

- $A_t$ : $(n \times n)$ describes how the state evolves from t-1 to t without controls or noise.
- $B_t$ : $(n \times l)$ describes how the control $u_t$ changes the state from t-1 to t.
- $C_t$ : $(k \times n)$ describes how to map the state $x_t$ to an observation $z_t$.
- $\epsilon_t$는 process noise, $\delta_t$는 measurement noise
    - Gaussian distribution, zero-mean, independent and normally distributed
    - $R_t$는 motion coavariance, $Q_t$는 measurement coavariance
- $n$은 state vector의 차원
- $l$은 control command $u$의 차원
- $k$는 observation의 차원

<aside>
💡 $A_t=I$ ?

Control command가 없으면 state가 변하지 않는 경우 $A_t=I$ (Identity mtx)로 두는 경우가 있다. (i.e. $u_t=0$ 이면 $x_t=x_{t-1}$) 그러나 자동차 페달을 밟지 않아도 constant 속도가 남아 자동차의 위치가 바뀌거나, 바람에 의해 움직일 수 있는 것처럼 $A_t \neq I$를 추천한다.

</aside>

<aside>
💡 **Linear model exmaple & Discretization**
칼만 필터는 continuous time, discrete time domain에 모두 존재한다. 현실에서 시스템이 continuous 하지만, 알고리즘 구현에서 discrete 하기 때문에 일반적으로 discrete time 칼만 필터를 사용한다. 아래 예시를 보면 Discretization을 해준다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2010.png)

</aside>

Gaussian Distribution의 공식은 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2011.png)

- $f(x)$ : probability density function
- $\sigma$ : standard deviation
- $\mu$ : mean

강의에서는 Gaussian Distribution을 풀어서 쓴다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2012.png)

칼만 필터를 방정식으로 만든 것을 대입하면 아래와 같은 두 식을 만들어낼 수 있다.

## Motion Model (under Gaussian noise)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2013.png)

- $R_t$ : motion covariance
- $R_t^{-1}$ : $(Cov)^{-1}$ = motion model의 uncertainty = motion에 추가해야 하는 noise

## Observation Model (under Gaussian noise)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2014.png)

- $Q_t$ :  measurement covariance

즉, 두 식 $p(x_t|u_t,x_{t-1}), p(z_t|x_t)$는 가우시안 정규 분포를 따른다.

그렇다면 $bel$ 함수는 가우시안 분포를 따를까? 가우시안 분포의 곱은 가우시안 분포이기 때문에, $\bar{bel}$ 이 가우시안이면 $bel$도 가우시안 이다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2015.png)

그렇다면 $\bar{bel}$은 가우시안 분포를 따를까? $\bar{bel}$함수의 정의도 가우시안 분포의 곱으로 정의하기 때문에 가우시안 분포를 따른다고 할 수 있다. 하지만 여기는 초기의  $bel$함수도 가우시안 분포를 따른다는 것을 보여주어야 $\bar{bel}$함수의 가우시안 분포를 따른다는 것이 성립이 된다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2016.png)

- **[$\bar{bel}$ 함수가 가우시안 분포 가진다는 것을 증명]**
    
    강의에서는 $\bar{bel}$ 함수가 가우시안 분포를 가지는 것에 대해 가우시안 분포의 곱과 Marginalization을 활용하여 풀어서 증명한다. 결과만 이야기하면 **모든 성분들은 가우시안 분포를 가진다!**
    
    ![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2017.png)
    
    ![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2018.png)
    
    ![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2019.png)
    

가우시안 분포를 표현할 때는 2가지의 parameter가 존재한다. 바로 평균(mean : $\mu$)과 공분산 행렬(covariance matrix : $\Sigma$)이다. 따라서 Bayes Filter에서 함수로 표현했던 부분을 단 두개의 매개변수 $\mu,\Sigma$로 나타낼 수 있다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2020.png)

# 3. Kalman Filter psudo code

---

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2021.png)

LINE 1 : Input

- $\mu_{t-1}$ : previous mean
- $\Sigma_{t-1}$ : previous covariance matrix (uncertainty of our previous belief)
- $u_t$ : control command
- $z_t$ : current observation

LINE 2-3 : Prediction Step

- LINE 2 : predicted mean $\bar{\mu}_t$ 계산
    - $A_t$ : 다른 Control 및 Noise를 제외한 $(t-1, t)$에서의 state 관계를 나타낸 mtx
    - $B_t$ : Control Input $u_t$와 state vector와의 관계 나타낸 mtx
- LINE 3 : predicted covariance(uncertainty) $\bar{\Sigma}_t$ 계산
    - $R_t$ : 모델에 대한 부정확성
        - $R_t$ 작다 = 모델이 정확하다 = $\bar{\Sigma}_t$ 크게 증가하지 않는다.
        - $R_t$ 크다 = 모델이 부정확하다 = $\bar{\Sigma}_t$ 크다.

LINE 4-6 : Correction Step

- LINE 4 : Weighting factor $K_k$ 계산
    - $K_k$ : Kalman Gain, 관측값과 예측 관측값의 error를 얼마나 업데이트할지 결정
        - $K_k$ 높다 = measurement 신뢰해서 더 많은 업데이트
        - $K_k$ 낮다 = measurement와 motion 예측의 차이가 있지만 작게 업데이트
        - 센서의 노이즈의 cov 값인 $Q_t$을 이용
    - $C_t$ : state vector와 observation 값의 관계를 설명하는 mtx
- LINE 5 : New mean $\mu _t$ update
- LINE 6 : Covariance matrix $\Sigma_t$ 계산

이해를 돕기 위해 **칼만 필터의 Timing Diagram, Flow Chart**를 나타내면 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2022.png)

# 4. Extended Kalman Filter(EKF)

---

Kalman Filter는 Model이 Linear하고, 모든 확률 분포가 가우시안 확률 분포를 가질 때 사용하는 Filter이다. 따라서 이 가정이 깨지게 된다면 Kalman Filter는 제대로 동작하지 않는다. 하지만 현실에서는 이러한 가정을 지키지 못하는 경우가 훨씬 많다. 예를 들어 2D plane에서의 Localization에서 state vector에 방향에 대한 값을 추가해 주는데, 이때 sine과 cosine 값이 들어가기 때문에 model이 Non-linear하게 된다. **EKF는 Kalman Filter를 확장시켜 Non-linear한 상황에서도 쓸 수 있는 Filter이다. 즉,** **Taylor 급수를 이용해 선형화 하여 Non-linear 한 경우에도 사용 가능한 Kalman Filter이다.**

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2023.png)

이러한 Non-linear한 function이 문제가 되는 이유는 가우시안 확률 분포를 가지는 Input을 model에 넣었을 때 가우시안 확률 분포를 가지지 않는 Ouput이 나오기 때문이다. 이러한 문제를 해결하기 위해 1차 테일러 급수식(first order taylor expansion)으로 **Local Linearization** 과정을 거친다.

<aside>
💡 **Remark. Jacobian**

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2024.png)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2025.png)

</aside>

EKF도 칼만 필터와 마찬가지로 Prediction step과 Correction step을 거친다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2026.png)

- $g(u_t,μ_{t-1}))$: 이전 상태 $μ_{t−1}$ 에서의 상태 전이 함수 값
- $\frac{\partial g}{\partial x_{t-1}} \Big|_{x_{t-1} = \mu_{t-1}}$: 상태 전이 함수의 자코비안 행렬 $G_t$
- $(x_{t-1} - \mu_{t-1})$: 평균으로부터 얼마나 떨어졌는지 나타내는 값
- $h(\barμ_t)$: 예측 상태에서의 관측값
- $\frac{\partial h}{\partial x_t} \Big|_{x_t = \bar{\mu}_t}$: 관측 모델의 자코비안 행렬 $H_t$
- $(x_t - \bar{\mu}_t)$: 예측 상태 $\barμ_t$ 로부터의 변화량

Local linearization 이므로 함수의 전체적인 Non-linearity는 해결할 수 없다. 발생할 수 있는 문제는 두 가지가 있다.

1. 1차 테일러 급수로 선형화한 값과 실제 Non-linear한 model의 차이
    - 크게 다르다면 문제가 될 수 있다.
2. Input의 uncertainty (= Covariance Matrix)
    - **Input의 uncertainty가 크면 approximation error도 커져 선형화 값이 부정확할 수 있다.** local 선형화를 했지만 non-linear 영역과도 크게 상관이 생긴다.
    - **Input의 uncertainty가 작으면 approximation error도 작다.** 표준편차가 작으므로 확률 분포가 좁게 형성되고, 이는 테일러 급수로 선형화한 모델과 실제 Non-linear한 model의 차이를 적게 만든다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2027.png)

EKF를 식으로 조금 더 자세하게 알아보자. 칼만 필터와 마찬가지로 $p(x_t|u_t,x_{t-1}), p(z_t|x_t)$ 두 확률 분포를 구해보면 Model을 Linearized하게 만들어줬기 때문에 가우시안 확률 분포로 나온다.

## Linearized Motion Model

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2028.png)

## Linearized Observation Model

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2029.png)

# 5.  EKF psudo code

---

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2030.png)

기존의 칼만 필터와 엄청 유사하지만 $A_t,C_t$가 Jacobian matrix $G_t,H_t$로 바뀌었다는 것을 주의하자! $g$는 $G_t$를, $h$는 $H_t$를 local linearization 한 것이다.

- **Perfect Measurement**

**만약 Observation model(Sensor)가 Noise가 없다면 계산은 어떻게 될까?** 즉 센서가 완벽해서 noise=0이고 Q는 0으로 가득한 mtx이다. LINE 4-5를 계산해보면 측정값 $z_t$는 항상 정확하게 예측값 $h(\bar{\mu}_t)$과 동일

$$
\mu_t=(H^T_t)^{-1}*z_t
$$

이다. 이 말은 현재 들어온 observation vector만을 이용하여 현재의 mean 값을 update한다는 이야기이다.

- **Worst Measurement**

반대로, **Observation model(Sensor)가 Noise가 엄청 많다면 계산은 어떻게 될까?** noise=$\infin$이고, noise를 나타내는 matrix인 $Q_t$가 무한한 값을 가지게 된다. Kalman Gain $K_t$=0이다. 따라서 이전에 prediction step에서 예측한 mean값이 현재의 mean값으로 update가 된다. 결과적으로 **센서 노이즈가 크면 상태 업데이트가 거의 이루어지지 않고, 예측값을 유지하는 방향으로 동작한다.**

$$
\mu_t=\bar{}\mu
$$

- **EKF Expample**

EKF는 다양한 예로 쓰일 수 있는데 Localization을 할 때 다음과 같이 쓰일 수 있다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2031.png)

센서가 noisy 하면 아래처럼 불확실성이 커진다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2032.png)

# 6.  EKF 이용한 SLAM

---

EKF를 이용한 SLAM은 First Approach SLAM이다.

요즘은 잘 사용하지 않으며, 다음과 같은 단점을 가진다.

1. 높은 계산 복잡도
2. 짧은 map에서만 사용 가능하다.

Known correspondence를 가정한다. $x_t$는 (3+2n)개의 state로 구성되어 있다. (로봇의 pose $x,y,\theta$ 3개, landmark의 위치 $x,y$ 2n개)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2033.png)

## EKF SLAM Cycle

Filter의 Cycle을 살펴보자. 아래와 같이 로봇이 있다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2034.png)

**(1) State Prediction**

먼저 state를 prediction 한다. $\Sigma$의 1행에 대해 robot pose에 대한 uncertainty가 증가하고, 1열에 대해 landmark에 대한 uncertainty가 증가한다.

이때 robot position은 update 되지만 랜드마크는 업데이트 되지 않는다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2035.png)

(2) Measurement Prediction

실제 로봇의 포즈를 통해 랜드마크가 어떻게 관측될 것인지 prediction 한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2036.png)

(3) Measurement

실제 센서를 통해 맵에 대한 정보를 받아온다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2037.png)

(4) Data association

measurement 한 값과prediction한 값을 적절히 조합한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2038.png)

(5) Update

업데이트 한다. 로봇의 위치와 랜드마크들이 correction 된다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2039.png)

## Example

예제를 풀기 위해 아래와 같이 가정한다.

- 로봇은 평면을 이동
- velocity-based motion model
- 로봇은 덩어리가 아닌 point landmarks를 관측
- range-bearing sensor (거리와 각도를 센싱)
- Known data association (우리가 보는 랜드마크가 몇번째 랜드마크인지 안다.)
- Known number of landmarks (랜드마크의 개수를 안다.)

(1) Initialization

- 로봇은 자신의 reference frame에서 출발한다. (모든 랜드마크는 unknown)
- 2N+3 demensions

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2040.png)

(2) Prediction Step : Motion

LINE 2를 구현하자.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2041.png)

robot의 motion에 기반해 state space를 업데이트 하는 것이 목적이다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2042.png)

위 robot motion in the plane 은 non-linear한 motion 식이다. augmented 된 map에 대한 position도 고려해야 하므로 2n+3-dimensional space로 바꿔준다. robot pose에 대해서는 I, 랜드마크에 대해서는 0인 것을 볼 수 있다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2043.png)

이제 LINE 3을 구현하자.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2044.png)

$G_t$는 non-linear function $g$를 자코비안으로 행렬 구해준다. 아래에서 $I$는 map에 대한 mtx로, 로봇의 모션이 platform에 영향을 주지만 랜드마크의 위치에는 영향을 주지 않음을 뜻한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2045.png)

Prediction Step을 정리하면 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2046.png)

(3) Correction Step : Observation

Known data association이고 내가 지금 관측한 랜드마크가 j번째인 것을 안다는 가정 하에 진행한다. (i.e. $c^i_t=j$ : t 시간에 관측한 i번째 measurement는 j번째 landmark이다.)

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2047.png)

알고리즘을 요약하면, 관측되지 않았다면(unobserved) 랜드마크를 초기화하고, expected observation을 계산한 후 $h$의 자코비안을 계산해 Kalman gain을 계산한다.

Range-bearing observation의 식은 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2048.png)

prediction step에서 랜드마크를 관측한 적이 없다면 로봇의 위치와 상대거리를 더하여 해당 랜드마크가 어디 있는지 구한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2049.png)

현재 추정에 따라 expected observation을 계산한다. $\delta$는 현재 로봇의 위치와 j번째 랜드마크의 위치의 차이이다. $\hat{z}^i_t=h$(non-linear)이다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2050.png)

자코비안을 계산하고 high dimensional space로 맵핑한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2051.png)

Correction step을 정리하면 아래와 같다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2052.png)

## Loop Closing

잘못된 loop closing은 발산을 야기할 수 있다. 오른쪽에서 loop closing 된 것을 보면 uncertainty가 줄어든 것을 볼 수 있다. 오른쪽 그림의 왼쪽 아래에는 여전히 불확실성이 있는데, 이는 오른쪽 위에서 발생한 loop closing이 왼쪽 아래까지 영향을 미치지 않기 때문이다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2053.png)

## Correlation

랜드마크와 로봇의 연결성을 볼 수 있다. fully-connted 그래프로 표현할 수 있으며, 모든 랜드마크들이 correlation을 가진다. 따라서 랜드마크들끼리의 correlation을 무시할 수 없다.

또한 correlation이 있으므로 하나의 랜드마크에 대한 x 위치를 정확하게 안다면 전체적으로 shift, fix가 일어나 다른 랜드마크의 위치도 정확성이 높아진다.

아래쪽 그림은 체커보드 패턴이라고 하는데, 더 많은 매핑을 할 수록 correlation이 커져 fully connedted 해진다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2054.png)

## Uncertainty

map covariance의 어떤 sub-matrix의 determinant는 initial 값이 크고 시간에 따라 감소한다. initial 값이 큰 이유는 랜드마크와 로봇의 uncertainty가 합쳐져 있기 때문이며, time step이 지나감에 따라 measurement가 업데이트 되기 때문에 감소한다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2055.png)

이때 uncertainty가 특정값(initial uncertainty of flatform) 이하로는 감소하지 않는다. 그 이유는 다음과 같다. 로봇의 움직임에 따라 uncertainty는 증가하게 된다. 따라서 현재 로봇의 위치가 가장 정확한 값이고 나아갈수록 더욱 부정확한 값이기 때문에 현재 uncertainty 이하로 감소할 수 없다. 이는 related sensor 사용했을 때의 경우이고, GPS와 같은 external 센서 사용하면 다르다.

![Untitled](7%20Kalman%20Filter%20&%20EKF/Untitled%2056.png)

## Complexity

- Cubic complexity는 measurement dimesionality에만 관련 있다. whole state와 관련 없는 이유는 한 번에 전체 scene을 관측하지 않고 적은 개수의 랜드마크를 관측하기 때문이다.
- step 별 cost는 랜드마크의 개수에 지배적으로 관련이 있다. : $O(n^2)$
- Momory consumption : $O(n^2)$
- EKF는 large map에서 계산하기 어렵다.

따라서 오늘날 EKF SLAM은 큰 환경을 가지는 곳에서 사용하지 않는다. 하지만 VO나 제한된 환경을 가질 수 있는 부분에서는 EKF SLAM도 좋은 선택지이다.

## EKF Summary

- Linear Gaussian 케이스에서 optimal solution 얻을 수 있다.
- non-linearities 가 크면 발산할 수 있다.
- noise가 작을수록 좋은 성능
- Unimodal estimates only (아닌 경우 particle filter 등 다른 방법 사용)
- 큰 scale이 아닌 medium-scale scenes 에서 성공적
- short-term estimates (VO)에서 사용 가능
- Approximations exists to reduce the computational complexity

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 7강 (Kalman Filter & EKF) 요약](https://taeyoung96.github.io/slam/SLAM_07/)

- 확률 통계 용어 정리

[확률 통계 용어정의](https://newsight.tistory.com/197)