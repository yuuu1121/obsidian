# 5-1. Basics about Bundle Adjustment in Visual SLAM

# 1. Bundle Adjustment란?

---

**2D pixel location을 기반으로, 3D point location과 camera frame 간의 3D relative motion을 동시에 최적화하는 Least Squares 기법**

![[Attachments/SLAM/Untitled.png]]

bundle of ray를 보정(adjust)한다는 의미로 Bundle Adjustment라고 한다. 보통  SIFT와 같은 feature extraction 알고리즘을 수행한 후 triangulation과 같은 과정을 거쳐 3차원 공간에 point들이 어디 위치하고 있는지 추정한다.

![[Attachments/SLAM/Untitled 1.png]]

위와 같은 드론으로 아래쪽에 위치한 카메라를 활용하여 3D Reconstruction을 수행하면 결과는 아래와 같다.

![[Attachments/SLAM/Untitled 2.png]]

위 그림에서 파란색 사각형 처럼 보이는 것이 이미지이고 아래쪽에 point cloud 형식으로 시각화된 것이 3차원 output이다. Bundle Adjustment의 결과를 활용하여 위와 같은 예제의 output을 만들 수 있다.

그렇다면 두 장의 이미지가 아닌 더 많은 이미지 set이 필요한 이유는 무엇일까?(Multi-view Reconstruction) 물체를 3차원으로 표현할 때 2장의 이미지로는 물체의 복잡한 표면을 모두 담아낼 수 없기 때문이다. 여러 이미지들을 활용하면 추정한 결과(camera pose or 3D location points)를 더 정교하게 최적화할 수 있다. 최적화 과정(Bundle Adjustment)을 수행하면 아래와 같이 대규모의 Map을 만드는 것도 가능하다.

![[Attachments/SLAM/Untitled 3.png]]

Bundle Adjustment는 Bundle Block Adjustment라고도 부르는데, Bundle Adjustment 과정을 Block 단위로 수행하여 많은 이미지 쌍을 동시에 고려해 최적화를 수행하기 때문이다. Bundle Adjustment라는 개념은 1950년대 photogrammetry분야의 Aerial Triangulation라는 분야에서 처음 나왔다. Aerial Triangulation은 areial 이미지들을 사용해 point의 3D 위치를 추정하는 것이다.

![[Attachments/SLAM/Untitled 4.png]]

**Control point란 위치를 아는 3D point**이다. 초창기에는 몇몇 control point를 이용해 camera pose를 추정하였다. 이제 Bundle Adjustment가 어떻게 동작하는지 알아보자.

# 2. Bundle Adjustment 과정

---

Bundle Adjustment는 카메라 pose와 3D 추정을 위한 Least Squares approach이다. Camera pose 추정과 3D point location 추정을 동시에 진행한다. 

Bundle Adjustment 방법을 정리하면 아래와 같다.

1. 이미지에서 feature point을 추출한다. 3D 공간에 특징점들의 실제 위치를 추정하는 것을 목표로 한다.
    - feature extraction 알고리즘 아무거나(SIFT,SURF,ORB 등) 사용한다.
    - 뽑은 feature points 만을 3D Reconstruction에 이용한다.
2. 6-DoF camera pose와 3D points들의 위치의 초기값을 정한다.
    - Non-linear squares 방법을 사용하기 때문에 초기값(Initial guess)이 존재해야 한다.
3. 3D points들을 가정한 camera pose에 투영(projection) 시킨다.
    - 3D points들을 이미지로 투영 시키면 이미지 상에 투영된 point들이 어느 위치에 있는지 알 수 있다.
4. 이미지에 투영된 point들의 위치와 실제 Measurement(feature extraction 알고리즘을 사용하여 측정된 points)들의 위치를 비교해 Reprojection error를 정의한다.
5. Reprojection error를 줄이기 위해 Non-linear squares 방법을 사용한다.
    - 오차가 작을수록 가정한 Camera pose와 3D points location이 잘 추정된 것이다.

BA 수식을 보기 전에 Image projection 수식은 다음과 같다.

![[Attachments/SLAM/Untitled 5.png]]

이제 BA의 수식을 보자.

