---
cssclass: cards
banner: "![[faroukhomepage2.png]]"
banner_y: 0.35
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
> ![[Pasted image 20230103220831.png|center|440]]
>  **[[Study/Deep_Learning/|Deep Learning]]**  <br> **[[Study/Machine_Learning/|Machine Learning]]**   <br> **[[Study/Reinforcement_Learning/|RL]]**   <br>  **[[Study/Statistics/|Statistics]]**
>
>  **Paper**
> ![[Pasted image 20230103220838.png|center|440]]
>**[[Paper/Reviews/|Reviews]]**  <br> **[[Paper/Zotero/|Zotero Notes]]**  <br> **[[Paper/논문 작성 유의사항|Writing Guide]]**
>
>  **Tools**
> ![[Pasted image 20230103220845.png|center|440]]
>**[[Obsidian Guide|📖 Guide]]**  <br> **[[Templates/|📝 Templates]]**  <br> **[[Daily Notes/|📅 Daily Notes]]**


>[!multi-column|right|2]
>
>> [!important]+ 📊 Project Progress
>> ![[Project Progress]]
>
>> [!danger]+ ⏳ Deadline
>> ![[Deadline]]

---
