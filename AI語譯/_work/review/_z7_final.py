# -*- coding: utf-8 -*-
import os
import _z6_lib as L
for c in ["11a_中四上","11b_中四上","11c_中四上"]:
    t,s=L.paras(c); cur=(len(t.split(s)),t.count("\n"))
    b=L.rd(os.path.join(L.BAKDIR,c+"_v.txt")); bak=(len(b.split(s)),b.count("\n"))
    print(c,cur,bak,"OK" if cur==bak else "MISMATCH")
print(L.para("11c_中四上",3)[:260])
