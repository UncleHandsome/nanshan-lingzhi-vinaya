# -*- coding: utf-8 -*-
"""把「抽樣十段」整理成一份 Word：每段 原文 → 白話 → AI 回覆框。

輸出：重審_行事鈔_3K_20261126/抽樣十段_原文白話_AI回覆.docx
"""
import glob
import html
import io
import json
import os
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DIR = os.path.join(B, '重審_行事鈔_3K_20261126', '抽樣十段')
OUT = os.path.join(B, '重審_行事鈔_3K_20261126', '抽樣十段_原文白話_AI回覆.docx')
KAI = 'DFKai-SB'
HEI = 'Microsoft JhengHei'
INK = RGBColor(0x1F, 0x1B, 0x16)
BROWN = RGBColor(0x8B, 0x5E, 0x3C)
BLUE = RGBColor(0x1F, 0x4E, 0x6B)
GRAY = RGBColor(0x6B, 0x63, 0x57)

rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', 'xingshichao.jsonl'), encoding='utf-8') if x.strip()]
seg = {}
for r in rows:
    segs = r.get('segments') or []
    for si, s in enumerate(segs, 1):
        key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
        seg[key] = {'vol': r.get('vol') or '', 'tr': (s.get('translation') or '')}

key2sec = {}
for p in sorted(glob.glob(os.path.join(B, 'docs', 'xingshichao', '*__p*.html'))):
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'<h2 class="sec"[^>]*>([^<]*)</h2>', t)
    sec = html.unescape(m.group(1)) if m else ''
    for k in re.findall(r'<div class="pair[^"]*" id="u([^"]+)"', t):
        key2sec[k] = sec


def han(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s or ''))


def set_run(run, text, font, size, bold=False, color=INK, italic=False):
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rPr.rFonts.set(qn('w:eastAsia'), font)
    return run


def para(doc, space_before=0, space_after=0, line=1.3, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    p.alignment = align
    return p


def borders(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement('w:' + side)
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '6')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), 'C9BFA8')
        borders.append(el)
    tcPr.append(borders)


def footer(doc):
    for sec in doc.sections:
        f = sec.footer.paragraphs[0]
        f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(f.add_run(), '行事鈔代表性十段・校閱用', HEI, 9, color=GRAY)
        set_run(f.add_run(), '　第 ', HEI, 9, color=GRAY)
        r = f.add_run()
        fld = OxmlElement('w:fldSimple')
        fld.set(qn('w:instr'), 'PAGE')
        f._p.append(fld)
        set_run(f.add_run(), ' 頁', HEI, 9, color=GRAY)


doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.2)
sec.right_margin = Cm(2.0)

# 封面
p = para(doc, space_before=60, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '四分律刪繁補闕行事鈔', KAI, 24, True, BROWN)
p = para(doc, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '代表性十段：原文／白話／AI 回覆', KAI, 17, True, INK)
p = para(doc, space_after=24, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '南山律典白話對照・校閱工作本', HEI, 11, color=GRAY)
for txt in ('來源：定稿 xingshichao.jsonl（3,042 段中選 10 段）',
            '每段原文均超過 200 字，涵蓋卷上、卷中、卷下共 10 個篇',
            '使用方式：把 AI 回覆貼進每段下方的「AI 回覆」框內',
            '提示詞全文附於最後一頁，可直接複製'):
    p = para(doc, space_after=2, line=1.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(), '· ' + txt, HEI, 10.5, color=GRAY)
doc.add_page_break()

files = sorted(p for p in glob.glob(os.path.join(DIR, '*.md')) if os.path.basename(p)[0].isdigit())
entries = []
for pth in files:
    t = io.open(pth, encoding='utf-8').read()
    m = re.search(r'## 行事鈔／([^\n]+)\n.*?### 原文\n+【[^】]+】\n(.*?)\n\n### 白話\n+【[^】]+】\n(.*?)\s*$', t, re.S)
    key, src, tr = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    entries.append((key, src, tr))

for i, (key, src, tr) in enumerate(entries, 1):
    vol = seg.get(key, {}).get('vol', '')
    p = para(doc, space_before=0, space_after=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '%d. ' % i, HEI, 13, True, BROWN)
    set_run(p.add_run(), '%s・%s' % (vol, key2sec.get(key, '')),
            HEI, 13, True, INK)
    p = para(doc, space_after=3, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), 'key %s　原文 %d 字　白話 %d 字' % (key, han(src), han(tr)),
            HEI, 9.5, color=GRAY)

    p = para(doc, space_before=2, space_after=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '原文', HEI, 10.5, True, BROWN)
    for li, line in enumerate(src.split('\n')):
        if not line.strip():
            continue
        p = para(doc, space_after=0, line=1.35)
        if li == 0:
            set_run(p.add_run(), '【鈔文】', KAI, 10.5, True, BROWN)
        set_run(p.add_run(), line.strip(), KAI, 12, False, INK)

    p = para(doc, space_before=4, space_after=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '白話', HEI, 10.5, True, BLUE)
    for li, line in enumerate(tr.split('\n')):
        if not line.strip():
            continue
        p = para(doc, space_after=0, line=1.35)
        if li == 0:
            set_run(p.add_run(), '【鈔文】', KAI, 10.5, True, BLUE)
        set_run(p.add_run(), line.strip(), KAI, 12, False, INK)

    # 每段另起一頁，留整頁 AI 回覆框
    doc.add_page_break()
    p = para(doc, space_before=0, space_after=2, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), 'AI 回覆', HEI, 12.5, True, GRAY)
    set_run(p.add_run(), '　第 %d 段・key %s・%s %s' % (i, key, vol, key2sec.get(key, '')),
            HEI, 10, color=GRAY)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(16.8)
    borders(cell)
    cp = cell.paragraphs[0]
    set_run(cp.add_run(), '（在此貼上 AI 回覆）', HEI, 9.5, italic=True, color=GRAY)
    for _ in range(26):
        cp = cell.add_paragraph()
        cp.paragraph_format.space_after = Pt(0)
        cp.paragraph_format.line_spacing = 1.35
    doc.add_page_break()

# 附：提示詞
p = para(doc, space_before=0, space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT)
set_run(p.add_run(), '附：校閱提示詞（內部 JSONL 版，可直接複製）', HEI, 13, True, BROWN)
prompt = io.open(os.path.join(B, '_src', 'review_prompt_universal.md'), encoding='utf-8').read()
tbl = doc.add_table(rows=1, cols=1)
cell = tbl.rows[0].cells[0]
cell.width = Cm(16.8)
borders(cell)
for idx, line in enumerate(prompt.split('\n')):
    cp = cell.paragraphs[0] if idx == 0 else cell.add_paragraph()
    cp.paragraph_format.space_after = Pt(0)
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.line_spacing = 1.25
    set_run(cp.add_run(), line if line else ' ', KAI, 9.5, False, INK)

footer(doc)
doc.save(OUT)
print('saved', OUT, '| entries', len(entries))
for i, (key, src, tr) in enumerate(entries, 1):
    print(i, key, seg.get(key, {}).get('vol', ''), key2sec.get(key, ''), han(src), han(tr))
