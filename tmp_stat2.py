import io,os,re,sys,glob
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
BAK=os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
chunks=["09b_卷二下之二","09c_卷二下之二","09d_卷二下之二","10a_卷三上之一","10b_卷三上之一","10c_卷三上之一","10d_卷三上之一","11a_卷三上之二","11b_卷三上之二","11c_卷三上之二","12a_卷三上之三","12b_卷三上之三"]
rows=[]
for ch in chunks:
    t=io.open(os.path.join(OUT,"q_%s.txt"%ch[:3]),encoding="utf-8").read()
    n=len(re.findall(r"<K\d+\|",t))
    cur=io.open(os.path.join(OUTD,ch+".txt"),encoding="utf-8",newline="").read()
    cands=sorted(glob.glob(os.path.join(BAK,ch+"_d*.txt")))
    bak=io.open(cands[-1],encoding="utf-8",newline="").read()
    pc=cur.split("\r\n\r\n"); pb=bak.split("\r\n\r\n")
    diffs=[i+1 for i in range(min(len(pc),len(pb))) if pc[i]!=pb[i]]
    lf=cur.count("\n")-cur.count("\r\n")
    rows.append((ch[:3],n,len(pc),len(pb),lf,len(diffs),diffs))
for r in rows: print("%s claims=%d parts=%d/%d lf=%d segs=%d %s"%r)
print("TOTAL claims",sum(r[1] for r in rows),"segs",sum(r[5] for r in rows))
