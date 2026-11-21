# 對話材料 #0685

- event: assistant/message
- seq: 97728
- time: 1794917606825

---

這輪先修最危險的兩個，其餘列清單。

## 已修

| 項目 | 改動 |
|:--|:--|
| `norm.py` | **停用 OpenCC s2t**；不再把「云／斗／几」誤轉「雲／鬥／幾」 |
| `norm.py` | 補殘留簡體處理：头→頭、鬓→鬢、须发→鬚髮、须→須 |
| `divergence` 三處 | lookahead 補 `【` 與「修訂後的譯文」，不再把第 3 欄吃進第 2 欄 |
| `qc_scan` | 律名檢查已去掉 `and not` |

驗證：`normalize('一斗　木几　論云　头发')` → 一斗　木几　論云　頭髮，古字不再被改。

## 尚未修（依你列的優先序）

| 優先 | 項目 |
|:--|:--|
| 1 | `mk_review_materials.load_pair()` 缺乙時整卷跳過 → 應給空乙、不丟卷 |
| 1 | `make_hybrid` 邊界重疊時同段建兩組 |
| 2 | `pack_judge` 漏印【記文】時靜默退回甲 |
| 2 | `pack_audit` PASS_A 漏寫時待審譯文變空 |
| 2 | `pack_final` 未先過 `col3()` |
| 2 | `qwen_local._looks_pasted` 誤殺儀式文句 |
| 2 | `local_corpus` per_book 與 layer 順序 |
| 3 | `run_pipeline` getmtime 判斷、`build_a2` 缺檔仍回 0、長段 workers 未繼承 |

## 文件

`校閱系統_程式與提示詞.md` 已重建：296.6 KB。

要我接著修第 1 優先那兩項嗎？