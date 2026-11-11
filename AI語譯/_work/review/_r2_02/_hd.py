# -*- coding: utf-8 -*-
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
M=L.load_map(); idx=M["idx"]
HARD=re.compile(r"相反|顛倒|譯反|主詞|受詞|施受|應作|誤譯|譯錯|讀成|當成|當作|混為|增譯|漏譯|未譯|查無|無據|不成詞|矛盾|丟了|脫落|意思|義理|非是|不是.{1,10}而是|文意|語意|錯解|誤解|方向|按語|應是|宜改|改作")
def blocks_of(pre):
    t=io.open(os.path.join(ROOT,"batch_qwen","r2","resp_%s.txt"%pre),encoding="utf-8-sig").read()
    return [b.strip() for b in re.split(r"\n\s*\n",t) if b.strip()]
def ids_in(b,pre,chunk):
    ids=[]
    for mm in re.finditer(r"(?<!\d)(\d{3})-(\d{4})(?!\d)",b):
        g=mm.group(1)+"-"+mm.group(2)
        if g in idx and idx[g]["chunk"]==chunk and g not in ids: ids.append(g)
    if not ids:
        for mm in re.finditer(r"(?<!\d)(\d{4})(?!\d)",b):
            g=pre+"-"+mm.group(1)
            if g in idx and idx[g]["chunk"]==chunk and g not in ids: ids.append(g)
    return ids
def digest(chunk,pres,bt=260,ot=200):
    ps=L.paras(chunk); per=collections.defaultdict(list); seen=set(); gen=[]
    for pre in pres:
        for b in blocks_of(pre):
            if not HARD.search(b): continue
            ids=ids_in(b,pre,chunk); key=b[:100]
            if not ids:
                if key in seen: continue
                seen.add(key); gen.append((pre,b)); continue
            for g in ids:
                if (g,key) in seen: continue
                seen.add((g,key)); per[g].append((pre,b))
    Ls=["# %s segs=%d"%(chunk,len(ps)),""]
    if gen: Ls.append("## 通則"); Ls+=["[%s] %s"%(p,b[:bt].replace("\n"," / ")) for p,b in gen[:5]]; Ls.append("")
    for g in sorted(per,key=lambda x:int(x.split("-")[1])):
        s=int(g.split("-")[1]); e=idx[g]
        Ls.append("=== 【%s】#%d"%(g,s)); Ls.append("原文："+e["orig"][:ot])
        Ls.append("現行："+(ps[s-1] if 0<s<=len(ps) else "NA"))
        for p,b in per[g]: Ls.append("[%s] %s"%(p,b[:bt].replace("\n"," / ")))
        Ls.append("")
    path=os.path.join(OUT,"h_"+chunk.split("_")[0]+".txt")
    io.open(path,"w",encoding="utf-8").write("\n".join(Ls))
    return path,len(per),sum(len(x) for x in Ls)
if __name__=="__main__":
    print(digest(sys.argv[1],sys.argv[2].split(",")))
