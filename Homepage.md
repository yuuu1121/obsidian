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
-  **TODO**
	- 📝 논문 작성
		- [ ] 서론 작성 #논문
		- [ ] 관련 연구 정리 #논문
		- [ ] 실험 결과 정리 #논문
		- [ ] 결론 작성 #논문
	- 🔬 실험
		- [ ] 데이터셋 준비 #실험
		- [ ] 모델 학습 #실험
		- [ ] 결과 분석 #실험
	- 📊 데이터 분석
		- [ ] 데이터 전처리 #데이터
		- [ ] 시각화 #데이터
	- 🎓 학위 과정
		- [ ] 중간 발표 준비 #학위
		- [ ] 논문 심사 준비 #학위
- **STUDY**
	- [[00. Deep Learning|Deep Learning]]
	- [[00. Machine Learning|Machine Learning]]
	- [[00. Reinforcement Learning|RL]]
	- [[00. OpenCV|OpenCV]]
- **PAPER**
	- [[00. Reviews|Reviews]]

<br>

**PROJECT TRACKING**

%%
sourceTag:: #project
excludeTag:: #exclude
toCount:: words
target:: 10000
%%

```dataviewjs
// 프로젝트별 태그와 이름 매핑
const projects = [
    { name: "📝 논문 작성", tag: "#논문" },
    { name: "🔬 실험", tag: "#실험" },
    { name: "📊 데이터 분석", tag: "#데이터" },
    { name: "🎓 학위 과정", tag: "#학위" },
];

// 현재 파일에서 태스크 가져오기
const currentFile = dv.page("Homepage");
const allTasks = currentFile?.file?.tasks || [];

let table = `| Project | Progress | Status |
| --- | --- | --- |
`;

projects.forEach(p => {
    // 해당 태그가 있는 태스크 필터링
    const projectTasks = allTasks.filter(t => t.text.includes(p.tag));
    const total = projectTasks.length;
    const completed = projectTasks.filter(t => t.completed).length;

    // 진행률 계산
    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;

    // 상태 결정
    let status = "대기";
    if (progress === 100) status = "✅ 완료";
    else if (progress > 0) status = "진행중";

    table += `| **${p.name}** | <progress value="${progress}" max="100"></progress> ${progress}% (${completed}/${total}) | ${status} |
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
