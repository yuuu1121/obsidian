# Factor Analysis (요인 분석)

## 개요
Factor Analysis는 관측된 변수들 사이의 상관관계를 소수의 잠재 요인(latent factor)으로 설명하는 통계 기법이다. [[Dimensionality Reduction]]의 한 방법으로, [[Principal Component Analysis]]와 관련이 깊다.

## 모델

### 수식
$$\mathbf{x} = \boldsymbol{\mu} + \mathbf{\Lambda}\mathbf{f} + \boldsymbol{\epsilon}$$

- $\mathbf{x}$: 관측 변수 (p차원)
- $\mathbf{f}$: 잠재 요인 (k차원, k << p)
- $\mathbf{\Lambda}$: 요인 부하량 행렬 (p × k)
- $\boldsymbol{\epsilon}$: 고유 오차 (unique factor)

### 가정
- $\mathbf{f} \sim N(0, \mathbf{I})$
- $\boldsymbol{\epsilon} \sim N(0, \boldsymbol{\Psi})$, $\boldsymbol{\Psi}$는 대각 행렬
- $\mathbf{f}$와 $\boldsymbol{\epsilon}$은 독립

## 공분산 구조
$$\mathbf{\Sigma} = \mathbf{\Lambda}\mathbf{\Lambda}^T + \boldsymbol{\Psi}$$

## PCA vs Factor Analysis

| 특성 | PCA | Factor Analysis |
|------|-----|-----------------|
| 목적 | 분산 최대화 | 공분산 설명 |
| 오차 | 없음 | 고유 오차 존재 |
| 요인 | 관측 변수의 선형 결합 | 잠재 변수 |
| 해석 | 기술적 | 인과적 |

## 요인 추출 방법

### 1. 주축 요인법 (Principal Axis Factoring)
공통분산만 분석

### 2. 최대우도법 (Maximum Likelihood)
모수 추정에 적합

### 3. 최소잔차법 (Minimum Residual)
잔차 최소화

## 요인 회전

### Orthogonal Rotation
- **Varimax**: 각 요인의 분산 최대화
- **Quartimax**: 각 변수의 요인 부하량 단순화

### Oblique Rotation
- **Promax**: 요인 간 상관 허용
- **Oblimin**

## 요인 수 결정

1. **Kaiser 기준**: 고유값 > 1
2. **Scree Plot**: elbow point
3. **평행 분석**: 무작위 데이터와 비교

## 예시 (Python)
```python
from sklearn.decomposition import FactorAnalysis

fa = FactorAnalysis(n_components=3)
fa.fit(X)
loadings = fa.components_.T
factors = fa.transform(X)
```

## 응용
- 심리학: 성격 요인 분석
- 마케팅: 소비자 선호 분석
- 금융: 위험 요인 식별

## 관련 개념
- [[Principal Component Analysis]]
- [[Dimensionality Reduction]]
- [[Latent Variable]]
