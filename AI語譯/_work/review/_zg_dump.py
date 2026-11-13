# -*- coding: utf-8 -*-
"""Dump paragraphs of a chunk (or a range) into UTF-8 file for inspection."""
import io
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    chunk = sys.argv[1]
    lo = int(sys.argv[2])
    hi = int(sys.argv[3])
    out = []
    for p in range(lo, hi + 1):
        out.append(u"===%s#%d=== len=%d" % (chunk, p, len(L.para(chunk, p))))
        out.append(L.para(chunk, p))
    with io.open(os.path.join(HERE, "_zg_dump.txt"), "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    main()
