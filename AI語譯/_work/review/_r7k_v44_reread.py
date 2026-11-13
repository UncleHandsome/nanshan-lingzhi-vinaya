# -*- coding: utf-8 -*-
"""Print current out text of edited segments for re-reading."""
import os, io, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


out = []
cache = {}
seen = set()
for ef in sys.argv[1:]:
    for chunk, items in json.loads(rd(ef)).items():
        if chunk not in cache:
            raw = rd(os.path.join(OUT, chunk + ".txt"))
            eol = "\r\n" if "\r\n" in raw else "\n"
            lines = raw.split(eol)
            idxs = [i for i, l in enumerate(lines) if l.strip()]
            cache[chunk] = (lines, idxs)
        lines, idxs = cache[chunk]
        for it in items:
            key = (chunk, it["idx"])
            if key in seen:
                continue
            seen.add(key)
            out.append("=== %s #%d\n%s" % (it["no"], it["idx"], lines[idxs[it["idx"] - 1]].strip()))
with io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_v44", "reread.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("segments: %d" % len(out))
