# 對話材料 #0857

- event: assistant/message
- seq: 111329
- time: 1795063327017

---

Now pack_judge fixture for multi-segment alternating labels. Build dir:
- 索引_pack.json {'p1': ['a1','a2']}
- p1_回.txt with:
```
【結論】
REVISED

【分歧與裁決】
[1][疏文] ... 
[2][疏文] ...

【修正後的譯文】
[1]
【疏文】改後疏1
【記文】改後記1

[2]
【疏文】改後疏2
【記文】改後記2
```
Note _by_i requires div lines starting [n]; Provide two lines.

Run `pack_judge.py --out dir --mode split --replies 回覆` (mat optional; if no mat, _jia_group empty).
Check outputs a1/a2 texts contain 改後記1/改後記2.

Potential issue: `A.col3` parses 修正後的譯文; body3 reorder L171/172 only moves `[n]\n【lab】` → label before [n] when [n] directly before label. Our reply has `[1]\n【疏文】`; L171 regex `(\[\d+\])\s*(?=【)` requires 【 immediately after optional whitespace; here newline then 【 → `\s*` includes newline, so it inserts newline after [1] → same. L172 requires `[n]\s*\n(\s*【)` → matches, rewrites to `【疏文】\n[1]`. So body becomes label-first blocks, as reviewer described.

New parser splits by line-start [n]: body after reorder:
```
【疏文】
[1]
改後疏1
【記文】改後記1

【疏文】
[2]
...
```
split yields prefix '【疏文】\n' (_pre_lab='疏文'), block1 txt='\n改後疏1\n【記文】改後記1\n\n' → prepend 疏文 → good; block2 similarly.

But wait: L171 also inserts newline before 【記文】 if [n] precedes? no [n] before 記文. Fine.

Run fixture.