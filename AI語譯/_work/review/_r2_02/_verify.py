# -*- coding: utf-8 -*-
"""Verify edits vs backup; emit TSV of changed paragraphs."""
import os, io, json, sys, glob, collections
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
BAK=os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
sys.path.insert(0,OUT)
import _r2lib as L

def rd(p):
    t=io.open(p,encoding="utf-8",newline="").read()
    parts=t.split("\r\n\r\n")
    if parts and parts[-1].endswith("\r\n"): parts[-1]=parts[-1][:-2]
    return parts

rows=[]; report=[]
for bp in sorted(glob.glob(os.path.join(BAK,"*.txt"))):
    ch=os.path.basename(bp)[:-4]
    old=rd(bp); new=L.paras(ch)
    report.append("%s: old=%d new=%d"%(ch,len(old),len(new)))
    if len(old)!=len(new):
        report.append("  !! 段數不同")
        continue
    diffs=[i+1 for i in range(len(old)) if old[i]!=new[i]]
    report.append("  changed segs: %s"%diffs)
    for i in diffs:
        rows.append(("02_戒疏",ch,i,new[i-1]))
rows.sort(key=lambda r:(r[1],r[2]))
with io.open(os.path.join(ROOT,"AI語譯","_work","review","fix_r2_02.tsv"),"w",encoding="utf-8",newline="") as f:
    for r in rows:
        f.write("%s\t%s\t%d\t%s\r\n"%r)
io.open(os.path.join(OUT,"_verify.txt"),"w",encoding="utf-8").write("\n".join(report))
print("rows",len(rows))
