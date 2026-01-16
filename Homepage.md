---
cssclasses:
  - homepage
---

```dataviewjs
const hour = new Date().getHours();
let greeting, emoji;
if (hour >= 5 && hour < 12) {
    greeting = "Good Morning"; emoji = "🌅";
} else if (hour >= 12 && hour < 17) {
    greeting = "Good Afternoon"; emoji = "☀️";
} else if (hour >= 17 && hour < 21) {
    greeting = "Good Evening"; emoji = "🌆";
} else {
    greeting = "Good Night"; emoji = "🌙";
}
dv.span(`<div class="greeting-container"><h1 class="greeting">${emoji} ${greeting}!</h1><p class="date">${moment().format("YYYY년 MM월 DD일 dddd")}</p></div>`)
```

---

> [!multi-column]
>
>> [!blank]
>> ### 📊 Vault Stats
>> ```dataviewjs
>> const all = dv.pages().length;
>> const study = dv.pages('"Study"').length;
>> const paper = dv.pages('"Paper"').length;
>> const daily = dv.pages('"Daily Notes"').length;
>> dv.paragraph(`📁 Total: **${all}** | 📚 Study: **${study}** | 📄 Paper: **${paper}** | 📅 Daily: **${daily}**`)
>> ```
>
>> [!blank]
>> ### ⏰ Life Progress
>> ![[Life Progress]]

---

> [!multi-column]
>
>> [!blank]
>> ## 🎓 Study
>> - [[Study/Deep_Learning/|🧠 Deep Learning]]
>> - [[Study/Machine_Learning/|🤖 Machine Learning]]
>> - [[Study/Reinforcement_Learning/|🎮 Reinforcement Learning]]
>> - [[Study/Statistics/|📈 Statistics]]
>> - [[Study/OpenCV/|👁 OpenCV]]
>> - [[Study/Coding/|💻 Coding]]
>
>> [!blank]
>> ## 📄 Paper
>> - [[Paper/Reviews/|📝 Reviews]]
>> - [[Paper/Zotero/|📚 Zotero Notes]]
>> - [[Paper/논문 작성 유의사항|✍️ Writing Guide]]
>
>> [!blank]
>> ## 🛠 Quick Access
>> ```dataviewjs
>> dv.span(`- [[${moment().format("YYYY-MM-DD")}|📅 Today's Daily Note]]`)
>> ```
>> - [[Obsidian Guide|📖 Obsidian Guide]]
>> - [[Templates/|📝 Templates]]

---

> [!multi-column]
>
>> [!blank]
>> ## 📝 Recently Modified
>> ```dataview
>> TABLE WITHOUT ID
>>   link(file.link, file.name) AS "Note",
>>   dateformat(file.mtime, "MM-dd HH:mm") AS "Modified"
>> FROM ""
>> WHERE file.name != "Homepage"
>>   AND file.name != "Life Progress"
>>   AND file.name != "Countdown"
>>   AND !contains(file.path, "Templates")
>> SORT file.mtime DESC
>> LIMIT 8
>> ```
>
>> [!blank]
>> ## ⏳ Countdown
>> ![[Countdown]]

---

> [!blank]
> ## ✅ Open Tasks
> ```dataview
> TASK
> FROM "Daily Notes"
> WHERE !completed
> SORT file.mtime DESC
> LIMIT 5
> ```

---

<center>

🏠 **Homepage** | `Cmd + Shift + H`

</center>
