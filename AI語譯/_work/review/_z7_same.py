# -*- coding: utf-8 -*-
import sys, io, os
import _z6_lib as L
nums = list(range(1786, 1811))
bad = 0
for n in nums:
    for s in L.mat(n):
        cur = L.para(s["chunk"], s["para"]).strip()
        mt = s["trans"].strip()
        if cur != mt:
            bad += 1
            print("DIFF", s["idx"], s["chunk"], s["para"], len(cur), len(mt))
print("TOTAL DIFF", bad)
