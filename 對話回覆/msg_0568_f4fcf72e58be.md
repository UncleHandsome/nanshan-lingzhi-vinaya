# 對話材料 #0568

- event: assistant/message
- seq: 83182
- time: 1794804242164

---

Need classify: output blocks counts vs keys:
- 尼鈔: 7 blocks / 13 keys → 7 translated? Maybe each output corresponds to a key in order; 6 remain.
- 戒疏: 41 label-blocks / 22 keys; some keys need multiple labels (疏+記) so 41 blocks could cover all 22? Maybe.
- 行事鈔: 1 block / 2 keys (long segment parts) → 1 of 2.

To classify accurately, match output text to key by comparing 原文? We can't directly; but can use distinctive terms. Alternative: infer from order: model likely processed keys in sorted order, outputs in same order. Count labels per key (from material) and map sequentially.

Compute per-key expected label counts from material md (`■ lab（原文）`), cumulative, then map blocks in order. That yields covered keys until blocks exhausted.

Do that for each book; list covered vs remaining. Then write classification report into folders, update output files with labels? User asks "稍微修改一下提示詞 讓他跑出來的時候也標明一下" — modify prompt to label each output with `【書名 卷 段｜key】` or at least `[key]` header. Downstream: for manual outputs, labels help. For pipeline, extra header could break parsers (blind replies are passed to judge material builder which reads labels 【疏文】; extra line before might be okay? mk_judge `_parse_reply` may require labels at start).

Safer: add to BLIND_PROMPT a first-line metadata comment: `<!-- key: ... -->`? Model doesn't know key unless material includes it. Materials include 出處 line `（出處：《書》chunk，第 N 段）`; prompt can require: "在譯文最前面加一行 `〔出處：《書》卷，第 N 段〕`". Then mk_judge would need to strip; could add strip in build_a2/mk_judge.

Maybe user means simpler: in output.txt each block should be marked with key so easy to classify. Modify prompt so model prepends `【段號：N】`? Hmm.

Given ambiguity, implement lightweight: modify BLIND_PROMPT to require first line `〔本段：<出處>〕` derived from material 出處, and add strip logic in mk_judge/mk_audit to remove that line. But risk.

Alternative non-prompt: create a manifest/classification file per book mapping output blocks to keys; and for future runs set qwen to save each reply with header. But user explicitly says modify prompt.

Compromise: add one line to BLIND_PROMPT: "譯文最前面請加一行出處標記：`（出處：《書名》卷次，第 N 段）`，僅此一行，勿再加其他說明。" Then update mk_judge `_parse_reply`/build_a2 to strip leading `（出處：...）` line. This is manageable.

But blocked outputs are manual, no prompt. Classification still by order.

Let's first classify outputs by cumulative labels:
- For each key sorted, expected labels count from md.
- Map output label-blocks sequentially; mark keys fully covered; partial for last.

Compute and write 00_分類.md in each 重翻/<book>, listing covered and remaining keys.

Then modify prompt + strip.

Then report and continue B (check judge job status).