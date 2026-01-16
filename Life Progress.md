```dataviewjs
// ═══════════════════════════════════════════════════════
// Life Progress Calculator
// Change your birth date below (year, month, day)
// ═══════════════════════════════════════════════════════

const birthYear = 1998;  // 생년
const birthMonth = 1;    // 월 (1-12)
const birthDay = 1;      // 일

const lifeExpectancy = 80; // 예상 수명

// ═══════════════════════════════════════════════════════
// Calculation (수정 불필요)
// ═══════════════════════════════════════════════════════

const today = new Date();
const birthDate = new Date(birthYear, birthMonth - 1, birthDay);
const endDate = new Date(birthYear + lifeExpectancy, birthMonth - 1, birthDay);

const totalDays = (endDate - birthDate) / (1000 * 60 * 60 * 24);
const daysPassed = (today - birthDate) / (1000 * 60 * 60 * 24);
const percentage = Math.min(100, Math.max(0, (daysPassed / totalDays) * 100)).toFixed(1);

const yearsOld = Math.floor(daysPassed / 365.25);
const daysRemaining = Math.max(0, Math.floor(totalDays - daysPassed));
const yearsRemaining = Math.floor(daysRemaining / 365.25);

dv.paragraph(`
<div class="life-progress">
  <div class="progress-header">
    <span>🎂 ${yearsOld}세</span>
    <span>${percentage}%</span>
    <span>⏳ ${yearsRemaining}년 남음</span>
  </div>
  <progress value="${percentage}" max="100"></progress>
</div>
`);
```
