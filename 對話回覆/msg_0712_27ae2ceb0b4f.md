# 對話材料 #0712

- event: assistant/message
- seq: 99544
- time: 1794923032466

---

`mk_revise` 的打包格式改了；`pack_audit` 檢查後不需要改。

## 已完成

| 項目 | 改動 |
|:--|:--|
| `mk_revise_materials` | 當 `md['packed']` 且有 `members` 時，`fmt` 改成 `[1] …\n[2] …`，不再用 `【疏文】…` 蓋掉 |
| 一般材料 | 仍用 `BC.fmt_for(...)` |

## `pack_audit` 的檢查結果

它沒有 `{logic_checklist}` 佔位符，也沒有直接組 `AUDIT_PROMPT`；共用清單是由 `mk_audit_materials` 帶入，所以不需要再補 `.replace`。

## 驗證

| 項目 | 結果 |
|:--|:--|
| `pack_audit` 編譯 | 通過 |
| `mk_revise` 編譯 | 通過 |

## 剩下

| 項目 |
|:--|
| `qwen_local`：`pack_judge` 材料不跑 `_strip_dup_labels` |
| `pack_judge.RULE` 補 4 行範例 |
| `qwen_local` 刪重複 `_looks_pasted` |
| 文件 4.4／4.7／5 同步 |

要我收最後這四項嗎？