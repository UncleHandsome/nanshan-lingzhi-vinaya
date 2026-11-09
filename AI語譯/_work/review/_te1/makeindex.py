# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from segdump_lib import load
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out"
OUT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1"

if __name__ == "__main__":
    book, chunk = sys.argv[1], sys.argv[2]
    segs = load(book, chunk)
    p = os.path.join(OUT, "index_%s_%s.txt" % (book, chunk))
    with open(p, "w", encoding="utf-8") as f:
        f.write("count= %d\n" % len(segs))
        for i, s in enumerate(segs, 1):
            f.write("%02d\t%d\t%s\n" % (i, len(s), s[:40].replace("\n", " ")))
    print(p)
