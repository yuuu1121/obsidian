# Importance Sampling

## 개요
Importance Sampling은 한 분포에서 얻은 샘플을 사용하여 다른 분포에 대한 기대값을 추정하는 기법이다. 강화학습의 Off-policy 학습에서 핵심적인 역할을 한다.

## 기본 원리

### 기대값 변환
분포 $p(x)$에서의 기대값을 분포 $q(x)$의 샘플로 추정:

$$E_p[f(x)] = \int f(x)p(x)dx = \int f(x)\frac{p(x)}{q(x)}q(x)dx = E_q\left[f(x)\frac{p(x)}{q(x)}\right]$$

### Importance Weight
$$w(x) = \frac{p(x)}{q(x)}$$

## 강화학습에서의 적용

### Off-Policy Learning
행동 정책(behavior policy) $\mu$로 수집한 데이터로 목표 정책(target policy) $\pi$ 학습

$$E_\pi[G_t] = E_\mu\left[\prod_{k=t}^{T-1}\frac{\pi(A_k|S_k)}{\mu(A_k|S_k)} G_t\right]$$

### Importance Sampling Ratio
$$\rho_{t:T-1} = \prod_{k=t}^{T-1}\frac{\pi(A_k|S_k)}{\mu(A_k|S_k)}$$

## 분산 문제

### Ordinary Importance Sampling
$$V(s) = \frac{\sum_{t \in \mathcal{T}(s)} \rho_{t:T(t)-1} G_t}{|\mathcal{T}(s)|}$$
- 편향 없음
- 분산이 클 수 있음 (무한대 가능)

### Weighted Importance Sampling
$$V(s) = \frac{\sum_{t \in \mathcal{T}(s)} \rho_{t:T(t)-1} G_t}{\sum_{t \in \mathcal{T}(s)} \rho_{t:T(t)-1}}$$
- 편향 있음 (점근적으로 0)
- 분산이 낮음

## 분산 감소 기법

### Per-decision Importance Sampling
전체 trajectory 대신 각 결정 단위로 계산

### Truncated Importance Sampling
$$\bar{\rho} = \min(\rho, c)$$

### Retrace($\lambda$)
$$\rho_t = \min\left(1, \frac{\pi(a_t|s_t)}{\mu(a_t|s_t)}\right)$$

## 사용 예시
```python
def importance_sampling_return(trajectory, target_policy, behavior_policy):
    rho = 1.0
    G = 0.0
    for (s, a, r) in reversed(trajectory):
        rho *= target_policy(s, a) / behavior_policy(s, a)
        G = r + gamma * G
    return rho * G
```

## 관련 개념
- [[Off-Policy Learning]]
- [[Experience Replay]]
- [[Temporal Difference]]
