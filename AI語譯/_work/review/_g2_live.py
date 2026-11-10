# -*- coding: utf-8 -*-
import io, re, csv, sys
P = r"AI語譯/out/04_比丘尼鈔/05a_卷下之上.txt"
t = io.open(P, encoding="utf-8").read()
paras = re.split(r"\r?\n\r?\n", t)
print("n paras", len(paras))
for i in (21, 22, 27, 28, 30):
    if i < len(paras):
        p = paras[i]
        print("=" * 90)
        print("seg", i + 1, "newlines", p.count("\n"), "len", len(p))
        print(repr(p[:600]))
