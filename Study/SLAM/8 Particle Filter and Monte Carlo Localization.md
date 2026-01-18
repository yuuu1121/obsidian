# 8. Particle Filter and Monte Carlo Localization

# 1. Particle Filter

---

Recursive filter는 다양한 종류가 있다.

- KF, EKF : Gaussian 분포 형태의 parametric probability distribution approach
    - KF : Gaussian, LInear
    - EKF : Non-Linear → Linear로 선형화
- Particle Filter : particle, sample, pose hypothesis라고 불리는 sample-based approach
    - Non-Gaussian → Gaussian
    - arbitrary distribution
    - 그러나 복잡도가 높다.
- Discrete Filter

Particle Filter는 particle set을 사용해 본인의 위치를 파악한다. Gaussian distribution을 가정하는 Kalman Filter와 달리, Particle Filter는 arbitrary distribution도 다룰 수 있다. **하나의 particle을 하나의 guess(hypothesis)로 볼 수 있다.** arbitrary distribution을 표현하기 위해 multiple sample을 사용한다.

## Frequency vs. Weight

![[Attachments/SLAM/Untitled.png]]

특정 area에 sample이 몇 개 있는지 센다. particle은 확률 밀도의 approximation으로 볼 수 있다. 각 샘플은 아주 작은 probability mass로 본다. (특정 지역에 있는 샘플의 수) = (그 지역의 확률)을 나타낸다.

큰 weight는 큰 probability mass를 뜻한다. 위 사진의 경우 모든 샘플이 같은 uniform weight j를 가진다. 만약 특정 샘플이 더 큰 가중치를 가진다면 아래 그림과 같이 해당 분포를 표현하기 위해 더 적은 샘플이 필요할 것이다. 즉, 우리는 높은 확률을 표현하기 위해 많은 수의 샘플을 사용하는 대신 더 큰 (가중치를 가진) 샘플을 사용할 수 있다.

![[Attachments/SLAM/Untitled 1.png]]

(frequency vs weight) : 위 사진은 frequency, 아래 사진은 weight를 이용해서 확률 분포를 나타낸 것이다. particle filter의 resampling 단계와 비슷하다. 우리는 주로 weighted sample을 사용하게 될 것이다. 하지만 이렇게 샘플로 표현하는 것은 approximation에 불과하다. 따라서 함수를 잘 표현하려면 많은 수의 샘플이 있어야 한다. (이론적으로는 그렇지만 실제로는 또 그렇지만도 않다.)

- Control Command를 이용해서 Prediction : Sampling from proposal
- Sensor observation 이용해서 Correction : Importance weight, Resampling

## Particle Set

각 샘플은 두 변수 $x, w$를 가진다. 모든 가중치는 하나로 더했을때 1이다.

• $x$ : 이 샘플이 어디 있는지 (1D/2D/3D Vector)
• $w$ : weight (Real number)

![[Attachments/SLAM/Untitled 2.png]]

p(x)는 direct impulse들의 weighted sum을 나타낸다. 각 샘플 위치에서 direct impulse가 존재한다. (normalized, approximation X)

approximation function은 어떻게 생겼을까?

![[Attachments/SLAM/Untitled 3.png]]

왼쪽은 가우시안 분포이고, 200~300개의 샘플이 있다. 오른쪽은 가우시안 분포가 아니다. 샘플의 분포에서 확연히 차이가 난다.

arbitrary function에서 closed-form sample을 쉽게 사용할 수 없다. 다시말해 finite number 이용하여 표현하기 힘들다. 가능한 방법은 closed form으로 샘플링하거나, efficiency lists을 샘플링할 수 있는 몇몇 함수가 있다. 만약 uniform distribution이라면 uniform random number를 생성하고, 가우시안 분포라면 평균 근처에서 더 많은 샘플 생성해야 할 것이다.

