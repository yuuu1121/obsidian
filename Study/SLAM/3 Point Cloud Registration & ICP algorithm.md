# 3. Point Cloud Registration & ICP algorithm

# 1. ICP(Iterative Closest Point)란?

---

Estimate the transformation to move one cloud so that it is aligned with the other one

= 3D data간의 alignment를 푸는 것

- STEP1 : Data Association
- STEP2 : Transformation 계산

![[Attachments/SLAM/Untitled.png]]

Optimize 방법

1. Point-to-Plane (많이 사용)
    - not SVD method
    - Least Squares method 사용
2. Projective ICP
3. Robust kernels

# 2. Point Cloud Registration이란?

---

Point Cloud Registration이란 **두 Point Cloud를 정합 하는 공간 변환을 찾는 과정**을 말한다. 이는 Mapping을 할 때 매우 중요한 과정인데 Scan matching을 하거나 Scan registration을 진행할 때 동일한 reference frame에서 보았을 때 각각의 Map point들이 일치해야 정확한 주위 환경을 Mapping 할 수 있기 때문이다. 따라서 Point Cloud Registration을 통해 **가장 정합을 잘하는 Rotation Matrix $R$과 Translation Vector** $t$를 찾는 것이 핵심이다.

![[Attachments/SLAM/Untitled 1.png]]

![[Attachments/SLAM/Untitled 2.png]]

$y_n,x_n,C$가 모두 주어져 있으면 Rotation Matrix $R$과 Translation Vector $t$ 를 활용해 두 Point Cloud를 정합할 수 있다. $R$과 $t$에 의해 옮겨진 Point Cloud를 $\bar{x}_n$라고 하자.

![[Attachments/SLAM/Untitled 3.png]]

이때 유클리디안 거리가 최소화 되도록 하는 **$R$과 $t$를 찾는 것이 Point Cloud Registration**이다.

![[Attachments/SLAM/Untitled 4.png]]

상황에 따라 해결법도 달라진다.

1. **두 Point Cloud의 대응관계(Correspondences)를 알 때 (Known Data Association)**
    - SVD Method
2. **두 Point Cloud의 대응관계(Correspondences)를 모를 때 (Unknown Data Association)**
    - ICP with SVD method
3. **Robust한 Least Squares Approaches를 이용하는 방법**
    - ICP with Least Square method

# 3. **Known Data Association**

---

**두 Point Cloud의 one-to-one 대응관계(Correspondences)를 알 때 Rotation Matrix $R$과 Translation Vector $t$ 를 어떻게 찾을까?** Q를 얼마나 rotate, shift 하면 P가 되는지 알고 있다. Orthogonal Procrustes problem이라고 하며, SVD를 이용해 풀 수 있다.

## Direct Optimal Solution with Known Data Association

이 방법은 Absolute Orientation Problem의 special case 이다. Absolute Orientation Problem이란 3D points의 집합을 정합할 때 Transformation을 결정하는 문제이다. Absolute Orientation Problem에서는 Scale parameter도 존재하지만, 여기서는 Scale parameter를 1로 고정하고 계산한다.

$$
\bar{x}_n=\lambda R x_n + t = R x_n + t \,(\lambda=1)
$$

이제 Point Cloud Registration을 푸는 방법을 이야기해보자. **대응관계(Correspondences)를 알고 있을 때는 Initial guess가 없어도, Iterate를 돌지 않아도 완벽한 해(Solution)를 구할 수 있다!**

<aside>
💡 - **Direct** : initial guess가 필요 없다
- **Optimal** : 더 좋은 solution이 없다

</aside>

이를 구하기 위해서는, 

1. Translation 계산 : 두 Point Cloud의 Center of massess(질량 중심)을 일치시키고 이동량 계산
2. Rotation 계산 : SVD(Singular Value Decomposition) 수행

수식으로 표현해보자.

![[Attachments/SLAM/Untitled 5.png]]

- $x_0$ : $x_n$의 weighted mean
- $y_0$ : $y_n$의 weighted mean
- $p_n$ : 가중치 (얼마나 확실한지, 모르면 모든 포인트에 일정하게 할당)

교차 공분산 행렬(Cross Covariance Matrix) $H$를 계산한다.

![[Attachments/SLAM/Untitled 6.png]]

이제 $H$에 대해 SVD를 계산한다.

![[Attachments/SLAM/Untitled 7.png]]

