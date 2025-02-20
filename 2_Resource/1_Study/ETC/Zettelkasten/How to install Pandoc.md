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
## Windows 설치

1. [Pandoc 다운로드 페이지](https://pandoc.org/installing.html)에서 Windows 설치 파일 다운로드.
2. 다운로드한 **msi** 파일 실행 후 설치 진행.
3. 명령 프롬프트에서 설치 확인:

   ```bash
   pandoc --version
   ```

4. PDF 생성에 필요한 LaTeX이 필요할 경우 **MiKTeX** 설치:

   ```bash
   choco install miktex
   ```

<br>



## Mac 설치

1. [Pandoc 다운로드 페이지](https://pandoc.org/installing.html)에서 Mac 설치 파일 다운로드.
2. 다운로드한 **.pkg** 파일 실행 후 설치 진행.
3. 터미널에서 설치 확인:

   ```bash
   pandoc --version
   ```

4. Homebrew를 통해 설치도 가능:

   ```bash
   brew install pandoc
   ```


<br>

## Linux 설치

- [[How to install Pandoc in Ubuntu|해당 링크 참고]]
