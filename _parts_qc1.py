import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
lines=[l.rstrip("\n") for l in open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8")]
print("lines:",len(lines))
bad=[]
keys=set()
for k,l in enumerate(lines):
    p=l.split("\t")
    if len(p)!=4: bad.append((k+1,"fields",len(p)))
    if p[0]!="資持記": bad.append((k+1,"book",p[0]))
    if not p[3].strip(): bad.append((k+1,"empty",p[1]))
    if p[3]!=p[3].strip(): bad.append((k+1,"space",p[1]))
    if (p[1],p[2]) in keys: bad.append((k+1,"dup",p[1]+p[2]))
    keys.add((p[1],p[2]))
print("bad:",bad[:10],"total bad",len(bad))
# check merged rows
out=[]
for idx in (90,91,206,207,218,219):
    r=by[idx]
    ln=[l for l in lines if l.split("\t")[1]==r["chunk"] and l.split("\t")[2]==r["seg"]][0]
    out.append(f"[{idx}] {r['chunk']} seg={r['seg']}")
    out.append(ln.split("\t")[3])
    out.append("")
open("_parts_merge.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
