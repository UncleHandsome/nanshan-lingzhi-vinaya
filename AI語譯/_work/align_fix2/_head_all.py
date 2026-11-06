# -*- coding: utf-8 -*-
import csv, io, os, glob

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_head_all.txt"
w = io.open(out, "w", encoding="utf-8")

for p in sorted(glob.glob(os.path.join(B, "篇*.csv"))):
    rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
    if not any(r and r[0] == "記" and r[4].strip() for r in rows):
        continue
    w.write("======== %s\n" % os.path.basename(p))
    rec = [(r[0], int(r[1]), r[2], r[4]) for r in rows if len(r) >= 5]
    for typ, no, txt, dui in rec[:8]:
        if typ == "鈔":
            w.write("  鈔%-2d len=%-3d %s\n" % (no, len(txt), txt[:80]))
        else:
            w.write("  記%-2d -> 鈔%-4s %s\n" % (no, dui, txt[:80]))
    w.write("\n")
w.close()
print("ok")
