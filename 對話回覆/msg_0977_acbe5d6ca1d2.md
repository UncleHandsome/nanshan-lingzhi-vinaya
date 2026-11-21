# 對話材料 #0977

- event: agent/inbox/spliced
- seq: 117285
- time: 1795087914920

---

對照您這套程式碼／提示詞，以及剛剛第 2 組實測（`05a_0015`、`02a_0038`、`03b_0095`、`02b_0011`、`06a_0037`）露出來的漏網案例，我幫您把**審核（audit）**、**修訂（revise）**以及接在後面的**定稿／拆包**環節完整盤點了一遍，整理出 **7 個程式面的實際 Bug／隱患** 與 **5 個提示詞面的具體強化點**：

---

## 一、程式面：審核／修訂／定稿鏈路的具體 Bug

### 1. `mk_revise_materials.py` (`evidence_block`) 截斷了 `web_fetch` 的真正命中段落（高優先）
* **成因**：
  * `qwen_local.py` 的 `web_fetch` 呼叫 `_extract_window(c, keyword, radius=1800, max_len=1800)`，是把關鍵字置中在 1800 字視窗的正中間（大約第 **900 字**附近）。
  * 但 `mk_revise_materials.py` 的 `evidence_block()` 設定 `cap = 650`，然後執行：
    `body = raw_txt if len(raw_txt) <= cap else (raw_txt[:cap] + '…')`
* **後果**：只取前 650 字，等於**只留下關鍵字前方的鋪墊，把第 900 字處真正命中的原典核心句整個切掉**，導致修訂模型在【初審檢索摘錄】裡看不到證據。
* **修法**：若 `src == 'web_fetch'` 且 `len(raw_txt) > cap`，改取「中段視窗」或比照 `quotes` 重算一次視窗，不要無腦 `raw_txt[:650]`（或直接把 `web_fetch` 的 `cap` 調高並居中擷取）。

### 2. `materials_io.py` (`verdict`) 會把「無漏譯／無須修改之處」誤判為 `FIX`（高優先）
* **成因**：在 `_looks_empty(s)` 中：
  ```python
  _m0 = re.match(r'^(?:均|皆|並|悉|經核)?(?:無|沒有|暫無|未見|未發現)(?:任何)?(?:硬傷|問題|必改|錯誤)?', _s0)
  if _m0:
      _rest = _s0[_m0.end():]...
      if not any(w in _rest for w in ('須','應','補','刪','改','修','缺','漏','誤','錯')):
          return True
  ```
  如果審核模型寫 `【結論】PASS`、`【必改硬傷】無須修改之處` 或 `無漏譯／無錯漏`：
  `_m0` 只吃掉開頭的「無」，剩下的 `_rest` 含「須／修／改／漏／錯」，於是回傳 `False`（不為空），`verdict()` 便強行翻盤判為 **`FIX`**！
* **後果**：白送進修訂階段浪費 `xhigh` 額度，甚至誘導修訂模型「沒錯硬改」。
* **修法**：在 `_m0` 前（或 inside `_looks_empty`）先排除常見否定短語，例如 `無須修?改|無需修?改|無漏譯|無錯漏|沒有錯漏|未見錯漏|無誤|不須修改`，或要求 `_looks_empty` 先剝除「無／沒有／未見＋（須修改／漏譯／錯漏／錯誤）」整段。另 `m = re.search(r'【結論】...', rt)` 也建議改為錨定行首並取最後一次出現（比照 line 141 的 `_ms`），避免內文偶爾提到「結論」字樣被搶匹配。

### 3. `mk_revise_materials.py` ＋ `pack_final.py` 對「單成員的已打包組」處理衝突（打包流必改）
* **成因**：`pack_audit.py` 若遇到原本就已打包的短段組（`packed=True`），會單獨成包（`len(pack) == 1`），但仍寫入 `'packed': True` 與 `'members': [it['key']]`（長度為 1）。
  1. `mk_revise_materials.py` 只檢查 `if md.get('members'):`（未檢查 `len > 1`），於是用錯了「多成員打包格式（`[1]\n【鈔文】…[2]\n【鈔文】…`）」，而非單成員原格式（`【鈔文】\n[1] …\n[2] …`）。
  2. 更嚴重的是 `pack_final.py` 第 121 行 `if len(members) == 1:` 無條件執行 `re.sub(r'(?m)^\[\d+\]\s*', '', body)`，**把原本短段打包的 `[1] [2]` 編號全部剝光**，導致下游 `qc_scan.py` 與 `assemble_book.py`（或 `split_pack.py`）報編號不完整或標籤重複！
