import io, json

rows = json.load(open(r"AI語譯/_work/review/_g1_rows.json", encoding="utf-8"))
cache = {}
def paras(book, chunk):
    key = (book, chunk)
    if key not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        lines = io.open(p, encoding="utf-8").read().split("\n")
        cache[key] = [(j, l) for j, l in enumerate(lines) if l.strip()]
    return cache[key]

out = []
for i, r in enumerate(rows):
    ps = paras(r["book"], r["chunk"])
    probe = r["current"].replace("\n", "")[:24]
    hits = [k for k, (j, l) in enumerate(ps) if probe and probe in l.replace("\n", "")]
    seg = int(r["seg"])
    out.append("ROW %2d seg=%3d pagehits=%s  %s" % (i, seg, hits[:3], r["current"][:20].replace("\n", "⏎")))
open(r"AI語譯/_work/review/_g1_segmap.txt", "w", encoding="utf-8").write("\n".join(out))
