---
date: 2024-09-09
status: Permanent
tags:
  - Study/Obsidian/Zettelkasten/서지관리
aliases: 
keywords:
  - zotero
related notes:
  - "[[2_Resource/1_Study/ETCs/Zettelkasten/Research Workflow - Zotero, Pandoc]]"
reference: 
author: 
url: 
dg-publish: false
---
### 1. 공식 Tarball 설치 방법

#### 1.1. Tarball 다운로드 및 설치
1. [Zotero 공식 다운로드 페이지](https://www.zotero.org/download/)에서 리눅스용 Zotero tarball 파일 다운로드.
2. 다운로드한 파일 압축 해제.

```bash
tar -xvf zotero-*.tar.bz2
```

3. 압축 해제된 디렉토리로 이동.

```bash
cd zotero
```

4. `zotero` 파일 실행하여 Zotero 시작.

```bash
./zotero
```

#### 1.2. 시스템에 Zotero 추가하기
Zotero를 시스템에 편리하게 실행할 수 있도록 하기 위해 다음 단계를 따라 실행 아이콘 생성.

##### 1.2.1. Zotero 디렉토리 시스템 위치로 이동
1. `zotero` 디렉토리 `/opt`와 같은 적절한 시스템 디렉토리로 이동.

```bash
sudo mv zotero /opt/zotero
```

##### 1.2.2. .desktop 파일 설정
1. `/opt/zotero` 디렉토리로 이동하여 `set_launcher_icon` 스크립트 실행하여 아이콘 경로 설정.

```bash
cd /opt/zotero
./set_launcher_icon
```

2. `zotero.desktop` 파일을 로컬 애플리케이션 디렉토리로 심볼릭 링크 생성. 
   애플리케이션 목록에 Zotero 표시.

```bash
ln -s /opt/zotero/zotero.desktop ~/.local/share/applications/zotero.desktop
```

##### 1.2.3. 런처에서 Zotero 실행
1. 애플리케이션 목록 (예: Ubuntu의 경우 'Show Applications' 또는 애플리케이션 그리드)에서 Zotero 찾기.
2. 이 아이콘을 런처에 드래그하여 고정 가능.

#### 1.3. 아이콘 재설정 (업데이트 후)
Zotero 업데이트 후 아이콘이 깨지면 `set_launcher_icon` 스크립트 다시 실행하여 아이콘 재설정.

```bash
cd /opt/zotero
./set_launcher_icon
```

#### 1.4. 문제가 발생한 경우
- 심볼릭 링크 삭제 후 다시 생성하여 문제 해결 가능.

```bash
rm ~/.local/share/applications/zotero.desktop
ln -s /opt/zotero/zotero.desktop ~/.local/share/applications/zotero.desktop
```

### 2. Debian/Ubuntu 기반 배포판 설치 (zotero-deb 패키지 이용)

1. 커뮤니티에서 유지 관리하는 `zotero-deb` 패키지 통해 더 쉽게 설치 가능. 
   이 패키지는 apt 통해 설치 및 업데이트 자동 처리.
   
2. `zotero-deb` 설치:

```bash
sudo apt install wget gpg
wget -qO- https://github.com/retorquere/zotero-deb/raw/master/install.sh | sudo bash
```

3. Zotero 설치:

```bash
sudo apt update
sudo apt install zotero
```

이 방법을 사용하면 업데이트도 자동으로 처리됨.

### 참고 사항
- 타사에서 제공하는 비공식 패키지 사용 가능하지만, 공식 Tarball 또는 `zotero-deb` 패키지 사용하는 것을 권장. 
  비공식 패키지는 일부 기능이 정상 작동하지 않을 수 있음.