---
title: "Chapter 1 — 쿼터니언의 정의와 성질 (Quaternion definition and properties)"
paper: "Quaternion kinematics for the error-state Kalman filter (Joan Solà, 2017)"
chapter: 1
tags: [ESKF, 쿼터니언, 사원수, 복소수, 대수, 지수사상]
---

# Chapter 1 · 쿼터니언의 정의와 성질

> [!abstract] 이 장을 한 문장으로
> 복소수를 한 번 더 확장해서 만든 수 체계인 **쿼터니언(사원수, quaternion)** 을 정의하고, 덧셈·곱셈·켤레·노름·역원 같은 기본 연산과 지수·로그를 정리한다. 아직 "회전"이라는 말은 거의 나오지 않는다. 회전을 담을 **그릇**을 먼저 만드는 장이다.

---

## 들어가며 — 왜 하필 쿼터니언인가?

로봇이나 드론의 자세(attitude)를 나타내는 방법은 여러 가지다. 오일러 각(roll-pitch-yaw), 회전행렬, 축-각도, 그리고 쿼터니언. 이 중에서 쿼터니언이 실무에서 압도적으로 많이 쓰이는데, 이유는 세 가지다.

첫째, **짐벌 락(gimbal lock)이 없다.** 오일러 각은 특정 자세(예: 피치 90°)에서 자유도 하나를 잃어버리는 고질병이 있다. 쿼터니언에는 그런 특이점이 없다.

둘째, **저장 공간이 작고 계산이 싸다.** 회전행렬은 숫자 9개가 필요한데 쿼터니언은 4개면 된다. 회전을 여러 번 합성할 때도 4×4 곱 한 번이면 끝이다.

셋째, **수치 오차가 쌓여도 고치기 쉽다.** 회전행렬은 오차가 쌓이면 "직교행렬"이라는 조건이 깨져서 복원하기가 번거롭지만, 쿼터니언은 그냥 **길이를 1로 다시 정규화**하면 된다.

이 장에서는 그 쿼터니언이 정확히 무엇인지, 어떤 규칙으로 계산하는지를 다진다. 회전과의 연결은 [[Chapter 02 - 회전과 상호관계|2장]]에서 본격적으로 나온다.

> [!tip] 먼저 읽으면 좋은 노트
> 쿼터니언이 왜 4개의 숫자인지, 왜 복소수의 확장인지에 대한 직관적인 설명은 [[쿼터니언이란 무엇인가]]에 따로 정리했다.

---

## 1. 쿼터니언의 정의

### 1.1 케일리-딕슨 구성 — 복소수를 한 번 더 확장하기

논문이 가장 매력적이라고 소개하는 정의 방식은 **케일리-딕슨 구성(Cayley-Dickson construction)** 이다. 아이디어는 단순하다. *"복소수 두 개를 다시 복소수처럼 묶자"* 는 것이다.

복소수 두 개 $A = a + bi$, $C = c + di$ 가 있다고 하자. 이걸 새로운 허수 단위 $j$ 로 묶어서

$$Q = A + Cj$$

라고 쓰고, $k \triangleq ij$ 라고 정의한다. 전개하면

$$Q = a + bi + cj + dk \in \mathbb{H}$$

가 되고, 이것이 바로 **쿼터니언**이다. $\mathbb{H}$ 라는 기호는 발견자인 **해밀턴(Hamilton)** 의 이름에서 왔다. 여기서 $\{a,b,c,d\} \in \mathbb{R}$ 은 평범한 실수이고, $\{i,j,k\}$ 는 세 개의 허수 단위다.

### 1.2 쿼터니언 대수 — 이 세 줄이 전부다

$\{i, j, k\}$ 가 어떻게 행동하는지가 쿼터니언의 모든 것을 결정한다. 규칙은 딱 하나로 시작한다.

$$i^2 = j^2 = k^2 = ijk = -1$$

**이 한 줄에서 나머지가 전부 유도된다.** 유도 결과를 적으면

$$ij = -ji = k, \qquad jk = -kj = i, \qquad ki = -ik = j$$

