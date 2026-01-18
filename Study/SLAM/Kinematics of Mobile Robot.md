# Kinematics of Mobile Robot

![image.png](Kinematics%20of%20Mobile%20Robot/image.png)

로봇 암은 base가 ground에 고정 되어 있고 링크가 하나의 체인으로 연결되어 있다. (Serial type)

모바일 로봇의 동작은 바퀴와 지면의 접점에서 **rolling과 sliding constraints**를 통해 정의된다.

### Non-holonomic system

Diffential equations는 final position에서 바로 적분 불가능하다.

![image.png](Kinematics%20of%20Mobile%20Robot/image%201.png)

### Mobile Robots with Wheels

- 모바일 로봇의 안정성은 3개의 바퀴부터 보장된다.
- 바퀴가 4개 이상일 경우 안정성 증가 (서스펜션 시스템 필요)
- 바퀴가 클수로 높은 장애물 극복 가능 (높은 토크 필요)
- 대부분 non-holonomic (정밀한 제어 필요)

### Kinematics of Differential Type Mobile Robots

Differential Type Mobile Robot : 하나의 축에 장착된 두 개의 바퀴를 사용하는 모바일 로봇

![image.png](Kinematics%20of%20Mobile%20Robot/image%202.png)

$$
\small{그림\ 2.}
$$

먼저 Kinematic Constraints (rolling, sliding)을 구해본다.

![image.png](Kinematics%20of%20Mobile%20Robot/image%203.png)

$$
\small{그림\ 3.}
$$

- $X_R,Y_R$: 로봇의 좌표계에서 X축과 Y축
- $\alpha$: 로봇 몸체와 바퀴가 이루는 각도
- $\beta$: 바퀴가 로봇 본체와 이루는 각도의 변화 (로봇의 진행 방향과 바퀴의 각도 차이)
- $r$: 바퀴의 반지름
- $l$: 로봇의 회전 중심과 바퀴 사이의 거리
- $\dot{\theta}$: 로봇의 회전 속도
- $\dot{\phi}$˙: 바퀴의 각속도
- $\dot{x_R}$: 로봇의 XR 방향 속도
- $\dot{y_R}$: 로봇의 YR 방향 속도

### **Rolling constraint = $r\dot{\phi}$**

로봇의 바퀴가 구르는 방향으로 미끄러지지 않고 회전하는 제약 조건이다.

즉, 바퀴가 구르는 방향으로의 속도 성분은 바퀴의 회전 속도와 관계가 있다.

속도 $v$  방향으로 rolling constraint가 작용한다.

바퀴의 중심을 기준으로  $X_R ,Y_R$ 좌표계에서 이동하는 로봇의 운동을 고려하여 $\dot{x_R} ,\dot{y_R}$ 의 성분을 찾는다. 

 $l\dot{\theta}$ 는 각속도를 반영한다.

수식을 구할 때, $v$ 축으로 $X_r ,Y_r$ 을 정사영을 내려 rolling constraint에 관한 성분을 구한다.

$l\dot{\theta}cos(\beta)$  : 로봇의 회전으로 인해 바퀴 중심이 이동하는 성분

수식을 구해보면 아래와 같다. 

$$
\dot{x_R}cos(\pi/2-(\alpha+\beta))+\dot{y_R}sin(\pi-(\alpha+\beta))+l\dot{\theta}sin(\pi/2-\beta) -r\dot{\phi}=0
$$

위 식을 정리해보면 다음과 같다.

$$
\dot{x_R}sin(\alpha+\beta)+\dot{y_R}cos(\alpha+\beta)+l\dot{\theta}cos(\beta) -r\dot{\phi}=0
$$

위 식을 행렬로 표현하면,

$$
\begin{bmatrix}sin(\alpha+\beta)&-cos(\alpha+\beta)&-lcos(\beta)\end{bmatrix}\begin{bmatrix}\dot{x_R}\\ \dot{y_R}\\\dot{\theta}\end{bmatrix} -r\dot{\phi}=0
$$

### **Sliding constriant**

바퀴가 바닥에서 미끄러짐 없이 회전할 때, 바퀴의 접선 방향으로는 운동이 일어나지 않는다.

즉, **로봇의 이동 방향과 수직한 축에 대해 속도 성분이 없다.**

수식을 구하기 위해,  바퀴 중심의 속도 성분에서 수직 성분을 찾아 이를 0으로 둔다.

- $x_Rcos(α+β)$: $X_R$축 방향 속도를 바퀴 축에 대해 수직으로 분해한 성분
- $\dot{y_R}sin⁡(α+β)$: $Y_R$축 방향 속도를 바퀴 축에 대해 수직으로 분해한 성분
- $\dot{\theta} \sin(\beta)$: 로봇의 회전으로 인해 바퀴 중심이 이동하는 속도 성분

이 성분들이 모두 합쳐진 결과는 바퀴 축에 수직한 방향으로의 총 속도 성분을 나타내며, 미끄러짐 없이 회전하려면 이 값이 0이 되어야 한다.

$$
\dot{x_R}cos(α+β)​​+\dot{y_R}sin(α+β)​​+\dot{θ}l⋅sin(β)=0
$$

위 식을 행렬로 표현하면, 

$$
\begin{bmatrix}cos(\alpha+\beta)&sin(\alpha+\beta)&lsin(\beta)\end{bmatrix}\begin{bmatrix}\dot{x_R}\\ \dot{y_R}\\\dot{\theta}\end{bmatrix}=0
$$

