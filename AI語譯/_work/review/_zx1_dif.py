# -*- coding: utf-8 -*-
import sys, difflib
sys.path.insert(0, r"AI語譯\_work\review")
import _zx1_lib as L
for n, segs in ((1296, ["0003","0007"]), (1303, ["0001","0002","0006"])):
    for sg in L.mat(n):
        if sg["seg"] in segs:
            a = sg["trans"]; b = L.para(sg["chunk"], sg["para"]).strip()
            sm = difflib.SequenceMatcher(None, a, b)
            print("== %s-%s %s#%d" % (sg["idx"], sg["seg"], sg["chunk"], sg["para"]))
            for tag,i1,i2,j1,j2 in sm.get_opcodes():
                if tag!="equal":
                    print("  ", tag, repr(a[i1:i2]), "->", repr(b[j1:j2]))
            print()
