---
date: 2024-02-22, 16:25
status: Problem Solving
tags:
  - Study/Coding/solution
aliases:
  - korina 버전 문제
reference: 
author: 
url:
  - https://github.com/open-mmlab/OpenPCDet/issues/1487#issuecomment-1763875867
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
  File "/workspace/pcdet/datasets/argo2/argo2_utils/so3.py", line 10, in <module>
    def quat_to_mat(quat_wxyz: Tensor) -> Tensor:
  File "/usr/local/lib/python3.8/dist-packages/torch/jit/_script.py", line 1318, in script
    fn = torch._C._jit_script_compile(
  File "/usr/local/lib/python3.8/dist-packages/torch/jit/_recursive.py", line 841, in try_compile_fn
    return torch.jit.script(fn, _rcb=rcb)
  File "/usr/local/lib/python3.8/dist-packages/torch/jit/_script.py", line 1318, in script
    fn = torch._C._jit_script_compile(
RuntimeError:
cannot statically infer the expected size of a list in this context:
  File "/usr/local/lib/python3.8/dist-packages/kornia/geometry/conversions.py", line 556

    # this slightly awkward construction of the output shape is to satisfy torchscript
    output_shape = [*list(quaternion.shape[:-1]), 3, 3]
                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~ <--- HERE
    matrix = matrix_flat.reshape(output_shape)
'quaternion_to_rotation_matrix' is being compiled since it was called from 'quat_to_mat'
  File "/workspace/pcdet/datasets/argo2/argo2_utils/so3.py", line 19
        (...,3,3) 3D rotation matrices.
    """
    return C.quaternion_to_rotation_matrix(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        quat_wxyz, order=C.QuaternionCoeffOrder.WXYZ
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ <--- HERE
    )
```
# 원인 분석
- `korina` 버전 문제로 추측됨
```bash
xxx@xxx:/workspace# pip3 list | grep kornia
kornia                      0.7.1
```
# 해결 방법
```bash
pip3 install korina==0.6.5
```