이처럼 Closed Form Sampling은 소수의 distribution에 대해서만 가능한데, Gaussian은 그 한 예시이다. 아래 방법을 이용해 우리는 샘플링을 더 쉽게 할 수 있다.

![[Attachments/SLAM/Untitled 4.png]]

(-standard deviation ~ standard deviation) 범위의 12개의 랜덤값을 다 더하고 2로 나눈다. 그러면 거의 가우시안 분포와 비슷하다(Approx.). 이는 가우시안 분포 형성하는 가장 쉬운 방법이다.

다른 임의의 분포에 대해서는 어떻게 해야할까?  **Importance Sampling Principle**을 이용한다. 

![[Attachments/SLAM/Untitled 5.png]]

- $f$ : target
- $g$ : proposal
- pre-condition(가정) :  $f(x)>0$ →  $g(x)>0$
    - 확률이 0이면 샘플 생성 불가능 하고, 가중치 계산할때 $g$로 나누어야 하는데 0이면 정의 X

mistake($f$와 $g$의 차이)를 보상함으로써 $f$의 샘플을 생성하기 위해 다른 distibution $g$를 사용할 수 있다. weight $w=\frac{f}{g}$를 이용해 $f$와 $g$의 차이를 계산한다. ($f$와 $g$의 point-wise evaluate)

즉 **closed form에서 샘플하지 못하는, 가우시안 분포가 아닌 function 을 표현 하기 위해 가우시안을 분포를 사용할 수 있다**. 이를 이용해 particle filter에서 state estimation을 한다.

# 2. Particle Filter Algorithm by 칼만필터링 수업

---

3번에서 Cyrill 교수님이 강의에서 알려준 Particle Filter를 보기에 앞서, 칼만필터링 수업에서 배운 내용을 토대로 전체적인 알고리즘을 이해하면 좋을 것 같다.

**System equation과 Measurement equation은 아래와 같다.** $w_k$는 system noise, $v_k$는 measurement noise이다.

![[Attachments/SLAM/Untitled 6.png]]

**Particle Filter의 알고리즘**은 아래와 같다.

![[Attachments/SLAM/Untitled 7.png]]

**Resampling 과정**은 아래와 같다. 이는 아래에서 다룰 Roulette Wheel에 대한 설명이다.

![[Attachments/SLAM/Untitled 8.png]]

예를 들어 w1=0.1, w2=0.1, w3=0.7 이고 첫번째 랜덤 넘버가 0.7이면 w1+w2+w3=0.9 가 되어야 rabdom number 를 넘으므로 첫번째 particle은 이전의 세번째 particle로 업데이트 된다. 두번째 랜덤 넘버가 0.1이면 두번째 particle은 이전의 두 번째 particle로 업데이트 된다. 세번째 랜덤 넘버가 0.5이면 세번째 particle은 이전의 세 번째 particle로 업데이트 된다. 이런 식으로 업데이트 해주면 **확률적으로 큰 weight를 가진 particle이 업데이트 된다.** 여기에 노이즈를 추가하여 조금 다른 particle이 될 수도 있다. 다만 이 방식은 뒤에 있는 particle들이 업데이트 되지 않는다는 단점이 있고, 이를 해결하기 위해 다른 샘플링 방식들을 사용할 수 있다.

$$
x^+_{k,i}=x^-_{k,j} \text{ with probability }w_j
$$

# 3. Particle Filter Algorithm by Cyrill Lecture

---

Dynamic State Estimation Problems에서 Particle Filter를 어떻게 사용하는지 살펴보자. Recursive Bayes filter이며, Non-parametric approach 이다. 샘플들의 distribution을 모델링한다. Bayes 필터이므로 prediction 단계에서 motion model 사용하고. correction step에서 observation 모델 사용한다. target과 proposal의 비율의 가중치를 주어 correction을 진행한다. **더 많은 샘플 사용할수록 더 근사화 잘 할 수 있다!**

