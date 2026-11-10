# -*- coding: utf-8 -*-
import io, re, hashlib, collections
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p = B + r"\白話\行事鈔資持記句級合編_卷中之二.docx"
d = Document(p)
ps = [x.text for x in d.paragraphs]
print('paras', len(ps))
# 備份比對：全域字元集與段落集合
bak = B + r"\歸檔\合編備份_卷中之二\行事鈔資持記句級合編_卷中之二.docx"
d0 = Document(bak)
ps0 = [x.text for x in d0.paragraphs]
print('backup paras', len(ps0))
print('非空段數', len([t for t in ps if t.strip()]), '原', len([t for t in ps0 if t.strip()]))
print('段落多重集合相同:', collections.Counter(ps) == collections.Counter(ps0))
print('字元多重集合相同:', collections.Counter(''.join(ps)) == collections.Counter(''.join(ps0)))
# 顏色/字型是否保留
runs = [(r.text[:6], r.font.size, r.font.name, r.font.bold) for q in d.paragraphs[:6] for r in q.runs]
print('前6段 runs:', runs)
# 印出前 30 個非空段首句
ne = [t for t in ps if t.strip()]
for i, t in enumerate(ne[:24]):
    print(i, repr(t[:46]))
