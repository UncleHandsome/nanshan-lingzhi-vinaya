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
    m = re.match(r'^【(鈔|記)(\d+)】(（[^）]*）)?', t)
    if m:
        rows.append(dict(kind=m.group(1), num=int(m.group(2)), sub=(m.group(3) or ''), body=t[m.end():]))
        i += 2
    else:
        i += 1
want = [82,83,84, 463,464,465,466,467,468,469,470]
out = io.open(B + r"\_tmp_jz2\buding.txt", "w", encoding="utf-8")
for r in rows:
    if r['num'] in [463,464,465,466,467,468,469] and r['kind']=='記':
        out.write("記%s%s\t%s\n\n" % (r['num'], r['sub'], r['body']))
out.close()
for r in rows:
    if r['kind']=='鈔' and 82 <= r['num'] <= 85:
        print('鈔%d: %s' % (r['num'], r['body'][:120]))
print('----')
for r in rows:
    if r['kind']=='記' and 463 <= r['num'] <= 468:
        print('記%d%s: %s' % (r['num'], r['sub'], r['body'][:150]))
