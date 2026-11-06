# -*- coding: utf-8 -*-
"""由 附錄_名相與度量衡.md 產生 docs/appendix.html 與 白話/附錄_名相與度量衡.docx"""
import os, io, re, html, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MD = os.path.join(B, '附錄_名相與度量衡.md')
SITE = os.path.join(B, 'docs')
OUTDOCX = os.path.join(B, '白話', '附錄_名相與度量衡.docx')

FONT = 'DFKai-SB'
LATIN = 'Times New Roman'


def parse(md):
    """Return list of blocks: ('h2', text) / ('h3', text) / ('p', text) / ('table', rows) / ('quote', text)"""
    lines = md.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith('# '):
            blocks.append(('h1', s[2:].strip()))
            i += 1
        elif s.startswith('## '):
            blocks.append(('h2', s[3:].strip()))
            i += 1
        elif s.startswith('### '):
            blocks.append(('h3', s[4:].strip()))
            i += 1
        elif s.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(('quote', ' '.join(buf)))
        elif s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not re.match(r'^[-: ]+$', ''.join(cells)):
                    rows.append(cells)
                i += 1
            blocks.append(('table', rows))
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '|', '>')):
                buf.append(lines[i].strip())
                i += 1
            blocks.append(('p', ' '.join(buf)))
    return blocks


def inline_html(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    return t


def to_html(blocks):
    out = []
    for kind, val in blocks:
        if kind == 'h1':
            out.append('<h1>' + inline_html(val) + '</h1>')
        elif kind == 'h2':
            out.append('<h2>' + inline_html(val) + '</h2>')
        elif kind == 'h3':
            out.append('<h3 style="font-size:1.05rem;margin:1.4rem 0 .4rem">' + inline_html(val) + '</h3>')
        elif kind == 'quote':
            out.append('<p class="intro">' + inline_html(val) + '</p>')
        elif kind == 'p':
            out.append('<p>' + inline_html(val) + '</p>')
        elif kind == 'table':
            rows = val
            parts = ['<table>']
            for ri, r in enumerate(rows):
                tag = 'th' if ri == 0 else 'td'
                parts.append('<tr>' + ''.join('<%s>%s</%s>' % (tag, inline_html(c), tag) for c in r) + '</tr>')
            parts.append('</table>')
            out.append(''.join(parts))
    return ''.join(out)


CSS_EXTRA = """
main table{border-collapse:collapse;width:100%;margin:.8rem 0 1.4rem;font-size:14.5px}
main table th,main table td{border:1px solid var(--line);padding:.38rem .55rem;text-align:left;vertical-align:top;line-height:1.6}
main table th{background:#f4efe2;font-weight:600}
main h3{margin-top:1.4rem}
main p{line-height:1.9}
"""


def build_html(blocks):
    body = to_html(blocks)
    books = [('xingshichao', '四分律刪繁補闕行事鈔'), ('jieshu', '四分律含注戒本疏'),
             ('yeshu', '四分律刪補隨機羯磨疏'), ('zhichi', '四分律行事鈔資持記'),
             ('nicao', '四分比丘尼鈔'), ('yichao', '四分律拾毗尼義鈔')]
    nav = ['<nav><h1><a href="index.html">南山律典・白話對照</a></h1>',
           '<div class="grp"><b>全書</b><a href="index.html">目錄</a>'
           '<a href="search.html">全文搜尋</a><a href="appendix.html">附錄</a></div>',
           '<div class="grp"><b>分卷</b><div class="bklist">']
    for out, title in books:
        vols = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SITE, out, '*.html')))
        if not vols:
            continue
        nav.append('<details class="navj"><summary>' + title + '</summary><ul>')
        for v in vols:
            nav.append('<li><a href="%s/%s.html">%s</a></li>' % (out, v, v))
        nav.append('</ul></details>')
    nav.append('</div></div></nav>')
    nav = ''.join(nav)
    footer = ('<footer style="margin:3.5rem 0 0;padding-top:1.2rem;border-top:1px solid var(--line);'
              'color:var(--fg2);font-size:12.5px;line-height:1.7">'
              '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯與附錄：本站自製。'
              '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權。'
              '</footer>')
    doc = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>附錄：名相、音注與度量衡｜南山律典・白話對照</title>'
           '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
           '<link rel="stylesheet" href="style.css?v=6"><style>' + CSS_EXTRA + '</style></head>'
           '<body><div class="wrap">' + nav + '<main>' + body +
           '<p class="intro" style="margin-top:2rem">回 <a href="index.html">目錄</a></p>'
           + footer + '</main></div></body></html>')
    p = os.path.join(SITE, 'appendix.html')
    io.open(p, 'w', encoding='utf-8').write(doc)
    return p


def build_docx(blocks):
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

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
    set_run(p.add_run('附錄'), 24, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_run(p.add_run('名相、音注與度量衡'), 18, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('《南山三大部》白話對照本 附錄'), 11, color=RGBColor(0x77, 0x77, 0x77))
    doc.add_page_break()

    for kind, val in blocks:
        if kind == 'h1':
            continue
        if kind == 'h2':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            set_run(p.add_run(val), 15, bold=True)
        elif kind == 'h3':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            set_run(p.add_run(val), 12.5, bold=True)
        elif kind == 'quote':
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(12)
            p.paragraph_format.space_after = Pt(6)
            set_run(p.add_run(val), 9.5, color=RGBColor(0x77, 0x77, 0x77))
        elif kind == 'p':
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.first_line_indent = Pt(24)
            pf.line_spacing = 1.4
            pf.space_after = Pt(4)
            txt = val.replace('**', '')
            set_run(p.add_run(txt), 11)
        elif kind == 'table':
            rows = val
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=0, cols=ncol)
            t.style = 'Table Grid'
            t.autofit = True
            for ri, r in enumerate(rows):
                cells = t.add_row().cells
                for ci in range(ncol):
                    txt = r[ci] if ci < len(r) else ''
                    para = cells[ci].paragraphs[0]
                    para.paragraph_format.space_after = Pt(0)
                    set_run(para.add_run(txt.replace('**', '')), 9, bold=(ri == 0))
            doc.add_paragraph().paragraph_format.space_after = Pt(2)

    doc.save(OUTDOCX)
    return OUTDOCX


if __name__ == '__main__':
    blocks = parse(io.open(MD, encoding='utf-8').read())
    print('blocks', len(blocks), 'tables', sum(1 for k, v in blocks if k == 'table'))
    print('html ->', build_html(blocks))
    print('docx ->', build_docx(blocks))
