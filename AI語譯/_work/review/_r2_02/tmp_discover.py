# -*- coding: utf-8 -*-
import json, io, os, re, glob
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
O=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
M=json.load(io.open(os.path.join(O,"_map.json"),encoding="utf-8"))
idx=M["idx"]
from collections import Counter
c=Counter(v["book"] for v in idx.values())
out=[]
out.append("books: "+repr(c))
bs=[v for v in idx.values() if v["book"].startswith("02_")]
pre=Counter(v["id"][:3] for v in bs)
out.append("02 count %d prefixes %d min %s max %s"%(len(bs),len(pre),min(pre),max(pre)))
out.append("prefixes: "+",".join(sorted(pre)))
chunks=Counter(v["chunk"] for v in bs)
out.append("chunks: "+repr(sorted(chunks.items())))
io.open("tmp_discover.txt","w",encoding="utf-8").write("\n".join(out))
