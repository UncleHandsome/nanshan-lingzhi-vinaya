# -*- coding: utf-8 -*-
import io, json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
base = {}
groups = {}
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    groups.setdefault(k, d)
    base[k] = d["current"].replace("\n", "")

for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    book, chunk, seg, new = l.split("\t")
    old = base[(book, chunk, seg)]
    for q1, q2, name in (("『", "』", "SHUANG"), ("（或", "", "ALT")):
        if new.count(q1) > old.count(q1) or (name == "ALT" and q1 in new):
            print("%s %s s%s %s: old%d new%d" % (book, chunk, seg, name, old.count(q1), new.count(q1)))
            # print the newly introduced fragment context
            idx = new.find(q1)
            while idx != -1:
                if idx > 60:
                    print("    ...%s..." % new[max(0, idx-50):idx+40])
                    break
                idx = new.find(q1, idx+1)
