# -*- coding: utf-8 -*-
import io, os, re
base="AI語譯"
lines=[l.rstrip("\n") for l in io.open(os.path.join(base,"_work","review","_g1_work.tsv"),encoding="utf-8") if l.strip()]
hdr=lines[0].split("\t"); rows=[dict(zip(hdr,l.split("\t"))) for l in lines[1:]]
MOVE=("錯配","串段","錯位","張冠李戴","滑動","漏譯")
m=[];e=[]
for i,r in enumerate(rows,1):
    p=r["problem"]
    ismove = any(k in p for k in ("錯配","串段","錯位","張冠李戴","滑動"))
    (m if ismove else e).append(i)
print("MOVE-type (%d): %s" % (len(m), m))
print("EDIT-type (%d): %s" % (len(e), e))
