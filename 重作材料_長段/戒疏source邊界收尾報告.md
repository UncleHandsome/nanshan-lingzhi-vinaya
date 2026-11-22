# 戒疏 source 邊界收尾報告

日期：2026-11-22 10:17（Asia/Taipei）  
範圍：`定稿/jieshu.jsonl`、`docs/jieshu/`、`docs/search/jieshu.js`  
未動：譯文、其他四書、其他書頁面。未跑 qwen。

本報告是 `重作材料_長段/戒疏source邊界修正報告.md`（09:58）的收尾：處理該報告 §7 剩下的 2 筆 segment，並記明 783 段字形差的保留決定。

---

## 1. 結論

```text
定稿 rows                        4,566
segments                        7,613
網站 pairs（四卷合計）            7,614
row.source == raw                4,566／4,566
row 級待修                       0
segment 級結構性待修              0
已知字形差／材料標記保留          783
translation 改動                 0
segment.source 改動              3 段（皆為邊界／段標）
docs/jieshu validate             issues 0
```

- 原本列出的 2 筆：`01c_卷一上之一_0059`、`戒疏-G19` 都已用精確 raw 邊界修好。
- 另在 segment 專項掃描發現 1 筆 `10d_卷三上之一_0086-1` 段標被截成半個（`疏】`），一併修好；不影響 row，也不改譯文。
- 783 段底本字形差／材料標記：**全部保留**，沒有改 source、沒有重切。
- `docs/jieshu` 已由生成器重建，四卷 pair 數不變；只有 3 個 pair 的 source 變動，譯文 0 變動。

---

## 2. 兩筆指定 segment 的處理結果

### 2.1 `01c_卷一上之一_0059`（已修）

| 項目 | 內容 |
|:--|:--|
| row raw 區間 | `[3961, 3965)`，4 個漢字「四分戒本」 |
| raw 上下文 | `《四分戒本》者，蓋開萬行之通衢……` |
| row.source | `《四分戒本》` |
| segment.source（修前） | `四分戒本。` |
| segment.source（修後） | `《四分戒本》` |
| 譯文 | 不變，`《四分戒本》` |
| 網站 pair | 卷一第 105 個 pair |
| 顯示修前 | `【律文】四分戒本。` ／ `【律文】《四分戒本》` |
| 顯示修後 | `【律文】《四分戒本》` ／ `【律文】《四分戒本》` |

**判斷**：這一段的 raw 邊界本來就有書名號 `《》`，後面緊接「者」，沒有句末 `。`。舊 segment 掉了 raw 的書名號、又多了 raw 沒有的 `。`；譯文則正確作 `《四分戒本》`。以 row 的精確顯示切片回填後，source 與譯文完全一致，漢字 0 增減。

> 這一筆不是「字形差」，是 segment 邊界標點錯位；故安全修。

### 2.2 `戒疏-G19`（已修）

| 項目 | 內容 |
|:--|:--|
| row raw 區間 | `[307760, 307853)`，93 個漢字 |
| raw 上下文 | `……及餘患也。\n　　【疏】「毀呰」者，正行罵也。……` |
| row.source 尾 | `……及餘患也。\n　　【疏】` |
| segment.source 尾（修前） | `……及餘患也。\n　　【疏】「` |
| segment.source 尾（修後） | `……及餘患也。` |
| 譯文 | 不變，尾端仍是「……以及其他病患。」 |
| 網站 pair | 卷四第 149 個 pair |
| 顯示修前 | source 尾多出 `【疏】「`，開引號未閉合 |
| 顯示修後 | source 停在本文句末 `。`；下一 pair 由 `【疏文】「毀呰」者……` 開始 |

**判斷**：

```text
【疏】 = 下一單元的段標，不屬於本段譯文
「     = 下一句「毀呰」者……的開引號，也不屬於本段
```

舊 segment 把兩者都吃進尾端，造成：

1. 網站 pair 尾端出現沒有內容的 `【疏】`；
2. 開引號 `「` 在本段尾、下一個 pair 開頭又出現一次，引號不成對。

