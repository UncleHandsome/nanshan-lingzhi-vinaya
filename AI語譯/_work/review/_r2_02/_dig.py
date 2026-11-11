# -*- coding: utf-8 -*-
"""Per-chunk digest: for each referenced seg, show orig/current + Qwen blocks that mention it."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
M = L.load_map(); idx=M["idx"]
refs = json.load(io.open(os.path.join(OUT,"_refs.json"),encoding="utf-8"))
by_chunk = refs["by_chunk"]; fall = refs["refs"]

def digest(chunk, trim=520):
    files = by_chunk[chunk]
    ps = L.paras(chunk)
    # collect blocks per seg
    per = collections.defaultdict(list)
    general = []
    for pre in files:
        t = io.open(os.path.join(ROOT,"batch_qwen","r2","resp_%s.txt"%pre),encoding="utf-8-sig").read()
        blocks = [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]
        for b in blocks:
            ids=[]
            for mm in re.finditer(r"(?<!\d)(\d{3})-(\d{4})(?!\d)", b):
                g=mm.group(1)+"-"+mm.group(2)
                if g in idx and idx[g]["chunk"]==chunk and g not in ids: ids.append(g)
            if not ids:
                for mm in re.finditer(r"(?<!\d)(\d{4})(?!\d)", b):
                    g=pre+"-"+mm.group(1)
                    if g in idx and idx[g]["chunk"]==chunk and g not in ids: ids.append(g)
            if not ids:
                if re.search(r"★|誤|錯|相反|顛倒|增譯|漏譯|術語|主詞|應作|統一|全批|系統", b):
                    general.append((pre,b))
                continue
            for g in ids: per[g].append((pre,b))
    lines=[]
    lines.append("# %s  段數=%d  回應檔=%s"%(chunk,len(ps),",".join(files)))
    lines.append("")
    if general:
        lines.append("## 通則（未指名段）")
        for pre,b in general[:8]:
            lines.append("[%s] %s"%(pre,b[:trim].replace("\n"," ")))
        lines.append("")
    for g in sorted(per, key=lambda x: int(x.split("-")[1])):
        s=int(g.split("-")[1]); e=idx[g]
        lines.append("="*8+" 【%s】#%d "%(g,s))
        lines.append("原文："+e["orig"])
        lines.append("現行："+(ps[s-1] if 0<s<=len(ps) else "NA"))
        for pre,b in per[g]:
            lines.append("[%s] %s"%(pre,b[:trim].replace("\n"," / ")))
        lines.append("")
    p=os.path.join(OUT,"dig_%s.txt"%chunk.split("_")[0])
    io.open(p,"w",encoding="utf-8").write("\n".join(lines))
    return p, len(per), sum(len(x) for x in lines)

if __name__=="__main__":
    ch=sys.argv[1]
    p,n,chars=digest(ch)
    print("wrote",p,"segs",n,"chars",chars)
