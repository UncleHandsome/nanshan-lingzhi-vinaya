# -*- coding: utf-8 -*-
import os, sys, difflib
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1")
from segdump_lib import load

TSV = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\fix_te1.tsv"
LOG = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1\verify.txt"

raw = open(TSV, encoding="utf-8").read()
lines = raw.split("\n")
if lines and lines[-1] == "":
    lines = lines[:-1]
out = []
out.append("lines=%d" % len(lines))
for ln in lines:
    parts = ln.split("\t")
    out.append("fields=%d key=%s" % (len(parts), "/".join(parts[:3])))
    if len(parts) != 4:
        out.append("  BAD LINE: %r" % ln[:80])
        continue
    book, chunk, seg, new = parts
    cur = load(book, chunk)[int(seg) - 1]
    if new == cur:
        out.append("  unchanged")
        continue
    sm = difflib.SequenceMatcher(None, cur, new)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append("  [%s] OLD<...%s...> NEW<...%s...>" % (
            tag, cur[max(0, i1-25):i2+25], new[max(0, j1-25):j2+25]))
open(LOG, "w", encoding="utf-8").write("\n".join(out))
print("ok", len(lines))
