---
title: "MCSPTE1AK144 (S32K144 + DEVKIT-MOTORGD) 모터 제어 키트 세팅 매뉴얼"
kit: "NXP MCSPTE1AK144 — S32K144EVB-Q100 + DEVKIT-MOTORGD + Sunrise 42BLY3A78-24110 PMSM"
tags: [Embedded, MotorControl, S32K144, PMSM, FOC, FreeMASTER, S32DS, GD3000, 트러블슈팅]
date: 2026-09-09
status: 검증 진행 중 (마지막 항목 참고)
---

# MCSPTE1AK144 모터 제어 키트 세팅 매뉴얼

> [!info] 이 노트의 목적
> NXP S32K144 모터 제어 키트를 **아무것도 없는 PC에서 모터가 도는 상태까지** 세팅한 실제 기록이다. 공식 Getting Started 가이드([nxp.com GS-MCSPTE1AK144](https://www.nxp.com/document/guide/s32k144-motor-control-kit-guides:GS-MCSPTE1AK144))의 순서를 따르되, 가이드에 없는 **2026년 시점의 호환성 문제와 하드웨어 함정** 4가지를 해결한 과정을 그대로 남긴다. 다음에 같은 키트를 다시 세팅할 때는 1~5장만 따라가면 되고, 막히면 6장 트러블슈팅에서 증상을 찾으면 된다.

> [!abstract] 한 줄 요약
> 소프트웨어 3개(S32DS 2.2, AMMCLib, FreeMASTER)를 깔고 → 점퍼 2세트(J107, J9/J10/J11)를 맞추고 → 프로젝트를 빌드·플래시하고 → FreeMASTER Variable Watch에서 Clear Faults → Run 하면 돈다. 단, **AMMCLib 최신판(1.1.45)은 S32DS 2.2와 링크가 안 되므로 컴파일러 플래그 2개를 추가**해야 하고, **전원을 켤 때마다 리셋을 눌러야 게이트 드라이버가 살아나는 문제**는 펌웨어 재시도 패치로 해결했다.

---

## 1. 키트 구성과 역할

| 구성품 | 역할 | 비고 |
|:---|:---|:---|
| S32K144EVB-Q100 | MCU 보드. Cortex-M4F, FOC 연산, PWM 생성 | 키트 동봉품은 R165/R167 제거·R166/R168 장착·C16 제거 개조가 되어 있음 (엔코더 신호용, 센서리스에는 무관) |
| DEVKIT-MOTORGD | 전력단. GD3000 게이트 드라이버 + 3상 FET 브리지 + 전류 센싱 | EVB 위에 아두이노 헤더로 결합 |
| Sunrise 42BLY3A78-24110 | 3상 PMSM, 극쌍 2, 정격 5000 rpm, 정격 6 A | 구형 키트는 Linix 45ZWN24-40 |
| 12 V 어댑터, USB 케이블 | 전원, OpenSDA 디버거·시리얼 | DC 입력 허용 8~18 V |

두 보드 사이 신호는 **J1~J6 아두이노 헤더의 안쪽 줄**로만 오간다. 핀 배치 전체는 QSG 5~6쪽에 표로 있고, 이 노트에서 실제로 쓴 핀은 아래 표다.

| 헤더 핀 | MCU 핀 | MOTORGD 신호 | 용도 |
|:---|:---|:---|:---|
| J1-01 | PTA2 | GD_EN | GD3000 출력 인에이블 (High = 켜짐) |
| J1-03 | PTA3 | GD_RST_B | GD3000 리셋 (Low 활성) |
| J1-05 ~ J1-15 | PTB8~11, PTC10~11 (FTM3 CH0~5) | PWMA/B/C HS·LS | 3상 PWM |
| J2-05 ~ J2-11 | PTB5, LPSPI0 | SPI_CS_B, MOSI, MISO, SCLK | GD3000 설정 통신 |
| J4-05, J4-07 | ADC0_SE4, ADC1_SE15 | PHA_I, PHB_I | 2-shunt 상전류 |
| J4-03 | ADC1_SE7 | DCBV | DC 버스 전압 |

---

## 2. 소프트웨어 설치

설치 순서가 중요하다. **S32DS 본체 → Update 2 → AMMCLib → FreeMASTER → 키트 SW** 순서를 권장한다. 키트 SW 설치 중에 AMMCLib 설치 안내가 뜨는데, 이미 깔려 있으면 건너뛴다.

### 2.1 S32 Design Studio for Arm 2.2

> [!warning] 3.x 버전이 아니라 반드시 2.2
> 키트 SW는 S32DS for ARM 2.2 + GCC 6.3.1 기준으로 빌드·검증됐다(`MCSPTE1AK144_ReleaseNotes.txt`). 3.x는 프로젝트 형식이 달라 그대로 열리지 않는다.

1. NXP 로그인 후 다운로드 포털 `https://www.nxp.com/webapp/swlicensing/sso/downloadSoftware.sp?catid=S32DS-IDE-ARM-V2-X` 에서 "S32 Design Studio for ARM 2.2 – Windows/Linux" 설치 파일(`S32DS_ARM_Win32_v2.2_b...exe`, 1 GB 이상)을 받는다. 같은 화면에 **활성화 코드**가 표시되고 메일로도 온다.
2. 관리자 권한으로 실행 → 활성화 코드 입력 → Activate online → 기본 경로 `C:\NXP\S32DS_ARM_v2.2`.
3. **Update 2 적용**: S32DS ARM 페이지에서 `S32DS-IDE-ARM_2.2.2_D2312.zip`을 받아 압축 해제. 이 폴더에는 실행 파일이 없다(Eclipse p2 업데이트 사이트). S32DS 실행 → Help → Install New Software → Add → **Local...** → 압축 푼 폴더 선택 → 항목 전부 체크 → Next → 재시작.

실행 파일 위치: `C:\NXP\S32DS_ARM_v2.2\eclipse\s32ds.exe`

### 2.2 AMMCLib (Automotive Math and Motor Control Library)

`nxp.com/ammclib` → S32K14x용 오브젝트 코드 버전(무료) → 기본 경로 `C:\NXP\AMMCLIB\S32K14x_AMMCLIB_v1.1.45`.

> [!danger] 1.1.45는 S32DS 2.2와 그냥 링크되지 않는다
> 2026-06 배포판 1.1.45는 GCC 10.2(S32DS 3.6.6)로 빌드됐고 LTO 바이트코드가 들어 있어 GCC 6.3 링커가 `lto-wrapper failed`로 죽는다. 해결은 [[#6.1 빌드 에러 Ld error lto-wrapper failed]] 참고. 플래그 2개만 넣으면 된다.

키트 SW 설치 프로그램은 설치 중 프로젝트의 `.cproject`를 스캔해 AMMCLib 경로를 자동으로 최신 버전으로 바꿔 준다. 원래 키트가 검증한 버전은 1.1.33이다.

### 2.3 FreeMASTER

`nxp.com/FreeMASTER` → 3.x 설치 (이 노트는 3.2 기준). 키트 검증 버전은 3.1.4.5인데 3.2도 문제없이 `.pmp`를 연다.

### 2.4 키트 SW (MCSPTE1AK144_SW)

Getting Started 페이지의 다운로드 링크 → `MCSPTE1AK144_SW.exe` → 기본 경로 `C:\NXP\MC_DevKits\MCSPTE1AK144`.

```
C:\NXP\MC_DevKits\MCSPTE1AK144\
├─ sw\
│  ├─ MCSPTE1AK144_PMSM_FOC_2Sh\        ← 이 노트에서 사용 (2-shunt FOC)
│  ├─ MCSPTE1AK144_PMSM_FOC_1Sh\
│  ├─ MCSPTE1AK144_PMSM_FOC_2Sh_FreeRTOS\
│  └─ MCSPTE1AK144_BLDC_6Step\
└─ doc\
   ├─ UserGuides\MCSPTE1AK144QSG.pdf     ← 점퍼표·핀맵·보드 그림
   ├─ Schematic\ (EVB, MOTORGD 회로도)
   └─ ApplicationNotes\ (AN12235 PMSM, AN12435 BLDC)
```

---

## 3. 하드웨어 세팅

### 3.1 점퍼

![[assets/motorgd_jumpers_J9-J11.jpg]]
*DEVKIT-MOTORGD J9/J10/J11. 사진은 거꾸로 찍힌 것. "3" 표시 핀이 노출되고 "1" 쪽 두 핀에 캡이 꽂혀 있으면 1-2 = PMSM.*

| 보드 | 점퍼 | 설정 | 의미 |
|:---|:---|:---|:---|
| MOTORGD | **J9, J10, J11** | **1-2** | PMSM FOC: 3상 전류 센싱을 ADC로. 2-3이면 BLDC용 역기전력 분배기가 ADC에 물려 **정지 상태에서 과전류 폴트**가 뜬다 |
| MOTORGD | J8 | Open (기본) | Hall/Encoder 5 V. Short는 3.3 V. 센서리스에는 무관 |
| EVB | **J107** | **1-2** | MCU를 12 V에서 급전. USB 급전(2-3)으로는 모터가 안 돈다 |
| EVB | J104 | 2-3 (기본) | 리셋 버튼이 MCU로 감. 1-2면 OpenSDA 부트로더 진입 |
| EVB | J108/J109 | Short (기본) | CAN 종단. 무관 |

### 3.2 모터 결선

![[assets/motorgd_phase_terminal.jpg]]
*MOTORGD 모터 단자대 PHA / PHB / PHC / GND. GND 단자는 비워 둔다.*

| 단자 | Sunrise | Linix |
|:---|:---|:---|
| PHA | 노랑 | 흰색 |
| PHB | 초록 | 파랑 |
| PHC | 파랑 | 초록 |

순서가 틀리면 회전 방향만 반대가 되고 기동은 된다.

> [!tip] 나사식 단자대에 페룰 물리는 법
> 나사를 **먼저 반시계로 서너 바퀴 풀어** 클램프를 연 다음 페룰 금속부가 안 보일 때까지 밀어 넣고 조인다. 나사가 조여진 상태에서 밀어 넣으면 클램프 위 빈 공간으로 들어가 겉보기엔 꽂혔는데 접촉이 없다. 조인 뒤 당겨서 확인. 확실히 하려면 전원 끄고 PHA–PHB 저항이 수 Ω(이 모터 2.5 Ω)인지 잰다.

### 3.3 전원과 USB

1. 12 V 어댑터를 **MOTORGD 보드의 전원 단자**에 꽂는다. EVB 배럴 잭이 아니다. DC 전압이 최대 속도를 정한다(8~18 V, 과전압 폴트 18 V).
2. USB를 EVB의 OpenSDA 커넥터에 꽂는다. 장치 관리자에 "OpenSDA - CDC Serial Port (COMn)"이 잡힌다. 이 PC에서는 COM8.
3. 과전류 비교기 트림 포텐셔미터는 가이드상 8~10 A. 이번에는 손대지 않았다.

> [!warning] 전원을 켠 뒤 EVB 리셋 버튼을 한 번 누른다
> 이유는 [[#6.5 Run인데 모터가 안 돌고 전류가 0 — GD3000 초기화 경쟁]] 참고. 펌웨어 패치를 적용하면 안 눌러도 된다.

![[assets/s32k144evb_board_overview.png]]
*S32K144EVB 부품 배치 (QSG 3쪽). 리셋 버튼(SW5)은 OpenSDA USB 커넥터 바로 아래.*

---

## 4. 빌드와 플래시 (S32DS)

### 4.1 프로젝트 임포트

1. S32DS 실행 → File → Import → General → **Existing Projects into Workspace** → Next.
2. Browse로 `C:\NXP\MC_DevKits\MCSPTE1AK144\sw\MCSPTE1AK144_PMSM_FOC_2Sh` 선택.
3. "Copy projects into workspace" 체크(가이드 권장). 이번에는 체크 없이 원본 위치에서 열었고 동작에는 문제없었다. 단, 배치 파일과 소스 수정은 열린 쪽 폴더에서 해야 한다.
4. Finish.

### 4.2 모터 파라미터 선택

기본은 Sunrise. Linix 모터라면 탐색기에서 프로젝트 폴더의 `SetMotor-LINIX_45ZWN24-40.bat`을 한 번 실행한다. 이 배치는 `Sources\Config\PMSM_appconfig.h`와 `FreeMASTER_control\MCAT\param_files\M1_params.txt`를 해당 모터용으로 덮어쓴다. S32DS 안에서는 Run → External Tools에 같은 항목이 있다.

### 4.3 AMMCLib 1.1.45 호환 플래그 (필수)

프로젝트 우클릭 → Properties → C/C++ Build → Settings → Tool Settings 탭.

| 트리 위치 | 입력란 | 추가할 값 |
|:---|:---|:---|
| Standard S32DS C Compiler → Miscellaneous | Other flags | `-fno-short-enums` |
| Standard S32DS C Linker → Miscellaneous | Linker flags | `-fno-use-linker-plugin` |

Configuration이 `Debug_FLASH [ Active ]`인지 확인하고 Apply and Close. 이유는 [[#6.1 빌드 에러 Ld error lto-wrapper failed]].

### 4.4 빌드

프로젝트 우클릭 → Clean → Build Project. Console 마지막에 `Finished building target: MCSPTE1AK144_PMSM_FOC_2Sh.elf`가 나오면 성공. `uses 32-bit enums` 경고가 몇 줄 남는 것은 newlib 관련이라 무해하다.

### 4.5 플래시와 실행

1. Run → **Debug Configurations** (Run Configurations 아님) → GDB PEMicro Interface Debugging → `MCSPTE1AK144_PMSM_FOC_2Sh_Debug_FLASH_PNE` → Debug.
2. main 첫 줄에서 멈추면 **Resume (F8)**. LED 녹색 점등 = READY.
3. 툴바 **Disconnect**(빨간 N). 이걸 안 하면 FreeMASTER가 COM 포트를 못 연다.

> [!bug] 툴바의 초록 동그라미(Run)를 누르면 안 된다
> `Cannot run program "...elf": Launching failed` 에러가 뜬다. ARM용 ELF를 PC에서 실행하려는 것. 항상 벌레 아이콘(Debug) 또는 Debug Configurations를 쓴다.

---

## 5. FreeMASTER로 모터 구동

### 5.1 연결

1. `C:\NXP\MC_DevKits\MCSPTE1AK144\sw\MCSPTE1AK144_PMSM_FOC_2Sh\FreeMASTER_control\S32K_PMSM_Sensorless.pmp` 더블클릭.
2. Project → Options → Comm → Port **COM8**, Speed **115200**.
3. Go (Ctrl+G). 하단 상태줄 `RS232; port=COM8; speed=115200`.

### 5.2 조작 = Variable Watch 표

별도의 ON 버튼은 없다. 화면 아래 Variable Watch 표의 값 칸을 **더블클릭 → 드롭다운 선택 → Enter** 로 조작한다. Enter를 눌러야 보드로 전송된다.

| 행 | 값 | 조작 |
|:---|:---|:---|
| Clear Faults | `--` → **Clear** | State가 Fault면 먼저 이걸로 지운다 |
| Speed Required | 500 | 처음은 낮게 |
| On/Off | Stop → **Run** | 시작. Stop으로 정지 |
| State | Ready → Calib → Align → Run | 진행 확인 |
| Position Mode | force → tracking → sensorless | 자동 전환 (Mode=automatic) |

보드 버튼으로도 된다: SW2/SW3 시작·속도, 동시 누름 = Clear Faults.

### 5.3 LED 상태

| LED | 상태 |
|:---|:---|
| 녹색 점등 | READY / INIT |
| 녹색 점멸 | CALIB / ALIGN |
| 파란 점멸 | RUN |
| 빨간 점멸 | FAULT |

### 5.4 속도 한계

| 한계 | 값 |
|:---|:---|
| 펌웨어 클램프 `N_MAX` | 5500 rpm |
| 모터 정격 | 5000 rpm |
| 12 V 버스 무부하 계산치 | 약 5000 rpm (Ke 0.005872 V·s/rad, 극쌍 2, 전압 이용률 0.9) |

1000 → 2000 → … 단계적으로 올리며 Control → Speed 화면에서 추정 속도가 따라오는지 본다. 음수 = 역회전.

### 5.5 유용한 화면 (왼쪽 Project Tree)

- **Faults & Trips**: 어떤 폴트인지. 위쪽 행은 래치, `- Trip` 행은 지금 이 순간 조건 충족 여부. Trip이 1이면 Clear해도 바로 다시 뜬다.
- **Sensors/Actuators → Currents → iABC**: 3상 전류 파형. Run 직후 4 A급 파형이 있어야 정상.
- **Voltage → Udc / uDQReq / PWM**: 버스 전압, 전압 명령, 듀티.
- 임의 변수 추가: Variable Watch 빈 줄 우클릭 → Create New Watched Variable → 심볼 선택. `tppDrvConfig.deviceConfig.opMode`가 **3**이어야 게이트 드라이버가 켜진 것(2 = 초기화 실패).

---

## 6. 트러블슈팅 (실제로 겪은 순서)

### 6.1 빌드 에러 `Ld error: lto-wrapper failed`

**증상**: Problems 창에 `Ld error: lto-wrapper failed`, `make: *** [makefile:62: ...elf] Error 1`. Console에는 `unrecognized argument in option '-march=armv7e-m+fp'`.

**원인**: AMMCLib 1.1.45의 `lib/s32ds_arm32/S32K14x_AMMCLIB.a`가 GCC 10.2.0으로 빌드된 LTO 오브젝트(1353개 LTO 섹션). S32DS 2.2의 GCC 6.3.1 링커 플러그인이 이를 읽다가 GCC 10 문법 옵션을 만나 실패. 키트가 검증한 1.1.33은 이런 문제가 없었으나, 키트 SW 설치 프로그램이 프로젝트 참조를 자동으로 1.1.45로 바꿔 놓는다.

**해결**: 4.3의 플래그 2개.

- `-fno-use-linker-plugin`: 링커가 LTO 섹션을 무시하고 같은 아카이브에 들어 있는 일반 코드(fat object)를 쓰게 한다. 이것만으로 링크는 통과한다.
- `-fno-short-enums`: **반드시 같이 넣어야 한다.** 라이브러리는 enum을 4바이트(`Tag_ABI_enum_size: int`)로 빌드됐고 프로젝트 기본은 1바이트(small)다. AMMCLib의 `tBool`이 enum이고 PI 컨트롤러·BEMF 옵저버 구조체 멤버로 쓰이므로, 맞추지 않으면 링크는 되지만 구조체 레이아웃이 어긋나 조용히 오동작한다. 적용 후 프로젝트 오브젝트 66개 전부 int로 확인했다.

**대안**: AMMCLib 1.1.33을 구해 설치하고 `.cproject`의 경로를 되돌리는 것. 다운로드 포털 "Previous versions"에 있는지는 확인 못 함.

### 6.2 정지 상태에서 OverPhaseA/BCurrent 폴트

![[assets/freemaster_faults_overcurrent.png]]

**증상**: 전원 켜자마자 State=Fault. Faults & Trips에서 OverPhaseACurrent, OverPhaseBCurrent와 그 Trip이 1. C상은 0(2-shunt는 C상을 계산하므로 단서 아님). Clear해도 즉시 재발.

**원인**: MOTORGD J9/J10/J11이 2-3(BLDC)에 있었음. 이 위치는 역기전력 전압 분배기를 전류 ADC 입력에 연결해서, 정지 상태인데도 펌웨어가 큰 전류로 읽는다(`I_PH_OVER` 7 A 초과).

**해결**: 세 점퍼를 1-2로. 전원 껐다 켜고 Clear Faults.

### 6.3 전원 켤 때마다 UnderDCBusVoltage 래치

**증상**: 래치 값만 1, Trip은 0.

**원인**: 12 V가 올라오는 동안 MCU가 먼저 부팅해 `U_DCB_UNDER` 8 V 미만을 한 번 봄. 정상 동작.

**해결**: Clear Faults 한 번. 이 현상 자체가 6.5의 힌트였다.

### 6.4 Run 상태(파란 LED)인데 모터가 안 돎 — 1차 진단

증상만으로는 원인이 여러 갈래라, 아래 순서로 갈랐다. 다음에도 같은 순서로 보면 된다.

| 확인 | 결과 | 배제된 것 |
|:---|:---|:---|
| 모터 손으로 돌려 봄 | 완전히 자유로움, 웅웅 없음 | 권선에 전류 없음 확정 |
| iABC | 0 A | 위와 동일 |
| Udc | 12.1 V 안정 | 전원·인버터 급전 |
| uDQReq | 7 V 포화 | 펌웨어 전류 제어기는 전압을 최대로 밀고 있음 |
| PWM 듀티 | 0.75~0.92 변동 | MCU PWM 생성 정상 |
| PHA–PHB 저항 (전원 OFF) | 2.5 Ω | 모터·결선 정상 |
| PHA/B/C–GND 전압 (Run) | 0.3 V | **FET 브리지가 스위칭 안 함** |
| J1 안쪽 줄 8핀 전압 | PWM 6핀 0~5 V 진동, 끝 두 핀 4.5 V / **0 V** | MCU→헤더 신호 정상, **GD_EN이 Low** |
| `tppDrvConfig.deviceConfig.opMode` | **2** (Initialization) | GD3000 초기화 실패 확정 |

중간에 EVB 개조 저항(R165~R168)을 의심했으나 회로도상 PTD10/PTD11 엔코더 신호용이라 무관했고, FTM 하드웨어 폴트 입력도 비활성이라 배제됐다.

### 6.5 Run인데 모터가 안 돌고 전류가 0 — GD3000 초기화 경쟁

![[assets/s32ds_debug_tpp276.png]]
*디버거로 리셋해 실행하면 tpp.c:276(네 검증을 모두 통과한 뒤의 줄)에 도달한다 = 디버거에서는 초기화 성공.*

**메커니즘** (`Sources/GD3000/tpp/tpp.c`, `TPP_SetOperationalMode`):

1. RST_B를 High로 올림 (→ J1-03 4.5 V로 관측)
2. SPI로 인터럽트 마스크 → 데드타임 캘리브레이션 → 모드 레지스터 → 인터럽트 클리어를 쓰고 **읽어서 검증**
3. 하나라도 실패하면 즉시 `return kStatus_TPP_InternalError` → **EN을 올리는 코드에 도달하지 못함** (→ J1-01 0 V)
4. 호출부 `GD3000_Init()`은 반환값을 확인하지 않아 재시도 없음. 펌웨어는 PWM을 만들며 정상인 척 돌고, GD3000 상태 레지스터는 초기값 0 그대로.

**왜 실패하나**: 냉간 전원 투입 시 MCU(5 V 레귤레이터 경유)가 수십 ms에 부팅해 곧바로 초기화를 시도하는데, GD3000은 회로도 주석대로 **VPWR > 8 V가 되어야 내부 레귤레이터·차지펌프가 켜진다**. 12 V가 올라오는 동안 칩이 아직 안 살아 있어 SPI 응답이 없다. 디버거 리셋(전원 안정 후 MCU만 리셋)이나 리셋 버튼에서는 성공한다.

**임시 해결**: 전원 → 2~3초 → EVB 리셋 버튼(SW5, J104=2-3 필요).

**영구 해결 (적용함)**: `Sources/GD3000/gd3000_init.c`의 `TPP_Init` 호출을 재시도 루프로 교체. 원본은 `gd3000_init.c.orig`.

```c
/* Retry GD3000 initialization: at a cold 12 V power-up the MCU boots before the
 * GD3000 supply (VPWR > 8 V) is ready, so the first SPI configuration fails and the
 * driver leaves EN low with no retry. Pulse RST_B and try again until it succeeds.
 * simplified: fixed 50 x 100 ms (5 s) budget; if still failing the app runs as before
 * (motor will not start) - the FreeMASTER opMode variable shows 2 instead of 3. */
{
    uint8_t retry;
    for (retry = 0U; retry < 50U; retry++)
    {
        if (TPP_Init(&tppDrvConfig, tppModeEnable) == kStatus_Success)
        {
            break;
        }
        /* Hold GD3000 in reset while its supply settles, then retry. */
        GPIO_AML_ClearOutput(tppDrvConfig.rstPinInstance, tppDrvConfig.rstPinIndex);
        WAIT_AML_WaitMs(100U);
    }
}
```

"DC 버스 전압 8 V 대기" 방식을 쓰지 않은 이유: 이 시점에는 ADC/PDB 측정 파이프라인이 아직 돌지 않아 전압을 읽을 수 없다. 재시도는 칩 응답을 직접 확인하므로 전원 상승 속도와 무관하다.

> [!todo] 검증 상태 (2026-09-09 16:30 기준)
> 패치는 빌드·링크까지 확인했고 보드 검증은 아직이다. 검증 절차: 12 V·USB 모두 뽑기 → 12 V → USB 순으로 꽂기 → **리셋 버튼 누르지 않고** FreeMASTER Go → `opMode`가 3인지 → Clear Faults → Run 500 rpm → 회전 확인. 두세 번 반복해 매번 3이면 확정. 결과를 여기에 적을 것.

### 6.6 FreeMASTER `Could not open the communication port (0x80004005)`

디버거가 붙어 있거나 다른 FreeMASTER 창이 포트를 잡고 있음. S32DS에서 Terminate(빨간 네모) → FreeMASTER 재실행 → Comm 탭 포트 재지정 → Go. 안 되면 USB 재삽입.

### 6.7 S32DS `Cannot run program "...elf": Launching failed`

Run(초록 동그라미)으로 실행한 것. Debug Configurations의 `_PNE` 항목으로 Debug. Run Configurations에 자동 생성된 C/C++ Application 항목은 지워 두면 헷갈리지 않는다.

### 6.8 기타 IDE 팁

- 파일 트리가 안 보이면 Window → Show View → Project Explorer, 또는 **Ctrl+Shift+R**로 파일명 검색. 줄 이동 Ctrl+L.
- 디버그 중 변수 값: Window → Show View → Variables, 또는 코드 위 마우스 오버.
- `Debug_FLASH` 폴더는 빌드 산출물만 있어 지워져도 다음 Build에서 재생성된다.
- 디버거와 FreeMASTER는 같은 OpenSDA를 쓰므로 **동시에 쓰지 않는다**. 디버거 → Disconnect → FreeMASTER Go 순서.

---

## 7. 진단 기법 메모 (다음에 재사용)

- **소프트웨어 상태 읽기**: FreeMASTER Variable Watch에 아무 전역 변수나 추가할 수 있다. 드라이버 상태(`tppDrvConfig.deviceConfig.opMode`, `statusRegister[0..3]`)를 보면 SPI 장치가 살았는지 바로 안다.
- **어느 줄에서 실패했는지**: S32DS 디버그로 실패 return 줄들에 브레이크포인트를 걸고 F8. 멈춘 줄 = 실패 단계, 그 직전 `error` = 실제 코드 (`MAKE_STATUS(group*100+code)`, TPP 그룹 115 → 11503 데드타임 캘리브레이션 실패, 11506 읽기 검증 불일치).
- **멀티미터 3종 세트**: (전원 OFF) 상간 저항 → (Run) 상 단자–GND DC 전압 → (Run) 헤더 핀 전압. 이 세 값으로 "모터 / FET 브리지 / MCU 신호" 중 어디가 끊겼는지 갈린다.
- **회로도 읽기**: `doc\Schematic\*.pdf`는 텍스트 추출이 불완전하므로 `pdftoppm -r 200`으로 PNG로 뽑아 확대해서 본다. 헤더 핀 번호 대조는 QSG 5~6쪽 표가 더 빠르다.
- **키트 SW의 컴파일 환경**: `MCSPTE1AK144_ReleaseNotes.txt`에 검증된 IDE·SDK·FreeMASTER·AMMCLib 버전이 적혀 있다. 최신 버전을 그냥 깔면 이번처럼 어긋난다.

---

## 8. 경로 모음

| 항목 | 경로 |
|:---|:---|
| S32DS | `C:\NXP\S32DS_ARM_v2.2\eclipse\s32ds.exe` |
| 툴체인 | `C:\NXP\S32DS_ARM_v2.2\S32DS\build_tools\gcc_v6.3\gcc-6.3-arm32-eabi\bin` |
| AMMCLib | `C:\NXP\AMMCLIB\S32K14x_AMMCLIB_v1.1.45` |
| 프로젝트 | `C:\NXP\MC_DevKits\MCSPTE1AK144\sw\MCSPTE1AK144_PMSM_FOC_2Sh` |
| FreeMASTER 프로젝트 | `...\FreeMASTER_control\S32K_PMSM_Sensorless.pmp` |
| 모터 파라미터 | `...\Sources\Config\PMSM_appconfig.h` |
| GD3000 드라이버 | `...\Sources\GD3000\tpp\tpp.c`, `...\Sources\GD3000\gd3000_init.c` |
| 워크스페이스 | `C:\Users\user\workspaceS32DS.ARM.2.2` |
| QSG | `C:\NXP\MC_DevKits\MCSPTE1AK144\doc\UserGuides\MCSPTE1AK144QSG.pdf` |
| 공식 가이드 | https://www.nxp.com/document/guide/s32k144-motor-control-kit-guides:GS-MCSPTE1AK144 |