Rotation Matrix $R$은 다음과 같이 계산한다.

![[Attachments/SLAM/Untitled 8.png]]

Translation Vector $t$는 다음과 같이 계산한다.

![[Attachments/SLAM/Untitled 9.png]]

Rotation Matrix $R$과 Translation Vector $t$을 구하여 Point Cloud Registration을 풀었다.

한 장으로 정리하면 아래와 같다.

![[Attachments/SLAM/Untitled 10.png]]

## Why solution used SVD is good?

왜 이 방법이 최적의 해(solution)일까? 우리는 왜 초기값(Initial guess)이 필요하지 않으며 Iterate를 돌지 않아도 완벽한 해를 구할 수 있는 것일까?

우리가 구하는 식을 재정의(Rewrite) 해보자. 우리가 원래 구해야 하는 식은 다음과 같다.

![[Attachments/SLAM/Untitled 4.png]]

이 식을 원점(origin)이 $y_0$인 Local Coordinate System으로 다시 재정의해보자. 이전에 정의한 것과 같이 $y_0$을 아래와 같이 정의 한 후

![[Attachments/SLAM/Untitled 11.png]]

우리가 구해야 하는 식을 아래와 같이 변경하자.

![[Attachments/SLAM/Untitled 12.png]]

이렇게 되면 구해야하는 Translation Vector가 바뀌였다. 다시 Translation Vector를 재정의 해보자.

$\bar{x}_n=Rx_n + t$ 식을 원점 $y_0$을 활용해 이동시키면 $\bar{x}_n-y_0=Rx_n + t-y_0$ 이다.

Rotation Matrix로 우변을 모두 묶으면 아래와 같은 식이 나온다. ($RR^T=I$)

![[Attachments/SLAM/Untitled 13.png]]

새로운 변수 $x_0$을 활용하여 다시 식을 정의해보자. $x_0$은 아까 Weighted mean을 구할 때 쓰던 변수가 아님에 주의하자.

$x_0=-R^Tt+R^Ty_0$이라고 할 때, 우리가 구해야 하는 식을 다음과 같이 쓸 수 있다.

![[Attachments/SLAM/Untitled 14.png]]

그렇다면 우리가 찾아야 하는 변수는 $R,t$가 아니라 $R,x_0$로 변한다.

![[Attachments/SLAM/Untitled 15.png]]

우리가 구해야 하는 식은 2차식인데 이를 행렬로 표현하여 Objective function을 정의한다. Objective function은 최적화시키려는 함수를 의미한다.

Objective function $\Phi (x_0,R)$이라 정의하고 이를 최소화시키는 $x^*_0,R^*$를 구하면 원하는 해를 구할 수 있다.

![[Attachments/SLAM/Untitled 16.png]]

Objective function을 풀어 쓴다.

![[Attachments/SLAM/Untitled 17.png]]

미분 하여 0이 되는 값을 찾자.

![[Attachments/SLAM/Untitled 18.png]]

미분한 식을 0으로 만드는 값을 찾아 정리하면 아래와 같다.

![[Attachments/SLAM/Untitled 19.png]]

이를 정리하면

![[Attachments/SLAM/Untitled 20.png]]

우리는 이전에 $y_0$을 아래와 같이 정의했었는데, 위의 식에 대입하면 우변이 0이 된다.

![[Attachments/SLAM/Untitled 11.png]]

따라서 우리는 아래 식을 얻을 수 있다.

![[Attachments/SLAM/Untitled 21.png]]

이 식을 이용해 $x_0$을 정의해보면 $x_0$은 $x_n$의 weighted mean이다.

![[Attachments/SLAM/Untitled 22.png]]

![[Attachments/SLAM/Untitled 23.png]]

결국 우리가 임의로 정의했던 $x_0$이 $x_n$의 Weighted mean일 때 최적의 해를 구할 수 있다.

동일한 방법을 $R$에도 적용해보자.

Objective function을 관찰하면 $R$에 관한 식은 아래에 빨간색 부분 밖에 없으므로 아래 식만 고려하면 된다.

![[Attachments/SLAM/Untitled 24.png]]

빨간색 부분의 부호가 (-)이므로 이를 최대화하면 Objective function은 최솟값을 가질 수 있다. ($RR^T=I$)

![[Attachments/SLAM/Untitled 25.png]]

좀 더 식을 간편하게 보기 위해

