---
cssclasses:
  - homepage
  - cards
---

```dataviewjs
const hour = new Date().getHours();
let greeting, emoji;
if (hour >= 5 && hour < 12) { greeting = "Good morning"; emoji = "🌅"; }
else if (hour >= 12 && hour < 17) { greeting = "Good afternoon"; emoji = "☀️"; }
else if (hour >= 17 && hour < 21) { greeting = "Good evening"; emoji = "🌆"; }
else { greeting = "Good night"; emoji = "🌙"; }

const today = moment().format("YYYY년 MM월 DD일 dddd");
dv.header(1, `${emoji} ${greeting}!`);
dv.paragraph(`📅 ${today}`);
```

---

## 🚀 Quick Access

> [!multi-column]
>
>> [!note|no-title]+ 🎓 **STUDY**
>>
>> **Deep Learning**
>> - [[Study/Deep_Learning/|Go to folder →]]
>>
>> **Machine Learning**
>> - [[Study/Machine_Learning/|Go to folder →]]
>>
>> **Reinforcement Learning**
>> - [[Study/Reinforcement_Learning/|Go to folder →]]
>>
>> **Statistics**
>> - [[Study/Statistics/|Go to folder →]]
>
>> [!note|no-title]+ 📄 **PAPER**
>>
>> **Reviews**
>> - [[Paper/Reviews/|Go to folder →]]
>>
>> **Zotero Notes**
>> - [[Paper/Zotero/|Go to folder →]]
>>
>> **Writing Guide**
>> - [[Paper/논문 작성 유의사항|Open →]]
>
>> [!note|no-title]+ 🛠 **TOOLS**
>>
>> **Today's Note**
>> ```dataviewjs
>> dv.span(`[[${moment().format("YYYY-MM-DD")}|📌 Open Today →]]`)
>> ```
>>
>> **Obsidian Guide**
>> - [[Obsidian Guide|Open →]]
>>
>> **Templates**
>> - [[Templates/|Go to folder →]]

---

## 📝 Recently Modified

```dataview
TABLE WITHOUT ID
	link(file.link, file.name) AS "📄 Note",
	file.folder AS "📁 Location",
	dateformat(file.mtime, "MM-dd HH:mm") AS "🕐 Modified"
FROM ""
WHERE file.name != "Homepage"
  AND file.name != "Obsidian Guide"
  AND !contains(file.path, "Templates")
  AND !contains(file.path, ".obsidian")
SORT file.mtime DESC
LIMIT 10
```

---

## ✅ Open Tasks

```dataview
TASK
FROM "Daily Notes"
WHERE !completed
SORT file.mtime DESC
LIMIT 5
```

---

## 📊 Vault Overview

```dataviewjs
const allFiles = dv.pages().length;
const studyNotes = dv.pages('"Study"').length;
const paperNotes = dv.pages('"Paper"').length;
const dailyNotes = dv.pages('"Daily Notes"').length;
const templates = dv.pages('"Templates"').length;

dv.paragraph(`
| 📁 Total | 🎓 Study | 📄 Paper | 📅 Daily | 📝 Templates |
|:---:|:---:|:---:|:---:|:---:|
| **${allFiles}** | **${studyNotes}** | **${paperNotes}** | **${dailyNotes}** | **${templates}** |
`);
```

---

## 🔗 Quick Links

| Action | Shortcut |
|--------|----------|
| 📅 Today's Daily Note | `Cmd + T` |
| 🔍 Quick Switcher | `Cmd + O` |
| 🕸 Graph View | `Cmd + G` |
| 📋 Command Palette | `Cmd + Shift + P` |
| ✏️ New Excalidraw | `Cmd + Shift + D` |
| 📊 New Kanban | `Cmd + Shift + K` |
