# 4-1. Graph-Based SLAM using Pose Graphs

# 1. Graph-Based SLAM이란?

---

센서에서 raw data를 받아 처리를 하는 부분을 front-end, front-end에서 만든 정보들을 활용해서 최적화를 진행하는 부분을 back-end라고 한다. Graph-Based SLAM은 다음과 같이 구성된다.

- **Front End** : 각 time step마다 pose 추정, pose 간의 관계를 edge로 표현해 그래프 구성
- **Back End** : 그래프 상에 존재하는 pose들을 업데이트 **(오늘 다룰 부분)**

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled.png)

Graph-based SLAM은 문제를 확률 그래프 모델로 모델링한다. Graph는 node와 edge로 구성된다.

- **node**는 특정 시간에서의 로봇 pose(3D or 6D)
- **edge**는 두 node 사이의 transformation(공간적 constraint)를 표현한다.

Graph-base SLAM은 Graph를 만들고, constraint로 구한 에러를 최소화하는 node configuration를 찾는다. 다시 말해, Graph-based SLAM의 목적은 **edge 값들을 활용해서 node 값들을 정교하게 계산**하는 것이다. edge값(constraints)을 이용해서 error function을 만들고 Least squares 접근법을 활용해서 최적화 한다. constraint는 두 pose 간 측정의 불확실성을 내포한다.

최근 SOTA를 찍은 SLAM 알고리즘들을 살펴보면 모두 Graph-based SLAM을 사용한다. Graph를 활용하여 SLAM system 최적화를 진행했을 때의 장점은 다음과 같다.

1. Observation에 대해 유연하게 대처할 수 있고, 관리하기 쉽다.
2. Pose를 활용해서 graph를 만든다면 랜드마크(Land mark) 없이 map을 만들 수 있다.
3. edge들로 node들간의 관계를 표현할 수 있어 pose들의 값에 접근 가능하다.
    
    → loop closure factor 형성 시 전체적으로 pose update 가능
    

## Graph-Based SLAM 이해를 위한 Mobile Robot의 예시

---

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%201.png)

그림처럼 모바일 로봇이 environment를 움직인다고 했을 때, 기준이 되는 특정 시간마다 **로봇의 Pose**를 표현 할 수 있고, pose와 pose 사이를 **Constraints**(두 pose 사이의 관계로, 변하지 않는 로봇의 회전바퀴 수 등으로 설명)을 활용해서 표현할 수 있다.

2D로 가정을 할 때, XY 좌표값과 로봇의 heading point가 robot pose에 대한 정보가 된다. robot pose는 변수로 취급 하지만, constraints는 변하지 않는 상수로 취급한다. 하지만 constraints인 wheel odometry에 불확실성이 있다는 것도 고려해야 한다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%202.png)

로봇이 environment를 돌아다니다가 위와 같이 이전에 방문했던 곳을 재방문하면 **Loop Closing** 과정이 발생한다. 이러한 상황은 SLAM system에서 굉장히 중요한 요소인데, 이전에 지났던 장소를 다시 지나게 되면서 **새로운 pose와 constraints 간의 관계를 만들 수 있다.** 즉, 가상의 constraints를 만들 수 있다.

예를 들어 ICP 알고리즘을 활용해 map point들을 alignmemt하는 과정에서 pose들을 계산할 수 있고, 현재 설명하고 있는 모바일 로봇의 같은 경우 현재 pose에서 내가 원하는 pose까지 얼마나
가야하는지 wheel odometry를 계산할 수 있다.

# 2. Graph-based SLAM 파헤치기

## 2-1. Edge 만드는 방법

---

이 강의에서는 $n$개의 node가 있다고 했을 때 $x=x_{1:n}$으로 node들을 표현하고, i번째 node인 $x_i$는 $i$번째 time에서의 robot의 pose를 의미한다.

Edge는 2가지 방법으로 만들 수 있다. 아래 그림에서 **X는 transformation matrix를 뜻한다.**

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%203.png)

1. **Odometry-Based edge**
    
    Odometry-Based edge는 위 예제에서 설명한 방법과 같다. odometry 정보를 활용해서 $x_i$에서 $x_{i+1}$로 갈 때 constraints를 가지고 edge를 만든다.
    
