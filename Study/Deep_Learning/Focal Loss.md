# Focal Loss

## 개요
Focal Loss는 [[Class Imbalance]] 문제를 해결하기 위해 제안된 손실 함수이다. RetinaNet 논문에서 처음 소개되었으며, 쉬운 샘플의 기여도를 줄이고 어려운 샘플에 집중하도록 설계되었다.

## 수식

### Cross Entropy Loss
$$CE(p_t) = -\log(p_t)$$

### Focal Loss
$$FL(p_t) = -\alpha_t(1-p_t)^\gamma \log(p_t)$$

- $p_t$: 정답 클래스의 예측 확률
- $\alpha_t$: 클래스 가중치 (class imbalance 조절)
- $\gamma$: focusing parameter (보통 2 사용)

## 작동 원리

### $(1-p_t)^\gamma$ 효과
- **잘 분류된 샘플** ($p_t \approx 1$): $(1-p_t)^\gamma \approx 0$ → loss 기여도 감소
- **잘못 분류된 샘플** ($p_t \approx 0$): $(1-p_t)^\gamma \approx 1$ → loss 기여도 유지

### $\gamma$ 값에 따른 변화
| $\gamma$ | 효과 |
|----------|------|
| 0 | Cross Entropy와 동일 |
| 1 | 약한 focusing |
| 2 | 일반적으로 사용 |
| 5 | 강한 focusing |

## 장점
1. **Hard Example Mining 자동화**: 어려운 샘플에 자동으로 집중
2. **Class Imbalance 해결**: 다수 클래스의 easy negative 영향 감소
3. **One-stage Detector 성능 향상**: [[1-Stage Detector]]에서 특히 효과적

## 사용 예시
```python
import torch
import torch.nn.functional as F

def focal_loss(pred, target, gamma=2.0, alpha=0.25):
    ce_loss = F.cross_entropy(pred, target, reduction='none')
    pt = torch.exp(-ce_loss)
    focal_weight = alpha * (1 - pt) ** gamma
    return (focal_weight * ce_loss).mean()
```

## 관련 개념
- [[Class Imbalance]]
- [[Loss Function]]
- [[1-Stage Detector]]
- [[2-Stage Detector]]
