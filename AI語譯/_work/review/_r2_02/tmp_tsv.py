# -*- coding: utf-8 -*-
import io, os, json, collections
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
HERE=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
rows=[json.loads(l) for l in io.open(os.path.join(HERE,"_apply2_log.jsonl"),encoding="utf-8") if l.strip()]
seen=[]; got=set()
for o in rows:
    k=(o["chunk"],o["seg"])
    if k in got: continue
    got.add(k); seen.append(o)
def para(chunk,seg):
    t=io.open(os.path.join(OUTD,chunk+".txt"),encoding="utf-8",newline="").read()
    ps=t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"): ps[-1]=ps[-1][:-2]
    return ps[seg-1]
out=[]
for o in seen:
    out.append("%s\t%s\t%d\t%s"%(o["chunk"].split("_")[0],o["chunk"],o["seg"],para(o["chunk"],o["seg"]).replace("\t"," ")))
body="\n".join(out)+"\n"
for p in [os.path.join(HERE,"fix_r2_02b.tsv"), os.path.join(ROOT,"AI語譯","_work","review","fix_r2_02b.tsv")]:
    io.open(p,"w",encoding="utf-8").write(body)
print("rows",len(out),"bytes",len(body))
