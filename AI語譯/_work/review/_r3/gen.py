# -*- coding: utf-8 -*-
"""Generate 說明_r3_前段.md: stats from r3_done.tsv + exact paragraph diff vs 歸檔/r3修正前."""
import os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
DONE = os.path.join(WORK, 'r3_done.tsv')
OUTMD = os.path.join(WORK, '說明_r3_前段.md')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
OUT = os.path.join(ROOT, 'AI語譯', 'out')

rows = {}
for ln in open(DONE, encoding='utf-8'):
    p = ln.rstrip('\n').split('\t')
    if len(p) < 6:
        continue
    nnn, items, fixed, rej, doubt, note = p[0].strip().lstrip('\ufeff'), int(p[1]), int(p[2]), int(p[3]), int(p[4]), p[5]
    if note == 'pending':
        continue
    rows[nnn] = (items, fixed, rej, doubt, note)

def paras(p):
    t = open(p, 'rb').read().decode('utf-8-sig')
    return [s.rstrip('\r') for s in t.split('\n') if s.rstrip('\r').strip()]

seg_by_book = collections.Counter()
seg_by_chunk = collections.Counter()
for book in os.listdir(BAK):
    bd = os.path.join(BAK, book)
    if not os.path.isdir(bd):
        continue
    for f in sorted(os.listdir(bd)):
        if not os.path.exists(os.path.join(OUT, book, f)):
            continue  # alternate backups such as *_b.txt
        a = paras(os.path.join(bd, f))
        b = paras(os.path.join(OUT, book, f))
        if len(a) != len(b):
            print('!! count mismatch', book, f, len(a), len(b))
            continue
        n = sum(1 for x, y in zip(a, b) if x != y)
        if n:
            seg_by_book[book] += n
            seg_by_chunk[(book, f)] += n
t_seg = sum(seg_by_book.values())
t_items = sum(v[0] for v in rows.values())
t_rej = sum(v[2] for v in rows.values())
t_doubt = sum(v[3] for v in rows.values())
nnns = sorted(rows)

L = []
L.append('# r3 前段校閱意見處理說明\n')
L.append('> 本檔由 `AI語譯/_work/review/_r3/gen.py` 依 `r3_done.tsv` 與實際譯文差異自動生成。\n')
L.append('## 一、範圍與依據\n')
_RESP = os.path.join(ROOT, 'batch_qwen', 'r3')
_all = [f[5:8] for f in sorted(os.listdir(_RESP)) if f.startswith('resp_') and f.endswith('.txt')]
_remain = [n for n in _all if n not in rows]
L.append('- 回覆來源：`batch_qwen/r3/resp_%s.txt` ～ `resp_%s.txt`（目錄現存 %d 檔；本次處理 %d 檔，尚餘 %d 檔）。'
         % (nnns[0], nnns[-1], len(_all), len(nnns), len(_remain)))
L.append('- 對應材料：`校閱_10K/校閱_%s.txt` ～ `校閱_%s.txt`。' % (nnns[0], nnns[-1]))
L.append('- 對照檔（權威來源）：`AI語譯/out/<書>/<chunk>.txt`。材料標籤 `【NNN-MMMM】<書>/<chunk>#段` 先以譯文全文精確比對定位；材料與現行譯文有微小落差者改用相似度比對（001–038 共 1900 段中 1848 段精確、52 段相似度 ≥0.94；181–221 之 205 段全部定位，無錯位。材料段號與 out 行號實測有位移，故一律以全文比對為準，不採段號。）')
L.append('- 改動方式：只換該段的字句（片語級替換），不動段落數、不動行尾（各檔 LF/CRLF 原樣保留）。')
L.append('- 備份：`歸檔/r3修正前/<書>/<chunk>.txt`（首次改動前的原樣）。')
L.append('- 逐檔紀錄：`r3_done.tsv`；改動明細：`fix_r3.tsv`；處理腳本：`_r3/seg.py`、`edit.py`、`edit2.py`、`gen.py`、`verify.py`。\n')
L.append('## 二、統計\n')
L.append('| 項目 | 數 |')
L.append('|---|---|')
L.append('| 處理回覆檔 | %d |' % len(rows))
L.append('| 處理意見條數 | %d |' % t_items)
L.append('| 實際改動段數 | %d（01_行事鈔 %d、02_戒疏 %d） |'
         % (t_seg, seg_by_book.get('01_行事鈔', 0), seg_by_book.get('02_戒疏', 0)))
