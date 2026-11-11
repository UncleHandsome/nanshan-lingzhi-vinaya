# -*- coding: utf-8 -*-
"""Locate text in a chunk's paragraphs: python _find.py 13a "needle" ["needle2" ...]

Prints occurrence count, paragraph number, and +/-90 char context.
"""
import io, os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
PER = json.load(io.open(os.path.join(HERE, "tmp_per.json"), encoding="utf-8"))


def fullname(tok):
    names = set()
    for k in PER:
        for v in PER[k].values():
            nm = v[0].split("/")[1]
            if nm.split("_")[0] == tok:
                names.add(nm)
    return names.pop() if len(names) == 1 else None


def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps


def main(tok, needles, ctx=90, full=False):
    chunk = fullname(tok) or tok
    ps = paras(chunk)
    L = []
    for nd in needles:
        hits = [(i + 1, p) for i, p in enumerate(ps) if nd in p]
        L.append("== [%s] hits=%d" % (nd, len(hits)))
        for s, p in hits:
            if full:
                L.append("#%d FULL: %s" % (s, p))
            else:
                i = p.find(nd)
                a = max(0, i - ctx); b = min(len(p), i + len(nd) + ctx)
                L.append("#%d ...%s..." % (s, p[a:b]))
        L.append("")
    out = "\n".join(L)
    io.open(os.path.join(HERE, "_find_out.txt"), "w", encoding="utf-8").write(out)
    print(len(out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:], full=("--full" in sys.argv))
