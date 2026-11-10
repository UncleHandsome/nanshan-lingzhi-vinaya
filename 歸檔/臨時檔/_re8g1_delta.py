import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
old=json.load(open(r"AI語譯\_work\review\_re8g1_mech.json",encoding="utf-8"))
oldmap={}
for x in old:
    oldmap.setdefault(x["gid"],set()).update(map(tuple,x["ok"]))
lines=[]
newp=0
for x in d:
    if not x["pairs"]: continue
    for o,n in x["pairs"]:
        if (o,n) in oldmap.get(x["gid"],set()): continue
        newp+=1
        lines.append(f'## {x["gid"]} seg={x["seg"]} {x["cls"]}')
        lines.append(f'  S: {x["S"]}')
        lines.append(f'  OLD: {o}')
        lines.append(f'  NEW: {n}')
        lines.append("")
print("new pairs", newp)
open(r"AI語譯\_work\review\_re8g1_delta.txt","w",encoding="utf-8").write("\n".join(lines))
