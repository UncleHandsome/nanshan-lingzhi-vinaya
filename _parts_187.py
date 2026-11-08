import json
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
r=by[187]
cur=[l.rstrip("\n") for l in open("AI語譯/out/資持記/15c_下三.txt",encoding="utf-8")]
raw=[l for l in cur if l.strip()]
print("seg",r["seg"],"len",len(r["current"]))
idx=[i+1 for i,l in enumerate(raw) if l==r["current"]]
print("match para:",idx,"total paras",len(raw))
out=[]
out.append("CUR: "+r["current"])
for k in (idx[0]-2, idx[0]-1, idx[0], idx[0]+1):
    if 0<=k-1<len(raw):
        out.append(f"--para{k}--")
        out.append(raw[k-1])
open("_parts_187.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
