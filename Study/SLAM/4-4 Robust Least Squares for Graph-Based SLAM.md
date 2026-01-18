# 4-4. Robust Least Squares for Graph-Based SLAM

# 1. Least Squares approach의 단점

---

**우리는 outlier를 어떻게 handling 할 것인가?** Least squares 방법은 error를 가우시안 분포로 가정하고 squared error의 합을 값을 최소화한다. 이러한 방법에는 크게 두 가지 단점이 존재한다.

1. **Outlier에 굉장히 취약**하다. 실제값과 측정값이 멀리 떨어져 있는 경우 큰 에러가 발생해 모델 자체에 큰 영향을 주게 된다.

실제로 Outlier를 핸들링하지 않으면 모델이 망가진다. 가장 왼쪽은 outlier=1개, 중간은 n개, 오른쪽은 많은 수의 outlier가 존재한다.

![[Attachments/SLAM/Untitled.png]]

1. Edge로 만드는 constraints가 **Gaussian distribution을 따른다고 가정**한다.

센서 모델의 경우 이러한 Gaussian distribution을 따르는 것이 나쁜 결과를 초래하진 않는다. 문제는 Data association이 애매모호한 경우이다. 이러한 Gaussian distribution은 현실 세계(real world)와는 다르기 때문에, 우리가 원치 않은 값으로 최적화가 이뤄질 수 있다.

예를 들어 오른쪽 분포처럼 평균이 아닌 부분에서 큰 값을 가진 분포의 경우 가우시안 분포가 성립하지 못한다. 일반적인 Least Squares 방법에서는 이러한 outlier가 없다는 가정 하에 진행되지만, 실제 환경에서는 outlier가 발생할 수 밖에 없다.

![[Attachments/SLAM/Untitled 1.png]]

**Data association이 모호하게 나타나는 경우**는 다음과 같은 경우에서 빈번하게 나타난다.

1) Landmark들이 모두 비슷하게 보일 때

2) 장소가 굉장히 유사한 곳을 mapping할 때

3) GPS의 신호를 활용하여 Data association을 만들 때 : GPS multi path(signal reflection)

![[Attachments/SLAM/Untitled 2.png]]

![[Attachments/SLAM/Untitled 3.png]]

위 사진은 Data association이 모호하게 나타나는 경우의 한 예이다. 로봇이 비슷한 모양 Landmark로 둘러쌓여 있을 때, 로봇의 pose에 대한 확률이 여러 곳에서 높게 나타난 것을 볼 수 있다.

이번 강의에서는 Data association이 모호할 때, 우리가 어떻게 Outlier를 처리하고 Robust한 Least squares approach를 적용할 것인지 아래 방법론들에 대해 다룰 것이다. 세 가지 중 아래 두 방법은 outlier에 weight를 줘 outlier의 영향을 줄이는 방법이다.

- Max Mixture or Dealing with Multiple Modes
- Dynamic Covariance Scaling
- Least Squares with Robust Kernels

# 2. MaxMixtures or Dealing with Multiple Modes

---

첫번째 방법은 **MaxMixtures or Dealing with Multiple Modes**이다. Model을 정의할 때 하나의 Gaussian Model로 정의하는 것이 아니라 여러 모드로 일반화할 수 있는 방법이다.

- Multi-model constraints에 유용하다. (D.A. ambiguities)
- Outlier 다루는 데 유용하다.

앞서 배웠던 Pose graph에서 최적화할 부분을 **Gaussian Model**로 정의하고 수식으로 풀어쓰면 다음과 같다. 우리가 최적화를 할 때 자주 보던 $e^T_{ij}\Omega_{ij}e_{ij}$에 Gaussian distribution만 적용한 것이다. $\eta$ 는 Gaussian distribution 식을 만들 때 사용한 상수값을 나타낸다.

Error minimization을 진행할 때는 Log likelihood를 사용하기 때문에 위의 식은 아래와 같이 변형된다. 지수(exponential)꼴로 복잡하게 정리됐던 식을 원소들의 덧셈으로 정리할 수 있다.

![[Attachments/SLAM/Untitled 4.png]]

![[Attachments/SLAM/Untitled 5.png]]

