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
        rows.append(dict(t=m.group(1), n=int(m.group(2)), body=t[m.end():], tr=seg[i+1] if i+1 < len(seg) else "", idx=len(rows)))
        i += 2
    else:
        i += 1
pat = re.compile(r'第([一二三四五六七八九十]+)[。，、]?〔')
out = io.open(B + r"\_tmp_jz2\ji_anchor_ctx.txt", "w", encoding="utf-8")
for r in rows:
    if r["t"] != "記": continue
    for m in pat.finditer(r["body"]):
        s = max(0, m.start()-25); e = min(len(r["body"]), m.end()+45)
        out.write("記%03d\tpos%d\t...%s...\n" % (r["n"], m.start(), r["body"][s:e]))
out.close()
print("ok")
