---
date: 2024-02-22
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
#0 146.1 ERROR: Cannot uninstall 'blinker'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
ERROR: Cannot uninstall 'blinker'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.
```
# 원인 분석
- 기존의 패키지를 uninstall하고 다시 새로운 버전을 설치하는 과정에서 어떤 파일을 지워야할지 결정할 수 없기 때문에 발생하는 installation 에러
# 해결 방법
- `pip install` 명령어에 `--ignore-installed` 옵션을 추가
- 여러 라이브러리에서 위와 같은 installation error가 발생할 수 있으므로 requirements.txt로 pip install을 할 때 아예 위의 옵션을 추가하면 좋음

