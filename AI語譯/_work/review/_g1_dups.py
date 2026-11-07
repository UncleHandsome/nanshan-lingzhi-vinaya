# -*- coding: utf-8 -*-
import io, os, collections
base="AI語譯"
lines=[l.rstrip("\n") for l in io.open(os.path.join(base,"_work","review","_g1_work.tsv"),encoding="utf-8") if l.strip()]
hdr=lines[0].split("\t"); rows=[dict(zip(hdr,l.split("\t"))) for l in lines[1:]]
d=collections.defaultdict(list)
for i,r in enumerate(rows,1): d[(r["book"],r["chunk"],r["seg"])].append(i)
dups={k:v for k,v in d.items() if len(v)>1}
out=[]
for k,v in dups.items(): out.append("%s %s seg%s -> rows %s" % (k[0],k[1],k[2],v))
io.open(os.path.join(base,"_work","review","_g1_dups.txt"),"w",encoding="utf-8").write("\n".join(out)+"\n")
print("unique keys: %d, dup keys: %d" % (len(d), len(dups)))
