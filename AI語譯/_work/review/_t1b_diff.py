# -*- coding: utf-8 -*-
import csv, os, sys, difflib

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
rev = os.path.join(base, "_work", "review")
out = os.path.join(base, "out")

def read_tsv(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.reader(f, delimiter="\t", quotechar='"')]

rrows = read_tsv(os.path.join(rev, "report_t1_located.tsv"))
arows = read_tsv(os.path.join(rev, "applied_t1_located.tsv"))
applied = {(r[0], r[1], r[2]) for r in arows[1:] if len(r) >= 3}

def segs(book, chunk):
    p = os.path.join(out, book, chunk + ".txt")
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

targets = [("03_業疏","01a_卷一之一","48"), ("02_戒疏","09b_卷二下之二","124"), ("02_戒疏","10d_卷三上之一","131")]
for d in (dict(zip(rrows[0], row)) for row in rrows[1:]):
    if (d["book"], d["chunk"], d["seg"]) not in targets:
        continue
    sl = segs(d["book"], d["chunk"])
    live = sl[int(d["seg"]) - 1]
    cur = d["current"]
    print("=" * 30, d["book"], d["chunk"], d["seg"])
    sm = difflib.SequenceMatcher(None, cur, live)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(tag, repr(cur[i1:i2]), "->", repr(live[j1:j2]))
    print("cur tail:", repr(cur[-15:]))
    print("live tail:", repr(live[-15:]))
