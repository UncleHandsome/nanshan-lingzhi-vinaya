# -*- coding: utf-8 -*-
import io
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
n=0
for ln in lines:
    p = ln.split("\t")
    t = p[3]
    i = t.find("」「")
    while i >= 0:
        n+=1
        print(p[1], p[2], "...", t[max(0,i-40):i+40].replace("\n"," "), "...")
        i = t.find("」「", i+1)
print("total", n)