![[Attachments/SLAM/Untitled 26.png]]

이처럼 정의한다. $a_n, b_n$은 열벡터이다. $x_0, y_0$은 이전에 정의했던 Weighted mean값이다. 그럼 식은 다음과 같이 정리된다.

![[Attachments/SLAM/Untitled 27.png]]

이를 trace의 정의를 이용해서 다음과 같이 나타낼 수 있다. $a,b, p$는 열벡터이므로 시그마 취한 값은 스칼라가 되기 때문에 trace 취해줄 수 있다.

$$
R^*=\underset{R}{argmax}\,tr(RH)
$$

위 식에서 나온 $H$는 Cross covariance matrix로 다음과 같이 정의된다.

![[Attachments/SLAM/Untitled 28.png]]

이제 $R$을 최대화하는 $tr(RH)$를 찾으면 된다. 이는 SVD를 이용한다.

![[Attachments/SLAM/Untitled 29.png]]

![[Attachments/SLAM/Untitled 30.png]]

$R=VU^T$라고 정의하자. 그럼 다음과 같은 식을 얻을 수 있다.

![[Attachments/SLAM/Untitled 31.png]]

$D$는 대각행렬이다.

![[Attachments/SLAM/Untitled 32.png]]

대각행렬의 전치행렬은 자기자신이다.

$$
tr(VD^{\frac{1}{2}}D^{\frac{1}{2}}V^T)=tr(VD^{\frac{1}{2}}(VD^{\frac{1}{2}})^T)
$$

$VD^{\frac{1}{2}}=A$라고 정의하자.

![[Attachments/SLAM/Untitled 33.png]]

$AA^T$는 positive definite 이므로 코시-슈바르츠 부등식에 의해 다음을 만족한다. $R'$은 임의의 어떤 Rotation Matrix이다.

![[Attachments/SLAM/Untitled 34.png]]

![[Attachments/SLAM/A1F31F3F-6C4C-414D-B5AC-7359D6208E5D.png]]

이는 아래 식을 의미한다. 여기서 $R'R$는 또 다른 Rotation Matrix를 의미한다.

![[Attachments/SLAM/Untitled 35.png]]

**즉, $RH$ 왼쪽에 어떠한 임의의 $R'$를 곱해도 $tr(RH)$ 보다 더 크지 못하므로, $tr(RH)$이 maximum이다! 따라서 $R=VU^T$일 때 $tr(RH)$가 최대의 값을 가질 수 있고, 결국 Objective function을 최소화하는 $R$은 SVD의 결과로 만들어진 $V,D$를 활용하여 만든 Matrix이다.**

그렇다면 SVD를 활용해 만든 Rotation Matrix가 Unique한 Solution일까?

$rank(H)=3$**이면 $\Phi$를 최소화하는 rotation이 unique하다**. 즉, $H$가 Full rank matrix일 경우 $svd(H)=UDV^T$이고 $D=Diag(d_1,d_2,d_3)$로 쓸 수 있다. 세 원소가 0보다 크면 이를 Unique한 Solution으로 볼 수 있다.

우리는 Objective function을 최소화하는 parameter $R$과 $x_0$를 알고 있으므로, Objective function을 만들 때 정의한 식 $x_0=-R^Tt+R^Ty_0$을 이용하여 Translation Vector를 $t=y_0-Rx_0$와 같이 나타낼 수 있다.

위 과정을 통해 초기값이 없어도 최적의 해를 구할 수 있는 방법을 증명했다! 여기서 행렬의 순서때문에 헷갈리는 상황이 발생할 수 있는데 아래의 슬라이드를 통해 결국 다 똑같다는 것을 말한다.

![[Attachments/SLAM/Untitled 36.png]]

# 4. Unk**own Data Association**

---

**두 Point Cloud의 대응관계(Correspondences)를 모를 때 Rotation Matrix $R$과 Translation Vector $t$ 를 어떻게 찾을까?** SVD를 이용해 ICP를 적용한다.

Unknown Data Association일 때는 Direct하고 Optimal한 Solution이 존재하지는 않는다.

그러나 두 Point Cloud Set(집합)의 대응 관계를 잘 추정(Estimate)하고, 그 후 Rotation Matrix $R$과 Translation Vector $t$를 찾는 방법으로 Point Cloud Registration을 진행한다면 최적의 해를 찾을 수 있다. 이것이 ICP Algorithm이다.

