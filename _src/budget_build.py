
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
budget = [x.strip() for x in re.split(r'\n\s*\n', io.open(B + r'\AI語譯\_work\t_budget.txt', encoding='utf-8').read()) if x.strip()]

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
sec.top_margin = Cm(1.5); sec.bottom_margin = Cm(1.4); sec.left_margin = Cm(1.7); sec.right_margin = Cm(1.7)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run('省錢版全流程  vs  flash-high 直譯'), 16, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(10)
set_run(p.add_run('《行事鈔》隨戒釋相篇　樣本六段（原文 2,853 字）'), 10, color=RGBColor(0x66,0x66,0x66))

for i in range(min(len(src), len(high), len(budget))):
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(10); qf.space_after = Pt(0); qf.keep_with_next = True
    set_run(q.add_run('原文　%d' % (i+1)), 9, bold=True, color=RGBColor(0x88,0x66,0x33))
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.left_indent = Pt(6); qf.space_before = Pt(1); qf.space_after = Pt(4); qf.line_spacing = 1.2
    set_run(q.add_run(src[i]), 9.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q, 'F7F3EA')

    a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    af = a.paragraph_format; af.first_line_indent = Pt(22); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(5)
    set_run(a.add_run('甲　flash-high 直譯\n'), 8.5, bold=True, color=RGBColor(0x21,0x5a,0x8a))
    set_run(a.add_run(high[i]), 11)

    b = doc.add_paragraph(); b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    bf = b.paragraph_format; bf.first_line_indent = Pt(22); bf.line_spacing = 1.25; bf.space_before = Pt(2); bf.space_after = Pt(4)
    set_run(b.add_run('乙　省錢版（lite 初譯＋flash-low 校對＋人工核實）\n'), 8.5, bold=True, color=RGBColor(0x8a,0x4a,0x1f))
    set_run(b.add_run(budget[i]), 11)

# 結尾統計
p = doc.add_paragraph(); p.paragraph_format.page_break_before = True
set_run(p.add_run('本次全流程的實測數據'), 15, bold=True)
rows = [
    ('步驟', '模型 / 設定', '耗時', 'token'),
    ('初譯', 'gemini-3.5-flash-lite，thinking 關閉', '17s', '入 2,785／出 4,100'),
    ('校對', 'gemini-3.8-flash，thinking low，JSON 輸出', '13s', '入 7,210／出 1,350'),
    ('核實與修改', '人工（我），13 處', '—', '0'),
]
t = doc.add_table(rows=len(rows), cols=4); t.style = 'Table Grid'
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = t.cell(ri, ci); cell.text = ''
        pr = cell.paragraphs[0]
        set_run(pr.add_run(val), 9.5, bold=(ri == 0))

p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10)
set_run(p.add_run('估價（每 10 萬字，未計 batch 五折）'), 11, bold=True)
for line in ['flash-high 直譯：約 $1.4　→《行事鈔》全書約 $7.4',
             '省錢版（lite＋low 校對＋人工）：約 $0.26　→ 全書約 $1.3',
             '再走 batch 五折：約 $0.65／全書']:
    q = doc.add_paragraph(); q.paragraph_format.space_after = Pt(1)
    set_run(q.add_run('・' + line), 10)

out = B + r'\白話\_省錢版對照_全流程.docx'
doc.save(out)
print('saved', out, len(budget))
