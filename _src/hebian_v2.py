# -*- coding: utf-8 -*-
"""行事鈔×資持記 篇級合編（v2：記文改以「鈔篇定位」歸篇，不再靠篇名對照）。

原 hebian.py 用篇名對照（MAP），記文分段名稱對不上時整篇記文會漏掉
（受戒、瞻病、諸雜、尼眾四篇）。本版改為：
  1. 依序把 30 篇鈔文的開頭特徵句，定位到記文原文流中的位置；
  2. 以相鄰定位點切分記文，落在區間內的記段即屬該篇；
  3. 定位失敗者沿用前一篇的結束點（該篇暫無記文，並印出警告）。
"""
import io, os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
FONT = 'DFKai-SB'
LATIN = 'Times New Roman'


def cn(n):
    d = '〇一二三四五六七八九'
    if n < 10:
        return d[n]
    if n < 20:
        return '十' + (d[n % 10] if n % 10 else '')
    return d[n // 10] + '十' + (d[n % 10] if n % 10 else '')


def set_run(r, size, bold=False, color=None):
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = LATIN
    rPr = r._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    rf.set(qn('w:ascii'), LATIN)
    rf.set(qn('w:hAnsi'), LATIN)
    rf.set(qn('w:eastAsia'), FONT)
    if color is not None:
        r.font.color.rgb = color


def shade(p, c):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), c)
    pPr.append(shd)


def han(s):
    return ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


def load(src, tr):
    S = os.path.join(D, 'TXT_分卷', src)
    T = os.path.join(D, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        tp = os.path.join(T, key + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tt))
    return out


# 鈔：切篇
cs = load('01_行事鈔', '01_行事鈔')
cs_sec = []
seen = set()
cur = None
for key, sp, tp in cs:
    for i in range(min(len(sp), len(tp))):
        m = re.match(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$', sp[i])
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            cur = dict(name=m.group(1), items=[(sp[i], tp[i])])
            cs_sec.append(cur)
        elif cur is not None:
            cur['items'].append((sp[i], tp[i]))
print('鈔篇', len(cs_sec))

# 記：所有段落依序（不再按篇名切）
zj_items = []
for key, sp, tp in load('資持記_細分', '資持記'):
    for i in range(min(len(sp), len(tp))):
        zj_items.append((sp[i], tp[i]))
print('記段', len(zj_items))

zh = [han(o) for o, t in zj_items]
zstarts = []
off = 0
for h in zh:
    zstarts.append(off)
    off += len(h)
ztext = ''.join(zh)
print('記文字數', len(ztext))


def probe_of(items, n=36):
    """取一篇開頭的特徵句（去掉標點後前 n 字，太短就接下一段）。"""
    buf = ''
    for o, t in items[:4]:
        buf += han(o)
        if len(buf) >= n:
            break
    return buf[:n] if len(buf) >= n else buf


# 依序定位每篇在記文中的起點
starts = []
last = 0
for idx, sec in enumerate(cs_sec):
    p = probe_of(sec['items'])
    pos = -1
    for cut in (36, 28, 20, 14):
        q = ztext.find(p[:cut], last)
        if q >= 0:
            pos = q
            break
    if pos < 0:
        # 用篇名再試一次
        q = ztext.find(han(sec['name']), last)
        if q >= 0:
            pos = q
    if pos < 0:
        print('  !! 無法定位 第%d篇 %s，記文留空' % (idx + 1, sec['name']))
        starts.append(None)
    else:
        starts.append(pos)
        last = pos
print('定位', sum(1 for s in starts if s is not None), '/', len(starts))

# 記段 → 篇
import bisect
valid = [(s, i) for i, s in enumerate(starts) if s is not None]
valid.sort()
sec_start = [s for s, i in valid]
sec_idx = [i for s, i in valid]
assign = {i: [] for i in range(len(cs_sec))}
for k, (o, t) in enumerate(zj_items):
    pos = zstarts[k]
    j = bisect.bisect_right(sec_start, pos) - 1
    if j < 0:
        continue
    assign[sec_idx[j]].append((o, t))
print('每篇記段數', [len(assign[i]) for i in range(len(cs_sec))])


def build(vol_name, n_from, n_to):
    doc = Document()
    st = doc.styles['Normal']
    st.font.size = Pt(11)
    st.font.name = LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(1.7)
    s.bottom_margin = Cm(1.6)
    s.left_margin = Cm(1.8)
    s.right_margin = Cm(1.8)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('四分律行事鈔資持記合編'), 20, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(16)
    set_run(p.add_run(vol_name + '（鈔文・記文對照）'), 12, color=RGBColor(0x66, 0x66, 0x66))
    for idx in range(n_from - 1, min(n_to, len(cs_sec))):
        sec = cs_sec[idx]
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(18)
        pf.space_after = Pt(4)
        pf.page_break_before = (idx > n_from - 1)
        set_run(p.add_run('第%s篇　%s' % (cn(idx + 1), sec['name'])), 15, bold=True)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        set_run(p.add_run('【鈔】'), 10, bold=True, color=RGBColor(0x8a, 0x4a, 0x1f))
        for o, t in sec['items']:
            q = doc.add_paragraph()
            qf = q.paragraph_format
            qf.left_indent = Pt(6)
            qf.space_before = Pt(4)
            qf.space_after = Pt(0)
            qf.line_spacing = 1.25
            qf.keep_with_next = True
            set_run(q.add_run(o), 10, color=RGBColor(0x6b, 0x5b, 0x4a))
            shade(q, 'F4EFE2')
            a = doc.add_paragraph()
            a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            af = a.paragraph_format
            af.first_line_indent = Pt(22)
            af.line_spacing = 1.4
            af.space_before = Pt(1)
            af.space_after = Pt(4)
            set_run(a.add_run(t), 11)
        items = assign[idx]
        if items:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            set_run(p.add_run('【記】　' + sec['name'] + '篇'), 10, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
            for o, t in items:
                q = doc.add_paragraph()
                qf = q.paragraph_format
                qf.left_indent = Pt(6)
                qf.space_before = Pt(4)
                qf.space_after = Pt(0)
                qf.line_spacing = 1.25
                qf.keep_with_next = True
                set_run(q.add_run(o), 10, color=RGBColor(0x6b, 0x5b, 0x4a))
                shade(q, 'EEF2F6')
                a = doc.add_paragraph()
                a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format
                af.first_line_indent = Pt(22)
                af.line_spacing = 1.4
                af.space_before = Pt(1)
                af.space_after = Pt(4)
                set_run(a.add_run(t), 11)
    out = os.path.join(D, '白話', '行事鈔資持記合編_%s.docx' % vol_name)
    doc.save(out)
    print(vol_name, 'saved', len(doc.paragraphs), 'paras')


build('上卷', 1, 12)
build('中卷', 13, 16)
build('下卷', 17, 30)
