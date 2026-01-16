---
date: 2024-02-22, 15:56
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://github.com/enthought/mayavi/issues/1232#issuecomment-1537507823
keywords:
  - OpenPCDet
---
# 문제 발생
- OpenPCDet에서 제공하는 `cu116.Dockerfile`로 도커 이미지를 생성하는 과정에서 문제 발생
```bash
#0 196.9   note: This error originates from a subprocess, and is likely not a problem with pip.
#0 196.9   ERROR: Failed building wheel for mayavi
#0 196.9 Successfully built SharedArray
#0 196.9 Failed to build mayavi
#0 196.9 ERROR: Could not build wheels for mayavi, which is required to install pyproject.toml-based projects
------
Dockerfile:68
--------------------
  66 |
  67 |     # OpenPCDet
  68 | >>> RUN pip3 install numpy==1.23.0 llvmlite numba tensorboardX easydict pyyaml scikit-image tqdm SharedArray open3d mayavi av2 kornia pyquaternion
  69 |     RUN pip3 install spconv-cu116
  70 |
--------------------
ERROR: failed to solve: process "/bin/sh -c pip3 install numpy==1.23.0 llvmlite numba tensorboardX easydict pyyaml scikit-image tqdm SharedArray open3d mayavi av2 kornia pyquaternion" did not complete successfully: exit code: 1
```
# 원인 분석
- [[2_Resource/1_Study/1_Coding/ErrorFix/Could not build wheels for _ which use PEP 517 and cannot be installed directly|PEP 517]]의 발생 원인과 비슷한 듯하지만 정확한 이유는 모르겠음. (**double check**)
# 해결 방법
- Dockerfile에서 `RUN pip3 install`에 있는 `mayavi`를 지우고 해당 코드 추가
```ruby
RUN pip3 install https://github.com/enthought/mayavi/zipball/master
```

