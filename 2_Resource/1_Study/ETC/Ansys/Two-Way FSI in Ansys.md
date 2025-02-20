---
date: 2024-09-04
status: Permanent
tags: 
aliases: 
keywords:
  - Ansys
  - FSI
  - One-way FSI
  - Fluent
  - Static Structural
reference: "[[FSI)](Fluid Solid Interaction Analysis (FSI|Fluid Solid Interaction Analysis (FSI)]].md)"
author: 
url: https://www.youtube.com/watch?v=VR4I1_HUrnc
dg-publish: true
---
# One-Way FSI
## 3D Modeling Tools
- FSI 해석을 위해 필요한 물체의 3D modeling
  CAD, Cartia, Solid Works 혹은 Ansys SpaceClaim 등 3D modeling tools를 사용
>[!info] 지원 포맷
>![[Pasted image 20240904202908.png|500]]![[스크린샷 2024-09-04 203008.png|500]]

<br>

## Ansys
### Fluid Flow (Fluent)
#### Ansys Workbench에 Fluent 추가 및 3D model 불러오기
- Ansys workbench 좌측 `Toolbox`에 있는 **Fluid Flow(Fluent)** tool을 `Project Schematic`에 드래그로 추가
- Fluent의 Geometry에서 3D model 데이터 Import
>[!info] Ansys Workbench
>![[Pasted image 20240904203627.png]]


<br>

#### Geometry
- SpaceClaim, DesignModeler, Discovery 중 아무거나 사용 가능 (여기서는 SpaceClaim 사용)

- 여러개의 Component로 구성된 모델을 하나로 통합
>[!info] Combine
>![[Pasted image 20240904204111.png]]

- 3D model에 이상이 없는지 확인
>[!info] Check Geometry
>![[Pasted image 20240904213231.png|300]]
  
- Fluid domain 생성
  Fluid domain은 `Enclousre`로 생성하는데, 이때 Inlet과 Outlet 영역을 제외한 면은 모두 Wall로 설정되기 때문에, 벽면의 마찰력으로 인한 유체의 유동이 물체의 유체 역학 해석에 영향을 미치지 않도록 충분히 크게 설정 
  >[!info] Enclosure
  >![[Pasted image 20240904213714.png|+grid]]![[Pasted image 20240904214053.png|+grid]]
  
  >[!info] Set units
  >![[Pasted image 20240904213928.png|+grid]]![[Pasted image 20240904213952.png|+grid]]

- Namespace 생성
  Inlet, outlet, [[walls]], [[walls-fluid-solid]], [[walls-solid-fluid]] 등을 생성
  >[!info] Create NS
  >![[Pasted image 20240904214927.png]]

<br>

#### Mesh
- Fluid Flow(Fluent)에서 `Mesh` ▶ `Edit`
>[!info] Editing mesh
>![[Pasted image 20240904215214.png|+grid]]![[Pasted image 20240904220451.png|+grid]]

- [[Inflation]] 추가
  Scope 에는 Fluid domain인 Enclosure를 선택하고, Definition boundary에는 `wall-fluid-solid` 선택
>[!info] Insert inflation
>
>![[Pasted image 20240904221046.png|+grid]]![[Pasted image 20240904221229.png|+grid]]
>![[Pasted image 20240904221718.png]]

- Mesh 생성
>[!info] Mesh generation
>![[Pasted image 20240904221446.png|+grid]]![[Pasted image 20240904221508.png|+grid]]<br>
>
>- Mesh size를 조절하고 싶을 경우
>  ![[Pasted image 20240904222519.png|300]]

- Workbench ▶ Fluent ▶ `Mesh` ▶ `Update`
>[!info] Update the mesh
>![[Pasted image 20240904222838.png|300]]

<br>

#### Setup
- Workbench ▶ Fluent ▶ `Setup` ▶ `Edit`
>[!info] Setup
>![[Pasted image 20240904222933.png|+grid]]![[Pasted image 20240904222942.png|+grid]]
>![[Pasted image 20240904223029.png]]

- Materials에 `water-liquid` 추가
  `Materials` ▶ `Fluid` ▶ `air` (Double click) ▶ `Fluent Database...`
