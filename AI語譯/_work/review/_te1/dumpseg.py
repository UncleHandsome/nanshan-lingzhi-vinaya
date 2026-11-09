# -*- coding: utf-8 -*-
import os, sys, json
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out"
OUT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1\seg"

def load(book, chunk):
    p = os.path.join(BASE, book, chunk + ".txt")
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    lines = txt.split("\n")
    segs, cur = [], []
    for ln in lines:
        if ln.strip() == "":
            if cur:
                segs.append("\n".join(cur)); cur = []
        else:
            cur.append(ln)
    if cur:
        segs.append("\n".join(cur))
    return segs

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    book, chunk, seg = sys.argv[1], sys.argv[2], int(sys.argv[3])
    segs = load(book, chunk)
    s = segs[seg-1]
    p = os.path.join(OUT, "%s__%s__%d.txt" % (book, chunk, seg))
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    print(p)
