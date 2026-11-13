# -*- coding: utf-8 -*-
import io, json, sys
import _z6_lib as L
for n in [int(x) for x in sys.argv[1:]]:
    d = json.load(io.open("_z7_e%d.json" % n, encoding="utf-8"))
    for e in d["edits"]:
        p = L.para(e["chunk"], e["para"])
        c = p.count(e["old"])
        if c != 1:
            print("BAD", n, e["para"], c, repr(e["old"][:50]))
print("check done")
