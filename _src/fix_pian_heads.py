# -*- coding: utf-8 -*-
"""在既有會本上做兩件事：
1. 篇2 起首記段中屬於前篇的尾巴，搬到前篇末尾
2. 篇1 開頭補上卷首鈔文（序與十門）
"""
import io, os, re, json
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
FONT = 'SimSun'; LATIN = 'Times New Roman'
han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))
HDR = re.compile(r'(\d*\s*釋[\u4e00-\u9fff]{1,6}篇(?:\\([^)）]*\\))?)')


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def add_ji(doc, tag, text, tr):
    r = doc.add_paragraph(); rf = r.paragraph_format
    rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
    rf.left_indent = Pt(14); rf.keep_with_next = True
    sr(r.add_run(tag + text), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
    b = doc.add_paragraph(); b.paragraph_format.first_line_indent = Pt(20)
    b.paragraph_format.left_indent = Pt(14)
    b.paragraph_format.line_spacing = 1.28; b.paragraph_format.space_after = Pt(2)
    sr(b.add_run(tr), 10)


def add_chao(doc, tag, text, tr):
    q = doc.add_paragraph(); qf = q.paragraph_format
    qf.space_before = Pt(6); qf.space_after = Pt(1); qf.line_spacing = 1.2; qf.keep_with_next = True
    sr(q.add_run(tag + text), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')
    b = doc.add_paragraph(); b.paragraph_format.first_line_indent = Pt(20)
    b.paragraph_format.line_spacing = 1.3; b.paragraph_format.space_after = Pt(2)
    sr(b.add_run(tr), 10.5)


# 1) 找出各篇首記段中屬於前篇的頭部
heads = {}
for p in range(2, 11):
    o, t = ZI[p - 1][0]
    m = HDR.search(o[:160])
    if m and m.start() > 4:
        head, tail = o[:m.start()].strip(), o[m.start():].strip()
        # 白話按字數比例切
        k = max(1, int(round(han(head) / max(1, han(o)) * len(re.findall(r'[^。！？]*[。！？]?', t)))))
        sents = re.findall(r'[^。！？]*[。！？]?', t)
        head_tr = ''.join(sents[:k])
        heads[p] = (head, head_tr)
        ZI[p - 1] = [(tail, t[len(head_tr):] if t.startswith(head_tr) else t)] + ZI[p - 1][1:]
        print('篇%02d 首記切出前篇尾巴 %d 字' % (p, len(head)))

# 2) 前篇末尾補上
for p, (head, head_tr) in heads.items():
    fp = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p - 1, SECS[p - 2]['name']))
    if not os.path.exists(fp):
        continue
    d = Document(fp)
    add_ji(d, '【記%03d】（續前篇）' % len(ZI[p - 2]), head, head_tr)
    d.save(fp)
    print('已補到', os.path.basename(fp))

# 3) 篇1 開頭補卷首鈔文
def load_chunk(key):
    sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', key + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', key + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    return sp, tt


sp, tt = load_chunk('00_卷首')
fp = os.path.join(B, '白話', '會本_篇01_標宗顯德.docx')
d = Document(fp)
q = d.add_paragraph(); q.paragraph_format.space_before = Pt(12)
sr(q.add_run('〔鈔首〕序與十門'), 12, bold=True, color=RGBColor(0x6b, 0x5b, 0x4a))
for i in range(min(len(sp), len(tt), 6)):
    add_chao(d, '【鈔首%02d】' % (i + 1), sp[i], tt[i])
d.save(fp)
print('篇01 已補鈔首', min(len(sp), len(tt), 6), '條')
