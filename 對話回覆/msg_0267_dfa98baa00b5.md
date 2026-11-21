# 對話材料 #0267

- event: assistant/message
- seq: 62013
- time: 1794625739742

---

The revision replies (修訂0) don't have a "修正後的譯文" heading because the revise prompt asks for plain output (【疏文】……). So col3 raises.

Fix: in build_a2, for FIX branch, use a tolerant extractor: if '修正後的譯文' present use col3; else use whole text (strip leading prompt-ish lines).

Let me patch: add col3_soft(rt) = try col3 else return cleaned text.

Also strip '【疏文】/【記文】' label lines? For final assembly we want labels preserved? The final output should be translation text; keeping labels helps. I'll keep them but strip leading whitespace.

Let me patch.