# -*- coding: utf-8 -*-
"""修正《四分律行事鈔資持記 句級合編》卷中之二 的鈔記錯位。

問題
----
`白話/行事鈔資持記句級合編_卷中之二.docx` 由《會本_篇14_隨戒釋相》第 904–1656
段切出，內容是「鈔 67–141（75 段）＋記 377–678（301 段）」共 376 組
（標籤段＋白話段）。

《資持記》的段落界線與「戒」的界線不齊：一戒記文末尾（不犯、開緣等科文）
常與下一戒的戒名科文併在同一記段，例如
    記385 ＝「為他下，釋出其相。」（故失精戒記末）
           ＋「第二。〔迦留陀夷…〕戒名中。…」（摩觸女人戒記首）
`hb_align` 依「該段主要在講哪一鈔」把它掛到下一戒的鈔，整段就掉到下一戒鈔之後。
實測 47 個戒界有 35 處如此，另有 1 處（捨墮25）反向早了兩段。

作法
----
以戒名為錨點切成 47 個戒單元（僧殘 13、二不定總科＋2 戒、三十捨墮總科＋30 戒）：
  * 鈔的錨點＝戒題首句（「摩觸女人戒第二。」「月望衣戒三。」「初長衣過限戒」）；
  * 記的錨點＝科文序＋制戒因緣（「第二。〔迦留陀夷…」）或「二不定，標指中」
    「三十捨墮，名兼罪懺」「初戒。〔佛在舍衛…」。
重排後每個戒單元「鈔段全部在前、記段全部在後」；鈔段之間、記段之間各保原序，
全卷鈔序與記序都不變，只是鈔段的插入點換位置。文字一字未改（白話段跟著搬）。

用法
----
    python _src/fix_hebian_jz2.py --dry-run      # 只檢查
    python _src/fix_hebian_jz2.py                # 套用（每戒：鈔全部 → 記全部）
    python _src/fix_hebian_jz2.py --mode pair    # 只修跨戒錯位，保留鈔記就近對照
"""
import io, os, re, sys, hashlib, collections
from docx import Document
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = os.path.join(B, '白話', '行事鈔資持記句級合編_卷中之二.docx')
YUAN = os.path.join(B, '白話', '會本_篇14_隨戒釋相.docx')
NOTE = os.path.join(B, '合編_卷中之二_重排說明.md')
K2, K3 = 904, 1656

