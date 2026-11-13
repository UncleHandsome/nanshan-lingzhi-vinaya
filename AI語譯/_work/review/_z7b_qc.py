import sys
sys.path.insert(0,'.')
import _z6_lib as L
for c in ["10c_中三下","10d_中三下"]:
    t,s = L.paras(c)
    print(c, "paras", len(t.split(s)), "lines", t.count("\n"), "crlf", "\r\n" in t)
# duplicate-sentence check on changed range
import re
for c,a,b in [("10c_中三下",10,66),("10d_中三下",1,15)]:
    for p in range(a,b):
        x = L.para(c,p)
        # find repeated 8-char substrings
        for i in range(len(x)-8):
            seg = x[i:i+8]
            if x.count(seg) > 1 and x.find(seg, i+1) == i+8:
                print("DUP?", c, p, seg); break
