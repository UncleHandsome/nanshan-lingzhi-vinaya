# 對話材料 #0003

- event: assistant/message
- seq: 248
- time: 1793881646409

---

site2.py builds the website straight from TXT_分卷 + AI語譯/out. Any edit to out/*.txt changes the site after re-running site2.py. Also 白話 PDFs need rebuilding (build_book.py + LibreOffice conversion).

Now for the 4-layer labels: commit 8159a1f "戒疏：四層標籤（律文/註文/疏文/記文）" — so 戒疏 already applied. Let me check the current state of 02_戒疏 out files for 【律文】 etc, and 業疏.

Also check docs/jieshu page for whether labels show.

Then determine what remains for item 2: probably 業疏 (疏/記 layers need structure; source has no labels in TXT_句讀?), 行事鈔 (鈔/註?), and the 合編.

Let me count label occurrences in out/ per book.