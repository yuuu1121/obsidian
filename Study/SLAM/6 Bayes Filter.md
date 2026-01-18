# 6. Bayes Filter

# 1. Bayes Filter란?

---

Bayes Filter는 Bayes’ theorem를 반복적으로 사용하는 Filter로, Recursive 하게 system의 현재 state를 추정한다.

베이즈 정리는 이전의 경험과 현재의 증거를 토대로 어떤 사건의 확률을 추론한다. 즉 prior와 likelihood를 이용하여 posterior를 구할 수 있다.

## State Estimation

![[Attachments/SLAM/Untitled.png]]

$t$라는 시간에서 로봇의 관찰값(observation) $z$와 로봇의 Control command $u$가 주어졌을 때 로봇의 state $x$를 추정한다.

![[Attachments/SLAM/Untitled 1.png]]

1부터 $t$까지 주어진 observation $z$와 control command $u$를 고려해서 $t$번째 로봇의 상태 $x$를 추정한다. Recursive 하다는 것은 로봇의 상태 $x_{t-1}$를 활용해서 로봇의 상태 $x_t$를 추정한다는 의미이다.

Bayes Filter의 가장 유명한 예제인 Robot의 위치 찾기를 보자.

![[Attachments/SLAM/Untitled 2.png]]

아래처럼 가정한다.

- 1차원 공간을 가정
- 로봇은 **Door인지 아닌지만을 판단**할 수 있다.
- Global Environment에 대해 아무것도 모르는 상태

처음에는 아무것도 모르는 상태이기 때문에 로봇의 위치를 **Uniform distribution**으로 나타낸다.

![[Attachments/SLAM/Untitled 3.png]]

로봇이 움직이면서 관찰한다. 센서값을 수집하면 global 환경에 대한 정보를 알 수 있다. $p(z|x)$는 관찰값으로, 문이 있는 위치를 나타낸다. 관측값에 의해 문 앞에 로봇이 위치해 있을 확률이 높다고 생각할 수 있으므로 로봇의 위치를 추정하는 belief $bel(x)$는 문의 위치에서 높아진다.

![[Attachments/SLAM/Untitled 4.png]]

로봇을 앞으로 움직이면(=motion) $bel(x)$도 함께 앞으로 움직인다. 처음 만들었던 state 확률분포는 처음에 있었던 state를 기준으로 만들어준 분포였기 때문에, 기준점이 움직이면 분포도 함께 움직여주어야 하기 때문이다. 이때 로봇이 얼마나 움직였는지 motion에 불확실성이 존재하기 때문에, 확률 분포가 조금 퍼져있는 형태가 된다.(smooth distribution)

![[Attachments/SLAM/Untitled 5.png]]

다시 새로운 관측값을 받는다. 새로운 관측값 $p(z|x)$와 기존의 $bel(x)$의 확률 분포를 모두 고려해 새로운 $bel(x)$를 구할 수 있다.

![[Attachments/SLAM/Untitled 6.png]]

이러한 과정을 반복하면 로봇의 현재 위치를 알 수 있다.

state estimation을 위해서는 recursive 하게 이전 state 정보를 이용해주어야 하고, 이를 반영한 것이 Bayes Filter이다. 로봇의 이전 $bel(x)$ 값과 observation 값 $p(z|x)$를 활용해 현재의 $bel(x)$ 값을 나타낸다.

# 2. Bayes Filter 식 유도

---

식 유도 전, 확률에 대한 기본적인 지식을 Remind 하자.

<aside>
💡 **Bayes’ theorem**

![[Attachments/SLAM/Untitled 7.png]]

![[Attachments/SLAM/Untitled 8.png]]

**<Proof>**

![[Attachments/SLAM/Untitled 9.png]]

</aside>

<aside>
💡 **Markov Property/Assumption**
미래의 상태를 예측할 때, 현재의 상태에 대해서만 영향을 받고 그 이전 모든 과거의 상태에 대해서는 영향을 받지 않는다는 의미이다. 즉, 미래는 과거와 독립적인 확률 과정을 가진다.

</aside>

<aside>
💡 **Law of Total Probability
(x의 확률) = (x와 여러 y의 교집합의 확률들을 합친 것)**

조건부 확률 $p(x|y)$로부터 조건이 붙지 않은 전체 확률 $p(x)$를 구할 때 사용하는 법칙이다. Marginalization은 Law of Total Probability와 비슷한데 조건부 확률 대신 결합 확률을 사용했다는 차이점이 있다.

![[Attachments/SLAM/Untitled 10.png]]

</aside>

중요한 가정이 있다. **과거는 미래에 영향을 주지 않는다.**

