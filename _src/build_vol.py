
import os, io, json, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(BASE, 'TXT_分卷', '01_行事鈔')
TR = os.path.join(BASE, 'AI語譯', 'out', '01_行事鈔')
WORK = os.path.join(BASE, 'AI語譯', '_work')
OUT = os.path.join(BASE, '白話')
FONT = 'DFKai-SB'; LATIN = 'Times New Roman'

def set_run(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.font.bold = bold; run.font.name = LATIN
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), LATIN); rFonts.set(qn('w:hAnsi'), LATIN)
    rFonts.set(qn('w:eastAsia'), FONT)
    if color is not None: run.font.color.rgb = color

def shade(p, hexcolor):
    pPr = p._p.get_or_add_pPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    pPr.append(shd)

def left_border(p, hexcolor):
    pPr = p._p.get_or_add_pPr(); pbdr = OxmlElement('w:pBdr'); left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single'); left.set(qn('w:sz'), '12'); left.set(qn('w:space'), '6'); left.set(qn('w:color'), hexcolor)
    pbdr.append(left); pPr.append(pbdr)

def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2); return run

def load():
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.txt') and not f.startswith('00_'))
    out = []
    for f in files:
        key = f[:-4]
        num = int(re.match(r'^(\d+)', key).group(1))
        src = io.open(os.path.join(SRC, f), encoding='utf-8').read().split('\n')[5:]
        sp = [x.strip() for x in src if x.strip() and not re.match(r'^\d+\s+.*篇\([上中下][一二三四]\)$', x.strip())]
        tr = io.open(os.path.join(TR, key + '.txt'), encoding='utf-8').read()
        tp = [x.strip() for x in re.split(r'\n\s*\n', tr) if x.strip() and not re.match(r'^\d+\s+.*篇\([上中下][一二三四]\)$', x.strip())]
        # 去掉開頭連續的篇目清單（與正文篇題重複）
        jp = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$')
        i = 0
        while i < len(sp) and not jp.match(sp[i]): i += 1
        j = i
        while j < len(sp) and jp.match(sp[j]): j += 1
        if j - i >= 3 and j < len(sp):
            del sp[i:j]
            if len(tp) > j: del tp[i:j]
            elif i < len(tp): del tp[i:]
        out.append(dict(key=key, num=num, juan=key.split('_', 1)[1], src=sp, tr=tp))
    return out

