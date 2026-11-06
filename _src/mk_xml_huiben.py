# -*- coding: utf-8 -*-
"""以 CBETA XML 鈔段落為單位、牒詞錨定重建會本（篇1-5）"""
import xml.etree.ElementTree as ET
import os, re, io, json, importlib.util
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TEI = '{http://www.tei-c.org/ns/1.0}'
han0 = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
VAR = {'說': '説', '眾': '衆', '為': '爲', '教': '敎', '即': '卽', '既': '旣',
       '並': '竝', '床': '牀', '收': '収', '煮': '煑', '查': '査'}
han = lambda s: ''.join(VAR.get(c, c) for c in han0(s))
PNAME = ['標宗顯德', '集僧通局', '足數眾相', '受欲是非', '通辨羯磨']
FONT = 'SimSun'; LATIN = 'Times New Roman'
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))

root4 = ET.parse(os.path.join(B, '_xml', 'T40n1804.xml')).getroot()
chao = {}
for d in root4.iter():
    if not d.tag.endswith('div'):
        continue
    head = (d.findtext(TEI + 'head') or '').strip()
    m = re.match(r'^(.*?)篇第', head)
    if not m:
        continue
    ps = [''.join(p.itertext()).strip() for p in d.findall(TEI + 'p')]
    chao[m.group(1)] = [p for p in ps if han(p)]


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def build(p):
    idx = p - 1
    nm = PNAME[idx]
    ch = chao[nm]
    sec = list(SECS[idx]['items'])
    chao_items = [it for it in sec if not SKIP.match(it[0].strip())]
    # 鈔白話：以分卷對應（數量需一致）
    if len(chao_items) != len(ch):
        print('篇%d 鈔數不符 xml%d vs 分卷%d' % (p, len(ch), len(chao_items)))
    zt = ZI[idx]
    # 鈔 han 串與位置→p
    H, pos2p = '', []
    for i, t in enumerate(ch):
        for c in han(t):
            H += c; pos2p.append(i)
    # 記錨定
    anchors = []
    cur = 0
    for k, (o, t) in enumerate(zt):
        h = han(o)[:80]
        best = None
        for L in (8, 7, 6, 5):
            for i in range(0, max(1, len(h) - L + 1)):
                seg = h[i:i + L]
                if len(set(seg)) < 3:
                    continue
                pos = H.find(seg, cur)
                if pos >= 0 and (best is None or pos < best):
                    best = pos
            if best is not None:
                break
        if best is not None:
            cur = best
            anchors.append(pos2p[best])
        else:
            anchors.append(anchors[-1] if anchors else 0)

    doc = Document()
    st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21); s.page_height = Cm(29.7)
    s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6)
    s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('四分律行事鈔・資持記　會本（XML 重建）'), 17, bold=True)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('第%d篇　%s' % (p, nm)), 11, color=RGBColor(0x66, 0x66, 0x66))

    by_p = {}
    for k, a in enumerate(anchors):
        by_p.setdefault(a, []).append(k)

    for i, ct in enumerate(ch):
        tt = chao_items[i][1] if i < len(chao_items) else ''
        qq = doc.add_paragraph(); qf = qq.paragraph_format
        qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
        sr(qq.add_run('【鈔%02d】' % (i + 1) + ct), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
        a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
        a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
        sr(a2.add_run(tt), 10.5)
        for k in by_p.get(i, []):
            zo, ztr = zt[k]
            r = doc.add_paragraph(); rf = r.paragraph_format
            rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
            rf.left_indent = Pt(14); rf.keep_with_next = True
            sr(r.add_run('【記%03d】' % (k + 1) + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
            b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
            b2.paragraph_format.left_indent = Pt(14)
            b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
            sr(b2.add_run(ztr), 10)
    out = os.path.join(B, '白話', '會本X_篇%02d_%s.docx' % (p, nm))
    doc.save(out)
    return out, len(ch), len(zt), anchors


for p in range(1, 6):
    out, nc, nz, anc = build(p)
    mono = all(b >= a for a, b in zip(anc, anc[1:]))
    print('篇%d %-6s 鈔%2d 記%3d 錨點單調=%s → %s' % (p, PNAME[p - 1], nc, nz, mono, os.path.basename(out)))
