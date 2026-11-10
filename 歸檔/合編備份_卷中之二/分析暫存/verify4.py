# -*- coding: utf-8 -*-
import io, re, html, collections
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
d = Document(B + r"\白話\行事鈔資持記句級合編_卷中之二.docx")
ps = [x.text for x in d.paragraphs if x.text.strip()][3:]
docx_pairs = [(ps[2*k], ps[2*k+1]) for k in range(len(ps)//2)]
h = io.open(B + r"\docs\hebian\卷中之二.html", encoding="utf-8").read()
items = re.findall(r'<div class="(o2|o)">(.*?)</div><div class="t">(.*?)</div>', h, re.S)
html_pairs = [(html.unescape(a), html.unescape(b)) for cls,a,b in items]
print('docx pairs', len(docx_pairs), 'html pairs', len(html_pairs))
bad = [(i, a[0][:30], b[0][:30]) for i,(a,b) in enumerate(zip(docx_pairs, html_pairs)) if a[0]!=b[0] or a[1]!=b[1]]
print('不一致', len(bad))
for x in bad[:5]: print(x)
print('鈔記順序一致:', [p[0][:3] for p in html_pairs[:6]])
# 找 摩觸 前後
k = [i for i,(a,b) in enumerate(html_pairs) if a.startswith('【鈔】摩觸女人戒第二。')][0]
for j in range(k-3, k+3):
    print(j, html_pairs[j][0][:34])
