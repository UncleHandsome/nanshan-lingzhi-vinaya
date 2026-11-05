
import os, re, io, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(BASE, '_src')
OUT = os.path.join(BASE, '白話')
FONT = 'DFKai-SB'
LATIN = 'Times New Roman'

secs = json.load(io.open(os.path.join(SRC, 'secs.json'), encoding='utf-8'))
ORIG = {}
for si in (1, 2, 3):
    for i, t in enumerate(secs[si]['items'], start=1):
        ORIG[(si, i)] = t

HEAD_MAP = {
 "【戒德之超勝與末世風氣之慨嘆】": "1:1",
 "【前代律記之流弊與本作宗旨】": "1:2-4",
 "【繁簡折衷與三卷架構】": "1:5-6",
 "【全書三十篇總目】": "",
 "【十門大綱詳釋】": "",
 "第一、序教興意（說明制教興起之意旨）": "1:37-39",
 "第二、制教輕重意（辨析制戒輕重之用意）": "1:47-48",
 "第三、對事約教判處意（依受體判持犯）": "1:49",
 "第四、用諸部文意（廣納各派律文之用意）": "1:50-57",
 "第五、文義決通意（貫通文字與義理之用意）": "1:58-61",
 "第六、教所詮意（教法所闡發之意旨）": "1:62-63",
 "第七、道俗七部立教通局意（化教與行教的分界）": "1:64-67",
 "第八、僧尼二部行事通塞意": "1:68",
 "第九、下三眾隨行異同意": "1:69-70",
 "第十、明鈔者（去偽存真與編修本心）": "1:71-74",
 "**後明作鈔之本意**：": "1:75",
 "【總標宗旨與痛陳末法弊病】": "2:1",
 "【立戒之目的與戒之四科】": "2:2",
 "1. 戒法": "2:3",
 "2. 戒體": "2:4",
 "3. 戒行": "2:5",
 "4. 戒相": "2:6",
 "【順戒法住與違戒法滅之經論明證】": "2:7",
 "【甲、順戒讚戒】": "2:8",
 "**一、化教小乘經論**": "2:9-10",
 "**二、化教大乘經論**": "2:11-12",
 "**三、制教律部與律論**": "2:13-14",
 "【乙、違戒法滅】": "2:15",
 "【辨破惡取空：釋「罪與不罪不可得」】": "2:16",
 "【總標：僧以「和」為義】": "3:1",
 "【鳴犍稚與集僧法儀】": "3:2-3",
 "【僧界劃分之範圍：作法界與自然界】": "3:4-5",
 "一、作法界（透過僧團白四羯磨正式結界之界域）": "3:6",
 "二、自然界（不假僧團作法、依天然環境或聚落自然形成的範圍）": "3:7",
 "1. 聚落界（村落市鎮）": "3:8-10",
 "2. 蘭若界（荒野幽靜處）": "3:11",
 "3. 道行界（行腳遊方之界）": "3:12",
 "4. 水界（江河湖海中）": "3:13",
 "【辨析自然界之體相：否定固定正方說】": "3:14-16",
 "【秉法用僧之分齊（四種僧數與清淨要件）】": "3:17-18",
 "1. 四人僧": "3:19",
 "2. 五人僧": "3:20",
 "3. 十人僧": "3:21",
 "4. 二十人僧": "3:22",
 "【羯磨用僧之行持與眾法清淨差別】": "3:23-26",
}

def parse_md(paths):
    lines = []
    for p in paths:
        lines.extend(io.open(p, encoding='utf-8').read().split('\n'))
    blocks = []
    cur = None
    def flush():
        nonlocal cur
        if cur and (cur.get('text','').strip() or cur['type'] == 'h1'):
            blocks.append(cur)
        cur = None
    for raw in lines:
        s = raw.rstrip()
        t = s.strip()
        if not t:
            flush(); continue
        if t == '---':
            flush(); continue
        m = re.match(r'^(#{1,4})\s+(.*)$', t)
        if m:
            flush()
            blocks.append({'type': 'h%d' % len(m.group(1)), 'text': m.group(2)})
            continue
        if t.startswith('> '):
            flush()
            blocks.append({'type': 'quote', 'text': t[2:]})
            continue
        if t == '>':
            continue
        m = re.match(r'^(\s*)\*\s+(.*)$', s)
        if m:
            flush()
            blocks.append({'type': 'li', 'level': 1 if len(m.group(1)) < 2 else 2, 'text': m.group(2)})
            continue
        m = re.match(r'^(\s*)(\d+)\.\s+(.*)$', s)
        if m:
            flush()
            blocks.append({'type': 'li', 'level': 1 if len(m.group(1)) < 2 else 2, 'text': m.group(2) + '. ' + m.group(3)})
            continue
        m = re.match(r'^\*\*(.+?)\*\*[:：]?$', t)
        if m:
            flush()
            blocks.append({'type': 'h4', 'text': t})
            continue
        if cur is None:
            cur = {'type': 'p', 'text': t}
        else:
            cur['text'] = cur.get('text','') + t
    flush()
    return blocks

def set_run(run, size, bold=False, color=None, italic=False):
    run.font.size = Pt(size); run.font.bold = bold; run.font.italic = italic
    run.font.name = LATIN
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), LATIN); rFonts.set(qn('w:hAnsi'), LATIN)
    rFonts.set(qn('w:eastAsia'), FONT)
    if color is not None:
        run.font.color.rgb = color

