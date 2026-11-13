# -*- coding: utf-8 -*-
"""Parse 校閱_7K/校閱_067..096.txt into segments; compare with current chunk lines."""
import re, json, io, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")

def read(p):
    with io.open(p, encoding="utf-8-sig") as f:
        return f.read()

def chunk_lines(name):
    t = read(os.path.join(OUT, name + ".txt"))
    return t.split("\n")

rows = []
for n in range(67, 97):
    p = os.path.join(ROOT, "校閱_7K", "校閱_%03d.txt" % n)
    txt = read(p)
    # segments
    for m in re.finditer(r"【(\d{3})-(\d{4})】([^\n]*)\n【原文】([^\n]*)\n【譯文】([^\n]*)", txt):
        rows.append(dict(doc=int(m.group(1)), seg=int(m.group(2)), ref=m.group(3).strip(),
                         src=m.group(4), tr=m.group(5)))

print("total segments parsed:", len(rows))
byfile = {}
for r in rows:
    byfile.setdefault(r["doc"], []).append(r)
for d in sorted(byfile):
    segs = byfile[d]
    print(d, len(segs), segs[0]["ref"], "->", segs[-1]["ref"])

# map ref -> chunk, idx
segmap = {}
for r in rows:
    m = re.match(r"(01_行事鈔)/(\S+?)#(\d+)$", r["ref"])
    if not m:
        print("BAD REF", r["ref"]); continue
    r["chunk"] = m.group(2); r["idx"] = int(m.group(3))
    segmap[(r["chunk"], r["idx"])] = r

# compare to current
cache = {}
for (_c, _i), r in sorted(segmap.items()):
    c = r["chunk"]
    if c not in cache:
        cache[c] = chunk_lines(c)
    ls = cache[c]
    # idx = non-empty line ordinal (1-based)
    ne = [(k, l) for k, l in enumerate(ls) if l.strip()]
    if _i > len(ne):
        print("OUT OF RANGE", c, _i); continue
    r["cur"] = ne[_i - 1][1]
    r["curline"] = ne[_i - 1][0]
    r["same"] = (r["cur"].strip() == r["tr"].strip())

print("\nchunk/index coverage:")
cov = sorted(set((r["chunk"], r["idx"]) for r in rows))
print(len(cov), "unique segs")
for c in sorted(set(x[0] for x in cov)):
    idxs = sorted(i for cc, i in cov if cc == c)
    print(c, "n=%d" % len(idxs), "min=%d max=%d" % (min(idxs), max(idxs)),
          "missing=%s" % (sorted(set(range(min(idxs), max(idxs) + 1)) - set(idxs)))[:200])

print("\nsame (material == current): %d ; differ: %d" % (sum(1 for r in segmap.values() if r["same"]), sum(1 for r in segmap.values() if not r["same"])))
with io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_s3_rows.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