### **Rolling constraint +** **Sliding constraint**

$$
\begin{bmatrix}sin(\alpha+\beta)&-cos(\alpha+\beta)&-lcos(\beta)\\cos(\alpha+\beta)&sin(\alpha+\beta)&lsin(\beta)\end{bmatrix}\begin{bmatrix}\dot{x_R}\\ \dot{y_R}\\\dot{\theta}\\\end{bmatrix}= \begin{bmatrix}r\dot{\phi} \\0\end{bmatrix}
$$

이제 그림 4와 같은 Differential Mobile Robot을 예시로 들어보자.

![image.png](Kinematics%20of%20Mobile%20Robot/image%204.png)

$$
\small{그림\ 4.}
$$

wheel 1 : $\alpha={-90}\degree, \beta=180\degree$

wheel 2 : $\alpha={90}\degree, \beta=0\degree$

각 바퀴에 대한 rolling, sliding constraint 수식을 합쳐 하나의 행렬로 만들고, 위 조건을 대입한다.

$$
\begin{bmatrix}sin(90\degree)&-cos(90\degree)&-lcos(180\degree)\\cos(90\degree)&sin(90\degree)&lsin(180\degree)\\sin(90\degree)&-cos(90\degree)&-lcos(0\degree)\\cos(90\degree)&sin(90\degree)&lsin(0\degree)\end{bmatrix}\begin{bmatrix}\dot{x_R}\\ \dot{y_R}\\\dot{\theta}\\\end{bmatrix}= \begin{bmatrix}r\dot{\phi_1} \\0\\r\dot{\phi_2} \\0\end{bmatrix}
$$

위 행렬식에서 2행과 4행이 같다. 

계산을 간단하게 만들기 위해 두 개의 행 중 하나를 소거한다.

소거되는 행에 따라 $\begin{bmatrix}r\dot{\phi_1} \\0\\r\dot{\phi_2} \\0\end{bmatrix}$행렬에서 0이 사라지는 위치가 달라진다.

이번 예제에서는 2행을 소거한다.

2행을 소거하고 각 바퀴의 조건을 대입한 식을 구해보면 아래와 같다.

$$
\begin{bmatrix}1&0&-l\\1&0&-l\\0&1&0\end{bmatrix}\begin{bmatrix}\dot{x_R}\\ \dot{y_R}\\\dot{\theta}\\\end{bmatrix}= \begin{bmatrix}r\dot{\phi_1} \\r\dot{\phi_2} \\0\end{bmatrix}
$$

위 수식에 그림 1의 수식을 대입하고, $\begin{bmatrix}\dot{x_I}\\ \dot{y_I}\\\dot{\theta}\\\end{bmatrix}$를 구한다.

$$
\begin{bmatrix}\dot{x_I}\\ \dot{y_I}\\\dot{\theta}\\\end{bmatrix}={\begin{bmatrix}cos(\theta)&sin(\theta)&0\\-sin(\theta)&cos(\theta)&0\\0&0&1\end{bmatrix}}^{-1}{\begin{bmatrix}1&0&-l\\1&0&-l\\0&1&0\end{bmatrix}}^{-1}\begin{bmatrix}r\dot{\phi_1} \\r\dot{\phi_2} \\0\end{bmatrix}
$$

위 수식에서 역행렬을 구해보면 다음과 같다.

Rotation Matrix의 역행렬은 Transpose한 것과 같기 때문에 전치 행렬을 구해준다.

3x3 행렬의 역행렬 구하는 방법 : 

[3x3 Inverse Matrix](Kinematics%20of%20Mobile%20Robot/3x3%20Inverse%20Matrix%20125d4ae18d3280fa8e01eb2fa2ab5fb6.md)

$$
\begin{bmatrix}\dot{x_I}\\ \dot{y_I}\\\dot{\theta}\\\end{bmatrix}={\begin{bmatrix}cos(\theta)&-sin(\theta)&0\\sin(\theta)&cos(\theta)&0\\0&0&1\end{bmatrix}}{\begin{bmatrix}1/2&1/2&0\\0&0&-l\\1/2l&-1/2l&0\end{bmatrix}}\begin{bmatrix}r\dot{\phi_1} \\r\dot{\phi_2} \\0\end{bmatrix}
$$

위 식을 전개를 하고 $v, w$에 대해 행렬을 소거하면 다음과 같다.

$$
\begin{bmatrix}\dot{x_I}\\ \dot{y_I}\\\dot{\theta}\\\end{bmatrix}={\begin{bmatrix}cos(\theta)&-sin(\theta)&0\\sin(\theta)&cos(\theta)&0\\0&0&1\end{bmatrix}}{\begin{bmatrix}\frac{1}{2}(r\dot{\phi_1}+r\dot{\phi_2})\\0\\\frac{1}{2}(r\dot{\phi_1}-r\dot{\phi_2})\end{bmatrix}}=\begin{bmatrix}cos(\theta)&0\\sin(\theta)&0\\0&1\end{bmatrix}\begin{bmatrix}v\\w\end{bmatrix}
$$

위 식에서 $\frac{1}{2}(r\dot{\phi_1}+r\dot{\phi_2})=v ,\frac{1}{2}(r\dot{\phi_1}-r\dot{\phi_2}) = w$이다.