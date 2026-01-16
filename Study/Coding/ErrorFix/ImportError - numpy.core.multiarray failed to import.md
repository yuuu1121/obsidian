---
date: 2024-02-22, 16:15
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://github.com/open-mmlab/OpenPCDet/issues/867#issuecomment-1075166761
keywords:
  - OpenPCDet
---
# 문제 발생
- Data Info를 생성하기 위해 `python3 -m pcdet.datasets.waymo.waymo_dataset`을 실행하는 과정에서 문제 발생
```bash
xxx@xxx:/workspace# python3 -m pcdet.datasets.waymo.waymo_dataset --func create_waymo_infos --cfg_file tools/cfgs/dataset_configs/waymo_dataset_multiframe.yaml
RuntimeError: module compiled against API version 0x10 but this version of numpy is 0xd . Check the section C-API incompatibility at the Troubleshooting ImportError section at https://numpy.org/devdocs/user/troubleshooting-importerror.html#c-api-incompatibility for indications on how to solve this problem .
Traceback (most recent call last):
  File "/usr/lib/python3.8/runpy.py", line 185, in _run_module_as_main
    mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
  File "/usr/lib/python3.8/runpy.py", line 111, in _get_module_details
    __import__(pkg_name)
  File "/workspace/pcdet/datasets/__init__.py", line 6, in <module>
    from pcdet.utils import common_utils
  File "/workspace/pcdet/utils/common_utils.py", line 7, in <module>
    import SharedArray
ImportError: numpy.core.multiarray failed to import
```
# 원인 분석
- SharedArray의 버전 문제로 추측됨
# 해결 방법
- SharedArray 버전 다운그레이드
```bash
pip3 install sharedarray==3.2.1
```