> [!important] 여기가 가장 중요한 대목
> $ij = k$ 인데 $ji = -k$ 다. **순서를 바꾸면 부호가 뒤집힌다.** 이것이 쿼터니언 곱이 **교환법칙을 만족하지 않는(non-commutative)** 근본 이유이고, 동시에 3D 회전을 표현할 수 있는 이유이기도 하다. 3D 회전도 순서를 바꾸면 결과가 달라지기 때문이다. (책상 위의 물건을 "오른쪽으로 90° 돌리고 앞으로 90° 눕히기"와 "앞으로 90° 눕히고 오른쪽으로 90° 돌리기"를 해 보면 다른 자세가 된다.)

### 1.3 쿼터니언은 복소수와 실수를 포함한다

정의를 보면 실수도, 허수도, 복소수도 전부 쿼터니언의 특수한 경우임을 알 수 있다.

$$Q = a \in \mathbb{R} \subset \mathbb{H}, \qquad Q = bi \in \mathbb{I} \subset \mathbb{H}, \qquad Q = a + bi \in \mathbb{Z} \subset \mathbb{H}$$

그리고 실수부가 0인, 즉 순수하게 허수부만 있는 쿼터니언을 따로 이름 붙여 **순허 쿼터니언(pure quaternion)** 이라 하고 $\mathbb{H}_p$ 로 쓴다.

$$Q = bi + cj + dk \in \mathbb{H}_p \subset \mathbb{H}$$

이 순허 쿼터니언이 나중에 **3D 벡터**를 쿼터니언 세계로 집어넣는 통로가 된다.

### 1.4 2D 회전과 3D 회전의 평행 관계

논문이 짚어 주는 아름다운 대응이 하나 있다.

| | 2D 평면 회전 | 3D 공간 회전 |
|---|---|---|
| 쓰는 수 | 단위 복소수 $z = e^{i\theta}$ | 단위 쿼터니언 $\mathbf{q} = e^{(u_xi+u_yj+u_zk)\theta/2}$ |
| 회전 방법 | 곱 **한 번**: $x' = z \cdot x$ | 곱 **두 번**: $x' = \mathbf{q} \otimes x \otimes \mathbf{q}^*$ |

즉 쿼터니언은 "확장된 복소수"이고, 회전시키는 방법도 복소수의 자연스러운 확장이다. 다만 **곱을 두 번** 한다는 점, 그리고 지수의 각도가 $\theta$ 가 아니라 **$\theta/2$** 라는 점이 결정적으로 다르다. 이 "반각(half angle)"의 정체는 [[Chapter 02 - 회전과 상호관계|2장]]에서 밝혀진다.

> [!warning] CAUTION — 모든 쿼터니언 정의가 같지는 않다
> 어떤 저자들은 곱을 $bi$ 대신 $ib$ 로 쓰고, 그 결과 $k = ji = -ij$ 가 되어 $ijk = +1$ 인 **왼손잡이(left-handed)** 쿼터니언을 얻는다. 또 많은 저자들이 실수부를 **맨 뒤**에 두어 $Q = ia + jb + kc + d$ 로 쓴다.
>
> 이런 선택들은 근본적인 차이는 아니지만 **세부 수식을 전부 다르게 만든다.** 이 논문은 위 정의를 쓰는 **Hamilton 규약**을 따른다. 이 혼란을 정리하는 것이 통째로 [[Chapter 03 - 쿼터니언 규약|3장]]의 주제다.

---

## 2. 쿼터니언을 적는 여러 가지 방법

$\{1, i, j, k\}$ 표기는 계산할 때 불편하다. 그래서 실무에서는 다음 표기들을 섞어 쓴다.

### 2.1 스칼라 + 벡터

$$Q = q_w + q_xi + q_yj + q_zk \iff Q = q_w + \mathbf{q}_v$$

여기서 $q_w$ 를 **실수부(real part)** 또는 **스칼라부(scalar part)**, $\mathbf{q}_v = (q_x, q_y, q_z)$ 를 **허수부(imaginary part)** 또는 **벡터부(vector part)** 라고 부른다.

### 2.2 순서쌍

$$Q = \langle q_w, \mathbf{q}_v \rangle$$

### 2.3 4차원 벡터 — 실제 계산에 쓰는 형태

$$\mathbf{q} \triangleq \begin{bmatrix} q_w \\ \mathbf{q}_v \end{bmatrix} = \begin{bmatrix} q_w \\ q_x \\ q_y \\ q_z \end{bmatrix}$$

이 표기 덕분에 **쿼터니언 연산을 행렬 대수로 처리**할 수 있다. 코드로 구현할 때는 거의 항상 이 형태를 쓴다.

특수한 경우를 이 표기로 적으면 이렇다.

