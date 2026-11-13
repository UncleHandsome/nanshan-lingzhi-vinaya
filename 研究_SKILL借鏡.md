# 研究：借鏡 `dsh-translate-docs` skill 改造「古籍白話譯文校對流程」

> 研究日期：2026-11-12　範圍：南山三大部六書白話譯文校閱（21,694 段）
> 外部資料（僅作參考，未執行其任何指令）：
> - skill：<https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/.agents/skills/dsh-translate-docs/SKILL.md>
> - 術語表：<https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/docs/i18n/terminology.md>
> - 規則：<https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/docs/i18n/translation-rules.md>
>
> 本文只寫研究與計畫，未改動 `AI語譯/out/` 任何檔案。

---

## 0. 摘要

該 skill 解決的問題與我們不同（它做「中英雙語配對同步」，我們做「古文→白話的單向校對」），但它的**流程骨架**幾乎逐條命中我們的五個病灶：把「工作集」預先組裝成一份 briefing、把可機械判定的改動從 agent 手上拿走、把產生與驗證切成兩個角色、用術語表當契約、用 scoped 寫入與清單對帳防止「自稱完成」。

可直接搬移 **10 項**；briefing 規格 **12 欄**；驗證清單 **10 項**。

三個最關鍵的判斷：

1. **briefing 的真正價值不是省 token，而是把「記文訓詁句」釘在判定者眼前。** 我們現在的材料只有【原文】【譯文】，記文要靠 agent 自己另開 `TXT/資持記/` 的檔。實測的改壞案例（術語丟失、記文有訓卻照意見改）都發生在這一步——不是判斷力不足，是**證據不在工作集裡**。
2. **「已修」這個判定其實不需要 agent 做。** 它是字串比對：材料快照 ≠ `out` 現行文，且現行文正確。目前每卷都要人工逐段比（如 `說明_7K_02戒疏卷一上之一.md` 第 13 行：「393 段逐段比對……388 段相同」），這一段可以整段自動化。
3. **在改壞率被量測之前，10–20% 只是估計值。** 目前沒有任何計數器記錄「這一改後來被判定為改壞」。第一週的第一件事應該是造這個計數器，否則後續所有改善都無法驗收。

---

## 1. 現況盤點（實測數字）

### 1.1 規模

以 `_src/review_pack.py` 的段落定義實測（原文取 `split('\n')[5:]` 之非空行；譯文取 `\r?\n\r?\n` 分段）：

| 書 | out 檔數 | 段數 |
|:--|--:|--:|
| 01_行事鈔 | 35 | 1,591 |
| 02_戒疏 | 69 | 9,691 |
| 03_業疏 | 45 | 5,189 |
| 資持記 | 73 | 4,182 |
| 04_比丘尼鈔 | 13 | 807 |
| 05_拾毗尼義鈔 | 9 | 234 |
| **合計** | **244** | **21,694** |

材料端：`校閱_7K/` 2,808 檔（平均 7.7 段／檔）、`batch_qwen/r7k/` 回覆 2,745 檔（**缺 63 檔**）、`校閱_10K/` 1,912 檔（舊規格）。已完成 01_行事鈔 13 卷、02_戒疏 試跑 2 卷。

**覆蓋率母數已可確立**：`校閱_7K` 內【原文】標記總數恰為 **21,694**，與 `out` 段數完全相等——代表 7K 材料對全書是無重複、無遺漏的 1:1 覆蓋。這讓 V3（覆蓋率對帳）有一個精確可驗的母數，不必再靠「大約」。

### 1.2 現行流程與實際瓶頸

| 步 | 動作 | 現況問題 |
|:--|:--|:--|
| 1 | Qwen 對每檔（約 10 段）提意見 → `resp_NNN.txt` | 只看到【原文】【譯文】，看不到記文 → 大量誤報 |
| 2 | 判定者讀材料＋意見，另開 `TXT/資持記/<卷>.txt` 對讀 | 開哪個檔、讀多細，**每個 agent 不一樣** |
| 3 | 四選一：真錯／已修／誤報／存疑 | 「已修」「誤報」靠人眼比對，可自動化 |
| 4 | 讀現行→只換目標段→寫回 | 有 `find` 恰一次的保護，但**無回歸 gate** |
| 5 | 寫 `說明_7K_<卷>.md`（總表＋逐檔明細） | 格式好，但**沒有機器可讀的判定欄** |
| 6 | 存疑 append `存疑材料/7K_存疑.md`（現 87 條） | 只能 append，曾發生整檔覆寫 |

### 1.3 五個病灶 → 根因 → 對應機制

| 病灶 | 根因（研究判斷） | 對應 skill 機制 |
|:--|:--|:--|
| 改壞率 10–20%（術語丟失、記文有訓卻改錯） | 判定時記文訓詁句不在眼前；允許整段重寫；無改後回歸 | M1 / M2 / M3 / M5 / M6 |
| 專名不統一（姚秦／後秦／秦代並存） | 無強制術語表，憑記憶與上下文 | M7 / M10 |
| 同一 agent 又改又驗 | 無角色分離、無 patch 契約 | M5 |
| 宣稱完成但只做 30/57 檔 | 完成判定靠自述，無清單對帳 | M8 / M9 |
| 意見命中率低（條級 12–23%） | 潤飾／增註／真錯混在一起送判 | briefing 的 opinions 預分類 |

條級命中率實測（以 `說明_7K_*.md` 總表回推）：

- 01_行事鈔 卷首（82 段）：改 31 處 vs 否決 226 條 → **12.1%**
- 01_行事鈔 卷上之一（162 段）：改 134 處 vs 否決 451 條 → **22.9%**
- 02_戒疏 卷一上之一（393 段）：50 檔中改段率極高（如 448 檔 9/9），但那是因為該卷為疑難密集區