이제 single이 아닌 multiple mode를 나타내보자. 우리가 multiple mode로 나타낼 수 있는 **첫번째 방법은 서로 다른 Gaussian distribution을 합하는 방법이다.** 그럼 식은 아래와 같이 달라진다.

서로 다른 $k$개의 Gaussian distribution에 대해서, 각 가우시안 분포에 대한 Weight term인 $w_k$를 부여하고 모두 합쳐서 식을 정의한다. 마찬가지로 Error minimization을 진행할 때는 Log likelihood를 사용하기 때문에 식은 아래와 같이 변형된다. 현재 pose x에 대해 어떤 observation z가 나와야 하는지 확률적으로 표현한다.

![[Attachments/SLAM/Untitled 6.png]]

![[Attachments/SLAM/Untitled 7.png]]

single Gaussian의 경우 log likelihood를 계산하기 쉬웠지만, k mode의 경우 log가 $\Sigma_k$ 연산자 안으로 들어가지 못해 쉽게 계산할 수 없다. 따라서 **Max Mixture는 근사치만 계산하도록 식을 재구성한다.** 강의에서는 **가장 중요한 mode의 값만 남겨둔다**고 표현한다. $\Sigma_k$ 연산자 대신 $max_k$ 연산자를 사용해 Log likelihood 적용 시 더 깔끔한 식으로 정리할 수 있다. **$max_k$ 연산자를 이용해 single Gaussian처럼 다룬다.**

![[Attachments/SLAM/Untitled 8.png]]

$max$ 연산자를 사용하기 때문에 “Max mixture”라고 부른다.

![[Attachments/SLAM/Untitled 9.png]]

위의 왼쪽은 두 Gaussian distribution을 나타낸 것이고, 오른쪽은 $\Sigma$연산자를 사용했을 때 Gaussian distribution, 중간은 $max$ 연산자를 사용했을 때 Gaussian distribution이다. approximation error가 조금 존재하지만 식을 간단하게 할 수 있기 때문에 $max$ 연산자를 사용해서 Gaussian distribution를 만든다.

![[Attachments/SLAM/Untitled 10.png]]

왼쪽 그래프를 보면 y1과 y2의 두 평균이 멀고 분산이 작아 서로 겹치는 구간이 적다. 이 경우 sum과 max 방식이 아주 적은 차이를 보인다. 오른쪽 그래프는 y1과 y2가 겹치는 부분이 많아 max과 sum의 차이가 꽤 있다. 하지만 실제 outlier가 발생하는 경우는 큰 에러(평균으로부터 멀리 떨어져 있다)가 발생하기 때문에 겹치는 부분이 많지 않아 max와 sum의 차이가 크지 않을 것이다.

따라서 Max mixture 식에서 Log Likelihood를 적용한 식은 아래와 같다. log term이 $max$ 연산자 안으로 들어갈 수 있어 쉽게 계산 가능하다.

![[Attachments/SLAM/Untitled 11.png]]

### Max Mixture 적용하는 과정

---

1. 모든 mode의 가우시안 분포에 대해 확률 계산
2. 현재 위치에서 가장 큰 값을 가지는 분포 선택
3. 최고값을 가지는 분포만을 가지고 **single Gaussian과 같은 방식으로** optimization 진행

"Max mixture" 을 사용하면 우리가 기존에 해왔던 Error minimization을 서로 다른 Gaussian distribution에 따라서만 값을 바꿔주고 최소값을 찾으면 되기 때문에 우리가 기존에 사용했던 Error minimization식을 그대로 활용할 수 있다.

- **Runtime**

max mixture는 모든 가우시안 분포를 계산해야 하므로 runtime이 조금 더 길지만, 기존의 Error minimization 방법과 차이가 얼마 나지 않는다는 것을 알 수 있다. 파란색 방식이 Standard Least Squares 방식이다.

![[Attachments/SLAM/Untitled 12.png]]

- **Performance**

![[Attachments/SLAM/Untitled 13.png]]

![[Attachments/SLAM/Untitled 14.png]]

- **Outlier에 Robust**