<aside>
💡 **ICP(Iterative Closest Point) Alogorithm**

Point Cloud Registration을 진행할 때 Data Association에 대해서 모를 경우, 대응관계를 추정하고 그 대응관계를 통해 tf를 계산하여 두 Point Cloud를 Align을 하는 과정 중 하나이다. 대응관계를 만들 때는 **가장 가까운 점**을 활용하며 반복적인 과정을 통해 오차를 최소화한다. (=최적의 Ratoation matrix, translation vector를 찾는다.)

</aside>

ICP 알고리즘에서는 Direct로 해를 찾을 수 없어 초기값(Initial guess)을 가정하고 문제를 풀어나간다. Reference frame에서의 point cloud의 위치나 대략적인 대응관계(Correspondences)를 초기값으로 가정한다.

## 4-1. Vanila ICP

**Vanila ICP는 가장 기본이 되는 ICP Algorithm이다.**

Point Cloud Set $x_n,y_n$이 있다고 할 때 ICP 알고리즘의 흐름을 대략적으로 설명하면 다음과 같다.

![[Attachments/SLAM/Untitled 37.png]]

1. Point Cloud $x_n$의 대략적인 대응관계를 초기값으로 설정한다. 보통 $x_n$에서 각각의 point에 대해, 가장 가까운 거리에 있는 $y_n$의 하나의 점과 매칭을 통해 대응관계를 만든다.
2. 대응관계에 따라, SVD를 이용해 Rotation Matrix $R$과 Translation vector $t$를 구한다.
3. $R,t$를 활용하여 다시 $\bar{x}_n=R*x_n+t$으로 만들어 $y_n$과 align 시킨다.
4. $\bar{x}_n$과 $y_n$의 차이를 Error로 정의하고 Error 값이 원하는 Threshold 값보다 적어질 때까지 1~3번 과정을 진행한다.

ICP 알고리즘은 초기에 Point Cloud가 충분히 가까울 때 잘 동작을 한다. Lidar를 활용하여 Point cloud를 뽑아냈을 때, Scan한 Data간의 시간차이가 짧으면 짧을수록 좋다.

**Vanila ICP의 경우 구현이 간단하지만 몇 가지 단점들이 존재한다.**

1. Iteration이 많이 필요할 수도 있다. 즉, iteration과 비례하여 시간이 오래 걸릴 수 있다.
2. 초기 대응관계(Correspondences)를 완전히 잘못 구하거나 나쁜 대응관계(Correspondences)를 이용할 경우 결과가 매우 나쁠 수 있다.

따라서 이러한 단점들을 보완하려는 연구들이 많이 진행되었고, ICP Algorithm은 다음과 같은 내용들에 Focus를 맞추어 연구가 진행되었다.

- 전체 Point Cloud가 아닌 부분적인 Point Cloud (points subset)만 사용
- 또 다른 Data Association 전략을 사용
- 가중치가 부여된 대응관계(Weight the Correspondences) 활용
- Outlier를 제거 후 point pairs를 맞추는 방법

이러한 ICP 알고리즘은 다양한 Performance에 초점이 맞추어져 있다.

- Speed
- Stability (local minimum)
- Tolerance(센서의 uncertainty) : Outlier나 Noise에 robust
- Basic of convergence(Maximum initial misalignment) : initial guess가 잘못되어도 robust 하게 잘 수렴할 수 있는 능력

## 4-2. Sampling을 통한 sub point set 사용

전체 Point Cloud가 아닌 부분적인 Point Cloud (points subset)만 사용한다. Vanila ICP 알고리즘에서는 모든 point를 사용하지만, 계산량이 너무 많다. 따라서 Sampling을 통해서 일부분(subset)의 Point Cloud를 사용하여 ICP 알고리즘을 사용한다.

Sampling을 하는 방법은 다음과 같다.

1. Use all points
2. Uniform sub-sampling
    - 동굴같은 환경에서 유리
3. Random sampling
4. Feature-based sampling
    - Feature를 쉽게 찾을 수 있는 경우 Feature-based sampling도 강력한 방법이다.
    - Full 3D scan과 Feature만 뽑았을 때를 비교하면, 추출된 point의 수가 훨씬 적어졌다(highly distinct points만 사용)는 것을 알 수 있고, 계산량적인 측면에서 ICP 알고리즘을 훨씬 개선시켰다고 이야기할 수 있다.
    - 대응관계(correspondences)를 찾는데 훨씬 간소화할 수 있고, Feature들이 잘 뽑혔다고 가정할 때 높은 효율성과 때로는 높은 정확도까지 보일 수 있다.
    - preprocessing 필요
    
    ![[Attachments/SLAM/Untitled 38.png]]
    
