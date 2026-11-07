# -*- coding: utf-8 -*-
import csv, os, difflib, io

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
rev = os.path.join(base, "_work", "review")
out = os.path.join(base, "out")

def read_tsv(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.reader(f, delimiter="\t", quotechar='"')]

rrows = read_tsv(os.path.join(rev, "report_t1_located.tsv"))

def segs(book, chunk):
    with open(os.path.join(out, book, chunk + ".txt"), "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

targets = {("03_業疏","01a_卷一之一","48"), ("02_戒疏","09b_卷二下之二","124"), ("02_戒疏","10d_卷三上之一","131")}
buf = []
for d in (dict(zip(rrows[0], row)) for row in rrows[1:]):
    if (d["book"], d["chunk"], d["seg"]) not in targets:
        continue
    live = segs(d["book"], d["chunk"])[int(d["seg"]) - 1]
    cur = d["current"]
    buf.append("=" * 30 + f" {d['book']} {d['chunk']} {d['seg']}")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, cur, live).get_opcodes():
        if tag != "equal":
            buf.append(f"{tag}: CUR={cur[i1:i2]!r} -> LIVE={live[j1:j2]!r}")
    buf.append("CUR tail: " + repr(cur[-12:]))
    buf.append("LIVE tail: " + repr(live[-12:]))
with open(os.path.join(rev, "_t1b_diff2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
