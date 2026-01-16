# Downsampling

## 개요
Downsampling은 데이터의 크기나 해상도를 줄이는 기법이다. 이미지 처리, 포인트 클라우드 처리, 신호 처리 등 다양한 분야에서 사용된다.

## 종류

### 1. 이미지 Downsampling

#### Nearest Neighbor
가장 가까운 픽셀 값 사용
- 장점: 빠름
- 단점: 계단 현상 (aliasing)

#### Bilinear Interpolation
주변 4개 픽셀의 선형 보간
$$f(x,y) = \sum_{i,j} w_{ij} f(i,j)$$

#### Bicubic Interpolation
주변 16개 픽셀 사용, 더 부드러운 결과

#### Max Pooling / Average Pooling
CNN에서 feature map 크기 축소
```python
nn.MaxPool2d(kernel_size=2, stride=2)
nn.AvgPool2d(kernel_size=2, stride=2)
```

### 2. 포인트 클라우드 Downsampling

#### [[Voxel]] Grid Downsampling
공간을 voxel로 나누고 각 voxel에서 대표점 선택
```python
import open3d as o3d
pcd_down = pcd.voxel_down_sample(voxel_size=0.05)
```

#### Random Sampling
무작위로 점 선택

#### Farthest Point Sampling (FPS)
가장 멀리 떨어진 점을 순차적으로 선택

### 3. 데이터 Downsampling (Class Imbalance)

#### Random Under-sampling
다수 클래스에서 무작위로 샘플 제거

#### Tomek Links
경계 근처의 다수 클래스 샘플 제거

#### NearMiss
소수 클래스와 가까운 다수 클래스 샘플만 유지

## Pooling in CNN

| 종류 | 특징 | 용도 |
|------|------|------|
| Max Pooling | 최대값 선택 | 특징 추출 |
| Average Pooling | 평균값 계산 | 전역 정보 |
| Global Average Pooling | 채널별 평균 | FC layer 대체 |

## 관련 개념
- [[Voxel]]
- [[Class Imbalance]]
- [[보간법(Interpolation)]]
