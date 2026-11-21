# 對話材料 #0196

- event: assistant/message
- seq: 57235
- time: 1794606823587

---

The user pasted a detailed review with concrete patches. They want me to apply these fixes presumably. The message doesn't explicitly say "apply", but the context implies: they're giving the fixes; I should implement them.

The list:
Code fixes in qwen_local.py:
1. 400 data_inspection_failed → fallback to clean text-only single round; if still blocked, save _400審查.txt.
2. Token blowup fixes:
   - count searches before cache check (so cache hits count)
   - web_fetch limit MAX_FETCH_PER_GROUP=2
   - trusted=False suppression when >=2 trusted
   - MAX_TOOL_ROUNDS 15 → 7, MAX_SEARCH 4 → 3
3. max_rounds fallback missing usage accumulation + _usage.json
4. mk_review_materials.py:
   - strip 【疏文】/【記文】/【鈔文】 prefix from o[k] in emit
   - _nicao_prompt() remove '或「銜接記文釋字須附原字」'

Prompt tweaks (4):
1. 第3欄格式: add "只輸出白話譯文，嚴禁在譯文開頭重貼原文或標點版原文。"
2. 分段後: "小標題後是否換行、以及長段問答或宣唱白文的外層引號，須與【現譯】或前後保持一致，勿任意半途刪去。"
3. 第1欄第1點: after 偷搬記文 add "（唯原譯已作簡短消歧義而刪掉會變質者除外）"
4. 括號條: 禁用審校標籤 → 禁用「（未改）」「※修正」等審校流程標籤

Let me implement all of these precisely.

Steps:
1. Edit qwen_local.py:
   - constants: MAX_TOOL_ROUNDS=7, MAX_SEARCH_PER_GROUP default 3, add MAX_FETCH_PER_GROUP=2
   - web_search: move counter before cache; add trusted suppression
   - web_fetch: add fetch counter
   - run(): add _save_result helper; catch RuntimeError 400 data_inspection_failed → fallback; ensure max_rounds path accumulates usage and saves
2. Edit mk_review_materials.py: strip prefixes in emit (both o[k] uses); _nicao_prompt removal.
3. Regenerate prompt-dependent files? The prompt changes affect materials; need to regenerate 20組_4段? The user says "把這幾個地方修完後...可以直接放量跑". Materials regeneration would be needed for new runs. I can regenerate the 20集 sample or not. I'll note it.

Also update the combined doc afterwards.

Let me implement carefully using edit tool on specific blocks. Need to read current relevant sections.

Let me read the run() function and web_search/web_fetch current state.