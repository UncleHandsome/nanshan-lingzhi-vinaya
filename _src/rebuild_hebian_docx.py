# -*- coding: utf-8 -*-
"""由最新 30 篇會本 docx 重建 12 卷「句級合編」docx"""
import os, re, glob
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四', '卷中之一', '卷中之二', '卷中之三', '卷中之四',
      '卷下之一', '卷下之二', '卷下之三', '卷下之四']

# 1) 由舊合編建立 篇→卷 對照
SEC = re.compile(r'^第(\d+)篇')
p2v = {}
for v in HB:
    fp = os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % v)
    if not os.path.exists(fp):
        continue
    for p in Document(fp).paragraphs:
        m = SEC.match(p.text.strip())
        if m:
            p2v.setdefault(int(m.group(1)), v)
print('篇→卷:', len(p2v))

# 2) 讀 30 篇
files = {}
for f in glob.glob(os.path.join(B, '白話', '會本_篇*_*.docx')):
    m = re.search(r'會本_篇(\d+)_', os.path.basename(f))
    if m:
        files[int(m.group(1))] = f

def new_doc():
    d = Document()
    st = d.styles['Normal']
    st.font.name = 'SimSun'
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
    return d

for v in HB:
    d = new_doc()
    for txt in ('行事鈔・資持記　句級合編', v):
        p = d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(txt)
    for n in sorted([k for k, vv in p2v.items() if vv == v]):
        fp = files.get(n)
        if not fp:
            continue
        src = Document(fp)
        ps = [p.text.strip() for p in src.paragraphs]
        # 篇名
        name = ''
        for t in ps:
            if t.startswith('第%d篇' % n):
                name = t
                break
        if name:
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(name)
        started = False
        i = 0
        while i < len(ps):
            t = ps[i]
            if t.startswith('【鈔') or t.startswith('【記'):
                started = True
                m = re.match(r'^【(鈔|記)\d+】（.*）?(.*)$', t)
                rest = t[t.find('】') + 1:]
                tag = '【鈔】' if t.startswith('【鈔') else '【記】'
                d.add_paragraph(tag + rest)
                if i + 1 < len(ps):
                    d.add_paragraph(ps[i + 1])
                    i += 2
                    continue
            i += 1
    out = os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % v)
    d.save(out)
    print(v, 'ok', len(d.paragraphs))