Outlier에 굉장히 Robust하게 작동할 수 있다. 서로 다른 모드를 적용하여 하나는 주요 constraints값으로 분포를 만들고, 다른 하나는 이상적인 Gaussian 분포(flat Gaussian)로 만들어 outlier를 제거하는 방식을 사용한다. 따라서 Data Association이 모호할 때 사용하면 굉장히 효과적이다. 아래와 같이 다양한 mode (빨간색, 파란색)에 대해서 서로 다른 분포를 만들고 Max mixture 방법을 사용한다.

![[Attachments/SLAM/Untitled 15.png]]

![[Attachments/SLAM/Untitled 16.png]]

# 3. Dynamic Covariance Scaling

---

두번째 방법은 **Dynamic Covariance Scaling**이다. 평균에서 멀리 떨어져 있는 constraint들은 weight down 하는 방법이다. 기존의 error function에 weighting term 을 추가해 outlier가 영향을 적게 미치도록 한다. wieght는 error value에 좌우된다. Robust Least Squares Estimation의 special case이다.

보통의 Least squares는 아래와 같은 식을 활용한다.

![[Attachments/SLAM/Untitled 17.png]]

Dynamic Covariance Scaling은 이 식에 Scale term ($s_{ij}$)을 추가해 아래와 같이 식을 만든다.

![[Attachments/SLAM/Untitled 18.png]]

각각의 observation마다 scale term을 추가할 경우, outlier에 해당하는 값은 scale term을 통해 Error minimization을 하는데 적은 영향을 끼치게 할 수 있다(wieght down).

- $\chi ^2_{ij}$ : 기존의 Least squares에서 사용하는 값
- $\Phi$ : 사전에 정의한 parameter의 값

$min$ 함수를 통해 1과 계산된 값 중 더 작은 값을 $s_{ij}$로 채택하기 때문에 $s_{ij}$는 1이거나 1보다 작은 값이다. 즉, **error가 기준값** $\Phi$ **보다 작으면 weight term=1로 두어 weigt를 주지 않고, error가** $\Phi$ **보다 커지면 더 강하게 scaling down한다.**

![[Attachments/SLAM/Untitled 19.png]]

Error function을 시각화하면 아래와 같다. 에러가 커질수록 weighting term이 0에 가까워져 적은 영향을 미친다.

![[Attachments/SLAM/Untitled 20.png]]

검은색 line은 기존의 Error function, 파란색 line은 scale factor, 빨간색 line은 Dynamic Covariance Scaling 방법을 적용한 Error function이다. 파란색 값이 1일 경우, 기존의 검은색 line과 빨간색 line은 같은 값을 가지게 되지만, 파란색 값이 작아질 경우(중심에서 멀어진 값들), Error에 대한 값도 작아
져 outlier에 강인하도록 식이 설계됐다.

**달라진 기울기는 선형화, Jacobian을 만들 때도 영향을 미치게 된다.**

Dynamic Covariance Scaling 방법은 Least Squares with Robust Kernel의 special case이다.

# 4. Least Squares with Robust Kernels

---

**Least Square의 문제점**

1. **가우시안 분포를 가정한다.**
    - 가우시안 분포는 에러가 커질수록(=그래프의 끝으로 갈수록) 적은 확률을 가진다.
    - 그런데 outlier를 다루기 위해서는 끝에 있는 부분에 대해서도 확률을 표현 할 수 있는 다른 확률 분포를 사용해야 한다.
    - 이때 에러의 분포를 어떤 것을 사용하느냐에 따라 얼마나 많은, 또는 어떤 종류의 outlier를 고려할 수 있는지가 달라진다.
    - outlier의 분포는 완전히 랜덤할 수도 있고, 어떤 특징이나 함수라는 정보를 가지고 있을 수도 있다.
2. **squared error(2차식)를 사용한다.**
    - Model이 Gaussian distribution이 아니라면 이차식으로 outlier에 robust하게 Error minimization을 하는 것이 힘들다.
    - 따라서 ‘Least Squares with Robust Kernels’ 방법에서는 에러를 구한 후 최적화 과정에서 squared error를 구하지 않고 에러를 $\rho$ function으로 만든다. **$\rho$ function은 에러의 확률분포를 정의**한다.

