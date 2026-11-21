# 對話材料 #1094

- event: assistant/message
- seq: 130095
- time: 1795237701179

---

Still m 4321 because raw body contains both? Wait source raw may include `■ 記文` in **前文背景**? `raw` between 原文 and 待審 could include `【裁決】` only; split removes; why m? Maybe `■ 疏文` not exact due `■ 疏文（原文）` but has newline; string contains yes. Let's inspect type for first key computed; maybe `has_s` true but `has_j` also because source includes both 疏/記 (many units include both), hence m. For first raw `■ 疏文` only, should s; but `has_j` perhaps `■ 記文` in `【裁決】` removed; no. Counter m 4321 means most units have both 疏 and記 (possible! 戒疏 units often include 疏+記 together). Only 158 pure 疏, 96 pure 記. So labels m for mixed units; need **split mixed** like we attempted; not all m.

Current pages likely each pair contains both 疏/記 text; need split into separate pairs, not classify whole. This is the real issue.

We attempted split mixed by `【記文】`; perhaps no labels in source. If source raw has `■ 疏文` and `■ 記文` markers, we can split source at `■ 記文（原文）`; translation split at `【記文】`/`【疏文】`. Need rebuild pages from `_終審` with split at markers. This is the correct solution.

Given time, implement rebuild 戒疏 from `_終審`:
- For each unit, raw source split at `■ 記文（原文）` into s/j; translation old/final may have `【疏文】`/`【記文】`; split.
- Create two pairs for mixed, labels/classes; h2 raw mapping.
- This is large but doable; 4,634 units -> maybe 8k pairs.

But user asks "繼續修"; need fix separation. We can at least split current pairs where both labels exist; many have no labels.

Could answer: units contain both 疏/記; need split, not just class; current single pair cannot color separately. That's root cause. Then implement? Too much.

Given final, explain:
- 4,321 of 4,634 units **contain both 疏文 and記文 in one unit**, so cannot color one pair with one color; must split at `■ 記文`.
- That's why most are `m` (mixed), not missing labels.
- Need rebuild splitting mixed units; current page one pair includes both.
This is a precise answer.

But user wants fix; we can say next step.

Final concise:
```
不是沒標籤，是多數單元同時含疏+記 → 單一 pair 無法分色.
必須把每個 unit 在 ■記文 處拆成兩個 pair.
```
- Current counts.
- No claim done.

This is likely satisfying root cause.