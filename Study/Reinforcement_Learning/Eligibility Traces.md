# Eligibility Traces

## 개요
Eligibility Traces는 Monte Carlo와 Temporal Difference(TD) 방법을 통합하는 메커니즘이다. 최근 방문한 상태들에 대한 "자격"을 추적하여 TD 에러를 과거 상태들에 분배한다.

## 핵심 아이디어

### TD(0) vs Monte Carlo
- **TD(0)**: 1-step 부트스트래핑, 분산 낮음, 편향 있음
- **Monte Carlo**: 전체 에피소드 사용, 편향 없음, 분산 높음
- **TD(λ)**: 두 방법을 λ로 보간

## Eligibility Trace 정의

각 상태에 대한 자격 $e_t(s)$:

### Accumulating Traces
$$e_t(s) = \begin{cases} \gamma \lambda e_{t-1}(s) + 1 & \text{if } s = S_t \\ \gamma \lambda e_{t-1}(s) & \text{otherwise} \end{cases}$$

### Replacing Traces
$$e_t(s) = \begin{cases} 1 & \text{if } s = S_t \\ \gamma \lambda e_{t-1}(s) & \text{otherwise} \end{cases}$$

## TD(λ) 알고리즘

### Forward View (λ-return)
$$G_t^\lambda = (1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}G_t^{(n)}$$

### Backward View
```
Initialize e(s) = 0 for all s
For each step:
    δ = r + γV(s') - V(s)      # TD error
    e(s) = e(s) + 1             # 현재 상태 자격 증가
    For all s:
        V(s) = V(s) + αδe(s)    # 자격에 비례하여 업데이트
        e(s) = γλe(s)           # 자격 감소
```

## λ 값의 영향

| λ | 특성 |
|---|------|
| 0 | TD(0)와 동일, 1-step |
| 1 | Monte Carlo와 동일 |
| 0.9 | 일반적으로 좋은 성능 |

## 장점

1. **빠른 학습**: 과거 상태도 즉시 업데이트
2. **유연성**: λ로 bias-variance 조절
3. **온라인 학습**: 에피소드 종료 전에 학습 가능

## SARSA(λ) 예시
```python
def sarsa_lambda(env, episodes, alpha, gamma, lambda_):
    V = defaultdict(float)

    for episode in range(episodes):
        e = defaultdict(float)  # eligibility traces
        s = env.reset()
        a = policy(s)

        while not done:
            s_, r, done = env.step(a)
            a_ = policy(s_)

            delta = r + gamma * V[s_] - V[s]
            e[s] += 1

            for state in e:
                V[state] += alpha * delta * e[state]
                e[state] *= gamma * lambda_

            s, a = s_, a_
```

## 관련 개념
- [[Temporal Difference]]
- [[Monte Carlo Methods]]
- [[SARSA]]
- [[Q-Learning]]