UNIT = [
    ('僧殘1 故失精戒', '僧殘篇中，故失精戒第一'),
    ('僧殘2 摩觸女人戒', '摩觸女人戒第二'),
    ('僧殘3 與女人麁語戒', '與女人麁語戒第三'),
    ('僧殘4 向女歎身索供戒', '向女歎身索供戒第四'),
    ('僧殘5 媒人戒', '媒人戒第五'),
    ('僧殘6 無主僧不處分過量房戒', '無主僧不處分過量房戒第六'),
    ('僧殘7 有主僧不處分房戒', '有主僧不處分房戒第七'),
    ('僧殘8 無根重罪謗他戒', '無根重罪謗他戒第八'),
    ('僧殘9 假根謗戒', '假根謗戒第九'),
    ('僧殘10 破僧違諫戒', '破僧違諫戒第十'),
    ('僧殘11 助破僧違諫戒', '助破僧違諫戒第十一'),
    ('僧殘12 污家擯謗違僧諫戒', '污家擯謗違僧諫戒第十二'),
    ('僧殘13 惡性拒僧違諫戒', '惡性拒僧違諫戒第十三'),
    ('二不定總科', '二不定中，文疏久列'),
    ('不定1 初不定', '初不定中，四緣犯之'),
    ('不定2 後不定', '後不定戒，略同前者'),
    ('三十捨墮總科', '三十捨墮，懺法如後'),
    ('捨墮1 長衣過限戒', '初長衣過限戒'),
    ('捨墮2 離三衣宿戒', '離三衣宿戒第二'),
    ('捨墮3 月望衣戒', '月望衣戒三'),
    ('捨墮4 取非親尼衣戒', '取非親尼衣戒四'),
    ('捨墮5 使非親尼浣故衣戒', '使非親尼浣故衣戒五'),
    ('捨墮6 從非親俗人乞衣戒', '從非親俗人乞衣戒六'),
    ('捨墮7 過分取衣戒', '過分取衣戒七'),
    ('捨墮8 勸增衣價戒', '勸增衣價戒八'),
    ('捨墮9 勸二家增衣價戒', '勸二家增衣價戒九'),
    ('捨墮10 過限急索衣價戒', '過限怱切索衣價戒十'),
    ('捨墮11 乞蠶綿作袈裟戒', '乞蠶綿作袈裟戒十一'),
    ('捨墮12 黑毛臥具戒', '黑毛臥具戒十二'),
    ('捨墮13 白毛三衣戒', '白毛三衣戒十三'),
    ('捨墮14 減六年作三衣戒', '減六年作三衣戒十四'),
    ('捨墮15 不貼坐具戒', '不貼坐具戒十五'),
    ('捨墮16 持羊毛過限戒', '持羊毛過限戒十六'),
    ('捨墮17 使非親尼浣染毛戒', '使非親尼浣染毛戒十七'),
    ('捨墮18 畜錢寶戒', '畜錢寶戒十八'),
    ('捨墮19 貿寶戒', '貿寶戒十九'),
    ('捨墮20 販賣戒', '販賣戒二十'),
    ('捨墮21 畜長鉢過限戒', '畜長鉢過限戒二十一'),
    ('捨墮22 乞鉢戒', '乞鉢戒二十二'),
    ('捨墮23 自乞縷使非親織戒', '自乞縷使非親織戒二十三'),
    ('捨墮24 勸織師增衣縷戒', '勸織師增衣縷戒二十四'),
    ('捨墮25 奪衣戒', '奪衣戒二十五'),
    ('捨墮26 畜七日藥過限戒', '畜七日藥過限戒二十六'),
    ('捨墮27 過前求雨衣過前用戒', '過前求雨衣過前用戒二十七'),
    ('捨墮28 過前受急施衣過後畜戒', '過前受急施衣過後畜戒二十八'),
    ('捨墮29 有難蘭若離衣戒', '有難蘭若離衣戒二十九'),
    ('捨墮30 說迴僧物入己戒', '說迴僧物入'),
]

