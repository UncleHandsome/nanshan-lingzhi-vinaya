# -*- coding: utf-8 -*-
"""篇19 記23 中片補譯；篇18 記116 切前/後並把前段移到鈔70 之後"""
import os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WH = os.path.join(B, '白話')

def set_text(p, text):
    for r in p.runs:
        r.text = ''
    p.add_run(text) if not p.runs else setattr(p.runs[0], 'text', text)

# ---- 篇19 ----
f = os.path.join(WH, '會本_篇19_鉢器制聽.docx')
d = Document(f)
ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記023】（中）'):
        body = ps[i + 1]
        set_text(body, '「聽門物多」是說寺門的器物繁多，不能一一分科條約，所以稱為「雜列」。')
        print('篇19 中片補譯完成')
        break
d.save(f)

# ---- 篇18 ----
f = os.path.join(WH, '會本_篇18_四藥受淨.docx')
d = Document(f)
ps = d.paragraphs
tag_i = src_i = body_i = None
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記116】'):
        tag_i, body_i = i, i + 1
        break
if tag_i is None:
    print('篇18 找不到記116')
else:
    tag_p, body_p = ps[tag_i], ps[tag_i + 1]
    src = tag_p.text.replace('【記116】（接前文）', '')
    tr = body_p.text
    k = src.find('三問，答中')
    if k <= 0:
        print('篇18 記116 無切點')
    else:
        a_src, b_src = src[:k], src[k:]
        # 譯文切點：找「第三個提問」或「三問」
        kt = tr.find('第三個提問')
        if kt < 0:
            kt = tr.find('三問')
        if kt <= 0:
            kt = len(tr) // 2
        a_tr, b_tr = tr[:kt], tr[kt:]
        from docx.shared import Pt, RGBColor
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        def new_par(text, is_tag):
            p = d.add_paragraph()
            r = p.add_run(text)
            r.font.size = Pt(9.5 if is_tag else 10)
            return p

        p1 = new_par('【記116】（前）' + a_src, True)
        b1 = new_par(a_tr, False)
        p2 = new_par('【記116】（後）' + b_src, True)
        b2 = new_par(b_tr, False)
        # 移動到鈔70 之後
        idx70 = None
        for i, p in enumerate(d.paragraphs):
            if p.text.strip().startswith('【鈔70】'):
                idx70 = i
                break
        if idx70 is not None:
            anchor = d.paragraphs[idx70 + 2]._element  # 鈔70 原文、譯文之後
            for el in (p1._element, b1._element):
                anchor.addprevious(el)
        # 刪除原記116（改由前/後兩段取代）
        tag_p._element.getparent().remove(tag_p._element)
        body_p._element.getparent().remove(body_p._element)
        # 刪除臨時附加的 p2/b2（保留原位置？）
        p2._element.getparent().remove(p2._element)
        b2._element.getparent().remove(b2._element)
        d.save(f)
        print('篇18 記116 已切分並前移')
