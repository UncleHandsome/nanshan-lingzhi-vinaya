# -*- coding: utf-8 -*-
import csv, io, os

p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\篇26_瞻病送終.csv"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_csv26.txt"

rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))
w = io.open(out, "w", encoding="utf-8")
w.write("rows=%d header=%s\n" % (len(rows), rows[0]))
for i, r in enumerate(rows[1:], 1):
    if len(r) < 5:
        w.write("ROW %d BAD len=%d %s\n" % (i, len(r), r))
        continue
    typ, no, orig, bai, dui = r[0], r[1], r[2], r[3], r[4]
    w.write("[%d] %s %s -> 對應鈔號=%r  len=%d | %s\n" % (i, typ, no, dui, len(orig), orig[:50]))
w.close()
print("ok")
