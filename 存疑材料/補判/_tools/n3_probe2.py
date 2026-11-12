# -*- coding: utf-8 -*-
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
def rd(p):
    with open(p, encoding="utf-8") as f: return f.read()
t = rd(os.path.join(ROOT, "TXT_分卷", "01_行事鈔", "00_卷首.txt"))
paras = [l.strip() for l in t.split("\n") if l.strip()]
for i, p in enumerate(paras, 1):
    if i <= 8 or 40 <= i <= 60:
        print(i, p[:70])
print("total", len(paras))
print("---- out ----")
o = [l.strip() for l in rd(os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", "00_卷首.txt")).split("\n") if l.strip()]
print("out total", len(o))
for i, p in enumerate(o, 1):
    if 40 <= i <= 56:
        print(i, p[:70])
