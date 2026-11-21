# 對話材料 #0356

- event: assistant/message
- seq: 70064
- time: 1794745948560

---

No packed materials with anchors in 尼鈔 — meaning 尼鈔 out materials aren't packed (the 打包 was only in 測試/_e2e5?). So old 尼鈔 replies are one per segment. Old done 737, whole-matched 304 → because new grouping packs segments (new packing rules) so new groups combine 2-6 old segments; whole sig won't match single-segment old reply.

Fix: for new packed group, if every constituent segment appears as its own old group (single-segment material), assemble [n] + each old reply. Our seg_map built only from packed old materials with anchors — need to build from single-segment old materials too: map norm(src) → reply for groups with exactly 1 segment.

Add: for old materials with single block and no anchors → seg[norm(block)] = reply (strip label in reply? reply may include 【鈔文】 prefix; when assembling need inner text).

This will recover 尼鈔 433, 行事鈔 527, 義鈔 57, and maybe 業疏/戒疏 unpaired singles? For 業疏 old singles don't exist.

Implement:
- In old_maps: if one block and no anchors → key norm(block) → reply with leading 【x】 line stripped (take text after first line if starts with 【).
- Assembly for new group: if all segments mapped → join.

Let me patch and rerun.