---
date: 2024-02-21, 10:21
status: Fleeting
tags: 
aliases: 
reference: 
author: 
url: 
related notes:
---
```bash
docker: Error response from daemon: unable to find user <user>: no matching entries in passwd file.
```
# 발생 원인
- 사용자 계정(nirsa)이 /etc/passwd 파일에 존재하지 않음 
  (즉, 사용자 계정이 생성되지 않음)
  (Dockerfile 에서 USER 명령을 사용하여 RUN,CMD,ENTRYPOINT 명령을 특정 사용자로 실행하려 했을 경우 발생할 수 있음)

# 해결 방법
- 해결 방법은 비교적 간단한데, 문제가 되는 사용자 계정을 생성
- Dockerfile에서 상단에 RUN useradd nirsa 등으로 사용자 계정을 생성 후 빌드를 시도