Particle Filter의 알고리즘을 살펴보자.

![[Attachments/SLAM/Untitled 5.png]]

(1) **Proposal Step = Prediction Step** : proposal distribution 이용해 particle을 샘플링한다. (user-defined choice)

- proposal로부터 sample을 그린다.(blue line)
- red line의 proposal은 flatform의 motion의 bayesian 예측값과 관련 있다.

![[Attachments/SLAM/Untitled 9.png]]

(2) **Correction Step** : importance weights를 계산한다.

- observation model을 통해 weight을 얻고 miss match 된 값을 보상한다.

![[Attachments/SLAM/Untitled 10.png]]

(3) **Resampling** : sample $i$의 확률을 $w^{[j]}_t$로 둔다. $J$번 반복한다. 샘플이 유한하므로 가중치가 너무 작아 0에 가까운 것은 없앤다. 샘플이 무한하게 있다면 무시해도 되는 단계이다.

→ finite sample의 수가 제한적이면 전체 분포에서 샘플 하나가 나타내는 contribution이 매우 적다. 다음 time step에서 하용할 샘플을 고를때 높은 확률을 가진 샘플들을 골라 resampling 함으로써 frequency에 의한 weighting으로 대체하는 게 전체 확률 분포를 다루는 데 더 좋다.

## Particle Filter Psudo Code

![[Attachments/SLAM/Untitled 11.png]]

LINE 3 : Prediction belief from my sample proposal

LINE 4 : weight 계산

LINE 5 : add weighted sample set as new temporary sample set

LINE 7~10 : Resampling : frequency weight를 가진 uniform weight sample을 얻을 수 있다.

# 4. Monte Carlo Localization

---

particle filter 이용해 “Where Am I?” 문제를 풀어 플랫폼의 위치와 방향을 추정한다.

![[Attachments/SLAM/Untitled 12.png]]

실제 로봇이 있는 곳이 가장 큰 확률이지만, 그럼에도 다른 곳에도 샘플이 있다. 우리는 particle 얼마나 믿을 수 있는가?

![[Attachments/SLAM/Untitled 13.png]]

particle filter는 한 샘플을 골라 pose hypothesis로 둔다. 모든 hypothesis는 자기가 실제 로봇이 존재하는 곳이라고 가정하고 가중치를 준다. 이때 모든 가설이 자신이 맞고 다른 가설이 틀렸다고 생각한다. 수많은 가설이 모이면 더 정확한 값 찾을 수 있다.

Monte Carlo Localization에서 각 particle은 pose hypothesis이다.

- **Proposal 은 motion model 이다.**
    - $u_t$가 1m 전진이면 $x_t$는 approximately 1m 전진한다.(sampling 이므로 99cm일수도, 2m일수도, 1m 33cm일수도 있다.)
    - 즉 예측 모델의 불확실성을 높인다.

$$
x^{[j]}_t \sim p(x_t|x_{t-1},u_t)
$$

- **Correction 은 observation model을 통해 이루어진다.**
    - 모든 샘플은 자신이 맞다고 생각하므로 observation model은 계산하기 쉽다. 구한 observation model로 weight를 구하면 아래와 같다.

$$
w^{[j]}_t =\frac{target}{proposal}\propto   p(z_t|x_{t},m)
$$

## Particle Filter for Localization Psudo Code

![[Attachments/SLAM/Untitled 14.png]]

## 1D Example

![[Attachments/SLAM/Untitled 15.png]]

## Resampling

sample $i$의 확률을 $w^{[i]}_t$로 둔다. $J$번 반복한다. unlikely sample을 more likely sample로 대체한다. $J=n$=(샘플의 개수) 이다.

![[Attachments/SLAM/Untitled 16.png]]

![[Attachments/SLAM/Untitled 17.png]]

weight를 0~1 사이로 normalize 시키고 룰렛처럼 원으로 나타낸다.

