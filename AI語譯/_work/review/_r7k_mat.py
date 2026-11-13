# -*- coding: utf-8 -*-
"""Print 校閱材料 entries for chunk N: id / 原文 / 譯文."""
import io, re, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HDR = re.compile(r"^【(\d+)-(\d+)】\s*(\S*)\s*$")


def main(n):
    p = ROOT + r"\校閱_7K\校閱_%d.txt" % n
    lines = io.open(p, encoding="utf-8").read().splitlines()
    cur = None
    src = tr = None
    for ln in lines:
        m = HDR.match(ln)
        if m:
            cur = (m.group(1), m.group(2), m.group(3))
            src = tr = None
            continue
        if ln.startswith("【原文】"):
            src = ln[4:]
        elif ln.startswith("【譯文】"):
            tr = ln[4:]
            if cur:
                print("### %s-%s %s" % cur)
                print("原:" + (src or ""))
                print("譯:" + (tr or ""))
                print()
            cur = None


main(int(sys.argv[1]))
