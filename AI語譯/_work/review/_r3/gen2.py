# -*- coding: utf-8 -*-
"""gen2.py -- 說明_r3_前段.md 產生器。
差別於 gen.py：
1. 只統計「前段」resp（001-180）的 r3_done.tsv 紀錄，後段（181+）另計不寫入。
2. 累計改動段數：有 <chunk>.txt 備份者比對該檔（001-038 原始）；
   只有 <chunk>_b.txt 者（039 以後首次觸及）比對 _b。
3. 另列本輪 039+ 改動段數（一律比對 _b）。
"""
import os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
DONE = os.path.join(WORK, 'r3_done.tsv')
OUTMD = os.path.join(WORK, '說明_r3_前段.md')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
OUT = os.path.join(ROOT, 'AI語譯', 'out')
SPLIT = '180'

rows, rows_late = {}, set()
order = []
for ln in open(DONE, encoding='utf-8'):
    p = ln.rstrip('\n').split('\t')
    if len(p) < 6:
        continue
    nnn, items, fixed, rej, doubt, note = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4]), p[5]
    if note == 'pending':
        continue
    if nnn > SPLIT:
        rows_late.add(nnn)
        continue
    if nnn not in rows:
        order.append(nnn)
    rows[nnn] = (items, fixed, rej, doubt, note)

def paras(p):
    t = open(p, 'rb').read().decode('utf-8-sig')
    return [s.rstrip('\r') for s in t.split('\n') if s.rstrip('\r').strip()]

seg_by_book = collections.Counter()
seg_by_chunk = collections.Counter()
seg2_by_chunk = collections.Counter()
seg3_by_chunk = collections.Counter()
def mat_chunks(lo, hi):
    """校閱_lo..hi 標籤所涵蓋的 (book,chunk) 集合"""
    import re
    LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
    MAT = os.path.join(ROOT, '校閱_10K')
    s = set()
    for n in range(lo, hi + 1):
        p = os.path.join(MAT, '校閱_%03d.txt' % n)
        if not os.path.exists(p):
            continue
        for ln in open(p, 'rb').read().decode('utf-8-sig').split('\n'):
            m = LBL.match(ln.rstrip('\r'))
            if m:
                s.add((m.group(3), m.group(4) + '.txt'))
    return s

_last = int(max(rows))
ALL_MAIN = mat_chunks(1, _last)
ALL_CUR = mat_chunks(39, _last)

for book in sorted(os.listdir(BAK)):
    bd = os.path.join(BAK, book)
    if not os.path.isdir(bd):
        continue
    names = set()
    for f in os.listdir(bd):
        if f.endswith(('_b.txt', '_c.txt')):
            names.add(f[:-6] + '.txt')
        else:
            names.add(f)
    for f in sorted(names):
        if not f.endswith('.txt'):
            continue
        if (book, f) not in ALL_MAIN:
            continue
        cur_p = os.path.join(OUT, book, f)
        if not os.path.exists(cur_p):
            continue
        b = paras(cur_p)
        orig_p = os.path.join(bd, f)
        bp = os.path.join(bd, f[:-4] + '_b.txt')
        cp = os.path.join(bd, f[:-4] + '_c.txt')
        if os.path.exists(orig_p):
            a = paras(orig_p)
            if len(a) != len(b):
                print('!! count mismatch', book, f, len(a), len(b))
            else:
                n = sum(1 for x, y in zip(a, b) if x != y)
                if n:
                    seg_by_book[book] += n
                    seg_by_chunk[(book, f)] += n
        if os.path.exists(bp):
            a2 = paras(bp)
            if len(a2) != len(b):
                print('!! _b count mismatch', book, f, len(a2), len(b))
            else:
                n2 = sum(1 for x, y in zip(a2, b) if x != y)
                if n2:
                    seg2_by_chunk[(book, f)] += n2
                if not os.path.exists(orig_p) and n2:
                    # 只有 _b：累計即本輪
                    seg_by_book[book] += n2
                    seg_by_chunk[(book, f)] += n2
        if os.path.exists(cp) and not os.path.exists(orig_p) and not os.path.exists(bp):
            a3 = paras(cp)
            if len(a3) != len(b):
                print('!! _c count mismatch', book, f, len(a3), len(b))
            else:
                n3 = sum(1 for x, y in zip(a3, b) if x != y)
                if n3:
                    seg_by_book[book] += n3
                    seg_by_chunk[(book, f)] += n3
                    seg3_by_chunk[(book, f)] += n3
t_seg = sum(seg_by_book.values())
t_seg2 = sum(seg2_by_chunk.values())
t_seg3 = sum(seg3_by_chunk.values())
t_items = sum(v[0] for v in rows.values())
t_rej = sum(v[2] for v in rows.values())
t_doubt = sum(v[3] for v in rows.values())
nnns = sorted(rows)

L = []
L.append('# r3 前段校閱意見處理說明\n')
L.append('> 本檔由 `AI語譯/_work/review/_r3/gen2.py` 依 `r3_done.tsv`（僅取 resp 001–%s）與實際譯文差異自動生成。\n' % SPLIT)
L.append('## 一、範圍與依據\n')
L.append('- 回覆來源：`batch_qwen/r3/resp_%s.txt` ～ `resp_%s.txt`（目錄現存 323 檔；本次處理 %d 檔，尚餘 %d 檔）。'
         % (nnns[0], nnns[-1], len(nnns), 323 - len(nnns)))
