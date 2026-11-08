# -*- coding: utf-8 -*-
import io, os
SRC = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\report_parts.tsv"
with io.open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\r\n")
        if not line: continue
        c = line.split("\t")
        if len(c) == 13 and c[0] == "32-0229":
            cur = c[10]
            i = cur.find("若為惡者")
            print("idx", i)
            print(repr(cur[i-40:i+40]))
            print("---- full tail ----")
            print(repr(cur[-120:]))
