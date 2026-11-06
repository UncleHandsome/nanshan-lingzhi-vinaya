# -*- coding: utf-8 -*-
"""篇6 會本（依義理對應表重排：記文一律排在所釋鈔文之後）"""
import io, os, re, json, sys, importlib.util, csv
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

# 記→鈔（依使用者提供的義理對應表；跨兩鈔者暫歸前者）
RANGES = [(1,7,1),(8,8,2),(9,10,3),(11,15,4),(16,20,5),(21,21,6),(22,23,7),(24,24,8),
          (25,26,9),(27,27,10),(28,29,11),(30,31,12),(32,33,13),(34,37,14),(38,44,15),
          (45,46,16),(47,49,17),(50,50,18),(51,51,19),(52,52,20),(53,53,21),(54,55,23),
          (56,56,25),(57,58,26),(59,60,29),(61,61,30),(62,65,31),(66,66,32),(67,67,33),
          (68,68,35),(69,73,37),(74,74,38),(75,76,40),(77,77,42),(78,81,43),(82,82,44),
          (83,83,45),(84,85,47),(86,86,48),(87,88,49),(89,93,52),(94,94,53),(95,98,54),
          (99,100,55)]
c_of = {}
for a, b, c in RANGES:
    for k in range(a, b + 1):
        c_of[k] = c
by_c = {}
for k in range(1, len(zi) + 1):
    by_c.setdefault(c_of.get(k, 1), []).append(k)

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
sr(p.add_run('行事鈔・資持記　會本（篇6 結界方法）'), 18, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('依義理對應重排：記文一律在所釋鈔文之後'), 10.5, color=RGBColor(0x66, 0x66, 0x66))

rows = []
for cno, it in enumerate(chao, 1):
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(9); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
    sr(q.add_run('【鈔%02d】' % cno + it[0]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')
    a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
    a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
    sr(a2.add_run(it[1]), 10.5)
    ks = by_c.get(cno, [])
    SHARED = {22: 53, 24: 55, 27: 58, 28: 58, 34: 67, 36: 68, 39: 74, 41: 76, 46: 83, 50: 88, 51: 88}
    if ks:
        lab = '記%d–%d' % (ks[0], ks[-1])
    elif cno in SHARED:
        lab = '（與前鈔共用記%d）' % SHARED[cno]
    else:
        lab = '（無記）'
    rows.append((cno, re.sub(r'\s+', '', it[0])[:34], lab))
    for k in ks:
        zo, zt = zi[k - 1]
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run('【記%03d】' % k + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(zt), 10)

out = os.path.join(B, '白話', '樣張_篇6結界方法_會本_義理重排.docx')
doc.save(out)
print('saved', out, '段落', len(doc.paragraphs))

csvp = os.path.join(B, '合編材料', '篇06_義理對應_重排.csv')
with io.open(csvp, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['鈔序', '鈔文起首', '記範圍'])
    for r in rows:
        w.writerow(r)
print('saved', csvp)
for r in rows[:12]:
    print('  ', r)
