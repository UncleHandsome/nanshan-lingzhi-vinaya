# -*- coding: utf-8 -*-
import os,io,json,glob
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
ops=[]
for p in ["ops_09b.json","ops_b1.json","ops_b2.json","ops_b2x.json","ops_b3.json","ops_b4.json","ops_b5.json"]:
    fp=os.path.join(OUT,p)
    if os.path.exists(fp): ops += json.load(io.open(fp,encoding="utf-8-sig"))
io.open(os.path.join(ROOT,"AI語譯","_work","review","_log_r2_02.json"),"w",encoding="utf-8").write(
    json.dumps(ops,ensure_ascii=False,indent=1))
import collections
c=collections.Counter((o["chunk"],o["seg"]) for o in ops)
print("edits",len(ops),"segs",len(c))
for k,v in sorted(c.items()): print(k,v)
