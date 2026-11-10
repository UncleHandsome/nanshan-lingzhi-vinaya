# -*- coding: utf-8 -*-
import json, io, os, sys
OUT = r"AI語譯/_work/review/_re0"
FIX = r"AI語譯/_work/review/fix_re0.tsv"
MIS = r"AI語譯/_work/review/re0_錯位.tsv"

cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        assert os.path.exists(p), p
        cache[k] = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
    return cache[k]

lines = io.open(FIX, encoding="utf-8").read().rstrip("\n").split("\n")
print("fix lines:", len(lines))
seen = set()
base_map = {}
for i, ln in enumerate(lines):
    parts = ln.split("\t")
    assert len(parts) == 4, (i, len(parts), ln[:60])
    book, chunk, seg, new = parts[0], parts[1], int(parts[2]), parts[3]
    assert (book, chunk, seg) not in seen, (book, chunk, seg)
    seen.add((book, chunk, seg))
    ps = paras(book, chunk)
    assert 1 <= seg <= len(ps), (book, chunk, seg, len(ps))
    assert new != ps[seg - 1], ("no change", book, chunk, seg)
    assert len(new) > 20
print("all rows valid; unique segments:", len(seen))
print("books:", {b: sum(1 for x in seen if x[0] == b) for b in {x[0] for x in seen}})

ml = io.open(MIS, encoding="utf-8").read().rstrip("\n").split("\n")
print("mis lines:", len(ml))
for ln in ml:
    parts = ln.split("\t")
    assert len(parts) == 6, (len(parts), ln[:50])
print("mis fields ok")

# check applied gids are all covered / no unhandled
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
skips = json.load(io.open(os.path.join(OUT, "skips.json"), encoding="utf-8"))
mis = json.load(io.open(os.path.join(OUT, "mis.json"), encoding="utf-8"))
applied = json.load(io.open(os.path.join(OUT, "applied.json"), encoding="utf-8"))
print("entries:", len(ents), "applied:", len(applied), "skips:", len(skips), "mis:", len(mis),
      "sum:", len(applied) + len(skips) + len(mis))
assert len(applied) + len(skips) + len(mis) == len(ents)
print("OK")
