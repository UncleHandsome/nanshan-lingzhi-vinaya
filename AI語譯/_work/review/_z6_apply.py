# -*- coding: utf-8 -*-
"""套用 _z6_e<nnnn>.json 的替換清單；驗 old 恰一次、段數不變，並回報統計。"""
import io
import json
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "_z6_log.jsonl")


def run(nums, dry=False):
    total = {"files": 0, "segs": 0, "yi": 0, "run": 0}
    for n in nums:
        p = os.path.join(HERE, "_z6_e%d.json" % n)
        if not os.path.exists(p):
            print("MISSING", n)
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        edits = d["edits"]
        before = {}
        for e in edits:
            c = e["chunk"]
            if c not in before:
                before[c] = L.snapshot(c)
        cnt = 0
        for c in before:
            ce = [e for e in edits if e["chunk"] == c]
            cnt += L.apply_edits(c, ce, dry=dry)
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
        print("OK %d edits=%d segs=%d yi=%d run=%d veto=%d doubt=%d" % (
            n, stats["edits"], stats["segs"], stats["yi"], stats["run"],
            stats["veto"], stats["doubt"]))
    print("TOTAL", total)


def check(nums):
    for n in nums:
        p = os.path.join(HERE, "_z6_e%d.json" % n)
        d = json.load(io.open(p, encoding="utf-8"))
        for c in sorted(set(e["chunk"] for e in d["edits"])):
            t, s = L.paras(c)
            ps = t.split(s)
            print(n, c, "paras", len(ps), "lines", t.count("\n"))


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check([int(x) for x in sys.argv[2:]])
    else:
        run([int(x) for x in sys.argv[1:]])
