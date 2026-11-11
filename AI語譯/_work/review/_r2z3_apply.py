# -*- coding: utf-8 -*-
"""Apply r2z3 minimal substring edits to 資持記 out files.

Usage: python _r2z3_apply.py edits.json
JSON: [{"chunk": "01c_上一上", "seg": 28, "old": "...", "new": "...", "why": "..."}]
Each edit must match exactly once inside that segment (paragraph = non-empty line).
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")


def load(chunk):
    p = os.path.join(OUT, chunk + ".txt")
    raw = open(p, encoding="utf-8", newline="").read()
    return p, raw


def apply(edits):
    by_chunk = {}
    for e in edits:
        by_chunk.setdefault(e["chunk"], []).append(e)
    log = []
    for chunk, es in by_chunk.items():
        p, raw = load(chunk)
        trailing = raw.endswith("\n")
        lines = raw.split("\n")
        # map segment number -> index in lines (non-empty paragraph lines)
        idxs = [i for i, ln in enumerate(lines) if ln.strip()]
        for e in es:
            li = idxs[e["seg"] - 1]
            ln = lines[li]
            n = ln.count(e["old"])
            if n != 1:
                raise SystemExit(f"MATCH {n} != 1: {chunk}#{e['seg']} old={e['old'][:40]!r}")
            lines[li] = ln.replace(e["old"], e["new"], 1)
            log.append(dict(chunk=chunk, seg=e["seg"], why=e.get("why", ""),
                            old=e["old"], new=e["new"]))
        new_raw = "\n".join(lines)
        if trailing and not new_raw.endswith("\n"):
            new_raw += "\n"
        if new_raw == raw:
            raise SystemExit(f"no change: {chunk}")
        open(p, "w", encoding="utf-8", newline="").write(new_raw)
        print(f"wrote {chunk}: {len(es)} edits")
    return log


if __name__ == "__main__":
    ed = json.load(open(sys.argv[1], encoding="utf-8"))
    lg = apply(ed)
    lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r2z3_log.jsonl")
    with open(lp, "a", encoding="utf-8", newline="\n") as f:
        for r in lg:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("applied", len(lg))
