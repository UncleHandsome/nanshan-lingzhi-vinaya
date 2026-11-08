# -*- coding: utf-8 -*-
import io, os, difflib
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
SRC = os.path.join(BASE, "AI語譯", "_work", "review", "report_parts.tsv")
OUT = os.path.join(BASE, "AI語譯", "_work", "review", "fix_parts_g3.tsv")

src = {}
order = []
with io.open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\r\n")
        if not line: continue
        c = line.split("\t")
        if len(c) == 13 and c[1] in ("02_戒疏", "03_業疏"):
            src[(c[1], c[2], c[3])] = c
            order.append((c[1], c[2], c[3]))

buf = []
n = 0
with io.open(OUT, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\r\n")
        if not line: continue
        c = line.split("\t")
        assert len(c) == 4, (line,)
        key = (c[0], c[1], c[2])
        old = src[key][10]
        new = c[3]
        n += 1
        sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
        parts = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal": continue
            pre = old[max(0, i1-18):i1]
            parts.append("%s[%s] -> [%s]%s" % (tag, old[i1:i2], new[j1:j2], new[j2:j2+18]))
        ratio = sm.ratio()
        buf.append("[%d] %s %s seg=%s  sim=%.3f  len %d->%d" % (n, c[0], c[1], c[2], ratio, len(old), len(new)))
        for p in parts:
            buf.append("    " + p)
        buf.append("")

print("\n".join(buf))
print("rows:", n)
