# -*- coding: utf-8 -*-
"""未譯段落清單 → DOCX → PDF。"""
import os, io, json, subprocess

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DATA = os.path.join(B, 'AI語譯', '_work', 'untranslated.json')
DOCX = os.path.join(B, '白話', '未譯段落清單.docx')
PDF = os.path.join(B, '白話', '未譯段落清單.pdf')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'
FONT = 'DFKai-SB'
LATIN = 'Times New Roman'


def set_run(r, size, bold=False, color=None):
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
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


def build():
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    data = json.load(io.open(DATA, encoding='utf-8'))
    total = sum(len(b['rows']) for b in data)
    chars = sum(x['chars'] for b in data for x in b['rows'])

    doc = Document()
    st = doc.styles['Normal']
    st.font.name = LATIN
    st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(1.7)
    s.bottom_margin = Cm(1.6)
    s.left_margin = Cm(1.8)
    s.right_margin = Cm(1.8)

    # footer page number
    p = s.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('— '), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    run = p.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = ' PAGE '
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    set_run(run, 8.5, color=RGBColor(0x88, 0x88, 0x88))
    set_run(p.add_run(' —'), 8.5, color=RGBColor(0x88, 0x88, 0x88))

    # cover
    for _ in range(5):
        doc.add_paragraph().add_run('')
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('未譯段落清單'), 26, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_run(p.add_run('《南山三大部》白話對照本'), 13, color=RGBColor(0x55, 0x55, 0x55))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    set_run(p.add_run('%d 段　約 %s 字' % (total, format(chars, ','))), 12, color=RGBColor(0x77, 0x77, 0x77))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('2026-11-06　掃描'), 10, color=RGBColor(0x99, 0x99, 0x99))
    doc.add_page_break()

    # summary
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run('一、總覽'), 15, bold=True)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('判定方式：譯文去掉段首標籤與空白後，與原文完全相同（≥10 字），或相似度 ≥ 0.95（≥20 字）；'
                      '已排除篇名、目錄、譯款等非正文行。'), 9, color=RGBColor(0x66, 0x66, 0x66))
    t = doc.add_table(rows=1, cols=3)
    t.style = 'Table Grid'
    hdr = t.rows[0].cells
    for i, h in enumerate(['書', '未譯段數', '約字數']):
        set_run(hdr[i].paragraphs[0].add_run(h), 10, bold=True)
    for b in data:
        if not b['rows']:
            continue
        cells = t.add_row().cells
        set_run(cells[0].paragraphs[0].add_run(b['title']), 9.5)
        set_run(cells[1].paragraphs[0].add_run(str(len(b['rows']))), 9.5)
        set_run(cells[2].paragraphs[0].add_run(format(sum(x['chars'] for x in b['rows']), ',')), 9.5)
    cells = t.add_row().cells
    set_run(cells[0].paragraphs[0].add_run('合計'), 9.5, bold=True)
    set_run(cells[1].paragraphs[0].add_run(str(total)), 9.5, bold=True)
    set_run(cells[2].paragraphs[0].add_run(format(chars, ',')), 9.5, bold=True)

    # details
    for b in data:
        if not b['rows']:
            continue
        p = doc.add_paragraph()
        p.paragraph_format.page_break_before = True
        p.paragraph_format.space_after = Pt(6)
        set_run(p.add_run('%s（%d 段）' % (b['title'], len(b['rows']))), 15, bold=True)
        cur = None
        for x in b['rows']:
            if x['key'] != cur:
                cur = x['key']
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(2)
                set_run(p.add_run(cur), 11, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(0)
            set_run(p.add_run('段 %d　%d 字' % (x['seg'], x['chars'])), 8.5, color=RGBColor(0x88, 0x88, 0x88))
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Pt(10)
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.line_spacing = 1.25
            set_run(p.add_run(x['src']), 9.5, color=RGBColor(0x6b, 0x5b, 0x4a))
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Pt(10)
            pf.space_before = Pt(0)
            pf.space_after = Pt(6)
            pf.line_spacing = 1.25
            set_run(p.add_run(x['tr']), 9, color=RGBColor(0x8a, 0x8a, 0x8a))

    doc.save(DOCX)
    print('docx', DOCX)
    subprocess.run([SOFFICE, '--headless', '--norestore',
                    '-env:UserInstallation=file:///C:/Temp/lo_profile_untrans',
                    '--convert-to', 'pdf', '--outdir', os.path.join(B, '白話'), DOCX],
                   capture_output=True)
    print('pdf', PDF)


if __name__ == '__main__':
    build()
