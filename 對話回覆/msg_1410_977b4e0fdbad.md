# 對話材料 #1410

- event: assistant/message
- seq: 139737
- time: 1795256072343

---

We have 4 true nicao translations with source/tr. Need add to canonical `nicao.jsonl` and render? We can add rows to canonical, then later render.

- Need current gaps H003,H012,H013,H014 positions; add canonical rows with vol/chunk, raw_start.
- Source/tr provided. Add key `G003` etc.
- Then canonical nicao 778 units.
- Render nicao? Not yet; but data.

Need determine raw positions for each source:
  - H003 `相。若僧時到...` find raw q at 5607 gap; current page gap; source begins `相。`; find exact at gap? Use `raw.find('若僧時到，僧忍聽，僧今於此四方相內結大界')` near 5607.
  - H012 `大德僧聽！此比丘尼某甲...` q 74427.
  - H013 q80354.
  - H014 q87184.
- Add rows with segments one `【鈔文】`.
- vol/chunk based on q: H003 卷上, H012/H013/H014 卷下.
- Need ensure no duplicate key.
- Write canonical and commit.

Do.