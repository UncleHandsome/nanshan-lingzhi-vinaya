# 對話材料 #1229

- event: assistant/message
- seq: 133719
- time: 1795246283254

---

Need rebuild nicao from terminal + revision replies. Need do carefully:
- 774 `_終審` units; `_終修/回覆` replies count? Build map.
- Each terminal `【原文】` may have `■ 鈔文（原文）`; translation `【待審譯文】` or reply.
- Need split by type? Source may contain multiple `■` markers; translation labels; build pairs per type/segment.
- Current pages 884; rebuild from 774 units likely fewer; long sections/12 punctuation? Terminal source unpunctuated, but nicao raw no punctuation; long sections maybe.
- User wants correct alignment; rebuild is right.

Need inspect terminal structure/count: `_終審` 774? `_終修/回覆` replies count. Use script.
- Parse each unit:
  - `【原文】` section; markers `■ 鈔文（原文）`, maybe `■ 註文` etc; source body.
  - translation: reply if exists else `【待審譯文】`; split by labels `【鈔文】`/`【註文】`/`【序文】`.
  - Pair by type/order; preserve segmentation.
- Build pages by volume from key prefix (`00_卷首`, `01a_卷上之上`, etc.) and h2 chunk.
- But current pages have 12 punctuation fixes and ten precepts; rebuild from terminal loses them. Could apply punctuation later; but user wants proper rebuild; okay.
- Need preserve **long sections**? Terminal may include long sub-units? Nicao `_終審` 774 vs current 884; long sections separate; rebuilding loses long 110 pairs. Hmm.
- Current 884 includes 774 general +110 long? Nicao long files maybe 10 sections split; need add later.

Given destructive risk, perhaps rebuild **translation mapping only**:
- Keep current page pairs/source/punctuation.
- For each pair, find terminal source match; replace translation with terminal/reply translation. Unmatched (background/long) flag/remove.
- This fixes mispairing without losing content.
- Current 884; terminal 774; 110 unmatched likely long; preserve.
- For each page pair source `o`, find terminal source normalized exact; if found, set `t` = terminal translation (or reply).
- If terminal has multiple types, page pair may be split; need map by type and segment. Current page pairs mostly one type; can map.
- For source `第一簡請`, no terminal `【原文】`; stays; should remove or mark. Could remove pairs with no terminal match and source not in long? But 110 long may be valid; don't remove.
- Count unmatched and inspect; likely mispaired background.

This is safer. User says rebuild nicao, but translation remap is rebuild alignment.

Need implement:
1. Build `term_map` from all `_終審` files:
   - key, raw source, translation (reply if exists else 待審).
   - Parse multiple `■ type` segments; map each segment source -> translation segment by type.
2. For each nicao page pair:
   - source body, type label.
   - Lookup by normalized source exact (or first20).
   - If found, replace translation with matching translation; if not, count.
3. Check result; commit.

Need know reply path `_終修/回覆/<key>_回.txt`; key from filename.
- For each terminal file, reply file same basename `_回.txt`; use if exists.
- Translation may contain labels; split by `【鈔文】` etc; map type.
- If translation only one type and source one type, okay.

Let's write script; output stats; build `.new` maybe. Use current pages; don't commit until check.

Parsing terminal:
```
i=【原文】; j=【待審譯文】; raw=t[i:j]; tr=t[j:e]
markers = re.finditer(r'■\s*(鈔文|註文|律文|序文)（原文）', raw)
for each segment: source text; type
translation labels: split `【type】`; if no labels, assign to first/only.
```
- `raw` may include `【裁決】` after? split.
- Reply translation may have `【鈔文】`.
- Build map `han(src)` -> translation segment for type.

Page pair:
- source `【鈔文】...`; find md5? use exact `han(o)`; if no, first20.
- If found, set t to mapped translation (with label).
- Count hit/miss.

Do stats first (not write).