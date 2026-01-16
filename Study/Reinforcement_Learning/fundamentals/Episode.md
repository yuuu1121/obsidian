---
date: 2025-01-27
tags:
  - Concepts/ReinforcementLearning/Fundamentals
aliases:
  - 에피소드
  - Episodic Tasks
  - Terminal State
keywords:
  - Episode
  - Terminal State
  - Episodic Tasks
  - Continuing Tasks
related notes:
  - "[[Reward]]"
  - "[[Rollout]]"
  - "[[Value Function]]"
reference:
  - David Silver's RL Course
author: David Silver
url: https://www.youtube.com/playlist?list=PLpRS2w0xWHTcTZyyX8LMmtbcMXpd3s4TU
---

# Episode

```ad-note
title: Summary
collapse: true

- ==Episode: 시작 상태에서 종료 상태까지의 완전한 경험 시퀀스==
- ==Terminal State 도달 시 에피소드 종료==
- ==Episodic Tasks vs Continuing Tasks로 강화학습 문제 분류==
- ==Task 유형에 따라 할인율과 학습 알고리즘 선택 결정==
- ==에피소드 길이는 학습 효율성과 수렴에 직접적 영향==
```

## Definition

- ==시작 상태에서 종료 상태까지의 하나의 완전한 경험 시퀀스==

$$S_0, A_0, R_1, S_1, A_1, R_2, \ldots, S_{T-1}, A_{T-1}, R_T, S_T$$

- $S_T$: Terminal state (종료 상태)
- $T$: Episode 길이 (가변적)
- 각 에피소드는 독립적 - 이전 에피소드가 다음에 영향 없음

<br/>

## Terminal State

==에피소드가 끝나는 특별한 상태==

- **Absorbing State**: 한 번 도달하면 자기 자신으로만 전이 ($p(s_T|s_T, a) = 1$)
- 보상은 보통 0 또는 특별한 종료 보상

**종료 조건:**
- 목표 달성 (목적지 도달, 게임 승리)
- 실패 상태 (게임 오버)
- 시간 제한 (최대 스텝 도달)

<br/>

## Episodic vs Continuing Tasks

| 구분 | Episodic Tasks | Continuing Tasks |
|:---|:---|:---|
| **정의** | 자연스러운 종료 존재 | 끝없이 계속됨 |
| **Terminal State** | 있음 | 없음 |
| **$\gamma$** | $\gamma = 1$ 가능 | ==$\gamma < 1$ 필수== (수렴 보장) |
| **Return** | $\sum_{k=0}^{T} \gamma^k r_{t+k+1}$ (유한) | $\sum_{k=0}^{\infty} \gamma^k r_{t+k+1}$ (무한) |
| **학습 방법** | Monte Carlo 가능 | TD 방법 필수 |

<br/>

## Episodic to Continuing Conversion

==Episodic task를 Continuing task로 변환 가능==

**방법:**
1. Terminal State를 Absorbing State로 처리 → 영원히 머무름
2. Terminal State를 일반 상태로 처리 → 보상 설계로 머무르게 유도
	→ 무한 trajectory이므로 ==$\gamma < 1$ 필수== (발산 방지)

<br/>

## Episode Length

에피소드 길이가 ==정책/가치 추정에 미치는 영향== (특히 [[Monte Carlo Methods]]에서 중요)

### Minimum Episode Length

각 상태에서 목표 도달에 ==최소 step 수==가 존재:

$$\text{Episode length} \geq \text{(시작 상태에서 target까지 최소 step 수)}$$

- 조건 불충족 시 return = 0 → ==value 추정 불가능==
- 조건 충족 시 ==유한 길이로 최적 정책 도출 가능== (무한 에피소드 불필요)

<br/>

### Spatial Value Pattern

에피소드 길이 증가에 따라 ==target에 가까운 상태부터 nonzero value== 획득:
1. **짧은 에피소드**: target 근처 상태만 학습 가능
2. **적절한 에피소드**: 모든 상태에서 target 도달 가능
3. **긴 에피소드**: 최적 value 수렴에 기여

<br/>

### Sparse Reward Problem

==목표 도달 전까지 양의 보상이 없는 설정==에서의 문제:
- 긴 에피소드 필요 → 목표 도달까지 탐색해야 양의 보상 획득
- 상태 공간이 크면 목표 도달 확률 낮음 → ==학습 효율 저하==

**해결책 - Reward Shaping**:
- 목표 근처에서 작은 양의 보상 부여 → ==목표 주변에 "attractive field"== 형성
- 더 짧은 에피소드로도 학습 가능

```ad-example
title: Example - 5×5 Grid World Episode Length
collapse: true

![[Pasted image 20260105165043.png|700]]

**설정**: 5×5 Grid, $r_{\text{target}} = 1$, $\gamma = 0.9$

| 에피소드 길이 | Value > 0인 상태 범위 | 결과 |
|:---|:---|:---|
| 1 | 목표에서 1칸 이내 | 대부분 value = 0 |
| 5 | 목표에서 5칸 이내 | 일부 상태만 정확 |
| ==15== | ==전체== | ==모든 상태에서 목표 도달 가능== |
| 100 | 전체 | 최적 정책 + 최적 value 수렴 |

→ ==최소 에피소드 길이 = 가장 먼 상태에서 목표까지 최소 step 수==
```

<br/>

## Related Concepts

- [[Reward]]: Episode 동안 누적되는 보상
- [[Reward#Discount Factor|Discount Factor]]: Continuing task에서 수렴 보장
- [[Rollout]]: Episode 또는 그 일부인 trajectory
- [[Value Function]]: Task 유형에 따라 정의 차이
- [[Monte Carlo Methods]]: Episodic tasks에서 사용
- [[Temporal Difference Learning]]: Continuing tasks에서 필수