→ **瓶頸不是「意見太少」，而是「意見沒有先分流」**。潤飾與增註類占了七至八成，把它們與真錯分開送判，是 briefing 最省成本的一刀。

---

## 2. 可搬移機制表（10 項）

「原文依據」為 skill 原文節錄（英文為原文，中文為本文所譯）。

| # | 機制 | 原文依據（skill 片段） | 我們的對應做法 | 預期效果（可量測） | 成本 |
|:--|:--|:--|:--|:--|:--|
| **M1** | **briefing 驅動：單一工作集** | "The briefing is the translator's whole working set — the subagent does not re-read the guidance corpus (the rules digest, terminology rows, and each changed unit's three-way context are inline) and does not re-derive the diff." | `_src/build_brief.py` 為每個 `校閱_NNN.txt` 產一份 `.md`：原文＋記文＋現行譯文＋基線＋意見＋術語＋規則摘要。派工只給 brief 路徑，禁止 agent 自行開 `TXT/資持記/` | 每段前置成本↓；同一卷不同 agent 看到**同一份證據**；術語漂移因記文訓詁句 inline 而下降 | 2.5 人日（約 400 行） |
| **M2** | **三方對照（last-confirmed / current source / current counterpart）** | "contains the authored side's diff since the last confirmed-consistent state, each changed unit's last-confirmed source, current source, and current counterpart text (with line numbers)" | 我們有天然三方：**原文**（權威）／**基線譯文**（`歸檔/7K卷修正前/<書>/<chunk>_v.txt`）／**現行譯文**。brief 顯示「基線→現行」的 diff 與「材料快照→現行」的差異 | 「已修」判定自動化（省去逐段人眼比對）；改壞可在 diff 中現形；回滾有錨點 | 0.5 人日（併入 M1） |
| **M3** | **最小編輯** | "Smallest edit that covers the diff. Preserve the reviewed phrasing of everything the diff does not touch, then verify the changed hunks clause by clause against the source: nothing added, nothing dropped." | 改寫只能提出「find → replace」的最小片段 patch（JSON），**禁止輸出整段**。改後段落 = 現行段套用 patch，其餘逐字不動 | 切斷「連帶改動」這個改壞主因；diff 可審；`find` 不唯一即拒絕套用 | 0.2 人日（提示詞＋schema） |
| **M4** | **機械改動 `--apply`：可判定者不交給 agent** | "Mechanical-only diff? `--apply` it. … `gen-translation-brief --apply <pair>` splices … and structure-validates the result before writing — no subagent, no hand-editing." | 三類走機械層：(a) 單詞級替換（`find` 在該段恰一次）；(b) 術語表「不要譯作→正譯」全域替換（白名單制）；(c) 全半形／異體字／重複標點 | 估計 20–30% 的接受改動免 agent；零判斷誤差；可批次重跑 | 1 人日（約 120 行） |
| **M5** | **產生／驗證分離（兩段式）** | "Pass 2 — verify against the source, clause by clause. Fidelity is checked here, not written in: confirm nothing was added or dropped, every term follows the table, and each code span survived verbatim." | 角色 A（改寫）只產 patch；角色 B（驗證）只產 verdict，**無寫檔權**，且看不到 A 的理由，只看 brief＋patch＋改後段落 | 消除自我確認偏誤；驗證可獨立量測攔截率 | 0.5 人日 |
| **M6** | **單獨讀一遍（無原文狀態下複讀）** | "Read the completed counterpart alone. After the source comparison, read the translated file without the source beside it and rewrite phrasing whose awkwardness only becomes visible in isolation." | 驗證第 9 項：不看原文，只讀改後白話段，回報「讀不懂／讀起來像另一件事／殘句」。專抓 `02_戒疏/11c_卷三上之二` 那種「……身分階位不同的緣故的緣故。」 | 抓出對讀看不出、只有盲讀會露出的病灶（重複、殘句、半文半白） | 0.2 人日 |
| **M7** | **術語表契約（含「不要譯作」與待定）** | "terminology.md is the source of truth in both directions … every listed term MUST follow its row and its '不要譯作' prohibitions." ／ "Never invent a rendering inline." ／ "an unlisted term … stays English under 「待定术语」" | `glossary.tsv` 五欄（見 §4）。brief 只 inline「本段命中列」；未列術語一律進 `candidates.tsv`，**不得臨場自創**；「待定」條目不得據以判 P0 | 術語錯位（P0 大宗）從「靠記憶」變「靠查表」；專名三寫並存可被 gate 掃出 | 2 人日（建表＋抽取） |
| **M8** | **scoped 寫入，拒絕裸跑** | "`--write` names exactly the pairs you confirmed — it refuses to run bare so a bulk re-record is always an explicit `--all`." | `apply_patch.py --卷 <書>/<卷>` 只接受明示卷別；`--all` 需另加 `--i-know`；每次寫入前備份並記 `edits.jsonl` | 誤覆蓋、跨卷誤寫 → 0；每批可回滾 | 0.5 人日 |
| **M9** | **清單對帳（missing / out-of-sync / ok）** | "`verify-translation-pairing --list` prints every in-scope document as missing / out-of-sync / ok. Missing and out-of-sync rows are contract violations; the normal check rejects them." | `check_coverage.py --卷`：派工 tsv 行數 ↔ 材料檔 ↔ 回覆檔 ↔ 說明／處理記錄 ↔ 實際 diff 段數，四欄對帳，缺一即紅 | 「30/57 卻回報完成」直接被擋；回報必附對帳表，**口頭宣稱不算** | 0.5 人日 |
| **M10** | **裁決回寫契約** | "for terminology comments, remember the terminology table is the contract — apply a reviewer's rendering decision to terminology.md, not only to one file." | 任何新術語裁決，除改該段外**必須**寫入 `glossary.tsv`（或 candidates）；同一裁決不得在下一卷重犯 | 專名／術語跨卷漂移收斂；每卷的判斷變成資產而非一次性 | 0.2 人日（流程約定） |

