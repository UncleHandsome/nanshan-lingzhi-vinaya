# -*- coding: utf-8 -*-
import sys, io, json
sys.path.insert(0, r"AI語譯\_work\review")
import _zx1_lib as L
dat = json.load(io.open(r"AI語譯\_work\review\_zx1_e1306.json", encoding="utf-8"))
for e in dat:
    p = L.para(e["chunk"], e["para"])
    c = p.count(e["old"])
    if c != 1:
        print("BAD %d count=%d old=%r" % (e["para"], c, e["old"]))
print("--- para14 ---")
print(L.para("01b_上一上", 14))
