# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\資持記\01_上一上.txt"
t = io.open(p, encoding="utf-8").read()
for i, ln in enumerate(t.split("\n")):
    if "冠超" in ln or "篇聚名報" in ln or "標宗顯德" in ln:
        print(i+1, ln.strip()[:200])