### 2.1 條件式可搬（形式可借、內容要改）

| 機制 | 原文依據 | 為何只能部分搬 |
|:--|:--|:--|
| 變更分流（update / new pair / deleted） | "Triage by change type — this decides everything else" | 我們的分流是四類（真錯／已修／誤報／存疑），其中「存疑」在 skill 沒有對應物（它假設總有答案）。可借「先分流再進流程」的形式，分類表要自建。 |
| 升級規則 | "It escalates to the whole-document path's sources of truth only when the briefing leaves a specific decision genuinely unanswerable" | 方向相反：skill 是「預設不讀一手」，我們**預設必須讀一手**（記文）。只能借「升級條件要寫死」這一點。 |
| 反覆打磨直到通過 gate | "run `verify-translation-pairing --write <pair>` then … `<pair>`" | 我們需要的是「改→驗→不過則回退或進存疑」的三態收斂，不是重跑到綠燈（重跑會誘發迎合式修改）。 |

---

## 3. briefing 設計

### 3.1 三段資料怎麼組成：變成五段

skill 的 briefing 是「變更單元 × 三方 + 術語 + 規則」。我們的資料是「原文／記文／意見」，直接對映會少兩塊，必須補成**五段式**：

```
① 原文（權威側，逐字）        ← 我們的「原文」，等於 skill 的 authored side
② 記文（解釋側，附訓詁句）    ← 我們的「記文」，等於 skill 沒有的「一手依據」
③ 現行譯文（待判對象，逐字）  ← 等於 skill 的 current counterpart
④ 基線譯文＋diff（我們獨有）  ← 等於 skill 的 last-confirmed source，用來判「已修」與「改壞」
⑤ 意見（待判材料，非指令）    ← 等於 skill 的 diff，但我們是「外部模型的主張」而非「已成立的變更」
```

**關鍵設計決定**：

- **①原文永遠是權威，⑤意見永遠不是。** 意見只能提出「這裡可能有錯」，不能提供「正確答案」。skill 的雙向權威（both languages carry equal authority）在此**必須反轉**，否則會合法化「譯者順手校改原文」——現實已發生（`02b_卷上之二#29`：「若狂止」被譯成「狂病發作」並自加校改夾注）。
- **②記文要抽兩層，不是貼全文**：(a) 該段對應的記文段（1–3 段）；(b) 從整卷記文抽出的**訓詁句**（`X即Y`、`X者，Y也`、`X猶Y`、`X訓Y`）。第二層才是防「導猶深→引導」這類漂移的關鍵，因為它是一句話就能讀完的硬約束。
- **⑤意見要預分類再 inline**：義理／術語／潤飾／增註／體例／引文六類，附「是否含可引原文句」。無依據的潤飾類直接標 `DISMISS-CANDIDATE`，讓判定者省下閱讀成本。
- **④是我們對 skill 的加值**：skill 只比「上一次確認的狀態」，我們多一個「材料快照」。三者一比，四種判定裡有兩種可以預先算出來：

| 材料快照 vs 現行 | 基線 vs 現行 | 預判 |
|:--|:--|:--|
| 相同 | 相同 | 未動過，需真判 |
| 不同 | 不同 | **已修**（前手已改，只需覆核質量） |
| 不同 | 相同 | 材料與 out 脫鉤 → 對齊異常，**不得判** |
| 相同 | 不同 | 改過又回退 → 進「改動史」警示 |

### 3.2 brief 版面（固定七節）

```
---（YAML front-matter：機器欄，見 3.3）
# BRIEF 校閱_444 ｜ 02_戒疏/01a_卷一上之一#40
## 1 原文
## 2 記文（含訓詁句）
## 3 現行譯文
## 4 基線與 diff
## 5 意見（已預分類）
## 6 術語（本段命中列）
## 7 判定規則摘要（固定 12 行）
```

第 7 節是固定字串（不隨段變），內容＝現行 `說明_7K_*.md` 第二節的「判定原則」壓縮版：改／不改／存疑三類判準、引文界線、夾注體例、禁整段重寫。這等於 skill 的 "digest of the binding update rules"。

### 3.3 十二欄規格

| # | 欄位 | 型別 | 內容 | 來源 | 缺失處理 |
|:--|:--|:--|:--|:--|:--|
| 1 | `id` | str | `書/chunk#idx` | 材料段標籤 | 必填，缺則整段不作 brief |
| 2 | `src` | str | 原文段，逐字 | `TXT_分卷/<書>/<chunk>.txt` 第 idx 個非空行（`split('\n')[5:]`） | 長度不符 → `align=mismatch`，只讀不判 |
| 3 | `src_ctx` | str | 前後各 1 段原文（截 200 字） | 同上 | 卷首／卷尾可缺 |
| 4 | `tr_cur` | str | 現行譯文，逐字 | `AI語譯/out/<書>/<chunk>.txt` 第 idx 個非空段 | 段數不足 → `mismatch` |
| 5 | `tr_base` + `diff_base` | str | 基線譯文＋「基線→現行」字元級 diff | `歸檔/7K卷修正前/<書>/<chunk>_v.txt`；無備份則 `git show` | 無備份 → `base=none`，不做已修預判 |
| 6 | `snapshot_state` | enum | `same` / `already-fixed` / `desync` / `reverted` | 材料譯文 vs `tr_cur` vs `tr_base`（§3.1 表） | 必填（可算） |
| 7 | `note` | str | 記文對讀段 1–3 段＋出處 | 見 §3.5 對映策略 | **寧可 `none`，不可貼錯** |
| 8 | `gloss` | list | 訓詁句 ≤6 條（`X即Y`／`X者Y也`／`X猶Y`／`X訓Y`） | 記文段＋同卷記文 regex | 空 → 標 `no-gloss`（本身就是訊號：此段無一手釋義，不得判 P0） |
| 9 | `terms` | list | 命中術語列（術語／正譯／不要譯作／依據） | `glossary.tsv` 掃 `src`+`tr_cur`+`opinions` | 無命中 → `terms=[]` |
| 10 | `opinions` | list | 該段全部意見，原樣＋編號＋預分類 | `batch_qwen/r7k/resp_NNN.txt` | 無回覆 → `no_opinion`（該檔不派工） |
| 11 | `prior` | object | 既有存疑條目、改動史、回退紀錄 | `存疑材料/7K_存疑.md`、`edits.jsonl` | 空物件 |
| 12 | `target` | object | 目標檔段落數、行尾、BOM、本段行號 | 讀 `out` 檔頭尾 | 必填（寫入保護用） |

