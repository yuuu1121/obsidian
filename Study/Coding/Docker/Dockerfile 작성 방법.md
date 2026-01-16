---
date: 2024-10-04
status: Permanent
tags:
  - Study/Coding/Docker
aliases:
  - Dockerfile
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Dockerfile
- 도커 이미지를 만들기 위한 Script 파일
- 여러 개발 환경에서 일관되게 동작하는 컨테이너를 만들기 위해 사용

<br>

- Image
	- Dockerfile을 바탕으로 생성된 컨테이너의 청사진
	- 베이스 이미지를 기반으로 하고, 그 위에 여러 명렬어들이 쌓이면서 새로운 이미지를 생성
- Container
	- 이미지를 실행 가능한 상태로 만들어 실제로 실행되는 환경

```Dockerfile
# 베이스 이미지 설정
FROM ubuntu:20.04

# 빌드 시 ARG 인자 설정
ARG APP_VERSION=1.0

# 환경 변수 설정
ENV APP_ENV=production \
    APP_VERSION=${APP_VERSION}

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y python3 python3-pip

# 작업 디렉토리 설정
WORKDIR /app

# 로컬 파일을 컨테이너로 복사
COPY . /app

# 의존성 설치
RUN pip3 install -r requirements.txt

# 애플리케이션 실행 포트 공개
EXPOSE 8080

# 기본 실행 명령 설정
CMD ["python3", "app.py"]
```


<br>

## Command of Dockerfile
- FROM
	- 베이스 이미지를 지정
- RUN
	- 이미지 빌드 중에 실행될 명령어
	- 패키지 설치나 파일 복사 등의 작업을 수행
- CMD
	- 컨테이너가 실행될 때 기본적으로 실행할 명령어
	- Dockerfile에 하나만 있어야 하며, 여러 개가 있을 경우 마지막 CMD가 사용됨
- ENTRYPOINT
	- 컨테이너가 실행될 때 기본적으로 실행될 명령어
		- `ENTRYPOINT`는 고정된 실행 파일을 지정하며, `CMD`는 그 실행 파일에 전달할 인자
	```Dockerfile
	ENTRYPOINT ["python3"]
	CMD ["app.py"]
	```

- COPY
	- 로컬 파일을 이미지의 파일 시스템으로 복사
	```Dockerfile
	# 현재 디렉토리(`.`)의 모든 파일을 이미지의 `/app` 디렉토리로 복사합니다.
	COPY . /app
	```

- ADD
	- `COPY`와 유사하지만, URL에서 파일을 다운로드하거나, tar 아카이브 파일을 자동으로 압축 해제하는 기능도 포함
	```Dockerfile
	# 원격 파일을 다운로드하여 `/app` 디렉토리에 저장합니다.
	ADD https://example.com/file.zip /app/file.zip
	```

- WORKDIR
	- 이미지의 작업 디렉토리를 설정
	- 이후 명령어들은 이 디렉토리에서 실행
- ENV
	- 환경 변수 설정
- EXPOSE
	- 컨테이너가 사용할 네트워크 포트를 지정
	- 단순히 문서화 용도로 사용되며, 실제로 포트를 열기 위해서는 `docker run` 명령어에서 포트를 지정해야 함
- VOLUME
	- 컨테이너와 호스트 간에 데이터를 공유하기 위한 볼륨을 설정
	```Dockerfile
	# 컨테이너의 `/data` 디렉토리를 호스트와 공유합니다.
	VOLUME /data
	```

- USER
	- 명령어를 실행할 유저를 설정
	- 보안상의 이유로 `root` 계정 대신 다른 계정을 사용할 때 해당 명령어 사용
- ARG
	- 빌드 시 인자를 설정
	- `ENV`와 비슷하지만, 빌드 시에만 사용되며, 컨테이너 내부에서는 사용할 수 없음
- SHELL
	- `RUN`, `CMD`, `ENTRYPOINT` 명령어에서 사용할 기본 셸을 설정
	```Dockerfile
	# 기본 셸을 bash로 설정합니다.
	SHELL ["/bin/bash", "-c"]
	```


<br>

## Build
- Dockerfile이 있는 디렉토리에서 `docker build` 명령어를 실행하여 이미지를 빌드
	
	```Dockerfile
	docker build -t <이미지_이름>:<태그> .
	```