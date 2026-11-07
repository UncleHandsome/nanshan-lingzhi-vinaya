# -*- coding: utf-8 -*-
import os, csv, difflib

base = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(base, "AI語譯", "_work", "review", "fix_p0_t2.tsv")

with open(FIX, encoding="utf-8") as f:
    raw = f.read()
assert "\r" not in raw, "CR found"
lines = [l for l in raw.split("\n") if l]
out = []
for i, l in enumerate(lines):
    parts = l.split("\t")
    assert len(parts) == 4, (i, len(parts))
    book, chunk, seg, new = parts
    assert new.strip(), i
    out.append("=" * 100)
    out.append("[%d] %s | %s | seg %s | len=%d" % (i, book, chunk, seg, len(new)))
    out.append(new)
    out.append("")

out.append("TOTAL ROWS: %d" % len(lines))
with open(os.path.join(base, "_fix_check.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("rows:", len(lines), "ok; CR present:", "\r" in raw)
