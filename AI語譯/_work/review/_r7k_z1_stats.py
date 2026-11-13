# -*- coding: utf-8 -*-
import os, json, difflib, csv
from collections import OrderedDict

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
segs = json.load(open(os.path.join(ROOT, r"AI語譯\_work\review\_r7k_z1_segs.json"), encoding="utf-8"))

def lines(p):
    return [l for l in open(p, encoding="utf-8", newline="").read().splitlines() if l.strip()]

cache = {}
def get(c):
    if c not in cache:
        op = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔", c + "_v.txt")
        if os.path.exists(op):
            a = lines(op)
        else:
            a = lines(os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", c + ".txt"))
        b = lines(os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", c + ".txt"))
        cache[c] = (a, b)
    return cache[c]

rej = {
"128":3,"129":2,"130":2,"131":2,"132":3,"133":2,"134":2,"135":2,"136":3,"137":3,
"138":3,"139":1,"140":2,"141":2,"142":2,"143":2,"144":2,"145":1,"146":2,"147":2,
"148":1,"149":1,"150":2,"151":2,"152":2,"153":2,"154":2,"155":2,"156":1,
"158":3,"159":3,"160":2,"161":2,"162":2,"163":2,"164":1,"165":2,"166":2,"167":2,
"168":2,"169":1,"170":2,"171":2,"2809":1}
doubt = {"130":1,"131":1,"148":1,"155":1,"166":1,"169":1}

stat = OrderedDict()
for s in segs:
    f = s["file"]; c = s["chunk"]; i = s["idx"]
    if f not in stat:
        stat[f] = {"chunk": c, "n": 0, "chg": 0, "edits": 0}
    stat[f]["n"] += 1
    a, b = get(c)
    if i - 1 < len(a) and i - 1 < len(b) and a[i-1] != b[i-1]:
        stat[f]["chg"] += 1
        sm = difflib.SequenceMatcher(None, a[i-1], b[i-1])
        stat[f]["edits"] += sum(1 for tag, *_ in sm.get_opcodes() if tag != "equal")

print("檔\tchunk\t段數\t改段\t改處\t否決\t存疑")
tot = [0,0,0,0,0]
for f, v in stat.items():
    d = doubt.get(f, 0)
    print(f"{f}\t{v['chunk']}\t{v['n']}\t{v['chg']}\t{v['edits']}\t{rej[f]}\t{d}")
    tot[0]+=v['n']; tot[1]+=v['chg']; tot[2]+=v['edits']; tot[3]+=rej[f]; tot[4]+=d
print("TOTAL\t\t%d\t%d\t%d\t%d\t%d" % tuple(tot))
