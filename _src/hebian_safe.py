# -*- coding: utf-8 -*-
"""合編（安全版）：每篇先排鈔文、再排記文，避免逐句交錯錯位"""
import io, os, re, sys, importlib.util
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

# 自己載入鈔文（帶卷別）
def load(src, tr):
    S = os.path.join(B, 'TXT_分卷', src)
    T = os.path.join(B, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((k, sp, tt))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
SECS = []
cur = None
for k, sp, tt in load('01_行事鈔', '01_行事鈔'):
    vol = k.split('_', 1)[1] if '_' in k else k
    if vol.startswith('卷首'):
        vol = '卷上之一'
    if k.startswith('00_'):
        continue
    for i, o in enumerate(sp):
        m = PATS.match(o.strip())
        if m:
            if any(x['name'] == m.group(1) for x in SECS):
                cur = next(x for x in SECS if x['name'] == m.group(1))
            else:
                cur = dict(name=m.group(1), items=[])
                SECS.append(cur)
            continue
        if cur is not None:
            cur['items'].append((o, tt[i] if i < len(tt) else '', vol))

FONT = 'SimSun'
LATIN = 'Times New Roman'
VOLS = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
        '卷中之一', '卷中之二', '卷中之三', '卷中之四',
        '卷下之一', '卷下之二', '卷下之三', '卷下之四']
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')


def sr(run, size, bold=False, color=None):
    run.font.size = Pt(size)
    run.bold = bold
    run.font.name = LATIN
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        run.font.color.rgb = color


def shade(p, color):
    from docx.oxml import OxmlElement
    sh = OxmlElement('w:shd')
    sh.set(qn('w:fill'), color)
    p._p.get_or_add_pPr().append(sh)


def main():
    for vol in VOLS:
        doc = Document()
        st = doc.styles['Normal']; st.font.size = Pt(10); st.font.name = LATIN
        st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
        s = doc.sections[0]
        s.page_width = Cm(21); s.page_height = Cm(29.7)
        s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.5)
        s.left_margin = Cm(1.8); s.right_margin = Cm(1.8)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr(p.add_run('行事鈔・資持記　句級合編'), 19, bold=True)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr(p.add_run(vol), 11, color=RGBColor(0x66, 0x66, 0x66))

        printed = 0
        for idx, sec in enumerate(SECS):
            chao = [(it[0], it[1]) for it in sec['items'] if it[2] == vol and not SKIP.match(it[0].strip())]
            if not chao:
                continue
            first_vol = next((it[2] for it in sec['items'] if not SKIP.match(it[0].strip())), vol)
            zi = ZI.get(idx, []) if first_vol == vol else []
            head = doc.add_paragraph(); head.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = head.paragraph_format; pf.space_before = Pt(14); pf.space_after = Pt(6)
            sr(head.add_run('第%d篇　%s' % (idx + 1, sec['name'])), 14, bold=True)
            # 鈔
            lab = doc.add_paragraph(); sr(lab.add_run('〔鈔文〕'), 11, bold=True, color=RGBColor(0x6b, 0x5b, 0x4a))
            for o, t in chao:
                q = doc.add_paragraph(); qf = q.paragraph_format
                qf.space_before = Pt(5); qf.space_after = Pt(0); qf.line_spacing = 1.25; qf.keep_with_next = True
                sr(q.add_run('【鈔】' + o), 10, color=RGBColor(0x6b, 0x5b, 0x4a)); shade(q, 'F4EFE2')
                a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
                a2.paragraph_format.line_spacing = 1.35; a2.paragraph_format.space_after = Pt(2)
                sr(a2.add_run(t), 10.5)
            # 記
            if zi:
                lab = doc.add_paragraph(); lab.paragraph_format.space_before = Pt(10)
                sr(lab.add_run('〔資持記〕'), 11, bold=True, color=RGBColor(0x21, 0x5a, 0x8a))
                for o, t in zi:
                    q = doc.add_paragraph(); qf = q.paragraph_format
                    qf.space_before = Pt(4); qf.space_after = Pt(0); qf.line_spacing = 1.22; qf.keep_with_next = True
                    sr(q.add_run('【記】' + o), 9.5, color=RGBColor(0x21, 0x5a, 0x8a)); shade(q, 'EEF2F6')
                    a2 = doc.add_paragraph(); a2.paragraph_format.first_line_indent = Pt(20)
                    a2.paragraph_format.line_spacing = 1.3; a2.paragraph_format.space_after = Pt(2)
                    sr(a2.add_run(t), 10)
            printed += 1
        out = os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % vol)
        doc.save(out)
        print('%s 篇%d 段%d' % (vol, printed, len(doc.paragraphs)))


if __name__ == '__main__':
    main()
