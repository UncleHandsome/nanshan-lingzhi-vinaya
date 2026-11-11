# -*- coding: utf-8 -*-
"""Review planned ops: locate q in corpus, show paragraph + source, check uniqueness."""
import io, os, re, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
MAP = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02", "_map.json"), encoding="utf-8"))["idx"]

ORIG = {}
for mid, v in MAP.items():
    if v.get("book") != "02_戒疏": continue
    ORIG.setdefault((v["chunk"], v["seg"]), []).append((mid, v["orig"]))

def load(ch):
    t = io.open(os.path.join(OUTD, ch + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return t, ps

FILES = {f[:-4]: f[:-4] for f in os.listdir(OUTD) if f.endswith(".txt")}
TOK = {}
for ch in FILES:
    TOK.setdefault(ch[:3], ch)

ops = json.load(io.open(sys.argv[1], encoding="utf-8"))
out = []
for i, op in enumerate(ops):
    q = op["q"]
    hits = []
    for ch in FILES:
        t, ps = load(ch)
        for j, p in enumerate(ps):
            if q in p:
                hits.append((ch, j + 1))
    out.append("[%02d] %s cat=%s new=%s" % (i, op.get("tag", ""), op["cat"], op["new"]))
    if len(hits) != 1:
        out.append("   !!! hits=%s" % hits)
    for ch, seg in hits:
        t, ps = load(ch)
        p = ps[seg - 1]
        a = p.find(q)
        out.append("   LOC %s#%d" % (ch[:3], seg))
        out.append("   CTX ...%s..." % p[max(0, a - 45):a + len(q) + 45])
        for mid, o in ORIG.get((ch, seg), [])[:2]:
            out.append("   ORIG[%s] %s" % (mid, o[:260]))
    out.append("")
io.open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
print("ops", len(ops), "multi/miss", sum(1 for l in out if l.strip().startswith("!!!")))
