# -*- coding: utf-8 -*-
"""產出「未改段（＝否決處）」的意見全文（用 dig 的分段器，容忍表格/編號）。"""
import os, sys, re, io
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of, RESP, VIEW  # noqa
from _rv_dig2 import split_items  # noqa

for n in sys.argv[1:]:
    p = os.path.join(RESP, "resp_%s.txt" % n)
    if not os.path.exists(p):
        continue
    text = io.open(p, encoding="utf-8").read()
    text = re.sub(r"(?m)^([\s#*\-•·]*)(【)(\d{4})(】)",
                  lambda m: m.group(1) + "【" + n + "-" + m.group(3) + "】", text)
    segs = {s["no"]: s for s in parse_x7(n)}
    same = set(k for k, s in segs.items() if cur_of(s) == s["tr"])
    buf = ["######## %s （未改段：%s） ########" % (n, " ".join(sorted(x.split("-")[1] for x in same)))]
    for nos, body in split_items(text):
        use = [x for x in nos if x in segs]
        if not use:
            continue
        if all(x in same for x in use):
            buf.append("\n=== %s ===\n%s" % ("、".join(use), body))
    out = os.path.join(VIEW, "veto2_%s.txt" % n)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("%s ok %d items" % (n, len(buf) - 1))
