---
date: 2024-02-22, 20:45
status: Permanent
tags:
  - Study/Filter/GroundFilter
aliases:
  - general_max_slope
  - local_max_slope
  - min_height_threshold
reference: 
author: 
url:
---
# Parameters
- **general_max_slope** (default: 15.0)
	- cur_point가 prev_point의 local cone에 들어가지 못했을 때, 혹은 들어갔지만 prev_point가 ground 였을 때 cur_point를 분류하기 위해 사용됨
	- **general_max_slope**가 작아지면 ground로 분류되기 어려워지기 때문에 no_ground point가 증가함
	- **general_max_slope**가 커지면 반대로 no_ground point가 줄어들지만, 대부분 포인트끼리의 거리가 가까워 prev_point의 local cone에 들어가기 때문에 default 값일 때와 큰 차이가 발생하진 않음
- **local_max_slope** (default: 25.0)
	- cur_point가 prev_point의 local cone에 들어갔을 때 prev_point의 상태에 따라 cur_point가 분류됨
		- 즉, 포인트들 간의 연관성을 의미
	- **local_max_slope**이 작아지면 연관성이 줄어들어 이전 포인트의 ground 상태가 전파되지 않으며, global cone에 의해 재 분류되기 때문에 no_ground point가 증가하지만, 대부분 포인트끼리의 거리가 가까워 local cone의 크기가 **min_height_threshold**에 의해 보정되기 때문에 default 값일 때와 큰 차이가 발생하진 않음
	- **local_max_slope**이 커지면 반대로 no_ground point가 줄어들지만, 대부분 포인트끼리의 거리가 가까워 local cone의 크기가 **min_height_threshold**에 의해 보정되기 때문에 default 값일 때와 큰 차이가 발생하진 않음
- **min_height_threshold**
	- cur_point와 prev_point의 거리가 매우 가까워 local cone이 매우 작아질 때, local cone의 크기를 보정
	- **min_height_threshold**가 작아지면 보정이 줄어들어 연관성이 줄어들기 때문에 no_ground point가 증가
	- **min_height_threshold**가 커지면 반대로 보정이 과하게 되어 연관성이 커지기 때문에 no_ground point가 감소

| *Parameters*                     |                   *의미*                    |         *감소*         |         *증가*         |
|:--------------------:|:-----------------------------------------:|:--------------------:|:--------------------:|
|  **general_max_slope**   |               포인트 재분류               | no_ground point 증가 | no_ground point 감소 |
|   **local_max_slope**    |              포인트의 연관성              | no_ground point 증가 | no_ground point 감소 |
| **min_height_threshold** | local cone 보정<div>포인트의 연관성</div> | no_ground point 증가 | no_ground point 감소 |
## Default
![[ray_ground_ori.mp4]]
## general_max_slope
| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| **general_max_slope**    | 15.0        | 1.0          |
| local_max_slope      | 25.0        | 25.0          |
| min_height_threshold | 0.2            | 0.2          |
![[ray_ground_1_1.mp4]]

| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| **general_max_slope**    | 15.0        | 30.0          |
| local_max_slope      | 25.0        | 25.0          |
| min_height_threshold | 0.2            | 0.2          |
![[ray_ground_1_2_45.mp4]]


## local_max_slope
| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| general_max_slope    | 15.0        | 15.0          |
| **local_max_slope**      | 25.0        | 0.0          |
| min_height_threshold | 0.2            | 0.2          |
![[ray_ground_2_1.mp4]]

| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| general_max_slope    | 15.0        | 15.0          |
| **local_max_slope**      | 25.0        | 75.0          |
| min_height_threshold | 0.2            | 0.2          |
![[ray_ground_2_2.mp4]]

## min_height_threshold
| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| general_max_slope    | 15.0        | 15.0          |
| local_max_slope      | 25.0        | 25.0          |
| **min_height_threshold** | 0.2            | 0.0          |
![[ray_ground_3_1.mp4]]

| *Parameters*       | *Default* | *Value* |
|:-------------------- |:----------- |:--------- |
| general_max_slope    | 15.0        | 15.0          |
| local_max_slope      | 25.0        | 25.0          |
| **min_height_threshold** | 0.2            | 1.0          |
![[ray_ground_3_2.mp4]]

