# -*- coding: utf-8 -*-
"""Build per-file views for 卷下之一: resp opinions + segments (src/tr)."""
import os, re, json, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view3")

segs_all = json.load(io.open(os.path.join(ROOT, r"AI語譯\_work\review\_r7k_z3_segs.json"), encoding="utf-8"))


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def make(n):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % n)
    buf.append("=" * 30 + " 意見 resp_%s " % n + "=" * 30)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = [s for s in segs_all if s["file"] == n]
    buf.append("=" * 30 + " 段落 %s（%d 段）" % (n, len(segs)) + "=" * 30)
    for s in segs:
        buf.append("\n--- %s-%s  %s#%d  %s" % (n, s["seg"], s["chunk"], s["idx"], "現行=材料" if s["same"] else "※已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[譯文] " + s["tr"])
    out = os.path.join(VIEW, "view_%s.txt" % n)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    return out


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(make(n))
