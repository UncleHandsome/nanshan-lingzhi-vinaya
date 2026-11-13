# -*- coding: utf-8 -*-
"""7K 資持記 中三下 補缺（1756-1768, 1781-1785）：套用 _zg_e<nnnn>.json；
驗 old 恰一次、段數/行數不變；落 `batch_qwen/r7k_done/資持記_中三下_缺.tsv`。"""
import io
import json
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = L.ROOT
LOG = os.path.join(HERE, "_zg_log.jsonl")
ROWS = os.path.join(ROOT, "batch_qwen", "r7k_done", u"資持記_中三下_缺.tsv")
HEADER = u"檔號\t卷\t改段數\t義理修正\t潤飾\t否決\t存疑\t備註\n"


def done_nums():
    if not os.path.exists(ROWS):
        return set()
    s = io.open(ROWS, encoding="utf-8").read().split("\n")
    out = set()
    for ln in s[1:]:
        if ln.strip():
            out.add(int(ln.split("\t")[0]))
    return out


def run(nums, dry=False):
    total = {"files": 0, "segs": 0, "yi": 0, "run": 0}
    for n in nums:
        p = os.path.join(HERE, "_zg_e%d.json" % n)
        if not os.path.exists(p):
            print("MISSING", n)
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        edits = d["edits"]
        chunks = []
        for e in edits:
            if e["chunk"] not in chunks:
                chunks.append(e["chunk"])
        before = {}
        for c in chunks:
            before[c] = L.snapshot(c)
        cnt = 0
        for c in chunks:
            ce = [e for e in edits if e["chunk"] == c]
            cnt += L.apply_edits(c, ce, dry=dry)
        stats = {"n": n, "edits": len(edits),
                 "segs": len(set((e["chunk"], e["para"]) for e in edits)),
                 "yi": sum(1 for e in edits if e["kind"] == "義"),
                 "run": sum(1 for e in edits if e["kind"] == "潤"),
                 "veto": d.get("veto", 0), "doubt": d.get("doubt", 0),
                 "note": d.get("note", "")}
        if not dry:
            after = dict((c, L.snapshot(c)) for c in chunks)
            bad = [c for c in chunks
                   if before[c][0].count("\n") != after[c][0].count("\n")
                   or before[c][0].count("\n\n") != after[c][0].count("\n\n")]
            if bad:
                raise SystemExit("LINE/PARA COUNT CHANGED %s" % bad)
            if n in done_nums():
                raise SystemExit("ALREADY REGISTERED %d" % n)
            with io.open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(stats, ensure_ascii=False) + "\n")
            row = u"%d\t中三下\t%d\t%d\t%d\t%d\t%d\t%s\n" % (
                n, stats["segs"], stats["yi"], stats["run"],
                stats["veto"], stats["doubt"], stats["note"])
            if not os.path.exists(ROWS):
                with io.open(ROWS, "w", encoding="utf-8", newline="") as f:
                    f.write(HEADER)
            with io.open(ROWS, "a", encoding="utf-8", newline="") as f:
                f.write(row)
        total["files"] += 1
        total["segs"] += stats["segs"]
        total["yi"] += stats["yi"]
        total["run"] += stats["run"]
        print("OK %d edits=%d segs=%d yi=%d run=%d veto=%d doubt=%d" % (
            n, stats["edits"], stats["segs"], stats["yi"], stats["run"],
            stats["veto"], stats["doubt"]))
        if not dry:
            sys.stdout.flush()
            for c in chunks:
                for pa in sorted(set(e["para"] for e in edits if e["chunk"] == c)):
                    print("--- %s#%d" % (c, pa))
                    print(L.para(c, pa))
    print("TOTAL", total)


if __name__ == "__main__":
    if sys.argv[1] == "dry":
        run([int(x) for x in sys.argv[2:]], dry=True)
    else:
        run([int(x) for x in sys.argv[1:]])
