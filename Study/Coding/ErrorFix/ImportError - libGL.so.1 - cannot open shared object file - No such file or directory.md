---
date: 2024-07-05, 11:49
status: Problem Solving
tags:
  - Study/Coding/solution
aliases:
  - libGL.so.1
keywords:
  - libGL.so.1
  - ImportError
related notes: 
reference: 
author: 
url:
---
# 문제 발생

```bash
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

- `import cv2` 에서 해당 에러 발생
# 원인 분석



# 해결 방법

```bash
apt-get update -y
apt-get install -y libgl1-mesa-glx
```

- 위 명령어 후에 아래 에러가 발생할 경우 추가로 `libglib2.0-0` 설치

```bash
  ImportError: libgthread-2.0.so.0: cannot open shared object file: No such file or directory
```

```bash
apt-get install -y libglib2.0-0
```
