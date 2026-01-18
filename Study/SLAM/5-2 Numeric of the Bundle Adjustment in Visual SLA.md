# 5-2. Numeric of the Bundle Adjustment in Visual SLAM

# 1. **Bundle Adjustment**

---

<5-1>에서 설명했던 Bundle Adjustment를 실제로 어떻게 사용하는지 설명해보자. BA는 non-linear least squares 방법이다. 이미지에서의 projection error를 최소화하며, 추정한 3D point들을 추정한 카메라 이미지들에 Project 한다. 이 projected 3D point들을 관측한 2D pixel 좌표와 비교한다. 여러 점들을 한 번에 bundle로 묶어 projection error를 줄이기 때문에 Bundle Adjustment 라고 한다.

![Untitled](5-1%20Basics%20about%20Bundle%20Adjustment%20in%20Visual%20SLAM/Untitled%206.png)

Unknown parameter는 다음과 같다. 이 파라미터들을 reprojection error 최소화 시키는 방향으로 refine 한다. 이 중에서 **6DoF Camera Pose와 3D point를 제외한 다른 파라미터들은 알고 있다고 가정하고 생략할수 있다.**

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled.png)

식을 정의했다면 Least squares approach를 사용해 최적화를 진행한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%201.png)

- A : Jacobian Matrix
- $\Sigma$ : Covariance matrix
- $x$ : unknown parameter
- $l$ : observation

### +) **SLAMDUNK 강의자료**

3차원 포인트를 이미지 상에 projection한 좌표와 실제 이미지에 있는 좌표를 비교하여 projection error를 최소화한다. BA를 통해 refine 할 수록 둘 사이의 거리는 가까워진다. 한 포인트를 여러 위치에서 바라보고, 한 카메라도 여러 포인트를 보게 되는데 동시에 번들로 묶어 진행하기 때문에 bundle adjustment라고 한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%202.png)

- C : center 좌표계(translation), K : intrinsic mtx
- X는 포인트의 3D homogenuous 좌표 / [u v w]T는 계산한 포인트의 2D homogenuous 좌표
- reprojection error : (이미지 상의 실제 픽셀 좌표) - (3D 포인트를 이용해 계산한 2D 좌표)
- error를 최소화하는 방향으로 unknown parameters를 refine 해야한다.
- scale factor는 w(z축 값)로 나눌 때 사라지므로 고려하지 않는다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%203.png)

**Gradient Descent 방법으로 최적화 한다.** Jacobian을 구할때, 우리가 구해야 하는 파라미터인 camera pose, 3D point가 Jacobian의 파라미터가 된다. 또한 observation의 constraint가 된다.

Normal equation은 Gauss Newton과 같다고 볼 수 있는데, $||y-X\theta||^2$ 는 error이고, $A^T\Sigma^{-1}A=J^2$는 Hessian이다. 더 빠르게 계산하고 singular에 빠지지 않기 위해 Levenberg, Levenberg-Marquardt 방법을 사용할 수 있다.

# 2. Example of **Bundle Adjustment**

---

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%204.png)

Normal equation은 Hessian과 Jacobian의 element들이다. 이것들을 double 형태로 저장하면 무려 2.8TB의 저장공간이 필요하다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%205.png)

검은색 line을 따라 UAV가 움직이고 있고, 49개의 map points가 있다고 가정하자. 그리고 꼭짓점 쪽에 삼각형으로 되어있는 points는 control points(map points의 위치를 정확히 아는 points)이다. 즉, 최적화를 하는 대상이 아니다. (최적화 해야할 map points는 전체 49개에서 4개의 control points를 뺀 45개의 map points이다.) 정사각형으로 표시된 것이 한 이미지를 나타낸 것인데, 첫번째 이미지에서는 총 6개의 map points들이 관찰되었고, 두번째부터 9개의 map points들이 관찰되었다. 본 예시에서는 촬영 영역에 control point를 설치해 boundary condition처럼 사용하였다.

이 예시의 구성은 아래와 같다.

- 6개의 image에서 6개의 points가 관찰된다.
- 15개의 image에서 9개의 points가 관찰된다.
- Observation : 342개
    - 관찰되는 이미지 포인트에 x, y 좌표 : 171X2=342
- Unknown parameters : 261개
    - 45개의 map points에 대해서 x,y,z 좌표 정보 : 45*3 = 135
    - 21개의 이미지에 대한 6DoF 정보 : 21 * 6 = 126
    - 135 + 126 = 261

## 2-1. 식 변형하기

---

계산의 편의성을 위해서 식을 변형해준다.

$$
\Delta l+v=A \Delta x
$$

- $\Delta l$ : Observation
- $v$ : correction
- $A$ : Jacobian Matrix
- $\Delta x$ : unknown variables

라고 정의하고 $\Delta x$를 3D points에 대한 변수와 6DoF에 대한 정보로 쪼개준다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%206.png)