修法只保留到 raw 本文最後一個漢字「也」及其句末 `。`，不移動 row 的 `raw_end`。row.source 尾端仍含 `【疏】`（row 邊界是 canonical raw 邊界），但網站 pair 由 segment 產生，頁面已不再顯示該段標與開引號。

> 修後 segment 的漢字比 row 少一個段標字「疏」（非正文）；其餘漢字 0 增減，譯文 0 改動。

### 2.3 額外發現：`10d_卷三上之一_0086-1`（已修）

| 項目 | 內容 |
|:--|:--|
| row raw 區間 | `[213885, 213919)` |
| row.source 頭 | `【疏】一、有一因生一果，可知。……` |
| segment.source 頭（修前） | `疏】一、有一因生一果，可知。……` |
| segment.source 頭（修後） | `一、有一因生一果，可知。……` |
| 譯文 | 不變，開頭就是「一、有一因生一果的……」，沒有段標 |
| 網站 pair | 卷三第 383 個 pair |
| 顯示修前 | `【疏文】疏】一、……`（半個段標） |
| 顯示修後 | `【疏文】一、……` |

**判斷**：這一段的 `source` 段標被截成 `疏】`，少了 `【`。網站本來就會依 `segment.label` 加上 `【疏文】`，所以正確做法不是把 `【` 補回去（會變成 `【疏文】【疏】`），而是把殘留的 `疏】` 去掉，讓 source 從本文「一、」開始，與譯文一致。這與同組 `0086-2`～`0086-20`（source 都直接從「二、」「三、」開始）一致。

> 這一筆不在原本的 2 筆清單內，是 segment 專項掃描新發現的標籤邊界問題；已修，漢字只去掉段標字「疏」，譯文 0 改動。

---

## 3. 783 段底本字形差：保留，不處理

### 3.1 定義

以 `fix_jieshu_source_boundary.py` 的 segment 定位規則重算：把 segment 開頭的 `【段別】` 去掉後，取其漢字序列，必須能在 row 的 `raw_start:raw_end` 漢字區間內連續定位。定位不到者為本節所稱的 783 段。

```text
segment 總數                 7,613
可定位                       6,830
  與 row 漢字完全相同            13
  只差邊界句讀                6,148
  段內含材料標記／其他          669
定位不到（本節保留）             783
```

### 3.2 783 段的組成

| 類別 | 段數 | 說明 |
|:--|--:|:--|
| 底本字形差／文字增減 | 743 | 例：`三本／三木`、`未／末`、`若子／若干`、`註／注`、`祇／祗`、`䇿／策`；也有 segment 比 row 多／少幾個字的情形 |
| 材料序號／行內段標 | 39 | segment source 帶 `[1]`、`[2]`… 或 `【疏】`、`【律】` 等材料標記 |
| ASCII 標題／頁碼 | 1 | `00_卷首_0061` 的 `No. 714-E …` |

明細（783 筆，含 key、segment index、原因、source 頭、row source 頭）：

```text
重作材料_長段/_掃描/戒疏_783字差保留.json
```

### 3.3 決定

```text
不改 source
不重切
不改 translation
不拉大／縮小 raw 區間
```

理由：

1. 這些是底本字形差或材料標記，不是這一輪的 source 邊界截斷；硬改會把底本字換成猜測字。
2. 783 段不影響 `row.source == raw`（row 級 4,566／4,566 全過），也不影響網站 pair 數與 pair 順序。
3. 使用者已決定「字形差可能不用處理」，且不要為字形差大規模重切。
4. 若日後要處理，應另開「字形差校勘」流程，逐段比對 `TXT/02_四分律含注戒本疏.txt` 與版本異文，不應在 source 邊界收尾中順手改。

> 這 783 段在網站上仍以現有 segment source 顯示；其原文與譯文可能有一二字差，屬已知保留，不列入本輪待修。

---

## 4. `recheck_scan.py --book 戒疏` 結果

