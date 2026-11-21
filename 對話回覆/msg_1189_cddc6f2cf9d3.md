# 對話材料 #1189

- event: assistant/message
- seq: 132873
- time: 1795244220711

---

`【鈔文】` appears only in **translation** `.t`, not source. User sees `【鈔文】` labels; asks why single book 行事鈔 has `【鈔文】` annotations. Answer:
- Some translation text includes `【鈔文】` because source material units were labeled/tagged `鈔文`; translation carried label. In 行事鈔 single book, the whole text is 鈔文, so label is redundant; should be removed.
- `【鈔文】` is an allowed type label per AGENTS, but for single 行事鈔 it's not needed; in 合編本 it distinguishes 鈔/記.
- Count 81 occurrences (23+28+30); remove from translation (and source if any).
- Also maybe source labels? none in source; only t.
- Remove `【鈔文】` from xingshichao pages, since book is 行事鈔; keep no label. Commit.
- Could also check `hebian` uses.

Do remove from xingshichao translation/source.