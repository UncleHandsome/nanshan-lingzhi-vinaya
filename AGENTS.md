# AGENTS.md — 南山律典白話專案：完整專案手冊

最後更新：2026-11-22  
對象：任何接手的 AGENT。  
**先讀完這份，再開工。遇到不確定，查原檔，不要猜。**

---

## 0. 最高原則（2026-11-21 定稿重建）

### 0.1 唯一來源

```text
定稿/*.jsonl              唯一資料來源
_終審／_終修／_定稿         原文與譯文來源
_長段/_定稿               長段已切好的小段
TXT_句讀校定/<book>.txt    網站原文句讀校定本
```

網站原文一律讀 `TXT_句讀校定`；漢字序列已驗證與 `TXT/<書>.txt` 完全一致。

`docs/**/*.html` 只是輸出，不是來源。

### 0.2 禁止機械性模糊比對

不可用「前 20／16／12／8 字命中」直接判定找到內容。

前綴比對只能產生候選，必須再驗：

1. 缺口全文是否被 unit 原文完整包含，或反之
2. 是否同卷、同順序
3. 是否只重疊一部分
4. 譯文範圍是否與缺口相符

只有「完整包含＋順序正確」才能補；部分重疊要切；不確定就標未解，不要硬補。

### 0.3 禁止用舊資料補洞

- 不用 `docs` 舊譯
- 不用 `_材料` 當原文
- 不用 `_長段` 整段大單位
- 不用頁面 pair 補缺口

### 0.4 長段

只用 `_長段/_定稿` 已切好的小段。

- 一個 key 對多缺口，必須切開
- 切不開就保留缺口
- 不拉大 unit 區間
- 不把長段整段塞入

### 0.5 缺口

先分類：

```text
卷首／序文／目次
卷題／篇題
正文
```

只有正文才進盲翻。卷題、目錄、校勘、異體字表不譯。

### 0.6 盲翻

- 材料要寫明輸出檔名
- 每段 `## 書-G編號`＋`【段別】原文`＋`【段別】白話`
- 單段超過 500 字必須切小段
- 不參考現譯
- 不改字、不增刪

### 0.7 驗收

```text
未定位 0
重疊 0
缺口如實列出
```

不得用假補洞把缺口歸零。

### 0.8 網站

**禁止直接改 `docs/**/*.html`。**

網站只能由生成器重建：

```text
定稿/*.jsonl
→ render_* / site_*
→ .new
→ validate_site.py
→ 原子替換
```

規則：

- 不得用 regex 直接 patch HTML
- 不得手工補錨點
- 錨點必須由標題生成
- 原文句讀用 `display_source`
- 驗收必須 0 失效錨點、0 無句讀長段落
- 驗收失敗就修資料或生成器，不是改頁面

---

## 0. 專案一句話

把南山三大部／五大部的古籍原文，做成：

1. 白話譯文（盲翻 → 裁決 → 終審 → 修訂 → 定稿）
2. 原文／白話逐段對照網站（`docs/`）
3. 長段（超長段落）再切成小段，讓網站可讀、可對齊

---

## 1. 全專案目錄

### 根目錄

| 路徑 | 作用 |
|:--|:--|
| `TXT/` | **最原始 CBETA 純文字**，一書一檔（如 `TXT/04_四分律比丘尼鈔.txt`） |
| `TXT_分卷/` | 由 `TXT/` 分卷後的文件，網站原文常用 |
| `TXT_分卷_標點/` | 有句讀的分卷原文（業疏等） |
| `TXT_句讀/` | 另一套句讀原文 |
| `原文/` | 原典與科判資料 |
| `_母本/` | 母本（隨機羯磨） |
| `提示詞包/` | 現行提示詞整理 |
| `AI語譯/` | 翻譯工作區；`out/` 是官網用譯文 |
| `測試/` | 正式書、QC、封存實驗、重譯 |
| `docs/` | 網站輸出 |
| `出書/` | 成書用全書文字 |
| `白話/` | 白話版 PDF／DOCX |
| `_src/` | 全部程式 |
| `歸檔/` | 舊版本、舊實驗、封存資料，**不要拿來當現行資料** |

### `測試/重譯/` 六書

```text
測試/重譯/行事鈔/
測試/重譯/戒疏/
測試/重譯/業疏/
測試/重譯/資持記/
測試/重譯/尼鈔/
測試/重譯/義鈔/
```

