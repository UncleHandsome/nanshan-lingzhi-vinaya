# -*- coding: utf-8 -*-
"""六書白話對照本：標楷體 14pt、緊湊排版、單欄／雙欄 DOCX＋PDF。

執行：
  python -X utf8 _src/export_kaiti_books.py
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import uuid
from collections import OrderedDict

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def build_stamp():
    """回傳 (commit 短碼, 產生時間字串)。

    `BOOKS_STAMP` 環境變數可指定 commit（區域修補單卷時，讓頁尾仍記同一版定稿）。
    """
    import subprocess, time
    h = (os.environ.get('BOOKS_STAMP') or '').strip()
    if not h:
        try:
            h = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=B,
                               capture_output=True, text=True).stdout.strip()
        except Exception:
            pass
    return (h or 'nogit'), time.strftime('%Y-%m-%d %H:%M')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'
FONT = 'DFKai-SB'  # 標楷體
BODY_PT = 14
LABEL_PT = 10.5
SRC_COLOR = RGBColor(0x6B, 0x5B, 0x4A)
TR_COLOR = RGBColor(0x1F, 0x1B, 0x16)
GREY = RGBColor(0x66, 0x66, 0x66)
LABEL_COLORS = {
    '疏文': RGBColor(0x8B, 0x5E, 0x3C),
    '記文': RGBColor(0x3F, 0x6F, 0x8F),
    '鈔文': RGBColor(0x7A, 0x5C, 0x3E),
    '律文': RGBColor(0x7A, 0x6A, 0x3A),
    '註文': RGBColor(0x6B, 0x6B, 0x6B),
    '序文': RGBColor(0x8A, 0x5A, 0x7A),
}
BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔', '南山三大部之一'),
    ('jieshu', '四分律含注戒本疏行宗記', '南山三大部之二'),
    ('yeshu', '四分律刪補隨機羯磨疏', '南山三大部之三'),
    ('nicao', '四分比丘尼鈔', '南山五大部之四'),
    ('yichao', '四分律拾毗尼義鈔', '南山五大部之五'),
    ('zhichi', '四分律行事鈔資持記', '南山三大部之記'),
]
LABELS = tuple(LABEL_COLORS)
OUT = {
    '單欄': (os.path.join(B, '白話對照本_標楷_單欄_DOCX'), os.path.join(B, '白話對照本_標楷_單欄_PDF')),
    '雙欄': (os.path.join(B, '白話對照本_標楷_雙欄_DOCX'), os.path.join(B, '白話對照本_標楷_雙欄_PDF')),
}


def set_run(run, size=BODY_PT, bold=False, color=None):
    run.font.name = FONT
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), FONT)
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
    bottom.set(qn('w:space'), '2')
    bottom.set(qn('w:color'), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def page_number(par):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'PAGE'
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    set_run(run, 9, False, GREY)


def columns(section, num):
    cols = section._sectPr.xpath('./w:cols')
    if cols:
        c = cols[0]
        c.set(qn('w:num'), str(num))
        c.set(qn('w:space'), '300')


def load_rows(book):
    """讀定稿。**保留定稿檔序**（＝原文順序），只依卷分組。

    2026-11-26 修：原本再依 (vol, chunk, raw_start) 排序，但定稿的 chunk
    欄有新舊兩種命名（`卷一上之一` 與 `01a_卷一上之一` 並存），字串排序會把
    同一卷的段落區塊搬來搬去，Word／PDF 內文順序因此錯亂（網站是依 raw_start
    排，所以網站正常）。定稿檔序本身就是 canonical（各卷 raw_start 單調遞增），
    卷內直接保持檔序即可。
    """
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r.get('vol') or '卷首', []).append(r)
    return [r for g in groups.values() for r in g]


def parts(row):
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


def header_footer(section, title, vol):
    # 解除與前一 section 的連結，並清空既有內容，避免頁首頁尾重複疊加
    try:
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
    except Exception:
        pass
    hp = section.header.paragraphs[0]
    for r in list(hp.runs):
        r._element.getparent().remove(r._element)
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run('%s　%s' % (title, vol)), 8.5, False, GREY)
    bottom_border(hp)
    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in list(fp.runs):
        r._element.getparent().remove(r._element)
    _h, _ts = build_stamp()
    set_run(fp.add_run('定稿 %s　' % _h), 8, False, GREY)
    page_number(fp)


def add_title(doc, title, series, vol=''):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(100)
    set_run(p.add_run(title), 24, True, RGBColor(0x3C, 0x2A, 0x1A))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('白話對照本'), 16, True, RGBColor(0x8B, 0x5E, 0x3C))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if vol:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(p.add_run(vol), 15, True, RGBColor(0x6B, 0x5B, 0x4A))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(series + '　唐·道宣律師　撰／述'), 10.5, False, GREY)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _h, _ts = build_stamp()
    set_run(p.add_run('標楷體 14pt‧緊湊排版‧定稿 commit %s‧%s' % (_h, _ts)), 9.5, False, GREY)


def _clear_part(part):
    """清空 header/footer：只留第一個段落並刪掉所有內容。"""
    ps = part.paragraphs
    for extra in list(ps)[1:]:
        extra._element.getparent().remove(extra._element)
    p0 = part.paragraphs[0]
    for r in list(p0.runs):
        r._element.getparent().remove(r._element)
    for child in list(p0._element):
        if child.tag.endswith('}pPr'):
            continue
        p0._element.remove(child)


def rewrite_headers(doc, title, vol):
    """統一重寫所有 section 的頁首頁尾，確保不重複。"""
    _h, _ts = build_stamp()
    for section in doc.sections:
        try:
            section.header.is_linked_to_previous = False
            section.footer.is_linked_to_previous = False
        except Exception:
            pass
        _clear_part(section.header)
        hp = section.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_run(hp.add_run('%s　%s' % (title, vol)), 8.5, False, GREY)
        bottom_border(hp)
        _clear_part(section.footer)
        fp = section.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(fp.add_run('定稿 %s　' % _h), 8, False, GREY)
        page_number(fp)


def _cell_bottom_border(cell):
    """表格儲存格淡底線（段與段之間的分隔）。"""
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), 'D9D0BE')
    borders.append(bottom)
    tcPr.append(borders)


def _cell_para(cell, first):
    if first and cell.paragraphs:
        p = cell.paragraphs[0]
    else:
        p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.12
    return p


def no_row_split(row):
    """避免 Word 表格列跨頁拆開（雙欄一列＝一對原文／白話）。"""
    from docx.oxml import OxmlElement
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement('w:cantSplit')
    trPr.append(el)


def _build_pairs_two_col(doc, rows):
    """雙欄版：左原文、右白話，逐段一列（和網站「並排」一致）。

    每篇（chunk）一張無框線表格，欄寬 原文 7.2cm／白話 10.8cm（2:3；A4 內文寬 18cm），
    段與段之間用淡底線分隔；每列左格放原文（含段別），右格放白話。
    """
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(r.get('chunk') or '', []).append(r)
    vols = []
    for r in rows:
        v = r.get('vol') or '卷首'
        if v not in vols:
            vols.append(v)
    for vi, v in enumerate(vols):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0 if vi == 0 else 10)
        p.paragraph_format.space_after = Pt(3)
        set_run(p.add_run(v), 16, True, RGBColor(0x8B, 0x5E, 0x3C))
        bottom_border(p, 'B9AD95', '8')
    for ch, rs in groups.items():
        if ch:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            set_run(p.add_run(ch), 11, True, RGBColor(0x6B, 0x5B, 0x4A))
        tbl = doc.add_table(rows=0, cols=2)
        tbl.autofit = False
        for i, w in enumerate((7.2, 10.8)):
            tbl.columns[i].width = Cm(w)
        for r in rs:
            row = tbl.add_row()
            no_row_split(row)
            left, right = row.cells[0], row.cells[1]
            left.width = Cm(7.2); right.width = Cm(10.8)
            first_l = first_r = True
            for lab, src, tr in parts(r):
                src = clean(src); tr = clean(tr)
                if not src and not tr:
                    continue
                p = _cell_para(left, first_l)
                first_l = False
                if src:
                    set_run(p.add_run('【%s】' % lab), LABEL_PT, True,
                            LABEL_COLORS.get(lab, SRC_COLOR))
                    set_run(p.add_run(src), BODY_PT, False, SRC_COLOR)
                if tr:
                    p2 = _cell_para(right, first_r)
                    first_r = False
                    set_run(p2.add_run(tr), BODY_PT, False, TR_COLOR)
            _cell_bottom_border(left)
            _cell_bottom_border(right)


def build_volume(book, title, series, vol, rows, two, do_pdf=True):
    doc = Document()
    # Normal style
    st = doc.styles['Normal']
    st.font.name = FONT
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    st.font.size = Pt(BODY_PT)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.line_spacing = 1.15
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.5); sec.bottom_margin = Cm(1.4)
    sec.left_margin = Cm(1.5); sec.right_margin = Cm(1.5)
    add_title(doc, title, series, vol)
    # 標題頁單欄；內文另起 section
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    for si, section in enumerate(doc.sections):
        header_footer(section, title, vol)
    if two:
        # 雙欄＝左原文、右白話，逐段對照（與網站並排一致）
        _build_pairs_two_col(doc, rows)
    else:
        last_vol = last_chunk = None
        for r in rows:
            v = r.get('vol') or '卷首'
            ch = r.get('chunk') or ''
            if v != last_vol:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10 if last_vol else 0)
                p.paragraph_format.space_after = Pt(3)
                set_run(p.add_run(v), 16, True, RGBColor(0x8B, 0x5E, 0x3C))
                bottom_border(p, 'B9AD95', '8')
                last_vol = v; last_chunk = None
            if ch and ch != last_chunk:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(5)
                p.paragraph_format.space_after = Pt(2)
                set_run(p.add_run(ch), 11, True, RGBColor(0x6B, 0x5B, 0x4A))
                last_chunk = ch
            for lab, src, tr in parts(r):
                src = clean(src); tr = clean(tr)
                if not src and not tr:
                    continue
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                set_run(p.add_run('【%s】' % lab), LABEL_PT, True,
                        LABEL_COLORS.get(lab, SRC_COLOR))
                set_run(p.add_run(src), BODY_PT, False, SRC_COLOR)
                if tr:
                    p2 = doc.add_paragraph()
                    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p2.paragraph_format.left_indent = Cm(0.25)
                    p2.paragraph_format.space_before = Pt(0)
                    p2.paragraph_format.space_after = Pt(4)
                    p2.paragraph_format.line_spacing = 1.15
                    set_run(p2.add_run(tr), BODY_PT, False, TR_COLOR)
    layout = '雙欄' if two else '單欄'
    ddir, pdir = OUT[layout]
    os.makedirs(ddir, exist_ok=True); os.makedirs(pdir, exist_ok=True)
    safe_vol = vol.replace('/', '_').replace('\\', '_')
    base = '%s_%s_白話對照本_%s' % (title, safe_vol, layout)
    docx = os.path.join(ddir, base + '.docx')
    rewrite_headers(doc, title, vol)
    doc.save(docx)
    prof = 'file:///C:/Temp/lo_kaiti_' + uuid.uuid4().hex[:8]
    if not do_pdf:
        return docx, None, 'docx-only'
    # 先轉到暫存目錄再搬進目標目錄：OneDrive 目錄偶爾會讓 LibreOffice
    # 直接寫入失敗（Io Abort 27），轉到 C:\Temp 後複製可避開。
    tmpdir = os.path.join(os.environ.get('TEMP', r'C:\Temp'),
                          'lo_pdf_' + uuid.uuid4().hex[:8])
    os.makedirs(tmpdir, exist_ok=True)
    cmd = [SOFFICE, '--headless', '--norestore', '-env:UserInstallation=' + prof,
           '--convert-to', 'pdf', '--outdir', tmpdir, docx]
    try:
        subprocess.run(cmd, capture_output=True, timeout=1200)
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
    ap.add_argument('--book', default='')
    ap.add_argument('--vol', default='', help='只重建指定卷（如 卷上）')
    ap.add_argument('--layout', choices=('single', 'double'), default='')
    ap.add_argument('--no-pdf', action='store_true')
    a = ap.parse_args()
    for book, title, series in BOOKS:
        if a.book and a.book not in (book, title):
            continue
        rows = load_rows(book)
        vols = OrderedDict()
        for r in rows:
            vols.setdefault(r.get('vol') or '卷首', []).append(r)
        for vol, rs in vols.items():
            if a.vol and vol != a.vol:
                continue
            for two in (False, True):
                if a.layout == 'single' and two: continue
                if a.layout == 'double' and not two: continue
                print('build', book, vol, '雙欄' if two else '單欄', flush=True)
                docx, pdf, st = build_volume(book, title, series, vol, rs, two, not a.no_pdf)
                print('->', docx, pdf or 'PDF FAIL', st, flush=True)

if __name__ == '__main__':
    main()