$$\text{일반: } \mathbf{q} = \begin{bmatrix} q_w \\ \mathbf{q}_v\end{bmatrix}, \qquad \text{실수: } \mathbf{q}_w = \begin{bmatrix} q_w \\ \mathbf{0}_v\end{bmatrix}, \qquad \text{순허: } \mathbf{q}_v = \begin{bmatrix} 0 \\ \mathbf{q}_v\end{bmatrix}$$

> [!note] 아래 첨자를 $(w,x,y,z)$ 로 쓰는 이유
> 논문은 쿼터니언의 **3D 데카르트 공간에서의 기하적 성질**에 관심이 있기 때문에 $(w,x,y,z)$ 를 쓴다. 다른 책들은 $(0,1,2,3)$ 이나 $(1,i,j,k)$ 를 쓰기도 하는데, 이쪽은 수학적 해석에 더 어울리는 표기다.

---

## 3. 쿼터니언의 주요 성질

### 3.1 덧셈 — 그냥 성분별로 더하면 된다

$$\mathbf{p} \pm \mathbf{q} = \begin{bmatrix} p_w \\ \mathbf{p}_v\end{bmatrix} \pm \begin{bmatrix} q_w \\ \mathbf{q}_v\end{bmatrix} = \begin{bmatrix} p_w \pm q_w \\ \mathbf{p}_v \pm \mathbf{q}_v\end{bmatrix}$$

덧셈은 **교환법칙과 결합법칙을 모두 만족한다.**

$$\mathbf{p} + \mathbf{q} = \mathbf{q} + \mathbf{p}, \qquad \mathbf{p} + (\mathbf{q} + \mathbf{r}) = (\mathbf{p} + \mathbf{q}) + \mathbf{r}$$

### 3.2 곱 — 쿼터니언의 심장

곱은 $\otimes$ 로 표기한다. 정의 (1)과 대수 규칙 (2)를 그대로 전개하면

$$\mathbf{p} \otimes \mathbf{q} = \begin{bmatrix}
p_wq_w - p_xq_x - p_yq_y - p_zq_z \\
p_wq_x + p_xq_w + p_yq_z - p_zq_y \\
p_wq_y - p_xq_z + p_yq_w + p_zq_x \\
p_wq_z + p_xq_y - p_yq_x + p_zq_w
\end{bmatrix}$$

이걸 스칼라/벡터 부분으로 나눠 쓰면 훨씬 뜻이 잘 보인다.

$$\mathbf{p} \otimes \mathbf{q} = \begin{bmatrix} p_wq_w - \mathbf{p}_v^\top \mathbf{q}_v \\ p_w\mathbf{q}_v + q_w\mathbf{p}_v + \mathbf{p}_v \times \mathbf{q}_v \end{bmatrix}$$

> [!important] 외적($\times$)의 등장이 모든 것을 설명한다
> 벡터부에 **외적 $\mathbf{p}_v \times \mathbf{q}_v$** 가 들어 있다. 외적은 순서를 바꾸면 부호가 뒤집히는 연산($\mathbf{a}\times\mathbf{b} = -\mathbf{b}\times\mathbf{a}$)이다. 그래서 일반적으로
> $$\mathbf{p} \otimes \mathbf{q} \neq \mathbf{q} \otimes \mathbf{p}$$
> 이다. **교환법칙이 성립하는 예외**는 외적이 0이 될 때뿐이다. 즉 (a) 둘 중 하나가 실수 쿼터니언이거나, (b) 두 벡터부가 서로 평행할 때다.

곱은 교환법칙만 안 될 뿐, **결합법칙과 분배법칙은 만족한다.**

$$(\mathbf{p} \otimes \mathbf{q}) \otimes \mathbf{r} = \mathbf{p} \otimes (\mathbf{q} \otimes \mathbf{r})$$
$$\mathbf{p} \otimes (\mathbf{q} + \mathbf{r}) = \mathbf{p}\otimes\mathbf{q} + \mathbf{p}\otimes\mathbf{r}$$

### 3.3 곱을 행렬로 — 구현할 때 꼭 쓰는 형태

쿼터니언 곱은 **두 인자 각각에 대해 선형(bi-linear)** 이다. 따라서 어느 쪽을 고정하든 행렬 곱으로 쓸 수 있다.

