# 對話材料 #1157

- event: assistant/message
- seq: 131975
- time: 1795241878513

---

Keys wrap S030-S057 then S001-S029? All 85, good. Counter 58正文, 26目录重复,1重复. Great! We can use judgments to clean:
- 26 目錄重複 + 1 重複 = 27 pairs remove.
- 58 真正正文: source may be correct raw; need replace source? Table gives corrected raw in column 5, but many have `<br>`; could parse and update source to raw, but translation remains; if source is merged/split, replacement may be okay.
- User likely wants apply all: remove duplicates, update raw for 正文.
- Risk; but data from AI.

Need map S keys to actual page pairs. We need reconstruct S key order from material file; it was generated sequentially across pages. We have material file `戒疏_短句_待定位_85.md` with S001...; each block source. We can map each S to existing page pair by source prefix (we did generation). To apply:
- Parse output table judgments and corrected raw column.
- For each S:
  - If 目錄重複/重複: remove pair matching material source from page.
  - If 真正正文: replace source with corrected raw (strip `【疏】`/`<br>` to plain) but page class/label; keep translation. However corrected raw may include multiple paragraphs and translation only one; could be okay.
- 58 replacements; 27 removals; page count -27.
- This is likely what user wants.

Need parse corrected raw column: table columns; `| key | 卷 | 判定 | TXT位置 | 校正後原文／備註 |`; regex row captures first 4; fifth includes `|`? Text has `|` rarely; use split.
- For each row, `parts = [x.strip() for x in line.strip('|').split('|')]`; 5 fields; corrected = parts[4], but may include `|`; join parts[4:].
- Clean corrected: remove backticks, `<br>`, `（備註...）` after; labels `【疏】` -> `【疏文】`; extract raw before `（備註`.
- For 正文, set source to `【疏文】` + cleaned raw? If source has `【記文】`? Most 正文 likely 疏/記; table uses `【疏】`; page class s/j; use existing class label.
- Remove pairs for duplicate keys by source exact/prefix.

Need map material S source. Parse material file blocks; extract `【原文】` text. Then find page pair whose source contains first 20/30 Han; replace/remove.
- Some S are duplicates; easy.

This is doable but may corrupt; user wants process. Let's implement with backup? Git restore possible.
- Use current jieshu pages; apply 85.
- Need count before; after.
- Build per volume; identify S key volume from material; remove/replace.
- For 正文 replacement, corrected raw may be **longer/multiple paragraphs**; wrap `<br>`.
- Translation existing may be shorter; okay.

Let's parse output and material; apply.