每書常見子目錄：

| 子目錄 | 內容 |
|:--|:--|
| `_材料` | 翻譯材料（原文＋提示詞＋背景） |
| `_盲翻` | 盲翻材料／輸出 |
| `_裁決` | 裁決材料與回覆 |
| `_終審` | 終審材料（原文＋待審譯文） |
| `_終修` | 舊修訂 |
| `_終修_20261121` | 2026-11-21 新修訂；`回覆/*_回.txt` 才是譯文 |
| `_定稿` | 定稿；部分書只有樣本 |
| `_長段` | 長段流程（見第 5 節） |
| `_對應.json` | 長段／分卷對應資料（若有） |

### `AI語譯/`

| 路徑 | 內容 |
|:--|:--|
| `AI語譯/out/<書>/` | 官網用譯文，一章一檔（如 `01a_卷一之一.txt`） |
| `AI語譯/_work/` | 對齊、句讀、搜尋、審核工作檔 |
| `AI語譯/out/*_備份_20261121/` | 新譯覆蓋前的備份 |

**`AI語譯/out` 是網站譯文來源；改動前先備份。**

### `docs/`

| 路徑 | 內容 |
|:--|:--|
| `docs/index.html` | 首頁 |
| `docs/nav.json` | 側欄目錄 |
| `docs/search/` | 全文搜尋索引 |
| `docs/xingshichao/` | 行事鈔 |
| `docs/jieshu/` | 戒疏 |
| `docs/yeshu/` | 業疏 |
| `docs/zhichi/` | 資持記 |
| `docs/nicao/` | 尼鈔 |
| `docs/yichao/` | 義鈔 |
| `docs/hebian/` | 行事鈔資持記句級合編 |

網站是靜態 HTML；`docs/style.css`、`docs/nav.js`、`docs/search.js` 是共用資源。

### `_src/`

全部腳本。重要分類：

| 類別 | 代表檔案 |
|:--|:--|
| 管線 | `run_pipeline.py`、`run_*.py`、`_night_orchestrator.py` |
| 材料 | `mk_*materials.py`、`mk_split_blind.py`、`mk_audit_materials.py` |
| 長段 | `mk_long_*`、`apply_long_*`、`run_long_*`、`write_long_finals.py` |
| 網站 | `site2.py`、`site_ju.py`、`site_hebian.py`、`build_appendix.py` |
| 提示詞 | `提示詞包/`、`提示詞現行版.md`、`校閱系統_程式與提示詞.md` |
| qwen | `qwen_local.py`、`qwen_cbeta.py` |
| 匯出 | `export_*_out.py`、`make_hebian.py` |

---

## 2. 六書現況（2026-11-21 快照）

| 書 | 正式流程 | 長段 | 網站 |
|:--|:--|:--|:--|
| 行事鈔 | `_終審` 1,442、`_定稿` 1,481 | 113 段；7 個約 100K 檔 | 舊頁，未全部切分 |
| 戒疏 | `_終審` 4,634、`_終修_20261121` 457、`_定稿` 14 | 21 段；**無長段定稿** | 舊頁；新譯已組成 69 章但未重建 |
| 業疏 | `_終審` 2,580、`_終修_20261121` 349、`_定稿` 14 | 18 段；4 段原文污染 | 舊頁；新譯已組成 44 章但未重建 |
| 資持記 | `_裁決` 8,364、`_終審` 13、`_定稿` 13 | 長段資料很少 | 舊頁；packaudit 未完成 |
| 尼鈔 | `_終審` 774、`_定稿` 781 | 10 段 | 已切 8／9 |
| 義鈔 | `_終審` 207、`_定稿` 209 | 27 段／369 小段 | 已內嵌切分 |

> 檔案數不等於完成；`_定稿` 14 檔通常只是樣本，不是全書。

---

## 3. 資料模型與命名

### 3.1 單位 key

常見格式：

```text
01a_卷一之一_0001
05c_卷中之一_L0023
11b_卷下之三_L0001
```

- 前綴是卷／章（`01a`、`05c`、`11b`）。
- 尾碼是段號；`L` 表示長段。
- `_回.txt` 是 qwen 回覆；`_usage.json`、`_evid.json` 是附屬資料。

### 3.2 段別標籤

