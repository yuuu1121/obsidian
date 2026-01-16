---
date: 2024-06-26, 11:53
status: Problem Solving
tags:
  - Study/Coding/solution
aliases:
  - qt.qpa.plugin
  - Docker GUI 에러
keywords:
  - Docker GUI 에러
related notes: 
reference: 
author: 
url:
---
# 문제 발생

```bash
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/opt/conda/lib/python3.10/site-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: xcb.
```

# 원인 분석

# 해결 방법

```bash
apt install make g++ pkg-config libgl1-mesa-dev libxcb*-dev libfontconfig1-dev libxkbcommon-x11-dev python libgtk-3-dev
```

- 또는
```bash
# Docker 밖에서
xhost +
```