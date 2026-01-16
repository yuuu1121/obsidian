---
date: 2024-09-09
status: Problem Solving
tags:
  - Study/Coding/solution
aliases: 
keywords:
  - apt-get update
  - update
related notes: 
reference: 
author: 
url: 
dg-publish: false
---
# Issue

`sudo apt-get update` 명령어 실행 중 여러 저장소에서 "Temporary failure resolving" 에러 발생. 주로 DNS 문제로 인해 패키지 리스트를 업데이트하지 못하는 상황.

## Root Cause Analysis
1. **DNS 문제**: `Temporary failure resolving` 에러는 시스템이 해당 저장소의 URL을 IP 주소로 변환하는 과정에서 문제가 발생할 때 나타남. 이는 인터넷 연결 문제 또는 잘못된 DNS 설정으로 인한 것일 가능성이 큼.
2. **인터넷 연결**: 네트워크 연결이 끊기거나 불안정할 경우 발생할 수 있음.
3. **네트워크 설정 문제**: VPN, 방화벽 또는 기타 네트워크 설정이 원인일 가능성 있음.
4. **DNS 서버 문제**: 사용 중인 DNS 서버가 응답하지 않거나 문제가 발생했을 수 있음.

## Solution
1. **인터넷 연결 확인**:
   - 인터넷 연결이 제대로 되어 있는지 확인.
   - `ping` 명령어를 사용하여 외부 사이트에 연결 가능한지 테스트.

   ```bash
   ping google.com
   ```

2. **DNS 서버 변경**:
   - 현재 설정된 DNS 서버가 문제가 있을 수 있으므로 Google DNS 또는 Cloudflare DNS로 변경.
   - `/etc/resolv.conf` 파일을 편집하여 DNS 서버를 변경할 수 있음.

   ```bash
   sudo nano /etc/resolv.conf
   ```

   다음 내용을 추가하거나 수정:

   ```
   nameserver 8.8.8.8  # Google DNS
   nameserver 1.1.1.1  # Cloudflare DNS
   ```

   변경 후 저장하고 나와서 다시 `sudo apt-get update` 실행