# -*- coding: utf-8 -*-
"""行事鈔×資持記 篇級合編（v3：以記文「釋X篇」標記切篇，不再靠篇名對照或引文定位）。

舊版 hebian.py 用篇名對照（MAP），記文名稱對不上時整篇記文會漏排
（受戒、瞻病、諸雜、尼眾四篇）。v3 直接找記文的「釋X篇」標記，
依位置切分後按序歸篇，並印出每篇的記段數供核對。
"""
import io, os, re, bisect
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
FONT = 'DFKai-SB'
LATIN = 'Times New Roman'
MARK = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')

MAP = [('標宗顯德', '點明宗旨'), ('集僧通局', '集僧'), ('足數眾相', '足數'), ('受欲是非', '受欲'), ('通辨羯磨', '羯磨'),
       ('結界方法', '結界'), ('僧網大綱', '僧網'), ('受戒緣集', '受戒'), ('師資相攝', '師資'), ('說戒正儀', '說戒'),
       ('安居策修', '安居'), ('自恣宗要', '自恣'), ('篇聚名報', '篇聚'), ('隨戒釋相', '戒相'), ('持犯方軌', '持犯'),
       ('懺六聚法', '懺六聚法'), ('二衣總別', '二衣'), ('四藥受淨', '四藥'), ('鉢器制聽', '鉢器'), ('對施興治', '對施'),
       ('頭陀行儀', '頭陀'), ('僧像致敬', '僧像致敬'), ('訃請設則', '赴請'), ('導俗化方', '導俗'), ('主客相待', '主客'),
       ('瞻病送終', '瞻病'), ('諸雜要行', '諸雜'), ('沙彌別法', '沙彌'), ('尼眾別行', '尼眾'), ('諸部別行', '諸部律')]


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


han = lambda s: ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


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


# 鈔：切篇（只取 30 篇，依「第N」序號去重）
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def cn_num(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十')
        return CN.get(a, 0) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s, 0)


cs_sec = []
cur = None
for key, sp, tp in load('01_行事鈔', '01_行事鈔'):
    for i in range(min(len(sp), len(tp))):
        if re.match(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$', sp[i].strip()):
            continue                      # 卷次標題行，略過
        m = re.match(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$', sp[i])
        if m and cn_num(m.group(2)) == len(cs_sec) + 1:
            cur = dict(name=m.group(1), items=[])
            cs_sec.append(cur)
        elif cur is not None:
            cur['items'].append((sp[i], tp[i]))
print('鈔篇', len(cs_sec))

# 記：全部段落 + 位置
zj = []
ztext = ''
starts = []
for key, sp, tp in load('資持記_細分', '資持記'):
    for i in range(min(len(sp), len(tp))):
        starts.append(len(ztext))
        ztext += han(sp[i])
        zj.append((sp[i], tp[i]))
print('記段', len(zj), '記字數', len(ztext))

# 找「釋X篇」標記
marks = []          # (pos, name, item_index)
for k, (o, t) in enumerate(zj):
    m = MARK.search(t) or MARK.search(o)
    if m:
        marks.append((starts[k], m.group(1), k))
print('標記', len(marks), [m[1] for m in marks])

name2idx = {z[1]: i for i, z in enumerate(MAP)}
assign = {i: [] for i in range(len(cs_sec))}
cur_idx = 0
seq = []
for pos, name, k in marks:
    idx = name2idx.get(name)
    if idx is None:
        print('  ?? 未知記名', name)
        continue
    seq.append((pos, idx, k, name))
seq.sort()
# 依序歸篇：從 marker 起到下個 marker 前的記段
bounds = [(pos, idx) for pos, idx, k, name in seq]
# 標記之前的記文屬卷首（序、目錄等），合編只收 30 篇，故不併入篇1
for j, (pos, idx) in enumerate(bounds):
    lo = pos
    hi = bounds[j + 1][0] if j + 1 < len(bounds) else len(ztext)
    for k, p in enumerate(starts):
        if lo <= p < hi:
            assign[idx].append(zj[k])
print('每篇記段數', [len(assign[i]) for i in range(len(cs_sec))])
missing = [i + 1 for i in range(len(cs_sec)) if not assign[i]]
if missing:
    print('!! 這些篇沒有記文:', missing)


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
            a.alignment = WD_ALIGN_PARAGRAPH.LEFT
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
                a.alignment = WD_ALIGN_PARAGRAPH.LEFT
                af = a.paragraph_format
                af.first_line_indent = Pt(22)
                af.line_spacing = 1.4
                af.space_before = Pt(1)
                af.space_after = Pt(4)
                set_run(a.add_run(t), 11)
    out = os.path.join(D, '白話', '行事鈔資持記合編_%s.docx' % vol_name)
    doc.save(out)
    print(vol_name, 'saved', len(doc.paragraphs), 'paras')


# 四冊：依《資持記》原書 16 卷，每 4 卷為一冊（卷一～卷四）。
# 依記文卷次換算到鈔篇的界線為：卷5→篇10（說戒）、卷9→篇14（戒相）、卷13→篇17（二衣）。
VOLS = [('卷一', 1, 9), ('卷二', 10, 13), ('卷三', 14, 16), ('卷四', 17, 30)]
for name, a, b in VOLS:
    build(name, a, b)
