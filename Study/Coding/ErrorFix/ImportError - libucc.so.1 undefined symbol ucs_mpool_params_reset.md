---
date: 2024-08-26
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
keywords:
  - libucc.so.1
  - ucs_mpool_params_reset
related notes: 
reference: 
author: 
url: 
dg-publish: true
---
# 문제 발생

- `{python}import torch` 과정에서 에러 발생

```shell
Traceback (most recent call last): File "/mast3r/ksm_demo.py", line 9, in <module> import torch File "/usr/local/lib/python3.10/dist-packages/torch/__init__.py", line 236, in <module> from torch._C import * # noqa: F403 ImportError: /opt/hpcx/ucc/lib/libucc.so.1: undefined symbol: ucs_mpool_params_reset
```

<br/>

# 원인 분석

- 이 에러는 PyTorch가 특정 라이브러리(`libucc.so.1`)에서 `ucs_mpool_params_reset`이라는 심볼을 찾지 못하여 발생
- 주로 라이브러리 간의 버전 불일치 또는 잘못된 환경 변수 설정으로 인해 발생

<br/>

# 해결 방법

- **라이브러리 문제 해결**:
    - `hwloc` 관련 라이브러리들을 제거하여 충돌을 방지
	    ```shell
	    sudo apt purge hwloc-nox libhwloc-dev libhwloc-plugins
		```
    
- **환경 변수 설정**:
    - `LD_LIBRARY_PATH` 환경 변수를 설정하여 올바른 라이브러리를 로드
	    ```shell
	    export LD_LIBRARY_PATH=/opt/hpcx/ucc/lib:$LD_LIBRARY_PATH
		```
