# -*- coding: utf-8 -*-
import csv, re
P = r"AI語譯/_work/review/report_re9.tsv"
rows = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows[i] = d

bookfile = r"AI語譯/out/05_拾毗尼義鈔/03a_卷中之一.txt"
txt = open(bookfile, encoding="utf-8").read()
lines = txt.split("\n")
cur = rows[245]["current"]
parts = cur.split("\n")
print("parts", len(parts), "first:", parts[0][:40])
print("last:", parts[-1][:40])
# find index of first part
for i, ln in enumerate(lines):
    if ln.startswith(parts[0][:20]):
        print("found at line", i)
        ok = True
        for k, p in enumerate(parts):
            if lines[i+k] != p:
                ok = False
                print(f"  mismatch at part {k}: file={lines[i+k][:40]!r} rep={p[:40]!r} (filelen={len(lines[i+k])}, replen={len(p)})")
                break
        print("exact concat match:", ok)
        break

print()
# same for 01b seg 4 (line 157)
bookfile2 = r"AI語譯/out/05_拾毗尼義鈔/01b_卷上之一.txt"
lines2 = open(bookfile2, encoding="utf-8").read().split("\n")
cur2 = rows[157]["current"]
p0 = cur2.split("\n")[0]
for i, ln in enumerate(lines2):
    if ln.startswith(p0[:20]):
        print("157 anchor at line", i, "len", len(ln), "rep len", len(p0), "equal:", ln == p0)
        print("  file:", ln[:80])
        print("  rep :", p0[:80])
        # diff position
        for j in range(min(len(ln), len(p0))):
            if ln[j] != p0[j]:
                print("  first diff at", j, "file:", ln[max(0,j-20):j+20], "| rep:", p0[max(0,j-20):j+20])
                break
        break
