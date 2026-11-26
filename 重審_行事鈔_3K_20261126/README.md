# 行事鈔 3K 審閱材料（2026-11-26）

用**內部 JSONL 提示詞**重新產生的《四分律刪繁補闕行事鈔》3K 審閱材料，供逐段複核白話。

## 內容
- 共 **776 個檔案**（`0001_xingshichao.md` … `0776_xingshichao.md`）。
- 每檔約 3K 字：檔首是完整提示詞（`_src/review_prompt_universal.md`，含 JSONL 錨點），後面是若干段：
  ```
  ## 行事鈔／<key>

  ### 原文
  【鈔文】…

  ### 白話
  【鈔文】…
  ```
- 合計 **3,042 個 key**（同一列若有多個分段，key 為 `<key>-1`、`<key>-2`…）。
- 每段原文與白話均與 `定稿/xingshichao.jsonl` 逐字相同（已驗證 0 差異）；切檔只切在段與段之間。

## 使用方式
1. 一次拿一份 `.md` 送 AI（提示詞已包含在檔首，不必另外貼）。
2. 回覆依提示詞末尾 `<<<JSONL_START>>> … <<<JSONL_END>>>` 的 JSONL 格式。
3. 收回的 JSONL 由 `_src/ingest_user_reply.py`／`_src/ingest_boundary_reply.py` 驗證後套用。

## 產生方式
```powershell
python -X utf8 _src/mk_3k_book.py --book xingshichao --out 重審_行事鈔_3K_20261126
```
（此程式重新產生時會清掉舊的 `.md`，但會保留本 README。）
