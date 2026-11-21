# 對話材料 #0387

- event: agent/inbox/spliced
- seq: 73717
- time: 1794779814605

---

整份更新版看過一輪，你們把很多關鍵優化（32 部書庫、`SRC_RE_ALL` 邊界、`--force` 防呆、`mk_split_blind` 背景上限、`PASS_A_KEEP_A`、`pack_judge`、`mk_draft_materials`）都已經寫進去了，非常紮實。

但逐行檢查新程式碼後，抓出 **5 個實際會搞壞產出或讓功能失效的 Bug**，以及 **2 個純粹造成 token 浪費、修掉不傷品質的盲點**：

---

### 一、必須立刻修的 5 個程式 Bug（目前寫法會直接出錯）

#### 1. `PASS_A_KEEP_A` 下游三連斷鏈（會直接把字面 `"PASS_A_KEEP_A"` 寫成定稿！）
- **`build_a2.py`**：頂部定義了 `_MARK = 'PASS_A_KEEP_A'` 和 `_from_jia()`，但 **`main()` 裡完全沒呼叫**！因為 `len('PASS_A_KEEP_A') == 13 >= 8`，`col3_soft()` 會正常回傳這串英文字，導致所有 `PASS_A` ＋ `PASS` 的組別，**最終定稿檔 `.txt` 裡會直接輸出 `"PASS_A_KEEP_A"`**。
- **`mk_revise_materials.py`**：完全沒有 `_MARK` 處理，遇到 `PASS_A` 被審核判 `FIX` 時，送進修訂的 `【目前譯文】` 會是字面 `"PASS_A_KEEP_A"`。
- **`mk_audit_materials.py`**：`_from_jia()` 用 `re.search` 只抓第一個 `（譯本甲）` 區塊，**會把雙欄組（《業疏》《戒疏》）的【記文】整個丟掉，且漏掉開頭的【疏文】／【記文】標籤**。
  - **修法**：把 `_from_jia()` 改成 `re.findall` 抽出全部 `(lab, body)` 並還原為 `【{lab}】\n{body}`，並把這套邏輯一併接進 `mk_revise_materials.py` 和 `build_a2.py` 的 `main()`（建議寫在 `materials_io.py` 共用）。

#### 2. `pack_judge.py` 四個隱蔽 Bug（現在跑會浪費大量檢索、甚至拆出空譯文）
1. **破壞 `qwen_local.py` 的原文長度統計**：打包後寫成 `■ 疏文（原文）[1]`，但 `SRC_RE_ALL` 寫的是 `（原文）\s*\n+`——中間多出 `[1]` 匹配失敗，導致所有打包短段 `_raw_len()` 退回算整份文件字數，**全部誤領滿額 5 次本地檢索**（改寫成 `[1] ` 放在正文開頭，或 `SRC_RE_ALL` 改為 `（原文）(?:\[\d+\])?\s*\n+`）。
2. **`do_split` 遇到 `PASS_A_KEEP_A` 會拆出全空譯文**：`PASS_A_KEEP_A` 裡沒有 `[1][2]` 編號，`do_split()` 按 `\[\s*(\d+)\s*\]` 切分會全部取到空字串。
3. **`do_split` 拿整份回覆 `t` 切分**：應該先切出第 3 欄 `col3(t)` 再按 `[n]` 拆回（否則第 2 欄出現 `[1]` 或數字標記會把段落切爛），且不可寫死全標 `REVISED`。
4. **打包時丟了 `【後文背景】` 且 `LBL_RE` 結尾誤寫 `\\Z`**：`head.split('【本次待審單元】')[0]` 把最後一段的 `【後文背景】` 全切掉了，不利承後判讀；且 raw string 裡的 `|\\Z` 要改回 `|\Z`。

#### 3. `qwen_local.py` 「過濾搜回本段自己」完全沒生效＋多個 `r'\\s'` 雙斜線失效
- **搜回本段過濾無效**：`qwen_local.py` 第 181 行寫 `h.get('text')`，但 `local_corpus.find()` 回傳字典的鍵名是 **`'kwic'`**（不是 `'text'`），所以永遠拿到空字串、一筆都沒過濾掉！
- **雙斜線正則失效**：`qwen_local.py` 第 181、433 行的 `r'[\\s　]'`，以及 `mk_judge_materials.py` 第 88 行的 `r'^\\s*...'`、第 105 行的 `r'[\\s　]'`，在 `r'...'` 裡 `\\s` 匹配的是反斜線和 `s` 字母，不是空白！
- **漏掉記文**：`_src_unit(text)` 只取第一個 `■ ……（原文）`，所以雙欄組的 `own_text` 沒涵蓋到 `記文`（改用 `SRC_RE_ALL.findall(text)`）。

