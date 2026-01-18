# 1. Introduction to SLAM

# 1. SLAM이란?

---

**SLAM(Simultaneous Localization and Mapping)**은 로봇이 Localization과 Mapping을 동시에 하는 것이다.

- **Localization** : 로봇의 위치를 추정하는 것
- **Mapping** : 로봇 주위에 무엇이 있는지 Map을 만드는 것
    - Sparse 한 Map : 필요한 3D Landmark만 표시
    - Dense 한 Map : 촘촘하게 표시

Mapping과 Localization은 서로 의존적이기 때문에 SLAM을 chicken-or-egg problem이라고 한다. 

## 1-1. Frontend, Backend

---

SLAM은 Frontend와 Backend로 나눌 수 있다.

- **Front-End : raw 센서 데이터를 가공**
    1. Feature Extraction
        1. Feature : feature 추출
        2. Direct : feature 추출 없이 모든 데이터 사용
    2. Data Associtation : Feature Tracking / Loop detecting
- **Back-End : Map Estimation**
    - Filter-based : EKF, Particle Filter
    - Graph-based(Least Square)

Backend에서 가장 인기 있는 optimization : g2o, gtsam, ceres

## 1-2. Localization

---

Dense 한 Map이 아닌 Landmark 이용한 Map의 예시를 보자. **Map은 알고 있는 상태**이다.

먼저 **Ideal 한 경우**를 보자.

- Robot motion : 바퀴 둘레, 바퀴의 회전 수 등을 토대로 움직인 거리 계산
- Landmark : 사전에 만들어 놓은 map
- Robot pose 추정 : 알고 있는 정보 바탕으로 robot pose 추정

![Untitled](1%20Introduction%20to%20SLAM/Untitled.png)

이제 **현실에서의 실제 상황**을 보자. Robot motion이 noisy 하기 때문에 Landmark observation(로봇 센서로 observation)도 noisy 하다. 우리는 noisy한 motion 과 landmark observation 을 기반으로 pose를 추정한다.

- 별표는 Landmark (noisy)
- 흰색 동그라미는 모바일로봇의 실제 위치
- 회색 동그라미는 예측된 위치이다 (noisy)

만약 map을 알고 있다면(=landmark의 위치를 알고 있다면) 1이 아닌 2에 landmark가 위치함을 알고 로봇의 위치도 3→4로 보정이 가능하다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%201.png)

실제 localization할 때는 다음의 이유로 error가 있다.

- 로봇이 측정하는 센서(ex. IMU)가 Noise가 있다.
- 로봇이 landmark를 관찰 했을 때, 측정 값(ex. laser, camera)가 Noise가 있다.

## 1-3. Mapping

---

**Odometry는 알고 있는 상태**이다.

- 노란색 별표는 실제 Landmark의 위치 (can be noisy)
- 회색 별포는 로봇이 측정한 Landmark의 위치 (noisy)
- 흰색 동그라미는 모바일 로봇의 실제 위치

![Untitled](1%20Introduction%20to%20SLAM/Untitled%202.png)

Landmark는 motion과 센서값을 통해 추정하기 때문에 mapping에도 error가 있을 수 밖에 없다.

## 1-4. SLAM(Localization + Mapping)

---

 실제로는 Robot Motion과 Landmark Observation 모두 noisy 하기 때문에 에러가 계속 누적된다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%203.png)

Localization과 Mapping 한 가지 task만 하는 것보다 SLAM의 에러가 더 클 수도 있다.

그럼에도 왜 SLAM system을 사용하려 할까?

- Localization은 정확한 landmark가 있어야 할 수 있다.
- Mapping은 정확한 motion이 있어야 할 수 있다.
- SLAM은 아무것도 없어도 바로 시작할 수 있다!
- 이론적으로 **‘Loop closure(이전에 방문한 landmark에 재방문한 경우)’**를 거치고 나면 이때까지 누적된 error를 없앨 수 있다.

# 2. Offline SLAM vs Online SLAM

---

SLAM system은 크게 Offline SLAM(=Full SLAM)과 Online SLAM으로 나눈다.

- **Offline SLAM(=Full SLAM)** : Sensor data를 모두 수집한 후에 Map을 만든다. 실시간 제약이 없어 계산을 오래할 수 있다. 따라서 일반적으로 조금 더 정확한 Map을 만들고 싶을 때 사용한다.
    - SfM, modern BA-based SLAM과 비슷하다.
- **Online SLAM** : 실시간으로 map도 만들고, localization도 한다. 공간을 인식하는 하나의 모듈로서 동작한다. control 모듈과 함께 사용하면 장애물 회피 등에 용이하다.
    - Filter-based SLAM과 비슷하다.

## 2-1. SLAM System의 수식적 표현

---

우리가 측정하고 알 수 있는 것들은 다음과 같다. **(Given)**

- **Robot’s contorl(motion)** : 센서에서 odometry를 받아온 값 - $u_{1:T} = (u_1, u_2, u_3,…, u_T )$
- **Observations(sensor)** : laser나 camera 센서를 통해 관찰된 값 - $z_{1:T} = (z_1, z_2, z_3,…, z_T )$

우리가 구해야하는 값들은 다음과 같다. **(Wanted)**

- **환경의 Map 정보** - $m$
- **Robot의 Path 정보(pose)** - $x_{1:T} = (x_1, x_2, x_3,…, x_T )$

