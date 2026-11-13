# -*- coding: utf-8 -*-
"""套用單一任意 _zb_*.json。"""
import io
import json
import sys

import _z6_lib as L

p = sys.argv[1]
d = json.load(io.open(p, encoding="utf-8"))
edits = d["edits"]
before = {}
for e in edits:
    before.setdefault(e["chunk"], L.snapshot(e["chunk"]))
cnt = 0
for c in before:
    cnt += L.apply_edits(c, [e for e in edits if e["chunk"] == c])
print("OK %s edits=%d segs=%d" % (p, cnt, len(set((e["chunk"], e["para"]) for e in edits))))