$$\mathbf{q}_1 \otimes \mathbf{q}_2 = [\mathbf{q}_1]_L\,\mathbf{q}_2 \qquad \text{그리고} \qquad \mathbf{q}_1 \otimes \mathbf{q}_2 = [\mathbf{q}_2]_R\,\mathbf{q}_1$$

여기서 $[\mathbf{q}]_L$, $[\mathbf{q}]_R$ 을 각각 **좌 곱 행렬**, **우 곱 행렬**이라 부른다.

$$[\mathbf{q}]_L = \begin{bmatrix}
q_w & -q_x & -q_y & -q_z \\
q_x & q_w & -q_z & q_y \\
q_y & q_z & q_w & -q_x \\
q_z & -q_y & q_x & q_w
\end{bmatrix}, \qquad
[\mathbf{q}]_R = \begin{bmatrix}
q_w & -q_x & -q_y & -q_z \\
q_x & q_w & q_z & -q_y \\
q_y & -q_z & q_w & q_x \\
q_z & q_y & -q_x & q_w
\end{bmatrix}$$

더 간결하게는

$$[\mathbf{q}]_L = q_w\mathbf{I} + \begin{bmatrix} 0 & -\mathbf{q}_v^\top \\ \mathbf{q}_v & [\mathbf{q}_v]_\times \end{bmatrix}, \qquad
[\mathbf{q}]_R = q_w\mathbf{I} + \begin{bmatrix} 0 & -\mathbf{q}_v^\top \\ \mathbf{q}_v & -[\mathbf{q}_v]_\times \end{bmatrix}$$

**두 행렬의 차이는 오직 오른쪽 아래 블록의 부호 하나뿐이다.** 이것이 좌·우 곱의 차이 전부다.

### 3.4 스큐 연산자 $[\cdot]_\times$ — 외적을 행렬로

위 식에 나온 $[\cdot]_\times$ 는 **외적을 행렬 곱으로 바꿔 주는** 연산자다.

$$[\mathbf{a}]_\times \triangleq \begin{bmatrix} 0 & -a_z & a_y \\ a_z & 0 & -a_x \\ -a_y & a_x & 0 \end{bmatrix}$$

이 행렬은 **반대칭(skew-symmetric)** 이다. 즉 $[\mathbf{a}]_\times^\top = -[\mathbf{a}]_\times$ 이고, 외적과 완전히 같은 일을 한다.

$$[\mathbf{a}]_\times\,\mathbf{b} = \mathbf{a} \times \mathbf{b}, \qquad \forall\, \mathbf{a},\mathbf{b} \in \mathbb{R}^3$$

> [!note] 이 연산자의 이름이 너무 많다
> 문헌마다 이 연산자를 $[\mathbf{a}]_\times$, $[\mathbf{a}\times]$, $\mathbf{a}^\wedge$, $\hat{\mathbf{a}}$, $[\mathbf{a}]$ 등 제각각으로 쓴다. 전부 같은 뜻이다. 이 노트에서는 논문을 따라 $[\mathbf{a}]_\times$ 로 통일한다. 이 연산자는 [[리 군과 리 대수]]에서 $\mathfrak{so}(3)$ 라는 이름으로 다시 등장한다.

### 3.5 좌·우 곱 행렬은 서로 교환된다

$\mathbf{q} \otimes \mathbf{x} \otimes \mathbf{p}$ 를 두 가지 순서로 묶어서 계산해 보면

$$\mathbf{q} \otimes \mathbf{x} \otimes \mathbf{p} = (\mathbf{q}\otimes\mathbf{x})\otimes\mathbf{p} = [\mathbf{p}]_R[\mathbf{q}]_L\,\mathbf{x} = \mathbf{q}\otimes(\mathbf{x}\otimes\mathbf{p}) = [\mathbf{q}]_L[\mathbf{p}]_R\,\mathbf{x}$$

따라서

$$[\mathbf{p}]_R[\mathbf{q}]_L = [\mathbf{q}]_L[\mathbf{p}]_R$$

즉 **좌 곱 행렬과 우 곱 행렬은 서로 교환된다.** 쿼터니언 곱 자체는 교환이 안 되는데 이 행렬들은 교환된다는 게 재미있는 지점이고, 2장의 "회전 마술"을 설명할 때 핵심 재료가 된다.

### 3.6 항등원

곱의 항등원은 실수 1을 쿼터니언으로 쓴 것이다.

