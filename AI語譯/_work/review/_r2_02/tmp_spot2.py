# -*- coding: utf-8 -*-
import io, os
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
def para(chunk,seg):
    t=io.open(os.path.join(OUTD,chunk+".txt"),encoding="utf-8",newline="").read()
    ps=t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"): ps[-1]=ps[-1][:-2]
    return ps[seg-1]
items=[("13a_卷三下之一",112),("16c_卷四上之一",142),("20b_卷四下之二",58),("18c_卷四上之三",23)]
L=[]
for c,s in items:
    L.append("="*10+" %s #%d"%(c.split("_")[0],s)); L.append(para(c,s)); L.append("")
io.open("_spot2.txt","w",encoding="utf-8").write("\n".join(L))
print("ok")
