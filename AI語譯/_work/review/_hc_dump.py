# -*- coding: utf-8 -*-
import sys
import _hc_lib as L

pairs = []
for a in sys.argv[1:]:
    c, p = a.split(":")
    pairs.append((c, int(p)))
for c, p in pairs:
    t = L.para(c, p)
    print(u"===== %s#%d (len %d) =====" % (c, p, len(t)))
    print(t)
    print("")