5. Normal-space sampling
    - 복잡한 feature 환경에서 유리
    - 각도 성분에 대해 균일하게 sampling
    - large smooth surface with only small variation 환경에 적절하다.
    - Uniform vs. Normal-Space Sampling
    
    ![[Attachments/SLAM/Untitled 39.png]]
    
    Uniform sampling은 간격이 균일하게 sampling을 하는 반면, Normal-space sampling은 굴곡진 부분에 대해서 조금 더 많은 sampling을 하는 것을 확인할 수 있다. Normal-space sampling 방법은 Smooth한 지형에서 조금씩 보이는 curvture나 조그마한 object가 붙어 있는 경우 sampling 하고 point cloud registration을 하는데 효율적인 방법이다.
    
    - Random vs. Normal-Space Sampling
    
    ![[Attachments/SLAM/Untitled 40.png]]
    
    Random sampling과 비교를 했을 때도 Normal-space sampling이 굴곡진 부분에 대해서 Alignment를 더 잘 수행했다.
    

## 4-3. 또 다른 Data Association 전략

Data Association을 잘 찾으면 우리는 Optimal한 Solution을 쉽게 찾을 수 있다. 따라서 Data Association을 잘하는 것이 ICP 알고리즘의 결과(속도, convergence 등)에 엄청난 영항을 미친다.

Vanila ICP 알고리즘에서는 가장 가까운 point를 활용해서 Data Association을 구축했지만, 이 방법이 잘 통하지 않는 환경도 존재할 것이다. 따라서 수많은 Data Association 방법이 제안되었다.

1. **Closest point**
    
    Vanila ICP 알고리즘에서도 사용을 하는 Data association 방법이다. 가장 가까운 점을 찾을 때 KD tree와 같은 구조를 사용하기도 하며, 간단한 방법이지만 오차를 최소화 하기 위해 수렴(Convergence)을 할 때 굉장히 많은 Iteration을 돌아야 한다.
    
    Closet point 방법으로 Data association을 하기 위해서는 초기값(Initial guess)을 알아야한다.
    만약 초기값을 알 수 없을 경우, 질량 중심(Center of mass)을 이용하여 두 Point cloud를 이동 시킨 후, 가장 가까운 point들을 활용하여 대응관계를 만든다.
    
    안정적지만, 느리다.
    
2. **Closest compatible point**
    
    설명할 수 있는(Compatible) Point를 사용하여 Data association을 하는 방법이다. 보통의 points들은 (x,y,z) 좌표를 가지고 있는데 depth, stereo camera를 활용하거나 Camera-LiDAR fusion을 할 경우 point에 여러 정보들이 추가될 수 있다.
    
    color, normal, curvature, high-order derivatives, other local features 등등 points를 설명할 수 있는 정보들을 활용하여 Data association을 만들어 조금 더 효율적으로 ICP 알고리즘을 수행할 수 있다. feature-based sampling과 비슷하다.
    
3. **Normal shooting**
    
    한 point에서 Normal vector를 구하고 그 방향과 만나는 또 다른 Point set에서의 점을 활용하여 Data association을 하는 방법이다. Smooth한 평면에서는 굉장히 유용한 Data association 방법이지만, Noise가 많거나 곡선이 많은 복잡한 환경에서는 좋지 않을 수 있다.
    
    ![[Attachments/SLAM/Untitled 41.png]]
    
    단순한 구조에서는 closet point 보다 좋지만, 복잡한 구조나 scanning noise가 심하면 closest point 보다 좋지 않다.
    
4. **Projection-based approaches**
    
    Point cloud를 RGB-D camera와 같은 센서에 Projection 시켰을 때, 서로 같은 점에 projection이
    된 Point들을 대응시켜 Data association을 하는 방법이다.
    
    ![[Attachments/SLAM/Untitled 42.png]]
    
    Nearest neighbor search를 단순화한 것이다. 반복할수록 조금씩 결과가 안 좋아진다.
    
