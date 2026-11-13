# -*- coding: utf-8 -*-
"""Apply edits: JSON [{chunk, idx, find, repl, note}] -> chunk file.
idx = non-empty-line ordinal (1-based), same as 校閱 ref.
Verifies: find appears exactly once in that line; preserves line endings.
Usage: python _s3_apply.py edits.json [--dry]
"""
import io, json, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")

def load(chunk):
    p = os.path.join(OUT, chunk + ".txt")
    b = open(p, "rb").read()
    return p, b.decode("utf-8")

def main():
    spec = json.load(io.open(sys.argv[1], encoding="utf-8"))
    dry = "--dry" in sys.argv
    bychunk = {}
    for e in spec:
        bychunk.setdefault(e["chunk"], []).append(e)
    for chunk, edits in bychunk.items():
        p, text = load(chunk)
        lines = text.split("\n")
        # non-empty line index map
        ne = [k for k, l in enumerate(lines) if l.strip()]
        for e in edits:
            pos = ne[e["idx"] - 1]
            line = lines[pos]
            n = line.count(e["find"])
            if n != 1:
                print("!! %s#%d find count=%d : %s" % (chunk, e["idx"], n, e["find"][:40]))
                continue
            new = line.replace(e["find"], e["repl"])
            lines[pos] = new
            print("OK %s#%d  %s" % (chunk, e["idx"], e.get("note", "")))
            if not dry:
                pass
        if not dry:
            with io.open(p, "w", encoding="utf-8", newline="") as f:
                f.write("\n".join(lines))
    if dry:
        print("(dry run, nothing written)")

if __name__ == "__main__":
    main()