# (單元序, 記號, 子標記, 段內位置 0=段首, 錨文字, 依據)
ANCH = [
    (1, 377, '', 16, '第一戒。', '卷頭「釋十三僧殘第一戒」'),
    (2, 385, '', 9, '第二。', '科文「第二。」＋制戒因緣'),
    (3, 398, '', 81, '第三。', '科文「第三。」＋制戒因緣'),
    (4, 402, '', 88, '第四。', '科文「第四。」＋制戒因緣'),
    (5, 405, '', 33, '第五。', '科文「第五。」＋制戒因緣'),
    (6, 412, '', 77, '第六。', '科文「第六。」＋制戒因緣'),
    (7, 439, '', 10, '第七。', '科文「第七。」＋制戒因緣'),
    (8, 441, '', 60, '第八。', '科文「第八。」＋制戒因緣'),
    (9, 446, '', 109, '第九。', '科文「第九。」＋制戒因緣'),
    (10, 448, '', 96, '第十。', '科文「第十。」＋制戒因緣'),
    (11, 453, '（後半）', 0, '十一。', '科文「十一。」＋制戒因緣（原有切分）'),
    (12, 454, '', 85, '十二。', '科文「十二。」＋制戒因緣'),
    (13, 461, '', 30, '十三。', '科文「十三。」＋制戒因緣'),
    (14, 463, '', None, '二不定，標指中', '二不定總科'),
    (15, 465, '', None, '一屏處不定。', '初二不定科文＋制戒因緣'),
    (16, 467, '', None, '二露處不定。', '後二不定科文＋制戒因緣'),
    (17, 468, '', None, '三十捨墮，名兼罪懺', '三十捨墮總科'),
    (18, 468, '', None, '初戒。〔佛在舍衛', '捨墮第一戒科文＋制戒因緣'),
    (19, 487, '（後半）', 0, '第二。', '科文「第二。」＋制戒因緣（原有切分）'),
    (20, 524, '', 25, '第三。', '科文「第三。」＋制戒因緣'),
    (21, 527, '', 23, '第四。', '科文「第四。」＋制戒因緣'),
    (22, 532, '', 67, '第五。', '科文「第五。」＋制戒因緣'),
    (23, 537, '', 0, '第六。', '科文「第六。」＋制戒因緣'),
    (24, 543, '', 78, '第七。', '科文「第七。」＋制戒因緣'),
    (25, 546, '', 43, '第八。', '科文「第八。」＋制戒因緣'),
    (26, 549, '', 0, '第九。', '科文「第九。」＋制戒因緣'),
    (27, 550, '', 74, '第十。', '科文「第十。」＋制戒因緣'),
    (28, 553, '', 28, '十一。', '科文「十一。」＋制戒因緣'),
    (29, 563, '', 16, '十二。', '科文「十二。」＋制戒因緣'),
    (30, 564, '', 83, '十三。', '科文「十三。」＋制戒因緣'),
    (31, 566, '', 33, '十四。', '科文「十四。」＋制戒因緣'),
    (32, 567, '', 93, '十五。', '科文「十五。」＋制戒因緣'),
    (33, 570, '', 59, '十六。', '科文「十六。」＋制戒因緣'),
    (34, 573, '', 31, '十七。', '科文「十七。」＋制戒因緣'),
    (35, 574, '', 47, '十八。', '科文「十八。」＋制戒因緣'),
    (36, 622, '', 93, '十九。', '科文「十九。」＋制戒因緣'),
    (37, 626, '', 36, '二十。', '科文「二十。」＋制戒因緣'),
    (38, 639, '', 63, '二十一。', '科文「二十一。」＋制戒因緣'),
    (39, 640, '', 63, '二十二。', '科文「二十二。」＋制戒因緣'),
    (40, 642, '', 28, '二十三。', '科文「二十三。」＋制戒因緣'),
    (41, 644, '', 56, '二十四。', '科文「二十四。」＋制戒因緣'),
    (42, 646, '', 0, '二十五。', '科文「二十五。」＋制戒因緣'),
    (43, 648, '（後半）', 0, '二十六。', '科文「二十六。」＋制戒因緣（原有切分）'),
    (44, 651, '（後半）', 0, '二十七。', '科文「二十七。」＋制戒因緣（原有切分）'),
    (45, 657, '', 65, '二十八。', '科文「二十八。」＋制戒因緣'),
    (46, 662, '', 0, '二十九。', '科文「二十九。」＋制戒因緣'),
    (47, 668, '', 119, '三十。', '科文「三十。」＋制戒因緣'),
]

TAG = re.compile(r'^【(鈔|記)】(（前）|（中）|（後半）|（前半）)?')


def yuan_pairs():
    ps = [p.text for p in Document(YUAN).paragraphs]
    seg = ps[K2:K3]
    out, i = [], 0
    while i < len(seg):
        m = re.match(r'^【(鈔|記)(\d+)】(（[^）]*）)?', seg[i])
        if m:
            out.append(dict(kind=m.group(1), num=int(m.group(2)), sub=(m.group(3) or ''),
                            body=seg[i][m.end():], tr=seg[i + 1] if i + 1 < len(seg) else ''))
            i += 2
        else:
            i += 1
    return out


def norm(t):
    m = TAG.match(t)
    if not m:
        raise SystemExit('合編段落缺標籤：%r' % t[:30])
    return m.group(1), (m.group(2) or '') + t[m.end():]


def hebian_paras():
    ps = list(Document(HB).paragraphs)
    texts = [p.text for p in ps]
    assert texts[0].startswith('行事鈔') and texts[2].startswith('第14篇'), texts[:3]
    body = texts[3:]
    assert len(body) == 752, len(body)
    return ps, texts[:3], [(body[2 * k], body[2 * k + 1]) for k in range(376)]


