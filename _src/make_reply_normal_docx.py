# -*- coding: utf-8 -*-
"""把 AAA.txt（AI 回覆，JSONL 版）整理成一般版格式，輸出 DOCX／PDF。

（一）考據初檢 （二）語言與定稿覆核 （三）修正後完整白話（JSONL fixed→translation）
"""
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
SRC = os.path.join(B, '重審_行事鈔_3K_20261126', '抽樣十段', 'AAA.txt')
OUT_DOCX = os.path.join(B, '重審_行事鈔_3K_20261126', '抽樣十段_AI回覆_整理版.docx')
KAI = 'DFKai-SB'
HEI = 'Microsoft JhengHei'
INK = RGBColor(0x1F, 0x1B, 0x16)
BROWN = RGBColor(0x8B, 0x5E, 0x3C)
BLUE = RGBColor(0x1F, 0x4E, 0x6B)
GREEN = RGBColor(0x2E, 0x5E, 0x46)
GRAY = RGBColor(0x6B, 0x63, 0x57)

# ── 定稿資料（原白話） ──
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


def clean(s):
    s = re.sub(r'(?m)^#+\s*', '', s)
    s = s.replace('**', '')
    s = re.sub(r'(?m)^\s*-{3,}\s*$', '', s)
    return s.strip()


def split_sections(t):
    idx = [m.start() for m in re.finditer(r'(?m)^#*\s*（一）考據初檢', t)]
    idx.append(len(t))
    out = []
    for i in range(len(idx) - 1):
        out.append(t[idx[i]:idx[i + 1]])
    return out


def parse_chunk(ch):
    ch = re.sub(r'(?m)^#+\s*', '', ch)
    m = re.search(r'"key"\s*:\s*"(\d+)"', ch)
    if not m:
        raise SystemExit('找不到 key：' + ch[:80])
    key = m.group(1)
    i2 = ch.find('（二）語言與定稿覆核')
    i3 = ch.find('（三）JSONL 結構化結果')
    ires = ch.find('修正結果')
    # （一）
    i1 = ch.find('（一）考據初檢')
    j1 = i1 + len('（一）考據初檢')
    end1 = i2 if i2 > 0 else (ires if ires > 0 else i3)
    review = clean(ch[j1:end1])
    # （二）
    j2 = i2 + len('（二）語言與定稿覆核')
    end2 = i3 if i3 > 0 else len(ch)
    if ires > j2:
        end2 = min(end2, ires) if ires < i3 or i3 < 0 else end2
    lang = clean(ch[j2:end2])
    # JSONL
    mm = re.search(r'<<<JSONL_START>>>(.*?)<<<JSONL_END>>>', ch, re.S)
    data = json.loads(mm.group(1).strip().splitlines()[0]) if mm else {}
    status = data.get('status', 'uncertain')
    note = data.get('note', '')
    trans = data.get('translation', '')
    return key, status, note, review, lang, trans


text = io.open(SRC, encoding='utf-8').read()
chunks = split_sections(text)
print('sections', len(chunks))
entries = []
for ch in chunks:
    key, status, note, review, lang, trans = parse_chunk(ch)
    orig = seg.get(key, {})
    if status == 'fixed':
        final = trans.strip()
        if not final:
            raise SystemExit('fixed 但沒有 translation：' + key)
    elif status == 'ok':
        final = '同原白話，無須修改。'
    else:
        final = orig.get('tr', '') + ('\n\n（存疑待查：%s）' % note if note else '')
    entries.append({'key': key, 'status': status, 'note': note,
                    'review': review, 'lang': lang, 'final': final,
                    'src': orig.get('src', ''), 'tr': orig.get('tr', ''),
                    'vol': orig.get('vol', ''), 'sec': key2sec.get(key, '')})

for e in entries:
    if not e['src'].startswith('【'):
        e['src'] = '【鈔文】\n' + e['src']
    if not e['tr'].startswith('【'):
        e['tr'] = '【鈔文】\n' + e['tr']

# ── Word ──
doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.2)
sec.right_margin = Cm(2.0)


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


