# 對話材料 #0002

- event: assistant/message
- seq: 160
- time: 1793881600032

---

User clarified: 行事鈔／戒疏／資持記 have no manual punctuation (句讀) — that's fine, they already have punctuation from the base text. So TODO #3 (句讀) isn't needed... wait, TODO item 4 was 句讀. The user says no problem. So we focus on the first three items as instructed.

Let me acknowledge and continue exploring efficiently. I need to:
1. Fix the remaining review items (~1005) → apply fixes to AI語譯/out/<book>/<key>.txt
2. Four-layer labels: build structure data mapping each segment to 律/註/疏/記, and add tags to translation
3. Annotations: 度量衡換算表、反切拼音、生僻字注音、學悔沙彌說明

This is a big job. Let me plan properly.

First, understand how the source text is labeled. In 戒疏/業疏 (會本), source lines start with 【疏】【律】【註】【記】. In 行事鈔 and 資持記? Let's check what labels appear in TXT_分卷 files.

Let me check the structure of the source files and translation files, and check whether translation already has labels like 【疏】.

Also look at build scripts used for the actual books: build_vol.py / build_reflow.py / build_ju_dui.py / hebian.py etc. Which one produced the current PDFs? Need to know which builder to re-run after edits. Let's check timestamps and the 白話 output (PDFs built at ~08:00-08:20?). Let me check PDF mtimes and DOCX folder.

Plan of attack for item 1 (1005 review items): 
- For each review item: locate file (from filename), seg index into translation paragraphs, apply "fix" text. But "fix" is a suggested rewrite, not always a full replacement; sometimes it's a note. E.g. kind=術語錯誤 fix might be "X→Y". Careful application needed. Given ~1005 items, use an LLM (subagent) per batch to apply fixes with context, writing updated segments. That's the realistic approach: batches of ~20-30 items, each subagent reads the file segments and writes corrected paragraphs. Then verify counts unchanged (paragraph count must be same) and backup.

But careful: subagents editing files directly could conflict. Better: subagents in a workflow return JSON of {file, seg, newtext} and a single script applies them, verifying. That's the pattern used in _work/fix_batches*.json apparently (batch_fix_all.py). Let me look at batch_fix_all.py to reuse the existing pipeline.

Item 2: four-layer labels. Need per-segment layer data. For 戒疏/業疏, source lines have labels already 【疏】【律】【註】【記】. For 行事鈔 (T40 no.1804), the structure is 鈔文 with 註 maybe? And 資持記 is 記文 alone. The 合編 combines 行事鈔 + 資持記. So "四層標籤【律】【註】【疏】【記】" applies to 戒疏/業疏 (會本) mainly, and 行事鈔 has 【律】quotes and 【註】? Let me check actual occurrences.

Then translation labels: 【律文】【註文】【疏文】【記文】.

Item 3: annotations — 度量衡換算表 (already exists as 附錄_名相與度量衡.md at root?), 反切拼音, 生僻字注音, 學悔沙彌說明. Probably: build an appendix/annotation system and insert notes into books? Let me read 附錄_名相與度量衡.md.

Let me read a bunch of things at once: 附錄_名相與度量衡.md, chk_all_counts.py, batch_fix_all.py, and grep label occurrences.

Also need to know: does the report say PDFs = 86 files? Currently 白話 has how many PDFs? Let me count.

Let me proceed with several parallel reads.