治理欄（front-matter 另加，不列入契約十二欄）：`brief_hash`（內容 md5）、`glossary_ver`、`built_at`、`builder_ver`。agent 回報必須引用 `brief_hash`，防「拿舊 brief 判新文」。

### 3.4 產生腳本規格（`_src/build_brief.py`）

```
用法
  python _src/build_brief.py --卷 02_戒疏/卷一上之一
  python _src/build_brief.py --chunk 444
  python _src/build_brief.py --missing --limit 50
  python _src/build_brief.py --卷 … --dry-run

輸入（依序）
  1. AI語譯/_work/review/卷派工/<書>_<卷>.tsv      → chunk 清單（第 1 欄，3 位數）
  2. 校閱_7K/校閱_<nnn>.txt                        → 材料段（【NNN-MMMM】標籤、原文、譯文）
  3. batch_qwen/r7k/resp_<nnn>.txt                 → 意見（缺則 no_opinion）
  4. TXT_分卷/<書>/<chunk>.txt
     （業疏改 TXT_分卷_標點/03_業疏/；資持記改 TXT_分卷/資持記_細分/）
  5. AI語譯/out/<書>/<chunk>.txt
  6. 歸檔/7K卷修正前/<書>/<chunk>_v.txt（可缺）
  7. TXT/資持記/<卷>.txt 或同 chunk 內【記文】段
  8. AI語譯/_work/glossary/glossary.tsv
  9. AI語譯/_work/review/rules_digest.txt（固定 12 行）

流程
  for chunk in 清單:
      解析材料 → [(seg_no, book, chunk, idx, src_snap, tr_snap)]
      對每段:
        a. 以 (book, chunk, idx) 定位 out 段與 TXT 段；段數不足 → mismatch
        b. 算 snapshot_state（4 種，見 §3.1）
        c. 取 note（§3.5 策略）；取不到 → none
        d. 抽 gloss（4 個 regex，去重，≤6 條）
        e. terms = glossary 掃描（術語欄與「不要譯作」欄都掃）
        f. opinions = 切條 → 歸戶 → 預分類 → 標「有無可引原文句」
           段號不屬本檔 → 隔離到 orphan/（防 449 串檔）
        g. 組 brief，套上限（正文 ≤8,000 字，超出先截 ctx 再截 note）
  寫 briefs/<書>/<卷>/<nnn>.md
  更新 briefs/index.tsv（brief, book, vol, chunk, segs, with_opinion, note_ok, terms_hit, bytes, hash）

自我檢查（builder 內建，任一失敗即整檔不產出）
  - 每段有 id / src / tr_cur（或標 mismatch）
  - 每段有 snapshot_state 與 target
  - 有 opinions 的段，意見數與 resp 檔解析數相符（±0）
  - 單檔 ≤ 8,000 字、≤ 12 段
  - index 的 hash 與檔案內容一致
```

### 3.5 記文對映策略（分工況）

| 書 | 記文在哪 | 策略 | 信度處理 |
|:--|:--|:--|:--|
| 02_戒疏 | 同段／緊鄰段的【記文】（《行宗記》已含在 `TXT/02_四分律含注戒本疏.txt`） | 取同 chunk 內緊鄰【記文】段；本段即【記文】則取同段前後 | 高，直接用 |
| 03_業疏 | 同上（疏文／記文同流） | 同上 | 高 |
| 資持記 | 本身就是記文 | 反向：對讀被釋的鈔段（用 `note_map` 反向索引） | 中；無對映則 none |
| 01_行事鈔 | `TXT/資持記/` 另一本書 | **需建 `note_map.tsv`**：以 `bounds_篇NN.json`（篇級累計邊界）給粗定位，再用 4-gram 交集在 ±40 記段窗口內細對；取最高分且 ≥ 門檻者。可重用 `_src/yeshu_offset_dp.py`、`_src/_mw_align.py` 的對齊做法 | 低於門檻 → **none** |
| 04_比丘尼鈔 / 05_拾毗尼義鈔 | 原文夾注（（）內）為主 | 抽夾注作 gloss，不硬找記文 | 中 |

**硬規則：貼錯的記文比沒有記文更糟。** 錯的記文會製造高品質的誤報（判定者引錯據），這是現行流程最隱形的失敗模式。所有低信度一律 `note: none`。

### 3.6 範例（節錄＋裁剪，非逐字全文）

```yaml
id: 01_行事鈔/00_卷首#41
snapshot_state: same
note_ok: true
gloss_n: 2
terms_hit: 3
```