- Roulette wheel은 화살표 한 개가 돌아가다가 멈췄을 때 그 점을 선택한다. 이해하기 쉬우나, 현실에서는 suboptimal 하다.
    - 0~1사이의 값을 가진 random number가 해당하는 위치를 찾기 위해 Binary serach
        
        ![[Attachments/SLAM/Untitled 18.png]]
        
- Stochastic universal sampling은 arrow를 n개 사용한다. 각 arrow 사이의 거리는 1/J이다. n개의 화살표를 돌려 끝나는 것들을 선택한다. **Low variance sampling**이기 때문에 계산 복잡도가 낮아 빠르다.
    - 1~1/J 사이의 값을 가진 random number 구한다.
    - binary search 할 필요 없이 linear 한 time만 걸리기 때문에 roulette wheel 보다 빠르다.

**모든 샘플이 같은 가중치를 가진다면** 무슨 일이 일어날까? 센서가 정말 안 좋아서 모두가 같은 가중치를 가진다면, observation은 아무 정보를 가지지 못하고 resamplilng step에서는 duplicated 되어 died out된다. 따라서 어느 점이 더 좋은지 모른다. 이런 상황에서도 여러 샘플 동시에 선택하면 같은 sample set을 계속 reproducing 하여 경향성(Resampling 한 후에도 샘플들이 순서대로 정렬되어 있기 때문에 “센서의 값들이 아무런 정보를 반영하지 못하고 있다”는 경향성 확인 가능)을 확인할 수 있다. 따라서 **Low variance stochastic univercial sampling을 resampling 할 때 많이 사용한다.** 또한 operation의 complexity도 낮다.

Sampling 구현 방법은 아래와 같다.

![[Attachments/SLAM/Untitled 19.png]]

![[Attachments/SLAM/Untitled 20.png]]

## MCL 적용 로봇

![[Attachments/SLAM/Untitled 21.png]]

## MCL 특징

- Pros
    - Handles non-Gaussian distributions
    - Works well in low-dimensional spaces
    - Can elegantly handle data association ambiguities
    - Can easily incorporate different sensing modalities
    - Comparably robust
    - Easy to implement
- Cons
    - Problematic in high-dimensional spaces
    - Problematic in situations with high uncertainty
    - Parcicle depletion problem
- Variants : particle filter 알고리즘의 variants
    - Real-Time particle filters : 다른 frame rate에서의 센서 데이터 다룸
    - Delayed state particle filters : 센서 데이터 stream의 substantial delays 다룸
    - Rao-Blackwellized particle filters : high-dimensional state spaces를 다룬다.

# 4. Summary

**[Particle Filter]**

Particle filter는 non-parametric, recursive Bayes filter이다. weighted samples의 set으로 Posterior를 표현할 수 있다. t+1의 샘플을 예측(proposal) 하고 proposal과 target의 차이를 계산해 가중치를 둔다. Particle filter는 적절한 motion 및 센서 모델을 설계한다.

- 장점

Non-Gaussien 분포를 표현할 수 있으며, 낮은 차원에서 잘 동작하며 비교적 robust 하다. data association ambiguities를 다룰 수 있으며 구현하기 쉽다(different modality).

- 단점

Particle의 dimension이 커지면 모호성도 커진다. 2차원 까지는 괜찮지만 높은 차원의 공간에서 좋지 않다. particle 수가 너무 적으면 particle depletion problem이 있다.

**[PF Localization(Monte-Carlo localization, MCL)]**

Particle들은 motion model에 따라 전파된다. observation의 likelihood에 따라 weighted된다. 이는 Monte-Carlo localization(MCL)이라고 불린다. MCL은 실내 모바일 로봇 위치 측위에서 gold standard이다.

# **Reference**

---

- Cyrill 교수님 강의
- SLAMDUNK Season2
- Importance Sampling

[중요 샘플링 (Importance Sampling)](https://pasus.tistory.com/52)