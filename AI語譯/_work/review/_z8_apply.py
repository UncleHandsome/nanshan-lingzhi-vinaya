# -*- coding: utf-8 -*-
"""7K 上四 c：套用 _z8_edits.json；驗 old 恰一次、段數行數不變、CRLF 不變。"""
import io
import json
import os
import sys

import _z8_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "_z8_edits.json")
LOG = os.path.join(HERE, "_z8_log.jsonl")


def run(nums, dry=False):
    d = json.load(io.open(DATA, encoding="utf-8"))
    total = dict(files=0, edits=0, segs=0, yi=0, run=0, veto=0, doubt=0)
    for n in nums:
        k = str(n)
        if k not in d:
            print("MISSING", n)
            continue
        rec = d[k]
        edits = rec["edits"]
        chunks = sorted(set(e["chunk"] for e in edits))
        before = {c: L.snapshot(c) for c in chunks}
        cnt = 0
        for c in chunks:
            ce = [e for e in edits if e["chunk"] == c]
            cnt += L.apply_edits(c, ce, dry=dry)
        after = {c: L.snapshot(c) for c in chunks}
        for c in chunks:
            bt, bl = before[c]
            at, al = after[c]
            if bl != al:
                raise SystemExit("LINES CHANGED %s %s %d->%d" % (n, c, bl, al))
        stats = dict(n=n, edits=len(edits),
                     segs=len(set((e["chunk"], e["para"]) for e in edits)),
                     yi=sum(1 for e in edits if e["kind"] == "義"),
                     run=sum(1 for e in edits if e["kind"] == "潤"),
                     veto=rec.get("veto", 0), doubt=rec.get("doubt", 0),
                     note=rec.get("note", ""))
        if not dry:
            with io.open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(stats, ensure_ascii=False) + "\n")
        total["files"] += 1
        for kk in ("edits", "segs", "yi", "run", "veto", "doubt"):
            total[kk] += stats[kk]
        print("OK %d edits=%d segs=%d yi=%d run=%d veto=%d doubt=%d" % (
            n, stats["edits"], stats["segs"], stats["yi"], stats["run"],
            stats["veto"], stats["doubt"]))
    print("TOTAL", total)


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry" in args
    run([int(x) for x in args if x != "--dry"], dry=dry)