指令：

```powershell
python -X utf8 _src/recheck_scan.py --book 戒疏 `
  --json 重作材料_長段/_掃描/戒疏source邊界.json `
  --out  重作材料_長段/_掃描/戒疏source邊界.md
```

### 4.1 總覽

```text
rows 4,566｜有旗標 4,566｜致命 266｜比例中位 2.06（膨脹門檻 2.57）
```

| 旗標 | 筆數 | 是否本輪處理 |
|:--|--:|:--|
| `SRC_TAIL_NO_END` | 253 | 逐筆核對後，全部是正常切段，不是截斷；不修 |
| `NO_LEAD_LABEL` | 4,566 | 戒疏定稿譯文不存段別標籤，網站生成器負責加；不修 |
| `GAP_SEG` | 22 | GAP／JE- 等缺口段標記；不是資料壞掉 |
| `THIRD_PERSON` | 8 | 譯文層風險旗標；不改譯文 |
| `BAD_VAR_QUOTE` | 6 | 譯文引號內異體字；不改譯文 |
| `BRACKET_OVERFLOW` | 7 | 譯文 `〔〕` 多於原文；不改譯文 |
| `TAIL_COLON` | 3 | 譯文句末冒號；不改譯文 |
| `INFLATE` | 304 | 譯文／原文比例風險；非 source 邊界 |
| `LONE_CORNER` | 2 | 譯文孤立 `『』`；非 source 邊界 |
| `DUAL_TOTAL` | 326 | 雙欄段總數詞；非 source 邊界 |
| `DASH_NOTE` | 207 | 譯文破折號插注；非 source 邊界 |
| `PREFACE_RISK` | 51 | 序跋／卷首風險；非 source 邊界 |
| `FALSE_FRIEND_HIT` | 347 | 全書通用高危詞觸發器 |
| `BOOK_TERM_HIT` | 53 | 戒疏抽樣具體詞觸發器 |

空譯文、缺欄、雙欄缺一欄、source 開頭 closing、背景外洩、`的等。`、`？等等。` 均為 **0**。

### 4.2 266 筆致命旗標的分類

| 組合 | 筆數 |
|:--|--:|
| 只有 `SRC_TAIL_NO_END` | 250 |
| `SRC_TAIL_NO_END` ＋ `TAIL_COLON` | 2 |
| `SRC_TAIL_NO_END` ＋ `BRACKET_OVERFLOW` | 1 |
| 只有 `BRACKET_OVERFLOW` | 6 |
| 只有 `BAD_VAR_QUOTE` | 6 |
| 只有 `TAIL_COLON` | 1 |
| **合計** | **266** |

### 4.3 `SRC_TAIL_NO_END` 253 筆的核對

對每一筆取「source 顯示切片」之後的下一個字元：

| 下一個字元 | 筆數 |
|:--|--:|
| 漢字 | 219 |
| 換行 | 28 |
| opening（`《`、`「`） | 4 |
| 罕用字 `䟦` | 1 |
| EOF | 1 |
| **closing／句末標點** | **0** |

