# -*- coding: utf-8 -*-
"""以備份比對：段數不變、僅預定段落變動、LF 不變。"""
import io
import os
import sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", u"資持記")
BAK = os.path.join(ROOT, u"歸檔", "7K卷修正前", u"資持記")

CHUNKS = ["02c", "05a", "05b", "06a", "07a", "07e", "08c", "09b", "10a",
          "11c", "12a", "13a", "13c", "14b", "14c", "15a", "15b", "15c",
          "15e", "16c"]


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def resolve(c):
    for f in os.listdir(OUT):
        if f.endswith(".txt") and f.split("_")[0] == c:
            return f[:-4]
    raise SystemExit(c)


for c in CHUNKS:
    full = resolve(c)
    cur = rd(os.path.join(OUT, full + ".txt"))
    bak = rd(os.path.join(BAK, c + "_v.txt"))
    sp = "\n\n"
    a, b = bak.split(sp), cur.split(sp)
    diff = [i + 1 for i in range(min(len(a), len(b))) if a[i] != b[i]]
    print("%-16s paras %d->%d  lines %d->%d  bytes %d->%d  changed=%s" % (
        full, len(a), len(b), bak.count("\n"), cur.count("\n"),
        len(bak.encode("utf-8")), len(cur.encode("utf-8")), diff))
