---
date: 2024-02-12, 20:51
status: Permanent
tags:
  - Study/Obsidian
aliases:
  - 마크다운
  - 마크다운_문법
  - 프론트매터
reference: 
author: 
url:
---
# General Markdown Grammer
## Headers
제목을 만들 때는 `#`을 사용하며, `#`의 개수에 따라 제목의 수준이 달라집니다.
```text
# 제목 1 (가장 큰 제목)
## 제목 2
### 제목 3
#### 제목 4
```

## Bold
텍스트를 굵게 표시하려면 `**굵게**` 또는 `__굵게__`를 사용하여 텍스트를 감싸면 됩니다.
```text
**굵은 텍스트**
__굵은 텍스트__
```

## Italic
텍스트를 기울임 (이탤릭) 체로 표시하려면 `*` 또는 `_`로 텍스트를 감싸면 됩니다. 앞에서 굵게 하기 위해서는 2개, 기울이는 것은 1개만 사용하는것이 차이점입니다.
```text
*이탤릭 텍스트*
_기울임 텍스트_
```

>[!tip] Bold + Italic
>
>```text
>***굵은 텍스트 + 이탤릭 텍스트***
>___굵은 텍스트 + 이탤릭 텍스트___
>```
>- 결과
>	***굵은 텍스트 + 이탤릭 텍스트***

## Strikethrough
텍스트에 취소선을 추가하려면 `~~`로 텍스트를 감싸면 됩니다.
```text
~~취소선 텍스트~~
```

## List
### 순서가 있는 리스트
```markdown
1. 항목 1
2. 항목 2
3. 항목 3
```

### 순서가 없는 리스트
```markdown
- 항목 1
- 항목 2
- 항목 3
```

## Link
링크를 삽입하려면 `[[URL|링크 텍스트]]` 형식을 사용합니다. 결과 링크의 맨 오른쪽에 붙은 아이콘이 현재 옵시디언 바깥으로 나가는 링크가 삽입되어있다는 의미를 나타냅니다.
```text
[슬기로운 통계생활](https://statisticsplaybook.com/)
```

## Image
이미지를 삽입하려면 `![[이미지 URL|대체 텍스트]]` 형식을 사용합니다.
```text
[위키피디아 흑요석](https://upload.wikimedia.org/360px-ObsidianOregon.jpg)
```