5. **Point-to-plane (최근 가장 많이 사용)**
    
    앞서 소개한 방법은 Point와 point를 Direct하게 이어서 유클리디안 거리를 만들었다면, Point-to-plane은 source point에서 Target point를 Direct하게 잇는 것이 아니라, Target point의 점과 점 사이에 있는 가상의 평면(또는 직선)을 만들고 Normal vector를 구해 가장 가까운 점을 고르고 유클리디안 거리를 계산하여 Data association을 만드는 방법이다.
    
    ![[Attachments/SLAM/Untitled 43.png]]
    
    LiDAR의 경우 거리가 커지면 sparse해진다. **point-to-point는 이러한 uncertainty를 반영하지 못하므로 적당한 initial guess를 할 수 없다.**
    
    가장 가까운 target의 point d에서 plane을 만들고 source의 point s에서 법선에 내린다(l).
    
    ![[Attachments/SLAM/Untitled 44.png]]
    
    Point-to-plane 방법은 최소화해야하는 함수 또한 조금 달라지는데, **Normal vector를 내적시킨 값을 최소화** 시킨다고 이해할 수 있다.
    
    ![[Attachments/SLAM/Untitled 45.png]]
    
    **Point-to-plane 방법은 최근 ICP 알고리즘을 사용하는데 가장 유용하게 사용하는 Data Association 방법이다!**
    

## 4-4. 가중치가 부여된 대응관계 활용

Point의 쌍을 만들 때, Points들의 신뢰도에 따라서 weight를 부여하는 방법이다. 신뢰도가 높은 pair에 더 높은 weight를 준다. 보통 사용하는 센서에서 나온 값이 불확실한 경우 weight를 사용하여 얼마나 noise가 있는지 알 수 있도록 한다. 이미 우리는 앞서 ICP 알고리즘 및 Point cloud registration을 설명할 때, weight의 개념을 사용하였다.

![[Attachments/SLAM/Untitled 46.png]]

## 4-4. 잠재적인 Outlier Pairs 제거

Outlier를 제거 후 point pairs를 맞추는 방법이다. 좋은 Data Association은 곧 ICP 알고리즘의 결과에 영향을 미친다. 따라서 Outlier pairs를 제거하는 것이 ICP 알고리즘 결과에 크게 영향을 주고
이를 제거하려는 연구들이 많이 진행되었다.

간단히 생각해볼 수 있는 방법은 Point끼리의 유클리디안 거리가 일정 Threshold를 넘을 경우,
Outlier pairs로 생각하고 이를 제거해주는 방법이다. 하지만 얼마나 miss-alignment 된 것인지는 모르기 때문에 threshold 찾는 것이 heuristic한 문제이다.

![[Attachments/SLAM/Untitled 47.png]]

또 다른 방법은 인접한 Points에서 대응관계로 묶인 Points들의 거리가 크게 차이가 난다면 Outlier pairs로 생각하고 이를 제거해주는 방법이다. 이 방법에 따른다면 아래 그림에서 왼쪽 대응관계가 Outlier pair로 판명될 것이다.

![[Attachments/SLAM/Untitled 48.png]]

이 방법을 발전시켜 가장 대응관계가 나쁜 $t$%를 제거하고 ICP 알고리즘을 수행하는 방법이 제안되었는데, 이를 **Trimmed ICP**라고 부른다. 여기서 $t$를 지정해주는 것 또한 하나의 문제인데, 주로 얼마나 Outlier가 많을 것 같은지 얼마나 많은 Points들이 Overlap 됐는지에 따라 결정된다.

마지막으로 조금 더 일반적인 방법으로 Outlier를 제거하고 싶다면 **RANSAC, sampling based, kernel function with robust optimization**을 활용하는 방법도 있다. Kernel function을 활용하게 된다면 잠재적으로 큰 에러 값에 대해 적은 영향을 받도록 할 수 있다.

이런 Outlier를 제거하는 방법은 ICP 알고리즘 뿐만아니라, “Moving object segmentation”과 같은 다양한 분야에서 활용될 수 있다.

## 4-5. ICP 알고리즘 최종 정리

1. 정합을 하기에 좋은 Point cloud를 Sub-sampling을 진행한다.
2. Points들의 대응관계를 결정한다. (상황에 따라 맞는 대응관계를 채택)
3. Robust한 성능을 보이기 위해, 가중치를 부여하거나 Outlier의 후보군을 제거한다.
4. 알고리즘을 활용하여 Rotation Matrix 과 Translation vector 를 구한다.
5. 모든 점에 대해서 Rotation Matrix 과 Translation vector 를 구한다.
6. Error 값을 구한다.
7. 일정 Threshold보다 Error가 작아질 때까지 반복한다.
8. 최종적인 Alignment를 만들어낸다. 

