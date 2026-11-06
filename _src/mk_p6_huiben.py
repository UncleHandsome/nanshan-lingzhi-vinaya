# -*- coding: utf-8 -*-
"""篇6 完整會本：記文按牒詞切段，重排到所釋鈔文之後"""
import io, os, re, json, sys, importlib.util
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
idx = 5
sec = SECS[idx]; zi = ZI[idx]
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))

# 切點（牒詞）——依使用者提供的義理對應表
MARK = {
    10: ['作法中二'],
    16: ['大界中'],
    22: ['三小界'],
    24: ['依位解者'],
    47: ['唱相，離過'],
    26: ['次問中'],
    27: ['三問'],
    29: ['四問中'],
    31: ['五問中'],
    33: ['第六問'],
    44: ['界形文略'],
    49: ['內唱中'],
    50: ['蘭若中'],
    52: ['定初始中'],
    53: ['空野唱中'],
    55: ['次科。五門三門者', '集僧中'],
    58: ['尼界者', '僧界中', '不受欲中'],
    61: ['白羯磨中'],
    65: ['注中'],
    67: ['戒場中'],
    68: ['結示中', '結法中'],
    73: ['結場中'],
    74: ['唱相中'],
    76: ['羯磨中', '三小中'],
    81: ['界外問難'],
    83: ['指結法中'],
    85: ['解中'],
    86: ['次有場中'],
    88: ['今準相翻', '雜相中', '三法起中'],
    94: ['第四明非法中'],
    95: ['棄捨失中'],
    98: ['不失中'],
}

# 每條鈔分配到的記（part 為 0 起的分段序號）
PLAN = {
    1: [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
    2: [(8, 0)],
    3: [(9, 0), (10, 0)],
    4: [(10, 1), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0)],
    5: [(16, 1), (17, 0), (18, 0), (19, 0), (20, 0)],
    6: [(21, 0), (22, 0)],
    7: [(22, 1), (23, 0), (24, 0)],
    8: [(24, 1)],
    9: [(25, 0), (26, 0)],
    10: [(26, 1), (27, 0)],
    11: [(27, 1), (28, 0), (29, 0)],
    12: [(29, 1), (30, 0), (31, 0)],
    13: [(31, 1), (32, 0), (33, 0)],
    14: [(33, 1), (34, 0), (35, 0), (36, 0), (37, 0)],
    15: [(38, 0), (39, 0), (40, 0), (41, 0), (42, 0), (43, 0), (44, 0)],
    16: [(44, 1), (45, 0), (46, 0), (47, 0)],
    17: [(47, 1), (48, 0), (49, 0)],
    18: [(49, 1), (50, 0)],
    19: [(50, 1), (51, 0)],
    20: [(52, 0)],
    21: [(52, 1), (53, 0)],
    22: [(53, 1)],
    23: [(54, 0), (55, 0)],
    24: [(55, 1)],
    25: [(55, 2), (56, 0)],
    26: [(57, 0), (58, 0)],
    27: [(58, 1)],
    28: [(58, 2)],
    29: [(58, 3), (59, 0), (60, 0)],
    30: [(61, 0)],
    31: [(61, 1), (62, 0), (63, 0), (64, 0), (65, 0)],
    32: [(65, 1), (66, 0)],
    33: [(67, 0)],
    34: [(67, 1)],
    35: [(68, 0)],
    36: [(68, 1)],
    37: [(68, 2), (69, 0), (70, 0), (71, 0), (72, 0), (73, 0)],
    38: [(73, 1), (74, 0)],
    39: [(74, 1)],
    40: [(75, 0), (76, 0)],
    41: [(76, 1)],
    42: [(76, 2), (77, 0)],
    43: [(78, 0), (79, 0), (80, 0), (81, 0)],
    44: [(81, 1), (82, 0)],
    45: [(83, 0)],
    46: [(83, 1)],
    47: [(84, 0), (85, 0)],
    48: [(85, 1), (86, 0)],
    49: [(86, 1), (87, 0), (88, 0)],
    50: [(88, 1)],
    51: [(88, 2)],
    52: [(88, 3), (89, 0), (90, 0), (91, 0), (92, 0), (93, 0), (94, 0)],
    53: [(94, 1), (95, 0)],
    54: [(95, 1), (96, 0), (97, 0), (98, 0)],
    55: [(98, 1), (99, 0), (100, 0)],
}


def split_para(text, marks):
    """依序在 marks 出現處切段，回傳 len(marks)+1 段"""
    parts, cur = [], text
    for m in marks:
        i = cur.find(m)
        if i <= 0:
            parts.append(cur)
            cur = ''
            continue
        parts.append(cur[:i])
        cur = cur[i:]
    parts.append(cur)
    return parts


def split_tr(tr, weights):
    """白話按比例在句號處切"""
    sents = re.findall(r'[^。！？]*[。！？]?', tr)
    sents = [s for s in sents if s]
    total = sum(han(s) for s in sents) or 1
    out, cur, acc, k = [], [], 0, 0
    targets = []
    run = 0
    for w in weights[:-1]:
        run += w
        targets.append(run)
    for s in sents:
        cur.append(s)
        acc += han(s)
        if k < len(targets) and acc >= targets[k]:
            out.append(''.join(cur)); cur = []; k += 1
    out.append(''.join(cur))
    while len(out) < len(weights):
        out.append('')
    return out


# 切好所有記段
pieces = {}
miss = []
for n in range(1, len(zi) + 1):
    o, t = zi[n - 1]
    if n in MARK:
        ps = split_para(o, MARK[n])
        if len(ps) != len(MARK[n]) + 1 or any(not p.strip() for p in ps):
            miss.append(n)
            pieces[n] = [(o, t)]
            continue
        w = [han(p) for p in ps]
        ts = split_tr(t, w)
        pieces[n] = list(zip(ps, ts))
    else:
        pieces[n] = [(o, t)]
print('切段失敗', miss)

used = set()
FONT = 'SimSun'; LATIN = 'Times New Roman'
def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color: run.font.color.rgb = color
def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)

doc = Document()
st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
s = doc.sections[0]
s.page_width = Cm(21); s.page_height = Cm(29.7)
s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6); s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('四分律行事鈔・資持記　會本'), 18, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('第6篇　結界方法（記文依牒詞切段，隨鈔排列）'), 10.5, color=RGBColor(0x66, 0x66, 0x66))

for cno, it in enumerate(chao, 1):
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(9); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
    sr(q.add_run('【鈔%02d】' % cno + it[0]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')
    a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
    a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
    sr(a2.add_run(it[1]), 10.5)
    for (n, part) in PLAN.get(cno, []):
        seq = pieces.get(n, [])
        if part >= len(seq):
            continue
        zo, zt = seq[part]
        used.add(n)
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        tag = '【記%03d】' % n + ('（後半）' if part else '') if len(seq) > 1 else '【記%03d】' % n
        sr(r.add_run(tag + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(zt), 10)

out = os.path.join(B, '白話', '會本_篇6結界方法.docx')
doc.save(out)
missed = [n for n in range(1, len(zi) + 1) if n not in used]
print('未排入的記段', missed)
print('saved', out, '段落', len(doc.paragraphs))
