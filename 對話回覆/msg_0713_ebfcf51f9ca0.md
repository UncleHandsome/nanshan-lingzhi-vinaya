# 對話材料 #0713

- event: assistant/message
- seq: 99610
- time: 1794923129642

---

單欄段落的提示詞清理已完成：`mk_blind` 與 `mk_split_blind` 都已改好，避免把記文的規則套到疏文，或把疏文的規則套到記文。

## 本輪完成

| 檔案 | 改動 |
|:--|:--|
| `mk_blind_materials` | 單獨【疏文】時，`_sr` 與 `_ban` 清空；單獨【記文】時，改用「記文釋義與科判動詞須與前文疏義相契」，且 `_ban` 不再接在「切勿譯入正文」後面 |
| `mk_split_blind` | 同步相同處理 |
| 流程文件 | 已重建，298.4 KB |

## 驗證

| 項目 | 結果 |
|:--|:--|
| 兩檔編譯 | 通過 |
| 文件重建 | 通過 |

## 仍剩

| 項目 |
|:--|
| `qwen_local`：`pack_judge` 材料不跑 `_strip_dup_labels` |
| `qwen_local`：刪掉重複的 `_looks_pasted` |
| `pack_judge.RULE` 補上 4 行範例 |
| `mk_audit` 與 `mk_revise` 各做 1 份實際產材料 smoke test |
| 文件 4.4、4.7、5 的數字同步 |

這五項先不再改動；目前主線可跑。需要我繼續處理，就說「繼續」。