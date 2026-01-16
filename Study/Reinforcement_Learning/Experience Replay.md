# Experience Replay

## 개요
Experience Replay는 에이전트의 경험(transition)을 버퍼에 저장하고, 학습 시 무작위로 샘플링하여 사용하는 기법이다. DQN에서 처음 도입되어 Deep RL의 안정성을 크게 향상시켰다.

## 동기

### 문제점 (Experience Replay 없이)
1. **샘플 간 상관관계**: 연속적인 경험은 강하게 상관됨 → i.i.d. 가정 위반
2. **데이터 비효율**: 한 번 경험하면 버려짐
3. **Catastrophic Forgetting**: 최근 경험에만 집중

## 작동 방식

### 1. 저장
Transition $(s_t, a_t, r_t, s_{t+1})$을 Replay Buffer $\mathcal{D}$에 저장

### 2. 샘플링
Buffer에서 무작위로 mini-batch 추출

### 3. 학습
샘플링된 batch로 네트워크 업데이트

```python
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
```

## 장점

1. **상관관계 제거**: 무작위 샘플링으로 i.i.d. 근사
2. **데이터 효율성**: 같은 경험을 여러 번 학습
3. **안정성**: 급격한 정책 변화 방지

## 변형

### Prioritized Experience Replay (PER)
TD-error가 큰 경험에 높은 우선순위
$$P(i) = \frac{p_i^\alpha}{\sum_k p_k^\alpha}$$

### Hindsight Experience Replay (HER)
실패한 경험도 다른 목표에 대해 성공으로 재해석

### Combined Experience Replay
온라인 경험과 전문가 데모 혼합

## 하이퍼파라미터

| 파라미터 | 일반적 값 | 설명 |
|----------|-----------|------|
| Buffer Size | 10,000 ~ 1,000,000 | 저장 용량 |
| Batch Size | 32 ~ 256 | 학습 단위 |
| 학습 시작 | 1,000 ~ 10,000 | 최소 저장량 |

## 관련 개념
- [[Deep Q-Network]]
- [[Temporal Difference]]
- [[Importance Sampling]]
