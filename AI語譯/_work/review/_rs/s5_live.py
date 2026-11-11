# -*- coding: utf-8 -*-
"""Corpus-wide liveness with markdown/space normalization."""
import io, os, re, json, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")

def norm(s):
    s = re.sub(r"[*_`~>#]", "", s)
    s = re.sub(r"\s+", "", s)
    return s

chunks = sorted(f[:-4] for f in os.listdir(OUTD) if f.endswith(".txt"))
TXT = {}
for ch in chunks:
    TXT[ch] = norm(io.open(os.path.join(OUTD, ch + ".txt"), encoding="utf-8", newline="").read())

R = json.load(io.open(os.path.join(HERE, "screen.json"), encoding="utf-8"))
for r in R:
    t = norm(r["text"])
    qs = [norm(q) for q in re.findall(r"[「『]([^」』\n]{4,90})[」』]", r["text"])]
    qs = [q for q in qs if len(q) >= 4]
    hits = []
    for q in qs:
        where = [ch for ch in TXT if q in TXT[ch]]
        if where:
            hits.append([q, where])
    r["chorus"] = hits

json.dump(R, io.open(os.path.join(HERE, "screen2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("total", len(R), "corpus-live", sum(1 for r in R if r["chorus"]))
for cat in "ABCD":
    sub = [r for r in R if cat in r["cats"]]
    print(cat, len(sub), "corpus-live", sum(1 for r in sub if r["chorus"]))
