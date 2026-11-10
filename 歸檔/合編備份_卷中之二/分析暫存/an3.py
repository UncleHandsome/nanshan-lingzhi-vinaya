# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
ps = [x.text for x in Document(B + r"\白話\會本_篇14_隨戒釋相.docx").paragraphs]
K2, K3 = 904, 1656
seg = ps[K2:K3]
rows = []
i = 0
while i < len(seg):
    t = seg[i]
    m = re.match(r'^【(鈔|記)(\d+)】', t)
    if m:
        rows.append((m.group(1), int(m.group(2)), K2+i, t[m.end():]))
        i += 2
    else:
        i += 1
# 鈔 starts
out = io.open(B + r"\_tmp_jz2\chao_starts.txt", "w", encoding="utf-8")
for k,(typ,num,pos,body) in enumerate(rows):
    if typ == "鈔":
        out.write("鈔%03d\t%04d\t%s\n" % (num, pos, body[:45]))
out.close()
pat = re.compile(r'戒第[一二三四五六七八九十]+|第[一二三四五六七八九十]+戒')
out2 = io.open(B + r"\_tmp_jz2\jie_anchor.txt", "w", encoding="utf-8")
for k,(typ,num,pos,body) in enumerate(rows):
    m = pat.search(body[:40]) or pat.search(body[:120])
    if m:
        out2.write("%s%03d\t%04d\t[%s]\t%s\n" % (typ, num, pos, m.group(0), body[:70]))
out2.close()
print("rows", len(rows), "chao", sum(1 for r in rows if r[0]=="鈔"), "ji", sum(1 for r in rows if r[0]=="記"))