$$\mathbf{q}_1 = 1 = \begin{bmatrix} 1 \\ \mathbf{0}_v \end{bmatrix}$$

### 3.7 켤레 (Conjugate)

$$\mathbf{q}^* \triangleq q_w - \mathbf{q}_v = \begin{bmatrix} q_w \\ -\mathbf{q}_v \end{bmatrix}$$

**벡터부의 부호만 뒤집는다.** 복소수의 켤레와 똑같은 발상이다. 성질은

$$\mathbf{q} \otimes \mathbf{q}^* = \mathbf{q}^* \otimes \mathbf{q} = q_w^2 + q_x^2 + q_y^2 + q_z^2 = \begin{bmatrix} q_w^2+q_x^2+q_y^2+q_z^2 \\ \mathbf{0}_v\end{bmatrix}$$

$$(\mathbf{p}\otimes\mathbf{q})^* = \mathbf{q}^* \otimes \mathbf{p}^*$$

> [!warning] 켤레를 취하면 순서가 뒤집힌다
> $(\mathbf{p}\otimes\mathbf{q})^* = \mathbf{q}^*\otimes\mathbf{p}^*$ 에서 **$\mathbf{p}$와 $\mathbf{q}$의 순서가 바뀐** 것에 주목하자. 행렬의 전치나 역행렬과 같은 패턴이다. 구현할 때 자주 틀리는 부분이다.

### 3.8 노름 (Norm)

$$\|\mathbf{q}\| \triangleq \sqrt{\mathbf{q}\otimes\mathbf{q}^*} = \sqrt{q_w^2+q_x^2+q_y^2+q_z^2} \in \mathbb{R}$$

그냥 4차원 벡터의 길이다. 성질은

$$\|\mathbf{p}\otimes\mathbf{q}\| = \|\mathbf{q}\otimes\mathbf{p}\| = \|\mathbf{p}\|\,\|\mathbf{q}\|$$

**곱의 길이는 길이의 곱이다.** 이 성질이 "단위 쿼터니언끼리 곱해도 계속 단위 쿼터니언"임을 보장해 준다. 회전을 아무리 합성해도 여전히 회전이라는 뜻이다.

### 3.9 역원 (Inverse)

$$\mathbf{q}\otimes\mathbf{q}^{-1} = \mathbf{q}^{-1}\otimes\mathbf{q} = \mathbf{q}_1$$

계산은

$$\mathbf{q}^{-1} = \mathbf{q}^*/\|\mathbf{q}\|^2$$

### 3.10 단위 쿼터니언 — 우리가 실제로 쓸 물건

$\|\mathbf{q}\| = 1$ 인 쿼터니언을 **단위(unit) 쿼터니언** 또는 **정규화된 쿼터니언**이라 한다. 이때 위 식에서 분모가 1이 되므로

$$\boxed{\mathbf{q}^{-1} = \mathbf{q}^*}$$

> [!important] 이 한 줄이 실무에서 엄청나게 중요하다
> 단위 쿼터니언을 회전으로 해석할 때, **역회전은 그냥 켤레를 취하면 된다.** 즉 부호 세 개만 뒤집으면 끝이다. 회전행렬에서 역회전을 구하려면 전치($\mathbf{R}^\top$)를 해야 하는데, 그보다도 싸다.

단위 쿼터니언은 항상 다음 형태로 쓸 수 있다.

$$\mathbf{q} = \begin{bmatrix} \cos\theta \\ \mathbf{u}\sin\theta\end{bmatrix}$$

여기서 $\mathbf{u}$ 는 단위벡터, $\theta$ 는 스칼라다. **이 형태가 2장에서 "축 $\mathbf{u}$ 를 중심으로 $2\theta$ 만큼 회전"으로 해석된다.** 벌써 반각이 보인다.

단위 쿼터니언들은 곱 연산과 함께 **비가환 군(non-commutative group)** 을 이루며, 여기서 역원은 켤레와 일치한다.

---

## 4. 추가 성질 — 지수와 로그

이 절은 나중에 회전을 미분하고 적분할 때 쓰는 도구를 미리 만들어 두는 곳이다. [[Chapter 04 - 섭동 미분 적분|4장]]의 준비 작업이라고 보면 된다.

### 4.1 교환자 (Commutator)

두 쿼터니언의 곱이 순서에 따라 얼마나 달라지는지를 재는 양이다.

