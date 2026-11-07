# -*- coding: utf-8 -*-
"""篇1-5,7-10 會本（支援 AI 標註的牒詞切點）"""
import io, os, re, json, glob, sys, importlib.util
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
BDIR = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')


def load_bounds(pp):
    fp = os.path.join(BDIR, 'bounds_篇%02d.json' % pp)
    if not os.path.exists(fp):
        return None
    try:
        d = json.load(io.open(fp, encoding='utf-8-sig'))
        bs = [(int(x['c']), int(x['n'])) for x in d.get('bounds', [])]
    except Exception:
        return None
    bs = [b for b in bs if b[1] >= 1]
    if len(bs) < 2:
        return None
    return bs
HDR = re.compile(r'(\d*\s*釋[\u4e00-\u9fff]{1,6}篇(?:\([^)）]*\))?)')
HEADS = {}
_h2 = lambda x: len(re.findall(r'[\u4e00-\u9fff]', x))
_s2 = lambda x: [y for y in re.findall(r'[^。！？；]*[。！？；]?', x) if y.strip()]
for _p in range(2, len(SECS)):
    _o, _t = ZI[_p - 1][0]
    _m = HDR.search(_o[:160])
    if _m and 4 < _m.start() < 120:
        _head = _o[:_m.start()].strip()
        if _head.startswith('四分律行事鈔資持記') or ('四分律行事鈔資持記' in _head and len(_head) < 40):
            continue          # 卷頭題記，不搬到前篇
        if _p == 23 and '世事昭' in _head and not _head.endswith('昭然'):
            _head = _head.rstrip('。') + '然'
        _ts = _s2(_t)
        _ratio = len(_t) / max(1, _h2(_o))
        _need = int(_h2(_head) * _ratio * 1.05)
        _htr = ''
        for _sx in _ts:
            if _h2(_htr) >= _need:
                break
            _htr += _sx
        # 對齊：若 _t 開頭不是 _htr，找它在前面出現的位置
        if _htr and not _t.startswith(_htr):
            _pos = _t[:400].find(_htr[:12]) if len(_htr) >= 12 else -1
            if _pos > 0:
                _htr = _t[:_pos] + _htr
        HEADS[_p] = (_head, _htr)
        _rest = _t[len(_htr):] if _t.startswith(_htr) else _t
        _rest = re.sub(r'^.*?解釋[\u4e00-\u9fff]{1,8}篇(?:\([^)）]*\))?', '', _rest, count=1)
        ZI[_p - 1] = [(_o[_m.start():].strip(), _rest)] + ZI[_p - 1][1:]

# 篇9：記1 取 記2 譯文前半（師通多種），記2 取後半
_o1p, _t1p = ZI[8][0]
_o2p, _t2p = ZI[8][1]
_pp = _t2p.find('「資」是取受')
if _pp < 0:
    _pp = _t2p.find('資」是取受')
if _pp > 0:
    _kp = _t2p.find('學習德業')
    _qp = _t2p.find('。', _kp) if _kp > 0 else _t2p.find('。', _pp)
    if _qp > 0:
        ZI[8] = [(_o1p, _t2p[:_qp + 1]), (_o2p, _t2p[_qp + 1:])] + ZI[8][2:]

# 篇19：清掉記001 譯文殘留的篇18 尾巴
_o19, _t19 = ZI[18][0]
if _t19 and '鉢' in _t19[:_t19.find('。', 0) + 200]:
    _ps = _s2(_t19)
    _st = 0
    for _i, _x in enumerate(_ps):
        if '鉢' in _x:
            _st = _i
            break
    if _st:
        ZI[18] = [(_o19, ''.join(_ps[_st:]))] + ZI[18][1:]

FONT = 'SimSun'; LATIN = 'Times New Roman'
IN = os.path.join(B, 'AI語譯', '_work', 'pian_split_in')
SO = os.path.join(B, 'AI語譯', '_work', 'pian_split_out')

han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def clean_tr(t):
    return t.lstrip('。，；、：')


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def _sents(x):
    out = re.findall(r'[^。！？；]*[。！？；]?', x)
    return [y for y in out if y.strip()]


