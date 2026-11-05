
# -*- coding: utf-8 -*-
import io, json, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
src = [x.strip() for x in io.open(B + r'\AI語譯\_work\t_src.txt', encoding='utf-8').read().split('\n') if x.strip()]
high = [x.strip() for x in re.split(r'\n\s*\n', io.open(B + r'\AI語譯\_work\t_high.txt', encoding='utf-8').read()) if x.strip()]
lite = [x.strip() for x in re.split(r'\n\s*\n', io.open(B + r'\AI語譯\_work\t_lite2.txt', encoding='utf-8').read()) if x.strip()]
issues = json.load(io.open(B + r'\AI語譯\_work\t_review.json', encoding='utf-8'))

FONT = 'DFKai-SB'; LATIN = 'Times New Roman'
def set_run(r, size, bold=False, color=None):
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = LATIN
    rPr = r._element.get_or_add_rPr(); rf = rPr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'), LATIN); rf.set(qn('w:hAnsi'), LATIN); rf.set(qn('w:eastAsia'), FONT)
    if color is not None: r.font.color.rgb = color

def shade(p, hexcolor):
    pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor); pPr.append(shd)

doc = Document()
st = doc.styles['Normal']; st.font.size = Pt(11); st.font.name = LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
sec = doc.sections[0]
sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.6); sec.bottom_margin = Cm(1.5); sec.left_margin = Cm(1.8); sec.right_margin = Cm(1.8)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run('譯法對照：flash-high 直譯  vs  lite 初譯'), 16, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run('《四分律行事鈔》隨戒釋相篇　樣本六段（原文 2,853 字）'), 10, color=RGBColor(0x66,0x66,0x66))

for i in range(min(len(src), len(high), len(lite))):
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(9); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = True
    set_run(q.add_run('原文　%d' % (i+1)), 9, bold=True, color=RGBColor(0x88,0x66,0x33))
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.left_indent = Pt(6); qf.space_before = Pt(1); qf.space_after = Pt(3); qf.line_spacing = 1.2
    set_run(q.add_run(src[i]), 10, color=RGBColor(0x6b,0x5b,0x4a)); shade(q, 'F7F3EA')

    a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    af = a.paragraph_format; af.first_line_indent = Pt(22); af.line_spacing = 1.25; af.space_before = Pt(3); af.space_after = Pt(3)
    set_run(a.add_run('甲　flash-high　'), 9, bold=True, color=RGBColor(0x21,0x5a,0x8a))
    set_run(a.add_run(high[i]), 11)

    b = doc.add_paragraph(); b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    bf = b.paragraph_format; bf.first_line_indent = Pt(22); bf.line_spacing = 1.25; bf.space_before = Pt(0); bf.space_after = Pt(2)
    set_run(b.add_run('乙　lite　　　'), 9, bold=True, color=RGBColor(0x8a,0x4a,0x1f))
    set_run(b.add_run(lite[i]), 11)

p = doc.add_paragraph(); p.paragraph_format.page_break_before = True
set_run(p.add_run('附：flash-high 校對乙版所抓出的問題（%d 條）' % len(issues)), 14, bold=True)
for it in issues:
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(7); qf.space_after = Pt(1); qf.line_spacing = 1.2
    set_run(q.add_run('・'), 10)
    set_run(q.add_run(str(it.get('quote',''))[:40]), 9.5, bold=True, color=RGBColor(0x33,0x33,0x33))
    a = doc.add_paragraph(); af = a.paragraph_format; af.left_indent = Pt(14); af.space_after = Pt(1); af.line_spacing = 1.25
    set_run(a.add_run('問題：'), 9, bold=True); set_run(a.add_run(str(it.get('issue',''))), 9.5)
    b = doc.add_paragraph(); bf = b.paragraph_format; bf.left_indent = Pt(14); bf.space_after = Pt(2); bf.line_spacing = 1.25
    set_run(b.add_run('建議：'), 9, bold=True, color=RGBColor(0x8a,0x4a,0x1f)); set_run(b.add_run(str(it.get('fix',''))), 9.5, color=RGBColor(0x44,0x44,0x44))

out = B + r'\白話\_對照樣本_譯法比較.docx'
doc.save(out)
print('saved', out, len(issues))
