# -*- coding: utf-8 -*-
"""Compact actionable list: for each flagged claim, show matched quotes with their containing sentence."""
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
        RAW[f[:-4]] = io.open(os.path.join(OUTD, f), encoding="utf-8", newline="").read()

cat = sys.argv[1]
sub = [r for r in R if cat in r["cats"] and r["chorus"]]
out = []
for r in sorted(sub, key=lambda r: (r["chunk"], r["seg"])):
    lines = []
    for q, where in r["chorus"]:
        for ch in where:
            t = RAW[ch].replace("\r\n", "\n")
            for m in re.finditer(re.escape(q), norm(t)):
                pass
            idx = norm(t).find(q)
            if idx < 0: continue
            # locate sentence boundaries in normalized text
            nt = norm(t)
            a = max(nt.rfind("。", 0, idx), nt.rfind("；", 0, idx), nt.rfind("！", 0, idx), nt.rfind("？", 0, idx)) + 1
            b0 = [nt.find(x, idx) for x in "。；！？"]
            b0 = [x for x in b0 if x >= 0]
            b = min(b0) + 1 if b0 else len(nt)
            lines.append("  Q[%s]: %s" % (ch[:3], nt[a:b][:200]))
    if not lines: continue
    out.append("=== %s #%d r%d cats=%s" % (r["chunk"][:3], r["seg"], r["rid"], r["cats"]))
    out.append("  CLM: " + r["text"][:420])
    out.extend(dict.fromkeys(lines))
io.open(os.path.join(HERE, "act_%s.txt" % cat), "w", encoding="utf-8").write("\n".join(out))
print(cat, "claims", len(sub), "chars", sum(len(x) for x in out))
