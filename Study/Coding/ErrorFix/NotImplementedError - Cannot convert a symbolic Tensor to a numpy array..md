---
date: 2024-02-22, 16:39
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://beausty23.tistory.com/137
  - https://github.com/open-mmlab/OpenPCDet/issues/949#issuecomment-1110740572
---
# 문제 발생
- 학습이 완료된 시점에서 해당 문제 발생
```bash
NotImplementedError: Cannot convert a symbolic Tensor (strided_slice:0) to a numpy array. This error may indicate that you're trying to pass a Tensor to a NumPy call, which is not supported
```
# 원인 분석
- 해당 문제는 tensorflow와 numpy간의 버전 충돌 때문에 발생한 것으로 추측됨 
# 해결 방법
- 이를 해결하기 위해선 numpy 버전을 다운그레이드 해야한다고 하는데 ([reference](https://beausty23.tistory.com/137)) 그러면 다른 패키지와 호환성이 맞지 않게 됨
```bash
error: numpy 1.19.5 is installed but numpy>=1.21.1 is required by {'scikit-image'}
```
- 찾아보니 tensorflow 2.5.0은` waymo-open-dataset-tf-2-5-0`과 의존성으로 묶여 있었으며, 현재는 `waymo-open-dataset-tf-2-6-0`과 `waymo-open-dataset-tf-2-11-0`까지 나왔기 때문에 해당 버전으로 업그레이드 진행 ([reference](https://github.com/open-mmlab/OpenPCDet/issues/949#issuecomment-1110740572))
- numpy 버전이 1.19 혹은 1.21로 설치되기 때문에 `numpy==1.23.4`로 재설치하면 해당 문제 해결됨