# 5. **Robust Least Squares Approaches**

---

**Robust한 Least Squares Approaches로 Rotation Matrix $R$과 Translation Vector $t$ 를 어떻게 찾을까?** Least Square method를 이용해 ICP를 적용한다.

이 방법은 SVD 알고리즘을 사용할 수 없을 때 사용할 수 있다. SVD로 푸는 방법보다 Least squares 접근 방법으로 푸는 것이 어떤 장점이 있을까?

1. SVD solution은 point-to-point correspondences를 가정한다.
2. Error function이 복잡해지면 Least squares 접근 방법이 요구된다.
3. 불확실성(Uncertainties)에 대해서 더 좋은 결과를 보인다. (Robust하다.)
4. Alignment를 진행할 때 서로 다른 Weight를 활용하여 Alignment를 더 잘 할 수 있다.

그렇다면 어떠한 방식으로 Least squares를 사용해서 Point cloud registration이 되는지 2D point-to-point registration을 통해서 이해해보자

## 2D point-to-point registration

우리가 결국 구해야 하는 것은 Rotation matrix $R$과 Translation vector $t$이다. SVD를 사용하는 것이 아닌 Gauss Newton Minimization을 사용하여 최적화를 진행해보자.

우선 사용한 수식은 아래와 같다.

![[Attachments/SLAM/Untitled 49.png]]

- $t_x$ : x로의 translation
- $t_y$ : y로의 translation
- $\theta$ : rotation angle

위 식에서 우리가 사용하는 error function은 Rotation Matirx에 Sine과 Cosine에 관한 값이 들어가 있기 때문에, Non-linear한 error function이라고할 수 있다. 따라서 이를 선형화해주는 작업이 필요하다.

Gauss Newton Method에서 했던 것과 마찬가지로 먼저 1차 미분에 대한 식을 구하기 위해 Jacobian을 알아야 한다. 여기서 Jacobian의 형태는 2x3 행렬이다. 2는 x성분 y성분을 의미하고 3은 parameter의 갯수 ($t_x, t_y, \theta$)를 의미한다. Jacobian에 대한 식은 아래와 같다.

![[Attachments/SLAM/Untitled 50.png]]

![[Attachments/SLAM/Untitled 51.png]]

맨 마지막 행렬의 $x_n, y_n$은 Error function에 있는 $x_n$의 성분을 x성분과 y성분으로 나누어서 쓴 것이니 주의하자.

<aside>
💡 **Remark**

![[Attachments/SLAM/Untitled 52.png]]

![[Attachments/SLAM/Untitled 53.png]]

</aside>

다음은 Gauss Newton Method를 이용해서 최적의 해를 구하는 과정을 거친다. Gauss Newton Method를 사용하기 위해서 $H,b$값을 구해준다. $H,b$의 의미는 $x$를 선형화를 할 때 $x=x+\Delta x$값으로 구하게 되는데 $\Delta x$만을 변수로 $x$를 상수로 봤을 때, $\Delta x$에 대한 이차식을 행렬로 표현한 것이 $H$, 1차식을 벡터로 표현한 것이 $b$이다.

위에서 구한 Jacobian을 이용하여 필요한 $H,b$를 구하는 식과 Gauss Newton Method를 쓴 방법은 강의자료에 아래와 같이 나와있다.

![[Attachments/SLAM/Untitled 54.png]]

이 방법을 사용하여 최적화를 진행하면 어떻게 될까? **SVD based method와는 다르게 매 step(또는 iteration)마다 Correspondence가 달라질 수도 있다!**

## Least Squares Registration using Point-to-Plane Metric

위와 같은 Least Squares Method는 기본적으로 Point-to-point metric을 사용했다. 위에서도 설명했듯이, data association을 진행할 때 Point-to-plane association 전략이 point-to-point보다 좋은 성능을 보이고 있기 때문에 최근 data association은 대부분 point-to-plane metric을 사용한다.

따라서 Point-to-plane을 least squares method에 사용해보자. error function은 아래와 같다.

![[Attachments/SLAM/Untitled 55.png]]