$\Delta t$는 camera orientation parameter이다.(not tf) 변형된 식은 다음과 같다.  $\Delta x$를 나눈 것에 맞추어 $A$ 행렬도 나누어준다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%207.png)

따라서 $i$번째 3D Map point, $j$번째 이미지(=카메라)에서 바라본 error equation은 아래와 같다. $U$는 unknown paraeters의 갯수이다. 그냥 변형된 식에 맞추어 쪼갰다고 생각하면 된다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%208.png)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%209.png)

Jacobian matrix를 쪼개는 것이 이 식 변형의 핵심이다. 우리가 고려하는 파라미터에 필요한 성분을 가지고 있는 matrix만 가지고 계산할 수 있기 때문이다. 즉, Jacobian matrix의 크기를 줄여 real-time으로 계산할 수 있다. **Jacobian matrix $A$는 sparse 하기 때문에 식의 변형을 통해 0으로 채워져 있는 성분을 제거해 계산량을 줄일 수 있다.** Jacobian matrix를 시각화하면 아래와 같다. 검은색 부분을 제외하면 모든 성분은 0이다. matrix가 커질수록 더 sparse 해진다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2010.png)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2011.png)

$B$  Matrix와 $C$ Matrix의 모양이 규칙적인 이유는 UAV의 trajectory가 일정하기 때문이다.

$C$ Matrix에 대해서 특징은 아래와 같다.

- $(2 \times 3)$ 크기의 sub-matrices $C^T_{ij}$로 이루어져 있다.
- 성분들이 의미하는 것은 실제 이미지에서 뽑아낸 feature point $x'_{ij}$과 3D point $\hat{X}_i$의 관계이다.

$B$ Matrix에 대해서 특징은 아래와 같다.

- $(2 \times 6)$ 크기의 sub-matrices $B^T_{ij}$로 이루어져 있다.
- 성분들이 의미하는 것은 실제 이미지에서 뽑아낸 feature point $x'_{ij}$과 카메라(이미지) orientation $j^{th}$의 관계이다.

## 2-2. 변형한 식으로 최적화 진행하기

---

$B$ matrix와 $C$ matrix는 어떻게 계산하고 찾아낼까? 실제로는 여러 math tool들을 활용한다.

- Compute Jacobians analytically : 식을 세우고 미분 값을 구하는 정석적인 방법
- Compute Jacobians numerically : 이번 강의에서 주로 다루는 내용

목표는 Least squares approach로 non-linear optimization을 하는 것이다. 따라서 우리는 아래와 같은 Matrix를 구해야 한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2012.png)

이러한 Normal matrix를 $C, B$ matrix를 활용해서 나타내면 다음과 같다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2013.png)

N에 대해 더 자세히 설명해보자. $B_i$는 포인트가 관측된 이미지이다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2014.png)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2015.png)

## 2-3. Orientation parameter delta_t 계산

---

최적화를 수행할 때 Orientation parameter만을 최적화 해보자.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2016.png)

Orientation parameter만을 최적화 하기 위해 식 변형을 해준다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2017.png)

이렇게 Reduced normal system을 구할 수 있다(마지막 줄). point의 수에 독립적이고, 여전히 sparse 하며, 크기는 $(126 \times 126)$=(# of obs)X(# of obs) 이다. Matrix를 시각화하면 아래와 같다. 검은색 부분이 non-zero 성분이고, 하얀색이 zero 성분이다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2018.png)

이제 실제로 계산을 진행하면 아래와 같다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2019.png)

$N_{kk}$ mtx는 Diagonal mtx 이기 때문에 계산량이 많지 않다. 이 식을 풀면 Orientation parameter $\Delta t$를 알 수 있다.

## 2-4. **Map points parameter** delta_k 계산

---

$\Delta t$를 구했으니 이 값을 이용해 Map points parameter $\Delta k$를 구한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2020.png)

위 식에서 Upper block의 식을 활용하여 $\Delta k$에 대한 식을 구하면 아래와 같다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2021.png)

$\Delta k$에 대해 정리하면 아래와 같다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2022.png)

지금까지 이야기한 과정을 정리해보면 다음과 같다.

우선 $N$ Matrix의 성분을 계산한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2023.png)

그 다음 $N_{tt}, h_t$를 계산한다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2017.png)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2024.png)

위 식에서 $\Delta t$를 계산한 후, 아래 식을 이용해 $\Delta k$를 계산한다. 이때 $N^{-1}_{kk}$는 앞에서 이미 구했으므로 다시 연산할 필요가 없다. (연산량 감소)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2025.png)

# 3. **BA without Control Points**

---

Control Points는 Map points들 중에서 위치를 알고 있는 Points들을 뜻한다. **Control Points가 없다는 것은 Reference frame이 정의되어 있지 않다**는 것과 같은 의미이다.

