# -*- coding: utf-8 -*-
import io, re
from docx import Document
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
ps = [x.text for x in Document(B + r"\白話\會本_篇14_隨戒釋相.docx").paragraphs]
seg = ps[904:1656]
rows = []
i = 0
while i < len(seg):
    t = seg[i]
    m = re.match(r'^【(鈔|記)(\d+)】', t)
    if m:
        rows.append(dict(t=m.group(1), n=int(m.group(2)), body=t[m.end():], idx=len(rows)))
        i += 2
    else:
        i += 1
out = io.open(B + r"\_tmp_jz2\ji_anchors2.txt", "w", encoding="utf-8")
# 1) any 第N occurrences for N >= 11
pat = re.compile(r'第[一二三四五六七八九十]+')
for r in rows:
    if r["t"] != "記": continue
    hits = [(m.start(), m.group(0)) for m in pat.finditer(r["body"])]
    big = [h for h in hits if h[0] < 200]
    if big:
        out.write("記%03d\t%s\t%s\n" % (r["n"], "|".join("%d:%s"%(a,b) for a,b in big), r["body"][:70]))
out.write("\n==== 科文/懺法/二不定 類關鍵詞 ====\n")
KW = ["三十捨墮", "二不定", "初不定", "後不定", "懺法", "捨墮"]
for r in rows:
    if r["t"] != "記": continue
    for k in KW:
        p = r["body"].find(k)
        if 0 <= p < 120:
            out.write("記%03d\t%s@%d\t%s\n" % (r["n"], k, p, r["body"][max(0,p-20):p+60]))
out.close()
print("ok")