```md
## 1 原文（節錄）
第一序教興意。夫至人興世，益物有方；隨機設教，理無虛授。……觀下律中，凡所制者，並懷異術。

## 2 記文（訓詁句）
- 「並」＝皆、都（全稱，非「多是」）
- 「異術」＝外道
- 「懷」即佛意（主語是佛意，不是「所對的」）

## 3 現行譯文
第一門：序教興意……觀下律中，世尊凡有所制，所對的「多是」心懷異端方術的外道。

## 4 基線 diff
（材料快照＝現行；無基線 → 首次校閱）

## 5 意見（節錄，已預分類）
- O1〔術語〕「並」譯「多是」弱化全稱 → 有原文句
- O2〔潤飾〕「部派宗執」帶貶義 → DISMISS-CANDIDATE
- O3〔增註〕「提誘」宜標譯按 → DISMISS-CANDIDATE（違體例）

## 6 術語
| 術語 | 正譯 | 不要譯作 | 依據 |
| 並 | 皆、都 | 多是 | 記「並，皆也」 |
| 異術 | 外道（方術） | 異端方術（單用） | 記「異術即外道」 |
| 撰結 | 撰集結成戒法 | 結集（專指佛滅後結集） | 記／律學語境 |

## 7 規則摘要
（固定 12 行：改／不改／存疑、引文界線、夾注體例、禁整段重寫……）
```

---

## 4. 術語表規格

### 4.1 五欄設計

沿用 skill 的「正譯／不要譯作／備註」骨架，把**「首次出現」換成「依據」**（我們沒有雙語首現體例，但有比首現更硬的需求：P0 必須可引一手）。

| 欄 | 名稱 | 內容 | 範例 | 說明 |
|:--|:--|:--|:--|:--|
| 1 | `術語` | 原文字形；異體、別寫以 `\|` 分隔 | `並`／`撰結`／`姚秦\|後秦` | 掃描鍵；比對時先做異體正規化 |
| 2 | `正譯` | 本專案定譯（白話） | `皆、都`／`撰集結成戒法`／`姚秦（即後秦）` | 唯一允許的譯法；空白＝尚未定（待定） |
| 3 | `依據` | 記文原句／律本／CBETA 卷次 | `記：並，皆也`／`記：異術即外道` | **可引用字串**，供 V7 溯源；無依據不得填 |
| 4 | `不要譯作` | 禁用譯法，含歷史錯譯 | `多是`／`結集`／`秦代` | gate 掃這個欄；可留白 |
| 5 | `備註` | 歧義分支、語境限制、夾注規則、兩讀 | `兩讀皆通，判存疑`／`引文內不得改字` | 人讀欄；`狀態` 不寫在這裡 |

治理欄（機器用，另存兩欄，不列入契約五欄）：`id`（`T0001`）、`狀態`（`候選`／`定案`／`凍結`／`待定`／`棄用`）。

**為什麼不放「首次出現」**：那是雙語配對的產物（首現加英文括注）。我們的中文譯文若照搬，會鼓勵「每遇術語就加（）」，而 Qwen 意見已經在大量建議加註、且現行判定原則是「全書體例不加註」——搬進來會直接與體例衝突。首現相關的只有一條可留：**同一術語在同一卷內不重複加註**，寫進第 5 欄即可。

### 4.2 抽取來源清單

| # | 來源 | 可抽什麼 | 預估條數 | 抽取方式 | 優先 |
|:--|:--|:--|--:|:--|:--|
| S1 | `附錄_名相與度量衡.md` | 罪名（波羅夷／僧殘／偷蘭遮……）、度量衡、異體字 | ~90 | 解析三節 markdown 表 | P0 |
| S2 | `交接/校閱計畫_白話譯文.md` §6.2 | 12 條高風險詞（知法、義加、唱相、相從、示問者、尼三、觸煮、共輿、進止、言議、相可、約） | 12 | 人工轉錄（已含「常見誤譯→正譯方向」） | P0 |
| S3 | `AI語譯/_work/review/說明_*.md`（19 檔） | 86 條「改」紀錄的「改前→改後＋記文依據」 | ~120 | 半自動：抽 `- **NNNN**：…改「…」` 與引號內記文 | P0 |
| S4 | `存疑材料/7K_存疑.md`（87 條） | 二讀未決術語 → `狀態=待定`，`正譯` 留白 | ~40 | 人工（需判斷是否為術語） | P1 |
| S5 | `TXT/資持記/*.txt`（16 檔）、`TXT/02_…戒本疏.txt` | 定義句 `X即Y`／`X者，Y也`／`X猶Y`／`X訓Y` | 300–600 | regex + 去重 + 頻次排序 | P0 |
| S6 | `_src/scan_modern_words.py`（`WORDS` 37 詞） | 現代法律／行政／商業禁用詞 | 37 | 直接讀清單 | P1 |
| S7 | `AI語譯/_work/review/說明_現代詞_*.md` | 實際處置（判決→判定、證據→明證、罪犯→罪過……） | ~20 | 半自動（表格式） | P1 |
| S8 | `TXT/` 卷首、序文、譯者傳 | 專名：朝代（姚秦／後秦）、人名（佛陀耶舍／竺佛念）、書名 | ~60 | grep ＋人工定案 | P0 |
| S9 | `歸檔/7K卷修正前/**` vs 現行 `out/**` | 實際改動對（A→B），可反推術語替換 | ~1,000 對 | diff 腳本（段級），再人工篩 | P2 |
| S10 | `docs/appendix.html` | 既有 200 條名相 | ~200 | 解析 HTML | P1 |
| S11 | 原文夾注（（）內） | 術語＋自帶解釋 | 待估 | regex | P2 |

