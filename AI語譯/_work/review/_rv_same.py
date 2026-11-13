# -*- coding: utf-8 -*-
"""列出每檔「同（未改）」的段，含該段有無入 dig。"""
import os, sys, re, io
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa

SEG = re.compile(r"\d{3,4}-\d{4}")
buf = []
for n in sys.argv[1:]:
    segs = parse_x7(n)
    same = [s["no"] for s in segs if cur_of(s) == s["tr"]]
    diff = [s["no"] for s in segs if cur_of(s) != s["tr"]]
    buf.append("%s 同(%d): %s" % (n, len(same), " ".join(x.split("-")[1] for x in same)))
    buf.append("     改(%d): %s" % (len(diff), " ".join(x.split("-")[1] for x in diff)))
open(os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_view", "same_%s.txt" % sys.argv[1]), "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
print("\n".join(buf))
