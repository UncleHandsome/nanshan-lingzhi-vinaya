# 對話材料 #0827

- event: assistant/message
- seq: 109763
- time: 1795054574565

---

Findings:

1. `split_units` in mk_judge: if body starts with untagged 疏文 then 【記文】, parts = ['疏文譯文\n\n', '記文', '記文譯文']; loop range(1,2,2) → i=1: out['記文']; parts[0] dropped. BUT fallback: `if not out and body` — out non-empty → dropped silently. Confirmed claim #2. Severity: real.

2. pack_judge: per_group splits each lab chunk by [n] markers; if 記文 chunk lacks [n] (because [2] stayed in 疏文 chunk), then `per_group` for n=2 has 疏文 only; `_jia_group(2)` returns 譯本甲 units; later logic: for n where raw_segs missing 記文, it may fill from jia. Need read 245-300 to confirm silent fill. Likely yes (claim #1). Confirm by simulation or reading.

3. local_corpus has no VAR_MAP attribute (it's in norm.py). The claim references local_corpus L38 `_VAR_MAP` — maybe named `VAR` or `_VAR`. Let me check the actual normalization function in local_corpus (there's `_plain`); find its map.

4. ALIASES check failed because script errored before. Rerun with correct names.

Let me inspect local_corpus top for var map and ALIASES, and read pack_judge 245-300.