只使用：

```text
【疏文】【記文】【鈔文】【律文】【註文】【序文】
```

不要自創 `【修訂譯文】` 之類標籤。

### 3.3 原典權威

- 看到疑似錯字，先查 `TXT/<書>.txt` 原始檔。
- 若 `TXT/` 原檔就是該字，那是**底本原字**；不得直接改成猜測字。
- 例：`木作離意`、`今時諸寒`、`客此丘來`、`與曰衣賢者`、`口口提`、`五繫心貪利` 都在 `TXT/04_四分律比丘尼鈔.txt` 原樣存在。
- 要說「疑訛」，必須指出另一版本異文；沒有版本依據就寫「底本如此」。

---

## 4. 譯文流程

### 4.1 階段

```text
材料 → 盲翻 → 裁決 → 終審 → 修訂（終修）→ 定稿
```

- `_終審`：原文＋待審譯文。
- `_終修_20261121/*.md`：修訂**材料**（含提示詞、原文、硬傷清單）。
- `_終修_20261121/回覆/*_回.txt`：真正修訂後譯文。
- `_定稿`：定稿；不是每書都完整。

### 4.2 提示詞

- 現行版：`提示詞現行版.md`
- 全套：`提示詞包/`

### 4.3 禁止

- 不要把 `_終修` 材料當定稿。
- 不要用檔案存在判定完成；要檢查覆蓋率／缺段。

---

## 5. 長段流程

### 5.1 流程

```text
_材料 → _盲翻 → 裁決 → _終審 → _終修 → _定稿
```

不是每書都跑完；`_長段/_材料` 有檔不代表有譯文。

### 5.2 已知異常

- 業疏 4 段原文污染、定稿只有開頭：
  - `04b_卷一之四_L0007`
  - `16a_卷三之五_L0023`
  - `18a_卷四之一_L0001`
  - `18b_卷四之一_L0053`
- 戒疏 21 段長段沒有 `_終審`／`_定稿`，不能算已完成。
- 行事鈔 `output3` 只涵蓋 `行事鈔_長段_02/03/06/07`；缺 `01/04/05`（51 段）。
- 尼鈔 `05a_卷下之上_L0006` 尚未對上 page pair。

### 5.6 網站套用方式

1. 在現有頁面找目標 pair／pair 範圍。
2. 依實際切點切分。
3. 只替換該 pair 範圍。
4. 保留頁面其他所有內容。
5. 驗證 pair 數增加、非長段內容還在。

**不要**把整個 `<main>` 換成只有長段；**不要**另開「長段對照」頁（除非明確要求）。

---

## 6. 網站

### 6.1 資料流

```text
TXT_分卷 / TXT_分卷_標點 + AI語譯/out/<書>
        ↓
docs/<book>/卷*.html
```

### 6.2 絕對禁止：import `_src/site2.py`

