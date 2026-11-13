# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\資持記\01_上一上.txt"
t = io.open(p, encoding="utf-8").read()
for kw in ["戒德難思", "眾象", "標宗"]:
    print("### " + kw)
    for i, ln in enumerate(t.split("\n")):
        if kw in ln:
            print(" ", i+1, ln.strip()[:160])