우리는 robot motion, observation이 noisy한 것을 안다. 얼마만큼 noisy 할까?

noise를 확률적 분포로 나타낼 수 있다(주로 Gaussian 사용)

![Untitled](1%20Introduction%20to%20SLAM/Untitled%204.png)

## 2-2. Offline SLAM의 수식적 표현

---

Localization과 Mapping 모두 Noise가 존재하기 때문에, 확률 분포를 이용하여 표현한다.

SLAM을 하나의 식으로 쓰면 다음과 같다. **T는 전체 시간**이다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%205.png)

위 식을 해석해보면 **$z_{1:T}$와 $u_{1:T}$를 고려해서 $x_{1:T}$와 $m$을 확률적으로 표현한다**는 뜻이다.

최근에는 Graph-based SLAM에 대한 연구가 많이 이루어지고 있는데, 이를 그림으로 표현하면 다음과 같다. $u_{t-1}$와 $u_t$ 사이에는 관계가 없으므로 두 노드는 연결되지 않는다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%206.png)

Offline SLAM이기 때문에 관찰할 수 있는 모든 센서의 값들을 가져와서 Map과 path를 계산한다.
Offline SLAM은 전체적인 경로를 만든다.

## 2-3. Online SLAM 의 수식적 표현

---

Online SLAM은 현재에 관찰되는 **$u$**와 **$z$**만을 이용하여 Map과 Path를 만들어낸다.
Online SLAM은 가장 최근 pose와 현재 보고 있는 map point 만 계산한다. 따라서 계산이 빠르다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%207.png)

Online SLAM의 Graphical Model은 아래와 같다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%208.png)

Online SLAM에서 쓰이는 식을 모두 적분을 하게 되면 Offline SLAM처럼 만들 수 있다. 즉, 현재 시점에서 구한 pose와 map을 계속 더하면 전체적인 경로 및 Map을 만들어낼 수 있다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%209.png)

# 3. SLAM이 어려운 이유

---

SLAM이 어려운 이유는 **불확실성(uncertainty)** 때문이다.

1. Robot path와 map이 둘 다 unknown
    
    Map과  pose 추정은 correlated 하다. 따라서 Map을 이용해서 Localization을 하고, localization을 이용해서 Map을 만드는데, 둘 다 모르는 상태에서 구해야 하기 때문에 서로 검증이 불가능하다. **불확실성이 점점 커진다**.
    

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2010.png)

1. Known vs Unknown correspondence ⇒ Data association Problem
    
    로봇이 위치할 확률을 빨간색 원으로 표시해보자. 만약 로봇에서 관찰된 landmark가 2개 있을 때, **로봇의 pose에 따라서 관찰되는 landmark가 달라**진다.
    
    이러한 문제점 때문에 우리는 **Data association(로봇의 pose에서 볼 수 있는 landmark들을 매칭)**이 필요하다. 하지만 이때 잘못된 Data association 선택하면 발산한다.
    

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2011.png)

# 4. SLAM의 여러 Pipelines

---

Pipeline이 여러 의미로 쓰이지만, 여기서는 여러 종류의 기법들이라고 생각할 수 있다. SLAM을 푸는 방법은 크게 3가지로 나눌 수 있다.

1. **Kalman Filter**
2. **Particle Filter**
3. **Graph-based SLAM**

이 강의에서는 Grpah-based SLAM을 위주로 설명 한다.

Grpah-based SLAM은 **Motion model**과 **Observation model**을 이용해서 풀게 된다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2012.png)

## 4-1. Motion Model (Grpah-based SLAM)

---

Motion Model로 구하는 것은 **로봇의 pose**이다.

이전 pose와 현재 control 값(encoder 등으로 관찰)들을 통해 현재의 pose를 확률적으로 구한다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2013.png)

확률 분포를 Gaussian Model로 표현할 수도 있고, Non-Gaussian model로도 표현할 수 있다. 이전 position에 대한 확률에 motion에 대한 확률이 더해져 불확실성이 증가한다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2014.png)

가우시안 분포는 선형 관계에만 적용된다. 예를 들어 X가 가우시안 분포이고 Y가 가우시안 분포이면 X+Y도 가우시안 분포를 가진다. 하지만 위에서 아래쪽 그림과 같이 Non-Linear 관계(회전행렬이므로 삼각함수 있어 Non-Linear)의 경우 가우시안 분포를 적용하지 못한다.

## 4-2. Observation Model (Graph-based SLAM)

---

Observation Model로 구하는 것은 **Map(landmark의 위치)**이다.

현재 pose에 대해 observation 값이 어떤 게 나와야 하는지 확률적으로 표현한다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2015.png)

마찬가지로 확률 분포를 Gaussian 또는 Non-Gaussian model로 표현할 수 있다. 현재 pose에서 sensor값 찍히는 곳에 대해 불확실성이 존재한다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2016.png)

# Mark) Model for Virtual Observation

---

두 포즈의 상대적인 포즈로 정보를 얻는다.

![Untitled](1%20Introduction%20to%20SLAM/Untitled%2017.png)

# 참고 자료

---

Cyrill 교수님 강의

SLAM DUNK Season2 강의

[Slam 1강 (Introduction to SLAM) 요약 - Taeyoung’s Blog (taeyoung96.github.io)](https://taeyoung96.github.io/slam/SLAM_01/)