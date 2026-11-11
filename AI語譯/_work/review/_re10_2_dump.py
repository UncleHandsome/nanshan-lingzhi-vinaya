# -*- coding: utf-8 -*-
"""Dump current out/<book>/<chunk>.txt segments for re10_2 segments."""
import io, os, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")

SEGS = [
    ("001-0005", "01_行事鈔", "00_卷首", 5),
    ("001-0007", "01_行事鈔", "00_卷首", 7),
    ("001-0008", "01_行事鈔", "00_卷首", 8),
    ("001-0026", "01_行事鈔", "00_卷首", 26),
    ("001-0029", "01_行事鈔", "00_卷首", 29),
    ("001-0033", "01_行事鈔", "00_卷首", 33),
    ("001-0053", "01_行事鈔", "00_卷首", 53),
    ("001-0058", "01_行事鈔", "00_卷首", 58),
    ("001-0075", "01_行事鈔", "00_卷首", 75),
    ("001-0097", "01_行事鈔", "01a_卷上之一", 15),
    ("001-0099", "01_行事鈔", "01a_卷上之一", 17),
    ("001-0103", "01_行事鈔", "01a_卷上之一", 21),
    ("001-0106", "01_行事鈔", "01a_卷上之一", 24),
    ("001-0110", "01_行事鈔", "01a_卷上之一", 28),
    ("001-0115", "01_行事鈔", "01a_卷上之一", 33),
]

def load(book, chunk):
    p = os.path.join(OUT, book, chunk + ".txt")
    raw = open(p, "rb").read()
    s = raw.decode("utf-8")
    nl = "\r\n" if "\r\n" in s else "\n"
    parts = s.split(nl + nl)
    return p, nl, parts

buf = []
cache = {}
for seg, book, chunk, n in SEGS:
    if (book, chunk) not in cache:
        cache[(book, chunk)] = load(book, chunk)
    p, nl, parts = cache[(book, chunk)]
    seg_txt = parts[n - 1]
    buf.append("=" * 100)
    buf.append(f"{seg} | {book}/{chunk}#{n} | total_parts={len(parts)}")
    buf.append("-" * 100)
    buf.append(seg_txt)
    buf.append("")

open(os.path.join(ROOT, "AI語譯", "_work", "review", "_re10_2_cur.txt"),
     "w", encoding="utf-8", newline="\n").write("\n".join(buf))
