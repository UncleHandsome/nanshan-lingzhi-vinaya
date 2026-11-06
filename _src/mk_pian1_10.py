# -*- coding: utf-8 -*-
"""篇1-10 會本（依人工對應表 hb_align；記段整段隨鈔排列）"""
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
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
FONT = 'SimSun'; LATIN = 'Times New Roman'


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def build(p):
    idx = p - 1
    sec = SECS[idx]
    zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
    by_c = {}
    for k, c in enumerate(am[:len(zi)]):
        c = int(c)
        if c <= 0:
            continue
        by_c.setdefault(c, []).append(k)
    front = [k for k in range(len(zi)) if k < len(am) and int(am[k]) == 0]

    doc = Document()
    st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21); s.page_height = Cm(29.7)
    s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6)
    s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('四分律行事鈔・資持記　會本'), 18, bold=True)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('第%d篇　%s' % (p, sec['name'])), 11, color=RGBColor(0x66, 0x66, 0x66))

    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)
        sr(q.add_run('〔篇前總釋〕'), 11, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
        for k in front:
            zo, zt = zi[k]
            r = doc.add_paragraph(); rf = r.paragraph_format
            rf.space_before = Pt(3); rf.space_after = Pt(1); rf.line_spacing = 1.2; rf.keep_with_next = True
            sr(r.add_run('【記%03d】' % (k + 1) + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
            b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
            b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
            sr(b2.add_run(zt), 10)

    for cno, it in enumerate(chao, 1):
        qq = doc.add_paragraph(); qf = qq.paragraph_format
        qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
        sr(qq.add_run('【鈔%02d】' % cno + it[0]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
        a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
        a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
        sr(a2.add_run(it[1]), 10.5)
        for k in by_c.get(cno, []):
            zo, zt = zi[k]
            r = doc.add_paragraph(); rf = r.paragraph_format
            rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
            rf.left_indent = Pt(14); rf.keep_with_next = True
            sr(r.add_run('【記%03d】' % (k + 1) + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
            b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
            b2.paragraph_format.left_indent = Pt(14)
            b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
            sr(b2.add_run(zt), 10)

    out = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p, sec['name']))
    doc.save(out)
    return out, len(chao), len(zi)


for p in range(1, 11):
    out, nc, nz = build(p)
    print('篇%02d %-8s 鈔%3d 記%3d → %s' % (p, SECS[p - 1]['name'], nc, nz, os.path.basename(out)))