`site2.py` 檔尾有未包在 `if __name__ == '__main__'` 的 `build()`。  
**只要 import 就會重建整個 docs/**，會覆蓋手工切分頁、index、nav、search。

不要 import、不要 `runpy`、不要「先 import 看看」。

### 6.3 現況

- `docs/yichao`：已內嵌切分（卷上／卷中各 280 組）；**不要用 site2 重建**。
- `docs/nicao`：已切 8／9。
- `docs/yeshu`、`docs/jieshu`：舊頁；新譯在 `AI語譯/out`，尚未安全重建。
- `docs/xingshichao`、`docs/zhichi`、`docs/hebian`：不要順手重建。

### 6.4 重建規則

1. 先備份 `docs/`。
2. 只重建目標書頁。
3. 重建後重新套用義鈔切分。
4. 驗證 pair 數、章節、非長段內容。
5. 才 push。

---

## 7. QC／審核／packaudit

- 審核結果：`PASS`、`FIX`、`ERROR`。
- `mk_revise_materials.py` 只抽 `FIX`；`PASS` 不進修訂。
- `_400審查` 是人工阻擋，不是正常回覆。
- `packaudit` 流程：
  `pack_audit.py` → qwen 打包審核 → `mk_revise_materials.py` → qwen 打包修訂 → `pack_final.py`
- `packaudit` 曾因 quirk：失敗仍回 rc=0；已改成非 0。
- 2026-11-21 07:50 grace stop 時：完成 579、失敗 4、未送 2,993；`STOP` 仍在。
- 若要續跑，packaudit 會自動清 local STOP 並跳過已完成。

---

## 7A. 20K 再審流程（定稿後複核）

### 7A.0 前置：定稿凍結與 source 邊界檢查（必做）

再審前先做，不可跳過：

```text
0. 先跑 _src/recheck_scan.py 產 risk_flags（0 成本；見 7A.0.1）
1. 全量掃 translation 空白、提示詞背景殘留（【前文背景】等）
2. 全量掃 source 開頭 closing 引號／缺【，結尾缺句末標點
3. 抽樣比對：譯文有完整句、source 卻截斷 → 先修 raw_start／raw_end
4. source 必須 == raw[raw_start:raw_end]
5. 定稿凍結後才產 20K 材料
```

**次序不可顛倒：先修 source 邊界，再做再審。** 若 source 邊界未修就送再審，模型會把譯文正確補出的「如前文已釋」「等諸法」判成無據增補。

### 7A.0.1 確定性前置掃描（`recheck_scan.py`）

只讀 `定稿/*.jsonl`，輸出 report／JSON，不改資料；`--strict` 有致命旗標即 rc=1。

```powershell
python -X utf8 _src/recheck_scan.py --book 尼鈔
python -X utf8 _src/recheck_scan.py --book 戒疏 --json 重作材料_長段/_掃描/戒疏.json
python -X utf8 _src/recheck_scan.py --out 重作材料_長段/再審前置掃描.md --strict
```

10 類旗標：空白／缺欄／source 頭尾、缺開頭標籤、背景外洩、GAP／BLIND／JE-／YE-、
第三人稱旁白、引號內 BAD_VAR、`〔` 溢出、句末冒號／「的等。」／「？等等。」、
膨脹 >1.9／縮水 <0.5／孤立『』、雙欄總數詞／無標點多「云言問答曰」／破折號／序跋。
另加 `FALSE_FRIEND_HIT`（全書通用高危假朋友）與 `BOOK_TERM_HIT`（各書抽樣已證實具體詞）。

**具體詞例只活在程式裡。** `recheck_scan.py` 的 `FALSE_FRIEND`／`BOOK_TERMS` 是 0 成本觸發器；
`SYSTEM_PROMPT`、`REAUDIT`／`REVISE`／`VERIFY`、`book_config.py` 各書 note **不得**再抄這些詞例
（避免關鍵字反射誤殺原文真有該詞的段落）。提示詞只留抽象錯誤類型，每類最多 1 個最泛用例子。

已證實案例：

```text
戒疏 02a_卷一上之二_0112 開頭缺「
戒疏 05d_卷二上之一_0085 開頭缺【
戒疏 08c_卷二下之一_0044 結尾缺。
業疏 YE-G02／YE-G03 空譯文與頭尾截斷
```

### 7A.1 目的

定稿完成後，以「一份 `.md` 約 20K 字」的連續批次再審，解掉逐段送審看不到前後文的問題：

```text
跨段專名／術語不一致
跨段指代與施受斷裂
長段切段接縫重複主語
業疏／戒疏疏記互核不一致
```

### 7A.2 唯一來源

```text
定稿/<book>.jsonl
```

不得讀 `docs/`、`_材料`、舊 `AI語譯/out` 當來源。

每批不跨 `vol`；同一 `chunk` 優先。為達到 20K 目標，允許跨同卷內相鄰 `chunk`，但同一 unit 的疏文＋記文不拆。

`--group-by vol` 是預設；`--group-by chunk` 只在該卷材料足夠時使用。

### 7A.3 六支主線腳本＋三支驗收

```text
_src/mk_reaudit_materials.py
  定稿 → _再審/<book>_r0001.md + .json

_src/split_reaudit.py
  驗核驗表、400／截斷對半切、依 [n] 拆回 FIX 計畫

_src/mk_rerevise_materials.py
  只為 FIX 單位產生單段修訂材料

_src/verify_reaudit.py
  VERIFY 回退閉環：OK 寫候選、RETRY 併硬傷重跑一次、二次 RETRY 進人工清單

_src/apply_reaudit.py
  FIX 回寫 定稿_v2/<book>.jsonl、qc、source==raw、變更對照

_src/check_final_merge.py --final
  7 項最終驗收（source==raw、未定位、重疊、空譯、標籤、缺口紀錄、非正文）

_src/book_consistency.py
  全書稱謂／專詞／性別代詞／標籤統計（只報告）

_src/recheck_scan.py
  0 成本前置掃描（見 7A.0.1）
```

### 7A.4 材料格式

每段交錯排列，讓 `qwen_local.py` 的 `SRC_RE_ALL` 只抓原文：

```markdown
### [01]（key: ys_01_0012）
■ 疏文（原文）[01]
……
■ 疏文（現譯）[01]
……
■ 記文（原文）[01]
……
■ 記文（現譯）[01]
……
```

`.json` 必須記錄：

```text
idx / key / chunk / raw_start / raw_end / labs / parts / src_hash
```

### 7A.5 20K 預算

```text
整份 .md：約 19K–20.5K 字
待審原文＋現譯：約 11.5K–14K 字
前文背景：原文 ≤1500 字＋前鄰譯文 ≤400 字
後文背景：原文 ≤600 字＋後鄰譯文 ≤300 字
資持記所釋鈔文：≤2500 字
```

### 7A.5b 提示詞與去過擬合原則（2026-11-22）

四支提示詞與 note 的分工：

```text
SYSTEM_PROMPT（qwen_local.py）
  全域只留「按需檢索、材料已附親註勿重搜、跨書僅供釐清本段詞義」；
  不列抽樣詞例、不強制每個疑點都搜、反切不強制補音。

REAUDIT_PROMPT（book_config.py；20K 版為 REAUDIT_PACK_PROMPT）
  只抓實質義理、文法邏輯與嚴重界線；恢復「合理顯義／必要消歧不判 FIX」護欄；
  純簡稱展開、反切、標點、單層引號不判 FIX（交 norm.py）。
  具體高危詞例只在 recheck_scan.py。

REVISE_PROMPT（book_config.py）
  三分法：(A) 無據增補與越界混入（含旁白、假引號）→ 刪除或還原中性泛稱；
  (B) 原典雙行夾注漏補 → 圓括號；(C) 實質誤譯與邏輯斷裂 → 正句重譯。
  允許正當駁回（硬傷誤判／必要語法消歧／強求他書細節），不輸出駁回按語。

VERIFY_PROMPT（book_config.py）
  只驗有實際改動的句段；未改項目回頭核原文，屬正當駁回或硬傷誤判者不判 RETRY。
  **VERIFY 用 QWEN_EFFORT='high'（不是 medium）**，避免「弱否決強」。
```

`book_config.notes_for()` 依段別與風險訊號掛載 `{dual_note}`（疏＋記）、`{long_note}`
（長段切片）、`{preface_note}`（序跋）、`{dangling_note}`（句末引導詞）、`{typo_note}`
（預檢疑訛）。`mk_audit_materials.py`／`pack_audit.py`／`mk_reaudit_materials.py`／
`mk_rerevise_materials.py` 都必須經 `BC.render()` 填滿佔位符，**不得再留死碼**。

### 7A.6 qwen 環境

再審（Step 2）：

```powershell
$env:QWEN_SHUJI_SRC='重譯/<book>/_再審'
$env:QWEN_KEY_FILE='qwk.txt'
$env:QWEN_LOCAL='1'; $env:QWEN_NO_WEB='0'
$env:QWEN_MAX_LOCAL='14'
$env:QWEN_MAX_SEARCH='4'
$env:QWEN_MAX_ROUNDS='10'
$env:QWEN_MAX_LAST_IN='90000'
$env:QWEN_HTTP_TIMEOUT='1200'
$env:QWEN_WORKERS='12'
$env:QWEN_RAW_SAVE='1'; $env:QWEN_NO_CITE='0'
$env:QWEN_EFFORT='xhigh'; $env:QWEN_KEEP_THINKING='1'
python -X utf8 _src/qwen_local.py
```

修訂（Step 3）：`QWEN_SHUJI_SRC='重譯/<book>/_再審修訂'`、`QWEN_MAX_SEARCH='1'`、`QWEN_NO_CITE='1'`、`QWEN_EFFORT='xhigh'`。

驗收（Step 4）：`QWEN_SHUJI_SRC='重譯/<book>/_再驗'`、`QWEN_NO_WEB='1'`、`QWEN_MAX_LOCAL='2'`、**`QWEN_EFFORT='high'`**、`QWEN_KEEP_THINKING='1'`。

### 7A.7 執行順序

```powershell
# 0) 前置（0 成本）
python -X utf8 _src/recheck_scan.py --book 義鈔 --out 重作材料_長段/再審前置掃描.md

# 1) 再審材料 → 再審
python -X utf8 _src/mk_reaudit_materials.py --book 義鈔 --target-chars 20000 --check-raw
python -X utf8 _src/qwen_local.py

# 2) 拆回 → 修訂材料 → 修訂
python -X utf8 _src/split_reaudit.py --book 義鈔 --bisect
python -X utf8 _src/mk_rerevise_materials.py --book 義鈔
python -X utf8 _src/qwen_local.py

# 3) 驗收（只驗有改動的段；RETRY 自動產第二次修訂材料）
python -X utf8 _src/verify_reaudit.py --book 義鈔 --dry-run
python -X utf8 _src/verify_reaudit.py --book 義鈔
#    若 _待重跑清單.txt 有 _再修/*.md，再跑一次 REVISE 與 VERIFY（至多 1 次）

# 4) 套用（寫 定稿_v2，不動 定稿）
python -X utf8 _src/apply_reaudit.py --book 義鈔 --revise 重作材料_長段/_驗收/義鈔

# 5) 全書一致性＋最終驗收
python -X utf8 _src/book_consistency.py --book 義鈔
python -X utf8 _src/check_final_merge.py --book 義鈔 --final --strict
```

### 7A.7b 黃金回歸與防過擬合驗證（跑批前必做）

```text
A. 黃金 50 段：尼鈔10＋行事鈔10＋義鈔10＋業疏10＋戒疏10（重作材料_長段/五書抽樣10）
   驗收三條件：召回 100%（專家清單實質誤譯全部 FIX 並修對）、
   無副作用（原本正確句不得改壞，VERIFY 攔下修 A 壞 B）、成本可控。

B. 負樣本 20 段（防誤殺）：抽「原文真的有高危詞或夾注、譯文原本正確」的段落，
   看 REAUDIT 假 FIX 率是否 >20%、VERIFY 是否誤打正當駁回為 RETRY。

C. 盲測 25 段（泛化）：五書各再抽 5 段完全沒參與設計的段落，人工快檢新錯誤類型。

清單產生：`python -X utf8 _src/mk_regression_sets.py`（只產清單，不跑 qwen）。
```

### 7A.8 驗收

```text
【分段核驗表】[01]..[N] 無漏號
400／截斷：0
FIX 比例合理（約 5%–15%）
source == raw：0 錯
未定位：0
重疊：0
qc_scan：0 致命
VERIFY：OK 候選；二次 RETRY 進 _人工複核清單.txt（不得無限重跑）
幅度警報：>1.25／<0.70 強制 VERIFY 或人工核對
book_consistency：稱謂／專詞／代詞離群清單人工核對
check_final_merge --final：7 項全達標
```

`apply_reaudit.py` 只替換 FIX 單位；PASS 單位從原定稿原樣複製，不得重譯。
`verify_reaudit.py` 只把 VERIFY 判 OK（或合法未改動）者寫入候選 `回覆/`；未驗者不得進候選。

### 7A.9 禁止

```text
不可把 20K 材料一次重吐全文
不可在修訂階段改 PASS 單位
不可用模糊比對補 [n]
不可跳過 split_reaudit 直接套回
不可用舊 docs 頁面當來源
```

### 7A.10 目前狀態

```text
mk_reaudit_materials.py：已存在（2026-11-22 改用新版 REAUDIT_PROMPT＋動態 note）
split_reaudit.py：已存在
mk_rerevise_materials.py：已存在（改用新版 REVISE_PROMPT）
verify_reaudit.py：新增（VERIFY 閉環；尚未跑批）
apply_reaudit.py：已存在（尚未正式跑批）
recheck_scan.py／book_consistency.py／check_final_merge.py：新增（只讀／只報告）
```

程式與提示詞已就緒，**尚未跑任何再審批次**（未呼叫 qwen、未寫 定稿_v2）。

### 7A.11 六書推進策略

**《資持記》接軌（免重工）**

```text
_終審_拆回 926 單位（PASS 778、FIX 148）；其餘 3,256 單位未終審。
1. 已拆回 148 筆 FIX：直接用新版 REVISE＋VERIFY 修訂驗收。
2. 未終審 3,256 筆：不再走舊 AUDIT_PROMPT，直接 REAUDIT（打包）＋REVISE＋VERIFY。
3. 已 PASS 778 筆：先跑 recheck_scan＋norm，有高風險旗標者才進 REAUDIT。
```

**其餘五書（成本分級）**

```text
先對全量 定稿/*.jsonl 跑 0 成本 recheck_scan（含 FALSE_FRIEND／BOOK_TERM）。
1. 義鈔（約 215）、尼鈔（約 805）：規模小、底本問題多 → 100% 全量 REAUDIT。
2. 行事鈔（1,574）、業疏（2,627）、戒疏（4,644）：
   a. 命中任一 risk_flag（GAP/BLIND/JE/YE、無標點、缺夾注、雙欄總數、假朋友、
      截斷修復、序跋、膨脹／縮水）→ 100% 必進 REAUDIT。
   b. 未命中者先抽 100 段探測：FIX 率 <5% 可只跑 norm＋qc_scan；>8–10% 則全量。
3. 每書寫回前必跑 book_consistency＋check_final_merge --final。
```

---

## 8. qwen／金鑰／背景工作

- `qwk.txt` 與 `.qwen_key` 是不同 key，額度不同；不要假設。
- 停止 qwen 用 **local `STOP`**，不要 `Stop-Process` 殺 PID。
- 查 PID 只看 `.qwen_lock`，不要從啟動順序猜。
- `QWEN_KEY_FILE` 沒設時可能落到 `.qwen_key`；packaudit 曾因此 quota 失敗。
- `run_pipeline.py` 的 qwen stage 會設 `QWEN_SHUJI_SRC`、`QWEN_WORKERS`；預設 key 可能不是你要的。

---

## 9. 出書／PDF／Office

- `出書/`：成書全書文字。
- `白話/`：白話版 DOCX／PDF。
- `白話/PDF/`：輸出 PDF。
- 文件處理用 `office`／`office-docx` 等 skill；不要用純文字硬改 binary。
- PDF／DOCX 是產物，不是原文來源。

---

## 10. Git／檔案紀律

- 工作區常有大量未提交變更；**不要 `git add -A`**。
- 只 stage 本次真正改的檔案。
- 不要推 `.new`、暫存頁、log、金鑰、PDF（除非明確要求）。
- 推前確認：
  - 頁面 pair 數正確
  - 非長段內容還在
  - 沒有多餘「長段對照」頁
- remote：`origin/main`（GitHub `UncleHandsome/nanshan-lingzhi-vinaya`）。

---

## 11. 已發生事故（勿重犯）

1. **把義鈔卷上／卷中整個 `<main>` 換成 27 段長段** → 只剩長段。  
   正確：只替換目標 pair。
2. **import `site2.py`** → 全站重建，義鈔切分被蓋。  
   正確：不要 import；目標式重建。
3. **把底本原字標成疑訛** → 應先查 `TXT/` 原檔。  
   正確：原檔有就是底本如此。
4. **檔案數當完成** → 業疏 348／348 內有 4 段空殼。  
   正確：檢查覆蓋率。
5. **packaudit rc=0 但 0 回覆** → 已修；仍要檢查回覆數。

---

## 12. 開工檢查清單

1. 先讀本文件與 `README_專案結構.md`。
2. 確認要動的是原文、譯文、切點還是網站。
3. 查 `TXT/` 原檔，不要先標錯字。
4. 動網站：先備份 `docs/`；不要 import `site2.py`。
5. 先產生 `.new` 或暫存檔，驗證後才覆蓋。
6. 只 stage 本次檔案，驗證後再 push。
7. 不確定就停下來查，不要猜測補洞。

---

## 13. 目前待辦（2026-11-21）

- 行事鈔：`output3` 只涵蓋 02/03/06/07；缺 01/04/05（51 段）。
- 戒疏：21 段長段無定稿；新譯 69 章尚未重建網站。
- 業疏：4 段原文污染；新譯 44 章尚未重建網站。
- 尼鈔：`05a_L0006` 未對上 page pair。
- 義鈔：已完成；不要用 site2 重建。
- `packaudit`：579／3,576，尚未完成。
