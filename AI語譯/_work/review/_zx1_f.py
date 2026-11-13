# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"AI語譯\_work\review")
import _zx1_lib as L
for f in ("01a_上一上","01b_上一上"):
    t,s = L.paras(f)
    ps = t.split(s)
    print(f, len(ps), "段", "len", len(t), "CRLF", "\r\n" in t)
# 抽讀 01b 首尾
print()
print(L.para("01b_上一上",1)[:80])
print("...")
print(L.para("01b_上一上",66)[:80])