확률밀도함수(PDF)를 정의하기 위해 $\rho$ function을 재정의하고 최적화를 위해 negative log likelihood를 구한다. $e$는 error function의 value이다. (not error vector)

![[Attachments/SLAM/Untitled 21.png]]

Gaussian distribution일 때는 $\rho(e_i(x))$함수를 우리가 기존에 사용했던 이차식 $\rho(e)=e^2$으로 사용하고 그렇지 않을 때는 다른 함수를 사용한다. 즉, 우리가 사용하던 식을 일반화 한 것이다.

따라서 이차식 이외에도 다양한 function들을 적용할 수 있다. 함수들의 종류는 아래와 같다. 어떤 $\rho$ function 을 적용하느냐에 따라 여러 outlier를 핸들링 할 수 있다.

- Gaussian : $\rho(e)=e^2$
- L1 norm : $\rho(e)=|e|$
- Huber function(Huber M-estimator) : solution 주변에서는 2차식, threshold 이상 멀어지면 선형

![[Attachments/SLAM/Untitled 22.png]]

- Tukey, Cauchy…

다양한 함수를 시각화한 모습은 아래와 같다. 그림의 함수들 중에는 L1 function을 제외하면 mean 주변에서는 quadratic form을 형성하고 에러가 기준값을 넘어가면 flat한 모습이다. (flat하다 = 자코비안이 0에 가깝다 = 에러가 optimization에 있어 영향이 거의 없다)

![[Attachments/SLAM/Untitled 23.png]]

## 4-1. Robust Estimation as Weighted Least Squares

---

Dynamic Covariance Scale(기존의 Least squares 방법에서 Weight를 추가한 방법)은 일종의 Robust Kernel 모델이다. 두 가지 방법을 비교해보자.

![[Attachments/SLAM/Untitled 24.png]]

그리고 위 두 식의 편미분값을 구하고, 비교를 한번 해보자. (optimum에서 gradient=0)

![[Attachments/SLAM/Untitled 25.png]]

위 식에서 빨간색 부분을 제외하곤 모든 부분이 같다는 것을 알 수 있고, $\rho$ function을 잘 설계하면 Weighted Least Squares(DCS)와 비슷하게 설계 할 수 있다는 것을 알 수 있다.

![[Attachments/SLAM/Untitled 26.png]]

우리는 **Weight를 잘 설계하면 Weighted Least Squares의 방법을 사용하여 Robust estimation을 활용할 수 있다!** 즉, Robust estimation과 Weighted Least Squares을 비슷하게 생각해도 무방하다.

Robust Least Squares를 정리하면 다음과 같다.

- DCS(Weighted Least Squares)의 방법을 사용하여 Robust estimation을 활용할 수 있다.
- Kernel(function의 모양)은 Jacobian에 영향을 준다.
- Kernel의 선택에 따라 Outlier를 잘 제거할 수 있다.

그렇다면 어떤 kernel을 선택해야 할까? Robust Kernel을 적용하기 위해서는 적절한 $\rho$ function을 결정해야 한다. **$\rho$ function 결정은 outlier의 분포를 따른다.** 만약 outlier가 Cauchy distribution을 따른다면 $\rho$ function도 Cauchy distribution과 유사한 형태로 정해진다. 하지만 실제로는 outlier의 분포에 대한 정보가 없는 경우가 많다. 따라서 적절한 $\rho$ function을 정의한다는 것은 경험적으로 알고 결정하거나 trial&error를 거치며 분포를 찾아야 한다.

Robust Kernel을 적용한 SLAM 알고리즘들은 최적화 과정에서 **Iteration을 거치며 $\rho$ function을 바꿔주며 outlier을 제거하는 전략**을 가져갈 수 있다.

1. $N_1$ 번의 iteration에서는 확률밀도함수(PDF)의 끝 부분(tail)도 영향을 많이 끼치는 것을 고려(strong tail)를 해서 outlier 제거를 많이 진행한다.
2. $N_2$ 번의 iteration에서는 확률밀도함수(PDF)의 끝 부분(tail)도 영향을 적게 끼치는 것을 고려(weak tail)를 해서 outlier 제거를 적게 진행한다.
3. 어느정도 outlier를 제거해 outlier에 robust 하다고 가정하고 에러의 영향이 큰 kernel(Gaussian 또는 Huber function 등)을 사용하여 최적화를 진행한다.

