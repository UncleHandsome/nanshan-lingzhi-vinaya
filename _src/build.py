
import os, re, sys, json
from lxml import etree
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RAW = os.path.join(BASE, 'raw')
TMP = os.path.join(BASE, '_build')
os.makedirs(TMP, exist_ok=True)

TEI = 'http://www.tei-c.org/ns/1.0'
CB = 'http://www.cbeta.org/ns/1.0'
NS = {'tei': TEI, 'cb': CB}
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
SKIP_DIV = {'apparatus', 'cbeta-notes', 'xuzang-notes', 'add-notes', 'w'}
INLINE_SKIP = {'note', 'lb', 'pb', 'anchor', 'space', 'caesura', 'milestone', 'figure', 'graphic'}

FONT = 'DFKai-SB'
LATIN = 'Times New Roman'
BODY_PT = 11.5

BOOKS = [
    dict(key='01', files=['T40n1804'], title='四分律刪繁補闕行事鈔', prefix='四分律刪繁補闕行事鈔卷',
         series='南山三大部之一', author='唐·道宣律師　撰', juan='三卷（上、中、下，各分四）',
         canon='大正新脩大藏經', vol='第40冊', no='No.1804', cid='T40n1804',
         note='大正藏本。原書新式標點，校勘注從略。'),
    dict(key='02', files=['X39n0714', 'X40n0714'], title='四分律含注戒本疏', prefix='四分律含注戒本疏行宗記卷',
         series='南山三大部之二（戒疏）', author='唐·道宣律師　撰　宋·元照律師　述記', juan='四卷',
         canon='卍新纂大日本續藏經', vol='第39–40冊', no='No.714', cid='X39n0714、X40n0714',
         note='與《行宗記》合會本。疏文以「【疏】」標起，記文以小型字排印。'),
    dict(key='03', files=['X41n0728'], title='四分律刪補隨機羯磨疏', prefix='四分律刪補隨機羯磨疏濟緣記卷',
         series='南山三大部之三（業疏）', author='唐·道宣律師　撰　宋·元照律師　述記', juan='四卷',
         canon='卍新纂大日本續藏經', vol='第41冊', no='No.728', cid='X41n0728',
         note='與《濟緣記》合會本。疏文以「【疏】」標起，記文以小型字排印。底本此篇標點從簡。'),
    dict(key='04', files=['X40n0724'], title='四分律比丘尼鈔', prefix='四分律比丘尼鈔卷',
         series='南山五大部之四', author='唐·道宣律師　述', juan='三卷（上、中、下，各分上下）',
         canon='卍新纂大日本續藏經', vol='第40冊', no='No.724', cid='X40n0724',
         note='底本此篇標點從簡。'),
    dict(key='05', files=['X44n0747'], title='四分律拾毗尼義鈔', prefix='四分律拾毗尼義鈔卷',
         series='南山五大部之五', author='唐·道宣律師　撰', juan='二卷（上、中；舊稱三卷）',
         canon='卍新纂大日本續藏經', vol='第44冊', no='No.747', cid='X44n0747',
         note='舊稱三卷，續藏所收僅上、中二卷。底本此篇標點從簡。'),
]

def clean(s):
    s = s.replace('\r', '').replace('\n', '')
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s

def build_gaiji(root):
    m = {}
    for c in root.iter('{%s}char' % TEI):
        xid = c.get(XMLID)
        disp = None; norm = None; compo = None; uni = None
        for mp in c.findall('tei:mapping', NS):
            t = mp.get('type'); v = (mp.text or '').strip()
            if t == 'normal_unicode' and v: uni = v
            elif t == 'unicode' and v and uni is None: uni = v
        for cp in c.findall('tei:charProp', NS):
            ln = cp.findtext('tei:localName', default='', namespaces=NS)
            val = cp.findtext('tei:value', default='', namespaces=NS)
            if ln == 'normalized form': norm = val
            elif ln == 'composition': compo = val
        if uni:
            try: disp = chr(int(uni.replace('U+', ''), 16))
            except Exception: disp = None
        if not disp and norm: disp = norm
        if not disp and compo: disp = compo
        if disp:
            if xid: m[xid] = disp
            for mp in c.findall('tei:mapping', NS):
                d = mp.get('{%s}dec' % CB)
                if d: m[int(d)] = disp
    return m

def text_of(el, gaiji):
    parts = []
    def rec(node):
        if node.text: parts.append(node.text)
        for ch in node:
            ln = etree.QName(ch).localname
            if ln in INLINE_SKIP: pass
            elif ln == 'g':
                ref = (ch.get('ref') or '').lstrip('#')
                parts.append(gaiji.get(ref, ch.text or ''))
            elif ln == 'app':
                lem = ch.find('tei:lem', NS)
                if lem is not None: rec(lem)
                else:
                    for r in ch.findall('tei:rdg', NS): rec(r)
            else: rec(ch)
            if ch.tail: parts.append(ch.tail)
    rec(el)
    return clean(''.join(parts))

