# -*- coding: utf-8 -*-
"""Dump per-file applied edits (label + new text, truncated) for report writing."""
import os, sys, importlib, json
D = os.path.dirname(__file__)
sys.path.insert(0, D)
mods = ["_v4_edits"] + ["_v4_edits%d" % i for i in range(2, 14)]
EDITS = []
for m in mods:
    try:
        EDITS += importlib.import_module(m).EDITS
    except ImportError:
        pass
byfile = {}
for e in EDITS:
    byfile.setdefault(int(e["label"][:3]), []).append(e)
buf = []
for f in sorted(byfile):
    buf.append("=== %d (%d 處) ===" % (f, len(byfile[f])))
    for e in byfile[f]:
        buf.append("  %s | %s" % (e["label"], e["new"][:70]))
open(os.path.join(D, "_v4_changes.txt"), "w", encoding="utf-8").write("\n".join(buf))
print(len(EDITS))
