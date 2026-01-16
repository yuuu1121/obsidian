---
date: <% tp.date.now("YYYY-MM-DD") %>
week: <% tp.date.now("YYYY-[W]ww") %>
tags: weekly
---

# <% tp.date.now("YYYY년 MM월") %> Week <% tp.date.now("ww") %>

<< [[<% tp.date.now("YYYY-[W]ww", -7, tp.file.title, "YYYY-[W]ww") %>|지난주]] | [[<% tp.date.now("YYYY-[W]ww", 7, tp.file.title, "YYYY-[W]ww") %>|다음주]] >>

---

## Weekly Goals
- [ ] **Goal 1:**
- [ ] **Goal 2:**
- [ ] **Goal 3:**

---

## This Week's Daily Notes
- [[<% tp.date.weekday("YYYY-MM-DD", 1) %>|월요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 2) %>|화요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 3) %>|수요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 4) %>|목요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 5) %>|금요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 6) %>|토요일]]
- [[<% tp.date.weekday("YYYY-MM-DD", 0) %>|일요일]]

---

## Study Summary
> 이번 주 공부한 내용 정리

### Topics Covered
-

### Key Learnings
-

---

## Weekly Review
### Accomplishments
-

### Challenges
-

### Next Week's Focus
-

---

#weekly/<% tp.date.now("YYYY/MM") %>
