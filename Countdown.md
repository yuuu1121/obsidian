```dataviewjs
// ═══════════════════════════════════════════════════════
// Countdown Events
// 아래에 이벤트를 추가/수정하세요
// 형식: { name: "이벤트명", date: "YYYY-MM-DD", emoji: "🎯" }
// ═══════════════════════════════════════════════════════

const events = [
    { name: "설날", date: "2026-01-29", emoji: "🧧" },
    { name: "봄학기 시작", date: "2026-03-02", emoji: "📚" },
    { name: "석가탄신일", date: "2026-05-24", emoji: "🪷" },
    { name: "여름방학", date: "2026-06-20", emoji: "🏖️" },
];

// ═══════════════════════════════════════════════════════
// Calculation (수정 불필요)
// ═══════════════════════════════════════════════════════

const today = moment().startOf('day');
let output = '<div class="countdown-list">';

events.forEach(event => {
    const eventDate = moment(event.date);
    const daysLeft = eventDate.diff(today, 'days');

    if (daysLeft >= 0) {
        let daysText;
        if (daysLeft === 0) {
            daysText = '<span class="today">오늘!</span>';
        } else {
            daysText = `<span class="days">${daysLeft}</span>일`;
        }

        output += `
        <div class="countdown-item">
            <span class="event-emoji">${event.emoji}</span>
            <span class="event-name">${event.name}</span>
            <span class="event-days">${daysText}</span>
        </div>`;
    }
});

output += '</div>';
dv.paragraph(output);
```
