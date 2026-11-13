# -*- coding: utf-8 -*-
"""7K 中四上 a：套用 _z7_e<nnnn>.json；驗 old 恰一次、段數行數不變。"""
import io
import json
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "_z7_log.jsonl")


def run(nums, dry=False):
    total = {"files": 0, "segs": 0, "yi": 0, "run": 0, "veto": 0, "doubt": 0}
    for n in nums:
        p = os.path.join(HERE, "_z7_e%d.json" % n)
        if not os.path.exists(p):
            print("MISSING", n)
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        edits = d["edits"]
        before = {}
        for c in sorted(set(e["chunk"] for e in edits)):
            before[c] = L.snapshot(c)
        cnt = 0
        for c in before:
            ce = [e for e in edits if e["chunk"] == c]
            cnt += L.apply_edits(c, ce, dry=dry)
        after = {c: L.snapshot(c) for c in before}
        for c in before:
            bt, bl = before[c]
            at, al = after[c]
            if bl != al or len(bt.split(L.sep(bt))) != len(at.split(L.sep(at))):
                raise SystemExit("SHAPE CHANGED %s %s lines %d->%d" % (n, c, bl, al))
        stats = {"n": n, "edits": len(edits),
                 "segs": len(set((e["chunk"], e["para"]) for e in edits)),
                 "yi": sum(1 for e in edits if e["kind"] == "義"),
                 "run": sum(1 for e in edits if e["kind"] == "潤"),
                 "veto": d.get("veto", 0), "doubt": d.get("doubt", 0),
                 "note": d.get("note", "")}
        if not dry:
            with io.open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(stats, ensure_ascii=False) + "\n")
        total["files"] += 1
        total["segs"] += stats["segs"]
        total["yi"] += stats["yi"]
        total["run"] += stats["run"]
        total["veto"] += stats["veto"]
        total["doubt"] += stats["doubt"]
        print("OK %d edits=%d segs=%d yi=%d run=%d veto=%d doubt=%d" % (
            n, stats["edits"], stats["segs"], stats["yi"], stats["run"],
            stats["veto"], stats["doubt"]))
    print("TOTAL", total)


if __name__ == "__main__":
    run([int(x) for x in sys.argv[1:]])
