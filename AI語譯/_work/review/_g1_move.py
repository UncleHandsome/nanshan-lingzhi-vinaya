# -*- coding: utf-8 -*-
import io, os, re
base="AI語譯"
lines=[l.rstrip("\n") for l in io.open(os.path.join(base,"_work","review","_g1_work.tsv"),encoding="utf-8") if l.strip()]
hdr=lines[0].split("\t"); rows=[dict(zip(hdr,l.split("\t"))) for l in lines[1:]]
MOVE=[1,2,3,4,5,6,8,9,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,33,34,36,37,38,39,40,43,45,47,49,51,52,54,55,56,57,63,70,71,72,73,77,78,82,83,84,85,88,89,90,91,92,93,94,98,99,100,101,102,104,105,106,107,113,120]
out=[]
for i in MOVE:
    r=rows[i-1]; s=r["suggestion"]; a=s.find("\u300c"); b=s.rfind("\u300d")
    q=s[a+1:b] if (a!=-1 and b>a) else ""
    ell="ELL" if "\u2026" in q else "FULL"
    o=r["orig"]; c=r["current"]
    out.append("[%d] %s seg%s cls=%s | Olen=%d Qlen=%d %s" % (i, r["chunk"], r["seg"], r["cls"], len(o), len(q), ell))
    out.append("  Q : " + q)
    out.append("  O : " + o[:70] + (" ..." if len(o)>70 else ""))
    out.append("  C : " + c[:70] + (" ..." if len(c)>70 else ""))
io.open(os.path.join(base,"_work","review","_g1_move.txt"),"w",encoding="utf-8").write("\n".join(out))
