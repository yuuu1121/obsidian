---
date: 2024-02-22, 15:48
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://stackoverflow.com/questions/64038673/could-not-build-wheels-for-which-use-pep-517-and-cannot-be-installed-directly
---
# 문제 발생
- OpenPCDet에서 제공하는 `cu116.Dockerfile`로 도커 이미지를 생성하는 과정에서 문제 발생
```bash
#0 233.7   ERROR: Failed building wheel for mayavi
#0 233.7 Successfully built SharedArray
#0 233.7 Failed to build mayavi
#0 234.6 ERROR: Could not build wheels for mayavi which use PEP 517 and cannot be installed directly
------
Dockerfile:65
--------------------
  63 |
  64 |     # OpenPCDet
  65 | >>> RUN pip3 install numpy==1.23.0 llvmlite numba tensorboardX easydict pyyaml scikit-image tqdm SharedArray open3d mayavi av2 kornia pyquaternion
  66 |     RUN pip3 install spconv-cu116
  67 |
--------------------
ERROR: failed to solve: process "/bin/sh -c pip3 install numpy==1.23.0 llvmlite numba tensorboardX easydict pyyaml scikit-image tqdm SharedArray open3d mayavi av2 kornia pyquaternion" did not complete successfully: exit code: 1
```
# 원인 분석
- 해당 문제는 Tensorflow를 설치하는 과정에서 h5py 라이브러리에서 발생한 문제로 보임
# 해결 방법
- `pip`와 `setuptools`의 버전을 업데이트하여 해당 문제 해결 가능
```bash
pip install --upgrade pip setuptools wheel
```

