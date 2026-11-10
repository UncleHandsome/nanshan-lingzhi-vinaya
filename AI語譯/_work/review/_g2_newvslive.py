# -*- coding: utf-8 -*-
import json, re, io, os, difflib
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
groups = {}
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)
cache = {}
def para(book, chunk, seg):
    k = (book, chunk)
    if k not in cache:
        p = os.path.join("AI語譯", "out", book, chunk + ".txt")
        t = io.open(p, encoding="utf-8").read()
        cache[k] = [x.strip() for x in re.split(r"\r?\n\r?\n", t) if x.strip()]
    return cache[k][int(seg) - 1]

newmap = {}
for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    b, c, s, n = l.split("\t")
    newmap[(b, c, s)] = n

n = 0
for k, rs in groups.items():
    live = para(*k).replace("\n", "")
    cur = rs[0]["current"].replace("\n", "")
    if live == cur:
        continue
    if k not in newmap:
        print("NO OUTPUT for", k); continue
    new = newmap[k]
    if new == live:
        print("MATCH LIVE", k)
        continue
    n += 1
    print("=" * 100)
    print(k, "rows:", [d["_line"] for d in rs], "newlen", len(new), "livelen", len(live))
    sm = difflib.SequenceMatcher(None, live, new)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        print("  %s LIVE(%d): %r" % (tag, i2-i1, live[max(0,i1-20):i2+20]))
        print("      NEW(%d): %r" % (j2-j1, new[max(0,j1-20):j2+20]))
print("differing groups:", n)
