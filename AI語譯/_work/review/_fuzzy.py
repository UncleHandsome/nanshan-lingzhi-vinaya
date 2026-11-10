# -*- coding: utf-8 -*-
import csv, re, sys, difflib
from collections import Counter
P = r"AI語譯/_work/review/report_re9.tsv"
rows = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows[i] = d

def fuzzy(cur, needle, k=6):
    if not needle: return None
    if needle in cur:
        i = cur.find(needle)
        return (1.0, i, cur[max(0,i-30):i+len(needle)+30])
    idx = {}
    starts = []
    for off in range(0, len(needle)-k+1):
        gram = needle[off:off+k]
        st = 0
        while True:
            p = cur.find(gram, st)
            if p == -1: break
            cand = p - off
            if cand >= 0:
                idx[cand] = idx.get(cand, 0) + 1
                starts.append(cand)
            st = p + 1
    if not idx: return (0.0, -1, "")
    best = max(idx.items(), key=lambda kv: kv[1])
    cand = best[0]
    # refine by local search +-5
    bsum, bpos = -1, cand
    for c in range(max(0,cand-6), cand+7):
        w = cur[c:c+len(needle)]
        r = difflib.SequenceMatcher(None, needle, w).ratio()
        if r > bsum:
            bsum, bpos = r, c
    return (bsum, bpos, cur[max(0,bpos-40):bpos+len(needle)+40])

def candidate_needles(d):
    out = []
    # quotes from problem first (they describe erroneous renderings)
    for q in re.findall(r"「([^」]{6,})」", d["problem"]):
        out.append(("prob", q))
    for q in re.findall(r"「([^」]{6,})」", d["suggestion"]):
        out.append(("sug", q))
    return out

TARGETS = [int(x) for x in sys.argv[1].split(",")]
for ln in TARGETS:
    d = rows[ln]
    cur = d["current"].replace("\n", "")
    print("="*110)
    print(f"### line={ln} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}")
    print("PROB:", d["problem"][:500])
    print("SUG :", d["suggestion"][:500])
    seen = set()
    cands = candidate_needles(d)
    # pick up to 3 longest quotes
    cands.sort(key=lambda x: -len(x[1]))
    for tag, q in cands[:3]:
        if q in seen: continue
        seen.add(q)
        r = fuzzy(cur, q)
        if r is None: continue
        ratio, pos, win = r
        print(f"  [{tag}] score={ratio:.3f} q={q[:60]}")
        print(f"      CUR: {win}")
