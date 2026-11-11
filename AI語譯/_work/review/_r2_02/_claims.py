# -*- coding: utf-8 -*-
"""Lean per-chunk claim digest with claim IDs. No current translation; short orig head."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
NEG=re.compile(r"無誤|無問題|正確|妥當|無需|不必|不需|均可|皆可|無礙|允當|貼切|精準|未見問題|沒有問題|無須")

def is_claim(r):
    if not r["claim"]: return False
    if NEG.search(r["text"]) and not re.search(r"建議|應作|宜改|改為|問題：",r["text"]): return False
    return True

def clean(t):
    t=t.replace("\n"," / ")
    t=re.sub(r"\*\*|`|^[-*•]\s*","",t)
    t=re.sub(r"\s+"," ",t)
    return t.strip()

def build(chunk, head=70, tmax=400, per_max=10):
    idx=L.load_map()["idx"]
    rows=json.load(io.open(os.path.join(OUT,"_items_all.json"),encoding="utf-8"))
    byseg=collections.defaultdict(list)
    for r in rows:
        if not r["ids"] or not is_claim(r): continue
        for g in r["ids"]:
            if g not in idx or idx[g]["chunk"]!=chunk: continue
            byseg[g].append(r)
    Ls=["### %s  segs=%d with_claims=%d"%(chunk,len(L.paras(chunk)),len(byseg))]
    n=0
    for g in sorted(byseg, key=lambda x:int(idx[x]["seg"])):
        e=idx[g]; s=int(e["seg"]); o=e["orig"]
        Ls.append("\n#%d %s 原:%s"%(s,g, o[:head]+("…" if len(o)>head else "")))
        for r in byseg[g][:per_max]:
            n+=1
            t=clean(r["text"]); 
            if len(t)>tmax: t=t[:tmax]+"…"
            Ls.append("[C%d-%02d] %s"%(r["resp"],r["bi"],t))
        if len(byseg[g])>per_max:
            for r in byseg[g][per_max:]:
                n+=1
                t=clean(r["text"]);
                if len(t)>tmax: t=t[:tmax]+"…"
                Ls.append("[C%d-%02d] %s"%(r["resp"],r["bi"],t))
    p=os.path.join(OUT,"cl_%s.txt"%chunk[:3])
    txt="\n".join(Ls)
    io.open(p,"w",encoding="utf-8").write(txt)
    return p,len(txt),n,len(byseg)

if __name__=="__main__":
    tot=0
    for ch in sys.argv[1].split(","):
        r=build(ch); print(r); tot+=r[1]
    print("TOTAL chars",tot)
