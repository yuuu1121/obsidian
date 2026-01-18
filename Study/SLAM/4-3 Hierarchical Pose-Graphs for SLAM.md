# 4-3. Hierarchical Pose-Graphs for SLAM

# 1. Hierarchical Pose-Graph 란?

---

Graph-based SLAM은 크게 Front-end와 back-end로 구분할 수 있다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled.png)

- Front-end : 센서에서 raw data를 받아 node, edge를 만들어 graph를 구성한다.
- Back-end : Front-end쪽에서 만든 node나 edge를 최적화 한다.
    - (= 형성된 그래프를 matrix 형태로 매핑 하고 transformation이 비선형이므로 non-linear least square 문제를 푼다. 각 step 마다 선형화를 통해 $\Delta$pose를 구해 전체 포즈를 업데이트 한다.)
- Front-end와 Back-end는 서로 상호작용(Interplay) 하며 정교한 Graph를 만들어 나간다.

실시간성이 중요한 **Online SLAM**에서, 우리는 아래와 같은 어려움을 겪는다.

1. 시간이 지날수록 그래프가 커져 Back-End에서 그래프 최적화를 할 때 **연산량이 늘어나고 포즈의 업데이트 속도가 느려진다.**
2. Loop closure factor를 찾을 때 거리 기반으로 현재 위치 중심 일정 거리 이하의 가까운 pose들에 대해서만 찾는다고 해도, 특정 거리 내에 노드가 많이 존재한다면 **loop closure 매칭(포즈와 포즈 간의 센서 데이터 매칭으로 loop closure를 찾는다.)을 위한 연산량이 커진다.**

**Hierarchical Pose-Graph의 목적은 연산량을 줄이는 데 있다.** Graph를 계층적(Hierarchical)으로 만들고 간략화함으로써 더 적은 수의 node와 edge만으로 최적화를 빠르게 수행할 수 있는 구조이다. 전체 그래프를 한 번에 최적화하는 게 아니라 계층적으로 업데이트 한다. 연산량 감소에 중점을 두어 실시간성을 위해 고안되었다. Loop Closure를 찾을 때도 해당 범위 내 모든 포즈가 아닌 가장 상위 계층 레벨의 포즈만 탐색한다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%201.png)

위 그림이 Hierarchical Pose-Graph를 시각화한 그림이다. bottom layer가 Robot이 돌아다니면서 Input data로부터 Graph를 만든 것이라고 하자. First layer는 bottom layer보다 node와 edge 수를 간략화하여 grah로 표현한다. 마찬가지로 second layer에서는 node와 edge의 수를 더 간략화하여 graph를 표현한다.

Hierarchical Pose-Graph의 기본적인 Idea는 다음과 같다.

- **node와 edge의 수가 적으면 적을수록 최적화 할 때 빠르다.**
- **Global한 map을 최적화할 때, 핵심적인 node와 edge들만 최적화 해도 충분하다.**

하나의 observation 마다 모든 graph를 최적화할 필요가 없다. Loop closing을 할 때도 재방문을 한 node 주변 node들에 대해서만 최적화 한다. 얼마나 많은 주변 node들을 최적화 할 것인지는 주변 노드들의 covariance matrix를 이용해 판단한다.

Hierarchical Pose-Graph의 방법을 사용할 때의 주요 가정은 **Robot이 순간이동(teleported)하지 않고, 자연스럽게 움직여야 하며 센서는 limited range를 가진다.**

# 2. Hierarchical Pose-Graph 동작

---

Hierarchical Pose-Graph이 어떻게 동작하는지 알아보자.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%202.png)

먼저 센서 데이터로부터 dense 한 graph를 만든다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%203.png)

이제 가까운 거리의 node들끼리 local connectivity를 기준으로 그룹화를 진행한다. 예를 들어, node와 node 사이가 50m 이상 차이 날 때 다른 그룹으로 취급한다. 본 강의에서는 거리를 기반으로 그룹을 나누었다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%204.png)

각 그룹 당 대표 node를 하나 정한다. 그림에는 빨간색으로 표신된 것이 대표 node이다. 본 강의에서는 가장 먼저 관측된 pose를 대표 node로 선정할 수 있다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%205.png)

