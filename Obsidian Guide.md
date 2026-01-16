# Obsidian 사용 가이드

---

## 목차
1. [[#핫키 (단축키)]]
2. [[#활성화된 플러그인]]
3. [[#플러그인 사용법]]
4. [[#Daily Note 시스템]]
5. [[#폴더 구조]]

---

## 핫키 (단축키)

> Mac: `Cmd` / Windows: `Ctrl`

### 기본 단축키

| 단축키 | 기능 |
|--------|------|
| `Cmd + T` | 오늘의 Daily Note 열기 |
| `Cmd + O` | Quick Switcher (파일 빠른 검색) |
| `Cmd + G` | Graph View (그래프 뷰) |
| `Cmd + Shift + P` | Command Palette (명령어 팔레트) |

### 사이드바

| 단축키 | 기능 |
|--------|------|
| `Cmd + Shift + L` | 왼쪽 사이드바 토글 |
| `Cmd + Shift + R` | 오른쪽 사이드바 토글 |

### 텍스트 서식

| 단축키 | 기능 | 결과 |
|--------|------|------|
| `Cmd + B` | 굵게 | **텍스트** |
| `Cmd + I` | 기울임 | *텍스트* |
| `Cmd + H` | 하이라이트 | ==텍스트== |
| `Cmd + Shift + S` | 취소선 | ~~텍스트~~ |
| `Cmd + `` ` `` | 인라인 코드 | `코드` |

### 템플릿 & 노트

| 단축키 | 기능 |
|--------|------|
| `Cmd + Shift + T` | 템플릿 삽입 |
| `Cmd + Shift + C` | 체크박스 삽입 |
| `Cmd + Enter` | 줄바꿈 (`<br>`) |

### 플러그인 단축키

| 단축키 | 기능 |
|--------|------|
| `Cmd + Shift + D` | Excalidraw 드로잉 생성 |
| `Cmd + Shift + K` | 새 Kanban 보드 생성 |
| `Cmd + Shift + B` | 블록 링크 복사 |
| `Cmd + Alt + L` | Zotero Literature Note 생성 |

### 네비게이션

| 단축키 | 기능 |
|--------|------|
| `Cmd + Alt + ←` | 뒤로 가기 |
| `Cmd + Alt + →` | 앞으로 가기 |

---

## 활성화된 플러그인

### 핵심 플러그인 (31개)

| 카테고리 | 플러그인 | 설명 |
|----------|----------|------|
| **Daily Notes** | Calendar | 캘린더에서 날짜 클릭하여 Daily Note 생성 |
| | Periodic Notes | Daily/Weekly Note 관리 |
| | Homepage | Obsidian 시작 시 Daily Note 자동 열기 |
| **템플릿** | Templater | 고급 템플릿 기능 (변수, 함수 등) |
| **데이터** | Dataview | SQL처럼 노트 쿼리 및 테이블 생성 |
| **논문/연구** | Zotero Connector | Zotero 연동 |
| | Citations | 인용 관리 |
| | Pandoc | 다양한 형식으로 내보내기 (PDF, Word 등) |
| **시각화** | Excalidraw | 손그림 다이어그램/스케치 |
| | Kanban | Trello 스타일 보드 |
| **편집** | Advanced Tables | 테이블 편집 도구 |
| | Outliner | 아웃라인 편집 향상 |
| | Quick LaTeX | 수식 입력 |
| | Code Styler | 코드 블록 스타일링 |
| **UI/UX** | Floating TOC | 떠 있는 목차 |
| | Hover Editor | 링크 호버 시 편집 팝업 |
| | Style Settings | 테마 커스터마이징 |
| | Editor Width Slider | 편집기 너비 조절 |
| **유틸리티** | Auto Link Title | URL 붙여넣기 시 제목 자동 가져오기 |
| | Copy Block Link | 블록 링크 쉽게 복사 |
| | Emoji Shortcodes | `:smile:` → 😄 |
| | Image Toolkit | 이미지 확대/축소 |
| | Local Images Plus | 이미지 로컬 저장 |
| | Link Embed | 링크 미리보기 |
| **백업** | Obsidian Git | GitHub 자동 백업 |
| **기타** | Tag Wrangler | 태그 관리 |
| | Admonition | 콜아웃 블록 |
| | Advanced URI | 외부에서 노트 열기 |

---

## 플러그인 사용법

### 1. Calendar (캘린더)
- **위치:** 오른쪽 사이드바
- **사용법:** 날짜 클릭 → Daily Note 자동 생성
- **점 표시:** 해당 날짜에 노트가 있으면 점으로 표시

### 2. Templater (템플릿)
- **템플릿 위치:** `Templates/` 폴더
- **사용법:** `Cmd + Shift + T` → 템플릿 선택
- **변수 예시:**
  - `2026-01-16` - 오늘 날짜
  - `Obsidian Guide` - 파일 이름

### 3. Dataview (데이터 쿼리)
코드블록으로 노트를 쿼리할 수 있습니다:

```dataview
TABLE file.ctime AS "생성일"
FROM "Study"
SORT file.ctime DESC
LIMIT 10
```

### 4. Excalidraw (드로잉)
- **생성:** `Cmd + Shift + D`
- **사용법:**
  - 왼쪽 도구 모음에서 도형 선택
  - 드래그하여 그리기
  - 텍스트 추가: `T` 키

### 5. Kanban (칸반 보드)
- **생성:** `Cmd + Shift + K`
- **사용법:**
  - 열(Column) 추가: `+ Add a list`
  - 카드 추가: 각 열에서 `+ Add a card`
  - 드래그 앤 드롭으로 카드 이동

### 6. Quick LaTeX (수식)
- **인라인 수식:** `$E = mc^2$` → $E = mc^2$
- **블록 수식:**
```
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### 7. Admonition (콜아웃)
```markdown
> [!note] 제목
> 내용

> [!warning] 주의
> 중요한 내용

> [!tip] 팁
> 유용한 정보
```

### 8. Zotero Integration
1. Zotero에서 논문 추가
2. Obsidian에서 `Cmd + Alt + L`
3. 논문 선택 → Literature Note 자동 생성

### 9. Git 자동 백업
- **설정:** 이미 구성됨
- **자동 커밋:** 2분마다
- **자동 푸시:** 5분마다
- **리포지토리:** `github.com/yuuu1121/obsidian`

### 10. Graph View (그래프 뷰)
- **열기:** `Cmd + G`
- **Local Graph:** 오른쪽 사이드바 하단
- **사용법:** 노트 간 연결 시각화, 클릭하여 노트 이동

---

## Daily Note 시스템

### 구조
```
Daily Notes/
├── 2026-01-16.md
├── 2026-01-17.md
└── ...
```

### 템플릿 내용
- **날짜 헤더** + 어제/내일 링크
- **Today's Focus** - 오늘의 메인 목표
- **Tasks** - Must Do / Should Do
- **Notes & Ideas** - 메모
- **태그** - `#daily/2026/01`

### 사용법
1. `Cmd + T` 또는 캘린더에서 날짜 클릭
2. 템플릿 자동 적용
3. 할 일 체크박스 사용: `- [ ]`

---

## 폴더 구조

```
YJU_Obsidian/
├── Study/                    # 공부 노트
│   ├── Deep_Learning/
│   ├── Machine_Learning/
│   ├── Statistics/
│   ├── Reinforcement_Learning/
│   ├── OpenCV/
│   ├── Coding/
│   ├── Filter/
│   ├── Ansys/
│   └── Zettelkasten/
├── Paper/                    # 논문 관련
│   ├── Reviews/
│   ├── Zotero/
│   └── 논문 작성 유의사항.md
├── Daily Notes/              # 일일 노트
├── Templates/                # 템플릿
│   ├── Daily Note.md
│   ├── Weekly Note.md
│   ├── Literature Note.md
│   └── Paper Review Templates/
├── Annotations/              # 개념 정의
└── Obsidian Guide.md         # 이 가이드
```

---

## 유용한 마크다운 문법

### 링크
- 내부 링크: `[[노트 이름]]`
- 별칭 링크: `[[노트 이름|표시할 텍스트]]`
- 외부 링크: `[텍스트](URL)`

### 임베드
- 노트 임베드: `![[노트 이름]]`
- 이미지: `![[이미지.png]]`
- 특정 헤더: `![[노트#헤더]]`

### 체크박스
```markdown
- [ ] 할 일
- [x] 완료된 일
```

### 콜아웃 타입
- `[!note]` - 노트
- `[!tip]` - 팁
- `[!warning]` - 경고
- `[!danger]` - 위험
- `[!example]` - 예시
- `[!quote]` - 인용

---

## PDF로 내보내기

1. 이 노트 열기
2. `Cmd + P` → "Export to PDF" 검색
3. 또는 우클릭 → "Export to PDF"

---

> 마지막 업데이트: 2026-01-16
>
> **Sources:**
> - [The Must-Have Obsidian plugins for 2025](https://www.dsebastien.net/2022-10-19-the-must-have-obsidian-plugins/)
> - [Best Obsidian Plugins for Academics](https://effortlessacademic.com/best-obsidian-plugins-for-academics/)
> - [Obsidian Forum](https://forum.obsidian.md/)