#### 4. `merge_long.py`、`mk_revise_materials.py`、`norm.py` 語法與邏輯小錯
- **`merge_long.py` 第 12 行**：在 `B = ...` 定義前就執行 `sys.path.insert(0, B + ...)`，會直接觸發 `NameError`。
- **`mk_revise_materials.py` 第 148 行**：`prompt + '\\n\\n' + _mb` 多了一個反斜線，會把字面 `\n\n` 貼進提示詞。
- **`norm.py`**：`LABEL_FIX` 在 `_tag_newline` 之後才執行，若原句為 `【修訂譯文】正文`，替換成 `【鈔文】正文` 後就不會換行；且不應把《資持記》／《業疏》的 `【修訂譯文】` 一律強制改成 `【鈔文】`（可交由組別標籤或至少在 `LABEL_FIX` 放行前先做 `_tag_newline`）。

#### 5. `mk_draft_materials.py` 面對「打包組」漏了 `【分段要求】`
- `mk_review_materials.py` 產出的打包組只在正文加了 `[1] `、`[2] `，本身不含 `【分段要求】` 提示文字；`mk_blind_materials.py` 有補這句，但 **`mk_draft_materials.py` 漏補了 `if md.get('packed'):`**，草譯遇到打包組時容易把 `[1][2]` 併成一段。
- 另外若碰上 `old_block` 為空（無舊譯可用），建議不要再送三欄自比，改走單欄盲翻省掉重複輸出。

---

### 二、2 個 100% 不傷品質、直接就能省浪費的盲點

#### 1. 書庫已經擴充到 **32 部**，但 `SYSTEM_PROMPT` 與 `ALIASES` 還停在 **22 部**
- 你們 4.1 節已經把《成實論》《大般涅槃經》《優婆塞戒經》《雜阿毘曇心論》《增壹阿含經》《大比丘三千威儀》《關中創立戒壇圖經》《四分比丘尼戒本》《梵網經》《瑜伽師地論》加進本地庫了（合計 **32 部、421,875 行**）。
- 但 **`qwen_local.py` 的 `SYSTEM_PROMPT` 和 `LOCAL_SCHEMAS` 還寫著「本地已收錄 22 部」且少列這 10 部**！模型看到《涅槃經》《優婆塞戒經》《成實論》不在名單裡，就會直接略過本地改跑 `web_search`（花時間又多一輪）！
- 同時 `local_corpus.py` 的 `ALIASES`：
  - 還留著舊 Bug：`('四分律刪補隨機羯磨疏濟緣記', '業疏')`（應改映為 `'濟緣記'`）；
  - 建議補齊新書常見簡稱（如 `('善生經', '優婆塞戒經')`、`('善生', '優婆塞戒經')`、`('涅槃經', '大般涅槃經')`、`('成論', '成實論')`、`('雜心論', '雜阿毘曇心論')`、`('瑜伽論', '瑜伽師地論')`、`('戒壇圖經', '關中創立戒壇圖經')`、`('三千威儀', '大比丘三千威儀')`、`('尼戒本', '四分比丘尼戒本')`），能明顯壓低查無重試輪數。

#### 2. `AUDIT_PROMPT` 重句錯字＋網搜語法微調、`修訂` 可放心降 `high`
- `AUDIT_PROMPT` 原則 3 留了重複句與錯標點（`……一律視為無據增詞。；僅「不補則……」`），順手刪掉重複那句即可；
- `AUDIT_PROMPT` 原則 4 寫「查平行文時 work 欄留空，改以空格分隔 2～3 個實詞」，建議改與 `SYSTEM_PROMPT` 一致（「**短語查無時**，改以空格分隔……」），避免審核第一搜就亂拆短詞撈出噪音；
- 第 4.4 節目前 `修訂（NO_TOOLS）` 仍設 **`xhigh`**，這關單純照 `xhigh 審核` 的硬傷清單做定點改字（且無工具輪數問題），若之後想省點小錢與時間，**這關降 `high` 是幾乎零風險的**。

---