def build(chunks, mode, vol, path):
    doc = Document()
    st = doc.styles['Normal']; st.font.name = LATIN; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.7); sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.8); sec.right_margin = Cm(1.8)

    for _ in range(3):
        p = doc.add_paragraph(); p.add_run(''); p.paragraph_format.space_after = Pt(0)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    set_run(p.add_run('四分律刪繁補闕行事鈔'), 26, bold=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run(p.add_run('白話語譯‧' + ('對照本' if mode == 'dui' else '全白話本')), 15)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(40)
    set_run(p.add_run(vol), 20, bold=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('唐·道宣律師　撰　　AI 語譯稿（兩輪校讀）'), 10, color=RGBColor(0x77, 0x77, 0x77))

    ns = doc.add_section(WD_SECTION.NEW_PAGE)
    ns.header.is_linked_to_previous = False; ns.footer.is_linked_to_previous = False
    ns.page_width = Cm(21.0); ns.page_height = Cm(29.7)
    ns.top_margin = Cm(1.7); ns.bottom_margin = Cm(1.6)
    ns.left_margin = Cm(1.8); ns.right_margin = Cm(1.8)
    hp = ns.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run('行事鈔白話' + ('（對照）' if mode == 'dui' else '') + '　' + vol), 8, color=RGBColor(0xaa, 0xaa, 0xaa))
    fp = ns.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(8.5); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    set_run(fp.add_run(' —'), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '1'); ns._sectPr.append(pg)

    prev_juan = None
    first = True
    for c in chunks:
        shown = c['juan']
        part = re.match(r'^(卷.+?)([a-z])$', shown)
        extra = ''
        if part:
            shown = part.group(1)
            extra = '（' + {'a': '一', 'b': '二', 'c': '三', 'd': '四'}.get(part.group(2), part.group(2)) + '）'
        if shown != prev_juan:
            p = doc.add_paragraph(style='Heading 1'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format; pf.page_break_before = (not first); pf.keep_with_next = True
            pf.space_before = Pt(0); pf.space_after = Pt(10)
            set_run(p.add_run('四分律刪繁補闕行事鈔' + shown), 17, bold=True, color=RGBColor(0, 0, 0))
            first = False
            prev_juan = shown
        elif extra:
            p = doc.add_paragraph(style='Heading 2')
            pf = p.paragraph_format; pf.space_before = Pt(10); pf.space_after = Pt(6); pf.keep_with_next = True
            set_run(p.add_run(shown + '（續）'), 12, bold=True, color=RGBColor(0x44, 0x44, 0x44))

        sp, tp = c['src'], c['tr']
        if mode == 'dui':
            m = min(len(sp), len(tp))
            for i in range(m):
                if re.match(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$', sp[i]) and sp[i] == tp[i]:
                    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    qf = q.paragraph_format; qf.space_before = Pt(1); qf.space_after = Pt(1); qf.line_spacing = 1.2
                    set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x55, 0x55, 0x55))
                    continue
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(5); qf.space_after = Pt(0); qf.line_spacing = 1.2; qf.keep_with_next = True
                set_run(q.add_run(sp[i]), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(tp[i]) < 40 else WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(tp[i]), 12)
            for t in sp[m:]:
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.left_indent = Pt(6); qf.space_before = Pt(4); qf.space_after = Pt(0); qf.line_spacing = 1.2
                set_run(q.add_run(t), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F7F3EA'); left_border(q, 'CDBC9C')
            for t in tp[m:]:
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.25; af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(t), 12)
        else:
            for t in tp:
                a = doc.add_paragraph(); a.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                af = a.paragraph_format; af.first_line_indent = Pt(24); af.line_spacing = 1.3
                af.space_before = Pt(2); af.space_after = Pt(4)
                set_run(a.add_run(t), 12)
    if vol == '下卷':
        p = doc.add_paragraph(); p.paragraph_format.page_break_before = True
        p.paragraph_format.space_after = Pt(8)
        set_run(p.add_run('附錄一　律典簡稱對照'), 15, bold=True)
        rows1 = [('《四分》', '《四分律》'), ('《僧祇》', '《摩訶僧祇律》'), ('《十誦》', '《十誦律》'),
                 ('《五分》', '《彌沙塞部和醯五分律》'), ('《善見》', '《善見律毘婆沙》'),
                 ('《多論》／《薩婆多》', '《薩婆多毘尼毘婆沙》'), ('《伽論》', '《薩婆多部毘尼摩得勒伽》'),
                 ('《母論》', '《毘尼母經》'), ('《明了》', '《律二十二明了論》'),
                 ('《義鈔》', '道宣《四分律拾毗尼義鈔》'), ('《大疏》', '首師《四分律疏》二十卷'),
                 ('《資持記》', '元照《四分律行事鈔資持記》')]
        for a, b in rows1:
            q = doc.add_paragraph(); qf = q.paragraph_format
            qf.left_indent = Pt(12); qf.space_after = Pt(1); qf.line_spacing = 1.25
            set_run(q.add_run(a), 9.5, bold=True); set_run(q.add_run('　＝　'), 9.5); set_run(q.add_run(b), 9.5)
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(8)
        set_run(p.add_run('附錄二　律度量衡與今制約算'), 15, bold=True)
        rows2 = [('一肘', '一尺八寸，約 45 公分'), ('一搩手', '中指至拇指張開，約 20–25 公分'),
                 ('一弓', '五肘，約 2.2 公尺'), ('一步', '六尺，約 1.4–1.8 公尺（本文以一步六尺計）'),
                 ('一拘盧舍', '五百弓／六百步，約 0.8–1 公里（《雜寶藏》作五里）'),
                 ('一由旬', '約 7–15 公里（小由旬約 40 里）'), ('一槃陀', '二十八肘，約 12.6 公尺'),
                 ('一斛', '十斗，約 60 公升（唐制）'), ('一秤', '約 1.5 公斤（本文「三十秤」約 45 公斤）')]
        for a, b in rows2:
            q = doc.add_paragraph(); qf = q.paragraph_format
            qf.left_indent = Pt(12); qf.space_after = Pt(1); qf.line_spacing = 1.25
            set_run(q.add_run(a), 9.5, bold=True); set_run(q.add_run('　'), 9.5); set_run(q.add_run(b), 9.5)
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(8)
        set_run(q.add_run('（以上折算依唐制與諸律互參，僅供閱讀參考；實際結界、裁衣仍應依師承與律本。）'), 8.5, color=RGBColor(0x77, 0x77, 0x77))
    doc.save(path)
    return len(doc.paragraphs)

if __name__ == '__main__':
    chunks = load()
    vols = {'上卷': [c for c in chunks if c['num'] <= 4],
            '中卷': [c for c in chunks if 5 <= c['num'] <= 8],
            '下卷': [c for c in chunks if c['num'] >= 9]}
    for v, cs in vols.items():
        for mode, label in (('dui', '白話對照本'),):
            path = os.path.join(OUT, '行事鈔_%s_%s.docx' % (label, v))
            n = build(cs, mode, v, path)
            print(v, label, len(cs), 'chunks', n, 'paras')
