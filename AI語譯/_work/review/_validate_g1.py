# -*- coding: utf-8 -*-
import csv, difflib
P = r"AI語譯/_work/review/report_re9.tsv"
F = r"AI語譯/_work/review/fix_re9_g1.tsv"

cur = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    h = next(r)
    for row in r:
        if len(row) < 10: continue
        d = dict(zip(h, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        cur.setdefault((d["chunk"], str(d["seg"])), d["current"])

raw = open(F, "rb").read()
print("bytes:", len(raw), "starts with BOM:", raw[:3] == b"\xef\xbb\xbf", "ends with LF:", raw.endswith(b"\n"))
text = raw.decode("utf-8")
lines = text.split("\n")
if lines and lines[-1] == "": lines.pop()
print("lines:", len(lines))
bad = 0
keys = []
low = []
for i, ln in enumerate(lines, 1):
    parts = ln.split("\t")
    if len(parts) != 4:
        print("BAD field count", i, len(parts)); bad += 1; continue
    b, c, s, new = parts
    keys.append((c, s))
    if b != "05_拾毗尼義鈔": print("bad book", i, b); bad += 1
    if (c, s) not in cur:
        print("key not in report", i, c, s); bad += 1; continue
    old = cur[(c, s)].rstrip("\n").replace("\n", "")
    if old == new:
        print("NO CHANGE", i, c, s); bad += 1
    r = difflib.SequenceMatcher(None, old, new).ratio()
    if r < 0.55:
        low.append((i, c, s, round(r,3), len(old), len(new)))
print("bad:", bad)
print("duplicate keys:", len(keys) - len(set(keys)))
print("low similarity rows:")
for x in low: print("  ", x)