이러한 경우 어떤 문제가 발생할까?

Normal equation에서 Rank deficiency가 일어난다. 이러한 현상을 **Gauge-freedom**이라고 한다. 따라서 추가적인 Constraints를 붙여 Datum(기준이 되는 면, 선, 점)을 만들어준다. Gauge Freedom 제거하기 위해서는 7(3 Rotation + 3 Translation + 1 Scale)개의 constraint가 더 필요하다. 추가할 수 있는 Constraints는 다음과 같다.

- 3D points들의 무게 중심(center)은 변하지 않는다고 가정한다. (Translation에 대한 Constraints)
- Main direction을 고정한다. (Rotation에 대한 Constraints)
- center 까지의 Points간의 평균 거리를 고정한다. (Scale에 대한 Constraints)

<aside>
💡 **Gauge-freedom**
같은 상태가 두 개의 다른 좌표계로 설명이 되는 시스템

Contol point 관측 시 내부의 값들은 차이가 없지만, 외부의 어떤 각도와 위치에서 관측하느냐에 따라 숫자가 달라진다. 여기서 자유도가 추가적으로 발생한다. 이런 것들을 고정하여 원하는 모습이 나오게 하거나 추가적인 자유도에서 야기되는 엉뚱한 방향으로의 수렴을 막는다.

<4-1>을 생각해보자. 왼쪽은 가장 아래 row를 추가해 자코비안 관점에서 pose 1에 대한 constraint를 추가해 Gauge Freedom을 없애는 효과를 가지고 있다. determinant가 0이 되지 않게 하는 효과도 있는데, gauge freedom 때문에 determinant 값이 0이 되기도 하므로 같은 말이다. 오른쪽은 가장 왼쪽 column을 제거해 카메라 1의 포즈를 고정하는 효과를 가진다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2026.png)

</aside>

Constraints Matrix를 $H$로 정의하고, 최적화를 진행할 때 Matrix에 대한 정보를 활용하면 Rank deficiency를 해결할 수 있다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2027.png)

### +) **SLAMDUNK 예시**

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2028.png)

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2029.png)

우리는 MATLAB toolbox를 이용해 계산할 수 있다. 아래는 픽셀 좌표 x에 대한 Rotation 벡터의 편미분 값인데 오른쪽을 보면 결과값이 매우 긴 것을 확인할 수 있다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2030.png)

Jacobian matrix는 매우 sparse 하다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2031.png)

Hessian matrix도 매우 sparse하다. 가장 연산량이 큰 부분이 $(J^TJ)^{-1}$, 즉 Hessian의 inverse를 구하는 부분이다. 이때 Hessian matrix를 block으로 나눌 수 있는데, block 이기 떄문에 inverse를 구하기가 쉽다. 각 block의 inverse를 구하여 전체 mtx의 inverse를 쉽게 구할 수 있다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2032.png)

## Outlier 제거하기

---

기본적으로 Noise를 Gaussian distribution으로 가정을 하기 때문에 이차식을 만들어 최적화를 진행했는데, 실제 현실 세계에서는 그렇지 않은 경우가 훨씬 많다.

이 때 Robust kernel을 활용하여 Outlier에 강인한 Error minimization을 수행할 수 있다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2033.png)

좋은 Initial guess를 가지고 있다면 Blake-Zisserman과 같은 kernel을 사용하는 것이 효율적이지만, Initial guess를 좋게 만들 수 없다면 Huber kernel을 사용하는 것을 추천하셨다.
계속 강조하지만 아래와 같은 Robust Kernel의 사용도 추천하셨다.

![Untitled](5-2%20Numeric%20of%20the%20Bundle%20Adjustment%20in%20Visual%20SLA/Untitled%2034.png)

# 4. Summary

---

이번 강의로 Bundle Adjustment를 실제로 수행할 때 사용하는 기법들에 대해서 알아보았다. Bundle Adjustment란 불확실성을 고려하여 Relative 그리고 Absolute Orientation을 찾아내는 방법이고, 여기서 사용하는 error를 reprojection error라고 한다. Least squares appraoch를 사용하여 최적화를 진행한다.

효율적으로 Bundle Adjustment를 푸는 방법의 핵심은 Sparse solver에 있다. 즉, J와 H행렬에 0 성분이 많은 점을 활용하여 효율적으로 계산을 진행한다.

우리가 찾아야 하는 paramters는 Orientation parameters와 Map point parameters로 이루어져 있다. Orientation parameters를 먼저 계산하여 찾은 다음, Map point parameters를 찾으면 조금 더 빠르게 parameters를 구할 수 있다.

또한 Control point에 있어 Gauge-Freedom을 제거하기 위해 고정한다.

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 5-2강 (Numeric of the Bundle Adjustment) 요약](https://taeyoung96.github.io/slam/SLAM_05_2/)