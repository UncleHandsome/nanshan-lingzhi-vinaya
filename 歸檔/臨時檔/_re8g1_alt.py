import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
n=0
for x in d:
    hit=[p for p in x["pairs"] if ("或：" in p[1] or "（或" in p[1])]
    if hit:
        n+=1
        print(x["gid"],x["seg"])
        for o,new in hit: print("   NEW:",new)
print("total",n)