>[!info] Create/Edit Materials
>![[Pasted image 20240904223430.png]]
>![[Pasted image 20240904223446.png|+grid]]![[Pasted image 20240904223521.png|+grid]]

- Fluid의 종류 변경
  `Cell Zone Conditions` ▶ `Fluid` ▶ `enclosure_enclosure`
>[!info] Fluid
>![[Pasted image 20240904223700.png]]

- Boundary conditions 설정
  `Boundary Conditions` ▶ `Inlet`
>[!info] Velocity Inlet
>![[Pasted image 20240904231455.png]]

- Report definitions 설정
  `Solution` ▶ `Report Definitions` ▶ `New`
>[!info] Report Definition
>![[Pasted image 20240904224854.png|+grid]]![[Pasted image 20240904225100.png|+grid]]


- Initialization
  `Solution` ▶ `Initialization`
>[!info] Solution Initialization
>![[Pasted image 20240904225217.png|300]]

- Run calculation
  `Solution` ▶  `Run Calculation`
>[!info] Run Calculation
>![[Pasted image 20240904225540.png|+grid]]![[Pasted image 20240904232654.png|+grid]]

- 결과 확인
  `Results` ▶ `Create` ▶ `Plane`
  `Results` ▶ `Contours` ▶ `New`
>[!info] Create Contours
>![[Pasted image 20240904230132.png|+grid]]![[Pasted image 20240904230143.png|+grid]]
>![[Pasted image 20240904233040.png|+grid]]![[Pasted image 20240904233059.png|+grid]]
>![[제목 없는 동영상 2.gif]]


<br><br>

### Static Structural
#### Ansys Workbench에 Static Structural 추가 및 Fluent와 연결
- Workbench 좌측 Toolbox에서 `Static Structural`를 Project Schematic에 추가
- `Geometry` 끼리 연결 및 Fluent의 `Solution`과 Static Structural의 `Setup` 연결
>[!info] Project Schematic
>![[Pasted image 20240905105237.png]]

#### Model
- `Static Structural` ▶ `Model` ▶ `Edit`
>[!info] Editing model
>![[Pasted image 20240905111206.png|+grid]]![[Pasted image 20240905111223.png|+grid]]

- Suppress fluid domain
  `Model` ▶ `Geometry` ▶ Select `Fluid domain` ▶ `Suppress Body`
>[!info] Suppress body
>![[Pasted image 20240905111435.png|300]]

- Generate mesh
  Outline에서 Mesh를 클릭하면 좌측 하단에 Mesh에 대한 상세 정보가 뜨며, `Sizing` ▶ `Span Angle Center`에서 Mesh quality를 선택할 수 있음
>[!info] Span Angle Center
>![[Pasted image 20240905111824.png||+grid]]![[Pasted image 20240905111928.png|+grid]]

- Material 선택
  `Model` ▶ `Geometry` ▶ Select `Solid` ▶ `Details of "Solid"` ▶ `Material` ▶ `Assignment`
>[!info] Material
>![[Pasted image 20240905112119.png|300]]

- Fixed Support 선택
  본 예제에서는 Hero wings의 Center link가 Cyclops에 부착되어 고정되어 있기 때문에 Center link를 Fixed Support로 선택
  `Static Structural` ▶ `Insert` ▶ `Fixed Support`
>[!info] Fixed Support
>![[Pasted image 20240905112610.png|+grid]]![[Pasted image 20240905112726.png|+grid]]

- Imported Pressure 선택
  `Static Structural` ▶ `Imported Load` ▶ `Insert` ▶ `Pressure` ▶ Select Named Selection `wall-solid-fluid`
>[!info] Imported Pressure
>![[Pasted image 20240905113007.png|300]]

- Solution 종류 선택
  `Static Structural` ▶ `Solution` ▶ `Insert` ▶ Select type of solutions what you want to analysis
>[!info] Solution
>![[Pasted image 20240905113428.png|+grid]]![[Pasted image 20240905203723.png|+grid]]

- Solve
>[!info] Results
>![[1) 2](제목 없는 동영상 (1|제목 없는 동영상 (1) 2]]%202.gif)![[2) 2](제목 없는 동영상 (2|제목 없는 동영상 (2) 2]]%202.gif)