$$\mathbf{p}\otimes\mathbf{q} - \mathbf{q}\otimes\mathbf{p} = 2\,\mathbf{p}_v \times \mathbf{q}_v$$

**차이는 정확히 외적의 두 배**다. 외적이 0이면 교환된다는 앞의 이야기와 정확히 맞아떨어진다.

### 4.2 순허 쿼터니언의 곱

$\mathbf{p}, \mathbf{q}$ 가 모두 순허 쿼터니언(실수부 0)이면

$$\mathbf{p}\otimes\mathbf{q} = \begin{bmatrix} -\mathbf{p}_v^\top\mathbf{q}_v \\ \mathbf{p}_v\times\mathbf{q}_v \end{bmatrix}$$

즉 **실수부에는 내적(부호 반대)이, 벡터부에는 외적이** 들어간다. 내적과 외적이 한 연산 안에 동시에 들어 있는 셈이다.

자기 자신과 곱하면 외적이 0이 되므로

$$\mathbf{q}_v\otimes\mathbf{q}_v = -\mathbf{q}_v^\top\mathbf{q}_v = -\|\mathbf{q}_v\|^2$$

그리고 **순허 단위 쿼터니언** $\mathbf{u}\in\mathbb{H}_p$, $\|\mathbf{u}\|=1$ 에 대해서는

$$\boxed{\mathbf{u}\otimes\mathbf{u} = -1}$$

> [!important] 허수 단위와 완전히 같다
> 복소수의 $i\cdot i = -1$ 과 **정확히 같은 식**이다. 즉 **임의의 순허 단위 쿼터니언은 허수 단위처럼 행동한다.**
>
> 복소수에는 그런 원소가 $\pm i$ 둘뿐이지만, 쿼터니언에는 **3차원 단위구 전체**가 그런 원소다. 무한히 많은 "허수 단위"가 있는 셈이고, 그중 어느 방향을 고르느냐가 곧 **회전축을 고르는 것**이 된다. 이것이 쿼터니언이 3D 회전을 담을 수 있는 대수적 뿌리다.

### 4.3 순허 쿼터니언의 거듭제곱

$\mathbf{v} = \mathbf{u}\theta$ ($\mathbf{u}$는 단위벡터, $\theta=\|\mathbf{v}\|$)라는 순허 쿼터니언을 생각하자. 위 결과를 반복 적용하면 **주기적인 패턴**이 나온다.

$$\mathbf{v}^2 = -\theta^2, \quad \mathbf{v}^3 = -\mathbf{u}\theta^3, \quad \mathbf{v}^4 = \theta^4, \quad \mathbf{v}^5 = \mathbf{u}\theta^5, \quad \mathbf{v}^6 = -\theta^6, \ \dots$$

**실수와 벡터가 번갈아 나오며 부호가 두 번마다 뒤집힌다.** 순허 단위 쿼터니언 $\mathbf{u}$ 만 놓고 보면 더 간단해진다.

$$\mathbf{u}^2 = -1, \quad \mathbf{u}^3 = -\mathbf{u}, \quad \mathbf{u}^4 = 1, \quad \mathbf{u}^5 = \mathbf{u}, \quad \mathbf{u}^6 = -1, \ \dots$$

허수 단위의 거듭제곱($i^2=-1$, $i^3=-i$, $i^4=1$, …)과 **글자 하나 다르지 않다.** 그래서 다음 결과가 나온다.

### 4.4 순허 쿼터니언의 지수 — 오일러 공식의 3D 판

지수함수를 테일러 급수로 펼치고 위 패턴을 대입하면, 실수 항과 벡터 항이 각각 코사인과 사인의 급수로 모인다.

$$e^{\mathbf{v}} = \sum_{k=0}^{\infty}\frac{1}{k!}\mathbf{v}^k = \left(1 - \frac{\theta^2}{2!} + \frac{\theta^4}{4!} + \cdots\right) + \left(\mathbf{u}\theta - \frac{\mathbf{u}\theta^3}{3!} + \frac{\mathbf{u}\theta^5}{5!} + \cdots\right)$$

정리하면

$$\boxed{e^{\mathbf{v}} = \exp(\mathbf{u}\theta) = \cos\theta + \mathbf{u}\sin\theta = \begin{bmatrix}\cos\theta \\ \mathbf{u}\sin\theta\end{bmatrix}}$$

