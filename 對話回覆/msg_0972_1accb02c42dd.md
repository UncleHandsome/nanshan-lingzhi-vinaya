# 對話材料 #0972

- event: assistant/message
- seq: 116568
- time: 1795081993514

---

再清掉四項；`col3()` 與 `pack_audit` 排序仍未動。

## 本輪

| # | 位置 | 改動 |
|:--|:--|:--|
| 1 | [build_a2.py:214](_src/build_a2.py#L214-L222) | 新增 `_got - _labs_exp` 檢查：譯文多出 `【鈔文】` 等非本段欄位時，列 `missing`、不寫定稿 |
| 2 | [check_align.py:37](_src/check_align.py#L37-L50) | 材料 ≤15 字的短題不再列入錯位判定，與 `realign_blind` 的豁免同步 |
| 3 | [qwen_local.py:1217](_src/qwen_local.py#L1217-L1225) | 全數成功時刪除殘留的 `_失敗清單.txt` |
| 4 | [mother_corpus.py:18](_src/mother_corpus.py#L18-L19) | `_VAR` 補 `毗眞裏牀徧呪覩羣竝`（10 字），對齊常見異體 |

## 仍未處理

- **5 份 `col3()` 解析器不一致**：`qwen_local._split_col3` 取最後標題，其餘取第一個。統一會動裁決／終審／修訂／定稿四處，風險較高，先留。
- **`pack_audit` 未依 `(chunk, s0)` 排序**：`n0001_` 新段不會與相鄰短段併包（只影響省流）。
- `mk_review_materials` 仍與 `AI語譯/out` 耦合（`load_pair` 已降級，但 `build_groups` 未全面改）。

## 狀態

- 全 `_src` 編譯 0 錯。
- 文件重建：356,517 bytes／7,758 行／82 fence。
- 未跑 API。