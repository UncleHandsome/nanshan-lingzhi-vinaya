
import os, re, json, io, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(BASE, '_src')
OUT = os.path.join(BASE, '白話')
os.makedirs(OUT, exist_ok=True)

FONT = 'DFKai-SB'
SONG = 'DFKai-SB'
LATIN = 'Times New Roman'

secs = json.load(io.open(os.path.join(SRC, 'secs.json'), encoding='utf-8'))

def load_trans(fn):
    d = {}
    cur = None
    buf = []
    for line in io.open(os.path.join(SRC, 'trans2', fn), encoding='utf-8').read().split('\n'):
        m = re.match(r'^@(\d+)\s*$', line.strip())
        if m:
            if cur is not None:
                d[cur] = '\n'.join(buf).strip()
            cur = int(m.group(1)); buf = []
        else:
            buf.append(line)
    if cur is not None:
        d[cur] = '\n'.join(buf).strip()
    return d

T = {1: {}, 2: {}, 3: {}}
T[1].update(load_trans('s01a.txt'))
T[1].update(load_trans('s01b.txt'))
T[2] = load_trans('s02.txt')
T[3] = load_trans('s03.txt')

SECTION_META = {
    1: dict(title='四分律刪繁補闕行事鈔序', plain='作者序', gloss='道宣律師自序，說明作鈔的緣起、體例與十門大意'),
    2: dict(title='標宗顯德篇第一', plain='第一篇　標舉宗旨，彰顯戒德', gloss='明戒法、戒體、戒行、戒相四科，並廣引經論讚戒、誡破戒'),
    3: dict(title='集僧通局篇第二', plain='第二篇　集僧的通局', gloss='明集僧的軌度、自然界與作法界的範圍，以及四種僧數'),
}

def set_run(run, size, bold=False, color=None, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = LATIN
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), LATIN); rFonts.set(qn('w:hAnsi'), LATIN)
    rFonts.set(qn('w:eastAsia'), font)
    if color is not None:
        run.font.color.rgb = color

def shade(p, hexcolor):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    pPr.append(shd)

def left_border(p, hexcolor):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single'); left.set(qn('w:sz'), '12')
    left.set(qn('w:space'), '6'); left.set(qn('w:color'), hexcolor)
    pbdr.append(left); pPr.append(pbdr)

def bottom_border(p, hexcolor):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '4')
    b.set(qn('w:space'), '1'); b.set(qn('w:color'), hexcolor)
    pbdr.append(b); pPr.append(pbdr)

def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    return run

NAME_RE = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$')

def load_notes(fn):
    d = {}
    cur = None; buf = []
    for line in io.open(os.path.join(SRC, 'trans2', fn), encoding='utf-8').read().split('\n'):
        m = re.match(r'^@(\d+)\.(\d+)\s*$', line.strip())
        if m:
            if cur: d[cur] = '\n'.join(buf).strip()
            cur = m.group(1) + '.' + m.group(2); buf = []
        else:
            buf.append(line)
    if cur: d[cur] = '\n'.join(buf).strip()
    return d

NOTES = load_notes('notes.txt')

def add_note(doc, text):
    for i, line in enumerate([x for x in text.split('\n') if x.strip()]):
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        qf = q.paragraph_format
        qf.left_indent = Pt(24); qf.first_line_indent = Pt(0)
        qf.line_spacing = 1.25; qf.space_before = Pt(1); qf.space_after = Pt(3)
        set_run(q.add_run('註　' if i == 0 else '　　'), 9, bold=True, color=RGBColor(0x8a, 0x6d, 0x3b))
        set_run(q.add_run(line), 9, color=RGBColor(0x5f, 0x5f, 0x5f))

