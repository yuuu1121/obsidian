---
title: "Chapter 3 — PyTorch로 하는 딥러닝 (Deep Learning with PyTorch)"
book: "Deep Reinforcement Learning Hands-On, 3rd Ed."
chapter: 3
tags: [DeepRL, 강화학습, PyTorch, 딥러닝, 텐서, autograd, GPU, GAN]
---

# Chapter 3 · PyTorch로 하는 딥러닝

> [!abstract] 이 챕터를 한 문장으로
> **PyTorch**는 "숫자 덩어리(텐서)를 다루고, 그 계산의 미분(기울기)을 자동으로 구해주는" 도구상자다. 이 챕터에서는 **텐서 → GPU 연산 → 자동미분(gradient) → 신경망 블록(`nn.Module`) → 손실함수·옵티마이저 → 학습 루프 → TensorBoard 모니터링**까지, Deep RL을 만들 때 반드시 필요한 PyTorch의 뼈대를 익힌다. 마지막엔 Atari 게임 화면을 흉내 내는 **GAN**을 직접 만들어 본다.

---

## 들어가며 — 왜 PyTorch가 필요한가?

1장에서 우리는 "에이전트가 환경과 상호작용하며 보상을 최대화하는 정책을 배운다"는 강화학습의 큰 그림을 배웠다. 그런데 정책이나 가치 함수를 실제로 **어떤 함수로 표현**할 것인가? 바둑판 크기의 표를 만들어 모든 경우를 다 적어둘 수도 있지만, 상태의 개수가 조금만 커져도(예: 게임 화면 픽셀 조합) 그런 표는 우주보다 커진다.

그래서 우리는 **신경망(Neural Network)** 이라는, 적은 개수의 "손잡이(가중치)"로 아주 복잡한 함수를 흉내 낼 수 있는 도구를 쓴다. 신경망·경사하강·역전파의 기본 아이디어는 이미 [[신경망 경사하강 역전파 기초]]에서 비유로 익혔다. 이 챕터는 그 아이디어를 **실제 코드로 돌리는 도구인 PyTorch**를 배우는 자리다.

> [!note] 이 챕터는 "완전한 딥러닝 교과서"가 아니다
> 저자도 밝히듯, 이 챕터는 여러분이 신경망·경사하강 같은 딥러닝 기초 개념을 이미 안다고 가정하고, **PyTorch라는 도구의 사용법**만 집중적으로 다룬다. 딥러닝 자체가 궁금하면 [[신경망 경사하강 역전파 기초]]를 먼저 복습하자.

이 챕터에서 다루는 것 세 가지:
- PyTorch 라이브러리 자체의 사용법과 구현 세부사항
- PyTorch 위에 얹어 쓰는 상위 레벨 라이브러리(예: Ignite)
- 학습 과정을 모니터링하는 PyTorch Ignite와 TensorBoard

> [!tip] 버전 안내
> 이 챕터의 모든 예제는 최신 **PyTorch 2.3.1** 기준으로 갱신되었다. 2판에서 쓰던 PyTorch 1.3.0과 비교해 API가 꽤 바뀌었으니, 옛날 버전을 쓰고 있다면 업그레이드를 권장한다.

---

## 1. 텐서 (Tensors)

### 1.1 텐서란 무엇인가?

**텐서(tensor)** 는 모든 딥러닝 도구의 **기본 벽돌**이다. 이름은 신비롭게 들리지만, 사실 텐서는 그냥 **다차원 배열(multi-dimensional array)** 일 뿐이다. [[텐서와 다차원배열]] 참고.

학교 수학에 비유하면 이렇다.

- 숫자 하나(스칼라) = **점** — 0차원
- 벡터(숫자들의 줄) = **선분** — 1차원
- 행렬(숫자들의 표) = **2차원 평면**
- 그 이상 차원의 숫자 묶음 = **텐서** (행렬처럼 따로 이름 붙은 게 없어서 뭉뚱그려 "텐서"라 부른다)

![[fig_3_1_v3.png]]
*그림 3.1 — 숫자 하나에서 n차원 텐서로 나아가는 모습(점 → 벡터 → 행렬 → 3D 텐서 → n텐서)*

> [!warning] 딥러닝의 "텐서" ≠ 수학의 "텐서"
> 딥러닝에서 텐서는 그냥 **다차원 배열**이다. 그런데 수학(텐서 미적분·텐서 대수)에서 "텐서"는 **벡터공간 사이의 사상(mapping)** 이라는 훨씬 무거운 의미를 가진 용어다. 딥러닝 커뮤니티가 이미 확립된 수학 용어를 다른 뜻으로 가져다 쓴 셈이라, 수학자들이 보면 눈살을 찌푸릴 수 있다는 농담 섞인 경고가 원서에 있다. 우리는 "다차원 배열"이라는 뜻으로만 쓰면 된다.

### 1.2 텐서 만들기

NumPy를 써봤다면 이미 텐서를 다뤄본 것과 같다. NumPy의 다차원 배열이 사실상 텐서이기 때문이다. 예를 들어 컬러 이미지 하나는 (너비, 높이, 색상채널) 3개 차원을 가진 3D 텐서로 표현할 수 있다.

PyTorch에서 텐서는 **원소의 타입**으로도 구분된다. 지원하는 타입은 13가지:

| 분류 | 종류 |
|---|---|
| 실수(float) | 16비트(`float16`, `bfloat16`), 32비트, 64비트 — 총 4종 |
| 복소수(complex) | 32비트, 64비트, 128비트 — 3종 |
| 정수(integer) | 8비트 부호있음/없음, 16·32·64비트 부호있음 — 5종 |
| 불리언 | `bool` — 1종 |

가장 자주 쓰는 클래스는 `torch.FloatTensor`(32비트 float), `torch.ByteTensor`(8비트 부호없는 정수), `torch.LongTensor`(64비트 부호있는 정수)다.

텐서를 만드는 3가지 방법:
1. 원하는 타입의 **생성자를 직접 호출**한다.
2. `torch.zeros()`처럼 **특정 값으로 채워진 텐서를 만들어 달라고 요청**한다.
3. **NumPy 배열이나 파이썬 리스트를 텐서로 변환**한다. 이 경우 타입은 원본을 따라간다.

```python
$ python
>>> import torch
>>> import numpy as np
>>> a = torch.FloatTensor(3, 2)   # 3행 2열의 float 텐서 생성 (내용은 0으로 초기화)
>>> a
tensor([[0., 0.],
        [0., 0.],
        [0., 0.]])
```

- `torch.FloatTensor(3, 2)`: **3×2 크기의 float 텐서**를 만든다. 최신 PyTorch는 메모리를 **0으로 초기화**해서 돌려준다(과거 버전은 초기화 안 된 쓰레기값을 그대로 뒀는데, 조금 빠른 대신 안전하지 않았다). 이 초기화 안 된 상태에 의존하지 말고 항상 값을 명시적으로 채우라고 책은 경고한다.

값을 명시적으로 0으로 채우는 두 가지 방법:

```python
>>> torch.zeros(3, 4)             # (1) 생성 함수로 아예 0으로 채워서 생성
tensor([[0., 0., 0., 0.],
        [0., 0., 0., 0.],
        [0., 0., 0., 0.]])

>>> a.zero_()                      # (2) 이미 있는 텐서를 그 자리에서 0으로 덮어쓰기
tensor([[0., 0.],
        [0., 0.],
        [0., 0.]])
```

> [!important] `inplace` 연산 vs `functional` 연산 — 이름 끝의 밑줄(`_`)
> PyTorch 연산은 두 종류다.
> - **inplace(제자리) 연산**: 함수 이름 끝에 밑줄(`_`)이 붙는다(예: `zero_()`). **텐서 내용 자체를 바꾸고**, 그 객체 자신을 반환한다.
> - **functional(함수형) 연산**: 원본은 그대로 두고, **수정된 새 복사본**을 만들어 돌려준다.
>
> inplace는 메모리·성능 면에서 더 효율적이지만, 그 텐서가 코드 여러 곳에서 공유되고 있다면 "몰래 바뀐 값" 때문에 숨은 버그가 생길 수 있다. 이 구분(끝에 `_`가 있으면 "제자리에서 바꾼다")은 PyTorch 전체에서 매우 자주 나오는 규칙이니 꼭 기억하자.

파이썬 리스트나 튜플로도 텐서를 만들 수 있다.

```python
>>> torch.FloatTensor([[1,2,3],[3,2,1]])   # 중첩 리스트를 그대로 텐서 내용으로 사용
tensor([[1., 2., 3.],
        [3., 2., 1.]])
```

NumPy 배열에서 텐서로 변환하는 예:

```python
>>> n = np.zeros(shape=(3, 2))
>>> n
array([[0., 0.],
       [0., 0.],
       [0., 0.]])
>>> b = torch.tensor(n)     # NumPy 배열 → PyTorch 텐서
>>> b
tensor([[0., 0.],
        [0., 0.],
        [0., 0.]], dtype=torch.float64)
```

`torch.tensor()` 함수는 NumPy 배열을 인자로 받아 **알맞은 모양의 텐서**를 만든다. 위 예에서 `np.zeros`가 기본으로 만드는 배열은 **64비트 float(double)** 타입이라, 결과 텐서도 `dtype=torch.float64`로 표시된다(`dtype`으로 실제 타입이 보인다).

> [!tip] double(64비트)은 대개 과하다
> 딥러닝에서는 보통 **64비트 정밀도가 필요 없다.** 오히려 메모리와 연산 속도만 손해다. 관행적으로 **32비트 float**, 심지어 **16비트 float**로도 충분한 경우가 많다. 명시적으로 32비트로 만들려면 NumPy 쪽에서 타입을 지정해야 한다.

```python
>>> n = np.zeros(shape=(3, 2), dtype=np.float32)
>>> torch.tensor(n)
tensor([[0., 0.],
        [0., 0.],
        [0., 0.]])
```

또는 `torch.tensor()`의 `dtype` 인자에 **PyTorch 쪽 타입**을 직접 지정해도 된다. (주의: NumPy 타입이 아니라 `torch.float32`처럼 `torch` 패키지 소속 타입이어야 한다.)

```python
>>> n = np.zeros(shape=(3,2))
>>> torch.tensor(n, dtype=torch.float32)
tensor([[0., 0.],
        [0., 0.],
        [0., 0.]])
```

> [!note] 호환성 메모 — `torch.tensor()` vs `torch.from_numpy()`
> `torch.tensor()`와 명시적 타입 지정은 PyTorch 0.4.0 버전에서 추가된, 텐서 생성을 단순화하는 개선이다. 예전에는 `torch.from_numpy()`가 NumPy 배열을 변환하는 표준 방법이었지만, 파이썬 리스트와 NumPy 배열이 섞였을 때 처리가 애매한 문제가 있었다. `from_numpy()`는 하위 호환을 위해 아직 남아있지만, 더 유연한 `torch.tensor()`를 쓰는 게 권장된다.

### 1.3 스칼라 텐서 (0차원 텐서)

PyTorch 0.4.0부터 **0차원 텐서(스칼라 값에 대응)** 를 지원한다(그림 3.1 맨 왼쪽 "점"에 해당). 이런 텐서는 예를 들어 다른 텐서의 모든 값을 더하는 연산(`sum()`)의 결과로 자연스럽게 나온다. 예전에는 이런 경우를 억지로 "차원 1짜리 1차원 텐서(벡터)"로 다뤄야 했는데, 값에 접근하려면 인덱싱까지 해야 해서 번거로웠다.

이제는 0차원 텐서가 기본 지원되고, `torch.tensor()` 함수로도 만들 수 있다. 실제 파이썬 값(스칼라)을 꺼내려면 특별한 `item()` 메서드를 쓴다.

```python
>>> a = torch.tensor([1,2,3])
>>> a
tensor([1, 2, 3])
>>> s = a.sum()            # 모든 원소를 더함 → 0차원(스칼라) 텐서
>>> s
tensor(6)
>>> s.item()                # 텐서 안의 "진짜 파이썬 숫자"를 꺼낸다
6
>>> torch.tensor(1)
tensor(1)
```

### 1.4 텐서 연산 (Tensor operations)

