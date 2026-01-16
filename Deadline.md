```dataviewjs
// ═══════════════════════════════════════════════════════════
// Deadline Countdown - 대학원생용
// 아래에 마감일을 추가/수정하세요
// 형식: { name: "이름", date: "YYYY-MM-DD" }
// ═══════════════════════════════════════════════════════════

const deadlines = [
    { name: "📝 논문 제출", date: "2026-03-15" },
    { name: "🎤 학회 발표", date: "2026-05-20" },
    { name: "📊 중간 보고", date: "2026-02-28" },
    { name: "🎓 졸업 심사", date: "2026-06-30" },
];

// ═══════════════════════════════════════════════════════════

const today = moment().startOf('day');

let output = '';
deadlines
    .map(d => ({ ...d, days: moment(d.date).diff(today, 'days') }))
    .filter(d => d.days >= 0)
    .sort((a, b) => a.days - b.days)
    .forEach(d => {
        let daysText = d.days === 0 ? '**오늘!**' : `**D-${d.days}**`;
        output += `${d.name} | ${daysText}\n`;
    });

dv.span(output || '등록된 마감일이 없습니다.');
```
