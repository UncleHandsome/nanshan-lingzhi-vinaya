# -*- coding: utf-8 -*-
import os
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out"

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
