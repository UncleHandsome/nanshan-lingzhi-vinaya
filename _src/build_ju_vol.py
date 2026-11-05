# -*- coding: utf-8 -*-
"""尼鈔、尼義鈔：以「句讀原文」重建分卷對照本與全白話本（取代原本未加句讀的分卷本）。

用法：python _src/build_ju_vol.py [--no-pdf]
"""
import os, io, sys, subprocess
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_ju

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '白話')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'
FONT = 'DFKai-SB'
LATIN = 'Times New Roman'

BOOKS = [
    ('03_業疏', '四分律刪補隨機羯磨疏', '業疏'),
    ('04_比丘尼鈔', '四分比丘尼鈔', '尼鈔'),
    ('05_拾毗尼義鈔', '四分律拾毗尼義鈔', '尼義鈔'),
]
VOLNAME = {'卷首': '卷一', '卷上': '卷上', '卷中': '卷中', '卷下': '卷下'}


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


def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = instr
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1)
    run._r.append(it)
    run._r.append(f2)


def build(title, vol_label, pairs, mode, path):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = LATIN
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(1.8)
    s.bottom_margin = Cm(1.7)
    s.left_margin = Cm(1.9)
    s.right_margin = Cm(1.9)

    for _ in range(4):
        doc.add_paragraph().add_run('')
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    set_run(p.add_run(title), 24, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run(vol_label), 14)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('白話語譯‧' + ('對照本' if mode == 'dui' else '全白話本')), 12, color=RGBColor(0x66, 0x66, 0x66))
    doc.add_page_break()

    for o, t in pairs:
        if mode == 'dui':
            q = doc.add_paragraph()
            qf = q.paragraph_format
            qf.left_indent = Pt(6)
            qf.space_before = Pt(5)
            qf.space_after = Pt(0)
            qf.line_spacing = 1.25
            qf.keep_with_next = True
            set_run(q.add_run(o), 10, color=RGBColor(0x6b, 0x5b, 0x4a))
            shade(q, 'F7F3EA')
        a = doc.add_paragraph()
        a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        af = a.paragraph_format
        af.first_line_indent = Pt(24)
        af.line_spacing = 1.35
        af.space_before = Pt(1)
        af.space_after = Pt(5)
        set_run(a.add_run(t), 11.5)
    doc.save(path)
    return len(doc.paragraphs)


def main():
    no_pdf = '--no-pdf' in sys.argv
    docxs = []
    for tag, title, prefix in BOOKS:
        pre = []
        vols = []
        for v, p in site_ju.get(tag):
            if v == '卷首':
                pre = p
            else:
                vols.append((v, p))
        if pre and vols:                       # 卷首（序等）併入卷上
            vols[0] = (vols[0][0], pre + vols[0][1])
        for vol, pairs in vols:
            if not pairs:
                continue
            name = '%s_%s' % (prefix, VOLNAME.get(vol, vol))
            for mode, label in (('dui', '白話對照本'),):
                p = os.path.join(OUT, '%s_%s.docx' % (name, label))
                n = build(title, vol, pairs, mode, p)
                docxs.append(p)
                print('%s %s %d 段 %d paras' % (name, label, len(pairs), n))
    if no_pdf:
        return
    for d in docxs:
        subprocess.run([SOFFICE, '--headless', '--norestore',
                        '-env:UserInstallation=file:///C:/Temp/lo_profile_juvol',
                        '--convert-to', 'pdf', '--outdir', OUT, d], capture_output=True)
    import glob, shutil
    for pat, dst in (('*_白話對照本.pdf', '對照本'),):
        dd = os.path.join(OUT, dst)
        os.makedirs(dd, exist_ok=True)
        for p in glob.glob(os.path.join(OUT, pat)):
            shutil.move(p, os.path.join(dd, os.path.basename(p)))
    print('converted', len(docxs))


if __name__ == '__main__':
    main()
