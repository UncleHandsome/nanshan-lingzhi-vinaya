# -*- coding: utf-8 -*-
import csv, io, os, json

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(B, "AI語譯", "_work", "align_fix2", "_csv28_trans.txt")
w = io.open(out, "w", encoding="utf-8")

p = os.path.join(B, "合編材料", "篇28_沙彌別法.csv")
rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
ji = [(int(r[1]), r[2], int(r[4])) for r in rows if r[0] == "記"]
cao = {int(r[1]): r[2] for r in rows if r[0] == "鈔"}

for no, txt, dui in ji:
    a = cao.get(dui, "")
    pv = cao.get(dui - 1, "")
    nx = cao.get(dui + 1, "")
    w.write("記%-3d -> 鈔%-3d\n" % (no, dui))
    w.write("  JI : %s\n" % txt[:70])
    w.write("  PRE(%d): ...%s\n" % (dui - 1, pv[-50:]))
    w.write("  ASS(%d): %s\n" % (dui, a[:50]))
    w.write("  NXT(%d): %s\n" % (dui + 1, nx[:50]))
    w.write("\n")
w.close()
print("ok")
