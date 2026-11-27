# -*- coding: utf-8 -*-
"""合編本（四分律行事鈔資持記・句級合編）→ 白話對照本 Word／PDF。

資料來源：`docs/hebian/<卷>.html`（由 定稿＋對位結果_20261125 生成，含【鈔文】／【記文】與白話）。
輸出到與六書相同的四個資料夾，檔名：
  四分律行事鈔資持記合編_<卷>_白話對照本_單欄.docx／pdf（雙欄同）

用法：
  python -X utf8 _src/export_hebian_books.py                 # 全部 12 卷、兩種版面
  python -X utf8 _src/export_hebian_books.py --vol 卷上之一 --layout double --no-pdf
"""
import argparse
import glob
import html as H
import io
import os
import re
import shutil
import subprocess
import uuid

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

import export_kaiti_books as EK

B = EK.B
OUT = EK.OUT
HB_DIR = os.path.join(B, 'docs', 'hebian')
TITLE = '四分律行事鈔資持記合編'
SERIES = '南山三大部・句級合編'
VOLS = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
        '卷中之一', '卷中之二', '卷中之三', '卷中之四',
        '卷下之一', '卷下之二', '卷下之三', '卷下之四']

ITEM_RE = re.compile(
    r'<h2 class="sec"[^>]*>(.*?)</h2>'
    r'|<div class="pair ([cj])[^"]*"[^>]*>'
    r'<div class="(?:o|o2)">(.*?)</div><div class="t">(.*?)</div></div>', re.S)


def _txt(s):
    s = s.replace('<br />', '\n').replace('<br/>', '\n').replace('<br>', '\n')
    s = re.sub(r'<[^>]+>', '', s)
    return H.unescape(s).strip()


def load_vol(vol, pages=None):
    """回傳 [('h', 章名) 或 ('p', label, source, translation), ...]

    合編頁已一篇一頁，依 `卷__p1, __p2…` 順序串接。
    pages 可指定只取某些篇頁（如 ['卷上之一__p2']）。
    """
    files = glob.glob(os.path.join(HB_DIR, vol + '__p*.html'))
    files.sort(key=lambda p: int(re.search(r'__p(\d+)\.html$', p).group(1)))
    if pages:
        want = set(pages)
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in want]
    items = []
    for fp in files:
        t = io.open(fp, encoding='utf-8').read()
        for m in ITEM_RE.finditer(t):
            if m.group(1) is not None:
                items.append(('h', _txt(m.group(1))))
                continue
            body = _txt(m.group(3))
            mm = re.match(r'^【([^】]+)】(.*)$', body, re.S)
            if mm:
                label, src = mm.group(1), mm.group(2).strip()
            else:
                label = '鈔文' if m.group(2) == 'c' else '記文'
                src = body
            items.append(('p', label, src, _txt(m.group(4))))
    return items


def _style_doc(doc):
    st = doc.styles['Normal']
    st.font.name = EK.FONT
    st.element.rPr.rFonts.set(EK.qn('w:eastAsia'), EK.FONT)
    st.font.size = Pt(EK.BODY_PT)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 1.15
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.5); sec.bottom_margin = Cm(1.4)
    sec.left_margin = Cm(1.5); sec.right_margin = Cm(1.5)


def _heading(doc, text, first=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0 if first else 10)
    p.paragraph_format.space_after = Pt(3)
    EK.set_run(p.add_run(text), 16, True, RGBColor(0x8B, 0x5E, 0x3C))
    EK.bottom_border(p, 'B9AD95', '8')