也就是：這 253 筆的 source 都已吃到 raw 邊界能吃的標點，後面接的是下一個漢字、換行或下一句的開引號；沒有「緊鄰 `。」」卻漏收」的情形。它們是 row 切成小段後停在中間的段落，不是截斷。

### 4.4 譯文層旗標（未動）

| 旗標 | keys |
|:--|:--|
| `BAD_VAR_QUOTE` | `08c_卷二下之一_0044`、`15a_卷三下之三_0118`、`15a_卷三下之三_0120`、`16a_卷四上之一_0014`、`16a_卷四上之一_0031`、`17c_卷四上之二_0034` |
| `BRACKET_OVERFLOW` | `01a_卷一上之一_0016`、`09c_卷二下之二_0043`、`09d_卷二下之二_0015`、`09d_卷二下之二_0027`、`11c_卷三上之二_0066`、`12b_卷三上之三_0052`、`15b_卷三下之三_0025` |
| `TAIL_COLON` | `00_卷首_0015`、`05c_卷二上之一_0054`、`13a_卷三下之一_0135` |

這些是譯文層的既有問題，不是 source 邊界；依「不改 translation」保留，留待另一次譯文修訂。本輪沒有因 `recheck_scan` 再改任何 row。

### 4.5 `NO_LEAD_LABEL` 4,566 筆的說明

戒疏定稿的 `translation` 欄不重複儲存 `【疏文】`／`【記文】` 等段別；網站由 `render_canonical_cb.py` 依 `segment.label` 產生。因此：

```text
定稿資料：translation 不含段別標籤
網站顯示：renderer 自動加【段別】
```

這不是本輪新增的資料缺失，也不影響網站 pair。`check_final_merge.py` 的第 5 項會把這個慣例判成 FAIL，原因見 §6。

---

## 5. `docs/jieshu` 重建與 validate

### 5.1 流程

```text
1. 備份 docs/jieshu 四頁
   → docs/_備份_jieshu_segclose_20261122_101328/

2. python -X utf8 _src/render_canonical_cb.py --book jieshu
   → 四頁 .html.new

3. python -X utf8 _src/validate_site.py --book jieshu --suffix .new --no-search
   → issues 0

4. 原子替換 .html.new → .html

5. python -X utf8 _src/build_search_index.py --only jieshu
   → search/jieshu.js 重建；manifest.js 保留其他書

6. python -X utf8 _src/validate_site.py --book jieshu
   python -X utf8 _src/validate_site.py
```

### 5.2 pair 數與變動

| 卷 | 重建前 pairs | 重建後 pairs | source 變動 pair | 譯文變動 pair |
|:--|--:|--:|--:|--:|
| 卷一 | 1,594 | 1,594 | 1 | 0 |
| 卷二 | 1,748 | 1,748 | 0 | 0 |
| 卷三 | 1,981 | 1,981 | 1 | 0 |
| 卷四 | 2,291 | 2,291 | 1 | 0 |
| **合計** | **7,614** | **7,614** | **3** | **0** |

- 四頁 `<main>` 以外的 HTML（header／nav／footer）逐字相同。
- 只有 3 個 pair 的 source 變動；3 個 pair 的譯文逐字相同。
- `docs/search/jieshu.js` 只有 3 個索引條目的 `o` 欄變動，條目數 7,614、順序、錨點 `pair-N` 全部不變。

### 5.3 validate 數字

```text
python -X utf8 _src/validate_site.py --book jieshu
pages 4 anchors 4 brbr 0 punct 0 search 7614 searchbad 0 issues 0   （exit 0）

python -X utf8 _src/validate_site.py
pages 44 anchors 106 brbr 0 punct 0 search 26669 searchbad 0 issues 0 （exit 0）
```

- 戒疏 4 頁、4 個導覽錨點、7,614 個搜尋條目全部可解析。
- 全站 44 頁、106 個錨點、26,669 個搜尋條目也全部 0 失效。
- 其他書頁面本次沒有重建。

---

## 6. row／segment 剩餘數

### 6.1 row 級

```text
rows                       4,566
source == raw              4,566／4,566
未定位                     0
區間重疊                   0
空白譯文／缺欄             0
row 級待修                 0
```

`check_final_merge.py --book 戒疏 --final` 的第 1～4 項也都是 OK（source==raw、未定位、重疊、空譯文）。

### 6.2 segment 級

```text
segments                   7,613
空白 segment 譯文           0
source 開頭 closing         0
source 尾端未閉合開引號      0
段標括號不平衡              0
結構性待修                  0

已知保留：
  底本字形差／材料標記        783

另外掃描到、但非待修：
  材料序號／行內段標（783 之外） 37
  長引文每行以「起（排版慣例）   19
  目錄／卷題／句中切分尾巴無句末標點 22
