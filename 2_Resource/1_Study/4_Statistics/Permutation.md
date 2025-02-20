---
date: 2024-05-03, 21:56
status: Permanent
tags:
  - Study/Statistics
aliases: 
keywords:
  - 경우의 수
  - 순열
  - Circular permutation
  - Group permutation
  - Rectangular permutation
related notes:
  - "[[Stirling's Formula]]"
reference: 
author: 
url: 
---
# 순열 (Permutation)
![[Pasted image 20240506160344.png]]

- <mark class="hltr-red">순서가 부여된 임의의 집합을 중복 없이 나열하는 모든 경우의 수</mark>
  서로 다른 $n$ 개에서 $r$ 개를 택하여 일렬로 나열할 때 첫 번째 자리에 올 수 있는 경우는 $n$ 가지이며, 두 번째 자리에는 첫 번째 자리에서 선택된 1개를 제외한 $(n-1)$ 가지

> $$_nP_r={n!\over (n-r)!}$$

---
## 그룹 순열 (Group Permutation)
- <mark class="hltr-red">중복된 것이 있는 임의의 집합을 나열하는 모든 경우의 수</mark>
  $n$ 개의 집합 중 <mark class="hltr-green">$m$ 개의 요소가 서로 중복일 때,</mark> 중복 된 요소가 서로 다르다고 가정하면 가능한 경우의 수는 $n!$ 이며, 그 중 중복된 경우는 $m!$ 가지<br>
  
>   $${n!\over m!}$$
   
<br>

  만약 $n$ 개의 집합 중 ==중복된 요소로 이루어진 집합이  $n_1, n_2, \cdots n_k$ 개 있을 경우==<br>
  
  >$${n!\over n_1!\times n_2!\times \cdots \times n_k!}$$

---
## 원순열 (Circular Permutation)
![[drawing240506_0.excalidraw]]

- <mark class="hltr-red">순서가 부여된 임의의 집합을 중복없이 원형으로 나열하는 모든 경우의 수</mark>
  <mark class="hltr-green">원형으로 나열하면 회전하여 일치하는 것을 모두 같은 것으로 보기 때문에 한 가지 경우가 됨</mark><br>
  
>   $${n!\over n}=(n-1)!$$

---
## 직사각 순열 (Rectangular Permutation)
![[drawing240506.excalidraw]]

- <mark class="hltr-red">순서가 부여된 임의의 집합을 중복없이 직사각형으로 나열하는 모든 경우의 수</mark>
  원형으로 나열 했을 때의 경우의 수에서 직사각형 두 변의 길이만큼 곱함<br>
  
>   $${6!\over 6}\times 3$$

