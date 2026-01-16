---
date: 2024-02-22, 16:20
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
reference: 
author: 
url:
  - https://machineindeep.tistory.com/32
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
  File "/workspace/pcdet/datasets/__init__.py", line 8, in <module>
    from .dataset import DatasetTemplate
  File "/workspace/pcdet/datasets/dataset.py", line 9, in <module>
    from .augmentor.data_augmentor import DataAugmentor
  File "/workspace/pcdet/datasets/augmentor/data_augmentor.py", line 7, in <module>
    from . import augmentor_utils, database_sampler
  File "/workspace/pcdet/datasets/augmentor/database_sampler.py", line 6, in <module>
    from skimage import io
  File "/usr/local/lib/python3.8/dist-packages/skimage/__init__.py", line 122, in <module>
    from ._shared import geometry
  File "geometry.pyx", line 1, in init skimage._shared.geometry
ValueError: numpy.ndarray size changed, may indicate binary incompatibility. Expected 88 from C header, got 80 from PyObject
```
# 원인 분석
- NumPy 버전 문제로 추측됨
# 해결 방법
- OpenPCDet의 `requirements.txt`에도 numpy의 버전이 지정되어 있지 않은 것으로 보아 업그레이드를 해도 문제가 없다고 판단하여 업그레이드 진행
```bash
pip3 install --upgrade numpy
pip3 install --upgrade numba
```

