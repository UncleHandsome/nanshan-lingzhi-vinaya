# -*- coding: utf-8 -*-
import csv, io, os, glob

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_first_ji.txt"
w = io.open(out, "w", encoding="utf-8")

for p in sorted(glob.glob(os.path.join(B, "篇*.csv"))):
    rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
    rec = [(r[0], int(r[1]), r[2], r[4]) for r in rows if len(r) >= 5 and r[1].strip().isdigit()]
    if not any(t == "記" and d.strip() for t, n, x, d in rec):
        continue
    cao = {n: x for t, n, x, d in rec if t == "鈔"}
    w.write("======== %s\n" % os.path.basename(p))
    # print first 3 記 with assigned cao
    cnt = 0
    for t, n, x, d in rec:
        if t == "記" and d.strip():
            dd = int(d)
            w.write("  記%-3d -> 鈔%-3d | 鈔len=%-4d %s\n" % (n, dd, len(cao.get(dd, "")), cao.get(dd, "")[:60]))
            w.write("        JI: %s\n" % x[:60])
            cnt += 1
            if cnt >= 3:
                break
    w.write("\n")
w.close()
print("ok")
