# 對話材料 #0896

- event: agent/inbox/spliced
- seq: 112406
- time: 1795065723798

---

整體來看，這套校閱管線的設計相當成熟，工程防呆也做得很細（例如：`src_hash` 防陳舊、雙線裁決防同誤、`PASS_A_KEEP_A` 標記回填、`local_search` 自搜過濾與無結果退還額度、`verdict()` 排除否定式誤判等）。

但逐行比對整套流程與各支腳本的資料交接後，確實存在幾個**實質 Bug 與隱性邊界地雷**，依嚴重程度整理如下：

---

### 一、確定會導致錯位或錯字的 Bug（建議優先修）

#### 1. `run_long_audit.py`：長段前文背景會把「待譯單元＋第一小段原文」吞進去
* **位置**：`mk_split_blind.py`（產出 `_長段/_材料`） vs `run_long_audit.py` 的 `build()`
* **原因**：
  `mk_split_blind.py` 寫出的標題是 `【本次待譯單元】`；但 `run_long_audit.py` 抽取前文背景的正則是：
  ```python
  re.search(r'【前文背景[^】]*】\s*\n+(.+?)(?=\n+【(?:本次待審單元|後文背景|所釋鈔文)|\Z)', ...)
  ```
  看齊點漏了 `本次待譯單元`！因為長段第 1 小段（`parts[0]`）一定帶有 `【後文背景】`，正則會一路跨過 `【本次待譯單元】` 與第 1 小段的 `■ 原文`，把它們全部塞進 `_終審材料` 的 `【前文背景】` 裡，導致終審與終修時前文背景結構錯亂且重複帶入第一段原文。
* **修法**：lookahead 補上 `本次待譯單元`。另外 `mk_split_blind.py` 也沒像 `mk_blind_materials.py` 一樣為《資持記》長段附上 `【所釋鈔文】`，可順手補齊。

#### 2. `norm.py`：律宗高頻詞「白發／頭發」會被誤改為「白髮／頭髮」
* **位置**：`norm.py` 第 105 行
  ```python
  _seg = re.sub(r'(?<=[頭头剃毛鬚须鬢鬓剪蓄束白落青披])[发發]', '髮', _seg)
  ```
* **原因**：
  `白` 與 `頭` 在律宗白話譯文中極常接「發起／發露／發出／發願」，例如「表**白發**露」「自**白發**起」「明**白發**出」「口**頭發**願」「念**頭發**起」，這條正則會一律把它們硬改成「白**髮**」「頭**髮**」。同時字表卻漏了「削、長、短、結、留、散、理」，導致簡體「削发／长发」會被後面的 `SIMP` 轉成「削發／長發」。
* **修法**：移除單字 `白`、`頭` 的無條件前瞻（或改為白名單雙字詞，如 `(?<=鬚|鬢|毛|剃|剪|蓄|束|落|披|削|結|散|理)[发發]` 與 `白髮` 僅限明確搭配詞如 `白髮蒼蒼`）。

#### 3. `norm.py` ＋ `build_a2.py`：標籤重複、單邊漏改與雙欄缺漏的漏洞
* **重複標籤**：在 `build_a2.py` 的 `is_fix` 分支，若修訂模型未寫 `【修正後的譯文】` 而自創了 `【修訂譯文】`（無「後」字），`txt` 為 `None`，程式會進 `if not txt:` 先在最前面補上 `【_lab0】\n`，接著呼叫 `norm.normalize(_raw)`——結果 `norm.normalize` 又把底下的 `【修訂譯文】` 轉成 `【_lab0】`，產生**兩個連續標籤**，最後被 `qc_scan.py` 抓出「殘留欄位標籤」。
* **打包段缺標籤**：若修訂模型在打包段（`packed=True`）輸出 `【修訂後的譯文】\n[1] ……` 而漏寫 `【鈔文】`，`col3(_rt)` 會直接成功並跳過補標籤邏輯，導致定稿缺 `【鈔文】` 標籤。
* **PASS 分支未檢核缺欄**：`build_a2.py` 檢查多欄缺漏（`_lack = sorted(_labs_exp - _got)`）只寫在 `if is_fix:` 內；若裁決階段漏譯了 `【記文】` 而終審放行 `PASS`，`else:` 分支不會攔截缺欄。此外，`len(_labs_exp) == 1` 時也未檢查單欄標籤是否與目標相符（例如《資持記》誤標成 `【疏文】`）。

#### 4. `pack_judge.py`：`do_split` 兩個字串判斷過於脆弱
* **位置 1**：`_pre_lab = _pre_labs[-1] if (_pre_labs and not _pre_txt) else ''`
  只要模型在第 3 欄第一個標籤前多寫了一句非括號說明（例如 `以下僅列改動段：`），`_strip_head_paren` 剝不掉，`_pre_txt` 變成非空，就會把 `_pre_lab` 清成 `''`，連帶讓 `[1]` 的內容被歸到 `'_head'` 而不是正欄，直接觸發 `_拆回異常.txt`（若 `[1]` 不在 `_by_i` 甚至會靜默放棄第 3 欄改動而沿用甲）。
