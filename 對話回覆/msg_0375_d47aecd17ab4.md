# 對話材料 #0375

- event: assistant/message
- seq: 71271
- time: 1794750360542

---

補丁全部套用完成，並驗證通過。

## 六組 Patch 對照

| # | 檔案 | 狀態 | 驗證 |
|--:|:--|:--|:--|
| 1 | `mk_review_materials.py` `emit()` | ✅ 已補 `body_prompt` | 材料首行為提示詞 |
| 2 | `merge_long.py` | ✅ 只剝第 2 段後標籤、`''.join`、`norm.normalize()` | 已加 `import re` |
| 3a | `SRC_RE_ALL` 邊界 | ✅ | 短句抓到 4 字 |
| 3b | `_quota()` 死碼與 `QWEN_MAX_FETCH` | ✅ 獨立覆寫 | `MAX_FETCH=2` → `(1,2)` |
| 3c | `src_hash` | ✅ 由 `src_text` 算 md5 | 實跑寫出 `b23cae598104` |
| 3d | NO_WEB 書單 | ✅ 補 5 部 | 22 部齊全 |
| 4a | `mk_judge` 支援律／註／序 | ✅ 改用 `units`＋`_pick` | 譯本甲不再空 |
| 4b | `split_sj` 去標籤 | ✅ | |
| 4c | 三支 `col3()` 剝括號 | ✅ | 三支皆回 `【鈔文】\n甲句。` |
| 5 | `local_corpus` 濟緣記別名 | ✅ | `→ 濟緣記` |
| 6 | `norm` 標籤換行 | ✅ | `【鈔文】\n第四…` |

## 過程中修掉的兩個自己造成的問題

| 問題 | 處理 |
|:--|:--|
| 改 `col3` 時切片切壞 `mk_audit_materials.py` | 已修復，語法 OK |
| helper 未定義就被呼叫 | 三支都補上 `_strip_head_paren()` |

## 全套語法

✅ 全部檔案通過。

## 目前狀態

| 項目 | 值 |
|:--|:--|
| 待翻 | 9,184 組（混合切法） |
| 測20b | 完成，報告已出 |
| 執行中 | **0** |
| 文件 | 需重建以同步新 patch |

要我重建文件，然後開跑嗎？