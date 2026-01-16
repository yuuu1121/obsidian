---
date: 2024-09-12
status: Permanent
tags:
  - Study/Coding/remoteControl
aliases: 
keywords:
  - ssh
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
### 1. 서버 측 준비

#### 1.1 저장소 업데이트
서버의 패키지 목록을 최신 상태로 유지하기 위해 먼저 업데이트를 진행.
```shell
sudo apt update
```

#### 1.2 OpenSSH 서버 설치
서버에 SSH 접속을 가능하게 하려면 OpenSSH 서버를 설치.
```shell
sudo apt install openssh-server
```

#### 1.3 SSH 서비스 상태 확인
SSH 서비스가 정상적으로 실행 중인지 확인. 아래 명령으로 확인 가능.
```shell
sudo systemctl status ssh
```
`active (running)` 상태가 보이면 정상적으로 작동 중.

#### 1.4 방화벽 설정 (필요 시)
방화벽이 활성화되어 있으면 SSH 트래픽을 허용해야 함.
```shell
sudo ufw allow ssh
sudo ufw reload
```

---

### 2. 클라이언트 측 준비

#### 2.1 서버 IP 주소 확인
클라이언트에서 서버에 접속하려면 서버의 IP 주소가 필요. 서버에서 아래 명령으로 IP 주소 확인.
```shell
ip a
```
`inet` 항목에 표시된 IP 주소를 확인.

#### 2.2 SSH 접속
클라이언트에서 터미널을 열고 다음 명령으로 서버에 접속.
```shell
ssh 사용자명@서버_IP
```
비밀번호 입력 후 정상적으로 접속 확인.

---

### 3. SSH 포트 변경 (선택사항)

#### 3.1 SSH 설정 파일 수정
기본적으로 SSH는 포트 22번을 사용. 이를 보안 목적으로 다른 포트로 변경하려면 설정 파일을 수정해야 함.
```shell
sudo nano /etc/ssh/sshd_config
```
`#Port 22`를 찾아서 주석을 제거하고 원하는 포트 번호로 변경. 예를 들어, 포트 12345로 설정:
```shell
Port 12345
```

#### 3.2 SSH 서비스 재시작
설정 변경 후 SSH 서비스를 재시작.
```shell
sudo systemctl restart ssh
```

#### 3.3 클라이언트에서 변경된 포트로 접속
새로운 포트로 접속하려면 아래와 같이 `-p` 옵션을 사용.
```shell
ssh -p 12345 사용자명@서버_IP
```

---

### 4. SSH 키 기반 인증 설정

#### 4.1 클라이언트에서 SSH 키 생성
비밀번호 대신 SSH 키를 이용해 서버에 접속할 수 있음. 클라이언트에서 SSH 키를 생성.
```shell
ssh-keygen -t rsa -b 4096
```
키 생성 시 비밀번호를 설정하지 않으면 비밀번호 없이 접속 가능.

#### 4.2 서버에 공개키 복사
생성한 공개키를 서버에 복사.
```shell
ssh-copy-id 사용자명@서버_IP
```

#### 4.3 키로 접속
이제 비밀번호 없이 SSH 키로 접속 가능.
```shell
ssh 사용자명@서버_IP
```