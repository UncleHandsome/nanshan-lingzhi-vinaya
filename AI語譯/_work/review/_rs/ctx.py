# -*- coding: utf-8 -*-
"""Show all occurrences (with paragraph + orig) of given words in 09b-21c."""
import io, os, re, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
MAP = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02", "_map.json"), encoding="utf-8"))["idx"]
ORIG = {}
for mid, v in MAP.items():
    if v.get("book") != "02_戒疏": continue
    ORIG.setdefault((v["chunk"], v["seg"]), []).append((mid, v["orig"]))

words = sys.argv[1].split(",")
out = []
for f in sorted(os.listdir(OUTD)):
    if not f.endswith(".txt"): continue
    ch = f[:-4]
    if ch[:3] < "09b": continue
    t = io.open(os.path.join(OUTD, f), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"): ps[-1] = ps[-1][:-2]
    for i, p in enumerate(ps):
        for w in words:
            if w in p:
                a = p.find(w)
                out.append("%s#%d [%s] ...%s..." % (ch[:3], i + 1, w, p[max(0, a - 30):a + len(w) + 30]))
                for mid, o in ORIG.get((ch, i + 1), [])[:1]:
                    out.append("   ORIG %s" % o[:200])
io.open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
print("lines", len(out))
