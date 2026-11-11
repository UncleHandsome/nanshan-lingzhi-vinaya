# -*- coding: utf-8 -*-
"""Repair: rebuild modified chunks from backup, replacing only changed lines; keep bytes."""
import os, io, json, sys
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BAK=os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
LOG=os.path.join(ROOT,"AI語譯","_work","review","_log_r2_02.json")
ops=json.load(io.open(LOG,encoding="utf-8"))
by={}
for o in ops: by.setdefault(o["chunk"],[]).append(o)
rep=[]
for ch,olist in by.items():
    rb=open(os.path.join(BAK,ch+".txt"),"rb").read().decode("utf-8")
    toks=rb.split("\r\n")
    assert toks[1::2]==[""]*len(toks[1::2]), ch   # every separator is empty -> one para per line
    n=len(toks)//2
    for o in olist:
        i=2*(o["seg"]-1)
        if i>=len(toks): rep.append("SKIP %s#%d out of range"%(ch,o["seg"])); continue
        p=toks[i]; c=p.count(o["old"])
        if c!=1:
            rep.append("FAIL %s#%d count=%d"%(ch,o["seg"],c)); continue
        toks[i]=p.replace(o["old"],o["new"])
    out="\r\n".join(toks)
    open(os.path.join(OUTD,ch+".txt"),"wb").write(out.encode("utf-8"))
    rep.append("OK %s paras=%d ops=%d"%(ch,n,len(olist)))
io.open(os.path.join(ROOT,"AI語譯","_work","review","_r2_02","_repair.txt"),"w",encoding="utf-8").write("\n".join(rep))
print("done",len(rep))
