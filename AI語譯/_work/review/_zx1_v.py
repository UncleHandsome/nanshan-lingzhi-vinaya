# -*- coding: utf-8 -*-
"""套用後回讀：印出每處改動前後 40 字的實況（不整段重讀）。"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _zx1_lib as L


def show(dat):
    seen = {}
    for e in dat:
        key = (e["chunk"], e["para"])
        if key not in seen:
            seen[key] = L.para(e["chunk"], e["para"])
        t = seen[key]
        i = t.find(e["new"])
        if i < 0:
            print(u"!! 找不到新版 %s#%d %r" % (e["chunk"], e["para"], e["new"]))
            continue
        a = max(0, i - 30)
        b = min(len(t), i + len(e["new"]) + 30)
        print(u"  %s#%d …%s…" % (e["chunk"], e["para"], t[a:b]))


if __name__ == "__main__":
    show(json.load(io.open(sys.argv[1], encoding="utf-8")))
