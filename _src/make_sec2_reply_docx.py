# -*- coding: utf-8 -*-
"""第2篇（集僧通局）37 段 AI 回覆 → 一般版 Word／PDF（標楷體 14pt）。"""
import glob
import html
import io
import json
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '重審_行事鈔_3K_20261126', '第2篇_集僧通局_分段', 'ooo.txt')
OUT_DOCX = os.path.join(B, '重審_行事鈔_3K_20261126', '第2篇_集僧通局_AI回覆_整理版.docx')
KAI = 'DFKai-SB'
HEI = 'Microsoft JhengHei'
INK = RGBColor(0x1F, 0x1B, 0x16)
BROWN = RGBColor(0x8B, 0x5E, 0x3C)
BLUE = RGBColor(0x1F, 0x4E, 0x6B)
GREEN = RGBColor(0x2E, 0x5E, 0x46)
GRAY = RGBColor(0x6B, 0x63, 0x57)

# 定稿：原文／白話
rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', 'xingshichao.jsonl'), encoding='utf-8') if x.strip()]
seg = {}
for r in rows:
    segs = r.get('segments') or []
    for si, s in enumerate(segs, 1):
        key = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
        seg[key] = {'vol': r.get('vol') or '',
                    'src': (s.get('display_source') or s.get('source') or '').strip(),
                    'tr': (s.get('translation') or '').strip()}
key2sec = {}
for p in sorted(glob.glob(os.path.join(B, 'docs', 'xingshichao', '*__p*.html'))):
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'<h2 class="sec"[^>]*>([^<]*)</h2>', t)
    sec = html.unescape(m.group(1)) if m else ''
    for k in re.findall(r'<div class="pair[^"]*" id="u([^"]+)"', t):
        key2sec[k] = sec
ORDER = [k for k in seg if key2sec.get(k) == '第2篇　集僧通局']


def clean(s):
    s = re.sub(r'(?m)^#+\s*', '', s)
    s = s.replace('**', '')
    s = re.sub(r'(?m)^\s*-{3,}\s*$', '', s)
    return s.strip()


raw = io.open(SRC, encoding='utf-8').read()
idx = [m.start() for m in re.finditer(r'(?m)^#*\s*（一）考據初檢', raw)]
idx.append(len(raw))
replies = {}
for i in range(len(idx) - 1):
    ch = raw[idx[i]:idx[i + 1]]
    ch = re.sub(r'(?m)^#+\s*', '', ch)
    m = re.search(r'"key"\s*:\s*"([^"]+)"', ch)
    key = m.group(1)
    i1 = ch.find('（一）考據初檢')
    i2 = ch.find('（二）語言與定稿覆核')
    i3 = ch.find('（三）JSONL 結構化結果')
    ires = ch.find('修正結果')
    end1 = min([x for x in (i2, ires if ires > 0 else 10 ** 9, i3) if x > 0])
    review = clean(ch[i1 + len('（一）考據初檢'):end1])
    j2 = i2 + len('（二）語言與定稿覆核')
    end2 = i3 if i3 > 0 else len(ch)
    if 0 < ires < end2:
        end2 = ires
    lang = clean(ch[j2:end2])
    mm = re.search(r'<<<JSONL_START>>>(.*?)<<<JSONL_END>>>', ch, re.S)
    data = json.loads(mm.group(1).strip().splitlines()[0]) if mm else {}
    replies[key] = {'review': review, 'lang': lang, 'data': data}

missing = [k for k in ORDER if k not in replies]
print('回覆段數', len(replies), '| 缺:', missing)


def han(x):
    return len(re.findall(r'[\u4e00-\u9fff]', x or ''))


doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.0)
sec.right_margin = Cm(1.8)


def set_run(run, text, font, size, bold=False, color=INK, italic=False):
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), font)


def para(doc, sb=0, sa=0, line=1.3, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing = line
    p.alignment = align
    return p


def body(doc, label, color, text, size=14):
    if label:
        p = para(doc, sb=4, sa=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
        p.paragraph_format.keep_with_next = True
        set_run(p.add_run(), label, HEI, 12.5, True, color)
    for line in text.split('\n'):
        if not line.strip():
            continue
        p = para(doc, sa=0, line=1.35)
        set_run(p.add_run(), line.strip(), KAI, size)


def footer(doc):
    for s in doc.sections:
        f = s.footer.paragraphs[0]
        f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(f.add_run(), '行事鈔第2篇集僧通局・AI 校閱回覆　第 ', HEI, 9, color=GRAY)
        fld = OxmlElement('w:fldSimple')
        fld.set(qn('w:instr'), 'PAGE')
        f._p.append(fld)
        set_run(f.add_run(), ' 頁', HEI, 9, color=GRAY)


# 封面
p = para(doc, sb=90, sa=6, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '四分律刪繁補闕行事鈔', KAI, 24, True, BROWN)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '卷上・第2篇 集僧通局', KAI, 18, True, INK)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), 'AI 校閱回覆（整理版）', KAI, 17, True, INK)
p = para(doc, sa=20, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '（一）考據初檢　（二）語言與定稿覆核　（三）修正後完整白話', HEI, 11, color=GRAY)
for line in ('共 37 段（原文標楷體 14pt）', '原始回覆為 JSONL 格式，已整理成一般版三節格式',
             '（三）為 fixed 段最終譯文；ok 段標明無須修改；存疑段保留原譯'):
    p = para(doc, sa=2, line=1.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(), '· ' + line, HEI, 11, color=GRAY)
doc.add_page_break()

status_cn = {'fixed': '已修正', 'ok': '無須修改', 'uncertain': '存疑待查'}
n = 0
for i, key in enumerate(ORDER, 1):
    r = replies.get(key)
    if not r:
        continue
    n += 1
    o = seg[key]
    data = r['data']
    status = data.get('status', 'uncertain')
    note = data.get('note', '')
    trans = (data.get('translation') or '').strip()
    if status == 'fixed' and trans:
        final = trans
    elif status == 'ok':
        final = '同原白話，無須修改。'
    else:
        final = o['tr'] + ('\n\n（存疑待查：%s）' % note if note else '')

    p = para(doc, sa=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '%d. ' % i, HEI, 16, True, BROWN)
    set_run(p.add_run(), 'key %s' % key, HEI, 16, True, INK)
    p = para(doc, sa=4, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '卷上・第2篇 集僧通局　狀態：%s　原文 %d 字' %
            (status_cn.get(status, status), han(o['src'])), HEI, 11, color=GRAY)

    body(doc, '原文', BROWN, '【鈔文】\n' + o['src'], 14)
    body(doc, '白話（原譯）', BLUE, '【鈔文】\n' + o['tr'], 14)
    body(doc, '（一）考據初檢', GREEN, r['review'], 14)
    body(doc, '（二）語言與定稿覆核', GREEN, r['lang'], 14)
    body(doc, '（三）修正後完整白話', GREEN, final, 14)
    doc.add_page_break()

footer(doc)
doc.save(OUT_DOCX)
print('saved', OUT_DOCX, '| 段數', n)
print('status:', {k: sum(1 for r in replies.values() if r['data'].get('status') == k)
                  for k in ('fixed', 'ok', 'uncertain')})
