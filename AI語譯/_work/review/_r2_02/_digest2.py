# -*- coding: utf-8 -*-
"""Build per-chunk review digest: for each segment with claims, orig + current + all claim texts."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
ID_FULL=re.compile(r"(?<!\d)(\d{3})-(\d{4})(?!\d)")
NEG=re.compile(r"無誤|無問題|正確|妥當|無需|不必|不需|均可|皆可|無礙|允當|貼切|精準|未見問題|沒有問題|無須")

def is_claim(r):
    if not r["claim"]: return False
    if NEG.search(r["text"]) and not re.search(r"建議|應作|宜改|改為|問題：",r["text"]): return False
    return True

def norm(s):
    return re.sub(r"[\s>*`#\-—…「」『』（）()\[\]【】,，。、：:；;！!？?\"'“”‘’|]+","",s)

def dedupe(rows):
    out=[]; seen=[]
    for r in rows:
        k=norm(r["text"])[:120]
        dup=False
        for s in seen:
            if k[:80] in s or s[:80] in k: dup=True;break
        if dup: continue
        seen.append(k); out.append(r)
    return out

def build(chunk, orig_lim=220, cur_lim=320, per_max=6):
    idx=L.load_map()["idx"]
    rows=json.load(io.open(os.path.join(OUT,"_items_all.json"),encoding="utf-8"))
    byseg=collections.defaultdict(list)
    for r in rows:
        if not r["ids"] or not is_claim(r): continue
        for g in r["ids"]:
            if g not in idx or idx[g]["chunk"]!=chunk: continue
            byseg[g].append(r)
    ps=L.paras(chunk)
    Ls=["### %s  (segs=%d, segs_with_claims=%d)"%(chunk,len(ps),len(byseg))]
    for g in sorted(byseg, key=lambda x:int(idx[x]["seg"])):
        e=idx[g]; s=int(e["seg"])
        o=e["orig"]; cur=ps[s-1] if 0<s<=len(ps) else "NA"
        Ls.append("\n===== %s  #%d"%(g,s))
        Ls.append("原文："+(o if len(o)<=orig_lim else o[:orig_lim]+"…"))
        Ls.append("現行："+(cur if len(cur)<=cur_lim else cur[:cur_lim]+"…"))
        rs=dedupe(byseg[g])
        for r in rs[:per_max]:
            t=r["text"].replace("\n"," / ")
            if len(t)>430: t=t[:430]+"…"
            Ls.append("  〔%d〕%s"%(r["resp"],t))
        if len(rs)>per_max: Ls.append("  （另有 %d 條同段意見）"%(len(rs)-per_max))
    p=os.path.join(OUT,"dg2_%s.txt"%chunk[:3])
    io.open(p,"w",encoding="utf-8").write("\n".join(Ls))
    return p, sum(len(x) for x in Ls), len(byseg)

if __name__=="__main__":
    for ch in sys.argv[1].split(","):
        print(build(ch))
