import csv, re

cur = {}
order = []
with open(r"AI語譯/_work/review/report_err.tsv", encoding="utf-8") as f:
    for d in csv.DictReader(f, delimiter="\t"):
        if d["book"] == "03_業疏":
            cur[d["gid"]] = d
            order.append(d)
seg2gid = {(d["chunk"], d["seg"]): d["gid"] for d in order}

pat = ["。。","，，","；；","：：","、、","（）","《》","「「","」」","！。","？。","，。","。，","  "]
badpat = []
lastchar = []
balance = []
for line in open(r"AI語譯/_work/review/fix_err_g2.tsv", encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    gid = seg2gid[(p[1], p[2])]
    new = p[3]
    old = cur[gid]["current"]
    for q in pat:
        if q in new and q not in old:
            badpat.append((gid, q))
    if new[-1] != old[-1]:
        lastchar.append((gid, old[-1], new[-1]))
    for o, c in [("「","」"),("《","》"),("（","）"),("〈","〉"),("『","』")]:
        if new.count(o) != new.count(c):
            balance.append((gid, o, new.count(o), c, new.count(c)))
print("bad patterns:", badpat)
print("last char changed:", lastchar)
print("unbalanced:", balance)
