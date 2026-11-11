# -*- coding: utf-8 -*-
"""Apply ops preserving exact bytes except edited paragraphs. Backup with _d suffix."""
import os, io, json, sys, shutil
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT  = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
BAK  = os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
sys.path.insert(0, OUT)
import _r2lib as L

def backup(ch):
    src=L.path(ch)
    base=os.path.join(BAK, ch+".txt")
    cand=os.path.join(BAK, ch+"_d.txt")
    k=2
    while os.path.exists(cand):
        cand=os.path.join(BAK, ch+"_d%d.txt"%k); k+=1
    shutil.copy2(src,cand)
    return cand

def main(ops_path, backup_first=True):
    ops=json.load(io.open(ops_path,encoding="utf-8-sig"))
    bychunk={}
    for o in ops: bychunk.setdefault(o["chunk"],[]).append(o)
    log=[]
    for ch,olist in bychunk.items():
        raw=L.read_raw(ch)
        parts=raw.split("\r\n\r\n")
        bak=backup(ch) if backup_first else None
        for o in olist:
            i=o["seg"]-1
            if not (0<=i<len(parts)): log.append("SKIP %s#%d"% (ch,o["seg"])); continue
            p=parts[i]; old=o["old"]; new=o["new"]
            n=p.count(old)
            if n==0: log.append("MISS %s#%d 「%s」"%(ch,o["seg"],old[:40])); continue
            if n>1:  log.append("DUP  %s#%d 「%s」x%d"%(ch,o["seg"],old[:40],n)); continue
            parts[i]=p.replace(old,new)
            log.append("OK   %s#%d %s -> %s"%(ch,o["seg"],old[:26],new[:26]))
        new_raw="\r\n\r\n".join(parts)
        io.open(L.path(ch),"w",encoding="utf-8",newline="").write(new_raw)
        # verify
        parts2=L.read_raw(ch).split("\r\n\r\n")
        assert len(parts2)==len(parts), (ch,len(parts),len(parts2))
    io.open(os.path.join(OUT,"_apply3log.txt"),"a",encoding="utf-8").write("\n".join(log)+"\n")
    print("OK",sum(1 for x in log if x.startswith("OK")),"of",len(ops))
    for x in log:
        if not x.startswith("OK"): print(x)

if __name__=="__main__": main(sys.argv[1])
