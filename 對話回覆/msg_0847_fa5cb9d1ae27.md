# 對話材料 #0847

- event: assistant/message
- seq: 111041
- time: 1795055897748

---

Review of 7 prompt-level issues. Several are stale (many already addressed this session):
1. STYLE 4 quote contradiction — current text: "忠實對譯之典籍原句與儀軌（保留「某甲」）、注疏舉所釋原詞，以「……」包圍（不得夾雜未譯文言或半文半白）；...注疏體例先引原文再白話者，引號內只放原文原句..." Indeed contradictory: first says quoted translation must not contain untranslated classical; second says quote holds original. Need clarify two modes: (a) 忠實對譯之引文 = 白話譯文 in quotes? Actually original design: direct quotes of sutra text are translated faithfully but kept in 「」 to mark quotation; so inside quotes is 白話譯文 of a quote, not raw classical. (b) 注疏「先引原文再白話」 = quote raw original then explain outside. Contradiction is real. Fix wording: 
- 「忠實對譯之典籍原句與儀軌、注疏所釋原詞：引號內放白話譯文（不得夾雜未譯文言或半文半白）」 — original intent (quotes mark translated citations, not verbatim).
- 注疏體例「先引原文再白話」：引號內放原文原句，白話在外；兩者不得混用.
Then qc_scan flags 引號內 ≥10 Han + ≥2 白話詞 — that would flag mode (a)! qc_scan check contradicts mode (a). Need align qc_scan: only flag if quote contains 白話長句 AND... hmm mode (a) quotes are 白話 by design, so qc_scan's "引號內疑白話" check is wrong for mode (a). Unless mode (a) applies only to 儀軌/短語? The rule says 典籍原句與儀軌以「……」包圍 — these are translated into 白話; so quotes contain 白話. Then qc check must be removed or narrowed to 半文半白 only (文言+白話 mixed), not pure 白話.

Given complexity, decide design: Which convention does corpus use? In published 白話 books, quotes 「」 usually contain translated 白話 of citations. So mode (a) is dominant. Then qc_scan's "引號內疑白話" check is a false-positive generator (I added it this session!). Need to remove/narrow it. Reviewer says qc_scan flags pure 白話 quotes; contradiction.

Best resolution: 
- STYLE 4 rewrite clearly: 引號內一律放「白話譯文」（逐句對譯），不得夾雜未譯文言或半文半白；原本無引號之文句要加引號需查證逐字引用；注疏體例「先引原文再白話」僅適用於原文本身即以引號標示之情況? Hmm but we added the "原文原句" rule earlier at user request (review said quotes should be raw original?). Ugh.

Recall earlier: we added "注疏體例先引原文再白話者，引號內只放原文原句..." based on prior review. That rule was to fix examples where translation quoted original then explained. Now this review says it contradicts the earlier half and qc_scan. We need a coherent convention. Which is actually used in corpus? Check a published 白話 sample with 「」 to see whether quotes contain 白話 or 文言.

Let me inspect a few lines from 白話 docs for quotes. Quick.

2. 科判短語 undefined — add definition to STYLE 1: "純科判綱目短語指獨立成行或分科標目（如「初明宗」「二辨體」），不含嵌在散文中的行內導語". Useful; add.

3. JUDGE template `[n]` confusion + two packing rules conflict. Current JUDGE format line: `[n][疏/...]`（單段不加編號）. Reviewer suggests main template only `[疏/...]`, [n] only in packing rule. But pack_judge RULE requires `[1][疏]` line-leading for split. If single segments have no [n], fine. For packed, model follows RULE not JUDGE format. Change JUDGE format to `[疏/記/鈔/律/註/序] 原文…` and keep "單段不加編號；打包時依【併批裁決要求】". But pack_judge's own RULE already says `[1][疏]`. Then no conflict. However mk_judge for packed short-segment groups (review materials packed, not pack_judge) uses `【分段要求】` requiring full [1][2] output; format template without [n] might confuse. Hmm: mk_judge passes fmt via BC.fmt_for? For packed materials, judge prompt's out_format may include [n]? Check mk_judge code: `fmt` maybe from md packed. If format needed, keep a dual note.

Simplest: in JUDGE_PROMPT, change fixed format to `` `[疏/記/鈔/律/註/序] 原文「……」｜……` `` and add sentence: 「打包時每條前加 `[n]`，依材料附的【分段要求】或【併批裁決要求】決定是否需逐條全列。」 This resolves both: single no [n]; packed rules distinguish full-list vs changed-only.

4. SHUJI_CTX missing 記文 疏云/鈔云/文云/注云 sentence. Add to SHUJI_CTX[1] or [0]: e.g. append to CTX[0]: 「記文之「疏云／鈔云／文云／注云」須依所釋之書判讀；」. Then all 疏記 prompts get it (review/audit/blind). Good.

5. AUDIT 撞義詞 broad + 逐句簡核 output bloat. Change AUDIT search trigger: 「古今撞義詞」→「疑似古今撞義且影響義理者」? And 逐句簡核: soften to allow grouping: "顯明無誤之句可合併略記，僅關鍵轉折、疑點與有誤須逐句比對". Reviewer recommends with L7 validation; but cost issue real. Implement softened wording (not remove), low risk.

6. REVISE scope ambiguity "另須符體例硬規" → change to "（僅限清單涉及之句）另須符..." and add tag whitelist to output line: 「標籤僅限【疏文】…【序文】，不得自創（如【修訂譯文】）。」

7. NO_TOOLS_SYSTEM lacks "僅供防誤展開，正文依體例" qualifier — add.

Also mk_punctuate note about 云/曰 colon — optional; fix wording.

Plus qc_scan quote check alignment with final STYLE decision.

Let me inspect actual quote usage in 白話 outputs to choose convention. Sample from 白話/*.txt? Files are docx; maybe TXT in 白話? Use docs or 定稿 txt. Grep 測試/重譯/業疏/_定稿 for 「 patterns; print a few lines with quotes.

Let's look.