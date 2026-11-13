# -*- coding: utf-8 -*-
"""Apply edits to 05_拾毗尼義鈔 out chunks by non-empty line number.
edits JSON: {"<chunkpath>": {"<k>": [["find","new"], ...]}}  (k = 1-based non-empty line)
Backup: 歸檔/7K卷修正前/<book>/<name>_v.txt (once).
"""
import os, sys, io, json, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def show(chunkpath, ks):
    book, name = chunkpath.split("/", 1)
    raw = rd(os.path.join(OUT, book, name + ".txt"))
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    for k in ks:
        print("[%d] %s" % (k, lines[idxs[k - 1]]))
        print()


def apply(chunkpath, efile):
    book, name = chunkpath.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    edits = json.loads(rd(efile))
    nseg = 0
    nops = 0
    for k in sorted(edits, key=lambda x: int(x)):
        i = idxs[int(k) - 1]
        old = lines[i]
        cur = old
        for find, new in edits[k]:
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND count=%d line=%s find=%r" % (c, k, find))
            cur = cur.replace(find, new)
            nops += 1
        if cur == old:
            raise SystemExit("no change line=%s" % k)
        lines[i] = cur
        nseg += 1
    d = os.path.join(BAK, book)
    if not os.path.isdir(d):
        os.makedirs(d)
    bp = os.path.join(d, name + "_v.txt")
    if not os.path.exists(bp):
        shutil.copy2(p, bp)
        print("backup " + os.path.relpath(bp, ROOT))
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(eol.join(lines))
    print("applied %s: %d lines, %d ops" % (chunkpath, nseg, nops))


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(sys.argv[2], [int(x) for x in sys.argv[3:]])
    elif sys.argv[1] == "apply":
        apply(sys.argv[2], sys.argv[3])
