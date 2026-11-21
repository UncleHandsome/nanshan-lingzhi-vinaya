# 對話材料 #0934

- event: assistant/message
- seq: 114069
- time: 1795067971009

---

Sample before vs 裁決 differences are mainly removing parentheses and rewording — sample before **is a later, cleaned version** (removed parenthetical explanations per STYLE), while 裁決 has parentheses. Actually 裁決 col3 has "（僧眾有無未到）" etc; sample before removed them. That suggests sample before was produced **after** 裁決 by some cleanup? Or sample before is from another pipeline (盲翻/舊譯) that avoided parentheses.

Wait earlier we saw 裁決 col3 for 1210: "鈔文「若猶」以下，是說明檢校，也就是查核僧眾有無未到" — has "，也就是" (sample lacks? diff insert). Sample before from 第3組: "【鈔文】鈔文「若猶」以下，是說明檢校查核（僧眾有無未到）" — contains parentheses, while 裁決 no parentheses. Diff shows sample deletes/inserts in one direction relative to c; hard to read but sample has parenthetical, 裁決 cleaned. Hmm.

Key point: they are close but neither superset.

User's premise: "裁決稿應該是更新提示詞跟附母本吧 怎麼裁決後的譯文會變 又沒有重跑" — They expected 裁決 outputs unchanged; maybe they're asking why sample/裁決 differ if no rerun. Answer: the `_裁決` replies were not rerun; their mtimes/content date to 03:56. The 40 sample "修訂前" is not the 裁決 col3; it's a later/edited version (maybe 定稿 or manually cleaned). Also `_裁決/回覆/*_usage.json` was rewritten at 07:41 by hash backfill, which changed directory timestamps and made it look updated.

Need verify mtimes for others: 業疏/戒疏 裁決 files date 11/18, sample 11/19; so definitely sample not from current 裁決? If no rerun, sample before should equal 裁決; it doesn't. So previous sample run likely used another text source (maybe old 定稿 or a "final" snapshot).

Could the sample 修訂前 be `_定稿` at that time and then 定稿 later overwritten? Check 定稿 07a ratio 0.985 vs 裁決 0.985; both close. For 1210 定稿 is old fallback with "界內有無遺漏未到之人", sample differs.

Maybe sample 修訂前 = **`_終修` output col3** for keys with revise; e.g., 1210 no 終修 (PASS), then 定稿=裁決; but sample differs.

Let's search sample text in all production files to identify exact source. Use a distinctive substring and grep across 測試/重譯/資持記 files (md/txt/json) with Python; limit to md/txt under book dir, read ~thousands files maybe okay. For 1210, substring "檢校查核（僧眾有無未到）". Search.