![[Attachments/SLAM/Untitled 6.png]]

- $\hat{X}_{i}$ : point의 3D location (homogeneous coordinate)
- $\hat{x}_{ij}'$ : 2D 이미지에서 추출한 feature point
- $\hat{v}_{x_{ij}'}$: $\hat{X}_{i}$와 $\hat{x}_{ij}'$의 오차값
- $\lambda$ : scale factor
    - 실제 이미지만으로는 거리를 알 수 없으므로 homogeneous object(3D)에서는 필요
    - 거리가 두 배가 되어도 같은 이미지 픽셀에 projection 된다. 이를 나타내주는 factor 이다.
- $i$ : 3D points 중에서 $i$번째 point
- $j$ : $j$번째 이미지의 ID
- $\hat{P}_j$ : projection mtx
    - $x_{ij}, p, q$ : Direct Linear Transform으로부터 찾은 projection parameter

수식에서 RHS는 투영한 point고, LHS는 실제 관측한 point에 오차를 더한 것이다.

projection matrix $\hat{P_j}$ 및 scale factor $\hat{\lambda}_{ij}$를 활용해서 3D point $\hat{X}_{i}$를 이미지에 투영시키고, 실제 이미지에서 추출한 feature point $\hat{x}_{ij}'$ 그리고 그 둘의 픽셀 단위 오차값 $\hat{v}_{x_{ij}'}$을 활용해서 식을 정의했다.

Uncertainty in the image coordinates란 각 사진의 픽셀에 대해 feature point를 얼마나 정확하게 추출했는지 나타내기 위한 값이다. 가능하다면 Correlation도 구한다.

이 과정을 수행할 때는 **Known Data association을 가정한다.** Known Data association이란 3D point $\hat{X}_{i}$를 이미지에 투영시켰을 때, 어떤 feature point $x'_{ij}$와 매칭이 되는지 알고 있다는 것이다. Data association을 확실하게 알고 있어야 Bundle Adjustment도 잘 수행되기 때문에 정확한 Data association을 찾는 것이 굉장히 중요하다.

**위 수식에서의 unknown parameters는 아래와 같다.**

![[Attachments/SLAM/Untitled 7.png]]

- $\hat{X}_i$ : 새로운 point의 3D location (x,y,z)
- $\hat{\lambda}_{ij}$ : 1D scale factor
- 6D exterior orientation (extrinsic parameter, 카메라 projection center의 3D location+camera가 바라보는 roll, pitch, yaw 담은 6DoF)
- $p$ : 5D projection parameters (intrinsic parameter)
- $q$ : Non-linear distortion parameters (Non-linear error 표현하는 potential error)

3D point 하나 당 15개의 파라미터가 필요하다. 파라미터 수가 많으면 H, b mtx가 매우 커지고 연산량이 늘어난다. $\Delta x=-H^{-1}b$ 에서 H mtx의 역행렬을 구하는 것이 매우 cost가 높은데, H mtx가 sparse 하다는 성질을 이용해 Shur decomposition 등을 이용하면 쉽게 역행렬을 구할 수 있다. Sparsity에 대해서는<4-1. Graph-Based SLAM>의 2-3을 참고하자. 이때 자신의 상황에 맞게 미지수의 개수를 제한 하는 것도 가능하다. 예를 들어 camera calibration을 통해 내부 파라미터를 알고 있다면 projection parameter는 알아내지 않아도 된다.

<aside>
💡 **Known Data Association**

⇒ world의 모든 point를 알고 카메라의 어디에 mapping 되는지 알기 때문에 $X_i$는 unique하게 찾아진다.

</aside>

## [SLAMDUNK에서 소개한 BA 방법]

우선, **3D point는 2D로 어떻게 전환될까?**

![[Attachments/SLAM/Untitled 8.png]]

즉, frame1, frame2 만을 가지고 카메라의 모션의 R, t를 추정할 수 있는지에 대한 문제로 재정의할 수 있다.

(2)에서 Gz로 나누는 이유는 아래와 같다. O에서 (a, b)와 (x, y)를 봤을 때 y=1에 맺히는 위치는 기울기인데 이는 3차원에서 z에 대해 나눈 것이다. (3)에서 fx, fy는 픽셀 단위이다. ux=Gx/Gz일 뿐이므로 fx를 이용해 픽셀 위치를 구한다. 

