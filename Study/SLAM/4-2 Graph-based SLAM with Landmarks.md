# 4-2. Graph-based SLAM with Landmarks

# 1.The graph with Landmarks

---

간단히 Pose graph SLAM에 대해서 이야기해보면, graph를 활용해서 SLAM의 문제를 해결하려는 방법이다. 모든 node는 로봇의 pose를 의미하고, 모든 edge는 node들 사이에 observation값을 표현하고 constraints이다. 하지만 edge에도 불확실성이 있기 때문에 이를 잘 판단하여 최적화를 진행해줘야 한다. 불확실성은 Covariance matrix를 통해서 판단했다.

<4-1. Graph-Based SLAM using Pose Graphs> 에서는 로봇의 pose만을 node로 생각하고 최적화를 진행했다. **Landmark-Based SLAM은 로봇의 Pose 뿐만 아니라 map에 있는 Landmark도 Graph로 표현한다.**

![[Attachments/SLAM/Untitled.png]]

위 사진은 Victoria Park dataset의 한 장면으로, 실제 환경에서 Lamdmark를 활용하여 Map을 만든 예시이다. 파란색이 로봇의 궤적이고 빨간색이 landkmark이다.자동차가 공원 주변을 돌아다니면서 차량에 부착되어 있는 laser 센서를 활용하여 나무, 바위 등 고정된 장애물들을 tracking하고 landmark로 표현하였다. Landmark까지 고려된 Graph를 간략하게 그림으로 표현하면 아래와 같다.

![[Attachments/SLAM/Untitled 1.png]]

파란색 화살표는 로봇 pose를 의미하는 것이고 위치정보(2D : X,Y / 3D : X,Y,Z)와 방향정보를 포함한다. 검은색 별로 표시된 Landmark의 경우 위치정보만을 포함한다. 그러므로 pose와 pose 사이를 연결하는 edge와 pose와 feature(Landmark) 사이를 연결하는 edge는 각각 서로 다른 정보를 가지고 있다.

정리를 해보면 다음과 같다.

- Node로 표현할 수 있는 것
    - Robot pose (위치 정보 + 방향 정보)
    - Landmark의 위치
- Edge로 표현할 수 있는 것
    - Landmark observations (관찰값) : 로봇 포즈에서 landmark 관찰
    - Odometry measurements (측정값) : pose와 pose 사이의 constraint

따라서 이 Grpah에서는 **최적화 해야할 대상이 Landmarks(위치)와 robot poses(위치+방향)**이다.

# 2. Landmarks Observation

---

Landmarks가 node로 추가되었다. p**ose와 feature(Landmark) 사이를 연결하는 edge**는 어떻게 구성되어 있을까?
Landmarks observation은 두 종류로 표현할 수 있다.

- $(x,y)$ sensor observation : 위치 정보에 대한 edge
    - 로봇의 위치에 대해 landmark의 상대적인 좌표를 알 수 있다.
- Bearing Only Observations : 방향 정보에 대한 edge
    - 로봇과 landmark 사이에 상대적인 회전각을 알 수 있다.

강의에서는 2차원 평면을 기준으로 설명한다.

## 2-1. (x,y) sensor observation

---

$(x,y)$ sensor observation을 수식으로 쓰면 다음과 같다. ($x_i$에서 $x_j$ 관찰)

![[Attachments/SLAM/Untitled 2.png]]

Pose와 pose 사이를 잇는 edge와 형태는 유사하지만, 벡터의 차원이 다른 것에 주의해야한다. 2D 평면을 기준으로 Robot pose는 방향과 위치를 나타낼 때 $(3 \times 1)$벡터로 나타내고, Landmark의 경우 위치만 나타내기 때문에 $(2 \times 1)$로 나타낼 수 있다. 따라서 Robot pose에서 translation($t_i$)에 대한 값만 가져온 다음, landmark($x_j$)와의 차이를 구하고 Robot pose의 rotation matrix의 역행렬($R^T_i$)만큼
곱해주는 방식으로 Edge를 만들게 된다.

