# -*- coding: utf-8 -*-
"""Locate each entry's target across all paragraphs of its chunk."""
import re, io, json, os
from collections import Counter, defaultdict

OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
Q = re.compile(r"「([^「」]*)」")

cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        cache[k] = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
    return cache[k]

rows = []
for e in ents:
    ps = paras(e["book"], e["chunk"])
    cur = e["current"] or ""
    probes = []
    for p in e["pairs"]:
        if p[1]:
            probes.append(("old:" + p[0], p[1]))
    for q in Q.findall(e["problem"] or ""):
        if len(q) >= 5 and q not in [x[1] for x in probes]:
            probes.append(("probq", q))
    # dedupe preserving order, longest first for matching
    seen = set(); pr = []
    for kind, s in probes:
        if s in seen: continue
        seen.add(s); pr.append((kind, s))
    pr.sort(key=lambda x: -len(x[1]))
    info = []
    for kind, s in pr:
        if s in cur:
            where = "SELF"
        else:
            hits = [i + 1 for i, para in enumerate(ps) if s in para]
            where = ("ELSE:" + ",".join(map(str, hits))) if hits else "NONE"
        info.append((kind, s[:30], where, len(s)))
    rows.append({"gid": e["gid"], "book": e["book"], "chunk": e["chunk"], "seg": e["seg"],
                 "type": e["type"], "cls": None, "info": info,
                 "problem": e["problem"], "suggestion": e["suggestion"], "current": cur})

json.dump(rows, io.open(os.path.join(OUT, "locate.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# compact text
lines = []
for r in sorted(rows, key=lambda x: (x["book"], x["chunk"], x["seg"], x["gid"])):
    lines.append("### %s seg=%d %s" % (r["gid"], r["seg"], r["type"]))
    for kind, s, where, ln in r["info"]:
        lines.append("   %-10s %-3s %s" % (where, ln, s))
    lines.append("")
io.open(os.path.join(OUT, "locate.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("written")
