# Normalization (정규화)

## 개요
Normalization은 데이터나 특성(feature)의 범위를 일정한 범위로 조정하는 기법이다. 신경망 학습의 안정성과 속도를 개선하는 데 중요한 역할을 한다.

## 종류

### 1. Data Normalization

#### Min-Max Normalization
데이터를 [0, 1] 범위로 변환
$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

#### Z-score Normalization (Standardization)
평균 0, 표준편차 1로 변환
$$x_{std} = \frac{x - \mu}{\sigma}$$

### 2. Layer Normalization (신경망)

#### Batch Normalization
미니배치 단위로 정규화
$$\hat{x} = \frac{x - \mu_{batch}}{\sqrt{\sigma_{batch}^2 + \epsilon}}$$

- 장점: 학습 안정화, Internal Covariate Shift 감소
- 단점: 배치 크기에 의존, 추론 시 별도 처리 필요

#### Layer Normalization
단일 샘플 내 모든 뉴런에 대해 정규화
$$\hat{x} = \frac{x - \mu_{layer}}{\sqrt{\sigma_{layer}^2 + \epsilon}}$$

- 장점: 배치 크기 무관, RNN에 적합

#### Instance Normalization
각 채널별로 독립적 정규화 (Style Transfer에 주로 사용)

#### Group Normalization
채널을 그룹으로 나누어 정규화

## Batch Normalization vs Layer Normalization

| 특성 | Batch Norm | Layer Norm |
|------|-----------|------------|
| 정규화 방향 | 배치 방향 | 특성 방향 |
| 배치 크기 의존성 | 있음 | 없음 |
| 주 사용처 | CNN | Transformer, RNN |
| 추론 시 | running mean/var 사용 | 실시간 계산 |

## 사용 예시 (PyTorch)
```python
import torch.nn as nn

# Batch Normalization
bn = nn.BatchNorm2d(num_features=64)

# Layer Normalization
ln = nn.LayerNorm(normalized_shape=[64, 32, 32])

# Group Normalization
gn = nn.GroupNorm(num_groups=8, num_channels=64)
```

## 관련 개념
- [[Activation Function]]
- [[Regularization]]
- [[Back Propagation]]
