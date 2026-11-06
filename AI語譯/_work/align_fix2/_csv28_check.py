# -*- coding: utf-8 -*-
import csv, io, os, json

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(B, "AI語譯", "_work", "align_fix2", "_csv28_check.txt")
w = io.open(out, "w", encoding="utf-8")

# CSV 28
p = os.path.join(B, "合編材料", "篇28_沙彌別法.csv")
rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
ji = [(r[1], r[2], r[4]) for r in rows if r[0] == "記"]
cao = [(r[1], r[2]) for r in rows if r[0] == "鈔"]
w.write("CSV28: 記=%d 鈔=%d\n" % (len(ji), len(cao)))

# batch
b = json.load(io.open(os.path.join(B, "AI語譯", "_work", "align_last3", "001.json"), encoding="utf-8"))
o = json.load(io.open(os.path.join(B, "AI語譯", "_work", "align_last3", "out_001.json"), encoding="utf-8"))["map"]
mp = {x["z"]: x["c"] for x in o}
items = b["items"]
cands = b["cand"]
w.write("batch: items=%d cand=%d\n" % (len(items), len(cands)))

# match each batch item to CSV 記 by prefix
def norm(s):
    return "".join(ch for ch in s if ch.strip())

offsets = []
for it in items[:12]:
    key = norm(it["text"])[:25]
    hit = None
    for idx, (no, txt, dui) in enumerate(ji):
        if norm(txt).startswith(key[:20]):
            hit = idx
            break
    offsets.append((it["z"], hit))
w.write("offset probe (z -> csv ji index): %s\n" % offsets)

# batch cand vs CSV 鈔
offc = []
for cd in cands[:10]:
    key = norm(cd["text"])[:25]
    hit = None
    for idx, (no, txt) in enumerate(cao):
        if norm(txt).startswith(key[:20]):
            hit = idx
            break
    offc.append((cd["c"], hit))
w.write("cand probe (c -> csv cao index): %s\n" % offc)
w.write("\n")
for i, it in enumerate(items):
    z = it["z"]
    c = mp.get(z)
    # find csv ji by exact prefix
    key = norm(it["text"])[:20]
    idx = None
    for j, (no, txt, dui) in enumerate(ji):
        if norm(txt).startswith(key):
            idx = j
            break
    dui = ji[idx][2] if idx is not None else "?"
    no = ji[idx][0] if idx is not None else "?"
    w.write("z%-3d c%-3d | csv記序號=%-4s 對應鈔號=%-5s %s\n" % (z, c, no, dui, "OK" if str(c + 1) == str(dui) else ""))
w.close()
print("ok")
