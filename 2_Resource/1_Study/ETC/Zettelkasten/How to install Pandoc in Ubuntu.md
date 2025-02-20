---
date: 2024-09-09
status: Permanent
tags:
  - Study/Obsidian/Zettelkasten/서지관리
aliases: 
keywords:
  - pandoc
related notes:
  - "[[2_Resource/1_Study/ETCs/Zettelkasten/Research Workflow - Zotero, Pandoc]]"
reference: 
author: 
url: 
dg-publish: false
---
### 1. 패키지 관리자를 통해 설치

리눅스 배포판에서 기본 제공하는 패키지 관리자 이용 가능. 아래는 몇 가지 배포판에서의 설치 명령어 예시.

- **Debian/Ubuntu**:

```bash
sudo apt update
sudo apt install pandoc
```

- **Fedora**:

```bash
sudo dnf install pandoc
```

- **Arch Linux**:

```bash
sudo pacman -S pandoc
```

### 2. 최신 버전 설치 (Tarball 이용)

패키지 관리자가 제공하는 버전이 오래됐거나 최신 버전이 필요하다면, 공식 사이트에서 직접 다운로드 후 설치 가능.

#### 2.1. Tarball 다운로드 및 설치
1. [Pandoc 다운로드 페이지](https://pandoc.org/installing.html)에서 최신 Pandoc tarball 파일 다운로드.
2. 다운로드한 tarball 파일 압축 해제.

```bash
tar xvzf pandoc-*.tar.gz
```

3. 압축 해제한 파일을 적절한 디렉토리 (예: `/usr/local/` 또는 `$HOME/.local/`)로 이동.

```bash
sudo tar xvzf pandoc-*.tar.gz --strip-components 1 -C /usr/local/
```

이 방법으로 Pandoc이 `/usr/local/` 디렉토리에 설치되며, 실행 파일은 `/usr/local/bin/`에서 사용할 수 있음.

### 3. .deb 파일 이용한 설치 (Debian/Ubuntu)

1. 다운로드 페이지에서 `.deb` 파일 다운로드.
2. 다음 명령어로 설치:

```bash
sudo dpkg -i <다운로드한 .deb 파일 경로>
```

### 참고 사항
- Pandoc은 기본적으로 LaTeX을 이용해 PDF 생성. 
  따라서 PDF 파일을 생성하려면 `texlive` 패키지를 추가로 설치하는 것이 좋음.

```bash
sudo apt install texlive
```