2. **Observation-Based edge**
Observation-Based edge는 Lidar나 카메라와 같은 센서를 활용해서 로봇이 다른 위치인  $x_i$, $x_j$ 에서 같은 환경에 대하여 observation값을 구하고 observation 값을 겹쳐서  $x_i$, $x_j$ 의 관계를 계산하고 이를 통해 edge를 만드는 방법이다. 예를 들어, 2D lidar 센서를 활용해 observation 값을 얻어내는 방법은 다음과 같다.
    
    $x_i$, $x_j$에서 Laser scan을 활용해 검정색 scan과 파란색 scan 값을 얻은 후, 두 scan값을 겹쳐 $x_i$, $x_j$의 관계를 계산한 값으로 edge를 만든다
    

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%204.png)

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%205.png)

Transformation을 표현할 때는 Homogenous Coordinates를 이용한다. Homogenous coordinate를 활용하면 edge를 하나의 행렬로 비교적 간단히 표현할 수 있다는 장점이 있다. 예를 들어 3차원 공간에서 로봇의 pose를 4x4로 표현하고 pose들의 관계는 역행렬을 활용해서 계산할 수 있다.

<aside>
💡 <Homogeneous coordinates>

n차원을 n+1 차원으로 나타낸다. 예를 들어 3D 공간의 모델링을 4D로 한다.
- HC로 변환(3D → 4D) : $(x,y,z)^T \to (x,y,z,1)^T$
- Backwards(4D → 3D): $(x,y,z,w)^T \to (\frac{x}{w},\frac{y}{w},\frac{z}{w})^T$
- Vector in HC : $v=(x,y,z,w)^T$

- Translation : $T=\begin{pmatrix}
1 & 0 & 0 & t_x \\
0 & 1 & 0 & t_y \\
0 & 0 & 1 & t_z \\
0 & 0 & 0 & 1 \\
\end{pmatrix}$

- Rotation : $R=\begin{pmatrix}
R^{3D} & 0 \\
0& 1 \\
\end{pmatrix}$

</aside>

앞서 설명했다시피 edge는 constraints이다. constraint는 노드 사이의 확률분포에서 나오는 것이므로 edge는 불확실성이 존재한다. 따라서 Information matrix를 활용해서 edge값에 대한 신뢰도를 알려준다. 즉, Information matrix값이 크면 edge 값이 비교적 정확하다는 뜻이고, information matrix값이 작으면 edge 값이 부정확하다는 뜻이다.

## 2-2. Pose graph

---

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%206.png)

현재 graph에서 $x_i$와 $x_j$는 각각 node들을 의미한다. 두 node들을 잇는 edge를 계산하기 위해 ICP와 같은 알고리즘을 사용해서 observation 값을 구한다.
edge에 들어가있는  $<z_{ij}, \Omega_{ij}>$에 대해서 설명해보자.  $z_{ij}$는 observation 값을 통해  $x_i$에서 바라본  $x_j$의 값이다. 이때 불확실성이 있기 때문에 Information matrix  $\Omega_{ij}$를 활용해서 불확실성 정도를 표현한다. cavariance 는 uncertainty의 척도이므로 그 inverse인 $\Omega_{ij}$는 신뢰도를 뜻한다. 즉, z를 형성하는 과정에서 사용한 센서의 신뢰도를 의미한다. 
우리가 Observation을 통해 구한 값이 기존에 node  $x_j$와 차이가 발생하기 때문에, 이에 대한 Error를  $e_{ij}(x_i, x_j)$로 표현하고 이를 최소화 해야 한다. 우리가 최소화 해야할 error function을 수학적으로 쓰면 아래와 같다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%207.png)

이때 Least squares 방법을 활용하여 최적화를 진행한다. $e_{ij}$를 구성하는데 단지 2개의 node들을 활용하면 되기 때문에 변수가 적고, SLAM system에서 각각 node들과 edge들이 독립적이기 때문에 효율적으로 최적화를 진행할 수 있다.

여기서 state vector $x^T$는 다음과 같이 정의한다. $x^T=(x^T_1, x^T_2,x^T_3,x^T_4, \cdots,x^T_n)$

하나의 원소 $x^T_n$는 하나의 node를 의미하고 이는 로봇의 pose에 해당한다.

Error function을 조금 더 뜯어보면 다음과 같다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%208.png)

