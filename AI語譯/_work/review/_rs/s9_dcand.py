# -*- coding: utf-8 -*-
"""D-focused: live quotes that themselves contain a repeated character (redundancy signature)."""
import io, os, re, json, collections

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

def has_rep(q):
    c = collections.Counter(q)
    return any(v >= 2 for k, v in c.items())

out = []
seen = set()
for r in R:
    if "D" not in r["cats"]: continue
    for q, where in r["chorus"]:
        if not (4 <= len(q) <= 40): continue
        if not has_rep(q): continue
        key = (r["chunk"], r["seg"], q)
        if key in seen: continue
        seen.add(key)
        # sentence
        ch = where[0]
        nt = RAW[ch]
        i = nt.find(q)
        a = max(nt.rfind("。", 0, i), nt.rfind("；", 0, i), nt.rfind("！", 0, i), nt.rfind("？", 0, i)) + 1
        bs = [nt.find(x, i) for x in "。；！？"]
        bs = [x for x in bs if x >= 0]
        b = min(bs) + 1 if bs else len(nt)
        out.append({"chunk": r["chunk"], "seg": r["seg"], "rid": r["rid"], "q": q,
                    "sent": nt[a:b][:220], "where": ch, "clm": r["text"][:300]})
json.dump(out, io.open(os.path.join(HERE, "Dcand.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("candidates", len(out), "distinct q", len({o['q'] for o in out}))
L = []
for o in sorted(out, key=lambda o: (o["where"], o["seg"])):
    L.append("%s#%d r%d Q=%s\n   S=%s" % (o["where"][:3], o["seg"], o["rid"], o["q"], o["sent"]))
io.open(os.path.join(HERE, "Dcand.txt"), "w", encoding="utf-8").write("\n".join(L))
print("chars", sum(len(x) for x in L))
