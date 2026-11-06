# -*- coding: utf-8 -*-
import io, json, os, csv

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D = os.path.join(B, "AI語譯", "_work", "align_fix2")
data = json.load(io.open(os.path.join(D, "002.json"), encoding="utf-8"))
out = json.load(io.open(os.path.join(D, "out_002.json"), encoding="utf-8"))
items = data["items"]; cands = data["cand"]
zs = [it["z"] for it in items]
cs = [c["c"] for c in cands]
mp = out["map"]

errs = []
if len(mp) != len(items):
    errs.append("count %d != items %d" % (len(mp), len(items)))
if [m["z"] for m in mp] != zs:
    errs.append("z seq mismatch")
if any(m["c"] not in cs for m in mp):
    errs.append("c out of range")
if any(mp[i]["c"] > mp[i + 1]["c"] for i in range(len(mp) - 1)):
    errs.append("not monotonic")
print("ERRORS:", errs if errs else "none")
print("items=%d entries=%d distinct_c=%d" % (len(items), len(mp), len(set(m["c"] for m in mp))))

# compare with old CSV map (對應鈔號, 1-based)
p = os.path.join(B, "合編材料", "篇27_諸雜要行.csv")
rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
old = []
last = None
for r in rows:
    if r and r[0].strip() == "記":
        v = r[4].strip() if len(r) > 4 else ""
        if v.isdigit():
            last = int(v)
        old.append(last)
print("old csv 記 rows", len(old), "old head", old[:12], "old tail", old[-6:])
new1 = [m["c"] + 1 for m in mp]
same = sum(1 for a, b in zip(old, new1) if a == b)
print("rows unchanged vs old csv: %d / %d" % (same, len(new1)))
print("new 對應鈔號: ", new1)
