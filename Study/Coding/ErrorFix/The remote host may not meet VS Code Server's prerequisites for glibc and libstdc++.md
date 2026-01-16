---
date: 2024-02-12, 20:58
status: Permanent
tags:
  - Study/Coding/solution
  - Study/Coding/remoteControl
aliases:
  - 원격제어
  - 원격제어에러
  - vscode에러
  - glibc
  - remote-ssh
reference: 
author: 
url:
---

# 문제
## 문제 발생

1. VScode error message:
	```html
	The remote host may not meet VS Code Server's prerequisites for glibc and libstdc++
	```
## 원인
- Error log
	```html
	[2024-02-05 09:42:58] error This machine does not meet Visual Studio Code Server's prerequisites, expected either...:   
	- find GLIBC >= v2.28.0 (but found v2.27.0 instead) for GNU environments
	- find /lib/ld-musl-x86_64.so.1, which is required to run the Visual Studio Code Server in musl environments
	```

- Sever 컴퓨터 glibc 버전 확인
	```bash
	ksm@dgist:~/Downloads$ ldd --version
	ldd (Ubuntu GLIBC 2.27-3ubuntu1.6) 2.27Copyright (C) 2018 Free Software Foundation, Inc.
	```

- 최근 Remote-ssh는 우분투 20.04 이상만 지원하는 것으로 보임 [참조 링크](https://github.com/microsoft/vscode/issues/203967#issuecomment-1921302060)
	**Ubuntu 64-bit x86, ARMv8l (AArch64)** (20.04+)
	
## 해결
1. 서버 컴퓨터 내 용량 확인 [참조 링크](https://velog.io/@jshfu/The-remote-host-may-not-meet-VS-Code-Servers-prerequisites-for-glibc-and-libstdc)
	```bash
	ksm@dgist:~/Downloads$ df -h -T | grep sdb
	/dev/sdb5      ext4      228G  126G   91G  59% /
	/dev/sdb1      vfat      511M  5.3M  506M   2% /boot/efi
	```
	용량은 충분히 있는 것으로 보임

2. **Download VS Code release 1.85** [참조 링크](https://github.com/microsoft/vscode/issues/203967#issuecomment-1921306310)
	1.85버전 VS Code는 우분투 18.04도 지원하기 때문에 해당 버전으로 다운그레이드하여 문제 해결