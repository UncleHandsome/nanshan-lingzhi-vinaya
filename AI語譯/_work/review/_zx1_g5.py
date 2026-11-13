# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\01_四分律刪繁補闕行事鈔.txt"
t = io.open(p, encoding="utf-8").read()
for kw in ["冠超", "五乘之軌導"]:
    print("### " + kw)
    n = 0
    for i, ln in enumerate(t.split("\n")):
        if kw in ln:
            print(" ", i+1, ln.strip()[:200]); n += 1
            if n > 4: break