def body(doc, label, label_color, text, size=10.5):
    if label:
        p = para(doc, sb=3, sa=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
        p.paragraph_format.keep_with_next = True
        set_run(p.add_run(), label, HEI, 11, True, label_color)
    for line in text.split('\n'):
        if not line.strip():
            continue
        p = para(doc, sa=0, line=1.3)
        set_run(p.add_run(), line.strip(), KAI, size)


def footer(doc):
    for s in doc.sections:
        f = s.footer.paragraphs[0]
        f.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(f.add_run(), '行事鈔代表性十段・AI 校閱回覆（整理版）　第 ', HEI, 8.5, color=GRAY)
        fld = OxmlElement('w:fldSimple')
        fld.set(qn('w:instr'), 'PAGE')
        f._p.append(fld)
        set_run(f.add_run(), ' 頁', HEI, 8.5, color=GRAY)


# 封面
p = para(doc, sb=80, sa=6, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '四分律刪繁補闕行事鈔', KAI, 24, True, BROWN)
p = para(doc, sa=4, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '代表性十段・AI 校閱回覆（整理版）', KAI, 17, True, INK)
p = para(doc, sa=20, align=WD_ALIGN_PARAGRAPH.CENTER)
set_run(p.add_run(), '（一）考據初檢　（二）語言與定稿覆核　（三）修正後完整白話', HEI, 10.5, color=GRAY)
for line in ('10 段：卷上 5 段、卷中 2 段、卷下 3 段',
             '原始回覆為 JSONL 格式，已整理成一般版三節格式',
             '「（三）修正後完整白話」為 fixed 段的最終譯文；ok 段標明無須修改'):
    p = para(doc, sa=2, line=1.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(), '· ' + line, HEI, 10, color=GRAY)
doc.add_page_break()

status_cn = {'fixed': '已修正', 'ok': '無須修改', 'uncertain': '存疑待查'}
for i, e in enumerate(entries, 1):
    p = para(doc, sa=1, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), '%d. ' % i, HEI, 13, True, BROWN)
    set_run(p.add_run(), '%s・%s' % (e['vol'], e['sec']), HEI, 13, True, INK)
    p = para(doc, sa=3, line=1.2, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run(p.add_run(), 'key %s　狀態：%s　｜ AI 回覆整理：JSONL → 一般版' %
            (e['key'], status_cn.get(e['status'], e['status'])), HEI, 9.5, color=GRAY)

    body(doc, '原文', BROWN, e['src'], 11)
    body(doc, '白話（原譯）', BLUE, e['tr'], 11)
    doc.add_paragraph()
    body(doc, '（一）考據初檢', GREEN, e['review'], 10.5)
    body(doc, '（二）語言與定稿覆核', GREEN, e['lang'], 10.5)
    body(doc, '（三）修正後完整白話', GREEN, e['final'], 11)
    doc.add_page_break()

footer(doc)
doc.save(OUT_DOCX)
print('saved', OUT_DOCX)

# ── 純文字版 ──
OUT_TXT = os.path.join(B, '重審_行事鈔_3K_20261126', '抽樣十段_AI回覆_整理版.txt')
lines = ['四分律刪繁補闕行事鈔', '代表性十段・AI 校閱回覆（整理版）',
         '格式：（一）考據初檢　（二）語言與定稿覆核　（三）修正後完整白話', '']
for i, e in enumerate(entries, 1):
    lines += [
        '%d. %s・%s（key %s，%s）' % (i, e['vol'], e['sec'], e['key'],
                                      status_cn.get(e['status'], e['status'])),
        '',
        '【原文】', e['src'], '',
        '【白話（原譯）】', e['tr'], '',
        '（一）考據初檢', e['review'], '',
        '（二）語言與定稿覆核', e['lang'], '',
        '（三）修正後完整白話', e['final'], '',
        '=' * 60, '',
    ]
io.open(OUT_TXT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('saved', OUT_TXT)

for e in entries:
    print(e['key'], e['status'], 'review', len(e['review']), 'lang', len(e['lang']), 'final', len(e['final']))