Edge가 다르게 정의됨에 따라 Error function도 다르게 정의 되는데 수식은 아래와 같다. 우리가 예측한 observation $\hat{z_{ij}}$과 실제로 관찰된 observation $z_{ij}$의 차이를 error로 한다. **(2D, (x,y))**

![[Attachments/SLAM/Untitled 3.png]]

![[Attachments/SLAM/Untitled 4.png]]

## 2-2. Bearing Only Observations

---

Bearing Only Observations는 방향 정보를 가지고 있는 edge이다. Landmark를 바라볼 때 Robot이 어떤 방향으로 바라봐야 하는지 알려준다. 수식적으로 표현하면 아래와 같다.

![[Attachments/SLAM/Untitled 5.png]]

2D 평면을 기준으로 방향에 대한 정보 $\theta$만 필요하기 때문에, 1차원 벡터로 표현할 수 있다. 수식에서 $(x_j-t_i).y$는 landmark($x_j$)와 Robot pose에서 translation($t_i$)에 $y$성분 차이를 의미하고, $(x_j-t_i).x$는 landmark($x_j$)와 Robot pose에서 translation($t_i$)에 $x$성분 차이를 의미한다.

마찬가지로 Error function도 바뀌게 되는데 수식으로는 아래와 같다. **(1D, $\theta$)**

![[Attachments/SLAM/Untitled 6.png]]

![[Attachments/SLAM/Untitled 7.png]]

# 3. Landmark를 통한 로봇 위치 파악 (Rank)

---

Pose graph와 마찬가지로 Gauss-newton 방법을 사용하여 최적화를 수행하게 된다. 따라서 자연스럽게 Matrix $H$를 구하게 된다. $H$는 Jacobian matrix와 Information matrix의 곱으로 만들어지는데, 수식은 $H=J^T\Omega J$로 정의하게 된다. $H$의 rank는 Jacobian에 의해 결정된다.

<aside>
💡 **<Remark>**
$rank(A^TA)=rank(A^T)=rank(A)$

</aside>

Edge를 어떻게 정의하느냐에 따라, 즉 Observation에 따라 행렬의 차원에 차이가 존재한다.

- **2D 평면을 기준으로 $(x,y)$ sensor observation**
    - 로봇 pose($x,y,\theta$)와 Landmark($x,y$)에 변수 5개와 edge에서의 변수 2개($x,y$)로 Matrix $H$를 구성하기 때문에 $(5*2)$로 표현된다.
    - $J_{ij}$의 block들은 는 최대 $(2 \times 3)$ matrices
        
        $$
        J_{ij}=\begin{bmatrix}
        \frac{\delta e_{ij}의x}{\delta x_i의 x}& \frac{\delta e_{ij}의x}{\delta x_i의 y} & \frac{\delta e_{ij}의x}{\delta x_i의 \theta} \\ \\
        \frac{\delta e_{ij}의y}{\delta x_i의 x}& \frac{\delta e_{ij}의y}{\delta x_i의 y} & \frac{\delta e_{ij}의y}{\delta x_i의 \theta}  \\\end{bmatrix}
        $$
        
    - 이 때 Matrix 의 rank는 **최대 2**이다.
- **2D 평면을 기준으로 Bearing Only observation**
    - 로봇 pose($x,y,\theta$)와 Landmark($x,y$)에 변수 5개와 edge에서의 변수 1개($\theta$)로 Matrix $H$를 구성하기 때문에 $(5*1)$로 표현된다.
    - $J_{ij}$의 block들은 는 $(1 \times 3)$ matrices
        
        $$
        J_{ij}=\begin{bmatrix}
        \frac{\delta e_{ij}의\theta}{\delta x_i의 x}& \frac{\delta e_{ij}의\theta}{\delta x_i의 y} & \frac{\delta e_{ij}의\theta}{\delta x_i의 \theta}\\\end{bmatrix}
        $$
        
    - 이 때 Matrix 의 **rank는 1**이다.

