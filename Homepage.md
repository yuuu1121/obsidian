---
cssclasses:
  - myhome
banner: "Pictures/pixel.jpg"
banner_y: 0.6
banner_x: 0.5
---

# Dashboard
-  ### **TODO**
	- [**Daily**](obsidian://advanced-uri?vault=YJU_Obsidian&daily=true)
	- **IROS**
		- [ ] 논문 초안 작성 📅2026-03-01 #논문
		- [x] 시뮬레이터 구현 #논문
		- [ ] Active Marker 제작 #논문
		- [ ] RTK-GPS 주문 #논문
		- [ ] Active Marker 아크릴 가공 주문 #논문
		- [ ] Active Marker 전선 주문 #논문
	- **PKRC**
		- [ ] 수중로봇 Wall Following 실제 구현 📅2026-01-18 #PKRC
		- [x] 수중로봇 IMU PID 제어 📅2026-01-16 #PKRC
		- [x] 수중로봇 Depth 제어 📅2026-01-16 #PKRC
		- [ ] Laser + Camera Altitude Estimation #PKRC
		- [ ] 전장 V3 #PKRC 
	-  **Cyclops**
		- [ ] USBL 동작 테스트 #Cyclops
		- [ ] 내부 실린더 전장 마운트 설계 #Cyclops 
	- **AUV**
		- [ ] idea 회의 #AUV
- ### **STUDY**
	- [[00. Deep Learning|Deep Learning]]
	- [[00. Machine Learning|Machine Learning]]
	- [[00. Reinforcement Learning|Reinforcement Learning]]
	- [[00. OpenCV|OpenCV]]
	- [[00. Reviews|Paper Review]]

<br>

# PROJECT TRACKING

%%
sourceTag:: #project
excludeTag:: #exclude
toCount:: words
target:: 10000
%%

```dataviewjs
// 현재 파일에서 태스크 가져오기
const currentFile = dv.page("Homepage");
const allTasks = currentFile?.file?.tasks || [];

// 모든 태스크에서 태그 자동 추출
const tagSet = new Set();
allTasks.forEach(t => {
    const matches = t.text.match(/#[\w가-힣]+/g);
    if (matches) {
        matches.forEach(tag => tagSet.add(tag));
    }
});

// 태그 배열로 변환 후 정렬
const tags = Array.from(tagSet).sort();

let table = `| Project | Progress | Status |
| --- | --- | --- |
`;

tags.forEach(tag => {
    // 해당 태그가 있는 태스크 필터링
    const projectTasks = allTasks.filter(t => t.text.includes(tag));
    const total = projectTasks.length;
    const completed = projectTasks.filter(t => t.completed).length;

    // 진행률 계산
    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;

    // 상태 결정
    let status = "대기";
    if (progress === 100) status = "✅ 완료";
    else if (progress > 0) status = "진행중";

    // 태그 이름에서 # 제거하고 표시
    const displayName = tag.replace("#", "");
    table += `| **${displayName}** | <progress value="${progress}" max="100"></progress> ${progress}% (${completed}/${total}) | ${status} |
`;
});

dv.span(table);
```

<br>

# DEADLINE

```dataviewjs
// 현재 파일에서 태스크 가져오기
const currentFile = dv.page("Homepage");
const allTasks = currentFile?.file?.tasks || [];

// 📅YYYY-MM-DD 또는 📅 YYYY-MM-DD 형식의 날짜가 있는 태스크 찾기
const deadlines = [];
allTasks.forEach(t => {
    const dateMatch = t.text.match(/📅\s*(\d{4}-\d{2}-\d{2})/);
    if (dateMatch && !t.completed) {
        // 태스크 텍스트에서 날짜와 태그 제거하여 이름 추출
        let name = t.text
            .replace(/📅\s*\d{4}-\d{2}-\d{2}/, '')
            .replace(/#[\w가-힣]+/g, '')
            .trim();
        deadlines.push({ name: name, date: dateMatch[1] });
    }
});

const today = moment().startOf('day');
let table = `| Event | D-Day |
| --- | --- |
`;

deadlines
    .map(d => ({ ...d, days: moment(d.date).diff(today, 'days') }))
    .filter(d => d.days >= -1)
    .sort((a, b) => a.days - b.days)
    .forEach(d => {
        let daysText = d.days === 0 ? '**오늘!**' : d.days < 0 ? '**지남**' : `D-${d.days}`;
        table += `| ${d.name} | ${daysText} |
`;
    });

if (deadlines.length === 0) {
    table += `| 📅 날짜 추가: 태스크에 📅2026-01-20 형식 | - |
`;
}

dv.span(table);
```

<br>

# DAILY SUMMARY

```dataviewjs
function isWithinWeek(page) {
	let filemoment = moment(page.file.name, 'YYYY-MM-DD')
	let today = moment().startOf('day');
	let tomorrow = today.clone().add(1, 'days').startOf('day');
	let weekago = today.clone().subtract(7, 'days').startOf('day');
	if (filemoment.isAfter(weekago) && filemoment.isBefore(tomorrow)) {
		return true;
	}
	return false;
}

dv.table(["Date","Note"], dv.pages('"Daily Notes"')
	.filter(isWithinWeek)
	.sort(b => b.file.name,'desc')
	.limit(7)
	.map(b => [dv.fileLink(b.file.name, false, moment(b.file.name,'YYYY-MM-DD').format("MM-DD ddd")), b.file.name])
)
```

<br>
