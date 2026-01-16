---
date: 2024-02-12, 20:49
status: Permanent
tags:
  - Study/Coding/remoteControl
  - Study
  - Study/Coding
aliases:
  - 원격제어
  - 공유폴더
reference: 
author: 
url:
---
# For Server Computer

1. 공유폴더 디렉토리 만들기
	```bash
	mkdir /home/<user name>/<folder name>
	```

2. samba 설치
	```bash
	sudo apt-get install samba
	```

3. 그룹 생성
```bash
sudo groupadd <group>
```

4. 그룹에 시스템 계정 추가
```bash
sudo gpasswd -a <id> <group>
```

5. samba 계정 및 패스워드 생성
	추가하려는 계정은 시스템에 존재하는 계정이어야 함
```bash
sudo smbpasswd -a <id>
```

6. samba 설정
```bash
sudo nano /etc/samba/smb.conf
```

```ini
# -----마지막 줄에 추가-----
[<forder name>]
	comment = share forder
	path = /home/<user name>/<folder name>
	writable = yes
	guewst ok = yes
	create mask = 0664
	directory mask = 0775
	browsable = yes
	public = no
	force group = <group>
	valid users <id1> <id2>
```

7. 139, 445 포트 개방
```bash
sudo ufw allow 139
sudo ufw allow 445
```

8. samba 재시작
```bash
sudo service smbd restart
```

# For Mac

1. Finder에서 cmd + k를 눌러 서버에 연결
2. 입력창에 smb://<ip\> 입력
3. 공유폴더 선택 후 확인