L.append('| 否決（含潤飾／加註／體例） | %d |' % t_rej)
L.append('| 存疑 | %d |' % t_doubt)
L.append('| 判「已修」而跳過 | 0 |\n')
L.append('改動分布：\n')
L.append('| 檔 | 改動段數 |')
L.append('|---|---|')
for (book, f), n in sorted(seg_by_chunk.items()):
    L.append('| %s/%s | %d |' % (book, f, n))
L.append('')
L.append('## 三、逐檔統計\n')
L.append('| resp | 條數 | 否決 | 存疑 | 備註 |')
L.append('|---|---|---|---|---|')
for n in nnns:
    it, fx, rj, db, nt = rows[n]
    L.append('| %s | %d | %d | %d | %s |' % (n, it, rj, db, nt))
L.append('')
L.append('## 四、否決類型（通則）\n')
L.append('1. **篇題／目錄譯名**（卷首三十篇目錄，如「二衣的總別」）：不改。正文各篇標題仍用原文，改目錄會造成前後不一致，屬體例另案。')
L.append('2. **加註建議**（術語首見加註、書名全稱、篇名還原、度量衡換算、人物小傳）：屬體例，不改正文。')
L.append('3. **純潤飾**（同義改寫、語序調整、語氣微調、同義反覆）：不改。')
L.append('4. **夾註體例**（要求把正文夾註一律移作註腳／〔按〕）：除個別註文已錯者外，不作全面重排。')
L.append('5. **引文查無**：少數意見所引現譯字句在現行譯文中查無（材料與現行譯文有微小落差），該條按「查無」跳過。')
L.append('6. **整體性主張**（如「增譯一律標記」「術語統一」「虛詞複查」）：僅就點名之具體字句修正，不作全篇改寫。\n')
L.append('## 五、存疑\n')
_ns, _n = [], 0
for _f, _b in (('01_行事鈔.md', '01_行事鈔'), ('02_戒疏.md', '02_戒疏')):
    _dm = os.path.join(ROOT, '存疑材料', 'r3_存疑', _f)
    if os.path.exists(_dm):
        _k = sum(1 for l in open(_dm, encoding='utf-8') if l.startswith('- **'))
        if _k:
            _ns.append('`存疑材料/r3_存疑/%s`（%d 條）' % (_f, _k))
            _n += _k
L.append('判定為存疑者共 %d 條（分見各檔備註）；其中需覆核古注、兩讀並存而逐條記錄者 %d 條，見 %s，現行譯文均未動。\n'
         % (t_doubt, _n, '、'.join(_ns) if _ns else '（無）'))
L.append('## 六、未完成\n')
L.append('已處理至 `resp_%s`；目錄中尚未處理者：%s。續跑時：讀 `resp_NNN.txt` → 以 `python AI語譯/_work/review/_r3/tj2.py NNN` 先分類 → 只對「仍存」者逐條深判 → 寫 `pNNN.txt`（`#items=|fixed=|rej=|doubt=|note=` 加 `舊<TAB>新`）交 `ap.py`（自動定位、自動備份、行尾不變）→ 於 `r3_done.tsv` 追加一行 → 重跑 `gen.py`。'
         % (nnns[-1], ('、'.join(_remain) if _remain else '無（目錄內皆已處理）')))
open(OUTMD, 'w', encoding='utf-8').write('\n'.join(L))
print('wrote', OUTMD, 'files', len(rows), 'items', t_items, 'segs', t_seg, 'rej', t_rej, 'doubt', t_doubt)
print('by chunk', dict(seg_by_chunk))

p = os.path.join(ROOT, 'batch_qwen', 'r2_done.txt')
cur = open(p, encoding='utf-8').read()
add = [n for n in nnns if ('r3:' + n) not in cur]
with open(p, 'a', encoding='utf-8') as f:
    for n in add:
        f.write('r3:%s\n' % n)
print('appended', len(add))
