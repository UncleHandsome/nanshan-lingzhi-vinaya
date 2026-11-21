# 對話材料 #0532

- event: assistant/message
- seq: 79738
- time: 1794789128634

---

Continue fixing remaining high-value items. Which are still unfixed:

1. local_corpus ±2 lines window size mismatch → implement character-based window: use pad chars (e.g., 400 chars) around anchor instead of fixed 5 lines. Find() currently uses lines lo/hi; change to accumulate chars around idx until pad chars. Simpler: estimate chars per line and choose line span = max(1, pad // avg_len) each side, capped. Implement per-book: compute avg line length from rec plain; use window chars pad=240: span = max(1, pad // max(10, len(r['plain']))) and build window from lines idx-span..idx+span with total chars cap.

2. _split_work compound name: if matched short prefix but rest starts with another book name (e.g., '資持記'), don't treat as work; return None, full query. Implement: after match nm, rest; if rest starts with any known book/alias → return None, q.

3. _save_result empty/content_filter → treat as fail (don't write _回). Add checks.

4. token length check use _plain before length; also fallback terms ['戒律'] issue: in local_corpus find, after filtering terms<2, if empty fallback shouldn't join into one term; better warn. Implement in qwen local_search: compute plain tokens via _LC._plain and check.

5. DeepSeek empty results not cached: in _cached_or_fetch, skip cache write if kind search and no results.

6. stop check in retry sleeps: add stop flag checks in qwen_post and _ds_post sleep loops.

7. pack_judge clear old out .md/.json and _拆回 before packing/splitting.

8. do_split single-char labels normalization (【疏】→【疏文】) before split.

9. pack_judge nonzero exit on bad? run_pipeline should stop if _拆回異常 exists: in pack_judge main after split, if bad: sys.exit(3)? run_pipeline call would fail → stops. Implement.

10. run_pipeline _mat/_blind prefer _hy only if newer than _材料/_盲翻? Simplest: if _hy exists AND _材料 not newer → use hy; else use 材料. Implement.

11. qc duplicate labels: use per-label line-start count (we did) — verify code handles single-column duplicate (yes any count>1). Pair symbols 『』（）《》〔〕 we added? Earlier added; verify.

Implement batch; time limited. Prioritize 1,2,3,5,7,8,9,10. Syntax check, rebuild doc, summarize.