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
    eol = "\r\n" if "\r\n" in ra else "\n"
    la = ra.split(eol)
    lb = rb.split(eol)
    diff = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    print("%-24s eol=%r lines %d/%d 非空段 %d/%d 異動=%d" % (
        name, eol, len(la), len(lb),
        sum(1 for x in la if x.strip()), sum(1 for x in lb if x.strip()), len(diff)))
    for i in diff:
        print("   L%-4d - %s" % (i + 1, la[i][:40]))
        print("        + %s" % (lb[i][:40],))
