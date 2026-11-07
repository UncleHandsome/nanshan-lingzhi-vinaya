# -*- coding: utf-8 -*-
import io, os, re, glob, json
base = "AI語譯"
rep = os.path.join(base, "_work", "review", "_g1_work.tsv")
lines = [l.rstrip("\n") for l in io.open(rep, encoding="utf-8") if l.strip()]
hdr = lines[0].split("\t")
rows = [dict(zip(hdr, l.split("\t"))) for l in lines[1:]]

# load all paragraphs of the book
chunks = ["00_卷首"] + sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(base,"out","03_業疏","*.txt")) if not os.path.basename(p).startswith("00"))
allp = []  # (chunk, idx, text)
for c in chunks:
    p = os.path.join(base, "out", "03_業疏", c + ".txt")
    if not os.path.exists(p): continue
    txt = io.open(p, encoding="utf-8").read()
    ps = [x.strip() for x in re.split(r"\r?\n\s*\r?\n", txt) if x.strip()]
    for i, t in enumerate(ps, 1):
        allp.append((c, i, t))

def norm(s):
    return re.sub(r"[\s\u3000]", "", s)

def quote_of(s):
    a = s.find("\u300c"); b = s.rfind("\u300d")
    if a != -1 and b != -1 and b > a:
        q = s[a+1:b]
        # keep only up to first ellipsis run for prefix match
        return q
    return None

report = []
for i, r in enumerate(rows, 1):
    s = r["suggestion"]; q = quote_of(s)
    pre = None
    if q:
        pre = norm(q)
        # cut at ellipsis
        for sep in ("\u2026\u2026", "\u2026"):
            k = pre.find(sep)
            if k > 0:
                pre = pre[:k]; break
        pre = pre[:20]
    hits = []
    if pre and len(pre) >= 6:
        for (c, idx, t) in allp:
            if norm(t).startswith(pre):
                hits.append((c, idx))
        if not hits:
            for (c, idx, t) in allp:
                if pre in norm(t):
                    hits.append((c, idx))
    report.append((i, r["chunk"], r["seg"], len(q) if q else -1, pre, hits[:3]))

for t in report:
    print("row=%d %-12s seg=%-3s qlen=%-4d hits=%s" % (t[0], t[1], t[2], t[3], t[5]))
