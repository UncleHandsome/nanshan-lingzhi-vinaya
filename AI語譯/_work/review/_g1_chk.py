# -*- coding: utf-8 -*-
import io, os, re, glob
base="AI語譯"
lines=[l.rstrip("\n") for l in io.open(os.path.join(base,"_work","review","_g1_work.tsv"),encoding="utf-8") if l.strip()]
hdr=lines[0].split("\t"); rows=[dict(zip(hdr,l.split("\t"))) for l in lines[1:]]
chunks=["00_卷首"]+sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(base,"out","03_業疏","*.txt")) if not os.path.basename(p).startswith("00"))
allp=[]
for c in chunks:
    p=os.path.join(base,"out","03_業疏",c+".txt")
    if not os.path.exists(p): continue
    ps=[x.strip() for x in re.split(r"\r?\n\s*\r?\n", io.open(p,encoding="utf-8").read()) if x.strip()]
    for i,t in enumerate(ps,1): allp.append((c,i,t))
def norm(s): return re.sub(r"[\s\u3000]","",s)
for i,r in enumerate(rows,1):
    s=r["suggestion"]; a=s.find("\u300c"); b=s.rfind("\u300d")
    q=s[a+1:b] if (a!=-1 and b>a) else None
    ell = "\u2026" in (q or "")
    found=None
    if q:
        pre=norm(q)
        k=pre.find("\u2026")
        if k>0: pre=pre[:k]
        pre=pre[:20]
        if len(pre)>=6:
            for (c,idx,t) in allp:
                if norm(t).startswith(pre): found=(c,idx); break
    print("row=%-3d seg=%-3s q=%s ell=%s found=%s" % (i, r["seg"], "Y" if q else "N", "Y" if ell else "N", found))
