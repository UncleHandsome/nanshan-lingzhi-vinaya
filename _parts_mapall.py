import json, os
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
base="AI語譯/out/資持記"
cache={}
out=[]
mismatch=[]
for r in rows:
    f=os.path.join(base, r["chunk"]+".txt")
    if f not in cache:
        raw=[l.rstrip("\r\n") for l in open(f,encoding="utf-8")]
        paras=[l for l in raw if l.strip()]
        cache[f]=(raw,paras)
    raw,paras=cache[f]
    c=r["current"]
    try:
        li=raw.index(c)   # 0-based line
        pi=paras.index(c) # 0-based paragraph
    except ValueError:
        li=pi=-1
    out.append((r["idx"],r["gid"],r["chunk"],r["seg"],li+1 if li>=0 else -1, pi+1 if pi>=0 else -1))
    if pi+1 != int(r["seg"]):
        mismatch.append((r["idx"],r["gid"],r["chunk"],r["seg"],li+1 if li>=0 else -1, pi+1 if pi>=0 else -1))
print("rows:",len(out),"not found:",sum(1 for o in out if o[5]==-1))
print("mismatch seg vs paragraph:",len(mismatch))
for m in mismatch: print(m)
