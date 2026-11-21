# 對話材料 #0959

- event: assistant/message
- seq: 116110
- time: 1795081222777

---

User says continue: likely fix remaining medium/low-risk bugs from review. Need prioritize and implement feasible ones:

4. norm/build_a2 label & 髮:
- add LABEL_FIX for 【修訂後的譯文】 etc; treat self labels as strip? `LABEL_FIX` maps None→current lab; better add keys with None still converts to label; duplicate. We could fix build_a2 dedupe already handles single mismatch? Earlier shared repair replaces first label only; if duplicate labels, qc flags. Need check current build_a2 normalization order: we fixed earlier to normalize first then prepend; duplicate maybe solved? Review may be stale. Verify quickly.
- Hair: current regex only preceded by hair chars; SIMP converts 发→發 globally unless protected. `頭髮` would become `頭發` due SIMP pair ('发','發')? There is no single 发 in SIMP? Check. Earlier added SIMP chars? Search. If SIMP has '发'→'發', `頭髮` (髮 traditional) unaffected. Issue only if input uses 发 simplified: 头发→頭发 then SIMP→頭發 wrong. Could add VAR/word conversions: 頭髮/白髮/長髮/結髮/髮爪. Add SIMP phrase pairs ('头发','頭髮'), ('白发','白髮'), ('长发','長髮'), ('结发','結髮'), ('发爪','髮爪') before single conversion. SIMP iteration order matters; add at start.
- `复` add ('复','復')? ambiguous 複; qc flags; add maybe ('复','復') risky. skip or add common phrases.
- LABEL_FIX add `【修訂後的譯文】`: currently None means replace with current lab, not strip. If model writes heading and no label, build_a2 normalize turns to lab then prepend check sees label, okay one label. Duplicate? If txt already includes 【記文】 plus heading, normalize turns heading into 【記文】 duplicate. Better add a pre-clean in build_a2: remove lines `^【(?:修訂後的譯文|修訂譯文|修正後的譯文)】$` before normalize. Also in norm LABEL_FIX maybe map to ''? It uses `_target or ('【%s】'%_lab)`, so can't strip; set target '' still falls back. Could modify LABEL_FIX handling: if _target == '': remove; but values None currently. Add new dict separate? Simpler build_a2 preclean.

5. pack_judge regex allow prefixes `(?:[-*•]|\d+[.、])?` and headings; plus `_only_a_line` fallback if no 裁決 group and line contains 沿用/無分歧 → treat as A-only. And dead branch `i not in _by_i...`? Lower priority.
6. long split quote, long audit check, final qc long: implement?
- `split_sentences` second pass could avoid splitting inside quotes; complex. Skip.
- run_long_audit check=False → user review says should abort on partial; earlier deliberately changed to continue. Maybe revert? Risk. Skip.
- final qc long: add in run_pipeline final stage qc_scan for _長段/_定稿 if exists. Could implement.
7. assemble_book regex line-start replace.
8. wait_done strict set check.
9. _looks_pasted threshold.
10. mk_review len mismatch warning (already has warning, skip).
11. run_l7 env mismatch (MAX_LOCAL 5; tools branch) — could fix.

Time/token: ~? We have 17k? Let's implement high-value medium:
A. build_a2 preclean self headings + norm hair phrases.
B. pack_judge prefix regex + only_a fallback.
C. assemble_book line-start replace.
D. run_pipeline final qc long; wait_done strict maybe.
E. _looks_pasted threshold (raise to 24/longer).
F. run_l7 MAX_LOCAL dynamic/stage.

Focus A-C, maybe E.

Check current build_a2 around fallback; add preclean:
```
_txt = re.sub(r'(?m)^\s*【(?:修訂後的譯文|修訂譯文|修正後的譯文|修訂後譯文)】\s*$','', _rt)
```
in fallback before normalize.

Norm hair: add phrase pairs at top of SIMP. Locate SIMP start line ~57; insert.

Pack_judge `_blk` regex line ~? add prefix. `_only_a_line` fallback:
```
_m=re.search(裁決...); if _m: group; else:
   if '沿用' in ln or '無分歧' in ln: return True
```
Also current `_only_a_line` requires 甲優; review says `[1] 無分歧，沿用譯本甲` should count. Add.

Assemble_book replace line.

Let's inspect exact sites.