def assign(yp):
    cur = None
    for r in yp:
        if r['kind'] == '鈔':
            for i, (name, pre) in enumerate(UNIT, 1):
                if r['body'].startswith(pre):
                    cur = i
                    break
            r['u'] = cur
    idx = {}
    for k, r in enumerate(yp):
        idx.setdefault((r['kind'], r['num'], r['sub']), k)
    A = []
    for (u, num, sub, pos, txt, why) in ANCH:
        k = idx.get(('記', num, sub))
        if k is None:
            raise SystemExit('找不到錨點段：記%d%s' % (num, sub))
        body = yp[k]['body']
        p = body.find(txt)
        if p < 0:
            raise SystemExit('錨文字不在 記%d%s：%r' % (num, sub, txt))
        if pos is not None and p != pos:
            raise SystemExit('錨點位置不符 記%d%s：表%d 實%d' % (num, sub, pos, p))
        A.append((u, k, p, txt, why))
    for k in range(1, len(A)):
        if (A[k][1], A[k][2]) <= (A[k - 1][1], A[k - 1][2]):
            raise SystemExit('錨點非遞增：記%d' % A[k][1])
    for k, r in enumerate(yp):
        if r['kind'] != '記':
            continue
        u = 1
        for (au, ai, apos, txt, why) in A:
            if ai < k or (ai == k and apos == 0):
                u = au
            else:
                break
        r['u'] = u
    return yp, A


def block_order(cl):
    order = []
    for u in range(1, len(UNIT) + 1):
        order += [k for k, r in enumerate(cl) if r['u'] == u and r['kind'] == '鈔']
        order += [k for k, r in enumerate(cl) if r['u'] == u and r['kind'] == '記']
    return order


def pair_order(cl):
    n = len(cl)
    order = list(range(n))
    for u in range(1, len(UNIT) + 1):
        cs = [k for k, r in enumerate(cl) if r['u'] == u and r['kind'] == '鈔']
        if not cs:
            continue
        lo = min(cs)
        nxt = [k for k, r in enumerate(cl) if r['kind'] == '鈔' and r['u'] == u + 1]
        hi = min(nxt) if nxt else n
        js = [k for k, r in enumerate(cl) if r['u'] == u and r['kind'] == '記']
        early = [k for k in js if k < lo]
        late = [k for k in js if k >= hi]
        if early:
            for k in early:
                order.remove(k)
            p = order.index(lo) + 1
            for j, k in enumerate(early):
                order.insert(p + j, k)
        if late:
            for k in late:
                order.remove(k)
            p = order.index(hi) if hi < n else len(order)
            for j, k in enumerate(late):
                order.insert(p + j, k)
    return order


def check(cl, order, base):
    res = []
    res.append(('段落總數', len(order) == len(base), '%d 組（原 %d）' % (len(order), len(base))))
    hs = [hashlib.sha1((cl[k]['kind'] + cl[k]['body']).encode('utf-8')).hexdigest() for k in order]
    res.append(('無重複段落', len(set(hs)) == len(hs), '%d 組皆唯一' % len(set(hs))))
    h0 = collections.Counter(hashlib.sha1((r['kind'] + r['body']).encode('utf-8')).hexdigest() for r in base)
    res.append(('內容不增不減', collections.Counter(hs) == h0, 'sha1 計數相同'))
    chars = collections.Counter(''.join(cl[k]['body'] for k in order))
    chars0 = collections.Counter(''.join(r['body'] for r in base))
    res.append(('字元總量不變', chars == chars0, '共 %d 字' % sum(chars.values())))
    c0 = [k for k in order if cl[k]['kind'] == '鈔']
    c1 = [k for k in range(len(cl)) if cl[k]['kind'] == '鈔']
    res.append(('鈔段順序不變', c0 == c1, '鈔 %d 段' % len(c0)))
    j0 = [k for k in order if cl[k]['kind'] == '記']
    j1 = [k for k in range(len(cl)) if cl[k]['kind'] == '記']
    res.append(('記段順序不變', j0 == j1, '記 %d 段' % len(j0)))
    bad = []
    for u in range(1, len(UNIT) + 1):
        cs = [i for i, k in enumerate(order) if cl[k]['u'] == u and cl[k]['kind'] == '鈔']
        js = [i for i, k in enumerate(order) if cl[k]['u'] == u and cl[k]['kind'] == '記']
        if cs and js and max(cs) > min(js):
            bad.append(UNIT[u - 1][0])
    res.append(('每戒鈔在記前', not bad, '例外：%s' % '、'.join(bad) if bad else '47 單元全過'))
    return res


