# -*- coding: utf-8 -*-
"""篇1-5,7-10 會本（支援 AI 標註的牒詞切點）"""
import io, os, re, json, glob, sys, importlib.util
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
FONT = 'SimSun'; LATIN = 'Times New Roman'
IN = os.path.join(B, 'AI語譯', '_work', 'pian_split_in')
SO = os.path.join(B, 'AI語譯', '_work', 'pian_split_out')

han = lambda s: len(re.findall(r'[\u4e00-\u9fff]', s))


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size); run.bold = bold; run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def _sents(x):
    out = re.findall(r'[^。！？；]*[。！？；]?', x)
    return [y for y in out if y.strip()]


def split_tr(tr, src_parts):
    src_s, tr_s = [], _sents(tr)
    for part in src_parts:
        src_s += _sents(part)
    if len(src_parts) <= 1:
        return [tr]
    # 依字數比例定位（此處不細修，AI 審校時再標）
    total = sum(max(1, han(x)) for x in src_parts)
    cuts, acc = [], 0
    for part in src_parts[:-1]:
        acc += han(part)
        idx = int(round(acc / total * len(tr_s)))
        cuts.append(max(1, min(idx, len(tr_s) - 1)))
    cuts = sorted(set(cuts))
    while len(cuts) < len(src_parts) - 1:
        cuts.append(min(len(tr_s) - 1, cuts[-1] + 1))
    cuts = cuts[:len(src_parts) - 1]
    parts, prev = [], 0
    for c in cuts:
        parts.append(''.join(tr_s[prev:c])); prev = c
    parts.append(''.join(tr_s[prev:]))
    while len(parts) < len(src_parts):
        parts.append('')
    return parts


def build(p, splits):
    idx = p - 1
    sec = SECS[idx]; zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
    by_c = {}
    last = 0
    for k, c in enumerate(am[:len(zi)]):
        c = int(c)
        if c > 0:
            c = max(c, last)   # 強制單調
            last = c
            by_c.setdefault(c, []).append(k)
    front = [k for k in range(len(zi)) if k < len(am) and int(am[k]) == 0]

    # 切點
    pieces = {}
    for e in splits:
        n = int(e['n']); marks = e['markers']; tg = [int(x) for x in e['targets']]
        base = int(am[n - 1]) if n - 1 < len(am) else 0
        if tg != list(range(base, base + len(tg))):
            continue
        o, t = zi[n - 1]
        parts, cur, ok = [], o, True
        for m in marks:
            i = cur.find(m)
            if i <= 0:
                ok = False
                break
            parts.append(cur[:i]); cur = cur[i:]
        parts.append(cur)
        if not ok or len(parts) != len(tg):
            continue
        ts = split_tr(t, parts)
        for part, tr, c in zip(parts, ts, tg):
            pieces.setdefault(c, []).append((n, part, tr))

    doc = Document()
    st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s = doc.sections[0]
    s.page_width = Cm(21); s.page_height = Cm(29.7)
    s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6); s.left_margin = Cm(2.0); s.right_margin = Cm(2.0)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('四分律行事鈔・資持記　會本'), 18, bold=True)
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr(q.add_run('第%d篇　%s' % (p, sec['name'])), 11, color=RGBColor(0x66, 0x66, 0x66))

    def emit_ji(n, zo, zt):
        r = doc.add_paragraph(); rf = r.paragraph_format
        rf.space_before = Pt(4); rf.space_after = Pt(1); rf.line_spacing = 1.2
        rf.left_indent = Pt(14); rf.keep_with_next = True
        sr(r.add_run('【記%03d】' % n + zo), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(r, 'EEF2F6')
        b2 = doc.add_paragraph(); b2.paragraph_format.first_line_indent = Pt(20)
        b2.paragraph_format.left_indent = Pt(14)
        b2.paragraph_format.line_spacing = 1.28; b2.paragraph_format.space_after = Pt(2)
        sr(b2.add_run(zt), 10)

    if front:
        q = doc.add_paragraph(); q.paragraph_format.space_before = Pt(10)
        sr(q.add_run('〔篇前總釋〕'), 11, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
        for k in front:
            emit_ji(k + 1, zi[k][0], zi[k][1])

    used = set()
    for cno, it in enumerate(chao, 1):
        qq = doc.add_paragraph(); qf = qq.paragraph_format
        qf.space_before = Pt(8); qf.space_after = Pt(1); qf.line_spacing = 1.25; qf.keep_with_next = True
        sr(qq.add_run('【鈔%02d】' % cno + it[0]), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(qq, 'F4EFE2')
        a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
        a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
        sr(a2.add_run(it[1]), 10.5)
        # 合併切點片段與整段，按記號排序
        rows = [(n, part, tr) for n, part, tr in pieces.get(cno, [])]
        for k in by_c.get(cno, []):
            if k + 1 not in used:
                rows.append((k + 1, zi[k][0], zi[k][1]))
                used.add(k + 1)
        for n, part, tr in sorted(rows, key=lambda x: x[0]):
            emit_ji(n, part, tr)

    out = os.path.join(B, '白話', '會本_篇%02d_%s.docx' % (p, sec['name']))
    doc.save(out)
    return out, len(chao), len(zi), len(used)


if __name__ == '__main__':
    pians = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 7, 8, 9, 10]
    for p in pians:
        sp = os.path.join(SO, 'split_篇%02d.json' % p)
        splits = []
        if os.path.exists(sp):
            d = json.load(io.open(sp, encoding='utf-8-sig'))
            splits = d.get('splits', [])
        out, nc, nz, used = build(p, splits)
        print('篇%02d %-8s 鈔%3d 記%3d 切點%2d → %s' % (p, SECS[p - 1]['name'], nc, nz, len(splits), os.path.basename(out)))
