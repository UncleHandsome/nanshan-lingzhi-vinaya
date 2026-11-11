# -*- coding: utf-8 -*-
"""Detect adjacent near-synonym / duplicated compounds in current paragraphs."""
import io, os, re, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

CJK = r"[\u4e00-\u9fff]"
PATS = [
    ("ABAC", re.compile(r"(%s)(%s)\1(%s)" % (CJK, CJK, CJK))),          # 隔絕隔離 (1st==3rd)
    ("ABCB", re.compile(r"(%s)(%s)(%s)\2" % (CJK, CJK, CJK))),          # 超越踰越 (2nd==4th)
    ("XYXY", re.compile(r"(%s%s)\1" % (CJK, CJK))),                     # 重複重複
]
rows = []
chunks = sorted(f[:-4] for f in os.listdir(OUTD) if f.endswith(".txt"))
for ch in chunks:
    ps = paras(ch)
    for i, p in enumerate(ps):
        if p.startswith("【條目文】"): continue
        for name, pat in PATS:
            for m in pat.finditer(p):
                frag = m.group(0)
                a = max(0, m.start() - 12); b = min(len(p), m.end() + 12)
                rows.append({"chunk": ch, "seg": i + 1, "kind": name, "frag": frag, "ctx": p[a:b]})
json.dump(rows, io.open(os.path.join(HERE, "dup.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("hits", len(rows))
for r in rows:
    print("%s#%d %s %s | %s" % (r["chunk"][:3], r["seg"], r["kind"], r["frag"], r["ctx"]))
