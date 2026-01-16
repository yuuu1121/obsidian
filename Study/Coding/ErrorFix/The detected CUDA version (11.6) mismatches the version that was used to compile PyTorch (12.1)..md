---
date: 2024-02-22, 16:05
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
---
# 문제 발생
- OpenPCDet에서 제공하는 `cu116.Dockerfile`로 도커 이미지를 생성하는 과정에서 문제 발생
```bash
#0 3.327 RuntimeError:
#0 3.327 The detected CUDA version (11.6) mismatches the version that was used to compile
#0 3.327 PyTorch (12.1). Please make sure to use the same CUDA versions.
------
Dockerfile:76
--------------------
  74 |     WORKDIR OpenPCDet
  75 |
  76 | >>> RUN python3 setup.py develop
  77 |
  78 |     WORKDIR /
--------------------
ERROR: failed to solve: process "/bin/sh -c python3 setup.py develop" did not complete successfully: exit code: 1
```
# 원인 분석
- CUDA 드라이버 버전 문제로 생각하고 GPU capability, CUDA Toolkit Driver Version 등을 확인하여  CUDA 버전을 변경하여 진행해보았으나 똑같은 에러 발생함
  (11.4, 11.3, 11.4)
- Dockerfile의 `RUN python3 setup.py develop` 부분을 지운 결과 이미지가 문제없이 생성되었으며, 이후 도커 컨테이너에서 torch version을 확인해보았음
```bash
xxx@xxx:/workspace# pip list | grep torch
torch                     1.11.0+cu113
torchaudio                0.11.0+cu113
torchvision               0.12.0+cu113
```
```bash
xxx@xxx:/workspace# python3
Python 3.8.10 (default, Nov 22 2023, 10:22:35)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
2.2.0+cu121
```
- 분명 `pip list`로 검색했을 땐 1.11버전이 출력되었으나, Python 내부에서 출력하였을 땐 `2.2.0+cu121`이 출력되었으며, 이 때문에 설치된 CUDA 버전과 PyTorch에서 요구하는 버전이 달라서 해당 에러가 발생
	- 정확한 이유는 모르겠음
# 해결 방법
- PyTorch를 지우고 재설치
```bash
pip3 uninstall torch torchaudio torchvision
pip3 install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
```
```bash
xxx@xxx:/workspace# python3
Python 3.8.10 (default, Nov 22 2023, 10:22:35)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
1.11.0+cu113
```
- 이후 `python3 setup.py develop`을 다시 수행