**v1 目標**：合併去重後 **400–600 條**，其中「不要譯作」有值者 ≥150 條、「依據」可引者 ≥300 條。P0 來源（S1/S2/S3/S5/S8）先做，其餘進 candidates。

**專名特別處理**（病灶 2 的正面解）：姚秦＝後秦（同一朝代異稱），「秦代」是錯的（易讀成秦始皇之秦）。此條必須有 `不要譯作=秦代`、`正譯=姚秦（即後秦）`、`依據=史傳／譯經記`，並在 gate 掃描時列出全部出現位置，一次性統一。實測分佈：`out/02_戒疏/01c_卷一上之一.txt`（「在秦代就已翻譯」）、`01d_卷一上之一.txt`（「後秦漢語意譯」×3、「姚秦時代」×2）。

### 4.3 維護流程

```
候選（candidates.tsv）
  └─ 校閱命中 + 至少一條可引依據 + 1 人覆核 ──→ 定案
        └─ 同一裁決第二次出現 ──→ 凍結（v1 起只增不改）
              └─ 需修改 ──→ 開變更記錄 + 全量重掃 + 版本號 +1
待定（正譯空白）
  └─ 找到一手依據 ──→ 定案
  └─ 逾 20 條未決 ──→ 升級為專題（一次查完，避免逐卷卡住）
```

五條硬規則：

1. **凍結只增不改。** 改一條會影響所有已校段落，必須走「變更記錄＋全量重掃」，否則前後批標準不一（`校閱計畫` 第十節已列此風險）。
2. **當批回寫，不直接改主表。** 校閱者遇到新術語，寫進該批 `candidates.tsv`；主表由固定流程合併，避免多人同時改。
3. **gate 掃描要能容錯。** `check_terms.py` 命中「不要譯作」→ 紅燈，但允許 `glossary_allow.tsv` 白名單（例如引文內、書名內），白名單也要留理由欄。
4. **brief 記錄 `glossary_ver`。** 同一批必須同一版表，否則無法重現判定。
5. **每季重抽 S5 定義句**，與現表 diff，新出現者進候選；這是表會自己長大的機制。

---

## 5. 驗證清單（驗證 agent 的 10 項檢查）

### 5.1 產生／驗證分離的落地

| 角色 | 做什麼 | 工具權限 | 輸出 |
|:--|:--|:--|:--|
| **A 改寫者** | 讀 brief，對每個真錯提出最小 patch | 可讀檔，**不可寫 `out/`** | `patch.json`（`id`／`op`／`find`／`replace`／`basis`／`confidence`） |
| **B 驗證者** | 讀 brief＋patch＋改後段落，逐項打勾 | **只讀**，不寫任何檔 | `verdict.json`（`id`／`pass` 或 `reject`／`failed_checks[]`／`reason`） |
| **C 套用器** | 純程式：檢查 `find` 唯一 → 套用 → 跑 gate | 唯一有寫入權者 | `edits.jsonl`、gate 報告 |

三條防偏誤規則：
- B **看不到 A 的 `reason`**，只看 patch 與改後文；
- B 的 verdict 必須指名失敗的檢查編號（不能只寫「不好」）；
- A 與 B 不一致 → 不進第三輪自動辯論，直接進「存疑」或人工（避免迎合式修改）。

### 5.2 十項檢查

| # | 檢查 | 執行者 | 方法 | 不通過怎麼辦 |
|:--|:--|:--|:--|:--|
| **V1** | 檔案完整性：段數、段序、行尾、BOM、尾端換行、空行結構不變 | 程式 | 與基線／備份逐位元比較；段數與 `target` 比對 | 整批回退（不逐段修） |
| **V2** | 非目標段零差異 | 程式 | 段級 diff，異動集合必須等於 patch 目標集合 | 回退越界段，記 `out-of-scope` |
| **V3** | 覆蓋率對帳 | 程式 | 派工 tsv 行數 = 材料檔 = 回覆檔（或已標 `no_opinion`）= 有 verdict 的段數 | 紅燈，不得宣稱完成 |
| **V4** | 禁用譯法掃描 | 程式 | `glossary.tsv` 第 4 欄全文掃 `out` 目標卷 | 逐處列出，人工判定或改寫 |
| **V5** | 術語一致性：同卷內同一術語只有一種譯法 | 程式＋抽核 | 以第 1 欄為鍵，掃該卷 `out`，列出多譯處 | 多譯 → 擇一，或進存疑 |
| **V6** | 引文界線：「」內不得增刪字，夾注不得混入引文 | 程式（字數）＋agent（語序） | 原文引文與譯文引文的字元集合差；`「」` 配對數；引號內是否含 `（）` | 還原引文，解釋移到引號外或刪 |
| **V7** | 依據可溯源：每條 patch 的 `basis` 必須在記文／律本原文中字面命中 | 程式 | 對 `basis` 做 4-gram 覆蓋率 ≥0.9 的比對，檢索範圍＝該段 note＋同卷記文 | 無據 → patch 作廢，降為「存疑」 |
| **V8** | 病灶掃描：重複詞、殘句、半文半白、標點疊用、段內贅字 | 程式 regex ＋ agent 複核 | `(的.{0,4})\1`、`。。`、`，。`、`的緣故的緣故`、連續虛詞 | 回退該處，只保留最小 patch |
| **V9** | 盲讀複核：不看原文，只讀改後段落 | agent | 回答三問：讀得懂嗎／像在說同一件事嗎／有沒有殘句 | 讀不懂 → reject，附最小證據 |
| **V10** | 義理四項對讀：主詞施受／範圍／否定／條件 | agent | 逐句對原文，寫出「誰→做什麼→對誰→在什麼條件下」再核譯文 | 任一項不符 → reject（P0） |

