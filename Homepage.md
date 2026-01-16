---
cssclass: cards
---

```dataviewjs
const currentHour = moment().format('HH');
let greeting;
if (currentHour >= 18 || currentHour < 5) {
    greeting = '🌙 Good Evening';
} else if (currentHour >= 5 && currentHour < 12) {
    greeting = '🌅 Good Morning';
} else {
    greeting = '☀️ Good Afternoon';
}
dv.header(1, greeting);
```

> [!cards|3]
>  **Study**
> ![](https://raw.githubusercontent.com/D3Ext/aesthetic-wallpapers/main/images/small-memory.png)
>  **[[Study/Deep_Learning/|Deep Learning]]**  <br> **[[Study/Machine_Learning/|Machine Learning]]**   <br> **[[Study/Reinforcement_Learning/|Reinforcement Learning]]**   <br>  **[[Study/Statistics/|Statistics]]**
>
>  **Paper**
> ![](https://raw.githubusercontent.com/D3Ext/aesthetic-wallpapers/main/images/lofi.png)
>**[[Paper/Reviews/|Reviews]]**  <br> **[[Paper/Zotero/|Zotero Notes]]**  <br> **[[Paper/논문 작성 유의사항|Writing Guide]]**
>
>  **Tools**
> ![](https://raw.githubusercontent.com/D3Ext/aesthetic-wallpapers/main/images/music.jpg)
>**[[Obsidian Guide|📖 Guide]]**  <br> **[[Templates/|📝 Templates]]**  <br> **[[Daily Notes/|📅 Daily Notes]]**


>[!multi-column|right|2]
>
>> [!important]+ 📊 Project Progress
>> ![[Project Progress]]
>
>> [!danger]+ ⏳ Deadline
>> ![[Deadline]]

---
