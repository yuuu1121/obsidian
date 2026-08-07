---
title: "수상선(USV) 3대 Koopman 다중 제어 — 리딩 리스트"
tags: [리딩리스트, Koopman, USV, 수상선, 다중로봇, 최적제어, 시뮬레이션]
status: 조사중
created: 2026-08-04
related: "[[Koopman 다중로봇 최적제어 Part1 - 개념과 정식화]]"
---

# 수상선(USV) 3대 Koopman 다중 제어 — 리딩 리스트

> [!abstract] 목적
> [[Koopman 다중로봇 최적제어 Part1 - 개념과 정식화|Zhao & Tao의 방법]](**게임이론 utility → Koopman → 선형계획법(LP) → 온라인 적응**)을 **수상선(USV) 3대**로 확장하기 위한 선행 연구 모음. 최종 목표는 실제 USV 하드웨어 실험이며, 시뮬레이션(Isaac Lab / Stonefish, ROS2) 검증을 먼저 거친다.

> [!note] 큰 그림
> 기반 논문 노선에 가장 가까운 건 **①의 Stackelberg·Distributed-Switching-Koopman** 두 편. 나머지 USV 논문은 대부분 **Koopman-MPC** 또는 **NMPC/RL** 계열이라, "왜 우리는 LP 환원을 쓰나"의 차별점을 잡는 비교군으로 유용하다. USV는 점질량이 아니라 **3자유도 저구동(Fossen)** 이므로 ①의 3-DOF·C3D가 동역학 다리를 놓는다.

읽음 표시: ⬜ 안 읽음 · 🔲 훑어봄 · ✅ 정독 · ⭐ 핵심

---

## ① 핵심 방법론 — Koopman + 다중로봇/USV 제어

| 상태  | 논문                                                                                                                             | 핵심                                                   | 메모                                    |
| :-: | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------- |
|  ✅  | [Stackelberg Game-Theoretic Trajectory Guidance for Multi-Robot Systems with Koopman](https://arxiv.org/pdf/2309.16098)        | 리더-팔로워 Stackelberg 게임 + Koopman로 팔로워 반응 학습. 계획시간 절반 | **1순위** · 정독완료 → [[Stackelberg-Koopman 리더-팔로워 궤적 유도\|리뷰]] |
|  ⬜  | [Distributed Switching MPC Meets Koopman for Dynamic Obstacle Avoidance](https://arxiv.org/abs/2511.17186)                     | 분산+다중차량+Koopman+충돌회피 (2025)                          | Part 2 분산식 확장                         |
|  ⬜  | [C3D: Cascade Control + Deep Koopman Learning for ASV](https://arxiv.org/pdf/2403.05972)                                       | Koopman USV 전역선형화+LQR, 실제 실험(station keeping 13.9%↑) | USV 도메인                               |
|  ⬜  | [OM-Koop: Online Memorable Koopman for Marine Robots](https://www.researchgate.net/publication/394462264)                      | 온라인 Koopman 학습 (2025)                                | [[재귀 최소제곱법과 공분산 리셋\|RLS 온라인 추정]]의 해양판 |
|  ⬜  | [Enhanced Koopman robust control for 3-DOF AUV](https://www.sciencedirect.com/science/article/abs/pii/S0029801824015658)       | 3자유도(surge·sway·yaw) 해양 Koopman (Ocean Eng, 2024)    | USV 동역학 근접                            |
|  ⬜  | [Trajectory tracking of work-class ROVs using KORMPC](https://www.sciencedirect.com/science/article/abs/pii/S0029801825024849) | Koopman robust MPC, 튜브 MPC로 보수성↓ (2025)              | Koopman-MPC 비교군                       |

## ② 다중 USV 조정·편대 (도메인 정식화·비교군)

| 상태 | 논문 | 핵심 | 메모 |
|:---:|---|---|---|
| ⬜ | [Coordinated Control of Multiple ASVs: Systematic Review](https://arxiv.org/html/2502.10080v1) | 다중 ASV 조정 전체 지형도 (2025) | **먼저 읽을 서베이** |
| ⬜ | [Safety-Certified Distributed Formation Control of Networked ASVs (CLF+CBF)](https://link.springer.com/article/10.1007/s11424-025-4494-8) | 제어Lyapunov+장벽함수 안전보장 분산 편대 | 안전보장 관점 |
| ⬜ | [Dual-Layer MPC Multi-Vessel Formation, collision-free](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/cth2.70029) | 2계층 MPC 편대+충돌회피 (IET, 2025) | 계층 구조 참고 |
| ⬜ | [Distributed formation control of underactuated UMVs (NMPC)](https://www.sciencedirect.com/science/article/abs/pii/S0029801824026106) | 저구동 다중선박 분산 NMPC+장애물회피 (2024) | 저구동 제약 |
| ⬜ | [Hybrid IAPF + MPC for underactuated multi-USV formation](https://doi.org/10.3390/jmse13081436) | 개선 인공전위장+MPC 다중 USV 회피 (JMSE, 2025) | 회피 비교군 |

## ③ 시뮬레이션 플랫폼 (Isaac Lab / Stonefish 계획 직결)

| 상태 | 자료 | 핵심 | 메모 |
|:---:|---|---|---|
| ⬜ | [RoboRAN: RL Framework for Autonomous Navigation](https://arxiv.org/html/2505.14526v2) | Isaac Lab USV sim-to-real, 정책을 실제 USV에 배포하는 최초 오픈소스 API | **하드웨어 이식 핵심** |
| ⬜ | [Stonefish: Open-Source Marine Robotics Simulator (IEEE)](https://ieeexplore.ieee.org/document/8867434/) | 실지오메트리 유체동역학 시뮬레이터 | **ROS1·ROS2 호환** (현 ROS1 PC 가능) |
| ⬜ | [MarineGym: High-Fidelity RL Sim for UUVs (Isaac Sim)](https://arxiv.org/html/2410.14117) | Isaac Sim 기반, GPU로 실시간 대비 1만 배 가속 | Isaac 계열 참고 |
| ⬜ | [Underwater Robotic Simulators Review](https://www.alphaxiv.org/overview/2504.06245v1) | 해양 시뮬레이터 비교 리뷰 (2025) | 플랫폼 선정 참고 |
| ⬜ | [DRL Framework for Reducing Sim-to-Real Gap in ASV Navigation](https://arxiv.org/pdf/2407.08263) | ASV sim-to-real 격차 축소 방법론 | 이식 격차 대비 |

---

## 다음 액션 (설계는 보류 중)

- [ ] ①의 Stackelberg (arXiv:2309.16098) 정독 → 기반 논문과 방법론 차이 정리
- [ ] ②의 서베이 (arXiv:2502.10080) 훑어 다중 ASV 지형도 파악
- [ ] USV 동역학(Fossen 3-DOF, 저구동) vs 기반 논문 점질량 모델 간극 노트화
- [ ] ROS2 환경 갖춰지면 `/superpowers:brainstorming` 재개 → 시뮬 설계

관련: [[Koopman 다중로봇 최적제어 Part1 - 개념과 정식화]] · [[Koopman 다중로봇 최적제어 Part2 - 시뮬레이션과 평가]] · [[개념 노트]]
