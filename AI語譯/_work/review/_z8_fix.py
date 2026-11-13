# -*- coding: utf-8 -*-
"""套用 _z8_fix.json（回讀後的小修）。"""
import io
import json
import os
import sys

import _z8_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "_z8_fix.json")
LOG = os.path.join(HERE, "_z8_log.jsonl")


def run(nums):
    d = json.load(io.open(DATA, encoding="utf-8"))
    for n in nums:
        rec = d[str(n)]
        edits = rec["edits"]
        chunks = sorted(set(e["chunk"] for e in edits))
        before = {c: L.snapshot(c) for c in chunks}
        for c in chunks:
            ce = [e for e in edits if e["chunk"] == c]
            L.apply_edits(c, ce)
        for c in chunks:
            if L.snapshot(c)[1] != before[c][1]:
                raise SystemExit("LINES CHANGED %s %s" % (n, c))
        stats = dict(n=n, fix=len(edits),
                     segs=len(set((e["chunk"], e["para"]) for e in edits)),
                     yi=sum(1 for e in edits if e["kind"] == "義"),
                     run=sum(1 for e in edits if e["kind"] == "潤"))
        with io.open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(stats, ensure_ascii=False) + "\n")
        print("FIX", n, stats)


if __name__ == "__main__":
    run([int(x) for x in sys.argv[1:]])