def split_tr(tr, src_parts):
    src_s, tr_s = [], _sents(tr)
    for part in src_parts:
        src_s += _sents(part)
    if len(src_parts) <= 1:
        return [tr]
    # 依字數比例定位（此處不細修，AI 審校時再標）
    total = sum(max(1, han(x)) for x in src_parts)
    cuts, acc = [], 0
    for part in src_parts[:-1]:
        acc += han(part)
        idx = int(round(acc / total * len(tr_s)))
        cuts.append(max(1, min(idx, len(tr_s) - 1)))
    cuts = sorted(set(cuts))
    while len(cuts) < len(src_parts) - 1:
        cuts.append(min(len(tr_s) - 1, cuts[-1] + 1))
    cuts = cuts[:len(src_parts) - 1]
    parts, prev = [], 0
    for c in cuts:
        parts.append(''.join(tr_s[prev:c])); prev = c
    parts.append(''.join(tr_s[prev:]))
    while len(parts) < len(src_parts):
        parts.append('')
    # 修正：若某片譯文最後一句是「下一科的導語」，移到下一片開頭
    for i in range(len(parts) - 1):
        ss = [x for x in _sents(parts[i]) if x.strip()]
        if len(ss) >= 2:
            last = ss[-1]
            body = last.strip()
            if han(body) < 22 and ('部分' in body or body.rstrip('。').endswith('中')
                                   or body.rstrip('。').endswith('科')):
                parts[i] = ''.join(ss[:-1])
                parts[i + 1] = last + parts[i + 1]
    return parts


HDR = re.compile(r'(?:四分律行事鈔資持記[^ ]{0,12}\s*)?(?:\d+\s*)?釋[\u4e00-\u9fff]{1,6}篇(?:\([^)）]*\))?\s*')


def clean(t):
    head, rest = t[:80], t[80:]
    return HDR.sub('', head) + rest


