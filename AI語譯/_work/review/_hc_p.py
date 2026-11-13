# -*- coding: utf-8 -*-
import sys
import _hc_lib as L

cmd = sys.argv[1]
if cmd == "p":
    print(L.para(sys.argv[2], int(sys.argv[3])))
elif cmd == "i":
    for c in sys.argv[2:]:
        print(c, L.idx(c))
elif cmd == "f":
    needle = sys.argv[2]
    for c, i in L.grep_all(needle):
        print(c, i)
