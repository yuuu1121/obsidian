---
date: 2024-07-31
status: Permanent
tags:
  - Study/Coding/Docker
aliases:
  - Window Docker 설치
keywords: 
reference: 
author: []
url: 
dg-publish: true
---
>[!note] 목차
>1. **WSL2 설치**
>2. [[Window에서 Docker 사용하기 - Docker 설치|Docker 설치]]
>3. [[Window에서 Docker 사용하기 - IDE 연결|IDE 연결]]

# WSL2 설치
1. Windows PowerShell 관리자 권한으로 실행
	![[3_Archive/1_Attachments/Pasted image 20240731141439.png]]
	
	- 문제 발생 시 해결방법
	  [[이 시스템에서 스크립트를 실행 할 수 없으므로 파일을 로드 할 수 없습니다.]]

2. 리눅스를 위한 window 하위 시스템 사용
	```powershell
	dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
	```

3. virtual machine 사용
	```powershell
	dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
	```

1. wsl 설치
	```powershell
	wsl --install
	```
	>[!note] 설치가 잘 안될 경우
	>```powershell
	>wsl --install --web-download
	>```

1. 재부팅
2. WSL version 2로 변경 및 확인
	```powershell
	wsl --set-default-version 2
	wsl --status
	wsl -l -v
	```

>[!tip] 다른 배포판 설치 방법
>```powershell
># 설치 가능한 배포판 목록 확인
>wsl --list --online
>
># ex) Ubuntu 20.04 설치
>wsl --install -d Ubuntu20.04 --web-downloadg
>
># Unbuntu 20.04 기본 설정
>wsl -s Ubuntu-20.04
>```