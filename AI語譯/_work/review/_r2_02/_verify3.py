# -*- coding: utf-8 -*-
"""Verify current vs backup: part count, differing segs, LF-only, counts."""
import os, io, sys, glob
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BAK  = os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
OUTD = os.path.join(ROOT,"AI語譯","out","02_戒疏")

def check(ch):
    cur_p=os.path.join(OUTD, ch+".txt")
    cands=sorted(glob.glob(os.path.join(BAK, ch+"_d*.txt")))
    bak_p=cands[-1] if cands else os.path.join(BAK, ch+".txt")
    cur=io.open(cur_p,encoding="utf-8",newline="").read()
    bak=io.open(bak_p,encoding="utf-8",newline="").read()
    pc=cur.split("\r\n\r\n"); pb=bak.split("\r\n\r\n")
    lf_only = cur.count("\n")-cur.count("\r\n")
    diffs=[i+1 for i in range(min(len(pc),len(pb))) if pc[i]!=pb[i]]
    print("%s parts %d/%d lf_only=%d endswith=%r diffs=%s"%(ch[:3],len(pc),len(pb),lf_only,cur[-4:],diffs))
    return len(pc),len(pb),diffs

if __name__=="__main__":
    for ch in sys.argv[1].split(","):
        check(ch)
