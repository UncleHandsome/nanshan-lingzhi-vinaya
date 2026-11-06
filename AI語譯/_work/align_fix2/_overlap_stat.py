# -*- coding: utf-8 -*-
import csv, io, os, glob
from collections import Counter

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料"
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix2\_overlap_stat.txt"
w = io.open(out, "w", encoding="utf-8")

def norm(s):
    return ''.join(ch for ch in s if ('\u3400' <= ch <= '\u9fff') or ch.isalnum())

def grams(s, n=2):
    return Counter(s[i:i+n] for i in range(len(s)-n+1))

tot = 0
ok = 0
detail = []
for p in sorted(glob.glob(os.path.join(B, "篇*.csv"))):
    if "篇26" in p or "篇27" in p:
        continue
    rows = list(csv.reader(io.open(p, encoding="utf-8-sig")))[1:]
    rec = [(r[0], int(r[1]), r[2], r[4]) for r in rows if len(r) >= 5 and r[1].strip().isdigit()]
    cao = {n: x for t, n, x, d in rec if t == "鈔"}
    caoG = {n: grams(norm(x)) for n, x in cao.items()}
    for t, n, x, d in rec:
        if t != "記" or not d.strip():
            continue
        g = grams(norm(x))
        best = None
        scores = []
        for cn, cg in caoG.items():
            sc = sum((g & cg).values())
            scores.append((sc, cn))
        scores.sort(reverse=True)
        top = scores[0]
        tot += 1
        if top[1] == int(d):
            ok += 1
        else:
            detail.append((os.path.basename(p), n, d, top[1], top[0], x[:40], cao.get(int(d), "")[:40], cao.get(top[1], "")[:40]))
w.write("total=%d argmax_hit=%d (%.1f%%)\n\n" % (tot, ok, 100.0 * ok / max(tot, 1)))
for row in detail[:120]:
    w.write("%s 記%d -> assigned %s ; argmax=%s(%d)\n    JI:%s\n    ASS:%s\n    MAX:%s\n" % row)
w.close()
print("ok", tot, ok)
