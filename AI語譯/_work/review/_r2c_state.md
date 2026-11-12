# r2 1533–1648 進度與做法（交接用）

## 範圍
- 回應：`batch_qwen/r2/resp_1533.txt`–`resp_1648.txt`
- 材料：`校閱_10K/校閱_1533.txt`–`校閱_1648.txt`
- 輸出：`AI語譯/out/<書>/<chunk>.txt`（只改該段）
- **1491–1532 已完成**（見 `說明_r2_1491.md`）；**1342–1490 由另一支處理，不要碰。**

## 工具（AI語譯/_work/review/）
- `_r2c_index.py`：索引＋全量對位（1533 起材料【譯文】與 out 現行 ratio=1.000，old 可直接取材料）。
- `_r2d_ws.py N [N...]`：印 resp 全文＋被引用的段（原文＋現行譯文）；段號解析支援 `#NN`、`【NNNN-NNNN】`、`段N`。
- `_r2d_build.py`：per-file 腳本 `B.make(N, [(seq, old, new, why)], verdicts)`，依 seq 自動取 book/chunk/seg 並驗 old 恰一次。
- `_r2d_apply.py edits_N.json [--dry] [--done]`：套用、備份 `_l`、寫 `_r2c_log/log_N.json`、append `batch_qwen/r2_done.txt`。
- `_r2d_stat.py [起] [迄]`：以 log 統計改段／改處／判定。
- `_r2c_cut.py N seq start len`：長段分片檢視。

## 注意
- 備份後綴：**`_l3`**（1588 起；`_l2` 為 1572–1587 輪所用，`_l` 為 1533–1571 輪，勿覆蓋）。首次改動 chunk 時建立 `歸檔/r2修正前/<書>/<chunk>_l3.txt`。
- 三書行尾皆 CRLF（由 Out 自動沿用）；段數、段內換行數不變（`_r2d_apply` 會驗）。
- 判定四類：真錯（改）／已修（不改）／誤報（不改：加註、體例、純潤飾、整體性主張一律否決）／存疑（寫入 `存疑材料/r2_存疑/<書>.md`）。
- 一個 resp 檔可能跨兩個 chunk（例如 1557、1558），seq 以檔案內 `NNNN-000N` 為準。
- **不要跑 build_dirty。**

## 進度
**1588–1648 全部 61 檔已完成**（r2 範圍結束，下一檔 1649 已超出本輪）。
1533–1571：39 檔、204 改段、782 改處、真錯 690、否決 195、存疑 52。
1572–1587：16 檔、139 改段、253 改處、真錯 139、誤報 53、存疑 11（存疑檔 1–11 條）。
1588–1648：61 檔、707 改段、1359 改處、真錯 711、誤報 161、存疑 31、已修 118（存疑檔 12–31 條）；說明見 `說明_r2_1588.md`。
累計 1588–1648 全部套用並登記（`batch_qwen/r2_done.txt`、`_r2c_log/log_1588.json`–`log_1648.json` 共 61 份）；備份 `_l3` 共 10 個 chunk。
- `_r2d_ws.py` 已修 3 位數段號（\d{1,3}）；**resp 的編號有時是 seq 而非 chunk 段號**（如 1576 的 #1–#14＝seq1–14），對不上時用 `--all`。
- 備份改 **`_l2`**：`_r2d_apply.py` 已改；01b/02a/02b 的 `_l2` 由 `_r2d_l2.py` 反向套 log 重建（bad=0）。
- 說明：`說明_r2_1572.md`（表格做到 1587）。之後 chunk：02b（1588 起）→ 03a → 03b → 04a → 04b → 05a → 05b → 06a → 06b → 07a（1648）。
- 已套用並登記（`batch_qwen/r2_done.txt`、`_r2c_log/log_1533.json`–`log_1571.json`）。
- 存疑已寫入 `存疑材料/r2_存疑/05_拾毗尼義鈔.md` 第 41–67 條。
- 之後 chunk：`03_業疏/01b_卷一之一`（1572 起，續 01b 之後進 02a）→ 02a → 02b → 03a → 03b → 04a → 04b → 05a → 05b → 06a → 06b → 07a（1648）。`03_業疏` 行尾亦 CRLF。
- 續做時：`python _r2d_ws.py 1572` 讀 resp＋段 → 判四類 → 寫 `_r2d_mkNNNN.py`（import `_r2d_build`）→ `python _r2d_mkNNNN.py`（看 COUNT 警告）→ `python _r2d_apply.py edits_NNNN.json --done` → 每 10–15 檔更新 `說明_r2_1533.md` 與存疑檔。
- 常見坑：resp 的 `#NN` 是**該 chunk 的段號**，不是檔案 seq；`_r2d_ws` 的 `=== NNNN-000X ... #NN` 才是對照。`_r2d_build` 用 seq。


