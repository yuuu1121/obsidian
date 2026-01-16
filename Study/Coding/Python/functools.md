---
date: 2024-08-19
status: Permanent
tags: 
aliases: 
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: true
---
# functools 란?

- Python 표준 라이브러리의 일부로, 함수형 프로그래밍을 지원하는 유용한 도구들을 제공하는 모듈
- 함수의 동작을 변경하거나, 반복적으로 사용되는 코드를 간결하게 작성할 수 있도록 도와주는 여러 기능을 포함

<br/>

## functools.partial

- Python에서 함수는 매개 변수를 입력받아 어떤 작업을 수행하는데, 때로는 ==이 매개변수들 중 일부가 **고정된 값**을 갖는 경우가 있음==
- 예를들어, 여러 번 호출하는 함수에서 매번 동일한 값을 전달해야 한다면, `partial` 함수를 사용하여 그 값을 고정시킨 새로운 함수를 정의하여 사용

	```python
	from functools import partial
	
	def multiply(a, b, c):
		return a * b * c
	```

- 이 함수에서 두 개의 값 'a'와 'b'를 항상 3과 5로 고정하고 싶을 때 `partial` 사용
- 새로운 함수는 세 번째 인자만 입력받아 결과를 반환함

	```python
	partial_multiply = partial(multiply, 3, 5)
	
	print(partial_multiply(6)) # output: 3 * 5 * 6 = 90
	```

- `partial` 함수에 *Func* 인자를 *Keywords 형식*으로도 줄 수 있으나, ==Arguments의 순서에 해당하는 Parameter가 Keywords에서 또 전달되는 경우==, 충돌하여 에러가 발생할 수 있음

```python
partial_multiply2 = partial(multiply, b = 5, a = 3) # It delivers 5 to 'b' parameter, and 3 to 'a' parameter

print(partial_multiply2(c = 6)) # output: 90

print(partial_multiply2(6)) # It raise TypeError: <lambda>() got multiple values for argument 'a'.
# Because args deliver a=6, and keywords defined in partial also deliver a = 6.
```