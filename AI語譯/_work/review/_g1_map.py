# -*- coding: utf-8 -*-
import io, os, re, json
base = "AI語譯"
rep = os.path.join(base, "_work", "review", "_g1_work.tsv")
rows = []
with io.open(rep, encoding="utf-8") as f:
    lines = [l.rstrip("\n") for l in f if l.strip()]
hdr = lines[0].split("\t")
for l in lines[1:]:
    f = l.split("\t")
    rows.append(dict(zip(hdr, f)))

cache = {}
def paras(chunk):
    if chunk in cache: return cache[chunk]
    p = os.path.join(base, "out", "03_業疏", chunk + ".txt")
    txt = io.open(p, encoding="utf-8").read()
    ps = [x.strip() for x in re.split(r"\r?\n\s*\r?\n", txt) if x.strip()]
    cache[chunk] = ps
    return ps

out = []
for i, r in enumerate(rows, 1):
    ps = paras(r["chunk"])
    seg = int(r["seg"])
    cur = r["current"]
    n = len(ps)
    match = [j+1 for j, p in enumerate(ps) if p == cur]
    out.append((i, r["chunk"], seg, n, match, len(cur)))
for t in out:
    print("row=%d %s seg=%d nparas=%d currentAt=%s len=%d" % t)