이제 대표 node만을 이용해 상위 계층의 graph를 만든다. 이때 대표 노드 사이의 edge를 만들어야 한다. 상위 계층에서의 edge는 직접적으로 관찰된 값으로 만드는 것이 아니라, 그룹화한 node들끼리 연결성을 활용하여 계산을 진행한다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%206.png)

이렇게 상위 계층의 graph에서는 조금 더 적은 node와 edge로 최적화가 가능해진다. 계층을 많이 만들고 싶으면 지금까지 했던 방법을 반복적으로 진행한다. 그 다음 상위 계층의 graph에서 최적화를 진행한 모습을 위 그림과 같이 나타낼 수 있다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%207.png)

우리가 최적화한 빨간색 node는 하위 계층을 대표하는 node였기 때문에 최적화를 진행했을 경우, 최적화 결과를 하위 계층의 node들로도 전파(propagte) 해줘야 한다. 이때, 항상 전파해주는 것이 아니고 **inconsistency가 있을 때만 전파**해준다. 즉, 변동이 큰 일부만 하위 레벨 업데이트를 해준다.

## 2-1. 상위 계층에서의 edge 결정하기

---

어떻게 상위 계층에서 edge를 계산하는 것일까?

우리는 pose graph에서 edge를 결정하는 방법 두 가지를 배웠다. 여기서는 Observation-Based edge를 활용하여 edge를 결정한다. 아래의 그림에서 virtual observation $Z$와 두 node간에 Information matrix $\Omega$를 찾는 것이 우리의 목표이다. 어떻게 local node edge 정보를 결합하여 계산하는 것일까?

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%208.png)

실제 업데이트를 할 때, 두 대표 노드끼리 edge가 존재하는 것이 아니므로 상위 그래프에서 대표 노드끼리의 edge를 만들어주어야 한다. node에는 기본적으로 각 pose들이 저장되어 있다. 따라서 빨간색 node에 있는 pose들을 활용하여 두 node의 상대적인 Transformation을 표현한다. 두 포즈 간의 uncertainty가 매핑된 것이 없기 때문에, 둘 중 하나를 fix하고 edge를 만든다. 우리는 edge를 만들 때 Information matrix $\Omega$를 활용해서 불확실성 정도를 표현했다. **A,B 노드 중 A가 고정이 되면 (A에서 B로의 tf uncertainty) = (B의 uncertainty) 이다.**

새롭게 만들어지는 edge의 Information matrix $\Omega$를 계산해보자.

Information matrix $\Omega$는 두 node의 불확실성을 표현하기 위한 행렬이고, Matrix $H$를 정의할 때 Information matrix $\Omega$가 들어간다. 그리고 Information matrix $\Omega$의 역행렬이 covariance matrix이다. 따라서 강의자료에서는 두 node $x_a,x_b$의 Information matrix $\Omega_{ab}$를 아래처럼 표현하고 있다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%209.png)

node $x_a$에서 바라본 불확실성을 Matrix $H^{-1}$의 (b,b)번째 성분을 값을 통해 알아내고 이를 다시 Information matrix 값으로 바꿔주기 위해 전체의 성분값의 Inverse값을 구한다. node a를 고정했으므로 [b, b] block만 고려한다.

이렇게 해서 상위 계층 간의 edge를 계산하는 방법에 대해서 알아봤다. 정리하자면 node들에는 robot의 pose가 각각 저장되어 있으므로 그 값을 활용하여 기존의 pose graph의 edge를 만드는 방법과 동일하게 edge를 결정한다.

이렇게 대표 노드 간의 Information matrix $\Omega$을 통해 상위 그래프 형성한 후, 최적화 하고 상위 레벨의 포즈들의 하위 레벨 포즈의 변동이 일정 임계치 이상이면 하위 포즈들에 전파한다.

## 2-2. 최적화 결과를 하위 계층으로 전파하기

---

최적화 결과를 어떻게 하위 계층으로 전파를 시켜주는 것일까?

상위 계층에서의 node들은 하위 계층에서 대표 node들이고, 대표 node들의 최적화는 자연스럽게 다른 node들에도 영향을 미친다. 최적화를 진행하면 node들의 이동(Shifting)이 생기는데, 전파를 시킬때는 단순하게 대표 node들의 이동(Shifting)을 그대로 적용한다. 즉, 같은 그룹의 하위 node들도 대표 node의 이동만큼 움직인다.

