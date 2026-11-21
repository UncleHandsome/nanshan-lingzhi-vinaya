# 對話材料 #0845

- event: assistant/message
- seq: 110450
- time: 1795055419234

---

本輪把 review 中已確認、尚未修的 9 項全部修完；每項都做最小驗證。

## 程式修正

| # | 位置 | 修正 | 驗證 |
|:--|:--|:--|:--|
| 1 | [mk_judge_materials.py:87](_src/mk_judge_materials.py#L87-L96) | `split_units` 保留 `parts[0]`：開頭未寫標籤的疏文歸 `default_lab`，不再整段丟棄 | `疏譯A／【記文】記譯B` → `{疏文:疏譯A, 記文:記譯B}` |
| 2 | [pack_judge.py:226](_src/pack_judge.py#L226-L250) | 標籤區塊內沒有 `[n]` 時，沿用上一個段號；`[2]【疏文】` 後接未標號 `【記文】` 不再回填譯本甲 | 端到端 fixture：拆回 `a_0012` 含「改後記2」 |
| 3 | [build_a2.py:133](_src/build_a2.py#L133-L143) | 修訂稿缺欄檢查：多欄材料少任一 `【欄】` 即印 `✗ 修訂缺欄`、不寫定稿、計入缺檔 | fixture 只給記文 → 輸出 0 檔、`缺 1`、非零退出 |
| 4 | [assemble_book.py:98](_src/assemble_book.py#L98) | 打包組剝除同行殘留 `[n]`（原本只剝行首） | `A [1] B\n[2] C` → `A B\nC` |
| 5 | [pack_audit.py:68](_src/pack_audit.py#L68-L84) | 相鄰判定改用 `s0／g1`（缺欄才退回索引差 ≤10），不再因 key 跳 +2 而幾乎不併包 | 兩組 s0=10/12 成功併成 1 包、segs=2 |
| 6 | [local_corpus.py:30](_src/local_corpus.py#L30-L31)、[:84](_src/local_corpus.py#L84-L90) | `_VAR_MAP` 增 11 個異體（廻→迴、敍→敘、祕→秘、衞→衛、弃→棄、処→處、体→體、无→無、証→證、堕→墮、徳→德）；`ALIASES` 補 `薩婆多論`、`摩得勒伽論`、`根本有部律`、`有部律` | `_norm_book('薩婆多論')` → 《薩婆多毘尼毘婆沙》；`_plain('廻体无')` → `迴體無` |
| 7 | [run_pipeline.py:153](_src/run_pipeline.py#L153-L157) | 重跑 `packjudge` 清空前，先把舊 `_裁決` 移成 `_裁決_舊_<時間戳>` | 語法檢、備份路徑已寫入文件 |
| 8 | [book_config.py:17](_src/book_config.py#L17) | STYLE 4 補：「亦不得代為訂正其訓釋」——祖師引文與原典有出入時仍依本段原文直譯 | 字串斷言 |
| 9 | [qwen_local.py:742](_src/qwen_local.py#L742-L743) | `_looks_pasted` 對以 `「『` 開頭的譯文不判重貼（避免長引句短段誤殺） | 原樣照貼仍 `True`；引號開頭 `False` |

## 狀態

- 全 `_src` 主模組編譯 0 錯；測試 fixture 已全刪。
- 文件重建：312,866 bytes／6,859 行／80 fence；9 項變更都已在 6.x 程式碼段反映。
- `pack_audit` 的 `_note`、`norm` 髮字、`JI_NOTE`、`REVISE` 護欄、`STYLE` 撞義詞等前幾輪已修，未重複動。

## 仍未修（需你決定）

| 項目 | 原因 |
|:--|:--|
| `提示詞包/` 仍是 11-16 舊版 | 需決定要用哪個環境（`LOCAL=1/NO_WEB=0`）重出整包 |
| `KEEP_THINKING`＋45k 上限 | 需實測 3–4 輪檢索的 token 曲線，不宜盲調 |
| `_force_pass` 非 `out` 比對跳過同誤 | 屬設計取捨，只在雙模型互比時生效 |
| `STYLE_SPEC 2` 科判短語除外 | 只影響 legacy 一審，未動 |
| 母本 84 份缺口 | 合編 docx 卷下之四尾段缺頁，程式無法補 |
| `offset`、`rows` 調整 | 已定調不做 |

下一步建議：先把「提示詞包」重出並對齊現行版本，再抽 10 組跑五關，確認這批修正沒有改變改動率。