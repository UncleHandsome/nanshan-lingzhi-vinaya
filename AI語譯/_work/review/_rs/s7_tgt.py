# -*- coding: utf-8 -*-
"""Clause-level targeting: keep only the claim clause that states the defect, plus the matching sentence."""
import io, os, re, json, collections, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")

def norm(s):
    s = re.sub(r"[*_`~>#]", "", s)
    return re.sub(r"\s+", "", s)

R = json.load(io.open(os.path.join(HERE, "screen2.json"), encoding="utf-8"))
RAW = {}
for f in os.listdir(OUTD):
    if f.endswith(".txt"):
        RAW[f[:-4]] = norm(io.open(os.path.join(OUTD, f), encoding="utf-8", newline="").read())

TRIG = {
 "A": r"讀不通|不成話|不成句|語法|主詞|主語|懸空|接不上|拗口|不順|語病|句子",
 "B": r"生造|不成詞|不詞|非詞|無此詞|自造|怪詞|硬湊",
 "C": r"現代|今義|現代漢語|專義|法律用語|行政|術語化|世俗法|刑法|司法",
 "D": r"重複|贅|疊字|疊用|疊義|同義|重出|累贅|衍字|冗",
}

cat = sys.argv[1]
trig = re.compile(TRIG[cat])
sub = [r for r in R if cat in r["cats"]]
rows = []
for r in sub:
    t = r["text"]
    # split claim into clauses
    parts = re.split(r"(?<=[。；;])|(?=\s-\s)|(?=｜)|(?=\|\s*\d{3,4}\s*\|)", t)
    hits = []
    for p in parts:
        if not trig.search(p): continue
        qs = [norm(q) for q in re.findall(r"[「『]([^」』\n]{2,60})[」』]", p)]
        qs = [q for q in qs if len(q) >= 2]
        live = [q for q in qs if any(q in TXT for TXT in RAW.values())]
        if live:
            hits.append((re.sub(r"\s+", " ", p).strip()[:260], live))
    if not hits: continue
    rows.append((r, hits))

out = []
for r, hits in sorted(rows, key=lambda x: (x[0]["chunk"], x[0]["seg"])):
    out.append("=== %s #%d r%d" % (r["chunk"][:3], r["seg"], r["rid"]))
    seenq = set()
    for clause, live in hits:
        out.append("  C: " + clause)
        for q in live:
            if q in seenq: continue
            seenq.add(q)
            for ch, nt in RAW.items():
                i = nt.find(q)
                if i < 0: continue
                a = max(nt.rfind("。", 0, i), nt.rfind("；", 0, i), nt.rfind("！", 0, i), nt.rfind("？", 0, i)) + 1
                bs = [nt.find(x, i) for x in "。；！？"]
                bs = [x for x in bs if x >= 0]
                b = min(bs) + 1 if bs else len(nt)
                out.append("    [%s] %s" % (ch[:3], nt[a:b][:190]))
io.open(os.path.join(HERE, "tgt_%s.txt" % cat), "w", encoding="utf-8").write("\n".join(out))
print(cat, "segs", len(rows), "lines", len(out), "chars", sum(len(x) for x in out))
