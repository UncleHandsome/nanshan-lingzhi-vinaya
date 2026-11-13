# -*- coding: utf-8 -*-
"""Tally edits per file label -> stats table."""
import json, os, importlib, sys
D = os.path.dirname(__file__)
sys.path.insert(0, D)
mods = ["_v4_edits"] + ["_v4_edits%d" % i for i in range(2, 14)]
EDITS = []
for m in mods:
    try:
        mod = importlib.import_module(m)
    except ImportError:
        continue
    EDITS += mod.EDITS
data = json.load(open(os.path.join(D, "_v4_data.json"), encoding="utf-8"))
segcount = {r["file"]: len(r["segs"]) for r in data}
changed = {r["file"]: set() for r in data}
for s in sum([r["segs"] for r in data], []):
    if not s["same"]:
        changed[int(s["label"][:3])].add(s["label"])
edits_by_file = {}
for e in EDITS:
    f = int(e["label"][:3])
    edits_by_file[f] = edits_by_file.get(f, 0) + 1
rows = []
for f in range(257, 293):
    rows.append((f, segcount[f], len(changed[f]), edits_by_file.get(f, 0)))
open(os.path.join(D, "_v4_stats.tsv"), "w", encoding="utf-8").write(
    "file\tsegs\tchg_segs\tedits\n" + "\n".join("%d\t%d\t%d\t%d" % r for r in rows))
print("total segs", sum(r[1] for r in rows), "chg segs", sum(r[2] for r in rows),
      "edits", sum(r[3] for r in rows), "files", len(rows))