def rewrite(order, pairs_ps):
    doc = Document(HB)
    body = doc.element.body
    sect = body.find(qn('w:sectPr'))
    ps = [p for p in doc.paragraphs if p.text.strip()]
    assert len(ps) == 755, len(ps)
    tail = [p._p for p in ps[3:]]
    assert len(tail) == 752
    for el in tail:
        body.remove(el)
    for k in order:
        sect.addprevious(tail[2 * k])
        sect.addprevious(tail[2 * k + 1])
    doc.save(HB)


def write_note(cl, order, mode, checks, moved, nseg, stats, counts):
    pos2 = {k: i + 1 for i, k in enumerate(order)}
    L = []
    L.append('# 合編_卷中之二 重排說明\n')
    L.append('> 對象：`白話/行事鈔資持記句級合編_卷中之二.docx`（四分律行事鈔資持記　句級合編　卷中之二／第14篇　隨戒釋相（續））  ')
    L.append('> 備份：`歸檔/合編備份_卷中之二/`（docx、PDF、HTML、會本_篇14、產生腳本、hb_align.json）\n')

    L.append('## 一、現行合編的資料結構\n')
    L.append('| 項目 | 內容 |\n|:--|:--|')
    L.append('| 上游產生 | `_src/mk_pian_split.py` 依 `AI語譯/_work/hb_align.json` 把記段插到對應鈔段之後，'
             '產出 `白話/會本_篇14_隨戒釋相.docx` |')
    L.append('| 切卷 | `_src/rebuild_hebian_v2.py` 取《會本_篇14》第 904–1656 段 → `白話/行事鈔資持記句級合編_卷中之二.docx`（755 段＝3 標題＋752 段） |')
    L.append('| 網站 | `_src/site_hebian.py` → `docs/hebian/卷中之二.html`、`docs/search/hebian.js` |')
    L.append('| PDF | `_src/mk_pdfs.py` → `白話/PDF/行事鈔資持記句級合編_卷中之二.pdf` |')
    L.append('| 本卷內容 | 鈔 67–141（75 段）＋記 377–671（301 段；其中 453、487、488、648、651 已切成 6 個片段）'
             '＝376 組，每組＝標籤段＋白話段（合編 docx 已去編號） |')
    L.append('| 戒單元 | 47＝僧殘 13＋二不定（總科＋2 戒）＋三十捨墮（總科＋30 戒） |')
    L.append('| 記段已有切分 | 記453、記487、記488、記648、記651 的（前）／（中）／（後半） |')

    L.append('\n## 二、錯位成因\n')
    L.append('《資持記》的段落界線與「戒」的界線不齊：上一戒記文末尾（不犯、開緣等科文）'
             '常和下一戒的戒名科文併在同一記段，例如\n')
    L.append('- `記385`＝「為他下，釋出其相。」（故失精戒記末）＋「第二。〔迦留陀夷以佛制前戒…〕戒名中。…」（摩觸女人戒記首）')
    L.append('- `記412`＝媒人戒記末＋「第六。〔佛在羅閱祇，開聽作房…〕」')
    L.append('- `記468`＝後不定記末＋「三十捨墮，名兼罪懺…」＋「初戒。〔佛在舍衛，六群畜多長衣…」')
    L.append('\n`hb_align` 以「這一段記文主要在解釋第幾號鈔」判定，這一整段就被掛到下一戒的鈔，'
             '於是掉到下一戒鈔之後。實測 47 個戒界有 **35 處**是這樣；另 **1 處**（捨墮25 奪衣戒）'
             '反向早了兩段（記646、記647 排在鈔136 之前）。\n')

    L.append('## 三、重排規則與錨點\n')
    if mode == 'block':
        L.append('每個戒單元：先出該戒**全部鈔段**（原序），再出該戒**全部記段**（原序）。'
                 '跨戒記段整段歸「開頭所屬」的戒（不切段，段數不變）。')
    else:
        L.append('只把越界的記段搬回本戒範圍（本戒鈔之後、下一戒鈔之前），'
                 '其餘維持「鈔段→該鈔之記段」的就近對照。')
    L.append('\n- 鈔錨點＝戒題首句：`摩觸女人戒第二`、`月望衣戒三`、`初長衣過限戒`、`初不定中`…')
    L.append('- 記錨點＝科文序＋制戒因緣：`第二。〔迦留陀夷…`、`二十一。〔佛在舍衛…`，'
             '及 `二不定，標指中`、`三十捨墮，名兼罪懺`、`初戒。〔佛在舍衛…`')
    L.append('- 錨點落在記段中間者（35 處），該段判歸前一戒（其開頭仍屬前一戒的記文），'
             '下一戒記群由次一段起算；若錨點在段首（記453（後半）、記537、記549、記646、'
             '記662 等）則該段即下一戒記群之首。')
    L.append('\n## 四、改了哪些段（原位置 → 新位置）\n')
    ncross, nearly, nextra = counts
    if mode == 'block':
        L.append('位置＝本卷 376 組的段序（1 起算）。'
                 'block 模式下多鈔段的 4 個戒（僧殘6、捨墮1、捨墮2、捨墮18）鈔段一併提前，'
                 '故搬動段數較多；其餘 43 戒只是把跨戒記段搬回本戒。\n')
        L.append('- 真正換位的段：**%d** 段 ＝ 跨戒記段 %d＋原本排在本戒鈔前的記段 %d＋多鈔戒的後續鈔段 %d' % (
            ncross + nearly + nextra, ncross, nearly, nextra))
        L.append('- 段序編號改變（含因前後插入而位移）：%d 段' % len(moved))
        L.append('- 只搬段落、不切段：376 組不增不減\n')
    else:
        L.append('位置＝本卷 376 組的段序（1 起算）。\n')
        L.append('- 真正換位的段：**%d** 段（跨戒記段 %d、原本排在鈔前的記段 %d）' % (
            ncross + nearly, ncross, nearly))
        L.append('- 段序編號改變：%d 段\n' % len(moved))
    L.append('| # | 段 | 首句 | 原位置 | 新位置 | 新歸屬 | 依據 |')
    L.append('|--:|:--|:--|--:|--:|:--|:--|')
    for i, (k, why) in enumerate(moved, 1):
        r = cl[k]
        tag = '%s%03d%s' % ('鈔' if r['kind'] == '鈔' else '記', r['num'], r['sub'])
        L.append('| %d | %s | %s… | %d | %d | %s | %s |' % (
            i, tag, r['body'][:16], k + 1, pos2[k], UNIT[r['u'] - 1][0], why))
    L.append('\n合計段序改變 **%d** 段，其餘 %d 段位置不變；重排後全卷仍是 376 組。\n' % (
        len(moved), nseg - len(moved)))

    L.append('## 五、驗證結果\n')
    L.append('| 檢查 | 結果 | 說明 |\n|:--|:--:|:--|')
    for name, ok, info in checks:
        L.append('| %s | %s | %s |' % (name, '○ 通過' if ok else '× 未通過', info))
    L.append('\n- 每戒區間順序：' + '、'.join(
        '%s（鈔%d→記%d）' % (UNIT[u - 1][0].split(' ')[0], a, b)
        for u, a, b in stats[:8]) + ' …（完整見下表）')
    L.append('\n### 各戒段數\n')
    L.append('| 戒單元 | 鈔段 | 記段 | 重排後位置範圍 |')
    L.append('|:--|--:|--:|:--|')
    for u, a, b in stats:
        pos = [i + 1 for i, k in enumerate(order) if cl[k]['u'] == u]
        L.append('| %s | %d | %d | %d–%d |' % (UNIT[u - 1][0], a, b, min(pos), max(pos)))

    L.append('\n## 六、重建輸出\n')
    L.append('```\n'
             'python _src/site_hebian.py                        # docs/hebian/卷中之二.html（＋搜尋索引）\n'
             'python _src/mk_pdfs.py --match 句級合編_卷中之二    # 白話/PDF/行事鈔資持記句級合編_卷中之二.pdf\n'
             '```\n')
    L.append('注意：日後若重跑 `_src/rebuild_hebian_v2.py` 重新產生合編 docx，本卷會回到錯位狀態，'
             '須再跑一次 `python _src/fix_hebian_jz2.py`。\n')

    L.append('## 七、本輪未處理\n')
    L.append('- 跨戒記段**不切開**，所以下一戒的戒名科文（「第二。〔…〕」等 35 處）仍留在上一戒記群末尾；'
             '若要每戒記群由自己的戒名科文起頭，必須切段（段數 +35），與「段落總數不增不減」的驗證衝突，故不做。')
    L.append('- 只動卷中之二；其餘 11 卷與《會本_篇14_隨戒釋相.docx》均未修改。')
    L.append('- 未改動任何原文或譯文用字，只搬動段落順序。')
    io.open(NOTE, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


def main():
    dry = '--dry-run' in sys.argv
    mode = 'block'
    if '--mode' in sys.argv:
        mode = sys.argv[sys.argv.index('--mode') + 1]
    if mode not in ('block', 'pair'):
        raise SystemExit('--mode 只接受 block / pair')

    yp = yuan_pairs()
    assert len(yp) == 376
    yp, anchors = assign(yp)
    ps, heads, pairs = hebian_paras()

    # 合編目前順序 → 對回會本段（重跑時順序已變也能對）
    key = {}
    for i, r in enumerate(yp):
        key.setdefault((r['kind'], r['sub'] + r['body']), []).append(i)
    cur_idx = []
    for (tag, tr) in pairs:
        kind, rest = norm(tag)
        cand = key.get((kind, rest))
        if not cand:
            raise SystemExit('合編段落對不上會本切片：%r' % tag[:40])
        cur_idx.append(cand.pop(0))
    assert sorted(cur_idx) == list(range(376)), '對應不是一對一'
    cl = [yp[i] for i in cur_idx]

    order = block_order(cl) if mode == 'block' else pair_order(cl)
    assert sorted(order) == list(range(376))
    checks = check(cl, order, yp)
    ok = all(c[1] for c in checks)

    pos2 = {k: i + 1 for i, k in enumerate(order)}
    firsts = {}
    for k, r in enumerate(cl):
        if r['kind'] == '鈔':
            firsts.setdefault(r['u'], k)
    moved = []
    ncross = nearly = nextra = 0
    for k in range(376):
        if pos2[k] == k + 1:
            continue
        r, u = cl[k], cl[k]['u']
        if r['kind'] == '記':
            nxt = [i for i, rr in enumerate(cl) if rr['kind'] == '鈔' and rr['u'] == u + 1]
            if nxt and k > min(nxt):
                why = '跨戒記段：開頭屬本戒記末、錨點在段中屬下一戒 → 搬回本戒記群末'
                ncross += 1
            elif k < firsts.get(u, 0):
                why = '記段原在本戒鈔段之前 → 搬到本戒鈔段之後'
                nearly += 1
            else:
                why = '同戒內：本戒後續鈔段提前到記群前，記段段序後移'
        else:
            if k != firsts.get(u, -1):
                why = '本戒鈔段集中到記群之前（非首鈔段提前）'
                nextra += 1
            else:
                why = '跨戒記段移入其前，段序後移一段'
        moved.append((k, why))
    moved.sort()

    stats = []
    for u in range(1, len(UNIT) + 1):
        a = sum(1 for r in cl if r['u'] == u and r['kind'] == '鈔')
        b = sum(1 for r in cl if r['u'] == u and r['kind'] == '記')
        stats.append((u, a, b))

    print('模式：%s' % mode)
    for name, o, info in checks:
        print('  %-8s %s  %s' % (name, 'OK  ' if o else 'FAIL', info))
    print('段序改變 %d / 376 段；實際換位 %d 段（跨戒 %d、早置 %d、鈔段 %d）' % (
        len(moved), ncross + nearly + nextra, ncross, nearly, nextra))
    if not ok:
        print('驗證未通過，未寫檔')
        return 1
    if dry:
        print('dry-run，未寫檔')
        return 0
    rewrite(order, ps)
    write_note(cl, order, mode, checks, moved, 376, stats, (ncross, nearly, nextra))
    print('已寫入', HB)
    print('已寫入', NOTE)
    return 0


if __name__ == '__main__':
    sys.exit(main())