def _chapter(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    EK.set_run(p.add_run(text), 12.5, True, RGBColor(0x6B, 0x5B, 0x4A))


def _single_body(doc, items):
    for it in items:
        if it[0] == 'h':
            _chapter(doc, it[1])
            continue
        _h, label, src, tr = it
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        EK.set_run(p.add_run('【%s】' % label), EK.LABEL_PT, True,
                   EK.LABEL_COLORS.get(label, EK.SRC_COLOR))
        EK.set_run(p.add_run(src), EK.BODY_PT, False, EK.SRC_COLOR)
        if tr:
            p2 = doc.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p2.paragraph_format.left_indent = Cm(0.25)
            p2.paragraph_format.space_before = Pt(0)
            p2.paragraph_format.space_after = Pt(4)
            p2.paragraph_format.line_spacing = 1.15
            EK.set_run(p2.add_run(tr), EK.BODY_PT, False, EK.TR_COLOR)


def _flush_two_col(doc, pairs):
    if not pairs:
        return
    tbl = doc.add_table(rows=0, cols=2)
    tbl.autofit = False
    for i, w in enumerate((7.2, 10.8)):
        tbl.columns[i].width = Cm(w)
    for label, src, tr in pairs:
        row = tbl.add_row()
        EK.no_row_split(row)
        left, right = row.cells[0], row.cells[1]
        left.width = Cm(7.2); right.width = Cm(10.8)
        first_l = first_r = True
        p = EK._cell_para(left, first_l)
        EK.set_run(p.add_run('【%s】' % label), EK.LABEL_PT, True,
                   EK.LABEL_COLORS.get(label, EK.SRC_COLOR))
        EK.set_run(p.add_run(src), EK.BODY_PT, False, EK.SRC_COLOR)
        if tr:
            p2 = EK._cell_para(right, first_r)
            EK.set_run(p2.add_run(tr), EK.BODY_PT, False, EK.TR_COLOR)
        EK._cell_bottom_border(left)
        EK._cell_bottom_border(right)


def _two_col_body(doc, items):
    cur = []
    for it in items:
        if it[0] == 'h':
            _flush_two_col(doc, cur)
            cur = []
            _chapter(doc, it[1])
        else:
            cur.append((it[1], it[2], it[3]))
    _flush_two_col(doc, cur)


def build(vol, two, do_pdf=True, pages=None, label=None, outdir=None):
    label = label or vol
    items = load_vol(vol, pages)
    doc = Document()
    _style_doc(doc)
    EK.add_title(doc, TITLE, SERIES, label)
    doc.add_section(WD_SECTION.NEW_PAGE)
    for section in doc.sections:
        EK.header_footer(section, TITLE, label)
    _heading(doc, label, first=True)
    if two:
        _two_col_body(doc, items)
    else:
        _single_body(doc, items)
    layout = '雙欄' if two else '單欄'
    ddir, pdir = OUT[layout]
    if outdir:
        ddir = pdir = outdir
    os.makedirs(ddir, exist_ok=True); os.makedirs(pdir, exist_ok=True)
    slug = label.replace('　', '').replace('・', '_').replace(' ', '')
    base = ('%s_%s' % (TITLE, slug)) if outdir else ('%s_%s_白話對照本_%s' % (TITLE, slug, layout))
    docx = os.path.join(ddir, base + '.docx')
    EK.rewrite_headers(doc, TITLE, label)
    doc.save(docx)
    if not do_pdf:
        return docx, None, 'docx-only'
    prof = 'file:///C:/Temp/lo_hb_' + uuid.uuid4().hex[:8]
    tmpdir = os.path.join(os.environ.get('TEMP', r'C:\Temp'), 'lo_hb_' + uuid.uuid4().hex[:8])
    os.makedirs(tmpdir, exist_ok=True)
    cmd = [EK.SOFFICE, '--headless', '--norestore', '-env:UserInstallation=' + prof,
           '--convert-to', 'pdf', '--outdir', tmpdir, docx]
    try:
        subprocess.run(cmd, capture_output=True, timeout=1800)
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return docx, None, 'timeout'
    pdf = os.path.join(pdir, base + '.pdf')
    src = os.path.join(tmpdir, base + '.pdf')
    moved = False
    if os.path.exists(src):
        try:
            shutil.move(src, pdf)
            moved = True
        except Exception:
            moved = False
    shutil.rmtree(tmpdir, ignore_errors=True)
    return docx, (pdf if moved else None), ('ok' if moved else 'pdf-fail')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vol', default='')
    ap.add_argument('--layout', choices=('single', 'double'), default='')
    ap.add_argument('--no-pdf', action='store_true')
    ap.add_argument('--page', action='append', default=[], help='只輸出指定篇頁，可重複，如 卷上之一__p2')
    ap.add_argument('--label', default='', help='篇頁標題（預設同卷名），如 卷上之一・第2篇 集僧通局')
    ap.add_argument('--outdir', default='', help='輸出到指定資料夾（不放入正式對照本系列）')
    a = ap.parse_args()
    if a.page:
        vols = sorted({p.split('__p')[0] for p in a.page})
        for vol in vols:
            pages = [p for p in a.page if p.startswith(vol + '__p')]
            layouts = (False,) if a.layout == 'single' else ((True,) if a.layout == 'double' else (False, True))
            for two in layouts:
                print('build hebian', vol, pages, '雙欄' if two else '單欄', flush=True)
                docx, pdf, st = build(vol, two, not a.no_pdf, pages, a.label or None, a.outdir or None)
                print('->', docx, pdf or 'PDF FAIL', st, flush=True)
        return
    for vol in VOLS:
        if a.vol and vol != a.vol:
            continue
        for two in (False, True):
            if a.layout == 'single' and two:
                continue
            if a.layout == 'double' and not two:
                continue
            print('build hebian', vol, '雙欄' if two else '單欄', flush=True)
            docx, pdf, st = build(vol, two, not a.no_pdf)
            print('->', docx, pdf or 'PDF FAIL', st, flush=True)


if __name__ == '__main__':
    main()