![[Attachments/SLAM/Untitled 9.png]]

카메라의 이동, point의 이동은 아래와 같이 나타낸다. 우리가 알고 있는 **3D point에 외부 파라미터와 내부 파라미터를 곱해 pixel plane으로 전환**한다. 로드리게스 회전은 축을 중심으로 어느 정도 회전이 일어나는지 알려준다.

![[Attachments/SLAM/Untitled 10.png]]

카메라 내부 파라미터에는 focal length($f_x, f_y$) 이외에 카메라와 렌즈 특성 때문에 생기는 추가적인 왜곡이 있다.

- $skew_{-}cf_x$ : ideal한 정사각형이 아니라 삐뚠 평행사변형. 최근 카메라에는 없다.
- $f_x, f_y$ 가 다른 경우 : 센서의 가로 세로 크기가 다른 경우
- $C_x, C_y$ : 상이 센서 중앙에 맺히지 않는 경우
    
    ![[Attachments/SLAM/Untitled 11.png]]
    
- Radiation Error
    
    원래는 네모나게 나타나는 이미지가 둥글거나 오목하게 나타나는 현상을 수학적으로 나타낸 것으로, camera calibration은 이러한 파라미터를 알아내는 것이다.
    
    ![[Attachments/SLAM/Untitled 12.png]]
    

이제, 그림 두 장으로 카메라의 움직임을 계산해보자.

![[Attachments/SLAM/Untitled 13.png]]

(2)는 feature extraction 과정, (3)은 correspondende 찾는 과정, (5)는 최초의 initial guess이다. (6)에서는 control point를 포함할 수도 있다. (1)~(6)의 과정에서 에러가 발생하면 앞의 에러가 BA까지 전파된다.

**즉, 알고 있는 3D 포인트가 있으면 R과 t로 얼마든지 reprojection이 가능하다.**

## 2-1. Example of Bundle Adjustment

---

![[Attachments/SLAM/Untitled 14.png]]

10000장의 이미지가 있고, 한 이미지당 1000개의 feature point을 추출한다고 가정하자. 3D point 하나는 평균적으로 10장의 이미지에서 관찰이 된다.

**우선 observation의 크기는 얼마나 될까?** 모든 이미지의 모든 feature point에 2D(x,y) 정보가 존재하고, 총 10000장의 이미지, 한 장당 1000개의 특징점이 있으므로, observation의 크기는 2*10000*1000 =20000000(=20M)이다.

**구해야 하는 unknown parameters는 몇 개일까?** 1000개의 특징점에 대한 3DOF (3*1000), 10000개의 scale factor, 10000개의 카메라에 대한 6DoF (하나의 카메라로만 이미지를 취득했을 경우 intrinsic parameter는 고정)를 모두 합한 값이다. 따라서 약 13000000(= 13M)정도 parameter들을 알아야 한다. (실제로 mapping 해야하는 포인트 = 1M)*(각 포인트는 3D 벡터)+(각 이미지의 각 포인트 당 $\lambda$ = 10M)+(각 이미지 마다 orientation=10k(6DoF))

우리가 구해야 하는 parameter의 수를 줄이기 위해서 **scale factor를 제거하는 방법**을 사용한다. Homogenous coordinates를 사용하는 대신에 Euclidean coordinates를 사용하는 방법으로 scale factor를 제거할 수 있다. (모든 것을 homogeneous 좌표계로 표현했기 때문에 $\lambda$ 사용했지만 현실에서 $\lambda$는 필요없다. 유클리디안 공간에서 포인트의 xy 좌표, 카메라의 3D 위치 벡터, 카메라의 3D 회전 파라미터만 고려하면 된다.) 그 결과 약 13000000(= 13M)정도 parameter들을 3000000(=3M)정도로 줄일 수 있다.

![[Attachments/SLAM/Untitled 15.png]]

우리가 구해야 하는 parameter를 알았으면 이제 **Least squares 방법을 사용**한다.

![[Attachments/SLAM/Untitled 16.png]]