## Blockquotes
인용구를 만들려면 `>`를 사용합니다. 또한 백슬래쉬 (`\`) 을 사용하면 마크다운 문법에 사용되는 기호들을 사용할 수 있습니다.
```text
> 첫번째 블록
>> 두번째 블록
>>> 세번째 블록
```


- 결과
> 첫번째 블록
>> 두번째 블록
>>> 세번째 블록

## Code

인라인 코드는 `backticks`로 감싸고, 코드 블록은 세 개의 `backticks`로 감싸서 작성합니다.
```text
인라인 코드: `print("Hello, World!")`

코드 블록:
	
	```
	def greet():
	    print("Hello, World!")
	```
```
|   |   |   |   |
|---|---|---|---|
|**언어**|**입력어**|**언어**|**입력어**|
|*Html*|*html*|*Bash*|*bash*|
|C|c|Ada|ada|
|*C++*|*c++*|C#|cs|
|CSS|css|*Markdown*|*markdown*|
|CoffeeScript|coffeescript|LISP|lisp|
|Fortran|fortran|ML|ml|
|D|d|Dart|dart|
|BASIC|basic|ActionScript|actionscript|
|MATLAB|matlab|F#|fs|
|OCaml|ocaml|Julia|julia|
|G-code|gcode|Haskell|haskell|
|Elixir|elixir|Erlang|erlang|
|Diff|diff|Ruby|ruby|
|GO|go|TOML|toml|
|Scala|scala|Processing|processing|
|Prolog|prolog|Pascal|pascal|
|INI|ini or INI|Java|java|
|*JavaScript*|*javascript*|*JSON*|*json*|
|Kotlin|kotlin|Less|less|
|Lua|lua|*Makefile*|*makefile*|
|Perl|perl|Objective-C|objectivec|
|PHP|php|*Python*|*python*|
|R|r|Rust|rust|
|SCSS|scss|*Shell*|*shell*|
|SQL|sql|Swift|swift|
|*YAML*|*yaml*|TypeScript|typescript|
|Visual Basic|vb|||

## Horizontal Rule
수평선을 추가하려면 `---`, `___`, 또는 `***`을 사용합니다.
```text
---
***
___
```

## Footnotes
### 기본 각주 문법
문장에 각주를 추가하려면 `[^1]`와 같은 방식으로 텍스트에 각주를 표시하고, 페이지 하단에 해당 각주에 대한 설명을 작성할 수 있습니다.
```text
이것은 간단한 각주[^1]입니다.

[^1]: 이것은 참조된 텍스트입니다.
```

- 결과
	![[58a89a5e3696dee4406bd962fe1e4f00_MD5.png|500]]

### 여러 줄의 각주 작성
각주가 여러 줄에 걸쳐 작성되어야 하는 경우 각 새 줄 앞에 2개의 공백을 추가합니다.
```text
이것은 각주가 여러줄로 달리는 경우[^2]입니다.

[^2]: 각주의 첫 줄입니다.  
  이것은 각주가 여러 줄에 걸쳐 작성될 때 사용하는 방법입니다.
```

- 결과
	![[dac9a2b90b974498b4bfc94f4cc275c1_MD5.png|500]]

### 이름이 지정된 각주
각주에 이름을 지정하여 각주를 더 쉽게 식별하고 참조를 연결할 수 있습니다. 이름이 지정된 각주도 번호로 표시됩니다.
```text
이것은 이름이 지정된 각주[^note]입니다.

[^note]: 이름이 지정된 각주는 여전히 숫자로 표시되지만, 참조를 더 쉽게 식별하고 연결할 수 있게 해줍니다.
```

- 결과
	![[41cf37cb267389e82227fe005c3ee977_MD5.png|500]]

### 문장 안 각주 넣기
각주를 문장 안에 인라인으로 추가할 수도 있습니다. 이 경우, `^`기호가 대괄호 바깥쪽에 위치합니다.
```text
인라인 각주도 사용할 수 있습니다. ^[이것은 인라인 각주입니다.]
```

- 결과
	![[db5b1c1f453dc49920775ff7fb0b1f08_MD5.png|500]]

## Table
본문에 표를 넣을 수 있습니다.  
헤더 셀을 구분할 때 3개 이상의 -(하이픈) 기호가 필요합니다.  
헤더 셀을 구분하면서 :(콜론) 기호로 셀(열/칸) 안에 내용을 정렬할 수 있습니다.  
가장 좌측과 가장 우측에 있는 |(vertical bar) 기호는 생략 가능합니다.
```text
| 첫번째(기본왼쪽정렬) | 두번째(가운데정렬) | 세번째(오른쪽정렬) |
|---|:---:|---:|
| `왼쪽` | 정렬확인1 | abc |
| `정렬` | 정렬확인2 | abcdefgh |
| `123` | 정렬확인,정렬확인,정렬확인 | abcdef |
| `456` | 정렬확인1234 | abc |
```

- 결과

| 첫번째(기본왼쪽정렬) | 두번째(가운데정렬) | 세번째(오른쪽정렬) |
|---|:---:|---:|
| `왼쪽` | 정렬확인1 | abc |
| `정렬` | 정렬확인2 | abcdefgh |
| `123` | 정렬확인,정렬확인,정렬확인 | abcdef |
| `456` | 정렬확인1234 | abc |

# For Obsidian Only
## Highlight
마크다운에는 기본적으로 텍스트 하이라이트 기능이 없습니다. 그러나, 옵시디언에서는 텍스트를 하이라이트 할 수 있습니다.
```
==하이라이트 텍스트==
```

- 결과
	==하이라이트 텍스트==

## Check Box
마크다운으로 체크 박스나 체크 리스트를 삽입하려면 각 목록 항목을 하이픈(`-`)과 공백 뒤에 `[ ]`로 시작하시면 됩니다. 공백 안에 x 표시를 할 경우, 목록에 취소선이 생기게 됩니다. 공백 안을 다른 문자로 채우게 되면, 완료 표시로 바뀌게 됩니다.
```text
- [x] 화분 물 주기
- [-] 우편함 확인
- [ ] 밀린 일기 작성
```

- 결과
	- [x] 화분 물 주기
	- [-] 우편함 확인

>[!tip] 참고
>옵시디언에서는 체크 박스를 쉽게 만들 수 있도록 단축키가 기본으로 제공됩니다. 체크박스를 만들기 원하는 행에 커서를 놓고 `Ctrl + L` 단축키를 누르게 되면 자동으로 체크 박스로 변하게 됩니다.

## Image Size
앞에서 설명한 일반적인 마크다운 이미지 삽입 코드에 옵시디언에서만 작동하는 이미지 크기를 조절하는 옵션이 존재합니다. `![[이미지 URL|대체 텍스트|가로x세로]]` 형식을 사용합니다.
```text
![위키피디아 흑요석|100x100](https://upload.wikimedia.org/commons/thumb/8/8c/ObsidianOregon.jpg/360px-ObsidianOregon.jpg)
```

>[!tip] 참고
># 위키링크 형식을 사용하는 경우
>```text
>![[image.png|200]]
>![[image.png|200x200]]
>```

## Internal Link
내부 링크는 노트 간 또는 블록 간에 서로 연결되는 링크입니다. `[[Markdown Grammer]]` 안에 페이지 이름을 넣어서 생성할 수 있습니다. 이를 통해 빠르게 관련 정보로 이동할 수 있습니다. 예를 들어, Vault 안에 “옵시디언 사용법”이라는 노트가 있는 경우, 다음과 같이 작성하면, 옵시디언 사용법 노트로 가는 링크가 생성됩니다.
```text
[[옵시디언 사용법]]
```

- 결과
	![[bf5e62e37e8dae902f31965ba581c3c6_MD5.png|150]]

## Embedding Link
내부 링크와는 다르게 노트 내용 자체를 다른 노트에 박아놓을 때 사용하는 마크다운 문법입니다. 알고 있는면 상당히 유용합니다. 
현재 노트에 다른 노트가 임베딩 되어 있다는 표시가 되어 있는 것을 확인 할 수 있습니다.
```text
![[옵시디언 사용법]]
```

- 결과
	![[c9c79ca93e1aa1d7f3b8c21e6823c060_MD5.png|500]]

## Block Reference
블록 참조는 다른 블록 내용을 현재 블록에 포함시키는 기능입니다. `![[블록 링크#^id]]` 형식으로 사용합니다.
ID를 부여한 문단 만 임베딩 되며, 사용자가 ID를 직접 부여하기 위해선 문단 끝에 `^myobsi` 형식으로 사용합니다.
![[94a907200b4fad9504e5223ed1ffa931_MD5.png|500]]
```text
![[옵시디언 사용법#^myobsi]]
```

- 결과
	![[4985d563e85f2ecd8601698b393af502_MD5.png|500]]

## Callout
내용을 쓰다가 강조하는 부분이 있다거나, 정리를 할 때 유용한 문법입니다.
```text
> [!note]  이것만  알아두세요!
>  옵시디언은 정말 편한 도구입니다.
```

- 결과
> [!note]  이것만  알아두세요!
>  옵시디언은 정말 편한 도구입니다.

### Callout 지원리스트
Callout 문법이 좋은 이유는 위의 문법에서 `[!note]` 부분을 다음과 같은 키워드로 바꿔주면 알맞은 아이콘에 색상이 다른 Callout 상자가 생성된다는 것입니다. 한번씩 시도해보세요! (같은 줄에 있는 단어들은 같은 아이콘 유사어들입니다.)

- [!note]
- [!abstract], [!summary], [!tldr]
- [!info]
- [!todo]
- [!tip], [!hint], [!important]
- [!success], [!check], [!done]
- [!question], [!help], [!faq]
- [!warning], [!caution], [!attention]
- [!failure], [!fail], [!missing]
- [!danger], [!error]
- [!bug]
- [!example]
- [!quote], [!cite]

# Meta Data
- 문서 자체는 아니지만 문서에 관련된 정보를 담고 있는 데이터
- 문서의 생성날짜, 마지막 수정시간, 태그 등
- 메타 데이터를 등록해놓으면, 나중에 Dataview나 Search 등을 통해 대시보드를 만들거나 통계관리를 할 수 있음

## Frontmatter
- 문서 맨 압에 메타데이터를 기록하는 공간을 만들어 두는 것

### 옵시디언 프론트매터 생성방법
1. 문서 맨 앞에 수평선(`---`)
2. `key: value` 형태로 원하는 매타 데이터를 기록
3. `value`가 여러 개일 때
	1. `key: [value1, value2, ...]`
	2. `key:` 에서 개행을 하고 그 밑에 목록(`-`) 형태로 적는 방법

```ad-summary
title: Frontmatter
~~~ruby
---
key1: value
key2: value
key3: [value1, value2, ...]
key4:
- value1
- value2
---
~~~
```

## 프론트매터 기본요소 (Tags, Aliases)
- 옵시디언 기본 `key` 값
  1. `tags`: 옵시디언 노트의 태그 속성 관리
  2. `aliases`: 옵시디언 노트의 별칭 속성 관리
  3. `cssclass`: css snippet 중 적용할 속성 관리
  4. `publish`: 옵시디언 publish 서비스 이용시, 출판 여부 관리

### Tags
- 문서에 꼬리말을 붙이는 문서 관리의 한 방식
- `TAGS`, `TAG`, `tags`, `tag`등 대소문자, 단수형 복수형에 상관없이 모두 같은 기능
- 검색이나 Dataview를 만들 때 태그를 기준으로 검색하거나 쿼리를 만들 수 있기 때문에 tag를 통한 구조화를 잘 해 놓는다면 문서 관리에 도움이 됨

#### Tags 입력 방법
1. 문서 처음의 프론트매터에 `tag: value` 형태로 입력
2. 문서 아무데나 `#tag1`과 같이 `#`를 사용해서 태그 입력

#### Tag 작성 규칙
- 프론트매터에 태그를 적을 때는 `#`을 쓰지 않음
- 태그에는 띄어쓰기를 허용하지 않음
- 띄어쓰기 대신, 다음처럼 대시(`-`), 언더바(`_`)fmf tkdyd
	- Camel 스타일: `moreThanOneWords`
	- Paskal 스타일: `MoreThanTwoWords`
	- Snake 스타일: `more_than_two_words`
	- kebab 스타일: `more-than-two-words`
- 계층형 태그 생성을 위해선 슬래시(`/`)를 사용
	- 예시: `machine/car/engine`

### Aliases
- 문서 이름은 1개이지만, 여러가지 별칭을 정해줄 수 있음
- 다른 문서에서 내부링크(internal link)를 형성할 때 '별칭'을 기준으로 검색을 할 수도 있고, 별칭이 기입된 모든 문서에 백링크를 걸어줄 수 있음

#### Aliases 입력 방법
- 프론트매터에 `aliases`를 추가해서 만들 수 있음
```ruby
---
aliases: [별칭1, 별칭2, ...]
aliases:
- 별칭1
- 별칭2
---
```

#### Aliases 활용하기
- 가장 좋은 방법은 내부링크(`[[Markdown Grammer]]`)를 걸어주거나 백링크(back link)를 걸어줄 때

## Inline field
- 문서 중간에 삽입할 수 있음
- 메타 데이터의 내용이 본문에 노출됨

### 옵시디언 인라인필드 생성방법
- 문서 중간에 `key::value` 또는 `[key::value]` 형태로 기입
- 프론트매터와 다르게 본문을 작성할 때 사용
````ad-example
~~~markdown
오늘 할 요리는 라면입니다. 들어갈 재료는 [재료::면], [재료::분말스프], [재료::건더기스프] 입니다.

```dataview
TABLE 재료
WHERE file.name = this.file.name
```
~~~
````
```dataview
TABLE 재료
WHERE file.name = this.file.name
```

# Reference
1. <https://statisticsplaybook.com/obsidian-markdown-cheatsheet/>
2. <https://velog.io/@phobos90/%EB%A7%88%ED%81%AC%EB%8B%A4%EC%9A%B4%EB%AC%B8%EB%B2%95%EC%A0%95%EB%A6%AC>
3. <https://kexplain.com/17>