def build(mode, out_docx):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = LATIN; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.7); sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.8); sec.right_margin = Cm(1.8)

    # cover
    for _ in range(3):
        p = doc.add_paragraph(); p.add_run(''); p.paragraph_format.space_after = Pt(0)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(26)
    set_run(p.add_run('南山三大部之一'), 13, color=RGBColor(0x77, 0x77, 0x77))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('四分律刪繁補闕行事鈔'), 26, bold=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    set_run(p.add_run('白話語譯' + ('‧對照本' if mode == 'dui' else '‧全白話本') + '（修訂版）'), 15)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('卷一（上之一）'), 13, color=RGBColor(0x55, 0x55, 0x55))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(30)
    set_run(p.add_run('序　·　標宗顯德篇第一　·　集僧通局篇第二'), 11, color=RGBColor(0x55, 0x55, 0x55))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    set_run(p.add_run('唐·道宣律師　撰'), 12)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(36)
    set_run(p.add_run('底本：《大正新脩大藏經》第40冊 No.1804（CBETA）'), 9.5, color=RGBColor(0x99, 0x99, 0x99))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('全書三十篇，本冊為第一批（序、第一、二篇）；其餘待續。'), 9.5, color=RGBColor(0x99, 0x99, 0x99))

    # body section
    ns = doc.add_section(WD_SECTION.NEW_PAGE)
    ns.header.is_linked_to_previous = False
    ns.footer.is_linked_to_previous = False
    ns.page_width = Cm(21.0); ns.page_height = Cm(29.7)
    ns.top_margin = Cm(1.7); ns.bottom_margin = Cm(1.6)
    ns.left_margin = Cm(1.8); ns.right_margin = Cm(1.8)
    hp = ns.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run('行事鈔白話' + ('（對照）' if mode == 'dui' else '')), 8, color=RGBColor(0xaa, 0xaa, 0xaa))
    bottom_border(hp, 'DDDDDD')
    fp = ns.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(8.5); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    set_run(fp.add_run(' —'), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '1'); ns._sectPr.append(pg)

    # 凡例
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(12)
    set_run(p.add_run('凡　例'), 16, bold=True)
    rules = [
        ('底本', '《大正新脩大藏經》第40冊 No.1804《四分律刪繁補闕行事鈔》，文字取自 CBETA 電子佛典，未改字。'),
        ('譯文', '以現代漢語語譯，力求貼近原意；律學術語酌加簡釋，不作過度發揮。'),
        ('分段', '依原文段落逐段對譯；「對照本」先列原文，次列語譯，段次一一對應。'),
        ('標點', '原文原有新式標點；無標點處由譯文自行句讀。'),
        ('校勘', '原書腳注校記從略。'),
        ('用途', '本書為初稿，供通讀理解之用；引用、講說請覆核原文。'),
    ]
    for k, v in rules:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = p.paragraph_format; pf.first_line_indent = Pt(20); pf.line_spacing = 1.4; pf.space_after = Pt(2)
        set_run(p.add_run('【' + k + '】'), 10.5, bold=True)
        set_run(p.add_run(v), 10.5)

    # 目次
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(28); p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('目　次'), 16, bold=True)
    toc = [('序', '四分律刪繁補闕行事鈔序'), ('第一篇', '標宗顯德篇第一'), ('第二篇', '集僧通局篇第二')]
    for a, b in toc:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
        set_run(p.add_run(a + '　'), 10, color=RGBColor(0x88, 0x88, 0x88))
        set_run(p.add_run(b), 10)
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(18)
    set_run(p.add_run('（全書三十篇，以下待續。）'), 10, color=RGBColor(0x99, 0x99, 0x99))

    # content
    first = True
    for si in (1, 2, 3):
        meta = SECTION_META[si]
        items = secs[si]['items']
        p = doc.add_paragraph(style='Heading 1')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(0); pf.space_after = Pt(4)
        pf.page_break_before = True; pf.keep_with_next = True
        first = False
        set_run(p.add_run(meta['title']), 17, bold=True, color=RGBColor(0, 0, 0))
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        set_run(p.add_run(meta['plain']), 10, color=RGBColor(0x88, 0x88, 0x88))
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(12)
        set_run(p.add_run(meta['gloss']), 9, color=RGBColor(0xaa, 0xaa, 0xaa))

        for idx, raw in enumerate(items, start=1):
            if not raw.strip():
                continue
            if NAME_RE.match(raw.strip()):
                p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pf = p.paragraph_format; pf.space_before = Pt(0); pf.space_after = Pt(0); pf.line_spacing = 1.15
                set_run(p.add_run(raw.strip()), 10, color=RGBColor(0x66, 0x66, 0x66))
                continue
            tr = T[si].get(idx)
            if mode == 'dui':
                p = doc.add_paragraph()
                pf = p.paragraph_format
                pf.left_indent = Pt(6); pf.space_before = Pt(7); pf.space_after = Pt(0); pf.line_spacing = 1.2; pf.keep_with_next = True
                set_run(p.add_run(raw), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a))
                shade(p, 'F7F3EA'); left_border(p, 'CDBC9C')
            if tr:
                p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                pf = p.paragraph_format
                pf.first_line_indent = Pt(23 if mode == 'dui' else 24)
                pf.line_spacing = 1.35 if mode == 'dui' else 1.5
                pf.space_before = Pt(3 if mode == 'dui' else 4); pf.space_after = Pt(5 if mode == 'dui' else 3)
                set_run(p.add_run(tr), 12 if mode == 'qian' else 11.5)
                nt = NOTES.get('%d.%d' % (si, idx))
                if nt:
                    add_note(doc, nt)
    # 修訂說明
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('修訂說明'), 16, bold=True)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('本版據《資持記》及律典重校，改正前版錯譯與「照抄式」譯文，要點如下：'), 10, color=RGBColor(0x66, 0x66, 0x66))
    fixes = [
        ('震嶺', '前譯作「鷲嶺」，誤。今改「漢地（震旦）」；九代指後漢至唐九朝。'),
        ('易以形聲', '前譯作「落實在形聲上就難」，義反。今改「容易藉言語音聲做表面文章」。'),
        ('眾網維持', '前譯成「要維持、要區別」，語氣反。今改「綱紀的維持、同異的分判都亂了套」。'),
        ('名僧', '前誤讀為「有名的僧人」。今改「以能秉法稱之為僧」。'),
        ('不敬上座無威儀', '前誤連讀成「不敬沒有威儀的上座」。今析為二事。'),
        ('五種怖畏', '前孤立列出「畜沙彌、與他依止」。今補明是無德而收徒。'),
        ('事在廢前', '前未譯。今加註：後代教法廢前代開緣。'),
        ('誼靜二儀', '前照抄。今改「喧靜二儀」並註明疑為形訛。'),
        ('五大色', '前照抄。今補明五正色與壞色之制。'),
        ('停僧殘行法', '前語意混亂。今補明開許充數及「和尚犯戒、戒子不知情」之義。'),
        ('度量衡', '前僅照錄步數。今補一步六尺、一肘尺八、七樹六十三步之理。'),
        ('偽白話', '前有多段僅換虛詞、甚至照抄（如「宅身佛海」「測思明慧」等），今全部改寫為現代漢語。'),
    ]
    for k, v in fixes:
        q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        qf = q.paragraph_format; qf.first_line_indent = Pt(20); qf.line_spacing = 1.35; qf.space_after = Pt(3)
        set_run(q.add_run(k + '：'), 9.5, bold=True)
        set_run(q.add_run(v), 9.5)
    doc.save(out_docx)
    return len(doc.paragraphs)

if __name__ == '__main__':
    n1 = build('dui', os.path.join(OUT, '行事鈔_白話對照本_卷一_修訂版.docx'))
    n2 = build('qian', os.path.join(OUT, '行事鈔_全白話本_卷一_修訂版.docx'))
    print('built', n1, n2)
    for si in (1, 2, 3):
        print(si, 'paras', len(secs[si]['items']), 'trans', len(T[si]))