分工比例：V1–V5、V7、V8 共 7 項可完全程式化（跑一次數秒）；只有 V6、V9、V10 需要 agent 判斷。**把 7 項交給程式，是這套流程最大的成本節省**——現在的「又改又驗」其實有七成在做人眼可程式化的事。

### 5.3 驗證者提示詞骨架

```
你是驗證者，不是改寫者，沒有寫檔權。
輸入：brief（含原文、記文、現行譯文、意見）、patch（find→replace）、改後段落。
任務：逐項檢查 V1–V10，只輸出 verdict.json。

規則：
- 不得提出新譯法；發現問題只回報「第幾項、證據句」。
- V7：patch.basis 必須能在 brief 的記文段找到；找不到即 reject，不得自行補據。
- V9：先不看原文讀一遍改後段落，覺得「讀起來像另一件事」就 reject。
- V10：對每個子句寫出「誰→做什麼→對誰→在什麼條件下」，與譯文不符即 reject。
- 不確定 → reject，reason 寫「證據不足」，由人工終判（不要猜）。
```

---

## 6. 不適用機制與理由

| # | 機制 | 原文依據 | 為何不適用 |
|:--|:--|:--|:--|
| N1 | **雙語配對、雙向權威** | "Both languages carry equal authority — a change is authored in either one, and that side is the source for that update." | 我們是單向：原文權威 > 譯文。照搬會讓「譯者順手校改原文」合法化——現實已有案例（`02b_卷上之二#29`「若狂止」被譯成「狂病發作」，並自加「原文作止，依律本應作發」的夾注）。這條必須**反向**設計：原文不可被譯文修正，疑則存疑。 |
| N2 | **三檔配對（`.md`／`.zh.md`／`.i18n.yaml`）、分節 hash、語言切換行、manifest** | "the three-file pair … the consistency record's per-section hashes, the language-switcher lines" | 我們沒有配對檔、沒有切換行、沒有 HTML 語言層。等價物是「out 段 ↔ 原文段 1:1」的契約，用 `review_state.json` 的 md5 ＋段數校驗即可，不需要 sidecar。搬進來只會多一層要維護的狀態。 |
| N3 | **結構簽名（heading depth／fenced code／table rows／list kinds／ordered-list starts）** | "The pairing gate checks heading depths, fenced code blocks, table row and column counts, list kinds, ordered-list starts, list item counts, link locale, and semantic targets." | `out` 是純段落，沒有 markdown 結構；唯一結構是「段數」與「篇名行」，已由 V1 覆蓋。硬搬會產生大量假陽性，且掩蓋真正的問題（段數與段序）。 |
| N4 | **code fence 逐字相同、inline code verbatim** | "fenced code blocks — **byte-identical, including comments** … inline code spans … verbatim, never translated" | 形式可借（＝我們的「引文」），實作不能搬：我們沒有 fence 可比對，引文邊界（「」到哪裡為止、夾注是否在引文內）需要語意判斷，不是字節比對。已降級為 V6（程式算字數、agent 判邊界）。 |
| N5 | **`--apply` 的 fence splice（整塊搬移）** | "splices the edited fences into the counterpart and structure-validates the result before writing" | 我們的等價物只能是「單詞級替換（find 恰一次）」。整段 splice 已被四次錯位否決（`10a#7`、`11a#21`、`01c#10`、`17a#80`，見 `交接/修訂套用規則.md`）。M4 因此限定在詞級與表驅動替換。 |
| N6 | **首次出現括注（first-mention annotation）** | "首次出現按「首次出現」列書寫（帶括號註釋）；後續出現只寫括號前的部分" | 我們沒有雙語首現體例，現行體例反而是「全書不加註」。照搬會與體例衝突，且 Qwen 意見已在大量建議加註（現行一律否決）——搬進來等於給加註背書。只保留「同卷不重複加註」。 |
| N7 | **排版 gate（CJK/Latin 空格、全半形、破折號、第二人稱）** | "MUST put one half-width space between Chinese text and Latin words … Chinese prose SHOULD prefer colons, periods … over em dashes." | 純漢文語料，只有「全形標點」「書名號配對」「括號配對」少量適用（已納入 V8）。搬整套規則是無效成本。 |
| N8 | **skill 調用邊界（`disable-model-invocation`）／PR／CI 流程** | "Run this extended workflow only when the user explicitly invokes … Never select or load it for ordinary documentation work" | 這是 harness 與 repo 治理機制，不是流程機制。只借其精神：**只有拿到 brief 才派工**，沒有 brief 的批次不受理（等於把「明確指名」變成「明確交付工作集」）。 |

---

## 7. 分階段實施計畫

### 7.1 第一週（5 個工作日）

原則：**先量測，再改流程。** 沒有 V1–V4 的回歸網，任何流程改造都無法驗收。

| Day | 工作 | 產出 | 當日驗收 |
|:--:|:--|:--|:--|
| **D1** | 地基：回歸網與對帳 | `_src/check_scope.py`（V1/V2）、`_src/check_coverage.py`（V3）、`_src/check_terms.py`（先用手工 30 條）、`out_baseline_<date>.json`（每段 md5） | 對 01_行事鈔 已完成 13 卷跑一輪：V1/V2 全綠；V3 列出既有缺口清單（含缺回覆 63 檔） |
| **D2** | 術語表 v1（種子 300 條） | `AI語譯/_work/glossary/glossary.tsv`（五欄＋兩治理欄）、`candidates.tsv`、`glossary_allow.tsv` | ≥300 條；「不要譯作」≥120 條；對 `out` 全域掃描，輸出**既有違規清單**（只列不修）；專名三寫全部定位 |
| **D3** | briefing builder | `_src/build_brief.py`＋`rules_digest.txt`＋`briefs/` 目錄結構 | 02_戒疏 卷一上之一 50 檔 brief 全產出；每檔 ≤8KB；欄位齊備率 100%；抽 3 檔人工確認「不開其他檔就能判」 |
| **D4** | 角色分離＋驗證器 | 兩個提示詞、`patch.schema.json`／`verdict.schema.json`、`_src/apply_patch.py`、`_src/verify_batch.py` | 取 D3 的 1 檔 dry-run：patch 100% 可套、`find` 不唯一者正確拒絕；對 10 條植入錯誤，verifier 攔截 ≥8 |
| **D5** | 單卷試跑與量測（**用已完成的人工卷當答案卷**） | 01_行事鈔 卷首（82 段，低改動率）＋ 02_戒疏 卷一上之一（393 段，高改動率）各跑一次；`calib_<卷>.tsv` | 見 §7.3；且與 `說明_7K_*.md` 的人工判定逐段對比，算出「判定一致率／遺漏／誤改」 |

