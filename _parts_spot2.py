import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
new={}
for line in open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8"):
    p=line.rstrip("\n").split("\t")
    new[(p[1],p[2])]=p[3]
sel=[43,44,51,93,99,140,143,144,145,147,148,172,173,174,177,201,205,209,213,69,152]
out=[]
for i in sel:
    r=by[i]; n=new[(r["chunk"],r["seg"])]
    out.append(f"### {i} {r['gid']} {r['chunk']} seg={r['seg']}  (len {len(n)})")
    out.append(n)
    out.append("")
open("_parts_spot2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