여기서 $A$는 Jacobian Matrix, $\Sigma$는 covariance matrix 로 나타내였고, 우리가 찾아야 하는 unknown parameters를 $x$, observations를 $l$로 표기하였다. 위 수식에는 많은 parameter가 존재하기 때문에, 실제로 Bundle Adjustment를 사용할 땐 조금 더 효과적인 방법을 사용하는데, 그 방법에 대해서는 5-2에서 다룬다. 여기서는 일단 parameter를 알고 있다고 가정한다.

## 2-2. MATLAB 코드

---

![[Attachments/SLAM/Untitled 17.png]]

이 경우 R 없이 t만 했는데, 실행시키면 J의 랭크가 일부 없어지며 추정이 불가하다. (t나 R만 하는 경우 자코비안의 Rank가 없어지는 경우가 있다.)

![[Attachments/SLAM/Untitled 18.png]]

→ **[Levenberg]** 따라서 예전에 했던 것처럼 작은숫자*I를 더해 랭크가 사라지지 않도록 하는 trick을 사용한다.

![[Attachments/SLAM/Untitled 19.png]]

→ **[Levenberg-Marquardt]** 또한 곡면의 기울기까지 더하여 계산하면 더 좋은 결과를 얻을 수 있다. 

![[Attachments/SLAM/Untitled 20.png]]

![[Attachments/SLAM/Untitled 21.png]]

아래 그림에서 왼쪽이 Levenberg, 오른쪽이 Levenberg-Marquardt 방법의 결과이다. (15회 iteration)

![[Attachments/SLAM/Untitled 22.png]]

## 2-3. Bundle Adjustment의 장점, 속성

---

**BA의 장점은 다음과 같다.**

- **statistically optimal solution**이다.
    
    Image projection 과정이 non-linear 하기 때문에 Gauss-Newton이나 Levenberg-Marquardt 최적화와 같은 non-linear 최적화 기법을 사용해야 한다. LS form으로 최적화 문제를 설계하고 모든 입력 데이터가 Gaussian 분포를 따른다면 최적화 문제는 MLE(Maximum likelihood estimation)이 된다. 즉 최적화 문제의 해가 statistically optimal 하다.
    
- Straight forward 방법, DLT, P3P, 5/8 point보다 **control point가 적게 필요하다.**
- 기법 상 5/8 point 알고리즘은 카메라의 모션이 어느 정도 있어야 잘 추정되지만, BA는 iteration 기법이므로 **두 개의 카메라 모션이 적을 때 더 잘 수렴**할 것으로 생각 된다.
- **연속적으로 적용 가능하다.**

**최적의 해를 찾기 위해서는**

- Data association을 잘 수행해야 하고, 이에 대한 uncertainties, correlation도 잘 고려해야 한다.
- Gaussian noise model을 따라야 한다.
- 초기값(initial guess)을 잘 찾아야 한다.
- orientation, calibration parameter, point location을 높은 정확도로 계산해야 한다.

# 3. Bundle Adjustment에서 고려해야 할 것들

---

우리가 카메라 이미지만으로 3D reconstruction을 진행하면 “photogrammetric model”을 얻을 수 있는데, 이는 정확한 scale값이 고려되지 않은 값이다. 따라서 scale까지 고려된 정확한 3D modeling을 수행하려면 몇 가지 추가적인 정보가 필요하다.

## 3-1. Absolute Orientation Through Control Points

**Absolute Orientation은 3D points의 집합을 정합할 때 Scale까지 고려해 Transformation을 결정하는 문제이다.** Control Points 정보를 Bundle Adjustment를 수행하는데 추가하면 실제 scale까지 고려하여 3D reconstruction을 진행할 수 있게 된다. 따라서 Absolute Orientation  문제를 풀기 위해서는 Control Point가 필요하다.

<aside>
💡 **Control Point**
**실제 3차원 공간에서 points들의 실제 위치를 아는 점**이다. straight forward 방법에서는 in condition을 방지하는 데 사용하고 이 강의의 BA에서는 주로 **scale 추정**에 사용한다. 비콘 등을 사용하여 알아낸다.

</aside>