D5 的校準設計是整個計畫的支點：`說明_7K_01卷首.md`（含 5 條「重要誤報」）、`說明_7K_01卷上之一.md`、`說明_7K_02戒疏卷一上之一.md`（含 6 條存疑）已把每段的「改／不改／存疑」寫死，這就是現成的答案卷。**不用另外標注資料，就能量出 precision／recall。**

### 7.2 第二～五週（概要）

全量共 86 卷（01_行事鈔 13、02_戒疏 22、03_業疏 23、04_比丘尼鈔 7、05_拾毗尼義鈔 5、資持記 16），對應 `AI語譯/_work/review/卷派工/` 的 86 個 tsv。

| 週 | 範圍 | 重點 |
|:--:|:--|:--|
| 第二週 | 02_戒疏 其餘 20 卷（約 8,800 段） | 跑通全卷；每卷抽 10% 做 V9/V10 人工複核；累積「改壞」計數器 |
| 第三週 | 04_比丘尼鈔 7 卷（807）＋05_拾毗尼義鈔 5 卷（234） | 短卷先清；`note` 走夾注策略。同時對 01_行事鈔 已完成 13 卷做回歸 audit（不重改，只掃 V4/V5） |
| 第四週 | 03_業疏 23 卷（5,189 段） | 注意底本：用 `TXT_分卷_標點/03_業疏`，不可用已作廢的 `TXT_分卷/03_業疏`（78 段） |
| 第五週 | 資持記 16 卷（4,182 段） | 走「反向對讀」（記文為主、鈔文為釋），note 策略另行驗證 |

### 7.3 驗收標準

| 指標 | 現況／基線 | 目標 | 量測方式 |
|:--|:--|:--|:--|
| 改壞率 | 10–20%（估計，未instrument） | **≤3%** | 每卷抽 30 段盲審（不看 patch，只看改前→改後） |
| 段數／結構破壞 | 0（既有保護） | **0** | V1 |
| 非目標段異動 | 未量測 | **0 段** | V2 |
| 派工覆蓋 | 曾 30/57 即回報完成 | **100%** | V3 對帳表，缺一不得宣稱完成 |
| 每條 patch 附可溯源依據 | 部分 | **100%**（V7 pass） | V7 |
| 新改動的禁用譯法 | 未量測 | **0 處** | V4 |
| 意見處理率（每條意見都有 verdict） | 泛論常未列 | **100%** | patch／verdict 對帳 |
| 判定一致率（vs 人工答案卷） | — | **≥80%** | D5 校準 |
| 誤改率（pipeline 改、人工判不改） | — | **≤10%** | D5 校準 |
| 驗證攔截率（10 條植入錯） | — | **≥80%** | D4 測試 |
| 每段 token／時間 | 未量測 | ≤ 現行 | 批次記錄 |

「一批算完成」的定義（沿用並收緊 `校閱計畫` 第九節）：V1–V3 全綠、V4–V8 無未處理紅點、所有 patch 有 verdict、存疑已 append、附對帳表。**缺一項即未完成，不接受文字自述。**

### 7.4 風險與回滾

| 風險 | 後果 | 對策 |
|:--|:--|:--|
| brief 太長被截斷 | 證據缺一半，判錯 | 硬上限 8,000 字；超出先截 `src_ctx`，再截 `note`，並在 brief 標 `truncated` |
| 記文貼錯段 | 製造高品質誤報（最危險） | 低信度一律 `none`；`note_map.tsv` 上線前先抽 50 段驗 precision ≥0.9 |
| 兩 agent 互相確認 | 一致性高但都錯 | B 不看 A 的理由；A/B 不一致直接進存疑，不自動辯論 |
| 術語表定太死 | 合法異譯被誤殺 | `glossary_allow.tsv` 白名單＋理由欄；「待定」條目不得據以判 P0 |
| 改動不可回滾 | 無法止血 | 每批備份＋`edits.jsonl`＋`out_baseline.json`；`apply_patch.py --revert <批號>` |
| 一次性鋪開 | 錯了才發現 | 一律單卷試跑 → 校準 → 才放量；第二週起每卷抽 10% 人審 |

---

## 附錄：機制對照速查

| 我們的病灶 | 直接對應 | 第一週能否解決 |
|:--|:--|:--|
| 改壞 10–20% | M1（記文 inline）＋M3（最小編輯）＋M5＋V9/V10 | 部分（機制到位，數字要第二週才穩） |
| 專名不統一 | M7＋M10＋V4 | 是（D2 建表即可掃出全部） |
| 又改又驗 | M5＋§5.1 三角色 | 是（D4） |
| 宣稱完成沒做完 | M8＋M9＋V3 | 是（D1） |
| 命中率 12–23% | briefing 的 opinions 預分類 | 是（D3） |
