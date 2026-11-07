# -*- coding: utf-8 -*-
import csv, os, json

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
rev = os.path.join(base, "_work", "review")

def read_tsv(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.reader(f, delimiter="\t", quotechar='"')]

t1 = read_tsv(os.path.join(rev, "report_t1_located.tsv"))
a1 = read_tsv(os.path.join(rev, "applied_t1_located.tsv"))
t2 = read_tsv(os.path.join(rev, "report_t2_located.tsv"))
a2 = read_tsv(os.path.join(rev, "applied_t2_located.tsv"))

def key(r):
    return (r[0], r[1], r[2])

applied1 = {key(r) for r in a1[1:] if len(r) >= 3}
applied2 = {key(r) for r in a2[1:] if len(r) >= 3}
t2map = {}
for r in t2[1:]:
    if len(r) >= 11:
        t2map.setdefault(key(r), []).append(r)

rows = [dict(zip(t1[0], r)) for r in t1[1:]]
buf = []
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    if k in applied1:
        continue
    tags = []
    if k in applied2:
        tags.append("APPLIED_T2")
    if k in t2map:
        tags.append("IN_T2")
    buf.append(f"{k[0]} | {k[1]} | {k[2]} | {' '.join(tags) if tags else 'ONLY_T1'}")
with open(os.path.join(rev, "_t1b_overlap.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")

# also dump the t2 suggested new for overlapping rows
buf2 = []
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    if k in applied1:
        continue
    if k in applied2:
        for r in a2[1:]:
            if len(r) >= 3 and key(r) == k:
                # applied t2 columns: book chunk seg level src old new
                buf2.append(f"### {k}\nOLD: {r[5]}\nNEW: {r[6]}\n")
with open(os.path.join(rev, "_t1b_t2new.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf2) + "\n")
print("ok")
