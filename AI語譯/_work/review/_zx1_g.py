# -*- coding: utf-8 -*-
import io, re
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\資持記\01_上一上.txt"
t = io.open(p, encoding="utf-8").read()
lines = t.split("\n")
for kw in ["三藏分宗", "五十餘家", "濫涉", "專隅"]:
    print("#### " + kw)
    for i, ln in enumerate(lines):
        if kw in ln:
            for j in range(max(0,i-1), min(len(lines), i+2)):
                s = lines[j].strip()
                if s: print("  %d: %s" % (j+1, s[:300]))
            print("  ---")
