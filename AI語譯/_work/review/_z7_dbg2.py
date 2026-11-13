# -*- coding: utf-8 -*-
import io, json
import _z6_lib as L
d = json.load(io.open("_z7_e1786.json", encoding="utf-8"))
for e in d["edits"]:
    p = L.para(e["chunk"], e["para"])
    c = p.count(e["old"])
    if c != 1:
        print("BAD", e["para"], c, repr(e["old"]), len(p))
print("P6 head", repr(L.para("11a_中四上",6)[:30]))
print("P7 head", repr(L.para("11a_中四上",7)[:40]))
print("P7 tail", repr(L.para("11a_中四上",7)[-40:]))
