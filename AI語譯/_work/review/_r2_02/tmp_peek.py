# -*- coding: utf-8 -*-
import io, os, re
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
R2=os.path.join(ROOT,"batch_qwen","r2")
out=[]
for n in [642,650,700,750,800,850,870,876,877,880,900,930,1397]:
    p=os.path.join(R2,"resp_%d.txt"%n)
    if not os.path.exists(p): out.append("%d MISSING"%n); continue
    t=io.open(p,encoding="utf-8-sig",errors="replace").read()
    out.append("="*30+" resp_%d  len=%d"%(n,len(t)))
    out.append(t[:900])
    out.append("")
io.open("tmp_peek.txt","w",encoding="utf-8").write("\n".join(out))
