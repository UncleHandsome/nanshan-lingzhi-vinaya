import json,io,collections,os
f=r"AI語譯\_work\review\_r2_02\_refs.json"
R=json.load(io.open(f,encoding="utf-8"))
print(list(R.keys()))
by=R.get("by_chunk")
print("by_chunk keys:", len(by))
tot=0
per=collections.Counter()
segs=collections.defaultdict(set)
for n,d in R["refs"].items():
    if not (550<=int(n)<=641): continue
    for g in d["all"]:
        tot+=1
        ch=g.split("-")[0]
        per[n]+=1
        segs[n].add(g)
print("resp files:",len([n for n in R["refs"] if 550<=int(n)<=641]))
print("total ref mentions:",tot)
print("unique seg-refs:",sum(len(v) for v in segs.values()))
print("per-file mention distribution:", collections.Counter(per.values()))
