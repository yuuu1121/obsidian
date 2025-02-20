---
date: 2024-05-06
status: Permanent
tags:
  - Study/Statistics
aliases: 
keywords:
  - 경우의 수
  - 조합
related notes: 
reference: 
author: 
url:
---
# 조합 (Combination)
- <mark class="hltr-red">$n$ 개의 요소 중 $r$ 개를 선택하여 순서 상관 없이 나열하는 모든 경우의 수</mark>
  순서가 부여된 $n$ 개의 요소 중 $r$ 개를 선택하여 나열하는 모든 경우의 수 ($_nP_r$, [[Permutation]])에서 <mark class="hltr-green">순서 상관 없이 나열하므로, $r$ 개를 나열하는 $_rP_r=r!$ 를 하나의 경우로 고려</mark><br>
  
>   $$_nC_r={_nP_r\over r!}={n!\over(n-r)!\cdot r!}={n \choose r}$$


---
## 그룹 조합 (Group Combination)
- 각각 $n, m$ 개의 요소로 이루어진 집합에서 $r$ 개를 선택하여 순서 상관 없이 나열하는 모든 경우의 수

> $${n+m\choose r}=\sum_{k=0}^r{n\choose k}{m\choose r-k}$$

<br>

| **Boys** | **Girls** |       **Combinations**        |
| :------: | :-------: | :---------------------------: |
|    0     |     r     | ${n \choose 0}{m \choose r}$  |
|    1     |    r-1    | ${n \choose 1}{m\choose r-1}$ |
| $\vdots$ | $\vdots$  |           $\vdots$            |
|    r     |     0     |  ${n\choose r}{m\choose 0}$   |