def walk(el, role, blocks, gaiji, skip_mulu=False):
    for ch in el:
        ln = etree.QName(ch).localname
        if ln == 'div':
            t = ch.get('type') or ''
            if t in SKIP_DIV: continue
            nr = 'commentary' if t == 'commentary' else ('orig' if t == 'orig' else role)
            has_head = ch.find('head', NS) is not None
            walk(ch, nr, blocks, gaiji, skip_mulu=has_head)
        elif ln == 'juan':
            if ch.get('fun') == 'open':
                label = ''
                mu = ch.find('cb:mulu', NS)
                if mu is not None: label = text_of(mu, gaiji).strip()
                blocks.append({'kind': 'juan', 'text': label, 'role': role})
        elif ln == 'mulu':
            if not skip_mulu:
                t = text_of(ch, gaiji).strip()
                if t: blocks.append({'kind': 'sub', 'text': t, 'role': role})
        elif ln == 'head':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'head', 'text': t, 'role': role})
        elif ln in ('p', 'item'):
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'p', 'text': t, 'role': role})
        elif ln == 'l':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'verse', 'text': t, 'role': role})
        elif ln == 'byline':
            t = text_of(ch, gaiji).strip()
            if t: blocks.append({'kind': 'byline', 'text': t, 'role': role})
        elif ln in ('lg', 'list'):
            walk(ch, role, blocks, gaiji, skip_mulu=skip_mulu)
        elif ln in ('note', 'anchor', 'lb', 'pb', 'space', 'caesura', 'milestone', 'table', 'figure', 'graphic'):
            continue
        else:
            walk(ch, role, blocks, gaiji, skip_mulu=skip_mulu)

def parse_book(b):
    blocks = []
    for fn in b['files']:
        tree = etree.parse(os.path.join(RAW, fn + '.xml'))
        root = tree.getroot()
        gaiji = build_gaiji(root)
        body = root.find('.//tei:text/tei:body', NS)
        walk(body, None, blocks, gaiji)
    return blocks

def fix_pua(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF or 0xF0000 <= o <= 0xFFFFD:
            out.append('\u25a1')
        else:
            out.append(ch)
    return ''.join(out)

def set_run(run, size, bold=False, color=None, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = LATIN
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), LATIN)
    rFonts.set(qn('w:hAnsi'), LATIN)
    rFonts.set(qn('w:eastAsia'), font)
    if color is not None:
        run.font.color.rgb = color

def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    return run

def para_border_bottom(p):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1'); bottom.set(qn('w:color'), 'BFBFBF')
    pbdr.append(bottom); pPr.append(pbdr)

def _norm_head(t):
    t = t.replace('\u3000', '').replace(' ', '')
    for ch in '\u25cb\u25ce\u25cf\u3007':
        t = t.replace(ch, '')
    return t.strip()

def tidy_blocks(blocks):
    out = []
    n = len(blocks)
    for i, b in enumerate(blocks):
        if b['kind'] in ('sub', 'head'):
            if '\uff5e' in b['text'] or '~' in b['text']:
                continue
            if b['kind'] == 'sub' and i + 1 < n and blocks[i+1]['kind'] in ('head', 'sub'):
                if _norm_head(blocks[i+1]['text']) == _norm_head(b['text']):
                    continue
        out.append(b)
    return out

