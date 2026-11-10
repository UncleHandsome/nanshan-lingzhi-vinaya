import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
new={}
for line in open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8"):
    p=line.rstrip("\n").split("\t")
    new[(p[1],p[2])]=p[3]
sel=[7,10,16,21,30,39,42,50,58,61,72,79,80,117,133,157,160,187,199,211,217,219]
out=[]
for i in sel:
    r=by[i]; n=new[(r["chunk"],r["seg"])]
    out.append(f"### {i} {r['gid']} {r['chunk']} seg={r['seg']}")
    out.append(n)
    out.append("")
open("_parts_spot.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
