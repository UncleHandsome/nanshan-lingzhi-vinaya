# 五書定稿（唯一來源）

這份 `定稿/` 是網站五本書的**唯一資料來源**。  
之後所有校對、補譯、比對、重建頁面，都先從這裡拿，不再直接改 `docs/`。

## 檔案

| 書 | 檔案 | 段數 |
|:--|:--|--:|
| 行事鈔 | `xingshichao.jsonl` | 1,988 |
| 戒疏 | `jieshu.jsonl` | 7,608 |
| 業疏 | `yeshu.jsonl` | 5,068 |
| 尼鈔 | `nicao.jsonl` | 806 |
| 義鈔 | `yichao.jsonl` | 558 |
| 合計 | | 16,028 |

## 每筆欄位

```json
{
  "book": "戒疏",
  "book_id": "jieshu",
  "vol": "卷一",
  "key": "卷一-001",
  "label": "疏文",
  "source": "原文……",
  "translation": "白話……",
  "raw_start": 12345,
  "raw_end": 12400
}
```

- `label`：只允許 `疏文`、`記文`、`鈔文`、`律文`、`註文`、`序文`
- `raw_start`／`raw_end`：在 `TXT/` 原書中的位置；`-1` 表示對不到
- `key`：卷別＋頁面順序

## 規則

1. 不再直接改 `docs/` 當成修資料。
2. 要改譯文、補缺口、調順序，先改 `定稿/*.jsonl`。
3. 改完用重建腳本輸出 `docs/`。
4. 每次重建後跑：

```text
python -X utf8 _src/pipeline_guard.py
```

5. 材料若與定稿衝突，以定稿為準。

## 目前狀態

- 行事鈔：1,988，全部對到 raw
- 戒疏：7,608，7,462 對到 raw，146 待模糊對齊
- 業疏：5,068，5,067 對到 raw
- 尼鈔：806，全部對到 raw
- 義鈔：558，全部對到 raw

## 重建

目前先以 `_src/build_canonical.py` 由 `docs/` 抽出；  
下一步要写 `_src/render_canonical.py`，由 JSONL 反向輸出頁面。  
在 render 完成前，`docs/` 仍是最後呈現，但**資料裁決以 `定稿/` 為準**。
