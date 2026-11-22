# -*- coding: utf-8 -*-
"""六書白話對照本：分卷 DOCX → PDF，沿用舊版「原文小字棕色、白話大字黑色」版型。"""
import io, json, os, subprocess, sys, uuid
from collections import OrderedDict
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT_DOCX = os.path.join(B, '白話對照本_分卷_DOCX')
OUT_PDF = os.path.join(B, '白話對照本_分卷_PDF')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'

BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔', '南山三大部之一'),
    ('jieshu', '四分律含注戒本疏行宗記', '南山三大部之二'),
    ('yeshu', '四分律刪補隨機羯磨疏', '南山三大部之三'),
    ('nicao', '四分比丘尼鈔', '南山五大部之四'),
    ('yichao', '四分律拾毗尼義鈔', '南山五大部之五'),
    ('zhichi', '四分律行事鈔資持記', '南山三大部之記'),
]
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文', '記序')
SRC_COLOR = RGBColor(0x6B, 0x5B, 0x4A)
GREY = RGBColor(0x66, 0x66, 0x66)


def set_run(run, size=10.5, bold=False, color=None, name='Microsoft JhengHei'):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def shade(par, fill):
    pPr = par._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    pPr.append(shd)


def bottom_border(par, color='D9D2C5', sz='6'):
    pPr = par._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), sz)
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def add_page_number(par):
    run = par.add_run()
    fld1 = OxmlElement('w:fldChar'); fld1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = 'PAGE'
    fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    set_run(run, 9, False, GREY)


def load_rows(book):
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    rows.sort(key=lambda r: (r.get('vol') or '', r.get('chunk') or '', r.get('raw_start', 0)))
    return rows


def row_parts(row):
    segs = row.get('segments') or []
    if segs:
        return [(s.get('label') or row.get('label') or '鈔文',
                 s.get('display_source') or s.get('source') or '',
                 s.get('translation') or '') for s in segs]
    return [(row.get('label') or '鈔文',
             row.get('display_source') or row.get('source') or '',
             row.get('translation') or '')]


def clean(s):
    s = (s or '').strip()
    for lab in LABELS:
        s = s.replace('【%s】' % lab, '')
    return s.strip()


def build_volume(book, title, series, vol, rows):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.9); sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(1.9); sec.right_margin = Cm(1.9)

    # header / footer
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run('%s　%s' % (title, vol)), 8.5, False, GREY)
    bottom_border(hp)

    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number(fp)

    # title block
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(70)
    set_run(p.add_run(title), 22, True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(vol), 16, True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('白話語譯‧對照本'), 13, False, GREY)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    set_run(p.add_run(series + '　唐·道宣律師　撰／述'), 9.5, False, GREY)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('2026-11-22　依定稿重新排版'), 9.5, False, GREY)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(60)
    set_run(p.add_run('原文：定稿 display_source（句讀版）　白話：定稿 translation'), 8.5, False, GREY)

    doc.add_page_break()
    last_chunk = None
    for row in rows:
        ch = row.get('chunk') or ''
        if ch and ch != last_chunk:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            set_run(p.add_run(ch), 13, True)
            bottom_border(p, 'B9AD95', '8')
            last_chunk = ch
        for lab, src, tr in row_parts(row):
            src = clean(src); tr = clean(tr)
            if not src and not tr:
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.25
            set_run(p.add_run('【%s】' % lab), 9.5, True, SRC_COLOR)
            set_run(p.add_run(src), 10.5, False, SRC_COLOR)
            if tr:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Cm(0.45)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(7)
                p.paragraph_format.line_spacing = 1.55
                set_run(p.add_run(tr), 12, False, RGBColor(0x11, 0x11, 0x11))

    os.makedirs(OUT_DOCX, exist_ok=True)
    safe = '%s_%s_白話對照本' % (title, vol)
    path = os.path.join(OUT_DOCX, safe + '.docx')
    doc.save(path)
    return path, safe


def convert(docx, timeout=900):
    os.makedirs(OUT_PDF, exist_ok=True)
    prof = 'file:///C:/Temp/lo_baihua_v_' + uuid.uuid4().hex[:8]
    cmd = [SOFFICE, '--headless', '--norestore',
           '-env:UserInstallation=' + prof,
           '--convert-to', 'pdf', '--outdir', OUT_PDF, docx]
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    pdf = os.path.join(OUT_PDF, os.path.splitext(os.path.basename(docx))[0] + '.pdf')
    if os.path.exists(pdf):
        return pdf, str(os.path.getsize(pdf))
    return None, 'no output'


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ''
    for book, title, series in BOOKS:
        if only and only not in (book, title):
            continue
        rows = load_rows(book)
        vols = OrderedDict()
        for r in rows:
            vols.setdefault(r.get('vol') or '卷首', []).append(r)
        for vol, rs in vols.items():
            print('build', book, vol, len(rs), flush=True)
            docx, safe = build_volume(book, title, series, vol, rs)
            pdf, info = convert(docx)
            print('->', pdf or 'FAIL', info, flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