* **位置 2**：`_only_a = all(('甲優' in ln and '乙優' not in ln and '重修' not in ln) for ln in _by_i[i])`
  只要模型在 `裁決（甲優）：` 後面的理由欄裡寫了否定說明（如「不採乙優」「無須重修」），就會因為字面上出現 `'乙優'` 或 `'重修'` 而誤判為異常，觸發 `_拆回異常.txt`。應只取 `裁決（……）` 括號內的結論字樣比對。

---

### 二、檢索機制與效能缺陷（實測「撞牆」與耗時的根因）

#### 5. `qwen_local.py`：`_exhausted` 幾乎永遠不會變 `True`
* **位置**：`run()` 迴圈內的 `_exhausted` 判斷：
  ```python
  _fetch_done = NO_WEB or stats.get('fetches', 0) >= _mf
  _exhausted = _over_tok or (_loc_done and _web_done and _fetch_done)
  ```
* **原因**：
  系統提示詞明確要求「摘要已足勿再 `web_fetch`」，模型實戰中幾乎不會用掉 `web_fetch` 額度（`fetches = 0 < 1`）。只要 `NO_WEB=0`，`_fetch_done` 就幾乎永遠是 `False`，進而使 `_exhausted` 永遠是 `False`——即使 `local_search`（5/5）與 `web_search`（2/2）全都用光了，API 依然送出 `tool_choice='auto'`，模型就有機會繼續叫 `local_search` 撞牆（這也是 L7 已經加了 `notice` 卻還是撞牆 20 次的原因之一）。
* **建議**：`web_fetch` 只是輔助工具，`_web_done` 用盡且 `_loc_done` 用盡時，不應被未使用的 `web_fetch` 拖住不切 `tool_choice='none'`（或者至少在 `_loc_done and _web_done` 成立且已經嘗試過搜尋後就切為 `none`）。

#### 6. `qwen_local.py` ＋ `local_corpus.py`：`query` 帶書名會繞過跨書放寬
* **原因**：
  `qwen_local.py` 的跨書放寬條件是 `if not hits and work:`，檢查的是工具參數 `work`。但若模型違反定義把書名寫進 `query`（如 `query="業疏 前六有非"`、`work=None`），`local_corpus._split_work()` 會在內部擅自切出 `work='業疏'` 去搜；若查無，回傳 `[]` 給 `qwen_local.py` 時，`qwen_local.py` 的 `work` 仍然是 `None`，因此**不會觸發跨書放寬**，直接回報全庫查無。

#### 7. `local_corpus.py`：未填 `work` 時每次搜尋都空轉掃描 50 萬行
* **位置**：`find()` 第 236 行：
  ```python
  _idxs = BOOK_LINES.get(work) if work and work in BOOK_LINES else range(len(LINES))
  ```
* **原因**：
  雖然前面已經用 `BOOK_BLOB` 過濾出真正命中 `anchor` 的書（`_blob`），但只要沒填 `work`，後面迴圈依然跑遍 `range(len(LINES))`（**500,067 行**），在 Python 層對沒命中的書逐行做 `if r['book'] not in _blob: continue`。在 `WORKERS=40` 高併發下，每個 thread 在執行這段純 Python 迴圈都會持有 GIL，拖慢整體反應。改成只遍歷 `for b in _blob: for idx in BOOK_LINES[b]:` 即可快上數十倍。

---

### 三、特定流程與邊界風險

#### 8. `norm.py` 與 `qc_scan.py` 對引號內簡體／異體字處理不一致
* `norm.py` 的 `_depth` 採**逐行重置**，跨行引文第 2 行起就失去保護；同時 `norm.py` 在引號內跳過所有 `SIMP` 簡轉繁，但 `qc_scan.py` 的簡體掃描在引號內卻只略過 `[无时么]` 三字——這會導致「逐字翻譯的白話引文『……』內若不小心夾了一個簡體字（如`说`、`这`、`义`），`norm.py` 不會幫修，但 `qc_scan.py` 會報錯」。
* 此外，`qc_scan.py` 的 `_out_noquote = re.sub(r'[「『][^」』]*[」』]', '', out)` 遇到雙層巢狀引號 `「……『……』……」` 時，會從 `「` 配到內層的 `』` 就截斷，導致後半句外層引文漏到引號外。

#### 9. `make_hybrid.py` 在無 `.json` 舊材料上的重複句誤標風險
* 當舊 `_材料` 目錄缺少 `.json` 時，`make_hybrid.py` 退回比對 `ns in _bodies` 來反推該檔覆蓋的段落索引 `idx`。
* 若同一卷內有多個相同的短段（例如科判標目 `【疏】今初`、`【記】問`），`for k, seg in enumerate(a): if ns in _bodies:` 會把**整卷所有的「今初」**都加入 `covered[ch]`，造成後面的同名段落被當成「已覆蓋」而跳過，最後在 `assemble_book.py` 回拼時變成缺段。另外舊包若無 `.json` 且屬打包段，`norm(b)` 會把 `[1][2]` 黏成一塊，無法匹配單段 `seg`。確保舊 `_材料` 都有 `.json` 可避開此問題，但回退邏輯本身有隱患。

#### 10. `mk_revise_materials.py` 與 `pack_final.py` 在 `r1 == audit` 時（舊批次打包審閱）可能吞入「所釋鈔文」
* 當執行 `pack_audit.py` 流程（`