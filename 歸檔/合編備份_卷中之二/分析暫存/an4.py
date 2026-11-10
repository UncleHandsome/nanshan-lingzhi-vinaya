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
        rows.append((m.group(1), int(m.group(2)), K2+i, t[m.end():], seg[i+1] if i+1 < len(seg) else ""))
        i += 2
    else:
        i += 1
pat = re.compile(r'第[一二三四五六七八九十]+(?=〔|。|，|、|名|中|之|戒)')
out = io.open(B + r"\_tmp_jz2\ji_anom.txt", "w", encoding="utf-8")
for typ, num, pos, body, tr in rows:
    if typ != "記": continue
    hits = [(m.start(), m.group(0)) for m in pat.finditer(body[:80])]
    if hits:
        out.write("記%03d\t%04d\t%s\t%s\n" % (num, pos, ";".join("%d:%s"%(a,b) for a,b in hits), body[:80]))
out.close()
print("done")