$Z_{ij}$는 측정값으로, 센서를 통해 $x_i$에서 바라본 $x_j$의 값을 의미하고, $(X_i^{-1}X_j)$는 node에 저장된 값을 활용해서 $x_i$에서 바라본 $x_j$의 값을 의미한다. $Z_{ij}=(X_i^{-1}X_j)$ 일 때 error=0이다. 다시 한 번 언급하면 $Z, X$는 transformation matrix이다.  $x_i^T=[t_x\,\,t_y\,\,\theta]$ 정보를 이용해 tf mtx $X_i=\begin{bmatrix}
R & T \\
0 & 1 \\
\end{bmatrix}$를 만들 수 있다. $t2v$는Transformation to vector라는 함수를 의미한다. 즉, $e_{ij}$는 아래처럼 tf mtx 에서 벡터로 변했다.

$$
\begin{bmatrix}
R & T \\
0 & 1 \\
\end{bmatrix}\overset{\underset{\mathrm{t2v}}{}}{=}
\begin{bmatrix}
T \\
\theta \\
\end{bmatrix}
$$

## 2-3. Gauss-Newton 방법을 활용한 Optimization

---

Graph Optimization은 **Uncertainty(constraint들의 합)를 최소화할 수 있는 pose들의 set $x^*$을 구하는 것**이다. 실제 SLAM 문제에서는 unknown 개수보다 observation 수가 더 많은 Overdetermined system이 된다. 이런 경우 단순한 Linear eqs. 로 풀기는 어렵기 때문에 Lear Square 방법을 사용해야 한다. 단순 Linear eqs. 로 풀기 어려운 이유는 노이즈 등으로 인해 모든 observation을 만족하는 해를 구하기 힘들기 때문이다.

하지만 pose=(x, y, heading)이면 pose와 pose 간의 tf가 Non-Linear 하기 때문에 $x^*$를 바로 구할 수 없다.

따라서 Error minimization을 할 때는 Gauss-newton 방법을 활용한다. 과정을 살펴보면 다음과 같다.

1. Error function 정의
2. Error function 선형화(Linearize)
3. Jacobian을 활용하여 미분값 계산
4. 미분값 0으로 만드는 값 찾기
5. 선형 시스템 해 구하기
6. Iteration을 통해 최적의 값 찾기

하나의 error function은 두 개의 node와 하나의 edge만을 활용해 만들어지기 때문에 우리가 계산한 Jacobian은 sparse하게 값을 가지게 되고 $x_i, x_j$에 대한 값을 제외하면 0의 성분을 가지고 있게 된다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%209.png)

시각화를 위해 0인 성분을 파란색으로, 0이 아닌 성분을 빨간색으로 표현하면 아래와 같다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2010.png)

**Sparse한 Jacobian은 Sparse한 $H,b$를 만들어낸다.** $H, b$는 우리가 선형화할 때 이용하는 값을 의미한다. 그림으로 표현하면 아래와 같다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2011.png)

- $b_{ij}^T$ : $x_i, x_j$에 대응하는 인덱스에 대해서만 0이 아니다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2012.png)

- $H_{ij}$(edge의 coefficient mtx) : $i,j$와 관련된 block들만 0이 아니다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2013.png)

지금까지 하나의 원소에 대해서만 이야기를 했고, 모든 원소를 더하면 아래와 같이 나타낼 수 있다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2014.png)

- $b$ : 모든 node가 constraints 가지고 있으므로 fully dense vector
- $H$ : on-diagonal element는 constraint, off-diagonal element는 loop-closure constraint

Matrix $H$가 sparse하기 때문에 Sparse **Cholesky decomposition, Conjugate gradients** 등 다양한 방법을 활용해서 보다 효과적으로 계산 할 수 있다.

# 3. 1D example of Graph-Based SLAM

## 3-1. 1st 1D example

---

Graph-Based SLAM이 어떻게 pose를 업데이트 하는지(구하는지) 살펴보자.

- noise가 없고, Linear한 observation만 있다고 가정한다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2015.png)

- step1

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2016.png)

- step2

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2017.png)

- step3

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2018.png)

- step4

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2019.png)

즉, **Graph ↔ Matrix,Vector로 매핑** 한다. Back end에서는 여러 방정식의 해를 구한다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2020.png)

## 3-2. 2nd 1D example

---

지금까지 설명한 Graph-based SLAM의 전체적인 방법을 간단한 예로 이해해보자.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2021.png)

위 그림과 같이 node $x_1$에서 node $x_2$까지 로봇이 1m 움직였다고 가정해보자. 따라서  $z_{12}=1$이다.

