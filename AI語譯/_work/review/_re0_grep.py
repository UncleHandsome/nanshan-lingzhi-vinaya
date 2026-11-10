import json, io, os
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8-sig"))
spec = json.load(io.open(os.path.join(OUT, "spec.json"), encoding="utf-8-sig"))
cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        cache[k] = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
    return cache[k]
lines = []
for gid, term in spec:
    e = next(x for x in ents if x["gid"] == gid)
    ps = paras(e["book"], e["chunk"])
    lines.append("### %s %s#%d term=%s" % (gid, e["chunk"], e["seg"], term))
    hits = 0
    for i, p in enumerate(ps):
        j = p.find(term)
        if j >= 0:
            hits += 1
            lines.append("  seg=%d ...%s..." % (i + 1, p[max(0, j - 80):j + len(term) + 80]))
    if not hits:
        lines.append("  NO HIT")
    lines.append("")
io.open(os.path.join(OUT, "grep.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("lines", len(lines))
