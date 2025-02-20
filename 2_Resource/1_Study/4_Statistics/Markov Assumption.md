---
date: 2024-02-13, 16:21
status: Permanent
tags: Study/Statistics
aliases: 
- Statistics
- Markov assumption
reference: 
author: 
url:
---

- 만약 state $x$에 대해 알고 있다면, 관측치 $z_n$은 $z_1, \cdots, z_{n-1}$과 독립
$$p(x|z_1, \cdots, z_n)={p(z_n|x)p(x|z_1, \cdots, z_{n-1})\over p(z_n|z_1, \cdots, z_{n-1})}=\eta_{1:n}\Pi_{i=1}^np(z_i|x)p(x)$$

[[filter]]