---
dg-publish: false
cssclasses:
  - dashboard
  - without-title
  - full-width
banner: "![[노을과 반영-035_2560x1440.jpg]]"
---

```dataviewjs
// 오늘의 날짜를 "YYYY-MM-DD" 형식으로 가져오기
let today = dv.date("today").toFormat("yyyy-MM-dd");

// 링크 생성
let filePath = `3_Archive/2_Calendar/Daily Notes/${today}.md`;

// 링크를 표시
dv.paragraph(`[[${filePath}|Today's Daily Note]]`);

```

[[TODO LIST]]

<br>

# Projects.
>[!multi-column]
>>[!note] #### In progress
>>- [ ] [[Kanban - Reinforcement Learning|Reinforcement Learning]]
>>- [ ] [[Kanban - PKRC]]
>
>>[!abstract] ##### On going
>>
>
>>[!info] ##### Pause
>>- [ ] [[Kanban - 3D Reconstruction from Stereo Images|3D Reconstruction from Stereo Images]]
>
>>[!check] ##### Done
>>- [x] [[Kanban - PKRC|PKRC - 균열 검출 로봇]]
>>- [x] [[Kanban - VideoRay|Kanban - VideoRay]]
>>- [x] [[Fluid Solid Interaction Analysis (FSI) in Ansys]]
>

<br><br>

# TODO Lists.
>[!multi-column]
>>[!quote] #### Today
>>```dataviewjs
>>let today = dv.date("today");
>>
>>let pages = dv.pages('"3_Archive/2_Calendar"')
>>  .filter(p => {
>>    let fileDate = p.date;
>>    let startRecur = p.startRecur;
>>    let endRecur = p.endRecur;
>>    let completed = p.completed;
>>
>>    // Exclude pages if 'completed' is present and not 'false'
>>    if (completed && completed !== false) {
>>      return false;
>>    }
>>
>>    if (p.type == "recurring") {
>>      return startRecur && today >= startRecur && today <= endRecur;
>>    } else {
>>      return fileDate && fileDate.equals(today);
>>    }
>>  })
>>  .sort(p => {
>>    // Recurring items are sorted by endRecur - 1 day, non-recurring by date
>>    return p.type == "recurring" ? p.endRecur.minus({ days: 1 }) : p.date;
>>  }, 'asc')
>>  .filter(p => !p.file.folder.includes("Daily Notes") && !p.file.folder.includes("Done"));
>>
>>dv.list(pages.map(p => p.file.link));
>>
>>```
>
>>[!warning] ##### Overdue
>>```dataviewjs
>>let today = dv.date("today");
>>
>>let pages = dv.pages('"3_Archive/2_Calendar"')
>>  .filter(p => {
>>    let fileDate = p.date;
>>    let endRecur = p.endRecur;
>>    let completed = p.completed;
>>    
>>    if (completed && completed !== false) {
>>      return false;  // If `completed` is present and not `false`, exclude the page
>>    }
>>
>>    if (p.type == "recurring") {
>>      return endRecur && endRecur < today;
>>    } else {
>>      return fileDate && fileDate < today;
>>    }
>>  })
>>  .sort(p => {
>>    let overdueDate = p.type == "recurring" ? p.endRecur : p.date;
>>    return overdueDate;
>>  }, 'asc')
>>  .filter(p => !p.file.folder.includes("Daily Notes") && !p.file.folder.includes("Done"));
>>
>>dv.list(pages.map(p => `${p.file.link} - Overdue by ${today.diff(p.type == "recurring" ? p.endRecur : p.date, "days")} days`));
>>
>>```
>
>>[!todo] ##### Unplanned
>>```dataviewjs
>>let pages = dv.pages('"/"')
>>    .where(p => p.file.tasks.some(t => t.text.includes("#task") && !t.completed));
>>
>>let output = [];
>>
>>for (let page of pages) {
>>    for (let task of page.file.tasks.filter(t => t.text.includes("#task") && !t.completed)) {
>>        // 들여쓰기를 직접 확인하여 최상위 항목만 필터링
>>        if (!task.text.startsWith("  ") && !task.text.startsWith("\t")) { 
>>            // 우선순위 확인을 위해 기호 체크
>>            let priority = 2;  // 기본 우선순위는 중간값 (기호 없는 경우)
>>            let priorityIcon = "";  // 우선순위 기호를 저장할 변수
>>
>>            if (task.text.includes("🔴")) {
>>                priority = 0;  // 가장 높은 우선순위
>>                priorityIcon = "🔴";
>>            } else if (task.text.includes("🟢")) {
>>                priority = 1;  // 두 번째 높은 우선순위
>>                priorityIcon = "🟢";
>>            } else if (task.text.includes("🟡")) {
>>                priority = 3;  // 가장 낮은 우선순위
>>                priorityIcon = "🟡";
>>            }
>>
>>            // 태스크 텍스트에서 #task 태그만 제거하고, 기호는 마지막에 추가
>>            let taskTextWithoutTag = task.text.replace("#task", "").replace(/[🔴🟢🟡]/g, "").trim() + ` ${priorityIcon}`.trim();
>>            // 우선순위를 추가하여 리스트에 저장
>>            output.push({ text: `${taskTextWithoutTag} ([[${page.file.path}|Link]])`, priority });
>>        }
>>    }
>>}
>>
>>// 우선순위에 따라 정렬
>>output.sort((a, b) => a.priority - b.priority);
>>
>>// 리스트 출력
>>dv.list(output.map(item => item.text));
>>
>>```
>
>>[!summary] ##### Next Week
>>```dataviewjs
>>let today = dv.date("today");
>>let weekday = today.weekday;  // 0 = 월요일, 6 = 일요일
>>
>>// 이번 주 월요일 계산
>>let thisMonday = today.minus({ days: (weekday === 0 ? 0 : weekday - 1) });
>>
>>// 다음 주 월요일과 일요일 계산
>>let nextMonday = thisMonday.plus({ days: 7 });
>>let nextSunday = nextMonday.plus({ days: 6 });
>>
>>let pages = dv.pages('"3_Archive/2_Calendar"')
>>  .filter(p => {
>>    let startRecur = p.startRecur;
>>    let endRecur = p.endRecur ? p.endRecur.minus({ days: 1 }) : null;
>>    let fileDate = p.date;
>>    let endDate = p.endDate ? p.endDate.minus({ days: 1 }) : null;
>>
>>    // 일반 항목: fileDate가 다음 주 월요일과 일요일 사이에 있는지 확인
>>    if (fileDate && fileDate >= nextMonday && fileDate <= nextSunday) {
>>        return true;
>>    }
>>    if (endDate && endDate >= nextMonday && endDate <= nextSunday) {
>>        return true;
>>    }
>>
>>    // 반복 항목 및 범위 항목 필터링
>>    if (startRecur && endRecur) {
>>        // Case 1: startRecur이 다음 주 이전이고, endRecur이 다음 주에 포함되거나 이후인 경우
>>        if (startRecur < nextMonday && endRecur >= nextMonday) {
>>            return true;
>>        }
>>        // Case 2: startRecur이 다음 주에 포함되고, endRecur이 다음 주에 포함되거나 이후인 경우
>>        if (startRecur >= nextMonday && startRecur <= nextSunday && endRecur >= nextMonday) {
>>            return true;
>>        }
>>    }
>>    
>>    if (fileDate && endDate) {
>>        // Case 1: fileDate이 다음 주 이전이고, endDate이 다음 주에 포함되거나 이후인 경우
>>        if (fileDate < nextMonday && endDate >= nextMonday) {
>>            return true;
>>        }
>>        // Case 2: fileDate이 다음 주에 포함되고, endDate이 다음 주에 포함되거나 이후인 경우
>>        if (fileDate >= nextMonday && fileDate <= nextSunday && endDate >= nextMonday) {
>>            return true;
>>        }
>>    }
>>    return false;
>>  })
>>  .sort(p => {
>>    return p.type == "recurring" ? p.endRecur.minus({ days: 1 }) : p.date;
>>  }, 'asc')
>>  .filter(p => !p.file.folder.includes("Daily Notes") && !p.file.folder.includes("Done"));
>>
>>dv.list(pages.map(p => {
>>  let start = p.startRecur || p.date;
>>  let end = p.endRecur ? p.endRecur.minus({ days: 1 }) : (p.endDate ? p.endDate.minus({ days: 1 }) : null);
>>  let displayDate = start ? start.toFormat("MM/dd") : "";
>>  let displayEnd = end ? end.toFormat("MM/dd") : "";
>>  
>>  if (start && end && start !== end) {
>>    return `(${displayDate} ~ ${displayEnd}) ${p.file.link}`;
>>  } else {
>>    return `(${displayDate}) ${p.file.link}`;
>>  }
>>}));
>>
>>```

<br><br>