L.append('- 對應材料：`校閱_10K/校閱_%s.txt` ～ `校閱_%s.txt`。' % (nnns[0], nnns[-1]))
L.append('- 對照檔（權威來源）：`AI語譯/out/<書>/<chunk>.txt`。材料標籤 `【NNN-MMMM】<書>/<chunk>#段` **不以段號定位**：改以材料【譯文】全文與 out 段落逐一比對（完全相同者取唯一精確命中，微差者取相似度 ≥0.94 之最佳者）。實測材料段號自 校閱_022 起與 out 段落相差 2 段以上，故段號不可信。')
L.append('- 改動方式：只換該段的字句（片語級替換），不動段落數、不動行尾（各檔 LF/CRLF 原樣保留）。')
L.append('- 備份：`歸檔/r3修正前/<書>/<chunk>.txt`（001–038 首次改動前的原樣）、`<chunk>_b.txt`（039–060 首次改動前的原樣）、`<chunk>_c.txt`（061 以後首次改動前的原樣）。')
L.append('- 逐檔紀錄：`r3_done.tsv`；改動明細：`fix_r3.tsv`（001–038）、`fix_r3b.tsv`（039–060）、`fix_r3c.tsv`（061 以後）；處理腳本：`_r3/seg.py`、`edit2.py`、`edit3.py`、`edit4.py`、`sug.py`、`find.py`、`gen2.py`、`verify.py`。\n')
L.append('## 二、統計\n')
L.append('| 項目 | 數 |')
L.append('|---|---|')
L.append('| 處理回覆檔 | %d |' % len(rows))
L.append('| 處理意見條數 | %d |' % t_items)
L.append('| 實際改動段數（累計，對原始備份） | %d（01_行事鈔 %d、02_戒疏 %d） |'
         % (t_seg, seg_by_book.get('01_行事鈔', 0), seg_by_book.get('02_戒疏', 0)))
L.append('| 其中 039 以後本輪改動段數 | %d |' % t_seg2)
L.append('| 其中 061 以後本輪改動段數 | %d |' % t_seg3)
L.append('| 否決（含潤飾／加註／體例） | %d |' % t_rej)
L.append('| 存疑 | %d |\n' % t_doubt)
L.append('改動分布（累計）：\n')
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
L.append('1. **篇題／目錄譯名**：不改。改目錄會造成前後不一致，屬體例另案。')
L.append('2. **加註建議**（術語首見加註、書名全稱、篇名還原、度量衡換算、人物小傳）：屬體例，不改正文。')
L.append('3. **純潤飾**（同義改寫、語序調整、語氣微調、同義反覆）：不改。')
L.append('4. **夾註體例**（要求把正文夾註一律移作註腳／〔按〕）：除個別註文已錯者外，不作全面重排。')
L.append('5. **引文查無**：意見所引現譯字句在現行譯文中查無者，按「查無」跳過。')
L.append('6. **整體性主張**（如「增譯一律標記」「術語統一」「虛詞複查」）：僅就點名之具體字句修正，不作全篇改寫。')
L.append('7. **增譯清理**：原文所無之形容詞、判斷語、使役義而影響義理者，予以刪削；僅屬語氣修飾者不改。\n')
L.append('## 五、存疑\n')
_dm = os.path.join(ROOT, '存疑材料', 'r3_存疑', '01_行事鈔.md')
_n = 0
if os.path.exists(_dm):
    _n = sum(1 for l in open(_dm, encoding='utf-8') if l.startswith('- **'))
L.append('判定為存疑者共 %d 條（分見各檔備註）；其中需覆核古注、兩讀並存而逐條記錄者 %d 條，見 `存疑材料/r3_存疑/01_行事鈔.md`，現行譯文均未動。\n' % (t_doubt, _n))
L.append('## 六、進度\n')
L.append('已處理至 `resp_%s`（前段範圍）。`resp_%03d` 以後另由後段處理。續跑時：以 `sug.py NNN`（逐條抽取 原文/現譯⇒建議）與 `find.py NNN "現譯片段"`（模糊定位並印上下文）判讀，再寫 `{"subs":[{"nnn":"NNN","pairs":[[舊,新],…]}],"log":[…]}` 交 `edit4.py`（自動定位、備份寫 `<chunk>_c.txt`、行尾不變、明細寫 `fix_r3c.tsv`）→ 重跑 `gen2.py`。'
         % (nnns[-1], int(nnns[-1]) + 1))
open(OUTMD, 'w', encoding='utf-8').write('\n'.join(L))
print('wrote', OUTMD, 'files', len(rows), 'items', t_items, 'segs', t_seg, 'thisrun', t_seg2, 'rej', t_rej, 'doubt', t_doubt)
print('by chunk', dict(seg_by_chunk))
print('this run', dict(seg2_by_chunk))
print('late rows', len(rows_late))
