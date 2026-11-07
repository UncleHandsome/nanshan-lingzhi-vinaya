import os, re, glob
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四', '卷中之一', '卷中之二', '卷中之三', '卷中之四',
      '卷下之一', '卷下之二', '卷下之三', '卷下之四']
SEC = re.compile(r'^第(\d+)篇')
OLD = r'C:\Users\lionc\OneDrive\桌面\XW\_舊資料_三大部_20261107\合編_舊docx'

p2v = {}
for v in HB:
    fp = os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % v)
    if not os.path.exists(fp):
        fp = os.path.join(OLD, '行事鈔資持記句級合編_%s.docx' % v)
    for p in Document(fp).paragraphs:
        m = SEC.match(p.text.strip())
        if m:
            p2v.setdefault(int(m.group(1)), v)

files = {}
for f in glob.glob(os.path.join(B, '白話', '會本_篇*_*.docx')):
    m = re.search(r'會本_篇(\d+)_', os.path.basename(f))
    if m:
        files[int(m.group(1))] = f

# 篇14 跨卷切片
p14 = [p.text.strip() for p in Document(files[14]).paragraphs]
K2, K3 = 904, 1656
SLICE = {'卷中之一': (0, K2), '卷中之二': (K2, K3), '卷中之三': (K3, len(p14))}

def new_doc():
    d = Document()
    st = d.styles['Normal']
    st.font.name = 'SimSun'
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
    return d

def add_pairs(d, lines):
    i = 0
    while i < len(lines):
        t = lines[i]
        if t.startswith('【鈔') or t.startswith('【記'):
            tag = '【鈔】' if t.startswith('【鈔') else '【記】'
            rest = t[t.find('】') + 1:]
            d.add_paragraph(tag + rest)
            if i + 1 < len(lines):
                d.add_paragraph(lines[i + 1])
                i += 2
                continue
        i += 1

for v in HB:
    d = new_doc()
    for txt in ('行事鈔・資持記　句級合編', v):
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(txt)
    nums = sorted([k for k, vv in p2v.items() if vv == v])
    if v in SLICE:
        nums = ([13, 14] if v == '卷中之一' else [14])
    for n in nums:
        fp = files.get(n)
        if not fp:
            continue
        ps = [p.text.strip() for p in Document(fp).paragraphs]
        if n == 14 and v in SLICE:
            seg = p14[SLICE[v][0]:SLICE[v][1]]
            name = ''
            for t in ps:
                if t.startswith('第14篇'):
                    name = t
                    break
            if name and v == '卷中之一':
                p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run(name)
            add_pairs(d, seg)
            continue
        name = ''
        for t in ps:
            if t.startswith('第%d篇' % n):
                name = t
                break
        if name:
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run(name)
        add_pairs(d, ps)
    d.save(os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % v))
    print(v, len(d.paragraphs))
