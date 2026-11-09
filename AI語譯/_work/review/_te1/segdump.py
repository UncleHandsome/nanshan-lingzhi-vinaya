# -*- coding: utf-8 -*-
import sys, os

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out"

def load(book, chunk):
    p = os.path.join(BASE, book, chunk + ".txt")
    with open(p, encoding="utf-8") as f:
        txt = f.read()
    # split into paragraphs on blank lines
    lines = txt.split("\n")
    segs = []
    cur = []
    for ln in lines:
        if ln.strip() == "":
            if cur:
                segs.append("\n".join(cur))
                cur = []
        else:
            cur.append(ln)
    if cur:
        segs.append("\n".join(cur))
    return segs

if __name__ == "__main__":
    book, chunk = sys.argv[1], sys.argv[2]
    segs = load(book, chunk)
    print("count=", len(segs))
    for i, s in enumerate(segs, 1):
        print(i, len(s), s[:50].replace("\n", "\\n"))
