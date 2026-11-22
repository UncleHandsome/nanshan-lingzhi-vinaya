# `_src` 腳本索引（2026-11-17）

> 全部 542 支保留，不搬動，避免 import 與 `_src/xxx.py` 路徑斷裂。
> 本檔只做分類，方便找檔。

## 一、今晚量產入口

| 腳本 | 用途 |
|:--|:--|
| `run_night.py` | 雙線啟動（A/B） |
| `run_night_a.py` | A 線：長段＋戒疏（`.qwen_key`） |
| `run_night_b.py` | B 線：業疏＋資持記（`qwk`） |
| `run_long_parallel.py` | 四書長段平行裁決 |
| `run_all_books.py` | 盲翻＋長段 |
| `run_pipeline.py` | 裁決→終審→修訂→定稿 |
| `qwen_local.py` | API 執行器 |
| `stop_all.py` | 停止 |

## 二、材料產生

`mk_review_materials.py`、`mk_blind_materials.py`、`mk_split_blind.py`、`mk_draft_materials.py`、`mk_split2_materials.py`、`mk_materials7.py`、`mk_judge_materials.py`、`mk_audit_materials.py`、`mk_revise_materials.py`、`mk_long_judge_materials.py`、`mk_long_judge_from_mapping.py`、`export_materials.py`、`prep_yeshu_b.py`

## 三、打包／拆回

`pack_judge.py`、`pack_audit.py`、`pack_final.py`、`split_pack.py`

## 四、定稿／回拼

`build_a2.py`、`build_book.py`、`build_ju_vol.py`、`assemble_book.py`、`merge_long.py`、`apply_long_judge.py`、`backfill_usage.py`

## 五、長段

`run_long_audit.py`、`run_long_missing.py`、`merge_long.py`、`mk_long_*`、`mk_pian_split.py`

## 六、網站／匯出

`site2.py`、`site_hebian.py`、`site_ju.py`、`site_assets.py`、`render_zhichi.py`、`validate_site.py`、`export_hsc_out.py`、`export_yichao_out.py`、`export_nicao_out.py`

## 七、QC／檢查

`qc_scan.py`、`qc_revise_diff.py`、`mk_qc_full_materials.py`、`check_stage.py`、`check_structure.py`、`check_selfclaim.py`、`chk_all_counts.py`

## 八、正規化／工具

`norm.py`、`materials_io.py`、`book_config.py`、`local_corpus.py`、`mark_same_judge.py`、`toc_rules.py`

## 九、手動修補／一次性

`apply_*.py`、`fix_*.py`、`_fix*.py`、`_patch*.py`、`_repair*.py`、`_freeze*.py`、`_wire*.py`、`_final*.py`、`mk_nicao*.py`、`mk_test*.py`、`mk_supplement.py`、`mk_revise_9.py`、`mk_revise_book.py`、`mk_jieshu_missing.py`、`mk_hsc_rev14_one.py`

這些多為當時個案修補，保留供追溯，不再當日常入口。

## 十、實驗／舊版

`run_l7.py`、`run_json_smoke.py`、`mk_dialog_with_src.py`、`mk_general_*`、`scan_*.py`、`review_*.py`、`batch_stats.py`、`locate_*.py`、`mech_check.py`、`unify_pini.py`、`yeshu_*.py`、`_mw_*.py` 等。

## 規則

1. 新增正式腳本請在上表登記。
2. 一次性修補用 `_` 或 `apply_` 開頭，勿混入量產入口。
3. 不確定是否還在用時，先 `grep` 有無被 import／`_src/` 呼叫，再決定封存。

## 20K 再審（定稿後複核）

`mk_reaudit_materials.py` → qwen → `split_reaudit.py` → `mk_rerevise_materials.py` → qwen → `apply_reaudit.py`

- 來源只讀 `定稿/<book>.jsonl`
- 一份 `.md` 約 20K 字
- `split_reaudit.py` 驗證 `[01]..[N]`、400／截斷對半切
- 只修 FIX 單位，PASS 不動
