---
date: 2024-08-04
status: Permanent
tags:
  - Study/Camera/3D-Reconstruction
  - Project/Stereo2PCD
aliases:
  - Semi-Global Block Matching
  - Stereo SGBM
  - Disparity map
keywords:
  - Stereo SGBM
  - Disparity map
  - Semi-Global Block Matching
reference: 
author: 
url: 
dg-publish: true
---
- [[Disparity Map (작성중)|Disparity Map]]을 생성하기 위한 OpenCV 기반 Semi-global block matching 알고리즘

<br/>

# Algorithm Analysis
```python
cv2.stereoSGBM_create(minDisparity, numDisparities, blockSize, P1, P2, disp12MaxDiff, preFilterCap, uniquenessRatio, speckleWindowSize, speckleRange, mode)
```

- `minDisparity`
	- 최소 시차(Disparity) 값 (default: 0)
	- 시차와 깊이(Depth)는 반비례 관계를 가지기 때문에 최대 깊이 값을 제한하는 것과 같은 효과를 가짐 ([[Study/Sensors/Stereo Camera/Stereo Camera Depth Estimation#Depth Estimation|Depth Estimation]])
- `numDisparities`
	- 최소, 최대 시차의 차이 값
	- 항상 0보다 커야하며, 16 배수
	- Depth estimation에서 Depth range 제한
- `blockSize`
	- [[Disparity Map (작성중)#Block Matching|Block Matching]]에 사용되는 블록의 크기
	- 홀수이어야 하며, 항상 1 이상 (보통 3~11 사이 값)
	- 작은 `blockSize`는 연산량이 작고 디테일을 잘 포착하지만 노이즈에 민감하며, 큰 `blockSize`는 연산량이 많고 디테일을 높칠 수 있지만 노이즈에 강인함 
- `P1`, `P2`
	- 시차의 부드러움을 제어하는 파라미터
	- 일반적인 `P1`, `P2` 의 값
	  `P1`: $8\times image\text{ }channels\times blockSize^2$
	  `P2`: $32\times image\text{ }channels\times blockSize^2$
	- 인접한 픽셀 간의 시차가 급격하게 변하는 것을 막고, 결과를 부드럽게 만들기 위한 패널티 값
- `disp12MaxDiff`
	- 좌우 시차 체크에서 허용되는 최대 차이 (비활성화: 0)
	- 좌우 이미지를 기준으로 각각 시차 맵 $D_{L2R}$, $D_{R2L}$를 계산한 후, 두 시차 맵 간의 최대 허용 차이를 설정
- `preFilterCap`
	- Stereo matching을 수행하기 전에 이미지의 노이즈를 줄이고 엣지나 텍스처를 명확하게 강조하기 위해 사용
	- 각 픽셀의 $x$ 축 방향 기울기(Gradient)를 계산하고 이 값을 [-`preFilterCap`, `preFilterCap`] 범위로 제한
- `uniquenessRatio`
	- 특정 픽셀에 애해 여러 대응 후보군 중 최저 비용 함수 값이 두 번째로 좋은 값보다 얼마나 더 좋은지를 백분율로 나타내는 마진
	- 애매모호한 매칭을 걸러내는데 사용되며, 일반적으로 5~15 사이 값    
- `speckleWindowSize`
	- 잡음 영역(Noise speckle)로 간주되는 연결된 픽셀 영역의 최대 크기
		- 예를 들어 `speckleWindowSize`가 100으로 설정되면, 100 픽셀 이하로 연결된 시차 영역을 잡음으로 간주되어 제거됨
	- 비활성화하려면 0으로 설정, 그렇지 않을 경우 일반적으로 50~200 사이 값
- `speckleRange`
	- 시차 맵의 특정 연결된 영역 내에서 시차 값의 최대 허용 변화 값
	- `speckleRange`를 양수로 설정하면, 이 값에 16이 곱해지며, 일반적으로 1 또는 2를 사용
- `mode`
	- `cv2.STEREO_SGBM_MODE_SGBM`
		- 표준 Semi-global block matching(SGBM) 알고리즘 사용
		- 블록 매칭과 전역 최적화를 결합하여 시차 맵 계산
	- `cv2.STEREO_SGBM_MODE_HH`
		- Heikkilä-Hämeri(SGBM HH) 알고리즘 사용
		- 2 패스 동적 프로그래밍 알고리즘을 사용하여 시차 맵을 더욱 정밀하게 계산
		- 메모리 사용량이 증가하지만, 더 정확한 결과 제공
		- 고해상도 이미지나 높은 정확도가 필요한 경우 적합
	- `cv2.STEREO_SGBM_MODE_SGBM_3WAY`
		- 3-way SGBM 모드를 사용하여 시차 맵 계산
		- 3 방향(좌-우, 우-좌, 위-아래)으로 최적화를 수행하여 시차 맵 계산
		- 더 높은 정확도를 제공하지만, 메모리 사용량과 연산 시간 매우 큼
	- `cv2.STEREO_SGBM_MODE_HH4`
		- 4-way Heikkilä-Hämeri(SGBM HH) 모드를 사용하여 시차 맵 계산
		- 최고 수준의 정확도 제공

>[!note]- Disparity vs Baseline, Resolution
>- Disparity vs Baseline
>  $$Disparity=\frac{f\cdot Baseline}{z}$$
>	- Disparity와 Baseline은 비례 관계이므로 Baseline이 멀어질수록 `minDisparity`와 `numDisparities`를 크게 설정해야 함
>- Disparity vs Resolution
>	- Resolution이 커질수록 Real world에서 동일한 점이 두 이미지 평면에서 차지하는 위치 간의 픽셀 값은 증가
>	- 하지만 한 픽셀이 나타내는 Real world에서의 거리는 줄어들기 때문에 결과적으로 해상도가 증가해도 시차 값은 동일하게 유지
>	  > 예상: $Disparity=\frac{m}{pixels}\times pixels$
>	  

>[!note]- blockSize vs Resolution
>- Resolution이 증가할수록 한 blockSize는 상대적으로 작아지기 때문에 적절하게 blockSize를 증가시킬 필요 있음