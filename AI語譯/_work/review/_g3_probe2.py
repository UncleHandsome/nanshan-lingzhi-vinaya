# -*- coding: utf-8 -*-
import io, os
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
SRC = os.path.join(BASE, "report_parts.tsv")
rows = []
for line in io.open(SRC, encoding="utf-8"):
    line = line.rstrip("\r\n")
    if not line: continue
    c = line.split("\t")
    if len(c) == 13:
        rows.append(c)
for needle in [u"善惡業性", u"業理", u"戒體的道理", u"業理微隱", u"略舉篇聚"]:
    hit = [(c[0], c[1], c[2], c[3]) for c in rows if needle in c[10]]
    print(needle, "->", hit[:6])
# also what chunk/seg is 24-0250 and its neighbours
for c in rows:
    if c[0] == "24-0250":
        print("ROW 24-0250:", c[1], c[2], "seg", c[3], "| ORIG:", c[8][:60])
        print("  CURRENT:", c[10][:80])
