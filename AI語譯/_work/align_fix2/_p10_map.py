# -*- coding: utf-8 -*-
import csv, io, os

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_p10_map.txt"
w = io.open(out, "w", encoding="utf-8")

for name in ["篇10_說戒正儀.csv", "篇02_集僧通局.csv", "篇04_受欲是非.csv"]:
    p = os.path.join(B, name)
    rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
    rec = [(r[0], int(r[1]), r[2], r[4]) for r in rows if len(r) >= 5 and r[1].strip().isdigit()]
    w.write("======== %s\n" % name)
    for t, n, x, d in rec:
        if t == "鈔":
            w.write("鈔%-3d len=%-4d %s\n" % (n, len(x), x[:70]))
        else:
            w.write("    記%-3d -> %-4s %s\n" % (n, d, x[:70]))
    w.write("\n")
w.close()
print("ok")