- 그 사이의 state를 모른다면 dependent 할테지만, 우리를 현재 system의 state를 알고 있으므로 과거와 미래는 independent 하다.
- = 미래 command는 과거에 영향을 미치지 않는다.

**이제 Bayes Filter의 식을 유도해보자.**

- Input
    - observation $z$
    - control $u$
- Output
    - state $x$

![[Attachments/SLAM/Untitled 11.png]]

$t$번째 시간의 $bel(x_t)$를 정의한다. 정확한 위치가 아닌 확률분포로 나타낸다. 1부터 t까지의 observation과 control이 주어졌을 때, t 시점에서의 state 분포는 어떠한가를 묻는다.

![[Attachments/SLAM/Untitled 12.png]]

**Bayes’ Rule**을 적용한다. 아래처럼 풀어줄 수 있는데, $z_{1:t}$에서 $z_t$만 남기고 $z_{1:t-1}$은 뒤로 넘긴다. 이때 분모 부분은 이미 아는 값이므로 상수로 볼 수 있다. 따라서 Normalizing term $\eta$으로 바꾸어준다.

![[Attachments/SLAM/Untitled 13.png]]

![[Attachments/SLAM/Untitled 14.png]]

**Markov Assumption**을 적용해 밑줄친 부분으로 간략화한다. t 시점의 observation $z_t$를 구할 때 과거의 observation, control들($z_{1:{t-1}}, u_{1:{t-1}}$)은 고려하지 않아도 되며, $u_t$는 현재값이지만 $z$를 구하는데는 영향을 끼치지 않는다.

![[Attachments/SLAM/Untitled 15.png]]

**Law of Total Probability**를 적용해 두번째 Block의 식도 변형한다. Recursive form으로 만들어주기 위해 확률분포를 분리한다. $z, u$는 그대로 두고 $x_t$를 $x_{t-1}$로 분리한다.

![[Attachments/SLAM/Untitled 16.png]]

다시 **Markov Assumption**을 적용해 간략화한다. $x_t$를 구하는데 그 이전 값들($z_{1:{t-1}}, u_{1:{t-1}}$)은 고려하지 않는다.

![[Attachments/SLAM/Untitled 17.png]]

마지막 Block에서 과거 state $p(x_{t-1})$을 구할 때 현재의 control $u_t$는 영향을 미칠 수 없으므로(independent) 제거한다. (**Markov Assumption**)

![[Attachments/SLAM/Untitled 18.png]]

이전에 정의한 $bel(x_{t-1})$을 이용해 식을 recursive한 형태로 써준다.

Bayes Filter의 유도를 정리하면 아래와 같다.

![[Attachments/SLAM/Untitled 19.png]]

# 3. Bayes Filter의 개념적인 접근

---

Bayes Filter를 개념적으로 크게 두 가지로 분류할 수 있다.

![[Attachments/SLAM/Untitled 20.png]]

- Prediction Step : 이전 값의 $bel(x_{t-1})$과 현재 control command인 $u_t$를 고려해 **현재의 상태를 예측**한다.
- Correction Step : Prediction Step에서 구한 값과 현재 관찰되는 값 $z_t$로 정교하게 **상태 값을 조정**한다.

Prediction Step에서는 Motion Model을 이용하고, Correction Step에서는 Observation model을 이용한다.

Bayes Filter는 State estimation을 할 때 사용하는 수학적인 Framework 이다. Motion model 및 Observation model을 어떻게 정의하느냐, 확률 분포를 어떻게 가정하느냐, Parametric filter인가 Non-parametric filter인가 에 따라 다양하게 확장이 가능하다.

KF, EFK, Particle Filter 등이 Bayes Filter에 기반을 두고 있다.

**Kalman Filter & EKF**

- parametric
- Gaussians
- Linear of linearized model(taylor linearization, taylor approximation)

**Particle filter**

- Non-parametric
- Arbitrary models (sampling required)
    - Non-Gaussian까지 고려할 수 있으나 계산 복잡도가 높다.

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- Bayes filter

[베이즈 필터 (Bayes Filter)](https://gaussian37.github.io/autodrive-ose-bayes_filter/)

- 강의 정리

[Slam 6강 (Bayes Filter) 요약](https://taeyoung96.github.io/slam/SLAM_06/)

- Law of Total Probability

[[기초 통계] Law of Total Probability 란? (Marginalization과의 관계)](https://m.blog.naver.com/sw4r/221385006874)

- Bayes Rule (베이즈 룰)

[Bayes Rule (베이즈 룰) | Hyeongmin Lee's Website](https://hyeongminlee.github.io/post/bnn001_bayes_rule/)

- 베이즈 정리

[[확률과 통계] 14. 베이즈 정리, Bayes' Theorem / Bayes' Rule](https://blog.naver.com/mykepzzang/220834940797)