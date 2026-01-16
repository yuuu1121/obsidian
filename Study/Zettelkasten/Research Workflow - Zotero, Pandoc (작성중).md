---
date: 2024-05-02, 16:37
status: Permanent
tags:
  - Study/Obsidian/Zettelkasten/서지관리
aliases:
  - Zotero 사용법
  - Pandoc 사용법
keywords:
  - zotero
  - pandoc
related notes: 
reference: 
author: 
url:
  - https://www.youtube.com/watch?v=C1nuZ2sJa9E
---
- [ ] 영상 보고 Zotero 및 Pandoc 설정하기 #task 🟢


### 1. Zotero 설치 및 확장 프로그램 설정
```ad-tip
title: How to install Zotero
collapse: true

[[How to install Zotero]]
```

#### 설치할 플러그인
- **Zotero Connector**: 크롬에서 찾은 논문을 Zotero에 바로 저장.
	- [Zotero Connector](https://chromewebstore.google.com/detail/zotero-connector/ekhagklcjbdpajgpjgmbionohlpdbjgc)
- **Better BibTeX**: 인용 관리 및 논문 고유 번호(Citation Key) 설정.
	- [Better BibTeX](https://retorque.re/zotero-better-bibtex/installation/)
- **Zotfile**: 파일을 스마트하게 관리(현재 업데이트 중지됨).
	- [Zotfile](https://zotfile.com/)
- **Markdown DB Connect**: Zotero와 Obsidian을 연동하여 문헌 메모 및 하이라이트 공유.
	- [Markdown DB Connect](https://github.com/daeh/zotero-markdb-connect)

<br>


#### 플러그인 설치 방법
1. **Zotero 애플리케이션** 실행.
2. 상단 메뉴에서 `Tools` 탭 ▶ `Plugins` ▶ `Zotero 플러그인 디렉토리`
3. 브라우저에서 원하는 플러그인 검색 및 `.xpi` 파일 다운로드
4.  Zotero에서 `Tools` ▶ `Plugins` ▶ `Setting` (톱니바퀴) ▶ `Install Plugin From File`

<br><br>


### 2. 논문 수집 및 태그 관리
#### 논문 수집
- **구글 학술 검색**을 통해 논문을 수집한 후, **Zotero Connector** 확장 프로그램을 이용해 Zotero에 저장.
	- 크롬에서 논문 페이지를 열고 **Zotero 저장 버튼** 클릭.

<br>


#### 태그 설정 및 관리
- 논문을 수집한 후, 태그를 설정하여 논문의 상태(읽기 여부, 메모 여부, 인용 여부)를 관리.
	- 예: **읽지 않은 논문**, **읽고 있는 논문**, **메모한 논문**, **인용한 논문** 등.
	
	```ad-note
	title: Tag Taxonomy
	collapse: true
	
	- 📥: **Unread, To Read** (Shortcut Key: 1)
	- 📚: **Next To Read** (Shortcut Key: 2)
	- 📙: **Reading** (Shortcut Key: 3)
	- ✅: **Done Reading** (Shortcut Key: 4)
	- 💡: **Cited, Used in Thesis** (Shortcut Key: 5)
	- 🚫: **Abandoned, Not Use** (Shortcut Key: 6)
	```

<br>



#### 태그 관리 예시
- **필터링**: 특정 태그를 사용하여 관련 논문만 필터링.
	- 예: "Artificial Intelligence" 태그가 포함된 논문만 표시.

<br><br>


### 3. Zotero와 Obsidian 연동
#### 연동 설정
1. **Zotero Integration 플러그인** 설치.
   - Obsidian에서 Zotero의 문헌을 실시간으로 가져오기 위한 플러그인.
2. **논문 메타데이터 설정**:
   - Obsidian의 템플릿에 Zotero에서 가져온 논문 제목, 저자, DOI 등의 메타데이터를 삽입.

<br>


#### Better BibTeX Citation Key 설정
1. **Zotero에서 Citation Key 설정**:
	- `Zotero` ▶ `환경설정` ▶ `better bibtex` ▶ `citication key formula`: 
	 ```
	 authors(n=1, etal=EtAl)+''+year
	 ```
	- `Zotero` ▶ `My Library` 우클릭 ▶ `Export Library` ▶ `Better CSL Json` ▶ `Keep update`
	- `Zotero` ▶ `cmd + A` ▶ 우클릭 ▶ `better bibtex` ▶ `refresh bibtex key`
2. **Obsidian에서 Citiation Key 설정:**
	- `Obsidian` ▶ `Zotero Integration` ▶ `Import Format`
3. **Obsidian에서 인용 추가**:
	- Zotero에서 하이라이트한 내용을 Obsidian으로 불러오고, 논문 인용을 쉽게 추가.
	- 템플릿 설정을 통해 자동으로 인용 메타데이터 추가 가능.
	- `Obsidian` `Obsidian` > `shift + cmd + L` `shift + cmd + L`

```ad-tip
title: Zotero Integration Hotkey
collapse: true

- Obsidian setting ▶ `Hotkey` ▶ **zotero integration** 검색 ▶ `Zotero Integration: Create Literature Notes`
```

<br><br>

### 4. MarkDBConnect를 이용하여 Obsidian의 Literature Notes 관리
#### MarkDBConnect 설정
1. `Zotero` ▶ `환경설정` ▶ `MarkDBConnect` ▶ `Folder Containing Markdown Reading Notes` ▶ Literature Note가 저장이 된 폴더 지정
2. `Advanced Settings` ▶ `Specify a Custom Tag Name?` ▶ 🏷️
3. `Tools` ▶ `MarkDB-Connect Sync Tags`



### 4. 논문 작성 후 Pandoc을 이용한 Word 파일 내보내기
```ad-tip
title: How to install Pandoc
collapse: true

[[How to install Pandoc]]
```

#### Pandoc 설치 및 설정
1. **Pandoc 설치** 후, 커맨드 라인에서 파일 변환을 실행.
2. **Zotero에서 생성된 CSL 파일 사용**:
   - `Zotero` > `Preferences` > `Cite` > 스타일 선택 후 `Tools` → `Style Editor` → **Save As**.
   - 변환 명령어:
     ```bash
     pandoc "file_path_to_export/file_name.md" --bibliography "/file_path_to_Zotero/MyLibrary.json" --citeproc --csl "/file_path_to_Zotero/cfb.csl" -o "/file_path_to_download/test.docx"
     ```

<br>


#### Pandoc 사용 예시
- **Markdown 파일**에서 **Word 파일**로 변환:
  - Obsidian에서 작성한 논문 초안을 **Pandoc**을 통해 Word 파일로 변환.
  - 변환된 Word 파일에서 필요한 부분을 포맷팅 수정 가능.

<br><br>


### 5. Zotero와 Obsidian 연동을 통한 논문 메타데이터 관리
- **Zotero의 논문 메타데이터를 Obsidian과 동기화**.
- Zotero에서 관리한 논문 태그와 메타데이터를 Obsidian에서 자동으로 불러와 관리 가능.



- 📥: **Unread, To Read** (Shortcut Key: 1)
- 📚: **Next To Read** (Shortcut Key: 2)
- 📙: **Reading** (Shortcut Key: 3)
- ✅: **Done Reading** (Shortcut Key: 4)
- 💡: **Cited, Used in Thesis** (Shortcut Key: 5)
- 🚫: **Abandoned, Not Use** (Shortcut Key: 6)
