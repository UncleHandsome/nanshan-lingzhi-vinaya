# -*- coding: utf-8 -*-
"""第2篇（集僧通局）精簡版 Word／PDF：只留原文與最終白話。"""
import glob
import html
import io
import json
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '重審_行事鈔_3K_20261126', '第2篇_集僧通局_分段', 'ooo.txt')
OUT_DOCX = os.path.join(B, '重審_行事鈔_3K_20261126', '第2篇_集僧通局_原文與最終白話.docx')
KAI = 'DFKai-SB'
HEI = 'Microsoft JhengHei'
INK = RGBColor(0x1F, 0x1B, 0x16)
BROWN = RGBColor(0x8B, 0x5E, 0x3C)
BLUE = RGBColor(0x1F, 0x4E, 0x6B)
GRAY = RGBColor(0x6B, 0x63, 0x57)
LBL = re.compile(r'^\s*(?:【(?:疏文|記文|鈔文|律文|註文|序文)】\s*)+')

rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', 'xingshichao.jsonl'), encoding='utf-8') if x.strip()]
seg = {}
for r in rows:
    segs = r.get('segments') or []
    for si, s in enumerate(segs, 1):
        key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
        seg[key] = {'vol': r.get('vol') or '',
                    'src': LBL.sub('', (s.get('display_source') or s.get('source') or '').strip()).strip(),
                    'tr': LBL.sub('', (s.get('translation') or '').strip()).strip()}
key2sec = {}
for p in sorted(glob.glob(os.path.join(B, 'docs', 'xingshichao', '*__p*.html'))):
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'<h2 class="sec"[^>]*>([^<]*)</h2>', t)
    sec = html.unescape(m.group(1)) if m else ''
    for k in re.findall(r'<div class="pair[^"]*" id="u([^"]+)"', t):
        key2sec[k] = sec
ORDER = [k for k in seg if key2sec.get(k) == '第2篇　集僧通局']

raw = io.open(SRC, encoding='utf-8').read()
idx = [m.start() for m in re.finditer(r'(?m)^#*\s*（一）考據初檢', raw)]
idx.append(len(raw))
replies = {}
for i in range(len(idx) - 1):
    ch = raw[idx[i]:idx[i + 1]]
    m = re.search(r'"key"\s*:\s*"([^"]+)"', ch)
    if not m:
        continue
    mm = re.search(r'<<<JSONL_START>>>(.*?)<<<JSONL_END>>>', ch, re.S)
    if not mm:
        continue
    data = json.loads(mm.group(1).strip().splitlines()[0])
    replies[m.group(1)] = data


def han(x):
    return len(re.findall(r'[\u4e00-\u9fff]', x or ''))


doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(1.8)


def set_run(run, text, font, size, bold=False, color=INK, italic=False):
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), font)


def para(doc, sb=0, sa=0, line=1.3, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing = line
    p.alignment = align
    return p


def body(doc, label, color, text, size=14):
    p = para(doc, sb=5, sa=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next = True
    set_run(p.add_run(), label, HEI, 12.5, True, color)
    for line in text.split('\n'):
        if not line.strip():
            continue
        p = para(doc, sa=0, line=1.4)
        set_run(p.add_run(), line.strip(), KAI, size)


def footer(doc):
    for s in doc.sections:
        f = s.footer.paragraphs[0]
        f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(f.add_run(), '行事鈔第2篇集僧通局・原文與最終白話　第 ', HEI, 9, color=GRAY)
        fld = OxmlElement('w:fldSimple')
        fld.set(qn('w:instr'), 'PAGE')
        f._p.append(fld)
        set_run(f.add_run(), ' 頁', HEI, 9, color=GRAY)


p = para(doc, sb=90, sa=6, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '四分律刪繁補闕行事鈔', KAI, 24, True, BROWN)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '卷上・第2篇 集僧通局', KAI, 18, True, INK)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '原文與最終白話', KAI, 17, True, INK)
p = para(doc, sa=20, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '共 37 段・標楷體 14pt', HEI, 11, color=GRAY)
doc.add_page_break()

n = 0
OVERRIDE = {'114-2', '114-4', '114-5', 'GAP02-2', 'GAP02-3', 'GAP02-6', '120',
            '124', '127-3', '129', '131', '133', '137'}
for i, key in enumerate(ORDER, 1):
    data = replies.get(key)
    if not data:
        continue
    n += 1
    o = seg[key]
    status = data.get('status')
    final = (data.get('translation') or '').strip()
    final = LBL.sub('', final).strip()
    if key in OVERRIDE:
        final = o['tr']
    if not final:
        final = o['tr']
    p = para(doc, sa=2, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '%d. ' % i, HEI, 16, True, BROWN)
    set_run(p.add_run(), '%s・%s（key %s）' % (o['vol'], key2sec.get(key, ''), key),
            HEI, 15, True, INK)
    body(doc, '原文', BROWN, '【鈔文】\n' + o['src'])
    body(doc, '最終白話', BLUE, '【鈔文】\n' + final)
    doc.add_page_break()

footer(doc)
doc.save(OUT_DOCX)
print('saved', OUT_DOCX, '| 段數', n)