Normal vector $n_n$을 구할 때는 Eigenvalue와 eigenvector가 활용되거나, 외적을 활용한다.

Error function이 달라졌기 때문에 Jacobian도 당연히 달라진다. 달라지는 형태는 아래 강의자료에서 확인할 수 있다. Error fuction을 구할 때, 벡터의 내적이 활용되므로 최종적인 형태는 1x3형태의 vector임을 주의하자.

![[Attachments/SLAM/Untitled 56.png]]

- $n_x$ : 법선 벡터의 x component
- $n_y$ : 법선 벡터의 y component

Jacobian을 구하면 아까 Gauss Newton method를 진행하기 위해 구했던 $H,b$를 구하고 동일한 과정을 거쳐 최적의 값을 찾으면 된다.

여기서 Point-to-plane 기반의 방법을 사용할 때 주의할 점은 결과값이 대칭(symmetric)이 아니라는 것이다! 말을 풀어서 설명하자면 Point cloud $x$를 $y$에 대해서 registration을 계산한 결과와 Point cloud $y$를 $x$에 대해서 진행한 결과 값이 달라진다는 것이다. 즉, 기준에 따라 결과 값이 다르게 나올 수 있다. 왜냐하면 Normal vector값이 달라지기 때문이다.

따라서 Noraml vector를 구할 때, $x$에 대한 Noraml vector 성분과 $y$에 대한 Noraml vector 성분을 더하는 과정을 거쳐 대칭이 안되는 문제를 해결하려 한다. 이러한 방법을 **Symmetric Point-to-plane** 방법이라고 한다. Noraml vector를 각각 구하는 과정이 있어야 하지만 성능이 확실히 좋아졌다고 한다.

![[Attachments/SLAM/Untitled 57.png]]

## Robust Least Squares

SVD based method나 Least squares method나 Robust하게 만드려면 결국 Data association을 잘해야 한다. Outlier를 제거하기 위해 Robust한 kernal을 사용하거나 / M-estimator같은 것들을 사용한다. 이러한 Kernal을 만드는 연구도 활발히 진행중인 것 같다. 또한 Heuristics한 방법이나 초기화를 잘 해서 outlier를 제거하려는 노력도 많다.

지금까지 강의에서 나온 내용을 정리하면 다음과 같다.

- Initial guess는 중요하다! (odometry나 constant velocity로 제공)
- Point-to-plane 방법이 point-to-point보다 성능이 좋다.
- Point-to-plane 방법을 사용할 때, Symmetric metric을 사용하면 성능이 더 올라갈 수 있다.
- Outlier을 제거하려는 노력이 중요하다.

Cyrill 교수님의 경험에 의해면 Point cloud에 uncertainties가 존재할 때, 현재 설명한 Point cloud registration 방법은 결과가 좋지 않다고 말씀하셨다. 따라서 Point cloud값이 확실할 때 이러한 방법들을 사용해야한다. Lidar SLAM을 할 때는 ICP를 많이 활용하지만, Visual SLAM의 경우 그렇지 않은데 아마 point cloud의 uncertainties 때문이지 않을까?

## Non-Rigid Registration

지금까지는 Rigid body일 때 point cloud registration을 하는 방법에 대해서 알아봤다. 하지만 물체가 Non-rigid일 경우는 어떻게 달라질까? 예를 들어 움직이는 사람을 Point cloud registration을 진행하거나 시간에 따라 길이가 변하는 식물을 Point cloud registration을 진행하려면 어떻게 할까?

심화 내용이기 때문에 방법만 나열은 해보면 다음과 같다.

- Skeleton Deformation을 활용해서 Data association을 만든다.
- 시간축을 기준으로 Interpolation을 진행한다.
- 좀더 정교한 Data associaton 방법을 활용한다

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 3-1강 (Point Cloud Registration & ICP algorithm) 요약](https://taeyoung96.github.io/slam/SLAM_03_1/)

[Slam 3-2강 (ICP algorithm & Unknown Data Association) 요약](https://taeyoung96.github.io/slam/SLAM_03_2/)

[Slam 3-3강 (ICP & Point Cloud Registration - Non-linear Least Squares) 요약](https://taeyoung96.github.io/slam/SLAM_03_3/)

- ICP 코드 주피터 노트북

[Notebook on nbviewer](https://nbviewer.org/github/niosus/notebooks/blob/master/icp.ipynb)