이 방법은 별로 좋은 방법이 아니다. $N_1, N_2$를 어떻게 결정하는지도 Issue가 될 것이고 outlier 제거가 얼만큼 됐는지도 heuristic하게 결정하기 때문이다. 또한 자코비안을 계속 새롭게 계산해야 하고 사용하는 커널에 따라 계속해서 코드를 수정해주어야 한다.

이를 보완하기 위해 Gereralized Robust Kernels가 등장한다.

## 4-2. Generalized Robust Kernels

---

CVPR 2019에 accepted된 “A General and Adaptive Robust Loss Function” 방법을 소개한다.

“A General and Adaptive Robust Loss Function”을 참고하면 조금 더 이해하기 쉬울 것이다.

["A General and Adaptive Robust Loss Function" Jonathan T. Barron, CVPR 2019](https://www.youtube.com/watch?v=BmNKbnF69eY&feature=youtu.be)

이 논문에서는 function을 다음과 같이 제안한다.

![[Attachments/SLAM/Untitled 27.png]]

- $e$ : 우리가 기존에 봤던 error 값
- $c$ : 우리가 어느 지점에서 이차식에서 어떤 function으로 바꿀지 결정
- $\alpha$ : 다양한 function을 선택 가능

$\alpha$ 값을 조정해 여러 $\rho$ function을 나타낼 수 있다.

![[Attachments/SLAM/Untitled 28.png]]

아래 그림은 $\rho$ function과 weight function을 시각화 한 그림이다. $\alpha$에 따라 function의 모양이 달라지는 것을 확인할 수 있다. $\alpha$ 가 작을수록 outlier의 영향을 줄이는 형태이다. $\alpha=-\infin$일 때는 error가 일정 부분보다 커지면 에러 분포에 대한 변화가 거의 없고 weighting도 0에 가까워 outlier에 대한 영향을 많이 줄일 수 있다.

![[Attachments/SLAM/Untitled 29.png]]

아래 그림의 Outlier distribution을 파란색 histogram(residuals)이라고 할 때, 다양한 $\alpha$에 따라 최적의 function을 만들 수 있는 것이 이 방법의 핵심이다. 최적의 function은 노란색 line으로 표현됐다. 각 분포에 따라 적절한 $\rho$ function이 다르다.

![[Attachments/SLAM/Untitled 30.png]]

Generalized Robust Kernel을 사용하면 outlier의 분포와 상관 없이 모두 다 최적화 해낼 수 있다!

## 4-3. Adaptive Robust Loss Function

---

하지만 Generalized Robust Kernel을 사용해 최적화 하면 원래 outlier의 분포에 대한 정보가 없는 경우 여러 $\alpha$ 값에 대해 시도하며 적절한 알파 값을 찾아야 한다. **이때 $\alpha$ 값 자체도 최적화 대상에 포함시키면 자동으로 최적의 알파를 찾을 수 있다.**

**또한  $\alpha$를 모든 에러를 0으로 만드는 trivial한 값으로 결정할 수도 있다는 문제점이 있는데, 이를 예방하기 위해 normalized funciton 이라고 하는 $Z(\alpha)$ term을 붙여 에러 함수를 새로 정의한다.**

이 방법론에서는 최적화할 식을 아래와 같이 다시 설계한다. 이전에는  $\alpha$ 값을 고정해두고  $\alpha$에 여러 값을 대입하며 최적화 과정을 시도했지만, 이제는 $\alpha$ 자체를 최적화시키며 최적화한다.

![[Attachments/SLAM/Untitled 31.png]]

앞서 $\rho$ function에서는 $c$도 parameter 였는데, $c$는 $\alpha$에 따라 결정되는 implicit parameter이다. 위 함수를 활용해 확률 밀도 함수를 만들면 다음과 같다. $Z(\alpha)$는 Normalized 하는 의미를 가진다.

![[Attachments/SLAM/Untitled 32.png]]

하지만 $Z(\alpha)$를 정의할 때 $(-\infin ,\infin)$범위에서 적분 하게 되는데 $\alpha$의 값이 양수일 때는 수렴 하지만, 음수일 때는 $e^{-\rho(e, \alpha,1)}$ term이 계속 양수를 유지하며 발산하기 때문에 문제가 된다. 따라서  $\alpha$를 양수로 제한해야 했다. 이때 적분을 할 때 범위를 유한한 값으로 정해주는 trick을 사용하면 $\alpha$가 음수여도 괜찮다. 논문에서는 $\tau=10c$ 로 잡았을 때 충분했다고 한다.

![[Attachments/SLAM/Untitled 33.png]]

아래의 가장 오른쪽 그림에서 보이듯, $\alpha$ 값이 작아지면 outlier에 대한 영향도 작아지지만 inlier에도 penalty가 생긴다. 따라서 tivial한 $\alpha$ 값이 아닌 최적의 $\alpha$ 값을 구할 수 있다. $Z(\alpha)$로 인해 그래프가 전체적으로 shift 된 것을 볼 수 있다.

![[Attachments/SLAM/Untitled 34.png]]

Adaptive Robust Kernel을 사용할 경우, 실제로는 다음과 같은 문제들도 생각해야 한다.

- $\alpha$ 자체가 최적화 대상이기 때문에 $\alpha$에 대해 새로운 Jacobian이 계속해서 계산 필요
- $\alpha$값을 바꾸는 것이 parameter 추정을 하는데 많은 영향을 미친다.
- 초기값에 민감하다. $\alpha$ 값이 initial guess에 따라 최적화를 아예 하지 못하는 경우도 있다.

따라서 ‘EM-based optimization with Adaptive Robust Kernel’ 방법을 제안한다.

## 4-4. EM-based optimization with Adaptive Robust Kernel

---

EM-based optimization with Adaptive Robust Kernel는 모델이 수렴할 때까지 E step과 M step을 반복한다. EM은 expectation maximization의 약자이다.

- E-step : 현재 예측값에 대해 계산한 에러를 최소화할 수 있는 $\alpha$를 찾는 것이 목표 (현재 예측한 x에 대해 최적화 할 수 있는 $\alpha$ 찾기)
- M-step : E-step에서 추정한 $\alpha$를 활용해 에러값을 최소화하는 예측값 x 찾는 것이 목표

$\alpha$ 값을 찾는 것과 x 값을 찾는 것을 분리할 수 있어 자코비안을 새로 계산할 필요가 없다. 또한 코드 수정 없이 앞에서 했던 방법의 적용이 가능하다.

강의 슬라이드로 표현하면 아래와 같다.

![[Attachments/SLAM/Untitled 35.png]]

이러한 Robust kernel 방법을 SLAM problem, ICP 알고리즘이나 Bundle adjustment에 적용하면 outlier에 강인하도록 알고리즘을 설계할 수 있다. Cyrill 교수님의 말에 의하면 EM-based optimization with Adaptive Robust Kernel이 가장 outlier를 잘 제거하는 결과를 보인다.

# 5. Summary

---

가장 중요한 것은 Outlier distribution의 모양은 무엇인가? 이다.

Outlier를 제거하기 위해 사용하는 여러가지 방법 중 첫번째 방법은 “MaxMixture”이다. 이 방법은 여러 Gaussian distribution을 합치고 계산의 편의성을 위해 연산자를 사용하는 방법이다.

두번째 방법은 “Dynamic Covariance Scaling”이다. 이 방법은 kernel을 하나로 채택하고 고정해야 할 때 사용하면 좋은 방법이다. 이 방법은 Robust least squares estimation의 특별한 방법이다.

마지막으로는 “Adaptive robust kernel을 활용한 Least squares” 방법이다. 보통의 경우 outlier distribution을 모르기 때문에 이 방법이 제일 유연하게 여러 상황에 대처할 수 있는 방법이라고 설명한다.

EM-based optimization이 가장 최근에 연구되고 제시된 방법이다.

# Reference

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 4-4강 (Robust Least Squares for Graph-Based SLAM) 요약](https://taeyoung96.github.io/slam/SLAM_04_4/)