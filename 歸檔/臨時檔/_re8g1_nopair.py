import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
lines=[]
n=0
for x in d:
    if x["pairs"]: continue
    n+=1
    lines.append(f'## {x["gid"]} chunk={x["chunk"]} seg={x["seg"]} {x["cls"]}')
    lines.append(f'  P: {x["P"]}')
    lines.append(f'  S: {x["S"]}')
    lines.append(f'  CUR: {x["CUR"]}')
    lines.append("")
print(n)
open(r"AI語譯\_work\review\_re8g1_nopair.txt","w",encoding="utf-8").write("\n".join(lines))
