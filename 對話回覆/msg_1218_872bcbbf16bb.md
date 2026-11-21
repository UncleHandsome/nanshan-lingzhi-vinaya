# 對話材料 #1218

- event: assistant/message
- seq: 133383
- time: 1795245634170

---

Correct raw empty 44! `correct` fails because source has labels/`<br>`/punctuation and `han(src)[:20]` may find; but `h.find` perhaps due D source from material has `【疏文】【疏文】`? We can inspect D003; `q` maybe not found because source includes `【疏文】` twice; han strips only one leading label, leaving second `疏文`; h.find fails. Need strip all leading labels and punctuation; `han` currently only one. Fix `han` remove all leading `【...】`; also source may have `【疏】` internal; remove? For matching first20, remove labels.
- `han` = remove all `【...】` occurrences at start, maybe all.
- Then find.
- Also raw `【疏】` positions.
Regenerate.

Do.