# -*- coding: utf-8 -*-
"""Batch digest: top-N hardest claims per chunk, with orig + current paras."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
M=L.load_map(); idx=M["idx"]
REFS=json.load(io.open(os.path.join(OUT,"_refs.json"),encoding="utf-8"))
STRONG=re.compile(r"相反|顛倒|譯反|主詞|受詞|施受|應作|誤譯|譯錯|讀成|當成|當作|混為|矛盾|不成詞|非是|不是.{1,12}而是|錯解|誤解|丟了|脫落|方向|說反|變成.{1,6}義|失準|曲解")
WEAK=re.compile(r"增譯|漏譯|未譯|查無|無據|意思|義理|文意|語意|應是|宜改|改作|精確|不一|統一")
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
def build(chunks, topn=6, bt=340, ot=190, path=None):
    Ls=[]
    for chunk in chunks:
        pres=REFS["by_chunk"].get(chunk,[])
        ps=L.paras(chunk); per=collections.defaultdict(list)
        for pre in pres:
            for b in blocks_of(pre):
                if not (STRONG.search(b) or WEAK.search(b)): continue
                for g in ids_in(b,pre,chunk):
                    per[g].append((pre,b))
        scored=[]
        for g,bl in per.items():
            sc=sum(2*len(STRONG.findall(b))+len(WEAK.findall(b)) for _,b in bl)
            scored.append((sc,g,bl))
        scored.sort(key=lambda x:-x[0])
        Ls.append("#"*20+" %s (segs=%d, claims=%d)"%(chunk,len(ps),len(per)))
        for sc,g,bl in scored[:topn]:
            s=int(idx[g]["seg"]); e=idx[g]
            Ls.append("=== 【%s】#%d score=%d"%(g,s,sc))
            Ls.append("原文："+e["orig"][:ot])
            Ls.append("現行："+(ps[s-1] if 0<s<=len(ps) else "NA"))
            for p,b in bl[:3]: Ls.append("[%s] %s"%(p,b[:bt].replace("\n"," / ")))
            Ls.append("")
    path=path or os.path.join(OUT,"batch.txt")
    io.open(path,"w",encoding="utf-8").write("\n".join(Ls))
    return path, sum(len(x) for x in Ls)
if __name__=="__main__":
    chs=sys.argv[1].split(","); topn=int(sys.argv[2]) if len(sys.argv)>2 else 6
    print(build(chs, topn=topn, path=sys.argv[3] if len(sys.argv)>3 else None))
