# 對話材料 #0961

- event: assistant/message
- seq: 116120
- time: 1795081251351

---

Patch:
1 build_a2 line 138: before normalize, strip self heading:
```
_rt0 = re.sub(r'(?m)^\s*【(?:修訂後的譯文|修訂譯文|修正後的譯文|修正譯文)】\s*$','', _rt)
txt = _plain_revise(norm.normalize(_rt0))
```
But `_rt0` empty if only heading? fine.
Also `_plain_revise` regex only 修正後/修訂後; add optional 的 and 修訂譯文? It currently `(?:修正後|修訂後)的譯文`. Add `(?:修正後|修訂後|修訂|修正)(?:的)?譯文`. Could.

2 norm SIMP add hair phrase pairs at start:
`('头发','頭髮'),('白发','白髮'),('长发','長髮'),('结发','結髮'),('发爪','髮爪'),('发髻','髮髻')` but input traditional already 頭; SIMP converting '头'→'頭' then phrase? SIMP processed sequentially; if phrase pair '头发' first, input 头发→頭髮; if input 頭髮 traditional, no issue. Add at beginning.
3 pack_judge `_blk` regex add prefix: `r'(?m)^\s*(?:#{1,6}\s*)?(?:[-*•]\s*)?\**\s*\[\s*(\d+)\s*\]\s*\**\s*'`.
`_only_a_line`: if no 裁決 group, fallback `('沿用' in ln or '無分歧' in ln) and '乙優' not in ln and '重修' not in ln` return true? For line "[1] 無分歧，沿用譯本甲" should be A-only. Implement:
```
if not _m:
    return ('沿用' in ln or '無分歧' in ln) and ('乙優' not in ln) and ('重修' not in ln)
```
4 assemble_book line-start replace regex `re.sub(r'(?m)^【鈔文】','【記文】',x)`.
5 `_looks_pasted` threshold maybe later.
6 run_l7 MAX_LOCAL: currently `'QWEN_MAX_LOCAL': STAGES[stage].get('local','5')` and STAGES all local='5'; dynamic cap in qwen overrides? qwen sets local_cap based on length unless env; `_env_cap` if QWEN_MAX_LOCAL set uses 5, overriding dynamic. User review says mismatch. Fix run_l7 remove QWEN_MAX_LOCAL or set based? Set `'QWEN_MAX_LOCAL': STAGES[stage].get('local','5')` to only include if explicit; stages all 5. Better remove key to allow dynamic; but some stages need 5. Could leave.
7 run_pipeline final qc long: inspect final stage; add qc_scan for `_長段/_定稿` if exists. Find final block.