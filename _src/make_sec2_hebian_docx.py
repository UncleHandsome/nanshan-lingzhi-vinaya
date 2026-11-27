# -*- coding: utf-8 -*-
"""合編本 Word（依合編頁對位：鈔文／記文兩欄，原文＋白話）。
用法：--page docs/hebian/卷上之一__p2.html --title "卷上之一・第2篇 集僧通局" --out 路徑.docx
"""
import argparse
import html as H
import io
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ap = argparse.ArgumentParser()
ap.add_argument('--page', default='docs/hebian/卷上之一__p2.html')
ap.add_argument('--title', default='卷上之一・第2篇 集僧通局')
ap.add_argument('--out', default='重審_行事鈔_3K_20261126/第2篇_集僧通局_合編本_原文與最終白話.docx')
A = ap.parse_args()
PAGE = A.page if os.path.isabs(A.page) else os.path.join(B, A.page)
OUT = A.out if os.path.isabs(A.out) else os.path.join(B, A.out)
TITLE = A.title
FONT = 'DFKai-SB'
HEI = 'Microsoft JhengHei'
SRC_COLOR = RGBColor(0x6B, 0x5B, 0x4A)
TR_COLOR = RGBColor(0x1F, 0x1B, 0x16)
INK = RGBColor(0x1F, 0x1B, 0x16)
BROWN = RGBColor(0x8B, 0x5E, 0x3C)
GRAY = RGBColor(0x6B, 0x63, 0x57)
BODY = 14

t = io.open(PAGE, encoding='utf-8').read()
main = re.search(r'<main[^>]*>(.*?)</main>', t, re.S).group(1)
BLOCK = re.compile(
    r'<div class="pair (c|j)[^"]*" id="u([cj])-([^"]+)">'
    r'<div class="(o|o2)">(.*?)</div><div class="t">(.*?)</div></div>', re.S)


def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = H.unescape(s)
    s = re.sub(r'^\s*【[^】]+】\s*', '', s)
    return s.strip()


items = []
cur = None
for m in BLOCK.finditer(main):
    kind, _k2, key, _oc, o, tr = m.groups()
    src, trn = clean(o), clean(tr)
    if kind == 'c':
        cur = {'ck': key, 'src': src, 'tr': trn, 'ji': []}
        items.append(cur)
    elif cur is not None:
        cur['ji'].append((key, src, trn))
n_c = sum(1 for x in items if x['src'])
n_j = sum(len(x['ji']) for x in items)
print('groups', len(items), '| 鈔', n_c, '| 記', n_j)

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.5)
sec.bottom_margin = Cm(1.4)
sec.left_margin = Cm(1.5)
sec.right_margin = Cm(1.5)


def set_run(run, text, size=BODY, bold=False, color=INK, font=FONT):
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), font)


def para(container, sb=0, sa=0, line=1.25, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = container.add_paragraph()
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing = line
    p.alignment = align
    return p


def add_texts(cell, src, tr, label_color=RGBColor(0x1F, 0x4E, 0x6B)):
    p = para(cell, sb=1, sa=0, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(), '原文', 10.5, True, BROWN, HEI)
    for line in src.split('\n'):
        if line.strip():
            p = para(cell, sa=0, line=1.25)
            set_run(p.add_run(), line.strip(), BODY, False, SRC_COLOR)
    p = para(cell, sb=4, sa=0, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(), '白話', 10.5, True, label_color, HEI)
    for line in tr.split('\n'):
        if line.strip():
            p = para(cell, sa=0, line=1.25)
            set_run(p.add_run(), line.strip(), BODY, False, TR_COLOR)


# 封面
p = para(doc, sb=80, sa=6, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '四分律行事鈔資持記', 24, True, BROWN)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '句級合編本', 20, True, INK)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), TITLE, 18, True, INK)
p = para(doc, sa=16, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '原文與最終白話', 16, True, INK)
for line in ('鈔文 %d 段、記文 %d 段並列' % (n_c, n_j),
             '左欄鈔文（行事鈔）、右欄記文（資持記）',
             '標楷體 14pt；對位依合編頁（允許一對多）'):
    p = para(doc, sa=2, line=1.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(), '· ' + line, 11, False, GRAY, HEI)
doc.add_page_break()

for i, it in enumerate(items, 1):
    rows = it['ji'] or [(None, '', '')]
    tbl = doc.add_table(rows=len(rows), cols=2)
    tbl.autofit = False
    tbl.columns[0].width = Cm(7.2)
    tbl.columns[1].width = Cm(10.8)
    for ri, (jk, jsrc, jtr) in enumerate(rows):
        row = tbl.rows[ri]
        left, right = row.cells[0], row.cells[1]
        left.width = Cm(7.2)
        right.width = Cm(10.8)
        if ri == 0:
            p = para(left, sb=1, sa=2, line=1.1, align=WD_ALIGN_PARAGRAPH.LEFT)
            set_run(p.add_run(), '%d. 鈔文 key %s' % (i, it['ck']), 10.5, True, GRAY, HEI)
            add_texts(left, it['src'], it['tr'])
        if jsrc.strip():
            add_texts(right, jsrc, jtr, RGBColor(0x2E, 0x5E, 0x46))
            p = para(right, sa=0, line=1.0, align=WD_ALIGN_PARAGRAPH.RIGHT)
            set_run(p.add_run(), '記文 key %s' % jk, 8.5, False, GRAY, HEI)
        else:
            p = para(right, sa=0)
            set_run(p.add_run(), '（無對應記文）', BODY, False, GRAY)

for s in doc.sections:
    f = s.footer.paragraphs[0]
    f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(f.add_run(), '行事鈔資持記・句級合編　%s　第 ' % TITLE, 9, False, GRAY, HEI)
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    f._p.append(fld)
    set_run(f.add_run(), ' 頁', 9, False, GRAY, HEI)

doc.save(OUT)
print('saved', OUT)
