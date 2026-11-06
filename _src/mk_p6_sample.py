# -*- coding: utf-8 -*-
"""試點：篇6 結界方法（55 鈔／100 記）的會本樣張"""
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
SECS = ex.sections()
ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
FONT = 'SimSun'; LATIN = 'Times New Roman'
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')

idx = 5                      # 篇6
sec = SECS[idx]
zi = ZI[idx]
am = AM[str(idx)]
print('篇', idx + 1, sec['name'], '鈔', len(sec['items']), '記', len(zi), '對應表', len(am))


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


doc = Document()
st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
s = doc.sections[0]
s.page_width = Cm(21); s.page_height = Cm(29.7)
s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6)
s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('行事鈔・資持記　會本樣張'), 18, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('第6篇　結界方法（55 鈔／100 記）'), 12, color=RGBColor(0x66, 0x66, 0x66))

# 鈔：保留非標題行，並記下它在 items 中的序號（1 起算）
chao = []
for it in sec['items']:
    o, t = it[0], it[1]
    if SKIP.match(o.strip()):
        continue
    chao.append((len(chao) + 1, o, t))

# 記 → 鈔號（am 已是鈔序，1 起算；0 表篇前）
by_c = {}
for k, c in enumerate(am[:len(zi)]):
    by_c.setdefault(int(c), []).append(k)

for cno, o, t in chao:
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
    sr(q.add_run('【鈔%02d】' % cno + o), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')
    a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
    a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
    sr(a2.add_run(t), 10.5)
    for k in sorted(by_c.get(cno, [])):
        zo, zt = zi[k]
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run('【記%03d】' % (k + 1) + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        b2.paragraph_format.left_indent = Pt(14)
        sr(b2.add_run(zt), 10)

out = os.path.join(B, '白話', '樣張_篇6結界方法_會本.docx')
doc.save(out)
print('saved', out, '段落', len(doc.paragraphs))
print('\n--- 前 12 個輸出段落 ---')
for p in doc.paragraphs[:14]:
    print('  ', p.text.strip()[:56])
