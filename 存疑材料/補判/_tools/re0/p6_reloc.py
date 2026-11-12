# -*- coding: utf-8 -*-
"""Relocate items whose 疑點 quotes do not appear in resolved 現行譯文."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
OUTJ = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def nz(s):
    return re.sub(r"[，。、：；！？「」『』（）〔〕〈〉《》…·\s]", "", s)

rows = json.load(open(os.path.join(TOOLS, "resolved4.json"), encoding="utf-8"))

cache = {}
def paras(book):
    if book in cache: return cache[book]
    d = os.path.join(OUTJ, book); res = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"): continue
        ps = [l for l in rd(os.path.join(d, fn)).split("\n") if l.strip()]
        for i, l in enumerate(ps):
            res.append((fn.split("_")[0], i + 1, l))
    cache[book] = res
    return res

def quotes(r):
    qs = re.findall(r"「([^」]{2,})」", r["su_note"])
    out = []
    for q in qs:
        if q.startswith("按"): continue
        out.append(q)
    return out

changed = []
for r in rows:
    if not (r["src"].strip() and r["cur"].strip()): continue
    qs = quotes(r)
    if not qs: continue
    if any(nz(q) in nz(r["src"]) or nz(q) in nz(r["cur"]) for q in qs):
        continue
    # relocate: find paragraph containing the longest quote
    best = None
    for q in sorted(qs, key=len, reverse=True):
        qq = nz(q)
        if len(qq) < 3: continue
        hits = [(ch, seg, l) for ch, seg, l in paras(r["book"]) if qq in nz(l)]
        if len(hits) == 1:
            best = hits[0] + (q,)
            break
    if best:
        r["chunk"], r["seg"], r["cur"] = best[0], best[1], best[2]
        r["relocated"] = True
        r["reloc_q"] = best[3]
        changed.append((r["key"], best[0], best[1], best[3]))
    else:
        r["relocated"] = False

json.dump(rows, open(os.path.join(TOOLS, "resolved5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("relocated", len(changed))
for c in changed[:40]:
    print(c[0], "->", c[1], c[2], "|", c[3][:30])
