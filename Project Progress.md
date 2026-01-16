```dataviewjs
// ═══════════════════════════════════════════════════════════
// Project Progress - 대학원생용
// 아래에 프로젝트를 추가/수정하세요
// ═══════════════════════════════════════════════════════════

const projects = [
    { name: "논문 작성", progress: 40 },
    { name: "실험 진행", progress: 65 },
    { name: "데이터 분석", progress: 30 },
    { name: "학위 과정", progress: 50 },
];

// ═══════════════════════════════════════════════════════════

function progressBar(value) {
    return `<progress value="${value}" max="100"></progress> | ${value}%`;
}

let table = `|  | Progress | % |
| --- | --- |:---:|
`;

projects.forEach(p => {
    table += `| **${p.name}** | ${progressBar(p.progress)}\n`;
});

dv.span(table);
```