텐서에 적용 가능한 연산은 수도 없이 많아 다 나열하기 어렵다. 보통은 PyTorch 공식 문서(http://pytorch.org/docs/)를 검색해서 찾는다. 연산을 찾을 곳은 두 군데다.

- **`torch` 패키지**: 함수가 텐서를 **인자로** 받는 형태 (예: `torch.stack(t)`)
- **텐서 클래스 자체**: 함수가 **그 텐서 위에서 직접 호출**되는 형태 (예: `t.stack()`)

대부분의 텐서 연산은 **NumPy와 대응**되도록 설계되어 있다. NumPy에 흔한 함수가 있으면 PyTorch에도 있을 가능성이 크다(예: `torch.stack()`, `torch.transpose()`, `torch.cat()`). NumPy에 익숙한 사람이라면 문서를 안 봐도 PyTorch 코드를 바로 읽을 수 있는 이유다.

### 1.5 GPU 텐서

PyTorch는 **CUDA GPU**를 투명하게(transparent) 지원한다. 즉 모든 연산에 CPU 버전과 GPU 버전이 둘 다 존재하고, **어떤 텐서를 다루느냐에 따라 자동으로 알맞은 버전이 선택**된다. [[GPU와 CUDA]] 참고.

지금까지 본 모든 텐서 타입은 CPU용이고, 각각에 대응하는 **GPU 버전**이 있다. 유일한 차이는 GPU 텐서가 `torch.cuda` 패키지에 있다는 것이다. 예를 들어 `torch.FloatTensor`는 CPU 메모리에 있는 32비트 float 텐서지만, `torch.cuda.FloatTensor`는 그 GPU 버전이다.

> [!note] CPU·GPU를 넘어선 "backend" 개념
> 사실 PyTorch 내부에는 **backend**라는 더 일반적인 개념이 있다. backend는 메모리를 가진 **추상적인 연산 장치**다. 텐서는 이 backend의 메모리에 할당되고 연산도 그 안에서 수행된다. 예를 들어 Apple 하드웨어에서는 `mps`라는 이름의 backend로 **Metal Performance Shaders(MPS)** 를 지원한다. 이 챕터는 CPU와 GPU에 집중하지만, 코드를 크게 고치지 않고도 훨씬 다양한 하드웨어에서 돌릴 수 있다.

CPU에서 GPU로(혹은 그 반대로) 텐서를 옮기려면 `to(device)` 메서드를 쓴다. 이미 그 장치에 있는 텐서라면 아무 일도 일어나지 않고 원래 텐서를 그대로 돌려준다. 장치 이름은 여러 방식으로 지정 가능한데, 가장 간단한 건 문자열이다 — CPU 메모리는 `"cpu"`, GPU는 `"cuda"`. GPU가 여러 장이면 콜론 뒤에 인덱스를 붙인다(0번부터 시작). 예: 두 번째 GPU 카드는 `"cuda:1"`.

```python
>>> a = torch.FloatTensor([2,3])
>>> a
tensor([2., 3.])
>>> ca = a.to('cuda')      # CPU 텐서를 GPU로 복사
>>> ca
tensor([2., 3.], device='cuda:0')
```

- `a.to('cuda')`: CPU에 있던 텐서 `a`의 **복사본을 GPU 메모리에** 만든다. 반환된 `ca`는 이제 `device='cuda:0'`이라는 표시가 붙는다.
- 두 복사본(`a`, `ca`) 모두 연산에 그대로 쓸 수 있고, GPU 관련 세부사항은 사용자에게 **완전히 투명**하다.

```python
>>> a + 1
tensor([3., 4.])
>>> ca + 1
tensor([3., 4.], device='cuda:0')
>>> ca.device
device(type='cuda', index=0)
```

`to()`와 `device` 클래스를 쓰는 조금 더 효율적인 방법도 있다. `torch.device` 클래스는 장치 종류와 (선택적으로) 인덱스를 담고 있고, 텐서의 `device` 속성으로 현재 위치도 확인할 수 있다.

> [!tip] 옛날 방식: `cpu()`/`cuda()` 메서드
> `to()`와 `torch.device`는 0.4.0에서 도입되었다. 그 이전에는 CPU↔GPU 복사를 각각 `cpu()`와 `cuda()`라는 **별도의 텐서 메서드**로 했다. 요즘은 프로그램 처음에 원하는 `torch.device` 객체를 만들어두고, 만드는 모든 텐서에 `to(device)`를 적용하는 방식이 더 일반적이다. 예전 메서드도 여전히 남아있어서, "무조건 CPU(또는 GPU)에 있게 강제하고 싶을 때" 편리하게 쓸 수 있다.

---

## 2. 그래디언트 (Gradients)

GPU를 투명하게 다룰 수 있다는 것만으로는 아직 부족하다. 딥러닝 도구의 진짜 "킬러 기능"은 **그래디언트(gradient, 기울기)의 자동 계산**이다. [[자동미분과 계산그래프]] 참고. 이 기능은 원래 Caffe 툴킷에서 처음 구현됐고, 이후 딥러닝 라이브러리들의 사실상 표준이 되었다.

옛날에는 그래디언트를 **손으로** 계산해야 했다 — 아무리 단순한 신경망이라도 극도로 고통스러운 일이었다. 모든 함수의 도함수를 구하고, 연쇄법칙을 적용하고, 그 계산 결과를 직접 코드로 구현해야 했다(제대로 됐길 기도하면서). 딥러닝의 원리를 깊이 이해하는 데는 좋은 연습이 될 수 있지만, 신경망 구조를 이것저것 바꿔가며 실험할 때마다 매번 반복하고 싶은 일은 절대 아니다.

다행히 이제 그런 시절은 지나갔다(마치 납땜인두와 진공관으로 하드웨어를 프로그래밍하던 시절이 지난 것처럼!). 지금은 수백 개 층으로 이뤄진 신경망을 정의하는 데 미리 만들어진 building block들을 조립하기만 하면 된다. 그러면 **모든 그래디언트가 알아서 계산되고, 역전파되고, 네트워크에 적용**된다. 단, 이를 위해서는 네트워크 구조를 반드시 **DL 라이브러리의 기본 단위(primitive)** 를 이용해 정의해야 한다.

![[fig_3_2_v3.png]]
*그림 3.2 — 신경망을 통한 데이터와 그래디언트의 흐름 방향(입력→출력은 데이터, 출력에서 거꾸로는 그래디언트)*

### 2.1 정적 그래프 vs 동적 그래프

그래디언트를 계산하는 방식에 따라 근본적인 차이가 생긴다. 두 가지 접근법이 있다.

| 방식 | 설명 | 대표 라이브러리 |
|---|---|---|
| **정적 그래프(Static graph)** | 계산을 **미리 정의**해야 하고, 나중에 바꿀 수 없다. 실제 계산 전에 라이브러리가 그래프를 처리·최적화한다. | TensorFlow(2.0 이전), Theano 등 |
| **동적 그래프(Dynamic graph)** | 그래프를 미리 정의할 필요가 없다. 데이터 변환에 쓸 연산을 그냥 **실행**하면 된다. 그 과정에서 라이브러리가 수행된 연산의 순서를 **기록**해두고, 그래디언트 계산을 요청하면 그 기록을 거꾸로 풀어(unroll)가며 네트워크 파라미터의 그래디언트를 누적한다. | PyTorch, Chainer 등 (일명 "notebook gradients") |

두 방식 모두 장단점이 있다.
- **정적 그래프**는 보통 더 빠르다. 모든 계산을 미리 GPU로 옮길 수 있어 데이터 전송 오버헤드가 줄어든다. 게다가 라이브러리가 연산 순서를 최적화하거나 필요없는 부분을 아예 제거할 자유가 더 크다.
- **동적 그래프**는 계산 부담이 조금 더 크지만, 개발자에게 훨씬 큰 자유를 준다. 예를 들어 "이 데이터에는 네트워크를 두 번 적용하고, 저 데이터에는 그래디언트를 배치 평균으로 클리핑한 완전히 다른 모델을 쓰겠다"처럼 **데이터마다 다르게 처리**할 수 있다.

동적 그래프의 또 다른 매력은 변환을 훨씬 **자연스럽고 "Python다운(Pythonic)"** 방식으로 표현할 수 있다는 것이다. 결국은 그냥 함수 몇 개를 가진 파이썬 라이브러리일 뿐이니, 그냥 호출하고 나머지는 라이브러리가 알아서 해주게 두면 된다.

> [!tip] `torch.compile` — 정적 그래프의 장점을 동적 그래프에
> PyTorch 2.0부터 `torch.compile` 함수가 도입되었다. 코드를 JIT(just-in-time) 컴파일해 최적화된 커널로 만들어, 속도를 높여준다. 이는 이전 버전의 TorchScript, FX Tracing 컴파일 방식을 계승·발전시킨 것이다. 역사적으로 재미있는 지점은, 원래 정반대 철학이었던 TensorFlow(정적 그래프)와 PyTorch(동적 그래프)가 점점 서로를 닮아가고 있다는 점이다 — 지금은 PyTorch도 `compile()`을 지원하고, TensorFlow도 "eager execution 모드"(동적 그래프처럼 즉시 실행)를 지원한다.

### 2.2 텐서와 그래디언트

PyTorch 텐서는 **그래디언트 계산과 추적 기능이 내장**되어 있다. 그래서 우리가 할 일은 그냥 데이터를 텐서로 바꾸고, `torch`가 제공하는 텐서 메서드·함수로 연산을 수행하는 것뿐이다. 물론 저수준 세부사항에 접근하고 싶다면 언제든 할 수 있지만, 대부분의 경우 PyTorch는 우리가 기대하는 대로 알아서 해준다.

모든 텐서가 갖는, 그래디언트와 관련된 속성 세 가지가 있다.

| 속성 | 뜻 |
|---|---|
| `grad` | 계산된 그래디언트를 담은, **원본과 같은 모양의 텐서**를 보관하는 프로퍼티 |
| `is_leaf` | 이 텐서가 **사용자가 직접 만든 것**이면 `True`, 어떤 함수 변환의 **결과물**(계산 그래프에서 부모가 있는 노드)이면 `False` |
| `requires_grad` | 이 텐서에 대해 **그래디언트를 계산해야 하는지** 여부. leaf 텐서는 이 값을 텐서를 만들 때(`torch.zeros()`나 `torch.tensor()` 등)의 설정으로부터 물려받는다. 기본값은 `requires_grad=False`이므로, 그래디언트가 필요하면 **명시적으로 켜야 한다.** |

이 그래디언트-리프(leaf) 관련 동작을 명확히 알아보기 위해 다음 세션을 보자.

```python
>>> v1 = torch.tensor([1.0, 1.0], requires_grad=True)
>>> v2 = torch.tensor([2.0, 2.0])
```

- 여기서 두 텐서를 만들었다. `v1`은 **그래디언트를 계산하도록** 설정했고(`requires_grad=True`), `v2`는 하지 않았다(기본값 `False`).

다음으로, 두 벡터를 원소별로 더하고(벡터 `[3, 3]`이 됨), 각 원소를 두 배로 만든 뒤 모두 더한다.

```python
>>> v_sum = v1 + v2
>>> v_sum
tensor([3., 3.], grad_fn=<AddBackward0>)
>>> v_res = (v_sum*2).sum()
>>> v_res
tensor(12., grad_fn=<SumBackward0>)
```

결과는 값이 12인 **0차원 텐서**다. 여기까지는 단순한 산수 계산일 뿐이다. 이제 이 표현식이 만들어낸 **내부 그래프**를 살펴보자.

![[fig_3_3_v3.png]]
*그림 3.3 — 위 표현식의 그래프 표현(v1, v2 → 덧셈 → ×2 → 합 Σ → v_res)*

이제 두 텐서의 속성을 확인해보면, `v1`과 `v2`만이 **leaf 노드**이고, `v2`를 제외한 **모든 변수가 그래디언트 계산 대상**임을 알 수 있다.

```python
>>> v1.is_leaf, v2.is_leaf
(True, True)
>>> v_sum.is_leaf, v_res.is_leaf
(False, False)
>>> v1.requires_grad
True
>>> v2.requires_grad
False
>>> v_sum.requires_grad
True
>>> v_res.requires_grad
True
```

`requires_grad` 속성은 일종의 **"전염성(sticky)"** 을 가진다는 점에 주목하자. 계산에 관여하는 변수 중 하나라도 `True`이면, 그 뒤에 이어지는 모든 노드도 자동으로 `True`가 된다. 이는 논리적으로 당연한 동작이다 — 계산의 모든 중간 단계에 대해 그래디언트가 필요하기 때문이다. 다만 "계산한다"는 것이 곧 "`.grad` 필드에 값을 보존해둔다"는 뜻은 아니라는 점에 유의하자.

> [!warning] 메모리 절약을 위해 그래디언트는 leaf 노드에만 저장된다
> 메모리 효율을 위해, PyTorch는 `requires_grad=True`인 **leaf 노드에 대해서만** 그래디언트를 저장한다. 중간(non-leaf) 노드의 그래디언트도 보관하고 싶다면 그 텐서의 `retain_grad()` 메서드를 호출해야 한다.

이제 우리 그래프의 그래디언트를 계산해보자.

```python
>>> v_res.backward()
>>> v1.grad
tensor([2., 2.])
```

- `v_res.backward()`: `v_res`라는 변수에 대해, 그래프 안의 **어떤 변수를 조금 바꾸면 v_res에 얼마나 영향을 미치는지**를 계산해달라고 PyTorch에 요청하는 것이다. 다시 말해 **v_res를 그 그래프의 다른 모든 변수로 미분**한다.
- 우리 예에서 `v1.grad`의 값이 2라는 것은, **`v1`의 어떤 원소든 1만큼 늘리면 `v_res`의 값이 2만큼 늘어난다**는 뜻이다.

앞서 말했듯, PyTorch는 `requires_grad=True`인 leaf 텐서에 대해서만 그래디언트를 계산한다. 실제로 `v2`의 그래디언트를 확인해보면 아무것도 없다.

```python
>>> v2.grad
```

이렇게 되는 이유는 **계산과 메모리의 효율성** 때문이다. 실제 신경망은 수백만 개의 최적화 대상 파라미터를 가지고, 그 사이에는 수백 개의 중간 연산이 존재한다. 경사하강 최적화 과정에서 우리가 진짜 관심 있는 건 **중간 행렬곱의 그래디언트가 아니라, 모델 파라미터(가중치)에 대한 손실의 그래디언트**뿐이다. 물론 입력 데이터 자체의 그래디언트가 필요한 경우도 있다(예: 기존 신경망을 속이는 적대적 예제를 만들거나, 사전 학습된 단어 임베딩을 조정하고 싶을 때). 그럴 때는 텐서를 만들 때 `requires_grad=True`를 지정하면 된다.

이제 우리는 나만의 신경망 최적화기를 직접 구현하는 데 필요한 것을 사실상 다 갖췄다. 이 챕터의 나머지는 신경망 구조의 더 상위 레벨 building block, 널리 쓰이는 최적화 알고리즘, 흔한 손실 함수 같은 **편의 기능**을 다룬다. 하지만 이 모든 걸 원하는 방식으로 직접 재구현할 수도 있다는 점은 기억해두자 — 이것이 PyTorch가 그토록 인기 있는 이유(우아함과 유연성) 중 하나다.

> [!note] 호환성 메모 — `Variable` 클래스의 소멸
> 텐서 안에 그래디언트 계산을 내장한 것은 PyTorch 0.4.0의 큰 변화 중 하나다. 그 이전 버전에서는 그래프 추적과 그래디언트 누적을 별도의, 아주 얇은 클래스인 `Variable`이 담당했다. 이 클래스는 텐서를 감싸는 래퍼(wrapper)로서, 역전파를 위해 연산의 이력을 자동으로 저장했다. `Variable`은 2.2.0 버전에도 아직 남아있고(`torch.autograd`에서 사용 가능) 곧 사라질 예정이므로 새 코드에서는 쓰지 않는 게 좋다. 그래디언트가 텐서 자체의 기본 속성이 되면서 API가 훨씬 깔끔해졌다.

---

## 3. NN building blocks — 신경망 조립 부품

`torch.nn` 패키지에는 기본적인 기능을 제공하는 미리 만들어진 클래스가 잔뜩 들어있다. 이들은 모두 **실전 사용**을 염두에 두고 설계되었다(미니배치를 지원하고, 상식적인 기본값을 가지며, 가중치도 적절히 초기화되어 있다). 이 패키지의 모든 모듈은 **callable(호출 가능)** 이라는 공통 규칙을 따른다 — 즉 어떤 클래스의 인스턴스도 마치 함수처럼 인자를 넣어 호출할 수 있다. 예를 들어 `Linear` 클래스는 옵션으로 편향(bias)을 가지는 순전파(feed-forward) 층을 구현한다.

```python
>>> l = nn.Linear(2, 5)
>>> v = torch.FloatTensor([1, 2])
>>> l(v)
tensor([-0.1039, -1.1386,  1.3761, -0.3679, -1.1161], grad_fn=<ViewBackward0>)
```

- `nn.Linear(2, 5)`: **입력 2개, 출력 5개**를 갖는, 무작위로 초기화된 순전파 층 하나를 만든다. [[활성화함수]]에서 다루는 비선형 함수 없이 순수하게 "선형 변환"(가중치 곱하고 더하기)만 한다.
- `l(v)`: 만든 층 `l`을 **함수처럼 호출**해서 텐서 `v`를 변환한다.

`torch.nn` 패키지의 모든 클래스는 `nn.Module`이라는 기반 클래스를 상속한다. 이 기반 클래스를 이용하면 나만의 상위 레벨 신경망 블록을 만들 수도 있다(다음 절에서 확인). 우선, 모든 `nn.Module`의 자식이 제공하는 유용한 메서드를 살펴보자.

- `parameters()`: **그래디언트 계산이 필요한 모든 변수**(즉 모듈의 가중치)를 순회하는 이터레이터를 반환한다.
- `zero_grad()`: 모든 파라미터의 그래디언트를 **0으로 초기화**한다.
- `to(device)`: 모든 모듈 파라미터를 지정한 장치(CPU 또는 GPU)로 옮긴다.
- `state_dict()`: 모든 모듈 파라미터를 담은 딕셔너리를 반환한다. 모델을 직렬화(serialize)할 때 유용하다.
- `load_state_dict()`: state dictionary로부터 모듈을 초기화한다.

전체 클래스 목록은 공식 문서(http://pytorch.org/docs)에서 확인할 수 있다.

### 3.1 `Sequential` — 층을 파이프처럼 잇기

이제 여러 층을 하나의 파이프로 이어붙일 수 있게 해주는 아주 편리한 클래스, `Sequential`을 소개한다. 예제로 바로 보여주는 게 가장 빠르다.

```python
>>> s = nn.Sequential(
...     nn.Linear(2, 5),
...     nn.ReLU(),
...     nn.Linear(5, 20),
...     nn.ReLU(),
...     nn.Linear(20, 10),
...     nn.Dropout(p=0.3),
...     nn.Softmax(dim=1))
>>> s
Sequential(
  (0): Linear(in_features=2, out_features=5, bias=True)
  (1): ReLU()
  (2): Linear(in_features=5, out_features=20, bias=True)
  (3): ReLU()
  (4): Linear(in_features=20, out_features=10, bias=True)
  (5): Dropout(p=0.3, inplace=False)
  (6): Softmax(dim=1)
)
```

한 줄씩 뜯어보면 다음과 같은 3층 신경망을 정의한 것이다.

- `nn.Linear(2, 5)` → `nn.ReLU()` → `nn.Linear(5, 20)` → `nn.ReLU()` → `nn.Linear(20, 10)` → `nn.Dropout(p=0.3)` → `nn.Softmax(dim=1)`
- **`nn.Linear(입력수, 출력수)`**: 순수 선형(1차) 변환 층. 가중치와 편향을 학습한다.
- **`nn.ReLU()`**: [[활성화함수]] 중 하나인 **ReLU(rectified linear unit)** 비선형 함수. 층과 층 사이에 넣어야 신경망이 "복잡한 곡선"도 표현할 수 있다(선형 층만 쌓으면 결국 전체가 하나의 선형 함수와 같아져 버린다).
- **`nn.Dropout(p=0.3)`**: 학습 중 무작위로 30%의 뉴런 출력을 꺼버려(0으로 만들어) **과적합(overfitting)** 을 막는 기법.
- **`nn.Softmax(dim=1)`**: 출력값들을 "확률처럼 보이는" 값(합이 1, 모두 0 이상)으로 바꿔준다. `dim=1`은 **어느 차원을 기준으로 정규화**할지를 뜻한다. 여기서 차원 0은 **배치(batch) 샘플**(한 번에 처리하는 데이터 묶음 — [[에폭 배치 미니배치]] 참고)이고, 차원 1이 실제 "클래스별 점수" 차원이므로, 그 차원을 따라 정규화한다.

이 신경망에 실제로 데이터를 흘려보내보자.

```python
>>> s(torch.FloatTensor([[1,2]]))
tensor([[0.0847, 0.1145, 0.1063, 0.1458, 0.0873, 0.1063, 0.0864, 0.0821, 0.0894,
         0.0971]], grad_fn=<SoftmaxBackward0>)
```

`torch.FloatTensor([[1,2]])`처럼 **바깥에 대괄호를 하나 더 씌운 것**에 주목하자. 이는 "샘플 1개짜리 미니배치"를 표현하기 위함이다(0번째 차원 = 배치 차원). 즉 우리는 벡터 하나를 담은 미니배치를 성공적으로 신경망에 통과시킨 것이다!

### 3.2 커스텀 층 (Custom layers)

앞서 `nn.Module` 클래스가 모든 신경망 building block의 **기반 부모 클래스**라고 언급했다. 이 클래스는 단순히 여러 층들을 하나로 묶어주는 것 이상의, 훨씬 풍부한 기능을 제공한다.

`nn.Module`이 자식 클래스에게 제공하는 핵심 기능은 다음과 같다.

- **하위 모듈(submodule) 자동 추적**: 예를 들어 여러분의 building block이 내부적으로 두 개의 순전파 층을 사용해 어떤 변환을 수행한다고 하자. 이 하위 모듈들을 등록(register)하기 위해 특별한 조치를 취할 필요는 없다 — 그냥 클래스의 필드에 대입하기만 하면 된다.
- **등록된 모든 하위 모듈의 파라미터를 다루는 함수 제공**: 모듈의 전체 파라미터 리스트를 얻거나(`parameters()`), 그래디언트를 0으로 만들거나(`zero_grad()`), CPU·GPU로 옮기거나(`to(device)`), 모듈을 직렬화·역직렬화(`state_dict()`, `load_state_dict()`)하거나, 심지어 여러분이 만든 callable로 일반적인 변형(`apply()` 메서드)까지 할 수 있다.
- **`Module` 적용의 컨벤션 확립**: 모든 모듈은 데이터 변환을 `forward()` 메서드를 오버라이드해서 구현해야 한다.
- **그 외 부가 기능**: 모듈 변환이나 그래디언트 흐름을 조정하는 훅(hook) 함수 등록 기능도 있지만, 이는 더 고급 용도라 여기서는 다루지 않는다.

이런 기능들 덕분에 우리는 하위 모델을 상위 레벨 모델에 **통일된 방식으로 중첩(nest)** 시킬 수 있다. 복잡성을 다룰 때 매우 유용한 특징이다. 그것이 단순한 한 층짜리 선형 변환이든, 1,001개 층을 가진 거대한 **ResNet(residual NN)** 괴물이든, `nn.Module`의 규칙만 따르면 **동일한 방식으로** 다룰 수 있다. 코드 재사용성과 단순화(관련 없는 구현 세부사항을 감출 수 있다는 점에서)에 아주 편리하다.

PyTorch 저자들은 세심한 설계와 파이썬 특유의 마법을 더해, 이 컨벤션을 따르기만 하면 커스텀 모듈을 아주 쉽게 만들 수 있게 해두었다. 그래서 커스텀 모듈을 만들 때 우리가 해야 할 일은 사실 딱 두 가지뿐이다 — **하위 모듈을 등록하는 것**과 **`forward()` 메서드를 구현하는 것.**

이걸 앞서 본 `Sequential` 예제와 똑같은 구조를, 더 일반적이고 재사용 가능한 방식으로 만들어보자(전체 예제는 `Chapter03/01_modules.py`에 있다). 다음은 `nn.Module`을 상속하는 우리의 모듈 클래스다.

```python
class OurModule(nn.Module):
    def __init__(self, num_inputs, num_classes, dropout_prob=0.3):
        super(OurModule, self).__init__()
        self.pipe = nn.Sequential(
            nn.Linear(num_inputs, 5),
            nn.ReLU(),
            nn.Linear(5, 20),
            nn.ReLU(),
            nn.Linear(20, num_classes),
            nn.Dropout(p=dropout_prob),
            nn.Softmax(dim=1)
        )
```

한 줄씩 설명하면 다음과 같다.

- `class OurModule(nn.Module):` — **`nn.Module`을 상속**해서 새 클래스를 정의한다. 이렇게 해야 `parameters()`, `zero_grad()` 등 앞서 설명한 기능을 공짜로 물려받는다.
- `def __init__(self, num_inputs, num_classes, dropout_prob=0.3):` — 생성자에서 **입력 크기, 출력(클래스) 크기, 그리고 선택적인 dropout 확률**을 인자로 받는다.
- `super(OurModule, self).__init__()` — **부모 클래스의 생성자를 가장 먼저 호출**해서 초기화를 맡긴다. `nn.Module`은 내부적으로 하위 모듈을 추적하기 위한 자료구조를 준비해야 하므로, 이 호출을 빼먹으면 안 된다.
- `self.pipe = nn.Sequential(...)` — 앞서 본 것과 같은 층 구성의 `Sequential`을 만들어 **`self.pipe`라는 필드에 대입**한다.

여기서 핵심은 두 번째 단계, `self.pipe` 대입이다. `nn.Sequential` 자신도 `nn.Module`을 상속하므로(`nn` 패키지의 모든 것이 그렇듯), 이 대입만으로 **이 하위 모듈이 자동으로 등록**된다. 등록을 위해 별도로 뭔가를 호출할 필요가 없다 — 그냥 필드에 하위 모듈을 대입하기만 하면, 생성자가 끝난 뒤 그 필드들이 알아서 다 등록된다. (참고로, 층 개수가 코드로 동적으로 정해져야 하는 경우를 위해 `nn.Module`에는 `add_module()`이라는, 하위 모듈을 명시적으로 등록하는 함수도 따로 있다.)

다음으로, `forward` 함수를 우리 데이터 변환 구현으로 오버라이드해야 한다.

```python
    def forward(self, x):
        return self.pipe(x)
```

- 우리 모듈은 `Sequential`을 감싸는 아주 단순한 래퍼(wrapper)이므로, 데이터를 변환하려면 그냥 `self.pipe`를 호출해주기만 하면 된다.

> [!warning] 모듈은 반드시 "호출(call)"해야 한다 — `forward()`를 직접 부르면 안 된다
> 어떤 모듈에 데이터를 통과시킬 땐, 그 모듈 인스턴스를 **callable로 취급해서** 호출해야 한다(즉 모듈 인스턴스가 함수인 척하고 인자를 넣어 부른다). `nn.Module`의 `forward()` 함수를 직접 부르면 안 된다. 그 이유는 `nn.Module`이 `__call__()` 메서드를 오버라이드해서, 인스턴스를 callable로 다룰 때 이 메서드가 대신 호출되기 때문이다. 이 메서드는 `nn.Module`이 해야 할 여러 가지 "마법 같은 뒷정리"를 수행한 뒤 우리의 `forward()`를 호출한다. `forward()`를 직접 부르면 이 `nn.Module`의 역할을 건너뛰게 되어 **잘못된 결과**를 얻을 수 있다.

이렇게 나만의 모듈을 정의하는 방법을 다 배웠다. 이제 실제로 사용해보자.

```python
if __name__ == "__main__":
    net = OurModule(num_inputs=2, num_classes=3)
    print(net)
    v = torch.FloatTensor([[2, 3]])
    out = net(v)
    print(out)
    print("Cuda's availability is %s" % torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Data from cuda: %s" % out.to('cuda'))
```

- 원하는 입력·출력 개수를 지정해 모듈을 생성한다.
- 만든 모듈을 (`forward()`가 아니라) **callable로서** 호출해 텐서를 변환하도록 요청한다.
- 그 뒤 신경망의 구조를 출력한다. (`nn.Module`이 `__str__()`과 `__repr__()`를 오버라이드해서, 내부 구조를 보기 좋게 표현해준다.)
- 마지막으로 변환 결과를 출력한다.

실행 결과는 다음과 같을 것이다.

```
Chapter03$ python 01_modules.py
OurModule(
  (pipe): Sequential(
    (0): Linear(in_features=2, out_features=5, bias=True)
    (1): ReLU()
    (2): Linear(in_features=5, out_features=20, bias=True)
    (3): ReLU()
    (4): Linear(in_features=20, out_features=3, bias=True)
    (5): Dropout(p=0.3, inplace=False)
    (6): Softmax(dim=1)
  )
)
tensor([[0.3297, 0.3854, 0.2849]], grad_fn=<SoftmaxBackward0>)
Cuda's availability is False
```

물론, PyTorch의 "동적" 특성에 관해 앞서 말한 것들은 여기서도 여전히 유효하다. `forward()` 메서드는 데이터의 **매 배치마다 호출**되므로, 데이터에 따라 복잡한 변환을 하고 싶다면(예: 계층적 softmax를 쓰거나, 어떤 네트워크를 적용할지를 무작위로 고르는 것 등) 얼마든지 그렇게 할 수 있다. 모듈 생성자의 인자 개수도 하나로 제한되지 않는다. 원한다면 여러 개의 필수 인자와 수십 개의 선택적 인자를 가진 모듈을 만들어도 아무 문제 없다.

이제 우리 삶을 단순하게 해줄 PyTorch의 중요한 두 조각, **손실 함수와 옵티마이저**를 익힐 차례다.

---

## 4. 손실 함수와 옵티마이저 (Loss functions and optimizers)

입력 데이터를 출력으로 바꾸는 네트워크만으로는 학습에 충분하지 않다. **학습 목표(learning objective)** 도 정의해야 한다. 이는 두 개의 인자 — **네트워크의 출력**과 **원하는 출력(정답)** — 를 받아, 하나의 숫자를 돌려주는 함수여야 한다. 그 숫자는 "예측이 원하는 결과에 비해 얼마나 가까운가"를 나타낸다. 이 함수를 **손실 함수(loss function)** 라 부르고, 그 출력값을 **손실 값(loss value)** 이라 부른다. 손실 값을 이용해 네트워크 파라미터의 그래디언트를 계산하고, 그 손실 값을 줄이는 방향으로 파라미터를 조정하며, 이는 모델이 미래에 더 나은 결과를 내도록 밀어붙인다. 손실 함수도, 네트워크 파라미터를 그래디언트로 조정하는 방법도 매우 흔하고 다양한 형태로 존재해서, 둘 다 PyTorch 라이브러리의 중요한 부분을 차지한다. 손실 함수부터 보자.

### 4.1 손실 함수 (Loss functions)

손실 함수는 `nn` 패키지에 있고, `nn.Module`의 서브클래스로 구현되어 있다. 보통 두 개의 인자를 받는다 — **네트워크의 출력(예측)** 과 **원하는 출력(정답 데이터, 데이터 샘플의 "라벨"이라고도 부른다)**. 이 책을 쓰는 시점 기준 PyTorch 2.3.1에는 20개가 넘는 손실 함수가 들어있고, 물론 원하는 어떤 커스텀 함수든 직접 만들 수도 있다. [[손실함수의 종류]] 참고.

가장 흔히 쓰이는 표준 손실 함수는 다음과 같다.

| 손실 함수 | 설명 |
|---|---|
| `nn.MSELoss` | 인자들 간의 **평균 제곱 오차(mean square error)**. 회귀(regression) 문제의 표준 손실. |
| `nn.BCELoss`, `nn.BCEWithLogits` | **이진 교차 엔트로피(binary cross-entropy)** 손실. 전자는 (보통 `Sigmoid` 층의 출력인) 단일 확률값을 기대하고, 후자는 입력으로 **원점수(raw score)** 를 받아 내부에서 직접 `Sigmoid`를 적용한다. 후자가 대체로 수치적으로 더 안정적이고 효율적이다. 이름에서 알 수 있듯 이진 분류 문제에서 자주 쓰인다. |
| `nn.CrossEntropyLoss`, `nn.NLLLoss` | 다중 클래스 분류 문제에 쓰이는 유명한 **"최대 우도(maximum likelihood)"** 기준. 전자는 각 클래스에 대한 원점수를 받아 내부에서 `LogSoftmax`를 적용하고, 후자는 로그 확률을 입력으로 기대한다. |

그 외에도 다양한 손실 함수가 있으며, 언제든 출력과 목표를 비교하는 나만의 `Module` 서브클래스를 만들 수도 있다. 이제 최적화 과정의 두 번째 조각을 살펴보자.

### 4.2 옵티마이저 (Optimizers)

기본 옵티마이저의 역할은 모델 파라미터의 그래디언트를 받아, 손실 값을 줄이는 방향으로 파라미터를 바꾸는 것이다. 손실 값을 줄임으로써, 우리는 모델을 원하는 출력 쪽으로 밀어붙이고, 이는 향후 모델의 성능이 더 좋아지리라는 희망을 준다. 파라미터를 바꾼다는 것 자체는 단순해 보일 수 있지만, 그 안에는 많은 디테일이 숨어 있고, 옵티마이저의 세부 절차는 여전히 뜨거운 연구 주제다. [[옵티마이저와 경사하강법 변형]] 참고.

`torch.optim` 패키지에는 여러 유명한 옵티마이저 구현이 담겨 있으며, 가장 널리 알려진 것은 다음과 같다.

- **`SGD`**: 선택적으로 모멘텀(momentum) 확장을 붙일 수 있는, 기본적인(vanilla) 확률적 경사하강(stochastic gradient descent) 알고리즘.
- **`RMSprop`**: Geoffrey Hinton이 제안한 옵티마이저.
- **`Adagrad`**: 적응형(adaptive) 그래디언트 옵티마이저.
- **`Adam`**: `RMSprop`과 `Adagrad`를 결합한, 꽤 성공적이고 인기 있는 조합.

모든 옵티마이저는 **동일한 인터페이스**를 노출하기 때문에, 서로 다른 최적화 방법을 손쉽게 바꿔가며 실험할 수 있다(때로는 최적화 방법의 선택이 수렴 동역학과 최종 결과에 정말 큰 차이를 만들기도 한다). 옵티마이저를 생성할 때는 최적화 과정 동안 조정될 텐서들의 이터러블(iterable)을 넘겨줘야 한다. 관례상, 상위 레벨 `nn.Module` 인스턴스의 `parameters()` 호출 결과를 그대로 넘기는 경우가 많다. 이 호출은 그래디언트를 가진 모든 leaf 텐서의 이터러블을 반환한다.

### 4.3 학습 루프의 공통 청사진 (Training loop blueprint)

이제 학습 루프의 흔한 구조를 논해보자.

```python
for batch_x, batch_y in iterate_batches(data, batch_size=32):
    batch_x_t = torch.tensor(batch_x)
    batch_y_t = torch.tensor(batch_y)
    out_t = net(batch_x_t)
    loss_t = loss_function(out_t, batch_y_t)
    loss_t.backward()
    optimizer.step()
    optimizer.zero_grad()
```

한 줄씩 짚어보자([[에폭 배치 미니배치]] 참고).

- `for batch_x, batch_y in iterate_batches(data, batch_size=32):` — 보통은 데이터를 여러 번 반복해서 순회한다(전체 예제 세트를 한 번 도는 것을 **에폭(epoch)** 이라 부른다). 데이터는 보통 CPU·GPU 메모리에 한 번에 다 담기엔 너무 크므로, 동일한 크기의 **배치(batch)** 로 잘라 쓴다.
- `batch_x_t = torch.tensor(batch_x)` / `batch_y_t = torch.tensor(batch_y)` — 데이터 샘플과 정답 라벨을 각각 텐서로 변환한다.
- `out_t = net(batch_x_t)` — 데이터 샘플을 네트워크에 통과시킨다.
- `loss_t = loss_function(out_t, batch_y_t)` — 네트워크의 출력과 정답 라벨을 손실 함수에 넣어, 네트워크 결과가 정답에 비해 얼마나 "나쁜지"를 나타내는 손실 값을 얻는다.
- `loss_t.backward()` — 손실 함수의 결과(텐서)에 대해 `backward()`를 호출한다. 네트워크에 대한 모든 변환(가중치, 편향, 컨볼루션 필터 같은 파라미터를 포함해)은 결국 중간 텐서 인스턴스들로 이뤄진 계산 그래프에 불과하므로, 이 호출 한 번으로 **수행된 모든 연산의 그래프를 거꾸로 풀며**, `require_grad=True`인 모든 leaf 텐서에 대해 그래디언트를 계산한다. 그래디언트가 계산될 때마다 그 텐서의 `.grad` 필드에 **누적**된다. 그래서 하나의 텐서가 계산 과정에 여러 번 참여해도 그래디언트가 알맞게 합산된다. 예를 들어 하나의 순환 신경망(RNN) 셀이 여러 입력 항목에 반복적으로 적용될 수 있다.
- `optimizer.step()` — `loss.backward()`가 끝나면 그래디언트가 다 쌓여 있고, 이제 옵티마이저가 일할 차례다. 생성될 때 전달받은 파라미터들의 모든 그래디언트를 가져다 **적용**한다. 이 작업이 바로 `step()` 메서드로 이뤄진다.
- `optimizer.zero_grad()` — 학습 루프의 마지막이자 절대 잊으면 안 되는 조각은 파라미터의 그래디언트를 **0으로 초기화**하는 것이다. 편의상 옵티마이저도 동일한 기능의 `zero_grad()` 호출을 제공한다. 때때로 이 호출은 학습 루프의 **맨 앞**에 두기도 하는데, 어느 쪽이든 큰 차이는 없다.

앞의 방식은 최적화를 수행하는 아주 유연한 방법이며, 정교한 연구에서 요구하는 수준까지도 충분히 감당할 수 있다. 예를 들어 두 개의 옵티마이저가 같은 데이터 위에서 서로 다른 모델의 옵션을 동시에 조정하게 만들 수도 있다(이는 실제로 **생성적 적대 신경망(GAN)** 학습에서 벌어지는 현실적인 시나리오다).

이렇게 해서 신경망 학습에 필요한 PyTorch의 핵심 기능은 다 다뤘다. 이 챕터는 이 모든 개념을 아우르는 실전 규모의 예제로 마무리되지만, 그 전에 NN 실무자에게 꼭 필요한 한 가지 중요한 주제 — **학습 과정 모니터링** — 를 다뤄야 한다.

---

## 5. TensorBoard로 모니터링하기

혼자서 신경망을 학습시켜본 적이 있다면, 그게 얼마나 고통스럽고 불확실할 수 있는지 알 것이다. 이미 하이퍼파라미터가 다 맞춰진 기존 튜토리얼·데모를 따라 하는 게 아니라, 데이터를 가져다 **처음부터** 뭔가를 만드는 이야기다. 요즘의 상위 레벨 딥러닝 툴킷들이 적절한 가중치 초기화, 옵티마이저의 베타·감마 등 여러 옵션을 이미 합리적인 기본값으로 세팅해두었어도, 여전히 여러분이 내려야 할 결정이 많고, 따라서 잘못될 수 있는 부분도 많다. 결과적으로, 여러분의 코드는 첫 실행에서 거의 절대 제대로 작동하지 않는다 — 이건 익숙해져야 할 일이다.

물론 경험과 연습이 쌓이면 문제의 원인을 파악하는 감각이 강해지지만, 그러려면 학습 과정 내부에서 무슨 일이 벌어지는지 어떻게든 **들여다볼 수 있는 데이터**가 필요하다. 심지어 작은 신경망(예: 작은 MNIST 튜토리얼용 네트워크)조차 수십만 개의 파라미터와 상당히 비선형적인 학습 동역학을 가질 수 있다.

딥러닝 실무자들은 학습 중 관찰해야 할 것들의 목록을 발전시켜왔다. 보통 다음이 포함된다.

- **손실 값**: 보통 기본 손실과 여러 정규화(regularization) 손실 등 여러 구성 요소로 이뤄진다. **전체 손실과 개별 구성 요소 모두**를 시간에 따라 관찰해야 한다.
- **학습·테스트 데이터셋에 대한 검증 결과**
- **그래디언트와 가중치에 관한 통계**
- **네트워크가 만들어낸 값들**: 예를 들어 분류 문제를 풀고 있다면, 예측된 클래스 확률의 **엔트로피(entropy)** 를 측정하고 싶을 것이다. 회귀 문제라면, 예측된 원시 값(raw value) 자체가 학습에 관해 많은 정보를 줄 수 있다.
- **학습률(learning rate)이나 다른 하이퍼파라미터**: 시간에 따라 조정된다면 그 값도 봐야 한다.

이 목록은 훨씬 더 길어질 수 있고, 단어 임베딩 프로젝션, 오디오 샘플, GAN이 생성한 이미지 같은 **도메인 특화 지표**도 포함될 수 있다. 하드웨어와 관련해 학습 속도(예: 한 에폭이 걸리는 시간)에 관한 값을 모니터링하고 싶을 수도 있다 — 최적화 효과나 문제를 파악하는 데 유용하다.

길게 말할 것 없이, 여러 값들을 시간에 따라 추적하고 분석 가능하게 표현해주는 **범용 솔루션**이 필요하다(엑셀 스프레드시트로 이런 통계를 보고 있는 걸 상상해보라). 다행히도 그런 도구가 이미 존재하며, 다음에 살펴본다.

### 5.1 TensorBoard 101

이 책의 초판이 쓰였을 때만 해도 신경망 모니터링을 위한 선택지가 그리 많지 않았다. 시간이 지나며 더 많은 사람과 회사가 ML·DL 분야에 뛰어들었고, MLflow(https://mlflow.org/) 같은 새로운 도구도 등장했다. 이 책에서는 여전히 TensorFlow에서 나온 **TensorBoard** 유틸리티에 집중하지만, 다른 대안을 시도해볼 수도 있다.

TensorFlow의 첫 공개 버전부터, TensorFlow에는 **TensorBoard**라는 특별한 도구가 포함되어 있었다. 이는 학습 도중과 이후에 신경망의 다양한 특성을 관찰·분석하는 문제를 풀기 위해 개발됐다. TensorBoard는 큰 커뮤니티를 가진 강력한 범용 솔루션이고, 보기에도 꽤 예쁘다.

![[fig_3_4_v3.png]]
*그림 3.4 — TensorBoard 웹 인터페이스 화면*

아키텍처 관점에서, TensorBoard는 컴퓨터에서 실행하는 **파이썬 웹 서비스**로, 학습 과정이 분석 대상 값을 저장할 디렉터리를 인자로 넘겨서 시작한다. 그러면 브라우저로 TensorBoard의 포트(보통 `6006`)에 접속해서, 값들이 실시간으로 갱신되는 인터랙티브 웹 인터페이스를 볼 수 있다. 특히 학습이 클라우드의 원격 머신에서 돌아가고 있을 때 편리하고 유용하다.

### 5.2 지표 그리기 (Plotting metrics)

TensorBoard 사용이 얼마나 간단한지 감을 잡기 위해, 신경망과는 관련 없지만 **TensorBoard에 값을 쓰는 것 자체**에 관한 작은 예제를 보자(전체 예제 코드는 `Chapter03/02_tensorboard.py`에 있다).

먼저 필요한 패키지를 임포트하고, 데이터를 기록할 writer를 만들고, 시각화할 함수들을 정의한다.

```python
import math
from torch.utils.tensorboard.writer import SummaryWriter

if __name__ == "__main__":
    writer = SummaryWriter()
    funcs = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
```

- `from torch.utils.tensorboard.writer import SummaryWriter` — 몇 년 전에는 TensorBoard를 쓰려면 여러 서드파티 라이브러리를 따로 설치해야 했지만, 요즘은 PyTorch가 **`torch.utils.tensorboard` 패키지에 이 데이터 포맷 지원을 기본 내장**하고 있다(TensorBoard는 원래 TensorFlow의 일부였다가 별도 프로젝트로 분리되었지만, 여전히 TensorFlow의 데이터 포맷을 쓴다).
- `writer = SummaryWriter()` — 기본적으로 `SummaryWriter`는 실행할 때마다 `runs` 디렉터리 안에 **고유한 하위 디렉터리**를 만들어, 여러 번의 학습 라운드를 비교할 수 있게 해준다. 새 디렉터리의 이름에는 **현재 날짜·시각과 호스트 이름**이 들어간다. 이를 재정의하려면 `SummaryWriter`에 `log_dir` 인자를 넘기면 된다. 서로 다른 실험의 의미를 담고 싶다면(예: `dropout=0.3`이나 `strong_regularisation` 같은) `comment` 인자로 디렉터리 이름 뒤에 접미사를 붙일 수도 있다.
- `funcs = {"sin": math.sin, "cos": math.cos, "tan": math.tan}` — 값을 시각화할 세 함수(사인·코사인·탄젠트)를 딕셔너리로 준비한다.

다음으로, 각도 범위를 순회한다.

```python
    for angle in range(-360, 360):
        angle_rad = angle * math.pi / 180
        for name, fun in funcs.items():
            val = fun(angle_rad)
            writer.add_scalar(name, val, angle)

    writer.close()
```

- `angle_rad = angle * math.pi / 180` — 도(degree) 단위 각도 범위를 **라디안(radian)** 으로 변환한다.
- `val = fun(angle_rad)` — 각 함수의 값을 계산한다.
- `writer.add_scalar(name, val, angle)` — 계산한 값을 writer에 추가한다. `add_scalar` 함수는 **세 개의 인자** — **파라미터 이름, 그 값, 현재 반복 회차(정수여야 함)** — 를 받는다.
- `writer.close()` — 루프가 끝난 뒤 반드시 writer를 **닫아야** 한다. writer는 기본적으로 (기본값 2분마다) **주기적으로 flush**를 하므로, 최적화 과정이 아주 길어도 값들은 계속 보인다. `SummaryWriter` 데이터를 명시적으로 flush하고 싶다면 `flush()` 메서드를 쓰면 된다.

이 코드를 실행하면 콘솔에는 아무 출력도 없지만, `runs` 디렉터리 안에 파일 하나를 담은 새 디렉터리가 생긴다. 결과를 보려면 TensorBoard를 시작해야 한다.

```
Chapter03$ tensorboard --logdir runs
TensorFlow installation not found - running with reduced feature set.
Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
TensorBoard 2.15.1 at http://localhost:6006/ (Press CTRL+C to quit)
```

원격 서버에서 TensorBoard를 돌리고 있다면, 다른 머신에서 접속 가능하도록 `--bind_all` 커맨드 라인 옵션을 추가해야 한다. 이제 브라우저에서 `http://localhost:6006`을 열면 이런 화면을 볼 수 있다.

![[fig_3_5_v3.png]]
*그림 3.5 — 예제 실행으로 만들어진 그래프(사인·코사인·탄젠트 곡선)*

그래프는 인터랙티브해서, 마우스로 특정 구간을 드래그해 확대해 세부사항을 볼 수 있다. 축소하려면 그래프 안에서 더블클릭하면 된다. 같은 프로그램을 여러 번 실행하면 왼쪽의 **Runs** 목록에 여러 항목이 생기고, 이들을 원하는 조합으로 켜고 끄며 여러 최적화의 동역학을 비교할 수 있다. TensorBoard는 스칼라 값뿐 아니라 이미지·오디오·텍스트 데이터·임베딩까지 분석할 수 있고, 심지어 네트워크의 구조를 보여줄 수도 있다. 이 모든 기능은 TensorBoard의 공식 문서를 참고하자.

---

## 6. 실전 예제 — Atari 이미지로 GAN 학습하기

이제 이 챕터에서 배운 모든 것을 하나로 모아, PyTorch를 이용한 **진짜 신경망 최적화 문제**를 풀어볼 시간이다.

거의 모든 딥러닝 책이 MNIST 데이터셋으로 딥러닝의 힘을 보여준다. 그래서 유전학 연구자들의 초파리처럼, MNIST는 지나치게 많이 쓰여 이제 지루한 데이터셋이 되었다. 이 전통을 깨고 조금 더 재미를 더하기 위해, 저자는 이 챕터 앞부분에서 잠깐 언급했던 **생성적 적대 신경망(GAN, generative adversarial network)** 을 소재로 골랐다. 이 예제에서는 여러 Atari 게임의 스크린샷을 생성하는 GAN을 학습시킨다. [[GAN 생성적적대신경망]] 참고.

가장 단순한 GAN 구조는 이렇다. 신경망 두 개를 두는데, 하나는 "사기꾼(cheater)" 역할(**생성자, generator**라고도 부름)을, 다른 하나는 "탐정(detective)" 역할(**판별자, discriminator**라고도 부름)을 맡는다. 두 네트워크는 서로 경쟁한다 — 생성자는 우리 데이터셋과 구별하기 어려운 가짜 데이터를 만들려 하고, 판별자는 생성된 샘플을 탐지하려 한다. 시간이 지나며 둘 다 실력이 늘어난다 — 생성자는 점점 더 그럴듯한 데이터 샘플을 만들어내고, 판별자는 가짜를 구별하는 더 정교한 방법을 고안해낸다.

> [!important] GAN의 두 선수 — 생성자와 판별자
> - **생성자(Generator)**: 가짜를 만드는 "사기꾼". 무작위 벡터(잠재 벡터, latent vector)를 입력받아 가짜 이미지를 만들어낸다.
> - **판별자(Discriminator)**: 진짜와 가짜를 가려내는 "탐정". 이미지를 입력받아, 그것이 진짜일 확률을 출력한다.
>
> 둘은 서로 다른 목표를 갖고 함께 학습되며, 이 "경쟁 학습"이 GAN의 핵심이다.

GAN의 실용적 쓰임새로는 이미지 품질 개선, 사실적인 이미지 생성, 특징 학습(feature learning) 등이 있다. 이 예제에서 실용적 유용성은 거의 없지만, 지금까지 PyTorch로 배운 모든 것을 보여주는 좋은 쇼케이스가 되어줄 것이다.

이제 시작해보자. 전체 예제 코드는 `Chapter03/03_atari_gan.py` 파일에 있다. 여기서는 가장 핵심이 되는 코드 조각만 살펴보고, 임포트 부분과 상수 선언은 생략한다. 다음은 Gym 게임을 감싸는 래퍼(wrapper) 클래스다.

```python
class InputWrapper(gym.ObservationWrapper):
    """
    Preprocessing of input numpy array:
    1. resize image into predefined size
    2. move color channel axis to a first place
    """
    def __init__(self, *args):
        super(InputWrapper, self).__init__(*args)
        old_space = self.observation_space
        assert isinstance(old_space, spaces.Box)
        self.observation_space = spaces.Box(
            self.observation(old_space.low), self.observation(old_space.high),
            dtype=np.float32
        )

    def observation(self, observation: gym.core.ObsType) -> gym.core.ObsType:
        # resize image
        new_obs = cv2.resize(
            observation, (IMAGE_SIZE, IMAGE_SIZE))
        # transform (w, h, c) -> (c, w, h)
        new_obs = np.moveaxis(new_obs, 2, 0)
        return new_obs.astype(np.float32)
```

- `class InputWrapper(gym.ObservationWrapper):` — 2장에서 배운 `ObservationWrapper`를 상속해, 게임 화면을 신경망에 알맞은 모양으로 바꿔주는 래퍼를 만든다.
- `__init__` 안에서는 관측 공간(`observation_space`)의 하한·상한을 우리가 정의할 `observation()` 함수로 변환해서 다시 설정한다.
- `observation()` 메서드는 이 클래스의 핵심으로, 다음 세 가지 변환을 수행한다.
  - `cv2.resize(observation, (IMAGE_SIZE, IMAGE_SIZE))` — 입력 이미지를 Atari 표준 해상도인 **210×160에서 정사각형 64×64 크기로 리사이즈**한다.
  - `np.moveaxis(new_obs, 2, 0)` — 이미지의 **색상 채널 축을 맨 마지막에서 맨 앞으로** 옮긴다. PyTorch의 컨볼루션 층은 입력 텐서의 모양을 **(채널, 높이, 너비)** 순서로 기대하기 때문에, 이 규칙에 맞춰준다.
  - `return new_obs.astype(np.float32)` — 이미지를 **바이트(byte)에서 float으로** 타입 변환한다.

그다음, `Discriminator`와 `Generator`라는 두 개의 `nn.Module` 클래스를 정의한다. 전자는 우리가 리사이즈한 컬러 이미지를 입력받아, 5개 층의 컨볼루션을 적용해 하나의 숫자로 변환하고, 그 숫자를 `Sigmoid` 비선형 함수에 통과시킨다. `Sigmoid`의 출력은 **판별자가 이 입력 이미지를 실제 데이터셋에서 왔다고 믿는 확률**로 해석된다.

`Generator`는 무작위 숫자로 이뤄진 벡터(잠재 벡터)를 입력으로 받아, **"전치 컨볼루션(transposed convolution)"**(**디컨볼루션(deconvolution)** 이라고도 부른다) 연산을 이용해 이 벡터를 원본 해상도의 컬러 이미지로 변환한다. (이 두 클래스는 코드가 길고 이 예제의 핵심은 아니므로, 여기서는 자세히 다루지 않는다. 전체 코드는 예제 파일에서 볼 수 있다.)

입력 데이터로는, 여러 Atari 게임을 무작위 에이전트가 동시에 플레이하면서 얻은 스크린샷을 쓴다. 그림 3.6은 그 입력 데이터가 어떻게 생겼는지 보여준다.

![[fig_3_6_v3.png]]
*그림 3.6 — 세 가지 Atari 게임에서 뽑은 샘플 스크린샷*

이미지는 다음 함수가 만들어내는 배치(batch) 단위로 묶인다.

```python
def iterate_batches(envs: tt.List[gym.Env],
                     batch_size: int = BATCH_SIZE) -> tt.Generator[torch.Tensor,
                                                                    None]:
    batch = [e.reset()[0] for e in envs]
    env_gen = iter(lambda: random.choice(envs), None)

    while True:
        e = next(env_gen)
        action = e.action_space.sample()
        obs, reward, is_done, is_trunc, _ = e.step(action)
        if np.mean(obs) > 0.01:
            batch.append(obs)
        if len(batch) == batch_size:
            batch_np = np.array(batch, dtype=np.float32)
            # Normalising input to [-1..1]
            yield torch.tensor(batch_np * 2.0 / 255.0 - 1.0)
            batch.clear()
        if is_done or is_trunc:
            e.reset()
```

- `batch = [e.reset()[0] for e in envs]` — 넘겨받은 각 환경(environment)을 리셋해서 초기 관측값들로 배치 리스트를 시작한다.
- `env_gen = iter(lambda: random.choice(envs), None)` — 넘겨진 환경 목록에서 **무작위로 하나씩 골라주는 무한 이터레이터**를 만든다.
- `while True:` 블록에서는 무작위로 고른 환경에서 **무작위 행동**을 실행하고(`e.action_space.sample()`), 그 결과 관측값을 배치에 추가한다.
- `if np.mean(obs) > 0.01:` — 관측값의 평균이 거의 0에 가까우면(즉 화면이 거의 새까맣다면) 배치에 넣지 않는다. 이는 어떤 게임에서 화면이 깜빡이는(flickering) 버그를 피하기 위한 처리다.
- `if len(batch) == batch_size:` — 배치가 원하는 크기가 되면, 넘파이 배열로 만들고 **`[-1, 1]` 범위로 정규화**(`batch_np * 2.0 / 255.0 - 1.0`)한 뒤 텐서로 변환해 `yield`한다. 그 뒤 배치를 비운다.
- `if is_done or is_trunc:` — 에피소드가 끝났거나 강제 종료됐다면 그 환경을 리셋한다.

이 함수는 환경 목록에서 무한히 샘플링하면서, 무작위 행동을 실행하고 관측값을 배치 리스트에 기억해둔다. 배치가 원하는 크기가 되면 이미지를 정규화하고, 텐서로 변환한 뒤 제너레이터에서 값을 넘겨준다(`yield`). 관측값의 평균이 0이 아닌지 확인하는 검사는, 어떤 게임의 이미지 깜빡임 버그를 막기 위해 필요하다.

이제 모델을 준비하고 학습 루프를 실행하는 `main` 함수를 보자.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", default="cpu", help="Device name, default=cpu")
    args = parser.parse_args()

    device = torch.device(args.dev)
    envs = [
        InputWrapper(gym.make(name))
        for name in ('Breakout-v4', 'AirRaid-v4', 'Pong-v4')
    ]
    shape = envs[0].observation_space.shape
```

- 커맨드 라인 인자(`-dev` 하나만 있으며, 계산에 쓸 장치를 지정)를 처리한다.
- 앞서 정의한 래퍼를 적용해 **여러 환경으로 이뤄진 풀(pool)** 을 만든다. 이 환경 배열은 나중에 `iterate_batches` 함수에 넘겨져 학습 데이터를 생성하는 데 쓰인다.

다음 부분에서는 클래스 인스턴스들 — summary writer, 두 네트워크, 손실 함수, 두 개의 옵티마이저 — 를 만든다.

```python
    net_discr = Discriminator(input_shape=shape).to(device)
    net_gener = Generator(output_shape=shape).to(device)

    objective = nn.BCELoss()
    gen_optimizer = optim.Adam(params=net_gener.parameters(), lr=LEARNING_RATE,
                                betas=(0.5, 0.999))
    dis_optimizer = optim.Adam(params=net_discr.parameters(), lr=LEARNING_RATE,
                                betas=(0.5, 0.999))
    writer = SummaryWriter()
```

- `objective = nn.BCELoss()` — 손실 함수로 **이진 교차 엔트로피(BCE)** 를 쓴다. 판별자의 출력(0~1 확률)과 "진짜(1)/가짜(0)" 라벨을 비교하기에 알맞은 손실이다.
- `gen_optimizer`, `dis_optimizer` — **생성자용, 판별자용 옵티마이저를 각각 따로** `Adam`으로 만든다.

> [!question] 왜 옵티마이저가 두 개나 필요할까?
> GAN이 학습되는 방식이 바로 그렇기 때문이다. 판별자를 학습시키려면, 알맞은 라벨(진짜는 1, 가짜는 0)을 붙인 진짜·가짜 데이터 샘플을 둘 다 보여줘야 한다. 이 과정에서는 **판별자의 파라미터만** 갱신한다.
>
> 그다음, 진짜·가짜 샘플을 판별자에 다시 통과시키되, 이번엔 **모든 샘플의 라벨을 1**로 준다. 이 두 번째 패스는 **생성자의 가중치만** 갱신한다. 이 두 번째 패스가 생성자에게 "판별자를 속여, 실제 샘플과 생성된 샘플을 헷갈리게 만드는 법"을 가르친다.

이어서, 손실을 누적할 배열, 반복 횟수 카운터, 진짜·가짜 라벨을 담을 변수를 정의한다. 학습 100회 반복이 지나면 걸린 시간을 보고하기 위해 현재 타임스탬프도 저장해둔다.

```python
    gen_losses = []
    dis_losses = []
    iter_no = 0

    true_labels_v = torch.ones(BATCH_SIZE, device=device)
    fake_labels_v = torch.zeros(BATCH_SIZE, device=device)
    ts_start = time.time()
```

- `true_labels_v = torch.ones(BATCH_SIZE, device=device)` — 진짜 데이터를 나타내는 **1로 채워진 라벨 텐서**.
- `fake_labels_v = torch.zeros(BATCH_SIZE, device=device)` — 가짜 데이터를 나타내는 **0으로 채워진 라벨 텐서**.

다음 학습 루프의 맨 앞에서, 무작위 벡터를 만들어 `Generator` 네트워크에 통과시킨다.

```python
    for batch_v in iterate_batches(envs):
        # fake samples, input is 4D: batch, filters, x, y
        gen_input_v = torch.FloatTensor(BATCH_SIZE, LATENT_VECTOR_SIZE, 1, 1)
        gen_input_v.normal_(0, 1)
        gen_input_v = gen_input_v.to(device)
        batch_v = batch_v.to(device)
        gen_output_v = net_gener(gen_input_v)
```

- `gen_input_v = torch.FloatTensor(BATCH_SIZE, LATENT_VECTOR_SIZE, 1, 1)` — (배치, 필터, x, y) 4차원 모양의 텐서를 만든다.
- `gen_input_v.normal_(0, 1)` — **제자리(inplace) 연산**으로 평균 0, 표준편차 1인 **정규분포 난수**를 채워 넣는다(함수 이름 끝의 `_`가 inplace 연산임을 알려준다는 점, 기억하는가?). 이것이 생성자의 "씨앗"이 되는 **잠재 벡터**다.
- `gen_output_v = net_gener(gen_input_v)` — 잠재 벡터를 생성자에 통과시켜 **가짜 이미지**를 만든다.

이제 판별자를 배치에 두 번 적용해서 학습시킨다. 한 번은 실제 데이터 샘플에, 한 번은 생성된 데이터에 적용한다.

```python
        dis_optimizer.zero_grad()
        dis_output_true_v = net_discr(batch_v)
        dis_output_fake_v = net_discr(gen_output_v.detach())
        dis_loss = objective(dis_output_true_v, true_labels_v) + \
                   objective(dis_output_fake_v, fake_labels_v)
        dis_loss.backward()
        dis_optimizer.step()
        dis_losses.append(dis_loss.item())
```

- `dis_output_true_v = net_discr(batch_v)` — 판별자에 **진짜 이미지**를 넣어 결과를 얻는다.
- `dis_output_fake_v = net_discr(gen_output_v.detach())` — 판별자에 **생성자가 만든 가짜 이미지**를 넣는다. 이때 `gen_output_v.detach()`가 핵심이다.
- `dis_loss = objective(dis_output_true_v, true_labels_v) + objective(dis_output_fake_v, fake_labels_v)` — 진짜 이미지는 "1(진짜)"이라 판단하도록, 가짜 이미지는 "0(가짜)"이라 판단하도록 유도하는 두 손실을 **더한다.**

> [!important] `detach()` — 왜 필요한가?
> 앞의 코드에서 생성자의 출력에 `detach()` 함수를 호출해야 하는 이유는, 이 학습 패스의 그래디언트가 **생성자 쪽으로 흘러 들어가는 것을 막기 위해서**다. `detach()`는 텐서의 메서드로, **부모 연산과의 연결을 끊은 복사본**을 만든다(즉 텐서를 그것을 만든 부모의 그래프에서 떼어낸다). 이 판별자 학습 단계에서는 판별자의 파라미터만 바뀌어야 하므로, 생성자 쪽으로 그래디언트가 새어나가지 않게 막아야 한다.

이제 생성자를 학습시킬 차례다.

```python
        gen_optimizer.zero_grad()
        dis_output_v = net_discr(gen_output_v)
        gen_loss_v = objective(dis_output_v, true_labels_v)
        gen_loss_v.backward()
        gen_optimizer.step()
        gen_losses.append(gen_loss_v.item())
```

이번에는 생성자의 출력을 판별자에 넣어주되(이번엔 `detach()`를 쓰지 않는다 — 그래디언트가 생성자까지 흘러가야 하니까), 라벨은 `True`(1)로 준다. 이렇게 하면 목적 함수가 생성자를 **"판별자가 생성 샘플과 진짜 데이터를 헷갈리게 만드는" 방향**으로 밀어붙인다.

학습과 관련된 코드는 여기까지이고, 다음 몇 줄은 손실을 보고하고 이미지 샘플을 TensorBoard로 보낸다.

```python
        iter_no += 1
        if iter_no % REPORT_EVERY_ITER == 0:
            dt = time.time() - ts_start
            log.info("Iter %d in %.2fs: gen_loss=%.3e, dis_loss=%.3e",
                      iter_no, dt, np.mean(gen_losses), np.mean(dis_losses))
            ts_start = time.time()
            writer.add_scalar("gen_loss", np.mean(gen_losses), iter_no)
            writer.add_scalar("dis_loss", np.mean(dis_losses), iter_no)
            gen_losses = []
            dis_losses = []
        if iter_no % SAVE_IMAGE_EVERY_ITER == 0:
            img = vutils.make_grid(gen_output_v.data[:64], normalize=True)
            writer.add_image("fake", img, iter_no)
            img = vutils.make_grid(batch_v.data[:64], normalize=True)
            writer.add_image("real", img, iter_no)
```

- `writer.add_scalar(...)` — 평균 손실 값을 TensorBoard에 기록한다(앞서 배운 그 함수다).
- `writer.add_image(...)` — 생성된 이미지("fake")와 실제 이미지("real")를 그리드로 묶어 TensorBoard에 이미지로 기록한다. 학습이 잘 되고 있는지 **눈으로** 확인할 수 있는 아주 유용한 수단이다.

이 예제의 학습은 꽤 긴 과정이다. GTX 1080Ti GPU에서는 100번 반복하는 데 약 2.7초가 걸린다. 학습 초반에는 생성된 이미지가 완전히 무작위 노이즈처럼 보이지만, 1만~2만 번 정도 반복하고 나면 생성자가 점점 더 능숙해져서, 생성된 이미지가 실제 게임 스크린샷과 점점 비슷해진다.

> [!tip] 소프트웨어 라이브러리의 발전 속도
> 초판·2판에서는 같은 하드웨어로 같은 예제를 돌리는 데 훨씬 오래 걸렸다. GTX 1080Ti에서 100회 반복에 예전엔 약 40초가 걸렸지만, 이제 PyTorch 2.2.0으로는 2.7초면 된다. 즉 예전엔 좋은 생성 이미지를 얻는 데 3~4시간이 걸렸다면, 이제는 약 30분이면 충분하다.

저자의 실험에서는 4만~5만 회 반복(1080 GPU 기준 약 30분) 학습 후 다음과 같은 이미지를 얻었다.

![[fig_3_7_v3.png]]
*그림 3.7 — 생성자 네트워크가 만들어낸 샘플 이미지*

보다시피, 우리 네트워크는 Atari 스크린샷을 상당히 잘 재현해냈다. 다음 절에서는 애드온 라이브러리인 **PyTorch Ignite**를 이용해 코드를 어떻게 더 단순화할 수 있는지 살펴본다.

---

## 7. PyTorch Ignite

PyTorch는 우아하고 유연한 라이브러리라서, 수많은 연구자·딥러닝 애호가·업계 개발자에게 사랑받는다. 하지만 유연성에는 대가가 따른다 — 문제를 풀려면 그만큼 많은 코드를 직접 써야 한다는 것. 새로운 최적화 방법이나 아직 표준 라이브러리에 없는 딥러닝 기법을 구현하는 경우처럼, 이 유연성이 매우 유용할 때도 있다. 그럴 땐 그저 공식(formula)을 파이썬과 PyTorch로 구현하기만 하면, 그래디언트 계산과 역전파의 모든 뒷일을 라이브러리가 알아서 해준다. 또 그래디언트, 옵티마이저 세부사항, 데이터가 네트워크를 통해 변환되는 방식을 아주 저수준에서 직접 만져야 하는 상황에서도 이 유연성이 빛을 발한다.

하지만 이런 유연성이 필요 없을 때도 있다. 예를 들어 이미지 분류기의 단순한 지도학습(supervised training)처럼 반복적인 작업을 할 때다. 이런 작업엔 순수 PyTorch가 너무 저수준일 수 있고, 매번 똑같은 코드를 반복해서 다뤄야 할 수 있다. 다음은 어떤 딥러닝 학습 절차에서든 필수적이지만, 그때마다 코드를 새로 써야 하는 주제들의 (완전하지 않은) 목록이다.

- 데이터 준비·변환과 배치 생성
- 손실 값, 정확도, F1-score 같은 학습 지표 계산
- 학습 중인 모델을 테스트·검증 데이터셋으로 주기적으로 평가
- 일정 반복 횟수마다 혹은 새로운 최고 성능이 나올 때마다 모델 체크포인트 저장
- TensorBoard 같은 모니터링 도구로 지표 전송
- 시간에 따라 학습률을 바꾸는 등 하이퍼파라미터 스케줄
- 콘솔에 학습 진행 메시지 출력

이 모든 걸 물론 순수 PyTorch만으로도 할 수 있지만, 그러려면 상당한 양의 코드를 직접 써야 한다. 이런 작업은 어느 딥러닝 프로젝트에서든 계속 반복해서 나타나므로, 매번 똑같은 코드를 되풀이해서 쓰는 건 금방 번거로워진다. 이 문제를 푸는 일반적인 방법은 그 기능을 **한 번만 작성해 라이브러리로 감싸고 재사용**하는 것이다. 이는 딥러닝에 국한된 이야기가 아니라, 소프트웨어 업계 어디서나 벌어지는 일이다. 만약 그 라이브러리가 오픈소스이고 품질이 좋다면(사용하기 쉽고, 충분한 유연성을 제공하고, 제대로 작성되어 있는 등), 사람들이 더 많이 쓰면서 인기를 얻게 될 것이다.

PyTorch를 위한, 흔한 작업을 단순화해주는 라이브러리는 여럿 있다 — `ptlearn`, `fastai`, `ignite` 등이다. "PyTorch 생태계 프로젝트"의 현재 목록은 https://pytorch.org/ecosystem 에서 확인할 수 있다.

이런 상위 레벨 라이브러리를 처음부터 쓰고 싶은 유혹이 들 수 있다 — 몇 줄 안 되는 코드로 흔한 문제를 풀 수 있게 해주니까. 하지만 여기엔 위험이 있다.

> [!warning] 상위 레벨 라이브러리만 알면 막힐 수 있다
> 저수준 세부사항을 이해하지 못한 채 상위 레벨 라이브러리 사용법만 안다면, 표준 방법으로는 풀 수 없는 문제에 부딪혔을 때 꼼짝없이 막힐 수 있다. 아주 역동적인 ML 분야에서는 이런 일이 자주 벌어진다.

이 책의 주된 목표는 여러분이 RL 방법과 그 구현, 적용 가능성을 확실히 이해하도록 하는 것이므로, **점진적인 접근**을 취한다. 초반에는 순수 PyTorch 코드만으로 방법을 구현하지만, 진도가 나갈수록 상위 레벨 라이브러리를 이용한 예제도 등장한다. RL을 위해서는 저자가 직접 만든 작은 라이브러리인 **PTAN**(https://github.com/Shmuma/ptan/)을 쓸 것이며, 이는 7장에서 소개된다.

DL 쪽 보일러플레이트 코드를 줄이기 위해, 이 책에서는 **PyTorch Ignite**(https://pytorch-ignite.ai)라는 라이브러리를 쓴다. 이 절에서는 Ignite를 간단히 훑어본 다음, 앞서 만든 Atari GAN 예제를 Ignite로 다시 작성한 버전을 살펴본다.

### 7.1 Ignite 개념

높은 수준에서 보면, Ignite는 PyTorch 딥러닝에서 학습 루프를 작성하는 일을 단순화해준다. 이 챕터 앞부분(손실 함수와 옵티마이저 절)에서 봤듯이, 최소한의 학습 루프는 다음으로 구성된다.

- 학습 데이터의 배치를 샘플링하기
- 이 배치에 신경망을 적용해 손실 함수(우리가 최소화하려는 단일 값)를 계산하기
- 그 손실에 대해 역전파를 실행해 네트워크 파라미터의 그래디언트를 얻기
- 옵티마이저에게 그 그래디언트를 네트워크에 적용해 달라고 요청하기
- 만족스럽거나 지칠 때까지 반복하기

Ignite의 핵심 부품은 **`Engine` 클래스**로, 데이터 소스를 순회하면서 처리 함수를 각 데이터 배치에 적용해준다. 여기에 더해, Ignite는 학습 루프의 **특정 조건**에서 호출될 함수를 등록할 수 있게 해준다. 이런 조건들을 **이벤트(Events)** 라 부르며, 다음과 같은 시점에 걸릴 수 있다.

- 전체 학습 과정의 시작/끝
- 학습 에폭(데이터를 한 번 순회하는 것)의 시작/끝
- 하나의 배치 처리의 시작/끝

여기에 더해, **커스텀 이벤트**도 존재해서, "100번 배치마다" 또는 "2 에폭마다" 특정 계산을 실행하도록 지정할 수도 있다.

다음은 실제로 동작하는 Ignite의 아주 단순한 예다.

```python
from ignite.engine import Engine, Events

def training(engine, batch):
    optimizer.zero_grad()
    x, y = prepare_batch()
    y_out = model(x)
    loss = loss_fn(y_out, y)
    loss.backward()
    optimizer.step()
    return loss.item()

engine = Engine(training)
engine.run(data)
```

- `def training(engine, batch):` — 우리의 **처리 함수(processing function)**. Ignite가 데이터 배치를 순회하며 이 함수를 매번 호출해준다. 함수 내부는 표준적인 학습 스텝 — 그래디언트 초기화, 순전파, 손실 계산, 역전파, 옵티마이저 스텝 — 그대로다.
- `engine = Engine(training)` — 우리 처리 함수로 `Engine` 인스턴스를 만든다.
- `engine.run(data)` — 데이터를 넣어 엔진을 실행한다.

이 코드는 데이터 소스, 모델, 옵티마이저 생성 같은 세부사항이 빠져 있어서 그대로 실행되지는 않지만, Ignite 사용법의 **기본 아이디어**를 보여준다. Ignite의 진짜 이점은, 기존 기능으로 학습 루프를 **확장**할 수 있다는 데 있다. 손실 값을 매끄럽게(smoothing) 만들어 100 배치마다 TensorBoard에 기록하고 싶은가? 문제없다! 두 줄만 추가하면 끝난다. 10 에폭마다 모델 검증(test)을 실행하고 싶은가? 검증을 실행하는 함수를 작성해서 `Engine` 인스턴스에 붙이기만 하면, 알아서 호출해준다.

Ignite 전체 기능에 관한 설명은 이 책의 범위를 벗어나지만, 공식 웹사이트(https://pytorch-ignite.ai)의 문서를 참고하면 된다.

### 7.2 Ignite로 Atari GAN 학습하기

Ignite를 실제로 보여주기 위해, 앞서 만든 Atari 이미지 GAN 학습 예제를 Ignite를 쓰도록 바꿔보자. 전체 예제 코드는 `Chapter03/04_atari_gan_ignite.py`에 있으며, 여기서는 이전 절과 **달라지는 부분**만 보여준다.

먼저 여러 Ignite 클래스를 임포트한다.

```python
from ignite.engine import Engine, Events
from ignite.handlers import Timer
from ignite.metrics import RunningAverage
from ignite.contrib.handlers import tensorboard_logger as tb_logger
```

- `Engine`, `Events` — 이미 설명했다.
- `ignite.metrics` 패키지 — 학습 과정의 성능 지표(혼동 행렬, 정밀도, 재현율 등)를 다루는 클래스가 들어 있다. 이 예제에서는 시계열 값을 매끄럽게 만드는 방법을 제공하는 **`RunningAverage`** 클래스를 쓴다. 앞선 예제에서는 손실 배열에 `np.mean()`을 호출해 이 작업을 했지만, `RunningAverage`가 더 편리하고(수학적으로도 더 올바른) 방법을 제공한다.
- `tb_logger` — Ignite `contrib` 패키지(커뮤니티가 기여한 기능들이 모인 곳)에서 가져온 **TensorBoard 로거**.
- `Timer` — 특정 이벤트 사이에 걸린 시간을 계산하는 간단한 방법을 제공하는 핸들러.

다음으로, 우리의 처리 함수를 정의해야 한다.

```python
def process_batch(trainer, batch):
    gen_input_v = torch.FloatTensor(BATCH_SIZE, LATENT_VECTOR_SIZE, 1, 1)
    gen_input_v.normal_(0, 1)
    gen_input_v = gen_input_v.to(device)
    batch_v = batch.to(device)
    gen_output_v = net_gener(gen_input_v)

    # train discriminator
    dis_optimizer.zero_grad()
    dis_output_true_v = net_discr(batch_v)
    dis_output_fake_v = net_discr(gen_output_v.detach())
    dis_loss = objective(dis_output_true_v, true_labels_v) + \
               objective(dis_output_fake_v, fake_labels_v)
    dis_loss.backward()
    dis_optimizer.step()

    # train generator
    gen_optimizer.zero_grad()
    dis_output_v = net_discr(gen_output_v)
    gen_loss = objective(dis_output_v, true_labels_v)
    gen_loss.backward()
    gen_optimizer.step()

    if trainer.state.iteration % SAVE_IMAGE_EVERY_ITER == 0:
        fake_img = vutils.make_grid(gen_output_v.data[:64], normalize=True)
        trainer.tb.writer.add_image("fake", fake_img, trainer.state.iteration)
        real_img = vutils.make_grid(batch_v.data[:64], normalize=True)
        trainer.tb.writer.add_image("real", real_img, trainer.state.iteration)
        trainer.tb.writer.flush()
    return dis_loss.item(), gen_loss.item()
```

이 함수는 데이터 배치를 받아, 이 배치에 대해 **판별자와 생성자 모델을 모두 갱신**한다. 핵심 로직은 이전 순수 PyTorch 버전과 동일하다(생성자 입력 생성 → 판별자 학습 → 생성자 학습). 다만 몇 가지 차이가 있다.

- `trainer.state.iteration` — Ignite의 `Engine`은 자신의 상태(`state`)에 **현재 반복 횟수를 자동으로 추적**해준다. 그래서 우리가 직접 `iter_no` 카운터를 관리할 필요가 없다.
- 이 함수는 학습 중 추적하고 싶은 어떤 데이터든 **반환**할 수 있다. 여기서는 두 손실 값(판별자, 생성자)을 반환한다. 이 반환값을 이용해 TensorBoard에 표시할 이미지도 저장할 수 있다.

이 작업이 끝나면, 우리가 할 일은 **`Engine` 인스턴스를 만들고, 필요한 핸들러들을 붙이고, 학습 과정을 실행**하는 것뿐이다.

```python
engine = Engine(process_batch)
tb = tb_logger.TensorboardLogger(log_dir=None)
engine.tb = tb
RunningAverage(output_transform=lambda out: out[1]).\
    attach(engine, "avg_loss_gen")
RunningAverage(output_transform=lambda out: out[0]).\
    attach(engine, "avg_loss_dis")

handler = tb_logger.OutputHandler(tag="train", metric_names=['avg_loss_gen',
'avg_loss_dis'])
tb.attach(engine, log_handler=handler, event_name=Events.ITERATION_COMPLETED)

timer = Timer()
timer.attach(engine)
```

- `engine = Engine(process_batch)` — 우리 처리 함수로 엔진을 만든다.
- `RunningAverage(output_transform=lambda out: out[1]).attach(engine, "avg_loss_gen")` — 두 개의 `RunningAverage` 변환을 만들어 우리 손실 두 값에 각각 붙인다(**attach**). 어떤 것이 엔진에 붙으면, `RunningAverage`는 소위 **"지표(metric)"** 를 만들어낸다 — 학습 과정 중에 계속 추적되는 파생 값이다. 여기서는 매끄럽게 만든 지표의 이름을 각각 생성자 손실용 `avg_loss_gen`, 판별자 손실용 `avg_loss_dis`로 짓는다. 이 두 값은 매 반복마다 TensorBoard에 기록된다.
- `timer = Timer()` / `timer.attach(engine)` — 타이머도 엔진에 붙인다. 생성자 인자 없이 만들어져서 **수동으로 제어**하는 단순한 타이머로 동작한다(`reset()` 메서드를 우리가 직접 호출한다).

마지막 코드 조각은 또 다른 이벤트 핸들러를 붙인다. 이 핸들러는 바로 우리가 만든 함수이며, **매 반복이 끝날 때마다** `Engine`이 호출해준다.

```python
@engine.on(Events.ITERATION_COMPLETED)
def log_losses(trainer):
    if trainer.state.iteration % REPORT_EVERY_ITER == 0:
        log.info("%d in %.2fs: gen_loss=%f, dis_loss=%f",
                  trainer.state.iteration, timer.value(),
                  trainer.state.metrics['avg_loss_gen'],
                  trainer.state.metrics['avg_loss_dis'])
        timer.reset()

engine.run(data=iterate_batches(envs))
```

- `@engine.on(Events.ITERATION_COMPLETED)` — 이 데코레이터로, `log_losses` 함수를 **"매 반복이 완료됐을 때"** 이벤트에 등록한다.
- 이 함수는 반복 인덱스, 걸린 시간, 매끄럽게 만든 지표 값들을 담은 로그 한 줄을 기록한다.
- `engine.run(data=iterate_batches(envs))` — 마지막 줄이 엔진을 시작한다. 데이터 소스로는 앞서 정의했던 함수를 그대로 넘긴다(`iterate_batches` 함수는 제너레이터이므로, 그 출력을 그대로 `data` 인자로 넘겨도 아무 문제 없다).

이게 전부다! `Chapter03/04_atari_gan_ignite.py` 예제를 실행하면, 이전 예제와 **완전히 동일하게 동작**한다. 이렇게 작은 예제에서는 큰 차이가 없어 보일 수 있지만, 실제 프로젝트에서는 Ignite를 쓰는 것이 대체로 코드를 더 깔끔하고 확장하기 쉽게 만들어준다.

---

## 요약

이 챕터에서 우리는 PyTorch의 기능과 특징을 빠르게 훑어보았다.

1. **텐서**의 기본 개념(다차원 배열), 생성 방법, 타입, GPU 지원을 배웠다.
2. **그래디언트**가 어떻게 자동으로 계산·추적되는지, `requires_grad`·`is_leaf`·`grad` 속성과 `backward()` 호출을 통해 배웠다.
3. `nn.Module`을 기반으로 **신경망을 building block으로 조립하는 법**(`Sequential`)과 **직접 커스텀 모듈을 만드는 법**을 익혔다.
4. **손실 함수와 옵티마이저**의 역할과 대표적인 종류(MSE, BCE, CrossEntropy / SGD, RMSprop, Adagrad, Adam)를 배웠고, 학습 루프의 표준 청사진(순전파 → 손실 계산 → `backward()` → `optimizer.step()` → `zero_grad()`)을 익혔다.
5. 학습 동역학을 관찰하기 위한 **TensorBoard** 사용법을 배웠다.
6. 이 모든 것을 종합해 **Atari 게임 화면을 생성하는 GAN**을 직접 구현했다.
7. 마지막으로, 학습 루프의 보일러플레이트를 줄여주는 상위 레벨 라이브러리 **PyTorch Ignite**를 소개받았다.

이 챕터의 목표는 이 책의 나머지 부분에서 쓰일 PyTorch에 관해 아주 빠른 소개를 주는 것이었다. 다음 챕터에서는 드디어 이 책의 본론 — RL 방법 — 을 다루기 시작한다.

---

## 🔑 이 챕터의 핵심 용어 (개념정리 링크)
- [[텐서와 다차원배열]]
- [[GPU와 CUDA]]
- [[자동미분과 계산그래프]]
- [[활성화함수]]
- [[옵티마이저와 경사하강법 변형]]
- [[손실함수의 종류]]
- [[에폭 배치 미니배치]]
- [[GAN 생성적적대신경망]]
- [[신경망 경사하강 역전파 기초]]

## 한눈에 보는 개념 지도
| 개념 | 코드/기호 | 한 줄 뜻 |
|---|---|---|
| 텐서 | `torch.Tensor` | 다차원 숫자 배열 (딥러닝의 기본 벽돌) |
| 요구 그래디언트 | `requires_grad` | 이 텐서의 그래디언트를 계산할지 여부 |
| 리프 텐서 | `is_leaf` | 사용자가 직접 만든(부모 없는) 텐서인지 여부 |
| 역전파 호출 | `.backward()` | 그래프를 거꾸로 풀며 그래디언트를 계산 |
| 신경망 기반 클래스 | `nn.Module` | 모든 층·모델의 부모 클래스 |
| 순전파 정의 | `forward()` | 데이터를 어떻게 변환할지 구현하는 자리 |
| 손실 함수 | `nn.MSELoss` 등 | 예측이 정답과 얼마나 다른지를 숫자로 |
| 옵티마이저 | `torch.optim.Adam` 등 | 그래디언트로 가중치를 갱신하는 방법 |
| 에폭 | epoch | 전체 데이터를 한 번 다 도는 단위 |
| 배치 | batch | 한 번에 처리하는 데이터 묶음 |
| 생성자 | Generator | 가짜 데이터를 만드는 GAN의 한 축 |
| 판별자 | Discriminator | 진짜/가짜를 구별하는 GAN의 한 축 |
