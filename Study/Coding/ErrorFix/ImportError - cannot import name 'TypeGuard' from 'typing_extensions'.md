---
date: 2024-02-22, 16:23
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://github.com/bokeh/bokeh/issues/12075#issuecomment-1086885374
keywords:
  - OpenPCDet
---
# 문제 발생
- Data Info를 생성하기 위해 `python3 -m pcdet.datasets.waymo.waymo_dataset`을 실행하는 과정에서 문제 발생
```bash
xxx@xxx:/workspace# python3 -m pcdet.datasets.waymo.waymo_dataset --func create_waymo_infos --cfg_file tools/cfgs/dataset_configs/waymo_dataset_multiframe.yaml
Traceback (most recent call last):
  File "/usr/lib/python3.8/runpy.py", line 185, in _run_module_as_main
    mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
  File "/usr/lib/python3.8/runpy.py", line 111, in _get_module_details
    __import__(pkg_name)
  File "/workspace/pcdet/datasets/__init__.py", line 15, in <module>
    from .argo2.argo2_dataset import Argo2Dataset
  File "/workspace/pcdet/datasets/argo2/argo2_dataset.py", line 15, in <module>
    from .argo2_utils.so3 import yaw_to_quat, quat_to_yaw
  File "/workspace/pcdet/datasets/argo2/argo2_utils/so3.py", line 3, in <module>
    import kornia.geometry.conversions as C
  File "/usr/local/lib/python3.8/dist-packages/kornia/__init__.py", line 3, in <module>
    from . import filters
  File "/usr/local/lib/python3.8/dist-packages/kornia/filters/__init__.py", line 3, in <module>
    from .bilateral import BilateralBlur, JointBilateralBlur, bilateral_blur, joint_bilateral_blur
  File "/usr/local/lib/python3.8/dist-packages/kornia/filters/bilateral.py", line 6, in <module>
    from kornia.core.check import KORNIA_CHECK, KORNIA_CHECK_IS_TENSOR, KORNIA_CHECK_SHAPE
  File "/usr/local/lib/python3.8/dist-packages/kornia/core/check.py", line 7, in <module>
    from typing_extensions import TypeGuard
ImportError: cannot import name 'TypeGuard' from 'typing_extensions' (/root/.local/lib/python3.8/site-packages/typing_extensions.py)
```
# 원인 분석
- `typing-extensions`의 버전이 오래되었기 때문이라고 추측
```bash
xxx@xxx:/workspace# pip3 list | grep typing*
typing-extensions           3.7.4.3
```
# 해결 방법
```bash
pip3 install --upgrade typing-extensions
```

