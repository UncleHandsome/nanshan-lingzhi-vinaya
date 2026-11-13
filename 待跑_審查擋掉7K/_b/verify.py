# -*- coding: utf-8 -*-
import io, os, glob
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BAK = os.path.join(ROOT, "歸檔", "7K擋檔修正前", "02_戒疏")
OUT = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
for b in sorted(glob.glob(os.path.join(BAK, "*_b.txt"))):
    name = os.path.basename(b)[:-6]
    p = os.path.join(OUT, name + ".txt")
    ra = io.open(b, encoding="utf-8", newline="").read()
    rb = io.open(p, encoding="utf-8", newline="").read()
    la = ra.split("\r\n")
    lb = rb.split("\r\n")
    crlf = ("\r\n" in ra) and ("\r\n" in rb)
    diff = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    print("%-24s lines %d/%d CRLF=%s 異動行=%d %s" % (
        name, len(la), len(lb), crlf, len(diff), "" if len(la) == len(lb) else "!! 行數不同"))
    print("    行號:", ",".join(str(i + 1) for i in diff))