그렇다면 이 Control Points를 어떻게 알 수 있을까? 또한 Control Points들을 구할 때 Noise가 있다고 가정해야 할까? 아니면 Control Points의 값을 그대로 믿고 쓰면 될까?

이는 우리가 어떤 것에 관심 있는지(=Objective function에 따라)에 따라 달라진다. Bundle Adjustment를 수행하는 초반에는 Control Points를 Noise가 있다고 가정하고, Outlier를 제거한 다음에는 남아있는 Control Points들을 고정하고 Bundle Adjustment를 수행한다.

![[Attachments/SLAM/Untitled 23.png]]

<aside>
💡 **Objective function에 따라서,**

(1) contol point 포함해 모든 point를 다루는 statistically optical solution 구하는 경우, 현실에서 실제 noisy 하므로 control point도 noisy 하다고 해야 한다.

(2) control point가 고정되어 있다 = enforcing geometry on BA sol = 특정 point는 움직이지 않고 고정해있다는 constraint 생성 = model 만들고 이를 some official map과 합치는 등 잘못된 정보 보정 가능

</aside>

**그렇다면 얼마나 많은 Control Points가 필요할까?**

강의에서는 Bundle Adjustment는 최소 3개의 Control Points가 필요하다고 한다. 고정되어야 할 7DoF가 있고 모든 포인트는 3D이기 때문이다. 이는 3~6개가 필요한 Direct Linear Transform 방법이나 P3P solution보다 훨씬 적은 수인데, 이는 Bundle Adjustment가 statistically optimal solution이라는 특징이 있기 때문이다.

만약 scale을 고려하지 않고 3D reconstruction을 수행할 경우, Control Points는 없어도 된다.

## 3-2. Initial Guess

Bundle Adjustment는 Least squares 방법으로 최적화를 수행하기 때문에 초기값은 필수이다. 그렇다면 어떻게 초기값을 얻어낼까? 이미지 쌍을 이용한 Direct method 방법을 사용한다.

**Direct method 방법이란 초기값 없이 Orientation을 구하는 방법**을 이야기 한다. N개의 이미지들에 대한 Direct solution은 아직 없기 때문에 이미지 쌍으로 쪼개서 초기값을 구하는 방법을 생각해볼 수 있다. 8 points algorithm 이나 5 points algorithm으로 카메라와 관련된 Rotation matrix $R$, translation vector $t$를 얻은 후, P3P 또는 RRS 알고리즘을 활용해 orientation을 구하는 방법이다.

하지만 이 방법을 사용해야 할 경우, 여러 문제점들이 존재한다.

- Outlier, gross error 제거를 잘 수행해야 한다.
- 이미지 쌍들에 대해 충분한 points들이 필요하다.
- 우리가 쓰는 cost function이 Convex 함수(볼록한 함수)라는 보장이 없으므로 local minima에 빠지거나 발산할 수 있다.

<aside>
💡 **Gross Error** : feature 추정 등의 과정 중에 발생
**Outlier** : 센서로부터 발생

</aside>

Outliers/Gross Error를 만드는 요인에는 크게 두 가지가 존재한다.

- Wrong correspondences
- Wrong point measurements

우리는 feature를 잘못 추출하거나,  추출된 feature의 쌍을 잘못 찾거나, 열에 의해 카메라 파라미터가 변형된 가능성도 있다. Wrong correspondences에 대해서 이야기해보자. 우리는 3장 이상의 이미지가 필요하다. 2장의 이미지만으로는 3D 좌표 추정은 가능하지만 수행한 triangulation의 결과가 맞는 값인지 틀린 값인지 비교를 할 수가 없기 때문이다. 따라서 하나의 3D points에 대해 최소 4개의 서로 다른 view가 필요하고 적어도 **5~6장의 서로 다른 view에서 본 이미지 값들이 있을 때 outlier를 판단하고 잘 추정할 수 있다.** 만약 3장이라면, 1-2와 2-3 중 어떤 값이 outlier 인지 모른다.

Outliers를 제거하는 또다른 방법은 **RANSAC 알고리즘**을 활용하는 것이다. 계산량이 더 많이 들지만, 조금 더 정확한 data association 값을 얻을 수 있다. 예를 들어 5 point algorithm에 RANSAC을 결합하여 사용할 수 있다.

