# -*- coding: utf-8 -*-
import io, os
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\fix_parts_g3.tsv"
lines = io.open(p, encoding="utf-8").read().split("\n")
want = {"78", "90"}  # seg numbers to show fully (short ones)
for l in lines:
    if not l: continue
    c = l.split("\t")
    if c[2] in want:
        print("=== %s %s seg=%s" % (c[0], c[1], c[2]))
        print(c[3])
        print()