def emit_ji_to(doc, tag, text, tr):
    r = doc.add_paragraph(); rf = r.paragraph_format
    rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
    rf.left_indent = Pt(14); rf.keep_with_next = True
    sr(r.add_run(tag + text), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
    b = doc.add_paragraph(); b.paragraph_format.first_line_indent = Pt(20)
    b.paragraph_format.left_indent = Pt(14)
    b.paragraph_format.line_spacing = 1.28; b.paragraph_format.space_after = Pt(2)
    sr(b.add_run(tr), 10)


def merge_qa8():
    o26, t26 = ZI[7][25]
    o27, t27 = ZI[7][26]
    k = o27.find('得法中')
    if k <= 0:
        return
    ZI[7][25] = (o26 + o27[:k], t26)
    # 譯文：找到「得法」相關句，切在句號後
    q = t27.find('得法')
    if q > 0:
        qe = t27.find('。', q)
        if qe > 0:
            ZI[7][25] = (o26 + o27[:k], t26 + t27[:qe + 1])
            ZI[7][26] = (o27[k:], t27[qe + 1:])
            return
    ZI[7][26] = (o27[k:], t27)


def move_siju():
    o49, t49 = ZI[3][48]
    o50, t50 = ZI[3][49]
    key = '四俱是，可知。'
    if o50.startswith(key):
        ZI[3][48] = (o49 + key, t49)
        ZI[3][49] = (o50[len(key):], t50)


def strip_dup_tail(p):
    if p != 8:
        return
    import re as _re
    o169, t169 = ZI[7][168]
    o170, t170 = ZI[7][169]
    # 找 o169 後綴與 o170 前綴的最長重疊
    best = 0
    for L in range(min(120, len(o169), len(o170)), 20, -1):
        if o169[-L:] == o170[:L]:
            best = L
            break
    if best >= 20:
        rest = o170[best:].lstrip('。；，')
        # 白話按比例切掉
        ratio = best / max(1, len(o170))
        cut = int(round(len(t170) * ratio))
        # 對到句號
        j = t170.find('。', cut)
        rest_t = t170[j + 1:] if j > 0 else t170
        ZI[7][169] = (rest, rest_t)


def build(p, splits):
    idx = p - 1
    sec = SECS[idx]; zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
    if p == 30:
        chao = chao[42:]
        am = [max(1, min(23, int(x) - 1)) if int(x) > 0 else 0 for x in am]
    by_c = {}
    BS = load_bounds(p)
    if BS:
        _last = 1
        _bs2 = []
        for _c, _n in BS:
            _n = max(_n, _last)
            _last = _n
            _bs2.append((_c, _n))
        BS = _bs2
        cmap = {}
        for i2, (c2, n2) in enumerate(BS):
            end2 = BS[i2 + 1][1] - 1 if i2 + 1 < len(BS) else len(zi)
            for n3 in range(n2, max(n2, end2) + 1):
                cmap[n3] = c2
        first_n = BS[0][1]
        fend = max([k + 1 for k in range(len(zi)) if k < len(am) and int(am[k]) == 0], default=0)
        for n3 in range(fend + 1, first_n):
            cmap[n3] = 1
        for n3 in range(1, len(zi) + 1):
            if n3 in cmap:
                by_c.setdefault(cmap[n3], []).append(n3 - 1)
    elif p == 10:
        # 篇10 的 c 是區塊粗標，改用 AI 切點推導逐記鈔號
        smap = {}
        for e in splits:
            smap[int(e['n'])] = e
        FORCED = {35: 5, 51: 13, 52: 15}
        cur = 1
        for n in range(1, len(zi) + 1):
            if n in FORCED:
                cur = FORCED[n]
            if n in smap:
                tg = [int(x) for x in smap[n]['targets']]
                for c in tg:
                    by_c.setdefault(c, []).append(n - 1)
                cur = tg[-1]
            else:
                by_c.setdefault(cur, []).append(n - 1)
    else:
        last = 0
        for k, c in enumerate(am[:len(zi)]):
            c = int(c)
            if c > 0:
                c = max(c, last)   # 強制單調
                last = c
                by_c.setdefault(c, []).append(k)
    front = [k for k in range(len(zi)) if k < len(am) and int(am[k]) == 0]

    # 切點
    pieces = {}
    used = set()
    # 整段搬移（manual: 只有 base、沒有 markers）
    for e in splits:
        if 'markers' not in e and 'base' in e:
            n0 = int(e['n'])
            for cc in list(by_c):
                if n0 - 1 in by_c[cc]:
                    by_c[cc].remove(n0 - 1)
            by_c.setdefault(int(e['base']), []).append(n0 - 1)
    PARTS = {}
    for e in splits:
        if 'markers' not in e:
            continue
        n = int(e['n']); marks = e['markers']; tg = [int(x) for x in e['targets']]
        base = (int(e['base']) if ('base' in e and p != 14) else (cmap.get(n, 0) if BS else (int(am[n - 1]) if n - 1 < len(am) else 0)))
        if p != 10 and not e.get('flex') and tg != list(range(base, base + len(tg))):
            continue
        if p == 10 and (tg != sorted(tg) or len(set(tg)) != len(tg)):
            continue
        # 尾片不得越過下一記段的鈔號，否則會造成記號逆序
        if p != 10 and (p == 14 or 'base' not in e) and not e.get('flex'):
            nxt = (cmap.get(n + 1, 0) if BS else (int(am[n]) if n < len(am) and int(am[n]) > 0 else 0)) or tg[-1]
            if tg[-1] > nxt:
                continue
        o, t = zi[n - 1]
        parts, cur, ok = [], o, True
        for m in marks:
            i = cur.find(m)
            if i <= 0:
                ok = False
                break
            parts.append(cur[:i]); cur = cur[i:]
        parts.append(cur)
        if not ok or len(parts) != len(tg):
            continue
        ts = split_tr(t, parts)
        PARTS[n] = len(tg)
        for idx2, (part, tr, c) in enumerate(zip(parts, ts, tg)):
            pieces.setdefault(c, []).append((n, idx2, part, tr))
            used.add(n)

    doc = Document()
    st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21); s.page_height = Cm(29.7)
    s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6); s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('四分律行事鈔・資持記　會本'), 18, bold=True)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('第%d篇　%s' % (p, sec['name'])), 11, color=RGBColor(0x66, 0x66, 0x66))

    def emit_ji_tagged(tag, zo, zt):
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run(tag + zo.rstrip('〕')), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
        _lead = ''
        _zt = clean_tr(zt)
        while _zt[:1] in ('〕', '」', '）'):
            _lead += _zt[0]
            _zt = _zt[1:]
        if _lead and doc.paragraphs:
            doc.paragraphs[-1].add_run(_lead)
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(_zt), 10)

    if p == 1:
        sp0 = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt0 = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read()) if x.strip()]
        bz = []
        bfp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_卷首.json')
        if os.path.exists(bfp):
            dd = json.load(io.open(bfp, encoding='utf-8-sig'))
            bz = sorted((int(x['c']), int(x['n'])) for x in dd.get('bounds', []))
        starts = {c: n for c, n in bz}
        if not starts:
            for k in front:
                emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])
            front = []
            starts = None
        cvals = [c for c, n in bz]
        ptr = 1
        for i, ct in enumerate(sp0):
            if starts is None:
                break
            cno = i + 1
            qq = doc.add_paragraph(); qf = qq.paragraph_format
            qf.space_before = Pt(6); qf.space_after = Pt(1); qf.line_spacing = 1.2; qf.keep_with_next = True
            sr(qq.add_run('【鈔首%02d】' % cno + ct), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
            if i < len(tt0):
                a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
                a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
                sr(a2.add_run(clean_tr(tt0[i])), 10.5)
            if cno in starts:
                ptr = starts[cno]
            # 下一個 c 的起點
            nxts = [starts[x] for x in cvals if x > cno]
            nxt = min(nxts) if nxts else len(zi) + 1
            nxt = max(nxt, ptr)
            nxt = min(nxt, len(front) + 1 if front else 224)
            for k in range(ptr - 1, min(nxt - 1, len(zi))):
                emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])
            ptr = nxt
        front = []

    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)
        sr(q.add_run('〔篇前總釋〕'), 11, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
        for k in front:
            emit_ji_tagged('【記%03d】' % (k + 1), clean(zi[k][0]), zi[k][1])

    if p == 10:
        nq = doc.add_paragraph(); nq.paragraph_format.left_indent = Pt(14)
        nq.paragraph_format.space_before = Pt(6)
        sr(nq.add_run('〔編者按：記003–008 係元照釋篇首原注（布薩譯名）之文；此段原注諸本多脫，CBETA T40n1804 亦無，故暫無鈔文可配，待補底本。〕'), 9, color=RGBColor(0x88, 0x66, 0x33))

    EMIT = set()
    for cno, it in enumerate(chao, 1):
        qq = doc.add_paragraph(); qf = qq.paragraph_format
        qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
        sr(qq.add_run('【鈔%02d】' % cno + it[0]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
        a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
        a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
        sr(a2.add_run(it[1]), 10.5)
        # 合併切點片段與整段，按記號排序
        rows = [(n, idx2, part, tr) for n, idx2, part, tr in pieces.get(cno, [])]
        for k in by_c.get(cno, []):
            if k + 1 not in used:
                rows.append((k + 1, 0, zi[k][0], zi[k][1]))
                used.add(k + 1)
        for n, idx2, part, tr in sorted(rows, key=lambda x: (x[0], x[1])):
            if (n, idx2) in EMIT:
                continue
            EMIT.add((n, idx2))
            tot = PARTS.get(n, 1)
            if tot > 1:
                sub = ['前半', '後半'] if tot == 2 else (['前', '中', '後'] if tot == 3 else ['一', '二', '三', '四', '五'][:tot])
                tag = '【記%03d】（%s）' % (n, sub[idx2] if idx2 < len(sub) else str(idx2 + 1))
            else:
                tag = '【記%03d】' % n
            emit_ji_tagged(tag, clean(part), tr)

    out = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p, sec['name']))
    doc.save(out)
    return out, len(chao), len(zi), len(used)


if __name__ == '__main__':
    pians = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 7, 8, 9, 10]
    for p in pians:
        sp = os.path.join(SO, 'split_篇%02d.json' % p)
        splits = []
        if os.path.exists(sp):
            d = json.load(io.open(sp, encoding='utf-8-sig'))
            splits = d.get('splits', [])
        mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
        if os.path.exists(mp):
            dm = json.load(io.open(mp, encoding='utf-8-sig'))
            man = dm.get('splits', [])
            mn = {int(x['n']) for x in man}
            splits = man + [x for x in splits if int(x['n']) not in mn]
        merge_qa8()
        move_siju()
        strip_dup_tail(p)
        out, nc, nz, used = build(p, splits)
        print('篇%02d %-8s 鈔%3d 記%3d 切點%2d → %s' % (p, SECS[p - 1]['name'], nc, nz, len(splits), os.path.basename(out)))
    # 各篇首記的前篇尾巴 → 補到前一篇
    for p, (head, htr) in HEADS.items():
        if '釋結界篇' in head or '資持記上二' in head:
            continue
        fp = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p - 1, SECS[p - 2]['name']))
        if not os.path.exists(fp):
            continue
        d = Document(fp)
        probe = ''.join(head.split())[:16]
        exist = any(probe and probe in ''.join(x.text.split()) for x in d.paragraphs)
        if exist:
            continue
        emit_ji_to(d, '【記%03d】（接前文）' % (len(ZI[p - 2]) + 1), head, htr)
        d.save(fp)
        print('  已補前篇尾巴到 篇%02d' % (p - 1))
