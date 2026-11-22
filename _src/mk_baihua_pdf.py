# -*- coding: utf-8 -*-
"""由 定稿/*.jsonl 產生六書白話對照本 DOCX，再用 LibreOffice 轉 PDF。"""
import io, json, os, subprocess, sys, uuid
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT_DOCX = os.path.join(B, '白話對照本_DOCX')
OUT_PDF = os.path.join(B, '白話對照本_PDF')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'

BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔'),
    ('jieshu', '四分律含注戒本疏行宗記'),
    ('yeshu', '四分律刪補隨機羯磨疏'),
    ('nicao', '四分比丘尼鈔'),
    ('yichao', '四分律拾毗尼義鈔'),
    ('zhichi', '四分律行事鈔資持記'),
]
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文', '記序')


def set_font(run, name='Microsoft JhengHei', size=10.5, bold=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def add_page_number(par):
    run = par.add_run()
    fld = run._r.makeelement(qn('w:fldSimple'), {qn('w:instr'): 'PAGE'})
    run._r.addnext(fld)


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


def strip_label(s):
    s = (s or '').strip()
    for lab in LABELS:
        s = s.replace('【%s】' % lab, '')
    return s.strip()


def build_docx(book, title):
    rows = load_rows(book)
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    set_font(r, size=22, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('白話對照本')
    set_font(r, size=16)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('2026-11-22')
    set_font(r, size=10)

    last_vol = None
    last_chunk = None
    for row in rows:
        vol = row.get('vol') or ''
        chunk = row.get('chunk') or ''
        if vol != last_vol:
            doc.add_page_break()
            p = doc.add_paragraph()
            r = p.add_run(vol or title)
            set_font(r, size=18, bold=True)
            last_vol = vol
            last_chunk = None
        if chunk != last_chunk:
            p = doc.add_paragraph()
            r = p.add_run(chunk)
            set_font(r, size=13, bold=True)
            last_chunk = chunk

        for lab, src, tr in row_parts(row):
            src = strip_label(src)
            tr = strip_label(tr)
            if not src and not tr:
                continue
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run('【%s】' % lab)
            set_font(r, size=10.5, bold=True)
            r = p.add_run(src)
            set_font(r, size=11)
            if tr:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.4)
                p.paragraph_format.space_after = Pt(5)
                r = p.add_run(tr)
                set_font(r, size=10.5)

    os.makedirs(OUT_DOCX, exist_ok=True)
    path = os.path.join(OUT_DOCX, title + '_白話對照本.docx')
    doc.save(path)
    return path


def convert(docx, timeout=900):
    os.makedirs(OUT_PDF, exist_ok=True)
    prof = 'file:///C:/Temp/lo_baihua_' + uuid.uuid4().hex[:8]
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
    for book, title in BOOKS:
        if only and only not in (book, title):
            continue
        print('build docx', book, flush=True)
        docx = build_docx(book, title)
        print('convert', docx, flush=True)
        pdf, info = convert(docx)
        print('->', pdf or 'FAIL', info, flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
