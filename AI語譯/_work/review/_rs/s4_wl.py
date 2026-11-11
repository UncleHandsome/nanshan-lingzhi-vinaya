# -*- coding: utf-8 -*-
"""Build per-category worklists: dedupe by (chunk,seg), include all claim texts + current paragraph."""
import io, os, re, json, collections, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
R = json.load(io.open(os.path.join(HERE, "screen.json"), encoding="utf-8"))

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

PC = {}
def gp(chunk):
    if chunk not in PC: PC[chunk] = paras(chunk)
    return PC[chunk]

cat = sys.argv[1]
minlive = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rows = [r for r in R if cat in r["cats"] and r["live"] >= minlive]
by = collections.OrderedDict()
for r in sorted(rows, key=lambda r: (r["chunk"], r["seg"], r["rid"])):
    by.setdefault((r["chunk"], r["seg"]), []).append(r)

out = []
for (ch, seg), rs in by.items():
    ps = gp(ch)
    cur = ps[seg-1] if 0 < seg <= len(ps) else "(NA)"
    out.append("=== %s #%d  (r%s)" % (ch[:3], seg, ",".join(str(x["rid"]) for x in rs)))
    out.append("CUR: " + cur)
    seen = set()
    for x in rs:
        t = x["text"]
        if t in seen: continue
        seen.add(t)
        out.append("CLM: " + t[:900])
io.open(os.path.join(HERE, "wl_%s.txt" % cat), "w", encoding="utf-8").write("\n".join(out))
print(cat, "claims", len(rows), "segs", len(by), "chars", sum(len(x) for x in out))
