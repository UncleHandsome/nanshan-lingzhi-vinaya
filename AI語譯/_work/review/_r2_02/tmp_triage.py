# -*- coding: utf-8 -*-
import io, os, re, glob, collections, json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"; R2=os.path.join(ROOT,"batch_qwen","r2")
PER=json.load(io.open("tmp_per.json",encoding="utf-8"))
nums=[n for n in sorted(int(re.search(r"resp_(\d+)",p).group(1)) for p in glob.glob(os.path.join(R2,"resp_*.txt"))) if 642<=n<=876]
full=0; hashonly=0; none=0; other=0
lines=[]
for n in nums:
    t=io.open(os.path.join(R2,"resp_%d.txt"%n),encoding="utf-8-sig",errors="replace").read()
    ids=re.findall(r"(\d{3})-(\d{4})",t)
    mine=[a+"-"+b for a,b in ids if a==str(n)]
    hashes=re.findall(r"#(\d{1,3})(?!\d)",t)
    segs={v[1] for v in PER[str(n)].values()}
    hh=[h for h in hashes if int(h) in segs]
    if mine: full+=1; tag="id"
    elif hh: hashonly+=1; tag="hash"
    else: none+=1; tag="none"
    lines.append("%d %s ids=%d hash=%d segs=%d"%(n,tag,len(mine),len(hh),len(segs)))
print("full-id",full,"hash-only",hashonly,"none",none)
io.open("tmp_triage.txt","w",encoding="utf-8").write("\n".join(lines))
