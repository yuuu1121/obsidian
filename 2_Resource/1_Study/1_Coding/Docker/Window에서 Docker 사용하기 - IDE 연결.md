---
date: 2024-07-31
status: Permanent
tags:
  - Study/Coding/Docker
aliases: 
keywords: 
related notes: 
reference: 
author: []
url: 
dg-publish: true
---
>[!note] 목차
>1. ~~[[Window에서 Docker 사용하기 - WSL2 설치|WSL2 설치]]~~
>2. ~~[[Window에서 Docker 사용하기 - Docker 설치|Docker 설치]]~~
>3. **IDE 연결**

# IDE 연결
1. VScode 다운로드
	[vscode 설치 링크](https://code.visualstudio.com/docs/?dv=win)

1. VScode extension 설치
   Python, Docker, Docker explorer extension

1. WSL에서 Docker container를 실행하면 Docker desktop 왼쪽의 Container 탭과 VScode의 Docker extension에서 확인 가능
   ![[3_Archive/1_Attachments/Pasted image 20240731154625.png]]
   ![[3_Archive/1_Attachments/Pasted image 20240731154643.png|+grid]]![[3_Archive/1_Attachments/Pasted image 20240731154847.png|+grid]]
2. Dev containers extension 설치
   - VScode의 왼쪽 Extension 탭에서 Remote explorer를 클릭하면 WSL targets에서 Ubuntu와 Dev containers에서 Docker container 목록을 확인 가능
   - 해당 Container 혹은 Ubuntu를 Connect 하면 VScode에서 터미널로 사용 가능
	![[3_Archive/1_Attachments/Pasted image 20240731155359.png]]
