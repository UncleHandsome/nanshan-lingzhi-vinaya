# -*- coding: utf-8 -*-
"""Apply edits: ops json = [{chunk,seg,old,new}]. Backup chunk once. Verify uniqueness."""
import os, io, json, sys, shutil
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT  = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
BAK  = os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
sys.path.insert(0, OUT)
import _r2lib as L

def main(ops_path):
    ops = json.load(io.open(ops_path, encoding="utf-8-sig"))
    os.makedirs(BAK, exist_ok=True)
    bychunk = {}
    for o in ops: bychunk.setdefault(o["chunk"], []).append(o)
    log = []
    for ch, olist in bychunk.items():
        src = L.path(ch); bak = os.path.join(BAK, ch+".txt")
        if not os.path.exists(bak): shutil.copy2(src, bak)
        ps = L.paras(ch)
        for o in olist:
            i = o["seg"]-1
            if not (0 <= i < len(ps)):
                log.append("SKIP %s#%d 超出段數"%(ch,o["seg"])); continue
            p = ps[i]; old = o["old"]; new = o["new"]
            n = p.count(old)
            if n == 0:
                log.append("MISS %s#%d 「%s」"%(ch,o["seg"],old[:40])); continue
            if n > 1:
                log.append("DUP  %s#%d 「%s」x%d"%(ch,o["seg"],old[:40],n)); continue
            ps[i] = p.replace(old, new)
            log.append("OK   %s#%d %s -> %s"%(ch,o["seg"],old[:30],new[:30]))
        L.write_paras(ch, ps)
    io.open(os.path.join(OUT,"_applylog.txt"),"w",encoding="utf-8-sig").write("\n".join(log))
    print("applied", sum(1 for x in log if x.startswith("OK")), "of", len(ops))
    for x in log:
        if not x.startswith("OK"): print(x)

if __name__=="__main__":
    main(sys.argv[1])