- 초기값 $x=(x_1\,\,x_2)^T=(0\,\,0)$
- 실제 관측값(1m 떨어져 있다)  $z_{12}=1$
- 얼마나 확실한지 $\Omega=2$
- error 계산  $e_{12}=z_{12}-(x_2-x_1)=1-(0-0)=1$
- $J_{12}=(1\,\,-1)$    ←  $e_{12}$에서 각각  $x_1$,  $x_2$에 대해 편미분
- $b_{12}=e^T_{12}\Omega_{12}J_{12}=(2\,\,-2)$
- $H_{12}=J^T_{12}\Omega_{12}J_{12}=\begin{pmatrix}
2 & -2 \\
-2 & 2 \\
\end{pmatrix}$

$$
\Delta x=-H^{-1}_{12}b_{12}
$$

여기서 주의할 점은 $\Delta x$를 구하려면 $H^{-1}$의 값이 필요한데, $det(H)=0$인 $H$가 있을 수 있다.

이런 상황이 발생한 이유는 상대적인 constraint만 표현하기 때문이다. 이를 해결하기 위해서는 Global coordinates에서 볼 때 기준이 하나 있어야 한다. 즉 $x_1$또는 $x_2$가 어디있는지 알아야 한다.

첫번째 node  $x_1$를 fix하기 위해 constraints를 더해준다. 즉, information을 더함으로써 첫번째 node의 uncertainty를 낮춘다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2022.png)

실제 첫번째 노드를 fix 하는 예제를 보자. fix 시키지 않으면 $|\Delta x_1| \neq 0$ 이 되어 업데이트 하면 아래의 파란색과 같이 첫번째 노드가 움직일 수 있다. 그러나 $H_{11}+1$을 해주면 아래의 빨간색과 같이 $x_i$이 고정된다.

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2023.png)

정리하면 **Global coordinates을 정해주는 것이 중요하고, Global coordinates를 바로 정하지 못할 경우 하나의 node에 대해 uncertainty를 낮춰주어야 한다.**

<aside>
💡 **<Proof>**

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2024.png)

</aside>

# 4. Uncertainty에 대하여

---

지금까지 기본적인 Graph-based SLAM에 대해서 알아봤다. 우리는 이전에 알고 있는 정보(priori)를 활용해서 system을 만들어야 한다.

바로 앞 예제에서도 살펴보았듯 어떠한 variable에 대해선 Fix된 값을 사용해야 한다. (node $x_i$의 global cooridinate에서의 위치 사용 또는 node $x_i$의 Information matrix 값을 조금 더 높게 하여 fix)

이러한 문제를 수식적으로 접근하면, Matrix를 만들 때 해당하는 행과 열을 지우고 최적화를 진행하면 된다. 예를 들어, node $x_0$의 값을 Fix하고 Gauss-newton method를 진행한다고 하면  $H,b$를 만들 때  $x_0$값과 연관된 행과 열을 지우고 부분적인  $H,b$를 만들어 최적화를 진행하는 것이다. 이렇게 되면 고정된 node 을 기준으로 graph optimization이 이뤄질 것이다.

**Uncertainty를 계산할 때는  $H$ matrix를 이용한다.** $H$를 만들 때 covariance matrix의 역행렬인 Information matrix를 이용하므로, $H$의 역행렬이 covariance matrix로 생각할 수 있기 때문이다. 따라서  $H$의 역행렬의 대각 성분을 통해 각각 variables의 uncertainties를 알 수 있다. 지금까지 이야기 했던 것들을 통해 node  $x_i$와 node  $x_j$의 uncertainty를 구할 수 있다.

1. Full Matrix  $H$를 계산한다.
2. node  $x_i$을 기준으로 삼기 위해서  $x_i$의 행과 열을 제거한다.
3.  $x_i$의 행과 열이 제거된 Matrix  $H$의 역행렬을 구하고,  $(j,j)$성분 값을 계산한다.
    
    → $(j,j)$ block은 고정된  $x_i$에 대한  $x_j$의 convariance matrix를 뜻한다.
    

이러한 과정은 **Loop closure**에서 이용할 수 있다.

# 5. Building Linear System

---

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2025.png)

![Untitled](4-1%20Graph-Based%20SLAM%20using%20Pose%20Graphs/Untitled%2026.png)

# 참고 자료

---

Cyrill 교수님 강의

SLAM DUNK Season2 강의

[Slam 4-1강 (Graph-based SLAM using Pose Graphs) 요약 - Taeyoung’s Blog (taeyoung96.github.io)](https://taeyoung96.github.io/slam/SLAM_04_1/)