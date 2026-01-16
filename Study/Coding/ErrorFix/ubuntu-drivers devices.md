---
date: 2024-06-26, 14:22
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
keywords: 
related notes: 
reference: 
author: 
url:
---
# 문제 발생

- `ubuntu-drivers devices` 를 실행시켰을 때 드라이버 리스트가 뜨지 않음

# 원인 분석

- [[ppa]] 가 갱신이 안되어 발생하는 문제

# 해결 방법

```bash
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt-get update
```