이때, Hierarchical Pose-Graph 방식이 연산량 관점에서 고안된 것이므로 실제 최적화 결과를 하위 레벨로 전파할 때도 매번 전파하는 것이 아닌, 대표 노드끼리의 최적화를 통해 변경될 하위 포즈들의 정도가 threshold 이상일 때만 업데이트를 실시한다. 업데이트 하는 하위레벨의 tf 정도가 너무 적다면 하위 레벨에서의 업데이트는 자제한다.

따라서 **하위 계층으로의 전파는 lower level inconsistent 됐을 때만 발생하며, 가장 낮은 level까지 내려가거나 대표 노드의 움직임이 threshold 이하로 움직일 때까지 하위 계정으로 전파된다.**

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%2010.png)

위 그림을 보면, 어떤 두 대표 노드 간의 측정이 왼쪽과 같이 되었을 때 하위 노드들의 inconsistence가 존재하기 때문에 해당 업데이트를 하위 레벨까지 전파한다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%2011.png)

위 그림처럼 실제 대표 노드 간의 거리가 더 짧은 것으로 관측되면 이 또한 inconsistence가 있는 것으로 보고 하위 레벨 포즈를 업데이트한다. 두 대표 노드 $x_a, x_b$가 서로 가까워지는 방향으로 이동했으므로 하위 레벨 노드들도 서로 가까워진다.

이 과정에서 추가적인 error가 발생할 수 있지만 여기서는 고려하지 않는다. 대표 node들의 움직임이 그렇게 크지 않기 때문에 critical한 문제는 발생하지 않기 때문이다. 물론 움직임이 얼마나 큰지 한번 확인할 필요는 있다.

# 3. Hierarchical Pose-Graph의 장점 및 고려사항

---

우리가 결국 정확한 Map을 만드려면 Lowest level에서 최적화를 진행해야 한다. 그럼에도 불구하고 이런 Hierarchical Pose-Graph를 활용했을 때의 장점은 무엇일까?

1. Initial guess가 좋지 않을 경우, high level graph에서 최적화를 진행하기 때문에 전체적인 수렴 속도를 빠르게 할 수 있다
2. **연산 시간 이득**(Online SLAM을 위해 고안되었기 때문에 연산 시간이 중요)
    1. 모든 node들을 최적화를 하는 것이 아니기 때문에 계산량이 크게 줄어든다.
    2. 그래프 전체를 업데이트 하는 것이 아니라, 일부 상위 레벨의 업데이트를 통해 전파한다. 하위 레벨로의 업데이트는 독립적(각 그룹 내에서의 업데이트는 독립으로 본다)이기 때문에 **병렬적**으로 처리 가능하다.
    3. **Loop Closure** 찾을 때도 범위 내 모든 포즈가 아닌 범위 내 상위 레벨만 search
    4. 최상위 레벨에서 포즈들을 업데이트 하고 이 업데이트 결과를 하위 레벨로 전파해서 전체적으로 tree 구조로 계층적으로 업데이트하는데, 업데이트 할 때도 **threshold** 이상일때만 업데이트 하므로 연산시간 이득

우리가 Hierarchical(계층) 구조를 활용해서 graph를 만들 경우, 이는 전체적인 graph를 간략하게 한 것이기 때문에 가장 lowest graph와 얼마나 차이가 있는지 확인해 보아야 한다.

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%2012.png)

![Untitled](4-3%20Hierarchical%20Pose-Graphs%20for%20SLAM/Untitled%2013.png)

위 그림에서 왼쪽은 가장 lowest graph에서의 불확실성 정도이고, 오른쪽은 higher level graph에서 불확실성 정도이다. 표에서도 알 수 있듯이 higher level의 graph에서 불확실성이 더 크다. Higher level graph는 approximation(근사)를 진행한 Graph라고 볼 수 있다.

# Reference

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- 강의 정리

[Slam 4-3강 (Hierarchical Pose Graphs for SLAM) 요약](https://taeyoung96.github.io/slam/SLAM_04_3/)