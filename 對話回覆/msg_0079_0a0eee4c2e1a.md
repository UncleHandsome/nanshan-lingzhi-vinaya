# 對話材料 #0079

- event: assistant/message
- seq: 27835
- time: 1794059474764

---

The 戒疏 out/段 uses labels 【律文】/【疏文】 per paragraph. And source chunks contain 【記】/【疏】 labels (113 hits). So t3's 原文 with 【疏】【記】 is a combined block from the source, and the 段 numbering doesn't match.

But the matching key: orig begins "【疏】【記】五十三..." — after norm (which doesn't strip 【】), the key "【疏】【記】五十三。「擊攊」" won't match any single source paragraph because source paragraphs may be separate.

Fix: strip 【...】 labels and use a key from the actual text ("擊攊，謂以手捵弄腋下") — that's the 記 text within the chunk? Since source has 【記】 labels, paragraph content includes them.

Let me check a source paragraph containing 擊攊.

Given context, I'll just note t3 needs a specialized matcher and is 223 items — a big batch requiring its own pass. Report status and ask whether to proceed with t3 after t2 (or clarify its source).

Actually the user said "繼續 還有 t3" — they want t3 processed too. I can say: t3 is 3.5x bigger (223 條), its 原文自帶【疏】【記】標記、段號與 chunk 對不上，需要改用「引文比對」定位；我正在處理。

To make progress, implement label-stripping and inner-text matching:
- norm: add 【】 to strip list.
- For matching: try key from orig after removing leading labels; if not found, try a 12-char window from the middle? Simpler: strip all 【…】 then take first 14 chars.

In this example, after strip: "五十三。「擊攊」，謂以手捵弄腋下..." — the chunk paragraph beginning "五十三" may exist in 記 portion.

Let me test: does source contain "五十三。「擊攊」"?

Quick grep 擊攊 in source shows 5 hits. So likely a paragraph contains it.

Let me patch norm to strip 【】 and also remove 【疏】【記】 prefixes automatically (norm does). Then re-parse t3 and see ok count.

Do it.