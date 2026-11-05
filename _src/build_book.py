# -*- coding: utf-8 -*-
import os, io, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
try:
    SRCDIR = sys.argv[4] if len(sys.argv) > 4 else sys.argv[1]
except Exception:
    SRCDIR = None
FONT = 'DFKai-SB'; LATIN = 'Times New Roman'

def set_run(r, size, bold=False, color=None):
    r.font.size = Pt(size); r.font.bold = bold; r.font.name = LATIN
    rPr = r._element.get_or_add_rPr(); rf = rPr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'), LATIN); rf.set(qn('w:hAnsi'), LATIN); rf.set(qn('w:eastAsia'), FONT)
    if color is not None: r.font.color.rgb = color

def shade(p, c):
    pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), c); pPr.append(shd)

def left_border(p, c):
    pPr = p._p.get_or_add_pPr(); pb = OxmlElement('w:pBdr'); l = OxmlElement('w:left')
    l.set(qn('w:val'), 'single'); l.set(qn('w:sz'), '12'); l.set(qn('w:space'), '6'); l.set(qn('w:color'), c)
    pb.append(l); pPr.append(pb)

def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2); return run

def load(book):
    J = os.path.join(BASE, 'TXT_句讀', book)
    S = os.path.join(BASE, 'TXT_分卷', SRCDIR); T = os.path.join(BASE, 'AI語譯', 'out', book)
    out = []
    files = sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x))
    for f in files:
        if not f.endswith('.txt'): continue
        key = f[:-4]
        jp = os.path.join(J, key + '.txt')
        srcfile = jp if os.path.exists(jp) else os.path.join(S, f)
        sp = [x.strip() for x in io.open(srcfile, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T, key + '.txt'), encoding='utf-8').read()) if x.strip()]
        if not tp: continue
        juan = key.split('_', 1)[1] if '_' in key else ''
        keep = [i for i, x in enumerate(sp) if not re.match(r'^(No\.\d+|四分律刪補隨機羯磨疏卷|四分律行事鈔卷)', x)]
        if len(keep) != len(sp):
            sp = [sp[i] for i in keep]
            tp = [tp[i] for i in keep if i < len(tp)]
        out.append(dict(key=key, juan=juan, src=sp, tr=tp))
    return out

def build(chunks, mode, title, path, single=False):
    doc = Document()
    st = doc.styles['Normal']; st.font.name = LATIN; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21.0); s.page_height = Cm(29.7)
    s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.5); s.left_margin = Cm(1.7); s.right_margin = Cm(1.7)
    for _ in range(4):
        doc.add_paragraph().add_run('')
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20); set_run(p.add_run(title), 24, bold=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10); set_run(p.add_run('白話語譯‧' + ('對照本' if mode == 'dui' else '全白話本')), 14)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('AI 語譯稿（flash 初譯 + 校對 + 人工核實）'), 9.5, color=RGBColor(0x77,0x77,0x77))

    ns = doc.add_section(WD_SECTION.NEW_PAGE)
    ns.header.is_linked_to_previous = False; ns.footer.is_linked_to_previous = False
    ns.page_width = Cm(21.0); ns.page_height = Cm(29.7)
    ns.top_margin = Cm(1.6); ns.bottom_margin = Cm(1.5); ns.left_margin = Cm(1.7); ns.right_margin = Cm(1.7)
    hp = ns.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run(title.replace('　', ' ')), 8, color=RGBColor(0xaa,0xaa,0xaa))
    fp = ns.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88,0x88,0x88))
    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(8.5); fr.font.color.rgb = RGBColor(0x88,0x88,0x88)
    set_run(fp.add_run(' —'), 8.5, color=RGBColor(0x88,0x88,0x88))

    prev = None; first = True
    jp = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$')
    for c in chunks:
        if (not single) and c['juan'] and c['juan'] != prev:
            p = doc.add_paragraph(style='Heading 1'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format; pf.page_break_before = (not first); pf.keep_with_next = True
            pf.space_before = Pt(0); pf.space_after = Pt(10)
            set_run(p.add_run(title + '　' + c['juan']), 15, bold=True)
            first = False; prev = c['juan']
        sp, tp = c['src'], c['tr']
        if len(sp) != len(tp):
            doc.add_paragraph('[段數不合：原文 %d，譯文 %d]' % (len(sp), len(tp)))
        m = min(len(sp), len(tp))
        if mode == 'dui':
            for i in range(m):
                if jp.match(sp[i]) and sp[i] == tp[i]:
                    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    q.paragraph_format.space_before = Pt(2); q.paragraph_format.space_after = Pt(1)
                    set_run(q.add_run(sp[i]), 10, color=RGBColor(0x55,0x55,0x55))
                    continue
                short = len(sp[i]) < 20 and len(tp[i]) < 30
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(1 if short else 5); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = (len(sp[i]) < 60); qf.keep_with_next = True
                set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(tp[i]) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(0 if short else 2); af.space_after = Pt(1 if short else 4)
                set_run(a.add_run(tp[i]), 12)
        else:
            for t in tp[:m]:
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(t) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.3; af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(t), 12)
    doc.save(path)
    return len(doc.paragraphs)

if __name__ == '__main__':
    SRCDIR_G = sys.argv[4] if len(sys.argv) > 4 else sys.argv[1]
    book = sys.argv[1]; title = sys.argv[2]; prefix = sys.argv[3]
    chunks = load(book)
    CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
    groups = {}
    for c in chunks:
        j = c['juan'].split('之')[0] if c['juan'] else '全'
        if j == '卷首': j = '卷一'
        groups.setdefault(j, []).append(c)
    def jnum(k):
        m = re.match(r'^卷([一二三四五六七八九十]+)$', k)
        return CN.get(m.group(1), 99) if m else 99
    order = sorted(groups.keys(), key=jnum)
    # merge 卷首(卷一) into 卷一上 if present
    if '卷一' in groups:
        sub = [k for k in order if k != '卷一' and k.startswith('卷一')]
        if sub:
            groups[sub[0]] = groups.pop('卷一') + groups[sub[0]]
            order = sorted(groups.keys(), key=jnum)
    assert sum(len(groups[k]) for k in order) == len(chunks)
    for mode, label in (('dui', '白話對照本'),):
        for j in order:
            sub = groups[j]
            nm = prefix if j == '全' else '%s_%s' % (prefix, j)
            path = os.path.join(BASE, '白話', '%s_%s.docx' % (nm, label))
            n = build(sub, mode, title + ('　' + j if j != '全' else ''), path, single=True)
            print(mode, j, len(sub), 'chunks', n, 'paras')
