
# -*- coding: utf-8 -*-
import io, os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
FONT='DFKai-SB'; LATIN='Times New Roman'
def set_run(r, size, bold=False, color=None):
    r.font.size=Pt(size); r.font.bold=bold; r.font.name=LATIN
    rPr=r._element.get_or_add_rPr(); rf=rPr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'),LATIN); rf.set(qn('w:hAnsi'),LATIN); rf.set(qn('w:eastAsia'),FONT)
    if color is not None: r.font.color.rgb=color
def add_field(par, instr):
    run=par.add_run(); f1=OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'),'begin')
    it=OxmlElement('w:instrText'); it.set(qn('xml:space'),'preserve'); it.text=instr
    f2=OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'),'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)

text = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read()
paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
doc = Document()
st = doc.styles['Normal']; st.font.size=Pt(12); st.font.name=LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
s = doc.sections[0]
s.page_width=Cm(21); s.page_height=Cm(29.7)
s.top_margin=Cm(2.0); s.bottom_margin=Cm(1.8); s.left_margin=Cm(2.2); s.right_margin=Cm(2.2)
p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run('四分律刪補隨機羯磨疏'), 22, bold=True)
p = doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after=Pt(18)
set_run(p.add_run('句讀本（原文，無白話）'), 12, color=RGBColor(0x66,0x66,0x66))
for q in paras:
    a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(q) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
    af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.6; af.space_before=Pt(2); af.space_after=Pt(2)
    set_run(a.add_run(q), 12)
fp = doc.sections[0].footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88,0x88,0x88)); add_field(fp,' PAGE ')
out = os.path.join(D,'白話','業疏_句讀本.docx')
doc.save(out)
print('paras', len(paras), 'saved')
