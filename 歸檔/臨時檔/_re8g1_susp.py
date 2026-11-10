import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
susp=[]
for x in d:
    for o,n in x["pairs"]:
        r=[]
        if x["CUR"].count(o)!=1: r.append(f"cnt={x['CUR'].count(o)}")
        if len(n)>len(o)*2+15: r.append(f"len {len(o)}->{len(n)}")
        if "……" in n: r.append("ellipsis")
        if n.endswith("」") and o.endswith("」"): pass
        if len(o)<5: r.append("shortold")
        if r: susp.append((x["gid"],x["seg"],o,n,";".join(r)))
print(len(susp))
out=[]
for g,s,o,n,r in susp:
    out.append(f"{g} seg={s} [{r}]\n  OLD: {o}\n  NEW: {n}")
open(r"AI語譯\_work\review\_re8g1_susp.txt","w",encoding="utf-8").write("\n".join(out))
