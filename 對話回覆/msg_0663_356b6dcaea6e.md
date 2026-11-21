# 對話材料 #0663

- event: agent/inbox/spliced
- seq: 93992
- time: 1794897690579

---

再往下深挖一層，把**最後幾處藏在正規化、拼回、對齊與容錯邏輯裡的細節問題**也翻出來（以下皆為前兩輪未重複的新發現）：

---

### 第四輪掃描新增問題（共 8 項）

#### 1. 【高風險】`mk_split_blind.py` 漏掉書名 `《》`，導致長段「自搜過濾」誤殺平行典籍
- **位置**：`mk_split_blind.py` 第 150 行 vs `qwen_local.py` 第 625 行
- **成因**：
  `mk_split_blind.py` 輸出出處格式是 `'（出處：%s，第 %d 段之 %d/%d）'`（沒用 `《書名》` 包住書名），而 `qwen_local.py` 是用 `re.search(r'（出處：《([^》]+)》', text)` 抓 `stats_book`。
- **後果**：
  所有大於 500 字的長段在跑盲翻時，`_cur_book` 都會變成空字串 `''`。在 `qwen_local.py` 第 231 行 `if not _cur_book and any(w and w in _ht for w in _wins): continue` 下，**只要《尼鈔》長段借用了《行事鈔》超過 20 字的平行原文，模型想呼叫 `local_search` 查《行事鈔》上下文時，會被當成「搜到自己」直接過濾掉**。
- **修法**：第 150 行改為 `'（出處：《%s》%s，第 %d 段之 %d/%d）' % (args.book, chunk, idx + 1, pi, len(parts))`。

---

#### 2. 【中風險】`norm.py` 漏收單字 `发`，遇到《四分律》高頻詞「落髮／剪髮／蓄髮」有錯轉風險
- **位置**：`norm.py` 第 90–122 行、第 140 行 vs `qc_scan.py` 第 55 行
- **成因**：
  1. `qc_scan.py` 會抓簡體字 `'发'`；但 `norm.py` 的 `VAR_MAP` 與 `SIMP` **完全沒收錄單字 `'发'`**（只靠第 140 行正則與選用的 `opencc`）。萬一目標環境未裝 `opencc`（`_CC = None`），模型輸出「发露」「发动」會繞過 `norm.py` 直接在 `qc_scan.py` 報錯。
  2. 第 140 行寫 `(?<=[头頭剃白毛须鬚鬓鬢])[发發]` → `'髮'`，漏了律典極常見的 **`落髮、剪髮、蓄髮、長髮、披髮、被髮、結髮、束髮、染髮`**。若先經 `opencc` 未必詞庫全中，放進 `SIMP` 又會錯變成「落發／剪發」。
- **修法**：
  - 第 140 行擴充為 `(?<=[頭头剃白毛鬚须鬢鬓落剪蓄長长披被束結结生露染])[发發]` → `'髮'`（注意需排在 `opencc` 與 `SIMP` 之前執行）。
  - `SIMP` 末尾補入 `('发', '發')`。

---

#### 3. 【中風險】`materials_io.py` 的 `is_keep_a()` 對 `PASS_A` 變體寬容不足，可能讓「沿用甲譯」進定稿
- **位置**：`materials_io.py` 第 71–75 行 vs `mk_audit_materials.py` / `build_a2.py`
- **成因**：
  `is_keep_a()` 只認 `PASS_A_KEEP_A` 與 `沿用譯本甲`。但只要模型在 `【結論】PASS_A` 下方第 3 欄一時寫成 `沿用甲譯`、`同譯本甲` 或 `PASS_A（沿用譯本甲）`（若加上說明又沒包好），`is_keep_a()` 會回傳 `False`。
