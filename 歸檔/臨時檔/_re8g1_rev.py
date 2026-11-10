import json
g1 = json.load(open(r"AI語譯\_work\review\_re8g1_rows.json", encoding="utf-8"))
d = json.load(open(r"AI語譯\_work\review\_re8g1_mech.json", encoding="utf-8"))
rows={}
for r in g1:
    rows.setdefault(r[0], r)
def key(x):
    return (x["chunk"], int(x["seg"]), x["gid"])
auto=[]
man=[]
for x in d:
    if x["ok"] and len(x["ok"])==1:
        auto.append(x)
    else:
        man.append(x)
auto.sort(key=key); man.sort(key=key)
lines=[]
lines.append(f"=== AUTO {len(auto)} rows ===")
for x in auto:
    old,new=x["ok"][0]
    lines.append(f'{x["gid"]}\t{x["seg"]}\t{old}\t=> {new}')
lines.append("")
lines.append(f"=== MANUAL {len(man)} rows ===")
for x in man:
    r=rows[x["gid"]]
    ps=" | ".join(f"{o} => {n}" for o,n in x["ok"]) if x["ok"] else "-"
    lines.append(f'## {x["gid"]} seg={x["seg"]} L={r[4]} {r[5]}')
    lines.append(f'  P: {r[6]}')
    lines.append(f'  S: {r[7]}')
    lines.append(f'  CUR: {r[9]}')
    if x["ok"]: lines.append(f'  PAIRS: {ps}')
    lines.append("")
open(r"AI語譯\_work\review\_re8g1_review.txt","w",encoding="utf-8").write("\n".join(lines))
print(len(auto), len(man))