> [!important] 이것이 이 논문에서 가장 자주 쓰이는 공식이다
> 복소수의 오일러 공식 $e^{i\theta} = \cos\theta + i\sin\theta$ 와 **판박이**다. 차이는 허수 단위 $i$ 자리에 3D 단위벡터 $\mathbf{u}$ 가 들어갔다는 것뿐이다.
>
> 그리고 결과를 보라. 우변은 3.10절에서 본 **단위 쿼터니언의 일반형과 정확히 같다.** 즉 **순허 쿼터니언의 지수는 항상 단위 쿼터니언**이다. $\|e^{\mathbf{v}}\| = \sqrt{\cos^2\theta+\sin^2\theta} = 1$ 이니 당연하다.
>
> 이 사실이 뜻하는 바는 크다. **"회전축과 각도(= 3개의 숫자)"를 넣으면 "회전 쿼터니언(= 4개의 숫자, 단위 길이)"이 튀어나오는 변환기**를 우리가 손에 넣은 것이다. 이것이 [[리 군과 리 대수|리 대수에서 리 군으로 가는 지수사상]]이다.

유용한 성질이 하나 더 있다.

$$e^{-\mathbf{v}} = (e^{\mathbf{v}})^*$$

**지수의 부호를 뒤집는 것과 켤레를 취하는 것이 같다.** 회전으로 읽으면 "반대로 돌리기 = 켤레"라는 3.10절의 이야기와 정확히 같은 말이다.

#### 작은 각에서의 근사 — 실무에서 매일 쓰는 식

> [!warning] $\theta\to0$ 이면 $\mathbf{u}=\mathbf{v}/\|\mathbf{v}\|$ 가 0으로 나눈다
> 로그사상과 같은 문제다. 논문은 $\sin\theta$ 와 $\cos\theta$ 의 테일러 급수를 잘라서 쓰라고 알려 준다. 절단 차수에 따라 근사가 달라진다.
>
> $$e^{\mathbf{v}} \approx \begin{bmatrix}1-\theta^2/2 \\ \mathbf{v}(1-\theta^2/6)\end{bmatrix} \approx \begin{bmatrix}1 \\ \mathbf{v}\end{bmatrix} \approx \begin{bmatrix}1 \\ \mathbf{0}\end{bmatrix}$$
>
> 오른쪽으로 갈수록 거친 근사다. **가운데 형태 $[1,\ \mathbf{v}]$ 가 ESKF에서 가장 많이 쓰인다.** $\mathbf{v}$ 로 나누는 연산이 없으므로 $\theta=0$ 에서도 안전하다.
>
> [[Chapter 04 - 섭동 미분 적분|4장]] 4.1절의 $\mathbf{q}\{\delta\boldsymbol{\theta}\}\approx[1,\ \delta\boldsymbol{\theta}/2]$ 가 바로 이 근사에 $\mathbf{v}=\delta\boldsymbol{\theta}/2$ 를 넣은 것이다. ESKF의 모든 자코비안이 단순해지는 출발점이 여기다.

### 4.5 일반 쿼터니언의 지수

실수부가 있는 일반 쿼터니언은 실수부를 그냥 밖으로 빼내면 된다. $\mathbf{q} = q_w + \mathbf{q}_v$ 이고 $q_w$ 는 실수여서 모든 것과 교환되므로

$$e^{\mathbf{q}} = e^{q_w + \mathbf{q}_v} = e^{q_w}e^{\mathbf{q}_v} = e^{q_w}\begin{bmatrix}\cos\|\mathbf{q}_v\| \\ \frac{\mathbf{q}_v}{\|\mathbf{q}_v\|}\sin\|\mathbf{q}_v\|\end{bmatrix}$$

### 4.6 단위 쿼터니언의 로그 — 지수의 반대 방향

$\|\mathbf{q}\|=1$ 이면 $\mathbf{q} = \cos\theta + \mathbf{u}\sin\theta$ 이므로, 지수의 정의를 거꾸로 읽으면

$$\log\mathbf{q} = \log(\cos\theta + \mathbf{u}\sin\theta) = \log(e^{\mathbf{u}\theta}) = \mathbf{u}\theta = \begin{bmatrix} 0 \\ \mathbf{u}\theta\end{bmatrix}$$

실제로 $\mathbf{q}$ 의 성분에서 계산하려면

$$\mathbf{u} = \mathbf{q}_v/\|\mathbf{q}_v\|, \qquad \theta = \arctan(\|\mathbf{q}_v\|, q_w)$$