def add_rich(p, text, size, color=None, base_bold=False):
    for part in re.split(r'(\*\*.+?\*\*|\*[^*]+?\*)', text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            set_run(p.add_run(part[2:-2]), size, bold=True, color=color)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            set_run(p.add_run(part[1:-1]), size, bold=base_bold, color=color, italic=True)
        else:
            set_run(p.add_run(part), size, bold=base_bold, color=color)

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

def add_field(par, instr):
    run = par.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    return run

def emit_orig(doc, spec):
    for pair in spec.split(','):
        pair = pair.strip()
        if not pair:
            continue
        a, _, b = pair.partition('-')
        si, i1 = a.split(':'); si = int(si); i1 = int(i1)
        i2 = int(b) if b else i1
        for i in range(i1, i2 + 1):
            t = ORIG.get((si, i))
            if not t:
                continue
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Pt(6); pf.space_before = Pt(4); pf.space_after = Pt(0)
            pf.line_spacing = 1.2; pf.keep_with_next = True
            set_run(p.add_run(t), 10.5, color=RGBColor(0x6b, 0x5b, 0x4a))
            shade(p, 'F7F3EA'); left_border(p, 'CDBC9C')

def build(mode, blocks, out_docx):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = LATIN; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.7); sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.8); sec.right_margin = Cm(1.8)

    for _ in range(3):
        p = doc.add_paragraph(); p.add_run(''); p.paragraph_format.space_after = Pt(0)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    set_run(p.add_run('南山三大部之一'), 12, color=RGBColor(0x77, 0x77, 0x77))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run('四分律刪繁補闕行事鈔'), 26, bold=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    set_run(p.add_run('白話語譯‧' + ('對照本' if mode == 'dui' else '全白話本')), 15)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    set_run(p.add_run('上卷　序．標宗顯德篇．集僧通局篇（餘篇待續）'), 10.5, color=RGBColor(0x55, 0x55, 0x55))
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    set_run(p.add_run('唐·道宣律師　撰'), 11)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(22)
    set_run(p.add_run('底本：《大正新脩大藏經》第40冊 No.1804（CBETA）'), 9, color=RGBColor(0x99, 0x99, 0x99))

    ns = doc.add_section(WD_SECTION.NEW_PAGE)
    ns.header.is_linked_to_previous = False
    ns.footer.is_linked_to_previous = False
    ns.page_width = Cm(21.0); ns.page_height = Cm(29.7)
    ns.top_margin = Cm(1.7); ns.bottom_margin = Cm(1.6)
    ns.left_margin = Cm(1.8); ns.right_margin = Cm(1.8)
    hp = ns.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(hp.add_run('行事鈔白話' + ('（對照）' if mode == 'dui' else '')), 8, color=RGBColor(0xaa, 0xaa, 0xaa))
    fp = ns.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(fp.add_run('— '), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    fr = add_field(fp, ' PAGE '); fr.font.size = Pt(8.5); fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    set_run(fp.add_run(' —'), 8.5, color=RGBColor(0x88, 0x88, 0x88))
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '1'); ns._sectPr.append(pg)

    for b in blocks:
        t = b['type']
        if t == 'h1':
            p = doc.add_paragraph(style='Heading 1')
            pf = p.paragraph_format
            pf.page_break_before = True; pf.space_before = Pt(0); pf.space_after = Pt(14)
            pf.keep_with_next = True
            set_run(p.add_run(b['text']), 17, bold=True, color=RGBColor(0, 0, 0))
        elif t == 'h2':
            p = doc.add_paragraph(style='Heading 2')
            pf = p.paragraph_format
            pf.page_break_before = False; pf.space_before = Pt(16); pf.space_after = Pt(6)
            pf.keep_with_next = True
            set_run(p.add_run(b['text'].strip('*')), 13, bold=True, color=RGBColor(0, 0, 0))
            if mode == 'dui':
                spec = HEAD_MAP.get(b['text'], '')
                if spec:
                    emit_orig(doc, spec)
        elif t in ('h3', 'h4'):
            p = doc.add_paragraph(style='Heading 3')
            pf = p.paragraph_format
            pf.space_before = Pt(12); pf.space_after = Pt(4); pf.keep_with_next = True
            set_run(p.add_run(b['text'].strip('*')), 11.5, bold=True, color=RGBColor(0, 0, 0))
            if mode == 'dui':
                spec = HEAD_MAP.get(b['text'], '')
                if spec:
                    emit_orig(doc, spec)
        elif t == 'quote':
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Pt(16); pf.space_before = Pt(0); pf.space_after = Pt(0); pf.line_spacing = 1.2
            add_rich(p, b['text'], 9.5, color=RGBColor(0x44, 0x44, 0x44))
        elif t == 'li':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf = p.paragraph_format
            pf.left_indent = Pt(24 if b['level'] == 2 else 12)
            pf.first_line_indent = Pt(-12)
            pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.25
            set_run(p.add_run('• '), 11, color=RGBColor(0x88, 0x88, 0x88))
            add_rich(p, b['text'], 11.5)
        else:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf = p.paragraph_format
            pf.first_line_indent = Pt(24)
            pf.space_before = Pt(2); pf.space_after = Pt(2); pf.line_spacing = 1.25
            add_rich(p, b['text'], 12)
    doc.save(out_docx)
    return len(doc.paragraphs)

if __name__ == '__main__':
    parts = [os.path.join(SRC, 'user', x) for x in ('p1.md', 'p2.md', 'p3.md', 'p4.md')]
    blocks = parse_md(parts)
    print('blocks', len(blocks))
    n1 = build('dui', blocks, os.path.join(OUT, '行事鈔_白話對照本_上卷.docx'))
    n2 = build('qian', blocks, os.path.join(OUT, '行事鈔_全白話本_上卷.docx'))
    print('built', n1, n2)