* **修法**：
  * `mk_revise_materials.py` 改為 `if len(md.get('members') or []) > 1:`。
  * `pack_final.py` 在 `len(members) == 1` 時，若 `md_pk.get('packed')` 為真且本就有多個 `[n]`，**不可剝除 `[1][2]…`**。

### 4. `pack_final.py` 的 `split_marked` 漏掉粗體 `**[1]**`，且缺少與 `build_a2.py` 同步的清潔邏輯
* **成因**：`pack_judge.py` 和 `split_pack.py` 都支援 `**[1]**`（`(?:\*\*|__)?`），但 `pack_final.py` 的 `split_marked` 正則只認 `` ` ``，遇到模型輸出 `**[1]**` 會拆包失敗並轉存 `_未拆.txt`。
* **補充**：`pack_final.py` 也缺少 `build_a2.py` 第 124 行的 `（按／駁回／維持原譯……）` 清除，以及當 `re.search(r'(?:修正後|...)譯文', _rt)` 為假時的 `_strip_head_paren` 清理。

### 5. `build_a2.py` ＋ `norm.py`：自創標籤遇上雙欄（疏＋記）時會變出重複 `【疏文】`
* **成因**：
  * 若修訂模型在雙欄段（有疏有記）多寫了一行自創標籤（例如 `【修訂後的譯文】` 或 `【修訂譯文】……` 同一行），`build_a2.py` 第 116 行的 `_rt0` 只剝「獨佔一整行」的 4 種標籤，漏掉 `【修訂後譯文】` 與同行黏連情況。
  * 接著送進 `norm.normalize()` 時，`norm.py` 的 `LABEL_FIX` 沒有 `【修訂後的譯文】`，而對 `【修訂譯文】` 會轉成「全文偵測到的 `_lab`（也就是 `【疏文】`）」，結果原本的 `【修訂譯文】\n【疏文】…\n【記文】…` 就變成 **`【疏文】\n【疏文】…`**，`qc_scan.py` 直接判異常。
* **修法**：在 `build_a2.py` 進入 `norm.normalize()` 前，先把所有 `【(?:修正|修訂)(?:後)?(?:的)?譯文】`（不限是否獨佔一行）直接剝除。

### 6. `norm.py` (`_ABBR_RESTORE`) 會把「簡稱＋《全稱》」洗成「多論《多論》」「雜心《雜心》」
* **實證**：在 `06a_卷一之六_0037` 記文中，模型寫了「多論《薩婆多毘尼毘婆沙》與雜心《雜阿毘曇心論》」。
* **問題**：`norm.py` 會直接把《全稱》替換回《簡稱》，變成「**多論《多論》與雜心《雜心》**」。
* **修法**：替換前檢查前面是否緊貼著同一簡稱（如 `多論《`、`雜心《`），或把 `簡稱[（(]?《全稱》[）)]?` 直接收斂為 `《簡稱》`。

### 7. `run_pipeline.py` 的 `_clean_audit_errors` 放在 `run_agent` 之後，會讓 `ERROR` 直接滑進修訂／定稿
* **成因**：`run_pipeline.py` 在 `st == 'audit'` 時，是跑完 `qwen_local.py` 才執行 `_clean_audit_errors` 把 `ERROR` 改名為 `_異常.txt`。若接著同指令跑 `,revise,final`，該筆不會被重跑，而是被 `revise` 跳過、`build_a2` 當成 `unaudited` 卡死。
* **修法**：在 `run_agent` **之前**先清一次 `_clean_audit_errors`（讓續跑可自動補跑），且在 `run_agent` 之後若有清出任何 `ERROR`，自動補跑一次或中止往下推。
* *（順帶小修：`mk_revise_materials.py` 第 236 行 `r1 == audit` fallback 時，`_cand` 建議加上 `_seg.find('\n【分段要求')`，避免該區塊漏進 `【目前譯文】`。）*

---