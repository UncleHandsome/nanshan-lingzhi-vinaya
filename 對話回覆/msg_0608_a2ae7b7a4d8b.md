# 對話材料 #0608

- event: assistant/message
- seq: 88869
- time: 1794867667328

---

User wants 行事鈔 revision materials for the remaining 14 (unrevised FIX groups), all in **one file** (one md containing all materials), so they can run.

Build single file `測試/行事鈔_修訂_補14.md` with 14 sections, each: 原文, 目前譯文, 硬傷清單 + shared REVISE prompt at top, numbered 【1】..【14】, and mapping key.

Need list of 14 keys (FIX without revise reply). Compute and build even though previous job created folder `_hsc_rev_missing` with md files; combine them into one file with prompt + numbering.

Check `_hsc_rev_missing` has 14 md; build combined file.

Format:
- prompt (REVISE_PROMPT with {fixes} per section? REVISE prompt expects fixes embedded; so each section should include its own prompt? That duplicates. Better: common instruction + per-section 【n】key + 原文/目前譯文/必改硬傷; instruct output per number.)
- Output format: 【1】<key> then 【鈔文】...

Build with script reading `_hsc_rev_missing/*.md` (each contains prompt + sections). Extract 原文/目前譯文/硬傷; combine.

Simplest: concatenate the 14 md files with separators? They each contain full prompt → 14 prompts, acceptable but bulky. User said one file; that's fine.

Better: common prompt once + 14 sections with fields.

Write script:
- parse each md: after '（檔名：k）', 【原文】..., 【目前譯文】..., and fixes = text after last '【必改硬傷】'? The md includes fixes inside prompt at top.
- Actually md built as: REVISE_PROMPT with fixes substituted, then ---, 檔名, 原文, 目前譯文. So fixes embedded at top; extracting is messy.

Alternative: regenerate materials directly from audit replies and files, using same logic as script, and write single file with per-section fixes.

Write new script `mk_hsc_rev14_one.py`:
- keys = FIX without revise reply.
- For each: orig, cur, fixes.
- Output: header prompt (generic revise instructions), then for each `## 【n】key` with 【原文】【目前譯文】【必改硬傷】, instruct to output `【n】` + revised text.
- Save `測試/行事鈔_修訂_補14.md`.

Do it.