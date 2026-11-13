# -*- coding: utf-8 -*-
"""7K 中四上 a：列某檔指定段（1-based）的原文與現譯。"""
import sys

import _z6_lib as L


def main():
    n = int(sys.argv[1])
    want = set(int(x) for x in sys.argv[2:])
    segs = L.mat(n)
    for i, s in enumerate(segs, 1):
        if want and i not in want:
            continue
        cur = L.para(s["chunk"], s["para"]).strip()
        print(u"== %s %s#%d ==" % (s["idx"], s["chunk"], s["para"]))
        print(u"[原] " + s["orig"])
        print(u"[譯] " + cur)


if __name__ == "__main__":
    main()