def build_docx(b, blocks, out_docx):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = LATIN
    st.font.size = Pt(BODY_PT)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.2); sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)

    # ---- cover ----
    def blank(n=1, pt=BODY_PT):
        for _ in range(n):
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(0)
            r = p.add_run(''); r.font.size = Pt(pt)

    blank(5)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(30)
    set_run(p.add_run(b['series']), 13, color=RGBColor(0x66, 0x66, 0x66))

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    set_run(p.add_run(b['title']), 30, bold=True)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run(b['juan']), 14)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(60)
    set_run(p.add_run(b['author']), 14)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run('底　本'), 10.5, color=RGBColor(0x80, 0x80, 0x80))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run('《' + b['canon'] + '》' + b['vol'] + '　' + b['no']), 10.5, color=RGBColor(0x80, 0x80, 0x80))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run('CBETA 電子佛典（' + b['cid'] + '）'), 10.5, color=RGBColor(0x80, 0x80, 0x80))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(b['note']), 9.5, color=RGBColor(0x99, 0x99, 0x99))

    # ---- body section ----
    new_sec = doc.add_section(WD_SECTION.NEW_PAGE)
    new_sec.header.is_linked_to_previous = False
    new_sec.footer.is_linked_to_previous = False
    new_sec.page_width = Cm(21.0); new_sec.page_height = Cm(29.7)
    new_sec.top_margin = Cm(2.2); new_sec.bottom_margin = Cm(2.0)
    new_sec.left_margin = Cm(2.2); new_sec.right_margin = Cm(2.2)

    hp = new_sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run(b['title']), 8.5, color=RGBColor(0x99, 0x99, 0x99))
    para_border_bottom(hp)

    fp = new_sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(fp.add_run('— '), 9.5, color=RGBColor(0x80, 0x80, 0x80))
    fr = add_field(fp, ' PAGE ')
    fr.font.size = Pt(9.5); fr.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    set_run(fp.add_run(' —'), 9.5, color=RGBColor(0x80, 0x80, 0x80))

    sectPr = new_sec._sectPr
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '1'); sectPr.append(pg)

    first_juan = True
    prev_head = None
    for blk in blocks:
        k = blk['kind']; t = fix_pua(blk['text']); role = blk['role']
        if k in ('head', 'sub'):
            if t == prev_head:
                continue
            prev_head = t
        else:
            prev_head = None
        if k == 'juan':
            p = doc.add_paragraph(style='Heading 1')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.space_before = Pt(0)
            pf.space_after = Pt(28)
            pf.keep_with_next = True
            pf.page_break_before = True
            first_juan = False
            set_run(p.add_run(b['prefix'] + t), 20, bold=True, color=RGBColor(0, 0, 0))
        elif k == 'head':
            p = doc.add_paragraph(style='Heading 2')
            pf = p.paragraph_format
            pf.space_before = Pt(16); pf.space_after = Pt(8)
            pf.keep_with_next = True
            set_run(p.add_run(t), 14, bold=True, color=RGBColor(0, 0, 0))
        elif k == 'sub':
            p = doc.add_paragraph(style='Heading 3')
            pf = p.paragraph_format
            pf.space_before = Pt(12); pf.space_after = Pt(4)
            pf.keep_with_next = True
            set_run(p.add_run(t), 12, bold=True, color=RGBColor(0, 0, 0))
        elif k == 'byline':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.space_before = Pt(4); pf.space_after = Pt(18)
            set_run(p.add_run(t), 10.5, color=RGBColor(0x70, 0x70, 0x70))
        elif k == 'verse':
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.space_before = Pt(0); pf.space_after = Pt(0)
            pf.left_indent = Pt(34); pf.line_spacing = 1.45
            set_run(p.add_run(t), BODY_PT)
        else:  # p
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf = p.paragraph_format
            if role == 'commentary':
                pf.left_indent = Pt(14)
                pf.first_line_indent = Pt(14)
                pf.space_before = Pt(4); pf.space_after = Pt(2)
                pf.line_spacing = 1.35
                set_run(p.add_run(t), 10, color=RGBColor(0x4d, 0x4d, 0x4d))
            else:
                pf.first_line_indent = Pt(BODY_PT * 2)
                pf.space_before = Pt(0); pf.space_after = Pt(0)
                pf.line_spacing = 1.5
                set_run(p.add_run(t), BODY_PT)

    doc.save(out_docx)

def build_txt(b, blocks, out_txt):
    lines = []
    lines.append(b['title'])
    lines.append(b['series'] + '　' + b['author'] + '　' + b['juan'])
    lines.append('底本：《%s》%s %s（%s）' % (b['canon'], b['vol'], b['no'], b['cid']))
    lines.append('')
    for blk in blocks:
        t = fix_pua(blk['text'])
        if blk['kind'] == 'juan':
            lines.append('')
            lines.append('【' + b['prefix'] + t + '】')
            lines.append('')
        elif blk['kind'] in ('head', 'sub'):
            lines.append('')
            lines.append(t)
            lines.append('')
        elif blk['kind'] == 'byline':
            lines.append('　　' + t)
        elif blk['kind'] == 'verse':
            lines.append('　　' + t)
        else:
            if blk['role'] == 'commentary':
                lines.append('　' + t)
            else:
                lines.append('　　' + t)
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    want = sys.argv[1:] or [b['key'] for b in BOOKS]
    for b in BOOKS:
        if b['key'] not in want: continue
        blocks = tidy_blocks(parse_book(b))
        docx = os.path.join(TMP, b['key'] + '_' + b['title'] + '.docx')
        txt = os.path.join(TMP, b['key'] + '_' + b['title'] + '.txt')
        build_docx(b, blocks, docx)
        build_txt(b, blocks, txt)
        print('OK', b['key'], b['title'], len(blocks), 'blocks ->', docx)
