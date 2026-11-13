# -*- coding: utf-8 -*-
"""批次內修正：套用 _zg_fix_<nnnn>.json，不落 TSV（用於同一檔套用後的複讀修補）。"""
import io
import json
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))


def run(nums):
    for n in nums:
        p = os.path.join(HERE, "_zg_fix_%d.json" % n)
        d = json.load(io.open(p, encoding="utf-8"))
        edits = d["edits"]
        chunks = []
        for e in edits:
            if e["chunk"] not in chunks:
                chunks.append(e["chunk"])
        before = dict((c, L.snapshot(c)[1]) for c in chunks)
        for c in chunks:
            ce = [e for e in edits if e["chunk"] == c]
            L.apply_edits(c, ce)
        for c in chunks:
            if L.snapshot(c)[1] != before[c]:
                raise SystemExit("LINE COUNT CHANGED %s" % c)
        print("FIXED %d edits=%d" % (n, len(edits)))
        for c in chunks:
            for pa in sorted(set(e["para"] for e in edits if e["chunk"] == c)):
                print("--- %s#%d" % (c, pa))
                print(L.para(c, pa))


if __name__ == "__main__":
    run([int(x) for x in sys.argv[1:]])
