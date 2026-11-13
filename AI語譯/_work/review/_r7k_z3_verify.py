# -*- coding: utf-8 -*-
"""Verify 卷下之一 edits against backups."""
import os, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔")
CHUNKS = ["09a_卷下之一", "09b_卷下之一", "09c_卷下之一", "10a_卷下之二"]


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


for ch in CHUNKS:
    p = os.path.join(OUT, ch + ".txt")
    b = os.path.join(BAK, ch + "_v.txt")
    if not os.path.exists(b):
        print(ch, "no backup (unchanged)")
        continue
    raw, old = rd(p), rd(b)
    print("=" * 20, ch, "EOL", "CRLF" if "\r\n" in raw else "LF",
          "| before", len(old.encode()), "after", len(raw.encode()),
          "| ends-newline", old.endswith("\n"), raw.endswith("\n"))
    eol = "\r\n" if "\r\n" in old else "\n"
    assert ("\r\n" in old) == ("\r\n" in raw), "EOL changed"
    lo = old.split(eol)
    ln = raw.split(eol)
    print("lines", len(lo), "->", len(ln))
    assert len(lo) == len(ln)
    n = 0
    for i, (a, c) in enumerate(zip(lo, ln)):
        if a != c:
            n += 1
            # non-empty index
            k = sum(1 for x in lo[:i + 1] if x.strip())
            print("  line %d (#%d) len %d -> %d" % (i + 1, k, len(a), len(c)))
    print("changed lines:", n)
