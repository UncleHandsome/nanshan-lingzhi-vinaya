# -*- coding: utf-8 -*-
import csv, io, os, glob

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_csv_all.txt"
w = io.open(out, "w", encoding="utf-8")
for p in sorted(glob.glob(os.path.join(B, "篇*.csv"))):
    rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))
    if not rows:
        continue
    hdr = rows[0]
    has = len(hdr) >= 5 and "對應鈔號" in hdr[4]
    nz = 0
    ji = 0
    for r in rows[1:]:
        if len(r) < 5:
            continue
        if r[0] == "記":
            ji += 1
            if r[4].strip():
                nz += 1
    w.write("%-28s rows=%-4d 記=%-4d filled=%-4d hdr=%s\n" % (os.path.basename(p), len(rows), ji, nz, hdr))
w.close()
print("ok")
