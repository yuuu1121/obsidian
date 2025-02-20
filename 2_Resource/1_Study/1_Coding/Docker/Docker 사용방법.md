---
date: 2024-08-13
status: Permanent
tags:
  - Study/Coding/Docker
aliases: 
keywords: 
reference: 
author: 
url: 
dg-publish: true
---
# Docker
- 애플리케이션을 컨테이너로 패키징하여 실행 환경을 손쉽게 배포하고 관리할 수 있도록 해주는 플랫폼
	- 코드, 라이브러리, 설정 파일을 포함한 애플리케이션의 모든 것을 일관된 환경에서 실행할 수 있음

<br>

- Image
	- 컨테이너의 실행 환경을 정의한 일종의 템플릿
- Container
	- 이미지를 기반으로 실행되는 인스턴스
	- 하나의 이미지에서 여러 개의 컨테이너를 생성해 다양한 작업을 수행할 수 있음
- [[Dockerfile 작성 방법]]
	- 도커 이미지를 정의하는 스크립트 파일
	- Dockerfile을 통해 애플리케이션 설치, 환경 설정, 의존성 설치 등의 과정을 자동화 할 수 있음
- Docker Hub
	- 도커 이미지를 저장하고 공유하는 공용 레지스트리
	- 다양한 공개 이미지를 다운로드하고, 자신의 이미지를 업로드하여 공유할 수 있음

<br>

## Command
#### docker pull
- Docker Hub에서 이미지를 다운로드하여 로컬 환경에 저장
	```shell
	docker pull <이미지_이름>:<태그>
	```

<br>

#### docker search
- Docker Hub에서 특정 이미지를 검색
	```shell
	docker search <이미지_이름>
	```

<br>

#### docker run
- 지정된 도커 이미지를 기반으로 컨테이너를 생성하고 실행
- 이미지가 로컬에 없으면 자동으로 `docker pull`을 통해 이미지를 다운로드한 후 실행
	```shell
	docker run [옵션] <이미지_이름>:<태그> [명령어]
	```

##### Options
- `-d`: 컨테이너를 백그라운드에서 실행
- `-p <호스트_포트>:<컨테이너_포트>`: 호스트와 컨테이너 간의 포트 연결
- `-v <호스트_디렉토리>:<컨테이너_디렉토리>`: 호스트와 컨테이너 간의 디렉토리 공유
- `--name <컨테이너_이름>`: 컨테이너에 특정 이름을 부여
- `-it`: 컨테이너를 인터랙티브 모드로 실행하여 터미널에 접근할 수 있도록 함
	- 이 옵션이 없으면 컨테이너가 실행된 후 입력을 받을 수 없음
- `--privileged`: 컨테이너가 호스트의 모든 장치에 접근할 수 있도록 허용
- `--gpus`: NVIDIA GPU 지원을 활성화하는 데 사용
- `--shm-size`: 공유메모리(shared memory) 크기 설정하는 옵션
	- 기본적으로 Docker 컨테이너는 /dev/shm 디렉토리에서 64MB의 공유 메모리 공간을 할당
- `-e`: 호스트의 환경 변수를 컨테이너에 전달
- `-w`: 컨테이너 내에서 기본 작업 디렉토리 설정

>[!example]- Command for using GPU and GUI
> ```shell
> docker run -it --privileged --gpus 'all,"capabilities=compute,utility,graphics"' --shm-size=32g -e DISPLAY=unix$DISPLAY -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix:rw  -v /usr/share/zoneinfo:/usr/share/zoneinfo:ro -e TZ=Asia/Seoul -v /dev:/dev --ipc=host -w /workspace 
> ```
> 
> - `--gpus 'all,"capabilities=compute,utility,graphics"'`
> 	- `all`: 모든 GPU를 컨테이너에 할당
> 	- `"capabilities=compute,utility,graphics"`: GPU에서 사용할 기능을 지정
> 		- `compute`: CUDA를 사용한 계산 작업
> 		- `utility`: GPU 관리 및 모니터링 작업
> 		- `graphics`: 그래픽 관련 기능 사용
> - `--shm-size=32g`
> 	- 32GB의 공유 메모리 공간 할당
> - `-e DISPLAY=unix$DISPLAY`
> 	- 호스트의 디스플레이 환경 변수를 컨테이너로 전달하여 그래픽 사용자 인터페이스(GUI) 애플리케이션을 실행할 수 있게 함
> 	- 이를 통해 GUI를 필요로 하는 애플리케이션이 컨테이너 내에서 실행되더라도 호스트의 디스플레이에 출력
> - `-e QT_X11_NO_MITSHM=1`
> 	- 일부 X11 애플리케이션(QT 기반 애플리케이션)이 SHM(공유 메모리)을 사용하지 않도록 설정하는 옵션
> 	- X11에서 MIT-SHM(공유 메모리 확장)은 때때로 컨테이너 환경에서 충돌할 수 있으므로 이 설정을 통해 문제가 발생하지 않도록 방지
> - `-v /tmp/.X11-unix:/tmp/.X11-unix:rw`
> 	- 컨테이너 내 애플리케이션이 호스트의 X11 서버와 상호작용하여 그래픽 애플리케이션을 실행할 수 있게 함
> - `-v /dev:/dev`
> 	- 호스트의 `/dev` 디렉토리를 컨테이너에 마운트하여 컨테이너가 호스트의 장치에 접근할 수 있게 허용
> 	- GPU 또는 기타 하드웨어 장치를 사용할 때 필요

<br>

#### docker save
- 도커 이미지를 하나의 파일로 저장(백업)하는 데 사용
	```shell
	docker save -o <파일명.tar> <이미지_이름>:<태그>
	```

<br>

#### docker load
- `docker save` 명령어로 저장된 이미지 파일을 로드하여 로컬 환경에 이미지를 복원
	```shell
	docker load -i <파일명.tar>
	```


<br>

### docker push
- 로컬에서 빌드한 이미지를 Docker hub에 업로드하여 공유하는 방법

1. **Docker Hub 로그인**
	- 이미지를 푸시하기 전에 Docker Hub에 로그인 필요.
	```shell
	docker login
	```

2. **이미지 태그 지정**
	- 푸시할 이미지에 Docker Hub 사용자 이름과 함께 태그 추가.
	```shell
	docker tag <로컬 이미지 이름>:<태그> <Docker Hub 사용자 이름>/<이미지 이름>:<태그>
	```
	- 예: `myapp:latest`를 `username/myapp:1.0`으로 태그
	```shell
	docker tag myapp:latest username/myapp:1.0
	```

3. **이미지 푸시**
	- 태그가 완료된 이미지를 Docker Hub로 푸시.
	```shell
	docker push username/myapp:1.0
	```
