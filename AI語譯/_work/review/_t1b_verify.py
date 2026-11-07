# -*- coding: utf-8 -*-
import csv, os, json, io, sys

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
        t = f.read()
    return [x for x in t.replace("\r\n", "\n").split("\n\n") if x.strip()]

report = []
for row in rrows[1:]:
    d = dict(zip(rrows[0], row))
    report.append(d)

lines = []
for d in report:
    key = (d["book"], d["chunk"], d["seg"])
    if key in applied:
        continue
    if not d["current"].strip():
        lines.append(f"MISSING current {key}")
        continue
    sl = segs(d["book"], d["chunk"])
    i = int(d["seg"]) - 1
    live = sl[i] if 0 <= i < len(sl) else "<OUT OF RANGE>"
    same = live == d["current"]
    lines.append(f"{d['book']} | {d['chunk']} | seg {d['seg']} | nparas={len(sl)} | live_len={len(live)} cur_len={len(d['current'])} | identical={same}")

sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
