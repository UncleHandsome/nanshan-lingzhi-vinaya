# -*- coding: utf-8 -*-
"""Show current paragraph(s) and source orig for given (chunk, seg) pairs."""
import io, os, re, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
MAP = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02", "_map.json"), encoding="utf-8"))["idx"]

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

ORIG = {}
for mid, v in MAP.items():
    if v.get("book") != "02_戒疏": continue
    ORIG.setdefault((v["chunk"][:3], v["seg"]), []).append((mid, v["orig"]))

for arg in sys.argv[1:]:
    ch, seg = arg.split("#")
    seg = int(seg)
    ps = paras([f[:-4] for f in os.listdir(OUTD) if f.startswith(ch + "_")][0])
    print("=== %s#%d" % (ch, seg))
    print("NOW : " + ps[seg - 1])
    for mid, o in ORIG.get((ch, seg), []):
        print("ORIG[%s]: %s" % (mid, o))
    print()
