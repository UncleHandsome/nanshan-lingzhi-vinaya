# -*- coding: utf-8 -*-
"""Per-chunk claim digest from _claims3.json."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

def build(chunk, tmax=420):
    idx=L.load_map()["idx"]
    cl=json.load(io.open(os.path.join(OUT,"_claims3.json"),encoding="utf-8"))
    byseg=collections.defaultdict(list)
    used=set()
    for c in cl:
        ids=[g for g in c["ids"] if g in idx and idx[g]["chunk"]==chunk]
        if not ids: continue
        g=ids[0]
        if c["cid"] in used: continue
        used.add(c["cid"])
        byseg[g].append((c,ids))
    Ls=["## %s"%chunk[:3]]
    n=0
    for g in sorted(byseg,key=lambda x:int(idx[x]["seg"])):
        Ls.append("#%s"%idx[g]["seg"])
        for c,ids in byseg[g]:
            n+=1
            t=c["text"]
            if len(t)>tmax: t=t[:tmax]+"…"
            extra=("+"+",".join(x.split("-")[1] for x in ids[1:])) if len(ids)>1 else ""
            Ls.append("<%s|r%d%s> %s"%(c["cid"],c["resp"],extra,t))
    p=os.path.join(OUT,"q_%s.txt"%chunk[:3])
    txt="\n".join(Ls)
    io.open(p,"w",encoding="utf-8").write(txt)
    return chunk,len(txt),n

if __name__=="__main__":
    tot=0
    for ch in sys.argv[1].split(","):
        r=build(ch); print(r); tot+=r[1]
    print("TOTAL",tot)