Rank가 중요한 이유를 예시를 들어 설명해보자. Robot이 Landmark를 관찰했다고 했을 때, Landmark 주변으로 Robot이 어디있는지 결정하려면 몇 개의 observation이 필요할까?

- **$(x,y)$ sensor observation**
    
    한 번 관찰한 경우, landmark 중심으로 하나의 원 위에서 존재 가능하다. 정확한 값을 구하기 위해서는 최소 2개의 observation이 있어야 한다.
    

![[Attachments/SLAM/Untitled 8.png]]

- **Bearing Only observation**
    
    landmark의 관찰값이 회전 각도에 대한 값만 있으므로 한 번 관찰한 경우는 아래 그림처럼 2차원 xy 평면 어디서나 존재할 수 있다. 정확한 값을 구하기 위해서는 최소 3개의 observation이 있어야 한다.
    

![[Attachments/SLAM/Untitled 9.png]]

## Under-determined System (**Levenberg Marquardt method**)

---

우리는 정확한 로봇의 위치를 파악하기 위해 필요한 observation 수를 Rank를 통해 판단할 수 있다. unique한 solution을 구하려면 System이 Full rank를 가지고 있어야 하기 때문이다.

그러나 **Landmark-based SLAM은 항상 Full rank임을 확신할 수 없다.** 최소 2번 또는 3번의 observation이 필요한데 landmark가 한 번만 관측되거나, 로봇에 대한 odometry 정보가 없을 수도 있기 때문이다. 이런 경우를 **Under-determined system**이라고 한다. 따라서 $H$의 rank는 constraints의 rank의 합보다 같거나 적다. 하지만 unique solution을 결정하기 위해는 full rank여야 한다.

Full Rank가 아닌 경우 **Gauss newton 방법에서 선형화를 진행할 때, 일부러 $H$에 damping factor $\lambda I$를 더해 system을 Full rank로 만든다.**

따라서 $H \Delta x=-b$가 아니라 $(H+ \lambda I)\Delta x=-b$의 해를 구한다.

damping factor를 작게 하면 system이 많이 변하게 하지 않게 하면서 system을 full rank로 만들 수 있다. 이렇게 damping factor을 추가하는 방법을 **Steepest Descent Approach**라고 한다. damping factor $\lambda$의 값을 조절하여 딥러닝의 adaptive learning rate 개념으로서 사용할 수 있다.

또한 개념적으로 Gauss-newton method에 Steepest Descent Approach를 추가한 방법을 **Levenberg Marquardt method**라고 한다. Levenberg Marquardt의 pseudo code는 아래와 같다.

![[Attachments/SLAM/Untitled 10.png]]

Levenberg Marquardt는 Visual SLAM에서 자주 등장하는 용어인 **Bundle Adjustment**에서도 사용하는 방법이다.

<aside>
💡 **<Bundle Adjustment>**

Bundle Adjustment는 서로 다른 viewpoints에서 찍힌 이미지에 기반해 environment에서 3차원 feature points들 간의 관계를 찾을 때 사용한다(3D reconstruction). Camera pose 간의 odometry를 모른다고 가정할 때 이미지에서 보이는 feature와 environment에서 3차원 feature points의 대응관계(correspondence)를 구하고, 결과적으로 camera의 pose와 3차원 feature points의 위치를 구하게 된다. Bundle Adjustment는 2D 이미지 plane에서 reprojection error를 최소화하는 것이 목표이다.

</aside>

# 참고 자료

---

Cyrill 교수님 강의

SLAM DUNK Season2 강의

[Slam 4-2강 (Graph-based SLAM with Landmarks) 요약 - Taeyoung’s Blog (taeyoung96.github.io)](https://taeyoung96.github.io/slam/SLAM_04_2/)