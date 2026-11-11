# -*- coding: utf-8 -*-
import io,os,json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BAK=os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
exp={"09b_卷二下之二":[166],"09c_卷二下之二":[53,74],"09d_卷二下之二":[16,27,50,53],
 "10a_卷三上之一":[25,26,27,34,135],"10b_卷三上之一":[1,3,15,62],"10c_卷三上之一":[20,117,131,132,134],
 "10d_卷三上之一":[1,6,7],"11a_卷三上之二":[58,61,84],"11b_卷三上之二":[53,102,108],
 "11c_卷三上之二":[32,102,103],"12a_卷三上之三":[40,41,46],"12b_卷三上之三":[14,16,69]}
rep=[]; rows=[]
for ch,segs in exp.items():
    b=open(os.path.join(BAK,ch+".txt"),"rb").read()
    c=open(os.path.join(OUTD,ch+".txt"),"rb").read()
    ok_lf = (c.count(b"\n")-c.count(b"\r\n"))==0
    tb=b.split(b"\r\n"); tc=c.split(b"\r\n")
    if len(tb)!=len(tc): rep.append("%s TOKENLEN %d/%d"%(ch,len(tb),len(tc))); continue
    diffs=[i//2+1 for i in range(len(tb)) if tb[i]!=tc[i]]
    rep.append("%s tokens=%d diff=%s expect=%s %s"%(ch,len(tb),diffs,segs,"OK" if diffs==segs and ok_lf else "**MISMATCH**"))
    for s in segs: rows.append((ch,s,tc[2*(s-1)].decode("utf-8")))
io.open(os.path.join(ROOT,"AI語譯","_work","review","_r2_02","_verify2.txt"),"w",encoding="utf-8").write("\n".join(rep))
rows.sort(key=lambda r:(r[0],r[1]))
with io.open(os.path.join(ROOT,"AI語譯","_work","review","fix_r2_02.tsv"),"w",encoding="utf-8",newline="") as f:
    for ch,s,t in rows: f.write("02_戒疏\t%s\t%d\t%s\r\n"%(ch,s,t))
print("rows",len(rows))