- **後果**：`mk_audit_materials.py` 會把**「沿用甲譯」四個字當成待審譯文**送給審核與修訂（而修訂階段手中已經沒有譯本甲原文，只能報錯或空修）。
- **修法**：
  1. `is_keep_a()` 放寬正規表達式：`re.fullmatch(r'[【\[（(]?\s*(?:PASS_A\s*[：:／/]?\s*)?(?:沿用|同)(?:譯本)?甲(?:譯|本)?\s*[】\]）)]?', s)`。
  2. 在 `mk_audit_materials.py` 與 `build_a2.py` 補一條保底：若結論明確判 `PASS_A` 且 `col3` 抽出結果不含 `【疏文／記文／鈔文…】` 標籤、純漢字又 `< 15` 字，一律視同 `is_keep_a` 強制回填 `譯本甲`。

---

#### 4. 【低～中風險】`qwen_local.py` 查無結果時的提示遺漏（文件 4.7 與程式碼不同步）
- **位置**：`qwen_local.py` 第 251–267 行 vs 文件 4.7 節
- **成因**：文件 4.7 記載查無時會提供提示引導模型不要用同詞反覆硬試，但 `qwen_local.py` 實際只在 `relaxed` 放寬成功時寫入 `payload['note']`；**當 `not hits`（全庫都查無）時，`payload` 只有 `{'num_found': 0, 'results': []}`，沒有任何 `note`**。
- **修法**：當 `not hits` 時寫入 `payload['note'] = '全庫查無此詞組；若仍須查證請改換 2～3 個不同實詞以空格分隔重試，勿以同一詞反覆試搜。'`，有助於避免模型耗盡剩餘額度。

---

#### 5. 【低～中風險】`assemble_book.py` 無 JSON 回退時只抓單段、未抓 `–g1`
- **位置**：`assemble_book.py` 第 40–46 行 vs `mk_judge_materials.py` 第 253 行
- **成因**：`assemble_book.py` 在沒有 `.json` 的回退分支寫 `_m = re.search(r'，第 (\d+)', _ex)` 並直接令 `_g1 = _s0 + 1`，遇到 `第 21–22 段`（疏＋記雙段）會漏算第 22 段並重複判定缺段。
- **修法**：改為 `re.search(r'，第 (\d+)(?:–(\d+))? 段', _ex)`，`_g1 = int(_m.group(2) or _m.group(1))`。

---

#### 6. 【低風險】`qc_scan.py` 兩項雜訊：標籤計入短文膨脹、引號重複檢查
- **位置**：`qc_scan.py` 第 45–63 行
- **成因**：
  1. `oh = len(HAN.findall(out))` 把 `【疏文】【記文】`（4 個漢字）算進譯文長度。對 10–15 字的超短條目，標籤本身就會把比例推高到 `> 2.4` 倍而誤報「短文膨脹」。應先剝除 `^【(?:疏文|記文|鈔文|律文|註文|序文)】` 再計字數。
  2. 第 53 行（`引號未閉合`）與第 61 行（`「」 未成對`）重複檢核了兩次全形單引號。

---

#### 7. 【低風險】`pack_judge.py` 拆回未過濾模型自創修訂標籤、`pack_final.py` 多餘空行
- **位置**：`pack_judge.py` 第 163–167 行；`pack_final.py` 第 67、78 行
- **細節**：
  - `pack_judge.py` 的 `re.split(r'【(' + LABS + r')】', body3)` 若遇到模型偶發輸出 `【疏文（修訂）】` 會失配，先套一次 `norm.LABEL_FIX` 即可擋掉。
  - `pack_final.py` 寫檔時 `norm.normalize(...) + '\n'` 會多出一個尾端換行（`norm.normalize()` 結尾已自帶 `'\n'`）。

---

#### 8. 【實驗基準一致性】`run_l7.py` 修訂階段 `effort` 與量產管線不同
- **位置**：`run_l7.py` 第 17 行 vs `run_pipeline.py` 第 185 行／文件 4.4 節
- **細節**：`run_pipeline.py`、`run_long_audit.py` 與文件 4.4 節都將修訂設為 `effort='xhigh'`，唯獨 `run_l7.py` 設為 `effort='high'`。若要拿 L7 當全量上線前的基準對照，建議統一調回 `'xhigh'`。

---