### 三、重點修補 Patch（可直接貼進對應檔案）

```python
# 1. 共用 _from_jia（放到 materials_io.py，給 mk_audit / mk_revise / build_a2 一起用）
def from_jia(md_text):
    hits = re.findall(
        r'■ (疏文|記文|鈔文|律文|註文|序文)（譯本甲）\s*\n+(.+?)(?=\n+■ |\n+【|\Z)',
        md_text or '', re.S)
    return '\n\n'.join('【%s】\n%s' % (lab, body.strip()) for lab, body in hits)
```

```python
# 2. qwen_local.py：修 SRC_RE_ALL（支援 pack_judge 的 [1]）、own_text（涵蓋疏+記）與自搜過濾
SRC_RE_ALL = re.compile(
    r'■ (?:疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?'
    r'\s*\n+(.+?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|分段要求|目前譯文)|\Z)',
    re.S,
)

# run() 裡：
stats['own_text'] = re.sub(r'[\s　]', '', ''.join(SRC_RE_ALL.findall(text)))

# local_search() 裡（在 hits 過濾後才判 empty）：
        own = (stats or {}).get('own_text') or ''
        if own and hits:
            _keep = []
            for h in hits:
                _kw = re.sub(r'[\s　]', '', h.get('kwic') or '')
                # 只過濾核心高度重疊（幾乎就是正在翻的那段）
                if own and len(own) >= 20 and own[:20] in _kw:
                    continue
                _keep.append(h)
            hits = _keep
```
*(記得同步把 `SYSTEM_PROMPT` 與 `LOCAL_SCHEMAS` 的「22 部」改成「32 部」並補上新 10 部書名。)*

```python
# 3. mk_draft_materials.py：補 packed 提醒
        if md.get('packed'):
            body += '\n\n【分段要求】本單元含多個短段，請保留 [1][2]… 編號逐條對應，勿合併、增減條數或改動編號。'
```

```python
# 4. build_a2.py 與 mk_revise_materials.py 接上 PASS_A_KEEP_A：
# mk_revise_materials.py 讀 a1 後：
        if a1 == 'PASS_A_KEEP_A':
            a1 = MI.from_jia(t)

# build_a2.py 在 else（非 FIX 且用裁決稿）處取得 txt 後：
        if txt == 'PASS_A_KEEP_A':
            _bm = os.path.join(base, key + '.md')
            if os.path.exists(_bm):
                txt = MI.from_jia(io.open(_bm, encoding='utf-8').read())
            elif blind:
                _bl = os.path.join(blind, '回覆', key + '_回.txt')
                if os.path.exists(_bl):
                    txt = io.open(_bl, encoding='utf-8').read().strip()
```

```python
# 5. pack_judge.py 關鍵修補：
LBL_RE = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（(原文|譯本甲|譯本乙)）\s*\n+(.+?)(?=\n+■ |\n+【|\Z)', re.S)

# do_pack() 保留最後一組的後文背景：
        _post = ''
        if '【後文背景' in pack[-1]['text']:
            _post = '\n【後文背景' + pack[-1]['text'].split('【後文背景', 1)[1]
        if _post:
            lines += ['', _post.strip(), '']

# do_split() 只切第 3 欄，且若遇到 PASS_A_KEEP_A 就寫回 PASS_A_KEEP_A 讓後續抽甲本：
        body3 = col3_soft(t) or t
        if body3.strip() == 'PASS_A_KEEP_A':
            for ok_key in originals:
                txt = '1. **結論**：`PASS_A`\n\n2. **分歧與裁決**：兩譯本實質義理無分歧，沿用譯本甲。\n\n3. **修正後的譯文**：\nPASS_A_KEEP_A\n'
                io.open(os.path.join(dst, ok_key + '_回.txt'), 'w', encoding='utf-8').write(txt)
            ok += 1
            continue
        parts = re.split(r'\[\s*(\d+)\s*\]', body3)
```

*(附註：`merge_long.py` 記得把 `B = ...` 移到 `sys.path.insert` 前面；`mk_revise_materials.py` 第 148 行 `'\\n\\n'` 改成 `'\n\n'`；`mk_judge_materials.py` 第 88、105 行的 `\\s` 改成 `\s`。)*

先把這幾個 Bug 修掉（特別是 `PASS_A_KEEP_A` 斷鏈跟 `pack_judge`），整條管線就既穩又不會白燒檢索額度了！