---
title: "개념정리 — 데이터클래스(dataclass)"
tags: [개념정리, DeepRL, 프로그래밍기초, 파이썬]
related: ["[[Chapter 07 - 고수준 RL 라이브러리]]"]
---

# 데이터클래스(dataclass)

> [!abstract] 한 줄 요약
> **dataclass**는 "몇 개의 값을 한 묶음으로 담아 이름 붙여 놓고 싶을 뿐"인 [[API와 클래스·객체|클래스]]를 아주 짧게 만들도록 도와주는 파이썬 문법이다. `__init__`이나 출력용 코드를 직접 안 써도, 필드 이름만 나열하면 나머지를 자동으로 만들어 준다.

## 1. 왜 필요한가?

여러 값을 하나로 묶고 싶을 때가 많다. 예를 들어 경험 하나를 표현하려면 상태·행동·보상·종료여부 네 값이 함께 필요하다. 보통 클래스라면 이렇게 써야 한다.

```python
class Experience:
    def __init__(self, state, action, reward, done_trunc):
        self.state = state
        self.action = action
        self.reward = reward
        self.done_trunc = done_trunc
```

값 네 개를 저장하려고 5줄이나 썼다. 필드가 늘어날수록 반복도 늘어난다.

## 2. dataclass로 줄이면

```python
from dataclasses import dataclass

@dataclass
class Experience:
    state: int
    action: int
    reward: float
    done_trunc: bool
```

`@dataclass`라는 **데코레이터**(클래스 위에 붙여서 기능을 자동으로 추가해 주는 장식) 한 줄만 붙이면, 파이썬이 자동으로:
- `__init__` (초기화 함수)을 만들어 준다 — `Experience(state=0, action=1, reward=1.0, done_trunc=False)`처럼 바로 생성 가능.
- `__repr__` (화면에 예쁘게 출력하는 함수)을 만들어 준다 — `print(exp)`하면 `Experience(state=0, action=1, ...)` 형태로 알아보기 쉽게 나온다.
- 값 비교(`==`)도 필드끼리 비교하도록 자동 지원한다.

> [!example] 비유 — 서식이 정해진 양식지
> 빈 종이에 매번 "이름:", "나이:", "주소:"를 손으로 써서 양식을 만드는 대신, 미리 인쇄된 **양식지**를 쓰는 것과 같다. 빈칸(필드 이름)만 채워 넣으면 나머지(출력 형식, 비교 방법)는 양식지가 알아서 처리한다.

## 3. PTAN에서의 쓰임

Chapter 7에서 본 `Experience`와 `ExperienceFirstLast`가 바로 dataclass다. `ExperienceSource`가 만들어 내는 경험 조각들이 이 형태로 오기 때문에, `exp.state`, `exp.reward`처럼 **필드 이름으로 바로 접근**할 수 있어 코드가 읽기 쉬워진다.

## 세 줄 정리
- dataclass는 값 여러 개를 묶는 단순한 클래스를 짧게 정의하게 해주는 파이썬 문법이다.
- `@dataclass`를 붙이면 초기화·출력·비교 코드를 자동으로 만들어 준다.
- PTAN의 `Experience`, `ExperienceFirstLast` 객체가 이 방식으로 정의되어 있다.