## 3-3. Robust Kernels

<4-4>에서 언급했듯이 **Least Squares 방법을 조금 더 Robust하게 만드는 방법 중 하나가 Robust Kernel을 사용하는 것이다.** Bundle Adjustment 방법 역시 Least Squares 방법이기 때문에 Robust Kernel을 적용하여 outlier에 강인하게 Error minimization을 수행할 수 있다.

![[Attachments/SLAM/Untitled 24.png]]

Bundle Adjustment 방법을 수행하는데 여러 가지를 고려해야 하지만, 다양한 software가 있으므로 이를 모두 직접 설계할 필요는 없다. 다만 정확한 Data association을 찾는 것이 엔지니어에게 필수적인 작업이다.

Cyrill 교수님께서 언급하신 Software는 다음과 같다.

- meshroom ([https://github.com/alicevision/meshroom](https://github.com/alicevision/meshroom))
- Photoscan ([https://www.google.com/photos/scan/](https://www.google.com/photos/scan/))
- Pix4D ([https://www.pix4d.com/](https://www.pix4d.com/)

# 4. Quality of the Results

---

Bundle Adjustment의 결과를 어떻게 평가할까? Precision을 다음과 같은 수식(아래)으로 측정 할 수 있다. 이론적으로는 Least squares 방법을 정의할 때 사용한 식(위)을 사용한다. 여기에 variance factor $\hat{\sigma}_0^2$을 곱한 값으로 empirical precision(경험적 정밀도)를 정의한다.

![[Attachments/SLAM/Untitled 25.png]]

![[Attachments/SLAM/Untitled 26.png]]

Notation이 조금 달라 헷갈릴 수 있지만, 결국 unknown parameter ($\hat{x}$)끼리의 불확실성을 정밀도를 측정하는데 사용하는 것이다.

그렇다면 어떤 값이 좋은 precision을 가졌다고 이야기할 수 있을까? variance factor $\hat{\sigma}_0^2$를 통해 precision을 평가하는데, variance factor가 1인 경우 Model이 정확하다는 의미이다. 얼마나 1의 가까운지는 statistical test를 통해 확인 할 수 있다.

직관적으로 이해하면, unknown parameter ($\hat{x}$)끼리의 불확실성이 작으면 높은 정밀도 값이 나오고, 이에 대한 3D Reconstruction 결과를 직접 확인하여 Bundle Adjustment의 결과를 평가할 수 있다는 것이다.

# 5. BA in SLAM

---

SLAM 에서는 다음과 같은 방법으로 BA가 사용된다.

1. **Slidind window optimization**
    
    실시간 SLAM에서 마지막 N개의 keyframe 정보를 기반으로 BA를 수행해 실시간으로 local map + pose 보정
    
2. **Loop Closure**
    
    실시간 SLAM에서 Loop closure detection이 발생하면 loop closure optimization을 다른 thread 에서 비실시간으로 수행하여 loop에 대한 global map + pose 보정
    
3. **Global Optimization**
    
    실시간 SLAM에서 다른 thread에서 global map + pose 보정 (잘 안 쓰임)
    
4. **Global Optimization as post-processing**
    
    SLAM이 끝난 후, 비실시간으로 global map + pose 보정
    

# 6. Summary

---

카메라와 관련된 여러 parameter, scale, 3D points를 unknown parameters로 정의하고 Least squares 방법을 통해 unknown parameters에 대해 최적의 해를 구하는 것이 Bundle Adjustment의 핵심이다.

Statistically optimal solution이기 때문에 Control points가 적어도 최적의 해를 구할 수 있으며, 여러 Least squares 방법과 마찬가지로 초기값을 잘 구하는 것과 Robust하게 함수를 설계하는 것이 Bundle Adjustment 결과에 영향을 미치게 된다.

Bundle Adjustment와 관련된 수식적인 내용은 <5-2>에서 다룰 예정이다.

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 5-1강 (The Basics about Bundle Adjustment) 요약](https://taeyoung96.github.io/slam/SLAM_05/)

- BA

[Bundle adjustment란?](http://www.cv-learn.com/20210313-ba/)