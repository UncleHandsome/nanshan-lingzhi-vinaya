# -*- coding: utf-8 -*-
"""依 合編材料/篇NN_*.csv 的「對應鈔號」重建合編 docx"""
import io, os, re, csv, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '合編材料')
OUTDIR = os.path.join(MAT, 'docx')
os.makedirs(OUTDIR, exist_ok=True)

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


def read_csv(p):
    rows = []
    with io.open(p, encoding='utf-8-sig') as fh:
        rd = csv.DictReader(fh)
        for r in rd:
            rows.append(r)
    return rows


def build_doc(title, blocks):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.4); sec.right_margin = Cm(2.4)
    st = doc.styles['Normal']
    st.font.name = 'SimSun'
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

    p = doc.add_paragraph()
    r = p.add_run(title)
    r.bold = True; r.font.size = Pt(16)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for kind, text, tr in blocks:
        if kind == 'sec':
            p = doc.add_paragraph()
            r = p.add_run(text)
            r.bold = True; r.font.size = Pt(13)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.size = Pt(10.5)
        if kind == '記':
            r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        else:
            r.font.color.rgb = RGBColor(0x6B, 0x4F, 0x2A)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.25
        p2 = doc.add_paragraph()
        r2 = p2.add_run(tr)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        p2.paragraph_format.line_spacing = 1.3
        p2.paragraph_format.space_after = Pt(4)
    return doc


def main():
    files = sorted(glob.glob(os.path.join(MAT, '篇*.csv')))
    print('csv', len(files))
    all_blocks = []
    for f in files:
        name = os.path.basename(f)[:-4]
        rows = read_csv(f)
        chao = [r for r in rows if r['類型'] == '鈔']
        ji = [r for r in rows if r['類型'] == '記']
        if not chao:
            continue
        by_c = {}
        last = 1
        for r in ji:
            v = (r.get('對應鈔號(可改)') or '').strip()
            try:
                c = int(v) if v else last
            except ValueError:
                c = last
            c = max(1, min(len(chao), c))
            last = c
            by_c.setdefault(c, []).append(r)
        blocks = [('sec', name.replace('_', '　'), '')]
        for i, r in enumerate(chao, 1):
            blocks.append(('鈔', '【鈔】' + r['原文'], r['白話']))
            for j in by_c.get(i, []):
                blocks.append(('記', '【記】' + j['原文'], j['白話']))
        all_blocks += blocks
        doc = build_doc('四分律行事鈔資持記　句級合編　' + name.replace('_', '　'), blocks)
        doc.save(os.path.join(OUTDIR, name + '.docx'))
    doc = build_doc('四分律行事鈔資持記　句級合編（人工對齊版）', all_blocks)
    out = os.path.join(MAT, '合編_人工對齊版.docx')
    doc.save(out)
    print('saved', out, '段落', len(all_blocks))


if __name__ == '__main__':
    main()