```

> `[1]`／`[2]` 是部分多段單元的刻意編號，source 與 translation 同步保留，不是背景外洩；這 37 段不在 783 內。
> 19 段「不平衡」是長引文每行都重新以 `「` 起、只在最後一行 `」` 關閉的排版慣例，不是缺引號。
> 22 段尾巴無句末標點是目錄、卷題、跋語或 row 中間切分，下一字是漢字／換行，不是截斷。
> 後兩項是全書掃描數字，可能與 783 有重疊，僅供說明，不另計待修。

### 6.3 本輪動到的 segment

| key | 修前 | 修後 | 性質 |
|:--|:--|:--|:--|
| `01c_卷一上之一_0059` | `四分戒本。` | `《四分戒本》` | 書名號／句末標點回 raw 邊界 |
| `戒疏-G19` | 尾端 `……也。\n　　【疏】「` | 尾端 `……也。` | 去掉下一單元段標與開引號 |
| `10d_卷三上之一_0086-1` | 開頭 `疏】一、……` | 開頭 `一、……` | 去掉半個段標 |

- 3 段都只改 `segment.source`；`segment.translation` md5 全部不變。
- 全書 `translation` md5 不變；`row.source` 0 改動。
- 3 段中 2 段各去掉一個段標字「疏」，其餘漢字 0 增減。

---

## 7. 產物與備份

### 7.1 新增／修改

```text
定稿/jieshu.jsonl
docs/jieshu/卷一.html
docs/jieshu/卷三.html
docs/jieshu/卷四.html
docs/search/jieshu.js
_src/fix_jieshu_segment_closeout.py
重作材料_長段/戒疏source邊界收尾報告.md
重作材料_長段/_掃描/戒疏source邊界.json
重作材料_長段/_掃描/戒疏source邊界.md
重作材料_長段/_掃描/戒疏_783字差保留.json
```

### 7.2 備份

```text
定稿/_舊_jieshu_before_segclose_20261122_101454.jsonl   （本輪最終修前）
定稿/_舊_jieshu_before_segclose_20261122_101255.jsonl   （第一次嘗試，保留）
docs/_備份_jieshu_segclose_20261122_101328/            （本輪任何改動前的四頁）
```

### 7.3 可重跑

```powershell
# dry-run（已修過會回報 changes 0）
python -X utf8 _src/fix_jieshu_segment_closeout.py

# 只重跑網站
python -X utf8 _src/render_canonical_cb.py --book jieshu
python -X utf8 _src/validate_site.py --book jieshu --suffix .new --no-search
# 原子替換 .new 後
python -X utf8 _src/build_search_index.py --only jieshu
python -X utf8 _src/validate_site.py --book jieshu
```

---

## 8. 附註：`check_final_merge --final` 的兩項已知落差

`python -X utf8 _src/check_final_merge.py --book 戒疏 --final` 目前回報 4／7，落差不是本輪 source 邊界造成：

| 項目 | 結果 | 原因 |
|:--|:--|:--|
| 5 缺開頭標籤／背景外洩 | FAIL 0／4566 | 戒疏定稿譯文不含 `【段別】`，網站 renderer 才加；見 §4.5。要改就得動 4,566 筆譯文，違反本輪「不改 translation」 |
| 6 缺口段再審紀錄 | 待跑 0／22 | 本輪沒有跑 qwen／再審批次；GAP 22 段仍是待再審狀態 |

第 7 項「非正文如實排除」是 WARN（4,559／4,566），列出 7 筆卷首／序跋類有譯文，屬既有分類提醒，不是 source 邊界問題。

本輪的驗收標準是：

```text
row.source == raw         0 錯
row 未定位／重疊／空譯     0
segment 結構性邊界問題     0
docs/jieshu validate       issues 0
translation 改動           0
```

以上全部達成。

---

## 9. 一句話

```text
戒疏 source 邊界收尾完成：
2 筆指定 segment 已修（另修 1 筆新發現的段標截斷），
783 段字形差保留不動，row 0、segment 結構性 0，
docs/jieshu 重建後 validate issues 0，translation 0 改動。
```
