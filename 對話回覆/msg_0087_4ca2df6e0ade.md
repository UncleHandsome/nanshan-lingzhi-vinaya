# 對話材料 #0087

- event: assistant/message
- seq: 28892
- time: 1794087411475

---

Found it: packs 15–18 have massive repeats (317, 500, 752, 311)! The report quoted 1186 段 and 1417 段 — exactly packs 16 and 17.

So the data IS corrupted in packs 15-18. Why? Those are likely the 業疏 group (yeshu_docx_items). The docx reader pairs 【疏】 with next paragraph if not starting with 【 — but in the docx, often the layout is: 原文段, 譯文段, 原文段, 譯文段... Some 譯文 may start with 【? No.

More likely: the docx contains 原文/譯文 pairs where the translation paragraph sometimes itself starts with 【 (e.g., 【記文】 labels), so my loop mis-pairs: when nxt starts with 【, I skip pairing and increment i by 1, then treat 譯文 as orig with next as its translation — cascading.

That would produce wrong pairs but not duplicates.

Duplicates arise if the same paragraph text is reused as "translation" for many origs — e.g., if docx has long series of 【疏】 paragraphs followed by translations? Hmm.

Wait packs 15-18 counts: 1453/1186/1417/1113 segs. 業疏 docx items count earlier ~? Let me check which group each pack belongs to via index.tsv.

Let me read index.tsv to map packs to groups.

Also inspect pack 17 around a repeated translation to see the pattern.

Let me check.