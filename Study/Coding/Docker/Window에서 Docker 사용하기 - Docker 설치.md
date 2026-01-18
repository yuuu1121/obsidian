---
date: 2024-07-31
status: Permanent
tags:
  - "#Study/Coding/Docker"
aliases: 
keywords: 
related notes: 
reference: 
author: []
url: 
dg-publish: true
---
>[!note] 목차
>1. ~~[[Study/Coding/Docker/Window에서 Docker 사용하기 - WSL2 설치|WSL2 설치]]~~
>2. **Docker 설치**
>3. [[Study/Coding/Docker/Window에서 Docker 사용하기 - IDE 연결|IDE 연결]]

# Docker 설치

1. **Docker for Windows** 설치
	[Docker 설치 링크](https://www.docker.com/)
	![[Attachments/General/Pasted image 20240731145240.png|+grid]]![[Attachments/General/Pasted image 20240731145251.png|+grid]]
2. Docker 확인하기
	```shell
	sudo docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
	```
	![[Attachments/General/Pasted image 20240731155622.png]]