> [!note] $\arctan$ 을 2-인자로 써야 하는 이유
> $\theta = \arctan(\|\mathbf{q}_v\|/q_w)$ 로 쓰면 $q_w$ 가 음수일 때 각도가 반 바퀴 어긋난다. 코드에서는 반드시 `atan2(norm(qv), qw)` 를 써야 한다. 흔한 버그 지점이다.

**로그의 결과는 항상 순허 쿼터니언**이고, 그 벡터부 $\mathbf{u}\theta$ 가 바로 **회전 벡터(rotation vector)** 다. 즉 로그는 "회전 쿼터니언 → 축·각도"를 뽑아내는 연산이다.

### 4.7 일반 쿼터니언의 로그

$$\log\mathbf{q} = \log(\|\mathbf{q}\|\,\tfrac{\mathbf{q}}{\|\mathbf{q}\|}) = \log\|\mathbf{q}\| + \log\tfrac{\mathbf{q}}{\|\mathbf{q}\|} = \begin{bmatrix}\log\|\mathbf{q}\| \\ \mathbf{u}\theta\end{bmatrix}$$

### 4.8 $\mathbf{q}^t$ 형태의 지수 — 보간의 씨앗

실수 $t$ 에 대해

$$\mathbf{q}^t = \exp(\log(\mathbf{q}^t)) = \exp(t\log\mathbf{q})$$

$\|\mathbf{q}\|=1$ 이면 $\log\mathbf{q} = \mathbf{u}\theta$ 이므로

$$\mathbf{q}^t = \exp(t\,\mathbf{u}\theta) = \begin{bmatrix}\cos t\theta \\ \mathbf{u}\sin t\theta\end{bmatrix}$$

> [!tip] 여기서 SLERP가 태어난다
> 지수 $t$ 가 **각도 $\theta$ 의 선형 배수로 튀어나왔다.** $t=0$ 이면 항등원, $t=1$ 이면 $\mathbf{q}$, 그 사이면 각도를 비례 배분한 중간 회전이다. 즉 $\mathbf{q}^t$ 는 **각도에 대한 선형 보간기**다. 이 아이디어를 그대로 발전시킨 것이 2.7절의 **SLERP(구면 선형 보간)** 이다.

---

## 정리 — 이 장에서 챙겨야 할 것

| 개념 | 공식 | 왜 중요한가 |
|---|---|---|
| 대수 규칙 | $i^2=j^2=k^2=ijk=-1$ | 모든 것의 출발점 |
| 곱 | $\mathbf{p}\otimes\mathbf{q} = \begin{bmatrix} p_wq_w - \mathbf{p}_v^\top\mathbf{q}_v \\ p_w\mathbf{q}_v + q_w\mathbf{p}_v + \mathbf{p}_v\times\mathbf{q}_v\end{bmatrix}$ | 회전 합성의 실체 |
| 곱 행렬 | $\mathbf{q}_1\otimes\mathbf{q}_2 = [\mathbf{q}_1]_L\mathbf{q}_2 = [\mathbf{q}_2]_R\mathbf{q}_1$ | 구현·자코비안 계산의 필수품 |
| 단위 역원 | $\mathbf{q}^{-1} = \mathbf{q}^*$ | 역회전이 공짜 |
| 지수 | $\exp(\mathbf{u}\theta) = \begin{bmatrix}\cos\theta\\ \mathbf{u}\sin\theta\end{bmatrix}$ | 축·각도 → 쿼터니언 |
| 로그 | $\log\mathbf{q} = \mathbf{u}\theta$ | 쿼터니언 → 축·각도 |

> [!warning] 아직 회전은 시작도 안 했다
> 이 장에서 "회전"이라는 말이 몇 번 나오긴 했지만, 어디까지나 예고편이었다. **왜 단위 쿼터니언이 회전을 표현하는지, 왜 곱을 두 번 하는지, 왜 각도가 절반인지**는 전부 [[Chapter 02 - 회전과 상호관계|2장]]에서 증명된다.

---

## 관련 노트

- [[쿼터니언이란 무엇인가]] — 복소수 → 쿼터니언 확장의 직관
- [[리 군과 리 대수]] — 지수·로그가 사실 무엇인지
- [[Chapter 02 - 회전과 상호관계]] — 다음 장
- [[Chapter 03 - 쿼터니언 규약]] — Hamilton vs JPL 혼란 정리
