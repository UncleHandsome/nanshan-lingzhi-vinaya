# -*- coding: utf-8 -*-
import os
from docx import Document
from docx.shared import Pt, RGBColor

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WH = os.path.join(B, '白話')


def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)


# 篇19 記23（中）補譯
f19 = os.path.join(WH, '會本_篇19_鉢器制聽.docx')
d = Document(f19)
ps = d.paragraphs
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記023】（中）'):
        set_text(ps[i + 1], '「聽門物多」是說寺門的器物繁多，不能一一分科條約，所以稱為「雜列」。')
        break
d.save(f19)
print('篇19 ok')

# 篇18 記116 切前後
f18 = os.path.join(WH, '會本_篇18_四藥受淨.docx')
d = Document(f18)
ps = d.paragraphs
ti = None
for i, p in enumerate(ps):
    if p.text.strip().startswith('【記116】'):
        ti = i
        break
if ti is None:
    print('篇18 無記116')
else:
    tag, body = ps[ti], ps[ti + 1]
    src = tag.text.strip()
    src = src[src.find('】') + 1:]
    tr = body.text
    k = src.find('三問，答中')
    kt = tr.find('第三個提問')
    if kt < 0:
        kt = tr.find('三問')
    if k > 0:
        a_src, b_src = src[:k], src[k:]
        if kt <= 0:
            kt = len(tr) // 2
        a_tr, b_tr = tr[:kt], tr[kt:]
        set_text(tag, '【記116】（後）' + b_src)
        set_text(body, b_tr)
        # 建立前段
        p_tag = d.add_paragraph()
        r = p_tag.add_run('【記116】（前）' + a_src)
        r.font.size = Pt(9.5)
        p_tr = d.add_paragraph()
        r2 = p_tr.add_run(a_tr)
        r2.font.size = Pt(10)
        # 移到鈔71 之前
        c71 = None
        for p in d.paragraphs:
            if p.text.strip().startswith('【鈔71】'):
                c71 = p
                break
        if c71 is not None:
            c71._element.addprevious(p_tag._element)
            c71._element.addprevious(p_tr._element)
        d.save(f18)
        print('篇18 記116 已切前後')
    else:
        print('篇18 找不到切點')
