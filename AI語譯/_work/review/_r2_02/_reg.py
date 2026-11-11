# -*- coding: utf-8 -*-
import os,io,json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
M=json.load(io.open(os.path.join(OUT,"_refs.json"),encoding="utf-8"))
import sys
sys.path.insert(0,OUT)
import _r2lib as L
chg={"09b":1,"09c":2,"09d":4,"10a":5,"10b":4,"10c":5,"10d":3,"11a":3,"11b":3,"11c":3,"12a":3,"12b":3}
rows=[]
for k in sorted(M["by_chunk"]):
    t=k.split("_")[0]
    if t not in chg: continue
    fs=sorted(M["by_chunk"][k])
    n=len(L.paras(k))
    rows.append("2026-11-11\tresp_%s-%s\t02_戒疏\t%s\t%d\t02戒疏-subagent\t說明_r2_02.md\t%d段中改%d段"%(fs[0],fs[-1],k,chg[t],n,chg[t]))
rows.sort(key=lambda r:r.split("\t")[3])
p=os.path.join(ROOT,"batch_qwen","r2_processed.tsv")
exists=os.path.exists(p)
io.open(p,"a",encoding="utf-8",newline="").write(("\n".join(rows))+"\r\n")
print("exists_before",exists,"rows",len(rows))
