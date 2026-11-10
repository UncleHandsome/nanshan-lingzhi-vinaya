import json, re
g1 = json.load(open(r"AI語譯\_work\review\_re8g1_rows.json", encoding="utf-8"))
d = json.load(open(r"AI語譯\_work\review\_re8g1_mech.json", encoding="utf-8"))
from collections import Counter
c=Counter()
for x in d:
    if not x["ok"]:
        c["no_valid"]+=1
    if len(x["ok"])==1: c["one_pair"]+=1
    if len(x["ok"])>=2: c["multi_pair"]+=1
    for old,new in x["ok"]:
        n = g1[[r[0] for r in g1].index(x["gid"])][9].count(old)
        if n>1: c["old_dup"]+=1
        if new and new in g1[[r[0] for r in g1].index(x["gid"])][9]: c["new_already"]+=1
print(c)
# also short pairs suspicious
for x in d:
    for old,new in x["ok"]:
        if len(old)<4: print("SHORT", x["gid"], repr(old), "->", repr(new))
