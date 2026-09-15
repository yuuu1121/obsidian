# Norm
- 벡터의 크기 또는 길이를 측정하는 수학적 개념
- 주로 벡터나 행렬의 크기를 계산할 때 사용

<br>

## Definition of Norm
- Norm은 일번적으로 다음 조건을 만족하는 함수

1. 비음성성(Non-negativity):  
   $$ ||x|| \geq 0 $$
   - 벡터의 노름은 항상 0 이상
   - $||x|| = 0$일 때, 벡터 $x$는 영벡터($x = 0$)

2. 동차성(Scalar Multiplication):  
   $$ ||\alpha x|| = |\alpha| \cdot ||x|| $$
   - 스칼라 $\alpha$로 벡터 $x$를 곱하면, 그 크기는 $|\alpha|$만큼 변함

1. 삼각 부등식(Triangle Inequality):  
   $$ ||x + y|| \leq ||x|| + ||y|| $$
   - 두 벡터의 합의 노름은 각 벡터의 노름의 합보다 크지 않음

<br>

## Types of Norm
1. 2-Norm (Euclidean norm):
   - 벡터의 유클리드 거리
   - 가장 많이 사용되는 노름
   - 수식:  
     $$ ||x||_2 = \sqrt{x_1^2 + x_2^2 + \cdots + x_n^2} $$  
     벡터 $x = (x_1, x_2, ..., x_n)$의 각 성분을 제곱한 후, 이를 더하고 제곱근을 취한 값
   - 벡터의 크기 또는 길이

2. 1-Norm (Manhattan norm):
   - 벡터 성분들의 절댓값을 모두 더한 값
   - 수식:  
     $$ ||x||_1 = |x_1| + |x_2| + \cdots + |x_n| $$
   - 이는 벡터가 1차원 직교 좌표계 상에서 이동한 거리를 의미

3. Infinity norm:
   - 벡터 성분 중 가장 큰 절댓값
   - 수식:  
     $$ ||x||_\infty = \max(|x_1|, |x_2|, \dots, |x_n|) $$

