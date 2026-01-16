# K-means Clustering

## 개요
K-means는 데이터를 K개의 클러스터로 분할하는 비지도 학습 알고리즘이다. 각 클러스터는 centroid(중심점)로 대표되며, 데이터 포인트는 가장 가까운 centroid에 할당된다.

## 알고리즘

### 1. 초기화
K개의 centroid를 무작위로 선택

### 2. 할당 (Assignment)
각 데이터 포인트를 가장 가까운 centroid에 할당
$$c_i = \arg\min_k \|x_i - \mu_k\|^2$$

### 3. 업데이트 (Update)
각 클러스터의 centroid를 재계산
$$\mu_k = \frac{1}{|C_k|}\sum_{x_i \in C_k} x_i$$

### 4. 반복
수렴할 때까지 2-3 반복

## 목적 함수
$$J = \sum_{k=1}^{K}\sum_{x_i \in C_k} \|x_i - \mu_k\|^2$$

## K 선택 방법

### Elbow Method
K에 따른 inertia(클러스터 내 분산) 그래프에서 elbow point 찾기

### Silhouette Score
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
- $a(i)$: 같은 클러스터 내 평균 거리
- $b(i)$: 가장 가까운 다른 클러스터와의 평균 거리

## 장단점

### 장점
- 구현이 간단
- 대용량 데이터에 효율적
- 결과 해석 용이

### 단점
- K를 미리 지정해야 함
- 초기값에 민감
- 구형 클러스터 가정
- Outlier에 민감

## 사용 예시
```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)
centroids = kmeans.cluster_centers_
```

## K-means++ 초기화
더 나은 초기 centroid 선택
1. 첫 centroid는 무작위 선택
2. 다음 centroid는 기존 centroid와 멀리 떨어진 점 선택 (확률적)

## 관련 개념
- [[Clustering Algorithms]]
- [[Distance]]
- [[Euclidean Clustering]]
- [[Gaussian Mixture Model]]
