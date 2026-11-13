# -*- coding: utf-8 -*-
"""列出未改段的原文／現行，供逐段掃描（否決處）。"""
import os, sys, io
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of, VIEW  # noqa

buf = []
for n in sys.argv[1:]:
    segs = parse_x7(n)
    buf.append("\n######## %s ########" % n)
    for s in segs:
        if cur_of(s) == s["tr"]:
            buf.append("--- %s\n[原] %s\n[今] %s" % (s["no"], s["src"], cur_of(s)))
io.open(os.path.join(VIEW, "sameview_all.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
print("ok %d lines" % len(buf))
