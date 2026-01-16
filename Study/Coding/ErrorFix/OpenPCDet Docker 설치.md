---
date: 2024-02-22, 15:39
status: Problem Solving
tags:
  - Study/Coding/solution
aliases:
  - CUDA 10.x
reference: 
author: 
url: 
keywords:
  - OpenPCDet
---
# 문제 발생
- [OpenPCDet](https://github.com/open-mmlab/OpenPCDet/tree/master/docker)에서 제공하는 Dockerfile로 build를 하였는데 오류 발생
```bash
xxx@xxx:~/workspace/OpenPCDet/docker$ docker build ./ -t openpcdet-docker:102
[+] Building 1.9s (3/3) FINISHED
 => [internal] load .dockerignore                                                                                0.0s
 => => transferring context: 2B                                                                                  0.0s
 => [internal] load build definition from Dockerfile                                                             0.0s
 => => transferring dockerfile: 1.95kB                                                                           0.0s
 => ERROR [internal] load metadata for docker.io/nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04                       1.9s
------
 > [internal] load metadata for docker.io/nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04:
------
Dockerfile:1
--------------------
   1 | >>> FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04
   2 |
   3 |     RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
--------------------
ERROR: failed to solve: nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04: docker.io/nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04: not found
```
# 원인 분석
- `nvidia/cuda:10.x`는 더이상 지원되지 않음
# 해결 방법
- OpenPCDet에서 `cu116.Dockerfile`로 CUDA 11.6 버전 Dockerfile을 제공해주고 있기 때문에 해당 파일로 도커 이미지 생성
