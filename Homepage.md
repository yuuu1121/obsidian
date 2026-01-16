---
cssclasses:
  - myhome
banner: "Pictures/fuji.jpg"
banner_y: 0.7
banner_x: 0.5
---

# Dashboard
- **AGENDA**
	- [Daily](obsidian://advanced-uri?vault=YJU_Obsidian&daily=true)
	- [[00. Templates|Templates]]
- **STUDY**
	- [[00. Deep Learning|Deep Learning]]
	- [[00. Machine Learning|Machine Learning]]
	- [[00. Reinforcement Learning|RL]]
	- [[00. Statistics|Statistics]]
- **PAPER**
	- [[00. Reviews|Reviews]]
- **TOOLS**
	- [[00. OpenCV|OpenCV]]
	- [[00. Coding|Coding]]
	- [[Obsidian Guide|Guide]]

<br>

**PROJECT TRACKING**

%%
sourceTag:: #project
excludeTag:: #exclude
toCount:: words
target:: 10000
%%

```dataviewjs
// 프로젝트 진행률 표시
const projects = [
    { name: "📝 논문 작성", progress: 40, status: "진행중" },
    { name: "🔬 실험", progress: 65, status: "진행중" },
    { name: "📊 데이터 분석", progress: 30, status: "대기" },
    { name: "🎓 학위 과정", progress: 50, status: "진행중" },
];

let table = `| Project | Progress | Status |
| --- | --- | --- |
`;

projects.forEach(p => {
    table += `| **${p.name}** | <progress value="${p.progress}" max="100"></progress> ${p.progress}% | ${p.status} |
`;
});

dv.span(table);
```

<br>

**DEADLINE**

```dataviewjs
const deadlines = [
    { name: "📝 논문 제출", date: "2026-03-15" },
    { name: "🎤 학회 발표", date: "2026-05-20" },
    { name: "📊 중간 보고", date: "2026-02-28" },
    { name: "🎓 졸업 심사", date: "2026-06-30" },
];

const today = moment().startOf('day');
let table = `| Event | D-Day |
| --- | --- |
`;

deadlines
    .map(d => ({ ...d, days: moment(d.date).diff(today, 'days') }))
    .filter(d => d.days >= 0)
    .sort((a, b) => a.days - b.days)
    .forEach(d => {
        let daysText = d.days === 0 ? '**오늘!**' : `D-${d.days}`;
        table += `| ${d.name} | ${daysText} |
`;
    });

dv.span(table);
```

<br>

**DAILY SUMMARY**

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

**OBSIDIAN ACTIVITY**

```dataviewjs
let allFile = dv.pages('!"Templates"').file
let total = allFile.length
let studyNotes = dv.pages('"Study"').length
let paperNotes = dv.pages('"Paper"').length
let dailyNotes = dv.pages('"Daily Notes"').length
let totalTask = allFile.tasks.length

dv.paragraph(
	`📁 **${total}** files | 📚 Study: **${studyNotes}** | 📄 Paper: **${paperNotes}** | 📅 Daily: **${dailyNotes}** | ✅ Tasks: **${totalTask}**`
)
```
