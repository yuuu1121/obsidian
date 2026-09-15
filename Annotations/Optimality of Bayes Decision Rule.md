### Optimality of Bayes Classification (정리)

**문제 설정**
- X는 d-차원의 패턴 공간 \(\Omega_X\)에서의 점으로 주어짐.
- 두 개의 클래스가 있음:
  - \(H_1 : X \in \omega_1\)
  - \(H_2 : X \in \omega_2\)
- \(\omega_1\)의 사전 확률 \(P(\omega_1) = p\)
- 각 클래스에 대한 조건부 밀도:
  - \(p_1(x) = p(x|\omega_1)\)
  - \(p_2(x) = p(x|\omega_2)\)

**결정 문제**
- 패턴 공간 \(\Omega_X\)을 두 개의 분리된 영역 \(\Omega_1\), \(\Omega_2\)로 나누어야 함.
  - \(x \in \Omega_i\)이면 가설 \(H_i\)를 받아들임.
  - 이 문제는 최적의 결정 함수 \(\delta(x)\)를 찾는 것.
  
**오류와 비용**
- 두 가지 오류 가능성:
  - \(x \in \omega_1\)일 때 \(\delta(x) = \omega_2\)
  - \(x \in \omega_2\)일 때 \(\delta(x) = \omega_1\)
- 오류 확률 정의:
  - 1종 오류 확률: \(\alpha = \int_{\Omega_2} p_1(x) dx\)
  - 2종 오류 확률: \(\beta = \int_{\Omega_1} p_2(x) dx\)

**리스크 \( \rho \)**
- 두 가지 오류에 대한 비용 \(c_1\), \(c_2\)를 정의하고, 평균 비용을 리스크 \( \rho \)라 부름.
  - \( \rho = c_1 p \alpha + c_2 (1 - p) \beta \)
  - 즉, \( \rho = c_1 p \int_{\Omega_2} p_1(x) dx + c_2 (1 - p) \int_{\Omega_1} p_2(x) dx \)
  
**베이즈 결정 규칙의 최적성**
- 베이즈 분류기는 리스크 \( \rho \)를 최소화하는 방식으로 \(\Omega_X\)를 최적으로 나눔.
- \(L(x) = \frac{p_2(x)}{p_1(x)}\)가 likelihood ratio이고, \(A = \frac{c_1 p}{c_2 (1 - p)}\)일 때:
  - \(L(x) \le A\)이면 \(x \in \Omega_1\)
  - \(L(x) > A\)이면 \(x \in \Omega_2\)
- 이 조건 하에서 리스크 \( \rho \)가 최소화됨. 

**증명 요약**
- \(\delta(x)\)는 베이즈 결정 함수이고, 이와 다른 결정 함수 \(\delta'(x)\)가 있다고 할 때, \(\rho(\delta') - \rho(\delta) \geq 0\)임을 보임.
  - 이는 두 영역 \(\Omega_1\)과 \(\Omega_2\) 사이의 차이에서 발생하는 추가적인 리스크로 인해 발생.
  - 따라서 베이즈 결정 규칙에 따른 \(\delta(x)\)가 리스크를 최소화하는 최적의 결정 함수임.