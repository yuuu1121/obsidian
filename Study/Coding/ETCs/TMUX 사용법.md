---
date: 2024-12-19
status: Permanent
tags: 
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: false
---

>[!summary] Contents
> 
> - [tmux 기본 명령어](#tmux%20%EA%B8%B0%EB%B3%B8%20%EB%AA%85%EB%A0%B9%EC%96%B4)
> 	- [세션 관리](#%EC%84%B8%EC%85%98%20%EA%B4%80%EB%A6%AC)
> 	- [창(Window) 관리](#%EC%B0%BD(Window)%20%EA%B4%80%EB%A6%AC)
> 	- [패널(Pane) 관리](#%ED%8C%A8%EB%84%90(Pane)%20%EA%B4%80%EB%A6%AC)
> 			- [입력 동기화](#**%EC%9E%85%EB%A0%A5%20%EB%8F%99%EA%B8%B0%ED%99%94**)
> 		- [3. tmux 설정 파일 활용](#**3.%20tmux%20%EC%84%A4%EC%A0%95%20%ED%8C%8C%EC%9D%BC%20%ED%99%9C%EC%9A%A9**)
> 			- [예제 설정 파일 (`~/.tmux.conf`)](#**%EC%98%88%EC%A0%9C%20%EC%84%A4%EC%A0%95%20%ED%8C%8C%EC%9D%BC%20(%60~/.tmux.conf%60)**)
> - [기타 유용한 명령어](#%EA%B8%B0%ED%83%80%20%EC%9C%A0%EC%9A%A9%ED%95%9C%20%EB%AA%85%EB%A0%B9%EC%96%B4)
> - [도움말 확인](#%EB%8F%84%EC%9B%80%EB%A7%90%20%ED%99%95%EC%9D%B8)
>

<br/><br/>

# tmux 기본 명령어

## 세션 관리

- **새로운 세션 생성**:
    
    ```bash
    tmux
    ```
    
    또는 이름을 지정하여 생성:
    
    ```bash
    tmux new -s 세션이름
    ```
    
- **현재 세션에서 나가기** (세션 종료 없이):
    
    ```bash
    Ctrl+b d
    ```
    
- **세션 목록 확인**:
    
    ```bash
    tmux list-sessions
    ```
    
- **기존 세션에 재접속**:
    
    ```bash
    tmux attach -t 세션이름
    ```
    
- **세션 종료**:
    
    ```bash
    tmux kill-session -t 세션이름
    ```
    
    또는 모든 세션 종료:
    
    ```bash
    tmux kill-server
    ```
    

<br/>

## 창(Window) 관리

- **새로운 창 생성**:
    
    ```bash
    Ctrl+b c
    ```
    
- **창 사이 이동**:
    
    - 다음 창으로 이동: `Ctrl+b n`
    - 이전 창으로 이동: `Ctrl+b p`
    - 특정 창으로 이동: `Ctrl+b 숫자` (예: `Ctrl+b 1`)
- **창 이름 변경**:
    
    ```bash
    Ctrl+b , (쉼표 입력 후 새 이름 입력)
    ```
    
- **창 닫기**:
    
    ```bash
    exit
    ```
    
    또는 `Ctrl+d`.
    

<br/>

## 패널(Pane) 관리

- **창을 수직 분할**:
    
    ```bash
    Ctrl+b %
    ```
    
- **창을 수평 분할**:
    
    ```bash
    Ctrl+b "
    ```
    
- **패널 간 이동**:
    
    - 위쪽으로 이동: `Ctrl+b ↑`
    - 아래쪽으로 이동: `Ctrl+b ↓`
    - 왼쪽으로 이동: `Ctrl+b ←`
    - 오른쪽으로 이동: `Ctrl+b →`
- **패널 크기 조정**:
    
    - 줄이기/늘리기: `Ctrl+b` + `Ctrl+방향키`
- **패널 닫기**:
    
    ```bash
    Ctrl+b x
    ```
    

<br/>

## 입력 동기화

- **패널 동기화 활성화**:
    
    ```bash
    Ctrl+b :
    setw synchronize-panes on
    ```
    
- **패널 동기화 비활성화**:
    
    ```bash
    Ctrl+b :
    setw synchronize-panes off
    ```
    

<br/><br/>

# tmux 설정 파일 활용

`tmux` 설정을 자동으로 적용하려면 `~/.tmux.conf` 파일을 생성하고 설정을 추가합니다.

#### **예제 설정 파일 (`~/.tmux.conf`)**

```bash
# 기본 키 바인딩 변경
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# 창 및 패널 번호 표시
set -g pane-border-status top

# 시간 표시
set -g status-right "%H:%M:%S"

# 이탈 시 메시지 표시 비활성화
set -g detach-on-destroy off
```

설정 적용:

```bash
tmux source-file ~/.tmux.conf
```

<br/><br/>

# 기타 유용한 명령어

- **로그 저장** (현재 세션 기록):
    
    ```bash
    Ctrl+b :
    capture-pane -S -1000
    save-buffer ~/tmux.log
    ```
    
- **스크롤 모드**:
    
    ```bash
    Ctrl+b [
    ```
    
    - 스크롤 후 종료: `q`
- **tmux 종료** (모든 세션 종료):
    
    ```bash
    tmux kill-server
    ```
    

<br/>

# 도움말 확인

- tmux 명령어 도움말:
    
    ```bash
    man tmux
    ```
    
- 특정 명령어 검색:
    
    ```bash
    tmux list-keys
    ```